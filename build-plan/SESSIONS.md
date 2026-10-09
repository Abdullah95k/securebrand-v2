# All sessions

Tick a session when its pull request has merged with a closed review. "Needs first" is the hard rule; waves are the recommended order.

## Wave 0 · Decide and freeze

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **D1** | Contract inventory | nothing | M | [brief](sessions/D1-contract-inventory.md) |
| [ ] | **D2** | Decisions and contract freeze | D1 | M | [brief](sessions/D2-decisions-and-contract-freeze.md) |
| [ ] | **D3** | Specs for the parts with no PRD | D2 | M | [brief](sessions/D3-specs-for-the-parts-with-no-prd.md) |

## Wave 1 · Foundation

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **F1** | Repository, toolchain, local stack, CI, Claude kit | nothing | M | [brief](sessions/F1-repository-toolchain-local-stack-ci-claude-kit.md) |
| [ ] | **F2** | Contracts package | D2, F1 | L | [brief](sessions/F2-contracts-package.md) |
| [ ] | **F3** | Control-plane schema | D2, F1 | L | [brief](sessions/F3-control-plane-schema.md) |
| [ ] | **F4** | SDK runtime (Node) | F2, F3 | L | [brief](sessions/F4-sdk-runtime.md) |
| [ ] | **F5** | SDK scheduling, quota client, adapter kit, fake platform | F4 | L | [brief](sessions/F5-sdk-scheduling-quota-client-adapter-kit-fake-pla.md) |
| [ ] | **F6** | Python SDK twin | F2, F4 | M | [brief](sessions/F6-python-sdk-twin.md) |
| [ ] | **F7** | Text fold and golden corpus | D2, F1 | M | [brief](sessions/F7-text-fold-and-golden-corpus.md) |
| [ ] | **F8** | ClickHouse schema | D2, F2 | M | [brief](sessions/F8-clickhouse-schema.md) |
| [ ] | **I1** | Infrastructure (staging first) | D2 | L | [brief](sessions/I1-infrastructure.md) |
| [ ] | **I2** | Observability | I1, F4 | M | [brief](sessions/I2-observability.md) |
| [ ] | **G0** | Gate: foundation | F1, F2, F3, F4, F5, F6, F7, F8 | S | [brief](sessions/G0-gate-foundation.md) |

## Wave 2 · Shared core

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **C0** | Reference vertical on the fake platform | F5, G0 | M | [brief](sessions/C0-reference-vertical-on-the-fake-platform.md) |
| [ ] | **C1** | `quota-governor` | F5, G0 | M | [brief](sessions/C1-quota-governor.md) |
| [ ] | **C2** | `raw-archiver` | F4, G0 | M | [brief](sessions/C2-raw-archiver.md) |
| [ ] | **C3** | `lang-dialect-id` | F6, F7, G0 | M | [brief](sessions/C3-lang-dialect-id.md) |
| [ ] | **C7** | `registry-writer` | F4, F3, G0 | M | [brief](sessions/C7-registry-writer.md) |
| [ ] | **C4** | `normalize-item` | F4, F7, C2 | L | [brief](sessions/C4-normalize-item.md) |
| [ ] | **C5** | `keyword-matcher` | F4, F7, F8, G0 | M | [brief](sessions/C5-keyword-matcher.md) |
| [ ] | **C6** | `store-writer` | F4, F8, G0 | M | [brief](sessions/C6-store-writer.md) |
| [ ] | **C8** | `poster-resolver` | F5, C0 | M | [brief](sessions/C8-poster-resolver.md) |
| [ ] | **C9** | `qualifier` | F4, F3, C1, G0 | M | [brief](sessions/C9-qualifier.md) |
| [ ] | **C10** | `backfill-orchestrator` | F5, C7, C1 | M | [brief](sessions/C10-backfill-orchestrator.md) |
| [ ] | **C11** | `comment-decay-scheduler` | F5, F3, C1, G0 | L | [brief](sessions/C11-comment-decay-scheduler.md) |
| [ ] | **C12** | `source-health-canary` | F5, C7 | M | [brief](sessions/C12-source-health-canary.md) |
| [ ] | **C13** | `deletion-propagator` | F8, C2, C6 | M | [brief](sessions/C13-deletion-propagator.md) |
| [ ] | **C14** | `retention-purger` | C13 | M | [brief](sessions/C14-retention-purger.md) |
| [ ] | **C15** | `aggregator` | C6, F8 | M | [brief](sessions/C15-aggregator.md) |
| [ ] | **E1** | End-to-end suite for G1 | C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15 | L | [brief](sessions/E1-end-to-end-suite-for-g1.md) |
| [ ] | **G1** | Gate: fake platform end to end | E1 | M | [brief](sessions/G1-gate-fake-platform-end-to-end.md) |

