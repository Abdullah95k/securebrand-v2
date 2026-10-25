// A1, A2 and A30: every migration applies in order on an empty database, the catalogue is the
// plan's, a second run applies nothing, re-running the seeds keeps what the admin console changed,
// and none of the tables the ADRs replaced exists.
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { MIGRATIONS_DIR, SUPABASE_DIR } from "../../tools/paths.ts";
import { inRollback, withClient } from "../helpers/db.ts";
import { databaseUrl, testDatabaseName, testDatabaseUrl } from "../helpers/env.ts";
import { dropDatabase, emptyDatabase, migrationUp } from "../helpers/fresh.ts";
import { migrationVersions } from "../helpers/targets.ts";

const url = testDatabaseUrl();
const EMPTY = `${testDatabaseName()}_m`;

interface TableShape {
  columns: string[];
  indexes: string[];
}

const EXPECTED = (
  JSON.parse(readFileSync(join(SUPABASE_DIR, "tests/fixtures/expected-schema.json"), "utf8")) as {
    tables: Record<string, TableShape>;
  }
).tables;

/** The public schema as `expected-schema.json` writes it. */
async function catalogue(dbUrl: string): Promise<Record<string, TableShape>> {
  return withClient(dbUrl, async (c) => {
    const columns = await c.query<{ relname: string; col: string }>(
      `select c.relname,
              a.attname || ' ' || format_type(a.atttypid, a.atttypmod)
              || case when a.attnotnull then ' not null' else '' end
              || coalesce(' default ' || pg_get_expr(d.adbin, d.adrelid), '')
              || case when a.attidentity <> '' then ' identity' else '' end as col
       from pg_attribute a
       join pg_class c on c.oid = a.attrelid
       join pg_namespace n on n.oid = c.relnamespace
       left join pg_attrdef d on d.adrelid = a.attrelid and d.adnum = a.attnum
       where n.nspname = 'public' and c.relkind in ('r', 'p', 'v') and a.attnum > 0
         and not a.attisdropped
       order by c.relname, a.attnum`,
    );
    const indexes = await c.query<{ tablename: string; indexdef: string }>(
      "select tablename, indexdef from pg_indexes where schemaname = 'public'",
    );
    const out: Record<string, TableShape> = {};
    for (const { relname, col } of columns.rows)
      (out[relname] ??= { columns: [], indexes: [] }).columns.push(col);
    for (const { tablename, indexdef } of indexes.rows) {
      const shape = (out[tablename] ??= { columns: [], indexes: [] });
      shape.indexes.push(
        indexdef
          .replace(
            /^CREATE (UNIQUE )?INDEX \S+ ON public\.\S+ USING /,
            (_m, unique: string | undefined) => (unique === undefined ? "" : "unique "),
          )
          .toLowerCase(),
      );
    }
    for (const shape of Object.values(out)) shape.indexes.sort();
    return out;
  });
}

describe("the migrations", () => {
  afterAll(async () => {
    await dropDatabase(EMPTY);
  });

  it("applies every migration in order on an empty database", async () => {
    await emptyDatabase(EMPTY);
    const output = migrationUp(EMPTY);
    for (const file of readdirSync(MIGRATIONS_DIR).filter((f) => f.endsWith(".sql")))
      expect(output).toContain(file);
    const applied = await withClient(databaseUrl(EMPTY), async (c) =>
      (
        await c.query<{ version: string }>(
          "select version from supabase_migrations.schema_migrations order by version",
        )
      ).rows.map((r) => r.version),
    );
    expect(applied).toEqual(migrationVersions());
  });

  it("the catalogue matches the expected schema snapshot", async () => {
    const actual = await catalogue(url);
    expect(Object.keys(actual).sort()).toEqual(Object.keys(EXPECTED).sort());
    for (const [table, shape] of Object.entries(EXPECTED)) {
      expect(actual[table]?.columns, `${table} columns`).toEqual(shape.columns);
      expect(actual[table]?.indexes, `${table} indexes`).toEqual([...shape.indexes].sort());
    }
  });

  it("a second run applies nothing and succeeds", async () => {
    const before = await withClient(
      url,
      async (c) =>
        (
          await c.query<{ n: number }>(
            "select count(*)::int as n from supabase_migrations.schema_migrations",
          )
        ).rows[0]?.n,
    );
    const output = migrationUp(testDatabaseName());
    expect(output).not.toMatch(/Applying migration/);
    const after = await withClient(
      url,
      async (c) =>
        (
          await c.query<{ n: number }>(
            "select count(*)::int as n from supabase_migrations.schema_migrations",
          )
        ).rows[0]?.n,
    );
    expect(after).toBe(before);
  });

  it("re-running the seed migrations keeps a changed feature flag value", async () => {
    const seeds = readdirSync(MIGRATIONS_DIR)
      .filter((f) => /_seed_[a-z_]+\.sql$/.test(f))
      .sort();
    expect(seeds.length).toBeGreaterThan(0);
    const counts = `select (select count(*) from public.budgets)::int as budgets,
      (select count(*) from public.budget_config)::int as config,
      (select count(*) from public.feature_flags)::int as flags,
      (select count(*) from public.retention_classes)::int as clocks,
      (select count(*) from public.permitted_uses)::int as uses,
      (select count(*) from public.credentials)::int as credentials,
      (select count(*) from public.canary_targets)::int as canary,
      (select count(*) from public.iq_reference)::int as places,
      (select count(*) from public.comment_series_profiles)::int as profiles`;
    const result = await inRollback(url, async (s) => {
      const before = await s.rows(counts);
      await s.rows(
        "update public.feature_flags set value = 'scrapecreators', reason = 'test' where name = 'FB_VENDOR_ROUTE' and scope = ''",
      );
      for (const file of seeds) await s.rows(readFileSync(join(MIGRATIONS_DIR, file), "utf8"));
      const after = await s.rows(counts);
      const flag = await s.rows<{ value: string }>(
        "select value from public.feature_flags where name = 'FB_VENDOR_ROUTE' and scope = ''",
      );
      return { before, after, value: flag[0]?.value };
    });
    expect(result.after).toEqual(result.before);
    expect(result.value).toBe("scrapecreators");
  });

  it("none of the replaced tables exists", async () => {
    const found = await withClient(url, async (c) =>
      (
        await c.query<{ relname: string }>(
          `select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
           where n.nspname = 'public' and (c.relname in ('vendor_keys', 'profile_cache', 'tt_user_cache',
             'comment_ledger', 'tt_comment_state', 'audit_log', 'cadence_rules')
             or c.relname like '%profile_cache%' or c.relname like '%cadence%')`,
        )
      ).rows.map((r) => r.relname),
    );
    expect(found).toEqual([]);
  });
});
