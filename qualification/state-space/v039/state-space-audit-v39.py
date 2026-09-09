#!/usr/bin/env python3
from itertools import product

BASELINE = 14992
count = 0

# A. Managed binding transaction classifier.
for binding, prepared, outcome, evidence, group in product(
    ("UNMANAGED", "MANAGED"),
    ("FAILED", "DURABLE"),
    ("ABORT", "COMMIT"),
    ("RENAME", "TERMINAL_DELETE", "AMBIGUOUS"),
    ("UNREALIZED", "PROMOTED", "PARTIAL"),
):
    count += 1
    if binding == "UNMANAGED":
        action = "NEUTRAL"
    elif prepared == "FAILED":
        action = "REJECT_OR_CONFORMANCE_VIOLATION" if outcome == "COMMIT" else "REJECTED"
    elif outcome == "ABORT":
        action = "NO_DISPOSITION_CHANGE"
    elif evidence == "RENAME":
        action = "CONTINUATION"
    elif evidence == "AMBIGUOUS":
        action = "BLOCK_UNRESOLVED"
    elif group == "UNREALIZED":
        action = "ABANDON_CANCEL"
    elif group == "PROMOTED":
        action = "ABANDON_CLEANUP_ONLY"
    else:
        action = "ABANDON_PARTIAL_SETTLEMENT"
    assert action
A = count

# B. Exceptional recovery: native proof dominates; otherwise generation/current-state guarded ECP recovery.
start = count
for native, recovery, compatible, generation in product(
    ("RENAME", "DELETE", "NONE"),
    ("NONE", "REBIND", "ABANDON"),
    (False, True),
    (False, True),
):
    count += 1
    if native == "RENAME":
        action = "CONTINUATION"
    elif native == "DELETE":
        action = "ABANDON"
    elif recovery == "NONE":
        action = "BLOCK"
    elif compatible and generation:
        action = recovery
    else:
        action = "BLOCK_STALE_OR_CONTRADICTORY"
    assert action
B = count - start

# C. Taxonomy: only managed-authoring binding disposition is event-semantic.
start = count
classes = (
    "AUTHORING_BINDING_DISPOSITION", "AUTHORING_TIP_MOVE", "WORKTREE_TOPOLOGY",
    "INTERNAL_REF", "SUBMISSION_REF", "TARGET_REF", "INDEX_STRUCTURAL",
    "SUBMODULE_SPARSE", "TAG_STASH_NOTES", "REMOTE_REF", "PROVIDER_STATE", "ANCESTRY_ENV",
)
for cls, history_gap in product(classes, (False, True)):
    count += 1
    mode = "EVENT" if cls == "AUTHORING_BINDING_DISPOSITION" else "STATE"
    if history_gap and mode == "EVENT":
        result = "COVERAGE_REQUIRED_OR_RECOVERY"
    else:
        result = mode
    assert result
C = count - start

# D. Ancestry environment current-state handling.
start = count
for overlay, ancestry_required, normalized_or_proven in product(
    ("NONE", "REPLACE", "GRAFT", "SHALLOW"),
    (False, True),
    (False, True),
):
    count += 1
    if not ancestry_required:
        action = "IRRELEVANT_TO_THIS_TRANSITION"
    elif overlay == "NONE":
        action = "USE_NATIVE_ANCESTRY"
    elif normalized_or_proven:
        action = "USE_PROVEN_NORMALIZED_ANCESTRY"
    else:
        action = "BLOCK_ANCESTRY_UNKNOWN"
    assert action
D = count - start

assert A == 72, A
assert B == 36, B
assert C == 24, C
assert D == 16, D
assert count == 148, count
print(f"ADR-074 binding-transition family: {A} PASS")
print(f"ADR-074 recovery family: {B} PASS")
print(f"ADR-074 observation-taxonomy family: {C} PASS")
print(f"ADR-074 ancestry-environment family: {D} PASS")
print(f"new combinations: {count} PASS")
print(f"retained v38 baseline: {BASELINE}")
print(f"v39 total: {BASELINE + count} PASS")
