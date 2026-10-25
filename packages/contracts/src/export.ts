// The generated artefacts under packages/contracts/schemas/: the JSON Schema of every schema id
// (Zod's own exporter, draft 2020-12; ADR-0030), and the patterns and closed lists the Python package
// reads, so the two languages cannot drift. Prettier formats each file as `pnpm fmt:check` expects.
import { fileURLToPath } from "node:url";
import { format, resolveConfig } from "prettier";
import { PATTERNS } from "./primitives.ts";
import * as vocabulary from "./vocabulary.ts";

export const SCHEMAS_DIR = fileURLToPath(new URL("../schemas/", import.meta.url));

function patternsArtefact(): Record<string, string> {
  return Object.fromEntries(Object.entries(PATTERNS).map(([name, re]) => [name, re.source]));
}

function vocabularyArtefact(): Record<string, readonly (string | number)[]> {
  const lists: [string, readonly (string | number)[]][] = [];
  for (const [name, value] of Object.entries(vocabulary)) {
    const list: readonly (string | number)[] = value;
    lists.push([name, list]);
  }
  return Object.fromEntries(lists.sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
}

/** Every artefact as its relative path and the exact text committed under schemas/. */
export async function exportArtefacts(): Promise<Map<string, string>> {
  const raw = new Map<string, unknown>([
    ["patterns.json", patternsArtefact()],
    ["vocabulary.json", vocabularyArtefact()],
  ]);
  const out = new Map<string, string>();
  for (const [path, value] of raw) {
    const filepath = `${SCHEMAS_DIR}${path}`;
    const options = (await resolveConfig(filepath)) ?? {};
    out.set(path, await format(JSON.stringify(value), { ...options, filepath }));
  }
  return out;
}
