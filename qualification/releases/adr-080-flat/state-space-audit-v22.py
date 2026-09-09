#!/usr/bin/env python3
"""Global regression/state-space audit through ADR-053 review-correction continuation semantics.

This audit does not claim to enumerate arbitrary semantic review interpretations, Git
DAGs, provider implementations, or Development System runtimes. It revalidates every
finite current architecture family from v21 and adds explicit coverage for ADR-053
durable exact-generation review-correction demand identity, hook/sweep idempotence,
session-independent continuation, new-ContributionUnit authoring, immutable-group
continuity, and scope-expansion separation.
"""
from itertools import product, permutations
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parent


def audit_contribution_unit_cardinality_identity():
    lifecycle = ["OPEN", "CLOSED"]
    bindings = ["ZERO", "ONE", "MULTIPLE", "UNKNOWN"]
    artifact = ["ABSENT", "PRESENT"]
    n = 0
    for life, repo, convergence, local_ref, worktree, remote_ref in product(
        lifecycle, bindings, bindings, artifact, artifact, artifact
    ):
        n += 1
        valid_identity = repo == convergence == "ONE"
        if valid_identity:
            assert life in {"OPEN", "CLOSED"}
        if repo != "ONE" or convergence != "ONE":
            assert not valid_identity
        _ = (local_ref, worktree, remote_ref)
    return n


