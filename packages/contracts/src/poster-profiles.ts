// poster.profiles/v1: one flat message built from the qualifier's ten rules (ADR-0033). An ordinary
// individual's answer (account_type `individual`, public_account false) carries only what the
// qualifier may read of a person and is keyed by its author_ref; every other answer, a public
// person's included, carries the full field set and is keyed by its candidate key (ADR-0010).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { extras } from "./context.ts";
import { countrySignals, dataShape, langShare, metadataShape } from "./metadata.ts";
import {
  authorRef,
  candidateKey,
  count,
  httpUrl,
  nonEmpty,
  platformId,
  share,
  timestamp,
  uuid,
  vendorName,
} from "./primitives.ts";
import {
  ACCOUNT_TYPES,
  PLATFORMS,
  PROFILE_REVIEW_REASONS,
  PROFILE_STATUSES,
  PROFILE_UNRESOLVABLE_REASONS,
  RESOLVE_ORIGINS,
  REVIEW_FLAGS,
  ROUTES,
  SOURCE_TYPES,
} from "./vocabulary.ts";

export const POSTER_PROFILES = "poster.profiles/v1";

// With `review` a review reason, with `unresolvable` an unresolvable one, with `resolved` none
// (ADR-0033; Q8), which validate() pairs with the status.
const reason = () =>
  z.enum([...PROFILE_REVIEW_REASONS, ...PROFILE_UNRESOLVABLE_REASONS]).nullable();

const common = (b: SchemaBuilder) => ({
  ...metadataShape(b, POSTER_PROFILES),
  platform: z.enum(PLATFORMS),
  status: z.enum(PROFILE_STATUSES),
  reason: reason(),
  followers: count().nullable(),
  verified: z.boolean().nullable(),
  client_ids: z.array(uuid()),
  resolved_at: timestamp(),
  cached: z.boolean(),
  cached_until: timestamp().nullable(),
  ...dataShape(b),
});

export function buildPosterProfiles(b: SchemaBuilder) {
  const individual = b.titled(
    "IndividualProfile",
    b.obj({
      ...common(b),
      author_ref: authorRef(),
      account_type: z.literal("individual"),
      individual: z.literal(true),
      public_account: z.literal(false),
    }),
  );
  const full = b.titled(
    "Profile",
    b.obj({
      ...common(b),
      candidate_key: candidateKey(),
      source_id: uuid().nullable(),
      source_type: z.enum(SOURCE_TYPES).nullable(),
      account_type: z.enum(ACCOUNT_TYPES).nullable(),
      individual: z.boolean().nullable(),
      public_account: z.boolean().nullable(),
      platform_id: platformId().nullable(),
      handle: nonEmpty().nullable(),
      url: httpUrl().nullable(),
      display_name: z.string().nullable(),
      posts_30d: count().nullable(),
      last_post_at: timestamp().nullable(),
      posts_per_day: z.number().min(0).nullable(),
      duplicate_text_share: share().nullable(),
      default_avatar: z.boolean().nullable(),
      account_created_at: timestamp().nullable(),
      owned_by_client: z.boolean().nullable(),
      country_signals: countrySignals(b).nullable(),
      lang_share: langShare(b).nullable(),
      keyword_ids: z.array(uuid()),
      // The route the source would be read on, which rule 5 and the qualifier's `add` take;
      // `provenance` says how the profile itself was fetched (ADR-0033, ADR-0003; Q8).
      route: z.enum(ROUTES).nullable(),
      vendor: vendorName().nullable(),
      review_flags: z.array(z.enum(REVIEW_FLAGS)),
      extras: extras(b).optional(),
      post_count: count().optional(), // read by x-full-archive-search (ADR-0033)
      origin: z.enum(RESOLVE_ORIGINS).optional(), // echoed from the resolve job (ADR-0066 L28; F-15)
      proposed_source_id: uuid().optional(), // a news site's profile (ADR-0040)
    }),
  );
  return b.titled("PosterProfilesV1", z.union([individual, full]));
}

export type PosterProfile = z.infer<ReturnType<typeof buildPosterProfiles>>;
