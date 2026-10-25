import { describe, expect, it } from "vitest";
import {
  D3_WRITERS,
  INDEX_SERVICES,
  allowedProducers,
  decisionRow,
  decisionRows,
  isAllowedDecisionProducer,
  isAllowedProducer,
  isAllowedTopicWriter,
  isKnownService,
  namesService,
  producerRows,
  requiredJobFields,
} from "../../src/registries/index.ts";
import { HEALTHS, REGISTRY_REASONS } from "../../src/vocabulary.ts";

describe("the producer table (ADR-0012, A22)", () => {
  it("refuses a (queue, kind, producer.service) the table does not list", () => {
    expect(isAllowedProducer("jobs.fb-page-feed-poller", "rotation", "fb-page-feed-poller")).toBe(
      true,
    );
    expect(
      isAllowedProducer("jobs.fb-page-feed-poller", "rotation", "comment-decay-scheduler"),
    ).toBe(false);
    expect(
      isAllowedProducer("jobs.fb-page-feed-poller", "comments", "comment-decay-scheduler"),
    ).toBe(false);
    expect(
      isAllowedProducer("jobs.fb-post-comments-fetcher", "comments", "comment-decay-scheduler"),
    ).toBe(true);
    expect(isAllowedProducer("jobs.x-recent-search", "reconciliation", "x-filtered-stream")).toBe(
      true,
    );
    expect(
      isAllowedProducer("jobs.x-user-timeline-poller", "reconciliation", "x-filtered-stream"),
    ).toBe(false);
  });

  it("an unknown (queue, kind) has no producers", () => {
    expect(allowedProducers("jobs.no-such-service", "rotation")).toEqual([]);
    expect(allowedProducers("jobs.store-writer", "rotation")).toEqual([]);
    expect(allowedProducers("jobs.qualifier", "resolve")).toEqual([]);
  });

  it("names the queue's own service for @queue rows, the analysis priority lanes included", () => {
    expect(
      isAllowedProducer("jobs.analysis-sentiment.priority", "analyze", "analysis-sentiment"),
    ).toBe(true);
    expect(
      isAllowedProducer("jobs.analysis-sentiment.priority", "analyze", "analysis-topics"),
    ).toBe(false);
    expect(isAllowedProducer("jobs.analysis-media", "rerun", "admin-api")).toBe(true);
    expect(isAllowedProducer("jobs.analysis-media.priority", "rerun", "admin-api")).toBe(false);
    expect(isAllowedProducer("jobs.yt-pubsub-receiver", "push", "yt-pubsub-receiver")).toBe(true);
  });

  it("gives ops and client requests one writer, the admin API, and the review answer and export kinds", () => {
    expect(isAllowedProducer("jobs.qualifier", "review_answer", "admin-api")).toBe(true);
    expect(isAllowedProducer("jobs.x-compliance-sync", "export", "admin-api")).toBe(true);
    expect(isAllowedProducer("jobs.normalize-item", "replay", "admin-api")).toBe(true);
    expect(isAllowedProducer("jobs.keyword-matcher", "rematch", "admin-api")).toBe(true);
    expect(isAllowedProducer("jobs.keyword-matcher", "rematch", "client-portal")).toBe(false);
    expect(isAllowedProducer("jobs.ig-mentions-fetcher", "ops_force", "ig-webhook-receiver")).toBe(
      true,
    );
    expect(isAllowedProducer("jobs.ig-mentions-fetcher", "ops_force", "admin-api")).toBe(true);
  });

  it("names the required kind fields of the rows that need them", () => {
    expect(requiredJobFields("jobs.ig-hashtag-search", "rotation", "ig-hashtag-search")).toEqual([
      "edge",
    ]);
    expect(
      requiredJobFields("jobs.ig-hashtag-search", "backfill", "backfill-orchestrator"),
    ).toEqual(["edge"]);
    expect(
      requiredJobFields("jobs.x-recent-search", "reconciliation", "x-filtered-stream"),
    ).toEqual(["query", "window_start", "window_end", "source_ids", "client_ids"]);
    expect(requiredJobFields("jobs.x-recent-search", "reconciliation", "x-recent-search")).toEqual(
      [],
    );
    expect(requiredJobFields("jobs.yt-comments-fetcher", "refresh", "yt-text-purger")).toEqual([
      "post_ref",
      "run_id",
      "must_finish_by",
      "refresh_for_client_ids",
    ]);
    expect(requiredJobFields("jobs.news-site-resolver", "refresh", "news-site-resolver")).toEqual([
      "candidate_key",
      "source_id",
    ]);
    expect(requiredJobFields("jobs.news-site-resolver", "refresh", "news-feed-poller")).toEqual([
      "candidate_key",
      "source_id",
      "reason",
    ]);
    expect(
      requiredJobFields("jobs.web-commoncrawl-scanner", "rotation", "web-commoncrawl-scanner"),
    ).toEqual(["crawl_id"]);
    expect(
      requiredJobFields("jobs.yt-replies-fetcher", "replies", "comment-decay-scheduler"),
    ).toEqual(["post_ref.thread_ids"]);
    expect(
      requiredJobFields("jobs.x-full-archive-search", "replies", "comment-decay-scheduler"),
    ).toEqual(["window_start"]);
    expect(requiredJobFields("jobs.aggregator", "recompute", "admin-api")).toEqual([
      "from",
      "to",
      "request_id",
      "requested_by",
    ]);
  });

  it("names only services of the service index or admin-api, client-portal and admin-console (Q4)", () => {
    const named = new Set([
      ...producerRows().flatMap((r) => r.producers),
      ...decisionRows()
        .flatMap((r) => r.producers)
        .filter((p) => p !== "@platform" && p !== "*"),
    ]);
    for (const p of named) expect(isKnownService(p), p).toBe(true);
    for (const w of D3_WRITERS) expect(named.has(w), w).toBe(true);
  });
});

