from fastapi import APIRouter, HTTPException
from ..models import TopicCreate, ClassroomCreate, TeacherReviewCreate
from ..core.database import get_db_connection
from ..core.plagiarism import PlagiarismDetector
from ..core.analytics import TeacherAnalyticsService
from ..core.cache import cache_manager, teacher_topics_cache_key, teacher_analytics_cache_key
import secrets
import string

router = APIRouter()
analytics_service = TeacherAnalyticsService()


@router.get("/analytics/{teacher_id}")
def get_teacher_analytics(teacher_id: int):
    try:
        # Return cached analytics if available
        cache_key = teacher_analytics_cache_key(teacher_id)
        cached = cache_manager.get_json(cache_key)
        if cached is not None:
            return cached

        data = analytics_service.get_teacher_analytics(teacher_id)
        try:
            cache_manager.set_json(cache_key, data, ttl_seconds=300)
        except Exception:
            pass
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_join_code(size: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(size))


@router.post("/create-classroom")
def create_classroom(payload: ClassroomCreate):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id FROM Users WHERE user_id = %s AND role = 'teacher'",
            (payload.teacher_id,)
        )
        teacher = cursor.fetchone()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        join_code = None
        for _ in range(10):
            candidate = _generate_join_code()
            cursor.execute("SELECT classroom_id FROM Classrooms WHERE join_code = %s", (candidate,))
            if not cursor.fetchone():
                join_code = candidate
                break

        if not join_code:
            raise HTTPException(status_code=500, detail="Could not generate unique classroom code")

        classroom_name = (payload.classroom_name or payload.subject_name).strip()
        if not classroom_name:
            raise HTTPException(status_code=400, detail="Classroom name is required")

        cursor.execute(
            """
            INSERT INTO Classrooms (teacher_id, classroom_name, subject_name, join_code)
            VALUES (%s, %s, %s, %s)
            """,
            (payload.teacher_id, classroom_name, payload.subject_name.strip(), join_code)
        )
        db.commit()

        return {
            "message": "Classroom created successfully",
            "classroom_id": cursor.lastrowid,
            "join_code": join_code,
            "classroom_name": classroom_name,
            "subject_name": payload.subject_name.strip(),
        }
    finally:
        db.close()


@router.get("/classrooms/{teacher_id}")
def get_teacher_classrooms(teacher_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT c.classroom_id, c.classroom_name, c.subject_name, c.join_code,
                   c.created_at, COUNT(cm.student_id) AS student_count
            FROM Classrooms c
            LEFT JOIN ClassroomMembers cm ON cm.classroom_id = c.classroom_id
            WHERE c.teacher_id = %s
            GROUP BY c.classroom_id
            ORDER BY c.created_at DESC
            """,
            (teacher_id,)
        )
        return cursor.fetchall()
    finally:
        db.close()


@router.delete("/delete-classroom/{classroom_id}")
def delete_classroom(classroom_id: int, teacher_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT classroom_id
            FROM Classrooms
            WHERE classroom_id = %s AND teacher_id = %s
            """,
            (classroom_id, teacher_id)
        )
        classroom = cursor.fetchone()
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found for this teacher")

        cursor.execute(
            """
            DELETE tr
            FROM TeacherReviews tr
            JOIN Essays e ON tr.essay_id = e.essay_id
            JOIN Topics t ON e.topic_id = t.topic_id
            WHERE t.classroom_id = %s
            """,
            (classroom_id,)
        )
        cursor.execute(
            """
            DELETE f
            FROM Feedback f
            JOIN Evaluations ev ON f.evaluation_id = ev.evaluation_id
            JOIN Essays e ON ev.essay_id = e.essay_id
            JOIN Topics t ON e.topic_id = t.topic_id
            WHERE t.classroom_id = %s
            """,
            (classroom_id,)
        )
        cursor.execute(
            """
            DELETE g
            FROM Grades g
            JOIN Evaluations ev ON g.evaluation_id = ev.evaluation_id
            JOIN Essays e ON ev.essay_id = e.essay_id
            JOIN Topics t ON e.topic_id = t.topic_id
            WHERE t.classroom_id = %s
            """,
            (classroom_id,)
        )
        cursor.execute(
            """
            DELETE ev
            FROM Evaluations ev
            JOIN Essays e ON ev.essay_id = e.essay_id
            JOIN Topics t ON e.topic_id = t.topic_id
            WHERE t.classroom_id = %s
            """,
            (classroom_id,)
        )
        cursor.execute(
            """
            DELETE e
            FROM Essays e
            JOIN Topics t ON e.topic_id = t.topic_id
            WHERE t.classroom_id = %s
            """,
            (classroom_id,)
        )
        cursor.execute("DELETE FROM Topics WHERE classroom_id = %s", (classroom_id,))
        cursor.execute("DELETE FROM ClassroomMembers WHERE classroom_id = %s", (classroom_id,))
        cursor.execute("DELETE FROM Classrooms WHERE classroom_id = %s", (classroom_id,))

        db.commit()
        # Invalidate cached topics list for this teacher so frontend sees updated assignments
        try:
            cache_manager.delete(teacher_topics_cache_key(teacher_id))
            cache_manager.delete(teacher_analytics_cache_key(teacher_id))
        except Exception:
            # cache invalidation failure shouldn't block the deletion
            pass
        return {"message": "Classroom deleted successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/add-topic")
