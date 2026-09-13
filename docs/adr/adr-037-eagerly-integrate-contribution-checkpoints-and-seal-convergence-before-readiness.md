---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Eagerly integrate contribution checkpoints and seal convergence membership before internal readiness"
id: "ADR-037"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "c7660041ca9626e377bfd8b56fbc36934c0a0bec8e2e5276f5fa342d667f70f1"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-037: Eagerly integrate contribution checkpoints and seal convergence membership before internal readiness

- **Status:** Accepted — artifact/lifecycle semantics amended by ADR-038
- **Date:** 2026-09-05
- **Decision order:** 037

## Context

ADR-035 made each `ContributionUnit` a bounded repository-local stream of contribution to exactly one `ConvergenceUnit`. The remaining open questions were:

1. who creates/chooses a `ConvergenceUnit` and assigns a new `ContributionUnit` to it;
2. whether a verified ContributionUnit checkpoint needs a second "integration readiness/release" signal before moving upward;
3. what exactly makes a `ConvergenceUnit` `READY_INTERNAL`.

The desired behavior is continuous convergence: invoking `ruu` is an opportunity to advance all managed Git state that can safely progress. A verified checkpoint should not wait merely because more contributions may be planned later. Conversely, the fact that all currently known contributions are resolved is insufficient to claim that the convergence scope itself is complete if the External Control Plane still expects to add another ContributionUnit.

Experimental or alternative work is a distinct convergence target, not a special kind of checkpoint that should be committed while being artificially withheld from its own ConvergenceUnit.

## Decision

### 1. Convergence-unit creation and ContributionUnit membership are externally authoritative

The External Control Plane owns:

```text
create/reuse convergence_unit_id
assign a newly created contribution_unit_id to exactly one convergence_unit_id
open/seal contribution membership for that convergence unit
```

`ruu` never infers this semantic grouping from:

```text
caller/session/task/ticket
branch/display name
changed file overlap
repository path/CWD
agent/model/process identity
```

A ContributionUnit's `convergence_unit_id` membership remains stable for that ContributionUnit identity. If the higher-level scope changes, a new ContributionUnit is created.

The concrete External Control Plane API/policy for deciding whether to create versus reuse a ConvergenceUnit is outside `ruu`.

### 2. No separate ContributionUnit integration-release/readiness state exists

Once an exact ContributionUnit state has become an authoritative managed checkpoint with valid development-validation evidence, that checkpoint is eligible for upward convergence immediately unless another existing mechanical precondition blocks the edge.

Normative rule:

```text
valid authoritative managed checkpoint S
+ exact topology known
+ required claims/authority held
+ no unresolved conflict
+ ancestry/synchronization preconditions satisfied
→ MUST attempt earliest mechanically safe ContributionUnit → ConvergenceUnit integration
```

There is no additional state such as:

```text
READY_FOR_INTEGRATION
RELEASED_EXACT
COMMITTED_BUT_NOT_RELEASED
```

A ContributionUnit may remain `OPEN` after one or more checkpoints have been integrated and may later produce additional contribution to the same convergence scope.

### 3. Experimental/alternative isolation is modeled by a distinct ConvergenceUnit

If work must remain isolated from the primary convergence result because it is an experiment, competing approach, or alternative candidate, the External Control Plane assigns that work to a different `ConvergenceUnit`.

Within that alternative ConvergenceUnit, verified checkpoints still converge eagerly in the normal way.

`ruu` does not implement experimentation by suppressing upward integration of otherwise valid checkpoints within a ContributionUnit.

### 4. ConvergenceUnit contribution membership has an externally authoritative `OPEN | SEALED` state

A ConvergenceUnit has a contribution-membership state distinct from exact Git readiness:

```text
OPEN
= additional ContributionUnits may still be attached to this convergence scope.

SEALED
= no additional ContributionUnit is currently expected/authorized to attach
  before this convergence result may be finalized internally.
```

The External Control Plane owns this membership declaration. `ruu` consumes and revalidates it; it does not infer sealing from the currently visible set of ContributionUnits.

`OPEN` does **not** block:

```text
checkpoint commit
policy-required exact external development validation
ContributionUnit → ConvergenceUnit integration
synchronization/reconciliation
continued contribution production
```

`OPEN` blocks only internal finalization/readiness of the ConvergenceUnit.

If later semantic/review work requires new contribution after a previously ready/bound result, the External Control Plane must explicitly reactivate the convergence scope and make membership `OPEN` before creating the new ContributionUnit. That transition invalidates exact readiness/source bindings as already required by ADR-010/011/021/027/032. The exact External Control Plane mapping from provider feedback to affected ConvergenceUnit scope remains outside `ruu`.

### 5. `READY_INTERNAL(OID)` is a mechanical exact-state assertion

A ConvergenceUnit may enter `READY_INTERNAL(OID)` only when all of the following hold together under the existing race-safe readiness barrier:

