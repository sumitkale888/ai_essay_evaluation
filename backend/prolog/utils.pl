% Shared helper for finding common elements in two lists
intersection([], _, []).
intersection([H|T], L2, [H|Res]) :- 
    member(H, L2), 
    intersection(T, L2, Res), !.
intersection([_|T], L2, Res) :- 
    intersection(T, L2, Res).