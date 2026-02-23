% Dividing the essay into 3 parts to check for structure
check_structure(TextList, 10, "Well-organized with a clear flow.") :-
    length(TextList, L), L > 100,
    has_intro_markers(TextList),
    has_conclusion_markers(TextList), !.

check_structure(_, 5, "Structure is weak. Ensure you have a clear introduction and conclusion.").

% Look for specific organizational markers
has_intro_markers(List) :- 
    member(Word, List), 
    member(Word, [firstly, begin, introduction, started, nowadays]).

has_conclusion_markers(List) :- 
    member(Word, List), 
    member(Word, [finally, conclusion, summary, overall, conclude]).