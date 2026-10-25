"""FOLD_VERSION and FOLD_DATA_SHA256 (D10, E7). C3 builds FOLD_VERSION into lang_model_version;
test_version.py ties both, and the golden expectations, to data/fold-versions.json."""

from text_fold._data import DATA_SHA256, TABLE

FOLD_VERSION: str = TABLE.version
FOLD_DATA_SHA256: str = DATA_SHA256
