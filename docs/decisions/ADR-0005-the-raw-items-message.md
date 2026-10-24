# ADR-0005 · The raw.items message

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk (F4, F6), raw-archiver, normalize-item, backfill-orchestrator, comment-decay-scheduler, and the lanes Discover and qualify, Fetch posts, Comments and Comments and stats (every `raw.items` producer)
Source: D2-Q005 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Most producers write a nested `{"envelope": {...}, "payload": {...}}` message (`fb-page-feed-poller §6.2 L110-L126`, `ig-account-media-poller §6.2 L106-L123`, `li-post-search §6.2 L85-L102` and others); ig-hashtag-search and yt-keyword-search write flat fields with the record under `payload`; tt-keyword-search, tt-hashtag-feed-poller and x-recent-search under `raw` and `includes`; the web engines and tg-message-search give only a prose list (CF-004). The readers assume nesting: raw-archiver reads `envelope.raw_ref` and writes an envelope file and a payload file (`raw-archiver §5.2 L50`, `§5.3 L67`), normalize-item "read[s] the envelope" (`normalize-item §5.2 L49`). Both shapes are on the approved list. The envelope's fields differ too (CF-005): the usual set (`fb-page-feed-poller §6.2 L112-L123`) is missing pieces in a dozen producers; normalize-item selects its mapper by `(service, api_version)` and reads `job_kind`, but `api_version` is written by two producers and `job_kind` by four (CF-005 d); producers stamp `retention_class` while normalize-item stamps it again "(source row, else route and platform default)" (`normalize-item §5.2 L55`; CF-005 c); raw-archiver needs `raw_ref` (`<object key>#<line>`, allocated by the SDK, `raw-archiver §11 L157`) where 33 producers write `batch`; and some twenty producer-specific fields (`edge`, `window`, `matching_rules`, `url_key` and others) have no shared definition. Some records cannot fill that set: resolver profiles of candidates have no `source_id` yet (`poster-resolver §5.2 L58`, `§6.2 L92`; `tg-channel-resolver §5.2 L57`; `tt-user-resolver §5.1 L41`), the web engines write one record per API response with no `platform_id` or `idempotency_key` (`web-search-perplexity §6.2 L89`), and the stream writes `"job_id": null, "attempt": null` (`x-filtered-stream §6.2 L121`). Why a record was read travels as `metrics_observation`, `job_kind`, `origin`, `delivery` or `ingest_mode` (CF-006): the first two have three readers between them (fb-reactions-fetcher labels observations from `metrics_observation`; normalize-item reads `job_kind`, and comment-decay-scheduler expects `job_kind = backfill` "carried from the raw envelope" onto `items.normalized`, `comment-decay-scheduler §5.1 L66`; AU-002, AU-015); `origin`, `delivery` and `ingest_mode` have none (CF-006 c).

Settles: CF-004, CF-005, CF-006, AU-002, AU-015.
Depends on: ADR-0002, ADR-0003, ADR-0006 (who computes the key), ADR-0008 (the record kinds).

## Options

1. **Nested `{envelope, payload}` for every producer, one envelope type built by the SDK with conditional fields, and one `job_kind`** (chosen): its rules are under Decision.
2. **Flat records with reserved top-level envelope names and the platform record always under `payload`.** Consequences: shorter messages; raw-archiver and normalize-item change how they split and read; reserved names can collide with platform fields.
3. **Both shapes on the wire, the SDK wrapping flat records before publishing.** Consequences: no PRD changes, but the SDK carries two input shapes forever, and fixtures must cover both.

   The envelope and label alternatives D1 named, rejected with option 1: a small required set with key and class computed downstream by normalize-item (CF-005 option 2; the key then differs by who computes it, CF-060); a required set per route family (CF-005 option 3; three envelope types where one with conditions does); `metrics_observation` as the one label, or both fields (CF-006 options 2 and 3; `job_kind` and the series step already say what the counts are).

## Decision

`raw.items` is one nested `{envelope, payload}` message for every producer. The payload is the platform record as returned, minus identities (ADR-0010). The SDK builds the envelope, with always-required, conditional and optional fields, and why a record was read travels as one field, `job_kind`.

- Shape: `payload` holds the platform record as returned (minus identities, ADR-0010), with `includes` and other response parts inside it; the envelope holds everything else.
- Envelope, always required: `platform`, `kind` (the record kind from ADR-0008, archive-only kinds such as `profile` and `search_response` included), `provenance` (ADR-0003), `retention_class`, `client_ids`, `job_id`, `attempt`, `job_kind`, `api_version`, `raw_ref`; plus `schema`, `message_id`, `produced_at`, `producer` (ADR-0002).
- Required by condition: `source_id`, or `candidate_key` for a record about a candidate that is not yet a source (ADR-0004 names `candidate_key` as that record's key); `platform_id` and `idempotency_key` for item kinds, while archive-only kinds carry a defined key instead (for `search_response`, the rule's `source_id` plus the request time); on push and stream records, a `job_id` made at receipt (a ULID, ADR-0006) with `attempt = 1`, the delivery id (`update_id`, `connection_id`) going in `context`; on a comment, `parent_id`, `root_id` and the optional `redacted_fields`, as ADR-0009 defines them; `redacted_fields` is optional on any record, comments included (ADR-0009).
- Optional: a typed `context` object, its keys declared per producer in the contracts package (the producer-specific fields go there, each defined). `batch` is dropped: `raw_ref` names the object and line.
- The SDK producer fills the envelope from the job and the adapter, and stamps `retention_class` from the source row, else the route and platform default; normalize-item copies it. Services hand over the payload and the adapter's fields, never a hand-built envelope.
- `job_kind` is the job's `kind` (for jobless receivers and the stream, the fixed values `push` and `stream`); it travels onto `items.normalized`, which is how backfilled records are recognised (AU-002, AU-015). `metrics_observation`, `origin`, `delivery` and `ingest_mode` are dropped; `item.metrics` labels derive from `job_kind` and the series step (ADR-0034).

Why: It is the majority shape and the one both readers expect; an SDK-built envelope with written conditions removes the missing fields at their source; one `job_kind` answers "why was this read" for every consumer.

## Consequences

One contracts type that all 48 producers can satisfy; raw-archiver and normalize-item work as written; the five flat-shape approved PRDs change their examples under ADR-0001.

- CONVENTIONS v1.1, `raw.items` in the event bus section: the shape, the required, conditional and optional envelope fields, `raw_ref`, `job_kind` and its fixed values `push` and `stream`.
- F2 defines the envelope type with its conditions and each producer's declared `context` keys; F4 and F6 fill the envelope from the job and the adapter.

Sessions that must read this: F2, F4, F6, C2, C4, C10, C11, then every `raw.items` producer (FB4, IG2, VTT1, VTT2, X1, YT8, VTG1, W1, W2, W4, N6, TG1, TG2, X4, X5, VLI1, YT4, N8, FB3, FB7, IG3, IG4, IG5, VIG1, VFB1, VFB2, VTG3, YT2).
