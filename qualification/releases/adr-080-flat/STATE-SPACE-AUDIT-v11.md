# Ruu — State-Space / Global Consistency Audit v11

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-041
- **Trigger:** ADR-041 replaces competing top-level convergers with coalesced convergence demand under one single-host fenced executor and retires exact-trigger ContributionUnit transferability.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete current architecture after the concurrency/authority model changed from:

```text
multiple simultaneous top-level Ruu invocations
+ exact-invocation worktree transferability
+ inter-converger claim contention
```

to:

```text
many explicit callers
→ durable coalescible convergence demand
→ at most one authoritative top-level executor
→ global fixed-point sweep over current state

ContributionUnit mutation authority
→ durable External Control Plane state
→ independent of trigger identity
```

The audit specifically checks that ADR-041 does not:

- lose convergence demand when many callers invoke concurrently;
- require FIFO replay of semantically identical global triggers;
- allow two top-level executor generations to adopt state simultaneously;
- use heartbeat/liveness as mutation authority;
- let a convergence trigger manufacture ContributionUnit authority;
- weaken exact worktree/resource claims or Git expected-old/CAS rules;
- strand work in the race between "caught up" and executor release;
- let old-executor cleanup destroy a newer executor generation's temporary state;
- weaken ADR-036 global-obligation coverage, ADR-040 reconciliation semantics, or the full-verification model.

This remains a factorized finite-state audit rather than enumeration of the unbounded Git DAG/provider state space.

## 2. New finite family: convergence-demand coalescing

`convergence_demand_coalescing` varies:

```text
executor:
  NONE
  CURRENT

outstanding demand:
  CAUGHT_UP
  ONE_NEW
  MANY_NEW

observation point:
  BEFORE_SWEEP
  AFTER_FIXED_POINT
```

Result: **12 combinations**.

Validated:

```text
MANY_NEW
→ may be covered by one later global sweep
→ does not imply one historical replay per trigger

no executor + outstanding demand
→ an executor must be establishable

current executor + newer demand after fixed point
→ executor must continue/re-sweep before quiescence
```

## 3. New finite family: single-executor fencing

`single_executor_fencing` varies current executor generation, acting generation, liveness observation, and exact expected-state match.

Result: **24 combinations**.

Authoritative adoption is permitted only when:

```text
actor generation == current executor generation
AND exact expected state matches
```

The liveness dimension is deliberately absent from the authorization predicate. A stale heartbeat may justify takeover policy, but it never grants authority by itself.

## 4. New finite family: trigger/authority independence

`trigger_authority_independence` varies:

```text
trigger:
  CALLER_A
  CALLER_B
  COALESCED
  NONE

mutation access:
  PROTECTED_EXTERNAL
  TRANSFERABLE_RUU
  TRANSFERABLE_GENERAL
  UNKNOWN

claim:
  NONE
  CURRENT_EXECUTOR_OPERATION
  INCOMPATIBLE_OTHER

topology:
  KNOWN
  UNKNOWN
```

Result: **96 combinations**.

Validated: changing the caller/trigger never changes mutation eligibility. Only durable External Control Plane authority, exact topology, and the current executor/operation claim participate in the predicate.

## 5. New finite family: executor-release / concurrent-demand race

`executor_release_demand_race` models the two serialized transaction orders:

```text
new demand commits before executor release transaction
OR
executor release commits before new demand transaction
```

Result: **4 combinations**.

Required outcome:

```text
demand first
→ current executor must observe/fail caught-up predicate and continue

release first
→ later demand must be able to establish a new executor
```

The forbidden state is a committed new demand that is invisible to a later release decision and leaves no executor able to service it.

## 6. New finite family: CoordinationStore fail-closed semantics

`coordination_store_fail_closed` varies schema compatibility, CAS affected-row count, and executor fence freshness.

Result: **24 combinations**.

Only:

```text
supported schema
+ exactly one expected-state row changed
+ current executor fence
```

may count as authoritative adoption.

Unsupported/newer/corrupt schema, zero/multiple affected rows, or stale executor fence fail closed.

## 7. New finite family: recovery namespace non-aliasing

`recovery_namespace_nonaliasing` varies cleanup generation, namespace generation, and current executor generation.

Result: **8 combinations**.

Validated: cleanup may target only the physical namespace belonging to its own generation. A stale executor generation cannot destructively alias a current generation's mutable workspace/anchor namespace.

## 8. Revalidated current authority families

The three authority-related families were deliberately reduced because ADR-041 removed two obsolete exact-invocation states:

```text
TRANSFERABLE_TO_THIS_INVOCATION
TRANSFERABLE_TO_OTHER_INVOCATION
```

Current modeled mutation access is:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

Current worktree claim identity is executor/operation-scoped rather than trigger-scoped.

Counts now include:

- `actor_correlation_irrelevance`: **96**
- `contribution_unit_worktree_mutation_authority`: **192**
- `contribution_unit_commit_verification_crosscheck`: **1,080**

The lower total versus v10 is therefore an actual state-space reduction, not omitted coverage.

## 9. Revalidated prior families

The executable v11 audit reruns all prior current families, including:

- ContributionUnit identity/cardinality/lifecycle and artifact independence;
- checkpoint-record CAS;
- External Control Plane responsibility boundary;
- exact `RECONCILIATION_REQUIRED` contract;
- candidate attribution by mutation boundary;
- external ConvergenceUnit grouping;
- eager ContributionUnit integration;
- sealed ConvergenceUnit readiness;
- experimental isolation;
- global managed-obligation coverage;
- external wait recheck;
- state-producing full-verification requirements;
- evidence reuse/fixed point/capacity;
- review request/revision invalidation;
- internal integration evidence.

Total finite combinations evaluated: **12,108**.

## 10. Static architecture consistency checks

The static audit verifies:

1. ADR numbering is contiguous from **001 through 041**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.1** and **30.11** resolved by ADR-041.
4. Main §30.13 records the fixed transactional/single-host semantic core while keeping exact implementation details open.
5. `OPEN-DESIGN-BACKLOG.md` no longer lists 30.1 or 30.11 as open and narrows 30.13.
6. The current main spec, External Control Plane contract, ADR-003, ADR-009, and ADR-033 contain no current exact-invocation transferability state.
7. `TRANSFERABLE_TO_RUU` is present in the current main spec and External Control Plane contract.
8. Main invariants include single-host coordination, coalesced demand, one fenced executor, race-safe release/catch-up, trigger-independent authority, and non-aliasing recovery namespaces.
9. ADR-041 requires durable transactional convergence demand and fenced executor ownership, with SQLite only a preferred/reference v1 backend rather than ontology.
10. ADR-036 global fixed-point semantics remain intact at the **executed sweep** level.
11. ADR-040 reconciliation and candidate-attribution guarantees remain intact.

## 11. Result

The executable audit reports **PASS** with **12,108 finite combinations**. After inclusion of this report, the package contains **55 Markdown artifacts** subject to static cross-checking.

## 12. Interpretation

The current architecture can now be summarized as:

```text
many callers
→ explicit convergence demand
→ demand generations coalesce

one fenced top-level executor
→ global current-state fixed-point sweep
→ internal safe parallelism remains allowed

trigger identity
→ no mutation authority

External Control Plane mutation state
+ exact current executor/operation claim
→ ContributionUnit mutation boundary

newer executor generation
→ fences older generations

Git/provider effects
→ remain exact-state/CAS/recovery governed
```

This closes the top-level concurrency ambiguity without introducing a global Git mutex or replay queue.
