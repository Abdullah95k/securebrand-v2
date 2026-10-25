// The registries are JSON data shared with the Python package, so the two languages cannot drift.
// They are read from packages/contracts/registries/, two levels above this file in src/ and dist/.
import { readFileSync } from "node:fs";

export function loadRegistry(name: string): unknown {
  return JSON.parse(readFileSync(new URL(`../../registries/${name}`, import.meta.url), "utf8")) as unknown;
}
