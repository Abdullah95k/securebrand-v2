# x-compliance-sync

**Platform:** X · **Route:** green · **Lane:** Support · **Owner:** Backend lead, compliance and retention · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

What we collect from X stays under X's control. X's Developer Agreement requires us to mirror deletions and status changes within 24 hours. A post may be deleted, its author may protect the account, deactivate it or be suspended, or X may withhold the post in a country. When that happens, every copy we hold and everything clients see must change too. We keep X content in ClickHouse, the text index, the raw and Parquet archives and caches. A deletion on X does not reach any of them on its own, and the `x_24h_sync` retention class removes nothing on a timer. Without this service, nothing would ever remove it.

x-compliance-sync is how we learn about those changes. Once a day, and whenever ops asks, it sends X the list of every post and user id we still hold and turns X's answer into deletions. Without it we would keep showing clients posts their authors removed, breach the agreement, and risk losing our X access, which is our only green route to X. A government client raises the bar. It buys under an Enterprise plan that X reviews, and both the client and X may ask us to prove that every deletion was mirrored on time. The audit record each run writes is that proof.

## 2. Objective (the end state this service delivers)

Every X post and user id we hold in identifiable form is checked against X at least once every 24 hours. Every id that X reports as deleted, protected, suspended, deactivated, or withheld in Iraq is removed or hidden everywhere within 24 hours of X's signal. Every run leaves an exportable audit record that proves it. Target: 100% of stored ids submitted on every daily run, zero deletions completed more than 24 hours after `signal_at`, and one audit record with status `pass` for every 24 hours.

## 3. Scope

### In scope

- Daily and on-demand runs: collecting stored X post and user ids, submitting batch compliance jobs and downloading the results.
- Turning results into `deletions` with reason `platform_sync` and class `x_24h_sync`, including the country-scoped `withhold` mode for Iraq.
- Reporting registered X sources that are suspended, protected or deactivated (and their return) to source-health-canary.
- Following its deletions to completion, one audit record per run, and exports for government clients and X.
- Checking that every stored X row carries the class `x_24h_sync`.

### Out of scope

- Applying deletions to stores, archives, caches and the text index, and notifying clients (deletion-propagator). Recomputing aggregates (aggregator).
- The cross-class 24-hour deadline watch and `clock_breach` (retention-purger, which this service feeds).
- Fetching X content (x-recent-search, x-full-archive-search, x-filtered-stream, x-user-timeline-poller, x-replies-fetcher). Restoring content when a user returns.
- Deletions with other reasons: retention, author requests, client offboarding.

## 4. Users and consumers

- **Ops and the compliance owner** trigger runs, read audit records and request exports.
- **Government clients and X reviewers** receive audit exports.
- **Downstream:** deletion-propagator consumes `deletions`. retention-purger reads `signal_at` and `due_at` for its `x_24h_sync` watch and cites our run ids in its audit. source-health-canary receives source statuses. quota-governor is involved only if compliance jobs are metered.
- **Upstream:** the five X fetchers produce the data. It reaches the window through store-writer (ClickHouse) and raw-archiver (archives and their index).

## 5. How it works

### 5.1 Trigger and rotation

This service is not a poller and the tier rotation does not apply: every run covers the whole window. The window is every X post id and user id still stored in identifiable form. That means ClickHouse `items` and `comments` rows with platform `x`, raw-archiver's index of the raw and Parquet archives, and `sources.platform_id` for registered X sources. The window has no time limit, because `x_24h_sync` purges nothing by time.

There are two triggers. (1) A daily run from a leader-elected loop (Postgres advisory lock) at `RUN_AT_UTC` (initial value to be set in the pilot). Each next run is scheduled from the start of the last one, so the cadence does not drift. (2) An `ops_force` job on `jobs.x-compliance-sync`, which can be limited to an id list or to one client's sources. Ops uses it after a request from X, before a government review, or after an incident.

