# Generated from schemas/item.metrics/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class CreatedAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Producer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class RefreshObservation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: Literal["refresh"]
    step: Annotated[str, Field(pattern="^(\\+24h|\\+7d|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$")]
    observed_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class ReadObservation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: Literal["first_sight", "poll", "backfill", "ops_force", "live_end"]
    step: None
    observed_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


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
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
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


class ItemMetricsV1(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["item.metrics/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
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
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    created_at: CreatedAt | None
    observation: Annotated[RefreshObservation | ReadObservation, Field(title="Observation")]
    metrics: Metrics
    channel_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    live_state: Literal["none", "upcoming", "live"] | MISSING = MISSING
    regressed: bool | MISSING = MISSING
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
