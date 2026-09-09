# Ruu — State-Space / Global Consistency Audit v12

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-042
- **Trigger:** ADR-042 closes backlog 30.13 with a reconciler-driven SQLite CoordinationStore, process-lifetime OS run ownership, durable generation/token fencing, append-only recoverable-effect journaling, explicit transaction boundaries, stable repository relocation binding, and recovery-resource GC rules.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete current architecture after the remaining v1 coordination-runtime questions were fixed.

The current top-level model is:

```text
many explicit callers
→ durable coalesced convergence demand
→ one OS-owned + SQLite-fenced top-level convergence run
→ current-state global reconciliation
→ recoverable external effects through immutable journal records
→ exact CAS adoption
→ fixed point / race-safe ACTIVE→IDLE release
```

The audit specifically checks that ADR-042 does not:

- turn `ruu` into a persisted workflow-step engine;
- allow physical OS ownership to substitute for durable adoption fencing;
- strand accepted demand in the short `IDLE`-before-unlock release window;
- allow a stale run/attempt to append current authority or adopt state;
- treat an Attempt record as proof that an external effect happened;
- hold SQLite transactions across Git/provider/network/test/long-filesystem work;
- require automatic heartbeat/TTL takeover of a live-but-hung local process;
- collect correctness-critical recovery state before independent reachability/recovery sufficiency exists;
- infer repository identity from a path/remote/inode;
- silently repair/initialize an incompatible established CoordinationStore;
- weaken any prior ContributionUnit, ConvergenceUnit, promotion, verification, review, reconciliation, or global-sweep invariant.

This remains a factorized finite-state audit rather than enumeration of the unbounded Git DAG/provider state space.

## 2. OS physical ownership versus SQLite durable fencing

`os_lock_sqlite_fence_separation` varies:

```text
physical ownership: CURRENT_OWNS | OTHER_OWNS | FREE
durable run state:  ACTIVE | IDLE
run token:          CURRENT | STALE | NONE
exact managed state: MATCH | MISMATCH
```

Result: **36 combinations**.

Authoritative adoption requires all of:

```text
current process owns the OS run lock
+ durable run_state = ACTIVE
+ current run_generation/run_token
+ exact expected managed state
```

Neither the OS lock alone nor a still-present old token is sufficient.

## 3. `ACTIVE → IDLE` release / concurrent-demand handshake

`active_idle_release_handshake` varies demand timing, physical lock state, and durable run state.

Result: **12 combinations**.

Validated:

```text
OS BUSY + ACTIVE
→ caller that already recorded demand may return

OS BUSY + IDLE
→ caller MUST retry ownership acquisition
→ old run is already fenced and cannot service the new demand

OS FREE
→ a caller can establish a successor generation
```

This explicitly covers the release-window lost-wakeup race that remained abstract in v11.

## 4. Operation / Attempt / Observation / Adoption

`operation_attempt_observation_adoption` varies operation-identity reuse, attempt fence freshness, observation freshness, and CAS affected-row count.

Result: **24 combinations**.

Validated:

```text
same operation_id + changed intent fingerprint
→ invalid

stale attempt fence
→ cannot append current authoritative observation/adoption

non-current/unbound observation
→ cannot authorize adoption

CAS affected rows != 1
→ no Adoption
```

Only an unchanged logical Operation, current fenced execution, exact current Observation, and exactly-one-row managed CAS can produce Adoption.

## 5. External-effect crash windows

`external_effect_crash_recovery` covers crashes:

```text
before effect
after effect but before Observation
after Observation but before Adoption
after Adoption
```

against actual external state:

```text
EXPECTED_OLD
DESIRED
OTHER
```

Result: **12 combinations**.

Any unresolved pre-Adoption crash requires exact observation before deciding what happened. Attempt metadata never distinguishes "effect happened" from "no effect" or third-party drift. `OTHER` never authorizes blind replay.

## 6. No external work inside SQLite transactions

`no_external_work_inside_sqlite_transaction` varies transaction state and work class.

Result: **12 combinations**.

While a CoordinationStore transaction is open, only store-local work is valid. Git, provider/network calls, tests, and long filesystem operations require the transaction to be closed.

This is the executable form of the ADR-042 `TX-A → external effect → Observation → TX-B` boundary.

## 7. Live-but-hung process behavior

`live_hung_process_liveness` varies process state, OS lock state, and the candidate policy of automatic takeover.

Result: **12 combinations**.

The physically consistent v1 states are:

```text
RUNNING → OS lock HELD
HUNG    → OS lock HELD
DEAD    → OS lock FREE
```

A live-but-hung process is not automatically superseded by heartbeat/TTL. Normal liveness is hardened through bounded subprocess/network operations and by representing provider/CI/review waits as ordinary nonterminal waiting obligations.

