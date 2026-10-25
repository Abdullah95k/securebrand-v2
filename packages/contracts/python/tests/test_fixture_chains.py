"""The fixtures' chains (review note 21): the ids a consumer copies, the keys the helpers derive,
and individuals present only as references under the published test key, from invented ids (D-8);
the twin of test/unit/fixture-chains.test.ts."""

import re
from typing import Any, cast

from listening_contracts.keys import author_ref, item_id

from conftest import FixtureKind, fixture, fixtures, golden, schema_dirs

# The invented authors of the fixture generator (scripts/fixtures/); a fixture carries their
# references only. Any other author_ref in a fixture is a literal, which D-8 rules out.
INVENTED_AUTHORS = (
    ("facebook", "1234567890"),
    ("facebook", "1000000000000000011"),
    ("facebook", "1000000000000000012"),
    ("facebook", "1000000000000000013"),
    ("instagram", "17841455555555555"),
    ("instagram", "17841466666666666"),
    ("linkedin", "ACoAAB1234567"),
    ("linkedin", "urn:li:person:Ab12Cd34"),
    ("linkedin", "urn:li:person:Ef56Gh78"),
    ("linkedin", "urn:li:person:Ij90Kl12"),
    ("news", "disqus:9418273650"),
    ("telegram", "5210987654"),
    ("tiktok", "6800000000000000999"),
    ("x", "1000000000000000001"),
    ("x", "1290000000000000077"),
    ("youtube", "UCaaaaaaaaaaaaaaaaaaaaaa"),
    ("youtube", "UCbbbbbbbbbbbbbbbbbbbbbb"),
)
KINDS: tuple[FixtureKind, ...] = ("valid", "invalid", "tolerant")


def _value(directory: str, file: str) -> dict[str, Any]:
    return fixture(directory, "valid", file).value


def _author_refs(value: object, out: list[str]) -> list[str]:
    """Every reference under an `author_ref` key, anywhere in `value` (a malformed one is a format
    case)."""
    if isinstance(value, list):
        for v in cast(list[object], value):
            _author_refs(v, out)
    elif isinstance(value, dict):
        for k, v in cast(dict[str, object], value).items():
            if k == "author_ref" and isinstance(v, str) and re.fullmatch("[0-9a-f]{64}", v):
                out.append(v)
            else:
                _author_refs(v, out)
    return out


def test_a_topic_consumer_copies_its_inputs_producer_job_id_along_the_poster_chain() -> None:
    profile = _value("poster.profiles/v1", "prd-poster-resolver.json")
    decision = _value("registry.decisions/v1", "prd-qualifier.json")
    event = _value("source.events/v1", "prd-registry-writer.json")
    assert decision["producer"]["job_id"] == profile["producer"]["job_id"]
    assert event["producer"]["job_id"] == decision["producer"]["job_id"]


def test_each_first_sight_job_carries_the_job_id_of_its_sibling_raw_record() -> None:
    jobs = [f for f in fixtures("job/v1", "valid") if f.value.get("kind") == "first_sight"]
    assert jobs
    for job in jobs:
        raw = _value("raw.items/v1", job.file)
        assert job.value["producer"]["job_id"] == raw["envelope"]["job_id"], job.name


def test_news_dedups_duplicate_names_the_extractors_article_by_its_key() -> None:
    verdict = _value("news.dedup/v1", "prd-news-dedup.json")
    article = _value("raw.items/v1", "prd-news-article-extractor.json")
    assert verdict["duplicate_of"] == article["envelope"]["idempotency_key"]


def test_a_public_persons_url_is_its_own_handles() -> None:
    person = _value("poster.profiles/v1", "public-person-individual.json")
    assert person["url"].endswith(f"/{person['handle']}")


def test_a_container_candidate_is_the_group_its_items_raw_record_names() -> None:
    hit = _value("discovery.hits/v1", "container-group.json")
    # The record keyword-matcher read: the hit's item, from the service its provenance names.
    service = hit["provenance"]["service"]
    raw = [
        f
        for f in fixtures("raw.items/v1", "valid")
        if f.value["envelope"]["provenance"]["service"] == service
        and "idempotency_key" in f.value["envelope"]
        and item_id(f.value["envelope"]["idempotency_key"]) == hit["item_id"]
    ]
    assert raw, "a raw record of the hit's item"
    for f in raw:
        context = f.value["payload"]["context"]
        assert context["type"] == "group", f.name
        assert context["id"] == hit["candidate"]["platform_id"], f.name
        assert context["name"] == hit["evidence"]["name"], f.name


def test_every_author_ref_in_the_fixtures_is_derived_under_the_test_key_from_an_invented_id() -> (
    None
):
    key = golden("author-ref.json")["test_key_utf8"].encode("utf-8")
    known = {author_ref(key, platform, pid) for platform, pid in INVENTED_AUTHORS}
    unknown: list[str] = []
    for directory in schema_dirs():
        for kind in KINDS:
            for f in fixtures(directory, kind):
                unknown += [f"{f.name} {r}" for r in _author_refs(f.value, []) if r not in known]
    partition_keys = _author_refs(golden("partition-keys.json"), [])
    unknown += [f"golden/partition-keys.json {r}" for r in partition_keys if r not in known]
    assert unknown == []
