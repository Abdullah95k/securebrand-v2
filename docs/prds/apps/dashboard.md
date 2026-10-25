# dashboard

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Frontend lead (apps) · **Status:** Draft v0, 25 Oct 2026 (D3 round 1: open points marked `pending (Qn)`, answered in `docs/handoffs/D3.md`)

## 1. Why this service exists

Clients do not read pipelines; they read what people say about them, how much, how it is changing and who is saying it. Every PRD that fetches or derives data names the client app as where that shows: "new posts from the Pages I watch, never older than my tier allows" (`fb-page-feed-poller §4 L32`), reaction breakdowns and velocity (`fb-reactions-fetcher §4 L31`), unique stories "also published by N outlets" (`news-dedup §4 L33`), topic and sentiment trends (`analysis-topics §4 L37`, `analysis-sentiment §4 L39`).

The dashboard is that app. It has two builds. U1 builds the slice Meta's App Review must see: analytics on named Pages, comparing them, engagement over time and post lists, with its screencast script (`build-plan/sessions/U1-dashboard-slice-for-meta-app-review.md` L7; `build-plan/README.md`, approvals table). Reviewers want to see a working analytics product (CONVENTIONS v1.1, Facebook fact sheet L300); a raw data pipeline or a "monitoring" framing fails review (D3 brief, "Watch for"). U3 builds the full dashboard with the analysis views (`U3-full-dashboard.md` L7). Both read only through query-api.

## 2. Objective (the end state this service delivers)

End state: a client user opens one web app, in their language, and sees for their client the volume, sentiment, topics, stories, sources and public accounts of their keywords and watched sources, each figure labelled with where it came from and how fresh it is, and never anything another client or an ordinary person's identity would reveal.

Measurable targets:

