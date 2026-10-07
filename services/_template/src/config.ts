// Configuration is read once, from the environment, at start-up (CONVENTIONS: config by
// environment variables; secrets come from the vault through listening-sdk, never from files in
// the repository). F4 replaces this module with the SDK's config schema.
import type { Level } from "./log.js";

export interface Config {
  readonly service: string;
  readonly port: number;
  readonly logLevel: Level;
}

const LEVELS: readonly Level[] = ["debug", "info", "warn", "error"];

function isLevel(value: string): value is Level {
  return (LEVELS as readonly string[]).includes(value);
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const rawPort = env.PORT ?? "8080";
  const port = Number(rawPort);
  if (!/^\d+$/.test(rawPort) || port > 65535) {
    throw new Error(`PORT must be a port number between 0 and 65535, got "${rawPort}"`);
  }
  const logLevel = env.LOG_LEVEL ?? "info";
  if (!isLevel(logLevel)) {
    throw new Error(`LOG_LEVEL must be one of ${LEVELS.join(", ")}, got "${logLevel}"`);
  }
  return Object.freeze({ service: "service-template", port, logLevel });
}
