// Versions (ADR-0002): a consumer reads the versions it reads, skips a version the package knows that
// it does not read, and parks a version the package does not know.
import { CATALOGUE, catalogueId } from "./catalogue.ts";

/** Every schema id the package knows, `dlq.<service>/v1` as one id (F-52). */
export const SCHEMA_IDS: readonly string[] = CATALOGUE.map((e) => e.id);

export type VersionVerdict = "read" | "skip" | "park";

/**
 * What a consumer does with a message whose `schema` is `schemaId`: `read` it when the consumer reads
 * that id, `skip` a version the package knows that the consumer does not read, `park` an unknown one.
 */
export function classifyVersion(schemaId: string, reads: readonly string[]): VersionVerdict {
  const id = catalogueId(schemaId);
  if (reads.map(catalogueId).includes(id)) return "read";
  return SCHEMA_IDS.includes(id) ? "skip" : "park";
}
