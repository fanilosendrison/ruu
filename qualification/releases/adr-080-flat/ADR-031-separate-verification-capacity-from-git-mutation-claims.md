# ADR-031: Separate verification execution capacity from Git mutation claims

- **Status:** Superseded as a Ruu component by ADR-057
- **Date:** 2026-09-04
- **Decision order:** 031

## Current normative reading after ADR-057

This ADR is **superseded as a `ruu` component**. Validation executor capacity/scheduling belongs entirely to the Development System. The only retained architectural lesson is negative: external development-validation compute must not be conflated with Git/provider mutation authority or claims.

## Context

The predecessor `git-commits-push` effectively serialized invocations and therefore serialized long full-suite verification on the current host. `ruu` deliberately replaces that coarse global serialization with fine-grained worktree/ref/promotion claims so unrelated agents and repositories can progress concurrently.

If verification concurrency were implicitly derived from those fine-grained claims, several expensive suites could begin simultaneously on a resource-constrained executor even though Git-state concurrency itself is safe.

Git correctness ownership and compute admission are separate concerns.

## Decision

Model verification execution capacity independently from Git mutation claims.

```text
mutation/ref/worktree claims
→ protect correctness of Git/provider resources
→ remain fine-grained

verification capacity
→ limits concurrent full-verification executions per configured executor/resource pool
→ may be coarse
```

A verification scheduler/admission layer MUST be able to queue otherwise-authorized verification work without turning that queue into a global Git mutation mutex.

Initial policy for the current old iMac executor may be:

```text
verification_capacity = 1
```

while independent contribution units, worktrees, claims, metadata reads, provider waits, and other safe actions remain concurrent.

Verification capacity is an executor property/policy, not an invariant that every host supports only one verification.

The verification executor is abstract. The domain MUST NOT depend semantically on Bazel, Docker, a VM, GitHub Actions, or any particular local/remote technology.

When queued work reaches an executor, its candidate/evidence preconditions are revalidated; stale candidates are not verified/promoted on the basis of an old queue reservation.

## Rationale

This preserves the concurrency benefits of `ruu` without accidentally losing the practical serialization that makes long full-suite validation viable on constrained hardware today.

It also permits future sharding, remote workers, more hardware, or higher capacity without changing Git authority semantics.

## Consequences

- Fine-grained claims do not imply parallel full-suite execution.
- A host can advertise capacity independently of repository topology.
- Verification queue latency becomes observable telemetry rather than a reason to weaken Git claims.
- If verification becomes a bottleneck, the preferred response is to optimize execution (parallel test workers, sharding, caching, remote execution, hardware) before weakening the required proof.
- Exact fairness, weighting, cancellation, priority, and remote-verification execution/trust remain open design questions; ADR-041 keeps the v1 `ruu` coordination domain itself single-host.

## Alternatives considered

- **Keep one global `ruu` mutex:** rejected because unrelated Git work should remain parallel.
- **Run every claimable verification immediately:** rejected because Git isolation does not prove CPU/RAM/runtime-isolation capacity.
- **Reduce required verification whenever the local machine is slow:** rejected because executor limitations should not redefine the semantic proof requirement.

## Related decisions

Amends ADR-005 and operationalizes ADR-029/ADR-030.

## Amendment by ADR-036

Queued/running/stale verification remains a nonterminal managed obligation in every invocation's global obligation universe. Capacity waiting is refreshed without becoming a global mutex; an activity index may accelerate discovery but cannot suppress the verification obligation.


## Amendment by ADR-041

The top-level `ruu` coordination domain is single-host in v1. Verification may still evolve toward remote/sharded execution as a separate evidence/capacity concern, but such workers do not become additional authoritative top-level convergers and do not expand the coordination domain without a future explicit decision.


## Superseded by ADR-057

The separation insight remains valid — Git mutation authority and test/validation compute capacity are different resources — but ADR-057 moves validation execution capacity completely outside `ruu`.

There is no `ruu` verification scheduler, `verification_capacity`, validation-worker queue, or `WAITING_VERIFICATION_CAPACITY` core state. The Development System may implement any local/remote scheduling model it needs. `ruu` sees only exact external validation evidence/demands and continues unrelated Git obligations while such external prerequisites are missing.
