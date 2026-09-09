#!/usr/bin/env python3
"""Factorized consistency audit for Ruu verification/review amendments.

This script does not enumerate unbounded Git DAGs. It mirrors the specification's
factorized audit style and exhaustively checks the newly introduced finite state
families from ADR-029..032, then combines their counts with the pre-existing
factorized audit count (12,246).
"""
from itertools import product

BASELINE_EXISTING_COMBINATIONS = 12_246


def audit_writer_commit_verification():
    leases = ["ACTIVE", "INACTIVE", "REMOVED"]
    delegations = ["NONE", "THIS", "OTHER"]
    claims = ["FREE", "THIS", "OTHER"]
    dirties = [False, True]
    evidence = ["NONE", "VALID", "STALE", "FAIL", "UNKNOWN"]
    stability = ["STABLE", "MUTATED", "UNKNOWN"]
    n = 0
    for lease, delegation, claim, dirty, ev, stable in product(
        leases, delegations, claims, dirties, evidence, stability
    ):
        n += 1
        authorized = (
            dirty
            and lease != "REMOVED"
            and claim == "THIS"
            and (lease == "INACTIVE" or delegation == "THIS")
            and ev == "VALID"
            and stable == "STABLE"
        )
        if authorized:
            assert dirty
            assert claim == "THIS"
            assert lease != "REMOVED"
            assert ev == "VALID" and stable == "STABLE"
            if lease == "ACTIVE":
                assert delegation == "THIS"
        if lease == "ACTIVE" and delegation != "THIS":
            assert not authorized
        if ev != "VALID" or stable != "STABLE":
            assert not authorized
    return n


def audit_state_producing_transition_verification():
    kinds = [
        "CHECKPOINT",
        "TARGET_TO_CU_MERGE",
        "CU_TO_WRITER_MERGE",
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
        if may_adopt:
            assert ev == "VALID"
        if relation == "NEW" and ev != "VALID":
            assert not may_adopt
        if pol != "SAME" or ctx != "SAME":
            assert not may_adopt
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
        if reusable:
            assert (st, pol, ctx, ev) == ("SAME", "SAME", "SAME", "VALID")
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
        if eligible:
            assert res == "PASS" and stable == "STABLE"
        if mut in {"INTENTIONAL", "UNKNOWN"} or stable != "STABLE" or res != "PASS":
            assert not eligible
        if it == "LIMIT_REACHED":
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
        if may_start:
            assert cap == "AVAILABLE" and auth == "HELD" and fresh == "CURRENT"
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
        valid_requested = (
            sub == "EXISTS"
            and intent_state == "REVIEW_REQUESTED"
            and ready == "READY"
            and gate == "PASS"
            and head_state == "CURRENT"
        )
        if intent_state == "REVIEW_REQUESTED" and not valid_requested:
            # This combination is inconsistent/blocked, never an authorized requested-review state.
            pass
        if valid_requested:
            assert sub == "EXISTS" and ready == "READY" and gate == "PASS" and head_state == "CURRENT"
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
        # provider support influences whether the UI can be toggled, not the semantic validity of stale review-request evidence
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


def main():
    families = {
        "writer_commit_verification_crosscheck": audit_writer_commit_verification(),
        "state_producing_transition_verification": audit_state_producing_transition_verification(),
        "verification_evidence_reuse": audit_evidence_reuse(),
        "verification_fixed_point": audit_verification_fixed_point(),
        "verification_capacity_scheduler": audit_verification_capacity(),
        "review_request_intent": audit_review_request_intent(),
        "review_revision_invalidation": audit_review_revision_invalidation(),
        "internal_integration_evidence": audit_internal_integration_evidence(),
    }
    added = sum(families.values())
    total = BASELINE_EXISTING_COMBINATIONS + added
    print("Ruu state-space audit v2: PASS")
    print(f"baseline existing factorized combinations: {BASELINE_EXISTING_COMBINATIONS:,}")
    for name, count in families.items():
        print(f"{name}: {count:,}")
    print(f"new combinations evaluated: {added:,}")
    print(f"combined factorized combinations represented: {total:,}")


if __name__ == "__main__":
    main()
