import itertools

import pytest

from listening_contracts.registries import (
    D3_WRITERS,
    INDEX_SERVICES,
    DecisionQuery,
    allowed_producers,
    decision_row,
    decision_rows,
    is_allowed_decision_producer,
    is_allowed_producer,
    is_allowed_topic_writer,
    is_known_service,
    names_service,
    producer_rows,
    required_job_fields,
)
from listening_contracts.vocabulary import VOCABULARY

# The qualifier's ten rules (qualifier §5.2), the values a decision's rule_hit takes.
RULE_HITS = list(range(1, 11))


def test_refuses_a_queue_kind_producer_service_the_table_does_not_list() -> None:
    assert is_allowed_producer("jobs.fb-page-feed-poller", "rotation", "fb-page-feed-poller")
    assert not is_allowed_producer(
        "jobs.fb-page-feed-poller", "rotation", "comment-decay-scheduler"
    )
    assert not is_allowed_producer(
        "jobs.fb-page-feed-poller", "comments", "comment-decay-scheduler"
    )
    assert is_allowed_producer(
        "jobs.fb-post-comments-fetcher", "comments", "comment-decay-scheduler"
    )
    assert is_allowed_producer("jobs.x-recent-search", "reconciliation", "x-filtered-stream")
    assert not is_allowed_producer(
        "jobs.x-user-timeline-poller", "reconciliation", "x-filtered-stream"
    )


def test_an_unknown_queue_kind_has_no_producers() -> None:
    assert allowed_producers("jobs.no-such-service", "rotation") == []
    assert allowed_producers("jobs.store-writer", "rotation") == []
    assert allowed_producers("jobs.qualifier", "resolve") == []


def test_names_the_queues_own_service_for_queue_rows_the_analysis_priority_lanes_included() -> None:
    assert is_allowed_producer("jobs.analysis-sentiment.priority", "analyze", "analysis-sentiment")
    assert not is_allowed_producer("jobs.analysis-sentiment.priority", "analyze", "analysis-topics")
    assert is_allowed_producer("jobs.analysis-media", "rerun", "admin-api")
    assert not is_allowed_producer("jobs.analysis-media.priority", "rerun", "admin-api")
    assert is_allowed_producer("jobs.yt-pubsub-receiver", "push", "yt-pubsub-receiver")


def test_gives_ops_and_client_requests_one_writer_the_admin_api() -> None:
    assert is_allowed_producer("jobs.qualifier", "review_answer", "admin-api")
    assert is_allowed_producer("jobs.x-compliance-sync", "export", "admin-api")
    assert is_allowed_producer("jobs.normalize-item", "replay", "admin-api")
    assert is_allowed_producer("jobs.keyword-matcher", "rematch", "admin-api")
    assert not is_allowed_producer("jobs.keyword-matcher", "rematch", "client-portal")
    assert is_allowed_producer("jobs.ig-mentions-fetcher", "ops_force", "ig-webhook-receiver")
    assert is_allowed_producer("jobs.ig-mentions-fetcher", "ops_force", "admin-api")


@pytest.mark.parametrize(
    ("queue", "kind", "service", "fields"),
    [
        ("jobs.ig-hashtag-search", "rotation", "ig-hashtag-search", ["edge"]),
        ("jobs.ig-hashtag-search", "backfill", "backfill-orchestrator", ["edge"]),
        (
            "jobs.x-recent-search",
            "reconciliation",
            "x-filtered-stream",
            ["query", "window_start", "window_end", "source_ids", "client_ids"],
        ),
        ("jobs.x-recent-search", "reconciliation", "x-recent-search", []),
        (
            "jobs.yt-comments-fetcher",
            "refresh",
            "yt-text-purger",
            ["post_ref", "run_id", "must_finish_by", "refresh_for_client_ids"],
        ),
        (
            "jobs.news-site-resolver",
            "refresh",
            "news-site-resolver",
            ["candidate_key", "source_id"],
        ),
        (
            "jobs.news-site-resolver",
            "refresh",
            "news-feed-poller",
            ["candidate_key", "source_id", "reason"],
        ),
        ("jobs.web-commoncrawl-scanner", "rotation", "web-commoncrawl-scanner", ["crawl_id"]),
        ("jobs.yt-replies-fetcher", "replies", "comment-decay-scheduler", ["post_ref.thread_ids"]),
        ("jobs.x-full-archive-search", "replies", "comment-decay-scheduler", ["window_start"]),
        ("jobs.aggregator", "recompute", "admin-api", ["from", "to", "request_id", "requested_by"]),
    ],
)
def test_names_the_required_kind_fields_of_the_rows_that_need_them(
    queue: str, kind: str, service: str, fields: list[str]
) -> None:
    assert required_job_fields(queue, kind, service) == fields


def test_names_only_services_of_the_service_index_or_the_d3_writers() -> None:
    named = {p for r in producer_rows() for p in r["producers"]} | {
        p for r in decision_rows() for p in r["producers"] if p not in ("@platform", "*")
    }
    for p in named:
        assert is_known_service(p), p
    for w in D3_WRITERS:
        assert w in named


