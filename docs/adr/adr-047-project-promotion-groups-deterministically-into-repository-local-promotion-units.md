---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Project PromotionGroups deterministically into repository-local PromotionUnits"
id: "ADR-047"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "bd581fbbe54dfa429be1eb650c61955f3b61349cf116b991250e11c6461f66d6"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-047: Project PromotionGroups deterministically into repository-local PromotionUnits

## Status

Accepted — 2026-09-06

## Context

ADR-045 made a PromotionUnit an immutable content-addressed set of exact `ExactConvergenceStateRef` members. ADR-046 then introduced a durable pre-exact `PromotionGroup` so a development session can declare, before exact OIDs exist, which repository-local ConvergenceUnits belong to one logical ship.

ADR-046 still mapped one completely resolved PromotionGroup to one PromotionUnit. That is not valid for a PromotionGroup spanning several repositories: a Git commit/ref, candidate, direct target advancement, or PR head is necessarily repository-local. A multi-repository exact-state set therefore cannot itself be one Git promotion object.

The intended v1 workflow is also more constrained than an arbitrary packaging problem: all ConvergenceUnits emitted by the same development session for the ship are intended to be published together. `ruu` is not asked to choose PR granularity, split a same-repository group into a stack, or infer publication intent. It receives durable grouping state from the External Control Plane and applies already-established repository/promotion policy and topology rules.

Backlog item 30.18 is therefore primarily a structural projection problem, not a semantic packaging decision and not primarily a Git merge/composition algorithm.

## Decision

Backlog item **30.18 is closed** by deterministically projecting each completely resolved PromotionGroup by source repository.

### 1. PromotionGroup remains the logical ship boundary

A PromotionGroup remains:

```text
PromotionGroupDefinition {
  members: Set<CanonicalConvergenceUnitRef>
}

CanonicalConvergenceUnitRef = (repository_id, convergence_unit_id)
```

It may span one or more repositories.

For the intended v1 session-scoped workflow, the External Control Plane groups all ConvergenceUnits produced by the same development session for that ship into the same closed PromotionGroup before convergence demand. Session/provenance identity establishes grouping upstream but does **not** participate in `promotion_group_id`; `ruu` still does not infer session identity from caller/process/CWD/branch state.

Changing group membership creates a different immutable PromotionGroup as defined by ADR-046.

### 2. Exact group resolution is complete before repository projection

For:

```text
G = {
  RepoA/CX,
  RepoA/CY,
  RepoB/CZ
}
```

`ruu` waits until every member has one current exact `READY_INTERNAL` state in one coherent snapshot:

```text
RepoA/CX@x
RepoA/CY@y
RepoB/CZ@z
```

There is still no partial semantic group resolution. Missing/stale/reopened members keep the group unresolved exactly as in ADR-046.

### 3. Projection is a deterministic partition by authoritative repository identity

For every repository `R` represented in a resolved group `G`, define:

```text
Project(G, R)
  = {
      ExactState(C)
      | C ∈ G.members
      ∧ repository(C) = R
    }
```

Exactly one non-empty projected member set exists per represented repository.

Therefore:

```text
PromotionGroup G
  → 1..N repository-local projections
  → 1..N PromotionUnits

N = number of distinct authoritative repository_ids in G.members
```

For the example:

```text
Project(G, RepoA) = {CX@x, CY@y}
Project(G, RepoB) = {CZ@z}
```

and ADR-045 materializes/reuses:

```text
PromotionUnit PA = {RepoA/CX@x, RepoA/CY@y}
PromotionUnit PB = {RepoB/CZ@z}
```

No ordering, caller choice, branch naming, commit ancestry, policy heuristic, or LLM decision participates in this partition.

### 4. PromotionUnit is structurally repository-local

A structurally valid v1 PromotionUnit MUST contain exact ConvergenceUnit-state refs from exactly one authoritative source repository:

```text
∀ a,b ∈ PromotionUnit.members:
  repository(a) = repository(b)
```

A cross-repository exact member set is not a valid PromotionUnit definition.

