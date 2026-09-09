# ADR-012: Isolate feature/main integration workspaces and model conflicts as recoverable blocked states

- **Status:** Accepted — amended by ADR-027, ADR-029, ADR-030, ADR-038, and ADR-040
- **Date:** 2026-09-04
- **Decision order:** 012

## Context

Feature/main reconciliation needs an index/checkout or equivalent Git operation state. Reusing a contribution unit's active worktree would violate contribution unit isolation. Merge conflicts and crashes can also leave Git in-progress state that must not be mistaken for successful convergence.

## Decision

Shared feature/main reconciliation uses a dedicated integration/convergence worktree or equivalent isolated plumbing, never an active contribution unit checkout.

A conflict creates an explicit owned `BLOCKED_CONFLICT` state. The affected target ref is not advanced as though reconciliation succeeded. The operation must later resolve+validate+commit/update, or abort+restore.

Recovery inspects real Git in-progress state before starting any incompatible operation.

## Rationale

Physical isolation and explicit blocked state make conflict handling and crash recovery deterministic instead of contaminating live contribution units.

## Consequences

- Unrelated edges/features/repos may continue while one edge is conflict-blocked.
- Recovery recognizes merge/conflict state and legacy/external rebase-in-progress state.
- Integration workspaces require their own ownership and cleanup.

## Alternatives considered

- **Perform shared merges in a contribution-unit worktree:** rejected because it can mutate a live contribution unit checkout.
- **Treat a conflict as partial success:** rejected because the protected ref has not safely converged.
- **Blindly restart after crash:** rejected because an in-progress Git operation may already exist.

## Supersession / amendment note

No local feature→main merge workspace is needed after ADR-018. The integration workspace remains required for Git-controlled feature merges such as protected-main→feature and feature→contribution unit reconciliation/conflict handling. PR→main is external governance.

## Amendment by ADR-027 and ADR-028

Isolated integration/projection workspaces are also required when materializing a promotion unit from exact convergence-unit inputs or rebuilding/restacking a submission ref. Conflicts in those operations are explicit blocked states and never mutate contribution-unit worktrees.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-029 and ADR-030

Isolated integration/projection workspaces are also candidate-verification workspaces.

When reconciliation/materialization creates a new exact state, that state is development-validated before the authoritative destination ref is advanced/published. A conflict or verification failure leaves the destination authoritative ref unchanged and the affected operation blocked/retryable.

A Ruu-synthesized candidate is immutable as a validation subject. If current policy requires development validation and no exact evidence exists, adoption waits on an external `DevelopmentValidationDemand`; `ruu` does not mutate the candidate through a test/generator fixed-point loop.

## Amendment by ADR-038

When a ContributionUnit's producer branch/worktree is absent but an unresolved exact managed checkpoint remains reachable, required synchronization/reconciliation may be materialized in an isolated integration workspace. The resulting verified exact checkpoint may advance the ContributionUnit's logical managed-checkpoint record under fine-grained expected-old/CAS coordination, without recreating the producer editing branch/worktree.

An operation-owned temporary reachability anchor may be used so crash/recovery cannot lose the newly produced exact state before ConvergenceUnit adoption or durable recovery recording.


## Amendment by ADR-040

A low-level owned merge may transiently enter `BLOCKED_CONFLICT`, but an authoring-required conflict must also produce a durable exact-state-bound `RECONCILIATION_REQUIRED` managed obligation before temporary operation state is discarded. Authoritative refs remain unchanged.

`ruu` may continue only when deterministic Git/repository mechanics produce an unambiguous candidate; that exact result still requires ordinary current-state revalidation and any policy-required exact external development-validation prerequisite. Semantic conflict authoring occurs in the external Development System. Any authored result later returns through current-state revalidation, claims/CAS, and any policy-required exact external development-validation prerequisite; the reconciliation descriptor itself grants no adoption authority.


## Amendment by ADR-057

Integration/materialization workspaces remain isolated Git-construction/recovery resources. They are no longer test-execution workspaces owned by `ruu`; newly synthesized candidates may instead wait on exact external development-validation evidence.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
