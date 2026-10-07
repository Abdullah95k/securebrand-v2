"""The job handler: one job in, its outputs out.

Replaying the same job must produce the same outputs and change nothing else (CLAUDE.md). F6
wraps it in py/listening_sdk's job wrapper, which owns retries, the DLQ after five attempts and
cursor advance after the producer acknowledges. The adapter is the only code that talks to the
outside (see docs/patterns/ADAPTER-PATTERN.md); mapping is pure, and outputs use the Pydantic
models generated from packages/contracts, with provenance and retention_class.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from service_template.log import Logger


class Adapter[Request, Record](Protocol):
    def fetch(self, request: Request) -> Sequence[Record]: ...


def handle[Request, Record, Output](
    request: Request,
    fields: dict[str, object],
    adapter: Adapter[Request, Record],
    mapper: Callable[[Record], Output],
    log: Logger,
) -> list[Output]:
    job_log = log.child(**fields)
    records = adapter.fetch(request)
    outputs = [mapper(record) for record in records]
    job_log.info("job handled", records=len(records), outputs=len(outputs))
    return outputs
