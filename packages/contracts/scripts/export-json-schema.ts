// Writes every artefact of src/export.ts under packages/contracts/schemas/ and removes stale ones:
// node scripts/export-json-schema.ts (pnpm --filter contracts export:schemas).
import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { SCHEMAS_DIR, exportArtefacts } from "../src/export.ts";

function listFiles(dir: string): string[] {
  try {
    return readdirSync(dir, { recursive: true, withFileTypes: true })
      .filter((e) => e.isFile())
      .map((e) => relative(SCHEMAS_DIR, join(e.parentPath, e.name)));
  } catch {
    return [];
  }
}

const artefacts = await exportArtefacts();
for (const stale of listFiles(SCHEMAS_DIR))
  if (!artefacts.has(stale)) rmSync(join(SCHEMAS_DIR, stale));
for (const [path, text] of artefacts) {
  const target = join(SCHEMAS_DIR, path);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, text);
}
console.log(`export:schemas wrote ${artefacts.size} files to ${SCHEMAS_DIR}`);
