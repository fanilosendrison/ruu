# ADR-003: Base commit collection on contribution-unit eligibility, not task completion

- **Status:** Accepted — amended by ADR-024, ADR-029, ADR-033, ADR-034, ADR-035, and ADR-041
- **Date:** 2026-09-04
- **Decision order:** 003

## Context

`ruu` may be invoked in the middle of a larger task simply to checkpoint current work. Conversely, an external producer may stop or crash without the semantic task being complete. Task status therefore cannot determine whether dirty state may be collected.

## Decision

Commit collection depends on repository-local contribution-unit safety, not semantic completion.

For the current authoritative executor/operation:

```text
PROTECTED_EXTERNAL
UNKNOWN
→ not collectible

TRANSFERABLE_TO_RUU
or TRANSFERABLE_GENERAL
+ exclusive worktree claim held by the current authoritative executor/operation
+ exact topology/state revalidation
+ stable exact development-validation evidence
→ exact managed checkpoint may be committed
```

A commit is a checkpoint, not a completion/readiness/closure signal. Waiting for user input, turn completion, or producer inactivity likewise does not determine contribution-unit closure.

## Rationale

The relevant safety question is whether the current authoritative executor/operation may mutate and commit this exact contribution-unit candidate now. Product/task completion is a different layer.

## Consequences

```text
commit != semantic completion
commit != contribution-unit closure
commit != convergence-unit readiness
commit != promotion readiness
```

No heartbeat, runtime liveness classification, invocation-principal identity, or convergence trigger substitutes for durable transferability + exclusive claim.

## Alternatives considered

- **Commit only DONE tasks:** rejected because intermediate verified checkpoints are required.
- **Infer eligibility from caller identity:** rejected by ADR-024.
- **Infer eligibility from runtime inactivity:** rejected by ADR-033.
- **Commit dirty state without exact full verification:** rejected by ADR-029/030.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
