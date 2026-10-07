// The job handler: one job in, its outputs out. Replaying the same job must produce the same
// outputs and change nothing else (CLAUDE.md). F4 wraps it in listening-sdk's job wrapper, which
// owns retries, the DLQ after five attempts and cursor advance after the producer acknowledges.
import type { Adapter } from "./adapter.js";
import type { LogFields, Logger } from "./log.js";
import { mapAll, type Mapper } from "./mapping.js";

export interface HandlerDeps<Request, Record, Output> {
  readonly adapter: Adapter<Request, Record>;
  readonly map: Mapper<Record, Output>;
  readonly log: Logger;
}

export async function handle<Request, Record, Output>(
  request: Request,
  fields: LogFields,
  deps: HandlerDeps<Request, Record, Output>,
): Promise<Output[]> {
  const log = deps.log.child(fields);
  const records = await deps.adapter.fetch(request);
  const outputs = mapAll(records, deps.map);
  log.info("job handled", { records: records.length, outputs: outputs.length });
  return outputs;
}
