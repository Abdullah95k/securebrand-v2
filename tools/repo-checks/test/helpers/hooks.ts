// Runs a Claude Code hook from .claude/hooks the way Claude Code does: the event's JSON payload on
// stdin, the exit code and stderr as the answer (exit 2 blocks the call and shows stderr to Claude).
import { join } from "node:path";
import { cleanEnv, ROOT, run, type RunResult } from "./repo.js";

export const HOOKS = join(ROOT, ".claude", "hooks");

export function runHook(
  name: string,
  payload: object,
  opts: { cwd: string; env?: NodeJS.ProcessEnv },
): RunResult {
  return run("bash", [join(HOOKS, name)], {
    cwd: opts.cwd,
    env: cleanEnv(opts.env),
    input: JSON.stringify(payload),
  });
}
