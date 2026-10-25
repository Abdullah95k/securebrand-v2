// The stack's connection and this checkout's test namespace: from the environment that make test
// and make check --acceptance export, else from the scripts that print them (scripts/stack-env.sh,
// scripts/test-namespace.sh). Everything here talks to localhost.
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { REPO_DIR } from "../../tools/paths.ts";

function exportsOf(script: string): Record<string, string> {
  const out = execFileSync(join(REPO_DIR, "scripts", script), [], {
    cwd: REPO_DIR,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
  });
  const vars: Record<string, string> = {};
  for (const line of out.split("\n")) {
    const m = /^export ([A-Z_][A-Z0-9_]*)='(.*)'$/.exec(line.trim());
    if (m?.[1] !== undefined && m[2] !== undefined) vars[m[1]] = m[2].replaceAll("'\\''", "'");
  }
  return vars;
}

function variable(name: string, script: string): string {
  const value = process.env[name] ?? exportsOf(script)[name];
  if (value === undefined || value === "")
    throw new Error(
      `${name} is not set and ${script} does not print it (is the stack up? make up)`,
    );
  return value;
}

/** The URL of the stack's own Supabase database (`postgres`), as supabase status reports it. */
export function stackDatabaseUrl(): string {
  return variable("SUPABASE_DB_URL", "stack-env.sh");
}

/** The name of this checkout's fresh database, test_<namespace>. */
export function testDatabaseName(): string {
  return variable("TEST_PG_DATABASE", "test-namespace.sh");
}

/** The URL of another database on the stack's Postgres server. */
export function databaseUrl(name: string): string {
  const url = new URL(stackDatabaseUrl());
  url.pathname = `/${name}`;
  return url.toString();
}

/** The URL of this checkout's fresh database. */
export function testDatabaseUrl(): string {
  return databaseUrl(testDatabaseName());
}