describe("the decision rows (ADR-0013, A22)", () => {
  const source = (decision: string, reason: string | null, health?: string) => ({
    decision,
    subject: "source_id" as const,
    reason,
    health,
  });

  it("allows the admin API's flag_off and flag_on decisions", () => {
    expect(
      isAllowedDecisionProducer(source("health_change", "flag_off", "blocked"), "admin-api"),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(source("health_change", "flag_on", "blocked"), "admin-api"),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(
        source("health_change", "flag_off", "blocked"),
        "fb-page-feed-poller",
      ),
    ).toBe(false);
  });

  it("allows the admin API's clearing health_change only with health ok and a non-flag reason (Q12)", () => {
    expect(
      isAllowedDecisionProducer(source("health_change", "bot_removed", "ok"), "admin-api"),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(source("health_change", "crawl_disallowed", "ok"), "admin-api"),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(source("health_change", "bot_removed", "blocked"), "admin-api"),
    ).toBe(false);
    expect(
      isAllowedDecisionProducer(source("health_change", "bot_removed", "degraded"), "admin-api"),
    ).toBe(false);
    expect(isAllowedDecisionProducer(source("health_change", "flag_off", "ok"), "admin-api")).toBe(
      false,
    );
  });

  it("refuses a source-level flag_off or flag_on with a health other than blocked (F-11)", () => {
    expect(
      isAllowedDecisionProducer(source("health_change", "flag_off", "degraded"), "admin-api"),
    ).toBe(false);
    expect(isAllowedDecisionProducer(source("health_change", "flag_on", "ok"), "admin-api")).toBe(
      false,
    );
  });

  it("accepts the canary's route-level flag_off with degraded (F-40)", () => {
    const route = {
      decision: "health_change",
      subject: "platform" as const,
      reason: "flag_off",
      health: "degraded",
    };
    expect(isAllowedDecisionProducer(route, "source-health-canary")).toBe(true);
    expect(isAllowedDecisionProducer(route, "admin-api")).toBe(false);
  });

  it("lets any service report credential_revoked, never as degraded (ADR-0016 L27)", () => {
    expect(
      isAllowedDecisionProducer(
        source("health_change", "credential_revoked", "blocked"),
        "fb-page-feed-poller",
      ),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(
        source("health_change", "credential_revoked", "blocked"),
        "normalize-item",
      ),
    ).toBe(true);
    expect(
      isAllowedDecisionProducer(
        source("health_change", "credential_revoked", "degraded"),
        "fb-page-feed-poller",
      ),
    ).toBe(false);
  });

  it("requires, accepts or refuses provenance on each decision row as its Provenance column says (F-14)", () => {
    const cases: [Parameters<typeof decisionRow>[0], string, string][] = [
      [{ decision: "add", subject: "candidate_key", reason: null }, "qualifier", "required"],
      [{ decision: "add", subject: "source_id", reason: null }, "client-portal", "refused"],
      [
        { decision: "add", subject: "source_id", reason: null },
        "tg-bot-channel-receiver",
        "required",
      ],
      [{ decision: "add", subject: "keyword_id", reason: null }, "admin-console", "refused"],
      [{ decision: "update", subject: "source_id", reason: null }, "ig-hashtag-search", "required"],
      [
        { decision: "update", subject: "source_id", reason: "budget_wait" },
        "ig-hashtag-search",
        "refused",
      ],
      [
        { decision: "remove_client", subject: "source_id", reason: "client_removed" },
        "retention-purger",
        "refused",
      ],
      [{ decision: "tier_change", subject: "source_id", reason: null }, "qualifier", "optional"],
      [
        { decision: "promote", subject: "source_id", reason: null },
        "yt-uploads-reconciler",
        "required",
      ],
      [{ decision: "promote", subject: "source_id", reason: null }, "qualifier", "refused"],
      [
        { decision: "retire", subject: "source_id", reason: "owner_request" },
        "retention-purger",
        "refused",
      ],
      [
        { decision: "retire", subject: "source_id", reason: "authorization_revoked" },
        "tt-client-videos-fetcher",
        "required",
      ],
      [
        { decision: "retire", subject: "source_id", reason: "not_found" },
        "yt-channel-resolver",
        "required",
      ],
      [
        { decision: "push_coverage", subject: "source_id", reason: "lease_lapsed" },
        "yt-pubsub-receiver",
        "refused",
      ],
      [
        {
          decision: "health_change",
          subject: "source_id",
          reason: "crawl_disallowed",
          health: "blocked",
        },
        "news-robots-checker",
        "required",
      ],
      [
        {
          decision: "health_change",
          subject: "platform",
          reason: "empty_200_rate",
          health: "fallback",
        },
        "source-health-canary",
        "required",
      ],
      [
        { decision: "review", subject: "candidate_key", reason: "age_gated" },
        "qualifier",
        "required",
      ],
      [{ decision: "mention_only", subject: "author_ref", reason: null }, "qualifier", "required"],
    ];
    for (const [decision, service, provenance] of cases) {
      expect(decisionRow(decision, service)?.provenance, `${decision.decision} ${service}`).toBe(
        provenance,
      );
    }
  });

  it("no two rows that match one decision give it different provenance", () => {
    const services = [...INDEX_SERVICES, ...D3_WRITERS];
    for (const row of decisionRows()) {
      const reasons = row.reasons ?? [null, ...REGISTRY_REASONS];
      const healths = row.healths ?? [undefined, ...HEALTHS];
      for (const decision of row.decisions) {
        for (const service of services.filter((s) => namesService(row.producers, s))) {
          for (const reason of reasons) {
            for (const health of healths) {
              const q = { decision, subject: row.subject, reason, health };
              const matches = decisionRows().filter(
                (r) =>
                  r.decisions.includes(decision) &&
                  r.subject === row.subject &&
                  namesService(r.producers, service) &&
                  (r.reasons === undefined || r.reasons.includes(reason)) &&
                  (r.healths === undefined || (health !== undefined && r.healths.includes(health))),
              );
              const provenance = new Set(matches.map((r) => r.provenance));
              expect(provenance.size, JSON.stringify({ ...q, service })).toBe(1);
            }
          }
        }
      }
    }
  });

  it("refuses a decision type from a producer no row lists", () => {
    expect(
      isAllowedDecisionProducer(
        { decision: "push_coverage", subject: "source_id", reason: null },
        "ig-webhook-receiver",
      ),
    ).toBe(false);
    expect(
      isAllowedDecisionProducer(
        { decision: "retire", subject: "source_id", reason: "owner_request" },
        "qualifier",
      ),
    ).toBe(false);
    expect(
      isAllowedDecisionProducer(
        { decision: "add", subject: "candidate_key", reason: null },
        "poster-resolver",
      ),
    ).toBe(false);
  });
});

