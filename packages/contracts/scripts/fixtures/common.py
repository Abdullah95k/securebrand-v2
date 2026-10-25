"""Shared helpers for writing the contract fixtures under fixtures/contracts/ (F2). Every derived
id is computed with the package's own Python helpers, so a fixture agrees with the key rules by
construction; validate() then checks them in both languages."""

import copy
import json
import re
from pathlib import Path
from typing import Any

from listening_contracts.keys import (
    author_ref,
    content_hash,
    deletion_id,
    hit_id,
    idempotency_key,
    item_id,
    raw_ref,
)
from listening_contracts.ulid import deterministic_ulid

REPO = Path(__file__).resolve().parents[4]
ROOT = REPO / "fixtures" / "contracts"
TEST_KEY = b"listening-contracts author_ref test key v1 (published; not a secret)"

MANIFEST: list[dict[str, Any]] = []
EXPECTED: dict[str, dict[str, Any]] = {}
QUEUES: dict[str, dict[str, Any]] = {}
WRITTEN: set[str] = set()

# Recurring ids from the PRD examples.
CLIENT = "0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"
CLIENT2 = "e2a9d0b1-6c7f-4a38-9d5e-0f1a2b3c4d5e"


def ulid_for(time: str, *parts: str) -> str:
    """A stable ULID for a fixture: the time part is `time`, the rest from its parts."""
    return deterministic_ulid(time, ["fixture", *parts])


def meta(
    schema: str, service: str, job_id: str, produced_at: str, version: str = "1.0.0", name: str = ""
) -> dict[str, Any]:
    return {
        "schema": schema,
        "message_id": ulid_for(produced_at, schema, service, name or job_id),
        "produced_at": produced_at,
        "producer": {"service": service, "version": version, "job_id": job_id},
    }


def prov(route: str | None, vendor: str | None, service: str, fetched_at: str) -> dict[str, Any]:
    return {"route": route, "vendor": vendor, "service": service, "fetched_at": fetched_at}


def ref(person_id: str, platform: str) -> str:
    """An author_ref under the published test key (ADR-0010)."""
    return author_ref(TEST_KEY, platform, person_id)


def rawref(route: str, platform: str, day: str, service: str, batch: int, line: int) -> str:
    return raw_ref(route, platform, day, service, batch, line)


def key(platform: str, kind: str, pid: str) -> str:
    return idempotency_key(platform, kind, pid)


def iid(platform: str, kind: str, pid: str) -> str:
    return item_id(idempotency_key(platform, kind, pid))


def _dir(schema: str, kind: str) -> Path:
    base = "dlq/v1" if schema.startswith("dlq.") else schema
    d = ROOT / base / kind
    d.mkdir(parents=True, exist_ok=True)
    return d


# A lone surrogate, which UTF-8 cannot hold: a fixture that carries one writes it as a \u escape.
_LONE_SURROGATE = re.compile("[\ud800-\udfff]")


def json_text(obj: Any) -> str:
    """The JSON text a fixture is written as: UTF-8, except a lone surrogate's escape."""
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    return _LONE_SURROGATE.sub(lambda m: f"\\u{ord(m.group()):04x}", text)


def _dump(path: Path, obj: Any) -> None:
    text = json_text(obj)
    rel = str(path.relative_to(ROOT))
    if rel in WRITTEN:
        raise SystemExit(f"written twice: {rel}")
    WRITTEN.add(rel)
    path.write_text(text, encoding="utf-8")


def valid(
    schema: str, name: str, obj: Any, queue: str | None = None, client_type: str | None = None
) -> Any:
    _dump(_dir(schema, "valid") / f"{name}.json", obj)
    opts: dict[str, Any] = {}
    if queue:
        opts["queue"] = queue
    if client_type:
        opts["client_type"] = client_type
    if opts:
        QUEUES.setdefault(f"{schema}|valid", {})[f"{name}.json"] = opts
    return obj


def tolerant(schema: str, name: str, obj: Any, queue: str | None = None) -> Any:
    _dump(_dir(schema, "tolerant") / f"{name}.json", obj)
    if queue:
        QUEUES.setdefault(f"{schema}|tolerant", {})[f"{name}.json"] = {"queue": queue}
    return obj


def invalid(
    schema: str,
    name: str,
    obj: Any,
    path: list[str | int],
    rule: str,
    queue: str | None = None,
    client_type: str | None = None,
) -> None:
    _dump(_dir(schema, "invalid") / f"{name}.json", obj)
    entry: dict[str, Any] = {"path": path, "rule": rule}
    if queue:
        entry["queue"] = queue
    if client_type:
        entry["client_type"] = client_type
    EXPECTED.setdefault(schema, {})[f"{name}.json"] = entry


