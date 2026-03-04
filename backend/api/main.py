from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import LoginRequest, TopicCreate, EssaySubmission, RegisterRequest
from .database import get_db_connection
from pyswip import Prolog
import os
import re
from passlib.context import CryptContext

# --- SECURITY SETUP: ARGON2 ---
# Argon2 is the winner of the Password Hashing Competition and 
# usually installs on Windows without needing Visual Studio.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PROLOG INITIALIZATION ---
prolog = Prolog()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prolog_path = os.path.join(BASE_DIR, "prolog", "main_brain.pl").replace("\\", "/")

try:
    prolog.consult(prolog_path)
    print(f"Prolog consulted successfully from: {prolog_path}")
except Exception as e:
    print(f"Error consulting Prolog: {e}")

# --- AUTHENTICATION: REGISTER ---
@app.post("/register")
def register(request: RegisterRequest):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (request.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash with Argon2
        hashed_password = get_password_hash(request.password)
        
        query = "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        values = (request.name, request.email, hashed_password, request.role.lower())
        
        cursor.execute(query, values)
        db.commit()
        return {"message": "User created successfully", "role": request.role.lower()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- AUTHENTICATION: LOGIN ---
@app.post("/login")
def login(request: LoginRequest):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, role, name, password FROM Users WHERE email = %s", (request.email,))
        user = cursor.fetchone()

        if user and verify_password(request.password, user["password"]):
            return {
                "message": "Login successful", 
                "user_id": user["user_id"], 
                "role": user["role"], 
                "name": user["name"]
            }
        
        raise HTTPException(status_code=401, detail="Invalid email or password")
    finally:
        db.close()

# ... (Keep the rest of your teacher and student routes as they were)

# --- TEACHER ROUTES ---
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
    finally:
        db.close()

@app.get("/get-topics-teacher")
def get_topics_teacher():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT topic_id, title, description, keywords FROM Topics")
        return cursor.fetchall()
    finally:
        db.close()

@app.get("/topic-submissions/{topic_id}")
def get_topic_submissions(topic_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT u.name, g.final_score 
            FROM Users u
            JOIN Essays e ON u.user_id = e.student_id
            JOIN Evaluations ev ON e.essay_id = ev.essay_id
            JOIN Grades g ON ev.evaluation_id = g.evaluation_id
            WHERE e.topic_id = %s
        """
        cursor.execute(query, (topic_id,))
        return cursor.fetchall()
    finally:
        db.close()

# --- STUDENT ROUTES ---
@app.get("/get-topics-student")
def get_topics_student():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT topic_id, title, description FROM Topics")
        return cursor.fetchall()
    finally:
        db.close()

@app.get("/student-history/{student_id}")
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
    finally:
        db.close()

@app.post("/submit-essay")
def submit_essay(submission: EssaySubmission):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT keywords FROM Topics WHERE topic_id = %s", (submission.topic_id,))
        topic_row = cursor.fetchone()
        if not topic_row:
            raise HTTPException(status_code=404, detail="Topic not found")

        raw_keywords = topic_row.get('keywords') or "essay,writing,analysis"
        kw_list = [f"'{k.strip().lower()}'" for k in raw_keywords.split(',') if k.strip()]
        prolog_keywords = "[" + ",".join(kw_list) + "]"
        
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", submission.essay_text).lower()
        words = clean_text.split()
        
        if len(words) == 0:
            return {"status": "error", "message": "Essay is empty"}

        prolog_text_list = "[" + ",".join([f"'{w}'" for w in words]) + "]"
        query_str = f"evaluate_essay({prolog_text_list}, {prolog_keywords}, Score, Feedback)"
        result = list(prolog.query(query_str))
        
        if result:
            score = result[0]["Score"]
            feedback_raw = result[0]["Feedback"]
            feedback = feedback_raw.decode("utf-8") if isinstance(feedback_raw, bytes) else (
                "".join([chr(c) for c in feedback_raw]) if isinstance(feedback_raw, list) else str(feedback_raw)
            )
        else:
            score = 2
            feedback = "The essay does not follow the required structural patterns (Intro/Conclusion)."

        cursor.execute("INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
                       (submission.student_id, submission.topic_id, submission.essay_text))
        essay_id = cursor.lastrowid
        cursor.execute("INSERT INTO Evaluations (essay_id) VALUES (%s)", (essay_id,))
        eval_id = cursor.lastrowid
        cursor.execute("INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)", (eval_id, score))
        cursor.execute("INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)", (eval_id, feedback))
        db.commit()
        
        return {"status": "success", "score": score, "feedback": feedback, "word_count": len(words), "essay_id": essay_id}
    finally:
        db.close()