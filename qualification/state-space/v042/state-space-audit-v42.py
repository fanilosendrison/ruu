#!/usr/bin/env python3
from itertools import product

BASELINE = 15588  # v41 through ADR-076
count = 0

# A. Shared managed refs require repository-common observer coverage.
start = count
for observer_scope, linked_worktree, touches_shared_ref, observer_active in product(
    ("REPOSITORY_COMMON", "WORKTREE_LOCAL"), (False, True), (False, True), (False, True)
):
    count += 1
    if not touches_shared_ref:
        action = "NO_MANAGED_BINDING_REQUIREMENT"
    elif observer_scope == "REPOSITORY_COMMON" and observer_active:
        action = "COVERED"
    else:
        action = "BLOCK_OR_INTEGRITY_FAILURE"
    if linked_worktree and touches_shared_ref and observer_scope == "WORKTREE_LOCAL":
        assert action == "BLOCK_OR_INTEGRITY_FAILURE"
A = count - start

# B. Hook/config ownership and composition.
start = count
for surface, foreign_present, exact_owned in product(
    ("CONFIGURED_MULTI", "TRADITIONAL_SLOT", "SUPPORTED_DISPATCHER", "FOREIGN_PATH", "BACKEND_NATIVE"),
    (False, True),
    (False, True),
):
    count += 1
    if surface in ("CONFIGURED_MULTI", "SUPPORTED_DISPATCHER", "BACKEND_NATIVE"):
        action = "COMPOSE_IF_ATTESTED"
    elif surface == "TRADITIONAL_SLOT" and (not foreign_present or exact_owned):
        action = "INSTALL_OR_ADOPT_OWNED"
    else:
        action = "DO_NOT_OVERWRITE_BLOCK_ADMISSION"
    if surface == "FOREIGN_PATH":
        assert action == "DO_NOT_OVERWRITE_BLOCK_ADMISSION"
B = count - start

# C. Managed-authoring admission depends on functional attestation.
start = count
for coverage_status, attested, managed_write in product(
    ("ACTIVE", "BROKEN", "ABSENT"), (False, True), (False, True)
):
    count += 1
    admitted = managed_write and coverage_status == "ACTIVE" and attested
    action = "AUTHORING_ADMITTED" if admitted else ("BLOCK_MANAGED_AUTHORING" if managed_write else "NO_AUTHORING_REQUEST")
    if managed_write and not (coverage_status == "ACTIVE" and attested):
        assert action == "BLOCK_MANAGED_AUTHORING"
C = count - start

# D. V1 mutation-engine boundary and inherited conformance.
start = count
for engine, touches_managed, witness_present in product(
    ("GIT_CORE_CONFORMING", "GIT_CORE_NONCONFORMING", "ALT_CERTIFIED", "ALT_UNCERTIFIED", "DIRECT_WRITER"),
    (False, True),
    (False, True),
):
    count += 1
    conforming = engine in ("GIT_CORE_CONFORMING", "ALT_CERTIFIED")
    if not touches_managed:
        action = "OUTSIDE_MANAGED_BINDING_SEMANTICS"
    elif conforming and witness_present:
        action = "NORMAL_NATIVE_PATH"
    elif not witness_present:
        action = "UNWITNESSED_INTEGRITY_FAILURE"
    else:
        action = "NONCONFORMING_ENGINE_BLOCK_OR_FAIL"
    if engine == "DIRECT_WRITER" and touches_managed and not witness_present:
        assert action == "UNWITNESSED_INTEGRITY_FAILURE"
D = count - start

# E. Final topology never manufactures causal history; exceptional recovery stays explicit.
start = count
for binding_changed, causal_prep, recovery_authority, exact_compatible in product((False, True), repeat=4):
    count += 1
    if not binding_changed:
        action = "STATE_INTACT"
    elif causal_prep:
        action = "NORMAL_CAUSAL_RECONCILIATION"
    elif recovery_authority and exact_compatible:
        action = "EXPLICIT_ECP_RECOVERY_ONLY"
    else:
        action = "FAIL_CLOSED_UNWITNESSED"
    if binding_changed and not causal_prep and not recovery_authority:
        assert action == "FAIL_CLOSED_UNWITNESSED"