This restriction concerns PromotionUnit **source membership**. It does not prohibit a repository-local PromotionUnit from using a policy-authorized `CROSS_REPOSITORY` PR publication relation (for example a fork/source repository publishing to an upstream target repository).

ADR-045 content-addressing remains unchanged for valid repository-local member sets.

### 5. Same PromotionGroup + same repository means one PromotionUnit

`ruu` MUST NOT split one `(promotion_group_id, repository_id)` projection into several PromotionUnits.

Therefore:

```text
same PromotionGroup
+ same source repository
→ same repository-local PromotionUnit incarnation
```

If a session-produced group contains `RepoA/CX` and `RepoA/CY`, they project together into one repository-local PromotionUnit once exact.

This is not a policy/default guess. It is the deterministic meaning of the already-authoritative PromotionGroup boundary plus the mandatory Git repository boundary.

### 6. Different repositories create independently governed promotion tracks under one logical group

A cross-repository PromotionGroup does not imply a native atomic Git transaction.

Each resulting repository-local PromotionUnit has its own promotion lifecycle and EffectivePromotionPolicy resolution:

```text
G
├── PA / RepoA → DIRECT or PR → lifecycle A
└── PB / RepoB → DIRECT or PR → lifecycle B
```

The higher-level PromotionGroup may therefore observe aggregate progress such as:

```text
NONE_PROMOTED
PARTIALLY_PROMOTED
ALL_PROMOTED
UNKNOWN_INCONSISTENT
```

consistent with ADR-014. `PARTIALLY_PROMOTED` describes the cross-repository logical group, not a cross-repository PromotionUnit.

### 7. Group current resolution adopts a complete repository→PromotionUnit mapping

The reconciler-derived resolved form of a PromotionGroup is now conceptually:

```text
RESOLVED({
  repository_id -> PromotionUnitRef
})
```

The exact READY_INTERNAL source snapshot is read coherently and repository-partitioned deterministically. Content-addressed PromotionUnit definitions may be materialized idempotently, but adoption of the group's **current resolution mapping** is guarded by expected-state/CAS against the complete source snapshot.

If any source member moves/reopens/loses readiness before adoption, the current group resolution is not adopted and resolution retries from current state.

### 8. A stable pre-exact repository projection key is derivable, not a new semantic object

The pair:

```text
(promotion_group_id, repository_id)
```

uniquely identifies the repository-local projection boundary before exact OIDs are known.

V1 does not require a new caller-declared `PromotionIntent`, `PromotionSlot`, or semantic proposal-partition object for 30.18. Implementations may persist/index this derived pair for correlation, but it does not alter PromotionGroup or PromotionUnit content-addressing.

ADR-049 subsequently binds stable logical submission identity to this repository-local projection plus its canonical publication destination and always uses a distinct provider-facing submission ref.

### 9. PromotionTopology remains separate and is never synthesized by projection

Repository partitioning does not create stack/dependency edges.

`ruu` MUST NOT transform one same-repository group projection into several PromotionUnits merely to manufacture a stacked PR workflow.

PromotionTopology remains separate from repository partition and never causes one `(promotion_group_id, repository_id)` projection to split. ADR-050 subsequently refines its authority: current stack/dependency topology is derived from exact managed effective-base/predecessor/target facts among already-distinct promotion obligations, not caller publication intent and not branch/task/session names, arrival order, or arbitrary ancestry.

Restack semantics are subsequently closed by ADR-050; provider capability normalization is subsequently closed by ADR-051.

### 10. Exact Git candidate materialization is a separate downstream problem

For a repository-local PromotionUnit containing several exact source states:

```text
PromotionUnit {
  RepoA/CX@x,
  RepoA/CY@y
}
```

Git/provider publication still needs one exact repository-local candidate/head representation.

The deterministic composition/materialization algorithm, conflict representation, base selection, ancestry reuse, merge ordering/strategy, and recovery mechanics are **not** decided by this ADR. They were moved to backlog item **30.39 — repository-local multi-source candidate materialization**, subsequently closed by ADR-048.

Thus:

```text
logical multi-repository group projection
≠ repository-local Git candidate composition
```

