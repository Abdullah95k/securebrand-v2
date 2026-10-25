"""Fixtures for the n8n notices: n8n.alert/v1 (alert-evaluator's alert/v1 rewritten, every
rule_type, the automatic-fallback notice and the facts notice) and n8n.card/v1 (each card_type),
with the government rule (Q11; ADR-0067, ADR-0048)."""

from typing import Any

from common import (
    CLIENT,
    CLIENT2,
    invalid,
    meta,
    metadata_invalids,
    prd,
    ref,
    tolerant,
    ulid_for,
    valid,
    with_,
    without,
)

from listening_contracts.keys import card_id

PERSON_SOURCE = "a3c0f1e2-5b6d-4c7e-9f80-112233445566"
KEYWORD = "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3"
RULE = "5d0c2b7e-8a14-4f63-b9e1-2c7a6d4f0e18"
GOV_CLIENT = "c7f12d45-b7c5-467d-aa82-e7826ed8abf2"


def alerts() -> None:
    s = "n8n.alert/v1"
    alert_id = "01J9W5A2M7Q0R4T8V1X3Y5Z7B9"
    window = {
        "hour": "2026-10-06T08:00:00Z",
        "elapsed_fraction": 0.62,
        "evaluated_at": "2026-10-06T08:37:12Z",
    }
    keyword = {"keyword_id": KEYWORD, "label": "زين العراق", "purpose": "service_quality"}

    def alert(
        name: str,
        at: str,
        aid: str,
        channel: str,
        audience: str,
        client_id: str | None,
        alert_name: str,
        severity: str,
        subject: dict[str, Any],
        summary: str,
        details: dict[str, Any],
        fallthrough: str | None = None,
        service: str = "alert-evaluator",
    ) -> dict[str, Any]:
        return {
            **meta(s, service, ulid_for(at, "run", service, name), at, name=name),
            "alert_id": aid,
            "idempotency_key": f"{aid}:{channel}",
            "channel": channel,
            "fallthrough_channel": fallthrough,
            "audience": audience,
            "client_id": client_id,
            "alert": alert_name,
            "severity": severity,
            "subject": subject,
            "summary": summary,
            "details": details,
        }

    def client_alert(
        rule_type: str, metrics: dict[str, Any], scope: dict[str, Any], **extra: Any
    ) -> dict[str, Any]:
        return {
            "rule_id": RULE,
            "rule_type": rule_type,
            "renotify": False,
            "keyword": keyword,
            "scope": scope,
            "window": window,
            "fingerprint": f"{rule_type}:5d0c2b7e:a3c0f1e2",
            "cooldown_until": "2026-10-06T10:37:12Z",
            "metrics": metrics,
            **extra,
        }

    source_scope = {
        "level": "keyword_source",
        "platform": "facebook",
        "source": {"source_id": PERSON_SOURCE, "display_name": "Example Page"},
    }
    spike = alert(
        "prd",
        "2026-10-06T08:37:12Z",
        alert_id,
        "telegram",
        "client",
        CLIENT2,
        "volume_spike",
        "high",
        {"source_id": PERSON_SOURCE, "platform": "facebook", "keyword_id": KEYWORD},
        "زين العراق: 41 إشارة من Example Page منذ الثامنة، سبعة أضعاف المعتاد",
        client_alert(
            "volume_spike",
            {
                "mentions_so_far": 41,
                "baseline_median_same_hour": 9.4,
                "expected_so_far": 5.8,
                "ratio": 7.1,
                "baseline_days": 7,
            },
            source_scope,
        ),
        fallthrough="email",
    )
    valid(s, "prd-alert-evaluator", spike, client_type="commercial")
    prd(
        "alert-evaluator",
        "docs/prds/shared/alert-evaluator.md",
        86,
        s,
        "prd-alert-evaluator",
        [
            "schema alert/v1 becomes n8n.alert/v1, with message_id, produced_at and producer (ADR-0067 L25, ADR-0002)",
            "rule_id, rule_type, renotify, keyword, scope, window, metrics, fingerprint and cooldown_until move into details, the client-alert branch discriminated on rule_type (Q11, F-22)",
            "idempotency_key <alert_id>:<channel>, channel and fallthrough_channel added: one notice per alert and channel (alert-evaluator §5.3 L69; F-23)",
            "audience client beside client_id (F-46); alert names the rule, subject the source, platform and keyword (Q11)",
            "summary added: the one line a channel shows",
        ],
    )

    others: list[tuple[str, dict[str, Any], dict[str, Any]]] = [
        (
            "negative_share",
            {"negative": 18, "total": 30, "share": 0.6, "baseline_share": 0.22},
            source_scope,
        ),
        ("new_high_reach_poster", {"followers": 412000, "mentions": 3}, source_scope),
        ("keyword_first_seen", {"mentions": 1}, {"level": "keyword"}),
        (
            "post_deleted_high_reach",
            {"reach": 250000},
            {**source_scope, "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f"},
        ),
        (
            "engagement_spike",
            {"engagement": 2400, "baseline": 310, "ratio": 7.7},
            {**source_scope, "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f"},
        ),
        (
            "topic_spike",
            {"mentions": 64, "baseline": 12, "ratio": 5.3},
            {"level": "keyword_topic", "topic_id": "global:outage"},
        ),
        (
            "entity_or_logo",
            {"mentions": 9},
            {"level": "keyword_entity", "entity_id": "kb-pl-0007", "brand_id": "brand-0042"},
        ),
        (
            "story",
            {"articles": 5, "outlets": 4},
            {"level": "keyword_story", "story_id": "01J9N4W6C2R8T5K1V7X3M0DPZA"},
        ),
    ]
    by_type: dict[str, dict[str, Any]] = {"volume_spike": spike}
    for i, (rule_type, metrics, scope) in enumerate(others):
        aid = ulid_for("2026-10-06T08:40:00Z", "alert", rule_type)
        subject: dict[str, Any] = {"keyword_id": KEYWORD}
        if "source" in scope:
            subject = {"source_id": PERSON_SOURCE, "platform": "facebook", "keyword_id": KEYWORD}
        msg = alert(
            rule_type,
            f"2026-10-06T08:4{i}:00Z",
            aid,
            "email",
            "client",
            CLIENT2,
            rule_type,
            "warning",
            subject,
            f"زين العراق: {rule_type}",
            client_alert(rule_type, metrics, scope),
        )
        by_type[rule_type] = msg
        valid(s, rule_type.replace("_", "-"), msg, client_type="commercial")

    gov = alert(
        "government",
        "2026-10-06T08:38:00Z",
        ulid_for("2026-10-06T08:38:00Z", "alert", "government"),
        "email",
        "client",
        GOV_CLIENT,
        "volume_spike",
        "high",
        {"keyword_id": KEYWORD},
        "ارتفاع الإشارات إلى الكلمة المتابعة",
        client_alert(
            "volume_spike",
            {
                "mentions_so_far": 120,
                "baseline_median_same_hour": 30.5,
                "expected_so_far": 18.9,
                "ratio": 6.3,
                "baseline_days": 7,
            },
            {"level": "keyword"},
        ),
    )
    valid(s, "government-keyword-level", gov, client_type="government")
    route_fallback = alert(
        "route-fallback",
        "2026-10-06T11:30:05Z",
        ulid_for("2026-10-06T11:30:05Z", "alert", "fallback"),
        "slack",
        "ops",
        None,
        "automatic_fallback",
        "warning",
        {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
        "tiktok amber: tikhub returns empty pages; ensembledata takes over",
        {
            "subject_kind": "route",
            "platform": "tiktok",
            "route": "amber",
            "reason": "empty_200_rate",
            "vendor": "ensembledata",
        },
        service="registry-writer",
    )
    valid(s, "route-fallback-notice", route_fallback)
    source_fallback = alert(
        "source-fallback",
        "2026-10-07T09:00:05Z",
        ulid_for("2026-10-07T09:00:05Z", "alert", "source-fallback"),
        "email",
        "ops",
        None,
        "automatic_fallback",
        "warning",
        {"source_id": "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25", "platform": "tiktok"},
        "a client's TikTok account revoked its grant; the vendor route reads it",
        {
            "subject_kind": "source",
            "source_id": "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25",
            "reason": "credential_revoked",
            "vendor": "tikhub",
        },
        service="registry-writer",
    )
    valid(s, "source-fallback-notice", source_fallback)
    budget = alert(
        "budget",
        "2026-10-04T08:12:00Z",
        ulid_for("2026-10-04T08:12:00Z", "alert", "budget"),
        "telegram",
        "ops",
        None,
        "budget_80",
        "warning",
        {},
        "x_pay_per_use: 80% of the post-read budget used",
        {
            "facts": [
                {"label": "budget", "value": "x_pay_per_use"},
                {"label": "used", "value": "2,400,312 of 3,000,000 post reads"},
            ]
        },
        fallthrough="email",
        service="quota-governor",
    )
    valid(s, "facts-budget", budget)
    valid(
        s,
        "account-manager",
        alert(
            "account-manager",
            "2026-10-06T12:00:00Z",
            ulid_for("2026-10-06T12:00:00Z", "alert", "am"),
            "email",
            "account_manager",
            CLIENT,
            "authorization_revoked",
            "high",
            {"source_id": "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25", "platform": "tiktok"},
            "a client revoked the TikTok grant of its own account",
            {
                "facts": [
                    {"label": "account", "value": "متجر البصرة"},
                    {"label": "revoked at", "value": "2026-10-07T08:59:00Z"},
                ]
            },
            service="tt-client-videos-fetcher",
        ),
        client_type="commercial",
    )
    valid(
        s,
        "client-webhook",
        {
            **spike,
            **meta(
                s,
                "alert-evaluator",
                ulid_for("2026-10-06T08:37:13Z", "run", "webhook"),
                "2026-10-06T08:37:13Z",
                name="webhook",
            ),
            "channel": "webhook",
            "idempotency_key": f"{alert_id}:webhook",
            "fallthrough_channel": None,
        },
        client_type="commercial",
    )
    request = alert(
        "request",
        "2026-10-07T10:00:05Z",
        ulid_for("2026-10-07T10:00:05Z", "alert", "request"),
        "email",
        "ops",
        None,
        "export_ready",
        "info",
        {"request_id": "01J9R5S3V7W1X4Y8Z0A2B6C9DH"},
        "the X compliance export for September is ready",
        {"facts": [{"label": "rows", "value": "1090"}]},
        service="x-compliance-sync",
    )
    valid(s, "request-notification", request)

    metadata_invalids(s, spike)
    gopts = {"client_type": "government"}
    invalid(
        s,
        "government-subject-source",
        with_(gov, ("subject", "source_id"), PERSON_SOURCE),
        ["subject", "source_id"],
        "a government client's alert names no source (alert-evaluator §6.2 L102; F-50)",
        **gopts,
    )
    invalid(
        s,
        "government-subject-platform",
        with_(gov, ("subject", "platform"), "facebook"),
        ["subject", "platform"],
        "a government client's alert names no platform (F-50)",
        **gopts,
    )
    invalid(
        s,
        "government-scope-source",
        with_(
            gov,
            ("details", "scope", "source"),
            {"source_id": PERSON_SOURCE, "display_name": "Example Page"},
        ),
        ["details", "scope", "source"],
        "a government client's alert names no source (alert-evaluator §6.2 L102)",
        **gopts,
    )
    invalid(
        s,
        "government-scope-platform",
        with_(gov, ("details", "scope", "platform"), "facebook"),
        ["details", "scope", "platform"],
        "a government client's alert names no platform (alert-evaluator §6.2 L102)",
        **gopts,
    )
    invalid(
        s,
        "government-poster-rule",
        {
            **by_type["new_high_reach_poster"],
            "client_id": GOV_CLIENT,
            "subject": {"keyword_id": KEYWORD},
            "details": {
                **by_type["new_high_reach_poster"]["details"],
                "scope": {"level": "keyword"},
            },
        },
        ["details", "rule_type"],
        "a government client receives the keyword-level rule types only (alert-evaluator §5.3 C L65; ADR-0048)",
        **gopts,
    )
    invalid(
        s,
        "client-alert-without-client-type",
        spike,
        [],
        "a client's alert is checked against its client type, which the producer passes (fails closed; CONVENTIONS v1.1 L84)",
    )
    invalid(
        s,
        "open-details",
        with_(budget, ("details",), {"note": "free text"}),
        ["details", "note"],
        "details is one of three typed branches, never an open object (Q11)",
    )
    invalid(
        s,
        "idempotency-key-not-the-channels",
        with_(spike, ("idempotency_key",), f"{alert_id}:email"),
        ["idempotency_key"],
        "idempotency_key = <alert_id>:<channel> (alert-evaluator §5.3 L69)",
        client_type="commercial",
    )
    invalid(
        s,
        "client-without-client-id",
        with_(spike, ("client_id",), None),
        ["client_id"],
        "a client or account-manager notice names its client (F-46)",
        client_type="commercial",
    )
    invalid(
        s,
        "ops-with-client-id",
        with_(budget, ("client_id",), CLIENT),
        ["client_id"],
        "an ops notice names no client (F-46)",
    )
    invalid(
        s,
        "with-provenance",
        {
            **budget,
            "provenance": {
                "route": "green",
                "vendor": None,
                "service": "quota-governor",
                "fetched_at": "2026-10-04T08:12:00Z",
            },
        },
        ["provenance"],
        "an n8n notice carries producer only (F-51)",
    )
    invalid(
        s,
        "with-author-ref",
        {**budget, "author_ref": ref("1000000000000000001", "x")},
        ["author_ref"],
        "an alert carries no author_ref (alert-evaluator.md L65; F-51)",
    )
    invalid(
        s,
        "with-item-text",
        {**budget, "text": "النت منقطع بالبصرة"},
        ["text"],
        "an alert carries no item text (alert-evaluator.md L128; F-51)",
    )
    invalid(
        s,
        "with-handle",
        with_(budget, ("subject", "handle"), "example_poster_x"),
        ["subject", "handle"],
        "an alert carries no handle (alert-evaluator.md L128; F-51)",
    )
    invalid(
        s,
        "uppercase-alert-name",
        with_(budget, ("alert",), "Budget80"),
        ["alert"],
        "alert is a snake_case name (Q11)",
    )
    invalid(
        s,
        "unknown-channel",
        {**budget, "channel": "sms", "idempotency_key": f"{budget['alert_id']}:sms"},
        ["channel"],
        "channel is email, telegram, slack or webhook (F-23; O-11)",
    )
    invalid(
        s,
        "fallthrough-to-webhook",
        with_(budget, ("fallthrough_channel",), "webhook"),
        ["fallthrough_channel"],
        "the fall-through is an n8n channel (ADR-0067 L27)",
    )
    invalid(
        s,
        "unknown-severity",
        with_(budget, ("severity",), "critical"),
        ["severity"],
        "severity is info, warning or high (F-48)",
    )
    invalid(
        s,
        "volume-spike-without-ratio",
        without(spike, "details", "metrics", "ratio"),
        ["details", "metrics", "ratio"],
        "a volume spike reports its ratio (alert-evaluator §6.2 L86-L99)",
        client_type="commercial",
    )
    for rule_type, msg in by_type.items():
        if rule_type == "volume_spike":
            continue
        first = next(iter(msg["details"]["metrics"]))
        invalid(
            s,
            f"{rule_type.replace('_', '-')}-text-metric",
            with_(msg, ("details", "metrics", first), "many"),
            ["details", "metrics", first],
            "metrics are numbers (Q11)",
            client_type="commercial",
        )
    invalid(
        s,
        "fallback-unknown-reason",
        with_(route_fallback, ("details", "reason"), "vendor_down"),
        ["details", "reason"],
        "a fallback notice's reason is from the registry reason list (ADR-0021; Q11)",
    )
    invalid(
        s,
        "route-fallback-without-platform",
        without(route_fallback, "details", "platform"),
        ["details", "platform"],
        "a route's fallback notice names the platform and route (ADR-0021)",
    )
    invalid(
        s,
        "source-fallback-without-source-id",
        without(source_fallback, "details", "source_id"),
        ["details", "source_id"],
        "a source's fallback notice names the source (ADR-0021)",
    )
    invalid(
        s,
        "facts-number-value",
        with_(budget, ("details", "facts", 0, "value"), 80),
        ["details", "facts", 0, "value"],
        "facts are strings (Q11)",
    )
    invalid(
        s,
        "old-schema-id",
        with_(budget, ("schema",), "alert/v1"),
        ["schema"],
        "alert/v1 becomes n8n.alert/v1 (ADR-0067 L25)",
    )
    tolerant(s, "unknown-field", {**budget, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"})


def cards() -> None:
    s = "n8n.card/v1"

    def card(
        name: str,
        at: str,
        card_type: str,
        subject: dict[str, Any],
        extra: dict[str, Any],
        channel: str = "telegram",
        audience: str = "ops",
        client_id: str | None = None,
        service: str = "qualifier",
    ) -> dict[str, Any]:
        key = subject.get("candidate_key") or subject["source_id"]
        ref = subject.get("decision_id") or subject["request_id"]
        cid = card_id(card_type, key, ref)
        return {
            **meta(s, service, ulid_for(at, "run", service, name), at, name=name),
            "card_id": cid,
            "idempotency_key": f"{cid}:{channel}",
            "channel": channel,
            "card_type": card_type,
            "audience": audience,
            "client_id": client_id,
            "subject": subject,
            "title": extra.pop("title"),
            "summary": extra.pop("summary"),
            "facts": extra.pop("facts"),
            "opened_at": at,
            **extra,
        }

    review = card(
        "review",
        "2026-10-06T12:40:31Z",
        "qualifier_review",
        {
            "candidate_key": "instagram:example_store_iq",
            "decision_id": "01J9N2Q7Z4T8X1V6M3K0H5R2WB",
        },
        {
            "title": "مرشح للمراجعة: example_store_iq",
            "summary": "one Iraqi signal; 48,200 followers",
            "facts": [
                {"label": "followers", "value": "48200"},
                {"label": "signal", "value": "iraqi_place: البصرة"},
            ],
            "buttons": [
                {"action": "approve_tier_1", "label": "Tier 1"},
                {"action": "approve_tier_2", "label": "Tier 2"},
                {"action": "approve_tier_3", "label": "Tier 3"},
                {"action": "reject", "label": "Reject"},
                {"action": "mention_only", "label": "Mention only"},
            ],
            "default_action": "reject",
            "timeout_at": "2026-10-07T12:40:31Z",
        },
    )
    valid(s, "qualifier-review", review)
    grant = card(
        "grant",
        "2026-10-06T12:00:05Z",
        "grant_missing",
        {
            "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
            "request_id": "01J9N3B5C7D9E1F3G5H7J9K1M3",
        },
        {
            "title": "Facebook page access is missing",
            "summary": "the page stopped granting pages_read_engagement",
            "facts": [{"label": "page", "value": "FiberX"}],
            "regrant_url": "https://portal.example.iq/sources/6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11/regrant",
        },
        channel="email",
        audience="client",
        client_id=CLIENT,
        service="fb-page-feed-poller",
    )
    valid(s, "grant-missing", grant)
    manual = card(
        "manual",
        "2026-10-06T10:05:00Z",
        "manual_url",
        {
            "candidate_key": "linkedin:example-company-iq",
            "request_id": "01J9N3B5C7D9E1F3G5H7J9K1M3",
        },
        {
            "title": "LinkedIn page URL needed",
            "summary": "the company page did not resolve by name",
            "facts": [{"label": "name", "value": "Example Company Iraq"}],
            "inputs": [{"name": "company_url", "label": "Company page URL", "kind": "url"}],
        },
        channel="slack",
        service="li-org-resolver",
    )
    valid(s, "manual-url", manual)
    valid(s, "manual-url-with-timeout", {**manual, "timeout_at": "2026-10-07T10:05:00Z"})

    metadata_invalids(s, review)
    invalid(
        s,
        "card-id-not-the-subjects",
        with_(review, ("card_id",), "7c71f097-b1a9-5acf-a7de-077f9b01c9a3"),
        ["card_id"],
        "card_id = uuid_v5(ns_cards, <card_type>:<subject key>:<decision_id or request_id>) (F-47)",
    )
    invalid(
        s,
        "subject-without-ref",
        with_(review, ("subject",), {"candidate_key": "instagram:example_store_iq"}),
        ["subject"],
        "a card's subject names its decision or request (F-47)",
    )
    invalid(
        s,
        "review-without-buttons",
        without(review, "buttons"),
        ["buttons"],
        "a review card carries its buttons (qualifier §5.3 L67)",
    )
    invalid(
        s,
        "review-default-approve",
        with_(review, ("default_action",), "approve_tier_3"),
        ["default_action"],
        "a review card defaults to reject (qualifier §5.2 L61)",
    )
    invalid(
        s,
        "review-without-timeout",
        without(review, "timeout_at"),
        ["timeout_at"],
        "a review card times out after 24 hours (qualifier §5.2 L61)",
    )
    invalid(
        s,
        "review-unknown-action",
        with_(review, ("buttons", 0, "action"), "approve"),
        ["buttons", 0, "action"],
        "a button is one of the review actions (qualifier §5.3 L67)",
    )
    invalid(
        s,
        "grant-missing-with-buttons",
        {**grant, "buttons": review["buttons"]},
        ["buttons"],
        "a missing-grant card has no buttons (F-47)",
    )
    invalid(
        s,
        "grant-missing-without-link",
        without(grant, "regrant_url"),
        ["regrant_url"],
        "a missing-grant card carries its re-grant link (F-47)",
    )
    invalid(
        s,
        "manual-url-without-inputs",
        without(manual, "inputs"),
        ["inputs"],
        "a manual-URL card asks for its input (F-47)",
    )
    invalid(
        s,
        "manual-url-file-input",
        with_(manual, ("inputs", 0, "kind"), "file"),
        ["inputs", 0, "kind"],
        "an input is a url or a text (F-47)",
    )
    invalid(
        s,
        "unknown-card-type",
        with_(review, ("card_type",), "approval"),
        ["card_type"],
        "card_type is closed (Q11)",
    )
    invalid(
        s,
        "idempotency-key-not-the-channels",
        with_(review, ("idempotency_key",), f"{review['card_id']}:email"),
        ["idempotency_key"],
        "idempotency_key = <card_id>:<channel> (F-23)",
    )
    invalid(
        s,
        "webhook-channel",
        {**review, "channel": "webhook", "idempotency_key": f"{review['card_id']}:webhook"},
        ["channel"],
        "a card goes through n8n's channels only (ADR-0067)",
    )
    invalid(
        s,
        "with-provenance",
        {
            **review,
            "provenance": {
                "route": "green",
                "vendor": None,
                "service": "ig-account-resolver",
                "fetched_at": "2026-10-06T12:40:11Z",
            },
        },
        ["provenance"],
        "an n8n notice carries producer only (F-51)",
    )
    invalid(
        s,
        "client-without-client-id",
        with_(grant, ("client_id",), None),
        ["client_id"],
        "a client or account-manager card names its client (F-46)",
    )
    tolerant(s, "unknown-field", {**review, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"})


def run() -> None:
    alerts()
    cards()
