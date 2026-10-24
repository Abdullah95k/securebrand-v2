# ADR-0063 · X stream rule allocation

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: x-filtered-stream, x-recent-search
Source: D2-Q063 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The filtered stream holds up to 1,000 rules (`CONVENTIONS L87`). x-filtered-stream fills them in order: "client brand keyword sets (one rule each, priority 1), tier-1 accounts (priority 1), tier-2 (2), tier-3 (3)" (`x-filtered-stream §5.1 L40`, `§13 L191`); x-recent-search says "Tier-1 keyword rules also run as stream rules on x-filtered-stream; the 15-minute search stays on as the safety net" (`x-recent-search §5.1 L47`), without saying whether other keyword rules are streamed. How many rules keyword coverage takes decides how many accounts get real-time coverage, and how cost splits between stream and search (both are paid per post read).

Settles: CF-115, x-filtered-stream §14 Q4.

## Options

1. **Streamed rules chosen by priority within a fixed share** (chosen): its rules are under Decision.
2. **Every client brand keyword set on the stream**, as x-filtered-stream says. Consequences: accounts get only the rules keywords leave over; x-recent-search's cost split is rewritten.
3. **Only tier-1 keyword rules on the stream**, the narrow reading of x-recent-search. Consequences: lower stream volume; brand sets below tier 1 rely on 60-minute search.

## Decision

Tier-1 keyword rules go on the filtered stream first, up to a configured share of the capacity left after the headroom reserve; tier-1 accounts fill the rest, then tiers 2 and 3; x-recent-search keeps searching every keyword rule.

Tier-1 keyword rules come first, up to a configured share of the capacity left after the headroom reserve (`x-filtered-stream §5.1 L40`), set in the pilot; tier-1 accounts fill the rest, then tier 2 and 3; x-recent-search keeps searching every keyword rule, the tier-1 ones every 15 minutes as the safety net. Both PRDs state the same order and the share (x-recent-search, an approved PRD, moves under ADR-0001).

Why: It honours both PRDs' order and puts the trade-off in one number that can change without a contract change.

## Consequences

Keyword coverage can never crowd out tier-1 accounts; the share is a setting the pilot tunes; client brand keyword sets below tier 1 are not streamed and rely on 60-minute search.

- No CONVENTIONS change beyond a note under the X fact sheet.
- `DEFERRED.md`: the keyword share of the stream's capacity, a setting the pilot tunes (owner X4).

Sessions that must read this: X1, X4.