## Wave 3 · First real data, and the Meta review build

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **N0** | News probe and seed list | F1 | M | [brief](sessions/N0-news-probe-and-seed-list.md) |
| [ ] | **N1** | `news-robots-checker` | F5, N0, G1 | M | [brief](sessions/N1-news-robots-checker.md) |
| [ ] | **N2** | `news-site-resolver` | N1, C8, C9, C3 | M | [brief](sessions/N2-news-site-resolver.md) |
| [ ] | **N3** | `news-feed-poller` | N1, N2 | M | [brief](sessions/N3-news-feed-poller.md) |
| [ ] | **N4** | `news-sitemap-poller` | N1, N2 | M | [brief](sessions/N4-news-sitemap-poller.md) |
| [ ] | **N5** | `news-homepage-differ` | N1, N2 | M | [brief](sessions/N5-news-homepage-differ.md) |
| [ ] | **N6** | `news-article-extractor` | F6, N1, N0 | L | [brief](sessions/N6-news-article-extractor.md) |
| [ ] | **N7** | `news-dedup` | N6, C4 | M | [brief](sessions/N7-news-dedup.md) |
| [ ] | **N8** | `news-comments-fetcher` | N6, C11 | M | [brief](sessions/N8-news-comments-fetcher.md) |
| [ ] | **W0** | Web search probe | F1 | S | [brief](sessions/W0-web-search-probe.md) |
| [ ] | **W1** | `web-search-perplexity` | F5, C1, W0, G1 | M | [brief](sessions/W1-web-search-perplexity.md) |
| [ ] | **W2** | `web-search-mojeek` | F5, C1, W0, G1 | M | [brief](sessions/W2-web-search-mojeek.md) |
| [ ] | **W3** | `search-hit-router` | W1, C8, N2 | M | [brief](sessions/W3-search-hit-router.md) |
| [ ] | **W4** | `web-gdelt-poller` | W3 | S | [brief](sessions/W4-web-gdelt-poller.md) |
| [ ] | **W5** | `web-commoncrawl-scanner` | W3, N2 | M | [brief](sessions/W5-web-commoncrawl-scanner.md) |
| [ ] | **FB0** | Meta probe (development mode) | F1 | M | [brief](sessions/FB0-meta-probe.md) |
| [ ] | **FB1** | `fb-page-resolver` | FB0, C8, G1 | M | [brief](sessions/FB1-fb-page-resolver.md) |
| [ ] | **FB2** | `fb-page-feed-poller` | FB1, C1, C11 | L | [brief](sessions/FB2-fb-page-feed-poller.md) |
| [ ] | **Q1** | Query API v0 | D3, C6, C15, G1 | M | [brief](sessions/Q1-query-api-v0.md) |
| [ ] | **U1** | Dashboard slice for Meta App Review | Q1, FB2 | M | [brief](sessions/U1-dashboard-slice-for-meta-app-review.md) |
| [ ] | **E2** | Gate tooling for staging | G1, I1, I2 | M | [brief](sessions/E2-gate-tooling-for-staging.md) |
| [ ] | **G2** | Gate: staging with real data | N1, N2, N3, N4, N5, N6, N7, W1, W2, W3, E2 | M | [brief](sessions/G2-gate-staging-with-real-data.md) |

