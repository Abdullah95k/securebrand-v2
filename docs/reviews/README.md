# Reviews

One file per session, `docs/reviews/<ID>.md`, written by `/review-session <ID>` in a fresh session
from `build-plan/templates/REVIEW.md`; `/review-session <ID> recheck` appends a "Recheck <date>"
section with the new verdict. CI (`scripts/policy/check-handoff-review.sh`) reads the latest verdict:
a lane that changes code merges only on "ready to merge".
