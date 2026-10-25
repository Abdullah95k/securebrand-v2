import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import { golden, PACKAGE_DIR } from "../helpers.ts";

interface Sample {
  key: string;
  item_id: string;
}

describe("replay changes nothing", () => {
  it("every helper returns the same output for the same input in a fresh process and in the other language (the golden files are the shared record)", () => {
    const keys = golden<{
      keys: {
        input: { platform: string; kind: string; platform_id: string };
        key: string;
        item_id: string;
      }[];
    }>("keys.json").keys;
    const urls = golden<{ urls: { input: string; base?: string; url_hash: string }[] }>(
      "urls.json",
    ).urls;
    const script = `
      import { idempotencyKey, itemId, urlHash } from ${JSON.stringify(`${PACKAGE_DIR}src/keys/index.ts`)};
      const keys = ${JSON.stringify(keys.map((k) => k.input))};
      const urls = ${JSON.stringify(urls.map((u) => [u.input, u.base ?? null]))};
      const out = {
        keys: keys.map((k) => { const key = idempotencyKey(k.platform, k.kind, k.platform_id); return { key, item_id: itemId(key) }; }),
        urls: urls.map(([u, b]) => urlHash(u, b ?? undefined)),
      };
      process.stdout.write(JSON.stringify(out));
    `;
    const stdout = execFileSync(process.execPath, ["--input-type=module", "-e", script], {
      encoding: "utf8",
    });
    const out = JSON.parse(stdout) as { keys: Sample[]; urls: string[] };
    expect(out.keys).toEqual(keys.map((k) => ({ key: k.key, item_id: k.item_id })));
    expect(out.urls).toEqual(urls.map((u) => u.url_hash));
  });
});
