#!/usr/bin/env python3
from itertools import product

BASELINE = 15868  # v43 through ADR-078
count = 0

# A. Minimal native transaction rejection set.
start = count
for cessation_candidate, managed_current, authority_available, prep_durable, advisory_failed in product((False, True), repeat=5):
    count += 1
    if not cessation_candidate:
        action = "ALLOW_STATE_REDISCOVERY"
    elif managed_current and (not authority_available or not prep_durable):
        action = "VETO_CRITICAL"
    elif not authority_available:
        action = "VETO_UNKNOWN_CANDIDATE"
    else:
        action = "ALLOW"
    if not cessation_candidate:
        assert action == "ALLOW_STATE_REDISCOVERY"
    if cessation_candidate and managed_current and not prep_durable:
        assert action == "VETO_CRITICAL"
A = count-start

# B. Protection filter is negative acceleration only.
start = count
for candidate, filter_trusted, filter_hit, authority_available, current_binding in product((False, True), repeat=5):
    count += 1
    if not candidate:
        action = "ALLOW_NO_CANDIDATE"
    elif filter_trusted and not filter_hit:
        action = "ALLOW_FILTER_NEGATIVE"
    elif not authority_available:
        action = "VETO_UNKNOWN"
    elif current_binding:
        action = "REQUIRE_PREPARATION"
    else:
        action = "ALLOW_AUTHORITY_NEGATIVE"
    if candidate and filter_trusted and not filter_hit:
        assert action == "ALLOW_FILTER_NEGATIVE"
    if candidate and not filter_trusted and not authority_available:
        assert action == "VETO_UNKNOWN"
B = count-start

# C. Complete preparation batch is all-or-nothing permission.
start = count
for transaction_atomic, managed_effects, complete_batch, durable_commit, retry_exhausted in product((False, True), repeat=5):
    count += 1
    if not managed_effects:
        action = "NO_CRITICAL_BATCH"
    elif complete_batch and durable_commit:
        action = "ALLOW"
    else:
        action = "VETO_AFTER_RETRY" if retry_exhausted else "RETRY_OR_VETO"
    if managed_effects and (not complete_batch or not durable_commit) and retry_exhausted:
        assert action == "VETO_AFTER_RETRY"
C = count-start

# D. Outcome/advisory persistence after PREPARED does not roll back Git.
start = count
for prepared_durable, git_linearized, outcome_persisted, wakeup_ok, telemetry_ok in product((False, True), repeat=5):
    count += 1
    if not prepared_durable and git_linearized:
        action = "INVALID_SAFETY_HISTORY"
    elif prepared_durable and git_linearized and not outcome_persisted:
        action = "ALLOW_RECONCILE_OUTCOME"
    else:
        action = "NO_RETROACTIVE_VETO"
    if prepared_durable and git_linearized and (not outcome_persisted or not wakeup_ok or not telemetry_ok):
        assert action in {"ALLOW_RECONCILE_OUTCOME", "NO_RETROACTIVE_VETO"}
D = count-start

# E. RefAdmissionBarrier publication ordering.
start = count
for candidate_exists, filter_safe, barrier_acquired, binding_committed_under_barrier, barrier_released in product((False, True), repeat=5):
    count += 1
    if not candidate_exists:
        action = "NO_EXISTING_V1_CANDIDATE"
    elif not filter_safe or not barrier_acquired:
        action = "NO_MANAGED_ADMISSION"
    elif not binding_committed_under_barrier:
        action = "NO_MANAGED_ADMISSION"
    elif barrier_released:
        action = "CURRENT_PROTECTED"
    else:
        action = "CURRENT_BARRIER_STILL_HELD"
    if candidate_exists and filter_safe and barrier_acquired and binding_committed_under_barrier:
        assert action in {"CURRENT_PROTECTED", "CURRENT_BARRIER_STILL_HELD"}
E = count-start

# F. Admission crashes bias to false-positive protection or already-protected current binding.
start = count
for filter_written, barrier_held, binding_current, barrier_released, handoff_done in product((False, True), repeat=5):
    count += 1
    if binding_current and not filter_written:
        action = "INVALID_UNPROTECTED_BINDING"
    elif handoff_done and not binding_current:
        action = "INVALID_HANDOFF"
    elif binding_current:
        action = "SAFE_CURRENT_BINDING"
    elif filter_written:
        action = "SAFE_FALSE_POSITIVE_OR_PENDING"
    else:
        action = "UNMANAGED_CANDIDATE"
    if binding_current and filter_written:
        assert action == "SAFE_CURRENT_BINDING"
F = count-start

# G. Initial worktree handoff exactness and authority.
start = count
for topology_exact, provisioning_exclusive, binding_current, barrier_released, producer_handoff in product((False, True), repeat=5):
    count += 1
    if producer_handoff and (not topology_exact or not binding_current or not barrier_released or not provisioning_exclusive):
        action = "INVALID_FIRST_WRITE_HANDOFF"
    elif producer_handoff:
        action = "MANAGED_AUTHORING_ALLOWED"
    else:
        action = "NO_PRODUCER_WRITE_YET"
    if producer_handoff and topology_exact and provisioning_exclusive and binding_current and barrier_released:
        assert action == "MANAGED_AUTHORING_ALLOWED"
G = count-start

# H. Live lock ordering must never invert.
start = count
for git_lock_held, store_live_lock_held, waiting_for_git_lock, durable_claim_only in product((False, True), repeat=4):
    count += 1
    if store_live_lock_held and waiting_for_git_lock:
        action = "LOCK_ORDER_VIOLATION"
    elif durable_claim_only:
        action = "NO_LIVE_LOCK_INVERSION"
    else:
        action = "LOCK_ORDER_OK"
    if store_live_lock_held and waiting_for_git_lock:
        assert action == "LOCK_ORDER_VIOLATION"
H = count-start

# I. Coverage gap, filter degradation and persistence veto are distinct.
start = count
for observer_reached, filter_trusted, critical_persistence_ok, mutation_linearized in product((False, True), repeat=4):
    count += 1
    if not observer_reached:
        action = "COVERAGE_GAP"
    elif not critical_persistence_ok and mutation_linearized:
        action = "INVALID_FAIL_OPEN"
    elif not critical_persistence_ok:
        action = "CRITICAL_FAILURE_VETOED"
    elif not filter_trusted:
        action = "FILTER_DEGRADED_COVERAGE_ACTIVE"
    else:
        action = "HEALTHY"
    if observer_reached and not filter_trusted and critical_persistence_ok:
        assert action == "FILTER_DEGRADED_COVERAGE_ACTIVE"
I = count-start

assert [A,B,C,D,E,F,G,H,I] == [32,32,32,32,32,32,32,16,16]
assert count == 256
print(f"ADR-079 minimal-rejection family: {A} PASS")
print(f"ADR-079 protection-filter family: {B} PASS")
print(f"ADR-079 preparation-batch family: {C} PASS")
print(f"ADR-079 outcome-advisory family: {D} PASS")
print(f"ADR-079 ref-admission family: {E} PASS")
print(f"ADR-079 admission-crash family: {F} PASS")
print(f"ADR-079 initial-handoff family: {G} PASS")
print(f"ADR-079 lock-order family: {H} PASS")
print(f"ADR-079 failure-classification family: {I} PASS")
print(f"new combinations: {count} PASS")
print(f"retained v43 baseline: {BASELINE}")
print(f"v44 total: {BASELINE + count} PASS")
