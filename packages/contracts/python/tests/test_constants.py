"""Finding 6: Pydantic matches a literal by equality, even in strict mode (0 == False and
True == 1), so validate() checks that a constant keeps its JSON type, as Zod and the JSON Schema
`const` do. These are the 20 literal sites of the strict models, each given as the other JSON
type."""

from typing import Any

from listening_contracts.validate import validate

from conftest import fixture, schema_id_of

SITES: list[tuple[str, str, list[str | int], object]] = [
    ("job/v1", "rotation.json", ["tier"], True),
    ("poster.profiles/v1", "individual.json", ["individual"], 1),
    ("poster.profiles/v1", "individual.json", ["public_account"], 0),
    ("poster.profiles/v1", "prd-news-site-resolver.json", ["extras", "proposed_tier"], True),
    ("item.hits/v1", "source-match.json", ["occurrences"], False),
    ("registry.decisions/v1", "tier-change-profile.json", ["tier_change", "tier"], True),
    ("registry.decisions/v1", "update-refreshed-profile.json", ["update", "source", "tier"], True),
    ("registry.decisions/v1", "prd-qualifier.json", ["add", "source", "tier"], True),
    ("crawl.policies/v1", "prd-news-robots-checker.json", ["rsl", "found"], 0),
    ("crawl.policies/v1", "rsl-payment.json", ["rsl", "found"], 1),
    ("raw.items/v1", "prd-yt-keyword-search.json", ["envelope", "context", "partial"], 1),
    ("source.events/v1", "tier-change.json", ["previous", "tier"], True),
    ("source.events/v1", "prd-registry-writer.json", ["tier"], True),
    ("source.events/v1", "updated-client-removed.json", ["tier"], True),
    ("source.events/v1", "tier-change.json", ["tier"], True),
    ("source.events/v1", "lifecycle-dormant.json", ["tier"], True),
    ("source.events/v1", "health-change.json", ["tier"], True),
    ("source.events/v1", "fallback-on.json", ["tier"], True),
    ("source.events/v1", "fallback-off-flag-off.json", ["tier"], True),
    ("source.events/v1", "push-coverage-change.json", ["tier"], True),
]


def _set(value: Any, path: list[str | int], to: object) -> None:
    for step in path[:-1]:
        value = value[step]
    value[path[-1]] = to


def test_refuses_a_constant_given_as_the_other_json_type() -> None:
    """0 for false, true for 1: refused at the field with literal_error, in both modes."""
    for directory, file, path, swapped in SITES:
        f = fixture(directory, "valid", file)
        value = f.copy()
        _set(value, path, swapped)
        for mode in ("producer", "consumer"):
            result = validate(schema_id_of(directory), value, mode, **f.options)
            codes = [i["code"] for i in result.issues if i["path"] == path]
            assert codes == ["literal_error"], (file, path, mode, result.issues[:3])
