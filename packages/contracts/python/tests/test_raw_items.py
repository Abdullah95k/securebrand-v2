"""A20: raw.items/v1's envelope, record kinds and declared context (ADR-0005, ADR-0008,
ADR-0009)."""

from listening_contracts.registries import context_key_registry
from listening_contracts.validate import ValidationResult, validate
from listening_contracts.vocabulary import CONTENT_KINDS

from conftest import fixture, fixtures

ID = "raw.items/v1"
VALID = fixtures(ID, "valid")


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_accepts_each_producers_declared_context() -> None:
    registry = context_key_registry()
    for service, declared in registry["producers"].items():
        own = [f for f in VALID if f.value["envelope"]["producer"]["service"] == service]
        assert own, f"{service} has a valid fixture"
        seen = {k for f in own for k in f.value["envelope"].get("context", {})}
        seen.discard("item_key")
        assert sorted(seen) == sorted(declared["keys"]), service
    metrics = [f for f in VALID if f.value["envelope"]["kind"] == "metrics"]
    assert metrics
    for f in metrics:
        assert "item_key" in f.value["envelope"]["context"], f.name


def test_rejects_an_undeclared_context_key() -> None:
    value = fixture(ID, "valid", "prd-fb-page-feed-poller.json").copy()
    value["envelope"]["context"] = {"query_arm": "brand"}  # x-recent-search's key
    assert fails_at(validate(ID, value), ["envelope", "context", "query_arm"])
    # Context types hold in both modes; who may use a key is producer-mode registry data.
    assert validate(ID, value, "consumer").ok


def test_requires_platform_id_and_idempotency_key_on_item_kinds() -> None:
    for kind in CONTENT_KINDS:
        f = next(x for x in VALID if x.value["envelope"]["kind"] == kind)
        for name in ("platform_id", "idempotency_key"):
            value = f.copy()
            del value["envelope"][name]
            assert fails_at(validate(ID, value), ["envelope", name]), (kind, name)


def test_requires_parent_id_and_root_id_on_comments() -> None:
    f = fixture(ID, "valid", "prd-yt-replies-fetcher.json")
    assert f.value["envelope"]["kind"] == "comment"
    for name in ("parent_id", "root_id"):
        value = f.copy()
        del value["envelope"][name]
        assert fails_at(validate(ID, value), ["envelope", name]), name


def test_accepts_candidate_key_instead_of_source_id_on_any_record_kind_about_a_candidate() -> None:
    about = [f for f in VALID if "candidate_key" in f.value["envelope"]]
    kinds = {f.value["envelope"]["kind"] for f in about}
    assert {"profile", "post"} <= kinds
    post = fixture(ID, "valid", "post-about-a-candidate.json")
    assert post.value["envelope"]["producer"]["service"] == "li-org-resolver"
    assert "source_id" not in post.value["envelope"]
    assert validate(ID, post.value).ok


def test_requires_author_ref_null_allowed_on_comment_and_reaction_records() -> None:
    for file in ("prd-ig-own-comments-fetcher.json", "reaction.json"):
        f = fixture(ID, "valid", file)
        missing = f.copy()
        del missing["envelope"]["author_ref"]
        assert fails_at(validate(ID, missing), ["envelope", "author_ref"]), file
        nulled = f.copy()
        nulled["envelope"]["author_ref"] = None
        assert validate(ID, nulled).ok, file