If 24 hours pass after the last run started and no new run has begun, `run_missed` fires and the loop starts a run at once. A run must finish steps 1 to 7 within `RUN_WINDOW_HOURS` (below 24, to be set in the pilot). If it cannot, `run_overdue` fires and it retries with new jobs. There is no backfill, because every run submits the full window.

### 5.2 Step by step

1. Open the run. Write a row to `x_compliance_runs` with `run_id` (ULID), trigger and `started_at`.
2. Collect the ids. Posts: distinct X ids from ClickHouse `items` and `comments`, plus ids found only in the archive index. Users: `sources.platform_id`, plus author ids from the archive index (mentions keep only `author_hash` in ClickHouse). Ids with an open `platform_sync` deletion are left out. Reconcile the counts against the stores. Count rows whose `retention_class` is not `x_24h_sync` as `class_mismatch`; they are still submitted.
3. Check the budget. If `X_COMPLIANCE_METERED` is on, ask quota-governor for `x_pay_per_use`. Otherwise make no call.
4. Submit. Create one job for posts and one for users, and split further only above `JOB_MAX_IDS`. Upload the id files.
5. Wait. Poll every `JOB_POLL_SECONDS` and record `signal_at` per job.
6. Download. Stream the results and store them as evidence under `raw/green/x/<yyyy>/<mm>/<dd>/x-compliance-sync/<run_id>.jsonl.zst` (ids, statuses and X timestamps only).
7. Map and emit. Apply the table in 5.3, emit `deletions`, and call the canary hook for registered sources.
8. Watch. Read `deletion_requests` (status written by deletion-propagator) until every `deletion_id` is `completed` or 24 hours have passed since its `signal_at`. Runs may overlap only in this step.
9. Close. Write one `x_compliance_audit` row. It is `pass` only if the full window was submitted, no line was parked, and every deletion completed within 24 hours of `signal_at`. Otherwise it is `fail` and `audit_failed` fires.

### 5.3 The call it makes

X API v2 batch compliance, with the app-only bearer token of the company X app, injected per run from Supabase Vault. The paths, formats and limits below follow X's published design as we read it. They are **to be confirmed in the pilot**:

- `POST /2/compliance/jobs`, body `{"type": "tweets" | "users", "name": "<run_id>-<type>-<n>"}`. It returns `id`, `upload_url`, `upload_expires_at`, `download_url`, `download_expires_at` and `status`.
- `PUT <upload_url>`: plain text, one id per line, sent before `upload_expires_at`.
- `GET /2/compliance/jobs/{id}`: status `created`, `in_progress`, `complete`, `failed` or `expired`. On leader takeover, `GET /2/compliance/jobs?type=<type>&status=in_progress` finds the open jobs.
- `GET <download_url>`: JSON Lines, one object for each id that has a compliance event (expected fields `id`, `action`, `reason`, `created_at`, `redacted_at`). Ids that are absent are unchanged.
- Ids per job (`JOB_MAX_IDS`), concurrent jobs, URL lifetimes, processing time and endpoint rate limits: no value is assumed until the pilot confirms them.

`signal_at` is the earlier of two times: X's completion time on the job object, if it carries one, or our first observation of `complete`. `event_at` is X's own time for the change, if the result line carries one. Both are kept.

| X result | Scope | Mode | Effect |
|---|---|---|---|
| Post `deleted` | `item` | `delete` | Removed everywhere; aggregates recomputed |
| `protected`, `suspended`, `deactivated` | `item` (post results), `author` (user results) | `delete` | The post, or all the user's posts and comments, removed |
| `withheld`, IQ among the countries | `item` or `author` | `withhold` | Hidden from Iraqi clients; `countries` carried |
| `withheld`, IQ not among them | none | none | Counted `withheld_other`; handling to be confirmed in the pilot |
| Any other reason (for example a geo scrub) | none | parked | `dlq.x-compliance-sync`, `status_unknown` |

