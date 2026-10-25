"""Fixtures for the control topics and the job envelope: registry.decisions, source.events,
jobs.completed, job/v1 and the shared dlq.<service>/v1 record."""

import base64
import copy
import json
from typing import Any

from common import (
    CLIENT,
    CLIENT2,
    content_hash,
    deletion_id,
    hit_id,
    iid,
    invalid,
    meta,
    metadata_invalids,
    prd,
    prov,
    ref,
    tolerant,
    ulid_for,
    valid,
    with_,
    without,
)

from listening_contracts.keys import (
    candidate_key_from_handle,
    item_id,
    linkedin_post_id,
    news_site_candidate_key,
)
from listening_contracts.ulid import comment_decay_job_id

R_META = "schema, message_id, produced_at and producer stamped by the SDK; service and schema_version go (ADR-0002)"
PERSON = "person:01J9P2R4T6V8X0Z2B4D6F8H0KM"  # D3's person reference (its form is D3's; Q4)
REVIEWER = "person:01J9P2R4T6V8X0Z2B4D6F8H0KN"

# The qualifier's candidate of the PRD examples (poster-resolver, qualifier, registry-writer §6.2).
IG_CAND = "instagram:17841400000000000"
IG_SOURCE = "7f1c2a9e-5d1b-4c7e-9a3f-2b8e6d4c1a00"
IG_DECISION = "01M48B9AKGRHAJW420WYJS5QK3"
IG_PROV = prov("green", None, "ig-account-resolver", "2026-10-06T10:13:58Z")


def signals(**on: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        k: False
        for k in (
            "iraqi_place",
            "platform_country_iq",
            "phone_964",
            "iq_domain",
            "outlet_link",
            "seed_list",
        )
    }
    evidence = on.pop("evidence", [])
    out.update(on)
    out["signal_evidence"] = evidence
    return out


def share(
    ar: float = 0, ckb: float = 0, en: float = 0, ar_iraqi: float = 0, sample: int = 20
) -> dict[str, Any]:
    return {
        "ar": ar,
        "ckb": ckb,
        "en": en,
        "mixed": 0,
        "other": 0,
        "und": 0,
        "ar_iraqi": ar_iraqi,
        "sample": sample,
    }


IG_COLUMNS = {
    "platform": "instagram",
    "source_type": "account",
    "platform_id": "17841400000000000",
    "handle": "baghdad_eats",
    "url": "https://instagram.com/baghdad_eats",
    "display_name": "Baghdad Eats",
    "route": "green",
    "vendor": None,
    "tier": 2,
    "lifecycle": "active",
    "push_covered": False,
    "retention_class": "meta_on_request",
    "client_ids": [CLIENT],
    "owned_by_client": False,
    "added_by": "qualifier",
    "followers": 48200,
    "country_signals": signals(
        iraqi_place=True,
        evidence=[{"signal": "iraqi_place", "matched": "Baghdad", "where": "location"}],
    ),
    "lang_share": share(ar=0.90, en=0.10, ar_iraqi=0.70, sample=22),
    "platform_meta": {},
}


# --------------------------------------------------------------------------------------------
# registry.decisions/v1


