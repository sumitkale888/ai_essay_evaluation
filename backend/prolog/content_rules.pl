check_relevance(TextList, Keywords, 10, "Highly relevant to the topic.") :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L), L >= 3, !.

check_relevance(TextList, Keywords, 6, "Moderately relevant content.") :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L), L >= 1, !.

check_relevance(_, _, 2, "Warning: Content seems off-topic.").