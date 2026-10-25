// The call list: every real call the probe may make, built from the keywords and the caps, with no
// credential in it. `plan` prints it; `run` executes exactly this list and nothing else.
import { CAPS, type MojeekPlan, type Vendor } from "./config.ts";
import { type Keyword, sample } from "./keywords.ts";

export interface PlannedCall {
  id: string;
  vendor: Vendor;
  /** Which PRD assumption or question this call answers. */
  purpose: string;
  method: "GET" | "POST";
  /** URL without credentials. The Mojeek key is added by the HTTP layer at send time. */
  url: string;
  body?: Record<string, unknown>;
  /** Expected outcome, so the report can mark "different" when the answer is not this. */
  expect: "ok" | "empty" | "error";
}

const PPLX = "https://api.perplexity.ai/search";
const MOJEEK = "https://api.mojeek.com/search";
const GDELT = "https://api.gdeltproject.org/api/v2/doc/doc";
const CC = "https://index.commoncrawl.org";

/** A phrase that matches nothing, for the empty-result call. */
const NOTHING = "zqxjkv-w0-probe-no-such-phrase-8431";

function qs(params: Record<string, string>): string {
  return new URLSearchParams(params).toString();
}

const quote = (s: string): string => `"${s}"`;

export function perplexityCalls(keywords: Keyword[]): PlannedCall[] {
  const calls: PlannedCall[] = [];
  const base = { country: "IQ", search_language_filter: ["ar"] };
  const mk = (
    id: string,
    purpose: string,
    body: Record<string, unknown>,
    expect: PlannedCall["expect"] = "ok",
  ): void => {
    calls.push({ id, vendor: "perplexity", purpose, method: "POST", url: PPLX, body, expect });
  };
  const all = keywords.map((k) => quote(k.text));
  // 5.3 packs up to 5 queries per request: one query per keyword, all keywords covered.
  for (let i = 0; i < all.length; i += 5) {
    mk(
      `pplx-pack-${i / 5 + 1}`,
      "5.3 packed request, 5 queries, country IQ, language ar; per-query grouping",
      {
        query: all.slice(i, i + 5),
        ...base,
      },
    );
  }
  const ckb = keywords.filter((k) => k.lang === "ckb");
  const first = keywords[0];
  const canary = ckb[0] ?? first;
  if (canary !== undefined) {
    mk("pplx-ckb-canary", "14 Q1: is ckb accepted (start-up canary)", {
      query: quote(canary.text),
      country: "IQ",
      search_language_filter: ["ckb"],
    });
    mk("pplx-ar-ckb", "5.3 second request: language filter [ar, ckb]", {
      query: (ckb.length > 0 ? ckb : keywords).slice(0, 4).map((k) => quote(k.text)),
      country: "IQ",
      search_language_filter: ["ar", "ckb"],
    });
  }
  if (first !== undefined) {
    const t = first.text;
    // 5.3 first request: the five variants of one rule (exact phrase, plus place, spacing variants).
    mk("pplx-variants-1", "5.3 five variants of one rule in one request", {
      query: [quote(t), `${quote(t)} العراق`, quote(t.replace(/\s+/g, "")), quote(`${t} Iraq`), t],
      ...base,
    });
    mk("pplx-max-results", "5.3 max_results at the documented maximum; result count per query", {
      query: quote(t),
      ...base,
      max_results: 20,
    });
    mk("pplx-date-filter", "14 Q3 / 5.3 search_after_date_filter in MM/DD/YYYY", {
      query: quote(t),
      ...base,
      search_after_date_filter: "10/01/2026",
    });
    mk("pplx-no-country", "5.4 country is a preference: same query without it", {
      query: quote(t),
      search_language_filter: ["ar"],
    });
    mk("pplx-site-search", "5.3 search_domain_filter for site_search jobs (youtube.com)", {
      query: quote(t),
      ...base,
      search_domain_filter: ["youtube.com"],
    });
    mk("pplx-tokens-per-page", "5.3 max_tokens_per_page: effect on snippet length", {
      query: quote(t),
      ...base,
      max_tokens_per_page: 512,
    });
  }
  mk("pplx-empty", "empty result", { query: quote(NOTHING), ...base });
  mk(
    "pplx-error-bad-date",
    "error shape: malformed date filter (expected 400)",
    { query: quote(NOTHING), ...base, search_after_date_filter: "2026-10-01" },
    "error",
  );
  // Rate limit: four back-to-back requests, headers read, no retry on 429.
  if (first !== undefined) {
    for (let i = 1; i <= 4; i++) {
      mk(`pplx-burst-${i}`, "7 rate limit: back-to-back requests, headers and 429 behaviour", {
        query: quote(first.text),
        ...base,
      });
    }
  }
  return calls;
}

