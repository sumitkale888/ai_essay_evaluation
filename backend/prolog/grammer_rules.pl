% Define transition words that make an essay "flow"
transition_word('however').
transition_word('therefore').
transition_word('moreover').
transition_word('consequently').
transition_word('furthermore').

% Count how many transition words are used
count_transitions([], 0).
count_transitions([H|T], Count) :-
    transition_word(H),
    count_transitions(T, Rest),
    Count is Rest + 1, !.
count_transitions([_|T], Count) :-
    count_transitions(T, Count).

% Grade grammar/flow based on transition usage
check_vocabulary(TextList, 10, "Excellent use of connectors.") :- 
    count_transitions(TextList, C), C >= 4, !.
check_vocabulary(TextList, 7, "Good flow, but could use more transitions.") :- 
    count_transitions(TextList, C), C >= 2, !.
check_vocabulary(_, 4, "Sentence transitions are weak; use words like 'however' or 'therefore'.").