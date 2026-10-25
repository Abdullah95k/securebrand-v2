# Generated from schemas/n8n.alert/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class FallbackNotice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_kind: Literal["source", "route"]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    platform: (
        Literal[
            "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
        ]
        | MISSING
    ) = MISSING
    route: Literal["green", "amber"] | MISSING = MISSING
    reason: Literal[
        "bot_removed",
        "privacy_mode",
        "grant_missing",
        "account_unavailable",
        "credential_revoked",
        "not_found",
        "uploads_playlist_missing",
        "query_rejected",
        "feed_gone",
        "push_gap",
        "crawl_disallowed",
        "flag_off",
        "flag_on",
        "empty_200_rate",
        "low_yield",
        "server",
        "auth",
        "lease_lapsed",
        "subscription_failed",
        "owner_request",
        "authorization_revoked",
        "budget_wait",
        "client_removed",
        "review_timeout",
        "amber_excluded_government",
        "age_gated",
        "not_indexed",
        "unclassified",
        "ambiguous",
        "schema_unknown",
    ]
    vendor: Vendor | None


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class AlertSubject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    platform: (
        Literal[
            "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
        ]
        | MISSING
    ) = MISSING
    route: Literal["green", "amber"] | MISSING = MISSING
    vendor: Vendor | MISSING | None = MISSING
    keyword_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING


class Purpose(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]


class AlertKeyword(BaseModel):
    model_config = ConfigDict(extra="forbid")
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    label: Annotated[str, Field(min_length=1)]
    purpose: Purpose | None


class AlertSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    display_name: str


class AlertWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hour: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    elapsed_fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    evaluated_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class VolumeSpikeMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mentions_so_far: Annotated[int, Field(ge=0, le=9007199254740991)]
    baseline_median_same_hour: Annotated[float, Field(ge=0.0)]
    expected_so_far: Annotated[float, Field(ge=0.0)]
    ratio: Annotated[float, Field(ge=0.0)]
    baseline_days: Annotated[int, Field(ge=0, le=9007199254740991)]


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: Annotated[str, Field(min_length=1)]
    value: str


class FactsNotice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    facts: list[Fact]


class AlertScope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level: Annotated[str | MISSING, Field(pattern="^[a-z][a-z0-9_]*$")] = MISSING
    platform: (
        Literal[
            "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
        ]
        | MISSING
    ) = MISSING
    source: AlertSource | MISSING = MISSING
    item_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    topic_id: Annotated[str | MISSING, Field(pattern="^[A-Za-z0-9_.-]+:[^\\x00-\\x20]+$")] = MISSING
    entity_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    brand_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    story_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING


class VolumeSpikeAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["volume_spike"]
    metrics: VolumeSpikeMetrics


class NegativeShareAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["negative_share"]
    metrics: dict[str, float]


class NewHighReachPosterAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["new_high_reach_poster"]
    metrics: dict[str, float]


class KeywordFirstSeenAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["keyword_first_seen"]
    metrics: dict[str, float]


class PostDeletedHighReachAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["post_deleted_high_reach"]
    metrics: dict[str, float]


class EngagementSpikeAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["engagement_spike"]
    metrics: dict[str, float]


class TopicSpikeAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["topic_spike"]
    metrics: dict[str, float]


class EntityOrLogoAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["entity_or_logo"]
    metrics: dict[str, float]


class StoryAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    renotify: bool
    keyword: AlertKeyword | MISSING = MISSING
    scope: AlertScope | MISSING = MISSING
    window: AlertWindow
    fingerprint: Annotated[str, Field(min_length=1)]
    cooldown_until: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    rule_type: Literal["story"]
    metrics: dict[str, float]


class N8nAlertV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["n8n.alert/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    alert_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    idempotency_key: Annotated[str, Field(min_length=1)]
    channel: Literal["email", "telegram", "slack", "webhook"]
    fallthrough_channel: Literal["email", "telegram", "slack"] | None
    audience: Literal["client", "ops", "account_manager"]
    client_id: ClientId | None
    alert: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    severity: Literal["info", "warning", "high"]
    subject: AlertSubject
    summary: Annotated[str, Field(min_length=1)]
    details: (
        VolumeSpikeAlert
        | NegativeShareAlert
        | NewHighReachPosterAlert
        | KeywordFirstSeenAlert
        | PostDeletedHighReachAlert
        | EngagementSpikeAlert
        | TopicSpikeAlert
        | EntityOrLogoAlert
        | StoryAlert
        | FallbackNotice
        | FactsNotice
    )
