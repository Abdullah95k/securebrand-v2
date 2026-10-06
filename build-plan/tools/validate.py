"""Check sessions.py: every PRD assigned once, dependencies point backwards, parallel pairs are independent."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sessions import SESSIONS, BY_ID, WAVES
prd = json.load(open(os.path.join(HERE, 'prd_index.json')))
assigned = {}
errors = []
seen = set()
for s in SESSIONS:
    if s['id'] in seen: errors.append('dup id ' + s['id'])
    seen.add(s['id'])
    for n in s['needs']:
        if n not in BY_ID: errors.append(f"{s['id']} needs unknown {n}")
        elif n not in seen: errors.append(f"{s['id']} needs {n} defined later")
        elif BY_ID[n]['wave'] > s['wave']: errors.append(f"{s['id']} (w{s['wave']}) needs {n} (w{BY_ID[n]['wave']})")
    for a in s['alongside']:
        if a in BY_ID and a in s['needs']: errors.append(f"{s['id']} alongside {a} but also needs it")
    for sv in s['services']:
        if sv not in prd: errors.append(f"{s['id']} unknown service {sv}")
        if sv in assigned: errors.append(f"{sv} assigned twice: {assigned[sv]} {s['id']}")
        assigned[sv] = s['id']
missing = sorted(set(prd) - set(assigned))
print('sessions', len(SESSIONS), 'services assigned', len(assigned), 'missing', missing)
print('errors', errors)
from collections import Counter
print(Counter(s['wave'] for s in SESSIONS))
print(Counter(s['size'] for s in SESSIONS))
print(Counter(s['kind'] for s in SESSIONS))
# alongside symmetric check (informational)
asym = []
for s in SESSIONS:
    for a in s['alongside']:
        if a in BY_ID and s['id'] not in BY_ID[a]['alongside']:
            asym.append((s['id'], a))
print('asymmetric alongside (info):', asym)
# transitive closure: does any alongside pair depend on each other transitively?
import functools
@functools.lru_cache(None)
def anc(i):
    out = set()
    for n in BY_ID[i]['needs']:
        out.add(n); out |= anc(n)
    return frozenset(out)
conf = []
for s in SESSIONS:
    for a in s['alongside']:
        if a in BY_ID and (a in anc(s['id']) or s['id'] in anc(a)):
            conf.append((s['id'], a))
print('alongside but dependent (transitively):', conf)