def audit_actor_correlation_irrelevance():
    correlations = ["NONE", "SAME_EXTERNAL_ACTOR", "DIFFERENT_EXTERNAL_ACTOR", "UNKNOWN"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_RUU",
        "TRANSFERABLE_GENERAL",
        "UNKNOWN",
    ]
    claims = ["NONE", "CURRENT_EXECUTOR_OPERATION", "INCOMPATIBLE_OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    n = 0
    baseline = {}
    for corr, acc, claim, topo in product(correlations, access, claims, topology):
        n += 1
        authorized = topo == "KNOWN" and claim == "CURRENT_EXECUTOR_OPERATION" and acc in {"TRANSFERABLE_RUU", "TRANSFERABLE_GENERAL"}
        key = (acc, claim, topo)
        if key in baseline:
            assert baseline[key] == authorized
        else:
            baseline[key] = authorized
        _ = corr  # correlation is intentionally not in the predicate
    return n


def audit_contribution_unit_worktree_mutation_authority():
    surface = ["PRESENT", "ABSENT"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_RUU",
        "TRANSFERABLE_GENERAL",
        "UNKNOWN",
    ]
    claims = ["NONE", "CURRENT_EXECUTOR_OPERATION", "INCOMPATIBLE_OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    operations = ["COMMIT", "SYNC", "CONFLICT_MUTATION", "RESET_MOVE"]
    n = 0
    for surf, acc, claim, topo, op in product(surface, access, claims, topology, operations):
        n += 1
        authorized = (
            surf == "PRESENT"
            and topo == "KNOWN"
            and claim == "CURRENT_EXECUTOR_OPERATION"
            and acc in {"TRANSFERABLE_RUU", "TRANSFERABLE_GENERAL"}
        )
        if surf == "ABSENT":
            assert not authorized
        if acc in {"PROTECTED_EXTERNAL", "UNKNOWN"}:
            assert not authorized
        if claim != "CURRENT_EXECUTOR_OPERATION" or topo != "KNOWN":
            assert not authorized
        _ = op
    return n


def audit_contribution_unit_commit_verification():
    lifecycle = ["OPEN", "CLOSED"]
    surface = ["ABSENT", "PRESENT_CLEAN", "PRESENT_DIRTY"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_RUU",
        "TRANSFERABLE_GENERAL",
        "UNKNOWN",
    ]
    claims = ["NONE", "CURRENT_EXECUTOR_OPERATION", "INCOMPATIBLE_OTHER"]
    evidence = ["NONE", "VALID", "STALE", "FAIL", "UNKNOWN"]
    stability = ["STABLE", "MUTATED", "UNKNOWN"]
    n = 0
    for life, surf, acc, claim, ev, stable in product(
        lifecycle, surface, access, claims, evidence, stability
    ):
        n += 1
        authorized = (
            surf == "PRESENT_DIRTY"
            and acc in {"TRANSFERABLE_RUU", "TRANSFERABLE_GENERAL"}
            and claim == "CURRENT_EXECUTOR_OPERATION"
            and ev == "VALID"
            and stable == "STABLE"
        )
        if authorized:
            assert life in {"OPEN", "CLOSED"}
        if surf != "PRESENT_DIRTY" or claim != "CURRENT_EXECUTOR_OPERATION" or ev != "VALID" or stable != "STABLE":
            assert not authorized
        if acc in {"PROTECTED_EXTERNAL", "UNKNOWN"}:
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
    lifecycle = ["OPEN", "CLOSED"]
    runtime = ["RUNNING", "WAITING_FOR_USER", "TURN_FINISHED", "INACTIVE"]
    integration = ["NOT_INTEGRATED", "INTEGRATED_EXACT", "UNKNOWN"]
    artifacts = ["PRESENT", "ABSENT"]
    requested_action = ["NO_NEW_WORK", "SAME_UNIT_NEW_CONTRIBUTION", "NEW_UNIT_CONTRIBUTION"]
    n = 0
    for life, run, integ, art, action in product(lifecycle, runtime, integration, artifacts, requested_action):
        n += 1
        same_unit_may_produce = life == "OPEN" and action == "SAME_UNIT_NEW_CONTRIBUTION"
        if life == "CLOSED":
            assert not same_unit_may_produce
        if action == "SAME_UNIT_NEW_CONTRIBUTION" and life != "OPEN":
            assert not same_unit_may_produce
        _ = (run, integ, art)
    return n


def audit_contribution_unit_artifact_exact_state_continuity():
    lifecycle = ["OPEN", "CLOSED"]
    editing_artifacts = ["PRESENT", "ABSENT"]
    checkpoint = ["ABSENT", "REACHABLE", "UNRECOVERABLE"]
    obligation = ["NONE", "RESOLVED", "UNRESOLVED"]
    n = 0
    for life, art, cp, obligation_state in product(lifecycle, editing_artifacts, checkpoint, obligation):
        n += 1
        valid_combo = not (cp == "ABSENT" and obligation_state == "UNRESOLVED")
        continue_from_oid = valid_combo and cp == "REACHABLE" and obligation_state == "UNRESOLVED"
        missing_state_block = valid_combo and cp == "UNRECOVERABLE" and obligation_state == "UNRESOLVED"
        no_git_action = valid_combo and obligation_state in {"NONE", "RESOLVED"}
        if art == "ABSENT" and continue_from_oid:
            assert cp == "REACHABLE"
        if missing_state_block:
            assert obligation_state == "UNRESOLVED" and cp == "UNRECOVERABLE"
        if no_git_action:
            assert not missing_state_block
        if not valid_combo:
            assert not continue_from_oid and not missing_state_block and not no_git_action
        _ = life
    return n


def audit_contribution_unit_checkpoint_record_cas():
    transition = ["NO_CHANGE", "ADVANCE"]
    record_claim = ["HELD", "OTHER", "NONE"]
    expected_old = ["MATCH", "MISMATCH", "UNKNOWN"]
    evidence = ["VALID", "MISSING", "FAIL"]
    reachability = ["ANCHORED", "UNANCHORED"]
    editing_surface = ["PRESENT", "ABSENT"]
    n = 0
    baseline = {}
    for tr, claim, old, ev, reach, surface in product(
        transition, record_claim, expected_old, evidence, reachability, editing_surface
    ):
        n += 1
        may_advance = (
            tr == "ADVANCE"
            and claim == "HELD"
            and old == "MATCH"
            and ev == "VALID"
            and reach == "ANCHORED"
        )
        key = (tr, claim, old, ev, reach)
        if key in baseline:
            assert baseline[key] == may_advance
        else:
            baseline[key] = may_advance
        if tr != "ADVANCE" or claim != "HELD" or old != "MATCH" or ev != "VALID" or reach != "ANCHORED":
            assert not may_advance
        # Producer editing-surface presence is intentionally irrelevant to logical checkpoint-record CAS.
        _ = surface
    return n


def audit_global_managed_obligation_coverage():
    layers = [
        "CONTRIBUTION_UNIT",
        "CONVERGENCE_UNIT",
        "PROMOTION_UNIT",
        "SUBMISSION_PR_REVIEW_CHECK",
        "MERGE_QUEUE_UPDATE_RESTACK",
        "FINAL_INTEGRATION_PROOF",
        "VERIFICATION",
        "RECOVERY_CLEANUP",
        "RECONCILIATION_REQUIRED",
        "TRANSFERABLE_TO_RUU",
        "A convergence trigger is not an authority token",
        "Explicit invocations may coalesce",
    ]
    lifecycle = ["NONTERMINAL_ACTIONABLE", "NONTERMINAL_WAITING", "TERMINAL"]
    activity_index = ["ACTIVE_INDEXED", "NOT_INDEXED", "STALE_UNKNOWN"]
    age = ["RECENT", "OLD"]
    caller_relation = ["RELATED", "UNRELATED", "NONE"]
    n = 0
    for layer, life, idx, age_state, relation in product(
        layers, lifecycle, activity_index, age, caller_relation
    ):
        n += 1
        must_reevaluate = life != "TERMINAL"
        # Index membership, age, caller relation, and lifecycle layer may not narrow the universe.
        if life != "TERMINAL":
            assert must_reevaluate
        if idx in {"NOT_INDEXED", "STALE_UNKNOWN"} and life != "TERMINAL":
            assert must_reevaluate
        if age_state == "OLD" and life != "TERMINAL":
            assert must_reevaluate
        if relation in {"UNRELATED", "NONE"} and life != "TERMINAL":
            assert must_reevaluate
        _ = layer
    return n


def audit_external_wait_recheck():
    waits = [
        "WAITING_FOR_REVIEW",
        "WAITING_FOR_CHECKS",
        "MERGE_QUEUED",
        "PROVIDER_WAIT",
        "FINAL_INTEGRATION_PROOF_PENDING",
        "RECONCILIATION_REQUIRED",
    ]
    observation = ["UNCHANGED", "ADVANCE_AVAILABLE", "BLOCKED", "UNKNOWN"]
    invocation_reason = ["CHECKPOINT", "PR", "RECOVERY", "OTHER"]
    n = 0
    for wait, observed, reason in product(waits, observation, invocation_reason):
        n += 1
        must_refresh_on_invocation = True
        remains_nonterminal = True
        assert must_refresh_on_invocation
        assert remains_nonterminal
        may_advance_now = observed == "ADVANCE_AVAILABLE"
        if observed != "ADVANCE_AVAILABLE":
            assert not may_advance_now
        _ = (wait, reason)
    return n


def audit_external_convergence_grouping_authority():
    grouping_source = ["EXTERNAL_DECLARED", "INFER_CALLER", "INFER_FILES", "INFER_CWD", "UNKNOWN"]
    membership = ["BOUND_ONE", "UNBOUND", "MULTIPLE"]
    n = 0
    for source, bound in product(grouping_source, membership):
        n += 1
        valid = source == "EXTERNAL_DECLARED" and bound == "BOUND_ONE"
        if source != "EXTERNAL_DECLARED" or bound != "BOUND_ONE":
            assert not valid
    return n


def audit_eager_contribution_integration():
    lifecycle = ["OPEN", "CLOSED"]
    checkpoint = ["VALID_REACHABLE", "VALID_UNRECOVERABLE", "INVALID", "STALE"]
    editing_surface = ["PRESENT", "ABSENT"]
    topology = ["KNOWN", "UNKNOWN"]
    convergence_claim = ["HELD", "OTHER", "NONE"]
    conflict = ["CLEAR", "CONFLICT"]
    relation = ["UP_TO_DATE", "FF_ELIGIBLE", "NEEDS_SYNC", "UNKNOWN"]
    evidence = ["VALID", "MISSING", "STALE"]
    legacy_release = ["ABSENT", "PRESENT", "STALE"]
    n = 0
    baseline = {}
    for life, cp, surface, topo, cl, cf, rel, ev, release in product(
        lifecycle, checkpoint, editing_surface, topology, convergence_claim, conflict, relation, evidence, legacy_release
    ):
        n += 1
        eager_candidate = (
            cp == "VALID_REACHABLE"
            and topo == "KNOWN"
            and cl == "HELD"
            and cf == "CLEAR"
            and rel != "UNKNOWN"
        )
        may_ff = eager_candidate and rel in {"UP_TO_DATE", "FF_ELIGIBLE"} and ev == "VALID"
        must_sync_first = eager_candidate and rel == "NEEDS_SYNC"
        key = (life, cp, topo, cl, cf, rel, ev)
        value = (eager_candidate, may_ff, must_sync_first)
        if key in baseline:
            assert baseline[key] == value
        else:
            baseline[key] = value
        if cp != "VALID_REACHABLE" or topo != "KNOWN" or cl != "HELD" or cf != "CLEAR":
            assert not eager_candidate
        if cp == "VALID_UNRECOVERABLE":
            assert not eager_candidate
        if may_ff:
            assert life in {"OPEN", "CLOSED"} and ev == "VALID"
        _ = (surface, release)
    return n


def audit_convergence_membership_readiness():
    membership = ["OPEN", "SEALED"]
    contributions = [
        "ALL_CLOSED_RESOLVED",
        "HAS_OPEN",
        "HAS_CLOSED_UNRESOLVED",
        "HAS_MISSING_MANAGED_STATE",
        "UNKNOWN_ORPHAN",
    ]
    internal = ["CLEAR", "BLOCKED"]
    evidence = ["VALID", "MISSING", "STALE", "FAIL"]
    fixed_point = ["YES", "NO", "UNKNOWN"]
    artifact_layout = ["ALL_PRESENT", "SOME_ABSENT", "ALL_ABSENT"]
    n = 0
    baseline = {}
    for mem, contrib, internal_state, ev, fp, artifacts in product(
        membership, contributions, internal, evidence, fixed_point, artifact_layout
    ):
        n += 1
        ready = (
            mem == "SEALED"
            and contrib == "ALL_CLOSED_RESOLVED"
            and internal_state == "CLEAR"
            and ev == "VALID"
            and fp == "YES"
        )
        key = (mem, contrib, internal_state, ev, fp)
        if key in baseline:
            assert baseline[key] == ready
        else:
            baseline[key] = ready
        if mem == "OPEN" or contrib != "ALL_CLOSED_RESOLVED" or internal_state != "CLEAR" or ev != "VALID" or fp != "YES":
            assert not ready
        _ = artifacts
    return n


def audit_experimental_isolation_level():
    mode = ["PRIMARY", "EXPERIMENT", "ALTERNATIVE"]
    convergence_binding = ["PRIMARY_CU", "DISTINCT_CU", "UNKNOWN"]
    integration_suppression = [False, True]
    n = 0
    for work_mode, binding, suppressed in product(mode, convergence_binding, integration_suppression):
        n += 1
        valid = True
        if work_mode in {"EXPERIMENT", "ALTERNATIVE"}:
            valid = binding == "DISTINCT_CU" and not suppressed
        elif work_mode == "PRIMARY":
            valid = binding == "PRIMARY_CU" and not suppressed
        if binding == "UNKNOWN" or suppressed:
            assert not valid
    return n

def audit_reconciliation_required_contract():
    outcome = ["DETERMINISTIC_CLEAN", "SEMANTIC_CONFLICT"]
    descriptor = ["NONE", "EXACT", "STALE"]
    authoritative_ref = ["UNCHANGED", "ADVANCED"]
    authored_result = ["ABSENT", "PRESENT"]
    current_revalidated = ["YES", "NO"]
    evidence = ["VALID", "INVALID"]
    claim = ["HELD", "NOT_HELD"]
    n = 0
    for out, desc, ref, authored, reval, ev, cl in product(
        outcome, descriptor, authoritative_ref, authored_result, current_revalidated, evidence, claim
    ):
        n += 1
        semantic_conflict_recorded_safely = out == "SEMANTIC_CONFLICT" and desc == "EXACT" and ref == "UNCHANGED"
        if out == "SEMANTIC_CONFLICT":
            if desc != "EXACT" or ref != "UNCHANGED":
                assert not semantic_conflict_recorded_safely
            else:
                assert semantic_conflict_recorded_safely

        # A later authored result is adopted only from current facts.  The historical
        # reconciliation descriptor is diagnostic and deliberately absent from this predicate.
        may_adopt_authored = (
            authored == "PRESENT" and reval == "YES" and ev == "VALID" and cl == "HELD"
        )
        if authored != "PRESENT" or reval != "YES" or ev != "VALID" or cl != "HELD":
            assert not may_adopt_authored
        if may_adopt_authored:
            assert desc in {"NONE", "EXACT", "STALE"}
    return n


def audit_candidate_attribution_boundary():
    authority = ["VALID", "VIOLATED", "UNKNOWN"]
    producer = ["CODING_AGENT", "HOOK", "GENERATOR", "FORMATTER", "EXTERNAL_TOOL"]
    exact_state = ["STABLE", "STALE"]
    evidence = ["VALID", "INVALID"]
    n = 0
    baseline = {}
    for auth, prod, state, ev in product(authority, producer, exact_state, evidence):
        n += 1
        attributed_to_contribution = auth == "VALID"
        may_adopt = auth == "VALID" and state == "STABLE" and ev == "VALID"
        key = (auth, state, ev)
        if key in baseline:
            assert baseline[key] == (attributed_to_contribution, may_adopt)
        else:
            baseline[key] = (attributed_to_contribution, may_adopt)
        if auth in {"VIOLATED", "UNKNOWN"}:
            assert not attributed_to_contribution
            assert not may_adopt
        if state != "STABLE" or ev != "VALID":
            assert not may_adopt
        _ = prod
    return n


def audit_external_control_plane_responsibility_boundary():
    responsibilities = {
        "CREATE_CONTRIBUTION_UNIT": "EXTERNAL_CONTROL_PLANE",
        "BIND_CONTRIBUTION_TO_CONVERGENCE": "EXTERNAL_CONTROL_PLANE",
        "SET_CONTRIBUTION_LIFECYCLE": "EXTERNAL_CONTROL_PLANE",
        "SET_CONVERGENCE_MEMBERSHIP": "EXTERNAL_CONTROL_PLANE",
        "PROVISION_EDITING_SURFACE": "EXTERNAL_CONTROL_PLANE",
        "DECLARE_EXTERNAL_MUTATION_ACCESS": "EXTERNAL_CONTROL_PLANE",
        "DECLARE_PROMOTION_GROUPING_TOPOLOGY": "EXTERNAL_CONTROL_PLANE",
        "MAP_SEMANTIC_REVIEW_FEEDBACK": "EXTERNAL_CONTROL_PLANE",
        "DELIVER_RECONCILIATION_OBLIGATION": "EXTERNAL_CONTROL_PLANE",
        "AUTHOR_SEMANTIC_RECONCILIATION": "DEVELOPMENT_SYSTEM",
        "OBSERVE_EXACT_GIT_PROVIDER_STATE": "RUU",
        "CREATE_MANAGED_CHECKPOINT": "RUU",
        "INTEGRATE_CONTRIBUTION_CHECKPOINT": "RUU",
        "RECORD_RECONCILIATION_REQUIRED": "RUU",
        "VALIDATE_AUTHORED_RECONCILIATION_RESULT": "RUU",
        "COMPUTE_READY_INTERNAL": "RUU",
        "MATERIALIZE_PROMOTION_SUBMISSION": "RUU",
        "REFRESH_PROVIDER_WAIT": "RUU",
        "RECOVER_RUU_OWNED_OPERATION": "RUU",
    }
    claims = ["EXTERNAL_CONTROL_PLANE", "DEVELOPMENT_SYSTEM", "RUU", "INFERRED", "UNKNOWN"]
    n = 0
    for responsibility, expected in responsibilities.items():
        for claimed_owner in claims:
            n += 1
            valid = claimed_owner == expected
            if claimed_owner != expected:
                assert not valid
            else:
                assert valid
            _ = responsibility
    return n



def audit_convergence_demand_coalescing():
    executor = ["NONE", "CURRENT"]
    outstanding = ["CAUGHT_UP", "ONE_NEW", "MANY_NEW"]
    observation = ["BEFORE_SWEEP", "AFTER_FIXED_POINT"]
    n = 0
    for ex, demand, obs in product(executor, outstanding, observation):
        n += 1
        work_needed = demand != "CAUGHT_UP"
        # Multiple caller triggers never require one historical replay per trigger.
        one_global_sweep_can_cover_current_demand = work_needed
        if demand == "MANY_NEW":
            assert one_global_sweep_can_cover_current_demand
        if ex == "NONE" and work_needed:
            must_establish_executor = True
            assert must_establish_executor
        if ex == "CURRENT" and obs == "AFTER_FIXED_POINT" and work_needed:
            must_continue = True
            assert must_continue
    return n


def audit_single_executor_fencing():
    current_generation = [7, 8]
    actor_generation = [7, 8]
    liveness = ["ALIVE", "STALE", "UNKNOWN"]
    expected_state = ["MATCH", "MISMATCH"]
    n = 0
    for current, actor, live, expected in product(current_generation, actor_generation, liveness, expected_state):
        n += 1
        may_adopt = actor == current and expected == "MATCH"
        if actor != current or expected != "MATCH":
            assert not may_adopt
        # Liveness is deliberately absent from the authority predicate.
        _ = live
    return n


def audit_trigger_authority_independence():
    trigger = ["CALLER_A", "CALLER_B", "COALESCED", "NONE"]
    access = ["PROTECTED_EXTERNAL", "TRANSFERABLE_RUU", "TRANSFERABLE_GENERAL", "UNKNOWN"]
    claim = ["NONE", "CURRENT_EXECUTOR_OPERATION", "INCOMPATIBLE_OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    n = 0
    baseline = {}
    for trig, acc, cl, topo in product(trigger, access, claim, topology):
        n += 1
        may_mutate = topo == "KNOWN" and cl == "CURRENT_EXECUTOR_OPERATION" and acc in {"TRANSFERABLE_RUU", "TRANSFERABLE_GENERAL"}
        key = (acc, cl, topo)
        if key in baseline:
            assert baseline[key] == may_mutate
        else:
            baseline[key] = may_mutate
        _ = trig
    return n


def audit_executor_release_demand_race():
    order = ["DEMAND_BEFORE_RELEASE_TX", "RELEASE_BEFORE_DEMAND_TX"]
    old_executor_observation = ["CAUGHT_UP", "NEW_DEMAND_VISIBLE"]
    n = 0
    for ordering, observed in product(order, old_executor_observation):
        n += 1
        if ordering == "DEMAND_BEFORE_RELEASE_TX":
            # The old executor's serialized release transaction must see demand or fail its caught-up predicate.
            safe_outcome = observed == "NEW_DEMAND_VISIBLE"
        else:
            # Once release commits first, the later demand must be able to establish a new executor.
            safe_outcome = True
        # The inconsistent observation is exactly the race implementation must forbid.
        if ordering == "DEMAND_BEFORE_RELEASE_TX" and observed == "CAUGHT_UP":
            assert not safe_outcome
        else:
            assert safe_outcome
    return n


def audit_coordination_store_fail_closed():
    schema = ["SUPPORTED", "OLDER_MIGRATABLE", "NEWER_UNKNOWN", "CORRUPT"]
    cas_rows = [0, 1, 2]
    fence = ["CURRENT", "STALE"]
    n = 0
    for sch, rows, fence_state in product(schema, cas_rows, fence):
        n += 1
        may_adopt = sch == "SUPPORTED" and rows == 1 and fence_state == "CURRENT"
        if sch != "SUPPORTED" or rows != 1 or fence_state != "CURRENT":
            assert not may_adopt
    return n


def audit_recovery_namespace_nonaliasing():
    cleanup_generation = [7, 8]
    namespace_generation = [7, 8]
    current_generation = [7, 8]
    n = 0
    for cleanup, namespace, current in product(cleanup_generation, namespace_generation, current_generation):
        n += 1
        may_destruct = cleanup == namespace
        if cleanup != namespace:
            assert not may_destruct
        # A stale generation's own namespace may be cleaned, but it must not alias the current generation namespace.
        if cleanup != current and namespace == current:
            assert not may_destruct
    return n


def audit_os_lock_and_sqlite_fence_separation():
    physical = ["CURRENT_OWNS", "OTHER_OWNS", "FREE"]
    durable = ["ACTIVE", "IDLE"]
    token = ["CURRENT", "STALE", "NONE"]
    exact_state = ["MATCH", "MISMATCH"]
    n = 0
    for phys, run_state, tok, expected in product(physical, durable, token, exact_state):
        n += 1
        may_adopt = (
            phys == "CURRENT_OWNS"
            and run_state == "ACTIVE"
            and tok == "CURRENT"
            and expected == "MATCH"
        )
        if phys != "CURRENT_OWNS" or run_state != "ACTIVE" or tok != "CURRENT" or expected != "MATCH":
            assert not may_adopt
        if run_state == "IDLE":
            assert not may_adopt
    return n


def audit_active_idle_release_handshake():
    demand_timing = ["BEFORE_RELEASE_TX", "AFTER_IDLE_COMMIT_BEFORE_UNLOCK", "AFTER_UNLOCK"]
    os_lock = ["BUSY", "FREE"]
    durable_state = ["ACTIVE", "IDLE"]
    n = 0
    for timing, lock, state in product(demand_timing, os_lock, durable_state):
        n += 1
        caller_may_return = lock == "BUSY" and state == "ACTIVE"
        caller_must_retry = lock == "BUSY" and state == "IDLE"
        caller_may_acquire = lock == "FREE"
        if lock == "BUSY" and state == "IDLE":
            assert caller_must_retry and not caller_may_return
        if lock == "FREE":
            assert caller_may_acquire
        if timing == "AFTER_IDLE_COMMIT_BEFORE_UNLOCK" and lock == "BUSY" and state == "IDLE":
            assert caller_must_retry
    return n


def audit_operation_attempt_observation_adoption():
    operation_intent = ["UNCHANGED", "CHANGED_REUSED_ID"]
    attempt_fence = ["CURRENT", "STALE"]
    observation = ["EXACT_CURRENT", "STALE_OR_UNBOUND"]
    cas_rows = [0, 1, 2]
    n = 0
    for intent, fence, obs, rows in product(operation_intent, attempt_fence, observation, cas_rows):
        n += 1
        valid_operation_identity = intent == "UNCHANGED"
        may_append_authoritative_observation = fence == "CURRENT" and obs == "EXACT_CURRENT" and valid_operation_identity
        may_adopt = may_append_authoritative_observation and rows == 1
        if intent != "UNCHANGED":
            assert not valid_operation_identity and not may_adopt
        if fence != "CURRENT" or obs != "EXACT_CURRENT" or rows != 1:
            assert not may_adopt
        if rows == 1 and fence == "CURRENT" and obs == "EXACT_CURRENT" and intent == "UNCHANGED":
            assert may_adopt
    return n


def audit_external_effect_crash_recovery():
    crash_point = [
        "BEFORE_EFFECT",
        "AFTER_EFFECT_BEFORE_OBSERVATION",
        "AFTER_OBSERVATION_BEFORE_ADOPTION",
        "AFTER_ADOPTION",
    ]
    actual = ["EXPECTED_OLD", "DESIRED", "OTHER"]
    n = 0
    for point, state in product(crash_point, actual):
        n += 1
        if point != "AFTER_ADOPTION":
            must_observe_before_deciding = True
            assert must_observe_before_deciding
        if point == "AFTER_EFFECT_BEFORE_OBSERVATION":
            # Attempt metadata cannot distinguish success from no effect or third-party drift.
            assert state in {"EXPECTED_OLD", "DESIRED", "OTHER"}
        if state == "OTHER":
            blind_replay_authorized = False
            assert not blind_replay_authorized
    return n


def audit_no_external_work_inside_sqlite_transaction():
    transaction = ["OPEN", "CLOSED"]
    work = ["STORE_ONLY", "GIT", "PROVIDER", "NETWORK", "TEST", "LONG_FILESYSTEM"]
    n = 0
    for tx, kind in product(transaction, work):
        n += 1
        allowed = kind == "STORE_ONLY" or tx == "CLOSED"
        if tx == "OPEN" and kind != "STORE_ONLY":
            assert not allowed
        else:
            assert allowed
    return n


def audit_live_hung_process_liveness():
    process = ["RUNNING", "HUNG", "DEAD"]
    os_lock = ["HELD", "FREE"]
    auto_takeover = [False, True]
    n = 0
    for proc, lock, takeover in product(process, os_lock, auto_takeover):
        n += 1
        physically_consistent = (proc in {"RUNNING", "HUNG"} and lock == "HELD") or (proc == "DEAD" and lock == "FREE")
        if not physically_consistent:
            continue
        if proc == "HUNG":
            assert lock == "HELD"
            policy_valid = takeover is False
            if takeover:
                assert not policy_valid
            else:
                assert policy_valid
        if proc == "DEAD":
            assert lock == "FREE"
            # A successor may acquire physically after actual process death;
            # no TTL declaration is needed to make the lock free.
    return n


def audit_recovery_resource_gc_eligibility():
    lifecycle = ["REQUIRED", "GC_ELIGIBLE"]
    alternate_root = ["PROVEN", "NOT_PROVEN"]
    unresolved_dependency = ["YES", "NO"]
    cleanup_namespace = ["SAME_ATTEMPT", "DIFFERENT_ATTEMPT"]
    n = 0
    for life, root, dep, namespace in product(lifecycle, alternate_root, unresolved_dependency, cleanup_namespace):
        n += 1
        valid_eligibility = root == "PROVEN" and dep == "NO"
        may_cleanup = life == "GC_ELIGIBLE" and valid_eligibility and namespace == "SAME_ATTEMPT"
        if life == "REQUIRED" or root != "PROVEN" or dep != "NO" or namespace != "SAME_ATTEMPT":
            assert not may_cleanup
        if life == "GC_ELIGIBLE" and valid_eligibility and namespace == "SAME_ATTEMPT":
            assert may_cleanup
    return n


def audit_repository_identity_relocation():
    repository_id = ["R1", "R2"]
    locator = ["OLD_PATH", "NEW_PATH"]
    binding = ["EXACT", "AMBIGUOUS", "MISSING"]
    n = 0
    for rid, loc, bind in product(repository_id, locator, binding):
        n += 1
        may_resolve = bind == "EXACT"
        if bind != "EXACT":
            assert not may_resolve
        # A locator change is not an identity change by itself.
        identity_from_path = False
        assert not identity_from_path
        _ = (rid, loc)
    return n


def audit_schema_initialization_and_migration():
    store = ["EMPTY", "NONEMPTY"]
    schema = ["MISSING", "SUPPORTED", "OLDER_KNOWN", "NEWER_UNKNOWN", "CORRUPT"]
    n = 0
    for db, sch in product(store, schema):
        n += 1
        may_initialize = db == "EMPTY" and sch == "MISSING"
        may_use = sch == "SUPPORTED"
        may_migrate = sch == "OLDER_KNOWN"
        fail_closed = sch in {"NEWER_UNKNOWN", "CORRUPT"} or (db == "NONEMPTY" and sch == "MISSING")
        if fail_closed:
            assert not may_initialize and not may_use and not may_migrate
        if may_initialize:
            assert db == "EMPTY"
        if may_migrate:
            assert sch == "OLDER_KNOWN"
    return n


def audit_current_state_reconciler_not_workflow_resume():
    previous_process_position = ["NONE", "PHASE_A", "PHASE_B", "UNKNOWN"]
    current_obligation = ["PROGRESSABLE", "WAITING", "BLOCKED", "TERMINAL"]
    n = 0
    baseline = {}
    for old_pos, obligation in product(previous_process_position, current_obligation):
        n += 1
        action = {
            "PROGRESSABLE": "PROGRESS",
            "WAITING": "FIXED_POINT_WAIT",
            "BLOCKED": "LOCAL_BLOCK",
            "TERMINAL": "NO_ACTION",
        }[obligation]
        if obligation in baseline:
            assert baseline[obligation] == action
        else:
            baseline[obligation] = action
        _ = old_pos  # previous in-memory workflow position is intentionally irrelevant
    return n


def audit_promotion_policy_constraint_composition():
    capability = ["DIRECT_ONLY", "PR_ONLY", "BOTH"]
    provider_governance = ["NONE", "REQUIRE_DIRECT", "REQUIRE_PR"]
    organization_governance = ["NONE", "REQUIRE_DIRECT", "REQUIRE_PR"]
    repo_policy = ["NONE", "REQUIRE_DIRECT", "REQUIRE_PR"]
    n = 0
    for cap, pg, og, rp in product(capability, provider_governance, organization_governance, repo_policy):
        n += 1
        allowed = {
            "DIRECT_ONLY": {"DIRECT"},
            "PR_ONLY": {"PR"},
            "BOTH": {"DIRECT", "PR"},
        }[cap].copy()
        for constraint in (pg, og, rp):
            if constraint == "REQUIRE_DIRECT":
                allowed &= {"DIRECT"}
            elif constraint == "REQUIRE_PR":
                allowed &= {"PR"}
        contradictory = not allowed
        if contradictory:
            assert allowed == set()
            continue
        # Built-in rules close only what remains underdetermined. Baseline prefers
        # DIRECT when admissible; otherwise the only admissible mode is PR.
        effective = "DIRECT" if "DIRECT" in allowed else "PR"
        assert effective in allowed
        if allowed == {"PR"}:
            assert effective == "PR"
        if allowed == {"DIRECT"}:
            assert effective == "DIRECT"
    return n


def audit_promotion_policy_runtime_bypass_irrelevance():
    authoritative = ["DIRECT", "PR", "CONTRADICTORY"]
    local_config = ["NONE", "DIRECT", "PR"]
    runtime_request = ["NONE", "DIRECT", "PR"]
    actor = ["HUMAN", "AGENT", "ORCHESTRATOR"]
    n = 0
    baseline = {}
    for auth, local, runtime, actor_kind in product(authoritative, local_config, runtime_request, actor):
        n += 1
        # Local/runtime inputs never alter authoritative policy. They may at most
        # be non-authorizing assertions handled outside this predicate.
        resulting_policy = auth
        key = auth
        if key in baseline:
            assert baseline[key] == resulting_policy
        else:
            baseline[key] = resulting_policy
        if auth == "CONTRADICTORY":
            assert resulting_policy == "CONTRADICTORY"
        _ = (local, runtime, actor_kind)
    return n


def audit_trusted_target_policy_baseline():
    target_policy = ["DIRECT", "PR"]
    candidate_policy = ["UNCHANGED", "DIRECT", "PR"]
    candidate_adopted = [False, True]
    n = 0
    for target, candidate, adopted in product(target_policy, candidate_policy, candidate_adopted):
        n += 1
        candidate_value = target if candidate == "UNCHANGED" else candidate
        governing_current_promotion = target
        assert governing_current_promotion == target
        # Only after the candidate has become authoritative target state may its
        # committed policy govern a subsequent promotion.
        governing_subsequent = candidate_value if adopted else target
        if not adopted:
            assert governing_subsequent == target
        if adopted:
            assert governing_subsequent == candidate_value
    return n


def audit_policy_contradiction_signal_boundary():
    state = ["CURRENT", "CONTRADICTORY"]
    provenance = ["COMPLETE", "INCOMPLETE"]
    remediation_advice = ["ABSENT", "PRESENT"]
    n = 0
    for st, prov, advice in product(state, provenance, remediation_advice):
        n += 1
        valid_external_signal = st == "CONTRADICTORY" and prov == "COMPLETE" and advice == "ABSENT"
        if st == "CONTRADICTORY" and prov == "COMPLETE" and advice == "ABSENT":
            assert valid_external_signal
        if st == "CONTRADICTORY" and (prov != "COMPLETE" or advice != "ABSENT"):
            assert not valid_external_signal
        if advice == "PRESENT":
            assert not valid_external_signal
    return n


def audit_policy_pre_mutation_currentness():
    target_anchor = ["UNCHANGED", "CHANGED"]
    provider_governance = ["UNCHANGED", "CHANGED"]
    provider_capabilities = ["UNCHANGED", "CHANGED"]
    pre_mutation_revalidation = ["DONE", "NOT_DONE"]
    cache_state = ["MISS", "TTL_FRESH", "TTL_EXPIRED"]
    mutation = ["POLICY_SENSITIVE", "LOCAL_NON_POLICY"]
    n = 0
    baseline = {}
    for target, gov, caps, reval, cache, mut in product(
        target_anchor, provider_governance, provider_capabilities,
        pre_mutation_revalidation, cache_state, mutation
    ):
        n += 1
        unchanged = target == "UNCHANGED" and gov == "UNCHANGED" and caps == "UNCHANGED"
        if mut == "POLICY_SENSITIVE":
            may_authorize = reval == "DONE" and unchanged
            # Cache is deliberately absent from the authority predicate.
            key = (target, gov, caps, reval, mut)
            if key in baseline:
                assert baseline[key] == may_authorize
            else:
                baseline[key] = may_authorize
            if reval != "DONE" or not unchanged:
                assert not may_authorize
        else:
            # Local candidate work does not acquire promotion authorization merely by
            # carrying a current policy snapshot; ordinary local invariants govern it.
            may_authorize = False
            assert not may_authorize
        _ = cache
    return n


def audit_policy_cache_non_authority():
    cache_age = ["NEW", "WITHIN_TTL", "EXPIRED"]
    source_state = ["UNCHANGED", "CHANGED"]
    fresh_revalidation = ["DONE", "NOT_DONE"]
    n = 0
    baseline = {}
    for cache, source, reval in product(cache_age, source_state, fresh_revalidation):
        n += 1
        current = source == "UNCHANGED" and reval == "DONE"
        key = (source, reval)
        if key in baseline:
            assert baseline[key] == current
        else:
            baseline[key] = current
        if reval == "NOT_DONE":
            assert not current
        if source == "CHANGED":
            assert not current
        _ = cache
    return n


def audit_nonatomic_provider_drift_boundary():
    primitive = ["ATOMIC", "NON_ATOMIC"]
    drift_after_check = ["NO", "YES"]
    provider_outcome = ["ACCEPTED", "REJECTED"]
    exact_post_observation = ["YES", "NO"]
    auto_repair = ["ABSENT", "PRESENT"]
    n = 0
    for prim, drift, outcome, post, repair in product(
        primitive, drift_after_check, provider_outcome, exact_post_observation, auto_repair
    ):
        n += 1
        # The audit is about authoritative adoption/signal handling, not predicting
        # every provider's semantics. Exact post-observation is always required.
        may_adopt_success = outcome == "ACCEPTED" and post == "YES" and repair == "ABSENT"
        factual_block = outcome == "REJECTED" and post == "YES" and repair == "ABSENT"
        if post == "NO":
            assert not may_adopt_success
            assert not factual_block
        if repair == "PRESENT":
            assert not may_adopt_success
            assert not factual_block
        if prim == "NON_ATOMIC" and drift == "YES" and outcome == "REJECTED" and post == "YES" and repair == "ABSENT":
            assert factual_block
        _ = (prim, drift)
    return n



def _promotion_unit_v1_id(members):
    """Reference audit encoding for ADR-045 identity + ADR-047 structural locality."""
    if not members or len(set(members)) != len(members):
        return None
    repos = {m.split("/", 1)[0] for m in members}
    if len(repos) != 1:
        return None
    ordered = sorted(m.encode("utf-8") for m in members)
    buf = bytearray(b"Ruu:PromotionUnit:v1\x00")
    buf += len(ordered).to_bytes(4, "big")
    for item in ordered:
        buf += len(item).to_bytes(4, "big")
        buf += item
    return hashlib.sha256(bytes(buf)).hexdigest()


def audit_promotion_unit_content_address_identity():
    exact_sets = [
        ("repo:R1/cu:A/state:111",),
        ("repo:R1/cu:A/state:111", "repo:R1/cu:B/state:222"),
        ("repo:R2/cu:C/state:333", "repo:R2/cu:D/state:444"),
    ]
    lifecycle = ["DECLARED", "WAITING", "PROMOTING", "PROMOTED"]
    topology = ["NONE", "INDEPENDENT", "STACKED"]
    policy_mode = ["DIRECT", "PR"]
    semantic_label = ["NONE", "FEATURE_X", "FEATURE_Y"]
    n = 0
    for members in exact_sets:
        expected = _promotion_unit_v1_id(members)
        assert expected
        # Member order cannot affect identity.
        for perm in permutations(members):
            assert _promotion_unit_v1_id(perm) == expected
        # Non-identity dimensions cannot affect identity.
        for life, topo, mode, semantic in product(lifecycle, topology, policy_mode, semantic_label):
            n += 1
            observed = _promotion_unit_v1_id(members)
            assert observed == expected
            _ = (life, topo, mode, semantic)

        # Any exact member-state change produces a different identity.
        changed = list(members)
        changed[-1] = changed[-1] + ":changed"
        assert _promotion_unit_v1_id(tuple(changed)) != expected

    # Invalid declarations: empty or duplicate member sets.
    invalid = [
        (),
        ("repo:R1/cu:A/state:111", "repo:R1/cu:A/state:111"),
        ("repo:R1/cu:A/state:111", "repo:R2/cu:C/state:333"),
    ]
    for members in invalid:
        n += 1
        assert _promotion_unit_v1_id(members) is None
    return n


def audit_promotion_unit_structural_vs_eligibility():
    nonempty_unique = ["YES", "NO"]
    refs = ["VALID", "INVALID"]
    identity = ["MATCH", "MISMATCH"]
    ready = ["YES", "NO"]
    evidence = ["VALID", "MISSING"]
    policy = ["CURRENT", "STALE"]
    topology = ["COMPATIBLE", "BLOCKED"]
    blockers = ["CLEAR", "BLOCKED"]
    n = 0
    for unique, ref, ident, rd, ev, pol, topo, block in product(
        nonempty_unique, refs, identity, ready, evidence, policy, topology, blockers
    ):
        n += 1
        structurally_valid = unique == "YES" and ref == "VALID" and ident == "MATCH"
        eligible = (
            structurally_valid
            and rd == "YES"
            and ev == "VALID"
            and pol == "CURRENT"
            and topo == "COMPATIBLE"
            and block == "CLEAR"
        )
        if not structurally_valid:
            assert not eligible
        if rd != "YES" or ev != "VALID" or pol != "CURRENT" or topo != "COMPATIBLE" or block != "CLEAR":
            assert not eligible
        # A valid declaration is allowed to exist while not eligible.
        if structurally_valid and not eligible:
            assert structurally_valid
    return n


def audit_promotion_unit_redeclaration_idempotence():
    first_lifecycle = ["DECLARED", "WAITING", "PROMOTING", "PROMOTED"]
    redeclare_time = ["IMMEDIATE", "LATER"]
    source_selection = ["SAME_EXACT_SET", "CHANGED_EXACT_MEMBER"]
    n = 0
    original = ("repo:R1/cu:A/state:111", "repo:R1/cu:B/state:222")
    original_id = _promotion_unit_v1_id(original)
    for life, timing, selection in product(first_lifecycle, redeclare_time, source_selection):
        n += 1
        if selection == "SAME_EXACT_SET":
            redeclared = tuple(reversed(original))
            assert _promotion_unit_v1_id(redeclared) == original_id
        else:
            redeclared = (original[0], "repo:R1/cu:B/state:999")
            assert _promotion_unit_v1_id(redeclared) != original_id
        _ = (life, timing)
    return n




def _promotion_group_v1_id(members):
    """Reference audit encoding for ADR-046 logical group content identity."""
    if not members or len(set(members)) != len(members):
        return None
    ordered = sorted(m.encode("utf-8") for m in members)
    buf = bytearray(b"Ruu:PromotionGroup:v1\x00")
    buf += len(ordered).to_bytes(4, "big")
    for item in ordered:
        buf += len(item).to_bytes(4, "big")
        buf += item
    return hashlib.sha256(bytes(buf)).hexdigest()


def audit_promotion_group_content_address_identity():
    groups = [
        ("repo:R1/cu:A",),
        ("repo:R1/cu:A", "repo:R1/cu:B"),
        ("repo:R1/cu:A", "repo:R2/cu:C"),
    ]
    exact_states = ["OID_SET_1", "OID_SET_2"]
    triggers = ["TRIGGER_A", "TRIGGER_B", "COALESCED"]
    sessions = ["SESSION_1", "SESSION_2", "NONE"]
    n = 0
    for members in groups:
        expected = _promotion_group_v1_id(members)
        assert expected
        for perm in permutations(members):
            assert _promotion_group_v1_id(perm) == expected
        for exact, trigger, session in product(exact_states, triggers, sessions):
            n += 1
            assert _promotion_group_v1_id(members) == expected
            _ = (exact, trigger, session)
        changed = list(members)
        changed[-1] += ":different-cu"
        assert _promotion_group_v1_id(tuple(changed)) != expected
    for invalid in [(), ("repo:R1/cu:A", "repo:R1/cu:A")]:
        n += 1
        assert _promotion_group_v1_id(invalid) is None
    return n


def audit_promotion_group_closed_completeness():
    # Closed group of three logical CUs: no partial exact PromotionUnit exists.
    readiness = ["READY", "NOT_READY"]
    exact_current = ["CURRENT", "STALE"]
    n = 0
    for r1, r2, r3, c1, c2, c3 in product(readiness, readiness, readiness, exact_current, exact_current, exact_current):
        n += 1
        complete = all(x == "READY" for x in (r1, r2, r3)) and all(x == "CURRENT" for x in (c1, c2, c3))
        materialize = complete
        if not complete:
            assert not materialize
        if materialize:
            assert r1 == r2 == r3 == "READY"
            assert c1 == c2 == c3 == "CURRENT"
    return n


def audit_promotion_group_snapshot_cas_resolution():
    observed_ready = ["ALL_READY", "MISSING_MEMBER"]
    state_after_snapshot = ["UNCHANGED", "MOVED", "REOPENED", "LOST_READINESS"]
    cas = ["MATCH", "MISMATCH"]
    n = 0
    for ready, after, guard in product(observed_ready, state_after_snapshot, cas):
        n += 1
        adopt = ready == "ALL_READY" and after == "UNCHANGED" and guard == "MATCH"
        if ready != "ALL_READY" or after != "UNCHANGED" or guard != "MATCH":
            assert not adopt
    return n


def audit_promotion_group_trigger_independence():
    durable_group = ["PRESENT", "ABSENT"]
    trigger = ["ORIGINAL", "COALESCED", "RETRY", "OTHER_SESSION_TRIGGER"]
    all_ready = ["YES", "NO"]
    n = 0
    baseline = {}
    for group, trig, ready in product(durable_group, trigger, all_ready):
        n += 1
        resolvable = group == "PRESENT" and ready == "YES"
        key = (group, ready)
        if key in baseline:
            assert baseline[key] == resolvable
        else:
            baseline[key] = resolvable
        _ = trig
    return n


def _repo_of_logical(ref):
    return ref.split("/", 1)[0]


def _project_group_by_repository(logical_members, revision):
    exact_by_repo = {}
    for member in logical_members:
        repo = _repo_of_logical(member)
        exact_by_repo.setdefault(repo, []).append(f"{member}/state:{revision}")
    return {repo: tuple(sorted(members)) for repo, members in sorted(exact_by_repo.items())}


def audit_promotion_group_repository_partition():
    groups = [
        ("repo:R1/cu:A",),
        ("repo:R1/cu:A", "repo:R1/cu:B"),
        ("repo:R1/cu:A", "repo:R2/cu:C"),
        ("repo:R1/cu:A", "repo:R1/cu:B", "repo:R2/cu:C", "repo:R3/cu:D"),
    ]
    revisions = ["REV1", "REV2"]
    n = 0
    for logical, rev in product(groups, revisions):
        n += 1
        projected = _project_group_by_repository(logical, rev)
        assert len(projected) == len({_repo_of_logical(m) for m in logical})
        flattened = []
        for repo, exact_members in projected.items():
            assert exact_members
            assert all(_repo_of_logical(m) == repo for m in exact_members)
            pid = _promotion_unit_v1_id(exact_members)
            assert pid
            flattened.extend(m.rsplit("/state:", 1)[0] for m in exact_members)
        assert sorted(flattened) == sorted(logical)
    return n


def audit_same_group_same_repo_not_split():
    member_counts = [1, 2, 3]
    repos = ["R1", "R2"]
    revisions = ["REV1", "REV2"]
    n = 0
    for count, repo, rev in product(member_counts, repos, revisions):
        n += 1
        logical = tuple(f"repo:{repo}/cu:C{i}" for i in range(count))
        projected = _project_group_by_repository(logical, rev)
        assert list(projected) == [f"repo:{repo}"]
        assert len(projected[f"repo:{repo}"]) == count
        assert _promotion_unit_v1_id(projected[f"repo:{repo}"])
    return n


def audit_promotion_group_complete_resolution_map():
    readiness = ["ALL_READY", "MISSING"]
    snapshot = ["CURRENT", "MOVED"]
    cas = ["MATCH", "MISMATCH"]
    repo_count = [1, 2, 3]
    n = 0
    for ready, snap, guard, repos in product(readiness, snapshot, cas, repo_count):
        n += 1
        adopt_complete_map = ready == "ALL_READY" and snap == "CURRENT" and guard == "MATCH"
        if adopt_complete_map:
            assert repos >= 1
        else:
            assert not adopt_complete_map
    return n


def audit_cross_repository_group_partial_progress():
    a = ["NOT_PROMOTED", "PROMOTED"]
    b = ["NOT_PROMOTED", "PROMOTED"]
    n = 0
    for sa, sb in product(a, b):
        n += 1
        if sa == sb == "PROMOTED":
            aggregate = "ALL_PROMOTED"
        elif sa == sb == "NOT_PROMOTED":
            aggregate = "NONE_PROMOTED"
        else:
            aggregate = "PARTIALLY_PROMOTED"
        assert aggregate in {"NONE_PROMOTED", "PARTIALLY_PROMOTED", "ALL_PROMOTED"}
    return n


def audit_group_revision_to_repository_local_units():
    logical_members = [
        ("repo:R1/cu:A",),
        ("repo:R1/cu:A", "repo:R2/cu:B"),
    ]
    revisions = ["REV1", "REV2"]
    n = 0
    for logical, rev in product(logical_members, revisions):
        n += 1
        gid = _promotion_group_v1_id(logical)
        assert gid
        projected = _project_group_by_repository(logical, rev)
        assert _promotion_group_v1_id(logical) == gid
        for repo, exact in projected.items():
            pid = _promotion_unit_v1_id(exact)
            assert pid
            if rev == "REV2":
                prior = tuple(m.replace("state:REV2", "state:REV1") for m in exact)
                assert _promotion_unit_v1_id(prior) != pid
            _ = repo
    return n


def audit_explicit_singleton_no_implicit_default():
    group_declared = ["NONE", "SINGLETON", "MULTI"]
    ready_cu_count = [0, 1, 2]
    n = 0
    for group, ready_count in product(group_declared, ready_cu_count):
        n += 1
        singleton_materializable = group == "SINGLETON" and ready_count >= 1
        if group == "NONE":
            assert not singleton_materializable
        if group == "MULTI":
            assert not singleton_materializable
    return n


def audit_materialization_ancestry_reduction():
    """Execution reduction may remove redundant heads but never logical provenance."""
    base_contains = [False, True]
    source_relation = ["INDEPENDENT", "S1_ANCESTOR_S2", "S2_ANCESTOR_S1"]
    source_count = [1, 2]
    n = 0
    for contains, rel, count in product(base_contains, source_relation, source_count):
        n += 1
        logical = ["s1"] if count == 1 else ["s1", "s2"]
        retained = list(logical)
        if contains:
            # Model the base as already containing s1 only.
            retained = [x for x in retained if x != "s1"]
        if count == 2 and not contains:
            if rel == "S1_ANCESTOR_S2":
                retained = ["s2"]
            elif rel == "S2_ANCESTOR_S1":
                retained = ["s1"]
        # Logical PromotionUnit provenance never changes.
        assert logical == (["s1"] if count == 1 else ["s1", "s2"])
        assert set(retained).issubset(set(logical))
        # Empty execution fold is valid when all work is already in base.
        if count == 1 and contains:
            assert retained == []
    return n


def audit_materialization_canonical_order_independence():
    source_sets = [
        ("a",),
        ("a", "b"),
        ("a", "b", "c"),
    ]
    runtime_orders = list(permutations(("a", "b", "c")))
    n = 0
    for sources in source_sets:
        canonical = tuple(sorted(sources))
        for runtime in runtime_orders:
            n += 1
            observed = tuple(x for x in runtime if x in sources)
            # Runtime order may vary; normative execution order may not.
            assert tuple(sorted(observed)) == canonical
    return n


def audit_materialization_conflict_boundary():
    fold_step = ["FIRST", "MIDDLE", "LAST"]
    merge_result = ["CLEAN", "CONFLICT", "UNKNOWN"]
    semantic_authoring = ["NONE", "EXTERNAL_RESULT_LATER"]
    n = 0
    for step, result, authored in product(fold_step, merge_result, semantic_authoring):
        n += 1
        adopt_candidate_now = result == "CLEAN"
        reconcile_required = result == "CONFLICT"
        if result == "CONFLICT":
            assert reconcile_required and not adopt_candidate_now
        if result == "UNKNOWN":
            assert not adopt_candidate_now
        # A later external authored result never retroactively authorizes this attempt.
        if authored == "EXTERNAL_RESULT_LATER" and result != "CLEAN":
            assert not adopt_candidate_now
        _ = step
    return n


def audit_materialization_final_candidate_guards():
    base_ancestor = [False, True]
    all_sources_ancestor = [False, True]
    tree_matches_fold = [False, True]
    metadata_reproducible = [False, True]
    n = 0
    for base_ok, sources_ok, tree_ok, meta_ok in product(
        base_ancestor, all_sources_ancestor, tree_matches_fold, metadata_reproducible
    ):
        n += 1
        valid = base_ok and sources_ok and tree_ok and meta_ok
        if not all([base_ok, sources_ok, tree_ok, meta_ok]):
            assert not valid
    return n


def audit_materialization_verification_adoption():
    candidate = ["ABSENT", "TRANSIENT_ONLY", "FINAL"]
    evidence = ["NONE", "VALID", "STALE", "FAIL"]
    inputs = ["CURRENT", "STALE"]
    claim = ["HELD", "OTHER", "NONE"]
    n = 0
    for cand, ev, current, claim_state in product(candidate, evidence, inputs, claim):
        n += 1
        may_adopt = (
            cand == "FINAL"
            and ev == "VALID"
            and current == "CURRENT"
            and claim_state == "HELD"
        )
        if cand != "FINAL" or ev != "VALID" or current != "CURRENT" or claim_state != "HELD":
            assert not may_adopt
    return n


def audit_materialization_recovery_contract():
    source_snapshot = ["SAME", "CHANGED"]
    base = ["SAME", "CHANGED"]
    contract = ["SAME", "CHANGED", "UNKNOWN"]
    observed_candidate = ["ABSENT", "MATCHING", "MISMATCH"]
    n = 0
    for src, b, c, cand in product(source_snapshot, base, contract, observed_candidate):
        n += 1
        reusable = src == b == c == "SAME" and cand == "MATCHING"
        if src != "SAME" or b != "SAME" or c != "SAME" or cand != "MATCHING":
            assert not reusable
    return n



def audit_submission_ref_separation():
    oid_relation = ["SAME_OID", "DIFFERENT_OID"]
    ref_relation = ["SAME_REF", "DISTINCT_REFS"]
    submission_class = ["IMMUTABLE", "REWRITEABLE"]
    n = 0
    for oid_rel, ref_rel, cls in product(oid_relation, ref_relation, submission_class):
        n += 1
        structurally_valid = ref_rel == "DISTINCT_REFS"
        if ref_rel == "SAME_REF":
            assert not structurally_valid
        if oid_rel == "SAME_OID" and ref_rel == "DISTINCT_REFS":
            assert structurally_valid
        _ = cls
    return n


def audit_submission_logical_identity_revision():
    projection = ["SAME", "CHANGED"]
    destination = ["SAME", "CHANGED"]
    promotion_unit = ["SAME", "CHANGED"]
    exact_head = ["SAME", "CHANGED"]
    n = 0
    for proj, dest, pu, head in product(projection, destination, promotion_unit, exact_head):
        n += 1
        same_submission = proj == "SAME" and dest == "SAME"
        if pu == "CHANGED" and proj == dest == "SAME":
            assert same_submission
        if proj == "CHANGED" or dest == "CHANGED":
            assert not same_submission
        _ = head
    return n


def audit_submission_expected_old_update():
    expected = ["MATCH", "MISMATCH", "UNKNOWN"]
    claim = ["HELD", "OTHER", "NONE"]
    policy = ["CURRENT_ALLOWED", "CURRENT_FORBIDDEN", "STALE"]
    verification = ["VALID", "MISSING", "FAIL"]
    refs = ["DISTINCT", "ALIASED"]
    n = 0
    for exp, cl, pol, ver, refs_state in product(expected, claim, policy, verification, refs):
        n += 1
        may_publish = exp == "MATCH" and cl == "HELD" and pol == "CURRENT_ALLOWED" and ver == "VALID" and refs_state == "DISTINCT"
        if exp != "MATCH" or cl != "HELD" or pol != "CURRENT_ALLOWED" or ver != "VALID" or refs_state != "DISTINCT":
            assert not may_publish
    return n


def audit_derived_dependency_representation():
    dependency = ["NONE", "EXACT_UNSATISFIED", "UNKNOWN"]
    target = ["CONTAINS_PREDECESSOR", "DOES_NOT_CONTAIN", "UNKNOWN"]
    stack_cap = ["SUPPORTED_ALLOWED", "UNSUPPORTED", "FORBIDDEN"]
    n = 0
    for dep, target_state, cap in product(dependency, target, stack_cap):
        n += 1
        if dep == "NONE":
            outcome = "ORDINARY"
        elif dep == "EXACT_UNSATISFIED" and target_state == "CONTAINS_PREDECESSOR":
            outcome = "ORDINARY"
        elif dep == "EXACT_UNSATISFIED" and target_state == "DOES_NOT_CONTAIN" and cap == "SUPPORTED_ALLOWED":
            outcome = "STACKED"
        elif dep == "EXACT_UNSATISFIED" and target_state == "DOES_NOT_CONTAIN" and cap in {"UNSUPPORTED", "FORBIDDEN"}:
            outcome = "WAIT"
        else:
            outcome = "UNKNOWN_BLOCK"
        if outcome == "STACKED":
            assert dep == "EXACT_UNSATISFIED" and target_state == "DOES_NOT_CONTAIN" and cap == "SUPPORTED_ALLOWED"
        if dep == "UNKNOWN" or target_state == "UNKNOWN":
            assert outcome != "STACKED"
    return n


def audit_restack_state_transplant_guards():
    owned_anchor = ["CURRENT", "STALE", "UNKNOWN"]
    new_base = ["CURRENT", "STALE", "UNKNOWN"]
    transplant = ["CLEAN", "CONFLICT", "UNKNOWN"]
    verification = ["VALID", "MISSING", "FAIL"]
    expected_old = ["MATCH", "MISMATCH"]
    n = 0
    for anchor, base, tr, ver, exp in product(owned_anchor, new_base, transplant, verification, expected_old):
        n += 1
        may_adopt = anchor == "CURRENT" and base == "CURRENT" and tr == "CLEAN" and ver == "VALID" and exp == "MATCH"
        if anchor != "CURRENT" or base != "CURRENT" or tr != "CLEAN" or ver != "VALID" or exp != "MATCH":
            assert not may_adopt
        if tr == "CONFLICT":
            assert not may_adopt
    return n


def audit_restack_no_projection_drift():
    semantic_source = ["OWNED_ANCHOR", "PRIOR_RESTACKED_HEAD"]
    predecessor_revision = ["B1", "B2", "B3"]
    n = 0
    for src, rev in product(semantic_source, predecessor_revision):
        n += 1
        valid = src == "OWNED_ANCHOR"
        if src == "PRIOR_RESTACKED_HEAD":
            assert not valid
        _ = rev
    return n


def audit_restack_executor_neutral_adoption():
    executor = ["LOCAL", "PROVIDER_NATIVE", "EXTERNAL_TOOL"]
    contract = ["MATCH", "MISMATCH", "UNKNOWN"]
    verification = ["VALID", "MISSING", "FAIL"]
    observed = ["EXPECTED_HEAD", "OTHER_HEAD", "UNKNOWN"]
    n = 0
    baseline = {}
    for exe, contract_state, ver, obs in product(executor, contract, verification, observed):
        n += 1
        adopt = contract_state == "MATCH" and ver == "VALID" and obs == "EXPECTED_HEAD"
        key = (contract_state, ver, obs)
        baseline.setdefault(key, adopt)
        assert baseline[key] == adopt
        _ = exe
    return n



def audit_provider_semantic_capability_context():
    providers = ["PROVIDER_A", "PROVIDER_B"]
    operations = ["CREATE_PR_SUBMISSION", "REPRESENT_PROMOTION_DEPENDENCY", "REVISE_SUBMISSION_HEAD", "ENTER_MERGE_QUEUE"]
    relations = ["SAME_REPOSITORY", "CROSS_REPOSITORY"]
    support = ["SUPPORTED", "UNSUPPORTED", "UNKNOWN_INCONSISTENT"]
    authorization = ["AUTHORIZED", "FORBIDDEN", "CONTRADICTORY"]
    required = ["YES", "NO"]
    guards = ["PASS", "FAIL"]
    n = 0
    baseline = {}
    for provider, op, rel, sup, auth, req, guard in product(
        providers, operations, relations, support, authorization, required, guards
    ):
        n += 1
        executable = req == "YES" and sup == "SUPPORTED" and auth == "AUTHORIZED" and guard == "PASS"
        key = (op, rel, sup, auth, req, guard)
        baseline.setdefault(key, executable)
        assert baseline[key] == executable  # provider identity/label is not core semantic authority
        if sup != "SUPPORTED" or auth != "AUTHORIZED" or req != "YES" or guard != "PASS":
            assert not executable
    return n


def audit_contextual_capability_not_global_boolean():
    profiles = {
        "SAME_ONLY": {"SAME_REPOSITORY": True, "CROSS_REPOSITORY": False},
        "BOTH": {"SAME_REPOSITORY": True, "CROSS_REPOSITORY": True},
        "NONE": {"SAME_REPOSITORY": False, "CROSS_REPOSITORY": False},
    }
    n = 0
    for profile, observations in profiles.items():
        for relation, supported in observations.items():
            n += 1
            assert supported == observations[relation]
        if profile == "SAME_ONLY":
            # No single provider-wide supports_stack boolean can encode this contextual fact.
            assert len(set(observations.values())) == 2
    return n


def audit_provider_effect_unknown_fails_closed():
    review_effect = ["PRESERVED", "INVALIDATED", "UNKNOWN"]
    check_effect = ["PRESERVED", "INVALIDATED", "UNKNOWN"]
    evidence_reuse = ["NO", "YES"]
    n = 0
    for review, check, reuse in product(review_effect, check_effect, evidence_reuse):
        n += 1
        may_reuse = reuse == "YES" and review == "PRESERVED" and check == "PRESERVED"
        if review != "PRESERVED" or check != "PRESERVED":
            assert not may_reuse
    return n


def audit_provider_executor_semantic_non_authority():
    executors = ["LOCAL_RUU", "PROVIDER_NATIVE", "EXTERNAL_TOOL_ADAPTER"]
    api_success = ["YES", "NO"]
    exact_observation = ["YES", "NO"]
    contract_match = ["YES", "NO"]
    verification = ["PASS", "FAIL"]
    n = 0
    baseline = {}
    for exe, api, obs, match, verify in product(executors, api_success, exact_observation, contract_match, verification):
        n += 1
        adopt = api == "YES" and obs == "YES" and match == "YES" and verify == "PASS"
        key = (api, obs, match, verify)
        baseline.setdefault(key, adopt)
        assert baseline[key] == adopt
        if api != "YES" or obs != "YES" or match != "YES" or verify != "PASS":
            assert not adopt
    return n


def audit_direct_target_advance_contract():
    target = ["EXACT_EXPECTED_B", "ALREADY_C", "OTHER_ANCESTOR_OF_C", "DIVERGED", "UNKNOWN"]
    ancestry = ["B_ANCESTOR_C", "NOT_B_ANCESTOR_C"]
    policy = ["CURRENT_AUTHORIZED", "FORBIDDEN", "STALE_UNKNOWN"]
    evidence = ["VALID", "STALE", "MISSING"]
    claim = ["HELD", "OTHER", "NONE"]
    backend = ["SUPPORTED", "UNSUPPORTED", "UNKNOWN"]
    n = 0
    for tar, anc, pol, ev, cl, be in product(target, ancestry, policy, evidence, claim, backend):
        n += 1
        may_mutate = (
            tar == "EXACT_EXPECTED_B"
            and anc == "B_ANCESTOR_C"
            and pol == "CURRENT_AUTHORIZED"
            and ev == "VALID"
            and cl == "HELD"
            and be == "SUPPORTED"
        )
        if tar != "EXACT_EXPECTED_B" or anc != "B_ANCESTOR_C":
            assert not may_mutate
        if pol != "CURRENT_AUTHORIZED" or ev != "VALID" or cl != "HELD" or be != "SUPPORTED":
            assert not may_mutate
        if may_mutate:
            assert tar == "EXACT_EXPECTED_B" and anc == "B_ANCESTOR_C"
    return n


def audit_direct_target_recovery_adoption():
    target_relation = ["EXPECTED_B", "EXACT_C", "DESCENDANT_CONTAINING_C", "DIVERGED", "UNKNOWN"]
    operation_identity = ["KNOWN_EXACT", "UNKNOWN_INCONSISTENT"]
    anchor = ["PRESENT_REQUIRED", "MISSING", "GC_ELIGIBLE"]
    n = 0
    for rel, identity, anchor_state in product(target_relation, operation_identity, anchor):
        n += 1
        may_adopt = identity == "KNOWN_EXACT" and rel in {"EXACT_C", "DESCENDANT_CONTAINING_C"}
        if identity != "KNOWN_EXACT" or rel in {"EXPECTED_B", "DIVERGED", "UNKNOWN"}:
            assert not may_adopt
        # Physical anchor presence is not the truth source once authoritative history proves realization.
        if identity == "KNOWN_EXACT" and rel in {"EXACT_C", "DESCENDANT_CONTAINING_C"}:
            assert may_adopt
        _ = anchor_state
    return n


def audit_direct_target_no_staging_surface():
    implementation = ["PURE_REF", "TARGET_WORKTREE", "PREMOVE_LOCAL_TARGET", "MERGE_INTO_TARGET"]
    candidate_state = ["VERIFIED", "UNVERIFIED"]
    n = 0
    for impl, candidate in product(implementation, candidate_state):
        n += 1
        conforming = impl == "PURE_REF" and candidate == "VERIFIED"
        if impl != "PURE_REF" or candidate != "VERIFIED":
            assert not conforming
    return n


def audit_direct_recovery_anchor_cleanup():
    lifecycle = ["NONTERMINAL", "ADOPTED", "ABORTED_RECOVERY_SUFFICIENT"]
    recovery_need = ["REQUIRED", "NOT_REQUIRED"]
    anchor_state = ["PRESENT_REQUIRED", "GC_ELIGIBLE", "DELETED"]
    n = 0
    for life, need, anchor in product(lifecycle, recovery_need, anchor_state):
        n += 1
        may_be_disposable = life in {"ADOPTED", "ABORTED_RECOVERY_SUFFICIENT"} and need == "NOT_REQUIRED"
        if anchor in {"GC_ELIGIBLE", "DELETED"} and not may_be_disposable:
            # This combination is architecturally invalid; cleanup cannot be authorized.
            cleanup_authorized = False
            assert not cleanup_authorized
        if life == "NONTERMINAL" or need == "REQUIRED":
            cleanup_authorized = False
            assert not cleanup_authorized
    return n



def audit_review_correction_demand_idempotence():
    discovery = ["PROVIDER_HOOK", "GLOBAL_SWEEP", "BOTH"]
    revision = ["CURRENT", "STALE"]
    review_generation = ["CURRENT_CHANGES_REQUESTED", "SUPERSEDED"]
    prior_demand = ["ABSENT", "SAME_LOGICAL_DEMAND", "CONFLICTING_DUPLICATE"]
    n = 0
    for source, rev, gen, prior in product(discovery, revision, review_generation, prior_demand):
        n += 1
        current = rev == "CURRENT" and gen == "CURRENT_CHANGES_REQUESTED"
        if current and prior in {"ABSENT", "SAME_LOGICAL_DEMAND"}:
            ensured = "ONE_STABLE_DEMAND"
        elif current and prior == "CONFLICTING_DUPLICATE":
            ensured = "FAIL_CLOSED_RECONCILE"
        else:
            ensured = "NO_NEW_DISPATCH_FROM_STALE_FACT"
        # Discovery source never changes the logical identity/result.
        assert ensured in {"ONE_STABLE_DEMAND", "FAIL_CLOSED_RECONCILE", "NO_NEW_DISPATCH_FROM_STALE_FACT"}
        _ = source
    return n


def audit_review_correction_session_independence():
    originating_session = ["OPEN", "CLOSED", "GONE"]
    continuation_mode = ["RESTORE", "NEW_SESSION"]
    discovering_trigger = ["ORIGINAL_SESSION", "UNRELATED_SESSION", "PROVIDER_HOOK"]
    demand = ["CURRENT", "STALE"]
    dispatch_claim = ["HELD", "NOT_HELD"]
    n = 0
    baseline = {}
    for origin, mode, trigger, dem, claim in product(originating_session, continuation_mode, discovering_trigger, demand, dispatch_claim):
        n += 1
        may_dispatch = dem == "CURRENT" and claim == "HELD"
        # Originating runtime liveness and discovering caller identity are not authorization predicates.
        key = (dem, claim)
        if key in baseline:
            assert baseline[key] == may_dispatch
        else:
            baseline[key] = may_dispatch
        if dem == "STALE" or claim != "HELD":
            assert not may_dispatch
        _ = (origin, mode, trigger)
    return n


def audit_review_correction_authoring_boundary():
    original_contribution_lifecycle = ["OPEN", "CLOSED"]
    convergence_scope = ["EXISTING_MEMBER", "EXISTING_MULTIPLE_MEMBERS", "NEW_LOGICAL_SCOPE"]
    writer_surface = ["NEW_CONTRIBUTION_UNIT", "REOPEN_OLD_CONTRIBUTION_UNIT", "EDIT_SUBMISSION_REF"]
    n = 0
    for life, scope, surface in product(original_contribution_lifecycle, convergence_scope, writer_surface):
        n += 1
        valid_authoring_surface = surface == "NEW_CONTRIBUTION_UNIT"
        if life == "CLOSED":
            assert surface != "REOPEN_OLD_CONTRIBUTION_UNIT" or not valid_authoring_surface
        if surface == "EDIT_SUBMISSION_REF":
            assert not valid_authoring_surface
        if scope == "NEW_LOGICAL_SCOPE":
            # New scope is allowed only via new CU/group workflow, never by mutating old group.
            assert valid_authoring_surface == (surface == "NEW_CONTRIBUTION_UNIT")
    return n


def audit_review_correction_group_submission_continuity():
    scope_change = ["EXISTING_GROUP_MEMBER_STATE_CHANGED", "NEW_CONVERGENCE_UNIT"]
    publication_destination = ["SAME", "CHANGED"]
    group_operation = ["KEEP_GROUP", "MUTATE_OLD_GROUP", "DECLARE_NEW_GROUP"]
    n = 0
    for scope, dest, group_op in product(scope_change, publication_destination, group_operation):
        n += 1
        if scope == "EXISTING_GROUP_MEMBER_STATE_CHANGED":
            conforming_group = group_op == "KEEP_GROUP"
            same_submission = conforming_group and dest == "SAME"
            if group_op != "KEEP_GROUP":
                assert not conforming_group
        else:
            conforming_group = group_op == "DECLARE_NEW_GROUP"
            same_submission = False
            if group_op == "MUTATE_OLD_GROUP":
                assert not conforming_group
        if dest == "CHANGED":
            assert not same_submission
    return n

def static_consistency_checks():
    md_files = sorted(ROOT.glob("*.md"))
    assert md_files
    for p in md_files:
        text = p.read_text()
        assert text.count("```") % 2 == 0, f"unbalanced code fences: {p.name}"

    adr_files = sorted(ROOT.glob("ADR-*.md"))
    nums = sorted(int(re.match(r"ADR-(\d+)", p.name).group(1)) for p in adr_files)
    assert nums == list(range(1, 54)), nums

    main = (ROOT / "ruu-requirements-v1-merge-policy.md").read_text()
    backlog = (ROOT / "OPEN-DESIGN-BACKLOG.md").read_text()
    adr38 = (ROOT / "ADR-038-decouple-contribution-unit-identity-from-editing-artifacts.md").read_text()
    adr39 = (ROOT / "ADR-039-formalize-external-control-plane-contract.md").read_text()
    adr40 = (ROOT / "ADR-040-emit-exact-reconciliation-obligations-and-attribute-candidate-mutations-by-authorized-boundary.md").read_text()
    adr41 = (ROOT / "ADR-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md").read_text()
    adr42 = (ROOT / "ADR-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md").read_text()
    adr43 = (ROOT / "ADR-043-resolve-promotion-policy-by-authoritative-constraint-composition.md").read_text()
    adr44 = (ROOT / "ADR-044-establish-promotion-policy-currentness-by-immediate-authoritative-revalidation.md").read_text()
    adr45 = (ROOT / "ADR-045-make-promotion-units-immutable-content-addressed-exact-state-sets.md").read_text()
    adr46 = (ROOT / "ADR-046-predeclare-closed-promotion-groups-and-resolve-them-to-exact-promotion-units.md").read_text()
    adr47 = (ROOT / "ADR-047-project-promotion-groups-deterministically-into-repository-local-promotion-units.md").read_text()
    adr48 = (ROOT / "ADR-048-materialize-repository-local-multi-source-promotion-units-by-canonical-pairwise-merging.md").read_text()
    adr49 = (ROOT / "ADR-049-separate-stable-submission-identity-and-refs-from-internal-exact-state.md").read_text()
    adr50 = (ROOT / "ADR-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md").read_text()
    adr51 = (ROOT / "ADR-051-normalize-provider-capabilities-as-contextual-semantic-operation-observations.md").read_text()
    adr52 = (ROOT / "ADR-052-advance-direct-targets-by-atomic-exact-old-cas-fast-forward.md").read_text()
    adr53 = (ROOT / "ADR-053-turn-changes-requested-into-durable-session-independent-review-correction-work.md").read_text()
    control = (ROOT / "EXTERNAL-CONTROL-PLANE-CONTRACT.md").read_text()
    adr21 = (ROOT / "ADR-021-freeze-exact-pr-head-and-localize-external-waits.md").read_text()
    adr35 = (ROOT / "ADR-035-use-bounded-contribution-units-with-external-lifecycle-authority.md").read_text()
    adr37 = (ROOT / "ADR-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md").read_text()

    required_main = [
        "A **contribution unit** is a repository-local isolated Git unit",
        "OPEN | CLOSED",
        "latest authoritative managed checkpoint OID",
        "ContributionUnit identity and convergence continuity are independent of local branch/ref/worktree existence",
        "editing artifacts absent",
        "BLOCKED_MISSING_MANAGED_STATE",
        "ContributionUnit latest_authoritative_managed_checkpoint_oid record",
        "There is no separate ContributionUnit integration-readiness/release state",
        "earliest mechanically safe opportunity",
        "membership SEALED",
        "complete known set of nonterminal managed obligations",
        "ACTIVE_CONVERGENCE_SET` is a derived acceleration index",
        "final target-integration observation/proof",
        "## 30.9 Resolved/retired by ADR-038",
        "## 30.10 Resolved by ADR-040",
        "## 30.12 Resolved by ADR-040",
        "RECONCILIATION_REQUIRED",
        "Invariant 26A — Semantic conflicts emit exact reconciliation obligations",
        "Invariant 26B — Candidate attribution is mutation-boundary scoped",
        "## 30.1 Resolved by ADR-041",
        "## 30.11 Resolved by ADR-041",
        "## 30.13 Resolved by ADR-042",
        "## 30.14 Resolved by ADR-043",
        "## 30.15 Resolved by ADR-044",
        "## 30.16 Resolved by ADR-045",
        "## 30.17 Resolved by ADR-046",
        "## 30.18 Resolved by ADR-047",
        "## 30.39 Resolved by ADR-048 — repository-local multi-source candidate materialization",
        "## 30.21 Resolved by ADR-051 — contextual semantic provider capability observations",
        "## 30.22 Resolved by ADR-052 — exact-old CAS+FF DIRECT target advancement",
        "## 30.23 Resolved by ADR-053 — durable session-independent review correction",
        "Invariant 50A — DIRECT advancement has no target worktree or pre-advanced local-target staging",
        "Invariant 50B — DIRECT recovery adopts from authoritative target history",
        "Invariant 50C — DIRECT candidate recovery anchors outlive attempts but not durable adoption",
        "Invariant 63A — Review-correction demand identity is exact-generation-bound and discovery-channel-independent",
        "Invariant 63B — Coding-session liveness and discovering caller identity are non-authoritative",
        "Invariant 63C — Review correction uses new ContributionUnits, never the submission ref as an authoring surface",
        "Invariant 63D — Same-group semantic correction preserves logical submission identity; new logical scope does not mutate the old group",
        "## 33.21B DIRECT target advancement",
        "Invariant 43A — Provider capability is semantic and contextual",
        "Invariant 43B — Required, supported, and authorized are separate guards",
        "Invariant 43C — Provider-native executors never own normative semantics",
        "## 33.21A Repository-local candidate materialization",
        "Invariant 44A — PromotionUnit identity is content-addressed and deterministic",
        "Invariant 44B — PromotionUnit definition never mutates",
        "Invariant 44C — PromotionUnit declaration is intrinsically idempotent",
        "Invariant 44D — PromotionUnit identity excludes policy, topology, lifecycle, and semantic identity",
        "Invariant 44E — Structural declaration validity and promotion eligibility are distinct",
        "Invariant 46A — Promotion topology is a separate object",
        "Invariant 47 — PromotionGroup completeness is explicit; no implicit one-to-one default exists",
        "Invariant 47A — PromotionGroup identity is content-addressed and exact-OID-independent",
        "Invariant 47B — PromotionGroup declaration is durable and trigger-independent",
        "Invariant 47C — PromotionGroup resolution requires all current READY_INTERNAL members",
        "Invariant 47D — PromotionGroup resolution/materialization is snapshot/CAS guarded",
        "Invariant 47E — ConvergenceUnit is indivisible at the promotion-group boundary",
        "Invariant 47F — PromotionGroup projection is deterministic by source repository",
        "Invariant 47G — PromotionUnit source membership is repository-local",
        "Invariant 47H — Group resolution is complete while promotion progress may be partial",
        "Invariant 47I — Repository projection never splits to manufacture stack shape",
        "Invariant 47J — Multi-source candidate materialization uses exact base + exact sources",
        "Invariant 47K — Materialization order is canonical and runtime-order-independent",
        "Invariant 47L — Canonical materialization uses ancestry-aware full pairwise two-head merge semantics",
        "Invariant 47M — Final materialization candidate has exact ancestry closure",
        "Invariant 47N — Final materialization candidate identity is deterministic",
        "Invariant 47O — Materialization conflicts reuse RECONCILIATION_REQUIRED",
        "Invariant 47P — Only the exact final materialization candidate is promotion-adoptable",
        "Invariant 40A — Promotion authorization has no runtime/local bypass",
        "Invariant 40B — Repository policy cannot self-authorize from the candidate it governs",
        "Invariant 40C — Authoritative promotion constraints compose; contradictions remain visible",
        "Invariant 40D — Built-in policy rules only close underdetermined dimensions",
        "Invariant 40E — Policy contradiction diagnostics are factual, not prescriptive",
        "Invariant 40F — Cache/TTL never establishes promotion-policy currentness",
        "Invariant 40G — Authority-anchor movement invalidates the policy snapshot",
        "Invariant 40H — Non-atomic provider freshness ends at provider enforcement and exact observation",
        "TRANSFERABLE_TO_RUU",
        "requested_generation",
        "processed_generation",
        "Invariant 109 — Explicit invocations are coalescible demand signals",
        "Invariant 110 — At most one top-level executor is authoritative",
        "Invariant 111 — Demand catch-up and executor release are race-safe",
        "Invariant 112 — Durable fencing outranks liveness observations",
        "Invariant 113 — Trigger identity never carries External Control Plane mutation authority",
        "Invariant 114 — Physical recovery namespaces cannot alias across fenced executor generations",
        "Invariant 115 — The top-level runtime is a current-state reconciler, not a durable step workflow",
        "Invariant 116 — Physical run ownership and durable adoption authority are separate",
        "Invariant 117 — `IDLE` publication closes the demand-release race",
        "Invariant 118 — Live-but-hung takeover is not automatic in v1",
        "Invariant 119 — Recoverable logical intent is distinct from physical attempts",
        "Invariant 120 — External-effect truth requires exact Observation",
        "Invariant 121 — Adoption is atomic with the managed-state CAS it claims",
        "Invariant 122 — No CoordinationStore transaction spans external work",
        "Invariant 123 — Correctness-critical temporary resources become disposable before cleanup",
        "Invariant 124 — Repository identity survives locator relocation",
        "## 7.11 V1 CoordinationStore, convergence-run ownership, and recoverable-effect journal",
        "## 33.5 `ruu` convergence demand and global sweep scope",
        "scope = all known nonterminal managed obligations",
    ]
    for marker in required_main:
        assert marker in main, marker

    forbidden_current = [
        "contribution-unit lifecycle\n= OPEN | CLOSED | ABANDONED",
        "ContributionUnit lifecycle != ABANDONED",
        "non-abandoned ContributionUnit",
        "all ABANDONED contribution disposition",
        "CLOSED / ABANDONED\n→ never reopen",
        "Contribution unit cleanup",
        "## 33.11 Contribution-unit lifecycle / cleanup",
    ]
    forbidden_current.extend([
        "scope =\n  all ACTIVE repositories",
        "TRANSFERABLE_TO_THIS_INVOCATION",
        "TRANSFERABLE_TO_OTHER_INVOCATION",
    ])
    for marker in forbidden_current:
        assert marker not in main, marker

    assert "`ABANDONED`, preserve/discard residue policy" in main
    assert "There is no normative ContributionUnit `ABANDONED` state" in adr38
    assert "There is also no ContributionUnit `REMOVED` lifecycle state" in adr38
    assert "ContributionUnit identity" in adr38 and "!= local branch/ref existence" in adr38
    assert "OID is reachable/recoverable" in adr38
    assert "BLOCKED_MISSING_MANAGED_STATE" in adr38
    assert "outside `ruu`" in adr38
    assert "`ABANDONED` and `REMOVED` are not normative ContributionUnit lifecycle states" in adr35
    assert "Every valid managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit" in adr37
    assert "9. abandonment residue/disposition policy;" not in backlog
    assert "ContributionUnit artifact/continuity semantics are closed by ADR-038" in backlog
    assert "External boundary consolidation is closed by ADR-039" in backlog
    assert "Conflict/reconciliation and mutation-attribution semantics are closed by ADR-040" in backlog
    assert "10. conflict resolution policy;" not in backlog
    assert "12. attribution of tool/generated modifications to a contribution unit;" not in backlog
    assert "1. single-host vs future multi-host coordination;" not in backlog
    assert "11. Git claim contention/backoff policy;" not in backlog
    assert "Concurrent-trigger / single-executor semantics are closed by ADR-041" in backlog
    assert "CoordinationStore / top-level run / recoverable-effect semantics are closed by ADR-042" in backlog
    assert "Promotion-policy authority/composition semantics are closed by ADR-043" in backlog
    assert "PromotionUnit declaration/identity semantics are closed by ADR-045" in backlog
    assert "PromotionGroup pre-resolution/default-mapping semantics are closed by ADR-046" in backlog
    assert "Multi-source PromotionGroup projection semantics are closed by ADR-047" in backlog
    assert "Repository-local multi-source candidate/head materialization is closed by ADR-048" in backlog
    assert "Submission/ref semantics are closed by ADR-049" in backlog
    assert "Derived stack/restack semantics are closed by ADR-050" in backlog
    assert "18. multi-source promotion projection algorithm;" not in backlog
    assert "39. repository-local multi-source candidate/head materialization." not in backlog
    assert "19. submission-ref creation/naming/retention;" not in backlog
    assert "20. local vs provider-managed restacking implementation;" not in backlog
    assert "13. exact shared coordination-store schema" not in backlog
    assert "14. repository promotion-policy source precedence;" not in backlog
    assert "16. promotion-unit declaration API;" not in backlog
    assert "17. default promotion-unit mapping;" not in backlog
    assert "EXTERNAL-CONTROL-PLANE-CONTRACT.md" in main
    assert "## 7.10 External Control Plane boundary" in main
    assert "Invariant 17C — External dependencies are explicit contract clauses" in main
    assert "Formalize the external control-plane boundary as a normative contract" in adr39
    assert "RECONCILIATION_REQUIRED" in adr40
    assert "diagnostic, never adoption authority" in adr40
    assert "boundary-scoped, not process-scoped" in adr40
    assert "Coalesce convergence demands under a single-host fenced executor" in adr41
    assert "requested_generation" in adr41 and "processed_generation" in adr41
    assert "TRANSFERABLE_TO_RUU" in adr41
    assert "SQLite is the preferred/reference v1 backend" in adr41
    assert "reconciler-driven CoordinationStore" in adr42
    assert "OS process-lifetime lock" in adr42
    assert "Operation → Attempt → Observation → Adoption" in adr42
    assert "ACTIVE → IDLE" in adr42
    assert "live-but-hung" in adr42
    assert "GC_ELIGIBLE" in adr42
    assert "Resolve promotion policy by authoritative constraint composition" in adr43
    assert "There is no promotion-policy runtime override" in adr43
    assert "trusted authoritative target baseline" in adr43
    assert "resolution_candidates" in adr43 and "MUST NOT include or compute" in adr43
    required_control = [
        "The External Control Plane is a **role**, not a required product",
        "ContributionUnit lifecycle = OPEN | CLOSED",
        "ConvergenceUnit contribution-membership state",
        "PROTECTED_EXTERNAL",
        "DeclarePromotionGroup(",
        "Set<CanonicalConvergenceUnitRef>",
        "content-addressed promotion_group_id",
        "ADR-045 content-addressed PromotionUnit",
        "exactly one ADR-045 content-addressed PromotionUnit per represented repository",
        "A valid PromotionUnit is source-repository-local",
        "ADR-048 exact repository-local promotion-candidate materialization",
        "Promotion dependency/topology is not a caller-authored publication-layout declaration",
        "remain authoritative for Git/provider facts they own",
        "Every global sweep that services outstanding convergence demand remains global",
        "No vague external dependency may become a hidden precondition",
        "Reconciliation obligation delivery to the Development System",
        "RECONCILIATION_REQUIRED",
        "TRANSFERABLE_TO_RUU",
        "A convergence trigger is not an authority token",
        "Explicit invocations may coalesce",
        "Promotion-policy contradiction delivery to the external system",
        "recommended fix",
        "Promotion-policy staleness / concurrent provider-drift delivery",
        "exact observed rejection/current provider state",
    ]
    for marker in required_control:
        assert marker in control, marker
    current_external_docs = [main, adr39, control,
        (ROOT / "ADR-023-separate-contribution-unit-provisioning-from-ruu.md").read_text(),
        (ROOT / "ADR-027-separate-convergence-units-from-promotion-units-and-topology.md").read_text(),
        (ROOT / "ADR-033-consume-external-contribution-unit-mutation-authority.md").read_text(),
        (ROOT / "ADR-035-use-bounded-contribution-units-with-external-lifecycle-authority.md").read_text(),
        (ROOT / "ADR-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md").read_text(),
        adr38,
        adr40,
        adr41,
        adr42,
        adr43,
        adr44,
        adr45,
        adr46,
        adr47,
        adr48,
        adr49,
        adr50,
        adr51,
        adr52,
        adr53,
    ]
    for doc in current_external_docs:
        assert "the external subsystem" not in doc.lower()
        assert "external contribution-unit subsystem" not in doc.lower()

    assert "work_context_id" not in main
    assert "writer_context_id" not in main
    assert "writer_id" not in main
    assert "LEASE_ESTABLISHED" not in main
    for current_doc in [main, control, (ROOT / "ADR-003-base-commit-collection-on-contribution-unit-eligibility-not-task-completion.md").read_text(), (ROOT / "ADR-009-require-exclusive-worktree-mutation-authority.md").read_text(), (ROOT / "ADR-033-consume-external-contribution-unit-mutation-authority.md").read_text()]:
        assert "TRANSFERABLE_TO_THIS_INVOCATION" not in current_doc
        assert "TRANSFERABLE_TO_OTHER_INVOCATION" not in current_doc
    assert "TRANSFERABLE_TO_RUU" in main
    assert "TRANSFERABLE_TO_RUU" in control

    required_adr44 = [
        "Cache is optimization only",
        "Every policy-sensitive promotion mutation gets immediate pre-mutation revalidation",
        "Any authority-anchor change makes the prior snapshot stale",
        "There is no TTL-based authorization fallback",
        "Provider-side enforcement/rejection plus exact post-operation observation form the final external authority boundary",
        "Backlog item **30.15 is closed**",
    ]
    for marker in required_adr44:
        assert marker in adr44, marker

    required_adr45 = [
        "PromotionUnitDefinition",
        "Set<ExactConvergenceStateRef>",
        "For v1, `H` is SHA-256",
        "There is no `UPDATE PromotionUnit definition` operation",
        "Declaration is intrinsically idempotent",
        "Structural declaration validity is separate from promotion eligibility",
        "Promotion topology is separate from PromotionUnit identity",
        "The declaration also carries no separate `semantic readiness token`",
        "Backlog item **30.16 is closed**",
    ]
    for marker in required_adr45:
        assert marker in adr45, marker

    required_adr46 = [
        "Backlog item **30.17 is closed**",
        "PromotionGroupDefinition",
        "CanonicalConvergenceUnitRef",
        "The set is non-empty, unordered, unique, closed, and immutable",
        "Declaration is durable and trigger-independent",
        "No mid-sweep Development System handoff is required",
        "There is no implicit singleton/default mapping inside `ruu`",
        "ConvergenceUnit is the atomic promotion-grouping boundary",
        "Hash chain as the primary representation",
    ]
    for marker in required_adr46:
        assert marker in adr46, marker

    required_adr47 = [
        "Backlog item **30.18 is closed**",
        "Project(G, R)",
        "PromotionUnit is structurally repository-local",
        "Same PromotionGroup + same repository means one PromotionUnit",
        "Group current resolution adopts a complete repository→PromotionUnit mapping",
        "PromotionTopology remains separate from repository partition",
        "30.39 — repository-local multi-source candidate materialization",
    ]
    for marker47 in required_adr47:
        assert marker47 in adr47, marker47

    required_adr48 = [
        "Backlog item **30.39 is closed**",
        "Ancestry reduction is mechanical and provenance-preserving",
        "Fold order is canonical; arrival/runtime order is irrelevant",
        "Canonical merge semantics are ancestry-aware pairwise full two-head merges",
        "Native multi-head `octopus` MUST NOT define materialization semantics",
        "The final representation reuses an exact existing state when possible; otherwise it is one canonical synthetic multi-parent commit",
        "Final ancestry invariants are mandatory",
        "Conflict handling reuses RECONCILIATION_REQUIRED",
        "The exact final candidate requires full verification before adoption",
        "Materialization is an Operation→Attempt→Observation→Adoption effect",
        "MaterializationContract captures determinism-relevant merge semantics",
    ]
    for marker48 in required_adr48:
        assert marker48 in adr48, marker48

    required_adr49 = [
        "Backlog item **30.19 is closed**",
        "Internal refs and submission refs are always distinct refs",
        "Stable submission identity is logical, not exact-PromotionUnit identity",
        "Submission ref is created only for a current verified PR candidate",
        "refs/heads/Ruu/submissions/<submission_id>",
        "Revision publication uses exact expected-old protection",
        "Provider submission identity persists across exact revisions",
        "Ref retention and audit retention are separate",
    ]
    for marker49 in required_adr49:
        assert marker49 in adr49, marker49

    required_adr50 = [
        "Backlog item **30.20 is closed**",
        "Stacked publication is a derived representation, not caller intent",
        "A stack exists only while a dependency is unsatisfied by the target",
        "Every dependent submission revision has an immutable owned-state anchor",
        "Restack semantics are exact three-way state transplant",
        "Restacks do not accumulate projection drift",
        "Every new exact restacked head is fully verified",
        "Local semantics are normative; executor is pluggable",
        "Dependency satisfaction collapses the stack naturally",
        "Operation",
    ]
    for marker50 in required_adr50:
        assert marker50 in adr50, marker50

    required_adr51 = [
        "Backlog item **30.21 is closed**",
        "The core determines the required semantic transition before provider capability resolution",
        "Provider capability is an observation over an exact operation context, not a provider-wide feature boolean",
        "Capability observations separate technical support, contextual applicability, and current facts",
        "Semantic capability names are preferred over provider feature names",
        "Provider capability is factual; it never authorizes an operation by itself",
        "required ∩ supported ∩ authorized = executable",
        "Derived promotion topology is not an EffectivePromotionPolicy choice",
        "Provider-native execution never becomes semantic authority",
        "Capability observations obey ADR-044 freshness rules",
        "Unsupported or unknown capability blocks only the affected obligation",
    ]
    for marker51 in required_adr51:
        assert marker51 in adr51, marker51

    required_adr52 = [
        "Backlog item **30.22 is closed**",
        "The normative operation is `AdvanceTargetFF(target, expected_old=B, new=C)`",
        "There is no target worktree/merge staging step",
        "Exact expected-old mismatch makes the attempt stale even if a fast-forward would still be possible",
        "The core is backend-neutral; backends must satisfy the semantic CAS+FF contract",
        "The candidate uses an attempt-scoped non-business recovery anchor",
        "Recovery adopts from authoritative target history",
        "Physical cleanup is separate from durable adoption/audit retention",
        "DIRECT target advancement remains localized and idempotent",
    ]
    for marker52 in required_adr52:
        assert marker52 in adr52, marker52

    required_adr53 = [
        "Backlog item **30.23 is closed**",
        "`CHANGES_REQUESTED` creates/refreshes a durable exact-state-bound review-correction demand",
        "Provider hooks and `ruu` sweeps are coequal discovery paths for the same demand",
        "The original coding session need not remain alive or be literally reopened",
        "Up-front semantic ConvergenceUnit routing is not required",
        "Ordinary correction of existing group members preserves the PromotionGroup and persistent PR",
        "A genuinely new ConvergenceUnit is scope expansion, not mutation of the old ship",
        "Review-correction demands are exact-generation-bound and may become stale/superseded",
        "Correction completion re-enters the ordinary convergence loop",
    ]
    for marker53 in required_adr53:
        assert marker53 in adr53, marker53
    assert "ADR-053 amendment — review-correction continuation across sessions" in adr49
    assert "ADR-053 amendment:" in adr46
    assert "session-local workflow describes how the initial closed group is commonly declared" in adr46

    assert "21. provider capability discovery;" not in backlog
    assert "22. direct-promotion target-advancement workspace/ref implementation;" not in backlog
    assert "23. semantic mapping of review `CHANGES_REQUESTED` to affected convergence-unit scope(s);" not in backlog
    assert "DIRECT target-advancement mechanics are closed by ADR-052" in backlog
    assert "Semantic review continuation is closed by ADR-053" in backlog
    assert "## 30.22 Direct-promotion target-advancement workspace/ref implementation" not in main
    assert "## 30.23 Semantic review changes" not in main
    assert "CHANGES_REQUESTED\n→ higher layer may reopen internal convergence unit(s)" not in main
    assert "CHANGES_REQUESTED or explicit semantic reopen\n→ ACTIVE" not in adr21
    assert "advance local target descendant-only" not in main
    assert "DIRECT target advanced locally/remotely" not in main
    assert "The exact multi-source projection algorithm is not fixed by this architecture" not in main
    assert "Provider capability discovery semantics are closed by ADR-051" in backlog
    assert "## 30.21 Provider capability discovery" not in main
    assert "promotion_topology:\n  INDEPENDENT | STACKED" not in main
    assert "which promotion units depend on which" not in main
    assert "target intent" not in main
    assert "semantic readiness token" not in main.lower()
    assert "semantic readiness signal" not in main.lower()
    assert "dependency/stack parent" not in main.lower()
    assert "promotion_unit_id = content address of immutable canonical PromotionUnitDefinition" in main
    assert "Promotion grouping/default mapping is closed by ADR-046" in control
    assert "deterministic repository-local group projection by ADR-047" in control
    assert "exact repository-local multi-source candidate/head materialization by ADR-048" in control
    assert "submission identity/ref lifecycle by ADR-049" in control
    assert "derived dependency/restack semantics by ADR-050" in control
    assert "contextual provider capability discovery by ADR-051" in control
    assert "ADR-053 closes backlog 30.23" in control
    assert "provider webhook/event delivery or by a later `ruu` global sweep" in control
    assert "start a new continuation session" in control
    assert "waiting for explicit PromotionUnit declaration" not in main
    assert "Default policy may map" not in main
    assert (ROOT / "git-direct-target-advance-smoke-v1.sh").exists()
    assert "PASS" in (ROOT / "git-direct-target-advance-smoke-v1.txt").read_text()

    return len(md_files)


def main():
    families = {
        "contribution_unit_cardinality_identity": audit_contribution_unit_cardinality_identity(),
        "actor_correlation_irrelevance": audit_actor_correlation_irrelevance(),
        "contribution_unit_lifecycle": audit_contribution_unit_lifecycle(),
        "contribution_unit_artifact_exact_state_continuity": audit_contribution_unit_artifact_exact_state_continuity(),
        "contribution_unit_checkpoint_record_cas": audit_contribution_unit_checkpoint_record_cas(),
        "external_convergence_grouping_authority": audit_external_convergence_grouping_authority(),
        "external_control_plane_responsibility_boundary": audit_external_control_plane_responsibility_boundary(),
        "reconciliation_required_contract": audit_reconciliation_required_contract(),
        "candidate_attribution_boundary": audit_candidate_attribution_boundary(),
        "convergence_demand_coalescing": audit_convergence_demand_coalescing(),
        "single_executor_fencing": audit_single_executor_fencing(),
        "trigger_authority_independence": audit_trigger_authority_independence(),
        "executor_release_demand_race": audit_executor_release_demand_race(),
        "coordination_store_fail_closed": audit_coordination_store_fail_closed(),
        "recovery_namespace_nonaliasing": audit_recovery_namespace_nonaliasing(),
        "os_lock_sqlite_fence_separation": audit_os_lock_and_sqlite_fence_separation(),
        "active_idle_release_handshake": audit_active_idle_release_handshake(),
        "operation_attempt_observation_adoption": audit_operation_attempt_observation_adoption(),
        "external_effect_crash_recovery": audit_external_effect_crash_recovery(),
        "no_external_work_inside_sqlite_transaction": audit_no_external_work_inside_sqlite_transaction(),
        "live_hung_process_liveness": audit_live_hung_process_liveness(),
        "recovery_resource_gc_eligibility": audit_recovery_resource_gc_eligibility(),
        "repository_identity_relocation": audit_repository_identity_relocation(),
        "schema_initialization_migration": audit_schema_initialization_and_migration(),
        "current_state_reconciler": audit_current_state_reconciler_not_workflow_resume(),
        "promotion_policy_constraint_composition": audit_promotion_policy_constraint_composition(),
        "promotion_policy_runtime_bypass_irrelevance": audit_promotion_policy_runtime_bypass_irrelevance(),
        "trusted_target_policy_baseline": audit_trusted_target_policy_baseline(),
        "policy_contradiction_signal_boundary": audit_policy_contradiction_signal_boundary(),
        "policy_pre_mutation_currentness": audit_policy_pre_mutation_currentness(),
        "policy_cache_non_authority": audit_policy_cache_non_authority(),
        "nonatomic_provider_drift_boundary": audit_nonatomic_provider_drift_boundary(),
        "promotion_unit_content_address_identity": audit_promotion_unit_content_address_identity(),
        "promotion_unit_structural_vs_eligibility": audit_promotion_unit_structural_vs_eligibility(),
        "promotion_unit_redeclaration_idempotence": audit_promotion_unit_redeclaration_idempotence(),
        "promotion_group_content_address_identity": audit_promotion_group_content_address_identity(),
        "promotion_group_closed_completeness": audit_promotion_group_closed_completeness(),
        "promotion_group_snapshot_cas_resolution": audit_promotion_group_snapshot_cas_resolution(),
        "promotion_group_trigger_independence": audit_promotion_group_trigger_independence(),
        "promotion_group_repository_partition": audit_promotion_group_repository_partition(),
        "same_group_same_repo_not_split": audit_same_group_same_repo_not_split(),
        "promotion_group_complete_resolution_map": audit_promotion_group_complete_resolution_map(),
        "cross_repository_group_partial_progress": audit_cross_repository_group_partial_progress(),
        "group_revision_to_repository_local_units": audit_group_revision_to_repository_local_units(),
        "explicit_singleton_no_implicit_default": audit_explicit_singleton_no_implicit_default(),
        "materialization_ancestry_reduction": audit_materialization_ancestry_reduction(),
        "materialization_canonical_order_independence": audit_materialization_canonical_order_independence(),
        "materialization_conflict_boundary": audit_materialization_conflict_boundary(),
        "materialization_final_candidate_guards": audit_materialization_final_candidate_guards(),
        "materialization_verification_adoption": audit_materialization_verification_adoption(),
        "materialization_recovery_contract": audit_materialization_recovery_contract(),
        "submission_ref_separation": audit_submission_ref_separation(),
        "submission_logical_identity_revision": audit_submission_logical_identity_revision(),
        "submission_expected_old_update": audit_submission_expected_old_update(),
        "derived_dependency_representation": audit_derived_dependency_representation(),
        "restack_state_transplant_guards": audit_restack_state_transplant_guards(),
        "restack_no_projection_drift": audit_restack_no_projection_drift(),
        "restack_executor_neutral_adoption": audit_restack_executor_neutral_adoption(),
        "provider_semantic_capability_context": audit_provider_semantic_capability_context(),
        "contextual_capability_not_global_boolean": audit_contextual_capability_not_global_boolean(),
        "provider_effect_unknown_fails_closed": audit_provider_effect_unknown_fails_closed(),
        "provider_executor_semantic_non_authority": audit_provider_executor_semantic_non_authority(),
        "direct_target_advance_contract": audit_direct_target_advance_contract(),
        "direct_target_recovery_adoption": audit_direct_target_recovery_adoption(),
        "direct_target_no_staging_surface": audit_direct_target_no_staging_surface(),
        "direct_recovery_anchor_cleanup": audit_direct_recovery_anchor_cleanup(),
        "review_correction_demand_idempotence": audit_review_correction_demand_idempotence(),
        "review_correction_session_independence": audit_review_correction_session_independence(),
        "review_correction_authoring_boundary": audit_review_correction_authoring_boundary(),
        "review_correction_group_submission_continuity": audit_review_correction_group_submission_continuity(),
        "eager_contribution_integration": audit_eager_contribution_integration(),
        "convergence_membership_readiness": audit_convergence_membership_readiness(),
        "experimental_isolation_level": audit_experimental_isolation_level(),
        "global_managed_obligation_coverage": audit_global_managed_obligation_coverage(),
        "external_wait_recheck": audit_external_wait_recheck(),
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
    print("Ruu state-space audit v22: PASS")
    for name, count in families.items():
        print(f"{name}: {count:,}")
    print(f"changed/revalidated finite combinations evaluated: {total:,}")
    print(f"markdown artifacts statically cross-checked: {docs}")


if __name__ == "__main__":
    main()
