% --- SENTENCE STRUCTURE RULES ---
% Penalize very short or very long sentences and reward balance.

sentence_quality(Essay, Score) :-
    essay_sentences(Essay, Sentences),
    Sentences \= [],
    maplist(sentence_word_count, Sentences, Lengths),
    count_short_sentences(Lengths, ShortCount),
    count_long_sentences(Lengths, LongCount),
    average_length(Lengths, Average),
    spread(Lengths, Spread),
    (   ShortCount =:= 0,
        LongCount =:= 0,
        Average >= 10,
        Average =< 22,
        Spread =< 10
    ->  Score = 10
    ;   ShortCount =:= 0,
        LongCount =< 1,
        Average >= 8,
        Average =< 25
    ->  Score = 8
    ;   ShortCount =< 1,
        LongCount =< 2,
        Average >= 6,
        Average =< 28
    ->  Score = 6
    ;   ShortCount =< 2,
        LongCount =< 3
    ->  Score = 4
    ;   Score = 2
    ).
sentence_quality(_, 0).

count_short_sentences([], 0).
count_short_sentences([Length|Rest], Count) :-
    count_short_sentences(Rest, TailCount),
    (Length < 5 -> Count is TailCount + 1 ; Count = TailCount).

count_long_sentences([], 0).
count_long_sentences([Length|Rest], Count) :-
    count_long_sentences(Rest, TailCount),
    (Length > 35 -> Count is TailCount + 1 ; Count = TailCount).

sentence_feedback(Essay, "Balanced sentence structure") :-
    sentence_quality(Essay, Score),
    Score >= 8.

sentence_feedback(Essay, "Short or overly long sentences reduce clarity") :-
    sentence_quality(Essay, Score),
    Score =< 4.
