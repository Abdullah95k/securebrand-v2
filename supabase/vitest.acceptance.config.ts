import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// The acceptance suite: the local stack's Postgres. The global setup builds this checkout's fresh
// database (test_<namespace>) from the migrations once; the files then run one at a time, since some
// of them build and drop databases of their own. "contracts/db" resolves to its source, so that
// make test SERVICE=supabase, which builds nothing first, tests the lock-key helper as it is (F2's
// handoff leaves the build order of the contracts' consumers to F4).
export default defineConfig({
  resolve: {
    alias: {
      "contracts/db": fileURLToPath(
        new URL("../packages/contracts/src/db/index.ts", import.meta.url),
      ),
    },
  },
  test: {
    include: ["tests/acceptance/**/*.test.ts"],
    globalSetup: ["tests/acceptance/global-setup.ts"],
    fileParallelism: false,
    testTimeout: 120_000,
    hookTimeout: 300_000,
    reporters: ["verbose"],
  },
});