def _source(decision: str, reason: str | None, health: str | None = None) -> DecisionQuery:
    return {"decision": decision, "subject": "source_id", "reason": reason, "health": health}


def test_allows_the_admin_apis_flag_off_and_flag_on_decisions() -> None:
    assert is_allowed_decision_producer(
        _source("health_change", "flag_off", "blocked"), "admin-api"
    )
    assert is_allowed_decision_producer(_source("health_change", "flag_on", "blocked"), "admin-api")
    assert not is_allowed_decision_producer(
        _source("health_change", "flag_off", "blocked"), "fb-page-feed-poller"
    )


def test_allows_the_admin_apis_clearing_health_change_only_with_ok_and_a_non_flag_reason() -> None:
    assert is_allowed_decision_producer(_source("health_change", "bot_removed", "ok"), "admin-api")
    assert is_allowed_decision_producer(
        _source("health_change", "crawl_disallowed", "ok"), "admin-api"
    )
    assert not is_allowed_decision_producer(
        _source("health_change", "bot_removed", "blocked"), "admin-api"
    )
    assert not is_allowed_decision_producer(
        _source("health_change", "bot_removed", "degraded"), "admin-api"
    )
    assert not is_allowed_decision_producer(_source("health_change", "flag_off", "ok"), "admin-api")


def test_refuses_a_source_level_flag_off_or_flag_on_with_a_health_other_than_blocked() -> None:
    assert not is_allowed_decision_producer(
        _source("health_change", "flag_off", "degraded"), "admin-api"
    )
    assert not is_allowed_decision_producer(_source("health_change", "flag_on", "ok"), "admin-api")


def test_accepts_the_canarys_route_level_flag_off_with_degraded() -> None:
    route: DecisionQuery = {
        "decision": "health_change",
        "subject": "platform",
        "reason": "flag_off",
        "health": "degraded",
    }
    assert is_allowed_decision_producer(route, "source-health-canary")
    assert not is_allowed_decision_producer(route, "admin-api")


def test_lets_any_service_report_credential_revoked_never_as_degraded() -> None:
    blocked = _source("health_change", "credential_revoked", "blocked")
    assert is_allowed_decision_producer(blocked, "fb-page-feed-poller")
    assert is_allowed_decision_producer(blocked, "normalize-item")
    degraded = _source("health_change", "credential_revoked", "degraded")
    assert not is_allowed_decision_producer(degraded, "fb-page-feed-poller")


@pytest.mark.parametrize(
    ("query", "service", "provenance"),
    [
        ({"decision": "add", "subject": "candidate_key", "reason": None}, "qualifier", "required"),
        ({"decision": "add", "subject": "source_id", "reason": None}, "client-portal", "refused"),
        (
            {"decision": "add", "subject": "source_id", "reason": None},
            "tg-bot-channel-receiver",
            "required",
        ),
        ({"decision": "add", "subject": "keyword_id", "reason": None}, "admin-console", "refused"),
        (
            {"decision": "update", "subject": "source_id", "reason": None},
            "ig-hashtag-search",
            "required",
        ),
        (
            {"decision": "update", "subject": "source_id", "reason": "budget_wait"},
            "ig-hashtag-search",
            "refused",
        ),
        (
            {"decision": "remove_client", "subject": "source_id", "reason": "client_removed"},
            "retention-purger",
            "refused",
        ),
        (
            {"decision": "tier_change", "subject": "source_id", "reason": None, "rule_hit": 6},
            "qualifier",
            "required",
        ),
        (
            {"decision": "tier_change", "subject": "source_id", "reason": None, "rule_hit": 10},
            "qualifier",
            "required",
        ),
        (
            {"decision": "tier_change", "subject": "source_id", "reason": None, "rule_hit": 9},
            "qualifier",
            "refused",
        ),
        (
            {"decision": "dormant", "subject": "source_id", "reason": None, "rule_hit": 9},
            "qualifier",
            "refused",
        ),
        (
            {"decision": "dormant", "subject": "source_id", "reason": None, "rule_hit": 3},
            "qualifier",
            "optional",
        ),
        (
            {"decision": "promote", "subject": "source_id", "reason": None},
            "yt-uploads-reconciler",
            "required",
        ),
        ({"decision": "promote", "subject": "source_id", "reason": None}, "qualifier", "refused"),
        (
            {"decision": "retire", "subject": "source_id", "reason": "owner_request"},
            "retention-purger",
            "refused",
        ),
        (
            {"decision": "retire", "subject": "source_id", "reason": "authorization_revoked"},
            "tt-client-videos-fetcher",
            "required",
        ),
        (
            {"decision": "retire", "subject": "source_id", "reason": "not_found"},
            "yt-channel-resolver",
            "required",
        ),
        (
            {"decision": "push_coverage", "subject": "source_id", "reason": "lease_lapsed"},
            "yt-pubsub-receiver",
            "refused",
        ),
        (
            {
                "decision": "health_change",
                "subject": "source_id",
                "reason": "crawl_disallowed",
                "health": "blocked",
            },
            "news-robots-checker",
            "required",
        ),
        (
            {
                "decision": "health_change",
                "subject": "platform",
                "reason": "empty_200_rate",
                "health": "fallback",
            },
            "source-health-canary",
            "required",
        ),
        (
            {"decision": "review", "subject": "candidate_key", "reason": "age_gated"},
            "qualifier",
            "required",
        ),
        (
            {"decision": "mention_only", "subject": "author_ref", "reason": None},
            "qualifier",
            "required",
        ),
    ],
)
def test_requires_accepts_or_refuses_provenance_on_each_decision_row_as_its_column_says(
    query: DecisionQuery, service: str, provenance: str
) -> None:
    row = decision_row(query, service)
    assert row is not None
    assert row["provenance"] == provenance


