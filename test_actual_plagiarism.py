"""
Test plagiarism detection with ACTUAL essays from database
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
except Exception as e:
    print(f"Prolog error: {e}")

evaluator = EssayEvaluator(prolog)

TOPIC_ID = 13
STUDENT_1_ID = 6
STUDENT_2_ID = 1

print("=" * 80)
print("PLAGIARISM DETECTION TEST - Using ACTUAL Database Essays")
print("=" * 80)

# Get the actual essay from database
db = get_db_connection()
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT essay_text FROM Essays WHERE essay_id = 56")
result = cursor.fetchone()

if not result:
    print("✗ Essay not found")
    db.close()
    exit(1)

ESSAY_TEXT = result['essay_text']
print(f"\nTest Essay (from Essay ID 56):")
print(f"  Length: {len(ESSAY_TEXT)} chars, {len(ESSAY_TEXT.split())} words")
print(f"  Preview: {ESSAY_TEXT[:150]}...")

print("\n" + "-" * 80)
print(f"Scenario: Student {STUDENT_1_ID} already submitted this essay")
print(f"          Student {STUDENT_2_ID} submits THE SAME essay")
print("-" * 80)

# Get previous essays for Student 2 (should include Student 1's essays)
print(f"\nPrevious essays for Topic {TOPIC_ID} (excluding Student {STUDENT_2_ID}):")
previous_essays = evaluator.get_previous_essays_for_topic(TOPIC_ID, exclude_student_id=STUDENT_2_ID)
print(f"  Found: {len(previous_essays)} essays")

# Check plagiarism
plagiarism_pct, comparisons = evaluator.plagiarism_detector.check_plagiarism(ESSAY_TEXT, previous_essays)
print(f"\nPlagiarism Detection Result:")
print(f"  ✓ Plagiarism: {plagiarism_pct:.2f}%")
print(f"  Comparisons made: {len(comparisons)}")

# Check if any essay is identical or near-identical
max_similarity = max([c['similarity_score'] for c in comparisons]) if comparisons else 0
print(f"  Maximum similarity found: {max_similarity:.4f} ({max_similarity * 100:.2f}%)")

# Find which essay had the maximum match
if comparisons:
    max_idx = max(range(len(comparisons)), key=lambda i: comparisons[i]['similarity_score'])
    print(f"  Highest match with comparison index {max_idx}: {comparisons[max_idx]['similarity_score']:.4f}")
    
    if plagiarism_pct >= 90:
        print(f"\n  ✓ SUCCESS - High plagiarism correctly detected! ({plagiarism_pct:.2f}%)")
    elif plagiarism_pct >= 70:
        print(f"\n  ⚠ WARNING - Medium plagiarism detected ({plagiarism_pct:.2f}%)")
    else:
        print(f"\n  ✗ ISSUE - Low plagiarism detected ({plagiarism_pct:.2f}%)")
        print(f"    This might be expected if the essays are genuinely different")

# Also check what's in the Essays table
print("\n" + "-" * 80)
print("Debug: Essays in database for this topic:")
cursor.execute(f"""
    SELECT e.essay_id, e.student_id, u.name, e.essay_text 
    FROM Essays e 
    JOIN Users u ON u.user_id = e.student_id 
    WHERE e.topic_id = {TOPIC_ID}
    ORDER BY e.submission_date
""")
essays = cursor.fetchall()
for e in essays:
    text_preview = e['essay_text'][:100].replace('\n', ' ')
    print(f"  Essay {e['essay_id']}: Student {e['student_id']} - {text_preview}...")

db.close()
print("\n" + "=" * 80)
