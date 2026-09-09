# ADR-024: Separate invocation principal from contribution-unit mutation authority

- **Status:** Accepted — delegation mechanics superseded by ADR-033/ADR-041; terminology clarified by ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- **Date:** 2026-09-04
- **Decision order:** 024

## Context

The actor that invokes `ruu` is not necessarily the actor/runtime that produced work in a given context. Invocation capability must therefore not imply authority to mutate every worktree.

## Decision

Keep these identities/authorities distinct:

```text
invocation_principal
= authenticated/authorized actor that may invoke ruu

contribution_unit_id
= opaque repository-local isolation identity

mutation_access
= external statement that this exact contribution unit is protected or transferable

worktree_claim
= Ruu's exclusive current-executor/operation mutation claim
```

Authorization to mutate a contribution-unit worktree requires valid transferability plus the exclusive claim. Invocation-principal identity alone is never sufficient.

No global producer identity is required by `ruu`.

## Rationale

Humans, scripts, agents, Turnlock, `/go`, and other orchestrators may all validly invoke convergence. Tying worktree ownership to caller identity would either block legitimate convergence or accidentally broaden authority.

## Consequences

- A privileged invocation principal cannot bypass external contribution-unit protection.
- Simultaneous invocation triggers coalesce; caller identity does not determine resource ownership.
- Durable External Control Plane transferability is independent of trigger identity; stale/fenced executor ownership never authorizes the current executor.
- Actor/session/process/model identity is not inferred from `contribution_unit_id`.

## Alternatives considered

- **Invocation capability implies authority over all contribution units:** rejected because it destroys isolation.
- **Infer authority from process/session ownership:** rejected because runtime identity and repository-local mutation authority are different concepts.
- **Maintain an internal active-context delegation ontology:** superseded by ADR-033's external mutation-access contract.


## Amendment by ADR-041

ADR-041 strengthens this separation: an explicit invocation is only a coalescible convergence-demand trigger and carries no ContributionUnit mutation authority. The historical `TRANSFERABLE_TO_THIS_INVOCATION` / `TRANSFERABLE_TO_OTHER_INVOCATION` model is retired. External mutation authority is durable trigger-independent External Control Plane state; the current fenced executor may mutate only after acquiring the exact required resource claim.

## Amendment by ADR-055

The External Control Plane companion contract now explicitly carries this pre-ADR-039 boundary: invocation/discovery trigger identity grants neither ContributionUnit mutation authority nor semantic ownership of unrelated review/reconciliation/settlement work, and cannot narrow global sweep scope.
