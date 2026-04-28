"""
Test plagiarism detection with real database students
"""
from backend.api.core.database import get_db_connection
from backend.api.core.evaluation import EssayEvaluator
from pyswip import Prolog
import os

# Initialize Prolog
prolog = Prolog()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
prolog_path = os.path.join(BASE_DIR, "backend", "prolog", "main_brain.pl").replace("\\", "/")

try:
    prolog.consult(prolog_path)
    print(f"✓ Prolog consulted successfully")
except Exception as e:
    print(f"✗ Prolog error: {e}")

# Initialize evaluator
evaluator = EssayEvaluator(prolog)

# Real data from database
TOPIC_ID = 13
STUDENT_1_ID = 6   # Sumit Kale
STUDENT_2_ID = 1   # Sumit Kale

# Same essay text
ESSAY_TEXT = "Artificial intelligence is transforming society. Machine learning enables computers to learn from data. Neural networks are inspired by biological neurons. These technologies have applications in healthcare, finance, and transportation. However, privacy and bias concerns exist. The future of AI depends on ethical development and responsible deployment."

print("=" * 80)
print("PLAGIARISM DETECTION TEST - Different Students, Same Essay")
print("=" * 80)
print()

# Check current essays for this topic
print("Current essays for Topic 13:")
db = get_db_connection()
cursor = db.cursor(dictionary=True)
cursor.execute("""
    SELECT e.essay_id, e.student_id, u.name, e.submission_date 
    FROM Essays e 
    JOIN Users u ON u.user_id = e.student_id 
    WHERE e.topic_id = %s 
    ORDER BY e.submission_date
""", (TOPIC_ID,))
essays = cursor.fetchall()
for e in essays:
    print(f"  Essay {e['essay_id']}: Student {e['student_id']} ({e['name']}) - {e['submission_date']}")
db.close()

print("\n" + "-" * 80)
print(f"Testing: Student {STUDENT_1_ID} submits test essay")
print("-" * 80)

# Get previous essays for Student 1
print(f"\nPrevious essays (excluding Student {STUDENT_1_ID}):")
previous_essays = evaluator.get_previous_essays_for_topic(TOPIC_ID, exclude_student_id=STUDENT_1_ID)
print(f"  Found: {len(previous_essays)} essays")
for i, essay in enumerate(previous_essays):
    print(f"    Essay {i+1}: {essay[:80]}...")

# Check plagiarism
if previous_essays:
    plagiarism_pct, comparisons = evaluator.plagiarism_detector.check_plagiarism(ESSAY_TEXT, previous_essays)
    print(f"\nPlagiarism check result:")
    print(f"  Plagiarism: {plagiarism_pct:.2f}%")
    print(f"  Comparisons made: {len(comparisons)}")
    for comp in comparisons:
        print(f"    - Comparison {comp['comparison_index']}: {comp['similarity_score']:.4f} ({comp['plagiarism_percentage']:.2f}%)")
else:
    print(f"\n  ✗ ERROR - No previous essays found to compare!")

print("\n" + "-" * 80)
print(f"Testing: Student {STUDENT_2_ID} submits SAME essay")
print("-" * 80)

# Get previous essays for Student 2
print(f"\nPrevious essays (excluding Student {STUDENT_2_ID}):")
previous_essays = evaluator.get_previous_essays_for_topic(TOPIC_ID, exclude_student_id=STUDENT_2_ID)
print(f"  Found: {len(previous_essays)} essays")
for i, essay in enumerate(previous_essays):
    print(f"    Essay {i+1}: {essay[:80]}...")

# Check plagiarism
if previous_essays:
    plagiarism_pct, comparisons = evaluator.plagiarism_detector.check_plagiarism(ESSAY_TEXT, previous_essays)
    print(f"\nPlagiarism check result:")
    print(f"  Plagiarism: {plagiarism_pct:.2f}%")
    print(f"  Comparisons made: {len(comparisons)}")
    for comp in comparisons:
        print(f"    - Comparison {comp['comparison_index']}: {comp['similarity_score']:.4f} ({comp['plagiarism_percentage']:.2f}%)")
    
    if plagiarism_pct > 80:
        print(f"\n  ✓ SUCCESS - High plagiarism correctly detected!")
    else:
        print(f"\n  ✗ ISSUE - Plagiarism not detected (expected >80%, got {plagiarism_pct:.2f}%)")
else:
    print(f"\n  ✗ ERROR - No previous essays found!")

print("\n" + "=" * 80)
