import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    reporters: ["verbose"],
    testTimeout: 120_000,
    hookTimeout: 600_000,
    // The scripts under test create temporary git repositories and child processes; keep the
    // number of workers modest so the machine is not overloaded.
    maxWorkers: 4,
  },
});
