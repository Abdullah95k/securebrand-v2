"""Generate the kit's build-plan files (session briefs, SESSIONS.md, GATES.md) from sessions.py.

Usage: python3 gen_briefs.py <kit root> <prd_index.json> <prd_io.json>
Run it again whenever sessions.py changes, so the briefs and the plan's tables stay identical.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sessions import SESSIONS, BY_ID, WAVES, SIZE

KIT = sys.argv[1]
PRD = json.load(open(sys.argv[2]))
IO = json.load(open(sys.argv[3]))
OUT = os.path.join(KIT, 'build-plan')
ORDER = {s['id']: n for n, s in enumerate(SESSIONS)}

def slug(text):
    t = re.sub(r'\(.*?\)', '', text).lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return t[:48].strip('-')

def brief_name(s):
    base = s['services'][0] if s['services'] else slug(s['title'])
    return f"{s['id']}-{base}.md"

# ---------- facts per service ----------
FOLDER_PLATFORM = {'facebook': 'Facebook', 'instagram': 'Instagram', 'tiktok': 'TikTok', 'x': 'X',
                   'linkedin': 'LinkedIn', 'telegram': 'Telegram', 'youtube': 'YouTube', 'news': 'News websites',
                   'web': 'Web search', 'shared': None}
GREEN_PROBE = {'facebook': 'FB0', 'instagram': 'FB0', 'youtube': 'YT0', 'x': 'X0', 'linkedin': 'LI0',
               'telegram': 'TG0', 'tiktok': 'TT0', 'news': 'N0', 'web': 'W0'}
AMBER_PROBE = {'facebook': 'VFB0', 'instagram': 'VIG0', 'tiktok': 'VTT0', 'linkedin': 'VLI0', 'telegram': 'VTG0'}
PROBE_ARG = {'N0': 'news', 'W0': 'web', 'FB0': 'meta', 'YT0': 'youtube', 'X0': 'x', 'LI0': 'linkedin',
             'TG0': 'telegram', 'TT0': 'tiktok', 'VFB0': 'fb-vendor', 'VIG0': 'ig-vendor', 'VTT0': 'tt-vendor',
             'VLI0': 'li-vendor', 'VTG0': 'tg-vendor'}
PROBE_FIXTURES = {'news': ['fixtures/news/'], 'web': ['fixtures/web/'], 'meta': ['fixtures/facebook/', 'fixtures/instagram/'],
                  'youtube': ['fixtures/youtube/'], 'x': ['fixtures/x/'], 'linkedin': ['fixtures/linkedin/'],
                  'telegram': ['fixtures/telegram/'], 'tiktok': ['fixtures/tiktok/'],
                  'fb-vendor': ['fixtures/facebook-vendor/'], 'ig-vendor': ['fixtures/instagram-vendor/'],
                  'tt-vendor': ['fixtures/tiktok-vendor/'], 'li-vendor': ['fixtures/linkedin-vendor/'],
                  'tg-vendor': ['fixtures/telegram-vendor/']}
CAPS = {
    'N0': 'at most 10 requests per site; one connection per host, 2 to 5 s apart',
    'W0': 'at most 30 Perplexity requests (about USD 0.15), 30 Mojeek queries, GDELT at 1 request per 5 s',
    'FB0': 'at most 300 Graph API calls, development mode, team accounts and test Pages only',
    'YT0': 'at most 2,000 quota units, of which at most 10 search.list calls',
    'X0': 'at most 2,000 post reads and 200 user reads (about USD 12 at list price)',
    'LI0': 'at most 200 calls, on your own test Page only',
    'TG0': 'your own test channel and its discussion group only',
    'TT0': 'at most 100 calls, sandbox accounts only',
    'VFB0': 'at most USD 5', 'VIG0': 'at most USD 5', 'VTT0': 'at most USD 5', 'VLI0': 'at most USD 5', 'VTG0': 'at most USD 5',
}

PROBE_SHEET = {'N0': 'News websites', 'W0': 'Web search', 'FB0': 'Facebook and Instagram', 'YT0': 'YouTube', 'X0': 'X',
               'LI0': 'LinkedIn', 'TG0': 'Telegram', 'TT0': 'TikTok', 'VFB0': 'Facebook', 'VIG0': 'Instagram',
               'VTT0': 'TikTok', 'VLI0': 'LinkedIn', 'VTG0': 'Telegram'}
GIVE_REWRITE = [
    ('INVENTORY.md and CONFLICTS.md', '`docs/contracts/INVENTORY.md` and `docs/contracts/CONFLICTS.md`'),
    ('INVENTORY.md (tables)', '`docs/contracts/INVENTORY.md` (tables)'),
    ('the foundation choices list (section 2)', 'the foundation choices table in `build-plan/README.md`'),
    ('(section 2)', '(the approvals table in `build-plan/README.md`)'),
    ('README decisions 1 to 9', 'the nine proposed decisions in `docs/prds/README.md`'),
    ('all 86 PRDs', 'all 86 PRDs in `docs/prds/`'),
    ('OPEN-QUESTIONS.md', '`docs/prds/OPEN-QUESTIONS.md`'),
]
GIVE_SKIP = {'the adrs', 'conventions v1.1', 'conventions.md'}

def rewrite_give(g):
    if g == 'INVENTORY.md': return '`docs/contracts/INVENTORY.md`'
    for a, b in GIVE_REWRITE:
        g = g.replace(a, b)
    return g

def tick_path(item):
    head, _, tail = item.partition(' ')
    if '/' in head and not head.startswith('`'):
        return f'`{head}`' + (' ' + tail if tail else '')
    return item

BASE_SECTIONS = ['Naming, repository, deployment', 'Idempotency and deduplication', 'Error handling, canaries and fallback',
                 'Observability and SLOs', 'Security and compliance in every service', 'Addendum: Other shared decisions']
LANE_SECTIONS = {
    'Fetch posts': ['The registry', 'Rotation policy', 'Quotas, budgets and the quota governor', 'Retention classes'],
    'Comments': ['Rotation policy (the comments part)', 'Addendum: Comment series profiles', 'Quotas, budgets and the quota governor', 'Retention classes'],
    'Comments and stats': ['Rotation policy (comments and metrics)', 'Addendum: Comment series profiles', 'Quotas, budgets and the quota governor', 'Retention classes'],
    'Discover and qualify': ['The registry', 'Qualifier rules', 'Quotas, budgets and the quota governor'],
    'Processing': ['The registry', 'Retention classes'],
    'Registry': ['The registry', 'Rotation policy', 'Qualifier rules', 'Quotas, budgets and the quota governor'],
    'Support': ['The registry', 'Retention classes', 'Quotas, budgets and the quota governor'],
}
KIND_SECTIONS = {
    'decision': ['the whole file'], 'spec': ['the whole file'],
    'gate': ['Rotation policy', 'Observability and SLOs', 'Retention classes', 'Security and compliance in every service'],
    'probe': ['Quotas, budgets and the quota governor', 'Security and compliance in every service', 'the platform fact sheet'],
    'app': ['Naming, repository, deployment', 'Retention classes', 'Security and compliance in every service'],
    'data': ['Security and compliance in every service'],
    'infra': ['Naming, repository, deployment', 'Observability and SLOs', 'Security and compliance in every service'],
}
FOUNDATION_SECTIONS = {
    'F1': ['Naming, repository, deployment'],
    'F2': ['the whole file'], 'F3': ['the whole file'],
    'F4': ['Naming, repository, deployment', 'Idempotency and deduplication', 'Error handling, canaries and fallback', 'Observability and SLOs', 'Security and compliance in every service'],
    'F5': ['Rotation policy', 'Quotas, budgets and the quota governor', 'Error handling, canaries and fallback', 'Addendum: Other shared decisions'],
    'F6': ['Idempotency and deduplication', 'Error handling, canaries and fallback', 'Observability and SLOs'],
    'F7': ['Naming, repository, deployment'],
    'F8': ['Naming, repository, deployment (analytics store)', 'Retention classes'],
    'C0': ['Rotation policy', 'Idempotency and deduplication', 'Error handling, canaries and fallback', 'Addendum: Comment series profiles', 'Addendum: Other shared decisions'],
}

LANE_TRAPS = {
    'Fetch posts': ['The due time is next_due_at in this service\'s own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)',
                    'Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator',
                    'The cursor advances only after the producer acknowledges the batch'],
    'Comments': ['Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own',
                 'Return new_count, seen_count, pages, cost_units and reply_candidates to the SDK job wrapper, which reports them on jobs.completed; the scheduler decides early stop and extension from them (ADR-0017, ADR-0019)',
                 'Compare with the stored set through the SDK comment-state helper: an edit is a new version where the platform gives comment ids, a new comment otherwise; a missing comment is a deletion (platform_sync) only after a confirmed second miss or a platform signal, never on a route whose reads are not complete listings (ADR-0009, ADR-0046, ADR-0062)'],
    'Comments and stats': ['Only comment-decay-scheduler emits these jobs; report counts on every job'],
    'Discover and qualify': ['Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream',
                             'Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed'],
    'Processing': ['Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version'],
    'Registry': ['registry-writer is the only writer of the registry\'s identity and policy columns and of source.events; each operational column has one named owner (ADR-0013, ADR-0014)'],
    'Support': ['Deletion and retention actions are audited before they run, so a replay changes nothing'],
}

def lane_of(svc):
    m = re.search(r'\*\*Lane:\*\*\s*([^·*]+)', PRD[svc]['header'])
    return m.group(1).strip() if m else None

def route_of(svc):
    h = PRD[svc]['header']
    return 'amber' if 'amber' in h.split('**Lane')[0] else ('green' if 'green' in h else 'shared')

def folder_of(svc):
    return PRD[svc]['path'].split('/')[0]

def handoff(i):
    return f"docs/handoffs/{i}.md"

def fmt_list(items):
    return '\n'.join(f'- {x}' for x in items) if items else '- None'

def sections_for(s):
    if s['id'] in FOUNDATION_SECTIONS: return FOUNDATION_SECTIONS[s['id']]
    if s['services']:
        lane = lane_of(s['services'][0])
        secs = BASE_SECTIONS + LANE_SECTIONS.get(lane, [])
        plat = FOLDER_PLATFORM.get(folder_of(s['services'][0]))
        if plat: secs = secs + [f'Per-platform fact sheets: {plat}']
        return secs
    secs = KIND_SECTIONS.get(s['kind'], BASE_SECTIONS)
    if s['kind'] == 'probe':
        secs = [x if x != 'the platform fact sheet' else f"Per-platform fact sheets: {PROBE_SHEET[s['id']]}" for x in secs]
    return secs

def contracts_block(svc):
    io = IO[svc]
    rows = []
    rows.append(f"- Topics read: {', '.join(f'`{t}`' for t in io['reads_topics']) or 'none named in 6.1'}")
    rows.append(f"- Topics written: {', '.join(f'`{t}`' for t in io['writes_topics']) or 'none named in 6.2'}")
    if io['jobs_in'] or io['jobs_out']:
        rows.append(f"- Job queues in: {', '.join(f'`{j}`' for j in io['jobs_in']) or 'its own `jobs.' + svc + '`'}; out: {', '.join(f'`{j}`' for j in io['jobs_out']) or 'none'}")
    else:
        rows.append(f"- Job queue: `jobs.{svc}` if the PRD's section 5.1 schedules jobs")
    rows.append(f"- Tables read: {', '.join(f'`{t}`' for t in io['reads_tables']) or 'see 6.1'}; written or updated: {', '.join(f'`{t}`' for t in io['writes_tables']) or 'see 6.2 and 6.3'}")
    rows.append('- This list is extracted from the PRD\'s section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.')
    return '\n'.join(rows)

def prompts_block(s):
    i = s['id']
    if s['kind'] == 'probe':
        arg = PROBE_ARG[i]
        return (f"- Start: `claude --worktree {i} --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)\n"
                f"- Run: `/probe-platform {arg} {CAPS[i]}`\n"
                f"- Review: a fresh session (`claude --worktree {i}`) checks the scrubbing test and the report against the brief; then merge")
    if s['kind'] == 'gate':
        g = 'G3-<platform>' if i == 'G3' else i
        return f"- Start: a fresh session on an up-to-date main: `git pull`, then `claude`\n- Run: `/integration-gate {g}`"
    if i in ('D1', 'D2', 'D3'):
        return (f"- Start: `claude --worktree {i}` (it writes documents, so not plan mode)\n"
                f"- Run: `/decide-session {i}`\n"
                f"- Review: read every file it produced yourself before merging{'; the decisions are yours' if i == 'D2' else ', then ask a fresh session to check them against the PRDs'}")
    env = 'ALLOW_CONTRACT_EDITS=1 ' if i in ('F2', 'F3', 'F8') else ''
    if s['kind'] == 'infra':
        approve = 'approve with "Yes, manually approve edits" so you review every command and change'
        mode = 'Manual mode'
    else:
        approve = 'approve with auto mode or accept-edits'
        mode = 'the mode you approved with'
    return (f"- Plan: `{env}claude --worktree {i} --permission-mode plan`, then `/plan-session {i}`; read the plan (Ctrl+G), {approve}\n"
            f"- Build: `/clear`, then `/build-session {i}` ({mode}); optionally keep it going with `/goal` (see `build-plan/README.md`)\n"
            f"- Review: a new terminal, `claude --worktree {i}`, then `/review-session {i}`\n"
            f"- Fix: `{env}claude --worktree {i}` (or the build terminal), `/fix-session {i}`; then a fresh session runs `/review-session {i} recheck`; merge when the review has no open blocker or should-fix")

def dod_block(s):
    lines = ['The definition of done in `build-plan/README.md` holds.'] if s['kind'] in ('service', 'core', 'foundation', 'app', 'infra') else []
    if s['id'] == 'E1':
        lines.append('Every G1 check in `build-plan/GATES.md` has a scenario, and `make e2e GATE=G1` runs them all from a clean `make up`.')
    if s['id'] == 'E2':
        lines.append('Every G2, G3 and G4 check in `build-plan/GATES.md` has a script or query in `tools/gates/`, and a dry run against staging produces a report.')
    k = s['kind']
    if k == 'probe':
        lines += ['Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.',
                  'Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.',
                  f"Spend stayed under the cap ({CAPS[s['id']]}).", 'Each difference is listed as a question for its PRD.']
    elif k == 'gate':
        lines += [f"`docs/gates/{s['id'] if s['id'] != 'G3' else 'G3-<platform>'}.md` shows every check in `build-plan/GATES.md` with evidence.",
                  'Each failure names its failing command and the session that owns it.']
    elif k == 'foundation':
        lines += ['The package README shows a service using it, with a runnable example.', 'Conformance or golden tests named in this brief pass in every language involved.']
    elif k == 'decision':
        lines += ['Every deliverable listed under "Hands on" exists and you have read it.']
    elif k == 'spec':
        lines += ['Each PRD follows the 14-section template with testable acceptance criteria, and is consistent with every PRD that names it in section 4.']
    elif k == 'app':
        lines += ['Screens checked in a browser against the PRD; a test proves a user never sees another client\'s data.']
    elif k == 'data':
        lines += ['Code done (merge): the guide is versioned; the sampling, export, agreement and evaluation tools are merged with tests.',
                  'Data done (before A1): at least 2,000 items labelled, agreement measured and reported, splits frozen and versioned.']
    elif k == 'infra':
        lines += ['Everything is in `infra/` as code; a deploy, a rollback and a restore were each rehearsed on staging.']
    return fmt_list(lines)

def brief(s):
    i = s['id']
    L = []
    L.append(f"# {i} · {s['title']}")
    L.append('')
    L.append(f"{WAVES[s['wave']]} · track {s['track']} · size {s['size']} ({SIZE[s['size']]}) · kind {s['kind']}{' · on the critical path' if s['critical'] else ''}")
    L.append('')
    L.append('## Builds')
    L.append('')
    L.append(s['builds'] + '.')
    if s['services']:
        for svc in s['services']:
            p = PRD[svc]; io = IO[svc]
            L.append('')
            L.append(f"Service `{svc}` · PRD `docs/prds/{p['path']}` · lane {lane_of(svc)} · route {route_of(svc)} · {io['ac']} acceptance criteria (section 13) · {io['oq']} open questions (section 14)")
    L.append('')
    L.append('## Needs first (merged, with a closed review)')
    L.append('')
    if s['needs']:
        for n in s['needs']:
            d = BY_ID[n]
            if d['kind'] == 'gate':
                L.append(f"- {n} {d['title']}: `docs/gates/{n}.md` is green")
            else:
                L.append(f"- {n} {d['title']}: `{handoff(n)}`")
    else:
        L.append('- Nothing. This session can start on day one.')
    if s['anytime'] or s['deadline']:
        L.append('')
        L.append(f"Any-time track: earliest {s['anytime'] or 'when the above are met'}; deadline {s['deadline'] or 'none'}.")
    L.append('')
    L.append('## Give the session (read in this order)')
    L.append('')
    items = ['This brief']
    if s['services']:
        for svc in s['services']:
            items.append(f"The PRD in full: `docs/prds/{PRD[svc]['path']}`")
    items.append('CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: ' + '; '.join(sections_for(s)))
    items.append('The ADRs in `docs/decisions/` whose "Applies to" line names this session\'s service, platform, lane or "all"')
    for n in s['needs']:
        if BY_ID[n]['kind'] != 'gate':
            items.append(f"Handoff of {n}: `{handoff(n)}`")
    if s['services'] and s['kind'] == 'service':
        svc = s['services'][0]; folder = folder_of(svc)
        if folder in GREEN_PROBE:
            probe = AMBER_PROBE.get(folder) if route_of(svc) == 'amber' else GREEN_PROBE[folder]
            arg = PROBE_ARG[probe]
            fxs = PROBE_FIXTURES[arg]
            if arg == 'meta': fxs = [f'fixtures/{folder}/']
            fx = ', '.join(f'`{f}`' for f in fxs)
            items.append(f"The {probe} probe report `docs/probes/{arg}.md` and the fixtures in {fx}")
            items.append('`docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)')
    for g in s['give']:
        if g.strip().lower() in GIVE_SKIP: continue
        g = rewrite_give(g)
        items.append(g[0].upper() + g[1:])
    for n, it in enumerate(items, 1):
        L.append(f"{n}. {it}")
    if s['services']:
        L.append('')
        L.append('## Contracts it touches (from PRD section 6)')
        L.append('')
        L.append(contracts_block(s['services'][0]))
    L.append('')
    L.append('## Hands on')
    L.append('')
    hands = []
    if s['services']:
        hands.append(f"Code and tests in `services/{s['services'][0]}/`")
    if s['kind'] not in ('gate',):
        hands.append(f"`{handoff(i)}` from `build-plan/templates/HANDOFF.md`")
    if s['kind'] not in ('gate', 'decision', 'spec', 'data') or i == 'A0':
        hands.append(f"`docs/reviews/{i}.md` from the fresh-session review")
    if s['kind'] == 'probe':
        arg = PROBE_ARG[i]
        hands += [f"`docs/probes/{arg}.md`"] + [f"Scrubbed fixtures in `{f}`" for f in PROBE_FIXTURES[arg]] + [f"The probe script and its scrubbing test in `tools/probes/{arg}/`"]
    hands += [tick_path(p) for p in s['produces'] if not (s['kind'] == 'probe' and (p.startswith('docs/probes') or p.startswith('fixtures/')))]
    L.append(fmt_list(hands))
    L.append('')
    L.append('## Watch for')
    L.append('')
    traps = list(s['traps'])
    if s['services']:
        traps += LANE_TRAPS.get(lane_of(s['services'][0]), [])
        if route_of(s['services'][0]) == 'amber':
            traps.append('Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a source a government client watches or a client-owned property never falls back to it (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor\'s factor (ADR-0057)')
    if s['kind'] == 'probe':
        traps.append(f"Cap: {CAPS[i]}")
        traps.append('Scrub before anything is committed: tokens, signed URLs, private individuals\' names, handles, ids and avatars')
    if i in ('F2', 'F3', 'F8'):
        traps.append('Start this session with ALLOW_CONTRACT_EDITS=1: it is one of the few allowed to write the contract paths')
    L.append(fmt_list(traps) if traps else '- Nothing beyond this brief and its PRD.')
    L.append('')
    L.append('## Done when')
    L.append('')
    L.append(dod_block(s))
    L.append('')
    L.append('## Runs alongside')
    L.append('')
    al = sorted(s['alongside'], key=lambda a: ORDER.get(a, 10**6))
    any_time = s['anytime'] or s['kind'] in ('probe', 'infra', 'spec', 'data')
    al = [x.replace('the external applications in section 2', 'the day-one approval applications (see the approvals table in `build-plan/README.md`)') for x in al]
    L.append(', '.join(al) if al else ('Any session (any-time track)' if any_time else 'Nothing in particular; see the wave table'))
    if s['human']:
        L.append('')
        L.append('## Your part')
        L.append('')
        L.append(s['human'] + '.')
    L.append('')
    L.append('## How to run it')
    L.append('')
    L.append(prompts_block(s))
    L.append('')
    return '\n'.join(L)

os.makedirs(os.path.join(OUT, 'sessions'), exist_ok=True)
for s in SESSIONS:
    open(os.path.join(OUT, 'sessions', brief_name(s)), 'w').write(brief(s))

# ---------- SESSIONS.md ----------
S = ['# All sessions', '',
     'Tick a session when its pull request has merged with a closed review. "Needs first" is the hard rule; waves are the recommended order.', '']
for w in sorted(WAVES):
    S.append(f'## {WAVES[w]}')
    S.append('')
    S.append('| Done | Session | Builds | Needs first | Size | Brief |')
    S.append('|---|---|---|---|---|---|')
    for s in SESSIONS:
        if s['wave'] != w: continue
        name = f"`{s['services'][0]}`" if s['services'] else s['title']
        S.append(f"| [ ] | **{s['id']}** | {name} | {', '.join(s['needs']) or 'nothing'} | {s['size']} | [brief](sessions/{brief_name(s)}) |")
    S.append('')
open(os.path.join(OUT, 'SESSIONS.md'), 'w').write('\n'.join(S))
print('briefs', len(SESSIONS))
