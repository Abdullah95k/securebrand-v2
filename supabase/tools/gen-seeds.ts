// Writes the reference-seed migration from CONVENTIONS (plan T5): the budgets rows of the canonical
// budget tags (L429) with their family rows in budget_config, and comment_series_profiles (L405 to
// L421). The limits follow the plan's Question 6; the drift tests compare the seeded tables with
// CONVENTIONS, read from a live database after every migration.
//
//   node tools/gen-seeds.ts    writes supabase/migrations/<REFERENCE_SEED_FILE>
//
// The drift tests never compare with this file (S15): once merged it stays as it is, and a later
// CONVENTIONS change goes in a new migration.
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import {
  amberServices,
  budgetTags,
  readConventions,
  seriesProfileRows,
  seriesSteps,
} from "./conventions.ts";
import { CONTRACTS_DIR, MIGRATIONS_DIR } from "./paths.ts";

export const REFERENCE_SEED_FILE = "20261026001400_seed_reference.sql";

/** Which amber service draws on which amber tag (the PRDs' budget tags; checked by a unit test). */
export const AMBER_TAG_SERVICES: Record<string, string[]> = {
  fb_vendor: ["fb-keyword-search", "fb-group-posts-poller", "fb-group-comments-fetcher"],
  ig_vendor: ["ig-keyword-search", "ig-comments-fetcher"],
  tt_vendor: [
    "tt-keyword-search",
    "tt-hashtag-feed-poller",
    "tt-user-resolver",
    "tt-profile-videos-poller",
    "tt-video-comments-fetcher",
    "tt-video-stats-refresher",
  ],
  li_vendor_post_search: ["li-post-search"],
  li_vendor_org_resolver: ["li-org-resolver"],
  li_vendor_company_posts: ["li-company-posts-poller"],
  li_vendor_post_comments: ["li-post-comments-fetcher"],
  tg_telemetrio_search: ["tg-message-search"],
  tg_telemetrio_stats: ["tg-channel-resolver"],
  tg_apify_posts: ["tg-channel-posts-poller"],
};

interface Attributes {
  unit: string;
  currency: string | null;
  unitPrice: number | null;
  period: string;
  resetRule: string;
}

const MONTHLY = (
  unit: string,
  currency: string | null = "USD",
  unitPrice: number | null = null,
) => ({
  unit,
  currency,
  unitPrice,
  period: "month",
  resetRule: "calendar_month",
});

/** Units, prices and reset rules per tag, from the CONVENTIONS fact sheets (L222 to L233). */
const ATTRIBUTES: Record<string, Attributes> = {
  fb_vendor: MONTHLY("requests"),
  ig_vendor: MONTHLY("credits"),
  tt_vendor: MONTHLY("requests"),
  li_vendor_post_search: MONTHLY("items"),
  li_vendor_org_resolver: MONTHLY("items"),
  li_vendor_company_posts: MONTHLY("items"),
  li_vendor_post_comments: MONTHLY("items"),
  tg_telemetrio_search: MONTHLY("requests"),
  tg_telemetrio_stats: MONTHLY("requests"),
  tg_apify_posts: MONTHLY("items"),
  perplexity_search: MONTHLY("requests", "USD", 0.005),
  mojeek_search: MONTHLY("queries", "GBP", 0.003),
  news_proxy_egress: MONTHLY("gb"),
  news_disqus: MONTHLY("requests", null),
  commoncrawl: MONTHLY("requests", null, 0),
  gdelt_doc_api: {
    unit: "requests",
    currency: null,
    unitPrice: 0,
    period: "day",
    resetRule: "utc_day",
  },
  tg_bot_api: {
    unit: "requests",
    currency: null,
    unitPrice: 0,
    period: "day",
    resetRule: "utc_day",
  },
  yt_pubsub_hub: {
    unit: "requests",
    currency: null,
    unitPrice: 0,
    period: "day",
    resetRule: "utc_day",
  },
  youtube_data_api: {
    unit: "units",
    currency: null,
    unitPrice: null,
    period: "day",
    resetRule: "provider_daily_reset",
  },
};

