% --- LOGICAL CONSISTENCY RULES ---
% Detect contradictions using statement facts.

:- dynamic statement/3.

statement_state(true).
statement_state(false).

contradiction(Essay) :-
    statement(Essay, Proposition, true),
    statement(Essay, Proposition, false).

logic_score(Essay, Score) :-
    (   contradiction(Essay)
    ->  Score = 2
    ;   Score = 10
    ).

logic_feedback(Essay, "Logical contradiction detected") :-
    contradiction(Essay).
