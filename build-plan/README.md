# Build plan

The full plan, with the build map and every wave table, is the "Listening platform build plan" document (https://claude.ai/code/artifact/c402eca9-d2ca-43d6-a8ce-cb6fb81fd17d). This file is the part the sessions need inside the repository.

## The six working rules

1. **Decide and freeze the contracts first.** Topics, jobs, tables, keys and budget tags are defined once in `packages/contracts` and the migrations. Services never edit them; a change goes through a proposal, your decision and a contract-change session.
2. **One service per session, from its PRD,** in its own worktree and branch.
3. **Tests come from PRD section 13 first,** as amended by the ADRs that apply (ADR-0001), and no test calls a live platform.
4. **A fresh session reviews.** The session that wrote the code never approves it.
5. **Handoffs carry the knowledge.** The next session gets the handoff notes of its "Needs first", not transcripts.
6. **Probe before you build an adapter.** Real calls happen only in probe sessions, under a cap, and become scrubbed fixtures.

## The session loop

| Step | Start | Run |
|---|---|---|
| Plan | `claude --worktree <ID> --permission-mode plan` | `/plan-session <ID>`, read the plan (Ctrl+G), approve |
| Build | `/clear` in the same worktree | `/build-session <ID>` |
| Review | a new terminal: `claude --worktree <ID>` | `/review-session <ID>` |
| Fix | the build session, or a fresh one (F2, F3 and F8 with `ALLOW_CONTRACT_EDITS=1`) | `/fix-session <ID>`, then in a fresh session `/review-session <ID> recheck` |
| Merge | when the review has no open blocker or should-fix, and everything in "Needs first" has merged | |

Other kinds: `/probe-platform <platform> <cap>` in Manual mode (`--permission-mode default`), `/integration-gate <G>` on an up-to-date main, `/decide-session <D1|D2|D3>` (not in plan mode: it writes documents), and `/contract-change <proposal>` in a session started with `ALLOW_CONTRACT_EDITS=1`. F2, F3 and F8 also start with `ALLOW_CONTRACT_EDITS=1`, because they create the contract paths.

Typing `/build-session` or `/fix-session` arms the stop gate for that session: Claude cannot finish while the checks for the changed packages fail (three rounds at most), unless it has filed a proposal or an issue. Other sessions are never gated.

To keep a long build going until it is really done:

```text
/goal every test in services/<name> passes, make check exits 0, docs/handoffs/<ID>.md exists and nothing under packages/contracts or the migrations changed, or stop after 40 turns
```

## Definition of done

1. Every acceptance criterion in PRD section 13, as amended by the ADRs that apply (ADR-0001), maps to a named test that passes; the map is in the plan, the evidence in the review.
2. The behaviours in PRD sections 5 and 8, as amended by the ADRs (ADR-0001), that no criterion covers have tests: rotation or series timing, catch-up, 429, 401 and 403, empty 200, a 5xx in the middle of pagination, DLQ after five attempts, replay idempotency.
3. `make check` passes, and no test touches the network.
4. Contracts are untouched, or changed only through an applied proposal.
5. Every output validates against its contract, and every data output carries provenance and `retention_class` (ADR-0003).
6. The metrics and alerts named in PRD section 10, as amended by the ADRs (ADR-0001), exist under those names.
7. No secret, token or private person's name appears in code, logs or fixtures, and a test proves the log scrubber works.
8. Every new runtime dependency has its line in `docs/dependencies.md`.
9. Each PRD section 14 question the build touched is answered in an ADR or listed in `docs/decisions/DEFERRED.md` with its owning session.
10. The handoff is written, the review is closed, and the pull request merges after its "Needs first".

## Foundation choices (decided in D2)

| Decision | Proposed default | Blocks |
|---|---|---|
| The nine decisions proposed in `docs/prds/README.md` | Accept as written unless D1 finds a conflict | F2, F3 |
| One writer per topic and per column | Every registry change goes through `registry.decisions` to registry-writer | F2, F3 |
| `item_id` derivation and canonical idempotency keys | A deterministic hash of the idempotency key, with golden vectors in both languages | F2 |
| Schema versioning | Additive changes within a version; a breaking change is a new version with a dual-publish window | F2 |
| Kafka clients | `@confluentinc/kafka-javascript` for Node and `confluent-kafka` for Python, both on librdkafka | F4, F6 |
| Cluster | k3s on Hetzner, unless your team already runs Nomad | I1 |
| Object storage | Hetzner Object Storage as primary, Backblaze B2 as the off-site copy of the raw archive | C2, I1 |
| Language of lang-dialect-id | Python (CAMeL Tools and KLPT), with a TypeScript copy of the fold for fallback | C3, F7 |
| ClickHouse topology | One node with backups in staging; a replicated pair before production | F8, I1 |
| Tooling | pnpm and Turborepo, TypeScript strict, Vitest; uv, ruff, pytest; Zod 4 to JSON Schema to Pydantic | F1, F2 |
| Local stack | docker compose with Redpanda, Supabase CLI, ClickHouse and SeaweedFS as local S3 | F1 |
| Environments | Local (fake platform only), staging (real APIs on small budgets), production | I1 |
| Dependency policy | A line in `docs/dependencies.md` per runtime dependency, checked against the vendor screen | F1 onward |

Decided later by their owning sessions: GPU pool or model API (A1 to A4), fold details beyond the PRD table (F7), series and threshold tuning after real data (after G2).

## Approvals and what they need

| Approval | Lead time (as published) | What it needs | Unblocks |
|---|---|---|---|
| Meta Business Verification | "a few days", depending on documents | Incorporation certificate; utility bill or bank statement with the same legal name and address | Access Verification, App Review |
| Meta Access Verification (Tech Provider) | about 5 days after Business Verification | How you use other businesses' data for them | Per-client system-user tokens |
| Meta App Review (PPCA, Instagram Public Content Access, Advanced Access, Webhooks) | "up to several weeks"; six weeks or more reported for PPCA | A working analytics UI on named Pages and its screencast (U1); privacy policy and data deletion URLs. Until approval, features work only for people with a role on the app | Facebook and Instagram in production |
| LinkedIn Community Management API, Development tier | not published | Approved use case, verified business email, organization, website, Page super-admin verification | LI0 and the LinkedIn sessions |
| LinkedIn Standard tier | not published | Completed Development integration, privacy policy, storage compliance, narrated recording of the full OAuth flow and each use case (U2) | LinkedIn in production |
| X developer app, pay-per-use | same day | console.x.com account, credits, use case; Enterprise before any government end user | X sessions |
| YouTube Data API key | same day | Google Cloud project; the Audit and Quota Extension form once yt-text-purger is live and use nears 10,000 units a day | YouTube sessions |
| Telegram bot | minutes | BotFather; a test channel and its discussion group | TG sessions |
| TikTok Display API app | sandbox now, review later | Website with privacy policy and terms; demo video showing every scope (U2) | TT1 in production |

## Files

- `SESSIONS.md`: every session, its dependencies and a checkbox
- `GATES.md`: what each gate checks
- `sessions/<ID>-<name>.md`: one brief per session
- `templates/`: plan, handoff, review, probe report, proposal, ADR, issue
- `tools/`: `sessions.py` (the single source for the briefs and the plan's tables), `gen_briefs.py`, `gen_doc.py`. After changing `sessions.py`, run `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` from the repository root.
