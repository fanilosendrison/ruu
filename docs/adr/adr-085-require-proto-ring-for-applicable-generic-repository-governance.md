---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require proto-ring for applicable generic repository governance"
id: "ADR-085"
status: "accepted"
date: "2026-09-27"
decision_body_sha256: "db3825e393a30c75b06827b4ac773647fe351d2dc76ef170ac77407520643a0e"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-083"
  supersedes: []
  confirms: []
governs:
  - "Mandatory use of proto-ring for applicable generic repository governance"
  - "Classification boundary between generic and Ruu-specific repository governance"
  - "Immutable local adoption of the proto-ring Shared Governance Provider contract"
---

# ADR-085 — Require proto-ring for applicable generic repository governance

## Context

ADR-083 authorized using a shared governance implementation provider without
transferring repository authority.

The provider remained theoretically optional.

Keeping a competing local generic implementation reintroduces the drift that
shared governance extraction is intended to remove.

The new decision therefore makes proto-ring mandatory for generic repository
governance.

No Ruu product semantics or qualification semantics are modified.

## Decision — mandatory provider

For every repository-governance responsibility classified as generic/reusable,
Ruu MUST follow the immutably bound proto-ring Shared Governance Provider
contract.

When an applicable proto-ring mechanism exists, Ruu MUST consume it and MUST NOT
maintain a competing local implementation.

## Decision — new mechanisms

Before a new repository-governance mechanism is introduced, its responsibility
MUST be classified as Ruu-specific or generic/reusable.

```text
Ruu-specific → local
generic/reusable → proto-ring
```

## Decision — missing provider capability

The absence of a generic capability from proto-ring does not authorize a
permanent local alternative.

```text
absence from proto-ring != permission for a permanent local generic mechanism
```

A temporary exception requires a later explicit accepted governance decision
satisfying the exception conditions in the Shared Governance Provider contract.

## Decision — authority boundary

Ruu continues to own locally:

```text
Ruu product semantics
normative specifications
external control-plane authority
accepted ADRs
qualification policy
qualification evidence
manifests
lineage
retained snapshots
immutable historical artifacts
replay semantics and outcomes
repository-specific profiles and overlays
repository-specific bindings
generated Ruu artifacts
Ruu-specific validation obligations
```

## Decision — immutable binding

The Shared Governance Provider contract is bound through the local document
`docs/repository-governance/ruu-shared-governance-provider.md` to the exact
immutable proto-ring identity:

```text
fanilosendrison/proto-ring
974ca31ff12630a90da6371cc27c1f5ef0cc590e
docs/contracts/shared-governance-provider.md
```

This contract pin is distinct from the package/executable pin.

This contract pin is distinct from the Projection Integrity contract pin.

None of these existing pins is changed implicitly.

## Amendment

ADR-085 amends ADR-083 as follows:

```text
ADR-083's permission to use shared governance implementation externally remains
valid, but for generic/reusable repository governance the provider choice is no
longer optional: the applicable immutably bound proto-ring mechanism is
mandatory.
```

## Consequences

* No competing local implementation of a generic proto-ring primitive.
* New generic repository-governance machinery belongs in proto-ring.
* Ruu-specific authority remains local.
* proto-ring upgrades remain explicit and immutably pinned.
* No product or qualification change is introduced.

## Verification obligation

Before this decision is treated as satisfied, the repository must demonstrate
that:

1. the local binding references the proto-ring Shared Governance Provider
   contract at the exact published SHA;
2. `AGENTS.md` routes any addition, modification, replacement, or design of
   repository governance to the local binding;
3. existing pins that are not explicitly migrated remain unchanged;
4. no copy of the generic contract exists in Ruu; and
5. the full Repository Integrity suite and the full Ruu qualification/replay
   sequence pass.
