---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require substrate-independent heterogeneous authoring surfaces"
id: "ADR-086"
status: "accepted"
date: "2026-09-28"
decision_body_sha256: "55ff80c9be7ce8cab6206b87dae5013bb1dc92694518857192b7dcf90fbe6e20"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-070"
    - "ADR-084"
  supersedes: []
  confirms:
    - "ADR-078"
governs:
  - "Product-intent authoring-surface substrate independence"
  - "Heterogeneous authoring-surface coexistence"
  - "Per-ContributionUnit authoring-surface realization"
  - "Convergence semantics independence from authoring-surface realization"
---

# ADR-086 — Require substrate-independent heterogeneous authoring surfaces

- **Status:** Accepted
- **Date:** 2026-09-28
- **Amends:** ADR-070, ADR-084, the consolidated specification, the External Control Plane contract, and the architecture overview
- **Confirms:** ADR-078

## Context

ADR-084 correctly replaced the mandatory linked Git worktree with the abstract
`ContributionUnit Authoring Surface` contract. The surface contract became
realization-neutral: any surface satisfying the common guarantees is admissible,
and the mechanism that isolates or realizes it stays outside the Ruu model.

That formulation makes each surface individually realization-neutral. It does
not yet make sufficiently explicit a stronger product property: several active
`ContributionUnit`s must be able to use **simultaneously different conforming
realizations**. Reading ADR-084 in isolation still permits an implementation to
homogenize the substrate globally while treating every individual surface as
conforming.

Without this requirement, an implementation could still introduce a global
homogeneous mode such as:

```text
authoring_surface_mode = WORKTREE
```

or:

```text
authoring_surface_mode = EXTERNALLY_ISOLATED_PRIMARY_TREE
```

and require that every active surface use the same realization.

That behavior would contradict the objective ADR-084 already accepted: Ruu must
depend on the guarantees of the surface contract, not on the mechanism that
realizes them. A coordination-domain-wide substrate mode is exactly such a
dependency, because it makes correctness depend on which mechanism was selected
rather than on whether each surface independently satisfies the common
contract.

The missing distinction is therefore between per-surface realization neutrality
and **product-level substrate independence with heterogeneous coexistence**. Ruu
needs the second property stated as product intent, because the first does not
entail it.

## Discovery classification

```text
decision-required, resolved; governing product-intent and authoring-surface conformance only
```

This decision strengthens the Product Intent and the `ContributionUnit
Authoring Surface` conformance contract. It does not select any substrate, does
not create a new surface type, does not change Git semantics, does not change
`ContributionUnit` identity, does not change `ConvergenceUnit` identity, does
not change checkpoint/convergence/promotion/publication semantics, does not
change the single-host coordination model, and does not create a new
environment-management product.

## Decision

### 1. Substrate independence is a governing product property

Ruu correctness and product semantics MUST depend on the common
`ContributionUnit Authoring Surface` contract, and MUST NOT depend on the
concrete isolation or realization mechanism:

```text
Ruu correctness and product semantics
MUST depend on
the common ContributionUnit Authoring Surface contract

and MUST NOT depend on
the concrete isolation or realization mechanism.
```

Ruu MUST NOT reject an authoring surface merely because it belongs to a
particular category of realization, provided that surface satisfies every
applicable guarantee of the contract.

No concrete mechanism becomes the canonical substrate of the product. The
linked Git worktree, the private primary working tree of an externally isolated
repository instance, and every other conforming mechanism remain replaceable
realizations below the same normative contract.

### 2. Heterogeneous realizations may coexist simultaneously

Different active `ContributionUnit`s MAY use simultaneously different conforming
realizations.

That coexistence MUST hold even when those `ContributionUnit`s belong to the
same coordination domain, to the same logical repository, to the same
`ConvergenceUnit`, to the same `LogicalInvocation` cohort, or are encountered by
the same global convergence sweep.

The presence of a conforming realization X for one `ContributionUnit` MUST NOT
impose X on any other `ContributionUnit`. Substrate selection is local to the
`ContributionUnit Authoring Surface` that actually provides the guarantees; it is
never a property of the coordination domain, the repository, the
`ConvergenceUnit`, the `LogicalInvocation`, or the sweep.

### 3. No global authoring-substrate mode

Any assumption of the following form is forbidden as a correctness or
conformance condition:

```text
all active ContributionUnits use linked worktrees
```

