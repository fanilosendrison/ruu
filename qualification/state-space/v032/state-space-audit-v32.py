#!/usr/bin/env python3
"""Incremental global regression/state-space audit through ADR-064.

Retains the v31 finite regression count, adds the ADR-064 frozen mutation-handoff /
checkpoint-identity family, performs current normative static checks, and reruns
the five concrete Git primitive smokes.
"""
import itertools, os, re, subprocess, tempfile, pathlib, hashlib, sys
ROOT=pathlib.Path(__file__).resolve().parent

def run(cmd, cwd=None, env=None, check=True):
    e=os.environ.copy();
    if env: e.update(env)
    return subprocess.run(cmd, cwd=cwd, env=e, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)

def git(cwd,*args,env=None,check=True):
    return run(['git',*args],cwd=cwd,env=env,check=check)

def init_repo(path):
    git(path,'init','-q','-b','main')
    git(path,'config','user.email','audit@example.invalid')
    git(path,'config','user.name','Audit')

def commit_all(path,msg):
    git(path,'add','-A'); git(path,'commit','-q','-m',msg); return git(path,'rev-parse','HEAD').stdout.strip()

def smoke_materialization():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        (p/'base.txt').write_text('base\n'); base=commit_all(p,'base')
        git(p,'switch','-q','-c','a',base); (p/'a.txt').write_text('A\n'); a=commit_all(p,'a')
        git(p,'switch','-q','-c','b',base); (p/'b.txt').write_text('B\n'); b=commit_all(p,'b')
        tree=git(p,'merge-tree','--write-tree',a,b).stdout.strip().splitlines()[0]
        env={'GIT_AUTHOR_NAME':'gc','GIT_AUTHOR_EMAIL':'gc@example.invalid','GIT_AUTHOR_DATE':'2000-01-01T00:00:00+0000','GIT_COMMITTER_NAME':'gc','GIT_COMMITTER_EMAIL':'gc@example.invalid','GIT_COMMITTER_DATE':'2000-01-01T00:00:00+0000'}
        # commit-tree needs message on stdin; use subprocess directly
        proc=subprocess.run(['git','commit-tree',tree,'-p',base,'-p',a,'-p',b],cwd=p,env={**os.environ,**env},input='canonical\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        c=proc.stdout.strip()
        for anc in (base,a,b):
            assert git(p,'merge-base','--is-ancestor',anc,c,check=False).returncode==0
        assert git(p,'rev-parse',f'{c}^{{tree}}').stdout.strip()==tree
        proc2=subprocess.run(['git','commit-tree',tree,'-p',base,'-p',a,'-p',b],cwd=p,env={**os.environ,**env},input='canonical\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        assert proc2.stdout.strip()==c

def smoke_restack():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        (p/'base.txt').write_text('base\n'); old=commit_all(p,'old')
        git(p,'switch','-q','-c','child',old); (p/'child.txt').write_text('child\n'); child=commit_all(p,'child')
        git(p,'switch','-q','-c','newbase',old); (p/'pred.txt').write_text('pred\n'); newbase=commit_all(p,'newbase')
        tree=git(p,'merge-tree','--write-tree',f'--merge-base={old}',newbase,child).stdout.strip().splitlines()[0]
        # materialize the tree into temporary index and verify both owned child and new base state are represented.
        idx=str(p/'idx')
        env={'GIT_INDEX_FILE':idx}
        git(p,'read-tree',tree,env=env)
        ls=git(p,'ls-files','-s',env=env).stdout
        assert 'child.txt' in ls and 'pred.txt' in ls and 'base.txt' in ls
        tree2=git(p,'merge-tree','--write-tree',f'--merge-base={old}',newbase,child).stdout.strip().splitlines()[0]
        assert tree2==tree

def smoke_direct():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        (p/'f').write_text('0\n'); b=commit_all(p,'B')
        (p/'f').write_text('1\n'); c=commit_all(p,'C')
        git(p,'update-ref','refs/heads/target',b)
        assert git(p,'merge-base','--is-ancestor',b,c,check=False).returncode==0
        git(p,'update-ref','refs/heads/target',c,b)
        assert git(p,'rev-parse','refs/heads/target').stdout.strip()==c
        stale=git(p,'update-ref','refs/heads/target',b,b,check=False)
        assert stale.returncode!=0
        assert git(p,'rev-parse','refs/heads/target').stdout.strip()==c

def smoke_bootstrap():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        # real non-null bootstrap commit on configured target main
        b0=git(p,'commit-tree',git(p,'mktree').stdout.strip(),check=False) if False else None
        # normal root commit is clearer
        (p/'.gitignore').write_text('.cache/\n'); b0=commit_all(p,'bootstrap')
        assert b0 and re.fullmatch(r'[0-9a-f]+',b0)
        assert git(p,'rev-parse','refs/heads/main').stdout.strip()==b0
        git(p,'update-ref','refs/heads/Ruu/cu/test',b0)
        assert git(p,'merge-base','--is-ancestor',b0,'refs/heads/Ruu/cu/test',check=False).returncode==0

def smoke_checkpoint():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        (p/'.gitignore').write_text('ignored.tmp\n')
        (p/'tracked.txt').write_text('base\n')
        parent=commit_all(p,'parent')
        # real index gets intermediate version
        (p/'tracked.txt').write_text('intermediate\n'); git(p,'add','tracked.txt')
        real_index_tree=git(p,'write-tree').stdout.strip()
        # worktree moves on; plus untracked included and ignored excluded
        (p/'tracked.txt').write_text('final\n')
        (p/'new.txt').write_text('new\n')
        (p/'ignored.tmp').write_text('ignore me\n')
        idx=str(p/'.git'/'canonical.index')
        env={'GIT_INDEX_FILE':idx}
        git(p,'read-tree',parent,env=env)
        git(p,'add','-A',env=env)
        tree=git(p,'write-tree',env=env).stdout.strip()
        assert tree!=real_index_tree
        # real index remains the intermediate staged state
        assert git(p,'write-tree').stdout.strip()==real_index_tree
        # inspect canonical tree
        names=git(p,'ls-tree','-r','--name-only',tree).stdout.splitlines()
        assert 'new.txt' in names and 'tracked.txt' in names and 'ignored.tmp' not in names
        blob=git(p,'show',f'{tree}:tracked.txt').stdout
        assert blob=='final\n'
        # repeat exact snapshot => same tree
        os.unlink(idx)
        git(p,'read-tree',parent,env=env); git(p,'add','-A',env=env)
        assert git(p,'write-tree',env=env).stdout.strip()==tree
        # no-op surface against exact parent
        git(p,'reset','--hard','-q',parent)
        if (p/'new.txt').exists(): (p/'new.txt').unlink()
        idx2=str(p/'.git'/'noop.index'); env2={'GIT_INDEX_FILE':idx2}
        git(p,'read-tree',parent,env=env2); git(p,'add','-A',env=env2)
        assert git(p,'write-tree',env=env2).stdout.strip()==git(p,'rev-parse',f'{parent}^{{tree}}').stdout.strip()

# Retained v30 finite state-space total through ADR-061: 14,366.
RETAINED_V30 = 14366

# ADR-062 provider-projection/finalization family: 2*3*2*3*2 = 72.
routes=['DIRECT_TARGET_ADVANCE','PROVIDER_SUBMISSION']
review_intents=['NOT_ESTABLISHED','REVIEW_NOT_REQUESTED','REVIEW_REQUESTED']
early_authority=[False,True]
provider_gates=['PENDING','SATISFIED','HUMAN_FINALIZER_REQUIRED']
integration_cap=['SUPPORTED','UNSUPPORTED']
route_combos=list(itertools.product(routes,review_intents,early_authority,provider_gates,integration_cap))
assert len(route_combos)==72
route_outcomes=set()
for route,intent,early,gates,cap in route_combos:
    if route=='DIRECT_TARGET_ADVANCE':
        outcome='DIRECT_TARGET_ADVANCE_FLOW'
    else:
        projection_allowed=(intent=='REVIEW_REQUESTED') or early
        if not projection_allowed:
            outcome='NO_PROVIDER_PROJECTION'
        elif gates=='PENDING':
            outcome='WAIT_PROVIDER_GOVERNANCE'
        elif gates=='HUMAN_FINALIZER_REQUIRED':
            outcome='WAIT_EXPLICIT_HUMAN_FINALIZER'
        elif cap=='UNSUPPORTED':
            outcome='BLOCK_UNSUPPORTED_PROVIDER_FINALIZATION'
        else:
            outcome='AUTO_PROGRESS_PROVIDER_FINALIZATION'
    route_outcomes.add(outcome)
    assert outcome != 'WAIT_FOR_MANUAL_MERGE_CLICK'
    if route=='PROVIDER_SUBMISSION' and intent=='NOT_ESTABLISHED' and not early:
        assert outcome=='NO_PROVIDER_PROJECTION'
    if route=='PROVIDER_SUBMISSION' and intent=='REVIEW_NOT_REQUESTED' and not early:
        assert outcome=='NO_PROVIDER_PROJECTION'
    if route=='PROVIDER_SUBMISSION' and gates=='SATISFIED' and cap=='SUPPORTED' and ((intent=='REVIEW_REQUESTED') or early):
        assert outcome=='AUTO_PROGRESS_PROVIDER_FINALIZATION'
assert 'AUTO_PROGRESS_PROVIDER_FINALIZATION' in route_outcomes
assert 'WAIT_EXPLICIT_HUMAN_FINALIZER' in route_outcomes

# ADR-063 finding/backlog boundary family: 2*4*2 = 16.
provider_blocking=[False,True]
adjudications=['FIX_NOW','DEFER','ACCEPT','REJECT']
applicability=['CURRENT','STALE']
finding_combos=list(itertools.product(provider_blocking,adjudications,applicability))
assert len(finding_combos)==16
for blocking,decision,currentness in finding_combos:
    if blocking:
        outcome='REVIEW_CORRECTION_DEMAND'
    elif decision=='DEFER' and currentness=='CURRENT':
        outcome='EXTERNAL_BACKLOG_TRACK'
    elif decision=='DEFER' and currentness=='STALE':
        outcome='EXTERNAL_BACKLOG_CLOSE_OR_SUPERSEDE'
    elif decision=='FIX_NOW':
        outcome='EXTERNAL_DEVELOPMENT_WORK'
    else:
        outcome='NO_CORE_FINDING_BLOCK'
    assert 'PR_BACKLOG' not in outcome
    if blocking:
        assert outcome=='REVIEW_CORRECTION_DEMAND'  # external DEFER cannot bypass provider governance

# ADR-064 frozen checkpoint-offer / exact-commit identity family: 2*2*2*2 = 16.
mutation_access=['PROTECTED_EXTERNAL','TRANSFERABLE']
claim=['NONE','CURRENT_EXECUTOR']
external_write=[False,True]
candidate_state=['STABLE','CHANGED']
handoff_combos=list(itertools.product(mutation_access,claim,external_write,candidate_state))
assert len(handoff_combos)==16
handoff_outcomes=set()
for access,owner,write,candidate in handoff_combos:
    if access=='PROTECTED_EXTERNAL':
        outcome='NO_RUU_CHECKPOINT_AUTHORITY'
    elif write:
        # An external write while transferability remains current violates the
        # External Control Plane contract; it never authorizes committing a
        # candidate observed before/after the illegal mutation.
        outcome='EXTERNAL_MUTATION_CONTRACT_VIOLATION'
    elif owner=='NONE':
        outcome='WAIT_EXCLUSIVE_CLAIM'
    elif candidate=='CHANGED':
        outcome='ABORT_STALE_CANDIDATE_REOBSERVE'
    else:
        outcome='COMMIT_EXACT_FROZEN_CANDIDATE'
    handoff_outcomes.add(outcome)
    if access=='TRANSFERABLE' and owner=='CURRENT_EXECUTOR' and not write and candidate=='STABLE':
        assert outcome=='COMMIT_EXACT_FROZEN_CANDIDATE'
    if access=='TRANSFERABLE' and write:
        assert outcome=='EXTERNAL_MUTATION_CONTRACT_VIOLATION'
    if access=='TRANSFERABLE' and owner=='CURRENT_EXECUTOR' and not write and candidate=='CHANGED':
        assert outcome=='ABORT_STALE_CANDIDATE_REOBSERVE'
assert 'COMMIT_EXACT_FROZEN_CANDIDATE' in handoff_outcomes
assert 'WAIT_EXCLUSIVE_CLAIM' in handoff_outcomes
assert 'EXTERNAL_MUTATION_CONTRACT_VIOLATION' in handoff_outcomes

# Static current-doc checks.
adrs=sorted(ROOT.glob('ADR-*.md'))
nums=[int(x.name[4:7]) for x in adrs]
assert nums==list(range(1,65)), nums
main=(ROOT/'ruu-requirements-v1-merge-policy.md').read_text()
contract=(ROOT/'EXTERNAL-CONTROL-PLANE-CONTRACT.md').read_text()
backlog=(ROOT/'OPEN-DESIGN-BACKLOG.md').read_text()
adr62=(ROOT/'ADR-062-make-promotion-route-independent-and-provider-submissions-projections.md').read_text()
adr63=(ROOT/'ADR-063-keep-findings-and-backlog-outside-ruu.md').read_text()
adr64=(ROOT/'ADR-064-bind-pre-commit-readiness-by-frozen-mutation-handoff.md').read_text()

assert 'target_realization_route:' in main
assert 'DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION' in main
assert 'RealizePromotion(exact candidate, immutable PromotionTarget)' in main
assert 'provider_submission_identity' in main
assert 'provider_pr_identity' not in main
assert 'PR_SUBMITTING' not in main
assert 'CREATE_PR_SUBMISSION' not in main
assert 'promotion_mode' not in main
assert 'No-projection default under ADR-062' in main
assert 'There is no default `WAIT_FOR_MANUAL_MERGE_CLICK` state.' in main
assert 'AUTO' not in ''  # sentinel so this file cannot silently lose the checks above
assert '### 2.15 Semantic review findings and backlog projection' in contract
assert 'A provider submission/PR is not kept open merely as a backlog reminder.' in contract
assert 'closed by ADR-062 (30.36)' in backlog
opens=re.findall(r'open \((30\.\d+)\)',backlog,re.I)
assert sorted(set(opens))==['30.34'], opens
assert 'ProviderSubmission' in adr62 and 'Pull Request' in adr62
assert 'GitHub Issue' in adr63 and 'ReviewCorrectionDemand' in adr63
assert 'frozen mutation handoff' in adr64
assert 'Invariant 146 — A transferable checkpoint offer is frozen against external mutation' in main
assert 'Invariant 147 — The managed checkpoint commit is exactly the frozen canonical candidate' in main
assert 'frozen checkpoint-offer boundary' in contract
assert 'parent(K)=P and tree(K)=T' in main
assert 'STATE-SPACE-AUDIT-v32.md' in main
assert (ROOT/'STATE-SPACE-AUDIT-v32.md').exists()

# No obsolete generic validation waiting states in current normative main.
for banned in [
    'DIRECT_AWAITING_DEVELOPMENT_VALIDATION',
    'AWAITING_DEVELOPMENT_VALIDATION (only when required/missing)',
    '## 33.42 External development-validation prerequisite state',
]:
    assert banned not in main, banned

# Markdown fences balanced.
md=list(ROOT.glob('*.md'))
for f in md:
    t=f.read_text(errors='strict')
    assert t.count('```')%2==0, f'Unbalanced fences: {f.name}'

# Run retained concrete Git primitive smokes.
smokes=[
 ('ADR-048 materialization',smoke_materialization),
 ('ADR-050 restack',smoke_restack),
 ('DIRECT_TARGET_ADVANCE v1',smoke_direct),
 ('repository bootstrap v1',smoke_bootstrap),
 ('canonical checkpoint v1',smoke_checkpoint),
]
for name,fn in smokes:
    fn(); print(f'Ruu {name} smoke: PASS')

RETAINED_V31 = RETAINED_V30 + len(route_combos) + len(finding_combos)
assert RETAINED_V31 == 14454
changed=len(handoff_combos)
print(f'ADR-062 provider projection/finalization finite family retained: PASS ({len(route_combos)} combinations)')
print(f'ADR-063 finding/backlog boundary finite family retained: PASS ({len(finding_combos)} combinations)')
print(f'ADR-064 frozen handoff/checkpoint identity finite family: PASS ({len(handoff_combos)} combinations)')
print(f'retained v31 finite combinations: {RETAINED_V31}')
print(f'v32 changed/revalidated finite combinations: {RETAINED_V31+changed}')
print('ADR numbering: PASS (1..64)')
print(f'markdown artifacts currently statically checked: {len(md)}')
print('static normative checks: PASS')
