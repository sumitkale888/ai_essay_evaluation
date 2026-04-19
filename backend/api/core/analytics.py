from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

from .database import get_db_connection
from .plagiarism import PlagiarismDetector


POSITIVE_HINTS = {
    "argument": ["strong argumentation"],
    "coherence": ["good coherence"],
    "vocabulary": ["good vocabulary"],
    "sentence": ["balanced sentence structure"],
    "introduction": ["strong introduction"],
    "conclusion": ["strong conclusion"],
    "logic": ["reasoning stays consistent", "logical"],
    "facts": ["facts", "examples", "data"],
    "relevance": ["highly relevant", "topic keywords are present"],
}

NEGATIVE_HINTS = {
    "argument": ["clearer claims", "supporting evidence"],
    "coherence": ["improve coherence", "transition words"],
    "vocabulary": ["improve vocabulary", "academic vocabulary"],
    "sentence": ["short or overly long", "sentence lengths"],
    "introduction": ["weak introduction", "stronger introduction"],
    "conclusion": ["weak conclusion", "clear conclusion"],
    "logic": ["contradiction", "reasoning stays consistent"],
    "facts": ["evidence is limited", "concrete facts"],
    "relevance": ["topic relevance is limited", "increase relevance"],
}


MISTAKE_BUCKETS = {
    "argument": ["claims", "argument", "evidence", "supporting"],
    "coherence": ["coherence", "flow", "transition"],
    "vocabulary": ["vocabulary", "word choice", "academic"],
    "sentence": ["sentence", "clarity", "length"],
    "introduction": ["introduction"],
    "conclusion": ["conclusion"],
    "logic": ["contradiction", "logic", "reasoning"],
    "facts": ["fact", "examples", "data", "credibility"],
    "relevance": ["relevance", "topic keywords", "off-topic"],
    "plagiarism": ["plagiarism", "similarity", "originality", "citations"],
}


DIMENSIONS = [
    "argument",
    "coherence",
    "vocabulary",
    "sentence",
    "introduction",
    "conclusion",
    "logic",
    "facts",
    "relevance",
]


