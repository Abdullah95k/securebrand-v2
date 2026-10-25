// The text package (F7): the Arabic and Sorani fold of lang-dialect-id 5.3 C, which normalize-item's
// fallback and keyword-matcher's compile import (they copy nothing), and its tokenizer helpers.
export { TextError, type TextErrorCode } from "./errors.ts";
export { fold, textNorm, type LangLabel } from "./fold.ts";
export {
  SORANI_ONLY_LETTERS,
  cpLength,
  cpSlice,
  hasSoraniLetter,
  tokenize,
  type Token,
} from "./tokens.ts";
export { FOLD_DATA_SHA256, FOLD_VERSION } from "./version.ts";
