# ADR-0066 · Client-owned property onboarding

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F3, registry-writer, backfill-orchestrator, poster-resolver, qualifier, li-org-resolver, fb-client-webhook-receiver, ig-webhook-receiver, li-notification-receiver, tg-bot-channel-receiver, tg-discussion-receiver, yt-pubsub-receiver, D3 (the client portal and admin console)
Source: D2-Q066 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

registry-writer leaves subscriptions to the receivers, which "react to `added` themselves" (`registry-writer §3 L32`), as three do (`fb-client-webhook-receiver §5.1 L46`, `li-notification-receiver §5.1 L42`, `yt-pubsub-receiver §5.2 L50`); ig-webhook-receiver reads no `source.events` and subscribes when "an account is connected", with no trigger (`§5.1 L45`, `§6.1 L99`; AU-018). Telegram onboarding (AU-026, AU-057) rests on "an onboarding record with a one-time code and a pre-allocated `source_id`" that no table holds (`tg-bot-channel-receiver §5.2 L67`), then a `discovery.hits` candidate with `origin = client_onboarding` and `proposed_source_id` that poster-resolver and the qualifier should treat as always qualifying (`tg-bot-channel-receiver §5.2 L70`; `tg-discussion-receiver §5.2 L67`); both receivers set `backfill_status = capped` (`tg-bot-channel-receiver §5.1 L50`, `tg-discussion-receiver §5.1 L51`). registry-writer inserts with `gen_random_uuid()` and sends manual adds to poster-resolver as `origin: manual` (`registry-writer §5.3 L69`, `§5.2 L61`), the only origins poster-resolver and the qualifier know besides `discovery` (`poster-resolver §3 L27`, `qualifier §3 L27`); li-org-resolver expects onboarding candidates from registry-writer as `seed` (`li-org-resolver §5.1 L44`). At stake: a client's own Telegram channel can be typed as an individual or looked up through a paid vendor, early posts are orphaned under an unused id, and a connected Instagram account may get no webhook.

Settles: AU-018, AU-026, AU-057, tg-bot-channel-receiver §14 Q4.
Depends on: ADR-0013 (decision producers), ADR-0014 (`added`), ADR-0020 (`backfill_status`), ADR-0032 (`resolve` jobs), ADR-0049 (push coverage).

## Options

1. **Owned properties as direct `add` decisions, requested sources through the manual path, nothing through `discovery.hits`** (chosen): its rules are under Decision.
2. **Onboarding through `discovery.hits`** (AU-057 option 2): poster-resolver accepts `origin = client_onboarding`, carries `proposed_source_id` and `owned_by_client`, and types groups as qualifying. Consequences: the Telegram PRDs stand and two approved PRDs change; owned properties pass a resolver, which for Telegram is the amber tg-channel-resolver, so a client's own green channel would be looked up through a vendor (against ADR-0052).
3. **Every client addition through the manual path** (AU-057 option 3, AU-026 option 3), the receivers mapping chats only after `added`. Consequences: no new producer, but resolver and qualifier work for properties the client has already proved it owns, and posts that arrive before the row exists are lost unless the receiver buffers them (AU-026 option 2).

## Decision

A client's own properties enter the registry as direct `add` decisions from whoever establishes ownership, with a pre-allocated `source_id` and no resolver or qualifier; sources a client asks for take registry-writer's manual path; nothing about onboarding travels on `discovery.hits`.

- Client-owned properties (Facebook Pages, Instagram accounts, LinkedIn pages, TikTok accounts, YouTube channels, Telegram channels and their linked groups) are added by whoever establishes ownership: the client portal or admin console (D3 specifies the flow) or, for Telegram, tg-bot-channel-receiver and tg-discussion-receiver once the bot's role is verified, since a private channel's chat id is known only then (`tg-bot-channel-receiver §5.2 L69`). The `add` decision (a named producer, ADR-0013) carries `owned_by_client = true`, `added_by = client`, the client id, route `green`, the reach tier from the count the connection returns (rule 6, `CONVENTIONS L247`) and a pre-allocated `source_id`; no resolver or qualifier runs.
- registry-writer inserts with that `proposed_source_id` instead of `gen_random_uuid()`; for a property already registered, the sender uses the existing id from the start and the add sets `owned_by_client`.
- Receivers subscribe on `added` (`owned_by_client = true`) for their platform, ig-webhook-receiver included (it adds `source.events` to its reads), and turn push coverage on once the subscription is verified (ADR-0049), as fb-client-webhook-receiver and yt-pubsub-receiver already order it (`fb-client-webhook-receiver §5.1 L46`, `yt-pubsub-receiver §5.1 L44`).
- Telegram: the one-time code and the channel's pre-allocated id live in a small onboarding table owned by tg-bot-channel-receiver (for example `tg_onboarding`, under ADR-0025's naming rule), created by the portal through the receiver's endpoint; tg-discussion-receiver allocates the group's id when it verifies the group. Neither receiver writes `backfill_status`: backfill-orchestrator sets `capped` with `capped_reason = no_history` (ADR-0020). This answers `tg-bot-channel-receiver §14 Q4 L197`: yes to the id, no to `discovery.hits`.
- Third-party sources a client asks for take registry-writer's manual path as written (`§5.2 L61`): poster-resolver with `origin: manual` and the seed-list flag, then the qualifier with rules 2, 4 and 10 skipped. li-org-resolver receives them from poster-resolver like any `resolve` job (ADR-0032), not as `seed` from registry-writer.

Why: Ownership proved by an authorisation or a bot's administrator role needs no discovery, resolution or Iraqi-signal check; sending it straight to the one registry writer leaves the approved discovery path untouched and avoids the paid and amber lookups the Telegram onboarding would trigger.

## Consequences

The approved poster-resolver and qualifier stay as written; the approved registry-writer gains the `proposed_source_id` rule and the new `add` producers, and the approved li-org-resolver loses origin `seed` (both move under ADR-0001); `discovery.hits` carries no onboarding fields (ADR-0031).

- CONVENTIONS v1.1: an owned add may carry a pre-allocated `source_id` (v1 L36); receivers subscribe on `added` (v1 L21).
- tg-bot-channel-receiver owns a small onboarding table under ADR-0025's naming rule.
- `DEFERRED.md`: the portal's onboarding screens (owner D3).

Sessions that must read this: F3, then C7, C8, C9, IG4, TG1, TG2, VLI2, D3.
