% --- COHERENCE RULES ---
% Logical flow and transition connectors.

connector_word(however).
connector_word(therefore).
connector_word(moreover).
connector_word(because).
connector_word(furthermore).
connector_word(consequently).
connector_word(although).
connector_word(nevertheless).
connector_word(thus).
connector_word(despite).

coherence_score(Essay, Score) :-
    essay_words(Essay, Words),
    findall(Connector, (member(Connector, Words), connector_word(Connector)), Matches),
    length(Matches, Count),
    (   Count >= 4 -> Score = 10
    ;   Count >= 2 -> Score = 8
    ;   Count >= 1 -> Score = 6
    ;   Score = 3
    ).

coherence_feedback(Essay, "Good coherence") :-
    coherence_score(Essay, Score),
    Score >= 8.

coherence_feedback(Essay, "Improve coherence") :-
    coherence_score(Essay, Score),
    Score =< 4.
