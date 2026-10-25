// Every refusal of the package is a TextError with a code, as contracts' ContractError is.

export type TextErrorCode =
  | "not_string" // the text is not a string
  | "no_lang" // no language label: the fold depends on the label, decided on the raw text first
  | "bad_lang" // a label outside contracts' LANG_LABELS
  | "not_unicode" // a lone surrogate, which no UTF-8 text can hold (F2's not_unicode)
  | "unicode_version"; // a runtime below Unicode 15.1 (D-2)

export class TextError extends Error {
  readonly code: TextErrorCode;

  constructor(code: TextErrorCode, message: string) {
    super(message);
    this.name = "TextError";
    this.code = code;
  }
}
