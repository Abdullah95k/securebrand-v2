// RFC 8785 canonical JSON, through the `canonicalize` library; values JSON cannot carry, and strings
// holding a lone surrogate, are refused first with the package's own errors, as in Python. Callers
// pass no numbers: integers beyond ±(2^53 - 1) are refused in Python and already rounded by
// JSON.parse here (review note 17).
import canonicalize from "canonicalize";
import { ContractError } from "./errors.ts";
import { assertWellFormed } from "./keys/text.ts";

function check(value: unknown, path: string): void {
  if (value === null || typeof value === "boolean") return;
  if (typeof value === "string") {
    assertWellFormed(value, path);
    return;
  }
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
    for (const [k, v] of Object.entries(value)) {
      assertWellFormed(k, `a key of ${path}`);
      check(v, `${path}.${k}`);
    }
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
