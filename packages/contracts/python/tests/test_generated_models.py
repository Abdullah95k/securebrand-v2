"""A3: the committed Pydantic models equal a fresh generation from the committed JSON Schemas
(ADR-0030)."""

import subprocess
import sys

from conftest import PACKAGE_DIR


def test_committed_models_equal_a_fresh_generation() -> None:
    result = subprocess.run(
        [sys.executable, str(PACKAGE_DIR / "scripts" / "gen_python.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or "run: uv run python scripts/gen_python.py"
