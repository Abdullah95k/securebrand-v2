"""Every new runtime dependency needs a row in docs/dependencies.md (CLAUDE.md, CONVENTIONS).

Usage: dependencies.py <repo root> <base commit>

Compares the runtime dependencies declared at <base commit> with those in the working tree:
  - npm: "dependencies" and "optionalDependencies" of every package.json (devDependencies are
    tools; workspace:, link:, file: and portal: versions are this repository's own packages);
  - PyPI: [project].dependencies and [project.optional-dependencies] of every pyproject.toml
    (dependency groups are tools; names with a path or workspace source in [tool.uv.sources] are
    this repository's own packages);
  - images: "image:" lines of compose files; FROM, COPY --from and RUN --mount=from= of
    Dockerfiles (build arguments resolved, the file's own stages skipped); the *_REPO and
    *_UPSTREAM entries of stack/versions.env; and in GitHub workflows the job containers, service
    containers and docker:// steps.
A dependency counts as new when no manifest declared it at the base commit; one that moved or
was removed never fails, and a renamed one is new. A row matches when its first cell (or a
backticked name in it) equals the dependency: images by repository without tag, npm names
exactly, PyPI names after PEP 503 normalisation. Standard library only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

REGISTER = "docs/dependencies.md"
LOCAL_NPM = ("workspace:", "link:", "file:", "portal:")
REQUIREMENT_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
VARIABLE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?-([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class Dependency:
    kind: str  # "npm", "PyPI" or "image"
    name: str  # as written, for messages
    key: str  # normalised, for comparison


def pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def image_repository(ref: str) -> str:
    ref = ref.split("@", 1)[0]
    slash = ref.rfind("/")
    colon = ref.rfind(":")
    if colon > slash:
        ref = ref[:colon]
    return ref


def is_workflow(path: str) -> bool:
    return re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", path) is not None


def is_manifest(path: str) -> bool:
    name = PurePosixPath(path).name
    if "/node_modules/" in f"/{path}" or "/.venv/" in f"/{path}":
        return False
    return (
        name in ("package.json", "pyproject.toml")
        or path == "stack/versions.env"
        or is_workflow(path)
        or re.fullmatch(r"(docker-)?compose(\.[\w-]+)?\.ya?ml", name) is not None
        or name == "Dockerfile"
        or name.startswith("Dockerfile.")
        or name.endswith(".Dockerfile")
    )


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout


def working_tree(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(
        "\0"
    ):
        if rel and is_manifest(rel) and (root / rel).is_file():
            files[rel] = (root / rel).read_text(encoding="utf-8", errors="replace")
    return files


def at_commit(root: Path, commit: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in git(root, "ls-tree", "-r", "--name-only", "-z", commit).split("\0"):
        if rel and is_manifest(rel):
            files[rel] = git(root, "show", f"{commit}:{rel}")
    return files


def env_file(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return values


def substitute(text: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(3)
        default = match.group(2)
        return values.get(name, default if default is not None else match.group(0))

    return VARIABLE.sub(repl, text)


def npm(text: str) -> set[Dependency]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return set()
    found: set[Dependency] = set()
    for field in ("dependencies", "optionalDependencies"):
        for name, version in (data.get(field) or {}).items():
            if isinstance(version, str) and version.startswith(LOCAL_NPM):
                continue
            found.add(Dependency("npm", name, name.lower()))
    return found


def pypi(text: str) -> set[Dependency]:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return set()
    project = data.get("project", {})
    requirements = list(project.get("dependencies", []))
    for extra in (project.get("optional-dependencies") or {}).values():
        requirements.extend(extra)
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    local = set()
    for name, source in sources.items():
        entries = source if isinstance(source, list) else [source]
        if any(isinstance(e, dict) and ("path" in e or e.get("workspace")) for e in entries):
            local.add(pep503(name))
    found: set[Dependency] = set()
    for requirement in requirements:
        match = REQUIREMENT_NAME.match(str(requirement))
        if match and pep503(match.group(1)) not in local:
            found.add(Dependency("PyPI", match.group(1), pep503(match.group(1))))
    return found


def compose(text: str, values: dict[str, str]) -> set[Dependency]:
    found: set[Dependency] = set()
    for match in re.finditer(r"^[ \t]*image:[ \t]*[\"']?([^\"'\s#]+)", text, re.MULTILINE):
        repo = image_repository(substitute(match.group(1), values))
        found.add(Dependency("image", repo, repo.lower()))
    return found


def dockerfile(text: str) -> set[Dependency]:
    args: dict[str, str] = {}
    stages: set[str] = set()
    found: set[Dependency] = set()

    def add(ref: str) -> None:
        image = substitute(ref.strip("'\""), args)
        if image.lower() in stages or image.isdigit() or image.lower() == "scratch":
            return
        if "$" not in image:
            repo = image_repository(image)
            found.add(Dependency("image", repo, repo.lower()))

    # Instructions continued with a trailing backslash are read as one line.
    for raw in re.sub(r"\\[ \t]*\r?\n", " ", text).splitlines():
        line = raw.strip()
        arg = re.match(r"(?i)^ARG\s+([A-Za-z_][A-Za-z0-9_]*)=(\S+)", line)
        if arg:
            args[arg.group(1)] = arg.group(2).strip("'\"")
            continue
        frm = re.match(r"(?i)^FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?", line)
        if frm:
            add(frm.group(1))
            if frm.group(2):
                stages.add(frm.group(2).lower())
            continue
        if re.match(r"(?i)^COPY\s", line):
            for ref in re.findall(r"(?i)(?:^|\s)--from=(\S+)", line):
                add(ref)
        elif re.match(r"(?i)^RUN\s", line):
            for mount in re.findall(r"(?i)(?:^|\s)--mount=(\S+)", line):
                for ref in re.findall(r"(?:^|,)from=([^,]+)", mount):
                    add(ref)
    return found


WORKFLOW_IMAGES = (
    re.compile(r"^[ \t]*image:[ \t]*[\"']?([^\"'\s#]+)", re.MULTILINE),
    re.compile(r"^[ \t]*container:[ \t]*[\"']?([^\"'\s#{]+)", re.MULTILINE),
    re.compile(r"^[ \t]*(?:-[ \t]+)?uses:[ \t]*[\"']?docker://([^\"'\s#]+)", re.MULTILINE),
)


def workflow(text: str) -> set[Dependency]:
    """Images of a GitHub workflow: job and service containers, and docker:// steps."""
    found: set[Dependency] = set()
    for pattern in WORKFLOW_IMAGES:
        for match in pattern.finditer(text):
            if "$" in match.group(1):  # an expression such as ${{ matrix.image }}
                continue
            repo = image_repository(match.group(1))
            found.add(Dependency("image", repo, repo.lower()))
    return found


