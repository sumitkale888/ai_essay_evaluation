% --- VOCABULARY RULES ---
% Detect advanced vocabulary usage.

advanced_vocabulary(articulate).
advanced_vocabulary(analytical).
advanced_vocabulary(sophisticated).
advanced_vocabulary(comprehensive).
advanced_vocabulary(nuanced).
advanced_vocabulary(substantial).
advanced_vocabulary(significant).
advanced_vocabulary(evidence).
advanced_vocabulary(mitigate).
advanced_vocabulary(effective).
advanced_vocabulary(coherent).
advanced_vocabulary(innovative).
advanced_vocabulary(critical).
advanced_vocabulary(perspective).
advanced_vocabulary(methodology).
advanced_vocabulary(synthesis).
advanced_vocabulary(implications).
advanced_vocabulary(clarity).
advanced_vocabulary(robust).
advanced_vocabulary(articulates).
advanced_vocabulary(paradigm).
advanced_vocabulary(illustrates).
advanced_vocabulary(transforms).
advanced_vocabulary(evaluate).
advanced_vocabulary(evaluation).
advanced_vocabulary(theoretical).
advanced_vocabulary(empirical).

vocab_score(Essay, Score) :-
    essay_words(Essay, Words),
    findall(Word, (member(Word, Words), advanced_vocabulary(Word)), Matches),
    length(Matches, Count),
    (   Count >= 12 -> Score = 10
    ;   Count >= 8 -> Score = 9
    ;   Count >= 5 -> Score = 8
    ;   Count >= 3 -> Score = 6
    ;   Count >= 1 -> Score = 4
    ;   Score = 2
    ).

vocab_feedback(Essay, "Good vocabulary") :-
    vocab_score(Essay, Score),
    Score >= 8.

vocab_feedback(Essay, "Improve vocabulary") :-
    vocab_score(Essay, Score),
    Score =< 4.
