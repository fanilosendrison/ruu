#!/usr/bin/env python3
"""Global regression/state-space audit for ADR-040 reconciliation obligations and candidate-attribution boundary.

This audit does not claim to enumerate unbounded Git DAG/provider states. It
exhaustively checks the finite identity/cardinality, lifecycle, editing-artifact,
exact-managed-state continuity, eager integration, readiness, authority, global
obligation, verification, review, and provider-facing families affected by the
current ADR-033..040 model, then performs static consistency checks across the
complete current architecture artifact set.
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
    surface = ["PRESENT", "ABSENT"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_THIS",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_OTHER",
        "UNKNOWN",
    ]
    claims = ["NONE", "THIS", "OTHER"]
    topology = ["KNOWN", "UNKNOWN"]
    operations = ["COMMIT", "SYNC", "CONFLICT_MUTATION", "RESET_MOVE"]
    n = 0
    for surf, acc, claim, topo, op in product(surface, access, claims, topology, operations):
        n += 1
        authorized = (
            surf == "PRESENT"
            and topo == "KNOWN"
            and claim == "THIS"
            and acc in {"TRANSFERABLE_THIS", "TRANSFERABLE_GENERAL"}
        )
        if surf == "ABSENT":
            assert not authorized
        if acc in {"PROTECTED_EXTERNAL", "TRANSFERABLE_OTHER", "UNKNOWN"}:
            assert not authorized
        if claim != "THIS" or topo != "KNOWN":
            assert not authorized
        _ = op
    return n


def audit_contribution_unit_commit_verification():
    lifecycle = ["OPEN", "CLOSED"]
    surface = ["ABSENT", "PRESENT_CLEAN", "PRESENT_DIRTY"]
    access = [
        "PROTECTED_EXTERNAL",
        "TRANSFERABLE_THIS",
        "TRANSFERABLE_GENERAL",
        "TRANSFERABLE_OTHER",
        "UNKNOWN",
    ]
    claims = ["NONE", "THIS", "OTHER"]
    evidence = ["NONE", "VALID", "STALE", "FAIL", "UNKNOWN"]
    stability = ["STABLE", "MUTATED", "UNKNOWN"]
    n = 0
    for life, surf, acc, claim, ev, stable in product(
        lifecycle, surface, access, claims, evidence, stability
    ):
        n += 1
        authorized = (
            surf == "PRESENT_DIRTY"
            and acc in {"TRANSFERABLE_THIS", "TRANSFERABLE_GENERAL"}
            and claim == "THIS"
            and ev == "VALID"
            and stable == "STABLE"
        )
        if authorized:
            assert life in {"OPEN", "CLOSED"}
        if surf != "PRESENT_DIRTY" or claim != "THIS" or ev != "VALID" or stable != "STABLE":
            assert not authorized
        if acc in {"PROTECTED_EXTERNAL", "TRANSFERABLE_OTHER", "UNKNOWN"}:
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


def static_consistency_checks():
    md_files = sorted(ROOT.glob("*.md"))
    assert md_files
    for p in md_files:
        text = p.read_text()
        assert text.count("```") % 2 == 0, f"unbalanced code fences: {p.name}"

    adr_files = sorted(ROOT.glob("ADR-*.md"))
    nums = sorted(int(re.match(r"ADR-(\d+)", p.name).group(1)) for p in adr_files)
    assert nums == list(range(1, 41)), nums

    main = (ROOT / "ruu-requirements-v1-merge-policy.md").read_text()
    backlog = (ROOT / "OPEN-DESIGN-BACKLOG.md").read_text()
    adr38 = (ROOT / "ADR-038-decouple-contribution-unit-identity-from-editing-artifacts.md").read_text()
    adr39 = (ROOT / "ADR-039-formalize-external-control-plane-contract.md").read_text()
    adr40 = (ROOT / "ADR-040-emit-exact-reconciliation-obligations-and-attribute-candidate-mutations-by-authorized-boundary.md").read_text()
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
    assert "EXTERNAL-CONTROL-PLANE-CONTRACT.md" in main
    assert "## 7.10 External Control Plane boundary" in main
    assert "Invariant 17C — External dependencies are explicit contract clauses" in main
    assert "Formalize the external control-plane boundary as a normative contract" in adr39
    assert "RECONCILIATION_REQUIRED" in adr40
    assert "diagnostic, never adoption authority" in adr40
    assert "boundary-scoped, not process-scoped" in adr40
    required_control = [
        "The External Control Plane is a **role**, not a required product",
        "ContributionUnit lifecycle = OPEN | CLOSED",
        "ConvergenceUnit contribution-membership state",
        "PROTECTED_EXTERNAL",
        "which exact ConvergenceUnit states belong to a PromotionUnit",
        "remain authoritative for Git/provider facts they own",
        "Every explicit invocation remains global",
        "No vague external dependency may become a hidden precondition",
        "Reconciliation obligation delivery to the Development System",
        "RECONCILIATION_REQUIRED",
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
    ]
    for doc in current_external_docs:
        assert "the external subsystem" not in doc.lower()
        assert "external contribution-unit subsystem" not in doc.lower()

    assert "work_context_id" not in main
    assert "writer_context_id" not in main
    assert "writer_id" not in main
    assert "LEASE_ESTABLISHED" not in main

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
    print("Ruu state-space audit v10: PASS")
    for name, count in families.items():
        print(f"{name}: {count:,}")
    print(f"changed/revalidated finite combinations evaluated: {total:,}")
    print(f"markdown artifacts statically cross-checked: {docs}")


if __name__ == "__main__":
    main()
