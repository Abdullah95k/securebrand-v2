// A17, A22 to A29, A35 to A37: the keys, CHECKs and triggers of each table group. Each case writes
// as the table's writer role (A8: the service role or admin_api writes what it owns), inside a
// transaction that is rolled back.
import { describe, expect, it } from "vitest";
import { asRole, inRollback, type Session } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const url = testDatabaseUrl();
const CHECK = "23514";
const UNIQUE = "23505";
const NOT_NULL = "23502";

const CLIENT = "00000000-0000-4000-8000-00000000c001";
const GOV = "00000000-0000-4000-8000-00000000c002";
const SOURCE = "00000000-0000-4000-8000-00000000c003";
const SOURCE_2 = "00000000-0000-4000-8000-00000000c004";
const KEYWORD = "00000000-0000-4000-8000-00000000c005";
const USER = "00000000-0000-4000-8000-00000000c006";
const REF = "b".repeat(64);
const ULID = (n: number) => `01K0000000000000000000${String(n).padStart(4, "0")}`;

/** The owner writes the rows a case needs from other writers' tables. */
async function base(s: Session): Promise<void> {
  await s.rows(`
    insert into auth.users (id, email) values ('${USER}', 'constraints@example.invalid');
    insert into public.clients (client_id, name, client_type, accepts_amber)
      values ('${CLIENT}', 'synthetic-c', 'commercial', true),
             ('${GOV}', 'synthetic-gov', 'government', false);
    insert into public.sources (source_id, platform, source_type, platform_id, route, tier,
        retention_class, added_by)
      values ('${SOURCE}', 'x', 'account', 'constraints-1', 'green', 2, 'x_24h_sync', 'ops'),
             ('${SOURCE_2}', 'x', 'keyword_rule', 'green:${REF}', 'green', 2, 'x_24h_sync', 'client');
  `);
}

/** Runs `fn` as `role` after the owner wrote base(); rolled back. */
async function as<T>(
  role: "service_role" | "admin_api",
  fn: (s: Session) => Promise<T>,
): Promise<T> {
  return inRollback(url, async (s) => {
    await base(s);
    await s.rows(`set local role ${role}`);
    return fn(s);
  });
}

describe("clients and access (A22)", () => {
  it("a government client with accepts_amber is rejected", async () => {
    const code = await asRole(url, "admin_api", (s) =>
      s.failure(
        "insert into public.clients (name, client_type, accepts_amber) values ('g', 'government', true)",
      ),
    );
    expect(code).toBe(CHECK);
  });

  it("a client without client_type is rejected", async () => {
    const code = await asRole(url, "admin_api", (s) =>
      s.failure("insert into public.clients (name) values ('no-type')"),
    );
    expect(code).toBe(NOT_NULL);
  });

  it("a new client accepts no amber and is not declared to X", async () => {
    const rows = await asRole(url, "admin_api", (s) =>
      s.rows<{ accepts_amber: boolean; x_end_user_declared: boolean; status: string }>(
        `insert into public.clients (name, client_type) values ('defaults', 'commercial')
         returning accepts_amber, x_end_user_declared, status`,
      ),
    );
    expect(rows[0]).toEqual({ accepts_amber: false, x_end_user_declared: false, status: "active" });
  });

  it("a client accepts only the flagged vendors the contracts list", async () => {
    const code = await asRole(url, "admin_api", (s) =>
      s.failure(
        "insert into public.clients (name, client_type, accepted_flagged_vendors) values ('v', 'commercial', '{sociavault}')",
      ),
    );
    expect(code).toBe(CHECK);
  });

  it("a client role names its client and a global staff role names none", async () => {
    const codes = await as("admin_api", async (s) => ({
      clientRoleWithout: await s.failure(
        `insert into public.client_members (user_id, role, added_by) values ('${USER}', 'client_viewer', 't')`,
      ),
      opsWithClient: await s.failure(
        `insert into public.client_members (user_id, client_id, role, added_by) values ('${USER}', '${CLIENT}', 'ops', 't')`,
      ),
      viewer: await s.failure(
        `insert into public.client_members (user_id, client_id, role, added_by) values ('${USER}', '${CLIENT}', 'client_viewer', 't')`,
      ),
      viewerAgain: await s.failure(
        `insert into public.client_members (user_id, client_id, role, added_by) values ('${USER}', '${CLIENT}', 'client_viewer', 't')`,
      ),
      ops: await s.failure(
        `insert into public.client_members (user_id, role, added_by) values ('${USER}', 'ops', 't')`,
      ),
      opsAgain: await s.failure(
        `insert into public.client_members (user_id, role, added_by) values ('${USER}', 'ops', 't')`,
      ),
    }));
    expect(codes).toEqual({
      clientRoleWithout: CHECK,
      opsWithClient: CHECK,
      viewer: null,
      viewerAgain: UNIQUE,
      ops: null,
      opsAgain: UNIQUE,
    });
  });
});

