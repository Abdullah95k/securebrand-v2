"""Generates the Pydantic v2 models of every schema id from the committed JSON Schemas (ADR-0030).

python/listening_contracts/models/strict/ holds the producer variant (extra='forbid') and
models/consumer/ the consumer variant (extra='ignore'), one module per schema id, written by
datamodel-code-generator and then sorted and formatted by ruff with this package's settings, so a
fresh generation is byte for byte the committed one (A3). Never edit the generated modules: a
construct the generator cannot render is rewritten in the Zod source.

    uv run python scripts/gen_python.py          # rewrite the committed models
    uv run python scripts/gen_python.py --check  # exit 1 when they differ from a fresh generation
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = PACKAGE_DIR / "schemas"
MODELS_DIR = PACKAGE_DIR / "python" / "listening_contracts" / "models"
CONFIG = PACKAGE_DIR / "pyproject.toml"
MODES = {"strict": "forbid", "consumer": "ignore"}
VARIANTS = {"strict": "the producer variant", "consumer": "the consumer variant"}

FLAGS = [
    "--input-file-type=jsonschema",
    "--output-model-type=pydantic_v2.BaseModel",
    "--target-python-version=3.13",
    "--target-pydantic-version=2.12",
    "--use-annotated",
    "--field-constraints",
    "--use-union-operator",
    "--use-standard-collections",
    "--enum-field-as-literal=all",
    "--use-double-quotes",
    "--disable-timestamp",
    # An optional field may be absent but never null, as in Zod (VERSIONING.md).
    "--use-missing-sentinel",
    "--collapse-root-models",
    "--use-title-as-name",
    # ruff runs below with this package's settings wherever the output goes.
    "--formatters=builtin",
]

PACKAGE_DOC = '''"""Pydantic models generated from schemas/ by scripts/gen_python.py.

strict/ is the producer variant (unknown fields refused), consumer/ the consumer variant (unknown
fields dropped), one module per schema id (ADR-0002, ADR-0030). Do not edit: regenerate.
"""
'''


def schema_files() -> list[Path]:
    """Every exported schema id (patterns.json and vocabulary.json are not schemas)."""
    return sorted(SCHEMAS_DIR.glob("*/*.json"))


def module_name(schema: Path) -> str:
    """raw.items/v1.json -> raw_items_v1, as src/export.ts names it."""
    rel = schema.relative_to(SCHEMAS_DIR).with_suffix("").as_posix()
    return rel.replace(".", "_").replace("/", "_")


def generate(out: Path) -> None:
    """Writes the models package (both variants) under `out`."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "__init__.py").write_text(PACKAGE_DOC, encoding="utf-8")
    for mode, extra in MODES.items():
        directory = out / mode
        directory.mkdir()
        doc = f'"""The {mode} models, {VARIANTS[mode]}: extra fields {extra}."""\n'
        (directory / "__init__.py").write_text(doc, encoding="utf-8")
        for schema in schema_files():
            rel = schema.relative_to(PACKAGE_DIR).as_posix()
            header = f"# Generated from {rel} by scripts/gen_python.py ({mode}). Do not edit."
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "datamodel_code_generator",
                    f"--input={schema}",
                    f"--output={directory / (module_name(schema) + '.py')}",
                    f"--extra-fields={extra}",
                    f"--custom-file-header={header}",
                    *FLAGS,
                ],
                check=True,
            )
    # The generator's import block and the order of `None` in a union, then the package's format,
    # made canonical whatever trailing commas the generator wrote (a file formatted so is stable
    # under the default settings `ruff format --check` uses).
    ruff = [sys.executable, "-m", "ruff"]
    subprocess.run(
        [
            *ruff,
            "check",
            f"--config={CONFIG}",
            "--fix",
            "--select=I001,RUF036",
            "--quiet",
            str(out),
        ],
        check=True,
    )
    subprocess.run(
        [
            *ruff,
            "format",
            f"--config={CONFIG}",
            "--config=format.skip-magic-trailing-comma = true",
            "--quiet",
            str(out),
        ],
        check=True,
    )


def tree(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted(root.rglob("*.py"))
    }


def differences() -> list[str]:
    """The model files that differ between the committed tree and a fresh generation."""
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "models"
        generate(fresh)
        new, old = tree(fresh), tree(MODELS_DIR) if MODELS_DIR.exists() else {}
    return sorted(k for k in new.keys() | old.keys() if new.get(k) != old.get(k))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Pydantic models (ADR-0030).")
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    args = parser.parse_args()
    if args.check:
        stale = differences()
        for name in stale:
            print(f"stale: models/{name}", file=sys.stderr)
        return 1 if stale else 0
    # Generate beside the committed tree and swap it in only once generation succeeds, so a failing
    # run leaves the committed models in place.
    with tempfile.TemporaryDirectory(dir=MODELS_DIR.parent) as tmp:
        fresh = Path(tmp) / "models"
        generate(fresh)
        if MODELS_DIR.exists():
            shutil.rmtree(MODELS_DIR)
        fresh.rename(MODELS_DIR)
    print(f"gen:python wrote {len(tree(MODELS_DIR))} files to {MODELS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
