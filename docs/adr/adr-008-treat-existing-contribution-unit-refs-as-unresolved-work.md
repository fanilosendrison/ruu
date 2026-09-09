# ADR-008: Track ContributionUnit obligations explicitly until exact terminal resolution

- **Status:** Accepted — terminology/lifecycle clarified by ADR-025, ADR-034, ADR-035, and ADR-038; readiness/ref semantics amended by ADR-037/ADR-038
- **Date:** 2026-09-04
- **Decision order:** 008

## Context

Allowing managed contribution state to become irrelevant merely because a branch/ref/worktree disappears creates ambiguity about whether an exact checkpoint still needs to converge. Conversely, treating physical artifact existence as the logical ContributionUnit itself incorrectly couples convergence to editing-artifact lifecycle.

## Decision

If a ContributionUnit has an unresolved authoritative managed checkpoint in the active convergence graph, that convergence unit still has unresolved contribution state.

A ContributionUnit stops blocking internal readiness only after its lifecycle is `CLOSED` and every exact managed contribution obligation that matters to convergence is resolved.

Physical branch/ref/worktree presence or absence is not itself the readiness criterion. Under ADR-038, an absent editing artifact is harmless when no unresolved exact managed contribution remains, and an unresolved checkpoint may continue to converge from its exact OID if that state remains recoverable.

Therefore `READY_INTERNAL` requires zero remaining unresolved ContributionUnit obligations plus the other exact readiness/verification conditions; historical or absent editing artifacts alone do not decide readiness.

## Rationale

The system should reason from explicit logical lifecycle and exact managed Git state, not infer semantics from branch/worktree cleanup or retention.

## Consequences

- Integration of the current state does not automatically close the ContributionUnit.
- `OPEN` ContributionUnits may still produce additional contribution to their current convergence scope.
- `CLOSED` ContributionUnits are terminal for future contribution production and never reopen.
- Any unresolved exact ContributionUnit checkpoint obligation blocks convergence-unit internal readiness.
- Branch/ref/worktree deletion or retention does not itself create or resolve a convergence obligation.
- A still-required exact checkpoint that becomes unrecoverable is a localized recovery/data-loss condition under ADR-038.

## Alternatives considered

- **Treat every retained historical ref as unresolved forever:** rejected because it conflates logical convergence obligations with artifact retention.
- **Treat missing refs/worktrees as automatically resolved:** rejected because an exact checkpoint may still be required.
- **Delete immediately after each integration:** outside `ruu` responsibility under ADR-038.
