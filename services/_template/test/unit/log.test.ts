import { describe, expect, it } from "vitest";
import { createLogger } from "../../src/log.js";

function capture(): { lines: Record<string, unknown>[]; write: (line: string) => void } {
  const lines: Record<string, unknown>[] = [];
  return { lines, write: (line) => lines.push(JSON.parse(line) as Record<string, unknown>) };
}

describe("log", () => {
  it("writes one JSON line per entry carrying job_id, source_id, route and vendor", () => {
    const out = capture();
    const now = (): Date => new Date("2026-10-07T00:00:00.000Z");
    const job = createLogger("service-template", { write: out.write, now }).child({
      job_id: "job-1",
      source_id: "src-1",
      route: "green",
      vendor: null,
    });
    job.info("fetched", { items: 3 });
    expect(out.lines).toEqual([
      {
        ts: "2026-10-07T00:00:00.000Z",
        level: "info",
        service: "service-template",
        msg: "fetched",
        job_id: "job-1",
        source_id: "src-1",
        route: "green",
        vendor: null,
        items: 3,
      },
    ]);
  });

  it("drops entries below the configured level", () => {
    const out = capture();
    const log = createLogger("service-template", { write: out.write, level: "warn" });
    log.debug("noise");
    log.info("noise");
    log.warn("kept");
    log.error("kept too");
    expect(out.lines.map((l) => l.msg)).toEqual(["kept", "kept too"]);
  });
});
