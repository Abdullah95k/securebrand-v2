// A31 (ADR-0069 (e); S2, S8): audit and evidence rows hold ids, hashes, reasons and timestamps
// only: no column named for content or a clear identity, and no identity in registry_audit's
// before and after snapshots.
import { describe, expect, it } from "vitest";
import { asRole, withClient } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const url = testDatabaseUrl();
const AUDIT_TABLES = [
  "registry_audit",
  "canary_audit",
  "retention_audit",
  "x_compliance_audit",
  "admin_audit",
];
const CONTENT =
  /^(text|.*_text|body|content|title|.*handle.*|name|display_name|.*_name|url|.*_url|username|email|phone)$/;

const audit = (snapshot: string) =>
  `insert into public.registry_audit (decision_id, decision, action, actor, source_id, after)
   values ('01K00000000000000000000H01', 'update', 'applied', 'registry-writer',
           '00000000-0000-4000-8000-000000000001', '${snapshot}')`;

describe("audit and evidence rows", () => {
  it("no audit table has a text, handle, name or url column", async () => {
    const columns = await withClient(
      url,
      async (c) =>
        (
          await c.query<{ table_name: string; column_name: string }>(
            `select table_name, column_name from information_schema.columns
           where table_schema = 'public' and table_name = any ($1)`,
            [AUDIT_TABLES],
          )
        ).rows,
    );
    expect(new Set(columns.map((c) => c.table_name))).toEqual(new Set(AUDIT_TABLES));
    expect(columns.filter((c) => CONTENT.test(c.column_name))).toEqual([]);
  });

  it("a registry_audit row whose after holds a handle, a url, a name or notes is rejected", async () => {
    const codes = await asRole(url, "service_role", async (s) => [
      await s.failure(audit('{"handle": "baghdad_eats"}')),
      await s.failure(audit('{"url": "https://instagram.com/baghdad_eats"}')),
      await s.failure(audit('{"display_name": "Baghdad Eats"}')),
      await s.failure(audit('{"notes": "added at the client\'\'s request"}')),
      await s.failure(audit('{"handle_sha256": "not a hash"}')),
    ]);
    expect(codes).toEqual(["23514", "23514", "23514", "23514", "23514"]);
  });

  it("a registry_audit row whose country_signals keeps signal_evidence is rejected", async () => {
    const code = await asRole(url, "service_role", (s) =>
      s.failure(
        audit(
          '{"country_signals": {"phone_964": true, "signal_evidence": [{"signal": "phone_964", "matched": "+964 770 000 0000", "where": "bio"}]}}',
        ),
      ),
    );
    expect(code).toBe("23514");
  });

  it("a registry_audit row with hashed identities and the policy columns is accepted", async () => {
    const hash = "d".repeat(64);
    const code = await asRole(url, "service_role", (s) =>
      s.failure(
        audit(
          `{"handle_sha256": "${hash}", "url_sha256": "${hash}", "display_name_sha256": "${hash}", "tier": 2, "country_signals": {"iraqi_place": true, "platform_country_iq": false, "phone_964": false, "iq_domain": false, "outlet_link": false, "seed_list": false}}`,
        ),
      ),
    );
    expect(code).toBeNull();
  });
});
