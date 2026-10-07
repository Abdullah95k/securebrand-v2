# Probes

The only code allowed to call real platforms, one folder per platform or vendor
(`tools/probes/<platform>/`), written by `/probe-platform <platform> <cap>` and run only in probe
sessions, under the call or spend cap in the brief. Each probe folder is a workspace (pnpm, or a uv
project) whose `test` script runs its scrubbing test, which never touches the network: `make check`
runs it. The probe itself is never a test. Scrubbed fixtures go to `fixtures/<platform>/`.
