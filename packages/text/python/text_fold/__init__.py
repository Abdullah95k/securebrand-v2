"""text_fold: the standard-library Python twin of packages/text's fold (F7, Q4).

It is written from docs/plans/F7.md "Fold specification v1" alone, never from the TypeScript fold,
so that it computes the golden corpus's expectations independently (E2). It reads the same
fold-table.json and contracts' LANG_LABELS, and refuses to import unless the runtime's Unicode is
15.1.0 (D-2).
"""

from text_fold._fold import SORANI_ONLY_LETTERS, fold, text_norm
from text_fold.errors import TextError
from text_fold.unicode import check_unicode_version
from text_fold.version import FOLD_DATA_SHA256, FOLD_VERSION

__all__ = [
    "FOLD_DATA_SHA256",
    "FOLD_VERSION",
    "SORANI_ONLY_LETTERS",
    "TextError",
    "check_unicode_version",
    "fold",
    "text_norm",
]
