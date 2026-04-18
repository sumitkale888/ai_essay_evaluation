from fastapi import APIRouter, HTTPException
from ..models import EssaySubmission, ClassroomJoinRequest
from ..core.database import get_db_connection
from ..core.evaluation import EssayEvaluator
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
        return cursor.fetchall()
    finally:
        db.close()


@router.get("/student-history/{student_id}")
def get_student_history(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT t.title, g.final_score, f.feedback_text, e.submission_date, e.essay_id
            FROM Essays e
            JOIN Topics t ON e.topic_id = t.topic_id
            LEFT JOIN Evaluations ev ON e.essay_id = ev.essay_id
            LEFT JOIN Grades g ON ev.evaluation_id = g.evaluation_id
            LEFT JOIN Feedback f ON ev.evaluation_id = f.evaluation_id
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
    """
    Submit and evaluate an essay with plagiarism detection.
    
    Flow:
    1. Check if topic exists
    2. Evaluate content quality via Prolog
    3. Check plagiarism against previous submissions
    4. Apply plagiarism penalty to base score
    5. Store results in database
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Verify topic exists
        cursor.execute("SELECT keywords, classroom_id FROM Topics WHERE topic_id = %s", (submission.topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")

        classroom_id = topic_row.get("classroom_id")
        if classroom_id is not None:
            cursor.execute(
                """
                SELECT 1 FROM ClassroomMembers
                WHERE classroom_id = %s AND student_id = %s
                """,
                (classroom_id, submission.student_id)
            )
            member = cursor.fetchone()
            if not member:
                raise HTTPException(status_code=403, detail="Student is not enrolled in this classroom")
        
        keywords = topic_row.get('keywords') or ""
        
        # 2. Run complete evaluation (content quality + plagiarism)
        evaluation_result = evaluator.evaluate_essay(
            essay_text=submission.essay_text,
            keywords=keywords,
            topic_id=submission.topic_id,
            student_id=submission.student_id
        )
        
        # If essay is too short, return early
        if evaluation_result['status'] == 'error':
            return evaluation_result
        
        # 3. Save essay to database
        cursor.execute(
            "INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
            (submission.student_id, submission.topic_id, submission.essay_text)
        )
        essay_id = cursor.lastrowid
        
        # 4. Save evaluation results
        cursor.execute(
            "INSERT INTO Evaluations (essay_id) VALUES (%s)",
            (essay_id,)
        )
        eval_id = cursor.lastrowid
        
        # 5. Store grade (with plagiarism penalty applied)
        cursor.execute(
            "INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)",
            (eval_id, evaluation_result['score'])
        )
        
        # 6. Store feedback
        combined_feedback = f"{evaluation_result['feedback']}\n\n{evaluation_result['plagiarism_feedback']}"
        cursor.execute(
            "INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)",
            (eval_id, combined_feedback)
        )
        
        # 7. Store plagiarism metadata if exists (optional - for future detailed analysis)
        # You can add a new PlagiarismCheck table if needed
        
        db.commit()
        
        # 8. Return comprehensive evaluation result
        return {
            "status": "success",
            "score": evaluation_result['score'],
            "base_score": evaluation_result['base_score'],
            "plagiarism": evaluation_result['plagiarism'],
            "plagiarism_level": evaluation_result['plagiarism_level'],
            "feedback": evaluation_result['feedback'],
            "plagiarism_feedback": evaluation_result['plagiarism_feedback'],
            "word_count": evaluation_result['word_count'],
            "is_plagiarized": evaluation_result['is_plagiarized'],
            "rubric_breakdown": evaluation_result.get('rubric_breakdown', {}),
            "improvement_tips": evaluation_result.get('improvement_tips', []),
            "score_band": evaluation_result.get('score_band', 'needs improvement'),
            "originality_label": evaluation_result.get('originality_label', 'highly original'),
            "comparison_count": len(evaluation_result.get('detailed_comparisons', [])),
            "essay_id": essay_id
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in submit_essay: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()