check_relevance(TextList, Keywords, Score, Feedback) :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L),
    length(TextList, TotalWords),
    ( (L >= 3, TotalWords > 100) -> 
        (Score = 10, Feedback = "Highly relevant and detailed.")
    ; (L >= 1, TotalWords > 50) -> 
        (Score = 6, Feedback = "Relevant but lacks depth.")
    ;   (Score = 2, Feedback = "Content is too short or off-topic.")
    ).