## Wave 4 · YouTube, X, and Facebook in development mode

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **YT0** | YouTube probe | F1 | S | [brief](sessions/YT0-youtube-probe.md) |
| [ ] | **YT1** | `yt-channel-resolver` | YT0, C8, G1 | M | [brief](sessions/YT1-yt-channel-resolver.md) |
| [ ] | **YT2** | `yt-pubsub-receiver` | YT1, I1 | M | [brief](sessions/YT2-yt-pubsub-receiver.md) |
| [ ] | **YT3** | `yt-uploads-reconciler` | YT1 | M | [brief](sessions/YT3-yt-uploads-reconciler.md) |
| [ ] | **YT4** | `yt-video-details-fetcher` | YT1, C11 | M | [brief](sessions/YT4-yt-video-details-fetcher.md) |
| [ ] | **YT5** | `yt-comments-fetcher` | YT4, C11 | M | [brief](sessions/YT5-yt-comments-fetcher.md) |
| [ ] | **YT6** | `yt-replies-fetcher` | YT5 | M | [brief](sessions/YT6-yt-replies-fetcher.md) |
| [ ] | **YT7** | `yt-text-purger` | YT5, C14 | M | [brief](sessions/YT7-yt-text-purger.md) |
| [ ] | **YT8** | `yt-keyword-search` | YT1, YT4, C1 | M | [brief](sessions/YT8-yt-keyword-search.md) |
| [ ] | **YT9** | `yt-web-search-bridge` | W1, W2, YT1 | S | [brief](sessions/YT9-yt-web-search-bridge.md) |
| [ ] | **X0** | X probe | F1 | S | [brief](sessions/X0-x-probe.md) |
| [ ] | **X1** | `x-recent-search` | X0, C1, C5, G1 | L | [brief](sessions/X1-x-recent-search.md) |
| [ ] | **X2** | `x-user-resolver` | X1, C8 | M | [brief](sessions/X2-x-user-resolver.md) |
| [ ] | **X3** | `x-user-timeline-poller` | X1 | M | [brief](sessions/X3-x-user-timeline-poller.md) |
| [ ] | **X4** | `x-filtered-stream` | X1, X3 | M | [brief](sessions/X4-x-filtered-stream.md) |
| [ ] | **X5** | `x-full-archive-search` | X1, C10 | M | [brief](sessions/X5-x-full-archive-search.md) |
| [ ] | **X6** | `x-replies-fetcher` | X3, C11 | M | [brief](sessions/X6-x-replies-fetcher.md) |
| [ ] | **X7** | `x-compliance-sync` | X0, C13, C14, G1 | M | [brief](sessions/X7-x-compliance-sync.md) |
| [ ] | **FB3** | `fb-backfill` | FB2, C10 | M | [brief](sessions/FB3-fb-backfill.md) |
| [ ] | **FB4** | `fb-reactions-fetcher` | FB2, C11 | M | [brief](sessions/FB4-fb-reactions-fetcher.md) |
| [ ] | **FB5** | `fb-post-comments-fetcher` | FB2, C11 | L | [brief](sessions/FB5-fb-post-comments-fetcher.md) |
| [ ] | **FB6** | `fb-page-search` | FB1, C8 | M | [brief](sessions/FB6-fb-page-search.md) |
| [ ] | **G3** | Gate: platform go-live (repeat per platform) | G2 | M | [brief](sessions/G3-gate-platform-go-live.md) |

## Wave 5 · Approval-gated platforms and the client portal

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **G4** | Gate: production readiness | G2, E2 | M | [brief](sessions/G4-gate-production-readiness.md) |
| [ ] | **U2** | Client portal | D3, Q1 | L | [brief](sessions/U2-client-portal.md) |
| [ ] | **FB7** | `fb-client-webhook-receiver` | FB2, U2, I1 | M | [brief](sessions/FB7-fb-client-webhook-receiver.md) |
| [ ] | **IG1** | `ig-account-resolver` | FB0, C8, G1 | M | [brief](sessions/IG1-ig-account-resolver.md) |
| [ ] | **IG2** | `ig-hashtag-search` | FB0, C1, C8, G1 | M | [brief](sessions/IG2-ig-hashtag-search.md) |
| [ ] | **IG3** | `ig-account-media-poller` | IG1, C11 | L | [brief](sessions/IG3-ig-account-media-poller.md) |
| [ ] | **IG4** | `ig-webhook-receiver` | IG3, U2, I1 | M | [brief](sessions/IG4-ig-webhook-receiver.md) |
| [ ] | **IG5** | `ig-mentions-fetcher` | IG4 | M | [brief](sessions/IG5-ig-mentions-fetcher.md) |
| [ ] | **IG6** | `ig-own-comments-fetcher` | IG3, IG4, C11 | M | [brief](sessions/IG6-ig-own-comments-fetcher.md) |
| [ ] | **LI0** | LinkedIn probe (Development tier) | F1 | S | [brief](sessions/LI0-linkedin-probe.md) |
| [ ] | **LI1** | `li-client-posts-poller` | LI0, U2, C14 | M | [brief](sessions/LI1-li-client-posts-poller.md) |
| [ ] | **LI2** | `li-own-comments-fetcher` | LI1, C11 | M | [brief](sessions/LI2-li-own-comments-fetcher.md) |
| [ ] | **LI3** | `li-notification-receiver` | LI1, LI2, I1 | M | [brief](sessions/LI3-li-notification-receiver.md) |
| [ ] | **TG0** | Telegram probe | F1 | S | [brief](sessions/TG0-telegram-probe.md) |
| [ ] | **TG1** | `tg-bot-channel-receiver` | TG0, I1, C8, G1 | M | [brief](sessions/TG1-tg-bot-channel-receiver.md) |
| [ ] | **TG2** | `tg-discussion-receiver` | TG1, C11 | M | [brief](sessions/TG2-tg-discussion-receiver.md) |
| [ ] | **TT0** | TikTok Display probe (sandbox) | F1 | S | [brief](sessions/TT0-tiktok-display-probe.md) |
| [ ] | **TT1** | `tt-client-videos-fetcher` | TT0, U2 | M | [brief](sessions/TT1-tt-client-videos-fetcher.md) |

