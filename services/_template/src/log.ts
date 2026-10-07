// Structured JSON log lines; every line can carry job_id, source_id, route and vendor
// (CLAUDE.md). A placeholder: F4 replaces it with listening-sdk's logger, which also scrubs
// secrets and tokens before anything is written.
export type Level = "debug" | "info" | "warn" | "error";

export interface LogFields {
  readonly job_id?: string;
  readonly source_id?: string;
  readonly route?: string;
  readonly vendor?: string | null;
  readonly [key: string]: unknown;
}

export interface Logger {
  debug(msg: string, fields?: LogFields): void;
  info(msg: string, fields?: LogFields): void;
  warn(msg: string, fields?: LogFields): void;
  error(msg: string, fields?: LogFields): void;
  /** A logger that adds `fields` to every line, for example the fields of one job. */
  child(fields: LogFields): Logger;
}

const ORDER: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };

// JSON.stringify throws on a bigint (a 64-bit post id, say); a log line must never fail the job.
const asJson = (_key: string, value: unknown): unknown =>
  typeof value === "bigint" ? value.toString() : value;

export interface LoggerOptions {
  readonly level?: Level;
  readonly write?: (line: string) => void;
  readonly now?: () => Date;
}

export function createLogger(
  service: string,
  options: LoggerOptions = {},
  base: LogFields = {},
): Logger {
  const min = ORDER[options.level ?? "info"];
  const write =
    options.write ??
    ((line: string): void => {
      process.stdout.write(`${line}\n`);
    });
  const now = options.now ?? ((): Date => new Date());

  const emit = (level: Level, msg: string, fields: LogFields = {}): void => {
    if (ORDER[level] < min) {
      return;
    }
    write(
      JSON.stringify({ ts: now().toISOString(), level, service, msg, ...base, ...fields }, asJson),
    );
  };

  return {
    debug: (msg, fields) => {
      emit("debug", msg, fields);
    },
    info: (msg, fields) => {
      emit("info", msg, fields);
    },
    warn: (msg, fields) => {
      emit("warn", msg, fields);
    },
    error: (msg, fields) => {
      emit("error", msg, fields);
    },
    child: (fields) => createLogger(service, options, { ...base, ...fields }),
  };
}
