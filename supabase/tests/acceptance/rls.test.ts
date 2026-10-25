// A5 to A8 and A38: row-level security on every table, a client user's reads limited to its own
// clients and to the columns it may see, nobody but the writer roles writing, and the definer
// helper behind the policies; on both databases (S10).
import { beforeAll, describe, expect, it } from "vitest";
import { asRole, withClient } from "../helpers/db.ts";
import { MATRIX, tablesOfClass } from "../helpers/expected.ts";
import {
  CLIENT_A,
  CLIENT_B,
  CLIENT_READS,
  SOURCE_A,
  SOURCE_SHARED,
  USER_A,
  USER_B,
  USER_MANAGER,
  USER_OPS,
  scenario,
} from "../helpers/scenario.ts";
import { assertMigrated, targets } from "../helpers/targets.ts";

const DENIED = "42501";
// A write to a view no role may write: the view cannot be written at all (it joins), which
// Postgres reports before the privilege check; the privilege suite shows no role holds a write.
const NOT_WRITABLE = "55000";
const writeRefused = (table: string): string =>
  MATRIX.tables[table]?.class === "V" ? NOT_WRITABLE : DENIED;
const CLIENT_TABLES = tablesOfClass("C");
const OTHER_TABLES = tablesOfClass("S", "A", "R", "V");
const ALL_TABLES = Object.keys(MATRIX.tables).sort();

/**
 * A column of `table` to name in an UPDATE, so the statement is well formed: an ordinary one, since
 * naming an identity column fails (428C9) before the privilege check this suite is about.
 */
async function firstColumn(url: string, table: string): Promise<string> {
  return withClient(url, async (c) => {
    const r = await c.query<{ column_name: string }>(
      `select column_name from information_schema.columns
       where table_schema = 'public' and table_name = $1 and is_identity = 'NO'
         and is_generated = 'NEVER'
       order by ordinal_position limit 1`,
      [table],
    );
    const name = r.rows[0]?.column_name;
    if (name === undefined) throw new Error(`no table ${table}`);
    return name;
  });
}

