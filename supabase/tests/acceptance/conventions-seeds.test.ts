// A18 and A19 (plan T5, S15): the seeded tables, read from a live database after every migration,
// equal what CONVENTIONS lists today, so a CONVENTIONS change without its new migration fails here.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { readConventions } from "../../tools/conventions.ts";
import {
  budgetConfigSeedRows,
  budgetSeedRows,
  profileSeedRows,
  serviceNames,
} from "../../tools/gen-seeds.ts";
import { CONTRACTS_DIR } from "../../tools/paths.ts";
import { inRollback } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const url = testDatabaseUrl();
const conventions = readConventions();
const services = serviceNames(
  readFileSync(join(CONTRACTS_DIR, "registries/services.json"), "utf8"),
);

describe("seeds generated from CONVENTIONS", () => {
  it("the budget seed equals the tags CONVENTIONS lists", async () => {
    const seeded = await inRollback(url, (s) =>
      s.rows<{ key: string; limit: string | null }>(
        `select budget_tag || '/' || sub_counter as key, "limit"::text as limit from public.budgets
         where period_start = '1970-01-01 00:00:00+00' order by 1`,
      ),
    );
    const expected = budgetSeedRows(conventions)
      .map((r) => ({
        key: `${r.tag}/${r.subCounter}`,
        limit: r.limit === null ? null : String(r.limit),
      }))
      .sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0));
    expect(seeded).toEqual(expected);
  });

  it("budget_config holds the rows the generator derives from CONVENTIONS", async () => {
    const seeded = await inRollback(url, (s) =>
      s.rows<{ key: string }>(
        "select budget_tag || '/' || scope || '/' || setting as key from public.budget_config order by 1",
      ),
    );
    const expected = budgetConfigSeedRows(conventions)
      .map((r) => `${r.tag}/${r.scope}/${r.setting}`)
      .sort();
    expect(seeded.map((r) => r.key)).toEqual(expected);
  });

  it("comment_series_profiles equals CONVENTIONS' comment series table", async () => {
    const seeded = await inRollback(url, (s) =>
      s.rows(
        `select profile, route_label as "routeLabel", platform, route,
                comment_services as "commentServices", series_text as "seriesText", steps, push,
                replies_text as "repliesText"
         from public.comment_series_profiles order by profile`,
      ),
    );
    const expected = profileSeedRows(conventions, services).sort((a, b) =>
      a.profile < b.profile ? -1 : 1,
    );
    expect(seeded).toEqual(expected);
  });
});