**Mapping.** Post ids map to `item_id` and `source_id` through ClickHouse, or through the raw envelope when the id is only in the archives. User ids map to `author_hash` (the SDK helper, with `AUTHOR_HASH_KEY` from Vault), and to `source_id` when the user is a registered source. The target carries `user_ids` so the archives can be searched. There is one message per `source_id` and status for posts, and one per `author_hash` for users. `deletion_id` = `del:platform_sync:<scope>:<sha256(platform_id, status, signal day)>`. A user already actioned with the same status and with nothing left stored is counted `unchanged` and gets no new message.

**Registered sources.** The SDK canary hook asks source-health-canary to set `health = blocked` so that x-user-timeline-poller stops polling the source. When X stops reporting the source, the hook sets `health` back to `ok`. Content is fetched again from that point on; nothing is restored.

### 5.4 What it gets

For each id that changed, it gets the status, the reason and X's timestamps, plus withheld countries if the batch result carries them (to be confirmed in the pilot). It gets no text, media, handles or explanations, and nothing about ids we did not submit.

## 6. Inputs and outputs

### 6.1 Reads

ClickHouse `items` and `comments` (distinct ids, counts, `retention_class`); raw-archiver's archive index; Postgres `sources`, `client_sources`, `deletion_requests`; `jobs.x-compliance-sync`; Supabase Vault (X app token, `AUTHOR_HASH_KEY`); quota-governor only if metered.

### 6.2 Writes

`deletions` (partitioned by `source_id`; author-scope messages keyed by `author_hash`); the canary hook; `dlq.x-compliance-sync`; evidence files; Postgres `x_compliance_runs`, the append-only `x_compliance_audit` (both to be added to the control-plane table list) and `service_runs`. Example `deletions` message:

```json
{
  "deletion_id": "del:platform_sync:item:9d2e4b7a1c0f3e58b6a9d4c2e7f1b3a5d8c0e6f2a4b9d1c3e5f7a0b2c4d6e8f1",
  "reason": "platform_sync", "scope": "item", "mode": "delete",
  "retention_class": "x_24h_sync",
  "source_id": "3a7d9c21-5e4b-4f8a-b6c0-2d1e9f7a3b54",
  "target": {"platform": "x", "kind": "post", "item_ids": ["01J9M4T6R8W2Y5B7D9F1H3K5N7"], "platform_ids": ["1842957310264891392"]},
  "platform_status": "deleted", "countries": null, "client_id": null,
  "requested_by": "x-compliance-sync", "run_id": "01J9PB2C4E6G8J0K2M4P6R8T0V", "x_job_id": "1843012947561203712",
  "event_at": "2026-10-05T19:42:07Z", "signal_at": "2026-10-06T02:47:31Z",
  "due_at": "2026-10-07T02:47:31Z", "emitted_at": "2026-10-06T02:51:09Z"
}
```

Example audit record (illustrative values):

```json
{
  "run_id": "01J9PB2C4E6G8J0K2M4P6R8T0V", "trigger": "daily",
  "started_at": "2026-10-06T01:55:00Z", "finished_at": "2026-10-06T05:55:10Z",
  "x_jobs": [{"type": "tweets", "job_id": "1843012947561203712", "signal_at": "2026-10-06T02:47:31Z"},
             {"type": "users", "job_id": "1843012951137462272", "signal_at": "2026-10-06T02:39:05Z"}],
  "ids_submitted": {"posts": 1240318, "users": 205611},
  "ids_returned": {"deleted": 912, "protected": 77, "suspended": 41, "withheld": 3, "deactivated": 58, "other": 0},
  "withheld_in_iq": 2, "class_mismatch": 0, "ids_actioned": 1090, "ids_completed": 1090,
  "signal_to_deleted_seconds": {"p50": 2410, "p95": 7930, "max": 11205},
  "evidence": ["raw/green/x/2026/10/06/x-compliance-sync/01J9PB2C4E6G8J0K2M4P6R8T0V.jsonl.zst"],
  "status": "pass"
}
```

