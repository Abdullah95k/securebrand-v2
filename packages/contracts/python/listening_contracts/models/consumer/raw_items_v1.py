# Generated from schemas/raw.items/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class RedactedField(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class AuthorRef(RootModel[str]):
    root: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]


class Producer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


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


class MatchedTerm(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Window(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    end: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class SearchQuery(BaseModel):
    model_config = ConfigDict(extra="ignore")
    variant: Annotated[str, Field(min_length=1)]
    rank: Annotated[int, Field(ge=0, le=9007199254740991)]


class UsageSignals(BaseModel):
    model_config = ConfigDict(extra="ignore")
    search: Literal["yes", "no", "unset"]
    ai_input: Literal["yes", "no", "unset"]
    ai_train: Literal["yes", "no", "unset"]


class MatchingRule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: Annotated[str, Field(pattern="^[0-9]+$")]
    tag: Annotated[str, Field(min_length=1)]


class CanonicalUrl(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class PublishedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class TextFullRef(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class TextExpiresAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class TextSha256(RootModel[str]):
    root: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]


class TitleSha256(RootModel[str]):
    root: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]


class ImageUrl(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class ArticlePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    final_url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    canonical_url: CanonicalUrl | None
    title: str | None
    excerpt: str | None
    published_at: PublishedAt | None
    text_full_ref: TextFullRef | None
    text_expires_at: TextExpiresAt | None
    text_sha256: TextSha256 | None
    title_sha256: TitleSha256 | None
    extractor: Annotated[str, Field(min_length=1)]
    extractor_version: Annotated[str, Field(min_length=1)]
    excerpt_chars: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    word_count: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    author: str | MISSING | None = MISSING
    language: str | MISSING | None = MISSING
    image_urls: list[ImageUrl] | MISSING = MISSING
    http_status: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING


class Context(BaseModel):
    model_config = ConfigDict(extra="ignore")
    window: Window | MISSING = MISSING
    query: SearchQuery | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    edge: Literal["recent_media", "top_media"] | MISSING = MISSING
    mention_type: Literal["tag", "mentioned_media", "mentioned_comment"] | MISSING = MISSING
    mention_of: Annotated[str | MISSING, Field(pattern="^[0-9]+$")] = MISSING
    received_at: Annotated[
        str | MISSING,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ] = MISSING
    url_key: Annotated[str | MISSING, Field(pattern="^news:url:[0-9a-f]{64}$")] = MISSING
    access_mode: Literal["direct", "headless", "proxy", "blocked"] | MISSING = MISSING
    usage_signals: UsageSignals | MISSING = MISSING
    update_id: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    discussion_source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    hashtag_id: Annotated[str | MISSING, Field(pattern="^[0-9]+$")] = MISSING
    hashtag_name: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    page: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    variant: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    country: Annotated[str | MISSING, Field(pattern="^[A-Z]{2}$")] = MISSING
    connection_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = (
        MISSING
    )
    matching_rules: list[MatchingRule] | MISSING = MISSING
    paid: bool | MISSING = MISSING
    query_arm: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    matched_terms: list[MatchedTerm] | MISSING = MISSING
    partial: Literal[True] | MISSING = MISSING
    live_state: Literal["none", "upcoming", "live"] | MISSING = MISSING
    call_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    completes_partial_from: Annotated[str | MISSING, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")] = (
        MISSING
    )
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    item_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ] = MISSING


class ArticleEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["article"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]


class ArticleMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    envelope: Annotated[ArticleEnvelope, Field(title="ArticleEnvelope")]
    payload: ArticlePayload


class PostEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["post"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]


class VideoEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["video"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]


class CommentEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: AuthorRef | None
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["comment"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]
    parent_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    root_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class ResultEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["result"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    idempotency_key: Annotated[
        str,
        Field(
            pattern="^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\\x00-\\x20]+|(news:article|web:result):[0-9a-f]{64})$"
        ),
    ]


class ProfileEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["profile"]


class ReactionEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: AuthorRef | None
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["reaction"]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class SearchResponseEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["search_response"]


class MetricsEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["raw.items/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
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
    client_ids: list[ClientId]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
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
    api_version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    author_ref: Annotated[str | MISSING, Field(pattern="^[0-9a-f]{64}$")] = MISSING
    redacted_fields: list[RedactedField] | MISSING = MISSING
    context: Context | MISSING = MISSING
    kind: Literal["metrics"]


class RecordMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    envelope: (
        PostEnvelope
        | VideoEnvelope
        | CommentEnvelope
        | ResultEnvelope
        | ProfileEnvelope
        | ReactionEnvelope
        | SearchResponseEnvelope
        | MetricsEnvelope
    )
    payload: dict[str, Any]


class RawItemsV1(RootModel[ArticleMessage | RecordMessage]):
    root: Annotated[ArticleMessage | RecordMessage, Field(title="RawItemsV1")]
