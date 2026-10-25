import { chmodSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, script, TempRepo } from "../helpers/repo.js";

// A fake docker: the daemon answers, no image is local, every pulled image is logged, and a pull of
// an image matching FAIL_MATCH (a shell pattern, * by default) fails with PULL_ANSWER until that
// image has failed FAIL_PULLS times. compose exits 3, so make up never reaches a real stack.
const FAKE_DOCKER = `#!/usr/bin/env bash
case "$1" in
  info) exit 0 ;;
  image) exit 1 ;;
  pull)
    img="\${!#}"
    echo "$img" >> "$SHIM_DIR/pulls.log"
    key="$(printf '%s' "$img" | tr '/:' '__')"
    n="$(cat "$SHIM_DIR/failed-$key" 2>/dev/null || echo 0)"
    case "$img" in
      \${FAIL_MATCH:-*})
        if [ "$n" -lt "\${FAIL_PULLS:-0}" ]; then
          echo $((n + 1)) > "$SHIM_DIR/failed-$key"
          echo "\${PULL_ANSWER:-Error response from daemon: toomanyrequests: Data limit exceeded}" >&2
          exit 1
        fi
        ;;
    esac
    exit 0
    ;;
  compose) exit 3 ;;
  *) echo "unexpected docker call: $*" >&2; exit 2 ;;
esac
`;

const MIRROR = "ghcr.io/abdullah95k/securebrand-v2/redpanda:v26.1.18";
const ECR = "public.ecr.aws/docker/library/clickhouse:26.3.38.2";

describe("scripts/stack-up.sh pulls the stack images", () => {
  let repo: TempRepo;
  let shim: string;

  function pulls(image: string): number {
    const log = join(shim, "pulls.log");
    if (!existsSync(log)) {
      return 0;
    }
    return readFileSync(log, "utf8")
      .split("\n")
      .filter((line) => line === image).length;
  }

  function up(extra: NodeJS.ProcessEnv): ReturnType<typeof script> {
    return script("stack-up.sh", [], {
      cwd: repo.dir,
      env: cleanEnv({
        PATH: `${shim}:${process.env.PATH ?? ""}`,
        SHIM_DIR: shim,
        IMAGE_PULL_RETRY_SECONDS: "0",
        IMAGE_PULL_WAIT_SECONDS: undefined,
        ...extra,
      }),
      // At origin/main a refused pull retried every 20 s for IMAGE_PULL_WAIT_SECONDS: fail fast.
      timeoutMs: 15_000,
    });
  }

  beforeEach(() => {
    shim = mkdtempSync(join(tmpdir(), "stack-up-shim-"));
    writeFileSync(join(shim, "docker"), FAKE_DOCKER);
    chmodSync(join(shim, "docker"), 0o755);
    repo = new TempRepo("stack-up-");
    repo
      .write(
        "stack/versions.env",
        [
          "REDPANDA_TAG=v26.1.18",
          "REDPANDA_REPO=ghcr.io/abdullah95k/securebrand-v2/redpanda",
          "REDPANDA_UPSTREAM=docker.redpanda.com/redpandadata/redpanda",
          "CLICKHOUSE_TAG=26.3.38.2",
          "CLICKHOUSE_REPO=public.ecr.aws/docker/library/clickhouse",
          "CLICKHOUSE_UPSTREAM=docker.io/library/clickhouse",
          "SEAWEEDFS_TAG=4.48",
          "SEAWEEDFS_REPO=ghcr.io/chrislusf/seaweedfs",
          "SEAWEEDFS_UPSTREAM=docker.io/chrislusf/seaweedfs",
          "",
        ].join("\n"),
      )
      .write("node_modules/.bin/supabase", "#!/bin/sh\nexit 0\n", 0o755)
      .commit("pins");
  });

  afterEach(() => {
    repo.cleanup();
    rmSync(shim, { recursive: true, force: true });
  });

  it("retries a failed mirror pull by default and names the registry's answer", () => {
    const result = up({ FAIL_MATCH: "ghcr.io/abdullah95k/*", FAIL_PULLS: "1" });
    expect(pulls(MIRROR), result.output).toBe(2);
    expect(result.output).toContain("toomanyrequests: Data limit exceeded");
    expect(result.output).toContain("IMAGE_PULL_WAIT_SECONDS=300");
  });

  it("fails at once when another registry answers with a data limit, naming its answer and IMAGE_REGISTRY=upstream", () => {
    const result = up({
      IMAGE_PULL_WAIT_SECONDS: "600",
      FAIL_MATCH: "public.ecr.aws/*",
      FAIL_PULLS: "99",
    });
    expect(result.code).not.toBe(0);
    expect(pulls(ECR), result.output).toBe(1);
    expect(result.output).toMatch(/the registry answered: .*Data limit exceeded/);
    expect(result.output).toContain("IMAGE_REGISTRY=upstream");
  });

  it('retries another registry\'s "Rate exceeded" up to 3 times', () => {
    const result = up({
      FAIL_MATCH: "public.ecr.aws/*",
      FAIL_PULLS: "2",
      PULL_ANSWER: "Error response from daemon: toomanyrequests: Rate exceeded",
    });
    expect(pulls(ECR), result.output).toBe(3);
    expect(result.output).not.toContain("could not pull");
  });

  it('gives up on another registry\'s "Rate exceeded" after the fourth pull, naming it', () => {
    const result = up({
      FAIL_MATCH: "public.ecr.aws/*",
      FAIL_PULLS: "99",
      PULL_ANSWER: "Error response from daemon: toomanyrequests: Rate exceeded",
    });
    expect(result.code).not.toBe(0);
    expect(pulls(ECR), result.output).toBe(4);
    expect(result.output).toMatch(/could not pull .*Rate exceeded/);
  });

  it("gives up after IMAGE_PULL_WAIT_SECONDS naming the wait, the answer and IMAGE_REGISTRY=upstream", () => {
    const result = up({
      IMAGE_PULL_WAIT_SECONDS: "0",
      FAIL_MATCH: "ghcr.io/abdullah95k/*",
      FAIL_PULLS: "99",
    });
    expect(result.code).not.toBe(0);
    expect(pulls(MIRROR), result.output).toBe(1);
    expect(result.output).toContain("IMAGE_PULL_WAIT_SECONDS=0");
    expect(result.output).toContain("toomanyrequests: Data limit exceeded");
    expect(result.output).toContain("IMAGE_REGISTRY=upstream");
  });
});
