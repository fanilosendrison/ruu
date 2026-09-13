---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Provision the repository-local convergence-unit ref before the first contribution unit"
id: "ADR-015"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "eb1bfd75e001981428bd2b9e5fb27fffadd4f2ce565a555b9dfc428d2656ba85"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-015: Provision the repository-local convergence-unit ref before the first contribution unit

- **Status:** Accepted — provisioning ownership clarified by ADR-023, terminology by ADR-025/034, authority boundary by ADR-033, brand-new repository bootstrap clarified by ADR-056; amended by ADR-061
- **Date:** 2026-09-04
- **Decision order:** 015

## Context

A contribution-unit ref/worktree must have a known repository-local parent before its first managed write. Concurrent creation of the shared convergence-unit ref also needs deterministic ownership so two provisioners do not create competing roots.

## Decision

The pre-edit contribution-unit provisioner establishes, atomically/recoverably:

```text
repository identity
→ convergence_unit_id + convergence_ref from freshly observed configured base
→ contribution_unit_id + contribution-unit ref from convergence ref
→ isolated worktree
→ external mutation-authority mechanism
→ write authorization
```

If the convergence-unit ref already exists, provisioning reuses the authoritative registered identity/ref after exact validation rather than creating a competing one.

`ruu` itself does not perform this pre-edit provisioning as a side effect.

## Rationale

Isolation cannot be retrofitted after writes have already happened, and the shared parent must be deterministic under concurrent provisioning.

## Consequences

- First managed write is forbidden before topology and mutation authority are established.
- Contribution-unit refs start from the convergence-unit ref, not directly from target/base.
- Provisioning is lazy but pre-edit.
- ADR-056 closes new-repository creation: a brand-new repository is externally authorized/provisioned and admitted only after its configured target exists at exact non-null bootstrap OID `B0`; this ADR then applies unchanged.


## Amendment by ADR-056

For a brand-new repository, this ADR does not run against an unborn/null target. The External Control Plane/Repository Provisioner first satisfies ADR-056 `RepositoryBootstrapContract` and establishes `REPOSITORY_ADMITTED` with configured target at exact `B0`. Only then does the pre-edit provisioner create/reuse the ConvergenceUnit ref from that freshly observed target and provision the first ContributionUnit. `ruu` remains outside repository creation.

## Amendment by ADR-061

Pre-edit provisioning must resolve both the repository-local ConvergenceBase and the ConvergenceUnit's immutable PromotionTarget before any attached ContributionUnit receives write authorization. Reuse of an existing ConvergenceUnit requires exact PromotionTarget equality; a different intended destination requires a distinct ConvergenceUnit rather than retargeting.

## Amendment by ADR-069

Ordinary new ContributionUnits still provision from the current ConvergenceUnit ref. A ContributionUnit created for an explicit `REVISE_EXISTING_GROUP` correction/reconciliation may instead be provisioned from the exact group/submission state authorized for that correction, while remaining bound to the same ConvergenceUnit identity. Its authored effect is reconciled forward into the live ConvergenceUnit lineage separately.

