import { mkdtempSync, readFileSync, rmSync, writeFileSync, existsSync, chmodSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, script, TempRepo } from "../helpers/repo.js";

// A fake docker that answers `buildx imagetools inspect` from digest files and records
// `buildx imagetools create`, so the mirror logic runs without a registry.
const FAKE_DOCKER = `#!/usr/bin/env bash
set -euo pipefail
echo "$*" >> "$SHIM_DIR/calls.log"
key() { printf '%s' "$1" | tr '/:' '__'; }
case "$1 $2 $3" in
  "buildx imagetools inspect")
    file="$SHIM_DIR/$(key "$4")"
    [ -f "$file" ] || { echo "ERROR: $4: not found" >&2; exit 1; }
    cat "$file"
    ;;
  "buildx imagetools create")
    [ "$4" = "--tag" ] || { echo "unexpected: $*" >&2; exit 2; }
    cp "$SHIM_DIR/$(key "$6")" "$SHIM_DIR/$(key "$5")"
    ;;
  *) echo "unexpected docker call: $*" >&2; exit 2 ;;
esac
`;

const MIRROR = "ghcr.io/owner/repo-x/cache";
const UPSTREAM = "docker.io/example/cache";
const DIGEST_A = `sha256:${"a".repeat(64)}`;
const DIGEST_B = `sha256:${"b".repeat(64)}`;

describe("scripts/mirror-images.sh", () => {
  let repo: TempRepo;
  let shim: string;

  function setDigest(ref: string, digest: string): void {
    writeFileSync(join(shim, ref.replace(/[/:]/g, "_")), `${digest}\n`);
  }

  function calls(): string[] {
    const log = join(shim, "calls.log");
    return existsSync(log) ? readFileSync(log, "utf8").trim().split("\n") : [];
  }

  function mirror(extra: NodeJS.ProcessEnv = {}): ReturnType<typeof script> {
    return script("mirror-images.sh", [], {
      cwd: repo.dir,
      env: cleanEnv({
        GITHUB_REPOSITORY: "Owner/Repo-X",
        SHIM_DIR: shim,
        PATH: `${shim}:${process.env.PATH ?? ""}`,
        ...extra,
      }),
    });
  }

  beforeEach(() => {
    shim = mkdtempSync(join(tmpdir(), "docker-shim-"));
    writeFileSync(join(shim, "docker"), FAKE_DOCKER);
    chmodSync(join(shim, "docker"), 0o755);
    repo = new TempRepo("mirror-");
    repo
      .write(
        "stack/versions.env",
        [
          "DB_TAG=1.0",
          "DB_REPO=public.ecr.aws/example/db",
          "DB_UPSTREAM=docker.io/example/db",
          "CACHE_TAG=7.0",
          `CACHE_REPO=${MIRROR}`,
          `CACHE_UPSTREAM=${UPSTREAM}`,
          "",
        ].join("\n"),
      )
      .commit("pins");
  });

  afterEach(() => {
    repo.cleanup();
    rmSync(shim, { recursive: true, force: true });
  });

  it("copies a pinned tag the mirror does not have yet and leaves anonymous upstreams alone", () => {
    setDigest(`${UPSTREAM}:7.0`, DIGEST_A);
    const result = mirror();
    expect(result.code, result.output).toBe(0);
    expect(calls()).toContain(`buildx imagetools create --tag ${MIRROR}:7.0 ${UPSTREAM}:7.0`);
    expect(calls().join("\n")).not.toContain("example/db");
  });

  it("leaves a mirrored tag alone when its digest matches the upstream's", () => {
    setDigest(`${UPSTREAM}:7.0`, DIGEST_A);
    setDigest(`${MIRROR}:7.0`, DIGEST_A);
    const result = mirror();
    expect(result.code, result.output).toBe(0);
    expect(result.output).toContain("already there");
    expect(calls().join("\n")).not.toContain("create");
  });

  it("refuses to replace a mirrored tag whose digest differs from the upstream's outside main", () => {
    setDigest(`${UPSTREAM}:7.0`, DIGEST_A);
    setDigest(`${MIRROR}:7.0`, DIGEST_B);
    const result = mirror();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain(`${MIRROR}:7.0`);
    expect(result.output).toContain(DIGEST_B);
    expect(result.output).toContain(DIGEST_A);
    expect(calls().join("\n")).not.toContain("create");
  });

  it("replaces a differing mirrored tag when MIRROR_REPLACE=1 (the workflow on main)", () => {
    setDigest(`${UPSTREAM}:7.0`, DIGEST_A);
    setDigest(`${MIRROR}:7.0`, DIGEST_B);
    const result = mirror({ MIRROR_REPLACE: "1" });
    expect(result.code, result.output).toBe(0);
    expect(calls()).toContain(`buildx imagetools create --tag ${MIRROR}:7.0 ${UPSTREAM}:7.0`);
  });

  it("fails with the upstream's name when the upstream tag cannot be read", () => {
    const result = mirror();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain(`${UPSTREAM}:7.0`);
    expect(calls().join("\n")).not.toContain("create");
  });
});
