# ADR-0027 · Hosting: cluster and object storage

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: I1, I2, E2, C2, raw-archiver, retention-purger, deletion-propagator, all (the cluster)
Source: D2-Q027 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS already names Hetzner servers and "Backblaze B2 or Hetzner Object Storage" (CONVENTIONS L3) and leaves the orchestrator open: "Kubernetes or Nomad; the PRDs say 'the cluster'" (CONVENTIONS L12). The build plan proposes k3s (a lightweight, standard distribution of Kubernetes, the common system for running containers on a group of servers) on Hetzner "unless your team already runs Nomad" (HashiCorp's simpler alternative to Kubernetes) (FC-06) and Hetzner Object Storage as primary with Backblaze B2 as the off-site copy of the raw archive (FC-07). Both vendors are on CONVENTIONS' cleared list (L6). Constraints from the briefs: TLS from Let's Encrypt with no Cloudflare dependency, and the Telegram webhook endpoint outside Iraq (I1 brief, "Watch for"; CONVENTIONS L200). The raw archive is the platform's replay source (raw-archiver), so losing it loses the ability to reprocess; that is the reason for an off-site copy.

Settles: FC-06, FC-07.

## Options

1. **k3s on Hetzner, Hetzner Object Storage primary, Backblaze B2 off-site copy of `raw/`** (chosen): its rules are under Decision.
2. **Nomad on Hetzner instead of k3s, same storage.** Consequences: worth it only if the team already runs Nomad, as the build plan says; fewer ready-made operators for Redpanda and ClickHouse, so I1 writes more of its own job specifications.
3. **Hetzner Object Storage only, no off-site copy.** Consequences: lower cost and one account fewer; a provider-level loss would lose the raw archive and with it every replay and reprocessing.
4. **Another provider (named by the user).** Consequences: it goes through the vendor screen (CONVENTIONS L6) and `docs/dependencies.md` first; I1's brief, which is written for Hetzner, changes.

## Decision

The cluster is k3s on Hetzner. Hetzner Object Storage is the primary object store, and Backblaze B2 holds the off-site copy of the raw archive (`raw/`). The B2 copy holds identifiable raw data, so it is a second archive, not a backup: every lifecycle rule and deletion rewrite applied to the primary is applied to it too. The user opens the Hetzner and Backblaze accounts when I1 starts.

Why: It matches CONVENTIONS and the build plan, uses only cleared vendors, keeps the hosting outside Iraq and protects the one store that cannot be rebuilt.

## Consequences

One vendor for compute and primary storage in the EU, outside Iraq; k3s is standard Kubernetes, so ready-made install packages (Helm charts) and operators (programs that install and run a database such as Redpanda or ClickHouse on the cluster) and ordinary Kubernetes skills apply; the B2 copy covers the loss of a Hetzner region or account. The B2 copy holds identifiable raw data, so it is a second archive, not a backup: every lifecycle rule and deletion rewrite that retention-purger and deletion-propagator apply to the primary (`raw-archiver §4 L37`, `§5.3 L73`) is applied to it too, and the lifecycle feature, which differs between B2 and Hetzner, is tested on both (`raw-archiver §12 L163`); backups in the sense of ADR-0069 (d) are the databases' snapshots; I1 prices both before staging, and the user opens the Hetzner and Backblaze accounts.

- CONVENTIONS v1.1: "the cluster" is k3s on Hetzner (v1 L12); Hetzner Object Storage is primary and Backblaze B2 the off-site copy of `raw/` (v1 L3 and L31).
- With ADR-0054's ten-year classes, the raw archive and its B2 copy hold up to ten years of raw data where a class allows it; I1 sizes and prices both stores for that before staging.
- User action: open the Hetzner and Backblaze accounts when I1 starts (`docs/handoffs/D2.md`).

Sessions that must read this: I1 (it cannot start without this), then C2, I2, E2 and the gates G2 to G4.