const X_SUB_COUNTERS: Record<string, Attributes> = {
  post_reads: {
    unit: "post_reads",
    currency: "USD",
    unitPrice: 0.005,
    period: "billing_cycle",
    resetRule: "billing_cycle",
  },
  user_reads: {
    unit: "user_reads",
    currency: "USD",
    unitPrice: 0.01,
    period: "billing_cycle",
    resetRule: "billing_cycle",
  },
  compliance: {
    unit: "ids",
    currency: "USD",
    unitPrice: 0,
    period: "billing_cycle",
    resetRule: "billing_cycle",
  },
};

/** Free tags whose limit is not closed (Question 6): YouTube's provider quota and GDELT's pacing. */
const OPEN_LIMITS: Record<string, number | null> = { youtube_data_api: 10000, gdelt_doc_api: null };

export interface BudgetRow extends Attributes {
  tag: string;
  subCounter: string;
  limit: number | null;
}

/** The budgets rows the seed holds, from CONVENTIONS and the plan's Question 6. */
export function budgetSeedRows(conventions: string): BudgetRow[] {
  const parsed = budgetTags(conventions);
  const rows: BudgetRow[] = [];
  const closed = (attrs: Attributes, tag: string, subCounter: string, limit: number | null) =>
    rows.push({ tag, subCounter, limit, ...attrs });
  for (const t of parsed.tags) {
    if (t.tag === "x_pay_per_use") {
      // No tag row: nothing above the zero-price compliance sub-counter can close it (S6).
      for (const sub of t.subCounters) {
        const attrs = X_SUB_COUNTERS[sub];
        if (attrs === undefined) throw new Error(`no attributes for x_pay_per_use/${sub}`);
        closed(attrs, t.tag, sub, t.zeroPrice.includes(sub) ? null : 0);
      }
      continue;
    }
    const attrs = ATTRIBUTES[t.tag];
    if (attrs === undefined) throw new Error(`no attributes for budget tag ${t.tag}`);
    const tagLimit = t.tag in OPEN_LIMITS ? (OPEN_LIMITS[t.tag] ?? null) : 0;
    closed(attrs, t.tag, "", tagLimit);
    // A bucket has no size until the pilot sets one; the tag's row still gates.
    for (const sub of t.subCounters) closed(attrs, t.tag, sub, null);
    if (t.amber) {
      const services = AMBER_TAG_SERVICES[t.tag];
      if (services === undefined) throw new Error(`no services for amber tag ${t.tag}`);
      for (const service of services) closed(attrs, t.tag, `service:${service}`, 0);
    }
  }
  for (const share of parsed.shares) {
    const attrs = ATTRIBUTES[share.tag];
    if (attrs === undefined) throw new Error(`no attributes for shared tag ${share.tag}`);
    closed(attrs, share.tag, `service:${share.service}`, 0);
  }
  for (const tag of parsed.counting) {
    const attrs = ATTRIBUTES[tag];
    if (attrs === undefined) throw new Error(`no attributes for counting tag ${tag}`);
    closed(attrs, tag, "", null);
  }
  return rows;
}

export interface ConfigRow {
  tag: string;
  scope: string;
  setting: string;
  value: unknown;
  reason: string;
}

/** Templates of the per-id families (ADR-0042; CONVENTIONS L222 to L233). */
const FAMILY_TEMPLATES: Record<string, Record<string, unknown>> = {
  meta_graph_pages: {
    unit: "calls",
    period: "rolling_24h",
    reset_rule: "rolling_24h",
    limit: null,
  },
  ig_graph: { unit: "calls", period: "rolling_24h", reset_rule: "rolling_24h", limit: null },
  ig_hashtag: { unit: "hashtags", period: "rolling_7d", reset_rule: "rolling_7d", limit: 30 },
  tt_display: { unit: "calls", period: "day", reset_rule: "utc_day", limit: null },
  linkedin_cm: { unit: "calls", period: "day", reset_rule: "utc_day", limit: null },
};

