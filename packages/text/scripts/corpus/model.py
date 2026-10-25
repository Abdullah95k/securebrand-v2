"""One golden.jsonl line per Case (docs/plans/F7.md, "Line format").

A Case with `expect` is an anchor: its text_norm was written by hand, before any code (E2). Every
other case's text_norm is computed by the Python twin from the specification (scripts/gen_golden.py).
"""

from dataclasses import dataclass

Row = int | str


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    lang: str
    text: str
    rows: tuple[Row, ...]
    expect: str | None = None
    title: str | None = None
    note: str | None = None


# The letters whose spelling differs between the folds, as escapes so that no font hides which one
# a case means.
KAF_AR = "ك"  # ك ARABIC LETTER KAF
KAF_FA = "ک"  # ک ARABIC LETTER KEHEH (Sorani and Persian kaf)
YEH_AR = "ي"  # ي ARABIC LETTER YEH
YEH_FA = "ی"  # ی ARABIC LETTER FARSI YEH (Sorani and Persian yaa)
MAKSURA = "ى"  # ى ARABIC LETTER ALEF MAKSURA
TEH_MARBUTA = "ة"  # ة
HEH = "ه"  # ه ARABIC LETTER HEH
AE = "ە"  # ە ARABIC LETTER AE (Sorani e)
HEH_DO = "ھ"  # ھ ARABIC LETTER HEH DOACHASHMEE
TATWEEL = "ـ"

# Format characters (rows 0 and 1).
ZWNJ = "‌"
ZWJ = "‍"
LRM = "‎"
RLM = "‏"
ALM = "؜"  # ARABIC LETTER MARK (D1)
RLE = "‫"
PDF = "‬"
LRI = "⁦"
PDI = "⁩"
WJ = "⁠"  # WORD JOINER (D1)
BOM = "﻿"
