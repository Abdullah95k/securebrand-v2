// A13: every closed list in a CHECK equals F2's list, read from the live catalogue and from
// packages/contracts itself (vocabulary.json, vendors.json), so a change in F2's lists that the
// migrations do not follow fails here.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { CONTRACTS_DIR } from "../../tools/paths.ts";
import { withClient } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const url = testDatabaseUrl();
const V = JSON.parse(
  readFileSync(join(CONTRACTS_DIR, "schemas/vocabulary.json"), "utf8"),
) as Record<string, (string | number)[]>;
const vendorsJson = JSON.parse(
  readFileSync(join(CONTRACTS_DIR, "registries/vendors.json"), "utf8"),
) as {
  amber: string[];
  green: string[];
};
const VENDORS = [...vendorsJson.amber, ...vendorsJson.green];
const list = (name: string): string[] => {
  const values = V[name];
  if (values === undefined) throw new Error(`vocabulary.json has no ${name}`);
  return values.map(String);
};

/** Each column CHECK and the F2 list (or lists) it holds. */
const CHECKED: [table: string, column: string, expected: string[]][] = [
  ["clients", "client_type", list("CLIENT_TYPES")],
  ["sources", "platform", list("PLATFORMS")],
  ["sources", "source_type", list("SOURCE_TYPES")],
  ["sources", "route", list("ROUTES")],
  ["sources", "vendor", VENDORS],
  ["sources", "tier", list("TIERS")],
  ["sources", "lifecycle", list("LIFECYCLES")],
  ["sources", "retention_class", list("RETENTION_CLASSES")],
  ["sources", "added_by", list("ADDED_BY")],
  ["sources", "health", list("HEALTHS")],
  [
    "sources",
    "health_reason",
    [...list("SOURCE_HEALTH_REASONS"), ...list("FLAG_REASONS"), ...list("ROUTE_HEALTH_REASONS")],
  ],
  ["sources", "retired_reason", list("RETIRE_REASONS")],
  ["registry_audit", "decision", list("DECISION_TYPES")],
  ["registry_audit", "reason", list("REGISTRY_REASONS")],
  ["decisions", "decision", list("DECISION_TYPES")],
  ["decisions", "reason", list("REGISTRY_REASONS")],
  ["poster_profiles", "platform", list("PLATFORMS")],
  // F2's three, plus poster-resolver's in-flight states (C5).
  ["poster_profiles", "status", [...list("PROFILE_STATUSES"), "resolving", "pending"]],
  [
    "poster_profiles",
    "reason",
    [...list("PROFILE_REVIEW_REASONS"), ...list("PROFILE_UNRESOLVABLE_REASONS")],
  ],
  ["poster_profiles", "account_type", list("ACCOUNT_TYPES")],
  ["poster_profiles", "retention_class", list("RETENTION_CLASSES")],
  ["credentials", "platform", list("PLATFORMS")],
  ["canary_targets", "platform", list("PLATFORMS")],
  ["canary_targets", "route", list("ROUTES")],
  ["canary_targets", "vendor", VENDORS],
  ["canary_targets", "source_type", list("SOURCE_TYPES")],
  ["canary_targets", "alternate_route", list("ROUTES")],
  ["canary_targets", "alternate_vendor", VENDORS],
  ["canary_audit", "platform", list("PLATFORMS")],
  ["canary_audit", "route", list("ROUTES")],
  ["canary_audit", "vendor", VENDORS],
  ["canary_audit", "health", list("HEALTHS")],
  ["canary_audit", "reason", [...list("ROUTE_HEALTH_REASONS"), ...list("FLAG_REASONS")]],
  ["keywords", "platforms", list("PLATFORMS")],
  ["comment_series", "profile", list("COMMENT_PROFILES")],
  ["comment_series", "route", list("ROUTES")],
  ["comment_series_profiles", "profile", list("COMMENT_PROFILES")],
  ["comment_series_profiles", "platform", list("PLATFORMS")],
  ["comment_series_profiles", "route", list("ROUTES")],
  ["backfill_runs", "reason", list("BACKFILL_REASONS")],
  ["backfill_runs", "capped_reason", list("CAPPED_REASONS")],
  ["news_sites", "access_mode", list("ACCESS_MODES")],
  ["crawl_policies", "status", list("CRAWL_STATUSES")],
  ["crawl_policies", "reason", list("CRAWL_REASONS")],
  ["crawl_policies", "access_mode", list("ACCESS_MODES")],
  ["crawl_policies", "robots_status", list("ROBOTS_STATUSES")],
  ["news_urls", "found_via", list("FOUND_VIA")],
  ["news_story_members", "matched_by", list("DEDUP_MATCHED_BY")],
  ["news_story_members", "language", list("LANG_LABELS")],
  ["retention_classes", "class", list("RETENTION_CLASSES")],
  ["retention_classes", "mode", [...list("DELETION_MODES"), "none"]],
  ["retention_classes", "vendor", ["", ...VENDORS]],
  ["retention_audit", "class", list("RETENTION_CLASSES")],
  ["deletion_propagations", "reason", list("DELETION_REASONS")],
  ["deletion_propagations", "scope", list("DELETION_SCOPES")],
  ["deletion_propagations", "mode", list("DELETION_MODES")],
  ["deletion_propagations", "retention_class", list("RETENTION_CLASSES")],
  ["kb_entities", "type", list("ENTITY_TYPES")],
  ["alert_rules", "type", list("ALERT_RULE_TYPES")],
  ["alert_rules", "severity", list("ALERT_SEVERITIES")],
  ["alert_rules", "platform", list("PLATFORMS")],
];

