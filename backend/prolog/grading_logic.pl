% FinalScore = (Vocab*0.3) + (Grammar*0.3) + (Content*0.4)
calculate_final_grade(V, G, C, FinalScore) :-
    RawScore is (V * 0.3) + (G * 0.3) + (C * 0.4),
    FinalScore is round(RawScore).