export function mojeekCalls(keywords: Keyword[], plan: MojeekPlan): PlannedCall[] {
  void plan; // The plan changes what is stored, not which calls are made.
  const calls: PlannedCall[] = [];
  const mk = (
    id: string,
    purpose: string,
    params: Record<string, string>,
    expect: PlannedCall["expect"] = "ok",
  ): void => {
    calls.push({
      id,
      vendor: "mojeek",
      purpose,
      method: "GET",
      url: `${MOJEEK}?${qs({ fmt: "json", ...params })}`,
      expect,
    });
  };
  const first = keywords[0];
  // 18 keywords, evenly over the languages, leaves room under the 30 cap for the shape calls below.
  for (const [i, k] of sample(keywords, 18).entries()) {
    mk(`mojeek-kw-${i + 1}`, "5.3 first page of one query: rb=IQ, lb=AR", {
      q: quote(k.text),
      rb: "IQ",
      lb: "AR",
    });
  }
  if (first !== undefined) {
    const q = quote(first.text);
    mk("mojeek-page-2", "5.3 depth: offset for the second page", {
      q,
      rb: "IQ",
      lb: "AR",
      s: "11",
    });
    mk("mojeek-page-3", "5.3 depth: offset for the third page", { q, rb: "IQ", lb: "AR", s: "21" });
    mk("mojeek-no-boost", "5.3 rb and lb are boosts: same query without them", { q });
    mk("mojeek-max-results", "5.3 number of results per query: t at a high value", {
      q,
      rb: "IQ",
      lb: "AR",
      t: "100",
    });
    mk("mojeek-site", "14 Q4 site: operator", { q: `${q} site:youtube.com`, rb: "IQ", lb: "AR" });
    mk("mojeek-or", "14 Q1 OR operator across Arabic and Latin forms", {
      q: `${q} OR ${quote(first.text.replace(/\s+/g, ""))}`,
      rb: "IQ",
      lb: "AR",
    });
    mk("mojeek-and", "14 Q1 exact phrase plus a second term", {
      q: `${q} العراق`,
      rb: "IQ",
      lb: "AR",
    });
  }
  const ckb = keywords.find((k) => k.lang === "ckb");
  if (ckb !== undefined) {
    mk("mojeek-lb-ckb", "14 Q2 a Sorani language boost (lb=CKB)", {
      q: quote(ckb.text),
      rb: "IQ",
      lb: "CKB",
    });
  }
  mk("mojeek-empty", "empty result", { q: quote(NOTHING), rb: "IQ", lb: "AR" });
  mk(
    "mojeek-error-bad-param",
    "error shape: unknown format value (expected 4xx)",
    { q: quote(NOTHING), fmt: "no-such-format" },
    "error",
  );
  return calls;
}

export function gdeltCalls(keywords: Keyword[]): PlannedCall[] {
  const calls: PlannedCall[] = [];
  const mk = (
    id: string,
    purpose: string,
    params: Record<string, string>,
    expect: PlannedCall["expect"] = "ok",
  ): void => {
    calls.push({
      id,
      vendor: "gdelt",
      purpose,
      method: "GET",
      url: `${GDELT}?${qs({ mode: "artlist", format: "json", ...params })}`,
      expect,
    });
  };
  for (const [i, k] of keywords.entries()) {
    mk(`gdelt-kw-${i + 1}`, "5.3 article list for one form, 7 days, newest first", {
      query: quote(k.text),
      timespan: "7d",
      maxrecords: "250",
      sort: "datedesc",
    });
  }
  const [a, b, c] = keywords;
  if (a !== undefined && b !== undefined) {
    const mixed = [a, b, c].filter((k): k is Keyword => k !== undefined);
    mk("gdelt-or-mixed", "14 Q2 combined OR query, mixed Arabic and Latin forms", {
      query: `(${mixed.map((k) => quote(k.text)).join(" OR ")})`,
      timespan: "7d",
      maxrecords: "250",
      sort: "datedesc",
    });
  }
  if (a !== undefined) {
    mk("gdelt-span-max", "5.3 maximum time span", {
      query: quote(a.text),
      timespan: "3months",
      maxrecords: "250",
      sort: "datedesc",
    });
    mk("gdelt-maxrecords", "5.3 maximum records: ask for more than 250", {
      query: quote(a.text),
      timespan: "1month",
      maxrecords: "1000",
      sort: "datedesc",
    });
    mk("gdelt-window", "5.3 startdatetime and enddatetime window", {
      query: quote(a.text),
      startdatetime: "20260920000000",
      enddatetime: "20260927000000",
      maxrecords: "250",
    });
    mk("gdelt-ar-second-pass", "14 Q5 second pass restricted to Arabic sources", {
      query: `${quote(a.text)} sourcelang:arabic`,
      timespan: "1month",
      maxrecords: "250",
    });
    mk("gdelt-iraq-second-pass", "14 Q5 second pass restricted to Iraqi source country", {
      query: `${quote(a.text)} sourcecountry:iraq`,
      timespan: "1month",
      maxrecords: "250",
    });
    mk(
      "gdelt-short-phrase",
      "5.3 minimum phrase length: a two-letter query (expect an error message)",
      { query: "ab", timespan: "1d" },
      "error",
    );
  }
  mk("gdelt-empty", "empty result", { query: quote(NOTHING), timespan: "1d" }, "empty");
  mk(
    "gdelt-bad-mode",
    "error shape: unknown mode",
    { query: quote(NOTHING), mode: "no-such-mode" },
    "error",
  );
  return calls;
}

