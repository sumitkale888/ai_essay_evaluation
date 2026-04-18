% --- LOAD UTILITIES & RULES ---

:- [utils].
:- [essay_quality_rules].
:- [content_rules].
:- [grammar_rules].
:- [grading_logic].
:- [structure_rules].
:- [plagiarism_rules].
:- [feedback_rules].


evaluate_essay(TextList, TopicKeywords, FinalScore, Feedback) :-
    normalize_essay_input(TextList, EssayText),
    essay_words(EssayText, Words),
    normalize_token_list(TopicKeywords, NormalizedKeywords),
    length(Words, L),
    (   L < 10
    ->  FinalScore = 0,
        Feedback = "Content is too short to evaluate."
    ;   (
            essay_quality_score(EssayText, NormalizedKeywords, QualityScore),
            essay_feedback(EssayText, QualityFeedback),
            relevance_score(Words, NormalizedKeywords, RelevanceScore),
            relevance_feedback(RelevanceScore, RelevanceFeedback),
            CombinedScore is (QualityScore * 0.85) + (RelevanceScore * 1.5),
            FinalScore is min(100, round(CombinedScore)),
            atomic_list_concat([QualityFeedback, " | ", RelevanceFeedback], Feedback)
        )).


relevance_score(Words, Keywords, Score) :-
    intersection(Words, Keywords, Matches),
    length(Matches, Count),
    (   Count >= 5 -> Score = 10
    ;   Count >= 3 -> Score = 8
    ;   Count >= 1 -> Score = 5
    ;   Score = 0
    ).

relevance_feedback(Score, "Highly relevant to the topic.") :-
    Score >= 8.

relevance_feedback(Score, "Some topic keywords are present.") :-
    Score >= 5,
    Score < 8.

relevance_feedback(_, "Topic relevance is limited.").