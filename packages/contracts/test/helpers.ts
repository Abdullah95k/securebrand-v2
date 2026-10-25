// Shared by the TypeScript suites: the fixtures under fixtures/contracts/ are the record both
// languages test against.
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import type { ValidateOptions } from "../src/validate.ts";

export const FIXTURES_DIR = fileURLToPath(new URL("../../../fixtures/contracts/", import.meta.url));
export const PACKAGE_DIR = fileURLToPath(new URL("../", import.meta.url));
export const REPO_DIR = fileURLToPath(new URL("../../../", import.meta.url));

export function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8")) as unknown;
}

// Golden files are plain JSON; each suite casts one to the interface it reads.
export function golden<T>(name: string): T {
  return readJson(`${FIXTURES_DIR}golden/${name}`) as T;
}

// The sidecars of a fixture directory are not fixtures.
const SIDECARS = new Set(["expected.json", "options.json"]);

export function listJson(dir: string): string[] {
  try {
    return readdirSync(dir)
      .filter((f) => f.endsWith(".json") && !SIDECARS.has(f))
      .sort();
  } catch {
    return [];
  }
}

export const utf8 = (s: string): Uint8Array => new TextEncoder().encode(s);

export type FixtureKind = "valid" | "invalid" | "tolerant";
export type Path = (string | number)[];

export interface Fixture {
  /** `<schema dir>/<kind>/<file>`, for test names. */
  readonly name: string;
  readonly file: string;
  readonly value: unknown;
  /** The queue and client type a fixture is validated with (options.json and expected.json). */
  readonly options: ValidateOptions;
  /** For an invalid fixture: the path of the error it must raise, and the rule it breaks. */
  readonly expected?: { readonly path: Path; readonly rule: string };
}

/** Every schema directory: `<topic>/v1`, `job/v1`, and `dlq/v1` for the shared dlq.<service>/v1. */
export function schemaDirs(): string[] {
  const out: string[] = [];
  for (const topic of readdirSync(FIXTURES_DIR, { withFileTypes: true })) {
    if (!topic.isDirectory() || topic.name === "golden") continue;
    for (const version of readdirSync(`${FIXTURES_DIR}${topic.name}`)) {
      out.push(`${topic.name}/${version}`);
    }
  }
  return out.sort();
}

/** The catalogue id a schema directory holds. */
export function schemaIdOf(dir: string): string {
  return dir === "dlq/v1" ? "dlq.<service>/v1" : dir;
}

interface Sidecar {
  path?: Path;
  rule?: string;
  queue?: string;
  client_type?: "commercial" | "government";
}

function readSidecar(path: string): Record<string, Sidecar> {
  return existsSync(path) ? (readJson(path) as Record<string, Sidecar>) : {};
}

function optionsOf(entry: Sidecar | undefined): ValidateOptions {
  const options: { queue?: string; clientType?: "commercial" | "government" } = {};
  if (entry?.queue !== undefined) options.queue = entry.queue;
  if (entry?.client_type !== undefined) options.clientType = entry.client_type;
  return options;
}

export function fixtures(dir: string, kind: FixtureKind): Fixture[] {
  const base = `${FIXTURES_DIR}${dir}/${kind}/`;
  const sidecar = readSidecar(`${base}${kind === "invalid" ? "expected.json" : "options.json"}`);
  return listJson(base).map((file) => {
    const entry = sidecar[file];
    const fixture: Fixture = {
      name: `${dir}/${kind}/${file}`,
      file,
      value: readJson(`${base}${file}`),
      options: optionsOf(entry),
    };
    if (kind === "invalid") {
      if (entry?.path === undefined || entry.rule === undefined) {
        throw new Error(`${fixture.name} has no entry in expected.json`);
      }
      return { ...fixture, expected: { path: entry.path, rule: entry.rule } };
    }
    return fixture;
  });
}

/** One fixture by name, for the unit suites. */
export function fixture(dir: string, kind: FixtureKind, file: string): Fixture {
  const found = fixtures(dir, kind).find((f) => f.file === file);
  if (!found) throw new Error(`no fixture ${dir}/${kind}/${file}`);
  return found;
}

/** A deep copy of a fixture's value as a plain JSON object, for a test to change. */
export function copyOf(f: Fixture): Record<string, unknown> {
  return structuredClone(f.value) as Record<string, unknown>;
}

export const samePath = (a: Path, b: Path): boolean => JSON.stringify(a) === JSON.stringify(b);