def decisions() -> None:
    s = "registry.decisions/v1"

    def dec(
        service: str,
        at: str,
        decision: str,
        reason: str | None,
        subject: dict[str, Any],
        block: dict[str, Any] | None,
        name: str,
        *,
        requested_by: str | None = None,
        provenance: dict[str, Any] | None = None,
        retention_class: str | None = None,
        decision_id: str | None = None,
        message_id: str | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        m = meta(s, service, job_id or ulid_for(at, "job", service, name), at, name=name)
        if message_id:
            m["message_id"] = message_id
        out: dict[str, Any] = {
            **m,
            "decision_id": decision_id or ulid_for(at, "decision", name),
            "decision": decision,
            "requested_by": requested_by or service,
            "reason": reason,
            **subject,
        }
        if block is not None:
            out[decision] = block
        if provenance is not None:
            out["provenance"] = provenance
            out["retention_class"] = retention_class
        return out

    # The qualifier's add (qualifier §6.2 L84). A topic consumer copies its input's producer.job_id
    # (F-17): here the poster-resolver profile it applies.
    profile = json.loads(
        (
            __import__("common").ROOT / "poster.profiles/v1/valid/prd-poster-resolver.json"
        ).read_text()
    )
    add = dec(
        "qualifier",
        "2026-10-06T10:14:30Z",
        "add",
        None,
        {"candidate_key": IG_CAND},
        {"source": IG_COLUMNS, "proposed_source_id": None, "origin": "discovery", "rule_hit": 6},
        "prd",
        provenance=IG_PROV,
        retention_class="meta_on_request",
        decision_id=IG_DECISION,
        message_id="01M48BA9VGH96Q50HZX9S88TJC",
        job_id=profile["producer"]["job_id"],
    )
    valid(s, "prd-qualifier", add)
    prd(
        "qualifier",
        "docs/prds/shared/qualifier.md",
        84,
        s,
        "prd-qualifier",
        [
            R_META,
            "source_id: null goes: a decision carries exactly one subject, here the candidate key (ADR-0013)",
            "the source columns move into the add block's source, with rule_hit and origin beside it (ADR-0013)",
            "the free-text reason iraqi_signals=2;followers=48200 goes: an add's reason is null, the rule is rule_hit and the signals are source.country_signals (ADR-0013, ADR-0014)",
            "review and expires_at go: they belong to the review and reject types (ADR-0013)",
            "lifecycle active, push_covered false, url's platform_meta {} and the full country_signals and lang_share keys added: registry-writer's column set (ADR-0013 L25, ADR-0033)",
            "requested_by names the qualifier (ADR-0013)",
            "provenance and retention_class: the resolver profile the decision applies, fetched by ig-account-resolver (ADR-0003 L26)",
        ],
    )

    # The canary's route-level health_change (source-health-canary §6.2 L102), rewritten under R-2.
    canary = dec(
        "source-health-canary",
        "2026-10-06T11:20:00Z",
        "health_change",
        "empty_200_rate",
        {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
        {
            "health": "fallback",
            "fallback": {"route": "amber", "vendor": "ensembledata"},
            "scope": None,
            "evidence": {
                "window_minutes": 15,
                "samples": 60,
                "empty_200": 9,
                "rate": 0.15,
                "targets": 5,
            },
        },
        "prd",
        provenance=prov("amber", "tikhub", "source-health-canary", "2026-10-06T11:19:58Z"),
        retention_class="vendor_agreed",
        decision_id="01J9Q4R8T2V6W0X3Y5Z7A1B9CD",
    )
    valid(s, "prd-source-health-canary", canary)
    prd(
        "source-health-canary",
        "docs/prds/shared/source-health-canary.md",
        102,
        s,
        "prd-source-health-canary",
        [
            R_META,
            "at becomes produced_at; action becomes decision and actor requested_by (ADR-0013)",
            "health, fallback, scope and evidence move into the health_change block (ADR-0013)",
            "health degraded with a fallback becomes health fallback: fallback is non-null exactly when health is fallback (ADR-0014 L27, ADR-0050 L31; R-2)",
            "scope null: an amber-to-amber swap declares none, non_government is a green-to-amber alternate's (source-health-canary L79, ADR-0052 L33 (d); R-2)",
            "provenance and retention_class added: the canary's probe of the route (ADR-0003 L26)",
        ],
    )

    owned_id = "4b9e2c71-8d3a-4f56-a0e1-7c2d9b8f3a64"
    owned_cols = {
        **IG_COLUMNS,
        "platform": "facebook",
        "source_type": "page",
        "platform_id": "104998877665544",
        "handle": "fiberx.iq",
        "url": "https://www.facebook.com/fiberx.iq",
        "display_name": "FiberX",
        "tier": 1,
        "owned_by_client": True,
        "added_by": "client",
        "followers": None,
        "country_signals": None,
        "lang_share": None,
    }
    owned = dec(
        "client-portal",
        "2026-10-06T07:30:02Z",
        "add",
        None,
        {"source_id": owned_id},
        {
            "source": owned_cols,
            "proposed_source_id": owned_id,
            "origin": None,
            "rule_hit": None,
            "client_priority": [{"client_id": CLIENT, "priority": True}],
        },
        "owned",
        requested_by=PERSON,
    )
    valid(s, "add-owned-property", owned)
    tg_group = "c2e9a4f1-6b3d-4e87-9a05-d1f8b7c3e2a6"
    tg_channel = "8a3f1c6e-2b9d-4e70-b5a4-f0c9d2e1b7a8"
    tg_cols = {
        **IG_COLUMNS,
        "platform": "telegram",
        "source_type": "group",
        "platform_id": "-1001987654321",
        "handle": None,
        "url": None,
        "display_name": "نقاشات زين العراق",
        "tier": 1,
        "owned_by_client": True,
        "added_by": "client",
        "followers": None,
        "country_signals": None,
        "lang_share": None,
        "retention_class": "meta_on_request",
        "platform_meta": {
            "linked_channel_source_id": tg_channel,
            "linked_chat_id": "-1001987650000",
        },
    }
    tg_add = dec(
        "tg-discussion-receiver",
        "2026-10-06T08:02:11Z",
        "add",
        None,
        {"source_id": tg_group},
        {"source": tg_cols, "proposed_source_id": tg_group, "origin": None, "rule_hit": None},
        "tg-group",
        provenance=prov("green", None, "tg-discussion-receiver", "2026-10-06T08:02:10Z"),
        retention_class="meta_on_request",
    )
    valid(s, "add-telegram-group", tg_add)
    site_id = "5e3b8f02-6d1c-4a97-b2e8-0c9f4d7a1e63"
    site_cols = {
        **IG_COLUMNS,
        "platform": "news",
        "source_type": "site",
        "platform_id": "example-daily.iq",
        "handle": "example-daily.iq",
        "url": "https://www.example-daily.iq/",
        "display_name": "Example Daily",
        "tier": 1,
        "retention_class": "news_excerpt",
        "followers": None,
        "country_signals": signals(
            iraqi_place=True,
            phone_964=True,
            iq_domain=True,
            seed_list=True,
            evidence=[{"signal": "iq_domain", "matched": ".iq", "where": "host"}],
        ),
        "lang_share": share(ar=0.95, en=0.05, ar_iraqi=0.05, sample=50),
    }
    valid(
        s,
        "add-news-site",
        dec(
            "qualifier",
            "2026-10-06T08:53:10Z",
            "add",
            None,
            {"candidate_key": news_site_candidate_key("example-daily.iq")},
            {
                "source": site_cols,
                "proposed_source_id": site_id,
                "origin": "discovery",
                "rule_hit": 6,
            },
            "site",
            provenance=prov("green", None, "news-site-resolver", "2026-10-06T08:52:40Z"),
            retention_class="news_excerpt",
        ),
    )
    manual_cols = {
        **IG_COLUMNS,
        "platform": "x",
        "source_type": "account",
        "platform_id": "1456789012345678901",
        "handle": "example_telecom_iq",
        "url": "https://x.com/example_telecom_iq",
        "display_name": "شركة المثال للاتصالات",
        "tier": 1,
        "retention_class": "x_24h_sync",
        "added_by": "ops",
        "followers": 18400,
    }
    valid(
        s,
        "add-manual-candidate",
        dec(
            "qualifier",
            "2026-10-06T11:03:30Z",
            "add",
            None,
            {"candidate_key": "x:1456789012345678901"},
            {
                "source": manual_cols,
                "proposed_source_id": None,
                "origin": "manual",
                "rule_hit": 6,
                "client_priority": [{"client_id": CLIENT, "priority": True}],
            },
            "manual",
            provenance=prov("green", None, "x-user-resolver", "2026-10-06T11:02:37Z"),
            retention_class="x_24h_sync",
        ),
    )
    valid(
        s,
        "add-reviewer-answer",
        dec(
            "qualifier",
            "2026-10-07T09:12:40Z",
            "add",
            None,
            {"candidate_key": IG_CAND},
            {
                "source": {**IG_COLUMNS, "tier": 3},
                "proposed_source_id": None,
                "origin": "discovery",
                "rule_hit": 2,
            },
            "answer",
            requested_by=REVIEWER,
            provenance=IG_PROV,
            retention_class="meta_on_request",
        ),
    )
    kw = "0cd402b6-9015-45f8-86b4-d90cc086d320"
    valid(
        s,
        "add-keyword",
        dec(
            "client-portal",
            "2026-10-06T07:40:00Z",
            "add",
            None,
            {"keyword_id": kw},
            {"platform_meta": {"instagram": {"ig_user_id": "17841400112233445"}}},
            "keyword",
            requested_by=PERSON,
        ),
    )
    valid(
        s,
        "update-keyword",
        dec(
            "admin-console",
            "2026-10-06T07:45:00Z",
            "update",
            None,
            {"keyword_id": kw},
            {},
            "keyword-update",
            requested_by=PERSON,
        ),
    )
    upd = dec(
        "qualifier",
        "2026-11-05T10:14:30Z",
        "update",
        None,
        {"source_id": IG_SOURCE},
        {"source": {"followers": 51200, "display_name": "Baghdad Eats | بغداد"}},
        "refresh",
        provenance=prov("green", None, "ig-account-resolver", "2026-11-05T10:13:58Z"),
        retention_class="meta_on_request",
    )
    valid(s, "update-refreshed-profile", upd)
    valid(
        s,
        "update-onboarding",
        dec(
            "client-portal",
            "2026-10-08T12:00:00Z",
            "update",
            None,
            {"source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566"},
            {
                "source": {
                    "route": "green",
                    "vendor": None,
                    "owned_by_client": True,
                    "push_covered": True,
                }
            },
            "onboarding",
            requested_by=PERSON,
        ),
    )
    hashtag = "e1d2c3b4-a596-4877-8b6a-5c4d3e2f1a09"
    valid(
        s,
        "update-budget-wait-amber",
        dec(
            "ig-hashtag-search",
            "2026-10-06T06:00:05Z",
            "update",
            "budget_wait",
            {"source_id": hashtag},
            {"source": {"route": "amber", "vendor": "sociavault"}},
            "budget-amber",
        ),
    )
    valid(
        s,
        "update-budget-wait-queued",
        dec(
            "ig-hashtag-search",
            "2026-10-06T06:00:06Z",
            "update",
            "budget_wait",
            {"source_id": hashtag},
            {"source": {"notes": "budget wait: queued for the next weekly window"}},
            "budget-queued",
        ),
    )
    yt_channel = "3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94"
    valid(
        s,
        "update-uploads-playlist",
        dec(
            "yt-uploads-reconciler",
            "2026-10-06T11:04:30Z",
            "update",
            None,
            {"source_id": yt_channel},
            {"source": {"platform_meta": {"uploads_playlist_id": "UUx3Kp9vQ2mLwR7tYb4nJ8sA"}}},
            "uploads",
            provenance=prov("green", None, "yt-uploads-reconciler", "2026-10-06T11:04:27Z"),
            retention_class="youtube_30d_text",
        ),
    )
    valid(
        s,
        "update-client-priority",
        dec(
            "admin-console",
            "2026-10-09T08:00:00Z",
            "update",
            None,
            {"source_id": IG_SOURCE},
            {"source": {}, "client_priority": [{"client_id": CLIENT2, "priority": False}]},
            "priority",
            requested_by=PERSON,
        ),
    )
    valid(
        s,
        "remove-client-offboarding",
        dec(
            "retention-purger",
            "2026-10-13T00:10:00Z",
            "remove_client",
            "client_removed",
            {"source_id": IG_SOURCE},
            {"client_id": CLIENT2},
            "offboarding",
        ),
    )
    valid(
        s,
        "remove-client-portal",
        dec(
            "client-portal",
            "2026-10-10T09:00:00Z",
            "remove_client",
            "client_removed",
            {"source_id": IG_SOURCE},
            {"client_id": CLIENT},
            "portal-remove",
            requested_by=PERSON,
        ),
    )
    tier_profile = valid(
        s,
        "tier-change-profile",
        dec(
            "qualifier",
            "2026-11-05T10:14:31Z",
            "tier_change",
            None,
            {"source_id": IG_SOURCE},
            {"tier": 1, "rule_hit": 6},
            "tier",
            provenance=prov("green", None, "ig-account-resolver", "2026-11-05T10:13:58Z"),
            retention_class="meta_on_request",
        ),
    )
    tier_sweep = valid(
        s,
        "tier-change-sweep",
        dec(
            "qualifier",
            "2026-10-20T02:00:00Z",
            "tier_change",
            None,
            {"source_id": IG_SOURCE},
            {"tier": 3, "rule_hit": 9},
            "tier-sweep",
        ),
    )
    valid(
        s,
        "dormant",
        dec(
            "qualifier",
            "2026-10-20T02:00:01Z",
            "dormant",
            None,
            {"source_id": IG_SOURCE},
            {"rule_hit": 3},
            "dormant",
        ),
    )
    # The sweep's decay takes a tier-3 source to dormant (qualifier §5.2 L60): no fetch behind it.
    dormant_decay = valid(
        s,
        "dormant-decay",
        dec(
            "qualifier",
            "2026-10-20T02:00:02Z",
            "dormant",
            None,
            {"source_id": IG_SOURCE},
            {"rule_hit": 9},
            "dormant-decay",
        ),
    )
    # A reviewer's tier for a profile under review (rule 10): the profile's provenance, and the
    # reviewer as requester (D-3).
    valid(
        s,
        "tier-change-review",
        dec(
            "qualifier",
            "2026-11-06T09:30:00Z",
            "tier_change",
            None,
            {"source_id": IG_SOURCE},
            {"tier": 2, "rule_hit": 10},
            "tier-review",
            requested_by=PERSON,
            provenance=prov("green", None, "ig-account-resolver", "2026-11-05T10:13:58Z"),
            retention_class="meta_on_request",
        ),
    )
    tt_source = "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8"
    valid(
        s,
        "promote-seen-posting",
        dec(
            "tt-profile-videos-poller",
            "2026-10-21T09:00:00Z",
            "promote",
            None,
            {"source_id": tt_source},
            None,
            "promote",
            provenance=prov("amber", "tikhub", "tt-profile-videos-poller", "2026-10-21T08:59:41Z"),
            retention_class="vendor_agreed",
        ),
    )
    valid(
        s,
        "promote-sweep",
        dec(
            "qualifier",
            "2026-10-21T02:00:00Z",
            "promote",
            None,
            {"source_id": tt_source},
            None,
            "promote-sweep",
        ),
    )
    valid(
        s,
        "retire-decay",
        dec(
            "qualifier",
            "2026-12-20T02:00:00Z",
            "retire",
            None,
            {"source_id": tt_source},
            {"rule_hit": 9},
            "retire",
        ),
    )
    valid(
        s,
        "retire-owner-request",
        dec(
            "retention-purger",
            "2026-10-12T09:00:00Z",
            "retire",
            "owner_request",
            {"source_id": IG_SOURCE},
            {"rule_hit": None},
            "owner",
        ),
    )
    revoked = "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25"
    valid(
        s,
        "retire-authorization-revoked",
        dec(
            "tt-client-videos-fetcher",
            "2026-10-07T09:00:04Z",
            "retire",
            "authorization_revoked",
            {"source_id": revoked},
            {"rule_hit": None},
            "revoked",
            provenance=prov("green", None, "tt-client-videos-fetcher", "2026-10-07T08:59:00Z"),
            retention_class="meta_on_request",
        ),
    )
    x_source = "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35"
    valid(
        s,
        "retire-not-found",
        dec(
            "x-user-timeline-poller",
            "2026-10-15T04:00:00Z",
            "retire",
            "not_found",
            {"source_id": x_source},
            {"rule_hit": None},
            "gone",
            provenance=prov("green", None, "x-user-timeline-poller", "2026-10-15T03:59:12Z"),
            retention_class="x_24h_sync",
        ),
    )
    valid(
        s,
        "push-coverage-on",
        dec(
            "yt-pubsub-receiver",
            "2026-10-06T09:00:00Z",
            "push_coverage",
            None,
            {"source_id": yt_channel},
            {"push_covered": True},
            "push-on",
        ),
    )
    valid(
        s,
        "push-coverage-lease-lapsed",
        dec(
            "yt-pubsub-receiver",
            "2026-10-11T09:00:00Z",
            "push_coverage",
            "lease_lapsed",
            {"source_id": yt_channel},
            {"push_covered": False},
            "push-off",
        ),
    )
    ig_own = "d4c3b2a1-9f8e-4d7c-8b6a-5f4e3d2c1b0a"
    degraded = dec(
        "ig-webhook-receiver",
        "2026-10-06T12:00:00Z",
        "health_change",
        "grant_missing",
        {"source_id": ig_own},
        {"health": "degraded"},
        "grant",
        provenance=prov("green", None, "ig-webhook-receiver", "2026-10-06T11:59:58Z"),
        retention_class="meta_on_request",
    )
    valid(s, "source-health-degraded", degraded)
    valid(
        s,
        "source-health-cleared",
        dec(
            "ig-webhook-receiver",
            "2026-10-07T12:00:00Z",
            "health_change",
            "grant_missing",
            {"source_id": ig_own},
            {"health": "ok"},
            "grant-ok",
            provenance=prov("green", None, "ig-webhook-receiver", "2026-10-07T11:59:58Z"),
            retention_class="meta_on_request",
        ),
    )
    valid(
        s,
        "source-health-credential-revoked",
        dec(
            "tg-bot-channel-receiver",
            "2026-10-06T13:00:00Z",
            "health_change",
            "credential_revoked",
            {"source_id": tg_channel},
            {"health": "blocked"},
            "cred",
            provenance=prov("green", None, "tg-bot-channel-receiver", "2026-10-06T12:59:58Z"),
            retention_class="meta_on_request",
        ),
    )
    valid(
        s,
        "source-health-crawl-disallowed",
        dec(
            "news-robots-checker",
            "2026-10-06T06:30:16Z",
            "health_change",
            "crawl_disallowed",
            {"source_id": site_id},
            {"health": "blocked"},
            "robots",
            provenance=prov("green", None, "news-robots-checker", "2026-10-06T06:30:11Z"),
            retention_class="news_excerpt",
        ),
    )
    flag = dec(
        "admin-api",
        "2026-10-06T14:00:00Z",
        "health_change",
        "flag_off",
        {"source_id": "c7e41b95-0a3d-4f82-b6c9-18d5e2a07f43"},
        {"health": "blocked"},
        "flag",
        requested_by=PERSON,
    )
    valid(s, "source-health-flag-off", flag)
    valid(
        s,
        "source-health-flag-on",
        {
            **flag,
            "reason": "flag_on",
            "decision_id": ulid_for("2026-10-08T14:00:00Z", "decision", "flag-on"),
        },
    )
    valid(
        s,
        "source-health-admin-clear",
        dec(
            "admin-api",
            "2026-10-07T15:00:00Z",
            "health_change",
            "privacy_mode",
            {"source_id": tg_channel},
            {"health": "ok"},
            "admin-clear",
            requested_by=PERSON,
        ),
    )
    route = dec(
        "source-health-canary",
        "2026-10-06T11:05:00Z",
        "health_change",
        "empty_200_rate",
        {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
        {
            "health": "degraded",
            "fallback": None,
            "scope": None,
            "evidence": {
                "window_minutes": 15,
                "samples": 60,
                "empty_200": 5,
                "rate": 0.083,
                "targets": 5,
            },
        },
        "route-degraded",
        provenance=prov("amber", "tikhub", "source-health-canary", "2026-10-06T11:04:58Z"),
        retention_class="vendor_agreed",
    )
    valid(s, "route-health-degraded", route)
    valid(
        s,
        "route-health-fallback-to-amber",
        dec(
            "source-health-canary",
            "2026-10-06T11:30:00Z",
            "health_change",
            "auth",
            {"platform": "facebook", "route": "green", "vendor": None},
            {
                "health": "fallback",
                "fallback": {"route": "amber", "vendor": "sociavault"},
                "scope": "non_government",
                "evidence": {
                    "window_minutes": 15,
                    "samples": 40,
                    "empty_200": 0,
                    "rate": 0.0,
                    "targets": 4,
                },
            },
            "route-fb",
            provenance=prov("green", None, "source-health-canary", "2026-10-06T11:29:58Z"),
            retention_class="meta_on_request",
        ),
    )
    valid(
        s,
        "route-health-ok",
        dec(
            "source-health-canary",
            "2026-10-06T14:20:00Z",
            "health_change",
            None,
            {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
            {"health": "ok", "fallback": None, "scope": None, "evidence": None},
            "route-ok",
            provenance=prov("amber", "tikhub", "source-health-canary", "2026-10-06T14:19:58Z"),
            retention_class="vendor_agreed",
        ),
    )
    valid(
        s,
        "route-health-flag-off",
        dec(
            "source-health-canary",
            "2026-10-06T15:00:00Z",
            "health_change",
            "flag_off",
            {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
            {"health": "degraded", "fallback": None, "scope": None, "evidence": None},
            "route-flag",
            provenance=prov("amber", "tikhub", "source-health-canary", "2026-10-06T14:59:58Z"),
            retention_class="vendor_agreed",
        ),
    )
    valid(
        s,
        "route-health-blocked",
        dec(
            "source-health-canary",
            "2026-10-06T16:00:00Z",
            "health_change",
            "server",
            {"platform": "x", "route": "green", "vendor": None},
            {
                "health": "blocked",
                "fallback": None,
                "scope": None,
                "evidence": {
                    "window_minutes": 15,
                    "samples": 30,
                    "empty_200": 0,
                    "rate": 0.0,
                    "targets": 3,
                },
            },
            "route-x",
            provenance=prov("green", None, "source-health-canary", "2026-10-06T15:59:58Z"),
            retention_class="x_24h_sync",
        ),
    )
    q = {"rule_hit": 5, "client_ids": [CLIENT]}
    valid(
        s,
        "queued-government",
        dec(
            "qualifier",
            "2026-10-06T10:15:00Z",
            "queued",
            "amber_excluded_government",
            {"candidate_key": "tiktok:6812345678901234567"},
            {"rule_hit": 5, "client_ids": ["c7f12d45-b7c5-467d-aa82-e7826ed8abf2"]},
            "queued",
            provenance=prov("amber", "tikhub", "tt-user-resolver", "2026-10-06T10:02:31Z"),
            retention_class="vendor_agreed",
        ),
    )
    valid(
        s,
        "mention-only-candidate",
        dec(
            "qualifier",
            "2026-10-06T11:04:10Z",
            "mention_only",
            None,
            {"candidate_key": "x:1000000000000000004"},
            {**q, "rule_hit": 7},
            "mention",
            provenance=prov("green", None, "x-user-resolver", "2026-10-06T11:04:00Z"),
            retention_class="x_24h_sync",
        ),
    )
    mention_author = dec(
        "qualifier",
        "2026-10-06T11:03:20Z",
        "mention_only",
        None,
        {"author_ref": ref("1000000000000000001", "x")},
        {**q, "rule_hit": 7},
        "mention-author",
        provenance=prov("green", None, "x-user-resolver", "2026-10-06T11:03:10Z"),
        retention_class="x_24h_sync",
    )
    valid(s, "mention-only-author", mention_author)
    reject = dec(
        "qualifier",
        "2026-10-06T12:41:00Z",
        "reject",
        None,
        {"candidate_key": "instagram:furat_restaurant"},
        {"rule_hit": 2, "client_ids": [CLIENT], "expires_at": "2027-04-04T12:41:00Z"},
        "reject",
        provenance=prov("green", None, "ig-account-resolver", "2026-10-06T12:40:11Z"),
        retention_class="meta_on_request",
    )
    valid(s, "reject", reject)
    valid(
        s,
        "reject-review-timeout",
        {
            **reject,
            "reason": "review_timeout",
            "reject": {**reject["reject"], "rule_hit": 10},
            "decision_id": ulid_for("2026-10-07T12:41:00Z", "decision", "timeout"),
        },
    )
    review = dec(
        "qualifier",
        "2026-10-06T12:40:30Z",
        "review",
        "age_gated",
        {"candidate_key": "instagram:furat_restaurant"},
        {"rule_hit": 2, "client_ids": [CLIENT]},
        "review",
        provenance=prov("green", None, "ig-account-resolver", "2026-10-06T12:40:11Z"),
        retention_class="meta_on_request",
    )
    valid(s, "review-age-gated", review)
    valid(
        s,
        "review-no-reason",
        {
            **review,
            "reason": None,
            "decision_id": ulid_for("2026-10-06T12:40:31Z", "decision", "review2"),
        },
    )

    metadata_invalids(s, add)
    invalid(
        s,
        "two-subjects",
        {**add, "source_id": IG_SOURCE},
        ["source_id"],
        "a decision carries exactly one subject (ADR-0013)",
    )
    invalid(
        s,
        "route-health-with-source",
        {**route, "source_id": IG_SOURCE},
        ["source_id"],
        "a route-level health_change carries no source_id (ADR-0013)",
    )
    invalid(
        s,
        "mention-only-two-subjects",
        {**mention_author, "candidate_key": "x:1000000000000000001"},
        ["candidate_key"],
        "an individual's mention is keyed by author_ref alone (ADR-0033)",
    )
    invalid(
        s,
        "tier-down",
        {**add, "decision": "tier_down"},
        ["decision"],
        "tier_down becomes tier_change (ADR-0013)",
    )
    invalid(
        s,
        "action-field",
        {**canary, "action": "health_change"},
        ["action"],
        "action becomes decision (ADR-0013)",
    )
    invalid(
        s,
        "actor-field",
        {**canary, "actor": "source-health-canary"},
        ["actor"],
        "actor becomes requested_by (ADR-0013)",
    )
    invalid(
        s,
        "free-text-reason",
        {**add, "reason": "iraqi_signals=2;followers=48200"},
        ["reason"],
        "reason is one closed list (ADR-0013, ADR-0014)",
    )
    invalid(
        s,
        "schema-version",
        {**add, "schema_version": 1},
        ["schema_version"],
        "schema_version gives way to schema (ADR-0002)",
    )
    invalid(
        s,
        "top-level-source-column",
        {**add, "tier": 2},
        ["tier"],
        "the source columns travel in the add block (ADR-0013)",
    )
    invalid(
        s,
        "review-on-add",
        {**add, "review": None},
        ["review"],
        "review goes from add: requested_by names the reviewer (ADR-0013, ADR-0067)",
    )
    invalid(
        s,
        "owned-add-id-mismatch",
        with_(owned, ("add", "proposed_source_id"), "5f0e1d2c-3b4a-4968-8776-5a4b3c2d1e0f"),
        ["add", "proposed_source_id"],
        "an owned property's add carries its pre-allocated id as the subject (ADR-0066; F-39)",
    )
    invalid(
        s,
        "owned-add-without-id",
        with_(owned, ("add", "proposed_source_id"), None),
        ["add", "proposed_source_id"],
        "an owned property's add carries its pre-allocated id as the subject (ADR-0066; F-39)",
    )
    invalid(
        s,
        "flag-off-degraded",
        with_(flag, ("health_change", "health"), "degraded"),
        ["health_change", "health"],
        "flag_off takes health blocked only (ADR-0021 L61; F-11)",
    )
    invalid(
        s,
        "flag-off-not-admin",
        {
            **flag,
            **meta(
                s,
                "x-user-timeline-poller",
                ulid_for("2026-10-06T14:00:00Z", "job", "flag-x"),
                "2026-10-06T14:00:00Z",
            ),
            "requested_by": "x-user-timeline-poller",
            "provenance": prov("green", None, "x-user-timeline-poller", "2026-10-06T13:59:00Z"),
            "retention_class": "x_24h_sync",
        },
        ["producer", "service"],
        "only the admin API sends flag_off and flag_on (ADR-0021 L61; F-11)",
    )
    invalid(
        s,
        "credential-revoked-degraded",
        dec(
            "tg-bot-channel-receiver",
            "2026-10-06T13:00:00Z",
            "health_change",
            "credential_revoked",
            {"source_id": tg_channel},
            {"health": "degraded"},
            "cred-degraded",
            provenance=prov("green", None, "tg-bot-channel-receiver", "2026-10-06T12:59:58Z"),
            retention_class="meta_on_request",
        ),
        ["health_change", "health"],
        "credential_revoked is never degraded (ADR-0016 L27; F-11)",
    )
    invalid(
        s,
        "source-health-fallback",
        with_(degraded, ("health_change", "health"), "fallback"),
        ["health_change", "health"],
        "a source-level health_change never sets fallback (ADR-0016)",
    )
    invalid(
        s,
        "admin-clear-degraded",
        dec(
            "admin-api",
            "2026-10-07T15:00:00Z",
            "health_change",
            "privacy_mode",
            {"source_id": tg_channel},
            {"health": "degraded"},
            "admin-degraded",
            requested_by=PERSON,
        ),
        ["producer", "service"],
        "the admin API clears a health reason with health ok only (Q12)",
    )
    invalid(
        s,
        "fallback-without-target",
        with_(canary, ("health_change", "fallback"), None),
        ["health_change", "fallback"],
        "fallback is non-null exactly when health is fallback (R-2)",
    )
    invalid(
        s,
        "target-without-fallback",
        with_(route, ("health_change", "fallback"), {"route": "amber", "vendor": "ensembledata"}),
        ["health_change", "fallback"],
        "fallback is non-null exactly when health is fallback (R-2)",
    )
    invalid(
        s,
        "scope-without-fallback",
        with_(route, ("health_change", "scope"), "non_government"),
        ["health_change", "scope"],
        "scope is null unless health is fallback (R-2)",
    )
    invalid(
        s,
        "route-ok-with-reason",
        with_(
            dec(
                "source-health-canary",
                "2026-10-06T14:20:00Z",
                "health_change",
                None,
                {"platform": "tiktok", "route": "amber", "vendor": "tikhub"},
                {"health": "ok", "fallback": None, "scope": None, "evidence": None},
                "route-ok2",
                provenance=prov("amber", "tikhub", "source-health-canary", "2026-10-06T14:19:58Z"),
                retention_class="vendor_agreed",
            ),
            ("reason",),
            "empty_200_rate",
        ),
        ["reason"],
        "a route's return to ok carries no reason",
    )
    invalid(
        s,
        "route-degraded-without-reason",
        {**route, "reason": None},
        ["reason"],
        "a route-level state other than ok names its reason",
    )
    invalid(
        s,
        "route-flag-off-blocked",
        with_({**route, "reason": "flag_off"}, ("health_change", "health"), "blocked"),
        ["health_change", "health"],
        "the canary's flag_off returns a route to degraded (ADR-0021 L61; F-40)",
    )
    invalid(
        s,
        "route-unknown-vendor",
        with_(canary, ("health_change", "fallback", "vendor"), "apify"),
        ["health_change", "fallback", "vendor"],
        "vendors are the registry's, by route (ADR-0051)",
    )
    invalid(
        s,
        "provenance-refused",
        {
            **owned,
            "provenance": prov("green", None, "client-portal", "2026-10-06T07:30:00Z"),
            "retention_class": "meta_on_request",
        },
        ["provenance"],
        "a decision a person enters carries requested_by, never provenance (ADR-0003 L26)",
    )
    invalid(
        s,
        "provenance-required",
        without(without(add, "provenance"), "retention_class"),
        ["provenance"],
        "the qualifier's decisions from profiles carry provenance (ADR-0003 L26)",
    )
    invalid(
        s,
        "provenance-without-class",
        without(add, "retention_class"),
        ["retention_class"],
        "provenance and retention_class travel together (ADR-0003)",
    )
    invalid(
        s,
        "tier-change-profile-without-provenance",
        without(without(tier_profile, "provenance"), "retention_class"),
        ["provenance"],
        "a tier_change under rule 6 or 10 applies a resolver profile and carries its provenance"
        " (ADR-0003 L26; D-3)",
    )
    invalid(
        s,
        "tier-change-sweep-with-provenance",
        {
            **tier_sweep,
            "provenance": prov("green", None, "ig-account-resolver", "2026-11-05T10:13:58Z"),
            "retention_class": "meta_on_request",
        },
        ["provenance"],
        "a rule-9 tier_change comes from the sweep over stored statistics: no provenance (D-3)",
    )
    invalid(
        s,
        "dormant-decay-with-provenance",
        {
            **dormant_decay,
            "provenance": prov("green", None, "ig-account-resolver", "2026-11-05T10:13:58Z"),
            "retention_class": "meta_on_request",
        },
        ["provenance"],
        "a rule-9 dormant comes from the sweep over stored statistics: no provenance (D-3)",
    )
    invalid(
        s,
        "tier-change-rule-not-allowed",
        with_(tier_profile, ("tier_change", "rule_hit"), 4),
        ["producer", "service"],
        "the qualifier's tier_change comes from rules 6, 9 and 10 only (D-3)",
    )
    invalid(
        s,
        "not-a-decision-producer",
        {
            **add,
            "producer": {**add["producer"], "service": "keyword-matcher"},
            "requested_by": "keyword-matcher",
        },
        ["producer", "service"],
        "no producer row lets keyword-matcher send an add (ADR-0012, ADR-0013)",
    )
    invalid(
        s,
        "unknown-requester",
        {**add, "requested_by": "no-such-service"},
        ["requested_by"],
        "a requester that names a service is one the registry lists (Q18; F-09)",
    )
    invalid(
        s,
        "budget-wait-not-hashtag",
        {
            **dec(
                "fb-page-feed-poller",
                "2026-10-06T06:00:05Z",
                "update",
                "budget_wait",
                {"source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566"},
                {"source": {"route": "amber", "vendor": "sociavault"}},
                "budget-fb",
            )
        },
        ["producer", "service"],
        "budget_wait is ig-hashtag-search's alone (ADR-0052 L32 (c))",
    )
    invalid(
        s,
        "platform-meta-other-platform",
        with_(
            add,
            ("add", "source", "platform_meta"),
            {"uploads_playlist_id": "UUx3Kp9vQ2mLwR7tYb4nJ8sA"},
        ),
        ["add", "source", "platform_meta", "uploads_playlist_id"],
        "platform_meta keys belong to one platform and source type (ADR-0065 c), ADR-0041)",
    )
    invalid(
        s,
        "keyword-platform-meta-wrong-key",
        dec(
            "client-portal",
            "2026-10-06T07:40:00Z",
            "add",
            None,
            {"keyword_id": kw},
            {"platform_meta": {"instagram": {"linked_chat_id": "-1001987650000"}}},
            "kw-bad",
            requested_by=PERSON,
        ),
        ["add", "platform_meta", "instagram", "linked_chat_id"],
        "a keyword's Instagram platform_meta names its bound account only (F-13)",
    )
    invalid(
        s,
        "keyword-platform-meta-other-platform",
        dec(
            "client-portal",
            "2026-10-06T07:40:00Z",
            "add",
            None,
            {"keyword_id": kw},
            {"platform_meta": {"youtube": {"uploads_playlist_id": "UUx3"}}},
            "kw-yt",
            requested_by=PERSON,
        ),
        ["add", "platform_meta", "youtube"],
        "only Instagram hashtags carry keyword platform_meta (F-13)",
    )
    invalid(
        s,
        "lease-lapsed-still-covered",
        dec(
            "yt-pubsub-receiver",
            "2026-10-11T09:00:00Z",
            "push_coverage",
            "lease_lapsed",
            {"source_id": yt_channel},
            {"push_covered": True},
            "push-bad",
        ),
        ["push_coverage", "push_covered"],
        "a lapsed lease turns coverage off (ADR-0013)",
    )
    invalid(
        s,
        "ig-webhook-push-coverage",
        {
            **dec(
                "ig-webhook-receiver",
                "2026-10-06T09:00:00Z",
                "push_coverage",
                None,
                {"source_id": ig_own},
                {"push_covered": True},
                "push-ig",
            )
        },
        ["producer", "service"],
        "a client-owned Instagram account is never push_covered (ADR-0049, ADR-0066)",
    )
    invalid(
        s,
        "reject-without-expiry",
        without(reject, "reject", "expires_at"),
        ["reject", "expires_at"],
        "a reject carries its 180-day memory (qualifier §5.2)",
    )
    invalid(
        s,
        "rule-hit-out-of-range",
        dec(
            "qualifier",
            "2026-10-20T02:00:01Z",
            "dormant",
            None,
            {"source_id": IG_SOURCE},
            {"rule_hit": 11},
            "dormant-bad",
        ),
        ["dormant", "rule_hit"],
        "rule_hit is one of the qualifier's ten rules",
    )
    invalid(
        s,
        "tier-out-of-range",
        dec(
            "qualifier",
            "2026-10-20T02:00:00Z",
            "tier_change",
            None,
            {"source_id": IG_SOURCE},
            {"tier": 4, "rule_hit": 9},
            "tier-bad",
        ),
        ["tier_change", "tier"],
        "tiers are 1, 2 and 3 (ADR-0049)",
    )
    invalid(
        s,
        "retire-reason-not-allowed",
        dec(
            "qualifier",
            "2026-12-20T02:00:00Z",
            "retire",
            "owner_request",
            {"source_id": tt_source},
            {"rule_hit": 9},
            "retire-bad",
        ),
        ["producer", "service"],
        "owner_request is retention-purger's (ADR-0069)",
    )
    invalid(
        s,
        "review-unknown-reason",
        {**review, "reason": "suspended"},
        ["reason"],
        "the review reasons are ADR-0033's",
    )
    invalid(
        s,
        "amber-swap-with-scope",
        with_(canary, ("health_change", "scope"), "non_government"),
        ["health_change", "scope"],
        "an amber-to-amber swap declares no scope (source-health-canary L79, ADR-0052 L33 (d); R-2)",
    )
    invalid(
        s,
        "remove-client-without-client",
        dec(
            "retention-purger",
            "2026-10-13T00:10:00Z",
            "remove_client",
            "client_removed",
            {"source_id": IG_SOURCE},
            {},
            "remove-bad",
        ),
        ["remove_client", "client_id"],
        "remove_client names the client (retention-purger §5.3 L76)",
    )
    invalid(
        s,
        "promote-with-block",
        {
            **dec(
                "qualifier",
                "2026-10-21T02:00:00Z",
                "promote",
                None,
                {"source_id": tt_source},
                None,
                "promote-bad",
            ),
            "promote": {"rule_hit": 3},
        },
        ["promote"],
        "promote carries no block (ADR-0013)",
    )
    invalid(
        s,
        "queued-over-cap-reason",
        dec(
            "qualifier",
            "2026-10-06T10:15:00Z",
            "queued",
            "over_cap",
            {"candidate_key": "tiktok:6812345678901234567"},
            {"rule_hit": 5, "client_ids": [CLIENT]},
            "queued-bad",
            provenance=prov("amber", "tikhub", "tt-user-resolver", "2026-10-06T10:02:31Z"),
            retention_class="vendor_agreed",
        ),
        ["reason"],
        "over the cap is rule_hit 5 with reason null (qualifier §5.2)",
    )
    tolerant(s, "unknown-field", {**add, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"})
    tolerant(s, "unknown-source-column", with_(add, ("add", "source", "category"), "restaurant"))
    return None


# --------------------------------------------------------------------------------------------
# source.events/v1


def events() -> None:
    s = "source.events/v1"
    registry_cols = {
        "added_at": "2026-10-06T10:14:40Z",
        "health": "ok",
        "health_reason": None,
        "health_set_by": None,
        "health_changed_at": None,
        "notes": None,
    }

    def ev(
        at: str,
        event: str,
        reason: str | None,
        columns: dict[str, Any],
        previous: dict[str, Any] | None,
        decision_id: str,
        actor: str,
        name: str,
        message_id: str | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        m = meta(s, "registry-writer", job_id or ulid_for(at, "job", name), at, name=name)
        if message_id:
            m["message_id"] = message_id
        return {
            **m,
            "event": event,
            "reason": reason,
            "source_id": columns.pop("source_id"),
            **columns,
            "previous": previous,
            "decision_id": decision_id,
            "actor": actor,
            "at": at,
        }

    base_cols = {**IG_COLUMNS, **registry_cols}
    # registry-writer copies the qualifier decision's producer.job_id (F-17).
    decision = json.loads(
        (__import__("common").ROOT / "registry.decisions/v1/valid/prd-qualifier.json").read_text()
    )
    added = ev(
        "2026-10-06T10:14:40Z",
        "added",
        None,
        {"source_id": IG_SOURCE, **base_cols},
        None,
        IG_DECISION,
        "qualifier",
        "prd",
        message_id="01M48BAKM0NCCYDSZEC6V1PKHV",
        job_id=decision["producer"]["job_id"],
    )
    added["produced_at"] = "2026-10-06T10:14:41Z"
    valid(s, "prd-registry-writer", added)
    prd(
        "registry-writer",
        "docs/prds/shared/registry-writer.md",
        95,
        s,
        "prd-registry-writer",
        [
            R_META,
            "reason null added: every event carries reason, null where none applies (ADR-0014)",
            "url, display_name, lifecycle, push_covered, added_by, added_at, country_signals, lang_share, platform_meta, health, health_reason, health_set_by, health_changed_at and notes added: the source's columns after the change (ADR-0014, ADR-0013, ADR-0016, ADR-0049, ADR-0065)",
            "retention_class stays the source's registry column, which a control message may carry (ADR-0003)",
        ],
    )
    tier = ev(
        "2026-10-20T02:00:05Z",
        "tier_change",
        None,
        {"source_id": IG_SOURCE, **base_cols, "tier": 3},
        {"tier": 2},
        ulid_for("2026-10-20T02:00:00Z", "decision", "tier-sweep"),
        "qualifier",
        "tier",
    )
    valid(s, "tier-change", tier)
    valid(
        s,
        "updated-budget-wait",
        ev(
            "2026-10-06T06:00:07Z",
            "updated",
            "budget_wait",
            {
                "source_id": "e1d2c3b4-a596-4877-8b6a-5c4d3e2f1a09",
                **base_cols,
                "source_type": "hashtag",
                "platform_id": "17843853986012965",
                "handle": "زين_العراق",
                "url": None,
                "display_name": None,
                "route": "amber",
                "vendor": "sociavault",
                "added_by": "client",
                "followers": None,
                "country_signals": None,
                "lang_share": None,
                "retention_class": "vendor_agreed",
                "platform_meta": {"ig_user_id": "17841400112233445"},
            },
            {"route": "green", "vendor": None, "retention_class": "meta_on_request"},
            ulid_for("2026-10-06T06:00:05Z", "decision", "budget-amber"),
            "ig-hashtag-search",
            "budget",
        ),
    )
    valid(
        s,
        "updated-client-removed",
        ev(
            "2026-10-13T00:10:02Z",
            "updated",
            "client_removed",
            {"source_id": IG_SOURCE, **base_cols, "client_ids": [CLIENT]},
            {"client_ids": [CLIENT, CLIENT2]},
            ulid_for("2026-10-13T00:10:00Z", "decision", "offboarding"),
            "retention-purger",
            "removed",
        ),
    )
    valid(
        s,
        "lifecycle-dormant",
        ev(
            "2026-10-20T02:00:06Z",
            "lifecycle_change",
            None,
            {"source_id": IG_SOURCE, **base_cols, "lifecycle": "dormant"},
            {"lifecycle": "active"},
            ulid_for("2026-10-20T02:00:01Z", "decision", "dormant"),
            "qualifier",
            "dormant",
        ),
    )
    valid(
        s,
        "lifecycle-retired-not-found",
        ev(
            "2026-10-15T04:00:02Z",
            "lifecycle_change",
            "not_found",
            {
                "source_id": "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
                **base_cols,
                "platform": "x",
                "platform_id": "1456789012345678901",
                "handle": "example_telecom_iq",
                "url": "https://x.com/example_telecom_iq",
                "retention_class": "x_24h_sync",
                "lifecycle": "retired",
            },
            {"lifecycle": "active"},
            ulid_for("2026-10-15T04:00:00Z", "decision", "gone"),
            "x-user-timeline-poller",
            "retired",
        ),
    )
    health = ev(
        "2026-10-06T12:00:02Z",
        "health_change",
        "grant_missing",
        {
            "source_id": "d4c3b2a1-9f8e-4d7c-8b6a-5f4e3d2c1b0a",
            **base_cols,
            "owned_by_client": True,
            "added_by": "client",
            "health": "degraded",
            "health_reason": "grant_missing",
            "health_set_by": "ig-webhook-receiver",
            "health_changed_at": "2026-10-06T12:00:00Z",
        },
        {"health": "ok", "health_reason": None, "health_set_by": None, "health_changed_at": None},
        ulid_for("2026-10-06T12:00:00Z", "decision", "grant"),
        "ig-webhook-receiver",
        "health",
    )
    valid(s, "health-change", health)
    fb_cols = {
        **base_cols,
        "platform": "facebook",
        "source_type": "page",
        "platform_id": "104557812990341",
        "handle": None,
        "url": "https://www.facebook.com/profile.php?id=104557812990341",
        "display_name": "زين العراق - فرع البصرة",
        "followers": 9100,
    }
    fon = ev(
        "2026-10-06T11:30:03Z",
        "fallback_on",
        "auth",
        {
            "source_id": "5c0e8a24-7b1d-4f39-a6e2-9d3c1b7f0a58",
            **fb_cols,
            "route": "amber",
            "vendor": "sociavault",
            "retention_class": "vendor_agreed",
            "health": "fallback",
            "health_reason": "auth",
            "health_set_by": "source-health-canary",
            "health_changed_at": "2026-10-06T11:30:00Z",
        },
        {
            "health": "ok",
            "route": "green",
            "vendor": None,
            "retention_class": "meta_on_request",
            "health_reason": None,
            "health_set_by": None,
            "health_changed_at": None,
        },
        ulid_for("2026-10-06T11:30:00Z", "decision", "route-fb"),
        "source-health-canary",
        "fallback-on",
    )
    valid(s, "fallback-on", fon)
    valid(
        s,
        "fallback-off-flag-off",
        ev(
            "2026-10-06T15:00:03Z",
            "fallback_off",
            "flag_off",
            {
                "source_id": "5c0e8a24-7b1d-4f39-a6e2-9d3c1b7f0a58",
                **fb_cols,
                "health": "degraded",
                "health_reason": "flag_off",
                "health_set_by": "source-health-canary",
                "health_changed_at": "2026-10-06T15:00:00Z",
            },
            {
                "health": "fallback",
                "route": "amber",
                "vendor": "sociavault",
                "retention_class": "vendor_agreed",
                "health_reason": "auth",
                "health_changed_at": "2026-10-06T11:30:00Z",
            },
            ulid_for("2026-10-06T15:00:00Z", "decision", "route-flag"),
            "source-health-canary",
            "fallback-off",
        ),
    )
    valid(
        s,
        "fallback-on-flag-on",
        {
            **fon,
            "reason": "flag_on",
            "health_reason": "flag_on",
            "actor": PERSON,
            "message_id": ulid_for("2026-10-08T14:00:03Z", s, "flag-on"),
            "decision_id": ulid_for("2026-10-08T14:00:00Z", "decision", "flag-on"),
        },
    )
    valid(
        s,
        "push-coverage-change",
        ev(
            "2026-10-11T09:00:02Z",
            "push_coverage_change",
            "lease_lapsed",
            {
                "source_id": "3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
                **base_cols,
                "platform": "youtube",
                "source_type": "channel",
                "platform_id": "UCx3Kp9vQ2mLwR7tYb4nJ8sA",
                "handle": "@shorja.tv",
                "url": "https://www.youtube.com/channel/UCx3Kp9vQ2mLwR7tYb4nJ8sA",
                "display_name": "سوق الشورجة",
                "retention_class": "youtube_30d_text",
                "push_covered": False,
                "platform_meta": {"uploads_playlist_id": "UUx3Kp9vQ2mLwR7tYb4nJ8sA"},
            },
            {"push_covered": True},
            ulid_for("2026-10-11T09:00:00Z", "decision", "push-off"),
            "yt-pubsub-receiver",
            "push",
        ),
    )
    metadata_invalids(s, added)
    invalid(
        s,
        "added-with-previous",
        {**added, "previous": {"tier": 3}},
        ["previous"],
        "previous is null on added (ADR-0014)",
    )
    invalid(
        s,
        "unknown-actor",
        {**added, "actor": "no-such-service"},
        ["actor"],
        "an actor that names a service is one the registry lists (Q18; F-09)",
    )
    invalid(
        s,
        "tier-change-with-space",
        {**tier, "event": "tier change"},
        ["event"],
        "tier change becomes tier_change (ADR-0014)",
    )
    invalid(
        s,
        "retired-as-event",
        {**tier, "event": "retired"},
        ["event"],
        "dormant and retired become lifecycle_change (ADR-0014)",
    )
    invalid(
        s,
        "backfill-status",
        {**tier, "event": "updated", "backfill_status": "done"},
        ["backfill_status"],
        "backfill_status events go (ADR-0020)",
    )
    invalid(
        s,
        "provenance",
        {**added, "provenance": IG_PROV},
        ["provenance"],
        "a control message carries producer only (ADR-0003)",
    )
    invalid(
        s,
        "service-field",
        {**added, "service": "registry-writer"},
        ["service"],
        "service gives way to producer (ADR-0002)",
    )
    invalid(
        s,
        "fallback-on-not-fallback",
        {**fon, "health": "degraded"},
        ["health"],
        "entering fallback gives fallback_on (ADR-0014 L27, ADR-0050 L31)",
    )
    invalid(
        s,
        "health-change-to-fallback",
        {**health, "health": "fallback"},
        ["health"],
        "entering fallback is fallback_on, never health_change (ADR-0014 L27)",
    )
    invalid(
        s,
        "reason-not-on-type",
        {**tier, "reason": "lease_lapsed"},
        ["reason"],
        "each reason only on the types the closed list names (ADR-0014)",
    )
    invalid(
        s,
        "flag-on-on-fallback-off",
        {**fon, "event": "fallback_off", "health": "degraded", "reason": "flag_on"},
        ["reason"],
        "flag_on travels on fallback_on (ADR-0021)",
    )
    invalid(
        s,
        "not-registry-writer",
        {**added, "producer": {**added["producer"], "service": "qualifier"}},
        ["producer", "service"],
        "registry-writer alone writes source.events (ADR-0014)",
    )
    invalid(
        s,
        "platform-meta-other-type",
        with_(added, ("platform_meta",), {"linked_chat_id": "-1001987650000"}),
        ["platform_meta", "linked_chat_id"],
        "platform_meta keys belong to one platform and source type (ADR-0013 c))",
    )
    invalid(
        s,
        "lifecycle-decay-reason",
        {
            **tier,
            "event": "lifecycle_change",
            "lifecycle": "dormant",
            "previous": {"lifecycle": "active"},
            "reason": "decay",
        },
        ["reason"],
        "decay is the qualifier's rule_hit, not a reason (ADR-0014)",
    )
    invalid(
        s,
        "push-coverage-flag-reason",
        {
            **tier,
            "event": "push_coverage_change",
            "push_covered": False,
            "previous": {"push_covered": True},
            "reason": "flag_off",
        },
        ["reason"],
        "push_coverage_change takes lease_lapsed or subscription_failed (ADR-0014)",
    )
    tolerant(s, "unknown-field", {**added, "registry_version": 3})


# --------------------------------------------------------------------------------------------
# jobs.completed/v1


def completed() -> None:
    s = "jobs.completed/v1"

    def rep(
        queue: str,
        kind: str,
        job: str,
        at: str,
        status: str,
        reason: str | None,
        report: dict[str, Any] | None = None,
        name: str = "",
        **fields: Any,
    ) -> dict[str, Any]:
        service = queue.removeprefix("jobs.").removesuffix(".priority")
        out = {
            **meta(s, service, job, at, name=name or kind),
            "job_id": job,
            "queue": queue,
            "kind": kind,
            **fields,
            "attempt": fields.pop("attempt", 1),
            "status": status,
            "reason": reason,
            "finished_at": at,
            "report": report
            or {
                "new_count": 0,
                "seen_count": 0,
                "pages": 1,
                "cost_units": 1,
                "reply_candidates": [],
            },
        }
        return out

    fb_src = "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11"
    done = rep(
        "jobs.fb-page-feed-poller",
        "rotation",
        "01M48DXKW0Q8N3K5D2B7T4W9XC",
        "2026-10-06T09:15:44Z",
        "done",
        None,
        {"new_count": 3, "seen_count": 22, "pages": 2, "cost_units": 2, "reply_candidates": []},
        source_id=fb_src,
    )
    valid(s, "done-rotation", done)
    xs = "7c1d9a2e-55b4-4f1e-8a0c-3e9f6b2d4a71"
    xrot = rep(
        "jobs.x-recent-search",
        "rotation",
        "01M487XBH0A2B4C6D8E0F2G4H6",
        "2026-10-06T09:16:00Z",
        "partial",
        None,
        {"new_count": 41, "seen_count": 3, "pages": 4, "cost_units": 44, "reply_candidates": []},
        source_id=xs,
        paid_user_reads=41,
        free_rereads=3,
        uncovered={"window_start": "2026-10-06T08:00:00Z", "window_end": "2026-10-06T08:20:00Z"},
    )
    valid(s, "partial-x-rotation-uncovered", xrot)
    xgap = rep(
        "jobs.x-recent-search",
        "reconciliation",
        "01M487XBH0B2C4D6E8F0G2H4J6",
        "2026-10-06T09:40:00Z",
        "done",
        None,
        {"new_count": 12, "seen_count": 0, "pages": 1, "cost_units": 12, "reply_candidates": []},
        source_id=xs,
        paid_user_reads=12,
        free_rereads=0,
        gap_unfilled=None,
    )
    valid(s, "done-x-gap", xgap)
    valid(
        s,
        "partial-x-gap-unfilled",
        {
            **xgap,
            "status": "partial",
            "gap_unfilled": {
                "window_start": "2026-10-06T07:00:00Z",
                "window_end": "2026-10-06T07:05:00Z",
            },
            "message_id": ulid_for("2026-10-06T09:40:01Z", s, "gap2"),
        },
    )
    capped = rep(
        "jobs.fb-backfill",
        "backfill",
        "01M48DXKW00GHZSJPM5NRWV7R3",
        "2026-10-06T11:20:00Z",
        "capped",
        None,
        {"new_count": 600, "seen_count": 0, "pages": 24, "cost_units": 24, "reply_candidates": []},
        source_id=fb_src,
        capped_reason="route_cap",
        oldest_item_at="2026-08-02T06:11:00Z",
        attempt=2,
    )
    valid(s, "capped-backfill", capped)
    valid(
        s,
        "capped-keyword-history",
        rep(
            "jobs.x-full-archive-search",
            "keyword_history",
            "01M48E1KW0Q8N3K5D2B7T4W9XC",
            "2026-10-06T12:00:00Z",
            "capped",
            None,
            {"new_count": 0, "seen_count": 0, "pages": 1, "cost_units": 1, "reply_candidates": []},
            source_id=xs,
            capped_reason="no_history",
            oldest_item_at=None,
            paid_user_reads=0,
            free_rereads=0,
        ),
    )
    post = "100064583471102_1198837625012734"
    pref = {"item_id": iid("facebook", "post", post), "platform": "facebook", "platform_id": post}
    comments = rep(
        "jobs.fb-post-comments-fetcher",
        "comments",
        comment_decay_job_id("2026-10-06T15:14:00Z", pref["item_id"], "comments", "+6h"),
        "2026-10-06T15:15:10Z",
        "done",
        None,
        {
            "new_count": 18,
            "seen_count": 40,
            "pages": 3,
            "cost_units": 3,
            "reply_candidates": [{"thread_id": "1198837625012734_884512", "reply_count": 7}],
        },
        source_id=fb_src,
        post_ref=pref,
        series_step="+6h",
        complete=True,
        stored_before=40,
        comments_total=None,
    )
    valid(s, "done-comments", comments)
    yt_pref: dict[str, Any] = {
        "item_id": iid("youtube", "video", "dQw4w9WgXcQ"),
        "platform": "youtube",
        "platform_id": "dQw4w9WgXcQ",
        "thread_ids": ["UgzK7pQ2mV9xR4tL1bN6AaABAg"],
    }
    valid(
        s,
        "done-replies-unchanged",
        rep(
            "jobs.yt-replies-fetcher",
            "replies",
            "01M48F0V80ZZGG928KMD5XX36J",
            "2026-10-07T07:03:00Z",
            "done",
            None,
            {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 0, "reply_candidates": []},
            source_id="3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
            post_ref=yt_pref,
            series_step="+24h",
            complete=True,
            stored_before=3,
            comments_total=None,
        ),
    )
    valid(
        s,
        "quota-denied",
        rep(
            "jobs.x-user-timeline-poller",
            "rotation",
            "01M48G0V80ZZGG928KMD5XX36J",
            "2026-10-06T10:00:00Z",
            "quota_denied",
            None,
            {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 0, "reply_candidates": []},
            source_id="a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
            paid_user_reads=0,
            free_rereads=0,
        ),
    )
    valid(
        s,
        "failed-dead-lettered",
        rep(
            "jobs.ig-account-media-poller",
            "rotation",
            "01M48H0V80ZZGG928KMD5XX36J",
            "2026-10-06T10:30:00Z",
            "failed",
            None,
            {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 5, "reply_candidates": []},
            source_id="b9e0f1a2-3c4d-4e5f-8a6b-7c8d9e0f1a2b",
            attempt=5,
        ),
    )
    valid(
        s,
        "skipped-flag-off",
        rep(
            "jobs.tt-keyword-search",
            "rotation",
            "01M48J0V80ZZGG928KMD5XX36J",
            "2026-10-06T10:31:00Z",
            "skipped_flag_off",
            "flag_off",
            {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 0, "reply_candidates": []},
            source_id="1e2d3c4b-5a69-4788-9a6b-5c4d3e2f1a0b",
        ),
    )
    not_allowed = rep(
        "jobs.x-replies-fetcher",
        "comments",
        "01M48K0V80ZZGG928KMD5XX36J",
        "2026-10-06T10:32:00Z",
        "not_allowed",
        "outside_window",
        {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 0, "reply_candidates": []},
        source_id=xs,
        post_ref={
            "item_id": iid("x", "post", "1843201122334455667"),
            "platform": "x",
            "platform_id": "1843201122334455667",
        },
        series_step="+7d",
        paid_user_reads=0,
        free_rereads=0,
    )
    valid(s, "not-allowed", not_allowed)
    valid(
        s,
        "gone-comments-disabled",
        rep(
            "jobs.yt-comments-fetcher",
            "comments",
            "01M48M0V80ZZGG928KMD5XX36J",
            "2026-10-06T10:33:00Z",
            "gone",
            "comments_disabled",
            {"new_count": 0, "seen_count": 0, "pages": 1, "cost_units": 1, "reply_candidates": []},
            source_id="3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
            post_ref={
                "item_id": iid("youtube", "video", "q3Vt8LmZ2xA"),
                "platform": "youtube",
                "platform_id": "q3Vt8LmZ2xA",
            },
            series_step="+1h",
            complete=False,
            stored_before=0,
            comments_total=None,
        ),
    )
    valid(
        s,
        "done-resolver-refresh",
        rep(
            "jobs.x-user-resolver",
            "refresh",
            "01M48N0V80ZZGG928KMD5XX36J",
            "2026-11-05T11:02:40Z",
            "done",
            None,
            candidate_key="x:1456789012345678901",
            source_id="a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
            paid_user_reads=1,
            free_rereads=0,
        ),
    )
    valid(
        s,
        "done-robots-refresh",
        rep(
            "jobs.news-robots-checker",
            "refresh",
            "01J9N3Q8D5W2K7X1R4T9V0MZBD",
            "2026-10-07T06:30:15Z",
            "done",
            None,
            host="www.example-daily.iq",
        ),
    )
    valid(
        s,
        "done-commoncrawl-rotation",
        rep(
            "jobs.web-commoncrawl-scanner",
            "rotation",
            "01M4F71ZR0A8N3K5D2B7T4W9XC",
            "2026-10-09T03:00:00Z",
            "done",
            None,
            {
                "new_count": 14,
                "seen_count": 220,
                "pages": 40,
                "cost_units": 0,
                "reply_candidates": [],
            },
            crawl_id="CC-MAIN-2026-38",
        ),
    )
    valid(
        s,
        "done-rematch",
        rep(
            "jobs.keyword-matcher",
            "rematch",
            "01M4G00000A8N3K5D2B7T4W9XC",
            "2026-10-06T13:00:00Z",
            "done",
            None,
            {
                "new_count": 210,
                "seen_count": 0,
                "pages": 0,
                "cost_units": 0,
                "reply_candidates": [],
            },
            client_id=CLIENT,
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DG",
        ),
    )
    valid(
        s,
        "done-analysis-priority-lane",
        rep(
            "jobs.analysis-sentiment.priority",
            "analyze",
            "01M4886GG018V1FH131HTSP75D",
            "2026-10-06T09:15:12Z",
            "done",
            None,
            {"new_count": 1, "seen_count": 0, "pages": 0, "cost_units": 1, "reply_candidates": []},
            source_id="a3c0f1e2-5b6d-4c7e-9f80-112233445566",
        ),
    )
    valid(
        s,
        "done-export",
        rep(
            "jobs.x-compliance-sync",
            "export",
            "01M4H00000A8N3K5D2B7T4W9XC",
            "2026-10-07T10:00:00Z",
            "done",
            None,
            {"new_count": 0, "seen_count": 0, "pages": 0, "cost_units": 0, "reply_candidates": []},
            client_id=None,
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DH",
        ),
    )
    metadata_invalids(s, done)
    invalid(
        s,
        "kind-field-on-other-kind",
        {**done, "complete": True},
        ["complete"],
        "complete is a comments and replies field (ADR-0017)",
    )
    invalid(
        s,
        "oldest-item-on-comments",
        {**comments, "oldest_item_at": "2026-10-06T08:00:00Z"},
        ["oldest_item_at"],
        "oldest_item_at is a backfill and keyword_history field (ADR-0017)",
    )
    invalid(
        s,
        "x-field-off-x",
        {**done, "paid_user_reads": 3},
        ["paid_user_reads"],
        "paid_user_reads is an X job's field (ADR-0017)",
    )
    invalid(
        s,
        "uncovered-not-partial",
        {**xrot, "status": "done"},
        ["uncovered"],
        "an uncovered window goes with status partial (ADR-0064)",
    )
    invalid(
        s,
        "uncovered-on-gap-job",
        {
            **xgap,
            "uncovered": {
                "window_start": "2026-10-06T08:00:00Z",
                "window_end": "2026-10-06T08:20:00Z",
            },
        },
        ["uncovered"],
        "uncovered belongs to the rotation on jobs.x-recent-search (ADR-0064)",
    )
    invalid(
        s,
        "gap-unfilled-on-rotation",
        {**xrot, "gap_unfilled": None},
        ["gap_unfilled"],
        "gap_unfilled belongs to the X gap job (ADR-0064)",
    )
    invalid(
        s,
        "capped-without-reason",
        without(capped, "capped_reason"),
        ["capped_reason"],
        "a capped job names its cap (ADR-0020)",
    )
    invalid(
        s,
        "capped-reason-on-done",
        {**done, "capped_reason": "budget"},
        ["capped_reason"],
        "capped_reason goes with status capped (ADR-0020)",
    )
    invalid(
        s,
        "unknown-not-allowed-reason",
        {**not_allowed, "reason": "skipped_government"},
        ["reason"],
        "one spelling, amber_excluded_government (Q8)",
    )
    invalid(s, "status-ok", {**done, "status": "ok"}, ["status"], "ok becomes done (ADR-0017)")
    invalid(
        s,
        "coverage-days",
        {**capped, "coverage_days": 90},
        ["coverage_days"],
        "coverage_days goes (ADR-0017)",
    )
    invalid(
        s,
        "report-capped",
        with_(capped, ("report", "capped"), True),
        ["report", "capped"],
        "the status says capped (ADR-0017)",
    )
    invalid(
        s,
        "not-the-queue-service",
        {**done, "producer": {**done["producer"], "service": "fb-backfill"}},
        ["producer", "service"],
        "the job wrapper of the queue's own service writes the report (ADR-0017)",
    )
    invalid(
        s,
        "missing-key",
        without(done, "source_id"),
        ["source_id"],
        "a report carries its job's partition key (ADR-0004, ADR-0017)",
    )
    invalid(
        s,
        "provenance",
        {**done, "provenance": prov("green", None, "fb-page-feed-poller", "2026-10-06T09:15:40Z")},
        ["provenance"],
        "a control message carries producer only (ADR-0003)",
    )
    invalid(
        s,
        "negative-cost",
        with_(done, ("report", "cost_units"), -1),
        ["report", "cost_units"],
        "cost_units is not negative",
    )
    root = __import__("common").ROOT

    def load(name: str) -> dict[str, Any]:
        return json.loads((root / s / "valid" / name).read_text())

    invalid(
        s,
        "quota-denied-with-reason",
        {**load("quota-denied.json"), "reason": "budget"},
        ["reason"],
        "quota_denied carries no reason (Q8)",
    )
    invalid(
        s,
        "failed-with-capped-reason",
        {**load("failed-dead-lettered.json"), "capped_reason": "failed"},
        ["capped_reason"],
        "capped_reason goes with status capped (ADR-0020)",
    )
    invalid(
        s,
        "skipped-without-reason",
        {**load("skipped-flag-off.json"), "reason": None},
        ["reason"],
        "a flag-off skip names flag_off (Q8)",
    )
    invalid(
        s,
        "gone-video-gone",
        {**load("gone-comments-disabled.json"), "reason": "video_gone"},
        ["reason"],
        "one spelling, not_found (Q8)",
    )
    tolerant(s, "unknown-report-field", with_(done, ("report", "dropped_count"), 0))


# --------------------------------------------------------------------------------------------
# job/v1


def jobs() -> None:
    s = "job/v1"

    def job(
        queue: str,
        service: str,
        kind: str,
        job_id: str,
        due_at: str,
        name: str,
        produced_at: str | None = None,
        producer_job: str | None = None,
        **fields: Any,
    ) -> dict[str, Any]:
        at = produced_at or due_at
        # producer.job_id (F-17): a scheduler's job carries its own job_id, a D3 writer's the
        # request's request_id, any other job the job or input message its producer was handling.
        if producer_job is not None:
            run = producer_job
        elif service == "comment-decay-scheduler":
            run = job_id
        elif service in ("admin-api", "client-portal", "admin-console") and "request_id" in fields:
            run = fields["request_id"]
        else:
            run = ulid_for(at, "run", service, name)
        return {
            **meta(s, service, run, at, name=name),
            "job_id": job_id,
            "kind": kind,
            "due_at": due_at,
            "attempt": fields.pop("attempt", 1),
            **fields,
        }

    def v(name: str, queue: str, obj: dict[str, Any]) -> dict[str, Any]:
        return valid(s, name, obj, queue=queue)

    def raw_job(name: str) -> str:
        """The job_id of a raw record written earlier, which the job it led to copies (F-17)."""
        raw = json.loads(
            (__import__("common").ROOT / f"raw.items/v1/valid/{name}.json").read_text()
        )
        return str(raw["envelope"]["job_id"])

    def bad(name: str, queue: str, obj: dict[str, Any], path: list[str | int], rule: str) -> None:
        invalid(s, name, obj, path, rule, queue=queue)

    fb_src = "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11"
    # backfill-orchestrator §6.2 L106
    bf = job(
        "jobs.fb-backfill",
        "backfill-orchestrator",
        "backfill",
        "01J9P3Y6B2N7C4D8F0G5H1JKQR",
        "2026-10-06T10:14:44Z",
        "prd",
        source_id=fb_src,
        run_id=ulid_for("2026-10-06T10:14:40Z", "backfill-run", fb_src),
        reason="add",
        window_start="2026-07-08T10:14:44Z",
        window_end="2026-10-06T10:14:44Z",
        cap={"max_age_days": 90, "max_items": 600},
    )
    v("prd-backfill-orchestrator", "jobs.fb-backfill", bf)
    prd(
        "backfill-orchestrator",
        "docs/prds/shared/backfill-orchestrator.md",
        106,
        s,
        "prd-backfill-orchestrator",
        [
            "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)",
            "route and vendor go: a job never carries them (ADR-0011, ADR-0018)",
            "run_id initial becomes a ULID; reason add says why the backfill runs (ADR-0020)",
            "window_start and window_end added: the 90-day cap's window (ADR-0020)",
        ],
        note="sent on jobs.fb-backfill, the source's backfill queue",
    )
    post = "100064583471102_1198837625012734"
    pref = {"item_id": iid("facebook", "post", post), "platform": "facebook", "platform_id": post}
    cm = job(
        "jobs.fb-post-comments-fetcher",
        "comment-decay-scheduler",
        "comments",
        comment_decay_job_id("2026-10-06T15:14:00Z", pref["item_id"], "comments", "+6h"),
        "2026-10-06T15:14:00Z",
        "prd",
        produced_at="2026-10-06T09:16:02Z",
        source_id=fb_src,
        post_ref=pref,
        series_step="+6h",
        profile="fb_page",
    )
    v("prd-comment-decay-scheduler", "jobs.fb-post-comments-fetcher", cm)
    prd(
        "comment-decay-scheduler",
        "docs/prds/shared/comment-decay-scheduler.md",
        141,
        s,
        "prd-comment-decay-scheduler",
        [
            "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)",
            "route and vendor go (ADR-0011, ADR-0018)",
            "job_id the deterministic ULID of (due_at; item_id, lane, series_step), so a replayed schedule repeats it (ADR-0006)",
            "post_ref.item_id from the post's key with the key helper (ADR-0006)",
        ],
        note="sent on jobs.fb-post-comments-fetcher (profile fb_page)",
    )
    vid = "k7Qm2Xv9TbE"
    fs = job(
        "jobs.yt-video-details-fetcher",
        "yt-pubsub-receiver",
        "first_sight",
        "01J9N7QW3E5R8T2Y6V0H4M9P1A",
        "2026-10-06T09:12:44Z",
        "prd",
        producer_job=raw_job("prd-yt-pubsub-receiver"),
        source_id="3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
        post_ref={
            "item_id": iid("youtube", "video", vid),
            "platform": "youtube",
            "platform_id": vid,
        },
        origin_kind="push",
    )
    v("prd-yt-pubsub-receiver", "jobs.yt-video-details-fetcher", fs)
    prd(
        "yt-pubsub-receiver",
        "docs/prds/youtube/yt-pubsub-receiver.md",
        127,
        s,
        "prd-yt-pubsub-receiver",
        [
            "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)",
            "post_ref the scheduler's object for one video, not a bare id (ADR-0011, ADR-0065 a))",
            "series_step goes; origin_kind push added (ADR-0065 a))",
        ],
        note="the PRD's second example; its raw.items example is under raw.items/v1",
    )
    rv = "Xk3vQ9pL2aE"
    fr = job(
        "jobs.yt-video-details-fetcher",
        "yt-uploads-reconciler",
        "first_sight",
        "01J9P4D3A1M6W2C8F5H0K7N4QS",
        "2026-10-06T11:04:28Z",
        "prd",
        producer_job=raw_job("prd-yt-uploads-reconciler"),
        source_id="a3d9f1c4-5e27-4b8a-9f60-2c1e7d4b8a93",
        post_ref={"item_id": iid("youtube", "video", rv), "platform": "youtube", "platform_id": rv},
        origin_kind="reconciliation",
    )
    v("prd-yt-uploads-reconciler", "jobs.yt-video-details-fetcher", fr)
    prd(
        "yt-uploads-reconciler",
        "docs/prds/youtube/yt-uploads-reconciler.md",
        133,
        s,
        "prd-yt-uploads-reconciler",
        [
            "schema, message_id, produced_at and producer stamped by the SDK (ADR-0002)",
            "the id list becomes one job per video, post_ref the scheduler's object (ADR-0065 a), ADR-0011)",
            "due_at added (ADR-0011)",
        ],
        note="the PRD's second example (b7Tz0qR4mWc gets its own job); its raw.items example is under raw.items/v1",
    )

    rot = job(
        "jobs.fb-page-feed-poller",
        "fb-page-feed-poller",
        "rotation",
        "01M48DXKW0Q8N3K5D2B7T4W9XC",
        "2026-10-06T09:15:00Z",
        "rot",
        source_id=fb_src,
        tier=1,
    )
    v("rotation", "jobs.fb-page-feed-poller", rot)
    bad(
        "tier-true",
        "jobs.fb-page-feed-poller",
        {**rot, "tier": True},
        ["tier"],
        "a constant keeps its JSON type: 0 is not false and true is not 1 (finding 6)",
    )
    tag = "e1d2c3b4-a596-4877-8b6a-5c4d3e2f1a09"
    igrot = job(
        "jobs.ig-hashtag-search",
        "ig-hashtag-search",
        "rotation",
        "01M48DXKW0R8N3K5D2B7T4W9XC",
        "2026-10-06T06:00:00Z",
        "igrot",
        source_id=tag,
        edge="recent_media",
    )
    v("rotation-hashtag-edge", "jobs.ig-hashtag-search", igrot)
    ccrot = job(
        "jobs.web-commoncrawl-scanner",
        "web-commoncrawl-scanner",
        "rotation",
        "01M4F71ZR0A8N3K5D2B7T4W9XC",
        "2026-10-09T02:00:00Z",
        "ccrot",
        crawl_id="CC-MAIN-2026-38",
    )
    v("rotation-commoncrawl", "jobs.web-commoncrawl-scanner", ccrot)
    v(
        "reconciliation-daily",
        "jobs.tg-bot-channel-receiver",
        job(
            "jobs.tg-bot-channel-receiver",
            "tg-bot-channel-receiver",
            "reconciliation",
            "01M48P0V80ZZGG928KMD5XX36J",
            "2026-10-07T03:00:00Z",
            "daily",
            source_id="8a3f1c6e-2b9d-4e70-b5a4-f0c9d2e1b7a8",
        ),
    )
    xs = "7c1d9a2e-55b4-4f1e-8a0c-3e9f6b2d4a71"
    xgap = job(
        "jobs.x-recent-search",
        "x-filtered-stream",
        "reconciliation",
        "01M487XBH0B2C4D6E8F0G2H4J6",
        "2026-10-06T09:30:00Z",
        "gap",
        source_id=xs,
        query='("دجلة تيليكوم" OR "Dijla Telecom") lang:ar',
        window_start="2026-10-06T08:55:00Z",
        window_end="2026-10-06T09:25:00Z",
        source_ids=[xs],
        client_ids=[CLIENT],
    )
    v("reconciliation-x-gap", "jobs.x-recent-search", xgap)
    li_post = linkedin_post_id("7248000000000000000", "activity")
    li_pref: dict[str, Any] = {
        "item_id": iid("linkedin", "post", li_post),
        "platform": "linkedin",
        "platform_id": li_post,
    }
    v(
        "reconciliation-thread",
        "jobs.li-own-comments-fetcher",
        job(
            "jobs.li-own-comments-fetcher",
            "comment-decay-scheduler",
            "reconciliation",
            "01M48Q0V80ZZGG928KMD5XX36J",
            "2026-10-08T09:00:00Z",
            "thread",
            source_id="0f9e8d7c-6b5a-4493-8271-605f4e3d2c1b",
            post_ref=li_pref,
        ),
    )
    v(
        "reconciliation-lease-lapsed",
        "jobs.yt-uploads-reconciler",
        job(
            "jobs.yt-uploads-reconciler",
            "yt-uploads-reconciler",
            "reconciliation",
            "01M48R0V80ZZGG928KMD5XX36J",
            "2026-10-11T09:05:00Z",
            "lease",
            source_id="3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
            reason="lease_lapsed",
        ),
    )
    ig_pref: dict[str, Any] = {
        "item_id": iid("instagram", "post", "17990012345678901"),
        "platform": "instagram",
        "platform_id": "17990012345678901",
    }
    v(
        "reconciliation-webhook",
        "jobs.ig-own-comments-fetcher",
        job(
            "jobs.ig-own-comments-fetcher",
            "ig-webhook-receiver",
            "reconciliation",
            "01M48S0V80ZZGG928KMD5XX36J",
            "2026-10-06T12:05:00Z",
            "webhook",
            source_id="d4c3b2a1-9f8e-4d7c-8b6a-5f4e3d2c1b0a",
            post_ref=ig_pref,
        ),
    )
    v(
        "backfill-hashtag-edge",
        "jobs.ig-hashtag-search",
        job(
            "jobs.ig-hashtag-search",
            "backfill-orchestrator",
            "backfill",
            "01M48T0V80ZZGG928KMD5XX36J",
            "2026-10-06T06:10:00Z",
            "bf-tag",
            source_id=tag,
            run_id=ulid_for("2026-10-06T06:09:00Z", "backfill-run", tag),
            reason="client",
            window_start="2026-09-29T06:10:00Z",
            window_end="2026-10-06T06:10:00Z",
            cap={"max_age_days": 7, "max_items": None},
            edge="top_media",
        ),
    )
    kh = job(
        "jobs.x-full-archive-search",
        "backfill-orchestrator",
        "keyword_history",
        "01M48E1KW0Q8N3K5D2B7T4W9XC",
        "2026-10-06T11:58:00Z",
        "kh",
        source_id=xs,
        run_id=ulid_for("2026-10-06T11:57:00Z", "backfill-run", xs),
        reason="add",
        window_start="2026-09-06T11:58:00Z",
        window_end="2026-10-06T11:58:00Z",
        cap={"max_age_days": 30, "max_items": 2000},
    )
    v("keyword-history", "jobs.x-full-archive-search", kh)
    yt_pref: dict[str, Any] = {
        "item_id": iid("youtube", "video", "dQw4w9WgXcQ"),
        "platform": "youtube",
        "platform_id": "dQw4w9WgXcQ",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "thread_ids": ["UgzK7pQ2mV9xR4tL1bN6AaABAg"],
    }
    rep_job = job(
        "jobs.yt-replies-fetcher",
        "comment-decay-scheduler",
        "replies",
        comment_decay_job_id("2026-10-07T07:00:00Z", yt_pref["item_id"], "comments", "+24h"),
        "2026-10-07T07:00:00Z",
        "replies",
        produced_at="2026-10-06T07:00:00Z",
        source_id="3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
        post_ref=yt_pref,
        series_step="+24h",
        profile="yt",
    )
    v("replies-thread-ids", "jobs.yt-replies-fetcher", rep_job)
    x_pref: dict[str, Any] = {
        "item_id": iid("x", "post", "1843201122334455667"),
        "platform": "x",
        "platform_id": "1843201122334455667",
    }
    xr = job(
        "jobs.x-full-archive-search",
        "comment-decay-scheduler",
        "replies",
        comment_decay_job_id("2026-10-13T08:51:40Z", x_pref["item_id"], "comments", "+7d"),
        "2026-10-13T08:51:40Z",
        "xreplies",
        produced_at="2026-10-06T09:16:00Z",
        source_id=xs,
        post_ref=x_pref,
        series_step="+7d",
        profile="x",
        window_start="2026-10-06T08:51:40Z",
    )
    v("replies-x-window", "jobs.x-full-archive-search", xr)
    mpref = {"item_id": iid("facebook", "post", post), "platform": "facebook", "platform_id": post}
    mj = job(
        "jobs.fb-reactions-fetcher",
        "comment-decay-scheduler",
        "metrics",
        comment_decay_job_id("2026-10-07T07:12:09Z", mpref["item_id"], "metrics", "+24h"),
        "2026-10-07T07:12:09Z",
        "metrics",
        produced_at="2026-10-06T09:16:03Z",
        source_id=fb_src,
        post_ref=mpref,
        series_step="+24h",
    )
    v("metrics", "jobs.fb-reactions-fetcher", mj)
    refresh_job = ulid_for("2026-10-07T07:20:00Z", "refresh-job")
    v(
        "metrics-client-refresh",
        "jobs.fb-reactions-fetcher",
        {
            **mj,
            "producer": {**mj["producer"], "job_id": refresh_job},
            "job_id": refresh_job,
            "due_at": "2026-10-07T07:20:00Z",
            "series_step": "refresh:01J9R5S3V7W1X4Y8Z0A2B6C9DE",
            "message_id": ulid_for("2026-10-07T07:19:00Z", s, "mrefresh"),
        },
    )
    v(
        "refresh-resolver",
        "jobs.x-user-resolver",
        job(
            "jobs.x-user-resolver",
            "x-user-resolver",
            "refresh",
            "01M48N0V80ZZGG928KMD5XX36J",
            "2026-11-05T11:00:00Z",
            "xref",
            candidate_key="x:1456789012345678901",
            source_id="a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
        ),
    )
    site = "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90"
    v(
        "refresh-news-site",
        "jobs.news-site-resolver",
        job(
            "jobs.news-site-resolver",
            "news-feed-poller",
            "refresh",
            "01M48T1V80ZZGG928KMD5XX36J",
            "2026-10-06T05:48:00Z",
            "siteref",
            candidate_key=news_site_candidate_key("example-daily.iq"),
            source_id=site,
            reason="feed_gone",
        ),
    )
    robots = job(
        "jobs.news-robots-checker",
        "news-robots-checker",
        "refresh",
        "01J9N3Q8D5W2K7X1R4T9V0MZBD",
        "2026-10-07T06:30:14Z",
        "robots",
        host="www.example-daily.iq",
    )
    v("refresh-robots", "jobs.news-robots-checker", robots)
    purge_pref = {**yt_pref}
    purge = job(
        "jobs.yt-comments-fetcher",
        "yt-text-purger",
        "refresh",
        "01M47F1V80FZGG928KMD5XX36J",
        "2026-10-06T02:10:00Z",
        "purge",
        source_id="2d7e9b41-5c3a-4f8e-b1d6-7a0c9e3f5b28",
        post_ref=purge_pref,
        run_id="01M47F0V80FZGG928KMD5XX36J",
        must_finish_by="2026-10-06T19:42:10Z",
        refresh_for_client_ids=[CLIENT],
    )
    v("refresh-before-purge", "jobs.yt-comments-fetcher", purge)
    v(
        "refresh-own-source",
        "jobs.fb-page-feed-poller",
        job(
            "jobs.fb-page-feed-poller",
            "fb-page-feed-poller",
            "refresh",
            "01M48V0V80ZZGG928KMD5XX36J",
            "2026-10-06T09:20:00Z",
            "own",
            source_id=fb_src,
        ),
    )
    res = job(
        "jobs.ig-account-resolver",
        "poster-resolver",
        "resolve",
        "01M48B9AKGZPWZF64KVNV761WT",
        "2026-10-06T10:13:50Z",
        "resolve",
        candidate_key=IG_CAND,
        platform="instagram",
        platform_id="17841400000000000",
        handle="baghdad_eats",
        url=None,
        client_ids=[CLIENT],
        seed_list=False,
        origin="discovery",
    )
    v("resolve", "jobs.ig-account-resolver", res)
    manual = job(
        "jobs.poster-resolver",
        "registry-writer",
        "manual_candidate",
        "01M48W0V80ZZGG928KMD5XX36J",
        "2026-10-06T11:00:00Z",
        "manual",
        candidate_key=candidate_key_from_handle("x", "example_telecom_iq"),
        platform="x",
        platform_id=None,
        handle="example_telecom_iq",
        url=None,
        client_ids=[CLIENT],
        seed_list=True,
        origin="manual",
        request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DJ",
        requested_by=PERSON,
    )
    v("manual-candidate", "jobs.poster-resolver", manual)
    v(
        "first-check",
        "jobs.news-robots-checker",
        job(
            "jobs.news-robots-checker",
            "news-site-resolver",
            "first_check",
            "01M48X0V80ZZGG928KMD5XX36J",
            "2026-10-06T08:52:41Z",
            "first",
            host="www.example-daily.iq",
            source_id="5e3b8f02-6d1c-4a97-b2e8-0c9f4d7a1e63",
        ),
    )
    recheck = job(
        "jobs.news-robots-checker",
        "news-article-extractor",
        "recheck",
        "01J9N3Q8D5W2K7X1R4T9V0MZBC",
        "2026-10-06T06:30:10Z",
        "recheck",
        host="www.example-daily.iq",
        requested_by="news-article-extractor",
    )
    v("recheck", "jobs.news-robots-checker", recheck)
    ops = job(
        "jobs.fb-page-feed-poller",
        "admin-api",
        "ops_force",
        "01M48Y0V80ZZGG928KMD5XX36J",
        "2026-10-06T14:10:00Z",
        "ops",
        source_id=fb_src,
        request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DK",
        requested_by=PERSON,
    )
    v("ops-force", "jobs.fb-page-feed-poller", ops)
    v(
        "ops-force-resolver",
        "jobs.fb-page-resolver",
        job(
            "jobs.fb-page-resolver",
            "admin-api",
            "ops_force",
            "01M48Z0V80ZZGG928KMD5XX36J",
            "2026-10-06T14:11:00Z",
            "opsres",
            candidate_key="facebook:100064583471102",
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DM",
            requested_by=PERSON,
        ),
    )
    v(
        "ops-force-no-source",
        "jobs.x-compliance-sync",
        job(
            "jobs.x-compliance-sync",
            "admin-api",
            "ops_force",
            "01M4900V80ZZGG928KMD5XX36J",
            "2026-10-06T14:12:00Z",
            "opsx",
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DN",
            requested_by=PERSON,
            client_id=CLIENT,
        ),
    )
    v(
        "ops-force-commoncrawl",
        "jobs.web-commoncrawl-scanner",
        job(
            "jobs.web-commoncrawl-scanner",
            "admin-api",
            "ops_force",
            "01M4910V80ZZGG928KMD5XX36J",
            "2026-10-09T05:00:00Z",
            "opscc",
            crawl_id="CC-MAIN-2026-38",
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DP",
            requested_by=PERSON,
        ),
    )
    v(
        "ops-force-targeted",
        "jobs.ig-mentions-fetcher",
        job(
            "jobs.ig-mentions-fetcher",
            "ig-webhook-receiver",
            "ops_force",
            "01M4920V80ZZGG928KMD5XX36J",
            "2026-10-06T12:06:00Z",
            "opsig",
            source_id="d4c3b2a1-9f8e-4d7c-8b6a-5f4e3d2c1b0a",
            target_ids=["17990012345678901"],
        ),
    )
    atom = (
        '<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom"><entry><id>yt:video:k7Qm2Xv9TbE</id>'
        "<yt:videoId>k7Qm2Xv9TbE</yt:videoId><yt:channelId>UCx3Kp9vQ2mLwR7tYb4nJ8sA</yt:channelId></entry></feed>"
    )
    push = job(
        "jobs.yt-pubsub-receiver",
        "yt-pubsub-receiver",
        "push",
        "01J9N7QV8D2K6M4P0R3S5T7W9X",
        "2026-10-06T09:12:44Z",
        "push",
        source_id="3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
        body=atom,
        received_at="2026-10-06T09:12:44Z",
        headers={
            "content-type": "application/atom+xml",
            "x-hub-signature": "sha1=0f3c9d2a7b1e4f6a8c0d2e4f6a8b0c2d4e6f8a0b",
        },
    )
    v("push-atom", "jobs.yt-pubsub-receiver", push)
    v(
        "push-json",
        "jobs.fb-client-webhook-receiver",
        job(
            "jobs.fb-client-webhook-receiver",
            "fb-client-webhook-receiver",
            "push",
            "01M4930V80ZZGG928KMD5XX36J",
            "2026-10-06T09:40:12Z",
            "pushfb",
            source_id="a3c0f1e2-5b6d-4c7e-9f80-112233445566",
            body={
                "object": "page",
                "entry": [
                    {
                        "id": "1234567890",
                        "time": 1791278412,
                        "changes": [{"field": "feed", "value": {"item": "comment", "verb": "add"}}],
                    }
                ],
            },
            received_at="2026-10-06T09:40:12Z",
            headers={
                "content-type": "application/json",
                "x-hub-signature-256": "sha256=5d1c9e3a7f2b4d6e8a0c1e3f5a7b9d1c3e5f7a9b1d3f5a7c9e1b3d5f7a9c1e3b",
            },
        ),
    )
    replay = job(
        "jobs.normalize-item",
        "admin-api",
        "replay",
        "01M4940V80ZZGG928KMD5XX36J",
        "2026-10-06T16:00:00Z",
        "replay",
        run_id="01J9P4K2M8E5T7C0Q1W3X6YZAB",
        **{"from": "2026-10-01T00:00:00Z", "to": "2026-10-06T00:00:00Z"},
        platforms=["facebook"],
        reason="normalizer_upgrade",
        request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DQ",
        requested_by=PERSON,
    )
    v("replay", "jobs.normalize-item", replay)
    v(
        "rerun",
        "jobs.analysis-topics",
        job(
            "jobs.analysis-topics",
            "admin-api",
            "rerun",
            "01M4950V80ZZGG928KMD5XX36J",
            "2026-10-06T17:00:00Z",
            "rerun",
            run_id="01M4950V80A8N3K5D2B7T4W9XC",
            task="topics.global",
            model_version="topics-iq-2026.11.tx8",
            **{"from": "2026-09-06T00:00:00Z", "to": "2026-10-06T00:00:00Z"},
            client_id=CLIENT,
            taxonomy_id="global",
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DR",
            requested_by=PERSON,
        ),
    )
    v(
        "rematch",
        "jobs.keyword-matcher",
        job(
            "jobs.keyword-matcher",
            "admin-api",
            "rematch",
            "01M4G00000A8N3K5D2B7T4W9XC",
            "2026-10-06T12:58:00Z",
            "rematch",
            client_id=CLIENT,
            keyword_ids=["0cd402b6-9015-45f8-86b4-d90cc086d320"],
            window_days=30,
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DG",
            requested_by=PERSON,
        ),
    )
    del_id = deletion_id(
        "platform_sync",
        "item",
        "3a7d9c21-5e4b-4f8a-b6c0-2d1e9f7a3b54",
        "delete",
        "2026-10-06T02:47:31Z",
        {
            "platform": "x",
            "kind": "post",
            "item_ids": [iid("x", "post", "1842957310264891392")],
            "platform_ids": ["1842957310264891392"],
        },
    )
    rc = job(
        "jobs.aggregator",
        "deletion-propagator",
        "recompute",
        "01M4960V80ZZGG928KMD5XX36J",
        "2026-10-06T09:41:00Z",
        "recompute",
        run_id="01M4960V80A8N3K5D2B7T4W9XC",
        deletion_id=del_id,
        buckets=[
            {"source_id": "3a7d9c21-5e4b-4f8a-b6c0-2d1e9f7a3b54", "hours": ["2026-10-05T19:00:00Z"]}
        ],
        keyword_ids=["9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3"],
    )
    v("recompute-buckets", "jobs.aggregator", rc)
    v(
        "recompute-range",
        "jobs.aggregator",
        job(
            "jobs.aggregator",
            "admin-api",
            "recompute",
            "01M4970V80ZZGG928KMD5XX36J",
            "2026-10-06T18:00:00Z",
            "recompute-range",
            **{"from": "2026-10-01T00:00:00Z", "to": "2026-10-02T00:00:00Z"},
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DS",
            requested_by=PERSON,
        ),
    )
    v(
        "retention-sweep",
        "jobs.yt-text-purger",
        job(
            "jobs.yt-text-purger",
            "retention-purger",
            "retention_sweep",
            "01M47F0V80FZGG928KMD5XX36K",
            "2026-10-06T02:00:00Z",
            "sweep",
            run_id="01M47F0V80FZGG928KMD5XX36J",
            cutoff="2026-09-06T02:00:00Z",
            next_sweep_at="2026-10-07T02:00:00Z",
        ),
    )
    norm_item = iid("facebook", "post", "1234567890_9876543210")
    analyze = job(
        "jobs.analysis-sentiment.priority",
        "analysis-sentiment",
        "analyze",
        "01M4886GG018V1FH131HTSP75D",
        "2026-10-06T09:14:05Z",
        "analyze",
        source_id="a3c0f1e2-5b6d-4c7e-9f80-112233445566",
        item_id=norm_item,
        item_version=1,
        content_hash=content_hash(None, "النت منقطع بالبصرة من الصبح، شنو السالفة؟"),
    )
    v("analyze-priority", "jobs.analysis-sentiment.priority", analyze)
    v(
        "analyze",
        "jobs.analysis-media",
        {
            **analyze,
            **meta(
                s,
                "analysis-media",
                ulid_for("2026-10-06T09:14:06Z", "run", "media"),
                "2026-10-06T09:14:06Z",
                name="media",
            ),
            "job_id": "01M4886GG0GDQ0Y9RD0QSBJD30",
        },
    )
    x_item = iid("x", "post", "1843201122334455667")
    kw = "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3"
    v(
        "candidate-retry",
        "jobs.keyword-matcher",
        job(
            "jobs.keyword-matcher",
            "keyword-matcher",
            "candidate_retry",
            "01M4980V80ZZGG928KMD5XX36J",
            "2026-10-06T09:20:00Z",
            "retry",
            source_id="c41b7a90-3d2e-4f5a-8b6c-7d8e9f0a1b2c",
            hit_id=hit_id(x_item, CLIENT2, kw),
            item_id=x_item,
            raw_ref="raw/green/x/2026/10/06/x-recent-search/000042.jsonl.zst#310",
            keyword_ids=[kw],
            client_ids=[CLIENT2],
            hit_at="2026-10-06T08:51:40Z",
            matched_term="زين العراق",
            form_id="f2",
            keyword_set_version="cs:3f9a1c0d7e2b4a6c8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d",
        ),
    )
    v(
        "review-answer",
        "jobs.qualifier",
        job(
            "jobs.qualifier",
            "admin-api",
            "review_answer",
            "01M4990V80ZZGG928KMD5XX36J",
            "2026-10-07T09:12:30Z",
            "answer",
            candidate_key=IG_CAND,
            card_id="7d1c3e5a-9b2f-5d4e-8a6c-1e3f5a7b9d2c",
            decision_id=ulid_for("2026-10-06T12:40:30Z", "decision", "review"),
            action="approve_tier_3",
            request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DT",
            requested_by=REVIEWER,
        ),
    )
    export = job(
        "jobs.x-compliance-sync",
        "admin-api",
        "export",
        "01M4H00000A8N3K5D2B7T4W9XC",
        "2026-10-07T09:00:00Z",
        "export",
        client_id=None,
        **{"from": "2026-09-01T00:00:00Z", "to": "2026-10-01T00:00:00Z"},
        request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DH",
        requested_by=PERSON,
    )
    v("export", "jobs.x-compliance-sync", export)

    metadata_invalids(s, rot)
    for k, val in (("priority", 1), ("route", "green"), ("vendor", None)):
        bad(
            f"carries-{k}",
            "jobs.fb-page-feed-poller",
            {**rot, k: val},
            [k],
            "priority, route and vendor never travel in a job (ADR-0011, ADR-0018)",
        )
    bad(
        "reason-as-kind",
        "jobs.fb-backfill",
        {**bf, "kind": "first_run"},
        ["kind"],
        "reason is never the type (ADR-0011)",
    )
    bad(
        "analyze-with-item",
        "jobs.analysis-sentiment.priority",
        {**analyze, "item": {"text": "النت منقطع"}},
        ["item"],
        "a job carries no platform data (ADR-0003; Q6)",
    )
    bad(
        "analyze-with-provenance",
        "jobs.analysis-sentiment.priority",
        {
            **analyze,
            "provenance": prov("green", None, "fb-page-feed-poller", "2026-10-06T09:13:58Z"),
        },
        ["provenance"],
        "a job carries no provenance (ADR-0003; Q6)",
    )
    bad(
        "producer-not-allowed",
        "jobs.fb-page-feed-poller",
        {**rot, "producer": {**rot["producer"], "service": "fb-backfill"}},
        ["producer", "service"],
        "the producer table has no row for this queue, kind and service (ADR-0012)",
    )
    bad(
        "kind-not-on-queue",
        "jobs.fb-page-feed-poller",
        {**bf},
        ["kind"],
        "a kind with no row on a queue leaves it (ADR-0012)",
    )
    bad(
        "hashtag-without-edge",
        "jobs.ig-hashtag-search",
        without(igrot, "edge"),
        ["edge"],
        "an ig-hashtag-search job names its edge (F-27)",
    )
    bad(
        "x-gap-without-window",
        "jobs.x-recent-search",
        without(xgap, "window_start"),
        ["window_start"],
        "the X gap job names its window (ADR-0064)",
    )
    bad(
        "missing-partition-key",
        "jobs.fb-page-feed-poller",
        without(rot, "source_id"),
        ["source_id"],
        "a job carries its queue's key (ADR-0004)",
    )
    bad(
        "resolver-without-candidate-key",
        "jobs.ig-account-resolver",
        without(res, "candidate_key"),
        ["candidate_key"],
        "a resolve job carries its candidate key (ADR-0032)",
    )
    bad(
        "replies-without-thread-ids",
        "jobs.yt-replies-fetcher",
        without(rep_job, "post_ref", "thread_ids"),
        ["post_ref", "thread_ids"],
        "a replies job lists its threads (ADR-0060)",
    )
    bad(
        "x-replies-without-window",
        "jobs.x-full-archive-search",
        without(xr, "window_start"),
        ["window_start"],
        "an X replies job names its window (ADR-0064)",
    )
    bad(
        "push-due-at-not-received",
        "jobs.yt-pubsub-receiver",
        {**push, "due_at": "2026-10-06T09:13:00Z"},
        ["due_at"],
        "a push job is due when received (ADR-0011)",
    )
    bad(
        "resolve-without-identity",
        "jobs.ig-account-resolver",
        {**res, "platform_id": None, "handle": None, "url": None},
        ["platform_id"],
        "a resolve job names the account by id, handle or url (ADR-0032)",
    )
    bad(
        "first-sight-id-list",
        "jobs.yt-video-details-fetcher",
        {**fr, "post_ref": ["Xk3vQ9pL2aE", "b7Tz0qR4mWc"]},
        ["post_ref"],
        "one video per first_sight job (ADR-0065 a))",
    )
    bad(
        "first-sight-series-step",
        "jobs.yt-video-details-fetcher",
        {**fs, "series_step": None},
        ["series_step"],
        "series_step goes from first_sight (ADR-0065)",
    )
    bad(
        "comments-backfill-step",
        "jobs.fb-post-comments-fetcher",
        {**cm, "series_step": "backfill"},
        ["series_step"],
        "series_step = backfill goes (ADR-0065)",
    )
    bad(
        "metrics-comment-step",
        "jobs.fb-reactions-fetcher",
        {**mj, "series_step": "+6h"},
        ["series_step"],
        "a metrics step is +24h, +7d or refresh:<request_id> (ADR-0034)",
    )
    bad(
        "manual-without-request",
        "jobs.poster-resolver",
        without(manual, "request_id"),
        ["request_id"],
        "a manual candidate names its request (ADR-0066)",
    )
    bad(
        "run-id-initial",
        "jobs.fb-backfill",
        {**bf, "run_id": "initial"},
        ["run_id"],
        "run_id is a ULID (ADR-0020)",
    )
    bad(
        "recompute-range-without-from",
        "jobs.aggregator",
        without(
            job(
                "jobs.aggregator",
                "admin-api",
                "recompute",
                "01M4970V80ZZGG928KMD5XX36J",
                "2026-10-06T18:00:00Z",
                "recompute-range",
                **{"from": "2026-10-01T00:00:00Z", "to": "2026-10-02T00:00:00Z"},
                request_id="01J9R5S3V7W1X4Y8Z0A2B6C9DS",
                requested_by=PERSON,
            ),
            "from",
        ),
        ["from"],
        "the admin API's recompute names its range (ADR-0012 L34)",
    )
    bad(
        "purge-refresh-without-deadline",
        "jobs.yt-comments-fetcher",
        without(purge, "must_finish_by"),
        ["must_finish_by"],
        "a refresh before a purge carries its deadline (ADR-0065 e))",
    )
    bad(
        "export-not-admin",
        "jobs.x-compliance-sync",
        {**export, "producer": {**export["producer"], "service": "x-compliance-sync"}},
        ["producer", "service"],
        "the admin API sends export jobs (ADR-0067 L26; Q13)",
    )
    bad(
        "ops-force-without-request",
        "jobs.fb-page-feed-poller",
        without(ops, "request_id"),
        ["request_id"],
        "the admin API's ops_force names its request (ADR-0012 L34)",
    )
    bad(
        "ops-force-unknown-requester",
        "jobs.fb-page-feed-poller",
        {**ops, "requested_by": "no-such-service"},
        ["requested_by"],
        "a requester that names a service is one the registry lists (Q18; F-09)",
    )
    bad(
        "recheck-without-requester",
        "jobs.news-robots-checker",
        without(recheck, "requested_by"),
        ["requested_by"],
        "a recheck names the service that asked (ADR-0022)",
    )
    bad(
        "recheck-unknown-requester",
        "jobs.news-robots-checker",
        {**recheck, "requested_by": "news-archive-crawler"},
        ["requested_by"],
        "a recheck's requester is a service the registry lists (F-09)",
    )
    bad(
        "recheck-person-requester",
        "jobs.news-robots-checker",
        {**recheck, "requested_by": "person:01J9P2R4T6V8X0Z2B4D6F8H0KM"},
        ["requested_by"],
        "a recheck names the service whose host gate asked, never a person (ADR-0040)",
    )
    bad(
        "candidate-retry-with-text",
        "jobs.keyword-matcher",
        {
            **job(
                "jobs.keyword-matcher",
                "keyword-matcher",
                "candidate_retry",
                "01M4980V80ZZGG928KMD5XX36J",
                "2026-10-06T09:20:00Z",
                "retry-bad",
                hit_id=hit_id(x_item, CLIENT2, kw),
                item_id=x_item,
                raw_ref="raw/green/x/2026/10/06/x-recent-search/000042.jsonl.zst#310",
                keyword_ids=[kw],
                client_ids=[CLIENT2],
                hit_at="2026-10-06T08:51:40Z",
                matched_term="زين العراق",
                form_id="f2",
                keyword_set_version="cs:3f9a1c0d7e2b4a6c8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d",
            ),
            "text": "زين العراق ما يشتغل",
        },
        ["text"],
        "a job carries ids and the client's terms, no platform text (ADR-0003)",
    )
    bad(
        "keyword-history-ops-reason",
        "jobs.x-full-archive-search",
        {**kh, "reason": "ops"},
        ["reason"],
        "a keyword history runs on add or client (ADR-0064, ADR-0059)",
    )
    first = json.loads((__import__("common").ROOT / s / "valid" / "first-check.json").read_text())
    bad(
        "first-check-without-host",
        "jobs.news-robots-checker",
        without(first, "host"),
        ["host"],
        "a first check names its host (ADR-0022)",
    )
    bad(
        "replay-without-requester",
        "jobs.normalize-item",
        without(replay, "requested_by"),
        ["requested_by"],
        "a replay names who asked (ADR-0012 L34)",
    )
    bad(
        "replay-unknown-requester",
        "jobs.normalize-item",
        {**replay, "requested_by": "no-such-service"},
        ["requested_by"],
        "a requester that names a service is one the registry lists (Q18; F-09)",
    )
    rerun = json.loads((__import__("common").ROOT / s / "valid" / "rerun.json").read_text())
    bad(
        "rerun-colon-task",
        "jobs.analysis-topics",
        {**rerun, "task": "topics:global"},
        ["task"],
        "task names hold no colon (ADR-0023)",
    )
    rematch = json.loads((__import__("common").ROOT / s / "valid" / "rematch.json").read_text())
    bad(
        "rematch-without-window",
        "jobs.keyword-matcher",
        without(rematch, "window_days"),
        ["window_days"],
        "a rematch names its window (keyword-matcher §5.3 H)",
    )
    sweep = json.loads(
        (__import__("common").ROOT / s / "valid" / "retention-sweep.json").read_text()
    )
    bad(
        "retention-sweep-without-cutoff",
        "jobs.yt-text-purger",
        without(sweep, "cutoff"),
        ["cutoff"],
        "a sweep names its cutoff (yt-text-purger §5.1 L44)",
    )
    answer = json.loads(
        (__import__("common").ROOT / s / "valid" / "review-answer.json").read_text()
    )
    bad(
        "review-answer-unknown-action",
        "jobs.qualifier",
        {**answer, "action": "approve"},
        ["action"],
        "the action is one of the card's buttons (qualifier §5.3 L67)",
    )
    tolerant(
        s,
        "unknown-field",
        {**rot, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"},
        queue="jobs.fb-page-feed-poller",
    )


# --------------------------------------------------------------------------------------------
# dlq.<service>/v1


def dlq() -> None:
    root = __import__("common").ROOT
    norm = json.loads((root / "items.normalized/v1/valid/prd-normalize-item.json").read_text())
    dels = json.loads((root / "deletions/v1/valid/prd-retention-purger.json").read_text())
    author_del, source_del, client_del = (
        json.loads((root / f"deletions/v1/valid/{name}.json").read_text())
        for name in ("author-request", "source-authorization-revoked", "client-offboarding")
    )
    rawmsg = json.loads((root / "raw.items/v1/valid/prd-fb-page-feed-poller.json").read_text())
    job = json.loads((root / "job/v1/valid/keyword-history.json").read_text())

    def dl(
        service: str,
        at: str,
        stage: str,
        original: dict[str, Any],
        error: dict[str, Any],
        consumer: dict[str, Any],
        name: str,
        **body: Any,
    ) -> dict[str, Any]:
        schema = f"dlq.{service}/v1"
        m = meta(schema, service, ulid_for(at, "run", service, name), at, name=name)
        return {
            **m,
            "stage": stage,
            "original": original,
            **body,
            "error": error,
            "consumer": consumer,
        }

    consume = dl(
        "store-writer",
        "2026-10-06T09:20:00Z",
        "consume",
        {
            "topic": "items.normalized",
            "partition": 3,
            "offset": 1842,
            "key": norm["source_id"],
            "schema": norm["schema"],
            "message_id": norm["message_id"],
        },
        {
            "class": "invalid",
            "message": "ClickHouse rejected the row: metrics_snapshot.reactions_by_type",
            "attempts": 5,
            "first_failed_at": "2026-10-06T09:14:10Z",
            "last_failed_at": "2026-10-06T09:19:58Z",
        },
        {"service": "store-writer", "group": "store-writer"},
        "consume",
        message=norm,
        provenance=copy.deepcopy(norm["provenance"]),
        retention_class=norm["retention_class"],
    )
    s = consume["schema"]
    valid(s, "consume-data-message", consume)
    raw_bytes = base64.b64encode(b'{"envelope": {"platform": "facebook", "kind": "post"').decode()
    rawdl = dl(
        "normalize-item",
        "2026-10-06T09:21:00Z",
        "consume",
        {
            "topic": "raw.items",
            "partition": 7,
            "offset": 99120,
            "key": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
            "schema": None,
            "message_id": None,
        },
        {
            "class": "invalid",
            "message": "the message is not JSON: unexpected end of input",
            "attempts": 1,
            "first_failed_at": "2026-10-06T09:20:59Z",
            "last_failed_at": "2026-10-06T09:20:59Z",
        },
        {"service": "normalize-item", "group": "normalize-item"},
        "raw",
        raw=raw_bytes,
    )
    valid(s, "consume-unparsed", rawdl)
    produce = dl(
        "retention-purger",
        "2026-10-06T00:30:00Z",
        "produce",
        {
            "topic": "deletions",
            "partition": None,
            "offset": None,
            "key": dels["source_id"],
            "schema": dels["schema"],
            "message_id": dels["message_id"],
        },
        {
            "class": "attempts_exhausted",
            "message": "the broker refused the chunk five times: NOT_ENOUGH_REPLICAS",
            "attempts": 5,
            "first_failed_at": "2026-10-06T00:05:12Z",
            "last_failed_at": "2026-10-06T00:29:58Z",
        },
        {"service": "retention-purger", "group": None},
        "produce",
        message=dels,
        provenance=copy.deepcopy(dels["provenance"]),
        retention_class=dels["retention_class"],
    )
    valid(s, "produce-chunk", produce)
    valid(
        s,
        "consume-raw-item",
        dl(
            "normalize-item",
            "2026-10-06T09:22:00Z",
            "consume",
            {
                "topic": "raw.items",
                "partition": 2,
                "offset": 551,
                "key": rawmsg["envelope"]["source_id"],
                "schema": "raw.items/v1",
                "message_id": rawmsg["envelope"]["message_id"],
            },
            {
                "class": "invalid",
                "message": "no mapper for facebook post from fb-page-feed-poller api_version v99.0",
                "attempts": 5,
                "first_failed_at": "2026-10-06T09:16:00Z",
                "last_failed_at": "2026-10-06T09:21:58Z",
            },
            {"service": "normalize-item", "group": "normalize-item"},
            "rawitem",
            message=rawmsg,
            provenance=copy.deepcopy(rawmsg["envelope"]["provenance"]),
            retention_class=rawmsg["envelope"]["retention_class"],
        ),
    )
    valid(
        s.replace("store-writer", "x-full-archive-search"),
        "consume-job",
        dl(
            "x-full-archive-search",
            "2026-10-06T12:01:00Z",
            "consume",
            {
                "topic": "jobs.x-full-archive-search",
                "partition": 0,
                "offset": 77,
                "key": job["source_id"],
                "schema": "job/v1",
                "message_id": job["message_id"],
            },
            {
                "class": "query_rejected",
                "message": "X rejected the query: too many operators",
                "attempts": 1,
                "first_failed_at": "2026-10-06T12:00:59Z",
                "last_failed_at": "2026-10-06T12:00:59Z",
            },
            {"service": "x-full-archive-search", "group": "x-full-archive-search"},
            "job",
            message=job,
        ),
    )
    unknown = copy.deepcopy(norm)
    unknown["schema"] = "items.normalized/v2"
    valid(
        s,
        "consume-unknown-version",
        dl(
            "store-writer",
            "2026-10-06T09:23:00Z",
            "consume",
            {
                "topic": "items.normalized",
                "partition": 1,
                "offset": 12,
                "key": norm["source_id"],
                "schema": "items.normalized/v2",
                "message_id": norm["message_id"],
            },
            {
                "class": "schema_unknown",
                "message": "items.normalized/v2 is not a version this consumer knows; parked",
                "attempts": 1,
                "first_failed_at": "2026-10-06T09:22:59Z",
                "last_failed_at": "2026-10-06T09:22:59Z",
            },
            {"service": "store-writer", "group": "store-writer"},
            "unknown",
            message=unknown,
            provenance=copy.deepcopy(norm["provenance"]),
            retention_class=norm["retention_class"],
        ),
    )

    # An author-, source- or client-scope deletion: its signal provenance is copied under its own
    # type (a null route where the signal is no fetch) and no class, which it has none of (F-42, D-1).
    def deletion_dl(
        stage: str, service: str, deletion: dict[str, Any], key: str, at: str, name: str
    ) -> dict[str, Any]:
        consumed = stage == "consume"
        return dl(
            service,
            at,
            stage,
            {
                "topic": "deletions",
                "partition": 4 if consumed else None,
                "offset": 30211 if consumed else None,
                "key": deletion[key],
                "schema": deletion["schema"],
                "message_id": deletion["message_id"],
            },
            {
                "class": "attempts_exhausted",
                "message": "ClickHouse refused the mutation five times: TOO_MANY_PARTS"
                if consumed
                else "the broker refused the deletion five times: NOT_ENOUGH_REPLICAS",
                "attempts": 5,
                "first_failed_at": "2026-10-07T09:01:00Z",
                "last_failed_at": "2026-10-07T09:29:58Z",
            },
            {"service": service, "group": service if consumed else None},
            name,
            message=deletion,
            provenance=copy.deepcopy(deletion["provenance"]),
        )

    author_dl = deletion_dl(
        "consume", "deletion-propagator", author_del, "author_ref", "2026-10-07T09:30:00Z", "author"
    )
    valid(s, "consume-author-deletion", author_dl)
    valid(
        s,
        "consume-source-deletion",
        deletion_dl(
            "consume",
            "deletion-propagator",
            source_del,
            "source_id",
            "2026-10-07T09:31:00Z",
            "source",
        ),
    )
    valid(
        s,
        "produce-client-offboarding",
        deletion_dl(
            "produce", "retention-purger", client_del, "client_id", "2026-10-07T09:32:00Z", "client"
        ),
    )

    # An original whose provenance fails its own type: the record copies neither (D-12, plan L397).
    def item_dl(message: dict[str, Any], name: str, **top: Any) -> dict[str, Any]:
        return dl(
            "store-writer",
            "2026-10-06T09:24:00Z",
            "consume",
            {
                "topic": "items.normalized",
                "partition": 3,
                "offset": 1907,
                "key": message["source_id"],
                "schema": message["schema"],
                "message_id": message["message_id"],
            },
            {
                "class": "invalid",
                "message": "the message fails items.normalized/v1",
                "attempts": 1,
                "first_failed_at": "2026-10-06T09:23:59Z",
                "last_failed_at": "2026-10-06T09:23:59Z",
            },
            {"service": "store-writer", "group": "store-writer"},
            name,
            message=message,
            **top,
        )

    valid(
        s,
        "consume-malformed-provenance",
        item_dl(with_(norm, ("provenance", "route"), "RED"), "malformed"),
    )
    metadata_invalids("dlq.store-writer/v1", consume)
    invalid(
        s,
        "message-and-raw",
        {**consume, "raw": raw_bytes},
        ["raw"],
        "message or raw, exactly one (Q5)",
    )
    invalid(
        s,
        "neither-message-nor-raw",
        without(without(without(consume, "message"), "provenance"), "retention_class"),
        ["message"],
        "message or raw, exactly one (Q5)",
    )
    invalid(
        s,
        "produce-with-offset",
        with_(produce, ("original", "partition"), 3),
        ["original", "partition"],
        "a produce-side entry has no consumed offset (F-21)",
    )
    invalid(
        s,
        "consume-without-group",
        with_(consume, ("consumer", "group"), None),
        ["consumer", "group"],
        "a consumed entry names its consumer group (Q5)",
    )
    invalid(
        s,
        "raw-with-provenance",
        {**rawdl, "provenance": norm["provenance"], "retention_class": norm["retention_class"]},
        ["provenance"],
        "provenance is copied only from a parsed data message (F-42)",
    )
    invalid(
        s,
        "provenance-not-the-messages",
        with_(consume, ("provenance", "fetched_at"), "2026-10-06T09:14:00Z"),
        ["provenance"],
        "the copied provenance equals the message's (F-42)",
    )
    invalid(
        s,
        "provenance-not-copied",
        without(without(consume, "provenance"), "retention_class"),
        ["provenance"],
        "a data message's provenance is copied to the top (F-42)",
    )
    invalid(
        s,
        "class-without-provenance",
        without(consume, "provenance"),
        ["provenance"],
        "provenance and retention_class travel together (ADR-0003)",
    )
    invalid(
        s,
        "schema-not-a-dlq",
        {**consume, "schema": "dlq/v1"},
        ["schema"],
        "the schema is dlq.<service>/v1 (Q5, F-52)",
    )
    invalid(
        s,
        "unknown-error-class",
        with_(consume, ("error", "class"), "timeout"),
        ["error", "class"],
        "error.class is closed (Q5)",
    )
    invalid(
        s,
        "zero-attempts",
        with_(consume, ("error", "attempts"), 0),
        ["error", "attempts"],
        "a dead letter failed at least once",
    )
    invalid(
        s,
        "not-own-dlq",
        {**consume, "producer": {**consume["producer"], "service": "normalize-item"}},
        ["producer", "service"],
        "each service writes its own dlq.<service> (CONVENTIONS v1.1 L41)",
    )
    invalid(s, "bad-base64", {**rawdl, "raw": "not base64!"}, ["raw"], "raw is base64")
    # A message cut inside an emoji by a UTF-16 slice ends in a lone surrogate (finding 5).
    invalid(
        s,
        "error-message-lone-surrogate",
        with_(consume, ("error", "message"), consume["error"]["message"] + "\ud83d"),
        ["error", "message"],
        "every string and key is well-formed Unicode (UTF-8 encodable, ADR-0006)",
    )
    invalid(
        s,
        "invented-class",
        {**author_dl, "retention_class": "meta_on_request"},
        ["retention_class"],
        "an author-, source- or client-scope deletion has no class to copy (F-42, D-1)",
    )
    null_class = with_(norm, ("retention_class",), None)
    invalid(
        s,
        "null-class-copied",
        item_dl(
            null_class,
            "null-class",
            provenance=copy.deepcopy(null_class["provenance"]),
            retention_class="meta_on_request",
        ),
        ["retention_class"],
        "a class is copied only from an original that has a valid one (F-42, D-1)",
    )
    null_route = with_(norm, ("provenance", "route"), None)
    invalid(
        s,
        "null-route-not-a-deletion",
        item_dl(
            null_route,
            "null-route",
            provenance=copy.deepcopy(null_route["provenance"]),
            retention_class=null_route["retention_class"],
        ),
        ["provenance"],
        "a null route is copied only from an author-, source- or client-scope deletion (F-42, D-1)",
    )
    tolerant(s, "unknown-field", {**consume, "replayed": False})


def not_messages() -> None:
    """The 6.2 examples that are no message on a topic or queue, with the reason (A6)."""
    sh = "docs/prds/shared/"
    for service, path, line, note in (
        (
            "aggregator",
            sh + "aggregator.md",
            80,
            "an aggregates_hourly row in ClickHouse, not a message",
        ),
        (
            "deletion-propagator",
            sh + "deletion-propagator.md",
            93,
            "the audit record kept in deletion_requests.verification, not a message",
        ),
        (
            "lang-dialect-id",
            sh + "lang-dialect-id.md",
            108,
            "the service's answer to its caller; it writes no topic and no table",
        ),
        (
            "quota-governor",
            sh + "quota-governor.md",
            100,
            "a request and its answer over quota-governor's interface, not a message",
        ),
        (
            "raw-archiver",
            sh + "raw-archiver.md",
            99,
            "the superseded raw.replay message: there is no raw.replay topic, a replay reads through raw-archiver's read endpoint (ADR-0039, ADR-0070)",
        ),
        (
            "store-writer",
            sh + "store-writer.md",
            100,
            "a ClickHouse items row, not a message; its fields follow items.normalized/v1",
        ),
        (
            "x-compliance-sync",
            "docs/prds/x/x-compliance-sync.md",
            118,
            "the x_compliance_audit record, not a message",
        ),
        (
            "x-filtered-stream",
            "docs/prds/x/x-filtered-stream.md",
            141,
            "the stream rules registered at X, not a message on a topic or queue",
        ),
        (
            "yt-text-purger",
            "docs/prds/youtube/yt-text-purger.md",
            164,
            "a retention_audit row, not a message",
        ),
    ):
        prd(service, path, line, None, None, [], note=note)


def run() -> None:
    not_messages()
    decisions()
    events()
    completed()
    jobs()
    dlq()
    _ = (item_id, CLIENT2)
