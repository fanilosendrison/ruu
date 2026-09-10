# ADR-069 — Bind PromotionGroups to work-bearing Ruu invocations and group-local exact state

**Status:** Accepted — 2026-09-07  
**Closes:** backlog 30.42, 30.43  
**Amends:** ADR-010, ADR-011, ADR-015, ADR-023, ADR-037, ADR-039, ADR-041, ADR-046, ADR-047, ADR-050, ADR-053, ADR-054, ADR-064, ADR-067

## Context

ADR-046 made a `PromotionGroup` a durable closed set of ConvergenceUnit identities and content-addressed the group solely by that member set. It also resolved a group from each member ConvergenceUnit's unqualified **current** `READY_INTERNAL` state.

Two ordinary properties of the development workflow falsify both choices.

First, one development session may invoke `ruu` repeatedly. Every work-bearing invocation closes the current implementation cohort, and the same ConvergenceUnits may legitimately appear again in a later invocation:

```text
Session S

work cohort 1:
  CU-A1 -> X
  CU-B1 -> Y
invoke ruu I1
-> G1 = {X,Y}

session continues

work cohort 2:
  CU-A2 -> same X
  CU-B2 -> same Y
invoke ruu I2
-> G2 = {X,Y}
```

`G1` and `G2` are distinct promotion obligations even though their ConvergenceUnit member sets are identical. Content-addressing `PromotionGroup` only by `{X,Y}` collapses those occurrences and makes a later legitimate group impossible after an earlier identical group has terminalized, including `CANCELLED`.

Second, multiple PromotionGroups may legitimately reference the same live ConvergenceUnit lineage. If `G1` adopts `X@A` and later ordinary work produces `G2` from `X@B`, movement of the live ConvergenceUnit must not silently revise `G1`. Conversely, a review correction explicitly bound to `G1` must be able to revise `G1` from its exact prior state without absorbing unrelated later work already present in `X@B`.

The architecture already has the correct exact-state descendant mechanism in ADR-050: a child promotion's immutable owned effect can be reprojected/restacked onto a changed predecessor without rewriting the child's internal owned state. What is missing is a durable work-bearing invocation boundary and group-local exact-state binding above that mechanism.

## Decision

### 1. Distinguish a work-bearing logical invocation from convergence demand and executor run

A **work-bearing logical invocation** is the durable checkpoint boundary at which a Development System hands one closed cohort of ContributionUnits to `ruu`.

It is distinct from both:

```text
LogicalInvocation
!= ConvergenceDemand
!= ReconcilerRun
```

`ConvergenceDemand` remains the coalescible monotonic wake-up relation of ADR-041. `ReconcilerRun` remains a global, recoverable, fenced execution attempt. A single global run may process state introduced by several logical invocations plus unrelated older obligations.

Demand-only triggers remain valid and need not create a LogicalInvocation. A work-bearing invocation creates durable logical state **and** raises convergence demand.

### 2. A work-bearing invocation has a durable idempotent identity and sealed ContributionUnit cohort

The Development System supplies an opaque `invocation_id` that identifies one logical work-bearing invocation occurrence within the coordination domain.

Required semantics:

```text
same invocation_id + same immutable invocation definition
-> idempotent replay

same invocation_id + different cohort or binding
-> integrity failure / fail closed

different invocation_id
-> distinct logical invocation occurrence
```

The caller must preserve/reuse the same `invocation_id` across retry of the same logical invocation. The exact generation mechanism is external to `ruu`; UUID, durable sequence, workflow-event identity, or equivalent are all acceptable when they provide the required crash/retry semantics.

A v1 work-bearing invocation records a non-empty closed immutable cohort of ContributionUnit handoffs:

```text
LogicalInvocation {
  invocation_id
  handoffs: Set<ContributionUnitHandoffRef>
  promotion_binding:
      NEW_GROUP
    | REVISE_EXISTING_GROUP(promotion_group_id, authority_ref)
}
```

The invocation is accepted/sealed only after every listed ContributionUnit handoff is durably frozen/bound to that invocation under ADR-064 mutation-authority rules. Before seal, partial preparation is not an accepted checkpoint cohort and may be safely resumed or aborted. The seal is the logical linearization point for cohort acceptance; physical Git checkpoint/integration work may then proceed incrementally and recoverably.

### 3. Ordinary `NEW_GROUP` invocation mechanically creates one PromotionGroup

For a sealed invocation `I`:

```text
ConvergenceMembers(I) =
  distinct(convergence_unit_of(CU) for CU in I.handoffs)
```

