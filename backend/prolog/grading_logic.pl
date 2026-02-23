% FinalScore = (Structure*0.3) + (Vocab*0.3) + (Relevance*0.4)
calculate_final_grade(S, V, R, FinalScore) :-
    RawScore is (S * 0.3) + (V * 0.3) + (R * 0.4),
    FinalScore is round(RawScore).