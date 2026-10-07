import { describe, expect, it } from "vitest";
import { loadConfig } from "../../src/config.js";

describe("config", () => {
  it("reads the port and the log level from the environment, with defaults", () => {
    expect(loadConfig({})).toEqual({ service: "service-template", port: 8080, logLevel: "info" });
    expect(loadConfig({ PORT: "9100", LOG_LEVEL: "debug" })).toMatchObject({
      port: 9100,
      logLevel: "debug",
    });
  });

  it("returns a frozen object, so configuration is read once and never changed", () => {
    expect(Object.isFrozen(loadConfig({}))).toBe(true);
  });

  it("rejects a port that is not a port number", () => {
    expect(() => loadConfig({ PORT: "http" })).toThrow(/PORT/);
    expect(() => loadConfig({ PORT: "70000" })).toThrow(/PORT/);
  });

  it("rejects an unknown log level", () => {
    expect(() => loadConfig({ LOG_LEVEL: "verbose" })).toThrow(/LOG_LEVEL/);
  });
});
