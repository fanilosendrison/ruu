# ADR-038: Decouple ContributionUnit identity from editing artifacts and remove abandonment semantics

- **Status:** Accepted — conflict/attribution follow-up resolved by ADR-040 — external boundary consolidated by ADR-039
- **Date:** 2026-09-05
- **Decision order:** 038
- **Subsequently amended by:** ADR-071 for deletion of a currently bound managed authoring ref; durable logical identity remains independent of the editing artifact

## Context

ADR-035 made `ContributionUnit` the bounded repository-local contribution identity, and ADR-037 made every valid managed checkpoint converge upward eagerly into its bound `ConvergenceUnit`.

Further review exposed two model errors:

1. `ABANDONED` tried to encode a semantic decision that does not belong to `ruu`. In normal agentic development, unwanted code is modified or deleted by the user/agent and later Git state expresses the new intent. Experimental/alternative work is already isolated at the `ConvergenceUnit` level.
2. The model still implicitly treated the local contribution branch/ref and worktree as if they were the durable identity/continuity of a ContributionUnit. Users and agents may legitimately create/delete those editing artifacts outside `ruu`; their absence alone is not an instruction to recreate, delete remote state, or mark a contribution semantically abandoned.

`ruu` exists to advance managed Git state that already exists and is authorized to progress. It does not own development-artifact lifecycle decisions.

## Decision

### 1. ContributionUnit lifecycle is only `OPEN | CLOSED`

Normative lifecycle:

```text
OPEN
= this contribution unit may still produce additional contribution
  to its current convergence scope.

CLOSED
= this contribution unit will produce no further contribution
  to its current convergence scope;
  any later work requires a new contribution_unit_id;
  its latest authoritative managed checkpoint, if any, remains subject
  to the ordinary convergence rules until resolved.
```

There is no normative ContributionUnit `ABANDONED` state in `ruu`.

There is also no ContributionUnit `REMOVED` lifecycle state in `ruu`. Physical branch/ref/worktree deletion or retention is development-artifact management outside this lifecycle.

`CLOSED` never returns to `OPEN`.

### 2. ContributionUnit identity is independent of branch/ref/worktree existence

A ContributionUnit is a durable logical orchestration identity with stable repository and convergence membership:

```text
contribution_unit_id
→ exactly one repository_id
→ exactly one convergence_unit_id
```

While work is actively provisioned it may have:

```text
local contribution ref/branch
isolated worktree
remote contribution ref
```

but those are physical editing/publication surfaces, not the identity itself.

Therefore:

```text
ContributionUnit identity
!= local branch/ref existence
!= worktree existence
!= remote branch existence
```

Deleting one of those artifacts manually or through an agent does not, by itself, mutate ContributionUnit lifecycle or create a Ruu obligation to recreate/delete anything else.

### 3. Durable convergence continuity is exact-state based

For convergence purposes, the durable contribution fact is the latest authoritative managed checkpoint OID known for the ContributionUnit, when one exists.

Conceptually:

```text
contribution_unit_id
+ repository_id
+ convergence_unit_id
+ lifecycle OPEN|CLOSED
+ latest_authoritative_managed_checkpoint_oid? 
```

The exact storage/schema remains an implementation detail, but correctness is OID/state based rather than branch/worktree-existence based.

A dirty/uncommitted filesystem state is actionable only while an editing surface exists and valid mutation authority can be acquired. It is not transformed into a durable managed checkpoint merely by being observed.

### 4. Missing editing artifacts are not automatically inconsistent

If a local contribution branch/ref or worktree is absent, `ruu` does not infer:

```text
CLOSED
remote deletion intent
local recreation intent
semantic abandonment
```

Instead it evaluates the actual managed obligation.

#### No unresolved exact contribution obligation

If the latest authoritative managed checkpoint is already fully resolved into the bound ConvergenceUnit, absence of the editing branch/worktree is irrelevant to convergence.

```text
editing artifacts absent
+ no unresolved exact managed contribution
→ no Ruu action required
```

#### Unresolved checkpoint remains retrievable

If an exact managed checkpoint still needs to converge and its OID is reachable/recoverable from any valid managed Git source, `ruu` may continue from that exact OID. It may use an isolated integration/verification workspace where required; the original producer worktree is not required for upward integration of an already-created checkpoint.

```text
editing artifacts absent
+ unresolved exact checkpoint OID reachable
→ continue ordinary convergence from exact OID
```

#### Required exact state is no longer recoverable

Only when a nonterminal managed obligation depends on an exact checkpoint OID that can no longer be recovered from any valid managed source does absence become a real integrity problem:

```text
unresolved managed obligation
+ required exact checkpoint OID known
+ exact state unrecoverable
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss condition
```

`ruu` does not guess a replacement state. The rest of the global sweep continues.

### 5. Editing-artifact lifecycle is outside `ruu`

Users/agents/External-Control-Plane tooling may create or delete contribution branches, worktrees, and remote refs through ordinary Git/tooling.

