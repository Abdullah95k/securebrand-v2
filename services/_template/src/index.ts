// Entry point: health endpoints for the cluster and a clean shutdown on SIGTERM. F4 replaces the
// health server with listening-sdk's, which also serves the Prometheus metrics of PRD section 10.
import { once } from "node:events";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { pathToFileURL } from "node:url";
import { loadConfig, type Config } from "./config.js";
import { createLogger, type Logger } from "./log.js";

export interface Running {
  readonly port: number;
  close(): Promise<void>;
}

export async function start(config: Config, log: Logger): Promise<Running> {
  let ready = false;
  const server = createServer((req, res) => {
    if (req.url === "/healthz") {
      res.writeHead(200, { "content-type": "application/json" }).end('{"status":"ok"}');
    } else if (req.url === "/readyz") {
      res
        .writeHead(ready ? 200 : 503, { "content-type": "application/json" })
        .end(`{"ready":${String(ready)}}`);
    } else {
      res.writeHead(404).end();
    }
  });
  server.listen(config.port);
  await once(server, "listening");
  ready = true;
  const { port } = server.address() as AddressInfo;
  log.info("started", { port });

  return {
    port,
    close: async () => {
      ready = false;
      server.close();
      server.closeAllConnections();
      await once(server, "close");
      log.info("stopped");
    },
  };
}

async function main(): Promise<void> {
  const config = loadConfig();
  const log = createLogger(config.service, { level: config.logLevel });
  const running = await start(config, log);
  const stop = (): void => {
    running.close().then(
      () => process.exit(0),
      (error: unknown) => {
        log.error("shutdown failed", { error: String(error) });
        process.exit(1);
      },
    );
  };
  process.once("SIGTERM", stop);
  process.once("SIGINT", stop);
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
