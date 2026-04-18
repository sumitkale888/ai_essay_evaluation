% --- ANALYTICS RULES ---
% Structured rubric breakdown for explainable scoring.

score_breakdown(Essay, Keywords, Argument, Coherence, Vocabulary, Sentence, Intro, Conclusion, Logic, Fact, Relevance) :-
    argument_score(Essay, Argument),
    coherence_score(Essay, Coherence),
    vocab_score(Essay, Vocabulary),
    sentence_quality(Essay, Sentence),
    intro_score(Essay, Keywords, Intro),
    conclusion_score(Essay, Conclusion),
    logic_score(Essay, Logic),
    fact_score(Essay, Fact),
    essay_words(Essay, Words),
    relevance_score(Words, Keywords, Relevance).
