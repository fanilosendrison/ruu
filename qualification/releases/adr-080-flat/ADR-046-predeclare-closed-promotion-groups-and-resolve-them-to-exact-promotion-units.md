# ADR-046: Predeclare closed PromotionGroups and resolve them to exact PromotionUnits

## Status

Accepted — 2026-09-05; materialization rule amended by ADR-047

## Context

ADR-045 made a PromotionUnit an immutable, content-addressed set of exact ConvergenceUnit-state references. That exact definition cannot exist until the relevant ConvergenceUnits have reached concrete `READY_INTERNAL(OID)` states.

Backlog item 30.17 still left open how a normal sweep gets from repository-local ConvergenceUnits to a PromotionUnit. A naive default such as:

```text
READY_INTERNAL(CX@x)
→ implicitly create PromotionUnit {CX@x}
```

would infer semantic independence from silence. That is unsafe for the common case where one agent/session implements one logical change across several repositories and those repository-local ConvergenceUnits must be promoted together.

Returning control to the external Development System only after `READY_INTERNAL` would preserve semantic authority but would split a single convergence run at a point where the caller already knew, before invoking `ruu`, which ConvergenceUnits belong to the same ship.

The architecture also cannot attach this information only to one invocation. ADR-041 makes explicit invocations coalescible demand signals, and ADR-042 makes current-state reconciliation/recovery authoritative rather than workflow-step resumption. Promotion grouping therefore needs durable, trigger-independent representation.

## Decision

Backlog item **30.17 is closed** by introducing a durable pre-resolution `PromotionGroup`.

### 1. PromotionGroup is the pre-exact semantic grouping object

The External Control Plane declares which logical ConvergenceUnits must resolve into one future PromotionUnit before it signals convergence demand.

A v1 PromotionGroup definition is:

```text
PromotionGroupDefinition {
  members: Set<CanonicalConvergenceUnitRef>
}

CanonicalConvergenceUnitRef {
  repository_id
  convergence_unit_id
}
```

The repository component is required because ConvergenceUnit identity is repository-local while a PromotionGroup may span repositories.

The set is non-empty, unordered, unique, closed, and immutable. It is complete at declaration time; `ruu` never infers that another member may or may not still arrive.

### 2. PromotionGroup identity is content-addressed

V1 derives:

```text
promotion_group_id =
  SHA-256(
    domain = "Ruu/promotion-group"
    || schema_version
    || canonical(sorted(members))
  )
```

The same canonical ConvergenceUnit set therefore identifies the same PromotionGroup. Changing membership creates a different PromotionGroup; there is no in-place member update.

The PromotionGroup identity is not a PromotionUnit identity:

```text
PromotionGroup
= stable logical ConvergenceUnit membership before exact resolution

PromotionUnit
= immutable exact READY_INTERNAL state set after resolution
```

A stable PromotionGroup may resolve to a different PromotionUnit after one of its ConvergenceUnits is semantically reopened and later reaches a different exact `READY_INTERNAL` state.

### 3. Declaration is durable and trigger-independent

Conceptually the External Control Plane performs:

```text
DeclarePromotionGroup(
  members: Set<CanonicalConvergenceUnitRef>
) → PromotionGroupRef

signal convergence demand
```

The authoritative declaration must be durable before/independently of the convergence trigger. It is not caller/session metadata attached only to one invocation.

This preserves ADR-041/ADR-042 semantics:

```text
trigger
≠ authority token
≠ semantic grouping payload whose loss would change correctness
```

Concurrent/coalesced invocations, crash recovery, and later global sweeps observe the same durable PromotionGroup definition.

### 4. `ruu` resolves completeness mechanically

For a declared group:

```text
G = {CX, CY, CZ}
```

`ruu` considers it currently resolvable only when every member has exactly one current exact state satisfying `READY_INTERNAL`:

```text
CX → READY_INTERNAL@x
CY → READY_INTERNAL@y
CZ → READY_INTERNAL@z
```

Then:

```text
Resolve(G) = {
  ExactConvergenceStateRef(CX@x),
  ExactConvergenceStateRef(CY@y),
  ExactConvergenceStateRef(CZ@z)
}
```

and ADR-045 deterministically materializes/reuses:

```text
PromotionUnit {
  CX@x,
  CY@y,
  CZ@z
}
```

If any declared member lacks a current valid `READY_INTERNAL` state, the group is mechanically unresolved/waiting. No partial PromotionUnit is created.

### 5. Resolution/materialization is snapshot/CAS guarded

The exact-state set used for PromotionUnit materialization must come from one coherent current-state snapshot guarded by expected-state/generation checks.

Conceptually:

```text
read all current member READY_INTERNAL exact refs
↓
validate complete closed membership
↓
CAS/adopt only if those member states/generations are still current
↓
materialize/reuse content-addressed PromotionUnit
```

