// Every object schema is written once, through a builder, and built twice: the producer variant
// refuses unknown fields and the consumer variant drops them (ADR-0002: producers validate strictly,
// consumers tolerate unknown fields of a known version).
import { z } from "zod";

export type Mode = "producer" | "consumer";

export interface SchemaMeta {
  readonly id?: string;
  readonly title?: string;
}

export interface SchemaBuilder {
  readonly mode: Mode;
  /** An object schema: strict in producer mode, stripping unknown keys in consumer mode. */
  obj<T extends z.ZodRawShape>(shape: T): z.ZodObject<T, z.core.$strict>;
  /** A shared definition, built once per builder and exported to JSON Schema `$defs` under `id`. */
  def<S extends z.ZodType>(id: string, build: () => S): S;
  /** A title for a top-level schema in the JSON Schema export. */
  titled<S extends z.ZodType>(title: string, schema: S): S;
}

export function createBuilder(
  mode: Mode,
  registry?: z.core.$ZodRegistry<SchemaMeta>,
): SchemaBuilder {
  const defs = new Map<string, unknown>();
  return {
    mode,
    obj<T extends z.ZodRawShape>(shape: T): z.ZodObject<T, z.core.$strict> {
      if (mode === "producer") return z.strictObject(shape);
      // The stripping object has the same output type as the strict one; only parsing differs.
      return z.object(shape);
    },
    def<S extends z.ZodType>(id: string, build: () => S): S {
      const known = defs.get(id);
      if (known) return known as S;
      const schema = build();
      defs.set(id, schema);
      registry?.add(schema, { id, title: id });
      return schema;
    },
    titled<S extends z.ZodType>(title: string, schema: S): S {
      registry?.add(schema, { title });
      return schema;
    },
  };
}
