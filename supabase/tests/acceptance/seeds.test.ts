// A15 to A18, A20, A21, A34: the reference seeds the migrations insert, read from the fresh test
// database after every migration has run.
import { describe, expect, it } from "vitest";
import { asRole, inRollback } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const url = testDatabaseUrl();

const rows = <R extends Record<string, unknown>>(sql: string, params: unknown[] = []) =>
  inRollback(url, (s) => s.rows<R>(sql, params));

describe("permitted_uses (A15)", () => {
  it("permitted_uses holds exactly the four rows ADR-0068 lists", async () => {
    const seeded = await rows(
      "select subject_kind, subject, use, allowed, clause, set_by from public.permitted_uses order by subject, use",
    );
    const youtube =
      "YouTube's terms forbid downloading video without YouTube's prior written permission (and the rights holders', where they apply)";
    const choice = "The user's answer of 9 Oct 2026: 'Start as not allowed'";
    const row = (subject: string, use: string, clause: string) => ({
      subject_kind: "platform",
      subject,
      use,
      allowed: false,
      clause,
      set_by: "F3 seed (ADR-0068)",
    });
    expect(seeded).toEqual([
      row("facebook", "train", choice),
      row("instagram", "train", choice),
      row("youtube", "download_audio", youtube),
      row("youtube", "download_video", youtube),
    ]);
  });

  it("use_permitted returns true for a subject with no row, and false for a seeded one", async () => {
    const answers = await asRole(url, "service_role", (s) =>
      s.rows<{ tiktok: boolean; disqus: boolean; host: boolean; youtube: boolean }>(
        `select public.use_permitted('platform', 'tiktok', 'train') as tiktok,
                public.use_permitted('platform', 'disqus', 'download_image') as disqus,
                public.use_permitted('news_host', 'example-daily.iq', 'train') as host,
                public.use_permitted('platform', 'youtube', 'download_video') as youtube`,
      ),
    );
    expect(answers[0]).toEqual({ tiktok: true, disqus: true, host: true, youtube: false });
  });

  it("use_permitted raises for a mistyped platform, an unknown kind and an unknown use", async () => {
    const codes = await asRole(url, "service_role", async (s) => [
      await s.failure("select public.use_permitted('platform', 'YouTube', 'download_video')"),
      await s.failure("select public.use_permitted('platfrom', 'youtube', 'download_video')"),
      await s.failure("select public.use_permitted('platform', 'youtube', 'download_videos')"),
      await s.failure("select public.use_permitted('vendor', 'brightdata', 'train')"),
      await s.failure("select public.use_permitted('news_host', 'Example.IQ', 'train')"),
    ]);
    expect(codes).toEqual(["22023", "22023", "22023", "22023", "22023"]);
  });
});

describe("retention_classes (A16)", () => {
  const ten = (cls: string) => [
    [cls, "text", "created_at", "10 years", "purge_text", "deletion-propagator"],
    [cls, "row", "created_at", "10 years", "purge_derived", "deletion-propagator"],
    [cls, "raw", "created_at", "10 years", "purge_derived", "deletion-propagator"],
    [cls, "derived", "created_at", "10 years", "purge_derived", "deletion-propagator"],
  ];
  const fetched = (cls: string, clock: string) => [
    [cls, "text", "fetched_at", clock, "purge_text", "deletion-propagator"],
    [cls, "row", "fetched_at", clock, "purge_derived", "deletion-propagator"],
    [cls, "raw", "fetched_at", clock, "purge_derived", "deletion-propagator"],
    [cls, "derived", "fetched_at", clock, "purge_derived", "deletion-propagator"],
  ];
  // The plan's clock table (T20; C3, C8, S5): one row per class and part, 37 in all.
  const PLAN = [
    ...ten("meta_on_request"),
    ...ten("vendor_agreed"),
    ...ten("x_24h_sync"),
    ...ten("telegram_bot"),
    ...ten("tiktok_display"),
    ...ten("news_excerpt"),
    ["news_excerpt", "cache", "fetched_at", "7 days", "purge_text", "deletion-propagator"],
    ...fetched("linkedin_48h", "48 hours"),
    ...fetched("linkedin_org", "42 days"),
    ["youtube_30d_text", "text", "fetched_at", "30 days", "purge_text", "yt-text-purger"],
    ["youtube_30d_text", "row", "created_at", "36 months", "purge_derived", "yt-text-purger"],
    ["youtube_30d_text", "raw", "created_at", "36 months", "purge_derived", "yt-text-purger"],
    ["youtube_30d_text", "derived", "created_at", "36 months", "purge_derived", "yt-text-purger"],
  ];

  it("retention_classes equals the plan's clock table, row for row", async () => {
    expect(PLAN).toHaveLength(37);
    const seeded = await rows<{ row: string[] }>(
      `select array[class, part, anchor, clock::text, mode, executor] as row
       from public.retention_classes where vendor = '' order by class, part`,
    );
    // The plan's clocks, as Postgres prints them.
    const expected = await rows<{ row: string[] }>(
      `select array[c, p, a, k::interval::text, m, e] as row
       from unnest($1::text[], $2::text[], $3::text[], $4::text[], $5::text[], $6::text[])
         as t(c, p, a, k, m, e)
       order by c, p`,
      [0, 1, 2, 3, 4, 5].map((i) => PLAN.map((r) => r[i])),
    );
    expect(seeded.map((r) => r.row)).toEqual(expected.map((r) => r.row));
    const all = await rows<{ n: number }>(
      "select count(*)::int as n from public.retention_classes",
    );
    expect(all[0]?.n).toBe(37);
  });

  it("no clock row deletes with a recompute, and tiktok_display has no revocation row", async () => {
    const found = await rows<{ deletes: number; events: number }>(
      `select count(*) filter (where mode = 'delete')::int as deletes,
              count(*) filter (where anchor = 'event')::int as events
       from public.retention_classes`,
    );
    expect(found[0]).toEqual({ deletes: 0, events: 0 });
  });

  it("retention_ttls gives store-writer each class's content and row clocks", async () => {
    const ttl = await rows<{ content: string; row: string }>(
      `select content_ttl::text as content, row_ttl::text as row from public.retention_ttls
       where class = 'youtube_30d_text' and vendor = ''`,
    );
    expect(ttl).toEqual([{ content: "30 days", row: "3 years" }]);
  });
});

