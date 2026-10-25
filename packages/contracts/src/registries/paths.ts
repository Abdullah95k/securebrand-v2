// Dotted paths into plain JSON values ("post_ref.thread_ids"), as the registries name fields.

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
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
