# Plagiarism Detection - Quick Start Guide

## What Was Added?

A complete plagiarism detection system that integrates with your existing essay evaluation pipeline.

---

## Files Created/Modified

### New Files Created:

1. **`backend/api/core/plagiarism.py`** (NEW)
   - Main plagiarism detection module
   - Uses TF-IDF + Cosine Similarity algorithm
   - Classifies plagiarism levels and generates feedback

2. **`backend/api/core/evaluation.py`** (NEW)
   - Essay evaluation orchestrator
   - Combines content quality (Prolog) + plagiarism detection
   - Applies plagiarism penalty to final score

3. **`backend/prolog/plagiarism_rules.pl`** (NEW)
   - Prolog rules for plagiarism classification
   - Penalty factors for different severity levels

4. **`test_plagiarism_demo.py`** (NEW)
   - Complete test scenario with 3 students
   - Shows how plagiarism detection works in practice

5. **`PLAGIARISM_DETECTION_GUIDE.md`** (NEW)
   - Comprehensive documentation
   - Architecture, algorithms, examples

6. **`requirements.txt`** (NEW)
   - Dependencies including scikit-learn

### Files Modified:

1. **`backend/api/models.py`**
   - Added `PlagiarismResult` model
   - Added `EvaluationResult` model

2. **`backend/api/routes/student.py`**
   - Updated `/submit-essay` endpoint
   - Now integrates plagiarism detection
   - Enhanced response with plagiarism data

3. **`backend/prolog/main_brain.pl`**
   - Load plagiarism_rules.pl

4. **`frontend/src/pages/ResultView.jsx`**
   - Display plagiarism percentage
   - Color-coded severity (green → yellow → orange → red)
   - Show plagiarism feedback
   - Calculate originality percentage
   - Alert warning for high plagiarism

---

## How It Works

### Student Submission Flow:

```
1. Student submits essay
   ↓
2. System retrieves topic keywords
   ↓
3. Prolog evaluates content quality (base score)
   ↓
4. System retrieves all previous essays for topic
   ↓
5. Plagiarism detection compares against all previous essays
   ↓
6. Similarity score converted to plagiarism percentage
   ↓
7. Penalty applied based on plagiarism level
   ↓
8. Final score = Base Score - Penalty
   ↓
9. Return comprehensive results to student
```

### Plagiarism Penalty Structure:

| Plagiarism % | Level | Penalty Factor | Example |
|---|---|---|---|
| 0-20% | Low | 0% (no penalty) | Score: 85 → 85 |
| 20-50% | Medium | 15% | Score: 85 → ~73 |
| 50-75% | High | 35% | Score: 85 → ~55 |
| >75% | Critical | 75% | Score: 85 → ~21 |

---

## Testing the Feature

### Option 1: Run Demo Script
```bash
cd c:\FASTAPI\Essay_evaluation
python test_plagiarism_demo.py
```

Output shows:
- 3 students submitting essays
- Student 1: 0% plagiarism (first submission)
- Student 2: High similarity to Student 1, score penalized
- Student 3: Original work, minimal similarity

### Option 2: Test Via API

**Submit Essay with Plagiarism Detection:**
```bash
curl -X POST http://127.0.0.1:8000/student/submit-essay \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "topic_id": 1,
    "essay_text": "Your essay content here..."
  }'
```

**Response:**
```json
{
    "status": "success",
    "score": 72.5,
    "base_score": 85.0,
    "plagiarism": 35.2,
    "plagiarism_level": "medium",
    "feedback": "Content demonstrates good understanding...",
    "plagiarism_feedback": "Plagiarism detection: 35.2%. Moderate similarity found. Please ensure proper citations.",
    "word_count": 450,
    "is_plagiarized": false,
    "comparison_count": 3,
    "essay_id": 42
}
```

---

## Frontend Display

### Result Page Shows:

1. **Final Score** (with base score if penalized)
2. **Plagiarism Section** with:
   - Similarity percentage
   - Plagiarism level (color-coded)
   - Status icon (✓ for clean, ⚠️ for flagged)
   - Detailed feedback
   - Number of comparisons made

3. **Stats Grid:**
   - Word count
   - Status
   - Originality percentage

4. **Warning Alert** (if plagiarism ≥ 50%)

---

## Key Features

✅ **Automatic Detection**
- Runs on every submission
- Compares against all previous essays for the topic
- First submission always shows 0% plagiarism

