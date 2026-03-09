from fastapi import APIRouter, HTTPException
from ..models import TopicCreate
from ..core.database import get_db_connection

router = APIRouter()

@router.post("/add-topic")
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

@router.get("/get-topics-teacher")
def get_topics_teacher():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT topic_id, title, description, keywords FROM Topics")
        return cursor.fetchall()
    finally:
        db.close()

@router.get("/topic-submissions/{topic_id}")
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

@router.delete("/delete-topic/{topic_id}")
def delete_topic(topic_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Cascade delete simulation
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