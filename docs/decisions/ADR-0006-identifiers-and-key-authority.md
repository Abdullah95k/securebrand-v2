# ADR-0006 · Identifiers and key authority

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q006 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS gives the key form `<platform>:<kind>:<platform_id>` (L69) but not who applies it (CF-060). normalize-item "assigns the idempotency key every store relies on" (`normalize-item §1 L9`) from its own mapper (`§5.2 L51`), while most producers stamp a key in the envelope (for example `yt-pubsub-receiver §6.2 L112`), raw-archiver receives it (`raw-archiver §5.4 L86`), and deletion-propagator derives `item_id` "with the SDK helper that normalize-item uses" (`deletion-propagator §5.3 L60`). Where the two keys differ (ADR-0007), dedup, versions and deletions follow whichever wins. The build plan's foundation choice is "a deterministic hash of the idempotency key, with golden vectors in both languages" (FC-03, build plan L53). The formats differ too:

- `item_id` is `uuid_v5(ns_items, idempotency_key)` (`normalize-item §5.2 L51`), but the three deletion producers put ULIDs in their targets (`retention-purger §6.2 L102`, `x-compliance-sync §6.2 L105`, `yt-text-purger §6.2 L149`), values no store holds (CF-071).
- `job_id` is a ULID (CONVENTIONS L277), with deterministic ULIDs where replay needs them (`comment-decay-scheduler §5.3 L84`, `backfill-orchestrator §5.3 L85`), but examples show UUIDs, `job_…`, dated sequences, composites such as `res:x:1234567890` (`poster-resolver §5.3 L67`), `null` (`x-filtered-stream §6.2 L121`) and `update_id` instead (`tg-bot-channel-receiver §6.2 L123`) (CF-070).
- `client_id` and `keyword_id` are UUIDs in most PRDs and `cl_17` or `kw_0412` in a few, approved ones among them (`poster-resolver §6.2 L89`) (CF-072).

Settles: FC-03, CF-060, CF-070, CF-071, CF-072.
Depends on: ADR-0002 (`message_id`, `producer.job_id`), ADR-0007 (the key forms the golden vectors cover).

## Options

1. **One key helper in the contracts package, run by producers and checked by normalize-item; uuid v5 item ids; ULID job ids; UUID client and keyword ids** (chosen): its rules are under Decision.
2. **normalize-item alone computes the key; envelope keys are informational or absent (CF-060 option 2).** Formats as in 1. Consequences: one place to change a key, but producers lose the key they use for their own state (read ledgers, comment hashes, the reconciler's check, `yt-uploads-reconciler §5.2 L63`), raw-archiver files records without one, and a mapper bug forks items unnoticed.
3. **The producer's key is used unchecked and the validators are loosened (CF-060 option 1, CF-070 option 3, CF-072 option 2).** Consequences: fewest edits, but nothing catches two routes keying one object differently (the CF-061 to CF-066 problem), fixtures mix id formats, and F3 types ids as text.

## Decision

One key helper in the contracts package, with TypeScript and Python twins and golden vectors: producers stamp `idempotency_key` with it, and normalize-item recomputes and checks it. `item_id = uuid_v5(ns_items, key)`; `job_id` is a ULID; `client_id` and `keyword_id` are UUIDs.

- Authority (CF-060): the producer stamps `idempotency_key` with the contracts package's helper (TypeScript and Python twins), from the record and the envelope fields a key needs (the post reference of an id-less comment). normalize-item recomputes it with the same helper and parks a mismatch as `schema_unknown` (`normalize-item §5.2 L50`); deletion-propagator and x-compliance-sync derive keys with the same helper; nothing downstream edits a key.
- `item_id` (FC-03, CF-071): `uuid_v5(ns_items, key)` everywhere, `ns_items` one UUID constant frozen in the contracts package; deletion targets carry these ids. Byte rules for the golden vectors: the key is the UTF-8 bytes of its NFC form; platform and kind segment in lower case; the id rendered as ADR-0007 says; a hash inside a key is SHA-256 over NFC text, 64 lower-case hex, with times as UTC `YYYY-MM-DDTHH:MM:SSZ`; a hash over structured data uses canonical JSON (RFC 8785). Vectors cover every key form of ADR-0007, decomposed Arabic, emoji and the id-less comment key.
- Other deterministic ids follow the same two patterns: a uuid v5 under its own frozen namespace (`hit_id`, `keyword-matcher §5.3 L77`), or a ULID whose time part is the event's own time and whose random part is the first 10 bytes of SHA-256 over a declared input (`comment-decay-scheduler §5.3 L84`). keyword-matcher's replay-stable `message_id` becomes such a ULID (time `hit_at`, input `hit_id`, `item_version`, `keyword_set_version`).
- `job_id` (CF-070): a ULID on every job, deterministic where replay needs it; a record made without a job (the push receivers, x-filtered-stream) gets a ULID at receipt with `attempt = 1`, as li-notification-receiver does (`§6.2 L133`), and `update_id` and `connection_id` move into the producer's declared context (ADR-0005); `producer.job_id` (ADR-0002) carries the ULID of the job behind the message, copied by topic consumers, never a composite or `null`.
- `client_id`, `keyword_id` (CF-072): UUIDs in messages, tables and the budget tags that embed a client (`meta_graph_pages:<client_id>`, CONVENTIONS L279; lower-case canonical form, ADR-0042); a keyword-rule source is named by its `source_id` (ADR-0044); the prefixed forms are example errors.

Why: It makes the build plan's choice concrete: the key is computed by one piece of shared code, checked at the single translation point, and reproducible from either language, so dedup, versions, deletions and replays agree.

## Consequences

One implementation tested byte for byte in two languages, and a producer bug parks records instead of silently forking an item.

- CONVENTIONS v1.1: the key section (who stamps and who checks the key, the `item_id` derivation, the byte rules) and the job section (`job_id`, deterministic ids, jobless records).
- F2 writes the helper, the frozen namespaces (`ns_items` and one per other deterministic id) and the golden vectors. F3 and F8 type the id columns `uuid`.
- PRD examples that show other id formats (`cl_17`, `kw_0412`, `job_…`, UUID and dated job ids, composites, `null`, ULIDs as deletion `item_ids`) are corrected in this pull request, approved PRDs among them under ADR-0001, each corrected example citing this ADR.

Sessions that must read this: F2, F3, F8, then F4, F6, C4, C6, C13, C14, X7, YT7 and every `raw.items` producer.
