# Handoffs

One file per session, `docs/handoffs/<ID>.md`, written at the end of `/build-session <ID>` (and
updated by `/fix-session <ID>`) from `build-plan/templates/HANDOFF.md`. A session reads the handoffs
of the sessions in its brief's "Needs first", never their transcripts. CI
(`scripts/policy/check-handoff-review.sh`) requires the handoff before a lane that changes code
merges.