def prd(
    service: str,
    prd_path: str,
    line: int,
    schema: str | None,
    fixture: str | None,
    rewrites: list[str],
    note: str | None = None,
) -> None:
    entry: dict[str, Any] = {"service": service, "prd": prd_path, "line": line, "schema": schema}
    if fixture:
        assert schema is not None
        base = "dlq/v1" if schema.startswith("dlq.") else schema
        entry["fixture"] = f"{base}/valid/{fixture}.json"
    else:
        entry["fixture"] = None
    if rewrites:
        entry["rewrites"] = rewrites
    if note:
        entry["note"] = note
    MANIFEST.append(entry)


def _json_blocks(prd_path: str) -> list[int]:
    """The first content line of every JSON block in a PRD's section 6.2."""
    lines = (REPO / prd_path).read_text(encoding="utf-8").splitlines()
    out: list[int] = []
    in62 = False
    fence = False
    for i, line in enumerate(lines, 1):
        if line.startswith("## ") or line.startswith("### "):
            in62 = line.startswith("### 6.2")
        if in62 and line.startswith("```json"):
            fence = True
            out.append(i + 1)
        elif fence and line.startswith("```"):
            fence = False
    return out


def _check_manifest() -> None:
    """Every entry names the first line of a 6.2 JSON block; every such block of every PRD has one."""
    for e in MANIFEST:
        blocks = _json_blocks(e["prd"])
        if e["line"] not in blocks and e["line"] + 1 in blocks:
            e["line"] += 1  # the fence line was given
        if e["line"] not in blocks:
            raise SystemExit(
                f"{e['service']}: line {e['line']} starts no 6.2 JSON block of {e['prd']} ({blocks})"
            )
    seen = {(e["prd"], e["line"]) for e in MANIFEST}
    for path in sorted(REPO.glob("docs/prds/*/*.md")):
        if path.parent.name.startswith("_"):
            continue
        rel = str(path.relative_to(REPO))
        for line in _json_blocks(rel):
            if (rel, line) not in seen:
                raise SystemExit(f"no manifest entry for {rel} line {line}")


def without(obj: Any, *path: str | int) -> Any:
    out = copy.deepcopy(obj)
    cur = out
    for p in path[:-1]:
        cur = cur[p]
    del cur[path[-1]]
    return out


def with_(obj: Any, path: tuple[str | int, ...], value: Any) -> Any:
    out = copy.deepcopy(obj)
    cur = out
    for p in path[:-1]:
        cur = cur[p]
    cur[path[-1]] = value
    return out


def finish() -> None:
    _check_manifest()
    MANIFEST.sort(key=lambda e: (e["prd"], e["line"], e["schema"] or ""))
    for schema, entries in EXPECTED.items():
        base = "dlq/v1" if schema.startswith("dlq.") else schema
        (ROOT / base / "invalid" / "expected.json").write_text(
            json_text(dict(sorted(entries.items()))), encoding="utf-8"
        )
    for k, entries in QUEUES.items():
        schema, kind = k.split("|")
        base = "dlq/v1" if schema.startswith("dlq.") else schema
        (ROOT / base / kind / "options.json").write_text(
            json.dumps(dict(sorted(entries.items())), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (ROOT / "prd-examples.json").write_text(
        json.dumps(
            {
                "description": "Every JSON example in the PRDs' section 6.2, rewritten into its v1 shape as the ADRs require (A6): one fixture per producer and topic, with the rewrites applied; examples that are not messages on a topic or queue name why.",
                "examples": MANIFEST,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


__all__ = [
    "CLIENT",
    "CLIENT2",
    "content_hash",
    "deletion_id",
    "hit_id",
    "iid",
    "invalid",
    "key",
    "meta",
    "prd",
    "prov",
    "rawref",
    "ref",
    "tolerant",
    "ulid_for",
    "valid",
    "with_",
    "without",
]


def metadata_invalids(schema: str, base: Any, prefix: tuple[str, ...] = ()) -> None:
    """The four no-metadata-* invalid fixtures of a schema, from one of its valid messages (A17)."""
    for f in ("schema", "message_id", "produced_at", "producer"):
        invalid(
            schema,
            f"no-metadata-{f.replace('_', '-')}",
            without(base, *prefix, f),
            [*prefix, f],
            f"every message carries {f} (ADR-0002)",
        )
