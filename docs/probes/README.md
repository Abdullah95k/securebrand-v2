# Probes

One report per platform or vendor, `docs/probes/<platform>.md`, written by
`/probe-platform <platform> <cap>` from `build-plan/templates/PROBE-REPORT.md`: the call shapes it
recorded, every PRD assumption marked confirmed, different or not tested, and the differences that
need a PRD answer. Its scrubbed fixtures go to `fixtures/<platform>/` and its code to
`tools/probes/<platform>/`.
