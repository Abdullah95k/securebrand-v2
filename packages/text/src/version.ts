// The fold's version (D10). FOLD_VERSION names the fold; FOLD_DATA_SHA256 hashes the data it folds
// with, and data/fold-versions.json records both for every released version (E7). C3 builds
// FOLD_VERSION into lang_model_version (lang-dialect-id 5.1, 13 item 12).
import { createHash } from "node:crypto";
import { DATA_BYTES, DATA_FILES, FOLD_TABLE } from "./data.ts";

export const FOLD_VERSION: string = FOLD_TABLE.version;

const sha256 = (data: string | Buffer): string => createHash("sha256").update(data).digest("hex");

/** sha256 of "<file> <sha256 of its bytes>\n" for the fold table, the 15.1 data and the registry. */
export const FOLD_DATA_SHA256: string = sha256(
  DATA_FILES.map(([name], i) => `${name} ${sha256(DATA_BYTES[i] ?? "")}\n`).join(""),
);
