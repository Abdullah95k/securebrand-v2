// STUB: the tests come first (docs/plans/F7.md, order of work). Replaced by the fold.
import type { LANG_LABELS } from "contracts";

export type LangLabel = (typeof LANG_LABELS)[number];

export function fold(text: string, lang: LangLabel): string {
  void lang;
  return text;
}

export function textNorm(
  title: string | null | undefined,
  text: string | null | undefined,
  lang: LangLabel,
): string {
  const parts: string[] = [];
  for (const s of [title, text])
    if (s !== null && s !== undefined && s !== "") parts.push(fold(s, lang));
  return parts.join(" ");
}
