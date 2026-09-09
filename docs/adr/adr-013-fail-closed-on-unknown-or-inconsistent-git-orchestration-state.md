# ADR-013: Fail closed on unknown or inconsistent Git/orchestration state

- **Status:** Accepted — extended by ADR-022, ADR-023, ADR-026, ADR-027, ADR-028, ADR-029, ADR-030, ADR-032, ADR-036, ADR-038, and ADR-040
- **Date:** 2026-09-04
- **Decision order:** 013

## Context

Persistent orchestration metadata can disagree with Git after crashes, manual operations, partial cleanup, or stale registries. Examples include orphan worktrees, unexpected detached HEAD, missing feature refs, or an in-progress operation with unknown owner.

## Decision

Introduce `UNKNOWN_INCONSISTENT` as a first-class state.

When ownership/topology cannot be reconstructed confidently:

- do not commit unknown work;
- do not delete unknown branches/worktrees;
- do not integrate/promote;
- do not overwrite refs;
- reconstruct authoritative Git facts or require explicit recovery first.

Git repository/ref/worktree state outranks orchestration metadata for repository facts.

## Rationale

Optimistically “repairing” ambiguous state can destroy work or promote incomplete code. Unknown state should stop destructive automation rather than guess.

## Consequences

- “registry says zero contribution units” is insufficient if orphan contribution-unit state may exist.
- Unknown states block feature promotion and cleanup.
- The finite state model can safely evolve: newly encountered states default to fail-closed.

## Alternatives considered

- **Trust registry as source of truth:** rejected because it can be stale after crashes/manual Git activity.
- **Automatically delete unexpected state:** rejected because ownership/work may be unknown.

## Amendment by ADR-022

Repository identity/location and catalog membership are also subject to fail-closed reconstruction.

Ambiguous duplicate identities, an unresolved known-repository location, or registry↔Git disagreement that could hide managed work keeps/re-enters the repository in active recovery and prevents destructive transitions or quiescent deactivation.

## Amendment by ADR-023

If a new managed write requires editing topology that was never provisioned, `ruu` does not silently create it. ADR-038 further narrows missing-artifact inconsistency: absence of a contribution branch/worktree alone is not inconsistent. Recovery is required only when a still-nonterminal managed obligation depends on exact Git state/topology that cannot be reconstructed or recovered.

## Amendment by ADR-026, ADR-027, and ADR-028

Fail-closed state now includes ambiguous/stale repository promotion policy, unsupported promotion-policy/provider combinations, ambiguous promotion-unit source bindings, unknown submission rewrite ownership, and unrecognized submission-head movement.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-029, ADR-030, and ADR-032

Unknown/stale/inconsistent development-validation evidence, development-gate/context binding, or review-request/head binding fails closed for the affected authoritative transition. Validation mutation/non-convergence/executor state is outside `ruu` under ADR-057.

These blocked states remain localized and do not become a global convergence mutex.

## Amendment by ADR-036

A stale/missing derived repository activity index cannot make authoritative nonterminal managed obligations disappear from an invocation. Index disagreement with authoritative obligation records is reconstructed or fails closed where ambiguity could hide managed work.

## Amendment by ADR-038

ContributionUnit identity and convergence continuity are exact-state based, not branch/worktree-existence based. `ruu` must not infer remote deletion, local recreation, closure, or semantic abandonment from missing editing artifacts. A known unresolved checkpoint OID that becomes unrecoverable is a localized `BLOCKED_MISSING_MANAGED_STATE`/recovery-data-loss condition; unrelated global progress continues.


## Amendment by ADR-040

A known/observed mutation that contradicts the required ContributionUnit mutation-authority boundary is treated as stale/inconsistent candidate state, not as an actor-attribution question. No authoritative adoption is permitted until valid authority and exact state are re-established and the resulting exact state satisfies any policy-required exact external development-validation prerequisite.

An authoring-required merge conflict is represented as a localized exact-state-bound `RECONCILIATION_REQUIRED` obligation. Its diagnostic snapshot does not authorize later adoption and is revalidated/superseded against current Git/topology/policy state on later sweeps.


## Amendment by ADR-057

Unknown external validation evidence fails closed for the affected Git transition, but test-runner/executor/mutation states are no longer part of the `ruu` unknown-state ontology.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
