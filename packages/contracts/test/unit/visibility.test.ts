import { describe, expect, it } from "vitest";
import {
  rawItemsKinds,
  topicWriters,
  visibilityOf,
  visibilityRule,
} from "../../src/registries/index.ts";
import { CONTENT_KINDS } from "../../src/vocabulary.ts";
import { FIXTURES_DIR, listJson, readJson } from "../helpers.ts";

// search-hit-router's `result` records carry the engine's provenance (ADR-0003 L25, ADR-0038 L26),
// so the engines that feed web:result items are the services the gate reads for them (F-18).
const WEB_RESULT_ENGINES = ["web-search-perplexity", "web-search-mojeek", "yt-web-search-bridge"];

describe("visibility per producer (ADR-0053, A24)", () => {
  it("every service that can appear as provenance.service on a content kind declares a visibility", () => {
    const content: readonly string[] = CONTENT_KINDS;
    const writers = (topicWriters()["raw.items/v1"] ?? []).filter(
      (w) => w !== "search-hit-router" && (rawItemsKinds(w) ?? []).some((k) => content.includes(k)),
    );
    expect(writers.length).toBeGreaterThan(40);
    for (const w of [...writers, ...WEB_RESULT_ENGINES])
      expect(visibilityRule(w), w).not.toBeNull();
  });

  it("a web:result fixture's provenance.service declares a visibility (F-18)", () => {
    const dir = `${FIXTURES_DIR}raw.items/v1/valid/`;
    const results = listJson(dir)
      .map(
        (f) =>
          readJson(dir + f) as { envelope?: { kind?: string; provenance?: { service?: string } } },
      )
      .filter((m) => m.envelope?.kind === "result");
    expect(results.length).toBeGreaterThan(0);
    for (const m of results) {
      const service = m.envelope?.provenance?.service ?? "";
      expect(WEB_RESULT_ENGINES).toContain(service);
      expect(visibilityOf(service, false)).toBe("pool");
    }
  });

  it("client-owned sources resolve to owner", () => {
    expect(visibilityOf("fb-page-feed-poller", true)).toBe("owner");
    expect(visibilityOf("fb-page-feed-poller", false)).toBe("watchers");
    expect(visibilityOf("tg-bot-channel-receiver", true)).toBe("owner");
    expect(visibilityOf("tg-bot-channel-receiver", false)).toBe("pool");
    expect(visibilityOf("li-client-posts-poller", false)).toBe("owner");
    expect(visibilityOf("ig-hashtag-search", true)).toBe("watchers");
  });

  it("names the client filter on top of pool: amber consent and the X gate", () => {
    expect(visibilityRule("tt-keyword-search")).toEqual({ rule: "pool", limit: "amber" });
    expect(visibilityRule("x-recent-search")).toEqual({ rule: "pool", limit: "x_gate" });
    expect(visibilityRule("yt-keyword-search")).toEqual({ rule: "pool", limit: null });
  });

  it("a service whose records never become client-facing items declares none", () => {
    for (const s of [
      "fb-page-resolver",
      "web-gdelt-poller",
      "web-commoncrawl-scanner",
      "fb-reactions-fetcher",
      "search-hit-router",
      "news-feed-poller",
    ]) {
      expect(visibilityRule(s), s).toBeNull();
      expect(visibilityOf(s, false), s).toBeNull();
    }
  });
});