/** The literals of the CHECKs on `column` alone, as Postgres prints them. */
async function checkLiterals(table: string, column: string): Promise<string[]> {
  return withClient(url, async (c) => {
    const r = await c.query<{ def: string }>(
      `select pg_get_constraintdef(con.oid) as def from pg_constraint con
       join pg_attribute a on a.attrelid = con.conrelid and a.attnum = any (con.conkey)
       where con.conrelid = $1::regclass and con.contype = 'c' and a.attname = $2
         and array_length(con.conkey, 1) = 1`,
      [`public.${table}`, column],
    );
    const literals = new Set<string>();
    for (const { def } of r.rows) {
      for (const m of def.matchAll(/'((?:[^']|'')*)'::text/g))
        literals.add((m[1] ?? "").replaceAll("''", "'"));
      for (const m of def.matchAll(/ARRAY\[([0-9, ]+)\]/g))
        for (const n of (m[1] ?? "").split(",")) literals.add(n.trim());
    }
    return [...literals].sort();
  });
}

describe("closed lists against F2's vocabulary", () => {
  it.each(CHECKED)(
    "the CHECK list of %s.%s equals the contracts vocabulary",
    async (table, column, expected) => {
      expect(await checkLiterals(table, column)).toEqual([...new Set(expected)].sort());
    },
  );

  it("the flagged vendors a client may accept are vendors of the contracts", async () => {
    const accepted = await checkLiterals("clients", "accepted_flagged_vendors");
    expect(accepted.length).toBeGreaterThan(0);
    for (const vendor of accepted) expect(VENDORS).toContain(vendor);
  });

  it("the government alert types of the trigger are F2's GOVERNMENT_ALERT_RULE_TYPES", async () => {
    const source = await withClient(
      url,
      async (c) =>
        (
          await c.query<{ src: string }>(
            "select prosrc as src from pg_proc where oid = 'public.alert_rules_government_type()'::regprocedure",
          )
        ).rows[0]?.src ?? "",
    );
    const first = /not in \(([^)]*)\)/.exec(source)?.[1] ?? "";
    const literals = [...first.matchAll(/'([a-z_]+)'/g)].map((m) => m[1] ?? "").sort();
    expect(literals).toEqual(list("GOVERNMENT_ALERT_RULE_TYPES").sort());
  });
});
