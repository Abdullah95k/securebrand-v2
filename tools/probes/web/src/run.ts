// Entry point. `plan` prints the call list and cost and makes no call. `run` makes the real calls,
// and refuses unless --approved is given with the SHA-256 prefix `plan` printed for this exact list
// (the user's yes is for that list), the credentials are set, and the keywords are real.
//
//   node --experimental-strip-types src/run.ts plan [--mojeek-plan business|startup]
//   node --experimental-strip-types src/run.ts run --approved <plan-hash> --mojeek-plan business|startup
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { CAPS, FIXTURE_DIR, KEYWORDS_FILE, type MojeekPlan, RAW_DIR } from "./config.ts";
import { Ledger, send, type CallResult } from "./http.ts";
import { isPlaceholder, parseKeywords } from "./keywords.ts";
import {
  commonCrawlCalls,
  gdeltCalls,
  mojeekCalls,
  perplexityCalls,
  summarise,
  type PlannedCall,
} from "./plan.ts";
import { log } from "./redact.ts";
import { parseAllowlist, scrubValue, shapeOnly, type ScrubContext } from "./scrub.ts";

const root = join(dirname(new URL(import.meta.url).pathname), "..", "..", "..", "..");
const read = (p: string): string => readFileSync(join(root, p), "utf8");

function arg(name: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

function planHash(calls: PlannedCall[]): string {
  return createHash("sha256").update(JSON.stringify(calls)).digest("hex").slice(0, 12);
}

function mojeekPlan(): MojeekPlan {
  const p = arg("mojeek-plan");
  if (p === "business" || p === "startup") return p;
  throw new Error(
    "--mojeek-plan business|startup is required: Startup terms forbid storing results",
  );
}

function build(crawlId: string): PlannedCall[] {
  const keywords = parseKeywords(read(KEYWORDS_FILE));
  return [
    ...perplexityCalls(keywords),
    ...mojeekCalls(keywords, "business"),
    ...gdeltCalls(keywords),
    ...commonCrawlCalls(crawlId),
  ];
}

function printPlan(calls: PlannedCall[]): void {
  for (const c of calls)
    log(`${c.id.padEnd(24)} ${c.vendor.padEnd(11)} ${c.method.padEnd(4)} ${c.purpose}`);
  log("");
  for (const s of summarise(calls))
    log(`${s.vendor.padEnd(12)} ${String(s.calls).padStart(3)} calls (cap ${s.cap})  ${s.cost}`);
  log(`plan hash ${planHash(calls)}`);
}

function writeJson(path: string, data: unknown): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(data, null, 2) + "\n");
}

async function main(): Promise<void> {
  const mode = process.argv[2];
  // The crawl id is only known after the crawl list is read; the plan uses a stable stand-in.
  const standIn = "CC-MAIN-LATEST";
  if (mode === "plan") {
    printPlan(build(standIn));
    return;
  }
  if (mode !== "run")
    throw new Error("usage: run.ts plan | run --approved <hash> --mojeek-plan <plan>");

  const keywords = parseKeywords(read(KEYWORDS_FILE));
  if (isPlaceholder(keywords)) throw new Error("keywords.txt still holds the placeholder");
  const plan = mojeekPlan();
  const calls = build(standIn);
  if (arg("approved") !== planHash(calls))
    throw new Error("--approved must equal the plan hash printed by `plan` for this keyword file");
  for (const name of ["PERPLEXITY_API_KEY", "MOJEEK_API_KEY"]) {
    if (!process.env[name]) throw new Error(`${name} is not set`);
  }
  if (!process.env["PROBE_CONTACT"])
    throw new Error("PROBE_CONTACT (a contact address for the user agent) is not set");

  const ledger = new Ledger();
  const ctx: ScrubContext = {
    allow: parseAllowlist(read("tools/probes/web/public-accounts.txt")),
    replaced: new Set(),
  };
  const today = new Date().toISOString().slice(0, 10);
  const manifest: Record<string, unknown>[] = [];

  const record = (call: PlannedCall, r: CallResult): void => {
    const request = { method: call.method, url: call.url, body: call.body ?? null };
    // Mojeek Startup: counts, timings and field names only, in raw/ as well as in the fixture.
    const storeBody = !(call.vendor === "mojeek" && plan === "startup");
    const body = storeBody ? r.body : shapeOnly(r.body);
    const rawDoc = {
      id: call.id,
      date: today,
      request,
      status: r.status,
      ms: r.ms,
      headers: r.headers,
      bodyIsJson: r.bodyIsJson,
      error: r.error ?? null,
      body,
    };
    writeJson(join(root, RAW_DIR, `${call.vendor}-${call.id}.json`), rawDoc);
    writeJson(join(root, FIXTURE_DIR, `${call.vendor}-${call.id}.json`), {
      ...rawDoc,
      body: scrubValue(body, ctx),
    });
    manifest.push({
      id: call.id,
      vendor: call.vendor,
      purpose: call.purpose,
      expect: call.expect,
      status: r.status,
      ms: r.ms,
    });
    log(`${call.id}: ${r.status}${r.error ? ` ${r.error}` : ""} ${r.ms} ms`);
  };

  // Common Crawl first needs the crawl list to name the latest crawl.
  const ordered = calls.filter((c) => c.vendor !== "commoncrawl");
  const cc = commonCrawlCalls(standIn);
  let crawlId = standIn;
  const collinfo = cc[0];
  if (collinfo !== undefined) {
    const r = await send(collinfo, ledger);
    record(collinfo, r);
    const first = Array.isArray(r.body) ? (r.body[0] as { id?: string } | undefined) : undefined;
    if (first?.id !== undefined) crawlId = first.id;
  }
  const rest = crawlId === standIn ? [] : commonCrawlCalls(crawlId).slice(1);
  for (const call of [...ordered, ...rest]) {
    if (ledger.stopped.has(call.vendor)) continue;
    const r = await send(call, ledger);
    record(call, r);
    // A 401, 403 or 429 ends that vendor for this run: no retries, nothing tried to get around it.
    if ([401, 403, 429].includes(r.status)) {
      ledger.stopped.add(call.vendor);
      log(`${call.vendor}: stopped after status ${r.status}`);
    }
  }
  writeJson(join(root, FIXTURE_DIR, "manifest.json"), {
    date: today,
    mojeekPlan: plan,
    crawlId,
    calls: manifest,
  });
  writeJson(join(root, RAW_DIR, "replaced.json"), [...ctx.replaced]);
  log(
    `spend: perplexity ${ledger.counts.perplexity}/${CAPS.perplexityRequests} requests, mojeek ${ledger.counts.mojeek}/${CAPS.mojeekQueries} queries, gdelt ${ledger.counts.gdelt}, commoncrawl ${ledger.counts.commoncrawl}`,
  );
}

main().catch((e: unknown) => {
  log(`error: ${e instanceof Error ? e.message : String(e)}`);
  process.exitCode = 1;
});
