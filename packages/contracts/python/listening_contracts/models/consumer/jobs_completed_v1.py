# Generated from schemas/jobs.completed/v1.json by scripts/gen_python.py (consumer). Do not edit.

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.experimental.missing_sentinel import MISSING


class ClientId(RootModel[str]):
    root: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]


class OldestItemAt(RootModel[str]):
    root: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class CommentsTotal(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class Producer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    service: Annotated[str, Field(pattern="^[a-z0-9]+(-[a-z0-9]+)*$")]
    version: Annotated[str, Field(max_length=64, pattern="^[^\\x00-\\x20]+$")]
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]


class ThreadId(RootModel[str]):
    root: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]


class PostRef(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: Annotated[
        str, Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    ]
    platform: Literal[
        "facebook", "instagram", "tiktok", "x", "linkedin", "telegram", "youtube", "news", "web"
    ]
    platform_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    url: Annotated[str | MISSING, Field(pattern="^https?:\\/\\/[^\\x00-\\x20]+$")] = MISSING
    thread_ids: list[ThreadId] | MISSING = MISSING


class ReplyCount(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=9007199254740991)]


class ReplyCandidate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    thread_id: Annotated[str, Field(pattern="^[^\\x00-\\x20]+$")]
    reply_count: ReplyCount | None


class UncoveredWindow(BaseModel):
    model_config = ConfigDict(extra="ignore")
    window_start: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    window_end: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]


class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    new_count: Annotated[int, Field(ge=0, le=9007199254740991)]
    seen_count: Annotated[int, Field(ge=0, le=9007199254740991)]
    pages: Annotated[int, Field(ge=0, le=9007199254740991)]
    cost_units: Annotated[float, Field(ge=0.0)]
    reply_candidates: list[ReplyCandidate]


class DoneReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["done"]
    reason: None


class PartialReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["partial"]
    reason: None


class CappedReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["capped"]
    reason: None
    capped_reason: Literal["route_cap", "budget", "deadline", "failed", "no_history", "flag_off"]


class QuotaDeniedReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["quota_denied"]
    reason: None


class FailedReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["failed"]
    reason: None


class SkippedFlagOffReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["skipped_flag_off"]
    reason: Literal["flag_off"]


class NotAllowedReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["not_allowed"]
    reason: Literal[
        "amber_excluded_government",
        "outside_window",
        "not_root",
        "not_permitted",
        "no_amber_client",
        "x_gate_closed",
    ]


class GoneReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    schema_: Annotated[Literal["jobs.completed/v1"], Field(alias="schema")]
    message_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    produced_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    producer: Producer
    job_id: Annotated[str, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
    queue: Annotated[str, Field(pattern="^jobs\\.[a-z0-9]+(-[a-z0-9]+)*(\\.priority)?$")]
    kind: Literal[
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
    host: Annotated[
        str | MISSING,
        Field(pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\\.?$"),
    ] = MISSING
    crawl_id: Annotated[str | MISSING, Field(pattern="^[^\\x00-\\x20]+$")] = MISSING
    client_id: ClientId | MISSING | None = MISSING
    run_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    request_id: Annotated[str | MISSING, Field(pattern="^[0-7][0-9A-HJKMNP-TV-Z]{25}$")] = MISSING
    post_ref: PostRef | MISSING = MISSING
    series_step: Annotated[
        str | MISSING,
        Field(
            pattern="^(\\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$"
        ),
    ] = MISSING
    attempt: Annotated[int, Field(ge=1, le=9007199254740991)]
    finished_at: Annotated[
        str,
        Field(
            pattern="^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\\.[0-9]{1,3})?Z$"
        ),
    ]
    report: Report
    oldest_item_at: OldestItemAt | MISSING | None = MISSING
    complete: bool | MISSING = MISSING
    stored_before: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    comments_total: CommentsTotal | MISSING | None = MISSING
    paid_user_reads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    free_rereads: Annotated[int | MISSING, Field(ge=0, le=9007199254740991)] = MISSING
    gap_unfilled: UncoveredWindow | MISSING | None = MISSING
    uncovered: UncoveredWindow | MISSING | None = MISSING
    status: Literal["gone"]
    reason: Literal["not_found", "comments_disabled", "no_thread"]


class JobsCompletedV1(
    RootModel[
        DoneReport
        | PartialReport
        | CappedReport
        | QuotaDeniedReport
        | FailedReport
        | SkippedFlagOffReport
        | NotAllowedReport
        | GoneReport
    ]
):
    root: Annotated[
        DoneReport
        | PartialReport
        | CappedReport
        | QuotaDeniedReport
        | FailedReport
        | SkippedFlagOffReport
        | NotAllowedReport
        | GoneReport,
        Field(title="JobsCompletedV1"),
    ]
