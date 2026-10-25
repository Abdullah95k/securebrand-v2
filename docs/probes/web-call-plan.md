# Web probe: call plan and expected cost (W0, step 1)

Written by the probe-writing session. No real call has been made. The next session runs
`tools/probes/web` once the user has said yes to this list and sent the keywords.

## Call shapes the PRDs use (sections 5.3 and 7)

| Vendor       | Call shape in the PRD                                                                                                                                                                                                                                                                                                                                           | Paging                        | Cost in the PRD                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------------------------------- |
| Perplexity   | `POST https://api.perplexity.ai/search`, Bearer key; `query` (string or up to 5), `country: "IQ"`, `search_language_filter: ["ar"]` or `["ar","ckb"]`, `max_results`, `max_tokens_per_page`, `search_after_date_filter` (MM/DD/YYYY), `search_domain_filter` (site_search only). Fields read: `title`, `url`, `snippet`, `date`, `last_updated`, response `id`. | none                          | USD 5 per 1,000 requests                    |
| Mojeek       | `GET` Web Search API, `q`, `rb=IQ`, `lb=AR`, key, format, number of results, offset (names to be confirmed). First page only in v1. Fields: title, URL, description, rank, date if any.                                                                                                                                                                         | offset, depth to be confirmed | GBP 3 per 1,000 queries (Business)          |
| GDELT        | `GET` DOC 2.0, article-list mode, JSON, `query` = forms joined with OR, `startdatetime`/`enddatetime` or `timespan`, `maxrecords`, `sort`. Fields: url, title, seendate, domain, language, sourcecountry. No key.                                                                                                                                               | none in article-list mode     | USD 0; 1 request per 5 s                    |
| Common Crawl | crawl list; captures with domain match `*.iq`; captures per seed registrable domain. Index API or columnar bulk read to be decided. Fields: URL, host, time, status, MIME, language. No key.                                                                                                                                                                    | index pages                   | USD 0; polite pace, user agent with contact |

## Planned calls, for 30 keywords (10 Arabic, 10 Sorani, 10 English)

Counts come from `pnpm --filter web probe:plan` with the real keyword file; the table below was
computed with 30 synthetic keywords. The run session must print the plan again and quote its hash.

| Vendor       | Calls | Cap | Expected cost                                 | What the calls are                                                                                                                                                                                                                                                                                                                                                                           |
| ------------ | ----- | --- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Perplexity   | 20    | 30  | USD 0.100 (cap USD 0.15)                      | 6 packed requests (5 queries each, so all 30 keywords once); `ckb` canary; `["ar","ckb"]` request; one rule's 5 variants; `max_results` 20; date filter; no `country`; `site_search` on youtube.com; `max_tokens_per_page`; one empty result; one malformed-date error; 4 back-to-back requests to read rate-limit headers (stop at the first 429, no retry)                                 |
| Mojeek       | 28    | 30  | GBP 0.084 (cap GBP 0.09) at the Business rate | 18 keywords (spread over the three languages) with `rb=IQ`, `lb=AR`; pages 2 and 3; no boosts; `t` at 100; `site:`; `OR`; phrase plus a term; `lb=CKB`; one empty result; one bad-format error. Not every keyword fits under the cap of 30; 12 are left out here.                                                                                                                            |
| GDELT        | 39    | 60  | USD 0                                         | every keyword once (7 days, 250 records, newest first); one mixed Arabic/Latin `OR` query; 3 months span; `maxrecords=1000`; explicit start/end window; `sourcelang:arabic`; `sourcecountry:iraq`; a two-letter query (error text); empty; unknown mode. 5.5 s between requests: about 215 s.                                                                                                |
| Common Crawl | 16    | 20  | USD 0                                         | crawl list; page count for `*.iq`; two index pages and a `limit` sample with the requested fields; page counts for `gov.iq`, `edu.iq`, `com.iq`, `org.iq`, `net.iq`, `mil.iq`; three public outlets as seeds (rudaw.net, shafaq.com, alsumaria.tv); one empty domain; one unknown crawl id. Sequential, 4 s apart, user agent with a contact address. The columnar bulk route is not tested. |

Guards in the code: the host allowlist (four hosts), per-vendor request ceilings, spacing, no
redirects (a redirect would resend a key), a stop on the first 401, 403 or 429 for that vendor, and
`--approved <plan hash>`: the run refuses unless the hash matches the list the user approved.

## How secrets stay out

The Mojeek key goes into the URL at the last step in `src/http.ts`. Planned calls, saved requests,
logs and error messages never contain it: every string goes through `redact()` (parameter patterns plus the
exact secret values read from the environment). Tests cover a URL, an encoded secret, a bearer
token and an error message that quotes a URL.

## Scrubbing

Social-media results (Facebook, Instagram, X, TikTok, YouTube, Telegram, LinkedIn and others) are treated as
private individuals unless the handle is in `tools/probes/web/public-accounts.txt`: the handle in the URL, the
name in the title and the snippet are replaced by stable fakes. News outlets and other sites keep their
URLs. The scrubbing test fails on a token pattern, a signed URL, or any original that the scrubber replaced
(recorded in `raw/replaced.json`, deleted with `raw/`).

## Credentials in this session

Checked by name only, values never printed:

- `PERPLEXITY_API_KEY`: not set in this container's shell
- `MOJEEK_API_KEY`: not set in this container's shell

## What the run session needs (carried in the NEEDS-INPUT message)

1. The user's yes to the call list and cost above.
2. The 30 keywords for `tools/probes/web/keywords.txt` (Arabic, Sorani, English). They appear in the committed fixtures.
3. The Mojeek plan, Business or Startup. On Startup the run stores only counts, timings and field names, and the Business assumptions stay "not tested".
4. A contact address for the Common Crawl user agent (`PROBE_CONTACT`), and the company name in the agent string (placeholder in code: `SecureBrand-listening-probe`).
5. Both keys present in the run session's environment.
6. A list of the client's own public social accounts for `public-accounts.txt`, if the fixtures should keep them.

Not covered by the brief, so not planned: the Mojeek API's own endpoint is assumed to be
`https://api.mojeek.com/search` and its parameter names (`fmt`, `rb`, `lb`, `s`, `t`) come from memory of its
documentation. The first Mojeek call is a canary; if its answer is not JSON, the run stops that vendor and the
report marks the PRD assumption "different".
