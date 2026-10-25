// The generated artefacts under packages/contracts/schemas/: the JSON Schema of every schema id
// (Zod's own exporter, draft 2020-12; ADR-0030), and the patterns and closed lists the Python package
// reads, so the two languages cannot drift. Prettier formats each file as `pnpm fmt:check` expects.
import { fileURLToPath } from "node:url";
import { format, resolveConfig } from "prettier";
import { z } from "zod";
import type { SchemaMeta } from "./builder.ts";
import { CATALOGUE, exportCatalogue } from "./catalogue.ts";
import { REPORT_KIND_FIELDS } from "./jobs-completed.ts";
import { PATTERNS } from "./primitives.ts";
import * as vocabulary from "./vocabulary.ts";

export const SCHEMAS_DIR = fileURLToPath(new URL("../schemas/", import.meta.url));

/** The directory name of a schema id: the id itself, the shared dlq.<service>/v1 as dlq/v1. */
const dirName = (id: string): string => (id === "dlq.<service>/v1" ? "dlq/v1" : id);

/** The committed JSON Schema of a schema id, relative to schemas/. */
export function schemaFile(id: string): string {
  return `${dirName(id)}.json`;
}

/** The generated Python module of a schema id, under listening_contracts/models/{strict,consumer}/. */
export function pythonModule(id: string): string {
  return dirName(id).replace(/[./]/g, "_");
}

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

/** The class name of a schema id's root model: the title its schema exports (RawItemsV1). */
export function rootTitle(id: string): string {
  return pythonModule(id)
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

/**
 * What the Python validator reads of the catalogue: each schema id, its class (data or control,
 * ADR-0003), its files and root class, and the kind fields of a jobs.completed report (ADR-0017).
 */
function catalogueArtefact(): unknown {
  return {
    schemas: CATALOGUE.map((e) => ({
      id: e.id,
      class: e.class,
      file: schemaFile(e.id),
      module: pythonModule(e.id),
      title: rootTitle(e.id),
    })),
    report_kind_fields: REPORT_KIND_FIELDS,
  };
}

/**
 * The producer variant of every schema id as JSON Schema draft 2020-12, its shared definitions under
 * `$defs` and its branches titled, so the Python generator names the classes after them. A construct
 * JSON Schema cannot carry throws rather than export a weaker schema (ADR-0030).
 */
function schemaArtefacts(): Map<string, unknown> {
  const registry = z.registry<SchemaMeta>();
  const out = new Map<string, unknown>();
  for (const [id, schema] of exportCatalogue(registry)) {
    out.set(
      schemaFile(id),
      z.toJSONSchema(schema, {
        target: "draft-2020-12",
        metadata: registry,
        unrepresentable: "throw",
      }),
    );
  }
  return out;
}

/** Every artefact as its relative path and the exact text committed under schemas/. */
export async function exportArtefacts(): Promise<Map<string, string>> {
  const raw = new Map<string, unknown>([
    ["catalogue.json", catalogueArtefact()],
    ["patterns.json", patternsArtefact()],
    ["vocabulary.json", vocabularyArtefact()],
    ...schemaArtefacts(),
  ]);
  const out = new Map<string, string>();
  for (const [path, value] of raw) {
    const filepath = `${SCHEMAS_DIR}${path}`;
    const options = (await resolveConfig(filepath)) ?? {};
    out.set(path, await format(JSON.stringify(value), { ...options, filepath }));
  }
  return out;
}