def versions_env(text: str) -> set[Dependency]:
    found: set[Dependency] = set()
    for key, value in env_file(text).items():
        if (key.endswith("_REPO") or key.endswith("_UPSTREAM")) and value:
            repo = image_repository(value)
            found.add(Dependency("image", repo, repo.lower()))
    return found


def collect(files: dict[str, str]) -> dict[Dependency, str]:
    values = env_file(files.get("stack/versions.env", ""))
    declared: dict[Dependency, str] = {}
    for path, text in sorted(files.items()):
        name = PurePosixPath(path).name
        if name == "package.json":
            deps = npm(text)
        elif name == "pyproject.toml":
            deps = pypi(text)
        elif path == "stack/versions.env":
            deps = versions_env(text)
        elif is_workflow(path):
            deps = workflow(text)
        elif name.endswith((".yml", ".yaml")):
            deps = compose(text, values)
        else:
            deps = dockerfile(text)
        for dep in deps:
            declared.setdefault(dep, path)
    return declared


def register_keys(text: str) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for line in text.splitlines():
        if not line.startswith("|") or re.match(r"^\|\s*-", line):
            continue
        first = line.strip("|").split("|", 1)[0].strip()
        names = re.findall(r"`([^`]+)`", first) or [first]
        for name in names:
            name = name.strip()
            if name and name.lower() != "name":
                keys.add(("plain", name.lower()))
                keys.add(("pep503", pep503(name)))
    return keys


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    root, base = Path(argv[1]), argv[2]
    before = {(d.kind, d.key) for d in collect(at_commit(root, base))}
    now = collect(working_tree(root))
    register_path = root / REGISTER
    keys = (
        register_keys(register_path.read_text(encoding="utf-8"))
        if register_path.is_file()
        else set()
    )

    missing = []
    for dep, path in sorted(now.items(), key=lambda item: (item[0].kind, item[0].key)):
        if (dep.kind, dep.key) in before:
            continue
        wanted = ("pep503", dep.key) if dep.kind == "PyPI" else ("plain", dep.key)
        if wanted not in keys:
            missing.append(f"  {dep.name} ({dep.kind}, declared in {path})")

    if missing:
        print(
            "check-dependencies: new runtime dependencies without a row in docs/dependencies.md:",
            file=sys.stderr,
        )
        print("\n".join(missing), file=sys.stderr)
        print(
            "Add one row each (name, kind, version, licence, owner, country, used by, session,"
            " screen result) after checking the vendor screen in docs/prds/_shared/CONVENTIONS.md.",
            file=sys.stderr,
        )
        return 1
    print("check-dependencies: every new runtime dependency has its row in docs/dependencies.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
