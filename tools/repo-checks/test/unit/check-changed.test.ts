import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, ROOT, run, script, TempRepo } from "../helpers/repo.js";

function gitIn(dir: string, ...args: string[]): string {
  const result = run("git", args, { cwd: dir });
  if (result.code !== 0) {
    throw new Error(`git ${args.join(" ")} failed in ${dir}:\n${result.output}`);
  }
  return result.stdout.trim();
}

// A small workspace shaped like this repository: TypeScript packages with a dependency edge
// (b depends on a), tools and end-to-end workspaces, and independent Python projects, one of
// which depends on another by path.
function scripts(test = 'node -e ""'): Record<string, string> {
  return { lint: 'node -e ""', typecheck: 'node -e ""', test };
}

function buildWorkspace(repo: TempRepo): void {
  repo
    .writeJson("package.json", {
      name: "ws",
      private: true,
      packageManager: "pnpm@10.34.6",
      devDependencies: { turbo: "2.10.13" },
    })
    .write(
      "pnpm-workspace.yaml",
      "packages:\n  - services/*\n  - packages/*\n  - tools/*\n  - tools/probes/*\n  - tests/e2e/*\n",
    )
    .writeJson("turbo.json", {
      tasks: { lint: {}, typecheck: {}, test: {}, "test:acceptance": { cache: false } },
    })
    .write(".gitignore", "node_modules/\n.turbo/\n")
    .writeJson("packages/a/package.json", { name: "a", version: "0.0.0", scripts: scripts() })
    .write("packages/a/index.js", "export const a = 1;\n")
    .writeJson("services/b/package.json", {
      name: "b",
      version: "0.0.0",
      dependencies: { a: "workspace:*" },
      scripts: scripts(),
    })
    .write("services/b/index.js", "export const b = 1;\n")
    .writeJson("services/c/package.json", { name: "c", version: "0.0.0", scripts: scripts() })
    .write("services/c/index.js", "export const c = 1;\n")
    .writeJson("tools/repo-checks/package.json", {
      name: "repo-checks",
      version: "0.0.0",
      scripts: scripts(),
    })
    .writeJson("tools/probes/meta/package.json", {
      name: "probe-meta",
      version: "0.0.0",
      scripts: scripts(),
    })
    .write("tools/probes/meta/scrub.test.js", "// scrubbing test\n")
    .writeJson("tests/e2e/G1/package.json", {
      name: "e2e-g1",
      version: "0.0.0",
      scripts: scripts(),
    })
    .write("tests/e2e/G1/suite.js", "// suite\n")
    .write("services/py-svc/pyproject.toml", '[project]\nname = "py-svc"\nversion = "0.0.0"\n')
    .write("services/py-svc/uv.lock", "version = 1\n")
    .write("services/py-svc/src/py_svc/main.py", "X = 1\n")
    .write(
      "py/listening_sdk/pyproject.toml",
      '[project]\nname = "listening-sdk"\nversion = "0.0.0"\n',
    )
    .write("py/listening_sdk/uv.lock", "version = 1\n")
    .write("py/listening_sdk/src/listening_sdk/__init__.py", "")
    .write(
      "services/py-dep/pyproject.toml",
      [
        "[project]",
        'name = "py-dep"',
        'version = "0.0.0"',
        'dependencies = ["listening-sdk"]',
        "",
        "[tool.uv.sources]",
        'listening-sdk = { path = "../../py/listening_sdk", editable = true }',
        "",
      ].join("\n"),
    )
    .write("services/py-dep/uv.lock", "version = 1\n")
    .write(
      "tools/probes/news/pyproject.toml",
      '[project]\nname = "probe-news"\nversion = "0.0.0"\n',
    )
    .write("tools/probes/news/uv.lock", "version = 1\n")
    .write("tools/probes/news/scrub.py", "X = 1\n")
    .write("fixtures/news/README.md", "# News\n\n- `article.html`: an article page (synthetic)\n")
    .write("fixtures/news/article.html", "<html><body>article</body></html>\n")
    .write("docs/notes.md", "# Notes\n")
    .write("Makefile", "check:\n\t@true\n");
}

interface Plan {
  base: string;
  ts: string[];
  tasks: string[];
  python: Map<string, string>;
  fixtures: boolean;
  raw: string;
}

