# ADR-0055 · LinkedIn retention

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F3, F8, linkedin (li-post-search, li-org-resolver, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-own-comments-fetcher, li-post-comments-fetcher), retention-purger, store-writer, poster-resolver
Source: D2-Q055 (user decision; changed by the user's answer, which keeps the recommended option for LinkedIn) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS defines `linkedin_48h` ("member social-activity data purged after 48 hours; organization data as the API terms allow", L77) and quotes the terms: "member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated)" (L192). Classes follow the route (L247), so amber LinkedIn would get `vendor_agreed` (24 months by default, L79). The PRDs split:

- Amber: posts carry `vendor_agreed` (`li-post-search §6.2 L92`, `li-company-posts-poller §6.2 L114`), but member reposts are held as `linkedin_48h` until legal decides (`li-company-posts-poller §7 L133`), and vendor comments carry `linkedin_48h`, "the stricter option, until legal decides" (`li-post-comments-fetcher §6.2 L120`, `§7 L139`); each asks the question the other way round (`li-post-search §14 Q2 L164`, `li-company-posts-poller §14 Q5 L188`, `li-post-comments-fetcher §14 Q1 L192`).
- Green: one class, `linkedin_48h`, for organization posts and member fields, which retention-purger should apply "by field" (`li-client-posts-poller §7 L135`), while retention-purger purges by kind and has no field-level mode (`retention-purger §5.3 L64`, `L70`; AU-078). Whether six weeks or six months applies is open and also sets the backfill cap (`li-client-posts-poller §5.1 L50`, `§14 Q2 L188`).
- Member profile data at 24 hours (`li-post-search §7 L115`, `li-org-resolver §7 L115`, `li-company-posts-poller §7 L133`) has no class.

The user's answer, 7 Oct 2026: "Q054, Q055, and Q056 data retention should be up to 10 years." Asked again, the user chose "10 years where allowed": every item is kept 10 years on X, Meta, Telegram, news, web and vendor routes, with deletion requests honoured; YouTube, LinkedIn and TikTok items are kept as long as their terms allow, and their counts and trends are kept 10 years. For LinkedIn that is option 1, under the ten-year default of ADR-0054.

Settles: CF-105, AU-078, li-client-posts-poller §14 Q2, li-company-posts-poller §14 Q5, li-own-comments-fetcher §14 Q2, li-own-comments-fetcher §14 Q3, li-post-comments-fetcher §14 Q1, li-post-search §14 Q2.

## Options

1. **LinkedIn's terms apply whatever the route: class by content, the stricter reading for members, `linkedin_org` for organizations on green and amber** (chosen): its rules are under Decision.
2. **As option 1, but `vendor_agreed` (24 months by default, L79) for organization posts on the amber route.** _Not taken: LinkedIn's terms cap organisation posts whatever the route._ Consequences: two years of amber organization posts for trend and search; but the vendor buys data from the same platform whose terms cap organization social activity at six weeks (L192), so keeping it 24 months is the same exposure as keeping member comments past 48 hours, unless the vendor contract and counsel say LinkedIn's terms do not bind data bought from a vendor.
3. **`linkedin_48h` on every LinkedIn record, green and amber, with field-level rules in retention-purger** (organization fields six weeks, member fields 48 hours, profile fields 24 hours). _Not taken._ Consequences: one class, but retention-purger and F8 need per-field purges that no other platform needs.
4. **Class by route as CONVENTIONS says:** _Not taken: under ADR-0054, `vendor_agreed` keeps up to ten years, against LinkedIn's 48-hour rule for member content._ `vendor_agreed` on every amber record and `linkedin_48h` on every green one, after legal confirms the vendor contract. Consequences: the simplest, but member comments bought from a vendor would be kept 24 months against LinkedIn's 48-hour rule for the same data, and green organization posts would be deleted at 48 hours unless the purger works per field.

## Decision

LinkedIn's terms set limits shorter than the ten-year default of ADR-0054, so option 1 stands: LinkedIn's terms apply whatever the route; member content is `linkedin_48h`, organisation posts are `linkedin_org` (six weeks, or six months if counsel confirms), and member profile data is never stored. LinkedIn's counts and trends keep ten years as aggregates (ADR-0056); per-post LinkedIn rollups wait for counsel (ADR-0048).

The LinkedIn PRDs say the restricted uses "are carried on every LinkedIn item regardless of route", organization data included (`li-post-search §7 L115`, `li-org-resolver §7 L115`). Member-authored content (comments, member posts, reposts of member posts) is `linkedin_48h` on every route, counted from `fetched_at`. Organization-authored posts and their counts get a new class `linkedin_org` on both routes: six weeks, or six months if counsel confirms that our access counts as "authenticated". Member fields inside an organization post (a mentioned member, an administrator) are hashed or dropped by the adapter before the first write (option 2 of AU-078, consistent with ADR-0010), so no field-level purge is needed. Member profile data is never stored (CONVENTIONS L114), except a member poster's id held until poster-resolver classes it, which must happen within 24 hours or the id is dropped (L192).

Why: LinkedIn's PRDs already say its terms follow the data, not the route; option 1 applies them the same way to members and to organizations, and avoids a field-level purge by not storing member fields in organization records. Option 2 would keep more history, at a legal risk. The user's answer keeps ten years only where the rules allow, and LinkedIn's do not.

## Consequences

One class per record, which retention-purger and the ClickHouse TTLs can apply; the green backfill cap is six weeks for now; amber organization history beyond six weeks survives only as aggregates; li-post-search's member posts, an approved PRD, move under ADR-0001; class by route (CONVENTIONS L247) gains a LinkedIn exception.

- CONVENTIONS v1.1: `linkedin_org` added; the LinkedIn class reworded (v1 L77): member content and organisation content, on every route, counted from `fetched_at`; the class-by-route rule (v1 L247) gains the LinkedIn exception; the LinkedIn fact sheet (v1 L192) cross-referenced.
- F3 seeds `linkedin_org`; F8 sets its TTL; the LinkedIn adapters hash or drop member fields in organisation records before the first write.
- `DEFERRED.md`: counsel on "authenticated", six weeks or six months, which also sets the green backfill cap (owner LI1, before LinkedIn's go-live); counsel's confirmation of the LinkedIn readings before production (G4), the registry columns filled from an organisation's profile, kept while the source exists, included (ADR-0003).

Sessions that must read this: F3, F8, C4, C6, C13, C14, then LI1, LI2, LI3, VLI1, VLI2, VLI3, VLI4.
