# Generated from schemas/n8n.card/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class CardSubject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_key: Annotated[
        str | MISSING,
        Field(
            pattern="^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\\x00-\\x20:]+|linkedin:[^\\x00-\\x20]+)$"
        ),
    ] = MISSING
    source_id: Annotated[
        str | MISSING,
        Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    ] = MISSING
    decision_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: Annotated[str, Field(min_length=1)]
    value: str


class CardButton(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["approve_tier_1", "approve_tier_2", "approve_tier_3", "reject", "mention_only"]
    label: Annotated[str, Field(min_length=1)]


class CardInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(pattern="^[a-z][a-z0-9_]*$")]
    label: Annotated[str, Field(min_length=1)]
    kind: Literal["url", "text"]


class QualifierReviewCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["n8n.card/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    card_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[str, Field(min_length=1)]
    channel: Literal["email", "telegram", "slack"]
    audience: Literal["client", "ops", "account_manager"]
    client_id: ClientId | None
    subject: CardSubject
    title: Annotated[str, Field(min_length=1)]
    summary: Annotated[str, Field(min_length=1)]
    facts: list[Fact]
    opened_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    card_type: Literal["qualifier_review"]
    buttons: Annotated[list[CardButton], Field(min_length=1)]
    default_action: Literal["reject"]
    timeout_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class ManualUrlCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["n8n.card/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    card_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[str, Field(min_length=1)]
    channel: Literal["email", "telegram", "slack"]
    audience: Literal["client", "ops", "account_manager"]
    client_id: ClientId | None
    subject: CardSubject
    title: Annotated[str, Field(min_length=1)]
    summary: Annotated[str, Field(min_length=1)]
    facts: list[Fact]
    opened_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    card_type: Literal["manual_url"]
    inputs: Annotated[list[CardInput], Field(min_length=1)]
    timeout_at: Annotated[
        str | MISSING,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ] = MISSING


class GrantMissingCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["n8n.card/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    card_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    idempotency_key: Annotated[str, Field(min_length=1)]
    channel: Literal["email", "telegram", "slack"]
    audience: Literal["client", "ops", "account_manager"]
    client_id: ClientId | None
    subject: CardSubject
    title: Annotated[str, Field(min_length=1)]
    summary: Annotated[str, Field(min_length=1)]
    facts: list[Fact]
    opened_at: Annotated[
        str,
        Field(
            pattern="^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    card_type: Literal["grant_missing"]
    regrant_url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class N8nCardV1(RootModel[QualifierReviewCard | ManualUrlCard | GrantMissingCard]):
    root: Annotated[
        QualifierReviewCard | ManualUrlCard | GrantMissingCard, Field(title="N8nCardV1")
    ]
