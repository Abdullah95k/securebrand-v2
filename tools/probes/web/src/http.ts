// The only place the probe talks to the network. Every call passes the host allowlist, the caps and
// the pacing here; credentials are added at the last moment and never leave this file.
import { ALLOWED_HOSTS, CAPS, type Vendor } from "./config.ts";
import type { PlannedCall } from "./plan.ts";
import { redact, registerSecret } from "./redact.ts";

export interface CallResult {
  id: string;
  vendor: Vendor;
  status: number;
  ms: number;
  /** Rate-limit and retry headers only. */
  headers: Record<string, string>;
  body: unknown;
  bodyIsJson: boolean;
  error?: string;
}

const KEEP_HEADERS =
  /^(retry-after|x-ratelimit-.*|ratelimit-.*|x-rate-limit-.*|content-type|x-request-id|date)$/i;

export class Ledger {
  readonly counts: Record<Vendor, number> = { perplexity: 0, mojeek: 0, gdelt: 0, commoncrawl: 0 };
  private readonly last: Record<Vendor, number> = {
    perplexity: 0,
    mojeek: 0,
    gdelt: 0,
    commoncrawl: 0,
  };
  readonly stopped = new Set<Vendor>();

  cap(vendor: Vendor): number {
    switch (vendor) {
      case "perplexity":
        return CAPS.perplexityRequests;
      case "mojeek":
        return CAPS.mojeekQueries;
      case "gdelt":
        return CAPS.gdeltRequests;
      case "commoncrawl":
        return CAPS.commonCrawlRequests;
    }
  }

  gap(vendor: Vendor): number {
    switch (vendor) {
      case "gdelt":
        return CAPS.gdeltMinGapMs;
      case "commoncrawl":
        return CAPS.commonCrawlMinGapMs;
      case "perplexity":
      case "mojeek":
        return 0;
    }
  }

  /** Throws when the call would pass the cap; otherwise counts it and waits out the spacing. */
  async admit(vendor: Vendor): Promise<void> {
    if (this.counts[vendor] >= this.cap(vendor))
      throw new Error(`${vendor}: cap of ${this.cap(vendor)} requests reached`);
    this.counts[vendor] += 1;
    const wait = this.last[vendor] + this.gap(vendor) - Date.now();
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
    this.last[vendor] = Date.now();
  }
}

function credential(vendor: Vendor): string | undefined {
  const name =
    vendor === "perplexity"
      ? "PERPLEXITY_API_KEY"
      : vendor === "mojeek"
        ? "MOJEEK_API_KEY"
        : undefined;
  if (name === undefined) return undefined;
  const v = process.env[name];
  registerSecret(v);
  return v === undefined || v === "" ? undefined : v;
}

export function userAgent(): string {
  // The contact address comes from the environment so no personal address is committed.
  const contact = process.env["PROBE_CONTACT"] ?? "";
  return `SecureBrand-listening-probe/0.1 (+contact: ${contact})`;
}

export async function send(call: PlannedCall, ledger: Ledger): Promise<CallResult> {
  const url = new URL(call.url);
  if (!(ALLOWED_HOSTS as readonly string[]).includes(url.hostname) || url.protocol !== "https:") {
    throw new Error(`refused: ${url.hostname} is not on the allowlist`);
  }
  const key = credential(call.vendor);
  if ((call.vendor === "perplexity" || call.vendor === "mojeek") && key === undefined) {
    throw new Error(`${call.vendor}: credential not set`);
  }
  const headers: Record<string, string> = { "user-agent": userAgent(), accept: "application/json" };
  if (call.vendor === "perplexity" && key !== undefined) headers["authorization"] = `Bearer ${key}`;
  if (call.vendor === "mojeek" && key !== undefined) url.searchParams.set("api_key", key);
  if (call.body !== undefined) headers["content-type"] = "application/json";

  await ledger.admit(call.vendor);
  const t0 = Date.now();
  try {
    // redirect: error — a redirect would resend the key to another host.
    const init: RequestInit = {
      method: call.method,
      headers,
      redirect: "error",
      signal: AbortSignal.timeout(60_000),
    };
    if (call.body !== undefined) init.body = JSON.stringify(call.body);
    const res = await fetch(url, init);
    const text = await res.text();
    let body: unknown = text;
    let bodyIsJson = false;
    try {
      body = JSON.parse(text);
      bodyIsJson = true;
    } catch {
      // not JSON: keep the text (GDELT reports bad queries as plain text)
    }
    const kept: Record<string, string> = {};
    res.headers.forEach((v, k) => {
      if (KEEP_HEADERS.test(k)) kept[k] = redact(v);
    });
    return {
      id: call.id,
      vendor: call.vendor,
      status: res.status,
      ms: Date.now() - t0,
      headers: kept,
      body,
      bodyIsJson,
    };
  } catch (e) {
    const msg = redact(e instanceof Error ? `${e.name}: ${e.message}` : String(e));
    return {
      id: call.id,
      vendor: call.vendor,
      status: 0,
      ms: Date.now() - t0,
      headers: {},
      body: null,
      bodyIsJson: false,
      error: msg,
    };
  }
}
