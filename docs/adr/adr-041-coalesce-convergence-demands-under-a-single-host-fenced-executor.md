# ADR-041: Coalesce convergence demands under a single-host fenced executor

- **Status:** Accepted
- **Date:** 2026-09-05
- **Decision order:** 041

## Context

ADR-036 established that an explicit `ruu` invocation does not own a caller-local task. It creates an opportunity to advance the **complete known set of nonterminal managed obligations** to the current global fixed point.

That makes the previous simultaneous-converger model unnecessarily strong. If several callers invoke `ruu` while one global sweep is already running, replaying each invocation as a separate FIFO work item repeats the same operation over successively newer global state. The meaningful information is only that **new convergence demand and/or new externally authoritative state became visible**.

The old authority vocabulary also attached some ContributionUnit transferability to an exact invocation:

```text
TRANSFERABLE_TO_THIS_INVOCATION
TRANSFERABLE_TO_OTHER_INVOCATION
```

That is incompatible with coalescing. A coalesced trigger has no durable per-trigger execution identity that should own a worktree. External mutation authority must therefore be durable state independent of the trigger that caused another sweep.

Current requirements need safe concurrency between many local callers/processes on one host. They do not require one coordination domain to span multiple hosts.

## Decision

### 1. The v1 coordination domain is single-host

`ruu` v1 guarantees one coordinated managed universe only within one host coordination domain.

```text
many local callers/processes
→ supported

one Ruu coordination domain spanning multiple hosts
→ not a v1 requirement
```

This does not forbid ordinary Git use from other machines. It means `ruu` does not claim distributed coordination semantics across them.

### 2. Explicit invocations are coalescible convergence demands

An explicit invocation is a **trigger**, not a durable FIFO work item.

The coordination substrate maintains a durable monotonic convergence-demand relation equivalent to:

```text
requested_generation
processed_generation
```

Each accepted explicit invocation publishes any prerequisite External Control Plane changes through their authoritative channel, then atomically advances the convergence-demand generation (or an equivalent monotonic durable token).

The trigger itself carries no ContributionUnit mutation authority, Git snapshot, task identity, or processing scope.

Multiple demands that arrive before the next sweep are coalesced:

```text
requested_generation: 54 → 55 → 56 → 57

one later global sweep may cover generations 55..57 together
```

No FIFO replay of I55, I56, I57 is required merely because three callers invoked the engine.

### 3. At most one top-level executor is authoritative in the local coordination domain

At most one active top-level `ruu` executor may own global progression at a time.

The executor:

```text
snapshot target_generation = requested_generation
→ perform the ADR-036 global fixed-point sweep over current authoritative state
→ record processed_generation >= target_generation only after that sweep reaches its current fixed point
→ re-read requested_generation
→ if requested_generation > processed_generation, sweep again
→ otherwise release executor ownership and exit
```

The transition from "demand caught up" to executor release must be race-safe with a concurrent new demand so work cannot be stranded.

This is **not** a global serialization of all internal work. The one top-level executor may still run independent repository/provider/verification operations in parallel where their own resource, capacity, exact-state, and policy constraints permit it.

### 4. Executor ownership is transactional and fenced

The durable coordination substrate must provide atomic executor ownership with a monotonically advancing fencing generation/token or semantically equivalent mechanism.

ADR-042 later fixes the concrete v1 mechanism: physical top-level ownership is a process-lifetime OS exclusive lock, while durable adoption authority is the current SQLite `run_generation + run_token`. V1 does not use heartbeat/TTL expiry for automatic takeover of a live-but-hung process.

Once a newer executor generation is transactionally established:

```text
older executor generation
→ no longer authorized to create/adopt new managed progression
```

A stale executor or late worker may still exist physically, but any authoritative managed-state adoption from a fenced execution must fail closed.

The concrete single-host acquisition/release handshake, including the race-safe `ACTIVE → IDLE` release boundary, is fixed by ADR-042.

### 5. External mutation transferability is durable and trigger-independent

The current mutation-access vocabulary becomes:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

Meanings:

```text
PROTECTED_EXTERNAL
→ an external producer/control-plane owner retains mutation authority
→ Ruu MUST NOT mutate the editing surface

TRANSFERABLE_TO_RUU
→ the External Control Plane has durably relinquished external mutation authority
  to the Ruu coordination domain
→ the current authoritative executor may attempt the exclusive worktree claim

TRANSFERABLE_GENERAL
→ no external producer retains mutation authority
→ the current authoritative executor may attempt the exclusive worktree claim
  under ordinary authorization/policy rules

UNKNOWN
→ fail closed
```

`TRANSFERABLE_TO_THIS_INVOCATION` and `TRANSFERABLE_TO_OTHER_INVOCATION` are retired from the current normative model.

A caller that changes ContributionUnit authority must make that authority change durably visible through the External Control Plane **separately from** signaling convergence demand. A convergence trigger can never manufacture or carry mutation authority.

