# Reader's guide: the fold golden file

Thank you for reading. The platform listens to Iraqi posts in Iraqi Arabic, standard Arabic and Sorani Kurdish. Before it searches a post for a client's keywords, it rewrites the text into one "folded" spelling, `text_norm`, so that a keyword typed once matches every common spelling. The folded text is only for matching: the post itself is always kept as written.

The sheet `golden-review.csv` holds every test case that contains Arabic script. Each row is a short sentence we invented (no real person's words), its language label, and the folded text we expect. Please check three things in each row.

1. **Is the sentence natural?** Would an Iraqi or a Kurd write it this way, in a post or a comment? If not, mark it `unnatural` and say what is odd.
2. **Is the expected folded text right?** Use the rules below. If it is wrong, mark `expected wrong` and write the right folded text in `corrected text_norm`.
3. **Does it read like a real person's words**, or is anything in it offensive or a real private person's name? Then mark `remove`.

Otherwise mark `ok`. The column "what the fold changed" lists the rules that apply to the row; the input column shows invisible characters as ⟨U+200C ZWNJ⟩ and the like.

## The rules, in plain words

The language label decides the rules: `ckb` (Sorani) uses the Kurdish rules, every other label uses the Arabic rules, except that in Arabic text a word holding ڕ ڵ ۆ ێ or ە is treated as Kurdish.

| What | Arabic rules | Kurdish rules |
| --- | --- | --- |
| vowel marks (فَتحة، شدّة …) and stretching ـ | removed | removed |
| أ إ آ ٱ | become ا | become ا |
| ة | becomes ه: البصرة → البصره | becomes ە: بةسرة → بەسرە |
| kaf | ک becomes ك | ك becomes ک: كوردستان → کوردستان |
| yaa | ى and ی become ي: على → علي | ي and ى become ی: ئاوي → ئاوی |
| ھ | kept | becomes ه: ھەولێر → هەولێر |
| ه followed by an invisible joiner (old keyboards) | (joiner removed) | becomes ە: خۆشه‌ → خۆشە |
| kept as written | چ گ پ ڤ ژ ؤ ئ ء | ڕ ڵ ۆ ێ ە چ گ پ ڤ ژ ئ |
| digits ٠–٩ and ۰–۹ | become 0–9 | become 0–9 |
| Latin letters | lower case: ZAIN → zain | lower case |
| punctuation، ؛ ؟ « », emoji, links | become spaces; links are removed | the same |
| #hashtags and @mentions | kept with their sign: #البصرة_تنتفض → #البصره_تنتفض | the same |

Examples: "النت منقطع بالبصرة من الصبح، شنو السالفة؟" folds to "النت منقطع بالبصره من الصبح شنو السالفه"; "ئاوي خواردنەوە نييە لە بەسرە" under `ckb` folds to "ئاوی خواردنەوە نییە لە بەسرە".

Known and accepted: Arabic written in Latin letters (shlonak, 7abibi) is only lower-cased; علي and على fold alike; in Arabic-labelled text, a Kurdish word without ڕ ڵ ۆ ێ ە (for example کوردستان) follows the Arabic rules.

## Questions for you

Please answer these in a few words each (in the email or note you send back):

1. Old Kurdish keyboards write ە as ه followed by an invisible joiner (ZWNJ). We turn that pair into ە. Is that right?
2. Some Kurdish texts write the h sound as ھ (U+06BE). We turn it into ه. Is that right?
3. Some write ە as ة. We turn it into ە in Kurdish text. Is that right?
4. We do not respell whole words, for example a word-initial ر stays ر (we do not write ڕ for it). Is that acceptable for searching?
5. Old keyboards often end a word with a plain ه for ە, with no joiner (خۆشه for خۆشە). We leave that ه as it is, because a word can also end in a real h. Should a final ه in Kurdish text become ە?
6. Is a common Iraqi Arabic or Sorani spelling variant missing from the rules?

## What to send back

The filled sheet (keep the columns as they are; any spreadsheet program can open it, and it saves as CSV), your answers to the six questions, and the date you finished. Your name is recorded only if you want it to be.
