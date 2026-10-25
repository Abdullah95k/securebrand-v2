// Reads the CONVENTIONS tables the reference seeds come from (plan T5): the canonical budget tags
// (CONVENTIONS v1.1 L429), the service index with its amber marks (L374 to L384) and the comment
// series profiles (L405 to L421). Each reader fails on text it does not recognise, so a reworded
// CONVENTIONS line stops the generator and the drift tests instead of seeding something else.
import { readFileSync } from "node:fs";
import { CONVENTIONS_FILE } from "./paths.ts";

export function readConventions(file: string = CONVENTIONS_FILE): string {
  return readFileSync(file, "utf8");
}

function backticked(text: string): string[] {
  return [...text.matchAll(/`([^`]+)`/g)].map((m) => m[1] ?? "");
}

/** Splits on `separator` outside parentheses. */
function splitTop(text: string, separator: string): string[] {
  const parts: string[] = [];
  let depth = 0;
  let current = "";
  for (const ch of text) {
    if (ch === "(") depth++;
    if (ch === ")") depth--;
    if (ch === separator && depth === 0) {
      parts.push(current);
      current = "";
    } else current += ch;
  }
  parts.push(current);
  return parts.map((p) => p.trim()).filter((p) => p !== "");
}

export interface BudgetTag {
  tag: string;
  /** The label CONVENTIONS gives it ("Facebook vendor", "web search"). */
  label: string;
  /** Bought from a vendor: the label names a vendor. */
  amber: boolean;
  subCounters: string[];
  /** Sub-counters CONVENTIONS calls zero-price. */
  zeroPrice: string[];
}

export interface BudgetTags {
  tags: BudgetTag[];
  /** Tags with an id placeholder: a row per id, created on first request. */
  families: string[];
  /** Listed but seeded only on a condition (analysis_model_api). */
  conditional: string[];
  /** Zero-price counting tags, never a gate. */
  counting: string[];
  /** The sub-counters every amber tag has. */
  amberSubCounters: string[];
  /** The shares CONVENTIONS names: a service's sub-counter on a tag. */
  shares: { tag: string; service: string }[];
}

/** The canonical budget tags of CONVENTIONS L429. */
export function budgetTags(conventions: string): BudgetTags {
  const line = conventions.split("\n").find((l) => l.startsWith("- Budget tags (canonical;"));
  if (line === undefined) throw new Error("CONVENTIONS has no '- Budget tags (canonical;' line");
  const start = line.indexOf("): ");
  const countingAt = line.indexOf("Zero-price counting tags, never a gate:");
  const everyAt = line.indexOf("Every amber tag has the sub-counters");
  if (start < 0 || countingAt < 0 || everyAt < 0)
    throw new Error("the budget tags line does not have its three known sentences");

  const result: BudgetTags = {
    tags: [],
    families: [],
    conditional: [],
    counting: [],
    amberSubCounters: [],
    shares: [],
  };
  const list = line
    .slice(start + 3, countingAt)
    .trim()
    .replace(/\.$/, "");
  for (const segment of splitTop(list, ";")) {
    const paren = segment.indexOf("(");
    const head = paren < 0 ? segment : segment.slice(0, paren);
    const inner = paren < 0 ? "" : segment.slice(paren + 1, segment.lastIndexOf(")"));
    const label = head
      .replace(/`[^`]*`/g, "")
      .replace(/,/g, "")
      .trim();
    if (/seeded only if/.test(segment)) {
      result.conditional.push(...backticked(head));
      continue;
    }
    for (const token of backticked(head)) {
      if (/^[a-z][a-z0-9_]*:<[a-z_]+>$/.test(token)) {
        result.families.push(token.slice(0, token.indexOf(":")));
        continue;
      }
      if (token.includes("<")) {
        // A name pattern such as li_vendor_<action>: its concrete tags follow in parentheses.
        for (const concrete of backticked(inner))
          result.tags.push({
            tag: concrete,
            label,
            amber: /vendor/.test(label),
            subCounters: [],
            zeroPrice: [],
          });
        continue;
      }
      if (!/^[a-z][a-z0-9_]*$/.test(token)) throw new Error(`unrecognised budget tag ${token}`);
      // "sub-counters `a`, `b` and the zero-price `c`, ..." or "buckets `a`, `b`, ..., named ...".
      const firstClause = inner.split(";")[0] ?? "";
      const subCounters = /^(sub-counters|buckets) /.test(firstClause)
        ? backticked(firstClause)
        : [];
      const zeroPrice = [...firstClause.matchAll(/zero-price `([^`]+)`/g)].map((m) => m[1] ?? "");
      result.tags.push({ tag: token, label, amber: /vendor/.test(label), subCounters, zeroPrice });
    }
  }

  const counting = line.slice(countingAt, everyAt);
  result.counting = backticked(counting);
  const every = line.slice(everyAt);
  const [amberPart, sharePart] = every.split(";");
  result.amberSubCounters = backticked(amberPart ?? "");
  const share = /\(([a-z0-9-]+)'s share of (.*)\)/.exec(sharePart ?? "");
  if (share?.[1] === undefined || share[2] === undefined)
    throw new Error("the budget tags line names no share");
  for (const tag of backticked(share[2])) result.shares.push({ tag, service: share[1] });
  return result;
}

/** The services of CONVENTIONS' service index (L372 to L384) marked "(amber)", by platform group. */
export function amberServices(conventions: string): Record<string, string[]> {
  const index = conventions.slice(conventions.indexOf("## Service index"));
  const out: Record<string, string[]> = {};
  for (const line of index.split("\n")) {
    const m = /^([A-Za-z]+) \(\d+\): (.*)\.$/.exec(line.trim());
    if (m?.[1] === undefined || m[2] === undefined) continue;
    const amber = splitTop(m[2], ",")
      .filter((s) => /\(amber\)/.test(s))
      .map((s) => s.replace(/\(amber\)/, "").trim());
    if (amber.length > 0) out[m[1].toLowerCase()] = amber;
  }
  return out;
}

export interface SeriesProfileRow {
  routeLabel: string;
  serviceText: string;
  seriesText: string;
  repliesText: string;
}

/** The rows of the comment series profiles table (CONVENTIONS L405 to L421). */
export function seriesProfileRows(conventions: string): SeriesProfileRow[] {
  const lines = conventions.split("\n");
  const header = lines.findIndex((l) =>
    l.startsWith("| Route | Comment service | Series after the post is first seen | Replies |"),
  );
  if (header < 0) throw new Error("CONVENTIONS has no comment series profiles table");
  const rows: SeriesProfileRow[] = [];
  for (const line of lines.slice(header + 2)) {
    if (!line.startsWith("|")) break;
    const cells = line
      .split("|")
      .slice(1, -1)
      .map((c) => c.trim());
    if (cells.length !== 4)
      throw new Error(`a comment series row with ${cells.length} cells: ${line}`);
    const [routeLabel, serviceText, seriesText, repliesText] = cells as [
      string,
      string,
      string,
      string,
    ];
    rows.push({ routeLabel, serviceText, seriesText, repliesText });
  }
  return rows;
}

/**
 * The steps of a series cell as F2 seriesStep labels: "+1 h" is "+1h"; "then weekly to day 30"
 * after +7 d adds +14d, +21d and +28d; a push row has none.
 */
export function seriesSteps(seriesText: string): { steps: string[]; push: boolean } {
  if (/^push\b/.test(seriesText)) return { steps: [], push: true };
  const steps = [...seriesText.matchAll(/\+(\d+) ([hd])\b/g)].map((m) => `+${m[1]}${m[2]}`);
  if (steps.length === 0) throw new Error(`no steps in the series cell: ${seriesText}`);
  if (/weekly (to|until) day 30/.test(seriesText)) {
    if (steps[steps.length - 1] !== "+7d")
      throw new Error(`"weekly to day 30" does not follow +7 d: ${seriesText}`);
    for (let day = 14; day <= 30; day += 7) steps.push(`+${day}d`);
  }
  return { steps, push: false };
}
