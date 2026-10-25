"""The Unicode 15.1.0 pin (D-2, D11) and the refusals (D8)."""

import json
import subprocess
import sys
import unicodedata

import pytest

from text_fold import TextError, check_unicode_version, fold, text_norm
from text_fold.unicode import WHITE_SPACE

from conftest import UNASSIGNED, chars


@pytest.mark.parametrize("version", ["15.0.0", "16.0.0", "17.0.0", ""])
def test_refuses_a_unicode_version_other_than_15_1_0(version: str) -> None:
    with pytest.raises(TextError) as refused:
        check_unicode_version(version)
    assert refused.value.code == "unicode_version"


def test_accepts_unicode_15_1_0() -> None:
    check_unicode_version("15.1.0")


def test_imports_on_this_runtime_whose_unicode_is_15_1_0() -> None:
    # This module imported text_fold, which checks the version at import.
    assert unicodedata.unidata_version == "15.1.0"


def test_refuses_to_import_where_unicodedata_reports_another_version() -> None:
    script = "import unicodedata\nunicodedata.unidata_version = '16.0.0'\nimport text_fold\n"
    run = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert run.returncode != 0
    assert "TextError: unicode_version:" in run.stderr


@pytest.mark.parametrize(
    ("text", "lang", "expected"),
    [
        pytest.param(chars(0x61, 0xA7CB, 0x62), "en", "a b", id="U+A7CB under en"),
        pytest.param(chars(0x0628, 0x0897, 0x062A), "ar", "ب ت", id="U+0897 under ar"),
        pytest.param(chars(0x0628, 0x0897, 0x062A), "ckb", "ب ت", id="U+0897 under ckb"),
    ],
)
def test_a_code_point_unassigned_in_15_1_folds_as_a_separator(
    text: str, lang: str, expected: str
) -> None:
    # U+A7CB and U+0897 are assigned by Unicode 16.0; under 15.1 they are separators (D4).
    assert unicodedata.category(text[1]) == "Cn"
    assert fold(text, lang) == expected


def test_the_unassigned_code_points_are_those_of_contracts_registry() -> None:
    # The TypeScript fold reads them from the registry (Q6); the twin takes them from unicodedata.
    registry = json.loads(UNASSIGNED.read_text(encoding="utf-8"))
    listed = {cp for first, last in registry["ranges"] for cp in range(first, last + 1)}
    unassigned = {cp for cp in range(0x110000) if unicodedata.category(chr(cp)) == "Cn"}
    assert listed == unassigned


def test_white_space_is_str_isspace_without_the_information_separators() -> None:
    listed = {cp for first, last in WHITE_SPACE for cp in range(first, last + 1)}
    spaces = {cp for cp in range(0x110000) if chr(cp).isspace()}
    assert listed == spaces - set(range(0x1C, 0x20))


@pytest.mark.parametrize("text", [None, b"x", 7, ["x"]])
def test_refuses_a_text_that_is_not_a_string(text: object) -> None:
    with pytest.raises(TextError) as refused:
        fold(text, "ar")  # pyright: ignore[reportArgumentType]
    assert refused.value.code == "not_string"


def test_refuses_a_call_without_a_language_label() -> None:
    with pytest.raises(TextError) as refused:
        fold("سلام", None)  # pyright: ignore[reportArgumentType]
    assert refused.value.code == "no_lang"


@pytest.mark.parametrize("lang", ["fa", "AR", "", 7])
def test_refuses_a_label_outside_contracts_lang_labels(lang: object) -> None:
    with pytest.raises(TextError) as refused:
        fold("سلام", lang)  # pyright: ignore[reportArgumentType]
    assert refused.value.code == "bad_lang"


def test_refuses_a_lone_surrogate_without_quoting_the_text() -> None:
    with pytest.raises(TextError) as refused:
        fold("private words \ud800", "ar")
    assert refused.value.code == "not_unicode"
    assert "private" not in str(refused.value)


@pytest.mark.parametrize(
    ("text", "lang", "code"),
    [
        pytest.param(7, None, "not_string", id="not a string, no label"),
        pytest.param("\ud800", None, "no_lang", id="surrogate, no label"),
        pytest.param("\ud800", "fa", "bad_lang", id="surrogate, bad label"),
    ],
)
def test_checks_the_text_then_the_label_then_the_code_points(
    text: object, lang: object, code: str
) -> None:
    with pytest.raises(TextError) as refused:
        fold(text, lang)  # pyright: ignore[reportArgumentType]
    assert refused.value.code == code


def test_text_norm_refuses_a_missing_label_even_with_nothing_to_fold() -> None:
    with pytest.raises(TextError) as refused:
        text_norm(None, None, None)  # pyright: ignore[reportArgumentType]
    assert refused.value.code == "no_lang"
