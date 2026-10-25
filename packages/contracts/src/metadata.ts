// What every message carries (ADR-0002, ADR-0003), and the definitions several topics share. Each
// takes the builder, so one definition serves the producer and the consumer variant.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import {
  PATTERNS,
  count,
  date,
  serviceName,
  share,
  timestamp,
  token,
  ulid,
  uuid,
  vendorName,
} from "./primitives.ts";
import { COUNTRY_SIGNALS, RETENTION_CLASSES, ROUTES, USAGE_SIGNAL_VALUES } from "./vocabulary.ts";

/** `producer {service, version, job_id}`: the service that emitted the message (ADR-0002, ADR-0006 L31). */
export const producer = (b: SchemaBuilder) =>
  b.def("Producer", () =>
    b.obj({ service: serviceName(), version: token().max(64), job_id: ulid() }),
  );

/** The four fields the SDK stamps on every message and job (ADR-0002). */
export const metadataShape = <S extends string>(b: SchemaBuilder, schemaId: S) => ({
  schema: z.literal(schemaId),
  message_id: ulid(),
  produced_at: timestamp(),
  producer: producer(b),
});

/** `dlq.<service>/v1`: the one schema id that is a pattern (Q5, F-52). */
export const dlqMetadataShape = (b: SchemaBuilder) => ({
  schema: z.string().regex(PATTERNS.dlqSchema),
  message_id: ulid(),
  produced_at: timestamp(),
  producer: producer(b),
});

/** Where the data came from: the route, vendor and service that fetched it, and when (ADR-0003). */
export const provenance = (b: SchemaBuilder) =>
  b.def("Provenance", () =>
    b.obj({
      route: z.enum(ROUTES),
      vendor: vendorName().nullable(),
      service: serviceName(),
      fetched_at: timestamp(),
    }),
  );

/**
 * The provenance of a signal that is no platform fetch (an author-, source- or client-scope
 * deletion): route and vendor are null for the reasons that involve no fetch (ADR-0003 L28; F-08).
 */
export const signalProvenance = (b: SchemaBuilder) =>
  b.def("SignalProvenance", () =>
    b.obj({
      route: z.enum(ROUTES).nullable(),
      vendor: vendorName().nullable(),
      service: serviceName(),
      fetched_at: timestamp(),
    }),
  );

export const retentionClass = () => z.enum(RETENTION_CLASSES);

/** The data fields of a data message (ADR-0003). */
export const dataShape = (b: SchemaBuilder) => ({
  provenance: provenance(b),
  retention_class: retentionClass(),
});

/** ADR-0033's six country signals and what matched, for review cards. */
export const countrySignals = (b: SchemaBuilder) =>
  b.def("CountrySignals", () =>
    b.obj({
      iraqi_place: z.boolean(),
      platform_country_iq: z.boolean(),
      phone_964: z.boolean(),
      iq_domain: z.boolean(),
      outlet_link: z.boolean(),
      seed_list: z.boolean(),
      signal_evidence: z.array(
        b.def("SignalEvidence", () =>
          b.obj({
            signal: z.enum(COUNTRY_SIGNALS),
            matched: z.string().min(1),
            where: z.string().min(1),
          }),
        ),
      ),
    }),
  );

/** Shares over the sample keyed by lang-dialect-id's labels, plus ar_iraqi and the sample size (ADR-0033). */
export const langShare = (b: SchemaBuilder) =>
  b.def("LangShare", () =>
    b.obj({
      ar: share(),
      ckb: share(),
      en: share(),
      mixed: share(),
      other: share(),
      und: share(),
      ar_iraqi: share(),
      sample: count(),
    }),
  );

/**
 * A count and a share as named definitions, the value types of the open maps: the Python generator
 * renders a named value type as a class, an inline one as an alias pyright and ruff refuse.
 */
export const countDef = (b: SchemaBuilder) => b.def("Count", () => count());
export const shareDef = (b: SchemaBuilder) => b.def("Share", () => share());

/** Engagement counts, each null where the platform has none (ADR-0034; F-34). */
export const metrics = (b: SchemaBuilder) =>
  b.def("Metrics", () =>
    b.obj({
      views: count().nullable(),
      likes: count().nullable(),
      comments: count().nullable(),
      shares: count().nullable(),
      // Each reaction type the platform returns, in lower case, to its count: platform data, not a
      // closed list (Facebook like, love, haha, wow, sad, angry, care). validate() checks the keys
      // are snake_case: a key pattern is a construct the Python generator cannot render (ADR-0030).
      reactions_by_type: z.record(z.string(), countDef(b)).nullable(),
      saves: count().nullable().optional(),
    }),
  );

/** Content-Signal directives, the hyphen replaced by an underscore (ADR-0068, ADR-0070 b)). */
export const usageSignals = (b: SchemaBuilder) =>
  b.def("UsageSignals", () =>
    b.obj({
      search: z.enum(USAGE_SIGNAL_VALUES),
      ai_input: z.enum(USAGE_SIGNAL_VALUES),
      ai_train: z.enum(USAGE_SIGNAL_VALUES),
    }),
  );

/**
 * platform_meta, typed per platform and source type (ADR-0065 c), ADR-0013 c), ADR-0041): each key
 * belongs to one (platform, source type), which validate() checks; every other pair has none yet.
 */
export const platformMeta = (b: SchemaBuilder) =>
  b.def("PlatformMeta", () =>
    b.obj({
      uploads_playlist_id: token().optional(), // youtube channel
      ig_user_id: z.string().regex(PATTERNS.digits).optional(), // instagram hashtag: the bound account
      linked_channel_source_id: uuid().optional(), // telegram group: its channel's source
      linked_chat_id: z.string().regex(PATTERNS.chatId).optional(), // telegram group: its channel's chat id
    }),
  );

/** A window of time, as fb-backfill's context and the X gap job name it. */
export const window = (b: SchemaBuilder) =>
  b.def("Window", () => b.obj({ start: timestamp(), end: timestamp() }));

/** A UTC calendar date, as Common Crawl's capture days are written. */
export const day = date;