describe("the registry (A23, A25, A26, A35 to A37)", () => {
  const source = (id: string, platformId: string) =>
    `insert into public.sources (source_id, platform, source_type, platform_id, route, tier,
       retention_class, added_by)
     values ('${id}', 'tiktok', 'creator', '${platformId}', 'amber', 1, 'vendor_agreed', 'qualifier')`;

  it("a duplicate platform id is rejected", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(source("00000000-0000-4000-8000-0000000000f1", "dup")),
      await s.failure(source("00000000-0000-4000-8000-0000000000f2", "dup")),
    ]);
    expect(codes).toEqual([null, UNIQUE]);
  });

  it("tier push is rejected, and so is a tier outside 1 to 3", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        source("00000000-0000-4000-8000-0000000000f3", "t").replace(
          ", 1, 'vendor",
          ", 'push', 'vendor",
        ),
      ),
      await s.failure(
        source("00000000-0000-4000-8000-0000000000f3", "t").replace(", 1, 'vendor", ", 4, 'vendor"),
      ),
    ]);
    expect(codes).toEqual(["22P02", CHECK]);
  });

  it("an insert with a given source_id keeps it, and a new source is pending and ok", async () => {
    const rows = await as("service_role", (s) =>
      s.rows<{ source_id: string; backfill_status: string; health: string; lifecycle: string }>(
        `${source("00000000-0000-4000-8000-0000000000f4", "kept")}
         returning source_id, backfill_status, health, lifecycle`,
      ),
    );
    expect(rows[0]).toEqual({
      source_id: "00000000-0000-4000-8000-0000000000f4",
      backfill_status: "pending",
      health: "ok",
      lifecycle: "active",
    });
  });

  it("route, vendor, lifecycle and health are closed lists", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(`update public.sources set route = 'red' where source_id = '${SOURCE}'`),
      await s.failure(
        `update public.sources set vendor = 'brightdata' where source_id = '${SOURCE}'`,
      ),
      await s.failure(
        `update public.sources set lifecycle = 'paused' where source_id = '${SOURCE}'`,
      ),
      await s.failure(`update public.sources set health = 'down' where source_id = '${SOURCE}'`),
    ]);
    expect(codes).toEqual([CHECK, CHECK, CHECK, CHECK]);
  });

  it("client_lists: an entry with both keys is rejected; a saved entry by source_id is accepted", async () => {
    const codes = await as("admin_api", async (s) => [
      await s.failure(
        `insert into public.client_lists (client_id, list, candidate_key, source_id, added_by)
         values ('${CLIENT}', 'seed', 'x:both', '${SOURCE}', 't')`,
      ),
      await s.failure(
        `insert into public.client_lists (client_id, list, source_id, added_by)
         values ('${CLIENT}', 'saved', '${SOURCE}', 't')`,
      ),
    ]);
    expect(codes).toEqual([CHECK, null]);
  });

  it("two named saved lists hold the same account, and a named watch list is rejected", async () => {
    const codes = await as("admin_api", async (s) => [
      await s.failure(
        `insert into public.client_lists (client_id, list, list_name, candidate_key, added_by)
         values ('${CLIENT}', 'saved', 'competitors', 'x:acme', 't')`,
      ),
      await s.failure(
        `insert into public.client_lists (client_id, list, list_name, candidate_key, added_by)
         values ('${CLIENT}', 'saved', 'press', 'x:acme', 't')`,
      ),
      await s.failure(
        `insert into public.client_lists (client_id, list, list_name, candidate_key, added_by)
         values ('${CLIENT}', 'saved', 'press', 'x:acme', 't')`,
      ),
      await s.failure(
        `insert into public.client_lists (client_id, list, list_name, candidate_key, added_by)
         values ('${CLIENT}', 'watch', 'named', 'x:acme', 't')`,
      ),
    ]);
    expect(codes).toEqual([null, null, UNIQUE, CHECK]);
  });

  it("client_sources records an owner apart from watchers", async () => {
    const rows = await as("service_role", async (s) => {
      await s.rows(
        `insert into public.client_sources (client_id, source_id, relation, added_by)
         values ('${CLIENT}', '${SOURCE}', 'owner', 'registry-writer'),
                ('${GOV}', '${SOURCE}', default, 'registry-writer')`,
      );
      return s.rows<{ client_id: string; relation: string }>(
        `select client_id, relation from public.client_sources where source_id = '${SOURCE}' order by relation`,
      );
    });
    expect(rows).toEqual([
      { client_id: CLIENT, relation: "owner" },
      { client_id: GOV, relation: "watcher" },
    ]);
  });

  const profile = (cols: string, values: string) =>
    `insert into public.poster_profiles (platform, key_form, status, ${cols}) values ('x', ${values})`;

  it("poster_profiles: an individual row with a handle is rejected", async () => {
    const code = await as("service_role", (s) =>
      s.failure(
        profile(
          "author_ref, account_type, individual, public_account, profile",
          `'author_ref', 'resolved', '${REF}', 'individual', true, false, '{"handle": "someone"}'`,
        ),
      ),
    );
    expect(code).toBe(CHECK);
  });

  it("poster_profiles: an ordinary individual's row keyed by candidate_key is rejected", async () => {
    const code = await as("service_role", (s) =>
      s.failure(
        profile(
          "candidate_key, account_type, individual, public_account",
          `'handle', 'resolved', 'x:somehandle', 'individual', true, false`,
        ),
      ),
    );
    expect(code).toBe(CHECK);
  });

  it("poster_profiles: an author_ref row is accepted, a resolving row by candidate_key too", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        profile(
          "author_ref, account_type, individual, public_account, followers, verified",
          `'author_ref', 'resolved', '${REF}', 'individual', true, false, 120, false`,
        ),
      ),
      await s.failure(profile("candidate_key", `'handle', 'resolving', 'x:pending_one'`)),
      await s.failure(profile("candidate_key", `'handle', 'pending', 'x:pending_two'`)),
    ]);
    expect(codes).toEqual([null, null, null]);
  });

  it("poster_profiles: a public person keeps its candidate_key, and a key names its platform", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        profile(
          "candidate_key, account_type, individual, public_account, profile",
          `'handle', 'resolved', 'x:public_person', 'individual', true, true, '{"handle": "public_person"}'`,
        ),
      ),
      await s.failure(
        `insert into public.poster_profiles (platform, key_form, status, candidate_key)
         values ('tiktok', 'handle', 'resolving', 'x:wrong_platform')`,
      ),
      await s.failure(
        profile(
          "candidate_key, author_ref",
          `'handle', 'resolving', 'x:both', '${"c".repeat(64)}'`,
        ),
      ),
    ]);
    expect(codes).toEqual([null, CHECK, CHECK]);
  });

  const audit = (cols: string, values: string) =>
    `insert into public.registry_audit (decision_id, decision, action, actor, ${cols})
     values (${values})`;

  it("one keyword add for two platforms writes two audit rows; a second row for one source is rejected", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        audit(
          "keyword_id, source_id, message_id",
          `'${ULID(1)}', 'add', 'applied', 'client-portal', '${KEYWORD}', '${SOURCE}', '${ULID(11)}'`,
        ),
      ),
      await s.failure(
        audit(
          "keyword_id, source_id, message_id",
          `'${ULID(1)}', 'add', 'applied', 'client-portal', '${KEYWORD}', '${SOURCE_2}', '${ULID(12)}'`,
        ),
      ),
      await s.failure(
        audit(
          "keyword_id, source_id",
          `'${ULID(1)}', 'add', 'no_op', 'client-portal', '${KEYWORD}', '${SOURCE}'`,
        ),
      ),
      await s.failure(
        audit(
          "source_id, message_id",
          `'${ULID(2)}', 'promote', 'applied', 'fb-page-feed-poller', '${SOURCE}', '${ULID(11)}'`,
        ),
      ),
    ]);
    expect(codes).toEqual([null, null, UNIQUE, UNIQUE]);
  });

  it("registry_audit: a mention_only row by author_ref is accepted, with no snapshot or source", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        audit("author_ref", `'${ULID(3)}', 'mention_only', 'applied', 'qualifier', '${REF}'`),
      ),
      await s.failure(
        audit(
          "author_ref, before",
          `'${ULID(4)}', 'mention_only', 'applied', 'qualifier', '${REF}', '{}'`,
        ),
      ),
      await s.failure(
        audit(
          "author_ref, source_id",
          `'${ULID(5)}', 'mention_only', 'applied', 'qualifier', '${REF}', '${SOURCE}'`,
        ),
      ),
      await s.failure(
        audit(
          "candidate_key, author_ref",
          `'${ULID(6)}', 'mention_only', 'applied', 'qualifier', 'x:c', '${REF}'`,
        ),
      ),
      await s.failure(audit("reason", `'${ULID(7)}', 'promote', 'applied', 'qualifier', null`)),
    ]);
    expect(codes).toEqual([null, CHECK, CHECK, CHECK, CHECK]);
  });

  it("registry_audit: a route-level change names exactly platform, route and vendor", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        audit(
          "route_scope, source_id",
          `'${ULID(8)}', 'health_change', 'applied', 'source-health-canary', '{"platform": "tiktok", "route": "amber", "vendor": "tikhub"}', '${SOURCE}'`,
        ),
      ),
      await s.failure(
        audit(
          "route_scope",
          `'${ULID(9)}', 'health_change', 'applied', 'source-health-canary', '{"platform": "tiktok", "route": "amber"}'`,
        ),
      ),
      await s.failure(
        audit(
          "route_scope",
          `'${ULID(10)}', 'health_change', 'applied', 'source-health-canary', '{"platform": "tiktok", "route": "amber", "vendor": null, "x": 1}'`,
        ),
      ),
    ]);
    expect(codes).toEqual([null, CHECK, CHECK]);
  });

  const decision = (cols: string, values: string) =>
    `insert into public.decisions (decision_id, decision, payload, ${cols}) values (${values})`;

  it("decisions: a sweep tier_change with only a source_id is accepted; two subjects or none are rejected", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        decision("source_id, rule_hit", `'${ULID(20)}', 'tier_change', '{}', '${SOURCE}', 9`),
      ),
      await s.failure(
        decision("candidate_key, source_id", `'${ULID(21)}', 'add', '{}', 'x:c', '${SOURCE}'`),
      ),
      await s.failure(decision("rule_hit", `'${ULID(22)}', 'reject', '{}', 9`)),
      await s.failure(
        decision("author_ref", `'${ULID(23)}', 'mention_only', '{"handle": "h"}', '${REF}'`),
      ),
      await s.failure(
        decision("author_ref", `'${ULID(24)}', 'mention_only', '{"rule_hit": 7}', '${REF}'`),
      ),
    ]);
    expect(codes).toEqual([null, CHECK, CHECK, CHECK, null]);
  });

  it("iq_reference: a city has its governorate, an outlet domain has no names", async () => {
    const codes = await as("admin_api", async (s) => [
      await s.failure(
        `insert into public.iq_reference (kind, name_ar, name_ckb, name_latin, added_by)
         values ('city', 'مدينة', 'شار', 'Synthetic City', 't')`,
      ),
      await s.failure(
        `insert into public.iq_reference (kind, domain, name_latin, added_by)
         values ('outlet_domain', 'example.iq', 'Example', 't')`,
      ),
      await s.failure(
        `insert into public.iq_reference (kind, domain, added_by) values ('outlet_domain', 'example.iq', 't')`,
      ),
    ]);
    expect(codes).toEqual([CHECK, CHECK, null]);
  });
});

