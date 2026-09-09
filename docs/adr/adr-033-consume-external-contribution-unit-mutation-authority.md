# ADR-033: Consume an external contribution-unit mutation-authority contract; do not own producer/runtime liveness

- **Status:** Accepted — terminology/cardinality/lifecycle clarified by ADR-034/ADR-035; external boundary consolidated by ADR-039; candidate-boundary semantics clarified by ADR-040; invocation-relative authority superseded by ADR-041
- **Date:** 2026-09-05
- **Decision order:** 033

## Context

Earlier decisions correctly required `ruu` to obtain exclusive authority before mutating an existing isolated worktree, but they expressed that boundary through internal liveness/lease/delegation concepts. That assigns too much producer-runtime responsibility to `ruu`.

`ruu` advances Git state from **already-existing managed contribution units**. The External Control Plane owns the producer/runtime mutation rights and decides when a repository-local contribution unit is safely transferable.

## Decision

### 1. Producer/runtime liveness is outside `ruu`

`ruu` does not define, observe, renew, expire, or recover a producer-liveness heartbeat/TTL lease.

For each managed ContributionUnit editing surface it consumes durable External Control Plane mutation-access state independent of any convergence trigger:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

Meaning:

```text
PROTECTED_EXTERNAL
→ an external work producer still retains mutation authority
→ Ruu MUST NOT mutate

TRANSFERABLE_TO_RUU
→ the External Control Plane has durably relinquished external mutation authority
  to the Ruu coordination domain
→ the current authoritative executor may attempt its exclusive worktree claim

TRANSFERABLE_GENERAL
→ no external producer retains mutation authority
→ the current authoritative executor may attempt the exclusive claim under ordinary authorization/policy

UNKNOWN
→ fail closed
```

The External Control Plane may implement these guarantees with any correct mechanism. Heartbeats, TTLs, process inspection, runtime guards, fencing tokens, etc. are not producer-liveness semantics owned by `ruu`. A convergence trigger never manufactures or carries this authority.

### 2. `contribution_unit_id` is opaque repository-local input

`ruu` binds topology, refs, worktrees, recovery, and claims to a stable opaque `contribution_unit_id` supplied by the External Control Plane.

It MUST NOT infer that identity from:

```text
process/session/model/agent identity
invocation principal
ref display name
worktree path
CWD
```

ADR-034 removes any global producer identity from the normative `ruu` model.

### 3. `ruu` owns only its side of the transfer boundary

```text
observe/revalidate durable external mutation-access state
→ if transferable, atomically acquire exclusive worktree claim for the current authoritative executor/operation
→ revalidate exact managed/Git state under the claim
→ perform authorized convergence mutations
→ release claim
```

The External Control Plane owns how external mutators become quiescent before transfer and how/when external work production may resume afterward.

### 4. Transferability is not mutation authority

```text
transferable + no exclusive claim
↛ may mutate

transferable
+ exclusive claim held by the current authoritative executor/operation
+ exact-state/topology/policy guards valid
→ mutation may proceed
```

The transfer/claim boundary must be race-safe. Transferability must be revalidated as part of, or under, the same authority arbitration that establishes the exclusive claim. While the claim is held, the External Control Plane MUST prevent external mutation/reacquisition of that worktree.

A stale/fenced executor or incompatible internal/recovery claim never authorizes the current executor. Unknown/contradictory state fails closed.

### 5. Crash responsibility is split at the boundary

```text
external producer/runtime crash
→ External Control Plane decides when the ContributionUnit is safely transferable

Ruu crash after owning a claim/Git operation
→ Ruu recovery reconciles its owned operation before safe reuse
```

## Rationale

The invariant `ruu` actually needs is:

> **never mutate a contribution-unit worktree unless external mutation authority has been safely relinquished/transferred and the current authoritative executor/operation holds the exclusive claim.**

This keeps `ruu` out of session management, process supervision, heartbeat/liveness service, and producer-runtime ownership.

## Consequences

- No normative heartbeat or producer TTL exists in `ruu`.
- Transferability and the executor/operation-scoped exclusive claim remain distinct.
- External protection applies even to a clean worktree.
- Runtime crash/stop/resume semantics stay outside `ruu`.
- `ruu` recovery remains responsible for operations it already owns.

## Alternatives considered

- **Internal heartbeat/TTL lease:** rejected because freshness is neither necessary nor sufficient to prove safe mutation authority and duplicates runtime responsibility.
- **Infer liveness from process/session state:** rejected because runtime identity is not repository-local mutation authority.
- **Invocation-principal identity implies ownership:** rejected by ADR-024.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-040

The valid mutation-authority boundary is also the normative candidate-attribution boundary for ContributionUnit work. `ruu` does not require process-level provenance for hooks/generators/subordinate tooling. A known mutation outside the authorized boundary is an integrity/staleness failure, not a reason to guess actor ownership.


## Amendment by ADR-041

Exact-invocation transferability is retired. `TRANSFERABLE_TO_RUU` is durable External Control Plane state for the local coordination domain; explicit invocations coalesce and carry no authority. The one current fenced executor may attempt the ordinary exclusive resource claim, which remains distinct from transferability.

## Amendment by ADR-064

Transferability at a dirty-checkpoint handoff has a stronger current meaning than mere claim eligibility. Once the External Control Plane has durably offered the current editing surface as transferable, no external writer may mutate it while that handoff remains current. Resumed semantic authoring requires legitimate revocation/reacquisition before any new write; if `ruu` already holds the exclusive claim, reacquisition waits for safe release/recovery. This frozen interval is the pre-commit exact-state bridge and does not assert that tests/reviews passed.
