// RFC 8785 canonical JSON, through the `canonicalize` library; values JSON cannot carry are refused
// first, where the library would drop or rewrite them.
import canonicalize from "canonicalize";
import { ContractError } from "./errors.ts";

function check(value: unknown, path: string): void {
  if (value === null || typeof value === "string" || typeof value === "boolean") return;
  if (typeof value === "number") {
    if (!Number.isFinite(value))
      throw new ContractError("not_json", `${path} is not a finite number`);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((v, i) => check(v, `${path}[${i}]`));
    return;
  }
  if (typeof value === "object" && Object.getPrototypeOf(value) === Object.prototype) {
    for (const [k, v] of Object.entries(value)) check(v, `${path}.${k}`);
    return;
  }
  throw new ContractError("not_json", `${path} is not a JSON value`);
}

export function canonicalJson(value: unknown): string {
  check(value, "$");
  const out = canonicalize(value);
  if (out === undefined) throw new ContractError("not_json", "$ is not a JSON value");
  return out;
}
