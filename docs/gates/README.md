# Gates

One report per gate, `docs/gates/<gate>.md` (G0, G1, G2, `G3-<platform>`, G4), written by
`/integration-gate <gate>`: a summary line, then one row per check of `build-plan/GATES.md` with its
command, an output excerpt and pass or fail. E1 builds the G1 suite (`make e2e GATE=G1`) and E2 the
scripts for G2 to G4 (`tools/gates/`).
