// A32 (plan T4, S11): the seed files hold only synthetic data and set no password: every client
// and source they write is named synthetic, every address is at example.invalid, no statement
// names a password or an encrypted_password, nothing looks like a token, and supabase/config.toml
// loads exactly the two seed files, the synthetic one first.
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { SEEDS_DIR, SUPABASE_DIR } from "../../tools/paths.ts";

const SEEDS = ["synthetic.sql", "local-auth.sql"];

/** A seed file without its comments: what the database runs. */
const code = (file: string): string =>
  readFileSync(join(SEEDS_DIR, file), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/--[^\n]*/g, "");

/** The values a seed inserts into `column` of `table`, from its insert statements. */
function inserted(sql: string, table: string, column: string): string[] {
  const out: string[] = [];
  const statement = new RegExp(
    `insert into public\\.${table}\\s*\\(([^)]*)\\)\\s*values\\s*([\\s\\S]*?)\\bon conflict`,
    "gi",
  );
  for (const m of sql.matchAll(statement)) {
    const index = (m[1] ?? "")
      .split(",")
      .map((c) => c.trim())
      .indexOf(column);
    if (index < 0) continue;
    for (const tuple of (m[2] ?? "").matchAll(/\(((?:[^()']|'(?:[^']|'')*'|\([^()]*\))*)\)/g)) {
      const values = [...(tuple[1] ?? "").matchAll(/'((?:[^']|'')*)'|([^,\s][^,]*)/g)].map(
        (v) => v[1] ?? v[2]?.trim() ?? "",
      );
      out.push(values[index] ?? "");
    }
  }
  return out;
}

// The token shapes scripts/check-fixtures.sh refuses under fixtures/, which it does not scan here.
const TOKENS: [string, RegExp][] = [
  ["a Meta access token", /EAA[A-Za-z0-9]{20,}/],
  ["a Google API key", /AIza[0-9A-Za-z_-]{35}/],
  ["a JWT", /eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/],
  ["a bearer token", /[Bb]earer\s+[A-Za-z0-9._~+/=-]{20,}/],
  ["an AWS access key", /(AKIA|ASIA)[0-9A-Z]{16}/],
  ["a Telegram bot token", /[0-9]{8,10}:[A-Za-z0-9_-]{35}/],
];

describe("seed files", () => {
  it("supabase/config.toml loads exactly the two seed files", () => {
    expect(readdirSync(SEEDS_DIR).sort()).toEqual([...SEEDS].sort());
    const config = readFileSync(join(SUPABASE_DIR, "config.toml"), "utf8");
    const paths = /^\[db\.seed\][\s\S]*?^sql_paths\s*=\s*\[([^\]]*)\]/m.exec(config)?.[1] ?? "";
    expect([...paths.matchAll(/"([^"]+)"/g)].map((m) => m[1])).toEqual(
      SEEDS.map((f) => `./seeds/${f}`),
    );
  });

  it("the seed files name only synthetic clients and users", () => {
    const synthetic = code("synthetic.sql");
    const clients = inserted(synthetic, "clients", "name");
    expect(clients).toHaveLength(2);
    for (const name of clients) expect(name).toMatch(/^synthetic-[a-z0-9-]+$/);
    const handles = inserted(synthetic, "sources", "handle");
    expect(handles.length).toBeGreaterThanOrEqual(12);
    for (const handle of handles) expect(handle).toMatch(/^(synthetic[a-z0-9_.-]*|null)$/);
    for (const name of inserted(synthetic, "sources", "display_name"))
      expect(name).toMatch(/^(Synthetic [A-Za-z0-9 ]+|null)$/);
    for (const url of inserted(synthetic, "sources", "url"))
      expect(url).toMatch(/^(https:\/\/[a-z0-9.-]+\.example\.invalid\/[A-Za-z0-9_./-]*|null)$/);
    for (const file of SEEDS)
      for (const address of code(file).match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+/g) ?? [])
        expect(address, file).toMatch(/^synthetic-[a-z0-9-]+@example\.invalid$/);
    expect(inserted(code("local-auth.sql"), "client_members", "role")).toEqual([
      "client_viewer",
      "client_viewer",
    ]);
  });

  it("no seed file sets a password or encrypted_password", () => {
    for (const file of SEEDS) {
      const sql = code(file);
      expect(sql, file).not.toMatch(/password|crypt\s*\(|gen_salt/i);
      for (const [kind, pattern] of TOKENS)
        expect(pattern.test(sql), `${file}: ${kind}`).toBe(false);
    }
    expect(code("synthetic.sql")).not.toMatch(/\bauth\./);
  });
});
