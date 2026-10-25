import re

from listening_contracts.models.strict import poster_profiles_v1, raw_items_v1
from listening_contracts.registries import (
    D3_WRITERS,
    INDEX_SERVICES,
    PLATFORM_SERVICES,
    context_key_registry,
    decision_rows,
    extras_key_registry,
    is_known_service,
    is_known_vendor,
    producer_rows,
    queue_service,
    raw_items_kinds,
    required_field_rows,
    topic_writers,
)
from listening_contracts.validate import ValidationResult, validate
from listening_contracts.vocabulary import VOCABULARY

from conftest import PACKAGE_DIR, fixture

SPECIAL = {"@queue", "@platform", "@service", "*"}


def _conventions_index() -> list[tuple[str, int, list[str]]]:
    """The service index as CONVENTIONS v1.1 L372 to L384 writes it:
    "Group (n): a, b (amber), ..."."""
    text = (PACKAGE_DIR.parents[1] / "docs" / "prds" / "_shared" / "CONVENTIONS.md").read_text(
        encoding="utf-8"
    )
    start = text.index("## Service index")
    block = text[start : text.index("\n## ", start + 1)]
    groups: list[tuple[str, int, list[str]]] = []
    for line in block.split("\n"):
        m = re.fullmatch(r"([A-Z][A-Za-z ,]*) \((\d+)\): (.+)\.", line)
        if m is None:
            continue
        # Drop the parenthetical notes ("(amber)", "(the one exception to the prefix rule, ...)").
        services = [s.strip() for s in re.sub(r"\s*\([^)]*\)", "", m.group(3)).split(", ")]
        groups.append((m.group(1), int(m.group(2)), services))
    return groups


def test_equals_conventions_service_index_86_services_in_11_groups() -> None:
    groups = _conventions_index()
    assert len(groups) == 11
    for name, count, services in groups:
        assert len(services) == count, name
    from_doc = [s for _, _, services in groups for s in services]
    assert len(from_doc) == 86
    assert sorted(INDEX_SERVICES) == sorted(from_doc)


def test_the_platform_services_are_the_66_of_the_facebook_to_web_groups() -> None:
    groups = _conventions_index()[:9]
    names = [name for name, _, _ in groups]
    assert names == [
        "Facebook",
        "Instagram",
        "TikTok",
        "X",
        "LinkedIn",
        "Telegram",
        "YouTube",
        "News",
        "Web",
    ]
    assert sorted(PLATFORM_SERVICES) == sorted(s for _, _, services in groups for s in services)
    assert len(PLATFORM_SERVICES) == 66


def test_knows_the_index_services_and_the_three_d3_writers_nothing_else() -> None:
    assert is_known_service("fb-page-feed-poller")
    for w in D3_WRITERS:
        assert is_known_service(w)
    assert not is_known_service("admin")
    assert not is_known_service("FB-PAGE-FEED-POLLER")


def test_an_amber_record_names_an_amber_vendor_a_green_one_a_licensed_engine_or_none() -> None:
    assert is_known_vendor("amber", "ensembledata")
    assert not is_known_vendor("amber", None)
    assert not is_known_vendor("amber", "mojeek")
    assert is_known_vendor("green", None)
    assert is_known_vendor("green", "gdelt")
    assert not is_known_vendor("green", "sociavault")
    assert not is_known_vendor("green", "apify_tugelbay")


def _known(s: str) -> bool:
    return s in SPECIAL or is_known_service(s)


def test_every_producer_table_row_names_job_kinds_known_queues_and_known_producers() -> None:
    for row in producer_rows():
        assert row["kind"] in VOCABULARY["JOB_KINDS"]
        assert is_known_service(queue_service(row["queue"])), row["queue"]
        for p in row["producers"]:
            assert is_known_service(p), (row["queue"], row["kind"], p)
    for r in required_field_rows():
        for q in r["queues"]:
            assert is_known_service(queue_service(q)), q
        for k in r["kinds"]:
            assert k in VOCABULARY["JOB_KINDS"]
        for p in r.get("producers", []):
            assert _known(p), p


