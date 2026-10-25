// Shared by the TypeScript suites: the fixtures under fixtures/contracts/ are the record both
// languages test against.
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const FIXTURES_DIR = fileURLToPath(new URL("../../../fixtures/contracts/", import.meta.url));
export const PACKAGE_DIR = fileURLToPath(new URL("../", import.meta.url));

export function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8")) as unknown;
}

// Golden files are plain JSON; each suite casts one to the interface it reads.
export function golden<T>(name: string): T {
  return readJson(`${FIXTURES_DIR}golden/${name}`) as T;
}

export function listJson(dir: string): string[] {
  try {
    return readdirSync(dir)
      .filter((f) => f.endsWith(".json") && f !== "expected.json")
      .sort();
  } catch {
    return [];
  }
}

export const utf8 = (s: string): Uint8Array => new TextEncoder().encode(s);
