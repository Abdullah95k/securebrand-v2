# text

The Arabic and Sorani fold of lang-dialect-id section 5.3 C (session F7), its tokenizer helpers, and its standard-library Python twin. One fold produces the `text_norm` that keyword-matcher matches on, from every item text and every client keyword; the golden corpus `fixtures/text/golden.jsonl` keeps the TypeScript fold, the Python twin and lang-dialect-id's own fold byte-identical (ADR-0028).

The specification is the plan's "Fold specification v1" (`docs/plans/F7.md`), summarised below. Version `fold-1`.

## Who uses it

- **normalize-item (C4)**, through `listening-sdk` (F4): while lang-dialect-id is unreachable it publishes `lang = "und"`, `text_norm = textNorm(title, text, "und")` and `lang_pending = true` (lang-dialect-id 8). Both import `text`; neither copies the fold. Extracting `hashtags`, `at_mentions` and `links` into arrays is normalize-item's own work.
- **keyword-matcher (C5)**: folds every keyword form under both folds (`fold(form, "ar")` and `fold(form, "ckb")`), and reports `offsets` as code-point spans of `text_norm`, as `tokenize` does (ADR-0031).
- **lang-dialect-id (C3)**: its `/v1/fold` may call the Python twin, `text_fold`; it builds `FOLD_VERSION` into `lang_model_version`.

## A service using it

`examples/normalize-fallback.ts` (build `contracts` and `text` first: `pnpm --filter contracts build && pnpm --filter text build`, then `node packages/text/examples/normalize-fallback.ts`):

```ts
// How the services use the fold. normalize-item's fallback (lang-dialect-id 8): while lang-dialect-id
// is unreachable, an item is published with lang "und", text_norm from this fold and lang_pending, and
// lang_rescore corrects it later. keyword-matcher compiles every keyword form under both folds
// (keyword-matcher 5.3 B) and reports offsets in code points of text_norm.
import { FOLD_VERSION, fold, textNorm, tokenize } from "text";

const item = { title: null, text: "شبكة زين بالبصرة ضعيفة اليوم 😡 #زين_العراق" };
const normalized = {
  lang: "und",
  lang_pending: true,
  text_norm: textNorm(item.title, item.text, "und"),
  fold: FOLD_VERSION,
};
console.log(JSON.stringify(normalized));

for (const form of ["زين العراق", "#زين_العراق", "كوردستان", "وڵاتێكي"]) {
  console.log(`${form}: ar ${fold(form, "ar")} | ckb ${fold(form, "ckb")}`);
}

const spans = tokenize(normalized.text_norm).map((t) => `${t.text} [${t.start}, ${t.end})`);
console.log(spans.join(" · "));
```

It prints:

```text
{"lang":"und","lang_pending":true,"text_norm":"شبكه زين بالبصره ضعيفه اليوم #زين_العراق","fold":"fold-1"}
زين العراق: ar زين العراق | ckb زین العراق
#زين_العراق: ar #زين_العراق | ckb #زین_العراق
كوردستان: ar كوردستان | ckb کوردستان
وڵاتێكي: ar وڵاتێکی | ckb وڵاتێکی
شبكه [0, 4) · زين [5, 8) · بالبصره [9, 16) · ضعيفه [17, 22) · اليوم [23, 28) · #زين_العراق [29, 40)
```

The two folds never give the same ي/ی or ك/ک, so a keyword typed in Arabic letters matches a Sorani text, and the reverse, without the folds cross-matching (keyword-matcher 5.3 B).

## API

TypeScript (`import ... from "text"`):

| Export                                      | What it does                                                                                                                                              |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fold(text, lang)`                          | The fold of one text under its language label, one of `contracts`' `LANG_LABELS`. The label is required: language is decided on the raw text first.       |
| `textNorm(title, text, lang)`               | `text_norm` of a record: the folded title and text, the non-empty ones joined by one space, title first. The label is checked even when both are missing. |
| `tokenize(textNorm)`                        | The tokens of a `text_norm` (`word`, `hashtag`, `mention`) with `[start, end)` offsets in code points.                                                    |
| `cpLength(s)`, `cpSlice(s, start, end)`     | Length and slices in code points, never UTF-16 units.                                                                                                     |
| `SORANI_ONLY_LETTERS`, `hasSoraniLetter(s)` | ڕ ڵ ۆ ێ ە, which send a token to the Sorani fold in Arabic mode.                                                                                          |
| `FOLD_VERSION`, `FOLD_DATA_SHA256`          | The fold's version (`fold-1`) and the hash of the data it folds with.                                                                                     |
| `TextError`                                 | Every refusal, with a `code`: `not_string`, `no_lang`, `bad_lang`, `not_unicode` (a lone surrogate), `unicode_version` (a runtime below Unicode 15.1).    |

Python, the twin (`packages/text/python/text_fold`, standard library only, Python 3.13):

```python
from text_fold import FOLD_VERSION, fold, text_norm