## Consequences

### Positive

- A session-scoped logical ship may span repositories without pretending Git offers a cross-repository commit or atomic promotion transaction.
- PromotionUnit obtains a clean repository-local invariant aligned with Git mutation/ref semantics.
- Cross-repository partial progress belongs naturally to the PromotionGroup aggregate while each PromotionUnit keeps a normal local lifecycle.
- Projection is deterministic: it is exactly `GROUP BY authoritative repository_id` over one already-closed logical ship.
- `ruu` introduces no new semantic packaging authority and requires no mid-sweep callback.
- Same-repository members of one PromotionGroup cannot be silently fragmented into micro-PRs/stacks.
- ADR-045 exact-state content addressing remains useful and unchanged for valid repository-local units.

### Costs / constraints

- ADR-046's original `one PromotionGroup → one PromotionUnit` wording is superseded.
- Existing persisted cross-repository PromotionUnit definitions, if any, are invalid under the current v1 model and must fail closed/migrate rather than be treated as current valid units.
- Multi-source same-repository candidate materialization was left open under 30.39 by this ADR and subsequently closed by ADR-048.
- Stable submission identity and pre-exact topology correlation must not be guessed from this ADR beyond the deterministic `(promotion_group_id, repository_id)` projection boundary.

## Rejected alternatives

### Keep one cross-repository PromotionUnit

Rejected. A single Git candidate/head/ref cannot contain exact states from unrelated repositories, and lifecycle/policy would become a composite pseudo-transaction inconsistent with ADR-014.

### Let the caller choose a proposal partition during Ruu execution

Rejected. The intended workflow already supplies authoritative logical grouping before convergence demand. Runtime caller preference is not part of Ruu authority.

### Introduce PromotionIntent / PromotionSlot to choose PR boundaries

Rejected for 30.18. No additional semantic choice is required: PromotionGroup gives the logical ship boundary and repository identity gives the mandatory Git partition boundary.

### Split same-repository group members automatically into stacked PRs

Rejected. That would invent promotion granularity/topology not present in authoritative input state.

### Group only by repository and discard PromotionGroup

Rejected. Repository identity cannot express that several repository-local promotions belong to the same session-scoped logical ship and must be tracked together at the higher level.

## Backlog impact

Backlog item **30.18 is closed**.

A new explicit item **30.39** retained the downstream unresolved problem of repository-local multi-source candidate/head materialization; ADR-048 subsequently closes it.

ADR-054 subsequently closes 30.24 and ADR-055 closes 30.25; 30.26 is subsequently closed by ADR-056 after ADR-053 closes 30.23, ADR-052 closes 30.22, ADR-051 closes 30.21, and ADR-049/ADR-050 close 30.19/30.20, with 30.19 now able to consider `(promotion_group_id, repository_id)` as a stable pre-exact correlation boundary without this ADR deciding submission-ref identity.

## Related decisions

Amends ADR-014, ADR-027, ADR-045, and ADR-046. Integrates with ADR-041/ADR-042 reconciler/CAS semantics and ADR-043/ADR-044 policy authority/currentness.

## Amendment by ADR-061

The one-PromotionUnit-per-source-repository projection rule gains a target-coherence precondition: all ConvergenceUnits in that source partition must share the same immutable PromotionTarget. A target-incoherent partition is invalid; projection never splits by target.

## Amendment by ADR-067 — current repository mapping replacement is explicit historical lineage

The `RESOLVED(repository_id → PromotionUnitRef)` mapping remains the current reconciler-derived repository projection. Replacing one repository entry with a new content-addressed PromotionUnit makes the old unit non-current and records an exact supersession edge; it does not mutate the PromotionGroup or the old PromotionUnit definition. `PROMOTED` old units remain historical success; unresolved old external effects remain recovery-visible until disposition is known.

## Amendment by ADR-069

Repository-local projection is unchanged structurally, but `Project(G,R)` now consumes the PromotionGroup's adopted **group-local exact member mapping** rather than re-reading each member's unqualified live current `READY_INTERNAL` state. Later unrelated live movement does not change an older group's projection.