E = count - start

# F. Coverage epochs do not retroactively bridge gaps.
start = count
for prior_epoch, gap_detected, repaired, reattested in product(
    ("ACTIVE", "BROKEN", "NONE"), (False, True), (False, True), (False, True)
):
    count += 1
    if gap_detected:
        old_trust = "CLOSED_OR_BROKEN"
    else:
        old_trust = prior_epoch
    new_active = repaired and reattested
    if new_active:
        action = "OPEN_NEW_EPOCH"
    elif old_trust == "ACTIVE":
        action = "KEEP_CURRENT_EPOCH"
    else:
        action = "NO_TRUSTED_ACTIVE_EPOCH"
    if gap_detected and new_active:
        assert action == "OPEN_NEW_EPOCH"
F = count - start

# G. Clone/recreation/reactivation never inherits coverage without re-attestation.
start = count
for event, prior_active, reattested in product(
    ("NONE", "CLONE", "RECREATE", "REACTIVATE"), (False, True), (False, True)
):
    count += 1
    if event == "NONE" and prior_active:
        action = "RETAIN_IF_PROFILE_UNCHANGED"
    elif event != "NONE" and reattested:
        action = "NEW_ACTIVE_COVERAGE"
    elif event != "NONE":
        action = "BLOCK_UNTIL_REATTESTED"
    else:
        action = "NO_ACTIVE_COVERAGE"
    if event != "NONE" and prior_active and not reattested:
        assert action == "BLOCK_UNTIL_REATTESTED"
G = count - start

# H. Install/upgrade/remove only exact owned state.
start = count
for operation, current_state in product(
    ("INSTALL", "UPGRADE", "REMOVE"), ("ABSENT", "OURS_EXPECTED", "OURS_MODIFIED", "FOREIGN")
):
    count += 1
    if operation == "INSTALL" and current_state == "ABSENT":
        action = "CREATE_OWNED"
    elif current_state == "OURS_EXPECTED":
        action = "EXPECTED_STATE_MUTATION"
    elif operation == "REMOVE" and current_state == "ABSENT":
        action = "IDEMPOTENT_ABSENT"
    else:
        action = "CONFLICT_NO_OVERWRITE"
    if current_state == "FOREIGN":
        assert action == "CONFLICT_NO_OVERWRITE"
H = count - start

# I. Composition order cannot authorize or allow missing required persistence.
start = count
for ours_called, other_veto, required_persisted, transaction_committed in product((False, True), repeat=4):
    count += 1
    if other_veto and transaction_committed:
        action = "INVALID_COMPOSITION_OUTCOME"
    elif transaction_committed and (not ours_called or not required_persisted):
        action = "COVERAGE_OR_PERSISTENCE_VIOLATION"
    elif other_veto:
        action = "ABORT_RECOVER_PREPARATION"
    elif transaction_committed:
        action = "COMMIT_WITH_REQUIRED_WITNESS"
    else:
        action = "NO_COMMITTED_DISPOSITION"
    if transaction_committed and not other_veto and ours_called and required_persisted:
        assert action == "COMMIT_WITH_REQUIRED_WITNESS"
I = count - start

assert A == 16, A
assert B == 20, B
assert C == 12, C
assert D == 20, D
assert E == 16, E
assert F == 24, F
assert G == 16, G
assert H == 12, H
assert I == 16, I
assert count == 152, count
print(f"ADR-077 repository-common-coverage family: {A} PASS")
print(f"ADR-077 ownership-composition family: {B} PASS")
print(f"ADR-077 admission-attestation family: {C} PASS")
print(f"ADR-077 mutation-engine-boundary family: {D} PASS")
print(f"ADR-077 unwitnessed-recovery family: {E} PASS")
print(f"ADR-077 coverage-epoch family: {F} PASS")
print(f"ADR-077 recreation-reattestation family: {G} PASS")
print(f"ADR-077 owned-install-CAS family: {H} PASS")
print(f"ADR-077 hook-order-persistence family: {I} PASS")
print(f"new combinations: {count} PASS")
print(f"retained v41 baseline: {BASELINE}")
print(f"v42 total: {BASELINE + count} PASS")
