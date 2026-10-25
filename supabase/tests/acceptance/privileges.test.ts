// A7 (S10): the privileges of every table, column and function in public equal the plan's matrix,
// on the fresh test database and on the stack's Supabase database, whose default privileges would
// otherwise grant anon and authenticated everything on a new table.
import { beforeAll, describe, expect, it } from "vitest";
import { withClient } from "../helpers/db.ts";
import { MATRIX, TABLE_PRIVILEGES, expectedPrivileges } from "../helpers/expected.ts";
import { assertMigrated, targets } from "../helpers/targets.ts";

describe.each(targets())("privileges on $label", ({ url }) => {
  beforeAll(async () => {
    await assertMigrated(url);
  });

  it("holds exactly the tables and views of expected-privileges.json", async () => {
    const names = await withClient(url, async (c) => {
      const r = await c.query<{ relname: string }>(
        `select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
         where n.nspname = 'public' and c.relkind in ('r', 'p', 'v', 'm') order by 1`,
      );
      return r.rows.map((row) => row.relname);
    });
    expect(names).toEqual(Object.keys(MATRIX.tables).sort());
  });

  it("the privileges of every table equal expected-privileges.json", async () => {
    const actual = await withClient(url, async (c) => {
      const out: Record<string, Record<string, string[]>> = {};
      for (const table of Object.keys(MATRIX.tables)) {
        out[table] = {};
        for (const role of MATRIX.roles) {
          const held: string[] = [];
          for (const privilege of TABLE_PRIVILEGES) {
            const r = await c.query<{ ok: boolean }>(
              "select has_table_privilege($1, $2, $3) as ok",
              [role, `public.${table}`, privilege],
            );
            if (r.rows[0]?.ok === true) held.push(privilege);
          }
          out[table][role] = held.sort();
        }
      }
      return out;
    });
    for (const table of Object.keys(MATRIX.tables))
      for (const role of MATRIX.roles)
        expect(actual[table]?.[role], `${role} on ${table}`).toEqual(
          expectedPrivileges(table, role),
        );
  });

  it("authenticated reads only the columns the matrix lists where it holds column grants", async () => {
    for (const [table, spec] of Object.entries(MATRIX.tables)) {
      const columns = await withClient(url, async (c) => {
        const r = await c.query<{ column_name: string; ok: boolean }>(
          `select column_name, has_column_privilege('authenticated', $1, column_name, 'SELECT') as ok
           from information_schema.columns where table_schema = 'public' and table_name = $2
           order by ordinal_position`,
          [`public.${table}`, table],
        );
        return r.rows.filter((row) => row.ok).map((row) => row.column_name);
      });
      const expected =
        spec.authenticated_columns ?? (spec.authenticated.includes("SELECT") ? null : []);
      if (expected === null) continue; // a table-level SELECT covers every column
      expect(columns.sort(), table).toEqual([...expected].sort());
    }
  });

  it("the functions in public are executable by exactly the roles the matrix lists", async () => {
    const actual = await withClient(url, async (c) => {
      const r = await c.query<{ signature: string; oid: number }>(
        `select p.proname || '(' || oidvectortypes(p.proargtypes) || ')' as signature, p.oid
         from pg_proc p where p.pronamespace = 'public'::regnamespace order by 1`,
      );
      const out: Record<string, string[]> = {};
      for (const { signature, oid } of r.rows) {
        out[signature] = [];
        for (const role of MATRIX.roles) {
          const ok = await c.query<{ ok: boolean }>(
            "select has_function_privilege($1, $2::oid, 'EXECUTE') as ok",
            [role, oid],
          );
          if (ok.rows[0]?.ok === true) out[signature].push(role);
        }
      }
      return out;
    });
    const expected = Object.fromEntries(
      Object.entries(MATRIX.functions).map(([signature, roles]) => [signature, [...roles].sort()]),
    );
    for (const roles of Object.values(actual)) roles.sort();
    expect(actual).toEqual(expected);
  });

  it("new tables in public get no default privileges for anon or authenticated", async () => {
    const acl = await withClient(url, async (c) => {
      const r = await c.query<{ acl: string }>(
        `select coalesce(array_to_string(d.defaclacl, ','), '') as acl from pg_default_acl d
         where d.defaclrole = 'postgres'::regrole and d.defaclnamespace = 'public'::regnamespace`,
      );
      return r.rows.map((row) => row.acl).join(",");
    });
    expect(acl).not.toMatch(/(^|,)(anon|authenticated)=/);
  });
});
