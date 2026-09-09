# ADR-011: Use an atomic convergence-unit readiness/promotion barrier

- **Status:** Accepted — transition semantics amended by ADR-018, ADR-025, ADR-026, ADR-027, ADR-034, ADR-035, and ADR-037
- **Date:** 2026-09-04
- **Decision order:** 011

## Context

Checking "zero unresolved contribution units remain" and then binding/promoting a convergence-unit result is subject to TOCTOU if another path can create a new contribution unit, reactivate convergence scope, or advance the relevant source between the readiness check and the promotion binding/mutation.

## Decision

The transition that turns exact convergence-unit readiness into an exact promotion binding/mutation must be guarded atomically with respect to the mutable repository-local convergence state.

The guarded predicate includes at least:

```text
contribution membership still SEALED
zero remaining unresolved contribution-unit obligations
exact convergence-unit source OID/readiness still current
no conflicting membership reopen / new-contribution-unit creation
current repository policy valid
exact promotion-source binding current
```

The concrete promotion action is repository-policy-driven:

```text
DIRECT → guarded descendant/expected-old target advancement
PR     → guarded source/submission binding/publication step
```

The barrier is short-lived and protects the state transition; it is not a global mutex or a review-duration lock.

## Rationale

Readiness and promotion must describe one exact source state, not two observations separated by an unguarded race window.

## Consequences

- New ContributionUnit attachment is forbidden while contribution membership is `SEALED`; explicit membership reopen/reactivation and new attachment must coordinate with the same mutable convergence-unit authority used by readiness binding.
- A stale readiness observation cannot authorize promotion.
- Unrelated repositories/units remain parallel.

## Amendment by ADR-069

The atomic readiness barrier still guards adoption of the exact live ConvergenceUnit state used at an invocation/group-authorized boundary. After successful adoption into one PromotionGroup's group-local resolution, later unrelated live movement does not retroactively invalidate that group's exact binding.

