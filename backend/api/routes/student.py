from fastapi import APIRouter, HTTPException
from ..models import EssaySubmission
from ..core.database import get_db_connection
from pyswip import Prolog
import os, re

router = APIRouter()
prolog = Prolog()

# --- PROLOG INITIALIZATION ---
# Base directory setup to find the prolog folder correctly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")

try:
    prolog.consult(prolog_path)
    print(f"Prolog consulted successfully from: {prolog_path}")
except Exception as e:
    print(f"Error consulting Prolog: {e}")

# --- GET AVAILABLE TOPICS ---
@router.get("/get-topics-student")
def get_topics_student():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT topic_id, title, description FROM Topics")
        return cursor.fetchall()
    finally:
        db.close()

# --- GET STUDENT PERFORMANCE HISTORY ---
@router.get("/student-history/{student_id}")
def get_student_history(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT t.title, g.final_score, f.feedback_text, e.submission_date
            FROM Essays e
            JOIN Topics t ON e.topic_id = t.topic_id
            JOIN Evaluations ev ON e.essay_id = ev.essay_id
            JOIN Grades g ON ev.evaluation_id = g.evaluation_id
            JOIN Feedback f ON ev.evaluation_id = f.evaluation_id
            WHERE e.student_id = %s
            ORDER BY e.submission_date DESC
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- SUBMIT AND EVALUATE ESSAY ---
@router.post("/submit-essay")
def submit_essay(submission: EssaySubmission):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Fetch Keywords for the selected topic
        cursor.execute("SELECT keywords FROM Topics WHERE topic_id = %s", (submission.topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row: 
            raise HTTPException(status_code=404, detail="Topic not found")

        # 2. Prepare Data for Prolog
        raw_keywords = topic_row.get('keywords') or ""
        kw_list = [f"'{k.strip().lower()}'" for k in raw_keywords.split(',') if k.strip()]
        prolog_keywords = "[" + ",".join(kw_list) + "]"
        
        # Clean text and calculate word count
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", submission.essay_text).lower()
        words = clean_text.split()
        word_count = len(words) # Calculated for the frontend

        if word_count < 10: 
            return {"status": "error", "message": "Essay too short (minimum 10 words)."}

        # 3. Query Prolog Brain
        prolog_text_list = "[" + ",".join([f"'{w}'" for w in words]) + "]"
        query_str = f"evaluate_essay({prolog_text_list}, {prolog_keywords}, Score, Feedback)"
        result = list(prolog.query(query_str))
        
        if result:
            score = result[0]["Score"]
            feedback_raw = result[0]["Feedback"]
            
            # Handling different PySwip return types (Bytes, List, or String)
            if isinstance(feedback_raw, bytes):
                feedback = feedback_raw.decode("utf-8")
            elif isinstance(feedback_raw, list):
                feedback = "".join([chr(c) for c in feedback_raw])
            else:
                feedback = str(feedback_raw)
        else:
            score = 0
            feedback = "The essay structure or relevance did not meet the evaluation criteria."

        # 4. Save Submission and Results to Database
        # Save Essay
        cursor.execute("INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
                       (submission.student_id, submission.topic_id, submission.essay_text))
        essay_id = cursor.lastrowid
        
        # Save Evaluation link
        cursor.execute("INSERT INTO Evaluations (essay_id) VALUES (%s)", (essay_id,))
        eval_id = cursor.lastrowid
        
        # Save Grade and Feedback
        cursor.execute("INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)", (eval_id, score))
        cursor.execute("INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)", (eval_id, feedback))
        
        db.commit()
        
        # Returning everything the React ResultView needs
        return {
            "status": "success", 
            "score": score, 
            "feedback": feedback, 
            "word_count": word_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()