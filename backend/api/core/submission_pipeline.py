from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException

from .database import get_db_connection


def process_submission(student_id: int, topic_id: int, essay_text: str, evaluator) -> Dict[str, Any]:
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT keywords, classroom_id FROM Topics WHERE topic_id = %s", (topic_id,))
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
                (classroom_id, student_id),
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="Student is not enrolled in this classroom")

        keywords = topic_row.get("keywords") or ""
        evaluation_result = evaluator.evaluate_essay(
            essay_text=essay_text,
            keywords=keywords,
            topic_id=topic_id,
            student_id=student_id,
        )

        if evaluation_result.get("status") == "error":
            return evaluation_result

        cursor.execute(
            "INSERT INTO Essays (student_id, topic_id, essay_text) VALUES (%s, %s, %s)",
            (student_id, topic_id, essay_text),
        )
        essay_id = cursor.lastrowid

        cursor.execute("INSERT INTO Evaluations (essay_id) VALUES (%s)", (essay_id,))
        eval_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Grades (evaluation_id, final_score) VALUES (%s, %s)",
            (eval_id, evaluation_result["score"]),
        )

        combined_feedback = f"{evaluation_result['feedback']}\n\n{evaluation_result['plagiarism_feedback']}"
        cursor.execute(
            "INSERT INTO Feedback (evaluation_id, feedback_text) VALUES (%s, %s)",
            (eval_id, combined_feedback),
        )

        db.commit()

        return {
            "status": "success",
            "score": evaluation_result["score"],
            "base_score": evaluation_result["base_score"],
            "plagiarism": evaluation_result["plagiarism"],
            "plagiarism_level": evaluation_result["plagiarism_level"],
            "feedback": evaluation_result["feedback"],
            "plagiarism_feedback": evaluation_result["plagiarism_feedback"],
            "word_count": evaluation_result["word_count"],
            "is_plagiarized": evaluation_result["is_plagiarized"],
            "rubric_breakdown": evaluation_result.get("rubric_breakdown", {}),
            "improvement_tips": evaluation_result.get("improvement_tips", []),
            "score_band": evaluation_result.get("score_band", "needs improvement"),
            "originality_label": evaluation_result.get("originality_label", "highly original"),
            "comparison_count": len(evaluation_result.get("detailed_comparisons", [])),
            "essay_id": essay_id,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