describe("scheduling, flags and credentials (A17, A24)", () => {
  it("a second service-level cursor row with a null source is rejected; scope_key defaults to empty", async () => {
    const result = await as("service_role", async (s) => ({
      first: await s.failure("insert into public.cursors (service) values ('x-recent-search')"),
      second: await s.failure("insert into public.cursors (service) values ('x-recent-search')"),
      scoped: await s.failure(
        `insert into public.cursors (service, source_id, scope_key) values ('x-recent-search', '${SOURCE}', 'reconcile')`,
      ),
      plain: await s.failure(
        `insert into public.cursors (service, source_id) values ('x-recent-search', '${SOURCE}')`,
      ),
      scopeKey: (
        await s.rows<{ scope_key: string }>(
          `select scope_key from public.cursors where service = 'x-recent-search' and source_id is null`,
        )
      )[0]?.scope_key,
    }));
    expect(result).toEqual({
      first: null,
      second: UNIQUE,
      scoped: null,
      plain: null,
      scopeKey: "",
    });
  });

  it("the scheduler indexes exist", async () => {
    const rows = await inRollback(url, (s) =>
      s.rows<{ indexdef: string }>(
        "select indexdef from pg_indexes where schemaname = 'public' and tablename = 'cursors' order by 1",
      ),
    );
    const defs = rows.map((r) =>
      r.indexdef.replace(/^CREATE (UNIQUE )?INDEX \S+ ON public\.cursors USING /, "$1"),
    );
    expect(defs).toEqual(
      expect.arrayContaining(["btree (service, next_due_at)", "btree (service, last_started_at)"]),
    );
  });

  it("a follower threshold of 0, a negative or a non-number is rejected", async () => {
    const codes = await asRole(url, "admin_api", async (s) => {
      const set = (v: string) =>
        s.failure(
          `insert into public.feature_flags (name, value, changed_by, reason)
           values ('PUBLIC_ACCOUNT_FOLLOWER_THRESHOLD', $1, 't', 'test')
           on conflict (name, scope) do update set value = excluded.value`,
          [v],
        );
      return [await set("0"), await set("-5"), await set("ten"), await set("5000")];
    });
    expect(codes).toEqual([CHECK, CHECK, CHECK, null]);
  });

  it("a vendor value outside the flag's list, an unknown flag and another override are rejected", async () => {
    const codes = await asRole(url, "admin_api", async (s) => [
      await s.failure(
        "update public.feature_flags set value = 'sociavault' where name = 'TT_VENDOR_ROUTE' and scope = ''",
      ),
      await s.failure(
        "update public.feature_flags set value = null where name = 'IG_VENDOR_ROUTE' and scope = ''",
      ),
      await s.failure(
        "insert into public.feature_flags (name, value, changed_by, reason) values ('FALLBACK', 'off', 't', 'test')",
      ),
      await s.failure(
        "insert into public.feature_flags (name, scope, value, changed_by, reason) values ('TT_VENDOR_ROUTE', 'tt-keyword-search', 'off', 't', 'test')",
      ),
      await s.failure(
        "update public.feature_flags set value = 'tikhub' where name = 'TT_VENDOR_ROUTE' and scope = ''",
      ),
    ]);
    expect(codes).toEqual([CHECK, CHECK, CHECK, CHECK, null]);
  });

  it("credentials: owner_not_verified is never healthy, and a vendor row names a known vendor", async () => {
    const vendor = (
      name: string,
      role: string,
      rank: number,
      state: string,
      reason: string | null,
    ) =>
      `insert into public.credentials (owner_kind, owner_name, role, fallback_rank, state, reason)
       values ('vendor', '${name}', '${role}', ${rank}, '${state}', ${reason === null ? "null" : `'${reason}'`})`;
    const codes = await as("service_role", async (s) => [
      await s.failure(vendor("tikhub", "test_role", 1, "ok", "owner_not_verified")),
      await s.failure(vendor("brightdata", "test_role", 1, "ok", null)),
      await s.failure(vendor("tikhub", "test_role", 1, "degraded", "owner_not_verified")),
      await s.failure(vendor("ensembledata", "test_role", 1, "ok", null)),
      await s.failure(
        "insert into public.credentials (owner_kind, owner_name, platform) values ('client', 'x-app', 'x')",
      ),
    ]);
    expect(codes).toEqual([CHECK, CHECK, null, UNIQUE, CHECK]);
  });
});