function parsePlan(text: string): Plan {
  const plan: Plan = { base: "", ts: [], tasks: [], python: new Map(), fixtures: false, raw: text };
  for (const line of text.split("\n")) {
    const base = /^base (.+)$/.exec(line);
    if (base?.[1] !== undefined) {
      plan.base = base[1];
    }
    const turbo = /^step turbo (.+?) :: (.*)$/.exec(line);
    if (turbo?.[1] !== undefined && turbo[2] !== undefined) {
      plan.tasks = turbo[1].split(" ");
      plan.ts = turbo[2].split(" ").filter(Boolean).sort();
    }
    const python = /^step python (\S+) :: (.*)$/.exec(line);
    if (python?.[1] !== undefined && python[2] !== undefined) {
      plan.python.set(python[1], python[2]);
    }
    if (/^step fixtures :: /.test(line)) {
      plan.fixtures = true;
    }
  }
  return plan;
}

describe("scripts/check-changed.sh", () => {
  let repo: TempRepo;

  function plan(...args: string[]): Plan {
    const result = script("check-changed.sh", ["--plan", ...args], { cwd: repo.dir });
    expect(result.code, result.output).toBe(0);
    return parsePlan(result.stdout);
  }

  beforeAll(() => {
    repo = new TempRepo("check-changed-");
    // No install: the script runs the turbo that ships with it on any workspace.
    buildWorkspace(repo);
    repo.commit("base");
  }, 300_000);

  afterAll(() => {
    repo.cleanup();
  });

  beforeEach(() => {
    repo.git("checkout", "-q", "-f", "main");
    repo.git("clean", "-q", "-fd");
    const branches = repo.git("branch", "--format=%(refname:short)").split("\n");
    for (const branch of branches) {
      if (branch !== "main" && branch !== "") {
        repo.git("branch", "-q", "-D", branch);
      }
    }
    repo.branch("sb/T1");
  });

  it("plans lint, typecheck and test for the changed packages and their dependants only", () => {
    repo.write("packages/a/index.js", "export const a = 2;\n");
    const result = plan();
    expect(result.base).toMatch(/^[0-9a-f]{40}$/);
    expect(result.tasks).toEqual(["lint", "typecheck", "test"]);
    expect(result.ts).toEqual(["a", "b"]);
    expect(result.python.size).toBe(0);
  });

  it("counts committed and untracked changes alike", () => {
    repo.write("services/c/index.js", "export const c = 2;\n").commit("c");
    repo.write("services/b/new.js", "export const n = 1;\n");
    expect(plan().ts).toEqual(["b", "c"]);
  });

  it("plans ruff, ruff format, pyright and pytest for every changed directory holding a pyproject.toml wherever it lives", () => {
    repo.write("services/py-svc/src/py_svc/main.py", "X = 2\n");
    repo.write("tools/probes/news/scrub.py", "X = 2\n");
    const result = plan();
    expect([...result.python.keys()].sort()).toEqual(["services/py-svc", "tools/probes/news"]);
    for (const steps of result.python.values()) {
      expect(steps).toContain("uv sync --locked");
      expect(steps).toContain("uv run ruff check .");
      expect(steps).toContain("uv run ruff format --check .");
      expect(steps).toContain("uv run pyright");
      expect(steps).toContain("uv run pytest");
    }
    expect(result.ts).toEqual([]);
  });

  it("plans the Python projects that depend on a changed one by path", () => {
    repo.write("py/listening_sdk/src/listening_sdk/__init__.py", "VERSION = 1\n");
    expect([...plan().python.keys()].sort()).toEqual(["py/listening_sdk", "services/py-dep"]);
  });

  it("adds repo-checks when root tooling changed", () => {
    repo.write("Makefile", "check:\n\t@echo changed\n");
    expect(plan().ts).toContain("repo-checks");
  });

  it("adds repo-checks when root tooling changed among thousands of other files", () => {
    repo.write("Makefile", "check:\n\t@echo changed\n");
    // More than a pipe buffer (64 KiB) of file names, all sorting after the Makefile.
    for (let i = 0; i < 3000; i += 1) {
      repo.write(`zz-bulk/${String(i).padStart(5, "0")}-${"x".repeat(40)}.md`, "x\n");
    }
    expect(plan().ts).toContain("repo-checks");
  });

  it.each(["ruff.toml", ".python-version", "uv.toml"])(
    "plans every Python project when the shared %s changed",
    (file) => {
      repo.write(file, "# shared by every Python project\n");
      expect([...plan().python.keys()].sort()).toEqual([
        "py/listening_sdk",
        "services/py-dep",
        "services/py-svc",
        "tools/probes/news",
      ]);
    },
  );

  it("includes tools and tests workspaces in the Turborepo filter", () => {
    repo.write("tools/probes/meta/scrub.test.js", "// scrubbing test, changed\n");
    repo.write("tests/e2e/G1/suite.js", "// suite, changed\n");
    expect(plan().ts).toEqual(["e2e-g1", "probe-meta"]);
  });

  it.each([
    ["re-recorded", (r: TempRepo) => r.write("fixtures/news/article.html", "<html>new</html>\n")],
    ["removed", (r: TempRepo) => r.remove("fixtures/news/article.html")],
  ])(
    "plans every workspace and Python project when a fixture is %s, since their tests read fixtures/",
    (_, change) => {
      change(repo);
      const result = plan();
      expect(result.ts).toEqual(["a", "b", "c", "e2e-g1", "probe-meta", "repo-checks"]);
      expect([...result.python.keys()].sort()).toEqual([
        "py/listening_sdk",
        "services/py-dep",
        "services/py-svc",
        "tools/probes/news",
      ]);
    },
  );

  it.each([
    ["committed", (r: TempRepo) => r.commit("an Arabic fixture")],
    ["not committed yet", () => undefined],
  ])("plans every workspace and Python project for a fixture named in Arabic, %s", (_, settle) => {
    // Git quotes a path holding non-ASCII bytes unless core.quotePath is off.
    repo.write("fixtures/text/نص-عراقي.txt", "نص\n");
    settle(repo);
    const result = plan();
    expect(result.ts).toEqual(["a", "b", "c", "e2e-g1", "probe-meta", "repo-checks"]);
    expect(result.python.size).toBe(4);
  });

  it("plans no test when only a fixture README changed", () => {
    repo.write(
      "fixtures/news/README.md",
      "# News\n\n- `article.html`: an article page, synthetic\n",
    );
    const result = plan();
    expect(result.ts).toEqual([]);
    expect(result.python.size).toBe(0);
    expect(result.fixtures).toBe(true);
  });

  it("plans nothing but the fixture check when only docs changed", () => {
    repo.write("docs/notes.md", "# Notes, changed\n");
    const result = plan();
    expect(result.ts).toEqual([]);
    expect(result.python.size).toBe(0);
    expect(result.fixtures).toBe(true);
    expect(result.raw).toMatch(/^step turbo none$/m);
  });

  it("adds acceptance suites when asked", () => {
    repo.write("services/c/index.js", "export const c = 3;\n");
    repo.write("services/py-svc/src/py_svc/main.py", "X = 3\n");
    const result = plan("--acceptance");
    expect(result.tasks).toEqual(["lint", "typecheck", "test", "test:acceptance"]);
    expect(result.python.get("services/py-svc")).toMatch(/uv run pytest -q$/);
  });

  it("falls back to the full check and prints a warning when no merge base with main exists", () => {
    repo.git("checkout", "-q", "--orphan", "unrelated");
    repo.commit("unrelated history");
    const result = script("check-changed.sh", ["--plan"], { cwd: repo.dir });
    expect(result.code, result.output).toBe(0);
    expect(result.stderr).toMatch(/no merge base with main/i);
    const full = parsePlan(result.stdout);
    expect(full.base).toBe("none");
    expect(full.ts).toEqual(["a", "b", "c", "e2e-g1", "probe-meta", "repo-checks"]);
    expect([...full.python.keys()].sort()).toEqual([
      "py/listening_sdk",
      "services/py-dep",
      "services/py-svc",
      "tools/probes/news",
    ]);
  });

  // A shallow clone of sb/T1 from a local bare origin (file://, no network): --depth implies
  // --single-branch, so origin/main is missing, and the merge base lies beyond the shallow history.
  function shallowClone(extra: string[] = []): { dir: string; cleanup: () => void } {
    const tmp = mkdtempSync(join(tmpdir(), "shallow-"));
    const origin = join(tmp, "origin.git");
    gitIn(tmp, "clone", "-q", "--bare", repo.dir, origin);
    const dir = join(tmp, "shallow");
    gitIn(
      tmp,
      ...["-c", "protocol.file.allow=always", "clone", "-q", "--depth", "1", ...extra],
      ...["--branch", "sb/T1", `file://${origin}`, dir],
    );
    return { dir, cleanup: () => rmSync(tmp, { recursive: true, force: true }) };
  }

  it("fetches main's history in a shallow clone and compares with the real merge base", () => {
    repo.write("packages/a/index.js", "export const a = 7;\n").commit("a");
    const main = repo.git("rev-parse", "main");
    const clone = shallowClone();
    try {
      const result = script("check-changed.sh", ["--plan"], { cwd: clone.dir });
      expect(result.code, result.output).toBe(0);
      const planned = parsePlan(result.stdout);
      expect(planned.base, result.output).toBe(main);
      expect(planned.ts).toEqual(["a", "b"]);
      expect(result.stderr).toMatch(/shallow clone/);
      expect(gitIn(clone.dir, "rev-parse", "--is-shallow-repository")).toBe("false");
    } finally {
      clone.cleanup();
    }
  });

  // The fetch the scripts run and name: a plain `git fetch --unshallow origin main` leaves origin/main
  // missing in a single-branch clone (its refspec covers only the branch it cloned).
  const UNSHALLOW = "git fetch --unshallow origin +refs/heads/main:refs/remotes/origin/main";

  it("names the shallow clone and git fetch --unshallow when main cannot be fetched", () => {
    repo.write("packages/a/index.js", "export const a = 8;\n").commit("a");
    const clone = shallowClone();
    try {
      gitIn(clone.dir, "remote", "set-url", "origin", "file:///nonexistent");
      const result = script("check-changed.sh", ["--plan"], { cwd: clone.dir });
      expect(result.code, result.output).toBe(0);
      expect(parsePlan(result.stdout).base).toBe("none");
      expect(result.stderr).toContain(`run ${UNSHALLOW}`);
    } finally {
      clone.cleanup();
    }
  });

  it("SB_NO_FETCH=1 leaves the clone shallow and names the fetch to run", () => {
    repo.write("packages/a/index.js", "export const a = 9;\n").commit("a");
    const clone = shallowClone();
    try {
      const result = script("check-changed.sh", ["--plan"], {
        cwd: clone.dir,
        env: cleanEnv({ SB_NO_FETCH: "1" }),
      });
      expect(result.code, result.output).toBe(0);
      expect(parsePlan(result.stdout).base).toBe("none");
      expect(result.stderr).toContain(`run ${UNSHALLOW}`);
      expect(gitIn(clone.dir, "rev-parse", "--is-shallow-repository")).toBe("true");
    } finally {
      clone.cleanup();
    }
  });

  it("the fetch its warning names, run by hand, finds the merge base in a single-branch shallow clone", () => {
    repo.write("packages/a/index.js", "export const a = 10;\n").commit("a");
    const main = repo.git("rev-parse", "main");
    const clone = shallowClone();
    try {
      const warned = script("check-changed.sh", ["--plan"], {
        cwd: clone.dir,
        env: cleanEnv({ SB_NO_FETCH: "1" }),
      });
      const command = /run (git fetch [^\n]*)$/m.exec(warned.stderr)?.[1] ?? "";
      expect(command, warned.output).toMatch(/^git fetch --unshallow origin /);
      gitIn(clone.dir, ...command.split(" ").slice(1));
      const result = script("check-changed.sh", ["--plan"], { cwd: clone.dir });
      expect(parsePlan(result.stdout).base, result.output).toBe(main);
      // review-session tells a reviewer in a shallow clone to run the same fetch.
      expect(
        readFileSync(join(ROOT, ".claude", "skills", "review-session", "SKILL.md"), "utf8"),
      ).toContain(UNSHALLOW);
    } finally {
      clone.cleanup();
    }
  });

  it.each([
    ["with --base origin/main", ["--base", "origin/main"]],
    ["without --base", []],
  ])(
    "the policy checks in a shallow clone compare with the merge base, not main's tip (%s)",
    (_, args) => {
      // main moved on after sb/T1 left it, with a change under a contract path that sb/T1 lacks:
      // compared with main's tip, sb/T1 would seem to change that path.
      repo.write("services/c/index.js", "export const c = 9;\n").commit("c");
      const mainBefore = repo.git("rev-parse", "main");
      repo.checkout("main");
      repo.write("packages/contracts/x.ts", "export {};\n").commit("main moves on");
      repo.checkout("sb/T1");
      let clone: { dir: string; cleanup: () => void } | undefined;
      try {
        clone = shallowClone(["--no-single-branch"]);
        const result = script("policy/check-contract-paths.sh", args, { cwd: clone.dir });
        expect(result.code, result.output).toBe(0);
        expect(result.stdout).toContain("no contract path changed");
      } finally {
        // Every test of this file shares the repository (beforeAll): put main back, whatever failed.
        repo.git("branch", "-f", "main", mainBefore);
        clone?.cleanup();
      }
    },
  );

  it("warns and checks everything when CHECK_BASE is not a commit of this repository", () => {
    repo.write("packages/a/index.js", "export const a = 5;\n");
    const result = script("check-changed.sh", ["--plan"], {
      cwd: repo.dir,
      env: cleanEnv({ CHECK_BASE: "0".repeat(40) }),
    });
    expect(result.code, result.output).toBe(0);
    expect(result.stderr).toContain("CHECK_BASE");
    const full = parsePlan(result.stdout);
    expect(full.base).toBe("none");
    expect(full.ts).toEqual(["a", "b", "c", "e2e-g1", "probe-meta", "repo-checks"]);
  });

  it("compares with CHECK_BASE when it names a commit", () => {
    repo.write("services/c/index.js", "export const c = 6;\n").commit("c");
    const before = repo.git("rev-parse", "HEAD").trim();
    repo.write("packages/a/index.js", "export const a = 6;\n").commit("a");
    const result = script("check-changed.sh", ["--plan"], {
      cwd: repo.dir,
      env: cleanEnv({ CHECK_BASE: before }),
    });
    expect(result.code, result.output).toBe(0);
    const planned = parsePlan(result.stdout);
    expect(planned.base).toBe(before);
    expect(planned.ts).toEqual(["a", "b"]);
  });

  it("gives the acceptance suites the stack variables and the test namespace", () => {
    repo.writeJson("services/c/package.json", {
      name: "c",
      version: "0.0.0",
      scripts: {
        ...scripts(),
        "test:acceptance": [
          'node -e "const e = process.env;',
          "const ok = e.TEST_NAMESPACE === 'sb_t1' && e.TEST_TOPIC_PREFIX === 'sb_t1.'",
          "&& e.KAFKA_BROKERS === '127.0.0.1:19092' && e.S3_ENDPOINT === 'http://127.0.0.1:8333'",
          '&& Boolean(e.CLICKHOUSE_URL); process.exit(ok ? 0 : 9)"',
        ].join(" "),
      },
    });
    repo.writeJson("turbo.json", {
      tasks: {
        lint: {},
        typecheck: {},
        test: {},
        "test:acceptance": { cache: false, env: ["TEST_*", "KAFKA_*", "S3_*", "CLICKHOUSE_*"] },
      },
    });
    const result = script("check-changed.sh", ["--acceptance"], {
      cwd: repo.dir,
      timeoutMs: 240_000,
    });
    expect(result.code, result.output).toBe(0);
    expect(result.output).toContain("make check passed");
  });

  it("a second run with no new changes plans the same steps", () => {
    repo.write("packages/a/index.js", "export const a = 4;\n");
    repo.write("services/py-svc/src/py_svc/main.py", "X = 4\n");
    const first = script("check-changed.sh", ["--plan"], { cwd: repo.dir });
    const second = script("check-changed.sh", ["--plan"], { cwd: repo.dir });
    expect(second.stdout).toBe(first.stdout);
  });

  it("exits non-zero when a planned step fails", () => {
    repo.writeJson("services/c/package.json", {
      name: "c",
      version: "0.0.0",
      scripts: scripts('node -e "process.exit(3)"'),
    });
    const result = script("check-changed.sh", [], { cwd: repo.dir, timeoutMs: 240_000 });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/failed.*turbo/i);
  });

  it('fails with "run uv lock" when a Python project has no lockfile', () => {
    repo.write("services/py-nolock/pyproject.toml", '[project]\nname = "py-nolock"\n');
    const result = script("check-changed.sh", [], { cwd: repo.dir, timeoutMs: 240_000 });
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("run uv lock");
    expect(result.output).toContain("services/py-nolock");
  });
});
