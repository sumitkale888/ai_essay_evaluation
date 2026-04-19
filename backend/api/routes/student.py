from fastapi import APIRouter, HTTPException
from ..models import EssaySubmission, ClassroomJoinRequest
from ..core.database import get_db_connection
from ..core.evaluation import EssayEvaluator
from ..core.cache import cache_manager, student_topics_cache_key
from ..core.submission_pipeline import process_submission
from pyswip import Prolog
import os

router = APIRouter()
prolog = Prolog()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")

try:
    prolog.consult(prolog_path)
    print(f"Prolog consulted successfully from: {prolog_path}")
except Exception as e:
    print(f"Error consulting Prolog: {e}")

# Initialize essay evaluator
evaluator = EssayEvaluator(prolog)


@router.post("/join-classroom")
def join_classroom(payload: ClassroomJoinRequest):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        join_code = payload.join_code.strip().upper()
        cursor.execute(
            """
            SELECT classroom_id, classroom_name, subject_name
            FROM Classrooms
            WHERE join_code = %s
            """,
            (join_code,)
        )
        classroom = cursor.fetchone()
        if not classroom:
            raise HTTPException(status_code=404, detail="Invalid classroom code")

        cursor.execute(
            """
            INSERT INTO ClassroomMembers (classroom_id, student_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE joined_at = CURRENT_TIMESTAMP
            """,
            (classroom["classroom_id"], payload.student_id)
        )
        db.commit()
        cache_manager.delete_pattern(f"student:topics:{payload.student_id}:*")
        return {
            "message": "Classroom joined successfully",
            "classroom": classroom,
        }
    finally:
        db.close()


@router.get("/classrooms/{student_id}")
def get_student_classrooms(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT c.classroom_id, c.classroom_name, c.subject_name, c.join_code,
                   c.created_at, u.name AS teacher_name
            FROM ClassroomMembers cm
            JOIN Classrooms c ON c.classroom_id = cm.classroom_id
            LEFT JOIN Users u ON u.user_id = c.teacher_id
            WHERE cm.student_id = %s
            ORDER BY c.created_at DESC
            """,
            (student_id,)
        )
        return cursor.fetchall()
    finally:
        db.close()


@router.get("/get-topics-student/{student_id}")
def get_topics_student(student_id: int, classroom_id: int | None = None):
    cache_key = student_topics_cache_key(student_id, classroom_id)
    cached = cache_manager.get_json(cache_key)
    if cached is not None:
        return cached

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        base_query = """
            SELECT t.topic_id, t.title, t.description, t.classroom_id,
                   c.classroom_name, c.subject_name
            FROM Topics t
            JOIN ClassroomMembers cm ON cm.classroom_id = t.classroom_id
            LEFT JOIN Classrooms c ON c.classroom_id = t.classroom_id
            WHERE cm.student_id = %s
        """
        params = [student_id]

        if classroom_id is not None:
            base_query += " AND t.classroom_id = %s"
            params.append(classroom_id)

        base_query += " ORDER BY t.topic_id DESC"
        cursor.execute(base_query, tuple(params))
        rows = cursor.fetchall()
        cache_manager.set_json(cache_key, rows, ttl_seconds=300)
        return rows
    finally:
        db.close()


@router.get("/student-history/{student_id}")
def get_student_history(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT t.title, g.final_score, f.feedback_text, e.submission_date, e.essay_id,
                   tr.teacher_score, tr.teacher_feedback, tr.reviewed_at, tu.name AS teacher_name
            FROM Essays e
            JOIN Topics t ON e.topic_id = t.topic_id
            LEFT JOIN Evaluations ev ON e.essay_id = ev.essay_id
            LEFT JOIN Grades g ON ev.evaluation_id = g.evaluation_id
            LEFT JOIN Feedback f ON ev.evaluation_id = f.evaluation_id
            LEFT JOIN TeacherReviews tr ON tr.essay_id = e.essay_id
            LEFT JOIN Users tu ON tu.user_id = tr.teacher_id
            WHERE e.student_id = %s
            ORDER BY e.submission_date DESC
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/submit")
@router.post("/submit-essay")
def submit_essay(submission: EssaySubmission):
    try:
        return process_submission(
            student_id=submission.student_id,
            topic_id=submission.topic_id,
            essay_text=submission.essay_text,
            evaluator=evaluator,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in submit_essay: {e}")
        raise HTTPException(status_code=500, detail=str(e))