describe("budgets", () => {
  it("a budget tag or sub-counter with a placeholder or a wildcard is rejected", async () => {
    const insert = (tag: string, sub: string) =>
      `insert into public.budgets (budget_tag, sub_counter, period_start, unit, period, reset_rule)
       values ('${tag}', '${sub}', '1970-01-01', 'requests', 'month', 'calendar_month')`;
    const codes = await as("service_role", async (s) => [
      await s.failure(insert("meta_graph_pages:<client_id>", "")),
      await s.failure(insert("fb_vendor", "service:*")),
      await s.failure(insert("ig_hashtag_*", "")),
      await s.failure(insert(`meta_graph_pages:${CLIENT}`, "")),
      await s.failure(insert("fb_vendor", `source:${SOURCE}`)),
    ]);
    expect(codes).toEqual([CHECK, CHECK, CHECK, null, null]);
  });

  it("the X read ledger keeps users as keyed references only", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        "insert into public.x_read_ledger (utc_day, resource_type, resource_id) values ('2026-10-26', 'user', '1842390117700000001')",
      ),
      await s.failure(
        `insert into public.x_read_ledger (utc_day, resource_type, resource_id) values ('2026-10-26', 'user', '${REF}')`,
      ),
      await s.failure(
        "insert into public.x_read_ledger (utc_day, resource_type, resource_id) values ('2026-10-26', 'post', '1842390117700000001')",
      ),
    ]);
    expect(codes).toEqual([CHECK, null, null]);
  });
});

