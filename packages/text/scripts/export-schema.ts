// Writes fixtures/text/golden.schema.json from the Zod schema in test/golden-case.ts.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { goldenSchemaJson } from "../test/golden-case.ts";

const out = fileURLToPath(new URL("../../../fixtures/text/golden.schema.json", import.meta.url));
writeFileSync(out, goldenSchemaJson());
console.log(`wrote ${out}`);
