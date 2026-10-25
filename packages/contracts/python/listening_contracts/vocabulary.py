"""The closed lists, as the TypeScript source exports them (schemas/vocabulary.json); each list's
source is named in packages/contracts/src/vocabulary.ts."""

from typing import cast

from listening_contracts._artefacts import artefact

_V = cast(dict[str, list[str]], artefact("vocabulary.json"))


def _list(name: str) -> tuple[str, ...]:
    return tuple(_V[name])


PLATFORMS = _list("PLATFORMS")
ROUTES = _list("ROUTES")
RETENTION_CLASSES = _list("RETENTION_CLASSES")
CONTENT_KINDS = _list("CONTENT_KINDS")
ARCHIVE_ONLY_KINDS = _list("ARCHIVE_ONLY_KINDS")
RECORD_KINDS = _list("RECORD_KINDS")
JOB_KINDS = _list("JOB_KINDS")
DELETION_REASONS = _list("DELETION_REASONS")
DELETION_SCOPES = _list("DELETION_SCOPES")
DELETION_MODES = _list("DELETION_MODES")
CARD_TYPES = _list("CARD_TYPES")
VOCABULARY: dict[str, tuple[str, ...]] = {name: tuple(values) for name, values in _V.items()}
