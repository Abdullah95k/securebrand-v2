// A11 (plan T15, Question 7): the row types committed in packages/contracts/src/db equal a fresh
// generation from a database built from the migrations (this checkout's test database), formatted
// as tools/gen-types.ts writes them.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { generateTypes } from "../../tools/gen-types.ts";
import { DATABASE_TYPES_FILE } from "../../tools/paths.ts";
import { testDatabaseName } from "../helpers/env.ts";
import { cliUrl } from "../helpers/fresh.ts";

describe("the database row types", () => {
  it("the committed database types equal a fresh supabase gen types", () => {
    const fresh = generateTypes(cliUrl(testDatabaseName()));
    expect(fresh).toMatch(/feature_flags: \{/);
    expect(readFileSync(DATABASE_TYPES_FILE, "utf8")).toBe(fresh);
  });
});