class TeacherAnalyticsService:
    def __init__(self) -> None:
        self.detector = PlagiarismDetector()

    def get_teacher_analytics(self, teacher_id: int) -> Dict[str, Any]:
        rows = self._fetch_teacher_rows(teacher_id)

        if not rows:
            return {
                "summary": {
                    "classroom_count": 0,
                    "student_count": 0,
                    "submission_count": 0,
                    "average_class_score": 0.0,
                    "high_plagiarism_rate": 0.0,
                },
                "classroom_analytics": [],
                "common_mistakes": [],
                "plagiarism_trends": [],
                "improvement_trends": [],
                "student_profiles": [],
            }

        submission_count = len(rows)
        student_ids = {row["student_id"] for row in rows}
        classroom_ids = {row["classroom_id"] for row in rows if row.get("classroom_id") is not None}

        effective_scores = [self._effective_score(row) for row in rows]
        average_class_score = round(sum(effective_scores) / submission_count, 2)

        plagiarism_map = self._compute_plagiarism_map(rows)
        high_plagiarism_count = sum(1 for essay_id, pct in plagiarism_map.items() if pct >= 50)
        high_plagiarism_rate = round((high_plagiarism_count / submission_count) * 100, 2)

        common_mistakes = self._common_mistakes(rows)
        classroom_analytics = self._classroom_analytics(rows, plagiarism_map)
        improvement_trends = self._score_trends(rows)
        plagiarism_trends = self._plagiarism_trends(rows, plagiarism_map)
        student_profiles = self._student_profiles(rows, plagiarism_map)

        return {
            "summary": {
                "classroom_count": len(classroom_ids),
                "student_count": len(student_ids),
                "submission_count": submission_count,
                "average_class_score": average_class_score,
                "high_plagiarism_rate": high_plagiarism_rate,
            },
            "classroom_analytics": classroom_analytics,
            "common_mistakes": common_mistakes,
            "plagiarism_trends": plagiarism_trends,
            "improvement_trends": improvement_trends,
            "student_profiles": student_profiles,
        }

    def _fetch_teacher_rows(self, teacher_id: int) -> List[Dict[str, Any]]:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    e.essay_id,
                    e.student_id,
                    u.name AS student_name,
                    e.topic_id,
                    t.classroom_id,
                    c.classroom_name,
                    e.essay_text,
                    e.submission_date,
                    g.final_score,
                    tr.teacher_score,
                    f.feedback_text
                FROM Essays e
                JOIN Topics t ON t.topic_id = e.topic_id
                JOIN Users u ON u.user_id = e.student_id
                LEFT JOIN Classrooms c ON c.classroom_id = t.classroom_id
                LEFT JOIN Evaluations ev ON ev.essay_id = e.essay_id
                LEFT JOIN Grades g ON g.evaluation_id = ev.evaluation_id
                LEFT JOIN Feedback f ON f.evaluation_id = ev.evaluation_id
                LEFT JOIN TeacherReviews tr ON tr.essay_id = e.essay_id
                WHERE t.teacher_id = %s
                ORDER BY e.submission_date ASC
                """,
                (teacher_id,),
            )
            return cursor.fetchall()
        finally:
            db.close()

    def _effective_score(self, row: Dict[str, Any]) -> float:
        teacher_score = row.get("teacher_score")
        if teacher_score is not None:
            return float(teacher_score)

        final_score = float(row.get("final_score") or 0.0)
        # Older rows may contain score in 0-10 scale. Normalize to 0-100.
        return final_score if final_score > 10 else final_score * 10

    def _feedback_to_heatmap(self, feedback_text: str) -> Dict[str, int]:
        text = (feedback_text or "").lower()
        scores: Dict[str, int] = {dim: 6 for dim in DIMENSIONS}

        for dim, hints in POSITIVE_HINTS.items():
            if any(hint in text for hint in hints):
                scores[dim] = 8

        for dim, hints in NEGATIVE_HINTS.items():
            if any(hint in text for hint in hints):
                scores[dim] = 4

        return scores

    def _common_mistakes(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        counts = defaultdict(int)

        for row in rows:
            text = (row.get("feedback_text") or "").lower()
            for bucket, terms in MISTAKE_BUCKETS.items():
                if any(term in text for term in terms):
                    counts[bucket] += 1

        ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        return [{"category": key, "count": value} for key, value in ordered[:6]]

    def _compute_plagiarism_map(self, rows: List[Dict[str, Any]]) -> Dict[int, float]:
        by_classroom = defaultdict(list)
        for row in rows:
            by_classroom[row.get("classroom_id")].append(row)

        result: Dict[int, float] = {}

        for class_rows in by_classroom.values():
            for row in class_rows:
                max_similarity = 0.0
                for candidate in class_rows:
                    if candidate["essay_id"] == row["essay_id"]:
                        continue
                    similarity = self.detector.calculate_similarity(
                        row.get("essay_text") or "",
                        candidate.get("essay_text") or "",
                    )
                    if similarity > max_similarity:
                        max_similarity = similarity

                result[row["essay_id"]] = round(max_similarity * 100, 2)

        return result

    def _classroom_analytics(
        self,
        rows: List[Dict[str, Any]],
        plagiarism_map: Dict[int, float],
    ) -> List[Dict[str, Any]]:
        by_classroom = defaultdict(list)
        for row in rows:
            by_classroom[row.get("classroom_id")].append(row)

        analytics = []
        for classroom_id, class_rows in by_classroom.items():
            scores = [self._effective_score(row) for row in class_rows]
            avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
            student_count = len({row["student_id"] for row in class_rows})
            plagiarized = [row for row in class_rows if plagiarism_map.get(row["essay_id"], 0.0) >= 50]
            plagiarism_rate = round((len(plagiarized) / len(class_rows)) * 100, 2) if class_rows else 0.0

            analytics.append(
                {
                    "classroom_id": classroom_id,
                    "classroom_name": class_rows[0].get("classroom_name") or "Unassigned",
                    "student_count": student_count,
                    "submission_count": len(class_rows),
                    "average_score": avg_score,
                    "plagiarism_rate": plagiarism_rate,
                }
            )

        analytics.sort(key=lambda row: row["average_score"], reverse=True)
        return analytics

    def _month_key(self, dt_value: Any) -> str:
        if isinstance(dt_value, datetime):
            return dt_value.strftime("%Y-%m")
        try:
            parsed = datetime.fromisoformat(str(dt_value))
            return parsed.strftime("%Y-%m")
        except ValueError:
            return str(dt_value)[:7]

    def _score_trends(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        monthly_scores = defaultdict(list)

        for row in rows:
            monthly_scores[self._month_key(row["submission_date"])].append(self._effective_score(row))

        trends = []
        for month in sorted(monthly_scores.keys()):
            scores = monthly_scores[month]
            trends.append({"month": month, "average_score": round(sum(scores) / len(scores), 2)})

        return trends

    def _plagiarism_trends(
        self,
        rows: List[Dict[str, Any]],
        plagiarism_map: Dict[int, float],
    ) -> List[Dict[str, Any]]:
        monthly = defaultdict(list)

        for row in rows:
            month = self._month_key(row["submission_date"])
            monthly[month].append(plagiarism_map.get(row["essay_id"], 0.0))

        trends = []
        for month in sorted(monthly.keys()):
            values = monthly[month]
            high = [value for value in values if value >= 50]
            trends.append(
                {
                    "month": month,
                    "avg_similarity": round(sum(values) / len(values), 2),
                    "high_risk_rate": round((len(high) / len(values)) * 100, 2),
                }
            )

        return trends

    def _student_profiles(
        self,
        rows: List[Dict[str, Any]],
        plagiarism_map: Dict[int, float],
    ) -> List[Dict[str, Any]]:
        by_student = defaultdict(list)
        for row in rows:
            by_student[row["student_id"]].append(row)

        profiles = []
        for student_id, entries in by_student.items():
            entries.sort(key=lambda row: row["submission_date"])
            scores = [self._effective_score(row) for row in entries]
            avg_score = round(sum(scores) / len(scores), 2)
            trend_delta = round(scores[-1] - scores[0], 2) if len(scores) > 1 else 0.0

            heatmap_accumulator = defaultdict(list)
            for row in entries:
                dimension_scores = self._feedback_to_heatmap(row.get("feedback_text") or "")
                for dim, score in dimension_scores.items():
                    heatmap_accumulator[dim].append(score)

            heatmap = {
                dim: round(sum(values) / len(values), 1) if values else 0.0
                for dim, values in heatmap_accumulator.items()
            }

            ranked = sorted(heatmap.items(), key=lambda item: item[1], reverse=True)
            strengths = [key for key, _ in ranked[:3]]
            weaknesses = [key for key, _ in ranked[-3:]]

            student_plagiarism = [plagiarism_map.get(row["essay_id"], 0.0) for row in entries]

            profiles.append(
                {
                    "student_id": student_id,
                    "student_name": entries[0].get("student_name") or f"Student {student_id}",
                    "submission_count": len(entries),
                    "average_score": avg_score,
                    "trend_delta": trend_delta,
                    "avg_similarity": round(sum(student_plagiarism) / len(student_plagiarism), 2),
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "heatmap": heatmap,
                }
            )

        profiles.sort(key=lambda row: row["average_score"], reverse=True)
        return profiles
