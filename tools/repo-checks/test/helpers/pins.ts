// Readers for the files that pin versions, shared by the pins and stack tests.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT } from "./repo.js";

export function readText(rel: string): string {
  return readFileSync(join(ROOT, rel), "utf8");
}

/** KEY=VALUE lines of an env file, comments and blank lines ignored. */
export function readEnvFile(rel: string): Record<string, string> {
  const vars: Record<string, string> = {};
  for (const raw of readText(rel).split("\n")) {
    const line = raw.trim();
    if (line === "" || line.startsWith("#")) {
      continue;
    }
    const eq = line.indexOf("=");
    if (eq > 0) {
      vars[line.slice(0, eq)] = line.slice(eq + 1);
    }
  }
  return vars;
}

/** The [tool.uv] required-version of a pyproject.toml, or of uv.toml. */
export function requiredUv(text: string): string | undefined {
  return /^required-version\s*=\s*"([^"]+)"/m.exec(text)?.[1];
}

/** True when an exact x.y.z version satisfies a ">=a.b.c,<d.e" or ">=a.b.c <d" range. */
export function satisfies(version: string, range: string): boolean {
  const parts = range.split(/[,\s]+/).filter(Boolean);
  return parts.every((part) => {
    const match = /^(>=|<=|<|>|==)?(\d+(?:\.\d+)*)$/.exec(part);
    if (!match?.[2]) {
      return false;
    }
    const cmp = compare(version, match[2]);
    switch (match[1]) {
      case ">=":
        return cmp >= 0;
      case ">":
        return cmp > 0;
      case "<=":
        return cmp <= 0;
      case "<":
        return cmp < 0;
      default:
        return cmp === 0;
    }
  });
}

function compare(a: string, b: string): number {
  const pa = a.split(".").map(Number);
  const pb = b.split(".").map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i += 1) {
    const diff = (pa[i] ?? 0) - (pb[i] ?? 0);
    if (diff !== 0) {
      return diff;
    }
  }
  return 0;
}