/** Outlets and zones named in the PRD (public organisations, safe to keep in fixtures). */
const CC_SEED_DOMAINS = ["rudaw.net", "shafaq.com", "alsumaria.tv"];
const CC_ZONES = ["iq", "gov.iq", "edu.iq", "com.iq", "org.iq", "net.iq", "mil.iq"];

/** `crawlId` is filled in by the runner from the crawl list (call cc-collinfo). */
export function commonCrawlCalls(crawlId: string): PlannedCall[] {
  const calls: PlannedCall[] = [];
  const idx = `${CC}/${crawlId}-index`;
  const mk = (
    id: string,
    purpose: string,
    url: string,
    expect: PlannedCall["expect"] = "ok",
  ): void => {
    calls.push({ id, vendor: "commoncrawl", purpose, method: "GET", url, expect });
  };
  mk("cc-collinfo", "5.3 crawl list (id, publication date)", `${CC}/collinfo.json`);
  const fl = "url,timestamp,status,mime,languages,digest";
  mk(
    "cc-iq-pages",
    "5.3 read 1: number of index pages for *.iq",
    `${idx}?${qs({ url: "*.iq", matchType: "domain", output: "json", showNumPages: "true" })}`,
  );
  mk(
    "cc-iq-page-0",
    "5.3 read 1: first page of *.iq, fields requested",
    `${idx}?${qs({ url: "*.iq", matchType: "domain", output: "json", fl, page: "0", pageSize: "1" })}`,
  );
  mk(
    "cc-iq-page-1",
    "5.3 read 1: second page (pagination sequence)",
    `${idx}?${qs({ url: "*.iq", matchType: "domain", output: "json", fl, page: "1", pageSize: "1" })}`,
  );
  mk(
    "cc-iq-limit",
    "5.3 limit: a small sample with every field",
    `${idx}?${qs({ url: "*.iq", matchType: "domain", output: "json", fl, limit: "20" })}`,
  );
  for (const zone of CC_ZONES.slice(1)) {
    mk(
      `cc-zone-${zone}`,
      "14 Q2 which second-level zones hold captures",
      `${idx}?${qs({ url: zone, matchType: "domain", output: "json", showNumPages: "true" })}`,
    );
  }
  for (const d of CC_SEED_DOMAINS) {
    mk(
      `cc-seed-${d}`,
      "5.3 read 2: captures of a seed registrable domain",
      `${idx}?${qs({ url: d, matchType: "domain", output: "json", fl, limit: "10" })}`,
    );
  }
  mk(
    "cc-empty",
    "empty result: a domain with no captures",
    `${idx}?${qs({ url: "zqxjkv-w0-probe.iq", matchType: "domain", output: "json", limit: "5" })}`,
    "empty",
  );
  mk(
    "cc-error-bad-crawl",
    "error shape: unknown crawl id",
    `${CC}/CC-MAIN-0000-00-index?${qs({ url: "example.iq", output: "json", limit: "1" })}`,
    "error",
  );
  return calls;
}

export interface Cost {
  vendor: Vendor;
  calls: number;
  cap: number;
  cost: string;
}

export function summarise(calls: PlannedCall[]): Cost[] {
  const n = (v: Vendor): number => calls.filter((c) => c.vendor === v).length;
  return [
    {
      vendor: "perplexity",
      calls: n("perplexity"),
      cap: CAPS.perplexityRequests,
      cost: `USD ${(n("perplexity") * CAPS.perplexityUsdPerRequest).toFixed(3)} (cap USD ${(CAPS.perplexityRequests * CAPS.perplexityUsdPerRequest).toFixed(2)})`,
    },
    {
      vendor: "mojeek",
      calls: n("mojeek"),
      cap: CAPS.mojeekQueries,
      cost: `GBP ${(n("mojeek") * CAPS.mojeekGbpPerQuery).toFixed(3)} (cap GBP ${(CAPS.mojeekQueries * CAPS.mojeekGbpPerQuery).toFixed(2)}; Business rate, trial/Startup may differ)`,
    },
    {
      vendor: "gdelt",
      calls: n("gdelt"),
      cap: CAPS.gdeltRequests,
      cost: "USD 0, about " + Math.ceil((n("gdelt") * CAPS.gdeltMinGapMs) / 1000) + " s of waiting",
    },
    {
      vendor: "commoncrawl",
      calls: n("commoncrawl"),
      cap: CAPS.commonCrawlRequests,
      cost:
        "USD 0, about " +
        Math.ceil((n("commoncrawl") * CAPS.commonCrawlMinGapMs) / 1000) +
        " s of waiting",
    },
  ];
}