```text
contribution membership == SEALED

no ContributionUnit in that convergence scope is OPEN

for every CLOSED ContributionUnit:
  its latest authoritative managed checkpoint, if any,
  is fully resolved into the exact ConvergenceUnit result

zero unknown/orphan ContributionUnit membership/state

zero BLOCKED_MISSING_MANAGED_STATE or unresolved internal synchronization/integration/reconciliation/conflict/recovery obligation

exact ConvergenceUnit result OID has valid development-validation evidence

re-evaluation reaches the internal fixed point:
  no currently authorized internal state-producing transition can further change that exact result
```

`READY_INTERNAL` does not require a second repository-specific semantic-readiness token beyond these conditions.

Repository-specific code-state correctness/testing policy belongs to the external Development System / repository governance. `ruu` consumes exact development-validation evidence when current policy requires it; human/product/governance/PR-author/review/provider requirements remain external/later publication concerns.

Therefore:

```text
READY_INTERNAL
!= product/task semantic completion assertion by Ruu
!= ship-ready
!= review approved
!= provider CI complete
!= mergeable
```

It means only that the exact sealed internal convergence result is mechanically complete and internally resolved for the current convergence scope.

### 6. Physical ContributionUnit artifact presence is not itself the readiness meaning

`READY_INTERNAL` is blocked by **unresolved contribution obligations**, not by historical ref existence as such.

A CLOSED ContributionUnit whose exact managed contribution obligations are fully resolved does not block readiness merely because a historical branch/ref/worktree exists or is absent. Editing-artifact cleanup/retention is outside the readiness meaning under ADR-038.

This amends the earlier shorthand "zero contribution-unit refs" to "zero unresolved contribution-unit obligations".

## Rationale

The model becomes monotonic at the right boundaries:

```text
ContributionUnit checkpoint
→ verify
→ commit
→ converge upward as early as mechanically safe

future planned ContributionUnit
→ does not delay current progress

ConvergenceUnit membership OPEN
→ progress continues, final readiness forbidden

ConvergenceUnit membership SEALED
+ all ContributionUnits CLOSED and all exact contribution obligations resolved
+ exact result verified
+ internal fixed point
→ READY_INTERNAL
```

This preserves continuous Git convergence without letting the engine infer semantic scope completeness from the accidental absence of currently registered work.

## Consequences

- Main backlog items 30.5, 30.6, and 30.7 are closed at the `ruu` semantic layer.
- The External Control Plane chooses/creates ConvergenceUnits and binds ContributionUnits to them.
- No ContributionUnit integration-readiness/release evidence class remains.
- Every valid managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit is advanced toward its bound ConvergenceUnit as early as mechanically safe.
- Experimental/alternative approaches use distinct ConvergenceUnits.
- ConvergenceUnit contribution membership is explicitly `OPEN` or `SEALED` and externally authoritative.
- `OPEN` membership blocks `READY_INTERNAL`, not ordinary convergence progress.
- `READY_INTERNAL` is exact-state-bound and mechanical; later semantic/review work invalidates/reopens convergence scope through the External Control Plane rather than reopening terminal ContributionUnits.
- Physical ContributionUnit branch/ref/worktree existence or deletion is not synonymous with internal readiness.

## Alternatives considered

- **Separate per-checkpoint integration-release flag:** rejected as redundant and contrary to continuous convergence.
- **Infer integration readiness from ContributionUnit closure:** rejected because `OPEN` units legitimately deliver multiple useful checkpoints before terminal closure.
- **Represent experimentation as a checkpoint that must not integrate:** rejected because isolation belongs at the ConvergenceUnit boundary.
- **Infer convergence completeness from currently known ContributionUnits:** rejected because additional ContributionUnits may still be planned.
- **Require zero physical ContributionUnit refs before READY_INTERNAL:** rejected as conflating logical resolution with cleanup/retention.
- **Put PR/review/governance checks inside READY_INTERNAL:** rejected because those belong to later promotion/provider layers.

## Amendment effect

This ADR amends ADR-006, ADR-008, ADR-010, ADR-011, ADR-019, ADR-021, ADR-027, ADR-030, and ADR-035 wherever they refer to a separate ContributionUnit integration-readiness signal, imply that ContributionUnit ref deletion itself defines readiness, or leave ConvergenceUnit membership completeness/readiness policy open.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-040

An unresolved `RECONCILIATION_REQUIRED` obligation is an unresolved internal reconciliation/conflict obligation and therefore blocks `READY_INTERNAL` for the affected ConvergenceUnit. A resolver report cannot clear readiness; only current Git-state progression plus required current-state revalidation plus any exact external development-validation evidence required by policy can do so.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-069

Reopening a ConvergenceUnit invalidates its **live current** readiness, but does not invalidate exact states already adopted into older PromotionGroups' group-local resolutions. Ordinary later work creates a new group occurrence at the next work-bearing invocation. Same-group correction/reconciliation requires explicit group-bound authority.

