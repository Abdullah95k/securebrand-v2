# Handoff · F1b Kit follow-ups after D1 and D2

2026-10-25 · lane `sb/F1b` (PR Abdullah95k/securebrand-v2#12) · build session in progress

## Progress

- GHCR package securebrand-v2/clickhouse created by run 40150405619; the user must make it public.
- Done and pushed: the plan's approval (c200b75), W1 (f66cd56), W2 (fedabd4), W3 (b598adc), W4 (521a8fc), W5 (95bda8e), W6 (dc910dd), W7 (262ab37), W8 (3f44e5f), W9 (a110634). Each test was shown failing for the stated reason before its change and passing after it.
- W9: ECR Public's digest for `public.ecr.aws/docker/library/clickhouse:26.3.38.2`, read here before the push, is `sha256:ea3ff4a4aa2a097ddaa91facb6c808f5045c661b2a9fe261f25de579f6e7c6da`; the Mirror images run 40150405619 (job 121040593322, success) copied `docker.io/library/clickhouse:26.3.38.2` at the same digest.
- Next: W10 (CI runs `pnpm fmt:check`), W11 (the mirror workflow on main only), W12 (Dependabot), W13 (F1's records, the label check), then this handoff in full, `/code-review`, the checks and the CI read.
- To resume: `git fetch origin && git checkout sb/F1b`; start dockerd and run `make bootstrap` as `docs/orchestration/README.md` says (in a fresh container it stops at the uv step: `python3 -m pip install --user --upgrade 'uv==0.12.23'`, then `PATH="$HOME/.local/bin:$PATH" make bootstrap`); `make check`; `make test SERVICE=repo-checks`.
