/** Thrown by every helper for an input it refuses; `code` names the rule. */
export class ContractError extends Error {
  readonly code: string;
  constructor(code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = "ContractError";
    this.code = code;
  }
}
