import { PLACEHOLDER_KEYWORD } from "./config.ts";

export type Lang = "ar" | "ckb" | "en";
export interface Keyword {
  text: string;
  lang: Lang;
}

// Letters that Sorani uses and Arabic does not.
const SORANI = /[ێڕڵۆڤەگپچژ]/u;
const ARABIC = /[؀-ۿ]/u;

export function detectLang(text: string): Lang {
  if (SORANI.test(text)) return "ckb";
  if (ARABIC.test(text)) return "ar";
  return "en";
}

/** One keyword per line; blank lines and lines starting with # are skipped. */
export function parseKeywords(content: string): Keyword[] {
  const seen = new Set<string>();
  const out: Keyword[] = [];
  for (const raw of content.split(/\r?\n/)) {
    const text = raw.trim();
    if (text === "" || text.startsWith("#") || seen.has(text)) continue;
    seen.add(text);
    out.push({ text, lang: detectLang(text) });
  }
  return out;
}

export function isPlaceholder(keywords: Keyword[]): boolean {
  return keywords.length === 0 || keywords.every((k) => k.text === PLACEHOLDER_KEYWORD);
}

/** Up to `n` keywords, spread evenly over the three languages, so a capped vendor sees all of them. */
export function sample(keywords: Keyword[], n: number): Keyword[] {
  const by: Record<Lang, Keyword[]> = { ar: [], ckb: [], en: [] };
  for (const k of keywords) by[k.lang].push(k);
  const out: Keyword[] = [];
  for (let i = 0; out.length < Math.min(n, keywords.length); i++) {
    for (const lang of ["ar", "ckb", "en"] as const) {
      const k = by[lang][i];
      if (k !== undefined && out.length < n) out.push(k);
    }
  }
  return out;
}
