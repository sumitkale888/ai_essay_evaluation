% --- REDUNDANCY RULES ---
% Detect repeated words and repeated phrases.

repeated_words(Essay, Count) :-
    essay_words(Essay, Words),
    count_repeated_words(Words, [], 0, Count).

repeated_phrases(Essay, Count) :-
    essay_words(Essay, Words),
    repeated_bigram_count(Words, [], 0, Count).

repeated_bigram_count([_, _], _, Count, Count) :-
    !.
repeated_bigram_count([First, Second|Rest], Seen, Acc, Count) :-
    Bigram = [First, Second],
    (   memberchk(Bigram, Seen)
    ->  Acc1 is Acc + 1
    ;   Acc1 = Acc
    ),
    repeated_bigram_count([Second|Rest], [Bigram|Seen], Acc1, Count).
repeated_bigram_count(_, _, Count, Count).

redundancy_penalty(Essay, Penalty) :-
    repeated_words(Essay, WordCount),
    repeated_phrases(Essay, PhraseCount),
    Total is WordCount + (PhraseCount * 2),
    (   Total =:= 0 -> Penalty = 0
    ;   Total =< 2 -> Penalty = 1
    ;   Total =< 5 -> Penalty = 3
    ;   Total =< 9 -> Penalty = 5
    ;   Penalty = 8
    ).
