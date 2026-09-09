#!/usr/bin/env python3
"""Incremental global regression/state-space audit through ADR-068.

Retains the valid v34 finite regression baseline, adds ADR-068 PromotionGroup
cancellation / ConvergenceUnit disposition families, performs current normative
static checks, and reruns the concrete Git primitive smokes including ordinary
branch deletion with a durable managed checkpoint anchor.
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

def smoke_provider_realization():
    script=ROOT/'git-provider-realization-smoke-v2.sh'
    assert script.exists()
    r=run([str(script)],cwd=ROOT)
    assert r.returncode==0
    assert 'provider-route C-H-R-O realization smoke: PASS' in r.stdout

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

def smoke_branch_deletion_neutrality():
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td); init_repo(p)
        (p/'base.txt').write_text('base\n'); base=commit_all(p,'base')
        git(p,'switch','-q','-c','topic',base)
        (p/'work.txt').write_text('managed checkpoint\n'); c=commit_all(p,'candidate')
        # Durable managed checkpoint anchor exists independently of the authoring branch.
        git(p,'update-ref','refs/Ruu/checkpoints/cu-demo',c)
        git(p,'switch','-q','main')
        git(p,'branch','-D','topic')
        assert git(p,'show-ref','--verify','refs/heads/topic',check=False).returncode!=0
        assert git(p,'rev-parse','refs/Ruu/checkpoints/cu-demo').stdout.strip()==c
        assert git(p,'show',f'{c}:work.txt').stdout=='managed checkpoint\n'
        # Deleting the ordinary authoring branch did not mutate/delete the managed exact state.
        assert git(p,'cat-file','-t',c).stdout.strip()=='commit'

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


# ADR-066 route-conformant final realization family: 2*3*3*3*2 = 108.
realization_routes=['DIRECT_TARGET_ADVANCE','PROVIDER_SUBMISSION']
candidate_target_relation=['EXACT','ANCESTOR','ABSENT']
projection_binding=['IDENTITY_C_EQ_H','EXACT_C_TO_H','MISSING_OR_MISMATCHED']
provider_finalization=['EXACT_H_TO_R','MISSING_OR_MISMATCHED','NONE']
result_target_relation=['PRESENT','ABSENT']
realization_combos=list(itertools.product(realization_routes,candidate_target_relation,projection_binding,provider_finalization,result_target_relation))
assert len(realization_combos)==108
realization_outcomes=set()
for route,c_rel,projection,finalization,r_rel in realization_combos:
    projection_ok=projection in ('IDENTITY_C_EQ_H','EXACT_C_TO_H')
    if route=='DIRECT_TARGET_ADVANCE':
        outcome='PROVEN_DIRECT_ROUTE' if c_rel in ('EXACT','ANCESTOR') else 'TARGET_REALIZATION_UNPROVEN'
    elif projection_ok and finalization=='EXACT_H_TO_R' and r_rel=='PRESENT':
        outcome='PROVEN_PROVIDER_ROUTE'
    elif c_rel in ('EXACT','ANCESTOR') and finalization!='EXACT_H_TO_R':
        outcome='TARGET_PRESENT_REQUIRED_PROVIDER_ROUTE_UNPROVEN'
    else:
        outcome='TARGET_REALIZATION_UNPROVEN'
    realization_outcomes.add(outcome)
    # Native C ancestry must never bypass required provider governance.
    if route=='PROVIDER_SUBMISSION' and c_rel in ('EXACT','ANCESTOR') and finalization!='EXACT_H_TO_R':
        assert outcome=='TARGET_PRESENT_REQUIRED_PROVIDER_ROUTE_UNPROVEN'
    # Provider trust starts at exact submitted H, so missing C→H projection fails.
    if route=='PROVIDER_SUBMISSION' and projection=='MISSING_OR_MISMATCHED':
        assert outcome!='PROVEN_PROVIDER_ROUTE'
    # Provider completion must bind exact H→R and R must be present in target.
    if route=='PROVIDER_SUBMISSION' and (finalization!='EXACT_H_TO_R' or r_rel=='ABSENT'):
        assert outcome!='PROVEN_PROVIDER_ROUTE'
    # DIRECT never needs provider attribution; only native C realization matters in this family.
    if route=='DIRECT_TARGET_ADVANCE' and c_rel in ('EXACT','ANCESTOR'):
        assert outcome=='PROVEN_DIRECT_ROUTE'
assert 'PROVEN_DIRECT_ROUTE' in realization_outcomes
assert 'PROVEN_PROVIDER_ROUTE' in realization_outcomes
assert 'TARGET_PRESENT_REQUIRED_PROVIDER_ROUTE_UNPROVEN' in realization_outcomes

# ADR-066 policy-drift/effect-commitment recovery family: 2*2*2*3*2*2 = 96.
recovery_routes=['DIRECT_TARGET_ADVANCE','PROVIDER_SUBMISSION']
old_authorized=[False,True]
current_authorized=[False,True]
commitment=['NONE','ESTABLISHED','UNKNOWN']
effect_observed=['ABSENT','PRESENT']
action=['OBSERVE_ADOPT','CAUSE_EFFECT']
recovery_combos=list(itertools.product(recovery_routes,old_authorized,current_authorized,commitment,effect_observed,action))
assert len(recovery_combos)==96
recovery_outcomes=set()
for route,old_auth,current_auth,commit,effect,act in recovery_combos:
    if act=='CAUSE_EFFECT':
        outcome='MAY_CAUSE_WITH_CURRENT_POLICY' if current_auth else 'BLOCK_STALE_AUTHORITY'
    elif effect=='ABSENT':
        outcome='NO_EFFECT_TO_ADOPT'
    elif current_auth:
        # Route/exact realization proof is assumed satisfied by the separate realization family.
        outcome='ADOPT_CURRENT_ROUTE_REALIZATION'
    elif old_auth and commit=='ESTABLISHED':
        outcome='ADOPT_HISTORICAL_COMMITTED_EFFECT'
    elif commit=='UNKNOWN':
        outcome='UNKNOWN_INCONSISTENT'
    else:
        outcome='ROUTE_AUTHORIZATION_UNPROVEN'
    recovery_outcomes.add(outcome)
    # Old authorization is never a future capability.
    if act=='CAUSE_EFFECT' and not current_auth:
        assert outcome=='BLOCK_STALE_AUTHORITY'
    # Historical adoption after drift requires established commitment under old authorization.
    if act=='OBSERVE_ADOPT' and effect=='PRESENT' and not current_auth and old_auth and commit=='ESTABLISHED':
        assert outcome=='ADOPT_HISTORICAL_COMMITTED_EFFECT'
    if act=='OBSERVE_ADOPT' and effect=='PRESENT' and not current_auth and commit=='UNKNOWN':
        assert outcome=='UNKNOWN_INCONSISTENT'
assert 'ADOPT_HISTORICAL_COMMITTED_EFFECT' in recovery_outcomes
assert 'BLOCK_STALE_AUTHORITY' in recovery_outcomes
assert 'UNKNOWN_INCONSISTENT' in recovery_outcomes

# ADR-067 current-resolution supersession family: 2*2*3 = 12.
old_promotion_state=['PROMOTED','NONTERMINAL']
current_mapping=['SAME','REPLACED_BY_P1']
old_effect_state=['NONE','COMMITTED_UNRESOLVED','REALIZED_ROUTE_CONFORMANT']
supersession_combos=list(itertools.product(old_promotion_state,current_mapping,old_effect_state))
assert len(supersession_combos)==12
supersession_outcomes=set()
for pstate,mapping,effect in supersession_combos:
    if mapping=='SAME':
        if pstate=='PROMOTED': outcome='REMAINS_PROMOTED_CURRENT_MAPPING'
        elif effect=='REALIZED_ROUTE_CONFORMANT': outcome='PROMOTED_CURRENT_MAPPING'
        else: outcome='CURRENT_TRACK_CONTINUES'
    elif pstate=='PROMOTED':
        outcome='REMAINS_PROMOTED_HISTORICAL'
    elif effect=='NONE':
        outcome='SUPERSEDED'
    elif effect=='COMMITTED_UNRESOLVED':
        outcome='NONCURRENT_RECOVERY_PENDING'
    else:
        outcome='PROMOTED_HISTORICAL'
    supersession_outcomes.add(outcome)
    if mapping=='REPLACED_BY_P1' and pstate=='PROMOTED':
        assert outcome=='REMAINS_PROMOTED_HISTORICAL'
    if mapping=='REPLACED_BY_P1' and pstate=='NONTERMINAL' and effect=='NONE':
        assert outcome=='SUPERSEDED'
    if mapping=='REPLACED_BY_P1' and pstate=='NONTERMINAL' and effect=='COMMITTED_UNRESOLVED':
        assert outcome=='NONCURRENT_RECOVERY_PENDING'
assert 'SUPERSEDED' in supersession_outcomes
assert 'NONCURRENT_RECOVERY_PENDING' in supersession_outcomes
assert 'PROMOTED_HISTORICAL' in supersession_outcomes

# ADR-068 PromotionGroup cancellation family: 2*2*3*2*2 = 48.
cancel_intent_current=[False,True]
realized_group_effect=[False,True]
unresolved_realization=['NONE','COMMITTED','UNKNOWN']
managed_surface=['TERMINAL_NONREALIZING','CAN_STILL_REALIZE']
authoring_artifact=['PRESENT','DELETED']
cancel_combos=list(itertools.product(cancel_intent_current,realized_group_effect,unresolved_realization,managed_surface,authoring_artifact))
assert len(cancel_combos)==48
cancel_outcomes={}
for intent,realized,unresolved,surface,artifact in cancel_combos:
    if not intent:
        outcome='NO_CANCELLATION_AUTHORITY'
    elif realized:
        outcome='CANCEL_FORBIDDEN_REALIZED_EFFECT'
    elif unresolved in ('COMMITTED','UNKNOWN'):
        outcome='RECOVERY_PENDING_EFFECT_MAY_REALIZE'
    elif surface=='CAN_STILL_REALIZE':
        outcome='TERMINAL_NONREALIZING_SURFACE_REQUIRED'
    else:
        outcome='GROUP_CANCELLED'
    cancel_outcomes[(intent,realized,unresolved,surface,artifact)]=outcome
    if realized and intent:
        assert outcome=='CANCEL_FORBIDDEN_REALIZED_EFFECT'
    if intent and not realized and unresolved in ('COMMITTED','UNKNOWN'):
        assert outcome=='RECOVERY_PENDING_EFFECT_MAY_REALIZE'
    if intent and not realized and unresolved=='NONE' and surface=='TERMINAL_NONREALIZING':
        assert outcome=='GROUP_CANCELLED'
# Ordinary authoring artifact presence/deletion cannot alter semantic cancellation outcome.
for intent,realized,unresolved,surface in itertools.product(cancel_intent_current,realized_group_effect,unresolved_realization,managed_surface):
    assert cancel_outcomes[(intent,realized,unresolved,surface,'PRESENT')]==cancel_outcomes[(intent,realized,unresolved,surface,'DELETED')]

# ADR-068 member ConvergenceUnit disposition family: 4*2*2*2*2 = 64.
group_terminal_state=['CANCELLED','ALL_PROMOTED','COMPENSATED','NONTERMINAL']
replacement_group=[False,True]
authoring_demand=[False,True]
lineage_disposal_current=[False,True]
artifact_presence=['PRESENT','DELETED']
disposition_combos=list(itertools.product(group_terminal_state,replacement_group,authoring_demand,lineage_disposal_current,artifact_presence))
assert len(disposition_combos)==64
disposition_outcomes={}
for gstate,replacement,demand,dispose,artifact in disposition_combos:
    if replacement or demand or gstate=='NONTERMINAL':
        outcome='LINEAGE_REMAINS_LIVE'
    elif gstate in ('ALL_PROMOTED','COMPENSATED'):
        outcome='NORMAL_PROMOTED_CLOSURE'
    elif dispose:
        outcome='ABANDONING_ELIGIBLE'
    else:
        outcome='WAIT_LINEAGE_DISPOSITION_AUTHORITY'
    disposition_outcomes[(gstate,replacement,demand,dispose,artifact)]=outcome
    if gstate=='CANCELLED' and not replacement and not demand and dispose:
        assert outcome=='ABANDONING_ELIGIBLE'
    if replacement or demand:
        assert outcome=='LINEAGE_REMAINS_LIVE'
    if gstate in ('ALL_PROMOTED','COMPENSATED') and not replacement and not demand:
        assert outcome=='NORMAL_PROMOTED_CLOSURE'
for gstate,replacement,demand,dispose in itertools.product(group_terminal_state,replacement_group,authoring_demand,lineage_disposal_current):
    assert disposition_outcomes[(gstate,replacement,demand,dispose,'PRESENT')]==disposition_outcomes[(gstate,replacement,demand,dispose,'DELETED')]

# ADR-068 immutable membership-change family: 2*2*2 = 8.
old_group_effect=['ZERO_REALIZED','REALIZED']
desired_membership=['SAME','CHANGED']
cancel_authority=[False,True]
membership_combos=list(itertools.product(old_group_effect,desired_membership,cancel_authority))
assert len(membership_combos)==8
for effect,desired,authority in membership_combos:
    if desired=='SAME':
        outcome='NO_MEMBERSHIP_MUTATION'
    elif effect=='REALIZED':
        outcome='SETTLEMENT_REQUIRED_OLD_GROUP_IMMUTABLE'
    elif authority:
        outcome='CANCEL_OLD_DECLARE_NEW_GROUP'
    else:
        outcome='WAIT_CANCELLATION_AUTHORITY_OLD_GROUP_IMMUTABLE'
    if desired=='CHANGED':
        assert outcome!='MUTATE_EXISTING_GROUP'
    if desired=='CHANGED' and effect=='ZERO_REALIZED' and authority:
        assert outcome=='CANCEL_OLD_DECLARE_NEW_GROUP'
    if desired=='CHANGED' and effect=='REALIZED':
        assert outcome=='SETTLEMENT_REQUIRED_OLD_GROUP_IMMUTABLE'

# Static current-doc checks.
adrs=sorted(ROOT.glob('ADR-*.md'))
nums=[int(x.name[4:7]) for x in adrs]
assert nums==list(range(1,69)), nums
main=(ROOT/'ruu-requirements-v1-merge-policy.md').read_text()
contract=(ROOT/'EXTERNAL-CONTROL-PLANE-CONTRACT.md').read_text()
backlog=(ROOT/'OPEN-DESIGN-BACKLOG.md').read_text()
adr62=(ROOT/'ADR-062-make-promotion-route-independent-and-provider-submissions-projections.md').read_text()
adr63=(ROOT/'ADR-063-keep-findings-and-backlog-outside-ruu.md').read_text()
adr64=(ROOT/'ADR-064-bind-pre-commit-readiness-by-frozen-mutation-handoff.md').read_text()
adr65=(ROOT/'ADR-065-prove-final-promotion-realization-by-native-git-or-exact-provider-result-binding.md').read_text()
adr66=(ROOT/'ADR-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md').read_text()
adr67=(ROOT/'ADR-067-terminalize-obsolete-unpromoted-promotion-units-by-current-resolution-supersession.md').read_text()
adr68=(ROOT/'ADR-068-cancel-unrealized-promotion-groups-explicitly-and-keep-git-artifact-deletion-semantically-neutral.md').read_text()

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
assert '### 2.15 Semantic review findings and backlog projection' in contract
assert 'A provider submission/PR is not kept open merely as a backlog reminder.' in contract
assert 'closed by ADR-062 (30.36)' in backlog
assert '## 30.36 Resolved by ADR-062 — REVIEW_NOT_REQUESTED no-projection default' in main
assert '## 30.36 REVIEW_NOT_REQUESTED eligibility policy' not in main
opens=re.findall(r'open \((30\.\d+)\)',backlog,re.I)
assert sorted(set(opens))==[], opens
assert 'ProviderSubmission' in adr62 and 'Pull Request' in adr62
assert 'GitHub Issue' in adr63 and 'ReviewCorrectionDemand' in adr63
assert 'frozen mutation handoff' in adr64
assert '## Amendment by ADR-066' in adr65
assert 'SubmissionProjectionProof' in adr66
assert 'ProviderFinalizationObservation(H → R' in adr66
assert 'Candidate ancestry in target is not a substitute' in contract
assert 'SUPERSEDED' in adr67
assert 'ABANDONED' in adr67  # explicit removal discussion exists
assert 'Invariant 146 — A transferable checkpoint offer is frozen against external mutation' in main
assert 'Invariant 147 — The managed checkpoint commit is exactly the frozen canonical candidate' in main
assert 'Invariant 148 — Promotion is terminal only after exact route-conformant target realization proof' in main
assert 'Invariant 149 — DIRECT native realization does not require Ruu actor attribution' in main
assert 'Invariant 150 — Provider submission projection binds immutable C to exact submitted H' in main
assert 'Invariant 151 — Provider finalization binds exact H to exact R and independently observes R in target history' in main
assert 'Invariant 152 — Native candidate ancestry cannot bypass a required provider route' in main
assert 'Invariant 153 — Historical authorization may explain committed effects but never authorize future causal mutation' in main
assert 'Invariant 154 — PromotionUnit PROMOTED is historical completion, not perpetual target-membership monitoring' in main
assert 'Invariant 155 — Rewritten-result semantic equivalence is not a Ruu prerequisite' in main
assert 'frozen checkpoint-offer boundary' in contract
assert '### 2.16 Provider transformation / route-conformant final target realization trust boundary' in contract
assert 'parent(K)=P and tree(K)=T' in main
assert (ROOT/'STATE-SPACE-AUDIT-v34.md').exists()
assert '## 30.34 Resolved by ADR-065 as corrected by ADR-066' in main
assert 'CLOSED by ADR-068 (30.41)' in backlog
assert '## 30.41 Resolved by ADR-068' in main
assert 'C → H' in main and 'H → R' in main
assert 'SUPERSEDED' in main
assert 'PromotionGroup CANCELLED' in adr68
assert 'ordinary Git artifact deletion' in adr68
assert 'Invariant 156 — Ordinary Git artifact deletion carries no hidden Ruu lifecycle semantics' in main
assert 'Invariant 157 — Group-bound non-delivery is decided at PromotionGroup scope' in main
assert 'Invariant 158 — PromotionGroup CANCELLED requires zero realized and zero still-realizing effects' in main
assert 'Invariant 159 — Ship-membership change is cancel-old plus declare-new, never mutation' in main
assert 'Invariant 160 — ConvergenceUnit ABANDONING is gated by higher-level terminal disposition' in main
assert 'CANCELLED          # explicit terminal withdrawal before any promotion effect has realized' in main
assert '↛ PromotionGroup CANCELLED' in main
assert 'STATE-SPACE-AUDIT-v35.md' in main
assert (ROOT/'STATE-SPACE-AUDIT-v35.md').exists()
# PromotionUnit generic lifecycle must not retain ABANDONED.
life=re.search(r'## 18\.2 Promotion-unit lifecycle(.*?)## 18\.3',main,re.S).group(1)
assert '\nABANDONED\n' not in life

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
 ('provider-route C-H-R-O realization v2',smoke_provider_realization),
 ('ordinary branch deletion / managed checkpoint neutrality',smoke_branch_deletion_neutrality),
]
for name,fn in smokes:
    fn(); print(f'Ruu {name} smoke: PASS')

RETAINED_V31 = RETAINED_V30 + len(route_combos) + len(finding_combos)
assert RETAINED_V31 == 14454
RETAINED_V32 = RETAINED_V31 + len(handoff_combos)
assert RETAINED_V32 == 14470
changed_v34=len(realization_combos)+len(recovery_combos)+len(supersession_combos)
assert RETAINED_V32+changed_v34 == 14686
adr068_changed=len(cancel_combos)+len(disposition_combos)+len(membership_combos)
print(f'ADR-062 provider projection/finalization finite family retained: PASS ({len(route_combos)} combinations)')
print(f'ADR-063 finding/backlog boundary finite family retained: PASS ({len(finding_combos)} combinations)')
print(f'ADR-064 frozen handoff/checkpoint identity finite family retained: PASS ({len(handoff_combos)} combinations)')
print(f'ADR-066 route-conformant realization finite family retained: PASS ({len(realization_combos)} combinations)')
print(f'ADR-066 policy-drift/commitment recovery finite family retained: PASS ({len(recovery_combos)} combinations)')
print(f'ADR-067 supersession finite family retained: PASS ({len(supersession_combos)} combinations)')
print(f'ADR-068 group cancellation finite family: PASS ({len(cancel_combos)} combinations)')
print(f'ADR-068 ConvergenceUnit disposition finite family: PASS ({len(disposition_combos)} combinations)')
print(f'ADR-068 immutable membership-change finite family: PASS ({len(membership_combos)} combinations)')
print(f'retained v34 finite combinations: {RETAINED_V32+changed_v34}')
print(f'v35 changed/revalidated finite combinations: {RETAINED_V32+changed_v34+adr068_changed}')
print('ADR numbering: PASS (1..68)')
print(f'markdown artifacts currently statically checked: {len(md)}')
print('static normative checks: PASS')
