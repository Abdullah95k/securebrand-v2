# fixtures/text: the fold golden corpus (F7)

The golden corpus of the text fold of lang-dialect-id section 5.3 C (`packages/text`, `docs/plans/F7.md`). No platform was called: every sentence was invented for this corpus on 25 Oct 2026, so nothing needed scrubbing. Names are limited to public organisations and brands, places and common given names used as spelling examples; handles use the reserved pattern `@example_*`, URLs and e-mail addresses the reserved domains of RFC 2606 (`example.com`, `example.org`, `example.net`), and phone numbers are visibly fictional (`0770 000 0000`). `packages/text/test/unit/corpus.test.ts` checks those rules.

| File | What it is | How it is produced |
| --- | --- | --- |
| `golden.jsonl` | One case per line: an input under a language label and its expected `text_norm`. An anchor's `text_norm` was written by hand; every other case's was computed by the Python twin from the specification, and both the TypeScript and the Python suites reproduce every line. | `cd packages/text && uv run python scripts/gen_golden.py`, from the case lists in `packages/text/scripts/corpus/`. Never edited by hand. |
| `golden.schema.json` | The JSON Schema (draft 2020-12) of one line. | `pnpm --filter text export:schema`, from `packages/text/test/golden-case.ts`. |
| `review/golden-review.csv` | The reader's sheet: every case holding Arabic script, with columns for the verdict, a corrected `text_norm` and a comment. | `pnpm --filter text review-sheet`, from `golden.jsonl`. |
| `review/READER-GUIDE.md` | The one-page guide and the rule questions for the Iraqi Arabic and Sorani reader. | Written by hand. |

A golden vector never changes inside a `FOLD_VERSION`: a correction after release is a new version (`packages/text/data/fold-versions.json`). The reader's returned sheet is committed beside the generated one as `review/golden-review-<date>.csv`.
