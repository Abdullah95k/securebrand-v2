// raw_ref: `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst#<line>`, the batch
// six digits (ADR-0005, ADR-0039).
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";

export interface RawRef {
  route: string;
  platform: string;
  /** YYYY-MM-DD */
  date: string;
  service: string;
  batch: number;
  line: number;
}

export function rawRef(ref: RawRef): string {
  const { route, platform, date, service, batch, line } = ref;
  if (!Number.isInteger(batch) || batch < 0 || batch > 999_999)
    throw new ContractError("bad_raw_ref", `batch ${batch}`);
  if (!Number.isInteger(line) || line < 0) throw new ContractError("bad_raw_ref", `line ${line}`);
  if (!PATTERNS.date.test(date)) throw new ContractError("bad_raw_ref", `date ${date}`);
  const out = `raw/${route}/${platform}/${date.replaceAll("-", "/")}/${service}/${String(batch).padStart(6, "0")}.jsonl.zst#${line}`;
  if (!PATTERNS.rawRef.test(out)) throw new ContractError("bad_raw_ref", out);
  return out;
}

export function parseRawRef(value: string): RawRef {
  if (!PATTERNS.rawRef.test(value)) throw new ContractError("bad_raw_ref", value);
  const [, route = "", platform = "", y = "", mo = "", d = "", service = "", rest = ""] =
    value.split("/");
  const [file = "", line = ""] = rest.split("#");
  return {
    route,
    platform,
    date: `${y}-${mo}-${d}`,
    service,
    batch: Number(file.slice(0, 6)),
    line: Number(line),
  };
}
