#!/usr/bin/env python3
import hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'QUALIFICATION-LINEAGE.json').read_text())
errors=[]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_artifact(owner, rec):
    if rec is None: return
    p=ROOT/rec['path']
    if not p.is_file():
        errors.append(f'{owner}: missing {rec["path"]}')
        return
    got=digest(p)
    if got != rec['sha256']:
        errors.append(f'{owner}: SHA mismatch {rec["path"]}: {got} != {rec["sha256"]}')

# State-space lineage must be contiguous from v2 through current v45.
audits=DATA['state_space_audits']
versions=[a['version'] for a in audits]
if versions != list(range(2,46)):
    errors.append(f'state-space versions not contiguous 2..45: {versions}')
registered=set()
for a in audits:
    if a.get('status')!='RETAINED': errors.append(f'audit v{a["version"]}: unexpected non-retained status')
    for key in ('report','executable','recorded_output'):
        verify_artifact(f'audit v{a["version"]}',a[key]); registered.add(a[key]['path'])

# Smoke lineage.
for s in DATA['git_smokes']:
    if s.get('status')!='RETAINED': errors.append(f'smoke {s["id"]}: unexpected non-retained status')
    verify_artifact(f'smoke {s["id"]}',s['script']); registered.add(s['script']['path'])
    if s.get('recorded_output'):
        verify_artifact(f'smoke {s["id"]}',s['recorded_output']); registered.add(s['recorded_output']['path'])

# No packaged qualification executable/result may exist outside the registry.
discovered=set()
for p in ROOT.glob('state-space-audit-v*.py'): discovered.add(p.name)
for p in ROOT.glob('state-space-audit-v*.txt'): discovered.add(p.name)
for p in ROOT.glob('STATE-SPACE-AUDIT-v*.txt'): discovered.add(p.name)
for p in ROOT.glob('STATE-SPACE-AUDIT-v*.md'): discovered.add(p.name)
for p in ROOT.glob('git-*-smoke-v*.sh'): discovered.add(p.name)
for p in ROOT.glob('git-*-smoke-v*.txt'): discovered.add(p.name)
unregistered=sorted(discovered-registered)
if unregistered: errors.append('unregistered qualification artifacts: '+', '.join(unregistered))

if errors:
    print('QUALIFICATION LINEAGE: FAIL')
    for e in errors: print(' - '+e)
    sys.exit(1)
print('QUALIFICATION LINEAGE: PASS')
print(f'state-space audits retained: v{versions[0]}..v{versions[-1]} ({len(versions)})')
print(f'Git smoke scripts retained: {len(DATA["git_smokes"])}')
print(f'registered qualification artifacts: {len(registered)}')
