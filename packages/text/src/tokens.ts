// STUB: the tests come first. Replaced by the tokenizer helpers.
export interface Token {
  readonly text: string;
  readonly start: number;
  readonly end: number;
  readonly kind: "word" | "hashtag" | "mention";
}

export const SORANI_ONLY_LETTERS: readonly string[] = [];

export function hasSoraniLetter(s: string): boolean {
  void s;
  return false;
}

export function cpLength(s: string): number {
  return s.length;
}

export function cpSlice(s: string, start: number, end?: number): string {
  return s.slice(start, end);
}

export function tokenize(textNorm: string): Token[] {
  void textNorm;
  return [];
}