## 8. Recovery-resource GC eligibility

`recovery_resource_gc_eligibility` varies:

```text
lifecycle: REQUIRED | GC_ELIGIBLE
alternate durable reachability: PROVEN | NOT_PROVEN
unresolved recovery dependency: YES | NO
cleanup namespace: SAME_ATTEMPT | DIFFERENT_ATTEMPT
```

Result: **16 combinations**.

Physical cleanup is permitted only after `GC_ELIGIBLE`, independent durable reachability is proven, no unresolved recovery dependency remains, and cleanup targets the resource's own non-reused attempt namespace.

Cleanup failure after eligibility is harmless garbage, not a correctness failure.

## 9. Stable repository identity across relocation

`repository_identity_relocation` varies opaque repository identity, old/new locator, and binding quality.

Result: **12 combinations**.

A locator change never creates repository identity by itself. Only an exact authoritative binding is usable; ambiguous/missing bindings fail closed. `repository_id` remains stable across an explicitly declared relocation.

## 10. Schema initialization / migration fail-closed behavior

`schema_initialization_migration` varies empty/non-empty store and:

```text
MISSING
SUPPORTED
OLDER_KNOWN
NEWER_UNKNOWN
CORRUPT
```

Result: **10 combinations**.

Validated:

```text
empty + missing schema
→ initialization allowed

known older schema
→ explicit ordered migration allowed

non-empty + missing authority
newer unknown schema
corrupt schema
→ fail closed
```

No established store is silently recreated from missing authority.

## 11. Current-state reconciler rather than workflow resume

`current_state_reconciler` varies prior in-process position and current obligation state.

Result: **16 combinations**.

The selected action depends only on the current obligation classification:

```text
PROGRESSABLE → progress
WAITING      → current fixed-point wait
BLOCKED      → localized block
TERMINAL     → no action
```

Previous process phase/position is deliberately absent from the predicate.

## 12. Revalidated ADR-041 concurrency families

The v12 executable audit also reruns the v11 families for:

- convergence-demand coalescing;
- single-generation fencing;
- trigger/External-Control-Plane authority independence;
- release/demand serialization;
- CoordinationStore fail-closed CAS/schema behavior;
- recovery namespace non-aliasing.

The ADR-042 handshake refines rather than replaces those invariants.

## 13. Revalidated prior architecture families

The executable audit reruns all prior current families, including:

- ContributionUnit identity/cardinality/lifecycle and artifact independence;
- managed checkpoint CAS and exact-state continuity;
- External Control Plane responsibility boundary;
- exact `RECONCILIATION_REQUIRED` semantics;
- mutation-boundary candidate attribution;
- ConvergenceUnit grouping, eager integration, sealing/readiness;
- global managed-obligation coverage and external wait refresh;
- state-producing full verification, evidence reuse/fixed point/capacity;
- review request/revision invalidation;
- internal integration verification.

Total finite combinations evaluated: **12,270**.

## 14. Static architecture consistency checks

The static audit verifies at least:

1. ADR numbering is contiguous from **001 through 042**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.13 resolved by ADR-042**.
4. `OPEN-DESIGN-BACKLOG.md` no longer lists item 13 as open and explicitly records ADR-042 closure.
5. Main §7.11 contains the concrete CoordinationStore/run/journal model.
6. Main invariants include ADR-042 invariants **115–124**.
7. ADR-042 contains the process-lifetime OS ownership, `run_generation + run_token`, `ACTIVE → IDLE` handshake, append-only effect-journal path, no-external-work transaction boundary, live-hung policy, and `GC_ELIGIBLE` recovery-resource lifecycle.
8. ADR-041 now points its intentionally open implementation details to ADR-042 closure.
9. The External Control Plane contract distinguishes stable `repository_id` from the relocatable current host-local locator.
10. Existing ADR-036/040/041 global-sweep, reconciliation, trigger-coalescing, and fencing guarantees remain intact.

## 15. Result

The executable v12 audit reports **PASS** with **12,270 finite combinations**.

The final static audit cross-checks **57 Markdown artifacts**.

## 16. Interpretation

The current architecture can now be summarized as:

```text
many callers
→ monotonic coalesced convergence demand

OS process-lifetime lock
→ physical single-host top-level run ownership

SQLite ACTIVE + run_generation + run_token
→ durable progression authority

ConvergenceEngine
→ current-state global reconciliation
→ no persisted workflow-step resume

Operation
→ Attempt(s)
→ exact Observation
→ CAS Adoption

Git/provider/non-atomic effects
→ never assumed from metadata
→ exactly re-observed after crash

recovery resource REQUIRED
→ independent durable safety proven
→ GC_ELIGIBLE
→ best-effort cleanup
```

Backlog 30.13 is closed without adding a distributed lease service or workflow runtime to v1.
