# Generated from schemas/crawl.policies/v1.json by scripts/gen_python.py (strict). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel


class CrawlDelaySeconds(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class RslAbsent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    found: Literal[False]


class Permit(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Prohibit(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class ChangedField(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class RequestedBy(RootModel[str]):
    root: Annotated[str, Field(max_length=256, min_length=1)]


class Producer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class Group(RootModel[str]):
    root: Annotated[str, Field(min_length=1)]


class Sitemap(RootModel[str]):
    root: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]


class RobotsRuleLists(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allow: list[str]
    disallow: list[str]


class UsageSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search: Literal["yes", "no", "unset"]
    ai_input: Literal["yes", "no", "unset"]
    ai_train: Literal["yes", "no", "unset"]


class Amount(RootModel[float]):
    root: Annotated[float, Field(ge=0.0)]


class RslPayment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Annotated[str, Field(min_length=1)]
    amount: Amount | None


class Http402(BaseModel):
    model_config = ConfigDict(extra="forbid")
    http_402: bool
    price: str | None


class Vendor(RootModel[str]):
    root: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["green", "amber"]
    vendor: Vendor | None
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    fetched_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class RslFound(BaseModel):
    model_config = ConfigDict(extra="forbid")
    found: Literal[True]
    url: Annotated[str, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")]
    permits: list[Permit]
    prohibits: list[Prohibit]
    payment: RslPayment | None


class RobotsRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group: Group | None
    rules: RobotsRuleLists
    sitemaps: list[Sitemap]
    hash: Annotated[str, Field(pattern="^[0-9a-f]{64}$")]


class CrawlPoliciesV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Annotated[Literal["crawl.policies/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    host: Annotated[
        str, Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$")
    ]
    status: Literal["allowed", "disallowed", "paywalled", "blocked"]
    crawl_allowed: bool
    reason: (
        Literal[
            "robots_unreachable",
            "content_signal_search_no",
            "robots_disallowed",
            "rsl_prohibited",
            "rsl_payment",
            "http_402",
            "challenge",
        ]
        | None
    )
    access_mode: Literal["direct", "headless", "proxy", "blocked"]
    crawl_delay_seconds: CrawlDelaySeconds | None
    robots_status: Literal["ok", "unavailable"]
    robots_rules: RobotsRules | None
    usage_signals: UsageSignals
    rsl: RslAbsent | RslFound
    payment: Http402
    checked_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    expires_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    policy_version: Annotated[int, Field(ge=1, le=9007199254740991)]
    changed_fields: list[ChangedField]
    requested_by: RequestedBy | None
    kind: Literal["first_check", "refresh", "recheck", "ops_force"]
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