For `promotion_binding = NEW_GROUP`, `ruu` creates exactly one PromotionGroup whose closed ConvergenceUnit membership is this mechanically derived set. The External Control Plane does not separately decide or declare which ConvergenceUnits from the invocation "go together".

A PromotionGroup is therefore an occurrence-bound durable promotion obligation:

```text
PromotionGroup {
  promotion_group_id
  origin_invocation_id
  members: Set<CanonicalConvergenceUnitRef>
  membership_fingerprint
  group-local current exact resolution
  lifecycle / settlement state
}
```

V1 derives an internal stable identity from the invocation occurrence, for example:

```text
promotion_group_id =
  SHA-256(
    domain = "Ruu/promotion-group/v2"
    || coordination_domain
    || invocation_id
  )
```

and independently derives:

```text
membership_fingerprint =
  SHA-256(canonical(sorted(members)))
```

The member set remains non-empty, unordered, unique, closed, and immutable.

Therefore:

```text
I1 != I2
members(G1) == members(G2)
-> G1 != G2
```

A later legitimate work-bearing invocation never has to manufacture ConvergenceUnit churn merely to escape an old terminal PromotionGroup identity.

### 4. Review/reconciliation continuation revises an existing group only under explicit group-bound authority

A logical invocation with:

```text
REVISE_EXISTING_GROUP(G, authority_ref)
```

does not create a new PromotionGroup. It may revise only `G`, and only when `authority_ref` is a current durable external obligation that explicitly authorizes semantic continuation of that group, such as an ADR-053 `ReviewCorrectionDemand` or an ADR-050 `RECONCILIATION_REQUIRED` continuation.

Every ConvergenceUnit touched by such a revision invocation must already be a member of `G`:

```text
ConvergenceMembers(I_revision) subset-of G.members
```

A genuinely new ConvergenceUnit is scope expansion and cannot be appended to the immutable group.

Ordinary later `NEW_GROUP` invocations never revise an older group, even when they contribute to exactly the same ConvergenceUnits.

### 5. PromotionGroup exact resolution is group-local, not an alias of live ConvergenceUnit current state

ADR-046's former rule:

```text
Resolve(G) = current READY_INTERNAL state of each member ConvergenceUnit
```

is superseded.

A PromotionGroup maintains a durable **group-local exact resolution**. Conceptually:

```text
G.current_resolution = {
  X -> exact state A,
  Y -> exact state Q,
  ...
}
```

An exact member state is adopted into `G` only from a coherent invocation/group-authorized convergence boundary. Once adopted, later unrelated movement, reopen, readiness loss, or new ordinary authoring on the live ConvergenceUnit does not invalidate or refresh the group-local exact binding.

Thus:

```text
G1[X] = A
live X: A -> B -> C

without G1-bound revision authority:
G1[X] remains A
```

This separates:

```text
current ConvergenceUnit readiness
```

from:

```text
historical/current exact state adopted for one PromotionGroup
```

The latter is an exact durable promotion-source binding, not a perpetual pointer to the live tip.

### 6. Initial group resolution is bound to the originating invocation

For a `NEW_GROUP` invocation, each group member is resolved from the exact ConvergenceUnit state that incorporates the invocation's handed-off ContributionUnits for that member and satisfies the ordinary internal convergence/readiness prerequisites for that checkpoint cohort.

Before external authoring is allowed to advance the same ConvergenceUnit lineage into a later ordinary work-bearing invocation, the prior invocation's required group-local exact boundary must be durably attributable/adoptable so later work cannot erase the earlier cohort boundary.

The exact adoption remains snapshot/CAS guarded. Partial or stale observations never become a group binding.

### 7. Group-bound correction starts from the exact state of that group, not the globally current ConvergenceUnit tip

If:

```text
G1[X] = A
later ordinary G2[X] = B
```

and `G1` receives blocking review feedback, correction authoring for `G1` must be based on the exact reviewed/group state `A` (or its exact current provider-submission projection when that is the authoritative reviewed state), not blindly on live `current(X)=B`.

A correction ContributionUnit may therefore be provisioned from an exact group/submission state while remaining bound to the same logical ConvergenceUnit `X`.

The correction can produce:

```text
G1[X]: A -> A'
```

without absorbing unrelated later work contained in `B`.

The same authored correction effect is then separately reconciled forward into the live ConvergenceUnit lineage so future ordinary development sees both the correction and later work. A conflict in that forward integration is a distinct reconciliation obligation and does not retroactively invalidate the correctness of the group-local correction itself.