describe("feature_flags (A17)", () => {
  it("feature_flags holds the seeded flags and the unset threshold", async () => {
    const flags = await rows<{ name: string; scope: string; value: string | null }>(
      "select name, scope, value from public.feature_flags order by name, scope",
    );
    expect(flags).toEqual([
      { name: "FB_VENDOR_ROUTE", scope: "", value: "off" },
      { name: "FB_VENDOR_ROUTE", scope: "fb-keyword-search", value: "off" },
      { name: "IG_VENDOR_ROUTE", scope: "", value: "off" },
      { name: "LI_VENDOR_ROUTE", scope: "", value: "off" },
      { name: "PUBLIC_ACCOUNT_FOLLOWER_THRESHOLD", scope: "", value: null },
      { name: "TG_POSTS_ACTOR", scope: "", value: "off" },
      { name: "TG_VENDOR_ROUTE", scope: "", value: "off" },
      { name: "TT_VENDOR_ROUTE", scope: "", value: "off" },
      { name: "X_PLAN", scope: "", value: "pay_per_use" },
    ]);
  });
});

describe("budgets (A18)", () => {
  it("budgets holds no tag with a placeholder or a wildcard, and no analysis_model_api", async () => {
    const bad = await rows<{ budget_tag: string }>(
      `select budget_tag from public.budgets
       where budget_tag ~ '[*<>]' or sub_counter ~ '[*<>]' or budget_tag like 'analysis_model_api%'
         or budget_tag like '%:%'`,
    );
    expect(bad).toEqual([]);
  });

  it("compliance and the counting tags are never closed", async () => {
    const open = await rows<{ tag: string; limit: string | null }>(
      `select budget_tag || '/' || sub_counter as tag, "limit"::text as limit from public.budgets
       where (budget_tag, sub_counter) in (('x_pay_per_use', 'compliance'), ('commoncrawl', ''),
         ('tg_bot_api', ''), ('yt_pubsub_hub', '')) order by 1`,
    );
    expect(open).toEqual([
      { tag: "commoncrawl/", limit: null },
      { tag: "tg_bot_api/", limit: null },
      { tag: "x_pay_per_use/compliance", limit: null },
      { tag: "yt_pubsub_hub/", limit: null },
    ]);
    const xTag = await rows(
      "select 1 from public.budgets where budget_tag = 'x_pay_per_use' and sub_counter = ''",
    );
    expect(xTag).toEqual([]);
  });

  it("every paid tag starts closed at limit 0, and YouTube carries its 10,000 units a day", async () => {
    const paid = await rows<{ tag: string }>(
      `select budget_tag || '/' || sub_counter as tag from public.budgets
       where budget_tag in ('fb_vendor', 'ig_vendor', 'tt_vendor', 'li_vendor_post_search',
         'li_vendor_org_resolver', 'li_vendor_company_posts', 'li_vendor_post_comments',
         'tg_telemetrio_search', 'tg_telemetrio_stats', 'tg_apify_posts', 'perplexity_search',
         'mojeek_search', 'news_proxy_egress', 'news_disqus')
         or (budget_tag, sub_counter) in (('x_pay_per_use', 'post_reads'), ('x_pay_per_use', 'user_reads'))
       group by 1 having bool_or("limit" is distinct from 0)`,
    );
    expect(paid).toEqual([]);
    const youtube = await rows<{ sub_counter: string; limit: string | null; reset_rule: string }>(
      `select sub_counter, "limit"::text as limit, reset_rule from public.budgets
       where budget_tag = 'youtube_data_api' order by sub_counter`,
    );
    expect(youtube).toEqual([
      { sub_counter: "", limit: "10000", reset_rule: "provider_daily_reset" },
      { sub_counter: "comments", limit: null, reset_rule: "provider_daily_reset" },
      { sub_counter: "ingest", limit: null, reset_rule: "provider_daily_reset" },
      { sub_counter: "reserve", limit: null, reset_rule: "provider_daily_reset" },
      { sub_counter: "search", limit: null, reset_rule: "provider_daily_reset" },
    ]);
  });

  it("every amber service has its service sub-counter, and the bridge its two shares", async () => {
    const services = await rows<{ tag: string; subs: string[] }>(
      `select budget_tag as tag, array_agg(sub_counter order by sub_counter) as subs
       from public.budgets where sub_counter like 'service:%' group by 1 order by 1`,
    );
    expect(services).toEqual([
      {
        tag: "fb_vendor",
        subs: [
          "service:fb-group-comments-fetcher",
          "service:fb-group-posts-poller",
          "service:fb-keyword-search",
        ],
      },
      { tag: "ig_vendor", subs: ["service:ig-comments-fetcher", "service:ig-keyword-search"] },
      { tag: "li_vendor_company_posts", subs: ["service:li-company-posts-poller"] },
      { tag: "li_vendor_org_resolver", subs: ["service:li-org-resolver"] },
      { tag: "li_vendor_post_comments", subs: ["service:li-post-comments-fetcher"] },
      { tag: "li_vendor_post_search", subs: ["service:li-post-search"] },
      { tag: "mojeek_search", subs: ["service:yt-web-search-bridge"] },
      { tag: "perplexity_search", subs: ["service:yt-web-search-bridge"] },
      { tag: "tg_apify_posts", subs: ["service:tg-channel-posts-poller"] },
      { tag: "tg_telemetrio_search", subs: ["service:tg-message-search"] },
      { tag: "tg_telemetrio_stats", subs: ["service:tg-channel-resolver"] },
      {
        tag: "tt_vendor",
        subs: [
          "service:tt-hashtag-feed-poller",
          "service:tt-keyword-search",
          "service:tt-profile-videos-poller",
          "service:tt-user-resolver",
          "service:tt-video-comments-fetcher",
          "service:tt-video-stats-refresher",
        ],
      },
    ]);
  });

  it("budget_config holds the sub-counter and per-id family rows", async () => {
    const families = await rows<{ budget_tag: string; setting: string }>(
      `select budget_tag, setting from public.budget_config where scope = 'family' order by 1, 2`,
    );
    const amber = [
      "fb_vendor",
      "ig_vendor",
      "li_vendor_company_posts",
      "li_vendor_org_resolver",
      "li_vendor_post_comments",
      "li_vendor_post_search",
      "tg_apify_posts",
      "tg_telemetrio_search",
      "tg_telemetrio_stats",
      "tt_vendor",
    ];
    const expected = [
      ...amber.flatMap((tag) => [
        { budget_tag: tag, setting: "source_sub_counter" },
        { budget_tag: tag, setting: "service_sub_counter" },
      ]),
      ...["ig_graph", "ig_hashtag", "linkedin_cm", "meta_graph_pages", "tt_display"].map((tag) => ({
        budget_tag: tag,
        setting: "template",
      })),
    ].sort((a, b) =>
      a.budget_tag === b.budget_tag
        ? a.setting.localeCompare(b.setting)
        : a.budget_tag.localeCompare(b.budget_tag),
    );
    expect(families).toEqual(expected);
    const shares = await rows<{ value: unknown }>(
      `select value from public.budget_config where budget_tag = 'tt_vendor' and scope = 'family'
       and setting = 'service_sub_counter'`,
    );
    expect(shares[0]?.value).toMatchObject({ limit: 0 });
  });

  it("the provider limits CONVENTIONS states are in budget_config", async () => {
    const limits = await rows<{ key: string; value: unknown }>(
      `select budget_tag || '/' || scope || '/' || setting as key, value from public.budget_config
       where scope <> 'family' order by 1`,
    );
    const byKey = Object.fromEntries(limits.map((r) => [r.key, r.value]));
    expect(byKey["x_pay_per_use//provider_cap_post_reads"]).toMatchObject({ value: 3000000 });
    expect(byKey["x_pay_per_use//provider_stream_rules"]).toMatchObject({ value: 1000 });
    expect(byKey["youtube_data_api//provider_daily_units"]).toMatchObject({ value: 10000 });
    expect(byKey["youtube_data_api//search_list_units"]).toMatchObject({ value: 100 });
    expect(byKey["gdelt_doc_api//min_interval_seconds"]).toMatchObject({ value: 5 });
  });
});

