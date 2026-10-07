# End-to-end suites

One workspace per gate, `tests/e2e/<gate>/`, run by `make e2e GATE=<gate>`. E1 builds the G1 suite
here (`tests/e2e/G1`) and keeps it as the regression suite: the real core services on the local
stack, driven by the fake platform and the fake clock. A suite is a pnpm workspace whose
`package.json` has an `e2e` script (or a uv project run with pytest); `make e2e` sets the stack's
variables and the test namespace before it runs. Gates G2 to G4 run on staging from `tools/gates/`.
