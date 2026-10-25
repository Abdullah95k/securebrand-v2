// A10 (.claude/rules/contracts.md; ADR-0013): docs/contracts/TABLE-OWNERS.md has a section for
// every table F3 creates, naming exactly one writer for each column the live catalogue holds, and
// gives every sources column the owner ADR-0013 gives it: registry-writer for the identity, policy
// and health columns, the source type's primary poller (CONVENTIONS' primary poller table) for the
// rotation summary, backfill-orchestrator for backfill_status and keyword-matcher for last_hit_at.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { CONTRACTS_DIR, CONVENTIONS_FILE, TABLE_OWNERS_FILE } from "../../tools/paths.ts";
import { withClient } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const registry = JSON.parse(
  readFileSync(join(CONTRACTS_DIR, "registries/services.json"), "utf8"),
) as {
  platform_groups: Record<string, string[]>;
  shared_groups: Record<string, string[]>;
  d3_writers: string[];
};
const SERVICES = new Set([
  ...Object.values(registry.platform_groups).flat(),
  ...Object.values(registry.shared_groups).flat(),
]);
/** The writers a column may name: a service, a D3 writer, or one of the document's three terms. */
const WRITERS = new Set([
  ...SERVICES,
  ...registry.d3_writers,
  "migration",
  "row-owner",
  "primary-poller",
]);

interface Section {
  table: string;
  columns: Map<string, string[]>;
  lines: string[];
}

/** The `## \`<table>\`` sections of TABLE-OWNERS.md, each with its column table's writers. */
function sections(): Map<string, Section> {
  const out = new Map<string, Section>();
  let current: Section | undefined;
  for (const line of readFileSync(TABLE_OWNERS_FILE, "utf8").split("\n")) {
    const heading = /^## (.*)$/.exec(line);
    if (heading !== null) {
      const table = /^`([a-z_]+(?:\.[a-z_]+)?)`$/.exec(heading[1] ?? "")?.[1];
      current = table === undefined ? undefined : { table, columns: new Map(), lines: [] };
      if (current !== undefined) out.set(current.table, current);
      continue;
    }
    if (current === undefined) continue;
    current.lines.push(line);
    const row = /^\| `([a-z_0-9]+)` \| ([^|]*) \|/.exec(line);
    if (row?.[1] !== undefined) {
      const writers = current.columns.get(row[1]) ?? [];
      writers.push((row[2] ?? "").trim());
      current.columns.set(row[1], writers);
    }
  }
  return out;
}

/** Every base table F3 creates, with its columns, from the live catalogue. */
async function catalogue(): Promise<Map<string, string[]>> {
  return withClient(testDatabaseUrl(), async (c) => {
    const r = await c.query<{ name: string; columns: string[] }>(
      `select case when n.nspname = 'public' then c.relname else n.nspname || '.' || c.relname end as name,
              array_agg(a.attname::text order by a.attnum) as columns
       from pg_class c
       join pg_namespace n on n.oid = c.relnamespace
       join pg_attribute a on a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped
       where n.nspname in ('public', 'svc_migrations') and c.relkind in ('r', 'p')
       group by 1`,
    );
    return new Map(r.rows.map((row) => [row.name, row.columns]));
  });
}

/** The single backticked writer of a Writer cell, or the cell itself when it is anything else. */
const writerOf = (cell: string): string => /^`([a-z0-9-]+)`$/.exec(cell)?.[1] ?? cell;

describe("TABLE-OWNERS.md", () => {
  it("TABLE-OWNERS names one writer for every column the catalogue holds", async () => {
    const tables = await catalogue();
    const owners = sections();
    expect([...owners.keys()].sort()).toEqual([...tables.keys()].sort());
    for (const [table, columns] of tables) {
      const section = owners.get(table);
      expect([...(section?.columns.keys() ?? [])].sort(), `${table}: columns listed`).toEqual(
        [...columns].sort(),
      );
      for (const [column, cells] of section?.columns ?? []) {
        expect(cells, `${table}.${column}: listed once`).toHaveLength(1);
        const writer = writerOf(cells[0] ?? "");
        expect(WRITERS.has(writer), `${table}.${column}: writer ${cells[0]}`).toBe(true);
        if (writer === "row-owner")
          expect(
            columns.includes("service") || columns.includes("executor"),
            `${table}: a row-owner table names its service in each row`,
          ).toBe(true);
        if (writer === "primary-poller") expect(table, `${table}.${column}`).toBe("sources");
      }
    }
  });

  it("every sources column has the owner ADR-0013 gives", async () => {
    const columns = (await catalogue()).get("sources") ?? [];
    const section = sections().get("sources");
    const operational: Record<string, string> = {
      last_polled_at: "primary-poller",
      next_poll_at: "primary-poller",
      backfill_status: "backfill-orchestrator",
      last_hit_at: "keyword-matcher",
    };
    expect(columns.length).toBeGreaterThan(0);
    for (const column of columns)
      expect(writerOf(section?.columns.get(column)?.[0] ?? ""), `sources.${column}`).toBe(
        operational[column] ?? "registry-writer",
      );
  });

  it("the primary poller of every source type is the one CONVENTIONS names", () => {
    // CONVENTIONS: "| Source type | Primary poller |", one row per source type; the poller cell
    // names the poller, then references in parentheses or backticks.
    const conventions = readFileSync(CONVENTIONS_FILE, "utf8").split("\n");
    const start = conventions.findIndex((l) => /^\| Source type \| Primary poller \|/.test(l));
    expect(start).toBeGreaterThan(-1);
    const expected = new Map<string, string>();
    for (const line of conventions.slice(start + 2)) {
      if (!line.startsWith("|")) break;
      const [label, cell] = line
        .split("|")
        .slice(1, 3)
        .map((s) => s.trim());
      expect(label).toBeTruthy();
      expected.set(label ?? "", (cell ?? "").replace(/\([^)]*\)/g, "").replace(/`[^`]*`/g, ""));
    }
    // TABLE-OWNERS, under sources: "| CONVENTIONS source type | Rows | Primary poller |".
    const lines = sections().get("sources")?.lines ?? [];
    const head = lines.findIndex((l) => /^\| CONVENTIONS source type \|/.test(l));
    expect(head).toBeGreaterThan(-1);
    const named = new Map<string, string[]>();
    for (const line of lines.slice(head + 2)) {
      if (!line.startsWith("|")) break;
      const cells = line
        .split("|")
        .slice(1, -1)
        .map((s) => s.trim());
      const label = cells[0] ?? "";
      const poller = writerOf(cells.at(-1) ?? "");
      expect(SERVICES.has(poller), `${label}: ${poller} is a service`).toBe(true);
      expect(expected.get(label), `${label}: a CONVENTIONS source type`).toBeDefined();
      expect(
        new RegExp(`(^|[^a-z-])${poller}([^a-z-]|$)`).test(expected.get(label) ?? ""),
        `${label}: CONVENTIONS names ${poller}`,
      ).toBe(true);
      named.set(label, [...(named.get(label) ?? []), poller]);
    }
    expect([...named.keys()].sort()).toEqual([...expected.keys()].sort());
  });
});
