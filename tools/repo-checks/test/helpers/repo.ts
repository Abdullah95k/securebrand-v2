// Helpers for exercising the repository's scripts on temporary git repositories.
// Scripts take their data from the git repository of their working directory, so a test runs the
// real script (by absolute path) inside a throwaway repository it builds file by file.
import { spawnSync } from "node:child_process";
import {
  chmodSync,
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..");
export const SCRIPTS = join(ROOT, "scripts");
export const FIXTURES = resolve(dirname(fileURLToPath(import.meta.url)), "../../fixtures");

export interface RunResult {
  code: number;
  stdout: string;
  stderr: string;
  /** stdout and stderr together, for assertions that do not care which stream a line went to. */
  output: string;
}

export interface RunOptions {
  cwd: string;
  env?: NodeJS.ProcessEnv;
  input?: string;
  timeoutMs?: number;
}

// Git must not read the developer's global configuration (signing, hooks, default branch).
const EMPTY_GITCONFIG = join(mkdtempSync(join(tmpdir(), "gitconfig-")), "config");
writeFileSync(EMPTY_GITCONFIG, "");

export const GIT_ENV: NodeJS.ProcessEnv = {
  GIT_CONFIG_GLOBAL: EMPTY_GITCONFIG,
  GIT_CONFIG_NOSYSTEM: "1",
  GIT_AUTHOR_NAME: "Repo Checks",
  GIT_AUTHOR_EMAIL: "repo-checks@example.invalid",
  GIT_COMMITTER_NAME: "Repo Checks",
  GIT_COMMITTER_EMAIL: "repo-checks@example.invalid",
};

/** The environment of the test process without the variables that steer the scripts. */
export function cleanEnv(extra: NodeJS.ProcessEnv = {}): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = { ...process.env, ...GIT_ENV };
  for (const key of Object.keys(env)) {
    if (
      key.startsWith("TEST_") ||
      key.startsWith("GITHUB_") ||
      key.startsWith("POLICY_") ||
      key === "CHECK_BASE" ||
      key === "PR_LABELS" ||
      key === "CI" ||
      key === "E2E_DIR" ||
      key === "IMAGE_REGISTRY" ||
      // Set by the scripts that started this test run (make test): a script under test must take
      // the test's PATH as its caller's.
      key === "SB_CALLER_PATH" ||
      // make passes its command-line variables (SERVICE=, GATE=, ...) to nested makes through
      // MAKEFLAGS and the environment; a test that runs make must start from none of them.
      [
        "MAKEFLAGS",
        "MAKELEVEL",
        "MFLAGS",
        "MAKEOVERRIDES",
        "SERVICE",
        "GATE",
        "ENGINE",
        "NAME",
        "ACCEPTANCE",
        "BASE",
        "FOLLOW",
      ].includes(key)
    ) {
      delete env[key];
    }
  }
  return { ...env, ...extra };
}

export function run(cmd: string, args: string[], opts: RunOptions): RunResult {
  const result = spawnSync(cmd, args, {
    cwd: opts.cwd,
    env: opts.env ?? cleanEnv(),
    input: opts.input,
    encoding: "utf8",
    timeout: opts.timeoutMs ?? 120_000,
    maxBuffer: 64 * 1024 * 1024,
  });
  if (result.error) {
    throw result.error;
  }
  const stdout = result.stdout;
  const stderr = result.stderr;
  return { code: result.status ?? 1, stdout, stderr, output: `${stdout}\n${stderr}` };
}

/** Runs a script from the repository's scripts/ directory inside `cwd`. */
export function script(name: string, args: string[], opts: RunOptions): RunResult {
  return run("bash", [join(SCRIPTS, name), ...args], opts);
}

export class TempRepo {
  readonly dir: string;

  constructor(prefix = "repo-") {
    this.dir = mkdtempSync(join(tmpdir(), prefix));
    this.git("init", "-q", "-b", "main");
  }

  path(rel: string): string {
    return join(this.dir, rel);
  }

  write(rel: string, content: string, mode?: number): this {
    const file = this.path(rel);
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, content);
    if (mode !== undefined) {
      chmodSync(file, mode);
    }
    return this;
  }

  writeJson(rel: string, value: unknown): this {
    return this.write(rel, `${JSON.stringify(value, null, 2)}\n`);
  }

  read(rel: string): string {
    return readFileSync(this.path(rel), "utf8");
  }

  exists(rel: string): boolean {
    return existsSync(this.path(rel));
  }

  remove(rel: string): this {
    rmSync(this.path(rel), { recursive: true, force: true });
    return this;
  }

  copyIn(src: string, rel: string): this {
    cpSync(src, this.path(rel), { recursive: true });
    return this;
  }

  git(...args: string[]): string {
    const result = run("git", args, { cwd: this.dir, env: cleanEnv() });
    if (result.code !== 0) {
      throw new Error(`git ${args.join(" ")} failed in ${this.dir}:\n${result.output}`);
    }
    return result.stdout.trim();
  }

  /** Stages everything and commits; returns the new commit's sha. */
  commit(message = "change"): string {
    this.git("add", "-A");
    this.git("commit", "-q", "--allow-empty", "-m", message);
    return this.git("rev-parse", "HEAD");
  }

  branch(name: string): this {
    this.git("checkout", "-q", "-b", name);
    return this;
  }

  checkout(ref: string): this {
    this.git("checkout", "-q", ref);
    return this;
  }

  cleanup(): void {
    rmSync(this.dir, { recursive: true, force: true });
  }
}

/** Parses the `export KEY='value'` lines a script prints for `eval`. */
export function parseExports(text: string): Record<string, string> {
  const vars: Record<string, string> = {};
  for (const line of text.split("\n")) {
    const match = /^export ([A-Z_][A-Z0-9_]*)=(.*)$/.exec(line.trim());
    if (match?.[1] !== undefined && match[2] !== undefined) {
      let value = match[2];
      if (value.startsWith("'") && value.endsWith("'")) {
        value = value.slice(1, -1).replaceAll("'\\''", "'");
      } else if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      vars[match[1]] = value;
    }
  }
  return vars;
}
