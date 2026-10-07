import { describe, expect, it } from "vitest";
import type { Adapter } from "../../src/adapter.js";
import { handle } from "../../src/handler.js";
import { createLogger } from "../../src/log.js";

// A fixture-backed adapter: the records a recorded response would yield.
const adapter: Adapter<string, { id: string }> = {
  fetch: (page) => Promise.resolve(page === "p1" ? [{ id: "a" }, { id: "b" }] : []),
};
const map = (record: { id: string }): string => `item:${record.id}`;
const fields = { job_id: "job-7", source_id: "src-3", route: "green", vendor: null };

describe("handler", () => {
  it("maps every fetched record and logs the job's fields", async () => {
    const lines: string[] = [];
    const log = createLogger("service-template", { write: (l) => lines.push(l) });
    const outputs = await handle("p1", fields, { adapter, map, log });
    expect(outputs).toEqual(["item:a", "item:b"]);
    expect(JSON.parse(lines[0] ?? "{}")).toMatchObject({
      ...fields,
      msg: "job handled",
      records: 2,
      outputs: 2,
    });
  });

  it("returns the same outputs when a job is replayed", async () => {
    const log = createLogger("service-template", { write: () => undefined });
    const first = await handle("p1", fields, { adapter, map, log });
    const second = await handle("p1", fields, { adapter, map, log });
    expect(second).toEqual(first);
  });
});
