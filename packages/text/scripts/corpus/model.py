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


# The letters whose spelling differs between the folds, by code point so that no font hides which
# one a case means.
KAF_AR = chr(0x0643)  # ك ARABIC LETTER KAF
KAF_FA = chr(0x06A9)  # ک ARABIC LETTER KEHEH (Sorani and Persian kaf)
YEH_AR = chr(0x064A)  # ي ARABIC LETTER YEH
YEH_FA = chr(0x06CC)  # ی ARABIC LETTER FARSI YEH (Sorani and Persian yaa)
MAKSURA = chr(0x0649)  # ى ARABIC LETTER ALEF MAKSURA
TEH_MARBUTA = chr(0x0629)  # ة
HEH = chr(0x0647)  # ه ARABIC LETTER HEH
AE = chr(0x06D5)  # ە ARABIC LETTER AE (Sorani e)
HEH_DO = chr(0x06BE)  # ھ ARABIC LETTER HEH DOACHASHMEE
TATWEEL = chr(0x0640)

# Format characters (rows 0 and 1).
ZWNJ = chr(0x200C)
ZWJ = chr(0x200D)
LRM = chr(0x200E)
RLM = chr(0x200F)
ALM = chr(0x061C)  # ARABIC LETTER MARK (D1)
RLE = chr(0x202B)
PDF = chr(0x202C)
LRI = chr(0x2066)
PDI = chr(0x2069)
WJ = chr(0x2060)  # WORD JOINER (D1)
BOM = chr(0xFEFF)
