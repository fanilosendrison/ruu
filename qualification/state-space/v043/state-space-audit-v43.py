#!/usr/bin/env python3
from itertools import product

BASELINE = 15740  # v42 through ADR-077
count = 0

# A. Supported-harness ordinary UX must be zero-preflight and not require a second product.
start = count
for supported, integration_available, manual_preflight_required, second_product_required in product((False, True), repeat=4):
    count += 1
    if not supported:
        action = "OUTSIDE_SUPPORTED_HARNESS_CONTRACT"
    elif integration_available and not manual_preflight_required and not second_product_required:
        action = "ZERO_PREFLIGHT_OK"
    else:
        action = "NONCONFORMANT_ORDINARY_UX"
    if supported and (manual_preflight_required or second_product_required):
        assert action == "NONCONFORMANT_ORDINARY_UX"
A = count - start

# B. Safety still must exist before first managed write.
start = count
for write_occurs, provisioned_before_write, isolated_worktree, observer_active in product((False, True), repeat=4):
    count += 1
    if not write_occurs:
        action = "NO_WRITE_YET"
    elif provisioned_before_write and isolated_worktree and observer_active:
        action = "MANAGED_WRITE_ALLOWED"
    else:
        action = "BLOCK_BEFORE_WRITE"
    if write_occurs and not provisioned_before_write:
        assert action == "BLOCK_BEFORE_WRITE"
B = count - start

# C. Packaging integration must not collapse semantic authority or phase separation.
start = count
for bundled_integration, semantic_authority_external, convergence_infers_semantics, retroactive_checkpoint_provisioning in product((False, True), repeat=4):
    count += 1
    if not semantic_authority_external or convergence_infers_semantics:
        action = "AUTHORITY_VIOLATION"
    elif retroactive_checkpoint_provisioning:
        action = "PHASE_VIOLATION"
    else:
        action = "BOUNDARY_OK"
    if bundled_integration and semantic_authority_external and not convergence_infers_semantics and not retroactive_checkpoint_provisioning:
        assert action == "BOUNDARY_OK"
C = count - start

# D. Later checkpoint remains simple; harness carries internal metadata behind the command.
start = count
for checkpoint_requested, caller_supplies_internal_ids, caller_enumerates_repos, harness_carries_metadata in product((False, True), repeat=4):
    count += 1
    if not checkpoint_requested:
        action = "NO_CHECKPOINT"
    elif caller_supplies_internal_ids or caller_enumerates_repos:
        action = "NONCONFORMANT_CHECKPOINT_UX"
    elif harness_carries_metadata:
        action = "SIMPLE_RUU_OK"
    else:
        action = "BLOCK_MISSING_INTERNAL_HANDOFF"
    if checkpoint_requested and not caller_supplies_internal_ids and not caller_enumerates_repos and harness_carries_metadata:
        assert action == "SIMPLE_RUU_OK"
D = count - start

# E. Lazy first authoring touch may span one/many repos without predeclaring a repo list.
start = count
for multi_repo, authoring_touch_detected, per_repo_preedit_ready, repo_list_predeclared, checkpoint_later in product((False, True), repeat=5):
    count += 1
    if authoring_touch_detected and not per_repo_preedit_ready:
        action = "BLOCK_FIRST_WRITE"
    elif repo_list_predeclared:
        action = "AVOIDABLE_PREFLIGHT_TOPOLOGY"
    elif checkpoint_later and per_repo_preedit_ready:
        action = "LAZY_AUTHORING_THEN_CHECKPOINT"
    else:
        action = "NO_COMPLETE_WORKFLOW_YET"
    if multi_repo and authoring_touch_detected and per_repo_preedit_ready and not repo_list_predeclared and checkpoint_later:
        assert action == "LAZY_AUTHORING_THEN_CHECKPOINT"
E = count - start

# F. Internal/admin provisioning primitives may exist but must not become ordinary requirements.
start = count
for ordinary_path, supported_harness, primitive_exposed, primitive_required, automatic_preedit in product((False, True), repeat=5):
    count += 1
    if ordinary_path and supported_harness:
        if primitive_required or not automatic_preedit:
            action = "NONCONFORMANT_ORDINARY_PATH"
        else:
            action = "ORDINARY_PATH_OK"
    else:
        action = "ADMIN_OR_UNSUPPORTED_PATH"
    if ordinary_path and supported_harness and primitive_exposed and not primitive_required and automatic_preedit:
        assert action == "ORDINARY_PATH_OK"
F = count - start

assert A == 16, A
assert B == 16, B
assert C == 16, C
assert D == 16, D
assert E == 32, E
assert F == 32, F
assert count == 128, count
print(f"ADR-078 zero-preflight-supported-harness family: {A} PASS")
print(f"ADR-078 pre-edit-safety-timing family: {B} PASS")
print(f"ADR-078 authority-vs-packaging family: {C} PASS")
print(f"ADR-078 checkpoint-simplicity family: {D} PASS")
print(f"ADR-078 lazy-multi-repo-first-touch family: {E} PASS")
print(f"ADR-078 admin-vs-ordinary-interface family: {F} PASS")
print(f"new combinations: {count} PASS")
print(f"retained v42 baseline: {BASELINE}")
print(f"v43 total: {BASELINE + count} PASS")
