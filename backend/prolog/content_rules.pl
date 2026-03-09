check_relevance(TextList, Keywords, Score, Feedback) :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L),
    ( L >= 3 -> 
        (Score = 10, Feedback = "Highly relevant.")
    ; L >= 1 -> 
        (Score = 5, Feedback = "Somewhat relevant.")
    ; (Score = 0, Feedback = "Completely off-topic.") % Changed from 2 to 0
    ).