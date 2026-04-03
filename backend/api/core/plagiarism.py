"""
Plagiarism Detection Module using TF-IDF and Cosine Similarity
Compares student essays against all previous submissions for the same topic
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple


class PlagiarismDetector:
    """
    Detects plagiarism by comparing essays using TF-IDF vectorization
    and cosine similarity metrics.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=5000
        )
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess essay text for comparison.
        
        Args:
            text: Raw essay text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase and remove extra whitespace
        text = text.lower().strip()
        # Remove multiple spaces
        text = ' '.join(text.split())
        return text
    
    def calculate_similarity(self, essay1: str, essay2: str) -> float:
        """
        Calculate similarity between two essays using cosine similarity.
        
        Args:
            essay1: First essay text
            essay2: Second essay text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not essay1 or not essay2:
            return 0.0
        
        # Preprocess texts
        text1 = self.preprocess_text(essay1)
        text2 = self.preprocess_text(essay2)
        
        try:
            # Vectorize both texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def check_plagiarism(self, current_essay: str, previous_essays: List[str]) -> Tuple[float, List[dict]]:
        """
        Check plagiarism against list of previous essays.
        
        Args:
            current_essay: Current student's essay
            previous_essays: List of previously submitted essays
            
        Returns:
            Tuple of (max_plagiarism_percentage, detailed_comparisons)
        """
        if not previous_essays:
            # First submission for this topic
            return 0.0, []
        
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        similarities = []
        detailed_results = []
        
        # Compare current essay with each previous essay
        for idx, prev_essay in enumerate(previous_essays):
            similarity = self.calculate_similarity(current_essay, prev_essay)
            plagiarism_percentage = similarity * 100
            
            similarities.append(similarity)
            detailed_results.append({
                'comparison_index': idx,
                'similarity_score': float(similarity),
                'plagiarism_percentage': float(plagiarism_percentage),
                'previous_essay_length': len(prev_essay.split())
            })
        
        # Return maximum plagiarism percentage found
        max_plagiarism = max(similarities) * 100 if similarities else 0.0
        
        return float(max_plagiarism), detailed_results
    
    def classify_plagiarism_level(self, plagiarism_percentage: float) -> str:
        """
        Classify plagiarism level based on percentage.
        
        Args:
            plagiarism_percentage: Plagiarism percentage (0-100)
            
        Returns:
            Classification: 'low', 'medium', 'high', 'critical'
        """
        if plagiarism_percentage < 30:
            return 'low'
        elif plagiarism_percentage <= 70:
            return 'medium'
        elif plagiarism_percentage < 90:
            return 'high'
        else:
            return 'critical'
    
    def get_plagiarism_feedback(self, plagiarism_percentage: float, plagiarism_level: str) -> str:
        """
        Generate feedback message based on plagiarism results.
        
        Args:
            plagiarism_percentage: Plagiarism percentage
            plagiarism_level: Classification level
            
        Returns:
            Feedback message
        """
        feedback_map = {
            'low': f"Plagiarism detection: {plagiarism_percentage:.1f}%. Low similarity detected (< 30%). Minor score penalty applied.",
            'medium': f"Plagiarism detection: {plagiarism_percentage:.1f}%. Moderate similarity detected (30-70%). Ensure proper citations.",
            'high': f"Plagiarism detection: {plagiarism_percentage:.1f}%. High similarity detected (> 70%). Review content originality.",
            'critical': f"Plagiarism detection: {plagiarism_percentage:.1f}%. Critical similarity detected (>= 90%). Potential academic integrity violation."
        }
        return feedback_map.get(plagiarism_level, "Unable to determine plagiarism level.")
