// A3 (.claude/rules/contracts.md: migrations are forward-only): every migration is named
// YYYYMMDDHHMMSS_<name>.sql with a real timestamp, versions are unique, a new migration sorts after
// every one main holds, and no migration file main holds is changed or removed on this branch.
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { MIGRATIONS_DIR, REPO_DIR } from "../../tools/paths.ts";

const NAME = /^([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})_[a-z0-9_]+\.sql$/;

const git = (...args: string[]): string =>
  execFileSync("git", args, {
    cwd: REPO_DIR,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
  });

/** origin/main, else main: the branch whose migrations are merged. */
function mainRef(): string {
  for (const ref of ["origin/main", "main"]) {
    try {
      git("rev-parse", "--verify", "-q", `${ref}^{commit}`);
      return ref;
    } catch {
      // not here; try the next
    }
  }
  throw new Error("neither origin/main nor main is here: git fetch origin main");
}

/** The migration files main holds, as repository paths. */
const merged = (): string[] =>
  git("ls-tree", "--name-only", `${mainRef()}`, "supabase/migrations/")
    .split("\n")
    .filter((p) => p.endsWith(".sql"));

const files = (): string[] => readdirSync(MIGRATIONS_DIR).sort();

describe("migration files", () => {
  it("every file name has the timestamp form", () => {
    expect(files().length).toBeGreaterThan(0);
    for (const file of files()) {
      const m = NAME.exec(file);
      expect(m, file).not.toBeNull();
      const [year, month, day, hour, minute, second] = (m ?? []).slice(1).map(Number);
      const at = new Date(Date.UTC(year ?? 0, (month ?? 0) - 1, day, hour, minute, second));
      expect(at.toISOString().slice(0, 19).replace(/[-T:]/g, ""), file).toBe(file.slice(0, 14));
    }
    const versions = files().map((f) => f.slice(0, 14));
    expect(new Set(versions).size).toBe(versions.length);
  });

  it("every new migration sorts after the last one main holds", () => {
    const onMain = new Set(merged().map((p) => p.split("/").at(-1) ?? ""));
    const last = [...onMain].sort().at(-1) ?? "";
    for (const file of files().filter((f) => !onMain.has(f))) expect(file > last, file).toBe(true);
  });

  it("no merged migration file differs from main", () => {
    const ref = mainRef();
    for (const path of merged()) {
      expect(existsSync(join(REPO_DIR, path)), `${path} is removed`).toBe(true);
      expect(readFileSync(join(REPO_DIR, path), "utf8"), `${path} differs from ${ref}`).toBe(
        git("show", `${ref}:${path}`),
      );
    }
  });
});
