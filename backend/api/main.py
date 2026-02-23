from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import LoginRequest, TopicCreate, EssaySubmission
from .database import get_db_connection
from pyswip import Prolog
import os

app = FastAPI()

# Enable CORS so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prolog
prolog = Prolog()
prolog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prolog", "main_brain.pl")
# Ensure the path works on Windows for Prolog
prolog.consult(prolog_path.replace("\\", "/"))

# --- AUTHENTICATION ---
@app.post("/login")
def login(request: LoginRequest):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, role, name FROM Users WHERE email = %s AND password = %s", (request.email, request.password))
    user = cursor.fetchone()
    db.close()
    
    if user:
        return {"message": "Login successful", "user_id": user["user_id"], "role": user["role"], "name": user["name"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- TEACHER ROUTE: Upload Essay Topic ---
@app.post("/add-topic")
def add_topic(topic: TopicCreate):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Topics (title, description) VALUES (%s, %s)", (topic.title, topic.description))
        db.commit()
        return {"message": "Topic added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- STUDENT ROUTE: Submit and Evaluate Essay ---
# Update the submit-essay logic to handle keywords
@app.post("/submit-essay")
def submit_essay(submission: EssaySubmission):
    # 1. Fetch Topic Keywords from DB
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT keywords FROM Topics WHERE topic_id = %s", (submission.topic_id,))
    topic = cursor.fetchone()
    
    # Convert keywords string "env,pollution,nature" to Prolog list ['env','pollution','nature']
    kw_list = [f"'{k.strip()}'" for k in topic['keywords'].split(',')]
    prolog_keywords = "[" + ",".join(kw_list) + "]"
    
    # 2. Process Essay Text
    words = submission.essay_text.lower().replace(".", "").replace(",", "").split()
    prolog_text_list = "[" + ",".join([f"'{w}'" for w in words]) + "]"
    
    # 3. Query Prolog with BOTH Essay and Keywords
    query = f"evaluate_essay({prolog_text_list}, {prolog_keywords}, Score, Feedback)"
    result = list(prolog.query(query))
    
    # ... rest of the code to save Score and Feedback ...
    
    if result:
        score = result[0]["Score"]
        # Prolog returns strings as bytes/lists; convert to python string
        feedback_raw = result[0]["Feedback"]
        feedback = feedback_raw.decode("utf-8") if isinstance(feedback_raw, bytes) else str(feedback_raw)
    else:
        score = 0
        feedback = "Prolog engine could not evaluate."

    # 3. Save to Database
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Save Essay
        cursor.execute(
            "INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
            (submission.student_id, submission.topic_id, submission.essay_text)
        )
        essay_id = cursor.lastrowid
        
        # Save Evaluation & Grade
        cursor.execute("INSERT INTO Evaluations (essay_id) VALUES (%s)", (essay_id,))
        eval_id = cursor.lastrowid
        cursor.execute("INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)", (eval_id, score))
        cursor.execute("INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)", (eval_id, feedback))
        
        db.commit()
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

# Helper to get topics for the student dropdown
@app.get("/get-topics")
def get_topics():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Topics")
    topics = cursor.fetchall()
    db.close()
    return topics