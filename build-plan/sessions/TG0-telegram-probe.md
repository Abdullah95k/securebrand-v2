# TG0 · Telegram probe

Wave 5 · Approval-gated platforms and the client portal · track Telegram · size S (one sitting) · kind probe

## Builds

Recorded Bot API updates from a test channel and its discussion group.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1; deadline before TG1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: Telegram
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. A bot from BotFather
6. A test channel and discussion group where the bot is admin

## Hands on

- `docs/handoffs/TG0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/TG0.md` from the fresh-session review
- `docs/probes/telegram.md`
- Scrubbed fixtures in `fixtures/telegram/`
- The probe script and its scrubbing test in `tools/probes/telegram/`

## Watch for

- Cap: your own test channel and its discussion group only
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (your own test channel and its discussion group only).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree TG0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform telegram your own test channel and its discussion group only`
- Review: a fresh session (`claude --worktree TG0`) checks the scrubbing test and the report against the brief; then merge
