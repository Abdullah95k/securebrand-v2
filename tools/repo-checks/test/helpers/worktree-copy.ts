// A throwaway copy of the current working tree (tracked and untracked files, ignored ones
// excluded) as a fresh one-commit git repository, with dependencies installed from the local
// pnpm store only. Acceptance tests that create or reformat files run there, never in the
// repository itself.
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { cleanEnv, ROOT, run, type RunResult } from "./repo.js";

export interface WorkingCopy {
  dir: string;
  run(cmd: string, args: string[], extra?: NodeJS.ProcessEnv, timeoutMs?: number): RunResult;
  cleanup(): void;
}

export function copyWorkingTree(): WorkingCopy {
  const dir = mkdtempSync(join(tmpdir(), "worktree-copy-"));
  const listed = run("git", ["ls-files", "-z", "--cached", "--others", "--exclude-standard"], {
    cwd: ROOT,
  });
  for (const rel of listed.stdout.split("\0").filter(Boolean)) {
    const src = join(ROOT, rel);
    let mode: number;
    try {
      mode = statSync(src).mode;
    } catch {
      continue; // deleted in the working tree but still in the index
    }
    const dest = join(dir, rel);
    mkdirSync(dirname(dest), { recursive: true });
    copyFileSync(src, dest);
    chmodSync(dest, mode & 0o777);
  }

  const copy: WorkingCopy = {
    dir,
    run(cmd, args, extra = {}, timeoutMs = 600_000) {
      return run(cmd, args, { cwd: dir, env: cleanEnv(extra), timeoutMs });
    },
    cleanup() {
      rmSync(dir, { recursive: true, force: true });
    },
  };

  for (const args of [
    ["init", "-q", "-b", "main"],
    ["add", "-A"],
    ["commit", "-q", "-m", "snapshot of the working tree"],
  ]) {
    const result = copy.run("git", args);
    if (result.code !== 0) {
      throw new Error(`git ${args.join(" ")} failed:\n${result.output}`);
    }
  }
  const install = copy.run("pnpm", ["install", "--offline", "--frozen-lockfile", "--silent"]);
  if (install.code !== 0) {
    throw new Error(`pnpm install --offline failed in the working copy:\n${install.output}`);
  }
  return copy;
}
