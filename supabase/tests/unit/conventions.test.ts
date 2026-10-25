// The CONVENTIONS readers behind the generated seeds (plan T5), on the real CONVENTIONS text, and
// the amber tag-to-service map the budget seed takes from the PRDs, checked against CONVENTIONS'
// amber marks.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  amberServices,
  budgetTags,
  readConventions,
  seriesProfileRows,
  seriesSteps,
} from "../../tools/conventions.ts";
import {
  AMBER_TAG_SERVICES,
  PROFILE_KEYS,
  profileSeedRows,
  serviceNames,
} from "../../tools/gen-seeds.ts";
import { CONTRACTS_DIR } from "../../tools/paths.ts";

const conventions = readConventions();
const services = serviceNames(
  readFileSync(join(CONTRACTS_DIR, "registries/services.json"), "utf8"),
);

describe("the budget tags of CONVENTIONS L429", () => {
  const parsed = budgetTags(conventions);

  it("reads every placeholder-free tag with its sub-counters", () => {
    expect(parsed.tags.map((t) => t.tag)).toEqual([
      "fb_vendor",
      "ig_vendor",
      "tt_vendor",
      "x_pay_per_use",
      "youtube_data_api",
      "li_vendor_post_search",
      "li_vendor_org_resolver",
      "li_vendor_company_posts",
      "li_vendor_post_comments",
      "tg_telemetrio_search",
      "tg_telemetrio_stats",
      "tg_apify_posts",
      "perplexity_search",
      "mojeek_search",
      "gdelt_doc_api",
      "news_proxy_egress",
      "news_disqus",
    ]);
    const x = parsed.tags.find((t) => t.tag === "x_pay_per_use");
    expect(x?.subCounters).toEqual(["post_reads", "user_reads", "compliance"]);
    expect(x?.zeroPrice).toEqual(["compliance"]);
    expect(parsed.tags.find((t) => t.tag === "youtube_data_api")?.subCounters).toEqual([
      "search",
      "ingest",
      "comments",
      "reserve",
    ]);
  });

  it("marks the vendor tags amber and only those", () => {
    expect(parsed.tags.filter((t) => t.amber).map((t) => t.tag)).toEqual(
      Object.keys(AMBER_TAG_SERVICES),
    );
  });

  it("reads the per-id families, the conditional tag, the counting tags and the shares", () => {
    expect(parsed.families).toEqual([
      "meta_graph_pages",
      "ig_graph",
      "ig_hashtag",
      "tt_display",
      "linkedin_cm",
    ]);
    expect(parsed.conditional).toEqual(["analysis_model_api"]);
    expect(parsed.counting).toEqual(["commoncrawl", "tg_bot_api", "yt_pubsub_hub"]);
    expect(parsed.amberSubCounters).toEqual(["service:<service>", "source:<source_id>"]);
    expect(parsed.shares).toEqual([
      { tag: "mojeek_search", service: "yt-web-search-bridge" },
      { tag: "perplexity_search", service: "yt-web-search-bridge" },
    ]);
  });

  it("fails on a CONVENTIONS without its budget tags line", () => {
    expect(() => budgetTags("# nothing here\n")).toThrow(/Budget tags/);
  });
});

describe("the amber services of CONVENTIONS' service index", () => {
  const amber = amberServices(conventions);

  it("finds the 18 amber services of five platforms", () => {
    expect(Object.keys(amber).sort()).toEqual([
      "facebook",
      "instagram",
      "linkedin",
      "telegram",
      "tiktok",
    ]);
    expect(Object.values(amber).flat()).toHaveLength(18);
  });

  it("every amber service draws on exactly one amber tag of its platform", () => {
    const mapped = Object.entries(AMBER_TAG_SERVICES).flatMap(([tag, list]) =>
      list.map((service) => ({ tag, service })),
    );
    expect(mapped.map((m) => m.service).sort()).toEqual(Object.values(amber).flat().sort());
    const prefixes: Record<string, string> = {
      facebook: "fb",
      instagram: "ig",
      tiktok: "tt",
      linkedin: "li",
      telegram: "tg",
    };
    for (const { tag, service } of mapped) {
      const platform = Object.entries(amber).find(([, list]) => list.includes(service))?.[0] ?? "";
      expect(tag.startsWith(prefixes[platform] ?? "?"), `${service} on ${tag}`).toBe(true);
    }
  });
});

describe("the comment series profiles of CONVENTIONS L405 to L421", () => {
  it("reads the eleven rows, one per F2 comment profile", () => {
    const rows = seriesProfileRows(conventions);
    expect(rows.map((r) => r.routeLabel)).toEqual(Object.keys(PROFILE_KEYS));
  });

  it("turns a series cell into F2 seriesStep labels", () => {
    expect(seriesSteps("+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30")).toEqual({
      steps: ["+1h", "+6h", "+24h", "+3d", "+7d", "+14d", "+21d", "+28d"],
      push: false,
    });
    expect(seriesSteps("+6 h, +24 h, +3 d, +7 d, +30 d").steps).toEqual([
      "+6h",
      "+24h",
      "+3d",
      "+7d",
      "+30d",
    ]);
    expect(
      seriesSteps("push (live); its own daily `reconciliation` check per group (ADR-0012)"),
    ).toEqual({
      steps: [],
      push: true,
    });
    expect(() => seriesSteps("every so often")).toThrow(/no steps/);
  });

  it("names each row's services in the order the row gives them", () => {
    const rows = profileSeedRows(conventions, services);
    const byProfile = Object.fromEntries(rows.map((r) => [r.profile, r]));
    expect(byProfile.x?.commentServices).toEqual(["x-replies-fetcher", "x-full-archive-search"]);
    expect(byProfile.yt?.commentServices).toEqual(["yt-comments-fetcher", "yt-replies-fetcher"]);
    expect(byProfile.x?.steps).toEqual([
      "+1h",
      "+6h",
      "+24h",
      "+3d",
      "+7d",
      "+14d",
      "+21d",
      "+28d",
    ]);
    expect(byProfile.tg_own).toMatchObject({
      steps: [],
      push: true,
      route: "green",
      platform: "telegram",
    });
    expect(byProfile.news).toMatchObject({
      platform: "news",
      commentServices: ["news-comments-fetcher"],
    });
  });
});
