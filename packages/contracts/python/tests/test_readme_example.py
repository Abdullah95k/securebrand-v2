"""A34: the package README's Python example runs as written and prints the output the README shows,
the same as the TypeScript example's."""

import contextlib
import io
import re

from conftest import PACKAGE_DIR

README = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")


def _block(lang: str) -> str:
    """The body of the first fenced block whose info string is `lang`."""
    m = re.search(r"^```" + lang + r"\n(.*?)^```$", README, re.MULTILINE | re.DOTALL)
    assert m is not None, f"README.md has no ```{lang} block"
    return m.group(1)


def test_the_readmes_python_example_runs() -> None:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(_block("python"), "README.md", "exec"), {"__name__": "readme_example"})
    assert out.getvalue() == _block("text")
