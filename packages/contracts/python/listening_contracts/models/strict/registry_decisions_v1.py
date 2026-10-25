# Generated from schemas/registry.decisions/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["green", "amber"]
    vendor: Vendor | None
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    fetched_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class ProposedSourceId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class RuleHit(RootModel[int]):
    root: Annotated[int, Field(ge=1, le=10)]


class PlatformId(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Handle(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Url(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Followers(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class SignalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal: Literal[
        "iraqi_place", "platform_country_iq", "phone_964", "iq_domain", "outlet_link", "seed_list"
    ]
    matched: Annotated[str, Field(min_length=1)]
    where: Annotated[str, Field(min_length=1)]


class LangShare(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ar: Annotated[float, Field(ge=0.0, le=1.0)]
    ckb: Annotated[float, Field(ge=0.0, le=1.0)]
    en: Annotated[float, Field(ge=0.0, le=1.0)]
    mixed: Annotated[float, Field(ge=0.0, le=1.0)]
    other: Annotated[float, Field(ge=0.0, le=1.0)]
    und: Annotated[float, Field(ge=0.0, le=1.0)]
    ar_iraqi: Annotated[float, Field(ge=0.0, le=1.0)]
    sample: Annotated[int, Field(ge=0, le=9007199254740991)]


class PlatformMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uploads_playlist_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    ig_user_id: Annotated[str | MISSING, Field(pattern="^[0-9]+$")] = MISSING
    linked_channel_source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    linked_chat_id: Annotated[str | MISSING, Field(pattern="^-?[0-9]+$")] = MISSING


class ClientPriority(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    priority: bool


class KeywordPlatformMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instagram: PlatformMeta | MISSING = MISSING


class RemoveClientBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class TierChangeBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tier: Literal[1, 2, 3]
    rule_hit: Annotated[int, Field(ge=1, le=10)]


class DormantBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_hit: Annotated[int, Field(ge=1, le=10)]


class RetireBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_hit: RuleHit | None


class PushCoverageBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    push_covered: bool


class SourceHealthBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    health: Literal["ok", "degraded", "blocked"]


class Fallback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["green", "amber"]
    vendor: Vendor | None


class CanaryEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_minutes: Annotated[int, Field(ge=0, le=9007199254740991)]
    samples: Annotated[int, Field(ge=0, le=9007199254740991)]
    empty_200: Annotated[int, Field(ge=0, le=9007199254740991)]
    rate: Annotated[float, Field(ge=0.0, le=1.0)]
    targets: Annotated[int, Field(ge=0, le=9007199254740991)]


class QualifierBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_hit: Annotated[int, Field(ge=1, le=10)]
    client_ids: list[ClientId]


class RejectBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_hit: Annotated[int, Field(ge=1, le=10)]
    client_ids: list[ClientId]
    expires_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class RemoveClient(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["remove_client"]
    reason: Literal["client_removed"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    remove_client: RemoveClientBlock


class TierChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["tier_change"]
    reason: None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    tier_change: TierChangeBlock


class Dormant(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["dormant"]
    reason: None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    dormant: DormantBlock


class Promote(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["promote"]
    reason: None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Retire(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["retire"]
    reason: Literal["owner_request", "authorization_revoked", "not_found"] | None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    retire: RetireBlock


class PushCoverage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["push_coverage"]
    reason: Literal["lease_lapsed", "subscription_failed"] | None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    push_coverage: PushCoverageBlock


class SourceHealthChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["health_change"]
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
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    health_change: SourceHealthBlock


class Queued(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["queued"]
    reason: Literal["amber_excluded_government"] | None
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    queued: QualifierBlock


class MentionOnlyCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["mention_only"]
    reason: None
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    mention_only: QualifierBlock


class MentionOnlyAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["mention_only"]
    reason: None
    author_ref: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    mention_only: QualifierBlock


class Reject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["reject"]
    reason: Literal["review_timeout"] | None
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    reject: RejectBlock


class Review(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["review"]
    reason: (
        Literal[
            "age_gated",
            "not_indexed",
            "unclassified",
            "ambiguous",
            "schema_unknown",
            "grant_missing",
        ]
        | None
    )
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    review: QualifierBlock


class CountrySignals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    iraqi_place: bool
    platform_country_iq: bool
    phone_964: bool
    iq_domain: bool
    outlet_link: bool
    seed_list: bool
    signal_evidence: list[SignalEvidence]


class KeywordBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform_meta: KeywordPlatformMeta | MISSING = MISSING


class SourceColumnChanges(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: (
        Literal[
            "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
        ]
        | MISSING
    ) = MISSING
    source_type: (
        Literal[
            "page",
            "group",
            "account",
            "creator",
            "channel",
            "company_page",
            "site",
            "hashtag",
            "keyword_rule",
        ]
        | MISSING
    ) = MISSING
    platform_id: PlatformId | MISSING | None = MISSING
    handle: Handle | MISSING | None = MISSING
    url: Url | MISSING | None = MISSING
    display_name: str | MISSING | None = MISSING
    route: Literal["green", "amber"] | MISSING = MISSING
    vendor: Vendor | MISSING | None = MISSING
    tier: Literal[1, 2, 3] | MISSING = MISSING
    lifecycle: Literal["active", "dormant", "retired"] | MISSING = MISSING
    push_covered: bool | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    owned_by_client: bool | MISSING = MISSING
    added_by: Literal["qualifier", "client", "ops"] | MISSING = MISSING
    followers: Followers | MISSING | None = MISSING
    country_signals: CountrySignals | MISSING | None = MISSING
    lang_share: LangShare | MISSING | None = MISSING
    platform_meta: PlatformMeta | MISSING = MISSING
    notes: str | MISSING | None = MISSING


class RouteHealthBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    health: Literal["ok", "degraded", "fallback", "blocked"]
    fallback: Fallback | None
    scope: Literal["non_government"] | None
    evidence: CanaryEvidence | None


class AddKeyword(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["add"]
    reason: None
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    add: KeywordBlock


class UpdateKeyword(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["update"]
    reason: None
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    update: KeywordBlock


class RouteHealthChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["health_change"]
    reason: Literal["empty_200_rate", "low_yield", "server", "auth", "flag_off"] | None
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    route: Literal["green", "amber"]
    vendor: Vendor | None
    health_change: RouteHealthBlock


class SourceColumns(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_type: Literal[
        "page",
        "group",
        "account",
        "creator",
        "channel",
        "company_page",
        "site",
        "hashtag",
        "keyword_rule",
    ]
    platform_id: PlatformId | None
    handle: Handle | None
    url: Url | None
    display_name: str | None
    route: Literal["green", "amber"]
    vendor: Vendor | None
    tier: Literal[1, 2, 3]
    lifecycle: Literal["active", "dormant", "retired"]
    push_covered: bool
    retention_class: Literal[
        "meta_on_request",
        "vendor_agreed",
        "x_24h_sync",
        "news_excerpt",
        "telegram_bot",
        "tiktok_display",
        "linkedin_48h",
        "linkedin_org",
        "youtube_30d_text",
    ]
    client_ids: list[ClientId]
    owned_by_client: bool
    added_by: Literal["qualifier", "client", "ops"]
    followers: Followers | None
    country_signals: CountrySignals | None
    lang_share: LangShare | None
    platform_meta: PlatformMeta


class UpdateSourceBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: SourceColumnChanges
    client_priority: list[ClientPriority] | MISSING = MISSING


class UpdateSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["update"]
    reason: Literal["budget_wait"] | None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    update: UpdateSourceBlock


class AddSourceBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: SourceColumns
    proposed_source_id: ProposedSourceId | None
    origin: Literal["discovery", "manual"] | None
    rule_hit: RuleHit | None
    client_priority: list[ClientPriority] | MISSING = MISSING


class AddCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["add"]
    reason: None
    candidate_key: Annotated[
        str,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ]
    add: AddSourceBlock


class AddSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["registry.decisions/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    requested_by: Annotated[str, Field(max_length=256, min_length=1)]
    provenance: Provenance | MISSING = MISSING
    retention_class: (
        Literal[
            "meta_on_request",
            "vendor_agreed",
            "x_24h_sync",
            "news_excerpt",
            "telegram_bot",
            "tiktok_display",
            "linkedin_48h",
            "linkedin_org",
            "youtube_30d_text",
        ]
        | MISSING
    ) = MISSING
    decision: Literal["add"]
    reason: None
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    add: AddSourceBlock


class RegistryDecisionsV1(
    RootModel[
        AddCandidate
        | AddSource
        | AddKeyword
        | UpdateSource
        | UpdateKeyword
        | RemoveClient
        | TierChange
        | Dormant
        | Promote
        | Retire
        | PushCoverage
        | SourceHealthChange
        | RouteHealthChange
        | Queued
        | MentionOnlyCandidate
        | MentionOnlyAuthor
        | Reject
        | Review
    ]
):
    root: Annotated[
        AddCandidate
        | AddSource
        | AddKeyword
        | UpdateSource
        | UpdateKeyword
        | RemoveClient
        | TierChange
        | Dormant
        | Promote
        | Retire
        | PushCoverage
        | SourceHealthChange
        | RouteHealthChange
        | Queued
        | MentionOnlyCandidate
        | MentionOnlyAuthor
        | Reject
        | Review,
        Field(title="RegistryDecisionsV1"),
    ]
