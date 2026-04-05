% --- TEXT UTILS ---
% Shared helpers for the essay quality rules.

normalize_essay_input(Input, Text) :-
    string(Input),
    !,
    Text = Input.
normalize_essay_input(Input, Text) :-
    atom(Input),
    !,
    atom_string(Input, Text).
normalize_essay_input(Input, Text) :-
    is_list(Input),
    !,
    atomic_list_concat(Input, ' ', Text).
normalize_essay_input(Input, Text) :-
    term_string(Input, Text).

normalize_token(Input, Token) :-
    string(Input),
    !,
    string_lower(Input, Token).
normalize_token(Input, Token) :-
    atom(Input),
    !,
    atom_string(Input, AtomText),
    string_lower(AtomText, Token).
normalize_token(Input, Token) :-
    term_string(Input, Text),
    string_lower(Text, Token).

normalize_token_list([], []).
normalize_token_list([H|T], [Normalized|Rest]) :-
    normalize_token(H, Normalized),
    normalize_token_list(T, Rest).

essay_words(Input, Words) :-
    normalize_essay_input(Input, Text),
    string_lower(Text, Lower),
    split_string(Lower, " \n\t\r.,!?;:()[]{}\"'`-/\\", " \n\t\r.,!?;:()[]{}\"'`-/\\", RawWords),
    exclude(=(""), RawWords, Words).

essay_sentences(Input, Sentences) :-
    normalize_essay_input(Input, Text),
    split_string(Text, ".!?", "", RawSentences),
    maplist(clean_sentence, RawSentences, CleanSentences),
    exclude(=(""), CleanSentences, Sentences).

clean_sentence(RawSentence, CleanSentence) :-
    normalize_space(string(Trimmed), RawSentence),
    string_lower(Trimmed, CleanSentence).

sentence_words(Sentence, Words) :-
    string_lower(Sentence, Lower),
    split_string(Lower, " \n\t\r.,!?;:()[]{}\"'`-/\\", " \n\t\r.,!?;:()[]{}\"'`-/\\", RawWords),
    exclude(=(""), RawWords, Words).

sentence_word_count(Sentence, Count) :-
    sentence_words(Sentence, Words),
    length(Words, Count).

count_matches(Words, Targets, Count) :-
    findall(Target, (member(Target, Targets), member(Target, Words)), Matches),
    length(Matches, Count).

count_keyword_hits(_, [], 0).
count_keyword_hits(Words, [Keyword|Rest], Count) :-
    count_keyword_hits(Words, Rest, TailCount),
    (   member(Keyword, Words)
    ->  Count is TailCount + 1
    ;   Count = TailCount
    ).

count_repeated_words([], _, Count, Count).
count_repeated_words([Word|Rest], Seen, Acc, Count) :-
    (   memberchk(Word, Seen)
    ->  Acc1 is Acc + 1
    ;   Acc1 = Acc
    ),
    count_repeated_words(Rest, [Word|Seen], Acc1, Count).

average_length(Lengths, Average) :-
    sum_list(Lengths, Sum),
    length(Lengths, Count),
    Count > 0,
    Average is Sum / Count.

spread(Lengths, Spread) :-
    max_list(Lengths, Max),
    min_list(Lengths, Min),
    Spread is Max - Min.