describe("topic writers (CONVENTIONS v1.1 L25 to L40)", () => {
  it("allows each topic's writers and refuses the rest", () => {
    expect(isAllowedTopicWriter("item.hits/v1", "keyword-matcher")).toBe(true);
    expect(isAllowedTopicWriter("item.hits/v1", "normalize-item")).toBe(false);
    expect(isAllowedTopicWriter("source.events/v1", "registry-writer")).toBe(true);
    expect(isAllowedTopicWriter("source.events/v1", "qualifier")).toBe(false);
  });

  it("restricts a raw.items writer to its record kinds", () => {
    expect(isAllowedTopicWriter("raw.items/v1", "fb-page-resolver", { kind: "profile" })).toBe(
      true,
    );
    expect(isAllowedTopicWriter("raw.items/v1", "fb-page-resolver", { kind: "post" })).toBe(false);
    expect(isAllowedTopicWriter("raw.items/v1", "li-org-resolver", { kind: "post" })).toBe(true);
    expect(isAllowedTopicWriter("raw.items/v1", "search-hit-router", { kind: "result" })).toBe(
      true,
    );
    expect(isAllowedTopicWriter("raw.items/v1", "tt-user-resolver", { kind: "profile" })).toBe(
      false,
    );
    expect(
      isAllowedTopicWriter("raw.items/v1", "tt-video-stats-refresher", { kind: "metrics" }),
    ).toBe(false);
  });

  it("names the service behind a jobs.completed report and a dead letter", () => {
    expect(
      isAllowedTopicWriter("jobs.completed/v1", "x-recent-search", {
        queue: "jobs.x-recent-search",
      }),
    ).toBe(true);
    expect(
      isAllowedTopicWriter("jobs.completed/v1", "x-filtered-stream", {
        queue: "jobs.x-recent-search",
      }),
    ).toBe(false);
    expect(isAllowedTopicWriter("dlq.normalize-item/v1", "normalize-item")).toBe(true);
    expect(isAllowedTopicWriter("dlq.normalize-item/v1", "store-writer")).toBe(false);
  });

  it("registry.decisions writers are the decision rows' producers", () => {
    expect(isAllowedTopicWriter("registry.decisions/v1", "qualifier")).toBe(true);
    expect(isAllowedTopicWriter("registry.decisions/v1", "client-portal")).toBe(true);
    expect(isAllowedTopicWriter("registry.decisions/v1", "store-writer")).toBe(true); // credential_revoked, any service
    expect(isAllowedTopicWriter("registry.decisions/v1", "nobody")).toBe(false);
  });
});
