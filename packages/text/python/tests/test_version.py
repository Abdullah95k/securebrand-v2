"""FOLD_VERSION and FOLD_DATA_SHA256 against the files (D10, E7; lang-dialect-id 13 criterion 12): a
change to the fold table, the 15.1 data, contracts' unassigned ranges or a golden vector without a
new FOLD_VERSION fails here."""

import hashlib
import json
import re

from text_fold import FOLD_DATA_SHA256, FOLD_VERSION

from conftest import FOLD_TABLE, FOLD_VERSIONS, UNASSIGNED, UNICODE_DATA, file_sha256, golden_sha256


def test_fold_version_is_the_fold_tables_version_token() -> None:
    table = json.loads(FOLD_TABLE.read_text(encoding="utf-8"))
    assert table["version"] == FOLD_VERSION
    assert re.fullmatch(r"fold-[1-9][0-9]*", FOLD_VERSION)


def test_fold_data_sha256_hashes_the_fold_table_the_15_1_data_and_the_unassigned_ranges() -> None:
    lines = (
        f"fold-table.json {file_sha256(FOLD_TABLE)}\n"
        f"unicode-15.1.json {file_sha256(UNICODE_DATA)}\n"
        f"unicode-15.1-unassigned.json {file_sha256(UNASSIGNED)}\n"
    )
    assert hashlib.sha256(lines.encode("utf-8")).hexdigest() == FOLD_DATA_SHA256


def test_the_fold_data_and_the_golden_expectations_hash_to_the_current_versions_entry() -> None:
    assert FOLD_VERSIONS.is_file(), f"{FOLD_VERSIONS} is missing: it records each version's hashes"
    history = json.loads(FOLD_VERSIONS.read_text(encoding="utf-8"))
    entries = [entry for entry in history["versions"] if entry["version"] == FOLD_VERSION]
    assert len(entries) == 1, f"fold-versions.json has {len(entries)} entries for {FOLD_VERSION}"
    assert entries[0]["fold_data_sha256"] == FOLD_DATA_SHA256
    assert entries[0]["golden_sha256"] == golden_sha256()
