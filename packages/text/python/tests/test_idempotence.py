"""Folding twice equals folding once (D9, E1), under ar and under ckb: over every single code point,
every ordered pair of D9's set, and a seeded random set of strings; and the counterexamples that
made the E1 lines necessary."""

import random
from collections.abc import Iterator

import pytest

from text_fold import fold

from conftest import chars, code_points, idempotence_failures

LANGS = ("ar", "ckb")

# D9's set: the Arabic block (which holds the Sorani letters), printable ASCII, Latin-1 and Latin
# Extended-A, the combining diacritical marks, and row 1's format characters (D1's among them).
PAIR_SET = sorted(
    {
        *range(0x0600, 0x0700),
        *range(0x0020, 0x007F),
        *range(0x00A0, 0x0180),
        *range(0x0300, 0x0370),
        0x061C,
        *range(0x200B, 0x2010),
        *range(0x202A, 0x202F),
        *range(0x2060, 0x2065),
        *range(0x2066, 0x206A),
        0xFEFF,
    }
)

# The random strings' symbols: Arabic and Sorani letters; the marks, tatweel and format characters
# the fold deletes or composes; Latin letters whose case folding is special and combining marks;
# tag signs, punctuation and white space; digits; URL prefixes; emoji, a skin tone, a variation
# selector, a keycap and a flag; presentation forms and a ligature; and U+0897, unassigned in 15.1.
SYMBOLS: tuple[str, ...] = (
    *"اأإآٱبتةثجحخدذرزسشصضطظعغفقكکلمنهھوؤيىیئءڕڵۆێەچگپڤژ",
    *map(chr, (0x0653, 0x0654, 0x0655, 0x0640, 0x064E, 0x0651, 0x0670, 0x06D6)),
    *map(chr, (0x200C, 0x200D, 0x200F, 0x061C, 0xFEFF)),
    # Dotless i, sigma and the Arabic-Indic digits look like other characters; that is the point.
    *"aAbBsSkKiIßİıǰΣσς",  # noqa: RUF001
    *map(chr, (0x0301, 0x0307, 0x0308, 0x030C, 0x0345)),
    *"#@_ .،؛؟/:-«»",
    chr(0x00A0),
    "\n",
    *"٠١٢٣۴۵0129",  # noqa: RUF001
    "http://",
    "https://",
    "www.",
    "\N{GRINNING FACE}",
    "\N{THUMBS UP SIGN}",
    *map(chr, (0x1F3FB, 0xFE0F, 0x20E3)),
    "\N{REGIONAL INDICATOR SYMBOL LETTER I}\N{REGIONAL INDICATOR SYMBOL LETTER Q}",
    *map(chr, (0xFB8E, 0xFBD9, 0xFEFB, 0x0897)),
)
RANDOM_SEED = 20261025
RANDOM_STRINGS = 100_000


def every_code_point() -> Iterator[str]:
    return (chr(cp) for cp in range(0x110000) if not 0xD800 <= cp <= 0xDFFF)


@pytest.fixture(scope="module")
def random_strings() -> list[str]:
    rng = random.Random(RANDOM_SEED)
    return ["".join(rng.choices(SYMBOLS, k=rng.randint(1, 12))) for _ in range(RANDOM_STRINGS)]


def test_the_pair_set_holds_707_code_points() -> None:
    # The plan's 708 (and its 708 x 708 = 501,264 pairs) counts U+061C twice: it lies inside
    # U+0600 to U+06FF. As a set, D9's members are 707.
    assert len(PAIR_SET) == 707


def test_the_random_symbols_are_the_123_the_specification_lists() -> None:
    assert len(SYMBOLS) == len(set(SYMBOLS)) == 123


@pytest.mark.parametrize("lang", LANGS)
def test_folding_twice_equals_folding_once_over_every_single_code_point(lang: str) -> None:
    failures = idempotence_failures(every_code_point(), lang)
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize("lang", LANGS)
def test_folding_twice_equals_folding_once_over_every_pair_of_the_d9_set(lang: str) -> None:
    members = [chr(cp) for cp in PAIR_SET]
    failures = idempotence_failures((a + b for a in members for b in members), lang)
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize("lang", LANGS)
def test_folding_twice_equals_folding_once_over_a_seeded_random_set(
    lang: str, random_strings: list[str]
) -> None:
    failures = idempotence_failures(random_strings, lang)
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize(
    ("text", "lang", "expected"),
    [
        # The critic's counterexamples (D9, E1).
        pytest.param(chars(0x0671, 0x0654), "ar", chars(0x0627), id="U+0671 U+0654 ar"),
        pytest.param(
            chars(0x0627, 0x0640, 0x0654), "ckb", chars(0x0627), id="U+0627 U+0640 U+0654 ckb"
        ),
        pytest.param(chars(0x00DF, 0x0307), "en", chars(0x73, 0x1E61), id="U+00DF U+0307 en"),
        pytest.param("ڕ_ری", "ar", "ڕ ري", id="reh joiner ri ar"),
        # The E1 lines' own examples (rows 2, 3 and 11, and the second NFKC's reason).
        pytest.param(
            chars(0x064A, 0x0640, 0x0654), "ar", chars(0x0626), id="U+064A U+0640 U+0654 ar"
        ),
        pytest.param(
            chars(0x06D5, 0x0640, 0x0654), "ckb", chars(0x06C0), id="U+06D5 U+0640 U+0654 ckb"
        ),
        pytest.param(chars(0x0623, 0x0654), "ar", chars(0x0627), id="U+0623 U+0654 ar"),
        pytest.param(chars(0x06CC, 0x0654), "ar", chars(0x0626), id="U+06CC U+0654 ar"),
        pytest.param(
            chars(0x06D5, 0x0640, 0x0654, 0x06CC),
            "ar",
            chars(0x06C0, 0x064A),
            id="U+06D5 U+0640 U+0654 U+06CC ar",
        ),
    ],
)
def test_the_e1_counterexamples_fold_as_specified_and_a_second_fold_changes_nothing(
    text: str, lang: str, expected: str
) -> None:
    once = fold(text, lang)
    assert once == expected, f"{code_points(once)} != {code_points(expected)}"
    assert fold(once, lang) == once