/** The budget_config rows the seed holds. */
export function budgetConfigSeedRows(conventions: string): ConfigRow[] {
  const parsed = budgetTags(conventions);
  const facts = "CONVENTIONS v1.1 L222 to L233 (budget facts)";
  const rows: ConfigRow[] = [
    {
      tag: "x_pay_per_use",
      scope: "",
      setting: "provider_cap_post_reads",
      value: { value: 3000000, period: "billing_cycle" },
      reason: facts,
    },
    {
      tag: "x_pay_per_use",
      scope: "",
      setting: "provider_stream_rules",
      value: { value: 1000 },
      reason: facts,
    },
    {
      tag: "youtube_data_api",
      scope: "",
      setting: "provider_daily_units",
      value: { value: 10000 },
      reason: facts,
    },
    {
      tag: "youtube_data_api",
      scope: "",
      setting: "search_list_units",
      value: { value: 100 },
      reason: facts,
    },
    {
      tag: "ig_hashtag",
      scope: "",
      setting: "provider_unique_hashtags_7d",
      value: { value: 30 },
      reason: facts,
    },
    {
      tag: "ig_graph",
      scope: "",
      setting: "comments_per_query",
      value: { value: 50 },
      reason: facts,
    },
    {
      tag: "meta_graph_pages",
      scope: "",
      setting: "provider_calls_per_engaged_user_24h",
      value: { value: 4800 },
      reason: facts,
    },
    {
      tag: "gdelt_doc_api",
      scope: "",
      setting: "min_interval_seconds",
      value: { value: 5 },
      reason: facts,
    },
  ];
  for (const family of parsed.families) {
    const template = FAMILY_TEMPLATES[family];
    if (template === undefined) throw new Error(`no template for budget family ${family}`);
    rows.push({
      tag: family,
      scope: "family",
      setting: "template",
      value: template,
      reason: "ADR-0042: quota-governor creates the tag's row on its first request",
    });
  }
  const amberFamily = "ADR-0042 L30: quota-governor creates the sub-counter on its first request";
  for (const t of parsed.tags.filter((tag) => tag.amber)) {
    rows.push({
      tag: t.tag,
      scope: "family",
      setting: "service_sub_counter",
      value: { limit: 0 },
      reason: amberFamily,
    });
    rows.push({
      tag: t.tag,
      scope: "family",
      setting: "source_sub_counter",
      value: { limit: null },
      reason: amberFamily,
    });
  }
  return rows;
}

/** The F2 service names, from the contracts' service index. */
export function serviceNames(servicesJson: string): string[] {
  const registry = JSON.parse(servicesJson) as {
    platform_groups: Record<string, string[]>;
    shared_groups: Record<string, string[]>;
  };
  return [
    ...Object.values(registry.platform_groups).flat(),
    ...Object.values(registry.shared_groups).flat(),
  ];
}

/** CONVENTIONS' route labels as F2 COMMENT_PROFILES keys. */
export const PROFILE_KEYS: Record<string, string> = {
  "Facebook Pages, green": "fb_page",
  "Facebook groups, amber": "fb_group",
  "Instagram client media, green": "ig_own",
  "Instagram other media, amber": "ig_other",
  "TikTok, amber": "tt",
  "X, green": "x",
  "YouTube, green": "yt",
  "LinkedIn client posts, green": "li_own",
  "LinkedIn other posts, amber": "li_other",
  "Telegram own channels, green": "tg_own",
  "News (Disqus sites), green": "news",
};

const PLATFORM_WORDS: Record<string, string> = {
  Facebook: "facebook",
  Instagram: "instagram",
  TikTok: "tiktok",
  X: "x",
  YouTube: "youtube",
  LinkedIn: "linkedin",
  Telegram: "telegram",
  News: "news",
};

export interface ProfileRow {
  profile: string;
  routeLabel: string;
  platform: string;
  route: string;
  commentServices: string[];
  seriesText: string;
  steps: string[];
  push: boolean;
  repliesText: string;
}

