# Generated from schemas/items.analysis/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class ItemCreatedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Dialect(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]


class KbVersion(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class PreprocVersion(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class TaxonomyVersion(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class ExpiresAt(RootModel[str]):
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


class SentimentProbs(BaseModel):
    model_config = ConfigDict(extra="ignore")
    positive: Annotated[float, Field(ge=0.0, le=1.0)]
    negative: Annotated[float, Field(ge=0.0, le=1.0)]
    neutral: Annotated[float, Field(ge=0.0, le=1.0)]
    mixed: Annotated[float, Field(ge=0.0, le=1.0)]


class OffsetItem(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Offset(RootModel[list[OffsetItem]]):
    root: Annotated[list[OffsetItem], Field(max_length=2, min_length=2)]


class SentimentTarget(BaseModel):
    model_config = ConfigDict(extra="ignore")
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    label: Literal["positive", "negative", "neutral", "mixed"]
    score: float
    matched_term: Annotated[str | MISSING, Field(min_length=1)] = MISSING
    offsets: list[Offset] | MISSING = MISSING
    confidence: Annotated[float | MISSING, Field(ge=0.0, le=1.0)] = MISSING


class TopTopic(RootModel[str]):
    root: Annotated[str, Field(pattern="^[A-Za-z0-9_.-]+:[^\\x00-\\x20]+$")]


class TopicScore(BaseModel):
    model_config = ConfigDict(extra="ignore")
    topic_id: Annotated[str, Field(pattern="^[A-Za-z0-9_.-]+:[^\\x00-\\x20]+$")]
    score: Annotated[float, Field(ge=0.0, le=1.0)]
    source: Literal["supervised", "zero_shot"]


class Intent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: Literal["complaint", "question", "praise", "request", "announcement", "other"]
    score: Annotated[float, Field(ge=0.0, le=1.0)]


class TopicClusterResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cluster_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class EntityId(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Level(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class GovernorateId(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class LinkScore(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, le=1.0)]


class Entity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["brand", "company", "institution", "place", "product", "person_public"]
    entity_id: EntityId | None
    start: Annotated[int, Field(ge=0, le=9007199254740991)]
    end: Annotated[int, Field(ge=0, le=9007199254740991)]
    source: Literal["model", "gazetteer", "both"]
    name_en: str | MISSING | None = MISSING
    level: Level | MISSING | None = MISSING
    governorate_id: GovernorateId | MISSING | None = MISSING
    surface: str | MISSING = MISSING
    link_score: LinkScore | MISSING | None = MISSING


class UnlinkedEntity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["brand", "company", "institution", "place", "product", "person_public"]
    surface: str
    start: Annotated[int, Field(ge=0, le=9007199254740991)]
    end: Annotated[int, Field(ge=0, le=9007199254740991)]


class FetchedMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: Annotated[int, Field(ge=0, le=9007199254740991)]
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    sha256: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    reused: bool


class Script(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]


class Confidence(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, le=1.0)]


class Frames(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class OcrMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: Annotated[int, Field(ge=0, le=9007199254740991)]
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    sha256: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    reused: bool
    text: str
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | MISSING | None = MISSING
    script: Script | MISSING | None = MISSING
    confidence: Confidence | MISSING | None = MISSING
    frames: Frames | MISSING | None = MISSING
    truncated: bool | MISSING = MISSING


class MediaTag(BaseModel):
    model_config = ConfigDict(extra="ignore")
    tag: Annotated[str, Field(min_length=1)]
    score: Annotated[float, Field(ge=0.0, le=1.0)]


class AsrSegment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start: Annotated[float, Field(ge=0.0)]
    end: Annotated[float, Field(ge=0.0)]
    text: str
    confidence: Confidence | MISSING | None = MISSING


class FrameTime(RootModel[float]):
    root: Annotated[float, Field(ge=0.0)]


class Logo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    brand_id: Annotated[str, Field(min_length=1)]
    score: Annotated[float, Field(ge=0.0, le=1.0)]
    box: Annotated[list[float] | MISSING, Field(max_length=4, min_length=4)] = MISSING
    frame_time: FrameTime | MISSING | None = MISSING


class TopicClusterAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["topic_cluster"]
    result: TopicClusterResult | None


class SentimentResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: Literal["positive", "negative", "neutral", "mixed"]
    score: float
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    probs: SentimentProbs | MISSING = MISSING
    low_confidence: bool | MISSING = MISSING
    sarcasm_prob: Annotated[float | MISSING, Field(ge=0.0, le=1.0)] = MISSING
    sarcasm_flag: bool | MISSING = MISSING
    code_switched: bool | MISSING = MISSING
    truncated: bool | MISSING = MISSING
    model_route: Annotated[str | MISSING, Field(min_length=1)] = MISSING


class SentimentAspectResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    targets: list[SentimentTarget]


class TopicsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    topics: list[TopicScore]
    top_topic: TopTopic | None
    intent: Intent | MISSING | None = MISSING
    low_confidence: bool | MISSING = MISSING


class EntitiesResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    entities: list[Entity]
    unlinked: list[UnlinkedEntity] | MISSING = MISSING
    private_person_mentions: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING


class MediaFetchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    media: list[FetchedMedia]


class MediaOcrResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    media: list[OcrMedia]


class TaggedMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: Annotated[int, Field(ge=0, le=9007199254740991)]
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    sha256: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    reused: bool
    tags: list[MediaTag]


class TranscribedMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: Annotated[int, Field(ge=0, le=9007199254740991)]
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    sha256: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    reused: bool
    segments: list[AsrSegment]
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | MISSING | None = MISSING
    dialect: Dialect | MISSING | None = MISSING


class LogoMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: Annotated[int, Field(ge=0, le=9007199254740991)]
    type: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    sha256: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    reused: bool
    logos: list[Logo]


class SentimentAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["sentiment"]
    result: SentimentResult | None


class SentimentAspectAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["sentiment_aspect"]
    result: SentimentAspectResult | None


class TopicsAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Annotated[str, Field(pattern="^topics\\.[A-Za-z0-9_.-]+$")]
    result: TopicsResult | None


class EntitiesAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["entities"]
    result: EntitiesResult | None


class MediaFetchAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["media_fetch"]
    result: MediaFetchResult | None


class MediaOcrAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["media_ocr"]
    result: MediaOcrResult | None


class MediaTagsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    media: list[TaggedMedia]


class MediaAsrResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    media: list[TranscribedMedia]


class MediaLogoResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    media: list[LogoMedia]


class MediaTagsAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["media_tags"]
    result: MediaTagsResult | None


class MediaAsrAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["media_asr"]
    result: MediaAsrResult | None


class MediaLogoAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["items.analysis/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    analysis_key: Annotated[
        str,
        Field(
            pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\\.[A-Za-z0-9_.-]+):[^\\x00-\\x20:]+$"
        ),
    ]
    input_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    model_version: Annotated[str, Field(pattern="^[^\\x00-\\x20:]+$")]
    item_created_at: ItemCreatedAt | None
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    content_hash: Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    run_kind: Literal["live", "rerun"]
    lane: Literal["priority", "standard"]
    status: Literal["ok", "skipped"]
    reason: (
        Literal[
            "no_text",
            "unsupported_lang",
            "low_priority_source",
            "unsupported_media",
            "media_unavailable",
            "ai_input_refused",
            "use_not_permitted",
        ]
        | None
    )
    lang: Literal["ar", "ckb", "en", "mixed", "other", "und"] | None
    dialect: Dialect | None
    kb_version: KbVersion | MISSING | None = MISSING
    preproc_version: PreprocVersion | MISSING | None = MISSING
    taxonomy_version: TaxonomyVersion | MISSING | None = MISSING
    degraded: bool | MISSING = MISSING
    zero_shot_unavailable: bool | MISSING = MISSING
    expires_at: ExpiresAt | None
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
    task: Literal["media_logo"]
    result: MediaLogoResult | None


class ItemsAnalysisV1(
    RootModel[
        SentimentAnalysis
        | SentimentAspectAnalysis
        | TopicsAnalysis
        | TopicClusterAnalysis
        | EntitiesAnalysis
        | MediaFetchAnalysis
        | MediaOcrAnalysis
        | MediaTagsAnalysis
        | MediaAsrAnalysis
        | MediaLogoAnalysis
    ]
):
    root: Annotated[
        SentimentAnalysis
        | SentimentAspectAnalysis
        | TopicsAnalysis
        | TopicClusterAnalysis
        | EntitiesAnalysis
        | MediaFetchAnalysis
        | MediaOcrAnalysis
        | MediaTagsAnalysis
        | MediaAsrAnalysis
        | MediaLogoAnalysis,
        Field(title="ItemsAnalysisV1"),
    ]
