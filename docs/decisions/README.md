# Decisions

Architecture decision records from `build-plan/templates/ADR.md`, one decision each
(`ADR-<nnnn>-<slug>.md`, with an "Applies to" line), and `DEFERRED.md` for the open questions not
decided yet, each with the session that must settle it. D2 writes the first set
(`/decide-session D2`); later sessions add ADRs for the PRD section 14 questions they settle. A plan
session reads the ADRs whose "Applies to" line names its session ID, service, platform, lane or "all", or whose "Sessions that must read this" line names it (ADR-0001), and the rows of `DEFERRED.md` that name it. Every session an ADR names in "Sessions that must read this" is also reached by its "Applies to" line, by ID, service, platform, lane or "all", or, for F4 to F6, by `listening-sdk`, the SDK they build.
