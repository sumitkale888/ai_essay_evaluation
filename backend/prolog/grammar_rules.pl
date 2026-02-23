check_vocabulary(TextList, Score, Feedback) :-
    Transitions = [firstly, moreover, however, therefore, finally, nowadays, overall],
    intersection(TextList, Transitions, Matches),
    length(Matches, Count),
    (Count >= 3 -> 
        Score = 10, Feedback = "Excellent use of transition words.";
     Count >= 1 -> 
        Score = 7, Feedback = "Good transitions, but could be improved.";
        Score = 4, Feedback = "Weak vocabulary flow; use more connectors."
    ).