/** The comment_series_profiles rows the seed holds, from CONVENTIONS L405 to L421. */
export function profileSeedRows(conventions: string, services: string[]): ProfileRow[] {
  return seriesProfileRows(conventions).map((row) => {
    const profile = PROFILE_KEYS[row.routeLabel];
    if (profile === undefined) throw new Error(`no profile key for the route ${row.routeLabel}`);
    const platform = PLATFORM_WORDS[row.routeLabel.split(/[ ,]/)[0] ?? ""];
    if (platform === undefined) throw new Error(`no platform for the route ${row.routeLabel}`);
    const route = /, (green|amber)$/.exec(row.routeLabel)?.[1];
    if (route === undefined) throw new Error(`no route in ${row.routeLabel}`);
    const commentServices = services
      .map((name) => ({
        name,
        at: row.serviceText.search(new RegExp(`(?<![a-z0-9-])${name}(?![a-z0-9-])`)),
      }))
      .filter((s) => s.at >= 0)
      .sort((a, b) => a.at - b.at)
      .map((s) => s.name);
    if (commentServices.length === 0) throw new Error(`no service named in ${row.serviceText}`);
    const { steps, push } = seriesSteps(row.seriesText);
    return {
      profile,
      routeLabel: row.routeLabel,
      platform,
      route,
      commentServices,
      seriesText: row.seriesText,
      steps,
      push,
      repliesText: row.repliesText,
    };
  });
}

const literal = (value: string | null): string =>
  value === null ? "null" : `'${value.replaceAll("'", "''")}'`;
const number = (value: number | null): string => (value === null ? "null" : String(value));
const textArray = (values: string[]): string =>
  `array[${values.map((v) => literal(v)).join(", ")}]::text[]`;

/** The SQL of the reference-seed migration. */
export function referenceSeedSql(conventions: string, services: string[]): string {
  const budgets = budgetSeedRows(conventions)
    .map(
      (r) =>
        `  (${literal(r.tag)}, ${literal(r.subCounter)}, '1970-01-01 00:00:00+00', ${literal(r.unit)}, ` +
        `${literal(r.currency)}, ${number(r.unitPrice)}, ${literal(r.period)}, ${literal(r.resetRule)}, ` +
        `${number(r.limit)})`,
    )
    .join(",\n");
  const config = budgetConfigSeedRows(conventions)
    .map(
      (r) =>
        `  (${literal(r.tag)}, ${literal(r.scope)}, ${literal(r.setting)}, ` +
        `${literal(JSON.stringify(r.value))}::jsonb, 'F3 seed', ${literal(r.reason)})`,
    )
    .join(",\n");
  const profiles = profileSeedRows(conventions, services)
    .map(
      (r) =>
        `  (${literal(r.profile)}, ${literal(r.routeLabel)}, ${literal(r.platform)}, ${literal(r.route)}, ` +
        `${textArray(r.commentServices)}, ${literal(r.seriesText)}, ${textArray(r.steps)}, ${r.push}, ` +
        `${literal(r.repliesText)})`,
    )
    .join(",\n");
  return `-- F3 · reference seeds generated from CONVENTIONS v1.1 by supabase/tools/gen-seeds.ts (plan T5):
-- the budgets rows of the canonical budget tags (L429) and their budget_config rows, with the limits
-- of the plan's Question 6, and the comment series profiles (L405 to L421). Do not edit by hand: a
-- CONVENTIONS change lands as a new migration, and the drift tests compare the seeded tables with
-- CONVENTIONS. ON CONFLICT DO NOTHING keeps a value the governor or ops changed (plan T4).

insert into public.budgets (budget_tag, sub_counter, period_start, unit, currency, unit_price,
    period, reset_rule, "limit")
values
${budgets}
on conflict do nothing;

insert into public.budget_config (budget_tag, scope, setting, value, changed_by, reason)
values
${config}
on conflict do nothing;

insert into public.comment_series_profiles (profile, route_label, platform, route, comment_services,
    series_text, steps, push, replies_text)
values
${profiles}
on conflict do nothing;
`;
}

function main(): void {
  const conventions = readConventions();
  const services = serviceNames(readFileSync(join(CONTRACTS_DIR, "registries/services.json"), "utf8"));
  writeFileSync(join(MIGRATIONS_DIR, REFERENCE_SEED_FILE), referenceSeedSql(conventions, services));
  process.stdout.write(`wrote supabase/migrations/${REFERENCE_SEED_FILE}\n`);
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) main();
