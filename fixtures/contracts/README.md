# Contract fixtures

The record both languages test `packages/contracts` against (F2). The TypeScript conformance suite (`packages/contracts/test/conformance/`) and the Python one (`packages/contracts/python/tests/test_conformance.py`) read the same files and must agree on every one (G0 check 2).

## Layout

- `<schema id>/valid/*.json`: messages that pass as a producer and as a consumer would validate them. `job/v1` is one directory for every queue; the shared `dlq.<service>/v1` definition uses `dlq/v1`.
- `<schema id>/invalid/*.json`: messages that break one rule each, named for the rule. `invalid/expected.json` gives each file's expected error `path` and the `rule`, with the ADR or question behind it; a validator must report an issue at that path in producer mode.
- `<schema id>/tolerant/*.json`: a valid message plus one unknown field, which a consumer accepts and drops and a producer refuses (ADR-0002).
- `valid/options.json` (and `queue` in `expected.json`): the queue a job is validated against, since a job's producer-table row, required fields and partition key depend on its queue (ADR-0004, ADR-0012).
- `prd-examples.json`: every JSON example in a PRD's section 6.2, one entry per example: the producing service, the PRD line, the schema, the rewritten fixture (`<schema id>/valid/prd-<service>.json`) with the rewrites the ADRs required, or a note saying why the example is no message on a topic or queue (A6).
- `golden/*.json`: the golden vectors of the key and id helpers, canonical JSON, URLs, query keys, deletion ids, partition keys and the vocabulary, which both languages reproduce byte for byte (A7 to A16, A19, A23).

## Writing fixtures

Every fixture except the golden files is written by `packages/contracts/scripts/fixtures/gen.py`, which derives each id, key and hash with the package's own Python helpers:

```sh
pnpm --filter contracts gen:fixtures
```

It rewrites every directory here except `golden/` and this file, so change a fixture in the generator, not by hand, then run both conformance suites.

No file here records a platform call: every message is synthetic, written from the PRD examples, so this directory needs no per-file provenance entry (`docs/handoffs/F1.md`). The ids of public pages, channels, groups and outlets are the PRD examples' illustrative ones. Every individual's id, handle and name is invented, and every `author_ref` is derived from an invented id under the published test key in `common.py` (not a secret, ADR-0010; D-8). A discovery poster's clear id and handle appear only where ADR-0010 L49 keeps them on the bus until the poster is classed (a `raw.items` payload and the `discovery.hits` candidate), in the candidate key a resolve job and its report carry as issued (`golden/partition-keys.json`, ADR-0032), and in reject cases. `poster.profiles/v1/valid/individual.json` is x-recent-search's poster (`x:1000000000000000001`, `example_poster_x`) answered as an ordinary individual: its `author_ref` is that invented id's reference under the test key. `scripts/check-fixtures.sh` scans this directory for tokens like every fixture directory.
