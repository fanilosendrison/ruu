# ADR-009: Require exclusive contribution-unit-worktree mutation authority

- **Status:** Accepted — authorization model amended by ADR-024, ADR-033, ADR-034, ADR-038, ADR-040, and ADR-041; bounded contribution-unit lifecycle clarified by ADR-035
- **Date:** 2026-09-04
- **Decision order:** 009

## Context

Even with isolated worktrees, `ruu` can race with an external producer, internal parallel operation, or stale/recovering execution if incompatible actors mutate the same worktree/index/ref relationship.

## Decision

Any `ruu` operation that mutates a contribution-unit worktree requires both:

```text
external mutation access is `TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL`
+
exclusive worktree claim held by the current authoritative executor/operation
```

The transfer/claim boundary must be race-safe: transferability is revalidated under the same authority arbitration that establishes the claim, and the External Control Plane prevents external reacquisition/mutation while the claim is held.

This requirement applies to commit collection, synchronization/candidate construction that mutates a checked-out contribution-unit state, and reset/checkout movement. Semantic conflict authoring is outside `ruu` under ADR-040. Contribution branch/worktree deletion lifecycle is outside `ruu` under ADR-038.

## Rationale

A clean checkout or authorized invocation principal does not prove exclusive mutation authority. The safety invariant is about the exact worktree resource and the current authoritative executor/operation, not the trigger that requested convergence.

## Consequences

- External protection is absolute for `ruu`.
- Transferability permits a claim attempt; it is not itself mutation authority.
- A stale/fenced executor or incompatible internal/recovery claim never authorizes the current executor.
- Unknown/contradictory authority fails closed.
- Producer/runtime liveness mechanisms remain outside `ruu`.

## Alternatives considered

- **Rely on caller identity:** rejected by ADR-024.
- **Rely on heartbeat/lease expiry inside `ruu`:** rejected by ADR-033.
- **Mutate clean worktrees without claiming them:** rejected because clean state does not prevent a concurrent producer from resuming.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](EXTERNAL-CONTROL-PLANE-CONTRACT.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-040

Candidate ownership is scoped to this valid mutation-authority boundary, not to the identity of the process that wrote individual files. Hooks/generators/subordinate tools executing inside the authorized boundary contribute to the same exact candidate. A known mutation that violates the boundary is a fail-closed integrity/staleness condition and cannot be adopted until authority/exact state are re-established and the exact result is fully reverified.


## Amendment by ADR-041

Top-level explicit invocations no longer compete for the worktree. They coalesce behind one fenced executor. The exclusive worktree claim remains required for race-safe External Control Plane transfer, internal parallel operations, and recovery, but it is executor/operation-scoped rather than invocation-trigger-scoped.
