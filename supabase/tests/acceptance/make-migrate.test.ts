// A4, A39 and A40 (plan T4, T19): make migrate's Postgres hook, scripts/migrate/postgres.sh,
// applies the pending migrations and reports each, then the service migrations; with --seed it
// loads the synthetic seed and never the local Auth seed, and a re-run changes nothing; the
// service runner applies a service migration once into svc_<service> and refuses an applied file
// that changed or a file that names another schema. Every case runs on its own database on the
// stack's Postgres server, named by MIGRATE_DB_URL, never on the stack's Supabase database.
import { spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { MIGRATIONS_DIR, REPO_DIR, SUPABASE_DIR } from "../../tools/paths.ts";
import { withClient } from "../helpers/db.ts";
import { databaseUrl, testDatabaseName } from "../helpers/env.ts";
import { cliUrl, dropDatabase, emptyDatabase, migrationUp } from "../helpers/fresh.ts";
import { migrationVersions } from "../helpers/targets.ts";

const DB = `${testDatabaseName()}_r`;
const scratch = mkdtempSync(join(tmpdir(), "f3-migrate-"));

interface Run {
  status: number | null;
  output: string;
}

/** Runs a command from the repository root against DB, with its stdout and stderr together. */
function run(command: string, args: string[]): Run {
  const r = spawnSync(command, args, {
    cwd: REPO_DIR,
    encoding: "utf8",
    env: { ...process.env, MIGRATE_DB_URL: cliUrl(DB) },
  });
  return { status: r.status, output: `${r.stdout}${r.stderr}` };
}

async function one<R>(sql: string): Promise<R> {
  return withClient(databaseUrl(DB), async (c) => (await c.query(sql)).rows[0] as R);
}

const appliedVersions = async (): Promise<string[]> =>
  (
    await one<{ versions: string[] }>(
      "select coalesce(array_agg(version order by version), '{}') as versions from supabase_migrations.schema_migrations",
    )
  ).versions;

/** A digest of every row the synthetic seed writes, and the counts the Auth seed would change. */
const seedState = () =>
  one<Record<string, string | number>>(
    `select (select count(*) from public.clients)::int as clients,
            (select count(*) from public.sources)::int as sources,
            (select count(*) from public.client_sources)::int as client_sources,
            (select count(*) from public.keywords)::int as keywords,
            (select count(*) from auth.users)::int as users,
            (select count(*) from public.client_members)::int as members,
            md5((select string_agg(t::text, ',' order by t::text) from public.clients t)
              || (select string_agg(t::text, ',' order by t::text) from public.sources t)
              || (select string_agg(t::text, ',' order by t::text) from public.client_sources t)
              || (select string_agg(t::text, ',' order by t::text) from public.keywords t)) as digest`,
  );

beforeAll(async () => {
  await emptyDatabase(DB);
});

afterAll(async () => {
  await dropDatabase(DB);
  rmSync(scratch, { recursive: true, force: true });
});

describe("make migrate", () => {
  it("make migrate applies a pending migration and reports it", async () => {
    // A database that holds every migration but the newest, as a running stack would before a
    // pull brings in a new one.
    const files = readdirSync(MIGRATIONS_DIR)
      .filter((f) => f.endsWith(".sql"))
      .sort();
    const newest = files.at(-1) ?? "";
    const older = join(scratch, "older");
    mkdirSync(join(older, "supabase/migrations"), { recursive: true });
    copyFileSync(join(SUPABASE_DIR, "config.toml"), join(older, "supabase/config.toml"));
    for (const f of files.slice(0, -1))
      copyFileSync(join(MIGRATIONS_DIR, f), join(older, "supabase/migrations", f));
    migrationUp(DB, older);
    expect(await appliedVersions()).toEqual(migrationVersions().slice(0, -1));

    const first = run("make", ["migrate", "ENGINE=postgres"]);
    expect(first.status, first.output).toBe(0);
    expect(first.output).toContain(`Applying migration ${newest}`);
    for (const f of files.slice(0, -1))
      expect(first.output).not.toContain(`Applying migration ${f}`);
    expect(await appliedVersions()).toEqual(migrationVersions());

    const second = run("make", ["migrate", "ENGINE=postgres"]);
    expect(second.status, second.output).toBe(0);
    expect(second.output).not.toContain("Applying migration");
    expect(await appliedVersions()).toEqual(migrationVersions());
  });

  it("postgres.sh --seed loads the synthetic seed and no auth user", async () => {
    const r = run(join(REPO_DIR, "scripts/migrate/postgres.sh"), ["--seed"]);
    expect(r.status, r.output).toBe(0);
    const state = await seedState();
    expect(state).toMatchObject({ clients: 2, users: 0, members: 0 });
    expect(state["sources"]).toBeGreaterThanOrEqual(12);
    expect(state["client_sources"]).toBeGreaterThan(0);
    expect(state["keywords"]).toBeGreaterThan(0);
  });

  it("a second --seed run changes nothing", async () => {
    const before = await seedState();
    const r = run(join(REPO_DIR, "scripts/migrate/postgres.sh"), ["--seed"]);
    expect(r.status, r.output).toBe(0);
    expect(await seedState()).toEqual(before);
  });
});

describe("the service runner", () => {
  const services = join(scratch, "services");
  const file = join(services, "demo-svc/migrations/20261026120000_create_rows.sql");
  const first = "create table demo_rows (row_id int primary key, note text);\n";
  const runner = () =>
    run(process.execPath, [
      join(SUPABASE_DIR, "tools/migrate-services.ts"),
      "--db-url",
      cliUrl(DB),
      "--services-dir",
      services,
    ]);

  beforeAll(() => {
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, first);
  });

  it("the service runner applies a service migration once", async () => {
    const r1 = runner();
    expect(r1.status, r1.output).toBe(0);
    expect(r1.output).toContain("demo-svc/migrations/20261026120000_create_rows.sql");
    const r2 = runner();
    expect(r2.status, r2.output).toBe(0);
    expect(r2.output).not.toContain("applied demo-svc/");
    expect(
      await one(
        `select to_regclass('svc_demo_svc.demo_rows') is not null as created,
                to_regclass('public.demo_rows') is null as not_in_public,
                (select count(*)::int from svc_migrations.applied where service = 'demo-svc') as applied,
                has_schema_privilege('service_role', 'svc_demo_svc', 'usage')
                  and has_table_privilege('service_role', 'svc_demo_svc.demo_rows', 'select')
                  and has_table_privilege('service_role', 'svc_demo_svc.demo_rows', 'insert')
                  and has_table_privilege('service_role', 'svc_demo_svc.demo_rows', 'update')
                  and has_table_privilege('service_role', 'svc_demo_svc.demo_rows', 'delete') as service_role,
                has_schema_privilege('authenticated', 'svc_demo_svc', 'usage') as authenticated,
                has_schema_privilege('anon', 'svc_demo_svc', 'usage') as anon`,
      ),
    ).toEqual({
      created: true,
      not_in_public: true,
      applied: 1,
      service_role: true,
      authenticated: false,
      anon: false,
    });
  });

  it("the service runner refuses an applied file that changed", async () => {
    writeFileSync(file, "create table demo_rows (row_id int primary key, note text, extra int);\n");
    try {
      const r = runner();
      expect(r.status, r.output).not.toBe(0);
      expect(r.output).toMatch(
        /demo-svc\/migrations\/20261026120000_create_rows\.sql changed after it was applied/,
      );
      expect(
        await one(
          `select (select count(*)::int from information_schema.columns
                   where table_schema = 'svc_demo_svc' and table_name = 'demo_rows') as columns`,
        ),
      ).toEqual({ columns: 2 });
    } finally {
      writeFileSync(file, first);
    }
  });

  it("the service runner refuses a service migration that names another schema", async () => {
    const reach = join(services, "demo-svc/migrations/20261026130000_reach_out.sql");
    writeFileSync(reach, "create table public.demo_leak (row_id int);\n");
    try {
      const r = runner();
      expect(r.status, r.output).not.toBe(0);
      expect(r.output).toMatch(/20261026130000_reach_out\.sql names schema public/);
      expect(
        await one(
          `select to_regclass('public.demo_leak') is null as absent,
                  (select count(*)::int from svc_migrations.applied where service = 'demo-svc') as applied`,
        ),
      ).toEqual({ absent: true, applied: 1 });
    } finally {
      rmSync(reach);
    }
  });
});
