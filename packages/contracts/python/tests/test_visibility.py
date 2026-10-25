from typing import Any

from listening_contracts.registries import (
    raw_items_kinds,
    topic_writers,
    visibility_of,
    visibility_rule,
)
from listening_contracts.vocabulary import CONTENT_KINDS

from conftest import FIXTURES_DIR, read_json

# search-hit-router's `result` records carry the engine's provenance (ADR-0003 L25, ADR-0038 L26),
# so the engines that feed web:result items are the services the gate reads for them (F-18).
WEB_RESULT_ENGINES = ["web-search-perplexity", "web-search-mojeek", "yt-web-search-bridge"]


def test_every_service_that_can_appear_as_provenance_service_on_a_content_kind_declares_one() -> (
    None
):
    writers = [
        w
        for w in topic_writers()["raw.items/v1"]
        if w != "search-hit-router" and any(k in CONTENT_KINDS for k in raw_items_kinds(w) or [])
    ]
    assert len(writers) > 40
    for w in [*writers, *WEB_RESULT_ENGINES]:
        assert visibility_rule(w) is not None, w


def test_a_web_result_fixtures_provenance_service_declares_a_visibility() -> None:
    results: list[dict[str, Any]] = []
    for path in sorted((FIXTURES_DIR / "raw.items" / "v1" / "valid").glob("*.json")):
        message = read_json(path)
        if message.get("envelope", {}).get("kind") == "result":
            results.append(message)
    assert results
    for m in results:
        service = m["envelope"]["provenance"]["service"]
        assert service in WEB_RESULT_ENGINES
        assert visibility_of(service, owned_by_client=False) == "pool"


def test_client_owned_sources_resolve_to_owner() -> None:
    assert visibility_of("fb-page-feed-poller", owned_by_client=True) == "owner"
    assert visibility_of("fb-page-feed-poller", owned_by_client=False) == "watchers"
    assert visibility_of("tg-bot-channel-receiver", owned_by_client=True) == "owner"
    assert visibility_of("tg-bot-channel-receiver", owned_by_client=False) == "pool"
    assert visibility_of("li-client-posts-poller", owned_by_client=False) == "owner"
    assert visibility_of("ig-hashtag-search", owned_by_client=True) == "watchers"


def test_names_the_client_filter_on_top_of_pool_amber_consent_and_the_x_gate() -> None:
    assert visibility_rule("tt-keyword-search") == {"rule": "pool", "limit": "amber"}
    assert visibility_rule("x-recent-search") == {"rule": "pool", "limit": "x_gate"}
    assert visibility_rule("yt-keyword-search") == {"rule": "pool", "limit": None}


def test_a_service_whose_records_never_become_client_facing_items_declares_none() -> None:
    for s in [
        "fb-page-resolver",
        "web-gdelt-poller",
        "web-commoncrawl-scanner",
        "fb-reactions-fetcher",
        "search-hit-router",
        "news-feed-poller",
    ]:
        assert visibility_rule(s) is None, s
        assert visibility_of(s, owned_by_client=False) is None, s
