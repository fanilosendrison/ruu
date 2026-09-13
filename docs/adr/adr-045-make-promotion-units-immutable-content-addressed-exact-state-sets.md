---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make PromotionUnits immutable content-addressed exact-state sets"
id: "ADR-045"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "70a1efc584517c932de68ebba30e38198a5fe49d49b4b1792debfccf5223921d"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-045: Make PromotionUnits immutable content-addressed exact-state sets

- **Status:** Accepted; amended by ADR-061
- **Date:** 2026-09-05
- **Decision order:** 045

## Context

ADR-027 separated repository-local ConvergenceUnits from promotion/submission units and promotion topology. ADR-039 assigned semantic promotion grouping to the External Control Plane. Backlog item 30.16 still left the concrete PromotionUnit declaration contract open and listed fields such as caller-supplied identity, target intent, stack parent, and an optional semantic-readiness token.

ADR-043 subsequently made promotion target/mode/topology authorization policy-driven and non-bypassable, so a PromotionUnit declaration cannot carry an alternate target or runtime promotion-policy override. The exact-state/CAS architecture also makes mutable, caller-named promotion definitions unnecessarily ambiguous.

The declaration contract therefore needs one narrow meaning:

> identify exactly which immutable ConvergenceUnit states constitute one promotion unit.

## Decision

### 1. PromotionUnit definition is only an exact member set

A PromotionUnit definition is a non-empty set of canonical exact ConvergenceUnit-state references:

```text
PromotionUnitDefinition {
  members: Set<ExactConvergenceStateRef>  // non-empty, unique, unordered
}
```

`ExactConvergenceStateRef` is the protocol's canonical exact-state reference for a ConvergenceUnit and includes whatever repository/state identity is required to name that exact state unambiguously. PromotionUnit does not duplicate a second independent `convergence_unit_id + OID` identity scheme when a canonical exact-state reference already exists.

Member order has no semantic meaning. Duplicate members are invalid/non-canonical and are collapsed only for canonical-equivalence checking; callers MUST supply a valid set representation.

### 2. PromotionUnit identity is content-addressed

The PromotionUnit identity is derived from the canonical immutable definition, not supplied as semantic identity by the External Control Plane:

```text
promotion_unit_id = H(domain + schema_version + canonical(sorted(members)))
```

For v1, `H` is SHA-256. The domain separator and schema/hash-version identifier are part of the hashed bytes. Canonical member references are sorted by their canonical byte representation and encoded unambiguously (length-delimited or an equivalently injective canonical encoding) before hashing.

Consequences:

```text
same exact member set
→ same promotion_unit_id

any exact member-state change
→ different promotion_unit_id
```

The same exact member set redelared later resolves to the same PromotionUnit, including after it has already completed promotion.

### 3. Definition is immutable

There is no `UPDATE PromotionUnit definition` operation.

If one member changes from an exact state `B@y` to `B@z`, the resulting definition has a different content address and is a different PromotionUnit.

Lifecycle changes do not change identity:

```text
DECLARED → eligible/waiting/blocked → promoted/terminal
```

all refer to the same content-addressed PromotionUnit definition.

### 4. Declaration is intrinsically idempotent

The external declaration surface is conceptually:

```text
DeclarePromotionUnit(members: Set<ExactConvergenceStateRef>)
  → PromotionUnitRef(promotion_unit_id)
```

If the canonical content address already exists, declaration returns/reuses that same immutable PromotionUnit. There is no caller-supplied PromotionUnit ID needed for retry idempotence.

A persisted row whose stored ID does not match the canonical definition is `UNKNOWN_INCONSISTENT` / identity-integrity failure and cannot authorize promotion.

### 5. Structural declaration validity is separate from promotion eligibility

Declaration validation checks mechanical facts only, including:

```text
non-empty canonical member set
all exact-state references are syntactically valid
all referenced exact ConvergenceUnit states are known/resolvable as required by current storage/recovery rules
content address matches canonical definition
```

The definition does not itself assert that promotion may happen now.

Promotion eligibility remains a separate current-state predicate. It may require, among other existing guards:

```text
all exact member states satisfy READY_INTERNAL/current exact-source rules
required verification evidence is valid
promotion topology dependencies are compatible
EffectivePromotionPolicy is valid and CURRENT
provider/target observations are current
no conflict/unknown/recovery blocker exists
```

Thus a structurally valid immutable PromotionUnit may exist while currently waiting, stale, blocked, or otherwise ineligible.

### 6. Promotion topology is separate from PromotionUnit identity

Dependency/stack edges are not intrinsic fields of a PromotionUnit and are not hashed into `promotion_unit_id`.

Conceptually:

```text
PromotionUnit P1 = {...}
PromotionUnit P2 = {...}

PromotionTopology = explicit relationship/edges among PromotionUnit refs
```

Changing topology does not change the identity of its PromotionUnit nodes. The exact topology declaration API remains outside this ADR except for this separation; restacking/materialization remains under later backlog items.

### 7. PromotionUnit carries no target, mode, runtime policy input, or semantic token

