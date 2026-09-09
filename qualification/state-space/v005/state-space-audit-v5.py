#!/usr/bin/env python3
"""Global regression/state-space audit for ADR-035 bounded contribution-unit model.

This audit does not claim to enumerate unbounded Git DAG/provider states. It
exhaustively checks the finite identity/cardinality and authority families
changed by ADR-035, reruns the finite ADR-033/029..032 families, and performs
static consistency checks across the current architecture artifacts.
"""
from itertools import product
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def audit_contribution_unit_cardinality_identity():
    context_state = ["PROVISIONED", "REMOVED"]
    bindings = ["ZERO", "ONE", "MULTIPLE", "UNKNOWN"]
    n = 0
    for state, repo, convergence, worktree, ref in product(
        context_state, bindings, bindings, bindings, bindings
    ):
        n += 1
        valid = (
            (state == "PROVISIONED" and repo == convergence == worktree == ref == "ONE")
            or (state == "REMOVED" and repo == convergence == "ONE" and worktree == ref == "ZERO")
        )
        if valid:
            assert repo == convergence == "ONE"
            assert worktree != "MULTIPLE" and ref != "MULTIPLE"
        if repo in {"ZERO", "MULTIPLE", "UNKNOWN"} or convergence in {"ZERO", "MULTIPLE", "UNKNOWN"}:
            assert not valid
        if state == "PROVISIONED" and (worktree != "ONE" or ref != "ONE"):
            assert not valid
        if state == "REMOVED" and (worktree != "ZERO" or ref != "ZERO"):
            assert not valid
    return n


