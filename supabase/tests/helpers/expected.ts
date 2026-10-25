// The expected privilege matrix (tests/fixtures/expected-privileges.json, written from the plan).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { SUPABASE_DIR } from "../../tools/paths.ts";

export type TableClass = "C" | "S" | "A" | "R" | "V";
export type ApiRole = "anon" | "authenticated" | "service_role" | "admin_api";

export interface TablePrivileges {
  class: TableClass;
  anon?: string[];
  authenticated: string[];
  authenticated_columns?: string[];
  service_role: string[];
  admin_api: string[];
}

interface Matrix {
  roles: ApiRole[];
  tables: Record<string, TablePrivileges>;
  functions: Record<string, ApiRole[]>;
}

export const MATRIX = JSON.parse(
  readFileSync(join(SUPABASE_DIR, "tests/fixtures/expected-privileges.json"), "utf8"),
) as Matrix;

export const TABLE_PRIVILEGES = [
  "SELECT",
  "INSERT",
  "UPDATE",
  "DELETE",
  "TRUNCATE",
  "REFERENCES",
  "TRIGGER",
  "MAINTAIN",
] as const;

/** The expected table privileges of `role` on `table`, sorted. */
export function expectedPrivileges(table: string, role: ApiRole): string[] {
  const spec = MATRIX.tables[table];
  if (spec === undefined) throw new Error(`expected-privileges.json has no table ${table}`);
  return [...(spec[role] ?? [])].sort();
}

/** The tables (not views) of a class, sorted. */
export function tablesOfClass(...classes: TableClass[]): string[] {
  return Object.entries(MATRIX.tables)
    .filter(([, spec]) => classes.includes(spec.class))
    .map(([name]) => name)
    .sort();
}

/** The role that writes a table's rows: admin_api where it holds INSERT, else service_role. */
export function writerRole(table: string): "admin_api" | "service_role" {
  const spec = MATRIX.tables[table];
  if (spec === undefined) throw new Error(`expected-privileges.json has no table ${table}`);
  return spec.admin_api.includes("INSERT") ? "admin_api" : "service_role";
}
