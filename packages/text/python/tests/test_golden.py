"""The twin against fixtures/text/golden.jsonl (lang-dialect-id 13, criteria 1 and 7; D9): the
Python half of the conformance the TypeScript fold's golden.test.ts runs on the same lines."""

import pytest

from text_fold import fold, text_norm

from conftest import GoldenCase, code_points, golden_cases

CASES = golden_cases()
IDS = [case.id for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_reproduces_every_golden_case_byte_for_byte(case: GoldenCase) -> None:
    folded = text_norm(case.title, case.text, case.lang)
    assert folded == case.text_norm, f"{code_points(folded)} != {code_points(case.text_norm)}"


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_folding_a_golden_text_norm_again_changes_nothing(case: GoldenCase) -> None:
    folded = fold(case.text_norm, case.lang)
    assert folded == case.text_norm, f"{code_points(folded)} != {code_points(case.text_norm)}"


def test_text_norm_joins_the_folded_title_and_text_with_one_space_title_first() -> None:
    assert text_norm("ZAIN Iraq", "شبكة ضعيفة", "ar") == "zain iraq شبكه ضعيفه"
    assert text_norm(None, "شبكة", "ar") == "شبكه"
    assert text_norm("شبكة", None, "ar") == "شبكه"


def test_text_norm_skips_an_input_that_is_empty_or_folds_to_nothing() -> None:
    assert text_norm("", "Zain", "en") == "zain"
    assert text_norm("\U0001f602", "Zain", "en") == "zain"
    assert text_norm("Zain", " ،؟ ", "ar") == "zain"
    assert text_norm(None, None, "und") == ""