print(fold("ئاوي خواردنەوە نييە لە بەسرە", "ckb"))
print(text_norm(None, "النت منقطع بالبصرة من الصبح، شنو السالفة؟", "ar"), FOLD_VERSION)
```

It prints:

```console
ئاوی خواردنەوە نییە لە بەسرە
النت منقطع بالبصره من الصبح شنو السالفه fold-1
```

The twin reads the same `data/fold-table.json`, `LANG_LABELS` from `contracts`' `schemas/vocabulary.json`, and takes Unicode 15.1 from Python 3.13's `unicodedata`; it refuses any other Unicode version.

## The fold

Two modes: `ckb` takes the Sorani fold for every token; every other label (`ar`, `en`, `mixed`, `other`, `und`) takes the Arabic fold, except that a token holding a Sorani-only letter (ڕ ڵ ۆ ێ ە) takes the Sorani fold. The rows run in order:

| Row | Arabic fold                                                                                                                                                                                                                                  | Sorani fold                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 0   | none                                                                                                                                                                                                                                         | ه + ZWNJ → ە (the legacy spelling), on the text as received |
| 1   | NFKC (Unicode 15.1); delete U+200B–U+200F, U+202A–U+202E, U+2060–U+2064, U+2066–U+2069, U+FEFF and U+061C                                                                                                                                    | same                                                        |
| 2   | delete the harakat U+064B–U+0652, U+0670, U+06D6–U+06ED and tatweel; then NFKC again                                                                                                                                                         | same                                                        |
| 3   | أ إ آ ٱ → ا, and a U+0653–U+0655 among the marks right after an ا is deleted                                                                                                                                                                 | same                                                        |
| 4   | ة → ه                                                                                                                                                                                                                                        | ة → ە, ھ → ه                                                |
| 5   | ک → ك                                                                                                                                                                                                                                        | ك → ک                                                       |
| 6   | ى ی → ي                                                                                                                                                                                                                                      | ي ى → ی                                                     |
| 7   | kept: چ گ پ ڤ ژ ؤ ئ ء                                                                                                                                                                                                                        | kept: ڕ ڵ ۆ ێ ە چ گ پ ڤ ژ ئ                                 |
| 8   | ٠–٩ and ۰–۹ → 0–9                                                                                                                                                                                                                            | same                                                        |
| 9   | full case folding (Unicode 15.1)                                                                                                                                                                                                             | same                                                        |
| 10  | tokens: URLs deleted; `#` and `@` keep their sign at the start of a hashtag or mention, which runs over letters, marks, numbers and `_`; every other character but a letter, mark or number is a space; white space collapses and is trimmed | same                                                        |
| 11  | NFKC again                                                                                                                                                                                                                                   | same                                                        |

The details:

- **URLs.** A URL starts where no letter, mark or number precedes it, with `http://`, `https://` or `www.` in any ASCII case, and runs to the next white space; it is deleted whole. A bare domain (`example.com`) is no URL: it becomes `example com`.
- **Kept characters** are Unicode 15.1's letters, marks and numbers, except the variation selectors, U+20DD–U+20E4 and the emoji skin-tone modifiers, which are spaces. Unassigned code points are spaces too.
- **Hashtags and mentions.** `#` or `@` keeps its sign when no letter, mark or number precedes it and a letter, mark, number or `_` follows; `_` outside a hashtag or mention is a space. So `#a#b` folds to `#a b` and `x@example.com` to `x example com`.
- **Which tokens take the Sorani fold**, in Arabic mode: a hashtag or mention, or a run of letters, marks and numbers, found after row 2.
- **Idempotent.** Folding twice equals folding once, for every input; the tests check every code point, every pair from the Arabic and Latin blocks with the marks, and a seeded random set, in both languages.

## Documented gaps

- Arabizi (Arabic in Latin letters) is only case-folded, never transliterated (ADR-0028).
- Kurmanji (Badini) is folded like any `other` text.
- علي and على collide under the Arabic fold (lang-dialect-id 12); keyword exclusions handle it.
- In Arabic mode, a Sorani token without a Sorani-only letter takes the Arabic fold: under `und` it stays wrong until `lang_rescore` (`كوردستان وڵاتێکی جوانە`). A legacy ه + ZWNJ inside it stays ه.
- A Sorani ە written with a plain final ه and no ZWNJ stays ه: the explicit character table does not guess it (Q1).
- NFKC can compose a Sorani-only letter away: ە followed by U+0654 becomes ۀ.
- Row 0 reads the text as received, so a presentation-form heh before a ZWNJ (ﻪ + ZWNJ) is not the legacy pair: it folds to ه (`uni-0031`).
- Row 2's range U+06D6–U+06ED also holds three signs that are no marks (U+06DD, ۞ U+06DE, ۩ U+06E9): they are deleted, not made spaces, so they join what stands on either side (`uni-0032`, `uni-0033`).
- The URL rule reads the text before row 2 deletes tatweel, which is a letter: a URL glued to a tatweel (`بالـhttps://…`) is no URL, and its parts stay as words (`url-0031`).

## Data, versions and the corpus

- `data/fold-table.json`: the fold's maps and ranges, read by both languages.
- `data/unicode-15.1.json`: Unicode 15.1's letters, marks, numbers, White_Space and case folding, which Node 24 (Unicode 17.0) cannot give. `python3 scripts/gen_unicode_data.py` regenerates it under Python 3.13; a test checks the committed file. The code points 15.1 leaves unassigned are `contracts`' (`registries/unicode-15.1-unassigned.json`), and NFKC is the runtime's, applied between them.
- `data/fold-versions.json`: every released version with its `FOLD_DATA_SHA256` and the hash of its golden expectations. Any change to the fold or a golden vector is a new `FOLD_VERSION`, with a new entry there and in `test/unit/version.test.ts`'s pinned list.
- `fixtures/text/golden.jsonl`: the golden corpus. `uv run python scripts/gen_golden.py` writes it from `scripts/corpus/`: an anchor keeps its hand-written `text_norm`, every other case's is computed by the Python twin, and both suites check every case. `pnpm --filter text review-sheet` writes the reader's sheet, `fixtures/text/review/golden-review.csv`.

## Tests

`make test SERVICE=text` runs both suites: Vitest under `test/` and pytest under `python/tests/`.