describe("keywords (Question 9)", () => {
  const keyword = (client: string, purpose: string) =>
    `insert into public.keywords (client_id, label, forms, purpose) values ('${client}', 'k', '[]', '${purpose}')`;

  it("a government client's keyword is for reputation or service quality only", async () => {
    const codes = await as("admin_api", async (s) => [
      await s.failure(keyword(GOV, "brand")),
      await s.failure(keyword(GOV, "reputation")),
      await s.failure(keyword(CLIENT, "competitor")),
      await s.failure(keyword(CLIENT, "other")),
    ]);
    expect(codes).toEqual([CHECK, null, null, CHECK]);
  });

  it("a new keyword waits for screening", async () => {
    const rows = await as("admin_api", (s) =>
      s.rows<{ screening_status: string }>(
        `${keyword(CLIENT, "brand")} returning screening_status`,
      ),
    );
    expect(rows[0]?.screening_status).toBe("pending");
  });

  it("a client with a brand keyword cannot become a government client", async () => {
    const codes = await as("admin_api", async (s) => [
      await s.failure(keyword(CLIENT, "brand")),
      await s.failure(
        `update public.clients set client_type = 'government', accepts_amber = false where client_id = '${CLIENT}'`,
      ),
    ]);
    expect(codes).toEqual([null, CHECK]);
  });
});

