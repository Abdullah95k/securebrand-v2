# Orchestrated build

The build plan in `build-plan/` is run by one orchestrator Claude Code session in the cloud, which launches a separate cloud session for every step of every session ID. This file says how that maps onto the kit, so a human or a worker session can see who does what.

## Rules the user set

- One worker session works on one session ID only (one service, package, gate or decision), never two.
- Every worker runs on the most capable model available (Claude Fable 5.1) at maximum effort. The kit's skills declare `effort: max`.
- The orchestrator approves build plans, after checking each one against its brief, PRD, ADRs and handoffs. Questions the documents do not settle go to the user through the orchestrator, in batches.
- The orchestrator merges foundation, core, service, app and gate lanes once their gates are met. The user reads and merges the decision lanes (D1, D2, D3) and every contract-change pull request.

## Lanes

Each session ID is a lane with one branch, `sb/<ID>` (for example `sb/F1`, `sb/C11`), and one pull request into `main`, which the orchestrator opens and owns. Worker sessions push only to their lane's branch and never open, merge or close pull requests.

| Kind | Steps, each a fresh worker session unless noted |
|---|---|
| Foundation, core, service, app | plan (`/plan-session`), build (`/build-session`), review (`/review-session`), fix (`/fix-session`, sent to the build session), recheck (`/review-session <ID> recheck`), merge |
| Decision and spec (D1, D2, D3) | decide (`/decide-session`), review by a fresh session, user reads and merges |
| Probe | probe (`/probe-platform`; the orchestrator relays the call list and cost to the user and waits for a yes), review, merge |
| Gate | gate (`/integration-gate`) on an up-to-date `main`; the report lands through its lane |
| Contract change | `/contract-change <proposal>` on branch `sb/CC-<proposal>`, then the user merges |

A step starts only when the brief's "Needs first" have merged into `main` with a closed review, as `build-plan/SESSIONS.md` says.

## How a worker talks to the orchestrator

Workers get the protocol in their system prompt. Nobody watches a worker session, so it never calls AskUserQuestion. Wherever the kit says to ask the user, wait for approval or name the next terminal, the worker pushes its work and ends its turn with one of these first lines:

- `ORCHESTRATOR: NEEDS-INPUT`, then numbered questions, each with options and a recommendation
- `ORCHESTRATOR: DONE`, then what it produced, the pushed commit and the checks it ran
- `ORCHESTRATOR: BLOCKED`, then the reason, after filing `docs/issues/` or `docs/proposals/` as the kit asks

The orchestrator answers in that session, from the documents where they settle the question, and from the user where they do not. Answers are recorded where the kit says: the plan, the handoff or an ADR.

## Cloud adaptations to the kit

- `claude --worktree`, plan mode and `/clear` are replaced by fresh cloud sessions per step on the lane's branch.
- `ALLOW_CONTRACT_EDITS=1` cannot be set when a cloud session starts, so `.claude/hooks/guard-contracts.sh` also allows contract edits on the branches `sb/F2`, `sb/F3`, `sb/F8` and `sb/CC-<proposal>`. CI remains the hard backstop.
- The Docker daemon is not running when a cloud container starts. Workers start it with `sudo -n dockerd` before `make up`.
- Cloud containers hold no platform credentials. Probe sessions, staging and infrastructure work need the user to add credentials to the cloud environment first.

## What only the user can supply

| Needed for | What |
|---|---|
| D2, D3 | Your decisions, asked through the orchestrator |
| F7, C3 | A reader of Iraqi Arabic and Sorani to check the fold golden file and 50 dialect outputs |
| A0 | Annotators who read Iraqi Arabic, Sorani and Badini |
| N0 | The list of Iraqi news websites |
| Probes (N0, W0, FB0, YT0, X0, LI0, TG0, TT0 and the vendor probes) | API keys and accounts, added as secrets to the cloud environment, and a yes for each probe's call list and cost |
| I1, I2, E2, G2 to G4 | Infrastructure accounts (the D2 choice, Hetzner by default) and approval of every infrastructure change |
| U1, U2, TT1, LI1 | The platform reviews in `build-plan/README.md` (Meta App Review, LinkedIn tiers, TikTok review): screencasts and submissions |
