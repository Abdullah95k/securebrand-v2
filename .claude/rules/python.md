---
paths:
  - "services/**/*.py"
  - "py/**"
---

# Python services

- Python services are news-article-extractor, the four analysis services and lang-dialect-id (ADR-0028). They use `py/listening_sdk` for consumers, producers, the job wrapper, DLQ, logs, metrics and health, with the same semantics as the Node SDK, proved by the shared conformance tests.
- Contract types are the Pydantic models generated from `packages/contracts`; never hand-write a message model.
- Typed code, ruff-clean, pytest; the Python version is pinned in `.python-version`; dependencies through uv with a lock file.
- Model files come from cleared sources only (Hugging Face is cleared); pin every model by version and record it in `model_versions`.
