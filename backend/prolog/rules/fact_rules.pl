% --- FACT-BASED RULES ---
% Build sentence facts and keyword containment facts from essay text.

essay_sentence_facts(Essay, Facts) :-
    essay_sentences(Essay, Sentences),
    sentence_fact_list(Sentences, 1, Facts).

sentence_fact_list([], _, []).
sentence_fact_list([Sentence|Rest], Id, [sentence(Id, Sentence)|Facts]) :-
    NextId is Id + 1,
    sentence_fact_list(Rest, NextId, Facts).

essay_sentence(Essay, SentenceId, SentenceText) :-
    essay_sentence_facts(Essay, Facts),
    member(sentence(SentenceId, SentenceText), Facts).

contains(Essay, SentenceId, Keyword) :-
    essay_sentence(Essay, SentenceId, SentenceText),
    sentence_words(SentenceText, Words),
    member(Keyword, Words).

fact_score(Essay, Score) :-
    essay_sentence_facts(Essay, Facts),
    length(Facts, SentenceCount),
    (   SentenceCount >= 4 -> Score = 10
    ;   SentenceCount >= 2 -> Score = 7
    ;   SentenceCount >= 1 -> Score = 4
    ;   Score = 0
    ).
