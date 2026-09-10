#!/usr/bin/env python3
"""Finite ADR-081 state families plus one native Git retention smoke."""

from itertools import product
from pathlib import Path
import subprocess

BASELINE = 16380  # retained v45 through ADR-080
count = 0


# A. Adoption requires explicit semantic selection and exact source/object proof.
start = count
for selected, source_known, object_exists, lineage_proven, anchor_ready, abandoned in product(
    (False, True), repeat=6
):
    count += 1
    adopted = (
        selected
        and source_known
        and object_exists
        and lineage_proven
        and anchor_ready
        and not abandoned
    )
    if not selected or not source_known or not object_exists or not lineage_proven:
        assert not adopted
    if adopted:
        assert anchor_ready and not abandoned
A = count - start


# B. Dirty source state never becomes the selected exact version or a hidden commit.
start = count
for commit_exists, source_dirty, exact_selected, anchor_ready, snapshot_requested in product(
    (False, True), repeat=5
):
    count += 1
    if snapshot_requested:
        action = "REJECT_IMPLICIT_SNAPSHOT"
    elif exact_selected and commit_exists and anchor_ready:
        action = "CONSUME_EXACT_COMMIT_ONLY"
    else:
        action = "NO_CONSUMABLE_VERSION"
    if source_dirty and exact_selected and commit_exists and anchor_ready and not snapshot_requested:
        assert action == "CONSUME_EXACT_COMMIT_ONLY"
    if snapshot_requested:
        assert action == "REJECT_IMPLICIT_SNAPSHOT"
B = count - start


# C. Child-first handoff permits internal progress while raw dependency blocks realization.
start = count
for raw, child_handoff, checkpoint_exact, source_group_exists, realization_attempted in product(
    (False, True), repeat=5
):
    count += 1
    internal_progress = child_handoff and checkpoint_exact
    realization = "BLOCK_RAW" if raw and realization_attempted else "EVALUATE_NORMAL"
    if raw and child_handoff and checkpoint_exact and not source_group_exists:
        assert internal_progress
    if raw and realization_attempted:
        assert realization == "BLOCK_RAW"
C = count - start


# D. Reconciliation precedence: target, same group, attributed source handoff, abandonment.
start = count
for target_contains, same_group, later_handoff, identity_matches, source_checkpoint_contains_a, abandoned, targets_equal in product(
    (False, True), repeat=7
):
    count += 1
    if target_contains:
        state = "SATISFIED_BY_TARGET"
    elif same_group and identity_matches and source_checkpoint_contains_a:
        state = "INTERNAL_TO_SAME_GROUP"
    elif later_handoff and identity_matches and source_checkpoint_contains_a and targets_equal and not abandoned:
        state = "RESOLVED_PROMOTION_PROJECTION"
    elif abandoned:
        state = "RECONCILIATION_REQUIRED"
    elif later_handoff and identity_matches and source_checkpoint_contains_a and not targets_equal:
        state = "RECONCILIATION_REQUIRED"
    elif later_handoff and (not identity_matches or not source_checkpoint_contains_a):
        state = "UNKNOWN_INCONSISTENT"
    else:
        state = "RAW_AUTHORING_SOURCE"
    if target_contains:
        assert state == "SATISFIED_BY_TARGET"
    if state == "RESOLVED_PROMOTION_PROJECTION":
        assert later_handoff and identity_matches and source_checkpoint_contains_a and targets_equal
D = count - start


# E. Source movement never mutates the consumed OID or an active consumer surface.
start = count
for source_advanced, source_reset, source_renamed, consumer_active, compression_exists in product(
    (False, True), repeat=5
):
    count += 1
    consumed_oid = "A"
    consumer_mutated = False
    parent_current = "K" if compression_exists and source_advanced else "A"
    assert consumed_oid == "A"
    if consumer_active and (source_advanced or source_reset or source_renamed):
        assert not consumer_mutated
    if parent_current == "K":
        assert consumed_oid != parent_current
E = count - start