def test_every_topic_writer_is_known_and_raw_items_lists_each_writers_record_kinds() -> None:
    for schema, writers in topic_writers().items():
        for w in writers:
            assert _known(w), (schema, w)
    raw = topic_writers()["raw.items/v1"]
    assert len(raw) == 56
    for w in raw:
        kinds = raw_items_kinds(w)
        assert kinds is not None, w
        for k in kinds:
            assert k in VOCABULARY["RECORD_KINDS"]


def test_every_decision_row_names_a_type_a_subject_known_producers_and_listed_values() -> None:
    subjects = {"candidate_key", "author_ref", "source_id", "platform", "keyword_id"}
    for row in decision_rows():
        for d in row["decisions"]:
            assert d in VOCABULARY["DECISION_TYPES"]
        assert row["subject"] in subjects
        for p in row["producers"]:
            assert _known(p), p
        for r in row.get("reasons", []):
            assert r is None or r in VOCABULARY["REGISTRY_REASONS"]
        for h in row.get("healths", []):
            assert h in VOCABULARY["HEALTHS"]
        for n in row.get("rule_hits", []):
            assert type(n) is int, n
            assert 1 <= n <= 10, n
        assert row["provenance"] in {"required", "refused", "optional"}


def test_only_raw_items_writers_declare_context_keys_and_only_resolvers_declare_extras_keys() -> (
    None
):
    raw = topic_writers()["raw.items/v1"]
    for service, entry in context_key_registry()["producers"].items():
        assert service in raw
        for k in entry["required"]:
            assert k in entry["keys"], service
    profiles = topic_writers()["poster.profiles/v1"]
    for service in extras_key_registry()["resolvers"]:
        assert service in profiles


# Producer mode checks the registry data (A23; Q1, F-09).


def _fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_producer_mode_refuses_a_service_or_vendor_the_registry_data_does_not_list() -> None:
    f = fixture("item.hits/v1", "valid", "prd-keyword-matcher.json")
    service = f.copy()
    service["producer"]["service"] = "keyword-matcher-v2"
    assert _fails_at(validate("item.hits/v1", service), ["producer", "service"])
    fetcher = f.copy()
    fetcher["provenance"]["service"] = "x-searcher"
    assert _fails_at(validate("item.hits/v1", fetcher), ["provenance", "service"])
    amber = fixture("raw.items/v1", "valid", "prd-tg-channel-posts-poller.json").copy()
    amber["envelope"]["provenance"]["vendor"] = "apify"
    assert _fails_at(validate("raw.items/v1", amber), ["envelope", "provenance", "vendor"])


def test_the_schemas_type_service_names_and_vendors_as_patterned_strings_not_enums() -> None:
    # A name the registry does not list yet passes the consumer, which knows no registry data.
    value = fixture("item.hits/v1", "valid", "prd-keyword-matcher.json").copy()
    value["producer"]["service"] = "keyword-matcher-v2"
    value["provenance"]["vendor"] = "a-new-engine"
    assert validate("item.hits/v1", value, "consumer").ok
    value["producer"]["service"] = "Keyword Matcher"
    assert not validate("item.hits/v1", value, "consumer").ok


def test_the_context_and_extras_models_hold_exactly_the_keys_some_producer_declares() -> None:
    declared = {k for e in context_key_registry()["producers"].values() for k in e["keys"]}
    declared |= {k for e in context_key_registry()["by_kind"].values() for k in e["keys"]}
    assert sorted(raw_items_v1.Context.model_fields) == sorted(declared)
    resolver_keys = {k for keys in extras_key_registry()["resolvers"].values() for k in keys}
    assert sorted(poster_profiles_v1.Extras.model_fields) == sorted(resolver_keys)
