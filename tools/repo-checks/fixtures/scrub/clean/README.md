# Clean scrubbed fixtures (test data for scripts/check-fixtures.sh)

| File | Call | Date | Scrubbed |
|---|---|---|---|
| page-feed.json | GET /{page-id}/feed?limit=100 (shape only, synthetic content) | 2026-10-07 | access token replaced with REDACTED |
| comments.jsonl | GET /{post-id}/comments?filter=stream (shape only, synthetic content) | 2026-10-07 | commenter names and ids replaced with stable fakes |
