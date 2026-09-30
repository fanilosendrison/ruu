---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Shared Governance Provider binding"
shared_governance_provider:
  mandatory: true
  authority_adr:
    id: "ADR-085"
  contract:
    repository: "fanilosendrison/proto-ring"
    commit: "974ca31ff12630a90da6371cc27c1f5ef0cc590e"
    path: "docs/contracts/shared-governance-provider.md"
---

# Ruu Shared Governance Provider binding

The `shared_governance_provider` frontmatter is the machine-readable local
projection of the accepted authority identified there. The prose below remains
human-readable guidance and does not replace that authority.

## Shared contract

Apply the canonical proto-ring Shared Governance Provider contract at this
immutable identity:

```text
fanilosendrison/proto-ring
974ca31ff12630a90da6371cc27c1f5ef0cc590e
docs/contracts/shared-governance-provider.md
```

Ruu adopts the canonical proto-ring Shared Governance Provider contract at the
immutable identity above.

Mutable proto-ring state is not authority for this binding.

## Binding effect

For generic/reusable repository-governance responsibilities, Ruu uses proto-ring
as the mandatory provider.

An applicable proto-ring mechanism must not be replaced, copied, forked, or
reimplemented locally.

## Ruu authority remains local

Ruu continues to own locally:

```text
product semantics
normative specifications
external control-plane authority
accepted decisions
qualification policy and evidence
manifests
lineage
retained snapshots
immutable historical artifacts
replay semantics and outcomes
repository-specific profiles and overlays
repository-specific mappings and bindings
generated Ruu artifacts
Ruu-specific validation obligations
repository coordinates and work-management configuration
```

## Existing proto-ring bindings

Projection Integrity retains its own contract pin in
`docs/repository-governance/ruu-projection-integrity.md`.

Exact Evidence Binding retains its own contract pin in
`docs/repository-governance/ruu-exact-evidence-binding.md`.

Governance Authority has its own immutable contract-authority pin in
`ruu-governance-authority.md`.

`requirements.txt` retains its own executable-provider pin. The Governance
Authority contract pin and this executable-provider pin remain independent.
Neither pin upgrades or determines the other.

Repository Integrity and the Git whitespace mechanism continue to use the
existing package pin.

The Shared Governance Provider contract upgrades none of those pins.

Each identity remains governed separately.

## New repository-governance mechanisms

Classify each new or changed repository-governance responsibility using the
shared contract:

```text
Ruu-specific → local
generic/reusable → proto-ring
```

## Immutable binding

This binding is the Ruu contract-authority pin for the Shared Governance
Provider contract.

It identifies only the governance contract adopted by Ruu.

Changing this immutable proto-ring binding is an explicit Ruu repository change.

## Authority boundary

Using proto-ring as mandatory provider for generic governance does not make
proto-ring authoritative over Ruu.

This binding changes repository governance only. It does not change Ruu product
semantics, accepted ADR content, qualification claims, evidence interpretation,
immutable historical artifacts, or the authority order in `AGENTS.md`.
