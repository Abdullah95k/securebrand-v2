import { describe, expect, it } from "vitest";
import { make } from "../helpers/stack.js";

const MINUTES = 60_000;

describe("make test SERVICE=<name>", () => {
  it(
    "runs vitest unit and acceptance suites for a TypeScript service",
    () => {
      const result = make(["test", "SERVICE=_template"]);
      expect(result.code, result.output).toBe(0);
      expect(result.output).toMatch(/test\/unit\/\S+\.test\.ts/);
      expect(result.output).toMatch(/test\/acceptance\/\S+\.test\.ts/);
    },
    5 * MINUTES,
  );

  it(
    "runs pytest unit and acceptance suites for a Python service",
    () => {
      const result = make(["test", "SERVICE=_template-py"]);
      expect(result.code, result.output).toBe(0);
      expect(result.output).toMatch(/tests\/unit\/\S+\.py/);
      expect(result.output).toMatch(/tests\/acceptance\/\S+\.py/);
    },
    5 * MINUTES,
  );

  it("fails naming the directories it searched for an unknown service", () => {
    const result = make(["test", "SERVICE=no-such-service"]);
    expect(result.code).not.toBe(0);
    for (const dir of [
      "services/no-such-service",
      "packages/no-such-service",
      "py/no-such-service",
      "tools/no-such-service",
    ]) {
      expect(result.output).toContain(dir);
    }
  });

  it("asks for a service when none is given", () => {
    const result = make(["test"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("SERVICE=");
  });
});
