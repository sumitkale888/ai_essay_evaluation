% --- INTRODUCTION & CONCLUSION RULES ---
% Detect opening and closing strength.

intro_marker(firstly).
intro_marker(first).
intro_marker(initially).
intro_marker(introduction).
intro_marker(undoubtedly).

intro_phrase("in conclusion").
intro_phrase("to begin with").
intro_phrase("this essay").
intro_phrase("the essay").

conclusion_marker(ultimately).
conclusion_marker(overall).
conclusion_marker(finally).
conclusion_marker(conclusion).
conclusion_marker(summary).

conclusion_phrase("in conclusion").
conclusion_phrase("to sum up").
conclusion_phrase("in summary").
conclusion_phrase("in closing").

intro_score(Essay, Score) :-
    intro_score(Essay, [], Score).

intro_score(Essay, Keywords, Score) :-
    essay_sentences(Essay, Sentences),
    (   Sentences = [FirstSentence|_]
    ->  sentence_words(FirstSentence, FirstWords),
        findall(Marker, (member(Marker, FirstWords), intro_marker(Marker)), IntroMatches),
        findall(Phrase, (intro_phrase(Phrase), sub_string(FirstSentence, _, _, _, Phrase)), IntroPhraseMatches),
        count_keyword_hits(FirstWords, Keywords, KeywordHits),
        length(FirstWords, FirstLength),
        (   (IntroMatches \= [] ; IntroPhraseMatches \= []), KeywordHits > 0, FirstLength >= 8
        ->  Score = 10
        ;   KeywordHits > 0, FirstLength >= 8
        ->  Score = 8
        ;   (IntroMatches \= [] ; IntroPhraseMatches \= []), FirstLength >= 6
        ->  Score = 6
        ;   FirstLength >= 5
        ->  Score = 4
        ;   Score = 2
        )
    ;   Score = 0
    ).

conclusion_score(Essay, Score) :-
    essay_sentences(Essay, Sentences),
    (   Sentences = []
    ->  Score = 0
    ;   last(Sentences, LastSentence),
        sentence_words(LastSentence, LastWords),
        findall(Marker, (member(Marker, LastWords), conclusion_marker(Marker)), ConclusionMatches),
        findall(Phrase, (conclusion_phrase(Phrase), sub_string(LastSentence, _, _, _, Phrase)), ConclusionPhraseMatches),
        length(LastWords, LastLength),
        (   (ConclusionMatches \= [] ; ConclusionPhraseMatches \= []), LastLength >= 6
        ->  Score = 10
        ;   LastLength >= 8
        ->  Score = 7
        ;   LastLength >= 5
        ->  Score = 4
        ;   Score = 2
        )
    ).

intro_feedback(Essay, "Strong introduction") :-
    intro_score(Essay, Score),
    Score >= 8.

intro_feedback(Essay, "Weak introduction") :-
    intro_score(Essay, Score),
    Score =< 4.

conclusion_feedback(Essay, "Strong conclusion") :-
    conclusion_score(Essay, Score),
    Score >= 8.

conclusion_feedback(Essay, "Weak conclusion") :-
    conclusion_score(Essay, Score),
    Score =< 4.
