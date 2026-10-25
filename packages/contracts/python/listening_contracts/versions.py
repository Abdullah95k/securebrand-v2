"""Versions (ADR-0002), the twin of src/versions.ts: a consumer reads the versions it reads, skips a
version the package knows that it does not read, and parks a version the package does not know. The
catalogue is the one the TypeScript exporter writes (schemas/catalogue.json)."""

from collections.abc import Sequence
from typing import Literal, TypedDict, cast

from listening_contracts._artefacts import artefact
from listening_contracts.patterns import matches

CatalogueEntry = TypedDict(
    "CatalogueEntry",
    {
        "id": str,
        "class": Literal["data", "control"],
        "file": str,
        "module": str,
        "title": str,
    },
)


class _CatalogueFile(TypedDict):
    schemas: list[CatalogueEntry]
    report_kind_fields: dict[str, list[str]]


_FILE = cast(_CatalogueFile, artefact("catalogue.json"))

CATALOGUE: tuple[CatalogueEntry, ...] = tuple(_FILE["schemas"])
"""Every schema id of the package, `dlq.<service>/v1` as one id (F-52)."""
SCHEMA_IDS: tuple[str, ...] = tuple(e["id"] for e in CATALOGUE)
REPORT_KIND_FIELDS: dict[str, tuple[str, ...]] = {
    field: tuple(kinds) for field, kinds in _FILE["report_kind_fields"].items()
}
"""The kind fields of a jobs.completed report and the kinds that may carry them (ADR-0017)."""

VersionVerdict = Literal["read", "skip", "park"]


def catalogue_id(schema_id: str) -> str:
    """The catalogue id of a concrete schema id: every dlq.<service>/v1 is one."""
    return "dlq.<service>/v1" if matches("dlqSchema", schema_id) else schema_id


def catalogue_entry(schema_id: str) -> CatalogueEntry | None:
    key = catalogue_id(schema_id)
    return next((e for e in CATALOGUE if e["id"] == key), None)


def classify_version(schema_id: str, reads: Sequence[str]) -> VersionVerdict:
    """`read` a version the consumer reads, `skip` a known one it does not, `park` the rest."""
    key = catalogue_id(schema_id)
    if key in {catalogue_id(r) for r in reads}:
        return "read"
    return "skip" if key in SCHEMA_IDS else "park"
