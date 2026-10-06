---
name: integration-gate
description: Verify a build gate (G0 to G4) end to end and write its report with evidence; fixes nothing. Run when every session the gate needs has merged.
argument-hint: <G0 | G1 | G2 | G3-<platform> | G4>
disable-model-invocation: true
effort: max
---

# Gate $ARGUMENTS

Verify only. Do not change code, tests or configuration in this session.

1. Make sure you are on an up-to-date main (`git fetch origin` and `git status`; tell me if main is behind origin). Read the section for $ARGUMENTS in `build-plan/GATES.md` and its brief in `build-plan/sessions/`. Confirm that every session the gate needs has merged and has a closed review; if one has not, stop and list them.
2. Bring up the environment the gate names: `make up` for G0 and G1, staging from G2 on. Use the suites and scripts built for gates (`make e2e GATE=G1` from E1, `tools/gates/` from E2); if one is missing, the gate fails on that check.
3. Run each check in the order listed. For each, record the command or query, an excerpt of its output, and pass or fail.
4. Write `docs/gates/$ARGUMENTS.md`: a summary line (green, or N checks failing), then one row per check with its evidence.
5. For each failure: the failing command, what it shows, and the session that owns the fix. Do not attempt the fix.
6. Tell me whether the next wave may start.
