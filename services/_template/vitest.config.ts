import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    // One line per test, with its file: make test SERVICE=<name> shows what ran.
    reporters: ["verbose"],
  },
});
