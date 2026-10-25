import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    // contracts is imported from its compiled dist/: build it when a fresh checkout lacks it.
    globalSetup: ["test/setup/contracts-dist.ts"],
    // One line per test, with its file: make test SERVICE=text shows what ran.
    reporters: ["verbose"],
    // The property tests fold every code point and every pair of D9's set (docs/plans/F7.md).
    testTimeout: 120_000,
  },
});