### 8. Unchanged group members retain their previous exact binding during a group revision

When a revision invocation touches only a subset of group members, all untouched members retain their prior group-local exact states.

Example:

```text
G = {X,Y}
current group resolution = {X@A, Y@Q}
correction touches X only

new group resolution = {X@A', Y@Q}
```

`Y` is not refreshed from unrelated live `current(Y)` state.

A changed group resolution materializes a new immutable ADR-045/047 PromotionUnit only for repository projections whose exact member set changed; unchanged projections may be reused.

### 9. ADR-050 remains the descendant propagation mechanism

If a parent group's exact state changes:

```text
old parent = A
new parent = A'
child owned state = B
```

an already-distinct child group's internal owned exact state is **not** automatically rewritten merely because its predecessor changed.

ADR-050 continues to compute the provider-facing/effective descendant projection by exact state transplant:

```text
Restack(old_base=A, owned_candidate=B, new_base=A') -> H'
```

A clean transplant preserves the child group's immutable owned effect while updating only its dependent submission projection.

If the transplant conflicts and semantic child authoring is required, `RECONCILIATION_REQUIRED` becomes explicit group-bound continuation authority for the child. Only then may a `REVISE_EXISTING_GROUP(child, authority_ref)` invocation produce a new exact child PromotionUnit. Ordinary predecessor movement alone does not create a cascade of new internal child PromotionUnits.

### 10. Terminal PromotionGroups freeze their group-local resolution

A terminal PromotionGroup (`ALL_PROMOTED`, `COMPENSATED`, `CANCELLED`, or any future terminal settlement state) cannot adopt a new group-local exact resolution.

Later evolution of shared ConvergenceUnits caused by other groups does not mutate the settled group's meaning:

```text
G1 terminal with G1[X] = A
G2 remains live
X later -> B

G1[X] remains A forever as historical settled state
```

This closes the ADR-068 hostile-audit terminal-resolution ambiguity. Terminality freezes the group's adopted settlement-time resolution/history, while exact historical PromotionUnits and realized effects remain independently auditable.

### 11. PromotionUnit supersession is now explicitly same-group revision driven

ADR-067 `SUPERSEDED` remains valid, but replacement of a repository-local PromotionUnit under the same PromotionGroup occurs only when that **same group** legitimately adopts a newer exact group-local resolution through an authorized revision.

Unrelated live ConvergenceUnit movement or a later ordinary PromotionGroup does not supersede an older group's PromotionUnit.

A previously `PROMOTED` exact PromotionUnit remains historical `PROMOTED` as already required by ADR-067/ADR-068 H4 semantics.

### 12. External Control Plane responsibility is narrowed

The External Control Plane / Development System remains authoritative for facts `ruu` cannot infer, including:

- ContributionUnit creation, identity, ConvergenceUnit binding, lifecycle, and authoring authority;
- which ContributionUnits form the current work-bearing invocation cohort;
- frozen mutation handoff and safe authoring reacquisition;
- whether an invocation is ordinary `NEW_GROUP` work or an explicitly authorized revision of an existing group;
- review-correction/reconciliation authority and semantic authoring;
- cancellation, compensation, settlement, policy, governance, and other external semantic dispositions.

It no longer separately declares `PromotionGroup {ConvergenceUnits...}` for ordinary new work. Group membership is a mechanical projection of the sealed work-bearing invocation cohort through the already-authoritative ContributionUnit→ConvergenceUnit bindings.

## Required invariants

```text
INV-161
A work-bearing Ruu invocation has a durable immutable identity and sealed ContributionUnit cohort distinct from its coalescible convergence-demand signal.
```

```text
INV-162
Every ordinary NEW_GROUP invocation creates one distinct PromotionGroup occurrence whose membership is mechanically derived from that invocation's ContributionUnits.
```

```text
INV-163
PromotionGroup identity is occurrence-bound; identical ConvergenceUnit member sets from distinct invocations remain distinct PromotionGroups.
```

```text
INV-164
A PromotionGroup exact resolution is group-local and is not the unqualified current READY_INTERNAL state of its member ConvergenceUnits.
```

```text
INV-165
Unrelated later authoring or ordinary invocations never revise an existing PromotionGroup, even when they reuse the same ConvergenceUnits.
```

```text
INV-166
An existing PromotionGroup may adopt a new exact resolution only from current explicit group-bound correction/reconciliation authority; unchanged members retain their prior exact group binding.
```

```text
INV-167
Group-bound correction authoring is based on that group's exact prior/reviewed state and must not silently absorb effects belonging to later independent invocations.
```

