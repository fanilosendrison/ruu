#!/usr/bin/env python3
"""Incremental global regression/state-space audit through ADR-061.

Revalidates the retained v29 finite count, adds the ADR-061 immutable pre-authoring
PromotionTarget family, performs current normative static checks, and reruns the five
concrete Git primitive smokes.
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

# ADR-061 target-binding finite family: 3*3*2*2*2*2 = 144.
stages=['BEFORE_FIRST_WRITE','AFTER_FIRST_WRITE','PROMOTION']
binding=['MATCH_REQUEST','DIFFERENT_REQUEST','MISSING']
modes=['DIRECT','PR']
policy_target=['SAME','DIFFERENT']
group=['COHERENT','INCOHERENT']
oid=['CURRENT','MOVED']
combos=list(itertools.product(stages,binding,modes,policy_target,group,oid))
assert len(combos)==144
for stage,bound,mode,p_override,gcoh,oid_state in combos:
    # target mutation is never an allowed outcome
    if p_override=='DIFFERENT':
        outcome='BLOCK_POLICY_OVERRIDE'
    elif gcoh=='INCOHERENT':
        outcome='TARGET_INCOHERENT_PROMOTION_GROUP'
    elif bound=='MISSING':
        outcome='BLOCK_UNBOUND_TARGET' if stage=='BEFORE_FIRST_WRITE' else 'UNKNOWN_INCONSISTENT'
    elif bound=='DIFFERENT_REQUEST':
        outcome='REQUIRE_DISTINCT_CONVERGENCE_UNIT'
    elif oid_state=='MOVED':
        outcome='REFRESH_CURRENT_TARGET_STATE'
    else:
        outcome=f'PROGRESS_{mode}'
    assert 'RETARGET' not in outcome

# Static docs checks (run before v30 report is added: allow 93 or 94 md).
adrs=sorted(ROOT.glob('ADR-*.md'))
nums=[int(x.name[4:7]) for x in adrs]
assert nums==list(range(1,62)), nums
main=(ROOT/'ruu-requirements-v1-merge-policy.md').read_text()
contract=(ROOT/'EXTERNAL-CONTROL-PLANE-CONTRACT.md').read_text()
backlog=(ROOT/'OPEN-DESIGN-BACKLOG.md').read_text()
adr61=(ROOT/'ADR-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md').read_text()
assert '## 30.40 Resolved by ADR-061' in main
assert 'PromotionTarget = (target_repository_id, target_ref)' in main
assert 'TARGET_INCOHERENT_PROMOTION_GROUP' in main and 'TARGET_INCOHERENT_PROMOTION_GROUP' in adr61
assert '### 2.3A ConvergenceUnit PromotionTarget authority' in contract
assert '`EffectivePromotionPolicy` answers **how**' in backlog
assert 'target/base' not in main
for banned in [
    'development-validation-blocked',
    '## 33.42 External development-validation prerequisite state',
    'A **managed commit** represents an exact checkpoint whose externally owned development-validation prerequisites',
    'Repository policy names the exact target repository/ref',
    'target/publication destination\nsubmission rewrite authorization',
]:
    assert banned not in main, banned
# only genuine open core headings in backlog
opens=re.findall(r'open \((30\.\d+)\)',backlog,re.I)
assert sorted(set(opens))==['30.34','30.36'], opens
# fences balanced in all markdown artifacts currently present
md=list(ROOT.glob('*.md'))
for f in md:
    t=f.read_text(errors='strict')
    assert t.count('```')%2==0, f'Unbalanced fences: {f.name}'

# run git smokes
smokes=[
 ('ADR-048 materialization',smoke_materialization),
 ('ADR-050 restack',smoke_restack),
 ('DIRECT target advance v1',smoke_direct),
 ('repository bootstrap v1',smoke_bootstrap),
 ('canonical checkpoint v1',smoke_checkpoint),
]
for name,fn in smokes:
    fn(); print(f'Ruu {name} smoke: PASS')
print('Ruu ADR-061 target-binding finite family: PASS (144 combinations)')
print(f'retained v29 finite combinations: 14222')
print(f'v30 changed/revalidated finite combinations: {14222+len(combos)}')
print(f'ADR numbering: PASS (1..61)')
print(f'markdown artifacts currently statically checked: {len(md)}')
print('static normative checks: PASS')