**Exports.** Ops requests an export through n8n for a client or for X and a date range. The output is CSV and JSON Lines with a SHA-256 manifest. A client export covers runs and per-id lines (X id, status, `signal_at`, `completed_at`) for that client's sources only. An X export covers everything. Neither contains text or handles.

### 6.3 State

`x_compliance_runs` holds the run id, job ids and step status, so a new leader resumes the same run without creating jobs. The other state is the leader lock and the flags `X_COMPLIANCE_METERED`, `RUN_AT_UTC`, `RUN_WINDOW_HOURS`, `JOB_MAX_IDS` and `JOB_POLL_SECONDS`. There are no per-source cursors.

## 7. Limits, quotas and cost

- Metering: compliance jobs are not post reads on the pay-per-use meter unless X documents otherwise (to be confirmed in the pilot). The budget tag `x_pay_per_use` applies only if they are. If they were metered at USD 0.005 per post read, one daily run over a single month of X history (0.6M ids) would cost USD 3,000, and five such runs would use the 3,000,000-read cap. Pay-per-use would then be unworkable, and the terms would move to Enterprise.
- Window growth: X brings 0.6M items a month (about 20,000 a day). The post window grows by about 7.2M ids a year if identifiable items are kept. The user count is to be measured in the pilot.
- Job limits: to be confirmed in the pilot (5.3).
- Other cost: compute, one distinct-id scan a day on ClickHouse and the archive index, and small evidence files. Their size is to be measured in the pilot.

## 8. Failure handling and fallback

- 429: exponential backoff with jitter from 30 s to 15 min. After 5 attempts the step goes to `dlq.x-compliance-sync` and an alert fires.
- 401 or 403: mark the route `degraded`, stop, fire `compliance_blocked` and mark the audit `fail`. The service never tries another token or app.
- Job `failed` or `expired`, or an upload or download URL past expiry: recreate the job for the same id file within the run and count it in the audit.
- Collection incomplete (a store is unavailable or the counts do not reconcile): retry within the window. If it is still incomplete, submit what was collected and mark the audit `fail` with `window_incomplete`.
- Malformed line or unknown reason: DLQ and `status_unknown`. It is never treated as "no change".
- An id that X returns but we no longer store is counted `already_absent` and gets no message.
- Redpanda produce failure: retry. The deterministic `deletion_id` makes a repeat harmless.
- deletion-propagator is late: retention-purger raises `x_deadline_at_risk` and `clock_breach`, and this run's audit is `fail`.
- There is no amber or alternate route for compliance. `fallback_on` is never set.

## 9. Non-functional requirements

- Throughput: collecting, uploading and parsing the full window fits inside `RUN_WINDOW_HOURS`. Timings are to be measured in the pilot. Files are streamed, never held whole in memory.
- Latency: 100% of deletions complete within 24 hours of `signal_at`. `signal_to_emit_seconds` is to be measured in the pilot.
- Idempotency: deterministic `deletion_id`. Run state in Postgres, so a run can be resumed.
- Scaling: one leader per run with a standby replica. There are no per-id API calls.
- Security: the token comes only from Vault and is never logged. Files, messages and logs hold ids and statuses only, with no text or handles. `x_compliance_audit` has no delete role. Only ops and the compliance owner can read it.

## 10. Metrics and alerts

`ids_submitted_total{type}`, `ids_returned_total{type,status}`, `x_jobs_total{type,status}`, `job_wait_seconds`, `signal_to_emit_seconds`, `signal_to_deleted_seconds`, `window_ids{type}`, `class_mismatch_total`, `run_duration_seconds`, `last_complete_run_timestamp`, `dlq_total`. Alerts: `run_missed`, `run_overdue`, `compliance_blocked`, `window_incomplete`, `status_unknown`, `class_mismatch`, `audit_failed`, `dlq_nonempty`. SLO: one complete run in every 24 hours, 100% of deletions within 24 hours of `signal_at`, and the DLQ reviewed daily.