## Wave 6 · Insight layer

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **A0** | Labelled evaluation set | D2 | M | [brief](sessions/A0-labelled-evaluation-set.md) |
| [ ] | **A1** | `analysis-sentiment` | F6, C4, A0, G1 | L | [brief](sessions/A1-analysis-sentiment.md) |
| [ ] | **A2** | `analysis-topics` | F6, C4, A0, G1 | L | [brief](sessions/A2-analysis-topics.md) |
| [ ] | **A3** | `analysis-entities` | F6, C4, A0, G1 | L | [brief](sessions/A3-analysis-entities.md) |
| [ ] | **A4** | `analysis-media` | F6, C4, G1 | L | [brief](sessions/A4-analysis-media.md) |
| [ ] | **A5** | `alert-evaluator` | C15, C5, G1, A1, A2, A3, A4 | M | [brief](sessions/A5-alert-evaluator.md) |
| [ ] | **U3** | Full dashboard | Q1, U2, A1, A2 | L | [brief](sessions/U3-full-dashboard.md) |

## Wave 7 · Amber vendor routes (optional)

| Done | Session | Builds | Needs first | Size | Brief |
|---|---|---|---|---|---|
| [ ] | **VFB0** | Facebook vendor probe | F5, G2 | S | [brief](sessions/VFB0-facebook-vendor-probe.md) |
| [ ] | **VFB1** | `fb-keyword-search` | VFB0, C5, C8 | M | [brief](sessions/VFB1-fb-keyword-search.md) |
| [ ] | **VFB2** | `fb-group-posts-poller` | VFB0, C10, C11 | M | [brief](sessions/VFB2-fb-group-posts-poller.md) |
| [ ] | **VFB3** | `fb-group-comments-fetcher` | VFB2, C11 | M | [brief](sessions/VFB3-fb-group-comments-fetcher.md) |
| [ ] | **VIG0** | Instagram vendor probe | F5, G2 | S | [brief](sessions/VIG0-instagram-vendor-probe.md) |
| [ ] | **VIG1** | `ig-keyword-search` | VIG0, IG2 | M | [brief](sessions/VIG1-ig-keyword-search.md) |
| [ ] | **VIG2** | `ig-comments-fetcher` | VIG0, IG3, C11 | M | [brief](sessions/VIG2-ig-comments-fetcher.md) |
| [ ] | **VTT0** | TikTok vendor probe | F5, G2 | S | [brief](sessions/VTT0-tiktok-vendor-probe.md) |
| [ ] | **VTT1** | `tt-keyword-search` | VTT0, C5 | M | [brief](sessions/VTT1-tt-keyword-search.md) |
| [ ] | **VTT2** | `tt-hashtag-feed-poller` | VTT0 | M | [brief](sessions/VTT2-tt-hashtag-feed-poller.md) |
| [ ] | **VTT3** | `tt-user-resolver` | VTT0, C8 | M | [brief](sessions/VTT3-tt-user-resolver.md) |
| [ ] | **VTT4** | `tt-profile-videos-poller` | VTT3, C10, C11 | M | [brief](sessions/VTT4-tt-profile-videos-poller.md) |
| [ ] | **VTT5** | `tt-video-comments-fetcher` | VTT4, C11 | M | [brief](sessions/VTT5-tt-video-comments-fetcher.md) |
| [ ] | **VTT6** | `tt-video-stats-refresher` | VTT4, C11 | M | [brief](sessions/VTT6-tt-video-stats-refresher.md) |
| [ ] | **VLI0** | LinkedIn vendor probe | F5, G2 | S | [brief](sessions/VLI0-linkedin-vendor-probe.md) |
| [ ] | **VLI1** | `li-post-search` | VLI0, C5 | M | [brief](sessions/VLI1-li-post-search.md) |
| [ ] | **VLI2** | `li-org-resolver` | VLI0, C8 | M | [brief](sessions/VLI2-li-org-resolver.md) |
| [ ] | **VLI3** | `li-company-posts-poller` | VLI2, C10, C11, C14 | M | [brief](sessions/VLI3-li-company-posts-poller.md) |
| [ ] | **VLI4** | `li-post-comments-fetcher` | VLI3, C11 | M | [brief](sessions/VLI4-li-post-comments-fetcher.md) |
| [ ] | **VTG0** | Telegram vendor probe | F5, G2 | S | [brief](sessions/VTG0-telegram-vendor-probe.md) |
| [ ] | **VTG1** | `tg-message-search` | VTG0, C5 | M | [brief](sessions/VTG1-tg-message-search.md) |
| [ ] | **VTG2** | `tg-channel-resolver` | VTG0, C8 | M | [brief](sessions/VTG2-tg-channel-resolver.md) |
| [ ] | **VTG3** | `tg-channel-posts-poller` | VTG2, C10, C11 | M | [brief](sessions/VTG3-tg-channel-posts-poller.md) |