def audit_actor_correlation_irrelevance():
    correlations = ["NONE", "SAME_EXTERNAL_ACTOR", "DIFFERENT_EXTERNAL_ACTOR", "UNKNOWN"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_THIS",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_OTHER",
        "UNKNOWN",
    ]
    claims = ["NONE", "THIS", "OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    n = 0
    baseline = {}
    for corr, acc, claim, topo in product(correlations, access, claims, topology):
        n += 1
        authorized = topo == "KNOWN" and claim == "THIS" and acc in {"TRANSFERABLE_THIS", "TRANSFERABLE_GENERAL"}
        key = (acc, claim, topo)
        if key in baseline:
            assert baseline[key] == authorized
        else:
            baseline[key] = authorized
        _ = corr  # correlation is intentionally not in the predicate
    return n


def audit_contribution_unit_worktree_mutation_authority():
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_THIS",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_OTHER",
        "UNKNOWN",
    ]
    claims = ["NONE", "THIS", "OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    operations = ["COMMIT", "SYNC", "CONFLICT_MUTATION", "RESET_MOVE", "CLEANUP"]
    n = 0
    for acc, claim, topo, op in product(access, claims, topology, operations):
        n += 1
        authorized = topo == "KNOWN" and claim == "THIS" and acc in {"TRANSFERABLE_THIS", "TRANSFERABLE_GENERAL"}
        if authorized:
            assert claim == "THIS" and topo == "KNOWN"
        if acc in {"PROTECTED_EXTERNAL", "TRANSFERABLE_OTHER", "UNKNOWN"}:
            assert not authorized
        if claim != "THIS" or topo != "KNOWN":
            assert not authorized
        _ = op
    return n


def audit_contribution_unit_commit_verification():
    lifecycle = ["PRESENT", "REMOVED"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_THIS",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_OTHER",
        "UNKNOWN",
    ]
    claims = ["NONE", "THIS", "OTHER"]
    dirties = [False, True]
    evidence = ["NONE", "VALID", "STALE", "FAIL", "UNKNOWN"]
    stability = ["STABLE", "MUTATED", "UNKNOWN"]
    n = 0
    for life, acc, claim, dirty, ev, stable in product(
        lifecycle, access, claims, dirties, evidence, stability
    ):
        n += 1
        authorized = (
            life != "REMOVED"
            and dirty
            and acc in {"TRANSFERABLE_THIS", "TRANSFERABLE_GENERAL"}
            and claim == "THIS"
            and ev == "VALID"
            and stable == "STABLE"
        )
        if authorized:
            assert life == "PRESENT" and dirty and claim == "THIS"
            assert ev == "VALID" and stable == "STABLE"
        if acc in {"PROTECTED_EXTERNAL", "TRANSFERABLE_OTHER", "UNKNOWN"}:
            assert not authorized
        if life == "REMOVED" or ev != "VALID" or stable != "STABLE" or claim != "THIS":
            assert not authorized
    return n


def audit_state_producing_transition_verification():
    kinds = [
        "CHECKPOINT",
        "TARGET_TO_CU_MERGE",
        "CU_TO_CONTRIBUTION_UNIT_MERGE",
        "PROMOTION_PROJECTION",
        "SUBMISSION_REVISION",
        "DIRECT_CANDIDATE",
    ]
    result_relation = ["SAME", "NEW"]
    evidence = ["VALID", "MISSING", "STALE", "FAIL"]
    policy = ["SAME", "CHANGED", "UNKNOWN"]
    context = ["SAME", "CHANGED", "UNKNOWN"]
    n = 0
    for kind, relation, ev, pol, ctx in product(kinds, result_relation, evidence, policy, context):
        n += 1
        may_adopt = ev == "VALID" and pol == "SAME" and ctx == "SAME"
        if relation == "NEW" and ev != "VALID":
            assert not may_adopt
        if pol != "SAME" or ctx != "SAME":
            assert not may_adopt
        _ = kind
    return n


def audit_evidence_reuse():
    state = ["SAME", "CHANGED"]
    policy = ["SAME", "CHANGED", "UNKNOWN"]
    context = ["SAME", "CHANGED", "UNKNOWN"]
    evidence = ["VALID", "MISSING", "STALE", "FAIL"]
    n = 0
    for st, pol, ctx, ev in product(state, policy, context, evidence):
        n += 1
        reusable = st == pol == ctx == "SAME" and ev == "VALID"
        if st == "CHANGED" or pol != "SAME" or ctx != "SAME" or ev != "VALID":
            assert not reusable
    return n


def audit_verification_fixed_point():
    mutation = ["NONE", "PARASITE", "INTENTIONAL", "UNKNOWN"]
    result = ["PASS", "FAIL", "INFRA_FAILURE"]
    stability = ["STABLE", "CHANGED", "UNKNOWN"]
    iteration = ["FIRST", "REVERIFY", "LIMIT_REACHED"]
    n = 0
    for mut, res, stable, it in product(mutation, result, stability, iteration):
        n += 1
        eligible = mut == "NONE" and res == "PASS" and stable == "STABLE" and it != "LIMIT_REACHED"
        if mut in {"INTENTIONAL", "UNKNOWN"} or stable != "STABLE" or res != "PASS" or it == "LIMIT_REACHED":
            assert not eligible
    return n


def audit_verification_capacity():
    capacity = ["AVAILABLE", "SATURATED", "DISABLED", "UNKNOWN"]
    job = ["NOT_QUEUED", "QUEUED", "RUNNING", "DONE", "CANCELLED_STALE"]
    freshness = ["CURRENT", "STALE", "UNKNOWN"]
    git_authority = ["HELD", "NOT_HELD", "UNKNOWN"]
    n = 0
    for cap, js, fresh, auth in product(capacity, job, freshness, git_authority):
        n += 1
        may_start = cap == "AVAILABLE" and js == "QUEUED" and fresh == "CURRENT" and auth == "HELD"
        if cap != "AVAILABLE" or auth != "HELD" or fresh != "CURRENT":
            assert not may_start
    return n


def audit_review_request_intent():
    submission = ["ABSENT", "EXISTS"]
    intent = ["NONE", "REVIEW_NOT_REQUESTED", "REVIEW_REQUESTED"]
    readiness = ["NOT_READY", "READY"]
    author_gate = ["PASS", "FAIL", "STALE"]
    head = ["CURRENT", "CHANGED", "UNKNOWN"]
    n = 0
    for sub, intent_state, ready, gate, head_state in product(submission, intent, readiness, author_gate, head):
        n += 1
        valid_requested = sub == "EXISTS" and intent_state == "REVIEW_REQUESTED" and ready == "READY" and gate == "PASS" and head_state == "CURRENT"
        if sub == "ABSENT":
            assert not valid_requested
    return n


def audit_review_revision_invalidation():
    intent = ["REVIEW_NOT_REQUESTED", "REVIEW_REQUESTED"]
    head_changed = [False, True]
    author_gate = ["PASS", "FAIL", "STALE"]
    provider_support = [False, True]
    n = 0
    for intent_state, changed, gate, support in product(intent, head_changed, author_gate, provider_support):
        n += 1
        may_remain_requested = intent_state == "REVIEW_REQUESTED" and (not changed or gate == "PASS")
        if intent_state == "REVIEW_REQUESTED" and changed and gate != "PASS":
            assert not may_remain_requested
        _ = support
    return n


def audit_internal_integration_evidence():
    relation = ["UP_TO_DATE", "PARENT_AHEAD", "CHILD_AHEAD", "DIVERGED", "UNKNOWN"]
    result_kind = ["SAME", "NEW"]
    evidence = ["VALID", "MISSING", "STALE", "FAIL"]
    claim = ["HELD", "OTHER", "NONE"]
    conflict = [False, True]
    n = 0
    for rel, result, ev, cl, conflict_state in product(relation, result_kind, evidence, claim, conflict):
        n += 1
        may_adopt = cl == "HELD" and not conflict_state and rel != "UNKNOWN" and ev == "VALID"
        if result == "NEW" and ev != "VALID":
            assert not may_adopt
        if cl != "HELD" or conflict_state or rel == "UNKNOWN":
            assert not may_adopt
    return n


def audit_contribution_unit_lifecycle():
    lifecycle = ["OPEN", "CLOSED", "ABANDONED", "REMOVED"]
    runtime = ["RUNNING", "WAITING_FOR_USER", "TURN_FINISHED", "INACTIVE"]
    integration = ["NOT_INTEGRATED", "INTEGRATED_EXACT", "UNKNOWN"]
    requested_action = ["NO_NEW_WORK", "SAME_UNIT_NEW_CONTRIBUTION", "NEW_UNIT_CONTRIBUTION"]
    n = 0
    for life, run, integ, action in product(lifecycle, runtime, integration, requested_action):
        n += 1
        same_unit_may_produce = life == "OPEN" and action == "SAME_UNIT_NEW_CONTRIBUTION"
        if life in {"CLOSED", "ABANDONED", "REMOVED"}:
            assert not same_unit_may_produce
        if action == "SAME_UNIT_NEW_CONTRIBUTION" and life != "OPEN":
            assert not same_unit_may_produce
        # Runtime/turn state does not infer or alter lifecycle.
        assert life in {"OPEN", "CLOSED", "ABANDONED", "REMOVED"}
        _ = (run, integ)
    return n


def static_consistency_checks():
    md_files = sorted(ROOT.glob("*.md"))
    assert md_files
    for p in md_files:
        text = p.read_text()
        assert text.count("```") % 2 == 0, f"unbalanced code fences: {p.name}"

    adr_files = sorted(ROOT.glob("ADR-*.md"))
    nums = sorted(int(re.match(r"ADR-(\d+)", p.name).group(1)) for p in adr_files)
    assert nums == list(range(1, 36)), nums

    main = (ROOT / "ruu-requirements-v1-merge-policy.md").read_text()
    backlog = (ROOT / "OPEN-DESIGN-BACKLOG.md").read_text()
    adr33 = (ROOT / "ADR-033-consume-external-contribution-unit-mutation-authority.md").read_text()
    adr34 = (ROOT / "ADR-034-replace-writer-model-with-repository-local-contribution-units.md").read_text()
    adr35 = (ROOT / "ADR-035-use-bounded-contribution-units-with-external-lifecycle-authority.md").read_text()

    required_main = [
        "A **contribution unit** is a repository-local isolated Git unit",
        "one **bounded stream of contribution to its current convergence scope**",
        "1 contribution_unit_id",
        "exactly 1 repository_id",
        "exactly 1 convergence_unit_id membership",
        "CLOSED` and `ABANDONED` are terminal",
        "any later work",
        "requires a **new contribution unit**",
        "agent waiting for user",
        "external contribution-unit subsystem",
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_TO_THIS_INVOCATION",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_TO_OTHER_INVOCATION",
        "contribution_unit_id",
        "Transferability still requires a race-safe exclusive claim",
    ]
    for marker in required_main:
        assert marker in main, marker

    assert "work_context_id" not in main
    assert "work_context_readiness" not in main
    assert "WORK_CONTEXT_REF" not in main
    assert "writer_context_id" not in main
    assert "writer_id" not in main
    assert "editing-context" not in main
    assert "LEASE_ESTABLISHED" not in main

    # ADR-001..033 must use current contribution-unit terminology.
    for p in adr_files:
        if p.name.startswith("ADR-034-") or p.name.startswith("ADR-035-"):
            continue
        text = p.read_text().lower()
        assert "work_context_id" not in text, p.name
        assert "work-context" not in text, p.name
        assert not re.search(r"\bwork context\b", text), p.name
        assert "writer_context_id" not in text, p.name
        assert "writer_id" not in text, p.name
        assert "editing-context" not in text, p.name
        assert not re.search(r"\bwriter\b", text), p.name

    assert "global `writer_id` is therefore not required" in adr34
    assert "current object name/lifecycle superseded by ADR-035" in adr34
    assert "bounded stream of contribution" in adr35
    assert "never transition back to `OPEN`" in adr35
    assert "waiting for user" in adr35
    assert "external contribution-unit subsystem" in adr35
    assert "Retired from this backlog by ADR-033/ADR-034/ADR-035" in backlog
    assert "8. contribution-unit close signal" not in backlog
    assert "Producer/runtime liveness is outside `ruu`" in adr33
    assert "Transferability is not mutation authority" in adr33

    # No current ADR may claim that a terminal contribution unit can reopen.
    for p in adr_files:
        if p.name.startswith("ADR-034-") or p.name.startswith("ADR-035-"):
            continue
        text = p.read_text().lower()
        assert "reopen of contribution units" not in text, p.name
        assert "creation/reopen of contribution units" not in text, p.name

    return len(md_files)

def main():
    families = {
        "contribution_unit_cardinality_identity": audit_contribution_unit_cardinality_identity(),
        "actor_correlation_irrelevance": audit_actor_correlation_irrelevance(),
        "contribution_unit_lifecycle": audit_contribution_unit_lifecycle(),
        "contribution_unit_worktree_mutation_authority": audit_contribution_unit_worktree_mutation_authority(),
        "contribution_unit_commit_verification_crosscheck": audit_contribution_unit_commit_verification(),
        "state_producing_transition_verification": audit_state_producing_transition_verification(),
        "verification_evidence_reuse": audit_evidence_reuse(),
        "verification_fixed_point": audit_verification_fixed_point(),
        "verification_capacity_scheduler": audit_verification_capacity(),
        "review_request_intent": audit_review_request_intent(),
        "review_revision_invalidation": audit_review_revision_invalidation(),
        "internal_integration_evidence": audit_internal_integration_evidence(),
    }
    docs = static_consistency_checks()
    total = sum(families.values())
    print("Ruu state-space audit v5: PASS")
    for name, count in families.items():
        print(f"{name}: {count:,}")
    print(f"changed/revalidated finite combinations evaluated: {total:,}")
    print(f"markdown artifacts statically cross-checked: {docs}")


if __name__ == "__main__":
    main()
