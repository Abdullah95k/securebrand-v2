// The two databases the privilege and row-level security suites run against (plan S10): this
// checkout's fresh test database, and the stack's own Supabase database, which must hold exactly
// this checkout's migrations (make up or make migrate applies them; the tests never do).
import { readdirSync } from "node:fs";
import { MIGRATIONS_DIR } from "../../tools/paths.ts";
import { withClient } from "./db.ts";
import { stackDatabaseUrl, testDatabaseUrl } from "./env.ts";

export interface Target {
  label: string;
  url: string;
}

export function targets(): Target[] {
  return [
    { label: "the fresh test database", url: testDatabaseUrl() },
    { label: "the stack's Supabase database", url: stackDatabaseUrl() },
  ];
}

/** The versions of this checkout's migration files, in order. */
export function migrationVersions(): string[] {
  return readdirSync(MIGRATIONS_DIR)
    .filter((f) => f.endsWith(".sql"))
    .map((f) => f.slice(0, 14))
    .sort();
}

/** Throws unless the database holds exactly this checkout's migrations. */
export async function assertMigrated(url: string): Promise<void> {
  const applied = await withClient(url, async (c) => {
    const exists = await c.query<{ ok: boolean }>(
      "select to_regclass('supabase_migrations.schema_migrations') is not null as ok",
    );
    if (exists.rows[0]?.ok !== true) return [];
    const rows = await c.query<{ version: string }>(
      "select version from supabase_migrations.schema_migrations order by version",
    );
    return rows.rows.map((r) => r.version);
  });
  const expected = migrationVersions();
  if (applied.join(",") !== expected.join(","))
    throw new Error(
      `the database at ${new URL(url).pathname} holds migrations [${applied.join(", ")}], ` +
        `not this checkout's [${expected.join(", ")}]: run make migrate (or make up)`,
    );
}
