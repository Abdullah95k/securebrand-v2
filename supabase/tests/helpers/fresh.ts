// Builds a fresh database on the stack's Postgres from this checkout's migrations: drop and create
// it, install the auth stub, apply every migration with the Supabase CLI (as make migrate does),
// then, if asked, load the seed files in the order supabase/config.toml lists them.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { REPO_DIR, SUPABASE_CLI, SUPABASE_DIR } from "../../tools/paths.ts";
import { ident, withClient } from "./db.ts";
import { databaseUrl } from "./env.ts";

export const AUTH_STUB = join(SUPABASE_DIR, "tests/fixtures/auth-stub.sql");

/** The seed files supabase/config.toml lists under [db.seed] sql_paths, in its order. */
export function seedFiles(): string[] {
  const config = readFileSync(join(SUPABASE_DIR, "config.toml"), "utf8");
  const section = /^\[db\.seed\][\s\S]*?^sql_paths\s*=\s*\[([^\]]*)\]/m.exec(config);
  if (section?.[1] === undefined)
    throw new Error("supabase/config.toml has no [db.seed] sql_paths");
  return [...section[1].matchAll(/"([^"]+)"/g)].map((m) => join(SUPABASE_DIR, m[1] ?? ""));
}

/** The CLI's URL form for a database on the local stack (no TLS on localhost). */
export function cliUrl(name: string): string {
  const url = new URL(databaseUrl(name));
  url.searchParams.set("sslmode", "disable");
  return url.toString();
}

/**
 * Applies the pending migrations of `workdir`'s supabase/migrations to database `name`, and
 * returns what the CLI printed: its progress ("Applying migration <file>...") goes to stderr.
 */
export function migrationUp(name: string, workdir: string = REPO_DIR): string {
  const r = spawnSync(SUPABASE_CLI, ["migration", "up", "--db-url", cliUrl(name)], {
    cwd: workdir,
    encoding: "utf8",
    env: { ...process.env, SUPABASE_NO_UPDATE_NOTIFIER: "1" },
  });
  const output = `${r.stdout}${r.stderr}`;
  if (r.status !== 0) throw new Error(`supabase migration up failed:\n${output}`);
  return output;
}

export async function dropDatabase(name: string): Promise<void> {
  await withClient(databaseUrl("postgres"), async (c) => {
    await c.query(`drop database if exists ${ident(name)} with (force)`);
  });
}

/** An empty database with the auth stub, and no migration applied. */
export async function emptyDatabase(name: string): Promise<void> {
  await dropDatabase(name);
  await withClient(databaseUrl("postgres"), async (c) => {
    await c.query(`create database ${ident(name)}`);
  });
  await withClient(databaseUrl(name), async (c) => {
    await c.query(readFileSync(AUTH_STUB, "utf8"));
  });
}

export async function loadSeeds(name: string, files: string[] = seedFiles()): Promise<void> {
  await withClient(databaseUrl(name), async (c) => {
    for (const file of files) await c.query(readFileSync(file, "utf8"));
  });
}

/** A fresh database built from the migrations, with the seeds when `seeds` is true. */
export async function freshDatabase(name: string, seeds = true): Promise<void> {
  await emptyDatabase(name);
  migrationUp(name);
  if (seeds) await loadSeeds(name);
}