The PromotionUnit declaration MUST NOT contain fields that can bypass or duplicate policy authority, including:

```text
target intent
target repository/ref selection
promotion mode
publication relation
policy override
local/runtime preference
```

Those are resolved by the authoritative `EffectivePromotionPolicy` under ADR-043/ADR-044.

The declaration also carries no separate `semantic readiness token`. The External Control Plane's act of declaring the exact member set is the semantic grouping assertion. Current promotion readiness is then determined mechanically by `ruu` from exact state and policy.

Higher-level task/feature/work-package identity remains external and is not part of `promotion_unit_id`.

## Rationale

This keeps the boundary narrow:

```text
Development System / External Control Plane
→ decides which exact states belong together semantically

Ruu PromotionUnit
→ immutable exact-state set with deterministic identity

PromotionTopology
→ separate relationship among PromotionUnits

EffectivePromotionPolicy
→ authoritative rules governing where/how promotion may occur
```

Content addressing removes caller-ID conflicts, makes retry idempotence intrinsic, prevents a PromotionUnit from changing meaning under the reconciler, and aligns promotion identity with the architecture's exact-state/CAS model.

## Consequences

### Positive

- A PromotionUnit has one deterministic meaning everywhere.
- Same declaration is idempotent without a separate idempotency key.
- No mutable definition can change under outstanding obligations.
- Promotion identity is independent of semantic task identity, topology, lifecycle, and provider-facing submission revision.
- Target/mode cannot be smuggled around promotion policy through the declaration API.
- Re-declaring an already-promoted exact set observes the same completed PromotionUnit instead of fabricating a duplicate promotion object.

### Costs

- The External Control Plane must retain any task/feature → PromotionUnit correlation it needs.
- A changed exact source state always creates a new PromotionUnit identity.
- Canonical exact-state reference encoding and content-address versioning become protocol compatibility requirements.

## Rejected alternatives

### Caller-supplied opaque PromotionUnit UUID

Rejected. It creates a mutable identity/payload consistency problem and duplicates idempotency machinery. Semantic identity belongs above `ruu`.

### Mutable PromotionUnit revisions

Rejected. If exact members change, the promotion object has changed. A new content address is clearer and preserves exact-state identity.

### Put target/mode in the declaration

Rejected. ADR-043 makes promotion authorization policy-driven and non-bypassable.

### Put dependency/stack parent in the PromotionUnit definition

Rejected. Topology is a relationship among PromotionUnits, not intrinsic identity of a node.

### Separate semantic-readiness token

Rejected. It duplicates the External Control Plane declaration and mixes semantic signaling with mechanical current-state promotion eligibility.

## Backlog impact

Backlog item **30.16 is closed**.

30.17 is resolved by ADR-046: semantic grouping is predeclared durably as an immutable closed content-addressed `PromotionGroup` over canonical ConvergenceUnit refs, then resolved mechanically to exact `READY_INTERNAL` member states and materialized as this ADR's PromotionUnit. There is no implicit singleton/default mapping.

30.18 is subsequently closed by ADR-047. At the time of this ADR, follow-up items included:

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

Amends ADR-027, ADR-039, ADR-043, and ADR-044. ADR-046 subsequently closes 30.17; ADR-047 closes 30.18 and adds repository-local structural validity without changing this ADR's content-address algorithm. ADR-054 subsequently closes 30.24 and ADR-055 closes 30.25; backlog 30.26 is subsequently closed by ADR-056 after ADR-053 closes 30.23 and ADR-052 closes 30.22, ADR-051 closes 30.21, ADR-049/ADR-050 close 30.19/30.20, and ADR-048 closes 30.39.


## ADR-046 amendment

The External Control Plane no longer waits for exact `READY_INTERNAL` refs and directly declares a PromotionUnit as the normal flow. It durably predeclares a closed content-addressed `PromotionGroup` over logical canonical ConvergenceUnit refs before convergence demand. `ruu` resolves that group to the current exact `READY_INTERNAL` refs under snapshot/CAS. ADR-047 subsequently partitions the complete exact set by authoritative source repository and invokes this ADR's immutable content-addressed PromotionUnit materialization once per represented repository. The content-address algorithm itself is unchanged.


## Amendment by ADR-047

ADR-047 adds a structural validity constraint without changing this ADR's content-address algorithm: every current v1 PromotionUnit MUST contain exact ConvergenceUnit-state refs from exactly one authoritative source repository. Cross-repository exact member sets are invalid PromotionUnit definitions. A completely resolved cross-repository PromotionGroup is partitioned by repository and yields one content-addressed PromotionUnit per represented repository.

This source-membership locality is distinct from `CROSS_REPOSITORY` PR publication relation, which remains an EffectivePromotionPolicy/provider concern.

## Amendment by ADR-061

PromotionTarget remains outside PromotionUnit content identity because it is already an immutable binding of each member ConvergenceUnit. Structural validity now also requires all members of one repository-local PromotionUnit projection to have the same PromotionTarget; conflicting same-source target bindings fail closed.

