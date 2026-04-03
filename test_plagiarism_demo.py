"""
Plagiarism Detection - Test & Demo Script
Demonstrates the plagiarism detection system with two student submissions
"""

from collections import defaultdict
from pathlib import Path

from backend.api.core.evaluation import EssayEvaluator
from backend.api.core.plagiarism import PlagiarismDetector
from pyswip import Prolog

# =============================================================================
# TEST SCENARIO: Two Students Submit Essays
# =============================================================================

# Sample essay data
TOPIC_ID = 1
TOPIC_KEYWORDS = "artificial intelligence, machine learning, neural networks"

# Student 1: Original Essay
STUDENT_1_ESSAY = """
Artificial intelligence (AI) is transforming the world in unprecedented ways. 
Machine learning, a subset of AI, enables computers to learn from data without 
being explicitly programmed. Neural networks, inspired by biological neurons, 
form the backbone of modern deep learning systems.

The applications of AI are vast and varied. In healthcare, AI helps doctors 
diagnose diseases more accurately. In finance, machine learning algorithms detect 
fraudulent transactions. In transportation, autonomous vehicles are becoming reality.

However, AI also presents challenges. Privacy concerns arise as AI systems process 
massive amounts of personal data. Bias in training data can lead to discriminatory 
outcomes. The job market faces disruption as automation replaces certain roles.

Despite these challenges, the future of AI is promising. Continued research in 
explainable AI will make systems more transparent. Ethical frameworks are being 
developed to ensure responsible AI deployment. Education and workforce development 
programs are preparing the next generation.

In conclusion, artificial intelligence and machine learning represent both tremendous 
opportunity and responsibility. As these technologies continue to evolve, society must 
ensure they benefit humanity while minimizing risks.
"""

# Student 2: Partially Plagiarized Essay (copies several sentences verbatim)
STUDENT_2_ESSAY = """
Artificial intelligence (AI) is transforming the world in unprecedented ways. 
Machine learning, a subset of AI, enables computers to learn from data without 
being explicitly programmed. Deep neural networks form the backbone of modern 
deep learning systems.

The applications of AI are vast and varied. In healthcare, AI helps doctors 
diagnose diseases more accurately. In finance, machine learning algorithms detect 
fraudulent transactions. In transportation, autonomous vehicles are becoming reality.

However, AI also presents challenges. Privacy concerns arise as AI systems process 
massive amounts of personal data. Bias in training data can lead to discriminatory 
outcomes. The job market faces disruption as automation replaces certain roles.

The future of AI is promising. Continued research in explainable AI will make 
systems more transparent. Ethical frameworks are being developed to ensure 
responsible AI deployment. Education and workforce development programs are 
preparing the next generation.

In conclusion, artificial intelligence and machine learning represent both tremendous 
opportunity and responsibility.
"""

# Student 3: Completely Original Essay
STUDENT_3_ESSAY = """
The rapid advancement of computational systems has opened new frontiers in data analysis. 
Predictive modeling techniques enable organizations to forecast trends and make 
informed decisions. These methodologies rely on sophisticated algorithms that identify 
patterns in complex datasets.

Several industries have experienced significant transformation. Retail businesses 
optimize inventory management through demand forecasting. Manufacturing plants improve 
quality control with automated inspection systems. Educational institutions personalize 
learning paths based on student performance analytics.

Nevertheless, implementation challenges persist. Data quality and completeness directly 
affect model reliability. Computational resources required for processing large datasets 
remain expensive. Interpretation of model decisions requires domain expertise.

Looking ahead, technological improvements will address current limitations. Cloud 
computing resources become increasingly accessible and cost-effective. Visualization 
tools make complex analyses more understandable. Cross-disciplinary collaboration 
strengthens practical applications.

In summary, computational analysis and predictive technologies are reshaping how 
organizations operate. Success depends on combining technical capabilities with 
human judgment and ethical considerations.
"""

