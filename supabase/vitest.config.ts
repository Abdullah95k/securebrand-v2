import { defineConfig } from "vitest/config";

// The unit suite: files, generators and parsers only, no database (make check runs it).
export default defineConfig({
  test: {
    include: ["tests/unit/**/*.test.ts"],
    // One line per test, with its file: make test SERVICE=supabase shows what ran.
    reporters: ["verbose"],
  },
});