- Every screen shows its data's `as_of` and route labels; 100% of item cards carry a provenance line (ADR-0003).
- First meaningful paint of the overview below 3 s on a 10 Mbit/s connection (target, measured in U3).
- The App Review screencast shows every permission Meta reviews in use, in one take of the scripted flow (`docs/approvals/meta-screencast.md`, U1's).

## 3. Scope

### In scope

- U1 (the App Review slice), section 5.2 A.
- U3 (the full dashboard), section 5.2 B; its list of views is pending (Q14).
- The alert inbox and the alert rule editor, the `alert_rules` writer ADR-0025 gives D3 (pending (Q15)).
- Saved lists of public accounts and segments (ADR-0010, ADR-0043), named lists pending (Q12).
- Disclosures the PRDs require on screen (section 5.3 C).

### Out of scope

- Keywords, sources, connections, requests, deletion requests and the provenance statement page: the client portal (`client-portal.md`). The two share one shell and sign-in (pending (Q3)).
- Ops screens: the admin console.
- A browsable LinkedIn feed (`li-client-posts-poller §7 L134`), and any view of an ordinary person's identity (ADR-0010).

## 4. Users and consumers

- Client communications, marketing and customer-service teams; government clients' communication offices, under the limits of 5.3 B (pending (Q7)).
- Account managers, inside a client's scope (pending (Q5)).
- Meta's App Review reviewers, through a reviewer account on the demo client (pending (Q13)); later LinkedIn's and TikTok's reviewers see the own-account views (`build-plan/README.md`, approvals table; U2 records those flows).

## 5. How it works

### 5.1 Trigger and rotation

Interactive web app; no schedule. Views refresh when opened and every 60 s while open on the overview and the alert inbox (the aggregator's open-hour cycle, `aggregator §5.1 L37`).

### 5.2 Step by step

**A. The App Review slice (U1).** One client workspace, its own Pages connected through Facebook Login for Business and named third-party Pages watched (pending (Q13)):

1. Pages overview: each watched Page's posts, reactions by type, comments and shares in the chosen period, side by side; source views of query-api (pending (Q6)).
2. Engagement over time: per Page, a series of reactions, comments and shares from the observations at first sight, +24 h and +7 d (`fb-reactions-fetcher §4 L31`; ADR-0034); two points per post are drawn as points, not a curve (`tt-video-stats-refresher §12 L154` states the rule for TikTok; the same holds here).
3. Post list: a Page's posts with text, time, reactions by type, comment count, the comment sentiment share where comments are scored, and a link to the post on Facebook; never a commenter's identity (the PPCA fact sheet: no `from` under PPCA).
4. For Instagram, the client's own business account: media with counts and comment volume; and hashtags as aggregated, de-identified volume, sentiment and topics (`ig-hashtag-search §4 L35`, `§12 L167`).
5. Wording: "Page analytics", "engagement", "comparison"; never "monitoring", "surveillance" or "tracking people". Views and reach of third-party Pages are not shown, since PPCA does not give them (`fb-reactions-fetcher §5.4 L92`).

**B. The full dashboard (U3).** Proposed views, pending (Q14):

1. Overview: mentions, reach, engagement and stories over time per keyword; negative share; the top topics; open alerts.
2. Mentions: the mention list with filters (keyword, platform, route, kind, language, dialect, sentiment, topic, segment), text search, and the item panel (provenance, analysis, metrics, story, matched term with its offsets highlighted, `keyword-matcher §4 L34`).
3. Sentiment and topics: shares with `mixed` shown as its own share and in the denominator (ADR-0048), topic volumes and topic by sentiment, intent labels (`analysis-topics §3 L26`).
4. Stories: unique stories with "also published by N outlets" and the origin named "earliest seen" (`news-dedup §4 L33`, `§12 L146`).
5. Sources: the client's watched sources with engagement and post lists (pending (Q6)), tier, freshness and health.
6. Public accounts: list, filter and rank by mentions, reach or engagement; save to a list; use the list as a segment (ADR-0010).
7. Entities, brands and media tags: from the entity rollup, governorates included (ADR-0048), once A3 and A4 run.
8. Own accounts: TikTok Display videos with their first-sight, +24 h and +7 d counts beside watched competitors, labelled green (`tt-client-videos-fetcher §4 L33`); LinkedIn client pages as analysis and aggregates, comment text in-app only for its 48 hours (`li-own-comments-fetcher §4 L30`).
9. Alerts: the inbox (open and resolved alerts; alert-evaluator prunes resolved alerts after 7 days, `alert-evaluator §6.3 L105`, so how far back the inbox reaches is pending (Q16)) and the rule editor (5.3 D).

### 5.3 The call it makes (the processing it performs)

**A. Data access.** Every figure comes from query-api's endpoints (`query-api.md` 5.3 D); the dashboard holds no credentials to ClickHouse or Postgres and computes no share itself, apart from formatting.

**B. Government workspaces.** A workspace whose client has `client_type = government` shows no amber data and no X data unless the X gate opens (CONVENTIONS v1.1 L251, L252); query-api enforces both. What else is hidden (source level, item lists, public-account rankings) is pending (Q7).

**C. Disclosures on screen.** Each from the PRD named:

- Amber items: the label "amber, <vendor>", the one form for every amber route (`li-org-resolver §4 L38`, `li-post-search §4 L38`); green items "green".
- Vendor search is a sample, not a census (`fb-keyword-search §12 L160`); Instagram vendor comments are the first ~15 visible, shown with `comments_count` (`ig-comments-fetcher §12 L157`).
- Facebook `/feed` is ranked (about 600 posts per Page per year) and a `capped` history is incomplete (`fb-backfill §7 L122`); Tier 1 freshness is "within 1 hour of Meta surfacing it" (`fb-page-feed-poller §12 L171`).
- Freshness relaxed by budget stretch (`quota-governor §12 L150`, `tg-channel-posts-poller §5.1 L52`), and web coverage paused for budget (`web-search-mojeek §7 L120`).
- Sentiment model switch dates as possible trend breaks, Sorani as lower confidence, the model version (`analysis-sentiment §5.3 L76`, `§12 L150`); `zero_shot` topics marked (`analysis-topics §12 L157`); topic rows add up to more than the total (`aggregator §12 L134`); reach is gross followers as of the rebuild (ADR-0048).
- YouTube comment text expired after 30 days (`yt-text-purger §4 L35`); hidden counts shown as "hidden", never 0 (`yt-video-details-fetcher §5.4 L78`).
- Telegram bot channels' history starts from the bot's join (`tg-bot-channel-receiver §5.1 L50`).
- No view decides "Iraqi" from `dialect` (`lang-dialect-id §13 L175`).

**D. The alert rule editor.** Writes `alert_rules` (`rule_id`, `client_id`, `type`, `keyword_id`, `scope`, `platform`, `params`, `severity`, `channels`, `cooldown_minutes`, `enabled`; `alert-evaluator §5.3 A L56`) through the client portal's server, audited with a ULID `request_id` (F2 handoff, O-12). Its checks, shared with alert-evaluator through `listening-sdk` (`alert-evaluator §3 L27`):

- the nine types of ADR-0048; for a government client only `volume_spike`, `negative_share` and `keyword_first_seen`, on `reputation` or `service_quality` keywords, `scope = keyword` (`alert-evaluator §5.3 C L65`; ADR-0048);
- at least one non-Telegram channel on every rule (`alert-evaluator §5.3 E L69`);
- a backtest before enabling (`alert-evaluator §5.1 L42`, `§12 L142`);
- a rule disabled for bad parameters is shown as such (`alert-evaluator §8 L118`);
- who may edit, and who approves the pilot defaults, pending (Q15).

### 5.4 What it gets

query-api's JSON. No raw text beyond what query-api returns, no author identity except public accounts, no cached news full text.

## 6. Inputs and outputs

### 6.1 Reads

query-api only (sections 5.3 A, `query-api.md` 6.1).

### 6.2 Writes

`alert_rules` and `client_lists` saved entries, through the client portal's server (`client-portal.md` 6.2), each write audited with its `request_id`. Nothing else.

### 6.3 State

Per-user view preferences (filters, chosen language, time range) in the browser; no shared state.

## 7. Limits, quotas and cost

No external API; no `budget_tag`. Page sizes and time windows follow query-api's limits (`query-api.md` 7).

## 8. Failure handling and fallback

- query-api returns 503: the view shows the last loaded figures greyed with "not current", never a blank as zero.
- `stale = true`: a banner "figures as of <as_of>".
- A source in `blocked` or `fallback`: its card shows the state and, for a client-owned property, the reconnect link of the missing-grant flow (ADR-0021; `client-portal.md` 5.2 C).

## 9. Non-functional requirements

- Languages and direction: pending (Q4); dates shown in Asia/Baghdad (UTC+3) with UTC stored.
- Accessibility: WCAG 2.1 AA contrast and keyboard use on every view (target, checked in U3).
- Security: Supabase Auth session; no token in local storage beyond the session; content-security policy without third-party scripts.
- Isolation: the two-client browser test of the briefs' "Done when".

## 10. Metrics and alerts

Front-end: `view_load_seconds{view}`, `api_errors_total{endpoint}` (reported to the app's server); alert `dashboard_error_rate_high` (above 2% of view loads for 15 minutes). Product: weekly active users per client, read by account managers.

## 11. Dependencies

query-api (Q1); the client portal's shell and sign-in (U2, for U3); FB2 (U1's "Needs first"); A1 and A2 for the analysis views (U3's "Needs first"); A3, A4 for entity and media views; alert-evaluator (A5) for alerts.

## 12. Risks and mitigations

- App Review rejection for a "monitoring" framing: the scripted wording of 5.2 A and a review of the screencast against it before submission.
- Overstating vendor coverage: the disclosures of 5.3 C on every affected figure.
- Clients reading topic rows as a total: the note of 5.3 C and totals from the topic-free query.

## 13. Acceptance criteria

1. A user of client A never sees a figure, item, source or account of client B (two-client browser test).
2. The App Review slice shows, for at least two named Pages, a side-by-side comparison, engagement over time from the +24 h and +7 d observations, and a post list with reactions by type; no screen uses the words "monitor", "monitoring" or "surveillance".
3. No view shows a commenter's or ordinary poster's name, handle, avatar or profile link.
4. Every item card shows route, vendor (or "green"), service and fetch time.
5. Every amber item shows "amber, <vendor>"; a government workspace shows no amber item.
6. A sentiment share chart counts `mixed` in the denominator and shows it as its own share.
7. A LinkedIn member comment's text is visible in the item panel and absent from every export and alert.
8. The rule editor refuses, for a government client, `new_high_reach_poster`, `post_deleted_high_reach` and the four types ADR-0048 added, and any rule whose only channel is Telegram.
9. A stale aggregate shows its `as_of` banner; a 503 never renders as zero.

## 14. Open questions

Pending the user's answers in `docs/handoffs/D3.md`: Q3, Q4, Q5, Q6, Q7, Q12, Q13, Q14, Q15, Q16.