def run_plagiarism_test():
    """
    Run complete plagiarism detection test with three student submissions
    """
    print("=" * 80)
    print("PLAGIARISM DETECTION SYSTEM - TEST SCENARIO")
    print("=" * 80)
    print()
    
    # Initialize components
    detector = PlagiarismDetector()

    class DemoEssayEvaluator(EssayEvaluator):
        def __init__(self, prolog_instance):
            super().__init__(prolog_instance)
            self._essay_store = defaultdict(list)

        def get_previous_essays_for_topic(self, topic_id: int, exclude_student_id: int = None) -> list:
            return list(self._essay_store[topic_id])

        def store_essay(self, topic_id: int, essay_text: str) -> None:
            self._essay_store[topic_id].append(essay_text)
    
    # Set up Prolog
    prolog = Prolog()
    prolog_path = (Path(__file__).resolve().parent / "backend" / "prolog" / "main_brain.pl").as_posix()
    
    try:
        prolog.consult(prolog_path)
        print(f"✓ Prolog loaded successfully")
    except Exception as e:
        print(f"⚠ Prolog setup: {e}")
    
    evaluator = DemoEssayEvaluator(prolog)
    
    print()
    print("=" * 80)
    print("SCENARIO: Three Students Submit Essays on AI/Machine Learning")
    print("=" * 80)
    print()
    
    # =========================================================================
    # STUDENT 1 SUBMISSION (First - No Previous Submissions)
    # =========================================================================
    print("STUDENT 1 SUBMISSION")
    print("-" * 80)
    print(f"Words: {len(STUDENT_1_ESSAY.split())}")
    print()
    
    # No previous essays for topic (first submission)
    student_1_result = evaluator.evaluate_essay(
        essay_text=STUDENT_1_ESSAY,
        keywords=TOPIC_KEYWORDS,
        topic_id=TOPIC_ID,
        student_id=1
    )
    evaluator.store_essay(TOPIC_ID, STUDENT_1_ESSAY)
    
    print(f"Status: {student_1_result['status']}")
    print(f"Score: {student_1_result['score']}/100 (Base: {student_1_result['base_score']})")
    print(f"Plagiarism Percentage: {student_1_result['plagiarism']}%")
    print(f"Plagiarism Level: {student_1_result['plagiarism_level'].upper()}")
    print(f"Is Plagiarized: {student_1_result['is_plagiarized']}")
    print(f"Feedback: {student_1_result['feedback']}")
    print(f"Plagiarism Feedback: {student_1_result['plagiarism_feedback']}")
    print()
    
    # =========================================================================
    # STUDENT 2 SUBMISSION (High Similarity to Student 1)
    # =========================================================================
    print("STUDENT 2 SUBMISSION (Partially Copied from Student 1)")
    print("-" * 80)
    print(f"Words: {len(STUDENT_2_ESSAY.split())}")
    print()
    
    # Compare against Student 1's essay
    student_2_result = evaluator.evaluate_essay(
        essay_text=STUDENT_2_ESSAY,
        keywords=TOPIC_KEYWORDS,
        topic_id=TOPIC_ID,
        student_id=2
    )
    evaluator.store_essay(TOPIC_ID, STUDENT_2_ESSAY)
    
    print(f"Status: {student_2_result['status']}")
    print(f"Score: {student_2_result['score']}/100 (Base: {student_2_result['base_score']})")
    print(f"Plagiarism Percentage: {student_2_result['plagiarism']}%")
    print(f"Plagiarism Level: {student_2_result['plagiarism_level'].upper()}")
    print(f"Is Plagiarized: {student_2_result['is_plagiarized']}")
    print(f"Feedback: {student_2_result['feedback']}")
    print(f"Plagiarism Feedback: {student_2_result['plagiarism_feedback']}")
    
    if student_2_result.get('detailed_comparisons'):
        print("\nDetailed Comparison Results:")
        for comp in student_2_result['detailed_comparisons']:
            print(f"  - Compared to essay #{comp['comparison_index'] + 1}")
            print(f"    Similarity: {comp['similarity_score']:.2%}")
            print(f"    Plagiarism: {comp['plagiarism_percentage']:.2f}%")
    print()
    
    # =========================================================================
    # STUDENT 3 SUBMISSION (Original Work)
    # =========================================================================
    print("STUDENT 3 SUBMISSION (Original Content)")
    print("-" * 80)
    print(f"Words: {len(STUDENT_3_ESSAY.split())}")
    print()
    
    # Compare against Student 1 and 2's essays
    student_3_result = evaluator.evaluate_essay(
        essay_text=STUDENT_3_ESSAY,
        keywords=TOPIC_KEYWORDS,
        topic_id=TOPIC_ID,
        student_id=3
    )
    evaluator.store_essay(TOPIC_ID, STUDENT_3_ESSAY)
    
    print(f"Status: {student_3_result['status']}")
    print(f"Score: {student_3_result['score']}/100 (Base: {student_3_result['base_score']})")
    print(f"Plagiarism Percentage: {student_3_result['plagiarism']}%")
    print(f"Plagiarism Level: {student_3_result['plagiarism_level'].upper()}")
    print(f"Is Plagiarized: {student_3_result['is_plagiarized']}")
    print(f"Feedback: {student_3_result['feedback']}")
    print(f"Plagiarism Feedback: {student_3_result['plagiarism_feedback']}")
    
    if student_3_result.get('detailed_comparisons'):
        print("\nDetailed Comparison Results:")
        for comp in student_3_result['detailed_comparisons']:
            print(f"  - Compared to essay #{comp['comparison_index'] + 1}")
            print(f"    Similarity: {comp['similarity_score']:.2%}")
            print(f"    Plagiarism: {comp['plagiarism_percentage']:.2f}%")
    print()
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    results = [
        ("Student 1 (Original)", student_1_result),
        ("Student 2 (Copied)", student_2_result),
        ("Student 3 (Original)", student_3_result),
    ]
    
    print(f"\n{'Student':<25} {'Score':<12} {'Plagiarism':<15} {'Level':<10} {'Flag'}")
    print("-" * 80)
    for name, result in results:
        flag = "🚩 ALERT" if result['is_plagiarized'] else "✓ PASS"
        print(f"{name:<25} {result['score']:>10}/100 {result['plagiarism']:>13.2f}% {result['plagiarism_level']:>10} {flag}")
    
    print()
    print("=" * 80)
    print("KEY OBSERVATIONS:")
    print("=" * 80)
    print("✓ Student 1: First submission = 0% plagiarism baseline")
    print(f"✓ Student 2: {student_2_result['plagiarism']:.2f}% similarity to Student 1 → Penalty Applied")
    print(f"  Score reduced from {student_2_result['base_score']} to {student_2_result['score']} ({student_2_result['plagiarism_level']} level)")
    print(f"✓ Student 3: {student_3_result['plagiarism']:.2f}% similarity → Original Work Confirmed")
    print()
    print("PLAGIARISM PENALTY STRUCTURE:")
    print("  - Low (<20%): No penalty")
    print("  - Medium (20-50%): 15% score reduction")
    print("  - High (50-75%): 35% score reduction")
    print("  - Critical (>75%): 75% score reduction")
    print()

if __name__ == "__main__":
    run_plagiarism_test()
