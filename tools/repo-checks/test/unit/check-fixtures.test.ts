import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { FIXTURES, script, TempRepo } from "../helpers/repo.js";

// Token-shaped strings are assembled at run time, so no secret-shaped literal is ever committed
// (GitHub push protection and the fixture check itself would flag one).
const alnum = (n: number): string => "Ab1".repeat(Math.ceil(n / 3)).slice(0, n);
const TOKENS: [string, string][] = [
  ["a Meta access token", `"token": "${"EA" + "AB"}${alnum(120)}"`],
  ["a Google API key", `"key": "${"AI" + "za"}${alnum(35)}"`],
  ["a JWT", `"jwt": "${"ey" + "J"}${alnum(20)}.${"ey" + "J"}${alnum(30)}.${alnum(40)}"`],
  ["a bearer token", `"auth": "${"Bea" + "rer"} ${alnum(40)}"`],
  ["an AWS access key", `"aws": "${"AK" + "IA"}${"ABCDEFGHIJKLMNOP"}"`],
  ["a Telegram bot token", `"bot": "${"12345" + "6789"}:${"AA"}${alnum(33)}"`],
  [
    "an access_token parameter",
    `"url": "https://graph.example.com/me?${"access" + "_token"}=${alnum(60)}"`,
  ],
  [
    "an S3 signed URL",
    `"url": "https://bucket.example.com/a.jpg?X-Amz-Credential=x&${"X-Amz-" + "Signature"}=${alnum(64)}"`,
  ],
  [
    "a Signature parameter",
    `"url": "https://cdn.example.com/a.mp4?Expires=1&${"Signa" + "ture"}=${alnum(40)}"`,
  ],
  ["a sig parameter", `"url": "https://cdn.example.com/a.jpg?e=1&${"si" + "g"}=${alnum(32)}"`],
];

describe("scripts/check-fixtures.sh", () => {
  let repo: TempRepo;

  function check(): ReturnType<typeof script> {
    return script("check-fixtures.sh", [], { cwd: repo.dir });
  }

  function platform(dir: string, files: Record<string, string>): void {
    const names = Object.keys(files);
    repo.write(
      `fixtures/${dir}/README.md`,
      `# ${dir}\n\n${names.map((n) => `- ${n}: recorded 2026-10-07`).join("\n")}\n`,
    );
    for (const [name, content] of Object.entries(files)) {
      repo.write(`fixtures/${dir}/${name}`, content);
    }
  }

  beforeEach(() => {
    repo = new TempRepo("fixtures-");
    repo.write(".gitignore", "fixtures/*/raw/\n");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it.each(TOKENS)("fails when a fixture holds %s", (_kind, line) => {
    platform("facebook", { "feed.json": `{\n  "id": "1",\n  ${line}\n}\n` });
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("fixtures/facebook/feed.json:3");
    // The finding names the file and line, never the secret itself.
    const secret = /"([^"]{30,})"\s*$/.exec(line)?.[1] ?? line;
    expect(result.output).not.toContain(secret.slice(-24));
  });

  it("checks new fixtures before they are committed", () => {
    repo.write("README.md", "x\n").commit();
    platform("instagram", { "media.json": `{\n  ${TOKENS[0]?.[1] ?? ""}\n}\n` });
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("fixtures/instagram/media.json:2");
  });

  it("fails when a fixture directory has no README listing its files", () => {
    repo.write("fixtures/instagram/media.json", "{}\n").commit();
    const missing = check();
    expect(missing.code).not.toBe(0);
    expect(missing.output).toContain("fixtures/instagram");

    repo.write("fixtures/instagram/README.md", "# Instagram\n\n- other.json\n").commit();
    const unlisted = check();
    expect(unlisted.code).not.toBe(0);
    expect(unlisted.output).toContain("media.json");
  });

  it("accepts a file listed in a README of its own subdirectory", () => {
    platform("youtube", { "search.json": "{}\n" });
    repo.write(
      "fixtures/youtube/comments/README.md",
      "- page-1.json: commentThreads, 2026-10-07\n",
    );
    repo.write("fixtures/youtube/comments/page-1.json", "{}\n");
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("fails when a raw directory is tracked", () => {
    platform("telegram", { "updates.json": "{}\n" });
    repo.write("fixtures/telegram/raw/updates.json", "{}\n");
    repo.git("add", "-f", "fixtures/telegram/raw/updates.json");
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("fixtures/telegram/raw");
  });

  it("ignores an untracked raw directory", () => {
    platform("telegram", { "updates.json": "{}\n" });
    repo.commit();
    repo.write("fixtures/telegram/raw/updates.json", TOKENS[0]?.[1] ?? "");
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("passes clean fixtures including Arabic, Sorani, emoji, URLs and hashtags", () => {
    repo.copyIn(join(FIXTURES, "scrub", "clean"), "fixtures/facebook");
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("accepts synthetic-* files without a README entry", () => {
    platform("x", { "search.json": "{}\n" });
    repo.write("fixtures/x/synthetic-rate-limited.json", '{"status": 429}\n');
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("accepts fixtures/contracts and fixtures/text without per-file README entries", () => {
    repo.write("fixtures/contracts/valid/raw-items.v1.json", "{}\n");
    repo.write("fixtures/contracts/invalid/raw-items.v1.missing-id.json", "{}\n");
    repo.write("fixtures/text/golden.jsonl", '{"in": "أهلاً", "out": "اهلا"}\n');
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("still scans fixtures/contracts and fixtures/text for tokens", () => {
    repo.write("fixtures/text/golden.jsonl", `{${TOKENS[1]?.[1] ?? ""}}\n`).commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("fixtures/text/golden.jsonl:1");
  });

  it("passes when there is no fixtures directory", () => {
    repo.write("README.md", "x\n").commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });
});
