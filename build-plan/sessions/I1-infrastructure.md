# I1 · Infrastructure (staging first)

Wave 1 · Foundation · track Infra · size L (3 to 5 days with review) · kind infra

## Builds

Hetzner servers, network and firewall, the cluster, Redpanda, ClickHouse, buckets with lifecycle rules, TLS ingress for webhooks, image registry, deploy pipeline, backups.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`

Any-time track: earliest after D2; deadline before G2.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Observability and SLOs; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D2: `docs/handoffs/D2.md`
5. CONVENTIONS deployment section
6. ADRs on the cluster and object storage
7. The list of public endpoints (Facebook, Instagram, LinkedIn and Telegram webhooks, YouTube PubSubHubbub)

## Hands on

- `docs/handoffs/I1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/I1.md` from the fresh-session review
- staging environment
- `infra/` as code (OpenTofu plus cluster manifests)
- runbook for deploy, rollback and restore

## Watch for

- Run this session in Manual permission mode and review every plan and apply
- TLS from Let's Encrypt; no dependency on Cloudflare (flagged in the vendor screen)
- The Telegram webhook endpoint must be outside Iraq (tg PRDs)

## Done when

- The definition of done in `build-plan/README.md` holds.
- Everything is in `infra/` as code; a deploy, a rollback and a restore were each rehearsed on staging.

## Runs alongside

Any session (any-time track)

## Your part

You approve every infrastructure change.

## How to run it

- Plan: `claude --worktree I1 --permission-mode plan`, then `/plan-session I1`; read the plan (Ctrl+G), approve with "Yes, manually approve edits" so you review every command and change
- Build: `/clear`, then `/build-session I1` (Manual mode); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree I1`, then `/review-session I1`
- Fix: `claude --worktree I1` (or the build terminal), `/fix-session I1`; then a fresh session runs `/review-session I1 recheck`; merge when the review has no open blocker or should-fix
