# ADR-005: Coordinate simultaneous `ruu` invocations with fine-grained claims and expected-ref checks

- **Status:** Accepted — top-level simultaneous-converger arbitration superseded by ADR-041; resource-claim/CAS core retained
- **Date:** 2026-09-04
- **Decision order:** 005

## Context

Several sessions may invoke `ruu` simultaneously. They can discover the same dirty worktree or race to advance the same convergence-unit/target ref. Blind concurrent mutation can create duplicate commits, stale-ref overwrites, or inconsistent integration.

## Decision

Use separate, fine-grained coordination mechanisms:

- atomic contribution-unit-worktree mutation claims for exclusive worktree operations;
- convergence-unit/target ref ownership or CAS-like expected-old-OID checks for shared refs;
- ContributionUnit authoritative managed-checkpoint record claim/CAS when exact-state progression occurs without a producer ref/worktree;
- fresh Git-state revalidation immediately before mutation;
- bounded retry/skip after losing a claim;
- no global mutex across unrelated repositories/convergence units.

Actual Git refs/OIDs are more authoritative than stale orchestration metadata.

## Rationale

Contribution unit commits can remain parallel while incompatible mutations of the same shared resource are serialized or guarded atomically.

## Consequences

- No duplicate collection of one dirty worktree.
- A stale observed convergence-unit/target tip cannot be overwritten blindly.
- Independent repositories/convergence units remain parallel.
- Every claim loser must refresh before retrying.

## Alternatives considered

- **Global Git mutex:** rejected because it unnecessarily serializes unrelated work.
- **Metadata-only locking:** rejected because metadata can become stale relative to actual Git state.
- **Blind branch/push overwrite:** rejected as unsafe under concurrent agents.

## Amendment by ADR-024/ADR-033

Invocation-principal identity is separate from contribution-unit mutation authority. Fine-grained claims cannot manufacture external authority. Under the current ADR-041 model a ContributionUnit worktree is claimable only when durable mutation access is `TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL`.

## Amendment by ADR-026 and ADR-028

Fine-grained coordination now also covers:
- direct target-promotion operations when repository policy is `DIRECT`;
- promotion-unit/submission-ref materialization;
- rewriteable submission-ref restack/rebase revisions.

Rewriteable submission updates require exact expected-old remote/local state; this exception never grants non-fast-forward authority over contribution unit, convergence-unit, or target refs.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-031

Git mutation/resource claims and verification compute admission are separate mechanisms.

Fine-grained claims continue to maximize safe concurrency across unrelated worktrees/refs/promotion resources. ADR-057 moves development-validation execution/capacity outside `ruu`; external validation waits therefore do not become Git mutation claims or a global Git mutex.

Historical ADR-031 wording referred to a `ruu` verification queue. Under ADR-057 that queue no longer exists in the core. The retained rule is narrower: **external development-validation scheduling/compute state never substitutes for worktree/ref mutation authority, and a Git claim never grants Development System validation authority or capacity.**

## Amendment by ADR-033

Fine-grained claims cannot manufacture external mutation authority. Under ADR-041 a ContributionUnit worktree is claimable only when the External Control Plane reports `TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL`. `PROTECTED_EXTERNAL` or `UNKNOWN` remains non-claimable.

The exclusive claim/CAS rules themselves are unchanged.

## Amendment by ADR-038

A ContributionUnit may remain logically valid after its producer branch/worktree disappears. If an unresolved authoritative checkpoint must be synchronized/reconciled in an isolated integration workspace, advancing the logical `latest_authoritative_managed_checkpoint_oid` requires fine-grained ownership/CAS on that exact ContributionUnit managed-state record.

The operation must preserve exact-old checking and durable reachability of the produced OID until it is either adopted by the bound ConvergenceUnit or recorded for recovery. This does not recreate the user's deleted contribution branch/worktree and does not grant editing-surface mutation authority.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-041

ADR-041 supersedes this ADR's assumption that several independent top-level `ruu` engines compete concurrently. V1 now coalesces simultaneous explicit invocations as durable convergence demand behind at most one authoritative top-level executor in the single-host coordination domain.

Therefore the historical `bounded retry/skip after losing a claim` / `claim loser refreshes before retrying` rules are no longer the scheduling policy between top-level invocations. Fine-grained claims and expected-old/CAS remain normative for actual mutable resources, internal parallelism, External Control Plane transfer arbitration, exact managed-state transitions, and recovery.

Current ContributionUnit mutation access is `PROTECTED_EXTERNAL | TRANSFERABLE_TO_RUU | TRANSFERABLE_GENERAL | UNKNOWN`; exact-invocation transfer states are retired.


## Amendment by ADR-057

Development-validation execution capacity is external to `ruu`. Fine-grained Git claims protect Git/provider correctness only; an external Development System may schedule tests however it chooses.
