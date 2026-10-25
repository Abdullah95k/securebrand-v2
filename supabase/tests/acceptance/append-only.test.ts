// A9 (T7, S8): the five audit tables are append-only for every role, the owner included, and
// purge_audit_rows deletes the rows it names only with a recorded retention run or deletion.
import { describe, expect, it } from "vitest";
import { asRole, inRollback } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const DENIED = "42501";
const RUN = "01K00000000000000000000R01";
const DELETION = "del:author_request:author:" + "a".repeat(64);

/** One valid row per audit table, an ordinary column to update, and the role that writes it. */
const AUDIT_TABLES: Record<
  string,
  { writer: "service_role" | "admin_api"; insert: string; column: string }
> = {
  registry_audit: {
    writer: "service_role",
    insert: `insert into public.registry_audit (decision_id, decision, action, source_id, actor)
             values ('01K00000000000000000000D01', 'promote', 'no_op',
                     '00000000-0000-4000-8000-000000000001', 'qualifier') returning audit_id::text as id`,
    column: "action",
  },
  canary_audit: {
    writer: "service_role",
    insert: `insert into public.canary_audit (record, platform, route, class)
             values ('fetch', 'x', 'green', 'ok') returning audit_id::text as id`,
    column: "record",
  },
  retention_audit: {
    writer: "service_role",
    insert: `insert into public.retention_audit (run_id, executor, trigger, started_at, status)
             values ('01K00000000000000000000R02', 'retention-purger', 'schedule', now(), 'pass')
             returning run_id as id`,
    column: "status",
  },
  x_compliance_audit: {
    writer: "service_role",
    insert: `insert into public.x_compliance_audit (run_id, trigger, started_at, status)
             values ('01K00000000000000000000X01', 'daily', now(), 'pass') returning run_id as id`,
    column: "status",
  },
  admin_audit: {
    writer: "admin_api",
    insert: `insert into public.admin_audit (request_id, actor, action)
             values ('01K00000000000000000000Q01', 'person:01K00000000000000000000P01', 'flag_change')
             returning audit_id::text as id`,
    column: "action",
  },
};

const url = testDatabaseUrl();

describe("append-only audit tables", () => {
  it.each(Object.keys(AUDIT_TABLES))(
    "an update or delete on %s with its writer role fails with a permission error",
    async (table) => {
      const spec = AUDIT_TABLES[table];
      if (spec === undefined) throw new Error(table);
      const codes = await asRole(url, spec.writer, async (s) => {
        const inserted = await s.failure(spec.insert);
        return {
          inserted,
          update: await s.failure(
            `update public.${table} set ${spec.column} = ${spec.column}`,
          ),
          delete: await s.failure(`delete from public.${table}`),
          truncate: await s.failure(`truncate public.${table}`),
        };
      });
      expect(codes).toEqual({ inserted: null, update: DENIED, delete: DENIED, truncate: DENIED });
    },
  );

  it.each(Object.keys(AUDIT_TABLES))(
    "the owner's update or delete on %s is refused by the trigger",
    async (table) => {
      const spec = AUDIT_TABLES[table];
      if (spec === undefined) throw new Error(table);
      const codes = await inRollback(url, async (s) => {
        await s.rows(spec.insert);
        return {
          update: await s.failure(
            `update public.${table} set ${spec.column} = ${spec.column}`,
          ),
          delete: await s.failure(`delete from public.${table}`),
          truncate: await s.failure(`truncate public.${table}`),
        };
      });
      expect(codes).toEqual({ update: DENIED, delete: DENIED, truncate: DENIED });
    },
  );

  it("purge_audit_rows refuses a purge without a recorded run or deletion", async () => {
    const codes = await asRole(url, "service_role", async (s) => {
      const [row] = await s.rows<{ id: string }>(AUDIT_TABLES.registry_audit?.insert ?? "");
      return {
        none: await s.failure("select public.purge_audit_rows('registry_audit', $1, null)", [
          [row?.id],
        ]),
        unknown: await s.failure("select public.purge_audit_rows('registry_audit', $1, $2)", [
          [row?.id],
          RUN,
        ]),
      };
    });
    expect(codes).toEqual({ none: DENIED, unknown: DENIED });
  });

  it("purge_audit_rows deletes the named rows with a recorded run, and only those", async () => {
    const result = await asRole(url, "service_role", async (s) => {
      await s.rows(
        `insert into public.retention_audit (run_id, executor, trigger, started_at, status)
         values ($1, 'retention-purger', 'client_contract_end', now(), 'pass')`,
        [RUN],
      );
      const [keep] = await s.rows<{ id: string }>(AUDIT_TABLES.canary_audit?.insert ?? "");
      const [gone] = await s.rows<{ id: string }>(AUDIT_TABLES.canary_audit?.insert ?? "");
      const [removed] = await s.rows<{ n: number }>(
        "select public.purge_audit_rows('canary_audit', $1, $2) as n",
        [[gone?.id], RUN],
      );
      const left = await s.rows<{ id: string }>(
        "select audit_id::text as id from public.canary_audit where audit_id::text = any ($1)",
        [[keep?.id, gone?.id]],
      );
      return { removed: removed?.n, left: left.map((r) => r.id) };
    });
    expect(result.removed).toBe(1);
    expect(result.left).toHaveLength(1);
  });

  it("purge_audit_rows takes a recorded deletion as evidence for an erasure", async () => {
    const removed = await asRole(url, "service_role", async (s) => {
      await s.rows(
        `insert into public.deletion_propagations (deletion_id, reason, scope, mode, signal_at, due_at)
         values ($1, 'author_request', 'author', 'delete', now(), now() + interval '24 hours')`,
        [DELETION],
      );
      const [row] = await s.rows<{ id: string }>(AUDIT_TABLES.x_compliance_audit?.insert ?? "");
      const [n] = await s.rows<{ n: number }>(
        "select public.purge_audit_rows('x_compliance_audit', $1, $2) as n",
        [[row?.id], DELETION],
      );
      return n?.n;
    });
    expect(removed).toBe(1);
  });

  it("only the service role may call purge_audit_rows", async () => {
    for (const role of ["admin_api", "authenticated", "anon"] as const) {
      const code = await asRole(url, role, (s) =>
        s.failure("select public.purge_audit_rows('admin_audit', '{}', $1)", [RUN]),
      );
      expect(code, role).toBe(DENIED);
    }
  });
});
