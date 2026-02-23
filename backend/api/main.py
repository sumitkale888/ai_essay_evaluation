from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import LoginRequest, TopicCreate, EssaySubmission
from .database import get_db_connection
from pyswip import Prolog
import os
import re

app = FastAPI()

# Enable CORS for Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PROLOG INITIALIZATION ---
prolog = Prolog()
# Get absolute path to your main_brain.pl
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")

try:
    prolog.consult(prolog_path)
    print(f"Prolog consulted successfully from: {prolog_path}")
except Exception as e:
    print(f"Error consulting Prolog: {e}")

# --- AUTHENTICATION ---
@app.post("/login")
def login(request: LoginRequest):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, role, name FROM Users WHERE email = %s AND password = %s", 
                       (request.email, request.password))
        user = cursor.fetchone()
        if user:
            return {"message": "Login successful", "user_id": user["user_id"], "role": user["role"], "name": user["name"]}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        db.close()

# --- TEACHER ROUTE: Add Essay Topic ---
@app.post("/add-topic")
def add_topic(topic: TopicCreate):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        query = "INSERT INTO Topics (title, description, keywords, teacher_id) VALUES (%s, %s, %s, %s)"
        values = (topic.title, topic.description, topic.keywords, topic.teacher_id)
        cursor.execute(query, values)
        db.commit()
        return {"message": "Topic added successfully", "topic_id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- STUDENT ROUTE: Submit and Evaluate Essay ---
@app.post("/submit-essay")
def submit_essay(submission: EssaySubmission):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        # 1. Fetch Topic Keywords
        cursor.execute("SELECT keywords FROM Topics WHERE topic_id = %s", (submission.topic_id,))
        topic_row = cursor.fetchone()

        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Handle NULL or empty keywords safely
        raw_keywords = topic_row.get('keywords') or "essay,writing,analysis"
        kw_list = [f"'{k.strip().lower()}'" for k in raw_keywords.split(',') if k.strip()]
        prolog_keywords = "[" + ",".join(kw_list) + "]"
        
        # 2. Sanitize and Process Essay Text for Prolog
        # Remove special characters and specifically single quotes which break Prolog syntax
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", submission.essay_text).lower()
        words = clean_text.split()
        word_count = len(words)
        
        if word_count == 0:
            return {"status": "error", "message": "Essay is empty"}

        prolog_text_list = "[" + ",".join([f"'{w}'" for w in words]) + "]"
        
        # 3. Query Prolog
        # evaluate_essay(TextList, Keywords, Score, Feedback)
        query_str = f"evaluate_essay({prolog_text_list}, {prolog_keywords}, Score, Feedback)"
        result = list(prolog.query(query_str))
        
        if result:
            score = result[0]["Score"]
            feedback_raw = result[0]["Feedback"]
            
            # Handle Prolog's varied return types (bytes or lists of codes)
            if isinstance(feedback_raw, bytes):
                feedback = feedback_raw.decode("utf-8")
            elif isinstance(feedback_raw, list):
                # Convert list of char codes to string
                feedback = "".join([chr(c) for c in feedback_raw])
            else:
                feedback = str(feedback_raw)
        else:
            score = 2
            feedback = "The essay does not follow the required structural patterns (Intro/Conclusion)."

        # 4. Save Everything to DB
        # Save the actual Essay
        cursor.execute(
            "INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
            (submission.student_id, submission.topic_id, submission.essay_text)
        )
        essay_id = cursor.lastrowid
        
        # Create Evaluation Entry
        cursor.execute("INSERT INTO Evaluations (essay_id) VALUES (%s)", (essay_id,))
        eval_id = cursor.lastrowid
        
        # Store Grade and Feedback
        cursor.execute("INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)", (eval_id, score))
        cursor.execute("INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)", (eval_id, feedback))
        
        db.commit()
        
        return {
            "status": "success",
            "score": score,
            "feedback": feedback,
            "word_count": word_count,
            "essay_id": essay_id
        }

    except Exception as e:
        db.rollback()
        print(f"Error during submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- UTILITY: Get Topics for Dropdown ---
@app.get("/get-topics")
def get_topics():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT topic_id, title, description, keywords FROM Topics")
        return cursor.fetchall()
    finally:
        db.close()