```text
INV-168
A terminal PromotionGroup's group-local exact resolution is frozen historical settlement state.
```

```text
INV-169
Parent-group exact-state movement restacks dependent provider projections under ADR-050; it does not by itself rewrite descendant groups' immutable owned exact state.
```

## Consequences

### Positive

- Repeated invocations in the same development session naturally create distinct promotion cohorts without inventing "ship intent" identities.
- Multi-repository grouping becomes mechanical: all ContributionUnits handed off together project to one PromotionGroup.
- A terminal cancelled/promoted group no longer blocks a later legitimate identical ConvergenceUnit member set.
- Multiple PromotionGroups may safely share one live ConvergenceUnit lineage without older groups following unrelated future authoring.
- Review corrections can revise the exact reviewed group without absorbing later work.
- ADR-050 provides descendant restack without internal-state rewrite cascades.
- Terminal group meaning is historically stable.
- The global reconciler remains trigger-coalescing and fixed-point driven; no FIFO invocation workflow executor is introduced.

### Costs / constraints

- Work-bearing invocation identity and cohort seal become durable managed facts.
- The Development System must preserve invocation idempotency across crash/retry.
- Correction/reconciliation provisioning must support exact group/submission bases rather than only the current ConvergenceUnit tip.
- Implementations must retain enough exact-state provenance to reconcile group-bound correction effects forward into the live ConvergenceUnit lineage.

## Rejected alternatives

### Keep `promotion_group_id = H(members)` and create new ConvergenceUnits to force uniqueness

Rejected. It pollutes ConvergenceUnit identity to compensate for a PromotionGroup occurrence-identity defect.

### Use development-session identity as PromotionGroup identity

Rejected. One session may produce several independent work-bearing invocations/groups.

### Use ordinary branch/ContributionUnit identity as PromotionGroup identity

Rejected. Later ContributionUnits may legitimately feed the same ConvergenceUnit while belonging to a later promotion cohort; branch/artifact identity is not the promotion occurrence boundary.

### Let every live ConvergenceUnit movement refresh every PromotionGroup that references it

Rejected. It causes older groups to absorb unrelated later work and makes terminal settlement unstable.

### Rewrite every descendant group's internal exact state whenever an ancestor group changes

Rejected. ADR-050 already preserves descendant owned effect through exact provider-state transplant. Internal rewrite is required only when transplant conflict creates an explicit semantic reconciliation obligation.

### Make the work-bearing invocation a FIFO workflow job

Rejected. Durable logical invocation identity does not own a reconciler run. ADR-041/042 coalesced demand, global fixed-point sweep, crash recovery, and fencing remain intact.

## Relationship to prior ADRs

ADR-041's statement that an explicit invocation is "only a trigger" is narrowed: its demand/wake-up component remains trigger-only, while a work-bearing checkpoint invocation also has the durable logical receipt defined here. Demand-only invocations remain trigger-only.

ADR-046 remains the historical source of the PromotionGroup concept, but its External-Control-Plane member declaration, member-set-only identity, and unqualified-current-READY_INTERNAL resolution rules are superseded by this ADR.

ADR-047 continues to project one group-local exact resolution deterministically into repository-local PromotionUnits.

ADR-050 remains authoritative for descendant exact-state transplant/restack and conflict escalation.

ADR-053 corrections remain session-independent, but correction authoring is explicitly group-bound and exact-state-based as defined here.

ADR-054's multiple-group ConvergenceUnit sharing is retained and becomes a normal case with independent group-local exact snapshots.

ADR-067 supersession remains repository-local exact-snapshot lifecycle, now triggered only by a legitimate newer resolution of the same PromotionGroup.

## Amendment by ADR-081 — source handoff claims raw authoring provenance

A raw AuthoringDependency predates PromotionGroup identity. The first qualifying handoff accepted after durable dependency-selection TX-A may CAS-claim the pending/raw obligation for its `(PromotionGroup, source repository)` projection only when the same source ContributionUnit's exact frozen checkpoint contains the consumed OID before downward synchronization, the group-local exact state incorporates that checkpoint, and source/consumer immutable PromotionTargets are exactly equal. A handoff accepted between TX-A and dependency-adoption TX-B may be adopted directly as resolved during TX-B/recovery. A historical group or arbitrary candidate containing the OID by ancestry does not qualify.

If source and consumer handoffs already belong to the same immutable group and the source's own exact frozen pre-sync checkpoint contains the consumed OID, the dependency is internal to the existing repository projection and creates no provider edge. Group membership is never changed to force that result.
