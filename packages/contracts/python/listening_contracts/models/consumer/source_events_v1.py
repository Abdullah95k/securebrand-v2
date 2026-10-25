# Generated from schemas/source.events/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class PlatformId(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Handle(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Url(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Followers(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class HealthSetBy(RootModel[str]):
    root: Annotated[str, Field(max_length=256, min_length=1)]


class HealthChangedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Producer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class SignalEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    signal: Literal[
        "iraqi_place", "platform_country_iq", "phone_964", "iq_domain", "outlet_link", "seed_list"
    ]
    matched: Annotated[str, Field(min_length=1)]
    where: Annotated[str, Field(min_length=1)]


class LangShare(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ar: Annotated[float, Field(ge=0.0, le=1.0)]
    ckb: Annotated[float, Field(ge=0.0, le=1.0)]
    en: Annotated[float, Field(ge=0.0, le=1.0)]
    mixed: Annotated[float, Field(ge=0.0, le=1.0)]
    other: Annotated[float, Field(ge=0.0, le=1.0)]
    und: Annotated[float, Field(ge=0.0, le=1.0)]
    ar_iraqi: Annotated[float, Field(ge=0.0, le=1.0)]
    sample: Annotated[int, Field(ge=0, le=9007199254740991)]


class PlatformMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")
    uploads_playlist_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    ig_user_id: Annotated[str | MISSING, Field(pattern="^[0-9]+$")] = MISSING
    linked_channel_source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    linked_chat_id: Annotated[str | MISSING, Field(pattern="^-?[0-9]+$")] = MISSING


class CountrySignals(BaseModel):
    model_config = ConfigDict(extra="ignore")
    iraqi_place: bool
    platform_country_iq: bool
    phone_964: bool
    iq_domain: bool
    outlet_link: bool
    seed_list: bool
    signal_evidence: list[SignalEvidence]


class PreviousColumns(BaseModel):
    model_config = ConfigDict(extra="ignore")
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
    added_at: Annotated[
        str | MISSING,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ] = MISSING
    health: Literal["ok", "degraded", "fallback", "blocked"] | MISSING = MISSING
    health_reason: (
        Literal[
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
        ]
        | MISSING
        | None
    ) = MISSING
    health_set_by: HealthSetBy | MISSING | None = MISSING
    health_changed_at: HealthChangedAt | MISSING | None = MISSING
    notes: str | MISSING | None = MISSING


class AddedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["added"]
    reason: None
    previous: None


class UpdatedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["updated"]
    reason: Literal["budget_wait", "client_removed"] | None
    previous: PreviousColumns


class TierChangeEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["tier_change"]
    reason: None
    previous: PreviousColumns


class LifecycleChangeEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["lifecycle_change"]
    reason: Literal["not_found", "owner_request", "authorization_revoked"] | None
    previous: PreviousColumns


class HealthChangeEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["health_change"]
    reason: (
        Literal[
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
            "empty_200_rate",
            "low_yield",
            "server",
            "auth",
        ]
        | None
    )
    previous: PreviousColumns


class FallbackOnEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["fallback_on"]
    reason: (
        Literal[
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
            "empty_200_rate",
            "low_yield",
            "server",
            "auth",
            "flag_on",
        ]
        | None
    )
    previous: PreviousColumns


class FallbackOffEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["fallback_off"]
    reason: (
        Literal[
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
            "empty_200_rate",
            "low_yield",
            "server",
            "auth",
            "flag_off",
        ]
        | None
    )
    previous: PreviousColumns


class PushCoverageChangeEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["source.events/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
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
    added_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    health: Literal["ok", "degraded", "fallback", "blocked"]
    health_reason: (
        Literal[
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
        ]
        | None
    )
    health_set_by: HealthSetBy | None
    health_changed_at: HealthChangedAt | None
    notes: str | None
    decision_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    actor: Annotated[str, Field(max_length=256, min_length=1)]
    at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    event: Literal["push_coverage_change"]
    reason: Literal["lease_lapsed", "subscription_failed"] | None
    previous: PreviousColumns


class SourceEventsV1(
    RootModel[
        AddedEvent
        | UpdatedEvent
        | TierChangeEvent
        | LifecycleChangeEvent
        | HealthChangeEvent
        | FallbackOnEvent
        | FallbackOffEvent
        | PushCoverageChangeEvent
    ]
):
    root: Annotated[
        AddedEvent
        | UpdatedEvent
        | TierChangeEvent
        | LifecycleChangeEvent
        | HealthChangeEvent
        | FallbackOnEvent
        | FallbackOffEvent
        | PushCoverageChangeEvent,
        Field(title="SourceEventsV1"),
    ]
