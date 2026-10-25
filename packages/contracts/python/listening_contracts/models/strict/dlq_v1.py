# Generated from schemas/dlq/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class DeadLetterError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    class_: Annotated[
        Literal[
            "schema_unknown",
            "invalid",
            "producer_not_allowed",
            "attempts_exhausted",
            "query_rejected",
        ],
        Field(alias="class"),
    ]
    message: Annotated[str, Field(min_length=1)]
    attempts: Annotated[int, Field(ge=1, le=9007199254740991)]
    first_failed_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    last_failed_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class SignalProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["green", "amber"] | None
    vendor: Vendor | None
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    fetched_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Schema(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class MessageId(RootModel[str]):
    root: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class ConsumedOriginal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topic: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    partition: Annotated[int, Field(ge=0, le=9007199254740991)]
    offset: Annotated[int, Field(ge=0, le=9007199254740991)]
    key: str | None
    schema_: Annotated[Schema | None, Field(alias="schema")]
    message_id: MessageId | None


class ConsumerGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    group: Annotated[str, Field(min_length=1)]


class ProducedOriginal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topic: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    partition: None
    offset: None
    key: str | None
    schema_: Annotated[Schema | None, Field(alias="schema")]
    message_id: MessageId | None


class ProducingService(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    group: None


class ConsumeDeadLetter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[str, Field(alias="schema", pattern="^dlq\\.[a-z0-9]+(-[a-z0-9]+)*\\/v1$")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    message: dict[str, Any] | MISSING = MISSING
    raw: Annotated[str | MISSING, Field(pattern="^[A-Za-z0-9+/]*={0,2}$")] = MISSING
    error: DeadLetterError
    provenance: SignalProvenance | MISSING = MISSING
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
    stage: Literal["consume"]
    original: ConsumedOriginal
    consumer: ConsumerGroup


class ProduceDeadLetter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[str, Field(alias="schema", pattern="^dlq\\.[a-z0-9]+(-[a-z0-9]+)*\\/v1$")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    message: dict[str, Any] | MISSING = MISSING
    raw: Annotated[str | MISSING, Field(pattern="^[A-Za-z0-9+/]*={0,2}$")] = MISSING
    error: DeadLetterError
    provenance: SignalProvenance | MISSING = MISSING
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
    stage: Literal["produce"]
    original: ProducedOriginal
    consumer: ProducingService


class DlqV1(RootModel[ConsumeDeadLetter | ProduceDeadLetter]):
    root: Annotated[ConsumeDeadLetter | ProduceDeadLetter, Field(title="DlqV1")]