def test_no_two_rows_that_match_one_decision_give_it_different_provenance() -> None:
    services = [*INDEX_SERVICES, *D3_WRITERS]
    rows = decision_rows()
    for row in rows:
        reasons: list[str | None] = list(
            row.get("reasons", [None, *VOCABULARY["REGISTRY_REASONS"]])
        )
        healths: list[str | None] = list(row.get("healths", [None, *VOCABULARY["HEALTHS"]]))
        rule_hits: list[int | None] = list(row.get("rule_hits", [None, *RULE_HITS]))
        candidates = [s for s in services if names_service(row["producers"], s)]
        for decision, service, reason, health, rule_hit in itertools.product(
            row["decisions"], candidates, reasons, healths, rule_hits
        ):
            matches = [
                r
                for r in rows
                if decision in r["decisions"]
                and r["subject"] == row["subject"]
                and names_service(r["producers"], service)
                and ("reasons" not in r or reason in r["reasons"])
                and ("healths" not in r or (health is not None and health in r["healths"]))
                and ("rule_hits" not in r or (rule_hit is not None and rule_hit in r["rule_hits"]))
            ]
            assert len({r["provenance"] for r in matches}) == 1, (
                decision,
                service,
                reason,
                health,
                rule_hit,
            )


def test_refuses_a_decision_type_from_a_producer_no_row_lists() -> None:
    push: DecisionQuery = {"decision": "push_coverage", "subject": "source_id", "reason": None}
    assert not is_allowed_decision_producer(push, "ig-webhook-receiver")
    retire: DecisionQuery = {
        "decision": "retire",
        "subject": "source_id",
        "reason": "owner_request",
    }
    assert not is_allowed_decision_producer(retire, "qualifier")
    add: DecisionQuery = {"decision": "add", "subject": "candidate_key", "reason": None}
    assert not is_allowed_decision_producer(add, "poster-resolver")
    # The qualifier's tier_change and dormant are bound to their rule (D-3).
    for decision, rule_hit in (("tier_change", 4), ("dormant", 6), ("tier_change", None)):
        query: DecisionQuery = {
            "decision": decision,
            "subject": "source_id",
            "reason": None,
            "rule_hit": rule_hit,
        }
        assert not is_allowed_decision_producer(query, "qualifier"), (decision, rule_hit)


def test_allows_each_topics_writers_and_refuses_the_rest() -> None:
    assert is_allowed_topic_writer("item.hits/v1", "keyword-matcher")
    assert not is_allowed_topic_writer("item.hits/v1", "normalize-item")
    assert is_allowed_topic_writer("source.events/v1", "registry-writer")
    assert not is_allowed_topic_writer("source.events/v1", "qualifier")


def test_restricts_a_raw_items_writer_to_its_record_kinds() -> None:
    assert is_allowed_topic_writer("raw.items/v1", "fb-page-resolver", kind="profile")
    assert not is_allowed_topic_writer("raw.items/v1", "fb-page-resolver", kind="post")
    assert is_allowed_topic_writer("raw.items/v1", "li-org-resolver", kind="post")
    assert is_allowed_topic_writer("raw.items/v1", "search-hit-router", kind="result")
    assert not is_allowed_topic_writer("raw.items/v1", "tt-user-resolver", kind="profile")
    assert not is_allowed_topic_writer("raw.items/v1", "tt-video-stats-refresher", kind="metrics")


def test_names_the_service_behind_a_jobs_completed_report_and_a_dead_letter() -> None:
    assert is_allowed_topic_writer(
        "jobs.completed/v1", "x-recent-search", queue="jobs.x-recent-search"
    )
    assert not is_allowed_topic_writer(
        "jobs.completed/v1", "x-filtered-stream", queue="jobs.x-recent-search"
    )
    assert is_allowed_topic_writer("dlq.normalize-item/v1", "normalize-item")
    assert not is_allowed_topic_writer("dlq.normalize-item/v1", "store-writer")


def test_registry_decisions_writers_are_the_decision_rows_producers() -> None:
    assert is_allowed_topic_writer("registry.decisions/v1", "qualifier")
    assert is_allowed_topic_writer("registry.decisions/v1", "client-portal")
    assert is_allowed_topic_writer("registry.decisions/v1", "store-writer")  # credential_revoked
    assert not is_allowed_topic_writer("registry.decisions/v1", "nobody")