def add_topic(topic: TopicCreate):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        if topic.classroom_id is not None:
            cursor.execute(
                "SELECT classroom_id FROM Classrooms WHERE classroom_id = %s AND teacher_id = %s",
                (topic.classroom_id, topic.teacher_id)
            )
            classroom = cursor.fetchone()
            if not classroom:
                raise HTTPException(status_code=404, detail="Classroom not found for this teacher")

        query = "INSERT INTO Topics (title, description, keywords, teacher_id, classroom_id) VALUES (%s, %s, %s, %s, %s)"
        values = (topic.title, topic.description, topic.keywords, topic.teacher_id, topic.classroom_id)
        cursor.execute(query, values)
        db.commit()
        try:
            cache_manager.delete(teacher_topics_cache_key(topic.teacher_id))
            cache_manager.delete(teacher_analytics_cache_key(topic.teacher_id))
        except Exception:
            pass
        return {"message": "Topic added successfully", "topic_id": cursor.lastrowid}
    finally:
        db.close()

@router.get("/get-topics-teacher/{teacher_id}")
def get_topics_teacher(teacher_id: int):
    cache_key = teacher_topics_cache_key(teacher_id)
    cached = cache_manager.get_json(cache_key)
    if cached is not None:
        return cached

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT t.topic_id, t.title, t.description, t.keywords, t.classroom_id,
                   c.classroom_name, c.subject_name
            FROM Topics t
            LEFT JOIN Classrooms c ON c.classroom_id = t.classroom_id
            WHERE t.teacher_id = %s
            ORDER BY t.topic_id DESC
        """
        cursor.execute(query, (teacher_id,))
        rows = cursor.fetchall()
        cache_manager.set_json(cache_key, rows, ttl_seconds=300)
        return rows
    finally:
        db.close()

@router.get("/topic-submissions/{topic_id}")
def get_topic_submissions(topic_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT
                e.essay_id,
                e.student_id,
                e.essay_text,
                e.submission_date,
                u.name,
                g.final_score,
                f.feedback_text AS ai_feedback,
                tr.teacher_score,
                tr.teacher_feedback,
                tr.reviewed_at,
                tu.name AS reviewed_by
            FROM Users u
            JOIN Essays e ON u.user_id = e.student_id
            JOIN Evaluations ev ON e.essay_id = ev.essay_id
            JOIN Grades g ON ev.evaluation_id = g.evaluation_id
            LEFT JOIN Feedback f ON ev.evaluation_id = f.evaluation_id
            LEFT JOIN TeacherReviews tr ON tr.essay_id = e.essay_id
            LEFT JOIN Users tu ON tu.user_id = tr.teacher_id
            WHERE e.topic_id = %s
            ORDER BY e.submission_date DESC
        """
        cursor.execute(query, (topic_id,))
        rows = cursor.fetchall()

        detector = PlagiarismDetector()
        report = []

        for row in rows:
            current_text = row.get("essay_text") or ""
            max_similarity = 0.0
            suspected_source = None

            for candidate in rows:
                if candidate["essay_id"] == row["essay_id"]:
                    continue

                similarity = detector.calculate_similarity(current_text, candidate.get("essay_text") or "")
                if similarity > max_similarity:
                    max_similarity = similarity
                    suspected_source = {
                        "student_id": candidate["student_id"],
                        "name": candidate["name"],
                        "essay_id": candidate["essay_id"],
                        "similarity_percentage": round(similarity * 100, 2),
                    }

            plagiarism_percentage = round(max_similarity * 100, 2)
            plagiarism_level = detector.classify_plagiarism_level(plagiarism_percentage)
            is_plagiarized = plagiarism_percentage >= 50

            report.append({
                "essay_id": row["essay_id"],
                "student_id": row["student_id"],
                "student_name": row["name"],
                "essay_text": row.get("essay_text") or "",
                "final_score": float(row["final_score"]),
                "ai_feedback": row.get("ai_feedback") or "",
                "teacher_score": float(row["teacher_score"]) if row.get("teacher_score") is not None else None,
                "teacher_feedback": row.get("teacher_feedback") or "",
                "teacher_reviewed_at": row.get("reviewed_at"),
                "teacher_name": row.get("reviewed_by"),
                "plagiarism_percentage": plagiarism_percentage,
                "plagiarism_level": plagiarism_level,
                "is_plagiarized": is_plagiarized,
                "suspected_source": suspected_source,
                "submission_date": row["submission_date"],
            })

        report.sort(key=lambda item: item["submission_date"], reverse=True)
        return report
    finally:
        db.close()


