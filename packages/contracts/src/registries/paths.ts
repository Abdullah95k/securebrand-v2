// Dotted paths into plain JSON values ("post_ref.thread_ids"), as the registries name fields.

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * A registry entry by name, own properties only: `toString` or `constructor` names no entry (D-5).
 */
export function own<T>(record: Readonly<Record<string, T>>, name: string): T | undefined {
  return Object.hasOwn(record, name) ? record[name] : undefined;
}

/** The value at `path`, or undefined when a step is missing or not an object. */
export function getPath(value: unknown, path: string): unknown {
  let current: unknown = value;
  for (const step of path.split(".")) {
    if (!isRecord(current) || !Object.hasOwn(current, step)) return undefined;
    current = current[step];
  }
  return current;
}

/** True when `path` is present and not null. */
export function hasValue(value: unknown, path: string): boolean {
  const found = getPath(value, path);
  return found !== undefined && found !== null;
}
