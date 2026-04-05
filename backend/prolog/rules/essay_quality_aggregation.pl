% --- QUALITY AGGREGATION ---
% Combines the modular Prolog scores and generates feedback.

essay_quality_score(Essay, Score) :-
    essay_quality_score(Essay, [], Score).

essay_quality_score(Essay, Keywords, Score) :-
    argument_score(Essay, ArgumentScore),
    coherence_score(Essay, CoherenceScore),
    vocab_score(Essay, VocabScore),
    sentence_quality(Essay, SentenceScore),
    intro_score(Essay, Keywords, IntroScore),
    conclusion_score(Essay, ConclusionScore),
    logic_score(Essay, LogicScore),
    fact_score(Essay, FactScore),
    redundancy_penalty(Essay, Penalty),
    RawAverage is (ArgumentScore + CoherenceScore + VocabScore + SentenceScore + IntroScore + ConclusionScore + LogicScore + FactScore) / 8,
    BaseScore is RawAverage * 10,
    AdjustedScore is BaseScore - Penalty,
    Score is max(0, round(AdjustedScore)).

final_score(Essay, Score) :-
    essay_quality_score(Essay, [], Score).

final_score(Essay, Keywords, Score) :-
    essay_quality_score(Essay, Keywords, Score).

feedback(Essay, "Strong argumentation") :-
    strong_argument(Essay).

feedback(Essay, "Good vocabulary") :-
    vocab_score(Essay, Score),
    Score >= 8.

feedback(Essay, "Improve vocabulary") :-
    vocab_score(Essay, Score),
    Score =< 4.

feedback(Essay, "Good coherence") :-
    coherence_score(Essay, Score),
    Score >= 8.

feedback(Essay, "Improve coherence") :-
    coherence_score(Essay, Score),
    Score =< 4.

feedback(Essay, "Balanced sentence structure") :-
    sentence_quality(Essay, Score),
    Score >= 8.

feedback(Essay, "Short or overly long sentences reduce clarity") :-
    sentence_quality(Essay, Score),
    Score =< 4.

feedback(Essay, "Strong introduction") :-
    intro_score(Essay, Score),
    Score >= 8.

feedback(Essay, "Weak introduction") :-
    intro_score(Essay, Score),
    Score =< 4.

feedback(Essay, "Strong conclusion") :-
    conclusion_score(Essay, Score),
    Score >= 8.

feedback(Essay, "Weak conclusion") :-
    conclusion_score(Essay, Score),
    Score =< 4.

feedback(Essay, "Logical contradiction detected") :-
    contradiction(Essay).

feedback(Essay, "Reduce repetition") :-
    repeated_words(Essay, Count),
    Count >= 4.

feedback(Essay, "Fact-based evidence is limited") :-
    fact_score(Essay, Score),
    Score =< 4.

essay_feedback(Essay, Feedback) :-
    findall(Message, feedback(Essay, Message), Messages),
    (   Messages = []
    ->  Feedback = "Essay evaluated successfully."
    ;   atomic_list_concat(Messages, " | ", Feedback)
    ).
