# ADR-0028 · lang-dialect-id in Python

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: lang-dialect-id, F4, F6, F7, normalize-item, keyword-matcher, poster-resolver, ig-account-resolver, li-org-resolver, news-site-resolver, analysis-media, analysis-sentiment
Source: D2-Q028 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS allows Python only for the analysis workers and the news extractor (CONVENTIONS L13). lang-dialect-id needs CAMeL Tools and KLPT, which are Python libraries: "Runtime: Python, because CAMeL Tools and KLPT are Python libraries" (`lang-dialect-id §9 L150`), and it asks to confirm a third exception or port the fold to TypeScript (`lang-dialect-id §14 Q1 L187`; CF-112). The build plan proposes Python with a TypeScript copy of the fold for fallback (FC-08), and the session plan already assumes it: C3 needs F6 (the Python SDK) and F7 (the fold and its golden corpus) first (`build-plan/SESSIONS.md`). F7 builds the folds "in TypeScript exactly as lang-dialect-id section 5.3 C defines them" with a golden corpus "both languages' code must pass" (F7 brief). Two smaller points ride on the same service. Its callers: lang-dialect-id names normalize-item as "the only caller of `/v1/detect`" (`lang-dialect-id §4 L34`, `§6.1 L99`), while poster-resolver sends it a sample of up to 20 recent posts per candidate (`poster-resolver §5.2 L58`), li-org-resolver asks the SDK's "language client" for a language share (`li-org-resolver §5.2 L56`), news-site-resolver takes one "from lang-dialect-id over the last 20 titles" (`news-site-resolver §5.2 L52`) and analysis-media sends transcripts (`analysis-media §5.3 L66`) (AU-074). And Arabic written in Latin letters (Arabizi): analysis-sentiment routes it through transliteration (`analysis-sentiment §5.2 L57`), but lang-dialect-id reads Arabizi "as `en` or `und`" (`lang-dialect-id §12 L164`), keeps transliteration out of scope (`§3 L29`) and asks whether to add a Latin-script Arabic class after the pilot (`§14 Q3 L189`); F7's brief records Arabizi as "not transliterated (documented gap)" (AU-075). The service already sets `script` (`arab`, `latn`, `mixed` or `none`, `lang-dialect-id §5.2 L51`, `§5.4 L92`), which normalize-item copies (`§6.2 L105`); but `latn` cannot tell Arabizi from English, since Latin tokens count as `en` (`§5.3 L63`).

Settles: FC-08, CF-112, AU-074, AU-075, lang-dialect-id §14 Q1, lang-dialect-id §14 Q2, lang-dialect-id §14 Q3, lang-dialect-id §14 Q4, poster-resolver §14 Q3.

## Options

1. **Python service, recorded as the third exception, with the fold also in TypeScript** (chosen): its rules are under Decision.
2. **Port the fold to TypeScript and keep only fastText and the dialect model in Python.** Consequences: the exception narrows to a model server but does not disappear; the CAMeL and KLPT behaviour the PRD relies on must be reimplemented and kept equal by hand.
3. **Node only, with fastText through WebAssembly and no CAMeL Tools or KLPT.** Consequences: no Python exception, but the Iraqi-dialect and Sorani features the PRD names are lost or rebuilt from scratch.

## Decision

lang-dialect-id is a Python service on the Python SDK, recorded as the third exception to the Node rule, with the fold also in TypeScript and both implementations checked against F7's golden corpus. Its callers are named. Arabizi and Kurmanji (Badini) are documented gaps in v1, measured by the pilot.

lang-dialect-id runs on the Python SDK (F6) with CAMeL Tools, KLPT and fastText; F7's TypeScript fold is byte-identical to the Python one on the golden corpus; it is a fallback only, used if the service is unreachable, since keyword-matcher and CI tools call `/v1/fold` (`lang-dialect-id §6.1 L99`). Its callers are named: normalize-item; the resolvers that compute `lang_share` under ADR-0033, ig-account-resolver, li-org-resolver and news-site-resolver (profile samples, through a batch form of `/v1/detect` wrapped by the SDK's language client), not poster-resolver, which reads their shares; and analysis-media (transcripts), and the service's pool is sized for them (AU-074 option 1). Arabizi gets no route in v1: `script` stays exactly as defined, the model does not measure Arabizi, and analysis-sentiment drops its transliteration branch. The pilot measures it by hand-labelling a sample of `latn` items, and an Arabizi class is considered after the pilot as `lang-dialect-id §14 Q3 L189` asks (AU-075 option 3).

It also answers: lang-dialect-id's other open points: Kurmanji (Badini) stays `other` in v1, a documented gap like Arabizi, with a label considered after the pilot (`§14 Q2`); `items.normalized` carries the top dialect class and its confidence, the full `dialect_scores` vector staying in lang-dialect-id's own evaluation log (`§14 Q4`, a vector can be added later under ADR-0002). The callers that send profile samples are the resolvers that compute `lang_share` (ADR-0033), through the SDK's batch call (`poster-resolver §14 Q3`).

Why: It is the plan the build sequence already follows, it uses the libraries the PRD is built on, and the shared golden corpus removes the risk of two folds drifting. Naming the callers sizes the service for its real load, and the Arabizi gap stays as F7 and lang-dialect-id planned it, sized by the pilot before any class is built.

## Consequences

CONVENTIONS L13 gains one exception; one golden corpus guards both implementations; no new field for F2 or C3; Arabizi posts are read as `en` or `und` and scored by the fallback model or left unscored in v1, a known gap measured only by the pilot's sample.

- CONVENTIONS v1.1, the language rule (v1 L13): "... and lang-dialect-id (Python, CAMeL Tools and KLPT; the fold also in TypeScript, both checked against F7's golden corpus)".
- `DEFERRED.md`: the pilot's hand-labelled `latn` sample and an Arabizi class after it (owner C3); a Kurmanji (Badini) label after the pilot (owner C3).

Sessions that must read this: F4 (the Node SDK's language client), C3, F7, F6, then C8, VLI2, A1, A4.
