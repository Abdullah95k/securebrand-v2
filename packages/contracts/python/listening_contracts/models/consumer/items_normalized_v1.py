# Generated from schemas/items.normalized/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class Url(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class CreatedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class LangConf(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, le=1.0)]


class Dialect(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]


class DialectConf(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, le=1.0)]


class Script(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]


class LangModelVersion(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Hashtag(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class AtMention(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Link(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class ExpiresAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Producer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class AuthorRef(RootModel[str]):
    root: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]


class AuthorSourceId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class ItemAuthor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    author_ref: AuthorRef | None
    author_type: Literal["source", "individual"]
    author_source_id: AuthorSourceId | None
    display_name: str | MISSING = MISSING
    author_followers: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING


class Media(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class Views(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Likes(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Comments(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Shares(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Saves(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Count(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991, title="Count")]


class UsageSignals(BaseModel):
    model_config = ConfigDict(extra="ignore")
    search: Literal["yes", "no", "unset"]
    ai_input: Literal["yes", "no", "unset"]
    ai_train: Literal["yes", "no", "unset"]


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class Provenance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    route: Literal["green", "amber"]
    vendor: Vendor | None
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    fetched_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Metrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    views: Views | None
    likes: Likes | None
    comments: Comments | None
    shares: Shares | None
    reactions_by_type: dict[str, Count] | None
    saves: Saves | MISSING | None = MISSING


class NormalizedPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.normalized/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    parent_seen: bool
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Url | None
    created_at: CreatedAt | None
    title: str | None
    text: str | None
    text_norm: str | None
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    lang_conf: LangConf | None
    dialect: Dialect | None
    dialect_conf: DialectConf | None
    script: Script | None
    lang_model_version: LangModelVersion | None
    lang_pending: bool
    author: ItemAuthor
    media: list[Media]
    hashtags: list[Hashtag]
    at_mentions: list[AtMention]
    links: list[Link]
    metrics_snapshot: Metrics
    expires_at: ExpiresAt | None
    normalizer_version: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    job_kind: Literal[
        "rotation",
        "reconciliation",
        "backfill",
        "keyword_history",
        "comments",
        "replies",
        "metrics",
        "first_sight",
        "refresh",
        "resolve",
        "manual_candidate",
        "first_check",
        "recheck",
        "ops_force",
        "push",
        "replay",
        "rerun",
        "rematch",
        "recompute",
        "retention_sweep",
        "analyze",
        "candidate_retry",
        "review_answer",
        "export",
        "stream",
    ]
    sensitive_event: bool
    text_full_ref: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    poster_platform_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    quoted_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    provenance: Provenance
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
    kind: Literal["post"]
    parent_id: None
    root_id: None


class NormalizedVideo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.normalized/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    parent_seen: bool
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Url | None
    created_at: CreatedAt | None
    title: str | None
    text: str | None
    text_norm: str | None
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    lang_conf: LangConf | None
    dialect: Dialect | None
    dialect_conf: DialectConf | None
    script: Script | None
    lang_model_version: LangModelVersion | None
    lang_pending: bool
    author: ItemAuthor
    media: list[Media]
    hashtags: list[Hashtag]
    at_mentions: list[AtMention]
    links: list[Link]
    metrics_snapshot: Metrics
    expires_at: ExpiresAt | None
    normalizer_version: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    job_kind: Literal[
        "rotation",
        "reconciliation",
        "backfill",
        "keyword_history",
        "comments",
        "replies",
        "metrics",
        "first_sight",
        "refresh",
        "resolve",
        "manual_candidate",
        "first_check",
        "recheck",
        "ops_force",
        "push",
        "replay",
        "rerun",
        "rematch",
        "recompute",
        "retention_sweep",
        "analyze",
        "candidate_retry",
        "review_answer",
        "export",
        "stream",
    ]
    sensitive_event: bool
    text_full_ref: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    poster_platform_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    quoted_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    provenance: Provenance
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
    kind: Literal["video"]
    parent_id: None
    root_id: None


class NormalizedComment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.normalized/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    parent_seen: bool
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Url | None
    created_at: CreatedAt | None
    title: str | None
    text: str | None
    text_norm: str | None
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    lang_conf: LangConf | None
    dialect: Dialect | None
    dialect_conf: DialectConf | None
    script: Script | None
    lang_model_version: LangModelVersion | None
    lang_pending: bool
    author: ItemAuthor
    media: list[Media]
    hashtags: list[Hashtag]
    at_mentions: list[AtMention]
    links: list[Link]
    metrics_snapshot: Metrics
    expires_at: ExpiresAt | None
    normalizer_version: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    job_kind: Literal[
        "rotation",
        "reconciliation",
        "backfill",
        "keyword_history",
        "comments",
        "replies",
        "metrics",
        "first_sight",
        "refresh",
        "resolve",
        "manual_candidate",
        "first_check",
        "recheck",
        "ops_force",
        "push",
        "replay",
        "rerun",
        "rematch",
        "recompute",
        "retention_sweep",
        "analyze",
        "candidate_retry",
        "review_answer",
        "export",
        "stream",
    ]
    sensitive_event: bool
    text_full_ref: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    poster_platform_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    quoted_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    provenance: Provenance
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
    kind: Literal["comment"]
    parent_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    root_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class NormalizedArticle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.normalized/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    parent_seen: bool
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Url | None
    created_at: CreatedAt | None
    title: str | None
    text: str | None
    text_norm: str | None
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    lang_conf: LangConf | None
    dialect: Dialect | None
    dialect_conf: DialectConf | None
    script: Script | None
    lang_model_version: LangModelVersion | None
    lang_pending: bool
    author: ItemAuthor
    media: list[Media]
    hashtags: list[Hashtag]
    at_mentions: list[AtMention]
    links: list[Link]
    metrics_snapshot: Metrics
    expires_at: ExpiresAt | None
    normalizer_version: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    job_kind: Literal[
        "rotation",
        "reconciliation",
        "backfill",
        "keyword_history",
        "comments",
        "replies",
        "metrics",
        "first_sight",
        "refresh",
        "resolve",
        "manual_candidate",
        "first_check",
        "recheck",
        "ops_force",
        "push",
        "replay",
        "rerun",
        "rematch",
        "recompute",
        "retention_sweep",
        "analyze",
        "candidate_retry",
        "review_answer",
        "export",
        "stream",
    ]
    sensitive_event: bool
    text_full_ref: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    poster_platform_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    quoted_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    provenance: Provenance
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
    kind: Literal["article"]
    parent_id: None
    root_id: None


class NormalizedResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.normalized/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    parent_seen: bool
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Url | None
    created_at: CreatedAt | None
    title: str | None
    text: str | None
    text_norm: str | None
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    lang_conf: LangConf | None
    dialect: Dialect | None
    dialect_conf: DialectConf | None
    script: Script | None
    lang_model_version: LangModelVersion | None
    lang_pending: bool
    author: ItemAuthor
    media: list[Media]
    hashtags: list[Hashtag]
    at_mentions: list[AtMention]
    links: list[Link]
    metrics_snapshot: Metrics
    expires_at: ExpiresAt | None
    normalizer_version: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    job_kind: Literal[
        "rotation",
        "reconciliation",
        "backfill",
        "keyword_history",
        "comments",
        "replies",
        "metrics",
        "first_sight",
        "refresh",
        "resolve",
        "manual_candidate",
        "first_check",
        "recheck",
        "ops_force",
        "push",
        "replay",
        "rerun",
        "rematch",
        "recompute",
        "retention_sweep",
        "analyze",
        "candidate_retry",
        "review_answer",
        "export",
        "stream",
    ]
    sensitive_event: bool
    text_full_ref: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    poster_platform_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    quoted_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_ids: list[ClientId] | MISSING = MISSING
    provenance: Provenance
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
    kind: Literal["result"]
    parent_id: None
    root_id: None


class ItemsNormalizedV1(
    RootModel[
        NormalizedPost | NormalizedVideo | NormalizedComment | NormalizedArticle | NormalizedResult
    ]
):
    root: Annotated[
        NormalizedPost | NormalizedVideo | NormalizedComment | NormalizedArticle | NormalizedResult,
        Field(title="ItemsNormalizedV1"),
    ]