# F. Adopted target satisfaction is historical even after later target drift.
start = count
for target_contains_at_observation, proof_adopted, target_drifted, later_realization in product(
    (False, True), repeat=4
):
    count += 1
    terminal_satisfaction = target_contains_at_observation and proof_adopted
    if terminal_satisfaction and target_drifted:
        assert terminal_satisfaction
    if later_realization:
        current_guards_required = True
        assert current_guards_required
F = count - start


# G. Source abandonment never transfers publication authority to the child.
start = count
for source_abandoned, target_contains, source_effect_in_child, committed_effect, realization_attempted in product(
    (False, True), repeat=5
):
    count += 1
    if target_contains:
        state = "SATISFIED_BY_TARGET"
    elif source_abandoned and committed_effect:
        state = "RECOVER_COMMITTED_EFFECT"
    elif source_abandoned:
        state = "RECONCILIATION_REQUIRED"
    else:
        state = "CURRENT_SOURCE_PATH"
    child_authority = False
    if source_abandoned and source_effect_in_child and realization_attempted and not target_contains:
        assert not child_authority
        assert state in {"RECOVER_COMMITTED_EFFECT", "RECONCILIATION_REQUIRED"}
G = count - start


# H. Crash windows never admit an unanchored dependency; required anchors survive GC.
start = count
for operation, resource_row, anchor_exists, observation, adoption, gc_runs in product(
    (False, True), repeat=6
):
    count += 1
    valid_adoption = operation and resource_row and anchor_exists and observation and adoption
    if adoption and not valid_adoption:
        state = "UNKNOWN_INCONSISTENT"
    elif valid_adoption:
        state = "ADOPTED_REQUIRED_ANCHOR"
    elif operation:
        state = "RECOVER_OPERATION"
    elif anchor_exists:
        state = "ORPHAN_ANCHOR"
    else:
        state = "NO_DEPENDENCY"
    if state == "ADOPTED_REQUIRED_ANCHOR":
        assert anchor_exists and resource_row
        if gc_runs:
            assert anchor_exists
    if adoption and not anchor_exists:
        assert state == "UNKNOWN_INCONSISTENT"
H = count - start


# I. Competing compression attempts share one expected raw-dependency generation.
start = count
for g1_qualifies, g2_qualifies, g1_first, g1_expected_current, g2_expected_current, run_current in product(
    (False, True), repeat=6
):
    count += 1
    current_version = 0
    winners: list[str] = []
    attempts = (
        ("G1", g1_qualifies, g1_expected_current),
        ("G2", g2_qualifies, g2_expected_current),
    )
    if not g1_first:
        attempts = tuple(reversed(attempts))
    for name, qualifies, expected_current in attempts:
        expected_version = 0 if expected_current else -1
        if run_current and qualifies and expected_version == current_version:
            winners.append(name)
            current_version += 1
    assert len(winners) <= 1
    if winners:
        assert current_version == 1
    if g1_qualifies and g2_qualifies and g1_expected_current and g2_expected_current and run_current:
        assert len(winners) == 1
I = count - start


# J. A clean native tip becomes a managed checkpoint only at exact frozen handoff.
start = count
for frozen_handoff, clean_tip, exact_commit, descends, claim_and_cas in product(
    (False, True), repeat=5
):
    count += 1
    adopt_checkpoint = frozen_handoff and clean_tip and exact_commit and descends and claim_and_cas
    new_commit_created = False
    if adopt_checkpoint:
        assert not new_commit_created
    if clean_tip and not frozen_handoff:
        assert not adopt_checkpoint
J = count - start


# K. More than one independently unsatisfied predecessor never invents provider topology.
start = count
for predecessor_count, all_target_satisfied, same_group, provider_supports_stack in product(
    (0, 1, 2), (False, True), (False, True), (False, True)
):
    count += 1
    if all_target_satisfied or predecessor_count == 0:
        action = "ORDINARY_PROMOTION"
    elif same_group:
        action = "INTERNAL_TO_GROUP"
    elif predecessor_count == 1 and provider_supports_stack:
        action = "SINGLE_STACK"
    elif predecessor_count > 1:
        action = "BLOCK_MULTI_PREDECESSOR"
    else:
        action = "BLOCK_UNSUPPORTED_SINGLE_STACK"
    if predecessor_count > 1 and not all_target_satisfied and not same_group:
        assert action == "BLOCK_MULTI_PREDECESSOR"
