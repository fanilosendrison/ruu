# ADR-035: Use bounded contribution units with external lifecycle authority

- **Status:** Accepted — integration/readiness semantics amended by ADR-037; abandonment/removal semantics superseded by ADR-038; external boundary consolidated by ADR-039
- **Date:** 2026-09-05
- **Decision order:** 035

## Context

ADR-034 removed global producer identity and made the repository-local Git isolation object explicit. Further analysis showed that the object is not merely a reusable work context: it is a **bounded incarnation of contribution to one current convergence scope**.

Producer/runtime lifecycle is not contribution lifecycle. An agent may be running, stopped, between turns, waiting for user input, or finished with one inference while its ContributionUnit remains logically open.

## Decision

### 1. `contribution_unit` is the normative repository-local bounded contribution object

A ContributionUnit is:

> **a repository-local isolated Git unit that carries one bounded stream of contribution to its current convergence scope.**

It may contain greenfield/from-scratch creation, additions, modifications, deletions, refactors, generation, migrations, or any mixture of those operations.

Its durable identity cardinality is:

```text
1 contribution_unit_id
→ exactly 1 repository_id
→ exactly 1 convergence_unit_id membership for this identity
```

An isolated worktree/ref is provisioned externally while new filesystem work is being produced, but ADR-038 makes those editing artifacts non-identifying and potentially ephemeral.

### 2. Contribution-unit lifecycle is scoped to the current convergence scope

Normative lifecycle meanings after ADR-038:

```text
OPEN
= this contribution unit may still produce additional contribution
  to its current convergence scope.

CLOSED
= this contribution unit will produce no further contribution
  to its current convergence scope;
  any later work requires a new contribution_unit_id;
  its latest authoritative managed checkpoint, if any, remains subject
  to ordinary convergence until resolved.
```

`CLOSED` never transitions back to `OPEN`.

`ABANDONED` and `REMOVED` are not normative ContributionUnit lifecycle states after ADR-038. Unwanted code is changed/deleted through later development Git state; branch/worktree deletion/retention is outside this lifecycle.

### 3. Runtime/turn/artifact state never determines contribution-unit lifecycle

The following do **not** imply `CLOSED`:

```text
agent/process currently inactive
agent waiting for user
agent turn finished
conversation waiting for user
checkpoint committed
worktree clean
policy-required exact external development-validation prerequisite satisfied
current contribution already integrated
current contribution-unit tip equal to convergence-unit tip
local branch/ref absent
worktree absent
remote branch absent/present
```

Therefore:

```text
producer/runtime lifecycle
≠ contribution-unit lifecycle
≠ Git/convergence state
≠ editing-artifact lifecycle
```

### 4. Lifecycle authority belongs to the External Control Plane

`ruu` does not infer or originate `OPEN` or `CLOSED`.

The external ContributionUnit subsystem owns the authoritative lifecycle declaration. `ruu` consumes/revalidates it where needed but does not decide whether semantic work is finished.

### 5. Later work always uses a new contribution unit

Once a ContributionUnit is `CLOSED`, later work cannot reopen it.

```text
C1 CLOSED
+ later user/review change
→ create C2 OPEN
```

The new unit may participate in the same ConvergenceUnit if the convergence scope remains the same.

### 6. Lifecycle remains separate from eager upward integration

A ContributionUnit may be `OPEN` while one or more exact verified managed checkpoints are integrated upward, and it may continue producing later contribution afterward.

ADR-037/ADR-038 define:

```text
valid managed checkpoint
+ mechanically safe edge
→ earliest safe upward integration MUST be attempted
```

Commit or verification PASS still does not imply ContributionUnit closure.

### 7. Convergence-unit readiness requires sealed membership and exact contribution resolution

A ConvergenceUnit can become `READY_INTERNAL` only after membership is `SEALED`, every ContributionUnit is `CLOSED`, every still-required exact managed checkpoint is resolved, internal reconciliation/recovery is clear, the exact result has valid external development-validation evidence when current policy requires it, and the internal fixed point is reached. Physical ContributionUnit branch/ref/worktree presence or absence is not itself the readiness meaning.

## Rationale

`contribution_unit` describes the object more precisely than `work_context` while keeping agent/runtime scheduling and artifact lifecycle out of the Ruunce semantics.

## Consequences

- `work_context` is superseded as current normative terminology by `contribution_unit`.
- `contribution_unit_id` is the repository-local bounded contribution identity with stable convergence membership.
- `CLOSED → OPEN` is forbidden; later work creates a new ContributionUnit.
- Waiting for user input or ending an agent turn does not close a ContributionUnit.
- Branch/worktree deletion does not close or erase a ContributionUnit.
- The external ContributionUnit subsystem owns lifecycle declarations; `ruu` consumes them.
- Commit, eager upward integration, ContributionUnit closure, ConvergenceUnit membership sealing/readiness, and promotion readiness remain distinct.

## Alternatives considered

- **Keep `work_context`:** rejected because it suggests a reusable/durable workspace rather than a bounded contribution incarnation.
- **Infer closure from agent/turn inactivity:** rejected because temporary waiting/inactivity says nothing about whether more contribution may appear.
- **Reopen a closed unit for later changes:** rejected because it destroys the meaning of terminal lifecycle.
- **Use `ABANDONED` for unwanted work:** superseded/rejected by ADR-038; code intent is expressed through subsequent Git state.

## Supersession / terminology effect

This ADR supersedes ADR-034's current `work_context` terminology while preserving ADR-034's core removal of global producer identity and repository-local cardinality decision. ADR-038 supersedes this ADR's former `ABANDONED`/`REMOVED` lifecycle semantics and makes editing-artifact presence independent of logical ContributionUnit identity.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](EXTERNAL-CONTROL-PLANE-CONTRACT.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