✅ **Intelligent Scoring**
- TF-IDF algorithm detects paraphrasing (not just word matching)
- Ignores common words (the, a, is)
- Emphasizes topic-specific terminology
- Fast (microseconds per comparison)

✅ **Fair Penalties**
- Proportional to plagiarism severity
- Protects students: minor similarities don't trigger heavy penalties
- Different penalty factors for different severity levels

✅ **Clear Feedback**
- Students see exact plagiarism percentage
- Understand severity level
- Get actionable feedback
- See how many essays were compared

✅ **Teacher Visibility**
- Can see flagged submissions
- Compare students for patterns
- Identify systematic plagiarism

---

## Configuration

### Adjust Plagiarism Thresholds

Edit `backend/api/core/plagiarism.py`:

```python
def classify_plagiarism_level(self, plagiarism_percentage: float) -> str:
    if plagiarism_percentage < 20:      # Change 20 to your threshold
        return 'low'
    elif plagiarism_percentage < 50:    # Change 50
        return 'medium'
    elif plagiarism_percentage < 75:    # Change 75
        return 'high'
    else:
        return 'critical'
```

### Adjust Penalty Factors

Edit `backend/api/core/evaluation.py`:

```python
penalty_factors = {
    'low': 0.0,        # Change 0.0
    'medium': 0.15,    # Change 0.15 (15%)
    'high': 0.35,      # Change 0.35 (35%)
    'critical': 0.75   # Change 0.75 (75%)
}
```

---

## Database Requirements

**No schema changes needed!**

The system works with existing tables:
- `Essays` - stores essay_text
- `Grades` - stores final_score (with penalty already applied)
- `Feedback` - stores combined feedback

Optional: Create `PlagiarismCheck` table for detailed analysis history (see guide)

---

## Dependencies Required

Install new packages:
```bash
pip install scikit-learn
pip install numpy
pip install scipy
```

Or install all:
```bash
pip install -r requirements.txt
```

---

## Common Workflows

### Workflow 1: Check Single Student
1. Go to `/student/student-history/{student_id}`
2. Previous results show score, plagiarism %, and feedback

### Workflow 2: Teacher Reviews Submissions
1. Go to `/teacher/topic-submissions/{topic_id}`
2. Can see all students' final scores (with penalties applied)
3. Flag high plagiarism submissions for review

### Workflow 3: Detect Serial Plagiarism
1. Compare plagiarism logs across multiple topics
2. Identify students with consistently high similarity
3. Escalate to academic integrity review

---

## Troubleshooting

### Q: Plagiarism always shows 0%
**A:** This is the first submission for this topic. Second submission will show comparison.

### Q: Scores seem different
**A:** Check base_score vs final_score. Plagiarism penalty was applied.

### Q: Getting scikit-learn error
**A:** Run `pip install scikit-learn`

### Q: Comparison seems inaccurate
**A:** System compares against essays in database for SAME topic only. Different topics = different comparisons.

---

## Performance Tips

For many essays (100+), consider:

1. **Enable Database Indexing:**
   ```sql
   CREATE INDEX idx_topic_student ON Essays(topic_id, student_id);
   ```

2. **Cache Previous Essays:**
   - Modify `EssayEvaluator.get_previous_essays_for_topic()` to use Redis or in-memory cache

3. **Async Evaluation:**
   - Use FastAPI's `BackgroundTasks` for non-critical submissions

---

## Next Steps

1. **Test the feature**: Run `python test_plagiarism_demo.py`
2. **Review the guide**: Read `PLAGIARISM_DETECTION_GUIDE.md`
3. **Monitor results**: Check student submissions for plagiarism flags
4. **Adjust settings**: Fine-tune thresholds and penalties as needed
5. **Plan enhancements**: Consider external database comparison (TurnItIn API)

---

## Support

For detailed information about:
- **Algorithm details** → See `PLAGIARISM_DETECTION_GUIDE.md` (Algorithm Details section)
- **API responses** → See `PLAGIARISM_DETECTION_GUIDE.md` (API Response Examples)
- **Scoring examples** → See `PLAGIARISM_DETECTION_GUIDE.md` (Scoring Examples)
- **Testing** → Run `python test_plagiarism_demo.py`

---

## Summary

✨ **You now have:**
- Full plagiarism detection system ✓
- Integrated scoring with penalties ✓
- Frontend display with severity indicators ✓
- Complete documentation ✓
- Test scenario with 3 students ✓
- Demo script showing how it works ✓

**Start using it immediately with your existing database!**
