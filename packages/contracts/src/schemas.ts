// The Zod schema of every schema id, in either mode (ADR-0002, ADR-0030): "producer" refuses unknown
// fields, "consumer" drops them. A schema carries the shape only; validate() from the package root adds
// the cross-field and registry checks JSON Schema cannot express, so services call validate().
export type { Mode } from "./builder.ts";
export { CATALOGUE, catalogueId, schemaFor } from "./catalogue.ts";
