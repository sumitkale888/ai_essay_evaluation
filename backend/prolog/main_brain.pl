:- [content_rules, grammar_rules, grading_logic, structure_rules].

% Main entry point
evaluate_essay(TextList, TopicKeywords, FinalScore, Feedback) :-
    % 1. Check Structure (Intro, Body, Conclusion)
    check_structure(TextList, StructScore, StructFeedback),
    
    % 2. Check Vocabulary & Transitions
    check_vocabulary(TextList, VocabScore, VocabFeedback),
    
    % 3. Check Topic Relevance (Do keywords exist?)
    check_relevance(TextList, TopicKeywords, RelScore, RelFeedback),
    
    % 4. Final Calculation (Weighted)
    calculate_final_grade(StructScore, VocabScore, RelScore, FinalScore),
    
    % 5. Combine all feedback
    atomic_list_concat([StructFeedback, " ", VocabFeedback, " ", RelFeedback], Feedback).