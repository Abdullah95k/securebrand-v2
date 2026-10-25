import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, script, TempRepo } from "../helpers/repo.js";

// The bind error of CI job 113820378262 (9 Oct): an outbound connection held the database port.
const BIND_ERROR =
  "failed to start docker container: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint supabase_db_securebrand: failed to bind host port for 0.0.0.0:54322:172.19.0.2:5432/tcp: address already in use";

// A fake Supabase CLI: records its calls, reports Supabase stopped unless STATUS_OK=1, and fails
// the first FAIL_STARTS starts with START_ERROR (the bind error by default).
const FAKE_CLI = `#!/usr/bin/env bash
echo "$*" >> "$SHIM_DIR/calls.log"
case "$1" in
  status)
    [ "\${STATUS_OK:-0}" = 1 ] && { echo "supabase local development setup is running."; exit 0; }
    echo "failed to inspect container health: No such container: supabase_db_securebrand" >&2
    exit 1
    ;;
  start)
    n=$(( $(cat "$SHIM_DIR/starts" 2>/dev/null || echo 0) + 1 ))
    echo "$n" > "$SHIM_DIR/starts"
    if [ "$n" -le "\${FAIL_STARTS:-0}" ]; then echo "\${START_ERROR}" >&2; exit 1; fi
    echo "Started supabase local development setup."
    ;;
  stop) echo "Stopped supabase local development setup." ;;
  *) echo "unexpected supabase call: $*" >&2; exit 2 ;;
esac
`;

const EXCLUDE =
  "start --exclude realtime,storage-api,imgproxy,mailpit,postgres-meta,studio,edge-runtime,logflare,vector,supavisor";

describe("scripts/supabase-start.sh", () => {
  let repo: TempRepo;
  let shim: string;

  function calls(): string[] {
    const log = join(shim, "calls.log");
    return existsSync(log) ? readFileSync(log, "utf8").trim().split("\n") : [];
  }

  function start(extra: NodeJS.ProcessEnv = {}): ReturnType<typeof script> {
    return script("supabase-start.sh", [], {
      cwd: repo.dir,
      env: cleanEnv({
        SHIM_DIR: shim,
        SUPABASE_RETRY_WAIT_SECONDS: "0",
        SUPABASE_FULL: undefined,
        START_ERROR: BIND_ERROR,
        ...extra,
      }),
    });
  }

  beforeEach(() => {
    shim = mkdtempSync(join(tmpdir(), "supabase-shim-"));
    repo = new TempRepo("supabase-start-");
    repo.write("node_modules/.bin/supabase", FAKE_CLI, 0o755).write("README.md", "x\n");
    repo.commit("base");
  });

  afterEach(() => {
    repo.cleanup();
    rmSync(shim, { recursive: true, force: true });
  });

  it("retries supabase start once, after supabase stop, when a host port is already in use", () => {
    const result = start({ FAIL_STARTS: "1" });
    expect(result.code, result.output).toBe(0);
    expect(calls()).toEqual(["status", EXCLUDE, "stop", EXCLUDE]);
    expect(result.output).toContain("a Supabase port is in use");
  });

  it("fails naming the port when the second start meets it too", () => {
    const result = start({ FAIL_STARTS: "2" });
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("supabase start failed twice");
    expect(result.output).toContain("':5432[0-9]'");
    expect(calls().filter((call) => call.startsWith("start"))).toHaveLength(2);
  });

  it("does not retry a start that fails for another reason", () => {
    const result = start({
      FAIL_STARTS: "1",
      START_ERROR: "failed to pull docker image: toomanyrequests: Rate exceeded",
    });
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("supabase start failed (output above)");
    expect(calls()).toEqual(["status", EXCLUDE]);
  });

  it("leaves a running Supabase alone", () => {
    const result = start({ STATUS_OK: "1" });
    expect(result.code, result.output).toBe(0);
    expect(calls()).toEqual(["status"]);
    expect(result.output).toContain("Supabase is already running");
  });
});
