# ADR-0009 · Comment records, content hash and edits

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk, normalize-item, store-writer, deletion-propagator, fb-client-webhook-receiver, ig-webhook-receiver, and the lanes Comments and Comments and stats (every comment fetcher and receiver)
Source: D2-Q009 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Every comment producer spells the same four facts its own way (CF-007): the parent link (`parent_platform_id`, `post_ref`, `parent_post_id`, `parent_video_id` and more); the content hash (`text_hash` in bare hex, `content_hash` with a `sha256:` prefix, `text_sha256`); the edit marker (`edit_of`, `version`, `observation`, `event`); and the redaction marker (`payload_redacted`, `removed_fields`, `minimized`, `identity: "hashed"`). normalize-item reads none of them and derives its own (`normalize-item §5.2 L49`, `L51`, `§5.3 L70`).

The Instagram fetchers hash "the SHA-256 of its `text`" (`ig-own-comments-fetcher §5.1 L49`) and compare it with normalize-item's stored `sha256(title + text + media urls)` (`normalize-item §5.2 L51`), so a comment with a media URL looks edited at every read (AU-090). CONVENTIONS says "changed text becomes a new version" (L63) but keys comments without platform ids on their text (L69), a form three vendor routes also use (`fb-group-comments-fetcher §5.4 L94`, `ig-comments-fetcher §6.2 L115`, `li-post-comments-fetcher §6.2 L129`) (CF-067 a, d). fb-post-comments-fetcher sends an edited PPCA comment under a new key with `edit_of` and expects a version (`§5.2 L68`), which normalize-item never reads (AU-049); news-comments-fetcher puts the version in the key, `news:comment:6203918455:v1` (`§6.2 L101`); the routes with ids keep the key (`fb-group-comments-fetcher §5.2 L65`, `tg-discussion-receiver §9 L163`) (CF-067 b, c). At stake: double-counted comments, false edits, and a parent link no reader can rely on.

Settles: CF-007, CF-067, AU-049, AU-090, RN-13.
Depends on: ADR-0006 (the key helper), ADR-0007 (keys), ADR-0010 (what an adapter removes), ADR-0062 (deletion on absence).

## Options

1. **One comment field set, one hash helper, versions under one key where the platform gives ids, and a new comment where it gives none** (chosen): its rules are under Decision.
2. **As 1, but id-less edits linked: the fetcher keeps `edit_of` and normalize-item publishes the new text as a version of the old key's `item_id` (CF-067 option 1, AU-049 option 1).** Consequences: an edit stays one item, but `item_id` stops being derivable from the key (ADR-0006), and two real comments can be merged, since "an edit cannot be told from two comments written in the same second" (`fb-post-comments-fetcher §5.2 L68`).
3. **No comment fields in the envelope: normalize-item derives parent, hash and version from the payload (CF-007 option 2).** Consequences: thinner envelopes, but PPCA and vendor payloads name no post, so those comments cannot be placed, and producers still need the hash.

## Decision

One comment field set (`parent_id`, `root_id`, `parent_seen`, `content_hash`, `version`, and `redacted_fields` on any record) and one SDK hash helper used on both sides. Where the platform gives comment ids, an edit is a new version under the same key; where it gives none, changed text is a new comment and the old key a deletion.

- Fields (CF-007 a), normalize-item's names on `items.normalized`: `parent_id`, the parent's `item_id` (the post for a top-level comment, the parent comment for a reply); `root_id`, the post's `item_id`; `parent_seen` for orphans (`normalize-item §5.1 L43`); `content_hash`; `version`. A comment's `raw.items` envelope carries `parent_id` and `root_id`, stamped by the producer from the job's `post_ref` (ADR-0011) and the key helper, since PPCA and vendor payloads name no post; normalize-item checks them where the payload has a reference. The envelope spellings above go.
- Redaction (CF-007 d): `redacted_fields`, one optional envelope field on any record: the payload paths an adapter removed or replaced (what it removes is ADR-0010's).
- Hash (CF-007 b, AU-090): one SDK helper, `content_hash = "sha256:"` plus the hex SHA-256 of the NFC text, preceded by the NFC title and U+001F when the item has a title. A comment has none, so its hash covers its text only; media URLs are left out, since signed URLs change. Producers hash their registered mapper's output (ADR-0008), so both sides hash the same string.
- Edits where the platform gives a stable id (CF-067 c, d): the key stays and normalize-item publishes `version + 1` when the hash changes (`normalize-item §5.2 L52`); producers send no edit marker (those above and `is_edited` go; the platform's edit time stays in the payload); news-comments-fetcher drops its `:vN` suffix. RN-13: D1 notes that CF-067 c) cites `tg-bot-channel-receiver §9 L159`, a post line; the rule covers posts too, and that line agrees.
- Edits where the platform gives none (CF-067 a, b, AU-049): the CONVENTIONS hash form becomes the rule for every id-less comment route, `<platform>:comment:<post id>:<sha256(created_time + text)>`, so changed text is a new comment. The old key becomes a `deletions` message (reason `platform_sync`) under ADR-0062's confirmed-miss rule, and on a route that never deletes on absence (Instagram vendor comments) the old text stays until retention removes it. fb-post-comments-fetcher drops `edit_of` and its `superseded` outcome (`§5.2 L68`, `§13 L176`), fb-group-comments-fetcher its id-less `superseded` (`§5.2 L65`). Vendor probes first confirm that creation times are stable across reads.

Why: One helper on both sides ends the false versions AU-090 found; one key with versions is what CONVENTIONS L63 and normalize-item already do; where no platform id exists, nothing reliably links old and new text, so the record shows one comment gone and one new.

## Consequences

One field set and one helper in F2, with golden vectors; normalize-item (approved) changes its hash formula under ADR-0001; an edited id-less comment shows as one deletion plus one new comment, counts stay right, the link between the texts is lost.

- CONVENTIONS v1.1: the edit rule (versions where ids exist; an id-less edit is a new comment plus a deletion), the hash key form for every id-less comment route, and the comment fields and `redacted_fields` with the `raw.items` envelope (ADR-0005).
- The probes of the id-less routes confirm that creation times are stable across reads before those routes rely on the hash key: FB0 for PPCA comments, VFB0, VIG0 and VLI0 for the vendor routes (`DEFERRED.md`).
- RN-13 is closed by this record.

Sessions that must read this: F2, F4, then C4, C6, C13, FB5, FB7, VFB3, IG4, IG6, VIG2, LI2, LI3, VLI4, VTT5, X6, YT5, YT6, N8, TG1, TG2.
