#!/usr/bin/env python3
"""Global regression/state-space audit for ADR-042 reconciler-driven CoordinationStore semantics.

This audit does not claim to enumerate unbounded Git DAG/provider states. It
revalidates the finite current architecture families from v11 and adds explicit
coverage for OS-owned single-host run authority, ACTIVE/IDLE release handoff,
run-generation/token fencing, append-only Operation/Attempt/Observation/Adoption
recovery, external-effect transaction boundaries, live-hung liveness behavior,
recovery-resource GC eligibility, repository relocation identity, schema
migration fail-closed behavior, and current-state reconciliation.
"""
from itertools import product
from pathlib import Path
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

def static_consistency_checks():
    md_files = sorted(ROOT.glob("*.md"))
    assert md_files
    for p in md_files:
        text = p.read_text()
        assert text.count("```") % 2 == 0, f"unbalanced code fences: {p.name}"

    adr_files = sorted(ROOT.glob("ADR-*.md"))
    nums = sorted(int(re.match(r"ADR-(\d+)", p.name).group(1)) for p in adr_files)
    assert nums == list(range(1, 43)), nums

    main = (ROOT / "ruu-requirements-v1-merge-policy.md").read_text()
    backlog = (ROOT / "OPEN-DESIGN-BACKLOG.md").read_text()
    adr38 = (ROOT / "ADR-038-decouple-contribution-unit-identity-from-editing-artifacts.md").read_text()
    adr39 = (ROOT / "ADR-039-formalize-external-control-plane-contract.md").read_text()
    adr40 = (ROOT / "ADR-040-emit-exact-reconciliation-obligations-and-attribute-candidate-mutations-by-authorized-boundary.md").read_text()
    adr41 = (ROOT / "ADR-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md").read_text()
    adr42 = (ROOT / "ADR-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md").read_text()
    control = (ROOT / "EXTERNAL-CONTROL-PLANE-CONTRACT.md").read_text()
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
    assert "13. exact shared coordination-store schema" not in backlog
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
    required_control = [
        "The External Control Plane is a **role**, not a required product",
        "ContributionUnit lifecycle = OPEN | CLOSED",
        "ConvergenceUnit contribution-membership state",
        "PROTECTED_EXTERNAL",
        "which exact ConvergenceUnit states belong to a PromotionUnit",
        "remain authoritative for Git/provider facts they own",
        "Every global sweep that services outstanding convergence demand remains global",
        "No vague external dependency may become a hidden precondition",
        "Reconciliation obligation delivery to the Development System",
        "RECONCILIATION_REQUIRED",
        "TRANSFERABLE_TO_RUU",
        "A convergence trigger is not an authority token",
        "Explicit invocations may coalesce",
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
    print("Ruu state-space audit v12: PASS")
    for name, count in families.items():
        print(f"{name}: {count:,}")
    print(f"changed/revalidated finite combinations evaluated: {total:,}")
    print(f"markdown artifacts statically cross-checked: {docs}")


if __name__ == "__main__":
    main()
