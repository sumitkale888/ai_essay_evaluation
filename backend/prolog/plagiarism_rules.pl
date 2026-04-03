% --- PLAGIARISM DETECTION RULES ---
% Rules for evaluating plagiarism levels and applying penalties.

% Requirement-aligned thresholds:
% - low: similarity < 30
% - medium: 30..70
% - high: > 70
% - critical: >= 90

plagiarism_low(Similarity) :-
    Similarity < 30.

plagiarism_medium(Similarity) :-
    Similarity >= 30,
    Similarity =< 70.

plagiarism_high(Similarity) :-
    Similarity > 70,
    Similarity < 90.

plagiarism_critical(Similarity) :-
    Similarity >= 90.

% Classify plagiarism level based on similarity percentage
classify_plagiarism(Similarity, low) :- plagiarism_low(Similarity), !.
classify_plagiarism(Similarity, medium) :- plagiarism_medium(Similarity), !.
classify_plagiarism(Similarity, high) :- plagiarism_high(Similarity), !.
classify_plagiarism(Similarity, critical) :- plagiarism_critical(Similarity), !.

% Determine plagiarism penalty factor (0.0 to 1.0)
% Low is intentionally non-zero so any plagiarism lowers score.
plagiarism_penalty(low, 0.10).     % 10% penalty
plagiarism_penalty(medium, 0.15).  % 15% penalty
plagiarism_penalty(high, 0.35).    % 35% penalty
plagiarism_penalty(critical, 0.75).% 75% penalty

% Generate plagiarism feedback
plagiarism_feedback(low, "Plagiarism check: Minimal similarity detected (< 30%). Original work confirmed.").
plagiarism_feedback(medium, "Plagiarism check: Moderate similarity detected (30-70%). Ensure proper citations.").
plagiarism_feedback(high, "Plagiarism check: High similarity detected (> 70%). Review content originality.").
plagiarism_feedback(critical, "Plagiarism check: Critical similarity detected (>= 90%). Potential academic integrity violation.").

% Apply plagiarism penalty to base score
apply_plagiarism_penalty(BaseScore, PlagiarismPercentage, Level, FinalScore) :-
    plagiarism_penalty(Level, PenaltyFactor),
    PenaltyAmount is (PlagiarismPercentage / 100) * BaseScore * PenaltyFactor,
    FinalScore is BaseScore - PenaltyAmount.

% Check if essay is plagiarized (severity threshold)
is_plagiarized(Similarity) :-
    Similarity >= 50.