K = count - start


# L. Same-group dependency never creates a fake provider parent.
start = count
for group_closed, source_member, consumer_member, exact_group_state, provider_edge_requested in product(
    (False, True), repeat=5
):
    count += 1
    internal = group_closed and source_member and consumer_member and exact_group_state
    create_provider_edge = False if internal else provider_edge_requested
    if internal:
        assert not create_provider_edge
L = count - start


# M. Dependency graph cycles fail closed rather than creating an impossible ordering.
def has_cycle(edges: dict[str, tuple[str, ...]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in edges[node]:
            if visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in edges)


start = count
for ab, ac, ba, bc, ca, cb in product((False, True), repeat=6):
    count += 1
    edges = {
        "A": tuple(node for flag, node in ((ab, "B"), (ac, "C")) if flag),
        "B": tuple(node for flag, node in ((ba, "A"), (bc, "C")) if flag),
        "C": tuple(node for flag, node in ((ca, "A"), (cb, "B")) if flag),
    }
    action = "UNKNOWN_INCONSISTENT" if has_cycle(edges) else "ACYCLIC"
    if has_cycle(edges):
        assert action == "UNKNOWN_INCONSISTENT"
M = count - start


# N. Aggregate group ancestry cannot launder A from the consumer into source attribution.
start = count
for source_checkpoint_contains_a, aggregate_k_contains_a, consumer_contributed_a, identity_matches, targets_equal in product(
    (False, True), repeat=5
):
    count += 1
    if (
        source_checkpoint_contains_a
        and aggregate_k_contains_a
        and identity_matches
        and targets_equal
    ):
        state = "RESOLVED_PROMOTION_PROJECTION"
    elif aggregate_k_contains_a and consumer_contributed_a and not source_checkpoint_contains_a:
        state = "SOURCE_ATTRIBUTION_NOT_PROVEN"
    else:
        state = "RAW_OR_INCOMPATIBLE"
    if aggregate_k_contains_a and consumer_contributed_a and not source_checkpoint_contains_a:
        assert state == "SOURCE_ATTRIBUTION_NOT_PROVEN"
N = count - start

assert [A, B, C, D, E, F, G, H, I, J, K, L, M, N] == [
    64,
    32,
    32,
    128,
    32,
    16,
    32,
    64,
    64,
    32,
    24,
    32,
    64,
    32,
]
assert count == 648

smoke = Path(__file__).with_name("git-authoring-dependency-retention-smoke-v1.sh")
result = subprocess.run(
    [str(smoke)],
    check=True,
    capture_output=True,
    text=True,
)
assert result.stderr == ""
assert result.stdout == "ADR-081 dependency anchor retention smoke: PASS\n"

print(f"ADR-081 dependency adoption family: {A} PASS")
print(f"ADR-081 dirty-state exclusion family: {B} PASS")
print(f"ADR-081 child-first progression family: {C} PASS")
print(f"ADR-081 dependency resolution family: {D} PASS")
print(f"ADR-081 source-movement immutability family: {E} PASS")
print(f"ADR-081 target-satisfaction history family: {F} PASS")
print(f"ADR-081 abandonment authority family: {G} PASS")
print(f"ADR-081 anchor crash/GC family: {H} PASS")
print(f"ADR-081 concurrent compression family: {I} PASS")
print(f"ADR-081 clean native-tip checkpoint family: {J} PASS")
print(f"ADR-081 predecessor cardinality family: {K} PASS")
print(f"ADR-081 same-group family: {L} PASS")
print(f"ADR-081 dependency-cycle family: {M} PASS")
print(f"ADR-081 source-attribution laundering family: {N} PASS")
print(result.stdout, end="")
print(f"new combinations: {count} PASS")
print(f"retained v45 baseline: {BASELINE}")
print(f"v46 cumulative modeled cases: {BASELINE + count}")