describe("canary_targets (A20)", () => {
  it("canary_targets declares exactly the seeded alternates, all active", async () => {
    const declared = await rows(
      `select platform, route, source_type, service, alternate_route, alternate_vendor, flag_name,
              scope, active
       from public.canary_targets order by platform`,
    );
    expect(declared).toEqual([
      {
        platform: "instagram",
        route: "green",
        source_type: "hashtag",
        service: "ig-keyword-search",
        alternate_route: "amber",
        alternate_vendor: "sociavault",
        flag_name: "IG_VENDOR_ROUTE",
        scope: "non_government",
        active: true,
      },
      {
        platform: "telegram",
        route: "green",
        source_type: "channel",
        service: "tg-channel-posts-poller",
        alternate_route: "amber",
        alternate_vendor: null,
        flag_name: "TG_POSTS_ACTOR",
        scope: null,
        active: true,
      },
      {
        platform: "tiktok",
        route: "green",
        source_type: "account",
        service: "tt-profile-videos-poller",
        alternate_route: "amber",
        alternate_vendor: null,
        flag_name: "TT_VENDOR_ROUTE",
        scope: null,
        active: true,
      },
    ]);
  });
});

describe("credentials (A21)", () => {
  it("credentials vendor rows have their fallback order and a null vault reference", async () => {
    const vendors = await rows<{ role: string; order: string[] }>(
      `select role, array_agg(owner_name order by fallback_rank) as order from public.credentials
       where owner_kind = 'vendor' group by role order by role`,
    );
    expect(vendors).toEqual([
      { role: "facebook_groups", order: ["scrapecreators", "sociavault"] },
      { role: "facebook_keyword_search", order: ["sociavault"] },
      { role: "instagram", order: ["sociavault"] },
      { role: "linkedin", order: ["harvestapi"] },
      { role: "telegram_posts", order: ["tugelbay", "sovereigntaylor"] },
      { role: "telegram_search_stats", order: ["telemetrio"] },
      { role: "tiktok", order: ["ensembledata", "tikhub"] },
    ]);
    const keyed = await rows("select 1 from public.credentials where vault_ref is not null");
    expect(keyed).toEqual([]);
  });

  it("an unverified vendor's rows are degraded with owner_not_verified", async () => {
    const states = await rows<{ owner_name: string; states: string[] }>(
      `select owner_name, array_agg(distinct state || '/' || coalesce(reason, '')) as states
       from public.credentials where owner_kind = 'vendor' group by 1 order by 1`,
    );
    const degraded = ["degraded/owner_not_verified"];
    expect(states).toEqual([
      { owner_name: "ensembledata", states: ["ok/"] },
      { owner_name: "harvestapi", states: degraded },
      { owner_name: "scrapecreators", states: degraded },
      { owner_name: "sociavault", states: degraded },
      { owner_name: "sovereigntaylor", states: degraded },
      { owner_name: "telemetrio", states: ["ok/"] },
      { owner_name: "tikhub", states: degraded },
      { owner_name: "tugelbay", states: degraded },
    ]);
  });
});

