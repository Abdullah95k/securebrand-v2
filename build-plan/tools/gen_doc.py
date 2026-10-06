"""Print the plan document's wave tables from sessions.py (writes doc_s4.md ... doc_s11.md into the output directory).

Usage: python3 gen_doc.py [output directory]
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else '.'
from sessions import SESSIONS, BY_ID

DOC_SHORT = {
 'D1': 'Inventory of every topic, job queue, table, column, budget tag, flag and retention class in the 86 PRDs, and every conflict between them',
 'D3': 'PRDs for the query API, client portal (OAuth connect, keywords and sources, review queue, provenance, deletion requests), dashboard (with the App Review slice) and admin console',
 'F1': 'pnpm and Turborepo monorepo, TypeScript strict, Vitest, uv with ruff and pytest, docker compose (Redpanda, Supabase, ClickHouse, SeaweedFS), CI; fits the kit\'s check script, make targets and hooks to the toolchain',
 'F2': 'Zod schemas for every topic, job and envelope; JSON Schema and Pydantic exports; fixtures; key and item_id derivation with golden vectors; TypeScript and Python conformance tests',
 'F4': 'listening-sdk core: producer and consumer keyed by source_id, envelope validation, job wrapper with retries and DLQ, cursor after ack, jobs.completed, logs, metrics, health, Vault config, service generator',
 'F5': 'Rotation scheduler with leader election, quota client, HTTP adapter base with the error policy, canary hook, per-host gate, fake clock, scriptable fake platform',
 'F7': 'The Arabic and Sorani folds in TypeScript exactly as lang-dialect-id 5.3 C defines them, and a golden corpus both languages must pass',
 'F8': 'ClickHouse migrations for items, comments, analysis, metrics, aggregates, dimensions and hits; month partitions; TTL by retention class; text index',
 'I1': 'Hetzner servers, cluster, Redpanda, ClickHouse, buckets, TLS ingress for webhooks, image registry, deploy pipeline, backups',
}
DOC_GIVE = {
 'F4': 'CONVENTIONS idempotency, errors and observability sections; ADRs on the Kafka client and jobs.completed; fb-page-feed-poller as the reference consumer',
 'F5': 'fb-page-feed-poller 5.1; quota-governor 6; source-health-canary 5; news-robots-checker (host gate); CONVENTIONS rotation and errors',
 'I1': 'Cluster and storage ADRs; the list of public webhook endpoints (Facebook, Instagram, LinkedIn, Telegram, YouTube hub)',
 'D3': 'CONVENTIONS v1.1; the Meta, LinkedIn and TikTok review requirements (section 2); every PRD\'s section 4',
}

def name_cell(s):
    if s['services']:
        nm = s['services'][0]
        return f"**{s['id']}** `{nm}` ({s['size']})"
    return f"**{s['id']}** {s['title']} ({s['size']})"

def builds_cell(s):
    b = DOC_SHORT.get(s['id'], s['builds'])
    return b

def give_cell(s):
    if s['id'] in DOC_GIVE: return DOC_GIVE[s['id']]
    if not s['give']: return 'Standard set'
    return '; '.join(s['give'])

def needs_cell(s):
    return ', '.join(s['needs']) if s['needs'] else 'Nothing'

ALONG_OVERRIDE = {k: 'any session' for k in ['D3', 'I1', 'I2', 'N0', 'W0', 'FB0', 'YT0', 'X0', 'LI0', 'TG0', 'TT0', 'A0', 'E2']}
def along_cell(s):
    if s['id'] in ALONG_OVERRIDE: return ALONG_OVERRIDE[s['id']]
    order = {x['id']: n for n, x in enumerate(SESSIONS)}
    al = sorted(s['alongside'], key=lambda a: order.get(a, 10**6))
    return ', '.join(al) if al else '—'

def table(ids):
    rows = ['| Session | Builds | Needs first | Give it | Alongside |', '|---|---|---|---|---|']
    for i in ids:
        s = BY_ID[i]
        cells = [name_cell(s), builds_cell(s), needs_cell(s), give_cell(s), along_cell(s)]
        for c in cells: assert '|' not in c, (i, c)
        rows.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(rows)

def ids(track=None, wave=None, prefix=None):
    out = []
    for s in SESSIONS:
        if wave is not None and s['wave'] != wave: continue
        if track is not None and s['track'] != track: continue
        if prefix is not None and not s['id'].startswith(prefix): continue
        if s['kind'] == 'gate': continue
        out.append(s['id'])
    return out

sections = {}

sections['s4'] = "\n\n".join([
"## Waves 0 and 1: decide, then lay the foundation",
"Day one starts two sessions in parallel, D1 (the inventory) and F1 (the repository), while the external applications from the previous section go out. D2 needs you for a whole session. Once D2 closes, the contracts, the control-plane schema and the text fold run in parallel; the SDK waits for the contracts and the schema; the scheduling kit and the Python twin follow the SDK. Nothing in Wave 2 starts until gate G0 is green (see \"Quality gates\").",
"### Wave 0 · Decide and freeze (no service code)",
table(['D1', 'D2', 'D3']),
"D3 is in the any-time track: it only has to land before Q1 in Wave 3, but writing it early lets the Meta review build start without waiting on a spec.",
"### Wave 1 · Foundation",
table(['F1', 'F2', 'F3', 'F7', 'F8', 'F4', 'F5', 'F6', 'I1', 'I2']),
"The foundation is where quality is cheapest to buy: every later session inherits these packages. Give F2, F3, F4 and F5 the most capable model you have, plan each one in plan mode, and read their plans yourself before approving. I1 and I2 can run whenever you have a free slot, as long as they land before G2.",
])

sections['s5'] = "\n\n".join([
"## Wave 2: the shared core",
"Sixteen sessions in four batches of three or four, then E1. C0 comes first in batch A: it builds a reference poller, comments fetcher, resolver and search against the fake platform, using every SDK feature once, so every later platform session copies a pattern that has already passed review. The core services talk only through contracts, so a batch waits for the previous batch's merged contracts and handoffs, never for its internals. E1 then builds the end-to-end suite that gate G1 runs on the fake platform.",
"- **Batch A:** C0, C1, C2, C7 (C3 can join if you have a fourth slot)\n- **Batch B:** C3, C4, C5, C6\n- **Batch C:** C8, C9, C10, C11\n- **Batch D:** C12, C13, C14, C15\n- **Then:** E1, the G1 suite",
table(['C0', 'C1', 'C2', 'C7', 'C3', 'C4', 'C5', 'C6', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'E1']),
"normalize-item (C4) ships with the fake platform's mapper only. Every platform's first session that emits a new record shape adds its own mapper under `services/normalize-item/src/mappers/<platform>/` with fixture tests; that is the one cross-service edit a session may make, and its handoff must list it.",
])

sections['s6'] = "\n\n".join([
"## Wave 3: first real data, and the Meta review build",
"Three tracks in parallel, each opening with a probe, plus E2, which builds the tooling the next gates run. News and web prove the whole pipeline on real Iraqi data without any platform approval. The Meta track builds just enough Facebook to put real Page analytics in front of Meta's reviewers: submit App Review the day U1 merges. G2 then soaks news and web on staging for 72 hours.",
"Every platform session also gets its platform's probe report and fixtures and `docs/patterns/ADAPTER-PATTERN.md` from C0, in addition to the standard set.",
"### News",
table(ids(track='News')),
"### Web search",
table(ids(track='Web')),
"### Meta review build",
table(['FB0', 'FB1', 'FB2', 'Q1', 'U1']),
"### Gate tooling",
table(['E2']),
"Gate sessions only run and report, so whatever a gate checks has to be built first: E1 builds the G1 suite, and E2 the scripts for G2, G3 and G4. Each platform's go-live session fills in its own compliance check in E2's scripts.",
"U1 is not a demo built for show: it is the first slice of the real dashboard, on the real query API, which is why it comes after Q1 and why Meta's reviewers can be shown the same screens your clients will use.",
])

sections['s7'] = "\n\n".join([
"## Wave 4: YouTube, X, and Facebook in development mode",
"YouTube and X run as two tracks while Facebook keeps building in development mode during the review. Two hard deadlines: yt-text-purger (YT7) and x-compliance-sync (X7) must be merged before their platform's real data reaches staging, because YouTube's 30-day rule and X's 24-hour deletion mirroring apply to staging data as much as to production. Each platform passes its own G3 go-live gate before clients see its data.",
"### YouTube",
table(ids(track='YouTube')),
"### X",
table(ids(track='X')),
"### Facebook, continued in development mode",
table(['FB3', 'FB4', 'FB5', 'FB6']),
])

sections['s8'] = "\n\n".join([
"## Wave 5: approval-gated platforms and the client portal",
"The client portal comes first: its OAuth flows are what LinkedIn's Standard-tier review and TikTok's app review must see, and client-owned Facebook Pages and Instagram accounts connect through it. Facebook's webhook receiver and the Instagram track move to production when Meta approves. LinkedIn, Telegram and TikTok Display are green only for accounts your clients own or administer. The tracks below run alongside each other; inside a track, follow the order.",
"### Client portal and Facebook webhooks",
table(['U2', 'FB7']),
"### Instagram",
table(ids(track='Instagram')),
"### LinkedIn",
table(ids(track='LinkedIn', wave=5)),
"### Telegram",
table(ids(track='Telegram', wave=5)),
"### TikTok Display",
table(ids(track='TikTok', wave=5)),
"Once U2 merges, record LinkedIn's narrated screen recording (full OAuth flow and each use case) and TikTok's demo video (every scope shown) from the staging portal and submit both reviews.",
])

sections['s9'] = "\n\n".join([
"## Wave 6: the insight layer",
"Analysis quality is decided by the evaluation set, not by the model, so A0 comes before any model work: an annotation guide, at least 2,000 labelled Iraqi items with agreement scores, and an evaluation harness. The four analysis services then run in parallel, each measured against the same held-out test split. alert-evaluator can be built any time after the aggregator and keyword-matcher.",
table(['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'U3']),
"The FlutterFlow mobile app is built outside Claude Code against the query API (Q1); give its builder the query-api PRD and the staging endpoint.",
])

amber_rows = [s['id'] for s in SESSIONS if s['wave'] == 7]
sections['s10'] = "\n\n".join([
"## Wave 7: amber vendor routes (optional)",
"Amber is optional and starts only after three things: the vendor decision (business case per route), verification of the vendor's owners against the vendor screen (several vendors are only weakly cleared), and G2. Each vendor is a short track: a probe under a spending cap, then its services. Every amber service is behind its flag (off by default), carries `route = amber` and the vendor in provenance, and is excluded from government contracts. Vendor tracks run alongside each other; inside a track, sessions that share the same \"Needs first\" can run in parallel (for example VFB1 and VFB2 after VFB0).",
"What decides each vendor:\n\n- **Coverage you cannot get green:** third-party TikTok, Facebook groups and keyword search, Instagram comments on non-client media, LinkedIn company pages you do not administer, Telegram channels that have not added your bot.\n- **Owner verification:** ScrapeCreators, SociaVault and TikHub are weakly cleared (country known, owners not verified). Verify before signing.\n- **Contract terms:** retention under `vendor_agreed` needs the vendor's terms and your author notice; counsel signs off.\n- **Cost under the quota governor:** each vendor's monthly budget, with the 80% stretch rule.",
table(amber_rows),
])

anytime = [s for s in SESSIONS if s['anytime'] or s['deadline']]
rows = ['| Session | Earliest start | Deadline |', '|---|---|---|']
for s in anytime:
    nm = f"**{s['id']}** " + (f"`{s['services'][0]}`" if s['services'] else s['title'])
    start = s['anytime'] or ('after ' + ', '.join(s['needs'][:-1]) + ' and ' + s['needs'][-1] if len(s['needs']) > 1 else 'after ' + s['needs'][0])
    rows.append(f"| {nm} | {start} | {s['deadline'] or 'none'} |")
extra = [
 "| Contract-change sessions | when you approve a proposal | before the sessions that need the change |",
 "| YouTube quota audit (Audit and Quota Extension form) | after YT7 is live | before daily use passes about 80% of 10,000 units |",
 "| X Enterprise | when a government client or several clients are close | before any government end user's data is collected |",
 "| Runbooks and dashboards per service | with each service's handoff | before that platform's G3 |",
]
sections['s11'] = "\n\n".join([
"## The any-time track",
"These sessions can be slotted in whenever a worktree is free. Each has an earliest start, set by its \"Needs first\", and some have a hard deadline. The deadlines on YT7 and X7 are compliance deadlines, not convenience ones: real data from those platforms must not reach staging before they merge.",
"\n".join(rows + extra),
"A good habit: keep one slot for the any-time track while the main tracks run, so probes and specs are always ahead of the sessions that need them.",
])

def fix(v):
    v = v.replace('the external applications in section 2', 'the day-one applications')
    v = v.replace('(section 2)', '("Before the first session")')
    return v
sections = {k: fix(v) for k, v in sections.items()}
for k, v in sections.items():
    open(os.path.join(OUTDIR, f'doc_{k}.md'), 'w').write(v)
    print(k, len(v.encode('utf-8')))
