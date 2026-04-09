from fastapi import APIRouter, HTTPException
from ..models import TopicCreate, ClassroomCreate
from ..core.database import get_db_connection
from ..core.plagiarism import PlagiarismDetector
import secrets
import string

router = APIRouter()


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
        return {"message": "Topic added successfully", "topic_id": cursor.lastrowid}
    finally:
        db.close()

@router.get("/get-topics-teacher/{teacher_id}")
def get_topics_teacher(teacher_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT t.topic_id, t.title, t.description, t.keywords, t.classroom_id,
                   c.classroom_name, c.subject_name
            FROM Topics t
            LEFT JOIN Classrooms c ON c.classroom_id = t.classroom_id
            WHERE t.teacher_id = %s
            ORDER BY t.topic_id DESC
            """,
            (teacher_id,)
        )
        return cursor.fetchall()
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
                g.final_score
            FROM Users u
            JOIN Essays e ON u.user_id = e.student_id
            JOIN Evaluations ev ON e.essay_id = ev.essay_id
            JOIN Grades g ON ev.evaluation_id = g.evaluation_id
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
                "final_score": float(row["final_score"]),
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

@router.delete("/delete-topic/{topic_id}")
def delete_topic(topic_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
       
        cursor.execute("DELETE f FROM Feedback f JOIN Evaluations ev ON f.evaluation_id = ev.evaluation_id JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE g FROM Grades g JOIN Evaluations ev ON g.evaluation_id = ev.evaluation_id JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE ev FROM Evaluations ev JOIN Essays e ON ev.essay_id = e.essay_id WHERE e.topic_id = %s", (topic_id,))
        cursor.execute("DELETE FROM Essays WHERE topic_id = %s", (topic_id,))
        cursor.execute("DELETE FROM Topics WHERE topic_id = %s", (topic_id,))
        db.commit()
        return {"message": "Topic deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()