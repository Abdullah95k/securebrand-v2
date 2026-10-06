---
name: probe-platform
description: Record real responses from one platform's official API or one vendor under a call budget, scrub them into fixtures, and check every PRD assumption. Run before that platform's first service session.
argument-hint: <platform> [call or spend cap]
disable-model-invocation: true
effort: max
---

# Probe $0

No service code in this session. Credentials come from `.env` at run time: you cannot read `.env`, and you must never print, log or commit a token. Run this session in Manual mode (`--permission-mode default`) so I approve every real call.

Arguments given: $ARGUMENTS. The first word is the platform; anything after it is the call or spend cap. If no cap was given, use the cap in the brief.

| Argument | Brief | PRDs to read | Fixtures go to |
|---|---|---|---|
| news | N0 | `docs/prds/news/` | `fixtures/news/` |
| web | W0 | `docs/prds/web/` | `fixtures/web/` |
| meta | FB0 | green PRDs in `docs/prds/facebook/` and `docs/prds/instagram/` | `fixtures/facebook/`, `fixtures/instagram/` |
| youtube | YT0 | `docs/prds/youtube/` | `fixtures/youtube/` |
| x | X0 | `docs/prds/x/` | `fixtures/x/` |
| linkedin | LI0 | green PRDs in `docs/prds/linkedin/` | `fixtures/linkedin/` |
| telegram | TG0 | green PRDs in `docs/prds/telegram/` | `fixtures/telegram/` |
| tiktok | TT0 | `docs/prds/tiktok/tt-client-videos-fetcher.md` | `fixtures/tiktok/` |
| fb-vendor, ig-vendor, tt-vendor, li-vendor, tg-vendor | VFB0, VIG0, VTT0, VLI0, VTG0 | that platform's amber PRDs | `fixtures/<platform>-vendor/` |

1. Read the brief for $0 in `build-plan/sessions/`, then sections 5.3 and 7 of each PRD in the table. List every call shape those PRDs use: endpoint or vendor call, parameters, fields requested, pagination, page size.
2. Write the probe under `tools/probes/$0/`. It reads credentials from the environment, makes the fewest real calls that record one response per call shape (including one full pagination sequence, one empty result, and one error if it can be triggered safely), and stops at the cap.
3. Show me the call list and the expected cost, and wait for my yes before running anything.
4. Run it. Save raw responses only under the fixture directory's `raw/` folder, which is gitignored. Write scrubbed copies beside it: tokens and signed URLs removed; names, handles, ids and avatars of private individuals replaced with stable fakes (the same person gets the same fake everywhere); ids of public Pages, channels, outlets and companies kept. Add a `README.md` to the fixture directory saying, for each file, the call, the date and what was scrubbed.
5. Add a test under `tools/probes/$0/` that fails if any scrubbed fixture contains a token pattern or any original private name from the raw files. Run it, then delete the `raw/` folder.
6. Write `docs/probes/$0.md` from `build-plan/templates/PROBE-REPORT.md`: every PRD assumption about fields, limits, pagination, rate limits and costs marked confirmed, different or not tested, with evidence. Each difference becomes a question for the PRD, listed at the end.
7. Report the actual spend against the cap.
