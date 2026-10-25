// items.analysis/v1: one message per (item, task, model version) (ADR-0023), with provenance and
// retention class copied from the item (ADR-0003). `result` is typed per task: the fields readers use
// (store-writer's projections, aggregator's rollups, ADR-0023, ADR-0048) required, the rest optional;
// the shapes the PRDs give only in prose are Q8's. A skipped analysis carries a reason and no result.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape } from "./metadata.ts";
import {
  PATTERNS,
  count,
  nonEmpty,
  prefixedSha256,
  sha256Hex,
  share,
  snakeName,
  timestamp,
  token,
  uuid,
} from "./primitives.ts";
import {
  ANALYSIS_LANES,
  ANALYSIS_RUN_KINDS,
  ANALYSIS_SKIP_REASONS,
  ANALYSIS_STATUSES,
  CONTENT_KINDS,
  ENTITY_SOURCES,
  ENTITY_TYPES,
  INTENT_LABELS,
  LANG_LABELS,
  PLATFORMS,
  SENTIMENT_LABELS,
  TOPIC_SOURCES,
} from "./vocabulary.ts";

export const ITEMS_ANALYSIS = "items.analysis/v1";

const offsetPair = () => z.array(count()).length(2);
const topicId = () => z.string().regex(PATTERNS.topicId);

const shape = (b: SchemaBuilder) => ({
  ...metadataShape(b, ITEMS_ANALYSIS),
  analysis_key: z.string().regex(PATTERNS.analysisKey),
  input_hash: prefixedSha256(),
  item_id: uuid(),
  model_version: z.string().regex(PATTERNS.modelVersion),
  item_created_at: timestamp().nullable(),
  item_version: count().min(1),
  content_hash: prefixedSha256(),
  platform: z.enum(PLATFORMS),
  kind: z.enum(CONTENT_KINDS),
  source_id: uuid(),
  run_kind: z.enum(ANALYSIS_RUN_KINDS),
  lane: z.enum(ANALYSIS_LANES),
  status: z.enum(ANALYSIS_STATUSES),
  // With `skipped`, why; null with `ok` (validate() pairs them).
  reason: z.enum(ANALYSIS_SKIP_REASONS).nullable(),
  lang: z.enum(LANG_LABELS).nullable(),
  dialect: snakeName().nullable(),
  kb_version: count().nullable().optional(), // analysis-entities' knowledge base
  preproc_version: token().nullable().optional(), // analysis-sentiment
  taxonomy_version: count().nullable().optional(), // analysis-topics
  degraded: z.boolean().optional(), // analysis-entities on its gazetteer alone (§8 L129)
  zero_shot_unavailable: z.boolean().optional(), // analysis-topics (§8 L134)
  expires_at: timestamp().nullable(),
  ...dataShape(b),
});

const media = (b: SchemaBuilder, title: string, extra: z.ZodRawShape) =>
  z.array(
    b.def(title, () =>
      b.obj({
        index: count(),
        type: snakeName(),
        sha256: sha256Hex(),
        reused: z.boolean(),
        ...extra,
      }),
    ),
  );

