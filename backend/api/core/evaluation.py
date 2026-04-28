"""
Essay Evaluation Module
Integrates plagiarism detection with content quality scoring and Prolog-based evaluation
"""

from .plagiarism import PlagiarismDetector
from ..core.database import get_db_connection
from ..core.cache import cache_manager, evaluation_cache_key
from pyswip import Prolog
import re
import hashlib
from typing import Tuple, Dict, Any


class EssayEvaluator:
    """
    Evaluates essays based on:
    1. Content quality (via Prolog rules)
    2. Grammar/structure
    3. Plagiarism detection
    4. Final score with plagiarism penalty applied
    """
    
    def __init__(self, prolog_instance: Prolog):
        self.plagiarism_detector = PlagiarismDetector()
        self.prolog = prolog_instance
    
    def get_previous_essays_for_topic(self, topic_id: int, exclude_student_id: int = None) -> list:
        """
        Retrieve all previous essay submissions for a topic.
        
        Args:
            topic_id: Topic ID to search
            exclude_student_id: Student ID to exclude from results (optional)
            
        Returns:
            List of essay texts
        """
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        try:
            if exclude_student_id:
                query = """
                    SELECT essay_text FROM Essays 
                    WHERE topic_id = %s AND student_id != %s
                    ORDER BY submission_date ASC
                """
                cursor.execute(query, (topic_id, exclude_student_id))
            else:
                query = """
                    SELECT essay_text FROM Essays 
                    WHERE topic_id = %s
                    ORDER BY submission_date ASC
                """
                cursor.execute(query, (topic_id,))
            
            results = cursor.fetchall()
            return [row['essay_text'] for row in results]
        finally:
            db.close()
    
    def evaluate_essay(self, essay_text: str, keywords: str, topic_id: int, student_id: int) -> Dict[str, Any]:
        """
        Complete essay evaluation including plagiarism and content quality.
        
        Args:
            essay_text: Student's essay text
            keywords: Topic keywords (comma-separated)
            topic_id: Topic ID for plagiarism comparison
            student_id: Student ID
            
        Returns:
            Dictionary with score, plagiarism, feedback, etc.
        """
        
        # 1. Prepare text
        word_count = len(essay_text.split())
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", essay_text).lower()
        words = clean_text.split()

        # NOTE: Include student_id in cache key so that the same essay submitted by different
        # students gets evaluated separately (plagiarism detection depends on student_id)
        text_fingerprint = hashlib.sha256(
            f"{topic_id}|{keywords}|{clean_text}|{student_id}".encode("utf-8")
        ).hexdigest()
        cache_key = evaluation_cache_key(topic_id, text_fingerprint)

        cached = cache_manager.get_json(cache_key)
        if cached:
            return cached
        
        # 2. Check for minimum length
        if word_count < 10:
            return {
                "status": "error",
                "message": "Essay too short (minimum 10 words)",
                "score": 0,
                "plagiarism": 0,
                "plagiarism_level": "low",
                "feedback": "Essay is too short to evaluate.",
                "plagiarism_feedback": "",
                "word_count": word_count,
                "is_plagiarized": False,
                "rubric_breakdown": {},
                "improvement_tips": [],
                "score_band": "needs_improvement",
                "originality_label": "highly_original"
            }
        
        # 3. Get content quality score from Prolog
        try:
            # Convert teacher keyword phrases into normalized word tokens so
            # Prolog relevance can intersect with the tokenized essay content.
            keyword_tokens = []
            for kw in keywords.split(','):
                keyword_tokens.extend(re.findall(r"[a-zA-Z0-9]+", kw.lower()))

            # Keep deterministic order while removing duplicates.
            deduped_keyword_tokens = list(dict.fromkeys(token for token in keyword_tokens if token))
            kw_list = [f"'{k}'" for k in deduped_keyword_tokens]
            prolog_keywords = "[" + ",".join(kw_list) + "]"
            prolog_text_list = "[" + ",".join([f"'{w}'" for w in words]) + "]"
            
            query_str = f"evaluate_essay({prolog_text_list}, {prolog_keywords}, Score, Feedback)"
            result = list(self.prolog.query(query_str))
            
            if result:
                base_score = float(result[0]["Score"])
                prolog_feedback = result[0]["Feedback"]
                
                if isinstance(prolog_feedback, bytes):
                    prolog_feedback = prolog_feedback.decode("utf-8")
                elif isinstance(prolog_feedback, list):
                    prolog_feedback = "".join([chr(c) for c in prolog_feedback])
                else:
                    prolog_feedback = str(prolog_feedback)
            else:
                base_score = 40
                prolog_feedback = "The essay structure or relevance did not meet evaluation criteria."
        except Exception as e:
            print(f"Prolog evaluation error: {e}")
            base_score = 40
            prolog_feedback = f"Error in evaluation: {str(e)}"
        
        # 4. Check plagiarism
        previous_essays = self.get_previous_essays_for_topic(topic_id, exclude_student_id=student_id)
        plagiarism_percentage, detailed_comparisons = self.plagiarism_detector.check_plagiarism(
            essay_text, 
            previous_essays
        )
        
        plagiarism_level = self._classify_plagiarism_with_prolog(plagiarism_percentage)
        plagiarism_feedback = self._get_plagiarism_feedback(plagiarism_percentage, plagiarism_level)
        
        # 5. Apply plagiarism penalty
        final_score = self._apply_plagiarism_penalty(base_score, plagiarism_percentage, plagiarism_level)

        # 5b. Prolog-first explainability features
        rubric_breakdown = self._get_score_breakdown(prolog_text_list, prolog_keywords)
        improvement_tips = self._get_improvement_tips(prolog_text_list, prolog_keywords)
        score_band = self._get_score_band(final_score)
        originality_label = self._get_originality_label(plagiarism_percentage)
        
        # 6. Determine if plagiarized (threshold: 50%)
        is_plagiarized = plagiarism_percentage >= 50
        
        payload = {
            "status": "success",
            "score": round(final_score, 2),
            "plagiarism": round(plagiarism_percentage, 2),
            "plagiarism_level": plagiarism_level,
            "feedback": prolog_feedback,
            "plagiarism_feedback": plagiarism_feedback,
            "word_count": word_count,
            "is_plagiarized": is_plagiarized,
            "base_score": round(base_score, 2),
            "detailed_comparisons": detailed_comparisons,
            "rubric_breakdown": rubric_breakdown,
            "improvement_tips": improvement_tips,
            "score_band": score_band,
            "originality_label": originality_label
        }

        cache_manager.set_json(cache_key, payload, ttl_seconds=900)
        return payload

    def _normalize_prolog_value(self, value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        if isinstance(value, list):
            if all(isinstance(item, int) for item in value):
                return "".join(chr(item) for item in value)
            return " ".join(self._normalize_prolog_value(item) for item in value)
        return str(value)

    def _normalize_label(self, value: Any) -> str:
        return self._normalize_prolog_value(value).strip().replace("_", " ")

    def _get_score_breakdown(self, prolog_text_list: str, prolog_keywords: str) -> Dict[str, int]:
        try:
            query = (
                "score_breakdown("
                f"{prolog_text_list}, {prolog_keywords}, "
                "Argument, Coherence, Vocabulary, Sentence, Intro, Conclusion, Logic, Fact, Relevance)"
            )
            result = list(self.prolog.query(query))
            if result:
                row = result[0]
                return {
                    "argument": int(row.get("Argument", 0)),
                    "coherence": int(row.get("Coherence", 0)),
                    "vocabulary": int(row.get("Vocabulary", 0)),
                    "sentence": int(row.get("Sentence", 0)),
                    "introduction": int(row.get("Intro", 0)),
                    "conclusion": int(row.get("Conclusion", 0)),
                    "logic": int(row.get("Logic", 0)),
                    "facts": int(row.get("Fact", 0)),
                    "relevance": int(row.get("Relevance", 0)),
                }
        except Exception as e:
            print(f"Prolog score breakdown error: {e}")
        return {}

    def _get_improvement_tips(self, prolog_text_list: str, prolog_keywords: str, limit: int = 5) -> list:
        try:
            result = list(self.prolog.query(f"improvement_tip({prolog_text_list}, {prolog_keywords}, Tip)"))
            tips = []
            seen = set()
            for row in result:
                tip = self._normalize_prolog_value(row.get("Tip", "")).strip()
                if tip and tip not in seen:
                    tips.append(tip)
                    seen.add(tip)
                if len(tips) >= limit:
                    break
            return tips
        except Exception as e:
            print(f"Prolog improvement tips error: {e}")
            return []

    def _get_score_band(self, final_score: float) -> str:
        try:
            result = list(self.prolog.query(f"score_band({final_score}, Band)"))
            if result:
                return self._normalize_label(result[0]["Band"])
        except Exception as e:
            print(f"Prolog score band error: {e}")

        if final_score >= 85:
            return "excellent"
        if final_score >= 70:
            return "good"
        if final_score >= 50:
            return "fair"
        return "needs improvement"

    def _get_originality_label(self, plagiarism_percentage: float) -> str:
        try:
            result = list(self.prolog.query(f"originality_label({plagiarism_percentage}, Label)"))
            if result:
                return self._normalize_label(result[0]["Label"])
        except Exception as e:
            print(f"Prolog originality label error: {e}")

        if plagiarism_percentage < 20:
            return "highly original"
        if plagiarism_percentage < 40:
            return "mostly original"
        if plagiarism_percentage < 70:
            return "review needed"
        return "high risk similarity"

    def _classify_plagiarism_with_prolog(self, plagiarism_percentage: float) -> str:
        try:
            result = list(self.prolog.query(f"classify_plagiarism({plagiarism_percentage}, Level)"))
            if result:
                return self._normalize_prolog_value(result[0]["Level"]).lower()
        except Exception as e:
            print(f"Prolog plagiarism classification error: {e}")

        return self.plagiarism_detector.classify_plagiarism_level(plagiarism_percentage)

    def _get_plagiarism_feedback(self, plagiarism_percentage: float, level: str) -> str:
        try:
            result = list(self.prolog.query(f"plagiarism_feedback({level}, Feedback)"))
            if result:
                return self._normalize_prolog_value(result[0]["Feedback"])
        except Exception as e:
            print(f"Prolog plagiarism feedback error: {e}")

        return self.plagiarism_detector.get_plagiarism_feedback(plagiarism_percentage, level)
    
    def _apply_plagiarism_penalty(self, base_score: float, plagiarism_percentage: float, level: str) -> float:
        """
        Apply plagiarism penalty to base score.
        
        Args:
            base_score: Original content quality score
            plagiarism_percentage: Plagiarism percentage
            level: Plagiarism level classification
            
        Returns:
            Final score after penalty
        """
        try:
            result = list(
                self.prolog.query(
                    f"apply_plagiarism_penalty({base_score}, {plagiarism_percentage}, {level}, FinalScore)"
                )
            )
            if result:
                return max(0.0, float(result[0]["FinalScore"]))
        except Exception as e:
            print(f"Prolog plagiarism penalty error: {e}")

        penalty_factors = {
            'low': 0.10,
            'medium': 0.15,
            'high': 0.35,
            'critical': 0.75,
        }

        penalty_factor = penalty_factors.get(level, 0.0)
        penalty_amount = (plagiarism_percentage / 100) * base_score * penalty_factor
        return max(0.0, base_score - penalty_amount)
