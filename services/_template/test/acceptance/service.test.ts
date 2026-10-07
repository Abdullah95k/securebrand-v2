// The service as the cluster sees it: it starts, answers its health checks on localhost and shuts
// down cleanly. No network beyond the loopback interface.
import { describe, expect, it } from "vitest";
import { start } from "../../src/index.js";
import { createLogger } from "../../src/log.js";

describe("service", () => {
  it("answers its health checks and shuts down cleanly", async () => {
    const lines: string[] = [];
    const log = createLogger("service-template", { write: (l) => lines.push(l) });
    const running = await start({ service: "service-template", port: 0, logLevel: "info" }, log);
    const base = `http://127.0.0.1:${String(running.port)}`;

    const health = await fetch(`${base}/healthz`);
    expect(health.status).toBe(200);
    expect(await health.json()).toEqual({ status: "ok" });
    expect((await fetch(`${base}/readyz`)).status).toBe(200);
    expect((await fetch(`${base}/nope`)).status).toBe(404);

    await running.close();
    await expect(fetch(`${base}/healthz`)).rejects.toThrow();
    expect(lines.map((l) => (JSON.parse(l) as { msg: string }).msg)).toEqual([
      "started",
      "stopped",
    ]);
  });
});
