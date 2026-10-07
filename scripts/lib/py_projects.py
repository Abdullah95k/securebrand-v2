"""List the Python projects make check must run for a set of changed project directories.

Usage: py_projects.py <repo root> --all
       py_projects.py <repo root> <project dir>...

A Python project is any directory holding a pyproject.toml. The result adds every project that
depends on a listed one through a path source ([tool.uv.sources] name = { path = ... }), so a
change to py/listening_sdk also checks the services built on it. Directories are printed relative
to the repository root, one per line, sorted. Standard library only.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


def projects(root: Path) -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.decode()
    found = set()
    for rel in listed.split("\0"):
        if rel == "pyproject.toml" or not rel.endswith("/pyproject.toml"):
            continue
        if (root / rel).is_file():
            found.add(rel[: -len("/pyproject.toml")])
    return sorted(found)


def path_dependencies(root: Path, project: str) -> set[str]:
    try:
        data = tomllib.loads((root / project / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    deps: set[str] = set()
    for source in sources.values():
        entries = source if isinstance(source, list) else [source]
        for entry in entries:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                target = (root / project / entry["path"]).resolve()
                try:
                    deps.add(target.relative_to(root.resolve()).as_posix())
                except ValueError:
                    continue
    return deps


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[1])
    every = projects(root)
    if argv[2:] == ["--all"]:
        selected = set(every)
    else:
        selected = {d for d in argv[2:] if d in every}
        deps = {p: path_dependencies(root, p) for p in every}
        grew = True
        while grew:
            grew = False
            for project, targets in deps.items():
                if project not in selected and targets & selected:
                    selected.add(project)
                    grew = True
    for project in sorted(selected):
        print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