If a member moves, reopens, loses readiness, or otherwise invalidates the observed exact state before adoption, resolution is abandoned and retried from current state. The old exact state is never silently carried forward.

### 6. No mid-sweep Development System handoff is required

Once the durable PromotionGroup declaration exists, the global reconciler may perform in one uninterrupted convergence run:

```text
ContributionUnit progress
→ ConvergenceUnit progress
→ READY_INTERNAL exact states
→ PromotionGroup exact resolution
→ PromotionUnit materialization
→ further promotion obligations
```

The Development System is not called back merely to restate grouping after OIDs become known.

A handoff remains appropriate only for a genuine external decision/blocking condition, not for deterministic exact-state resolution of an already-declared group.

### 7. There is no implicit singleton/default mapping inside `ruu`

`READY_INTERNAL` alone never means "promote independently".

A singleton shipment is represented explicitly by:

```text
PromotionGroup {CX}
```

and resolves mechanically to:

```text
PromotionUnit {CX@current_READY_INTERNAL_oid}
```

A multi-repository shipment is represented identically:

```text
PromotionGroup {CX, CY, ...}
```

Therefore no repository-policy or built-in `1 ConvergenceUnit → 1 PromotionUnit` default is required or authoritative. Silence means no PromotionGroup declaration, not permission to manufacture a singleton.

### 8. ConvergenceUnit is the atomic promotion-grouping boundary

PromotionGroup membership is expressed at ConvergenceUnit granularity. `ruu` does not split one ConvergenceUnit by ContributionUnit provenance when forming a PromotionUnit.

Consequently, work that must remain independently promotable must be assigned by the External Control Plane to distinct ConvergenceUnits before convergence. If independent semantic work is intentionally placed in the same ConvergenceUnit, the resulting exact ConvergenceUnit state is one indivisible member for promotion-group resolution.

`ruu` still does not infer session, agent, task, or feature identity.

**ADR-053 amendment:** the session-local workflow describes how the initial closed group is commonly declared; it does not bind later correction authoring to that runtime. A later restored/new review-correction continuation session may create new ContributionUnits bound to existing member ConvergenceUnits without changing PromotionGroup membership. Only creation of a genuinely new ConvergenceUnit changes the logical member set and therefore requires a different PromotionGroup.

### 9. PromotionGroup is separate from PromotionTopology and EffectivePromotionPolicy

PromotionGroup answers:

```text
which logical ConvergenceUnits must resolve together?
```

PromotionUnit answers:

```text
which exact READY_INTERNAL states are the current resolved shipment object?
```

PromotionTopology answers:

```text
how do PromotionUnits depend/stack relative to one another?
```

EffectivePromotionPolicy answers:

```text
where and under which authoritative rules may the PromotionUnit be promoted?
```

None of topology, target/mode/publication policy, provider submission revision, runtime caller identity, or session identity participates in PromotionGroup content addressing.

## Consequences

### Positive

- The main agent/Development System can state grouping once, before the sweep, when it already knows which repository-local ConvergenceUnits its implementation touched.
- A single Ruu run can continue through `READY_INTERNAL` into PromotionUnit materialization without an artificial round-trip.
- Singleton and multi-repository shipments use one mechanism.
- Completeness is explicit and mechanical because the member set is closed at declaration time.
- Coalesced triggers and crash recovery cannot lose semantic grouping.
- PromotionUnit remains exact-state-bound and immutable as required by ADR-045.
- `ruu` never infers semantic independence from silence.

### Negative / constraints

- The External Control Plane must know the ConvergenceUnit identities that form the ship before signaling convergence demand that is expected to continue through promotion.
- If the semantic ship membership changes, a different immutable PromotionGroup is required.
- Independent work accidentally placed in one ConvergenceUnit cannot later be separated by PromotionGroup logic; that is a higher-level grouping error.
- Repository-local multi-source candidate/head materialization was separated as backlog 30.39 and subsequently closed by ADR-048.

## Rejected alternatives

### Implicit singleton for every READY_INTERNAL ConvergenceUnit

Rejected. `READY_INTERNAL` is an internal mechanical readiness fact and cannot imply semantic independence or publication intent.

### Return to the Development System after READY_INTERNAL and ask for grouping

Rejected as the default flow. The Development System already knows grouping before the sweep in the intended session-local workflow, while exact OIDs are the only missing information. The new PromotionGroup lets Ruu fill those exact states mechanically without interrupting the run.

### Invocation-local grouping marker only

Rejected. Explicit invocations may coalesce and are not authority tokens. Correctness-critical grouping must survive trigger loss/coalescing and crash recovery.

### Group by repository names

Rejected. Repository identity is too coarse and path/name is not authoritative; multiple ConvergenceUnits may coexist in one repository.

### Group by ContributionUnits and reconstruct many-to-one lineage later

