% Load utilities first, then the rules
:- [utils].
:- [content_rules].
:- [grammar_rules].
:- [grading_logic].
:- [structure_rules].

evaluate_essay(TextList, TopicKeywords, FinalScore, Feedback) :-
    % 1. Call structure check
    check_structure(TextList, S1, F1),
    % 2. Call vocabulary check
    check_vocabulary(TextList, S2, F2),
    % 3. Call relevance check
    check_relevance(TextList, TopicKeywords, S3, F3),
    % 4. Weighted Grade Calculation
    calculate_final_grade(S1, S2, S3, FinalScore),
    % Combine all feedback strings
    atomic_list_concat([F1, " ", F2, " ", F3], Feedback).