export function buildItemsAnalysis(b: SchemaBuilder) {
  const branch = (title: string, task: z.ZodType, result: z.ZodType) =>
    b.titled(title, b.obj({ ...shape(b), task, result: result.nullable() }));
  return b.titled(
    "ItemsAnalysisV1",
    z.union([
      branch(
        "SentimentAnalysis",
        z.literal("sentiment"),
        b.def("SentimentResult", () =>
          b.obj({
            label: z.enum(SENTIMENT_LABELS),
            score: z.number(),
            confidence: share(),
            probs: b
              .def("SentimentProbs", () =>
                b.obj({ positive: share(), negative: share(), neutral: share(), mixed: share() }),
              )
              .optional(),
            low_confidence: z.boolean().optional(),
            sarcasm_prob: share().optional(),
            sarcasm_flag: z.boolean().optional(),
            code_switched: z.boolean().optional(),
            truncated: z.boolean().optional(),
            model_route: nonEmpty().optional(),
          }),
        ),
      ),
      branch(
        "SentimentAspectAnalysis",
        z.literal("sentiment_aspect"),
        b.def("SentimentAspectResult", () =>
          b.obj({
            targets: z.array(
              b.def("SentimentTarget", () =>
                b.obj({
                  keyword_id: uuid(),
                  label: z.enum(SENTIMENT_LABELS),
                  score: z.number(),
                  matched_term: nonEmpty().optional(),
                  offsets: z.array(offsetPair()).optional(),
                  confidence: share().optional(),
                }),
              ),
            ),
          }),
        ),
      ),
      branch(
        "TopicsAnalysis",
        z.string().regex(PATTERNS.topicsTask),
        b.def("TopicsResult", () =>
          b.obj({
            topics: z.array(
              b.def("TopicScore", () =>
                b.obj({ topic_id: topicId(), score: share(), source: z.enum(TOPIC_SOURCES) }),
              ),
            ),
            top_topic: topicId().nullable(),
            intent: b
              .def("Intent", () => b.obj({ label: z.enum(INTENT_LABELS), score: share() }))
              .nullable()
              .optional(),
            low_confidence: z.boolean().optional(),
          }),
        ),
      ),
      branch(
        "TopicClusterAnalysis",
        z.literal("topic_cluster"),
        b.def("TopicClusterResult", () => b.obj({ cluster_id: token() })),
      ),
      branch(
        "EntitiesAnalysis",
        z.literal("entities"),
        b.def("EntitiesResult", () =>
          b.obj({
            entities: z.array(
              b.def("Entity", () =>
                b.obj({
                  type: z.enum(ENTITY_TYPES),
                  entity_id: nonEmpty().nullable(),
                  start: count(),
                  end: count(),
                  source: z.enum(ENTITY_SOURCES),
                  name_en: z.string().nullable().optional(),
                  level: nonEmpty().nullable().optional(),
                  governorate_id: nonEmpty().nullable().optional(),
                  surface: z.string().optional(),
                  link_score: share().nullable().optional(),
                }),
              ),
            ),
            unlinked: z
              .array(
                b.def("UnlinkedEntity", () =>
                  b.obj({
                    type: z.enum(ENTITY_TYPES),
                    surface: z.string(),
                    start: count(),
                    end: count(),
                  }),
                ),
              )
              .optional(),
            private_person_mentions: count().optional(),
          }),
        ),
      ),
      branch(
        "MediaFetchAnalysis",
        z.literal("media_fetch"),
        b.def("MediaFetchResult", () => b.obj({ media: media(b, "FetchedMedia", {}) })),
      ),
      branch(
        "MediaOcrAnalysis",
        z.literal("media_ocr"),
        b.def("MediaOcrResult", () =>
          b.obj({
            media: media(b, "OcrMedia", {
              text: z.string(),
              lang: z.enum(LANG_LABELS).nullable().optional(),
              script: snakeName().nullable().optional(),
              confidence: share().nullable().optional(),
              frames: count().nullable().optional(),
              truncated: z.boolean().optional(),
            }),
          }),
        ),
      ),
      branch(
        "MediaTagsAnalysis",
        z.literal("media_tags"),
        b.def("MediaTagsResult", () =>
          b.obj({
            media: media(b, "TaggedMedia", {
              tags: z.array(b.def("MediaTag", () => b.obj({ tag: nonEmpty(), score: share() }))),
            }),
          }),
        ),
      ),
      branch(
        "MediaAsrAnalysis",
        z.literal("media_asr"),
        b.def("MediaAsrResult", () =>
          b.obj({
            media: media(b, "TranscribedMedia", {
              segments: z.array(
                b.def("AsrSegment", () =>
                  b.obj({
                    start: z.number().min(0),
                    end: z.number().min(0),
                    text: z.string(),
                    confidence: share().nullable().optional(),
                  }),
                ),
              ),
              lang: z.enum(LANG_LABELS).nullable().optional(),
              dialect: snakeName().nullable().optional(),
            }),
          }),
        ),
      ),
      branch(
        "MediaLogoAnalysis",
        z.literal("media_logo"),
        b.def("MediaLogoResult", () =>
          b.obj({
            media: media(b, "LogoMedia", {
              logos: z.array(
                b.def("Logo", () =>
                  b.obj({
                    brand_id: nonEmpty(),
                    score: share(),
                    box: z.array(z.number()).length(4).optional(),
                    frame_time: z.number().min(0).nullable().optional(),
                  }),
                ),
              ),
            }),
          }),
        ),
      ),
    ]),
  );
}

export type ItemAnalysis = z.infer<ReturnType<typeof buildItemsAnalysis>>;