`ruu` does not own or infer those lifecycle decisions merely because a ContributionUnit becomes `CLOSED` or because an artifact disappears.

In particular:

```text
local branch absent
+ remote branch present
→ valid Git state; no automatic remote deletion

local branch absent
→ no automatic local recreation

ContributionUnit CLOSED
→ no automatic branch/worktree cleanup by Ruu
```

The provisioning subsystem remains responsible for establishing editing surfaces before new managed writes, as defined by ADR-023.

### 6. Eager convergence no longer has an abandonment exclusion

ADR-037's upward-integration predicate becomes:

```text
valid authoritative managed checkpoint S
+ exact topology/membership known
+ required claims/authority for the operation held
+ no unresolved conflict
+ ancestry/synchronization preconditions satisfied
→ MUST attempt earliest mechanically safe ContributionUnit → ConvergenceUnit integration
```

Both `OPEN` and `CLOSED` ContributionUnits may have an unresolved authoritative checkpoint that still needs to converge.

### 7. `READY_INTERNAL` depends on resolved exact contribution obligations, not artifact cleanup/disposition

A sealed ConvergenceUnit may become `READY_INTERNAL(OID)` only when:

```text
membership == SEALED
zero OPEN ContributionUnits
for every CLOSED ContributionUnit:
  its latest authoritative managed checkpoint, if any, is fully resolved
  into the exact ConvergenceUnit result
zero unknown/orphan membership/state that can hide managed contribution
zero BLOCKED_MISSING_MANAGED_STATE / unresolved internal sync/integration/
  reconciliation/conflict/recovery obligation
valid exact development-validation evidence for the OID when required by current policy
internal fixed point reached
```

Physical contribution branch/ref/worktree presence or absence is not itself a readiness condition.

## Rationale

This keeps `ruu` focused on its actual purpose:

```text
existing managed Git state
→ verify/checkpoint when a mutable editing surface is available
→ synchronize/reconcile
→ eagerly integrate exact managed checkpoints
→ promote/publish/provider-progress
→ global fixed point
```

Semantic changes are represented by subsequent code/Git state, not by an orchestration-level "abandon this contribution" flag. Editing-artifact deletion is an ordinary user/agent/tooling action, not a convergence decision.

OID-based continuity also avoids false inconsistencies when a worktree or branch is intentionally removed after its useful Git state has already been checkpointed or converged.

## Consequences

- `ABANDONED` is removed from the normative ContributionUnit model.
- `REMOVED` is removed from the normative ContributionUnit lifecycle.
- ContributionUnit lifecycle is `OPEN | CLOSED` only.
- Later work after `CLOSED` uses a new ContributionUnit.
- `ruu` does not delete/recreate local/remote contribution branches or worktrees merely to mirror artifact presence.
- Branch/worktree absence does not block convergence when the required exact managed checkpoint is already resolved or remains recoverable.
- Exact managed-state loss is a localized recovery/data-loss condition only when a still-required OID becomes unrecoverable.
- Backlog item 30.9 (abandonment residue/disposition) is retired as a false problem in the `ruu` model.
- At the time of this ADR, conflict resolution policy (30.10) and tool/generated mutation attribution (30.12) remained open. ADR-040 subsequently closes both without changing this ADR's artifact/exact-state decision.

## Alternatives considered

- **Keep `ABANDONED` to mean unwanted code:** rejected because unwanted code is corrected/deleted through subsequent development state; `ruu` should not model product intent.
- **Use `ABANDONED` for failed/crashed sessions:** rejected because runtime failure is recovery/lifecycle state outside semantic contribution intent.
- **Treat local branch absence as remote-deletion intent:** rejected because local-only deletion is valid Git behavior and absence is not an intent signal.
- **Automatically recreate missing local branches:** rejected because artifact lifecycle is not owned by `ruu` and recreation may contradict user intent.
- **Treat every missing worktree/ref as `UNKNOWN_INCONSISTENT`:** rejected because a ContributionUnit may remain logically meaningful through exact durable checkpoint state after editing surfaces disappear.

## Amendment effect

This ADR amends ADR-002, ADR-005, ADR-008, ADR-009, ADR-012, ADR-013, ADR-023, ADR-034, ADR-035, and ADR-037 wherever they make ContributionUnit identity/readiness depend on branch/worktree cleanup, include `ABANDONED`/`REMOVED` as ContributionUnit lifecycle semantics, or classify mere editing-artifact absence as an orchestration inconsistency.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-068 — ordinary artifact deletion remains neutral even when higher-level ship cancellation exists

ADR-068 introduces explicit `PromotionGroup CANCELLED` settlement for withdrawal of a still-unrealized declared ship. That does **not** change this ADR's artifact boundary. A user/agent deleting an ordinary authoring branch/ref/worktree remains ordinary Git artifact management and does not itself create ContributionUnit closure, ConvergenceUnit `ABANDONING`, PromotionGroup `CANCELLED`, or any other semantic lifecycle transition. Higher-level cancellation/disposal requires its own explicit authority and exact guards.
