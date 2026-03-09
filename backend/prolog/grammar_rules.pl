check_vocabulary(TextList, Score, Feedback) :-
    Transitions = [firstly, moreover, however, therefore, finally, nowadays, overall, 
                   furthermore, additionally, consequently, specifically, 
                   notably, clearly, despite, although, whereas],
    intersection(TextList, Transitions, Matches),
    length(Matches, Count),
    ( Count >= 3 -> (Score = 10, Feedback = "Excellent flow.")
    ; Count >= 1 -> (Score = 5, Feedback = "Basic flow.")
    ; (Score = 0, Feedback = "No logical connectors used.") % Changed from 4 to 0
    ).