describe("comments (A28)", () => {
  it("comment_state has no text or author column", async () => {
    const columns = await inRollback(url, async (s) =>
      (
        await s.rows<{ column_name: string }>(
          "select column_name from information_schema.columns where table_schema = 'public' and table_name = 'comment_state'",
        )
      ).map((r) => r.column_name),
    );
    expect(columns.length).toBeGreaterThan(0);
    for (const column of columns) expect(column).not.toMatch(/text|author|name|handle|body/);
  });

  it("a third lane is rejected", async () => {
    const insert = (lane: string) =>
      `insert into public.comment_series (item_id, lane, source_id, route, profile, anchor_at, status)
       values ('${KEYWORD}', '${lane}', '${SOURCE}', 'green', 'x', now(), 'scheduled')`;
    const codes = await as("service_role", async (s) => [
      await s.failure(insert("comments")),
      await s.failure(insert("metrics")),
      await s.failure(insert("replies")),
    ]);
    expect(codes).toEqual([null, null, CHECK]);
  });
});

describe("backfill runs", () => {
  it("a capped run names its reason, and a keyword history run is the client's or the add's", async () => {
    const run = (n: number, kind: string, reason: string, status: string, capped: string | null) =>
      `insert into public.backfill_runs (run_id, source_id, service, job_kind, reason, window_start,
         window_end, cap, status, capped_reason)
       values ('${ULID(40 + n)}', '${SOURCE}', 'x-full-archive-search', '${kind}', '${reason}',
               now() - interval '90 days', now(), '{"max_age_days": 90, "max_items": null}',
               '${status}', ${capped === null ? "null" : `'${capped}'`})`;
    const codes = await as("service_role", async (s) => [
      await s.failure(run(1, "backfill", "add", "capped", null)),
      await s.failure(run(2, "backfill", "add", "capped", "budget")),
      await s.failure(run(3, "keyword_history", "ops", "pending", null)),
      await s.failure(run(4, "keyword_history", "client", "pending", null)),
    ]);
    expect(codes).toEqual([CHECK, null, CHECK, null]);
  });
});