### 6. Fine-grained claims remain, but not for inter-invocation arbitration

ADR-005's expected-old/CAS and typed resource-claim safety remains applicable to actual mutable resources:

```text
ContributionUnit editing surface
ConvergenceUnit/internal refs
managed checkpoint records
PromotionUnit/submission operations
DIRECT target promotion
remote publication
provider operation identity
isolated integration/workspace resources
```

However, v1 no longer runs several independent top-level convergers that compete for those resources. Fine-grained claims protect:

- race-safe transfer from the External Control Plane;
- internal parallel operations under the one executor;
- exact resource ownership and recovery;
- stale/late operation rejection.

They are not a scheduling mechanism between simultaneous explicit invocations.

### 7. Managed-state adoption remains exact-state and fail-closed

The coordination store and Git/provider state cannot form one atomic transaction. Therefore non-atomic external effects remain recoverable through exact-state observation/journaling rules.

At minimum:

```text
managed coordination transitions
→ transactional expected-state/CAS semantics
→ a failed expected-state update never counts as adoption

Git ref transitions
→ exact expected-old OID/CAS

external effect completed but durable finalization interrupted
→ recovery observes current exact Git/provider state before deciding next action
```

Temporary mutable workspaces/anchors created by an executor generation must not be reusable in a way that lets late cleanup from an older fenced generation destroy a newer generation's physical state. Generation/incarnation-specific namespaces or an equivalent non-aliasing guarantee are required.

ADR-042 fixes the v1 CoordinationStore schema families, migration/fail-closed discipline, `Operation → Attempt → Observation → Adoption` journal, transaction boundaries, stable repository identity/relocation binding, recovery-resource lifecycle, and physical run-ownership mechanism.

### 8. Storage semantic core

The v1 architecture requires a **single-host durable transactional coordination store** capable of representing at least:

```text
managed logical coordination state
convergence demand generation
active executor ownership/fence
recoverable operation state
```

SQLite is the preferred/reference v1 backend because it provides local multi-process transactions, durability, uniqueness/CAS primitives, and schema versioning without a service dependency. The architecture is defined by the transactional semantics above, not by SQLite-specific APIs.

## Rationale

A global fixed-point engine is naturally idempotent with respect to duplicate triggers:

```text
F(F(state)) = F(state)
```

subject to fresh external state. Replaying every caller as a separate historical invocation therefore adds contention and handoff complexity without adding semantic work.

Coalescing preserves exactly the information that matters: **new current state may be available; converge again**.

Separating mutation authority from the trigger also restores the correct ownership boundary. The External Control Plane owns durable editing authority; `ruu` owns exact Git convergence under its current fenced executor and resource claims.

## Consequences

- Backlog **30.1** is closed: v1 is single-host.
- Backlog **30.11** is closed: there is no inter-converger retry/backoff/skip policy; simultaneous calls coalesce behind one authoritative executor.
- Backlog **30.13** was narrowed by this ADR and is subsequently closed by ADR-042.
- A burst of many explicit invocations may require only one additional global sweep.
- A trigger carries no worktree authority and no caller-local processing scope.
- Exact-invocation transferability states are retired.
- Old/stale executors cannot authorize adoption after a newer fenced generation is established.
- Internal parallelism remains possible despite one top-level executor.

## Amendments

This ADR amends ADR-003, ADR-005, ADR-007, ADR-009, ADR-022, ADR-024, ADR-028, ADR-031, ADR-033, ADR-034, ADR-036, ADR-039, and the normative External Control Plane contract where they describe simultaneous top-level convergers, invocation-scoped claims, exact-invocation transferability, invocation replay, or local coordination storage.

ADR-042 subsequently closes the concrete v1 CoordinationStore/run-ownership/journal questions intentionally left open here.


## Amendment by ADR-046

Promotion grouping follows the same trigger-independence rule as mutation authority. A `PromotionGroup` declaration is durable External-Control-Plane state established before/independently of convergence demand; it is not invocation-local payload. Coalescing or losing an explicit trigger therefore cannot lose or alter the grouping that the subsequent global sweep must resolve.

## Amendment by ADR-052

A DIRECT target operation claim fences one `AdvanceTargetFF(target, expected_old=B, new=C)` obligation. Top-level single-host execution ownership does not replace the exact-old CAS because humans/providers/other Git actors may still advance the authoritative target outside this coordination domain.



## Amendment by ADR-057

Development-validation workers/queues are external and do not participate in top-level executor fencing. `ruu` only consumes exact validation evidence or records external validation demands.

## Amendment by ADR-069

The statement that an explicit invocation is "a trigger, not a durable FIFO work item" remains correct for **convergence demand/executor scheduling** but is narrowed for work-bearing checkpoint calls. A work-bearing logical invocation also has a durable immutable `invocation_id`, sealed ContributionUnit cohort, and promotion binding. Its demand signal still coalesces; distinct logical invocation occurrences do not. Demand-only calls remain trigger-only.

