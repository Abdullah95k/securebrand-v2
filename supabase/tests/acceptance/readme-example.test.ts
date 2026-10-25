// A12 (Question 7): supabase/README.md shows a service reading its feature flag and its cursor
// row through pg with the generated row types. The README's example is examples/read-control.ts
// word for word; the workspace's typecheck (make check) covers that file, and here it runs against
// this checkout's test database.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { SUPABASE_DIR } from "../../tools/paths.ts";
import { withClient } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const EXAMPLE = join(SUPABASE_DIR, "examples/read-control.ts");

describe("the README example", () => {
  it("the README shows examples/read-control.ts", () => {
    const readme = readFileSync(join(SUPABASE_DIR, "README.md"), "utf8");
    const block = /```ts\n([\s\S]*?)```/.exec(readme)?.[1];
    expect(block).toBe(readFileSync(EXAMPLE, "utf8"));
  });

  it("the README example runs against the local stack", async () => {
    const url = testDatabaseUrl();
    await withClient(url, (c) =>
      c.query(
        `insert into public.cursors (service, scope_key, cursor, next_due_at)
         values ('fb-page-feed-poller', '', 'synthetic-cursor-1', '2026-10-26T06:00:00Z')`,
      ),
    );
    try {
      const r = spawnSync(process.execPath, [EXAMPLE], {
        cwd: SUPABASE_DIR,
        encoding: "utf8",
        env: { ...process.env, DATABASE_URL: url },
      });
      expect(r.status, r.stderr).toBe(0);
      expect(r.stdout).toContain("FB_VENDOR_ROUTE is off");
      expect(r.stdout).toContain("cursor synthetic-cursor-1, next due 2026-10-26 06:00:00+00");
    } finally {
      await withClient(url, (c) =>
        c.query(
          "delete from public.cursors where service = 'fb-page-feed-poller' and cursor = 'synthetic-cursor-1'",
        ),
      );
    }
  });
});
