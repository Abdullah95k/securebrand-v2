# Generated from schemas/search.results/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class KeywordId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
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


class Variant(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Lang(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class Country(RootModel[str]):
    root: Annotated[str, Field(pattern="^[A-Z]{2}$")]


class RequestId(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: Annotated[str, Field(min_length=1)]
    variant: Variant | None
    lang: Lang | None
    country: Country | None
    request_id: RequestId | None


class Date(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)$"
        ),
    ]


class LastUpdated(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)$"
        ),
    ]


class SearchHit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rank: Annotated[int, Field(ge=1, le=9007199254740991)]
    title: str | None
    url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    snippet: str | None
    date: Date | None
    last_updated: LastUpdated | None


class Domain(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$")
    ]


class GdeltHints(BaseModel):
    model_config = ConfigDict(extra="ignore")
    domain: Domain | None
    language: str | None
    source_country: str | None


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


class SearchResultsV1(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["search.results/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    engine: Literal["perplexity", "mojeek", "gdelt"]
    source_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    keyword_ids: list[KeywordId]
    client_ids: list[ClientId]
    query: SearchRequest
    result: SearchHit
    canonical_url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    canonical_url_hash: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]
    raw_ref: Annotated[
        str,
        Field(
            pattern="^raw\\/(green|amber)\\/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)\\/[0-9]{4}\\/(0[1-9]|1[0-2])\\/(0[1-9]|[12][0-9]|3[01])\\/[a-z0-9]+(-[a-z0-9]+)*\\/[0-9]{6}\\.jsonl\\.zst#[0-9]+$"
        ),
    ]
    hints: GdeltHints | MISSING = MISSING
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
