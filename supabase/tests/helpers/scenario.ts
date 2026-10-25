// A row-level security scenario: inside one transaction that is rolled back, the owner writes two
// synthetic clients with one row each in every client-facing table, plus the Auth users and
// memberships A6 and A38 need; the test then takes a role and a user and reads.
import type pg from "pg";
import type { Role, Session } from "./db.ts";
import { session, withClient } from "./db.ts";

export const CLIENT_A = "00000000-0000-4000-8000-0000000000a1";
export const CLIENT_B = "00000000-0000-4000-8000-0000000000b1";
export const USER_A = "00000000-0000-4000-8000-0000000000a2"; // client_viewer of A
export const USER_B = "00000000-0000-4000-8000-0000000000b2"; // client_admin of B
export const USER_MANAGER = "00000000-0000-4000-8000-0000000000c2"; // account_manager of A
export const USER_OPS = "00000000-0000-4000-8000-0000000000d2"; // ops (global)
export const SOURCE_A = "00000000-0000-4000-8000-0000000000a3";
export const SOURCE_B = "00000000-0000-4000-8000-0000000000b3";
export const SOURCE_SHARED = "00000000-0000-4000-8000-0000000000e3";
export const RULE_A = "00000000-0000-4000-8000-0000000000a4";
export const RULE_B = "00000000-0000-4000-8000-0000000000b4";

const SETUP = `
insert into auth.users (id, email) values
  ('${USER_A}', 'rls-user-a@example.invalid'), ('${USER_B}', 'rls-user-b@example.invalid'),
  ('${USER_MANAGER}', 'rls-manager@example.invalid'), ('${USER_OPS}', 'rls-ops@example.invalid');
insert into public.clients (client_id, name, client_type) values
  ('${CLIENT_A}', 'synthetic-rls-a', 'commercial'), ('${CLIENT_B}', 'synthetic-rls-b', 'commercial');
insert into public.client_members (user_id, client_id, role, added_by) values
  ('${USER_A}', '${CLIENT_A}', 'client_viewer', 'rls-test'),
  ('${USER_B}', '${CLIENT_B}', 'client_admin', 'rls-test'),
  ('${USER_MANAGER}', '${CLIENT_A}', 'account_manager', 'rls-test'),
  ('${USER_OPS}', null, 'ops', 'rls-test');
insert into public.client_settings (client_id, service, settings) values
  ('${CLIENT_A}', 'qualifier', '{}'), ('${CLIENT_B}', 'qualifier', '{}');
insert into public.sources (source_id, platform, source_type, platform_id, route, tier,
    retention_class, client_ids, added_by) values
  ('${SOURCE_A}', 'x', 'account', 'rls-a', 'green', 3, 'x_24h_sync', '{${CLIENT_A}}', 'ops'),
  ('${SOURCE_B}', 'x', 'account', 'rls-b', 'green', 3, 'x_24h_sync', '{${CLIENT_B}}', 'ops'),
  ('${SOURCE_SHARED}', 'x', 'account', 'rls-shared', 'green', 3, 'x_24h_sync',
   '{${CLIENT_A},${CLIENT_B}}', 'ops');
insert into public.client_sources (client_id, source_id, added_by) values
  ('${CLIENT_A}', '${SOURCE_A}', 'rls-test'), ('${CLIENT_B}', '${SOURCE_B}', 'rls-test'),
  ('${CLIENT_A}', '${SOURCE_SHARED}', 'rls-test'), ('${CLIENT_B}', '${SOURCE_SHARED}', 'rls-test');
insert into public.client_lists (client_id, list, candidate_key, added_by) values
  ('${CLIENT_A}', 'watch', 'x:rls_watch_a', 'rls-test'),
  ('${CLIENT_B}', 'watch', 'x:rls_watch_b', 'rls-test');
insert into public.keywords (client_id, label, forms, purpose) values
  ('${CLIENT_A}', 'rls-a', '[]', 'brand'), ('${CLIENT_B}', 'rls-b', '[]', 'brand');
insert into public.taxonomy_nodes (taxonomy_id, node_id, status) values
  ('global', 'rls-global', 'zero_shot'), ('${CLIENT_A}', 'rls-a', 'zero_shot'),
  ('${CLIENT_B}', 'rls-b', 'zero_shot');
insert into public.kb_entities (entity_id, type, scope, status) values
  ('rls-global', 'brand', 'global', 'active'), ('rls-a', 'brand', '${CLIENT_A}', 'active'),
  ('rls-b', 'brand', '${CLIENT_B}', 'active');
insert into public.brand_assets (brand_id, client_id, name, object_prefix, status) values
  ('rls-a', '${CLIENT_A}', 'Synthetic A', 'brands/rls-a/', 'active'),
  ('rls-b', '${CLIENT_B}', 'Synthetic B', 'brands/rls-b/', 'active');
insert into public.alert_rules (rule_id, client_id, type, scope, severity) values
  ('${RULE_A}', '${CLIENT_A}', 'volume_spike', 'keyword', 'info'),
  ('${RULE_B}', '${CLIENT_B}', 'volume_spike', 'keyword', 'info');
insert into public.alerts (alert_id, rule_id, client_id, fingerprint, window_key) values
  ('01K00000000000000000000A01', '${RULE_A}', '${CLIENT_A}', 'rls-a', 'w'),
  ('01K00000000000000000000B01', '${RULE_B}', '${CLIENT_B}', 'rls-b', 'w');
`;

/**
 * For each client-facing table, the query a client user runs and the owners of the rows it should
 * see: a client id, or "global" for the shared rows of the knowledge tables.
 */
export const CLIENT_READS: Record<string, string> = {
  clients: "select client_id::text as owner from public.clients",
  client_settings: "select client_id::text as owner from public.client_settings",
  client_lists: "select client_id::text as owner from public.client_lists",
  keywords: "select client_id::text as owner from public.keywords",
  taxonomy_nodes: "select taxonomy_id as owner from public.taxonomy_nodes",
  kb_entities: "select scope as owner from public.kb_entities",
  brand_assets: "select client_id::text as owner from public.brand_assets",
  alert_rules: "select client_id::text as owner from public.alert_rules",
  alerts: "select client_id::text as owner from public.alerts",
  client_sources: "select client_id::text as owner from public.client_sources",
  sources: "select source_id::text as owner from public.sources",
};

/**
 * Runs `fn` as `role` with `sub` after the owner has written the scenario, inside a transaction
 * that is rolled back.
 */
export async function scenario<T>(
  url: string,
  role: Role,
  sub: string | undefined,
  fn: (s: Session) => Promise<T>,
): Promise<T> {
  return withClient(url, async (client: pg.Client) => {
    await client.query("begin");
    try {
      await client.query(SETUP);
      const claims = JSON.stringify(sub === undefined ? { role } : { role, sub });
      await client.query("select set_config('request.jwt.claims', $1, true)", [claims]);
      if (role !== "postgres") await client.query(`set local role ${role}`);
      return await fn(session(client));
    } finally {
      await client.query("rollback");
    }
  });
}
