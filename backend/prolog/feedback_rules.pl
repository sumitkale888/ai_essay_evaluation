% --- FINAL LABEL RULES ---
% Human-readable labels derived from final score and originality.

score_band(Score, excellent) :- Score >= 85, !.
score_band(Score, good) :- Score >= 70, !.
score_band(Score, fair) :- Score >= 50, !.
score_band(_, needs_improvement).

originality_label(Plagiarism, highly_original) :- Plagiarism < 20, !.
originality_label(Plagiarism, mostly_original) :- Plagiarism < 40, !.
originality_label(Plagiarism, review_needed) :- Plagiarism < 70, !.
originality_label(_, high_risk_similarity).
