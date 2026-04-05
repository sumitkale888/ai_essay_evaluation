% --- ARGUMENT STRENGTH RULES ---
% Detect claims and supporting points.

supporting_marker(because).
supporting_marker(since).
supporting_marker(therefore).
supporting_marker(thereby).
supporting_marker(moreover).
supporting_marker(furthermore).
supporting_marker(additionally).
supporting_marker(consequently).
supporting_marker(thus).
supporting_marker(example).
supporting_marker(evidence).
supporting_marker(proof).
supporting_marker(support).
supporting_marker(supports).
supporting_marker(demonstrates).
supporting_marker(indicates).
supporting_marker(shows).
supporting_marker(proves).

claim_marker(should).
claim_marker(must).
claim_marker(argues).
claim_marker(illustrates).
claim_marker(indicates).
claim_marker(therefore).
claim_marker(hence).

supporting_statement_count(Essay, Count) :-
    essay_words(Essay, Words),
    findall(Marker, (member(Marker, Words), supporting_marker(Marker)), Matches),
    length(Matches, Count).

strong_argument(Essay) :-
    supporting_statement_count(Essay, Count),
    Count >= 3.

argument_score(Essay, Score) :-
    supporting_statement_count(Essay, Count),
    (   Count >= 5 -> Score = 10
    ;   Count >= 3 -> Score = 8
    ;   Count >= 1 -> Score = 5
    ;   Score = 2
    ).