Rejected for this need. The External Control Plane already owns ContributionUnit→ConvergenceUnit membership. Promotion grouping is most directly and deterministically declared over the logical ConvergenceUnits that will become PromotionUnit exact-state members.

### Hash chain as the primary representation

Rejected. The needed object is a closed unordered set across potentially multiple repositories, not a linear history. Content-addressing the canonical set is sufficient; no Merkle/provenance DAG is required for 30.17.

## Amendment by ADR-047

ADR-047 supersedes this ADR's original `one PromotionGroup → one PromotionUnit` materialization rule. A PromotionGroup remains one immutable closed logical ship and may span repositories, but after the whole group has current exact `READY_INTERNAL` states, `ruu` partitions the complete exact snapshot by authoritative source repository and materializes/reuses **exactly one repository-local PromotionUnit per represented repository**.

Thus a cross-repository group resolves to a complete `repository_id → PromotionUnitRef` mapping, not to one cross-repository PromotionUnit. Same PromotionGroup plus same repository is never split by `ruu`. PromotionTopology remains separate and is not synthesized by this projection. ADR-047 closes 30.18; downstream same-repository multi-source candidate/head composition was tracked separately as 30.39 and subsequently closed by ADR-048.

## Backlog impact

Backlog item **30.17 is closed**.

30.18 is resolved by ADR-047 through deterministic projection by authoritative source repository. At the time of this ADR, follow-up items included:

- repository-local multi-source candidate/head materialization (30.39; subsequently closed by ADR-048);
- submission-ref creation/naming/retention;
- local vs provider-managed restacking implementation;
- provider capability discovery (subsequently closed by ADR-051);
- DIRECT candidate workspace implementation;
- semantic review-correction continuation (subsequently closed by ADR-053);
- PromotionUnit completion versus ConvergenceUnit retirement;
- cross-repository compensation;
- new repository creation/provisioning authority (subsequently closed by ADR-056).

## Related decisions

Amends ADR-027, ADR-039, ADR-041, ADR-042, and ADR-045. ADR-047 subsequently amends the cross-repository materialization rule. ADR-054 subsequently closes 30.24 and ADR-055 closes 30.25; backlog 30.26 is subsequently closed by ADR-056 after ADR-053 closes 30.23 and ADR-052 closes 30.22, ADR-051 closes 30.21, ADR-049/ADR-050 close 30.19/30.20, and ADR-048 closes 30.39.

## ADR-054 amendment — group settlement gates ConvergenceUnit semantic closure

A PromotionGroup is not merely a pre-resolution grouping boundary; its aggregate terminal settlement also participates in the retirement guard of every member ConvergenceUnit. Repository-local PromotionUnit success within `PARTIALLY_PROMOTED` cannot close/retire that member lineage. ConvergenceUnit `PROMOTED` requires every relevant group/promotion obligation to be terminally settled and no current correction/authoring/reconciliation demand able to reopen it.

## Amendment by ADR-061

A declared PromotionGroup may contain several repositories, but every same-source repository projection must be PromotionTarget-coherent. Conflicting immutable targets in one same-source partition are not repaired by implicit splitting; resolution fails closed and the higher-level workflow must use appropriate distinct convergence/promotion scopes.

## Amendment by ADR-067 — current resolution replacement drives PromotionUnit supersession

No new PromotionGroup-resolution semantic object is introduced. This ADR's existing rule that a stable PromotionGroup may resolve to different exact PromotionUnits is sufficient. When the adopted current repository projection changes from `P0` to `P1`, ADR-067 records the exact `P0.superseded_by = P1` relation and terminalizes `P0` only after any unresolved committed/recovery effect for `P0` is safely resolved.

## Amendment by ADR-068 — immutable groups may terminally settle as CANCELLED before realization

A PromotionGroup's immutable membership survives semantic withdrawal. ADR-068 adds terminal `CANCELLED` settlement for an explicitly withdrawn **still-unrealized** group, but only after zero realized promotion effects and zero unresolved committed/uncertain or otherwise still-realizing managed promotion surfaces are established. Cancellation never edits membership. If desired membership changes before realization, the old group terminalizes as `CANCELLED` and the External Control Plane declares a distinct new immutable PromotionGroup.

`CANCELLED` participates in ADR-054 ConvergenceUnit closure/disposition guards, but cancellation of one group does not automatically abandon a member that remains referenced by another nonterminal/replacement group or current authoring/reconciliation demand.

## Supersession amendment by ADR-069

ADR-069 retains the `PromotionGroup` concept but supersedes three ADR-046 rules: ordinary group membership is no longer separately declared by the External Control Plane, `promotion_group_id` is no longer derived solely from the ConvergenceUnit member set, and resolution is no longer an alias of each member's unqualified live current `READY_INTERNAL` state. Ordinary groups are occurrence-bound to sealed work-bearing logical invocations, and exact state is group-local.