describe("iq_reference (A34)", () => {
  it("iq_reference holds the 19 governorates and their capitals, in three spellings", async () => {
    const counts = await rows<{ kind: string; n: number }>(
      "select kind, count(*)::int as n from public.iq_reference group by 1 order by 1",
    );
    expect(counts).toEqual([
      { kind: "city", n: 19 },
      { kind: "governorate", n: 19 },
    ]);
    const orphans = await rows(
      `select c.name_latin from public.iq_reference c
       left join public.iq_reference g on g.ref_id = c.parent_id and g.kind = 'governorate'
       where c.kind = 'city' and g.ref_id is null`,
    );
    expect(orphans).toEqual([]);
    const capitals = await rows<{ n: number }>(
      `select count(distinct parent_id)::int as n from public.iq_reference where kind = 'city'`,
    );
    expect(capitals[0]?.n).toBe(19);
    const named = await rows<{ governorate: string; capital: string }>(
      `select g.name_latin as governorate, c.name_latin as capital from public.iq_reference c
       join public.iq_reference g on g.ref_id = c.parent_id
       where g.name_latin in ('Baghdad', 'Erbil', 'Halabja', 'Nineveh') order by 1`,
    );
    expect(named).toEqual([
      { governorate: "Baghdad", capital: "Baghdad" },
      { governorate: "Erbil", capital: "Erbil" },
      { governorate: "Halabja", capital: "Halabja" },
      { governorate: "Nineveh", capital: "Mosul" },
    ]);
  });
});
