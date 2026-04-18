% --- IMPROVEMENT RULES ---
% Generates targeted suggestions based on rubric weaknesses.

improvement_tip(Essay, _Keywords, "Add clearer claims and supporting evidence in each paragraph.") :-
    argument_score(Essay, Score),
    Score =< 5.

improvement_tip(Essay, _Keywords, "Use more transition words to improve flow between ideas.") :-
    coherence_score(Essay, Score),
    Score =< 6.

improvement_tip(Essay, _Keywords, "Use more precise academic vocabulary and avoid generic words.") :-
    vocab_score(Essay, Score),
    Score =< 6.

improvement_tip(Essay, _Keywords, "Revise sentence lengths for better clarity and rhythm.") :-
    sentence_quality(Essay, Score),
    Score =< 6.

improvement_tip(Essay, Keywords, "Open with a stronger introduction that states the topic and direction.") :-
    intro_score(Essay, Keywords, Score),
    Score =< 6.

improvement_tip(Essay, _Keywords, "End with a clear conclusion that reinforces your main argument.") :-
    conclusion_score(Essay, Score),
    Score =< 6.

improvement_tip(Essay, _Keywords, "Check for contradictions and ensure your reasoning stays consistent.") :-
    logic_score(Essay, Score),
    Score =< 6.

improvement_tip(Essay, _Keywords, "Add concrete facts, examples, or data to strengthen credibility.") :-
    fact_score(Essay, Score),
    Score =< 6.

improvement_tip(Essay, Keywords, "Use more topic keywords naturally to increase relevance.") :-
    essay_words(Essay, Words),
    relevance_score(Words, Keywords, Score),
    Score =< 5.