@router.post("/review-submission")
def review_submission(payload: TeacherReviewCreate):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        if payload.teacher_score is not None and (payload.teacher_score < 0 or payload.teacher_score > 100):
            raise HTTPException(status_code=400, detail="Teacher score must be between 0 and 100")

        cursor.execute(
            """
            SELECT e.essay_id
            FROM Essays e
            JOIN Topics t ON t.topic_id = e.topic_id
            WHERE e.essay_id = %s AND t.teacher_id = %s
            """,
            (payload.essay_id, payload.teacher_id)
        )
        owned = cursor.fetchone()
        if not owned:
            raise HTTPException(status_code=404, detail="Essay not found for this teacher")

        cursor.execute(
            """
            INSERT INTO TeacherReviews (essay_id, teacher_id, teacher_score, teacher_feedback)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                teacher_id = VALUES(teacher_id),
                teacher_score = VALUES(teacher_score),
                teacher_feedback = VALUES(teacher_feedback),
                reviewed_at = CURRENT_TIMESTAMP
            """,
            (
                payload.essay_id,
                payload.teacher_id,
                payload.teacher_score,
                (payload.teacher_feedback or "").strip() or None,
            )
        )

        db.commit()
        return {"message": "Teacher review saved successfully", "essay_id": payload.essay_id}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.delete("/delete-topic/{topic_id}")
def delete_topic(topic_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
       
        cursor.execute("SELECT teacher_id FROM Topics WHERE topic_id = %s", (topic_id,))
        owner = cursor.fetchone()
        owner_id = owner[0] if owner else None

        cursor.execute("DELETE tr FROM TeacherReviews tr JOIN Essays e ON tr.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE f FROM Feedback f JOIN Evaluations ev ON f.evaluation_id = ev.evaluation_id JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE g FROM Grades g JOIN Evaluations ev ON g.evaluation_id = ev.evaluation_id JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE ev FROM Evaluations ev JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE FROM Essays WHERE topic_id = %s", (topic_id,))
        cursor.execute("DELETE FROM Topics WHERE topic_id = %s", (topic_id,))
        db.commit()
        if owner_id is not None:
            try:
                cache_manager.delete(teacher_topics_cache_key(owner_id))
                cache_manager.delete(teacher_analytics_cache_key(owner_id))
            except Exception:
                pass
        return {"message": "Topic deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()