```text
all active ContributionUnits use externally isolated primary working trees
```

The same prohibition applies to any equivalent global formulation, including a
domain-wide, repository-wide, `ConvergenceUnit`-wide, `LogicalInvocation`-wide,
or sweep-wide authoring-substrate mode.

A closed product enumeration of substrates such as `WORKTREE`, `VM`, `SANDBOX`,
`CONTAINER`, or `MICROVM` MUST NOT be introduced. Those concepts MUST NOT become
types of the Ruu domain.

An implementation MAY have realization-specific plumbing, adapters, or
capability discovery in order to establish the common guarantees. Those details
remain below the Ruu semantic boundary and MUST NOT leak into Ruu product
semantics, identity, or conformance decisions.

### 4. Realization is not semantic identity

Authoring-surface realization is distinct from every Ruu identity and semantic:

```text
authoring-surface realization
!= ContributionUnit identity
!= ConvergenceUnit identity
!= LogicalInvocation identity
!= coordination-domain membership
!= managed checkpoint identity
!= convergence semantics
!= promotion semantics
!= publication semantics
```

Changing realization, or using a different realization for a different
`ContributionUnit`, MUST NOT create a new logical identity merely because the
substrate changed.

The existing continuation/rebind rules, authority rules, exact-state rules, and
surface-admission rules remain applicable and unchanged.

### 5. The common contract remains mandatory

This decision relaxes nothing from ADR-084. Every authoring surface MUST still
satisfy, under the existing rules, at least:

```text
mutable isolation
exact repository/base state
binding before first managed write
current managed authoring ref
required observation capability
exclusive mutation authority
frozen handoff
exact whole-surface capture
all applicable native-Git evidence/admission requirements
```

An arbitrary realization that does not satisfy the contract remains
non-conforming.

The decision therefore never means:

```text
anything called a sandbox is automatically valid
```

It means:

```text
any realization satisfying the Ruu contract is valid,
independently of what isolation mechanism produced it.
```

### 6. Examples are non-exhaustive

The following are non-normative examples of realizations:

```text
dedicated linked Git worktree/ref surface
private primary Git working tree in an externally isolated repository instance
VM-backed development environment
container-backed development environment
sandboxed development environment
microVM-backed development environment
copy-on-write or filesystem-isolated development environment
future mechanisms satisfying the same contract
```

That list:

```text
is illustrative
is non-exhaustive
does not define Ruu substrate types
does not create support tiers
```

No entry in the list, and no absence from it, changes the admissibility of a
surface that satisfies the common contract.

## Explicit conclusions

```text
Ruu is substrate-independent at the ContributionUnit Authoring Surface boundary.

Different active ContributionUnits may simultaneously use different conforming authoring-surface realizations.

No coordination-domain-wide authoring substrate is required.

No concrete isolation mechanism is part of ContributionUnit identity or convergence semantics.

Concrete realization-specific plumbing may exist below the common surface contract but must not leak into Ruu product semantics.

ADR-084's pre-edit admission, managed-ref, observation, mutation-authority, frozen-handoff, and exact-capture requirements remain unchanged.

Ruu remains standalone and zero-preflight for supported harnesses.

No VM, sandbox, container, worktree, microVM, runtime, or environment topology becomes a Ruu domain type.
```

## Alternatives considered

### Global substrate mode

Rejected. It would make `ContributionUnit`s artificially homogeneous and would
make Ruu depend on a realization mechanism, contradicting the product property
that Ruu depends only on the guarantees of the surface contract.

### Enumerate supported substrate types in the domain model

Rejected. The list would be closed, would leak infrastructure into the product
domain, and would force a Ruu change for every new isolation mechanism instead of
admitting any mechanism that satisfies the contract.

### Make realization part of ContributionUnit identity

Rejected. The logical identity of the work does not depend on its physical
environment; realization would then appear in identity, rebind, checkpoint,
convergence, and publication semantics where it has no meaning.

### Relax the common Authoring Surface contract

Rejected. Substrate independence does not mean abandoning the safety and
correctness guarantees of the common contract; heterogeneous coexistence is
admissible only through those guarantees.

## Projection obligations

This decision MUST be projected into:

```text
docs/specification/ruu-spec.md
docs/specification/external-control-plane-contract.md
docs/architecture/overview.md
docs/adr/README.md
```

and into the applicable generated ADR projections.

No accepted ADR body may be modified by this projection.