## 11. Dependencies

- X API v2 batch compliance on the company app (pay-per-use; Enterprise once a government end user is on board).
- listening-sdk (`author_hash`, canary hook), Redpanda, Supabase Postgres and Vault, ClickHouse, and n8n for exports.
- Services: raw-archiver, store-writer, deletion-propagator (needs mode `withhold` and scope `author` with `user_ids`), retention-purger, aggregator, source-health-canary, and quota-governor if metered.

## 12. Risks and mitigations

- **The 24 hours may count from X's event time rather than our signal.** A daily run could then miss by up to a day. Mitigation: `event_at` is recorded, the interval can shorten without code changes, and the Enterprise compliance options are assessed (question 1).
- **The window grows without limit.** Mitigation: split jobs by `JOB_MAX_IDS`, watch the `window_ids` trend, and decide how long identifiable X items are kept.
- **A partial run looks complete.** Mitigation: counts are reconciled against the stores, and the audit fails otherwise.
- **Copies already outside our stores (client exports, sent alerts).** Mitigation: deletion-propagator notifies clients, and client terms oblige them to delete (counsel).

## 13. Acceptance criteria

1. A fixture contains X ids in `items`, `comments` and only in the archive index, registered sources, raw-only author ids and already-deleted ids. The run submits exactly the distinct stored ids, and the audit counts match.
2. With a mock API and `JOB_MAX_IDS` = N, N post ids create one posts job and N + 1 create two. A users job is always created. Every job id is in the audit.
3. `deleted`, `protected`, `suspended` and `deactivated` each yield a message with reason `platform_sync`, class `x_24h_sync` and mode `delete`. The scope is `item` for post results and `author` for user results, with no handle, and `due_at` = `signal_at` + 24 h.
4. `withheld` with IQ yields mode `withhold` with the country list. Without IQ, no message is emitted and `withheld_other` is counted.
5. An unknown reason lands in `dlq.x-compliance-sync`, fires `status_unknown`, and the audit is `fail`.
6. Replaying a result file, or a same-day `ops_force` run, emits identical `deletion_id`s, and deletion-propagator acts once.
7. A job held `in_progress` past `RUN_WINDOW_HOURS` fires `run_overdue` and is recreated. When the old job completes later, nothing is applied twice.
8. A 403 marks the route `degraded`, fires `compliance_blocked` and stops the run without another token.
9. If the leader is killed in step 5, another replica resumes the same run id and job ids.
10. Every run writes exactly one audit record with the fields of 6.2. It is `pass` only if the full window was submitted and every deletion completed within 24 hours of `signal_at`.
11. With `X_COMPLIANCE_METERED` off, nothing is counted on `x_pay_per_use`. With it on, an allowance is requested before each job.
12. A client export holds only that client's sources, with no text or handles, and a SHA-256 manifest that matches.
13. A registered source reported `suspended` turns `blocked`. When X no longer reports it, it returns to `ok`.

## 14. Open questions

1. Does the 24-hour clock run from X's signal or from the event on X? To be settled with counsel and at X's Enterprise review, including whether a compliance stream should replace daily batches.
2. Endpoint paths, upload and download formats, job limits, and whether results carry withheld status with country codes: to be confirmed in the pilot.
3. If jobs are metered, should quota-governor reserve compliance ahead of all other X reads and never deny it? Proposed: yes.
4. Handling of content withheld outside Iraq. Proposed: record only.
5. Should the X fetchers add `withheld` to `tweet.fields` and `user.fields`? x-recent-search's approved PRD does not request it.
6. Should X ingestion pause when no complete run has happened for more than 24 hours? Proposed: yes under government contracts.
7. How long should identifiable X items, evidence files and audit records be kept? With counsel.
