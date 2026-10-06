# G2 · Gate: staging with real data

Wave 3 · First real data, and the Meta review build · track Gates · size M (1 to 2 days with review) · kind gate

## Builds

72-hour staging soak of news and web on real data; data-quality sample; costs; restore drill.

## Needs first (merged, with a closed review)

- N1 news-robots-checker: `docs/handoffs/N1.md`
- N2 news-site-resolver: `docs/handoffs/N2.md`
- N3 news-feed-poller: `docs/handoffs/N3.md`
- N4 news-sitemap-poller: `docs/handoffs/N4.md`
- N5 news-homepage-differ: `docs/handoffs/N5.md`
- N6 news-article-extractor (Python): `docs/handoffs/N6.md`
- N7 news-dedup: `docs/handoffs/N7.md`
- W1 web-search-perplexity: `docs/handoffs/W1.md`
- W2 web-search-mojeek: `docs/handoffs/W2.md`
- W3 search-hit-router: `docs/handoffs/W3.md`
- E2 Gate tooling for staging: `docs/handoffs/E2.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Observability and SLOs; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of N1: `docs/handoffs/N1.md`
5. Handoff of N2: `docs/handoffs/N2.md`
6. Handoff of N3: `docs/handoffs/N3.md`
7. Handoff of N4: `docs/handoffs/N4.md`
8. Handoff of N5: `docs/handoffs/N5.md`
9. Handoff of N6: `docs/handoffs/N6.md`
10. Handoff of N7: `docs/handoffs/N7.md`
11. Handoff of W1: `docs/handoffs/W1.md`
12. Handoff of W2: `docs/handoffs/W2.md`
13. Handoff of W3: `docs/handoffs/W3.md`
14. Handoff of E2: `docs/handoffs/E2.md`

## Hands on

- `docs/gates/G2.md`

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- `docs/gates/G2.md` shows every check in `build-plan/GATES.md` with evidence.
- Each failure names its failing command and the session that owns it.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Start: a fresh session on an up-to-date main: `git pull`, then `claude`
- Run: `/integration-gate G2`
