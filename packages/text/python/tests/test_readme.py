"""The README's Python example (the brief's "Done when"): it runs under the twin and prints what the
README shows."""

import os
import re
import subprocess
import sys

from conftest import PACKAGE_DIR

README = PACKAGE_DIR / "README.md"


def _block(lang: str) -> str:
    """The body of the first fenced block of the README whose info string is `lang`."""
    m = re.search(rf"^```{lang}\n(.*?)^```$", README.read_text(encoding="utf-8"), re.M | re.S)
    assert m is not None, f"README.md has no ```{lang} block"
    return m.group(1)


def test_the_readmes_python_example_prints_what_the_readme_shows() -> None:
    run = subprocess.run(
        [sys.executable, "-c", _block("python")],
        capture_output=True,
        check=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert run.stdout == _block("console")