describe("news (A29)", () => {
  it("news_urls accepts duplicate_canonical", async () => {
    const code = await as("service_role", (s) =>
      s.failure(
        `insert into public.news_urls (url_hash, source_id, url, found_via, status)
         values ('${REF}', '${SOURCE}', 'https://example.iq/a/1', 'feed', 'duplicate_canonical')`,
      ),
    );
    expect(code).toBeNull();
  });

  it("a news site row exists before its source", async () => {
    const code = await as("service_role", (s) =>
      s.failure(
        `insert into public.news_sites (source_id, host, access_mode)
         values ('00000000-0000-4000-8000-00000000ffff', 'example-daily.iq', 'direct')`,
      ),
    );
    expect(code).toBeNull();
  });

  it("crawl_policies has no slot column", async () => {
    const columns = await inRollback(url, async (s) =>
      (
        await s.rows<{ column_name: string }>(
          "select column_name from information_schema.columns where table_schema = 'public' and table_name = 'crawl_policies'",
        )
      ).map((r) => r.column_name),
    );
    expect(columns).toContain("host");
    expect(columns.filter((c) => c.includes("slot"))).toEqual([]);
  });
});

describe("retention and deletions", () => {
  it("a deletion request holds a handle or its reference, never both", async () => {
    const codes = await as("service_role", async (s) => [
      await s.failure(
        `insert into public.deletion_requests (request_id, requester_contact, subject_handle, author_ref)
         values ('${ULID(60)}', 'contact', 'someone', '${REF}')`,
      ),
      await s.failure(
        `insert into public.deletion_requests (request_id, requester_contact, subject_handle)
         values ('${ULID(61)}', 'contact', 'someone')`,
      ),
    ]);
    expect(codes).toEqual([CHECK, null]);
  });

  it("only an item-scope deletion carries a retention class", async () => {
    const insert = (scope: string, cls: string) =>
      `insert into public.deletion_propagations (deletion_id, reason, scope, mode, retention_class, signal_at, due_at)
       values ('del:author_request:${scope}:${REF}', 'author_request', '${scope}', 'delete', ${cls}, now(), now())`;
    const codes = await as("service_role", async (s) => [
      await s.failure(insert("author", "'x_24h_sync'")),
      await s.failure(insert("item", "'x_24h_sync'")),
    ]);
    expect(codes).toEqual([CHECK, null]);
  });

  it("permitted_uses names a known platform, vendor or news host", async () => {
    const insert = (kind: string, subject: string) =>
      `insert into public.permitted_uses (subject_kind, subject, use, allowed, clause, set_by)
       values ('${kind}', '${subject}', 'train', false, 'test clause', 't')`;
    const codes = await as("admin_api", async (s) => [
      await s.failure(insert("platform", "YouTube")),
      await s.failure(insert("vendor", "brightdata")),
      await s.failure(insert("news_host", "Example.IQ")),
      await s.failure(insert("platform", "disqus")),
      await s.failure(insert("news_host", "example.iq")),
    ]);
    expect(codes).toEqual([CHECK, CHECK, CHECK, null, null]);
  });
});

describe("analysis and alerts (A27)", () => {
  it("a second active version of a task is rejected", async () => {
    const version = (v: string) =>
      `insert into public.model_versions (task, model_version, service, status, artefact_path)
       values ('sentiment', '${v}', 'analysis-sentiment', 'active', 'models/sentiment/${v}/')`;
    const codes = await as("service_role", async (s) => [
      await s.failure(version("v1")),
      await s.failure(version("v2")),
    ]);
    expect(codes).toEqual([null, UNIQUE]);
  });

  it("a government client's alert rule is one of the government types", async () => {
    const rule = (client: string, type: string) =>
      `insert into public.alert_rules (client_id, type, scope, severity)
       values ('${client}', '${type}', 'keyword', 'info')`;
    const codes = await as("admin_api", async (s) => [
      await s.failure(rule(GOV, "topic_spike")),
      await s.failure(rule(GOV, "negative_share")),
      await s.failure(rule(CLIENT, "topic_spike")),
    ]);
    expect(codes).toEqual([CHECK, null, null]);
  });
});
