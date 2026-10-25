"""The package root carries what a Python service calls, as the TypeScript root does."""

import listening_contracts
from listening_contracts import keys, registries


def test_the_package_root_exports_what_a_service_calls() -> None:
    root = vars(listening_contracts)
    for name in [
        "validate",
        "classify_version",
        "catalogue_id",
        "canonical_json",
        "idempotency_key",
        "parse_key",
        "item_id",
        "hit_id",
        "card_id",
        "author_ref",
        "content_hash",
        "deletion_id",
        "normalise_url",
        "query_key",
        "raw_ref",
        "deterministic_ulid",
        "partition_key",
        "is_allowed_producer",
        "is_allowed_topic_writer",
        "is_allowed_decision_producer",
        "visibility_of",
        "sign_n8n",
        "verify_n8n",
    ]:
        assert callable(root.get(name)), name
    assert {"raw.items/v1", "n8n.card/v1"} <= set(listening_contracts.SCHEMA_IDS)
    assert listening_contracts.NS_ITEMS == keys.NS_ITEMS
    assert "tiktok" in listening_contracts.PLATFORMS
    assert issubclass(listening_contracts.ContractError, Exception)


def test_every_name_in_all_is_defined() -> None:
    for name in listening_contracts.__all__:
        assert hasattr(listening_contracts, name), name


def test_the_root_helpers_are_the_modules_helpers() -> None:
    assert listening_contracts.item_id is keys.item_id
    assert listening_contracts.partition_key is registries.partition_key