describe.each(targets())("row-level security on $label", ({ url }) => {
  beforeAll(async () => {
    await assertMigrated(url);
  });

  it("every public table has row level security enabled", async () => {
    const tables = await withClient(url, async (c) => {
      const r = await c.query<{ relname: string; rls: boolean }>(
        `select c.relname, c.relrowsecurity as rls from pg_class c
         join pg_namespace n on n.oid = c.relnamespace
         where n.nspname = 'public' and c.relkind in ('r', 'p') order by c.relname`,
      );
      return r.rows;
    });
    expect(tables.map((t) => t.relname)).toEqual(tablesOfClass("C", "S", "A", "R"));
    expect(tables.filter((t) => !t.rls).map((t) => t.relname)).toEqual([]);
  });

  it.each(CLIENT_TABLES)("a client user reads only its own client's rows in %s", async (table) => {
    const query = CLIENT_READS[table];
    if (query === undefined) throw new Error(`no client read for ${table}`);
    const owners = await scenario(url, "authenticated", USER_A, async (s) =>
      (await s.rows<{ owner: string }>(query)).map((r) => r.owner),
    );
    const allowed = table === "sources" ? [SOURCE_A, SOURCE_SHARED] : [CLIENT_A, "global"];
    expect(owners.length, table).toBeGreaterThan(0);
    for (const owner of owners) expect(allowed, `${table} row of ${owner}`).toContain(owner);
    if (table === "sources") expect(owners.sort()).toEqual([SOURCE_A, SOURCE_SHARED].sort());
  });

  it.each(OTHER_TABLES)("a client user reads no row of %s", async (table) => {
    const code = await scenario(url, "authenticated", USER_A, (s) =>
      s.failure(`select * from public.${table} limit 1`),
    );
    expect(code).toBe(DENIED);
  });

  it("a client user cannot see another client's id in sources.client_ids", async () => {
    const codes = await scenario(url, "authenticated", USER_A, async (s) => ({
      client_ids: await s.failure("select client_ids from public.sources"),
      notes: await s.failure("select notes from public.sources"),
      health_set_by: await s.failure("select health_set_by from public.sources"),
      platform_meta: await s.failure("select platform_meta from public.sources"),
      country_signals: await s.failure("select country_signals from public.sources"),
      star: await s.failure("select * from public.sources"),
    }));
    expect(codes).toEqual({
      client_ids: DENIED,
      notes: DENIED,
      health_set_by: DENIED,
      platform_meta: DENIED,
      country_signals: DENIED,
      star: DENIED,
    });
  });

  it.each(ALL_TABLES)("a client user cannot write %s", async (table) => {
    const column = await firstColumn(url, table);
    const codes = await scenario(url, "authenticated", USER_B, async (s) => [
      await s.failure(`insert into public.${table} default values`),
      await s.failure(`update public.${table} set ${column} = ${column}`),
      await s.failure(`delete from public.${table}`),
    ]);
    expect(codes, table).toEqual([writeRefused(table), writeRefused(table), writeRefused(table)]);
  });

  it.each(ALL_TABLES)("anon reads and writes nothing in %s", async (table) => {
    const column = await firstColumn(url, table);
    const codes = await scenario(url, "anon", undefined, async (s) => [
      await s.failure(`select * from public.${table} limit 1`),
      await s.failure(`insert into public.${table} default values`),
      await s.failure(`update public.${table} set ${column} = ${column}`),
      await s.failure(`delete from public.${table}`),
    ]);
    expect(codes, table).toEqual([
      DENIED,
      writeRefused(table),
      writeRefused(table),
      writeRefused(table),
    ]);
  });

  it.each(tablesOfClass("R"))("the service role cannot change %s", async (table) => {
    const column = await firstColumn(url, table);
    const codes = await asRole(url, "service_role", async (s) => [
      await s.failure(`insert into public.${table} default values`),
      await s.failure(`update public.${table} set ${column} = ${column}`),
      await s.failure(`delete from public.${table}`),
    ]);
    expect(codes, table).toEqual([DENIED, DENIED, DENIED]);
  });

  it("the service role cannot write the admin-written tables", async () => {
    const adminWritten = Object.entries(MATRIX.tables)
      .filter(
        ([, spec]) => spec.admin_api.includes("INSERT") && !spec.service_role.includes("INSERT"),
      )
      .map(([name]) => name);
    expect(adminWritten).toContain("feature_flags");
    for (const table of adminWritten) {
      const code = await asRole(url, "service_role", (s) =>
        s.failure(`insert into public.${table} default values`),
      );
      expect(code, table).toBe(DENIED);
    }
  });

  it("the service role and admin_api read every table", async () => {
    for (const role of ["service_role", "admin_api"] as const)
      for (const table of ALL_TABLES) {
        const code = await asRole(url, role, (s) =>
          s.failure(`select * from public.${table} limit 1`),
        );
        expect(code, `${role} reads ${table}`).toBeNull();
      }
  });

  it("anon cannot call current_client_ids, and a caller with no user gets an empty set", async () => {
    const anon = await scenario(url, "anon", undefined, (s) =>
      s.failure("select public.current_client_ids()"),
    );
    expect(anon).toBe(DENIED);
    const nobody = await scenario(url, "authenticated", undefined, (s) =>
      s.rows<{ ids: string[] }>("select public.current_client_ids() as ids"),
    );
    expect(nobody[0]?.ids).toEqual([]);
  });

  it("a client user gets exactly its client-role memberships", async () => {
    for (const [user, expected] of [
      [USER_A, [CLIENT_A]],
      [USER_B, [CLIENT_B]],
    ] as const) {
      const rows = await scenario(url, "authenticated", user, (s) =>
        s.rows<{ ids: string[] }>("select public.current_client_ids() as ids"),
      );
      expect(rows[0]?.ids).toEqual(expected);
    }
  });

  it("an account manager's assignment and a global staff role grant no direct read", async () => {
    for (const user of [USER_MANAGER, USER_OPS]) {
      const seen = await scenario(url, "authenticated", user, async (s) => ({
        ids: (await s.rows<{ ids: string[] }>("select public.current_client_ids() as ids"))[0]?.ids,
        clients: (await s.rows("select client_id from public.clients")).length,
      }));
      expect(seen).toEqual({ ids: [], clients: 0 });
    }
  });

  it("current_client_ids is a definer function with its search path pinned", async () => {
    const rows = await withClient(url, (c) =>
      c.query<{ secdef: boolean; config: string[] | null }>(
        `select prosecdef as secdef, proconfig as config from pg_proc
         where oid = 'public.current_client_ids()'::regprocedure`,
      ),
    );
    expect(rows.rows[0]).toEqual({ secdef: true, config: ['search_path=""'] });
  });
});
