from fastapi import APIRouter, HTTPException
from ..models import TopicCreate
from ..core.database import get_db_connection
from ..core.plagiarism import PlagiarismDetector

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