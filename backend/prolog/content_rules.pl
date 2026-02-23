% Check if the essay meets depth requirements
check_content_rules(WordCount, 10, "Very informative content.") :- WordCount > 250, !.
check_content_rules(WordCount, 8, "Satisfactory content depth.") :- WordCount > 150, !.
check_content_rules(_, 5, "Content lacks depth and detail.").% Check how many topic-specific keywords were used
check_relevance(TextList, Keywords, 10, "Highly relevant to the topic.") :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L), L >= 3, !.

check_relevance(TextList, Keywords, 6, "Moderately relevant, but could use more technical terms.") :-
    intersection(TextList, Keywords, Matches),
    length(Matches, L), L >= 1, !.

check_relevance(_, _, 2, "Warning: Content seems off-topic.").

% Helper to find matching words
intersection([], _, []).
intersection([H|T], L2, [H|Res]) :- member(H, L2), intersection(T, L2, Res), !.
intersection([_|T], L2, Res) :- intersection(T, L2, Res).