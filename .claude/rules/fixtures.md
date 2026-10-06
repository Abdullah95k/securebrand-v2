---
paths:
  - "fixtures/**"
  - "tools/probes/**"
---

# Fixtures and probes

- `tools/probes/` is the only code allowed to call real platforms, and only in probe sessions, under the call or spend cap in the brief.
- Fixtures are scrubbed: no tokens or signed URLs; names, handles, ids and avatars of private individuals replaced with stable fakes; ids of public Pages, channels, outlets and companies kept.
- Raw responses live only in `fixtures/<platform>/raw/`, which is gitignored and deleted once the scrubbing test passes.
- Every fixture directory has a README listing, per file, the call that produced it, the date and what was scrubbed.
- Never edit a recorded fixture by hand to make a test pass; record a new one or write a synthetic fixture and name it `synthetic-*`.
