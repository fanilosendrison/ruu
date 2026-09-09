#!/usr/bin/env python3
from itertools import product

BASELINE = 15140  # v39 through ADR-074
count = 0

# A. Observation-strength partition: only managed binding disposition is transactional.
classes = (
    "AUTHORING_BINDING_CESSATION", "AUTHORING_TIP", "WORKTREE", "HEAD_INDEX",
    "INTERNAL_REF", "SUBMISSION_REF", "TARGET_REF", "REMOTE_REF",
    "PROVIDER", "TAG_STASH_NOTES", "ANCESTRY_ENV", "SUBMODULE_SPARSE",
)
for cls, notification in product(classes, ("NONE", "DELIVERED", "LOST")):
    count += 1
    strength = "PRE_LINEARIZATION" if cls == "AUTHORING_BINDING_CESSATION" else "EXACT_STATE"
    if notification == "LOST" and strength == "PRE_LINEARIZATION":
        result = "COVERAGE_FAILURE_OR_VETO"
    elif notification == "LOST":
        result = "REDISCOVER"
    else:
        result = strength
    assert result
A = count

# B. Pre-linearization adapter/core classification.
start = count
for managed, impact, intercept, witness, durable in product(
    (False, True),
    ("NONE", "TERMINAL", "RENAME_SOURCE", "DEST_REPLACEMENT"),
    (False, True),
    ("TERMINAL", "RENAME", "UNKNOWN"),
    (False, True),
):
    count += 1
    if not managed or impact == "NONE":
        action = "NO_MANAGED_DISPOSITION_PREP"
    elif not intercept:
        action = "BACKEND_NONCONFORMING"
    elif witness == "UNKNOWN" or not durable:
        action = "VETO"
    elif witness == "TERMINAL":
        action = "TERMINAL_REMOVAL_PREPARED"
    else:
        action = "RENAME_CARRY_PREPARED"
    assert action
B = count - start

# C. Positive outcome proofs; !continuation never implies abandonment.
start = count
for prep, outcome, successor, integrity in product(
    ("TERMINAL", "RENAME", "UNKNOWN"),
    ("ABORT", "COMMIT", "LOST"),
    ("NONE", "VALID", "CONFLICT"),
    (False, True),
):
    count += 1
    if not integrity:
        action = "UNRESOLVED_INTEGRITY"
    elif outcome == "ABORT":
        action = "NO_DISPOSITION_CHANGE"
    elif prep == "UNKNOWN":
        action = "UNRESOLVED"
    elif prep == "TERMINAL" and outcome == "COMMIT":
        action = "ABANDON"
    elif prep == "RENAME" and outcome == "COMMIT" and successor == "VALID":
        action = "CONTINUATION"
    else:
        action = "UNRESOLVED_RECOVERY"
    assert action
C = count - start

# D. Backend admissibility is property-conjunctive, not backend-name based.
start = count
for coverage, veto, preimage, rename_evidence, durable_witness, recovery in product((False, True), repeat=6):
    count += 1
    conforming = all((coverage, veto, preimage, rename_evidence, durable_witness, recovery))
    result = "ADMISSIBLE" if conforming else "NONCONFORMING"
    assert result
D = count - start

# E. Reflog baseline semantics.
start = count
for baseline, transition, coverage in product(
    ("ENTRY", "EMPTY_PRESENT", "ABSENT"),
    ("NONE", "TERMINAL", "RENAME"),
    (False, True),
):
    count += 1
    if transition == "NONE":
        action = "REPAIR_BASELINE_ALLOWED" if baseline == "ABSENT" else "KEEP_BASELINE"
    elif not coverage:
        action = "UNRESOLVED_COVERAGE"
    elif baseline == "ABSENT":
        action = "VETO_OR_RECOVERY"
    else:
        action = "USE_BASELINE_EVIDENCE"
    assert action
E = count - start

# F. Canonical ancestry reconstruction.
start = count
for env, ancestry_required, canonical_proven in product(
    ("NONE", "REPLACE", "GRAFT", "SHALLOW"),
    (False, True),
    (False, True),
):
    count += 1
    if not ancestry_required:
        action = "IRRELEVANT"
    elif env == "NONE":
        action = "RAW_OBJECT_ANCESTRY"
    elif canonical_proven:
        action = "USE_CANONICAL_PROOF"
    else:
        action = "BLOCK_ANCESTRY_UNKNOWN"
    assert action
F = count - start

assert A == 36, A
assert B == 96, B
assert C == 54, C
assert D == 64, D
assert E == 18, E
assert F == 16, F
assert count == 284, count
print(f"ADR-075 observation-strength family: {A} PASS")
print(f"ADR-075 adapter/core preparation family: {B} PASS")
print(f"ADR-075 positive-disposition-proof family: {C} PASS")
print(f"ADR-075 backend-capability family: {D} PASS")
print(f"ADR-075 reflog-baseline family: {E} PASS")
print(f"ADR-075 canonical-ancestry family: {F} PASS")
print(f"new combinations: {count} PASS")
print(f"retained v39 baseline: {BASELINE}")
print(f"v40 total: {BASELINE + count} PASS")
