# Generated from schemas/item.hits/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class LangModelVersion(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Url(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class ExpiresAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class OffsetItem(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Offset(RootModel[list[OffsetItem]]):
    root: Annotated[list[OffsetItem], Field(max_length=2, min_length=2)]


class Offset1Item(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Offset1(RootModel[list[Offset1Item]]):
    root: Annotated[list[Offset1Item], Field(max_length=2, min_length=2)]


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


class HitPoster(BaseModel):
    model_config = ConfigDict(extra="ignore")
    author_ref: AuthorRef | None
    author_type: Literal["source", "individual"]
    author_source_id: AuthorSourceId | None


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


class TextHit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["item.hits/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    hit_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    status: Literal["active", "retracted"]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    client_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    keyword_set_version: Annotated[str, Field(pattern="^cs:[0-9a-f]{64}$")]
    lang_model_version: LangModelVersion | None
    hit_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    url: Url | None
    poster: HitPoster
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
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
    matched_by: Literal["text"]
    matched_term: Annotated[str, Field(min_length=1)]
    form_id: Annotated[str, Field(min_length=1)]
    occurrences: Annotated[int, Field(ge=1, le=9007199254740991)]
    offsets: Annotated[list[Offset], Field(min_length=1)]
    offsets_in: Literal["text_norm"]


class SourceHit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["item.hits/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    hit_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    status: Literal["active", "retracted"]
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    item_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    kind: Literal["post", "video", "comment", "article", "result"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    client_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    keyword_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    keyword_set_version: Annotated[str, Field(pattern="^cs:[0-9a-f]{64}$")]
    lang_model_version: LangModelVersion | None
    hit_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    url: Url | None
    poster: HitPoster
    video_channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
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
    matched_by: Literal["source"]
    matched_term: None
    form_id: None
    occurrences: Literal[0]
    offsets: Annotated[list[Offset1], Field(max_length=0)]
    offsets_in: None


class ItemHitsV1(RootModel[TextHit | SourceHit]):
    root: Annotated[TextHit | SourceHit, Field(title="ItemHitsV1")]
