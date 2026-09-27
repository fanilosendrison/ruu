---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Projection Integrity binding"
---

# Ruu Projection Integrity binding

## Shared contract

Apply the canonical proto-ring Projection Integrity contract at this immutable
identity:

```text
fanilosendrison/proto-ring
ae8d05935553086b68d5d832dc9d3317328f0c89
docs/contracts/projection-integrity.md
```

Mutable provider state is not authority for this binding. The shared contract
owns generic canonical-owner, projection-mode, direct-source, currentness,
validation-ownership, synchronization, and completion rules. This profile owns
only the Ruu mappings and local extensions below.

## Local scope

Apply the shared contract whenever Ruu repository material states mechanically
derivable mutable repository state. This includes active ADR metadata,
generated indexes, active qualification registration, retained-evidence
lineage, current artifact presence, validation membership, and live engineering
work state.

Product-semantic correspondence and ordinary explanatory prose remain governed
by Ruu's specification and discovery-classification authority. Projection
validation does not create product meaning or qualification claims.

## Ruu owner mappings

Use these local bindings:

```text
docs/specification/ruu-spec.md
    → owns primary Ruu product semantics

docs/specification/external-control-plane-contract.md
    → owns its declared external authority boundary

accepted ADR frontmatter and canonical active ADR files
    → own active ADR identity, name, lifecycle, outgoing relations, governed
      scope, path, and decision-body integrity

docs/adr/index.md
    → generated projection from canonical active ADR frontmatter

docs/adr/README.md chronological history
    → mechanically validated maintained projection for ADR identity, name,
      status, path, order, and coverage
    → narrative annotations remain independently authored

repository filesystem and Git tree
    → own current maintained artifact presence and bytes

qualification/manifests/current.sha256
    → generated active-state projection from the maintained repository layout

qualification/releases/adr-080-flat/
    → immutable bounded historical snapshot for its declared release scope

qualification/lineage/lineage-v2.json
    → generated retained-lineage projection from immutable snapshot authority

qualification/state-space/ retained families and qualification/git-smoke/
    → bounded historical snapshot projections with byte-identity and lineage
      obligations

qualification/state-space/post-baseline/ registrations
    → own post-baseline qualification artifact registration and replay binding

AGENTS.md
    → owns repository authorization, qualification, and validation guardrails

tools/check-repository-integrity.py
    → owns current Repository Integrity profile membership and order

.github/workflows/qualification.yml
    → references Repository Integrity and owns CI bootstrap plus distinct replay

GitHub Issues, Project fields, and native relationships
    → own current engineering work state
```

README files remain explanatory consumers unless a more specific mapping above
assigns maintained projection responsibility.

## Active manifest

The active manifest is a strong Ruu-owned generated projection and state-binding
mechanism. Its generator discovers every maintained file outside declared local
exclusions, hashes exact bytes, sorts paths, and excludes the output itself so
one generation reaches a fixed point.

This mechanism remains Ruu-owned. It does not require another consumer to use a
whole-repository manifest and does not make the manifest product or
qualification authority.

## Immutable retained evidence

The immutable release snapshot, retained state-space and Git-smoke projections,
lineage, active snapshot-manifest copy, and permission checks remain Ruu-owned.
Their Projection Integrity obligations concern current custody, byte identity,
registration, provenance, and bounded historical scope.

Historical claim validity remains a Qualification concern. A preserved artifact
or recorded `PASS` string does not establish its original claim solely through
Projection Integrity.

Post-baseline evidence must remain outside retained lineage and use its declared
registration, continuity, artifact hashing, and replay contract.

## Qualification and evidence boundary

Ruu Qualification is distinct from Projection Integrity and Repository
Integrity. The top-level Qualification workflow requires current Repository
Integrity, then performs historical, post-baseline, and Git-smoke replay under
Ruu-owned evidence rules.

Neither proto-ring contract owns qualification membership, evidence, manifests,
lineage, snapshots, replay outcomes, or claims. Generated qualification
artifacts remain Ruu artifacts.

## Repository Integrity profile

The canonical local Repository Integrity profile includes every current
projection check required for Ruu's maintained state. It also includes the
Projection Integrity tests that guard this binding and validate every derivable
ADR-history field directly against canonical ADR frontmatter.

Generators are run explicitly before observational validation. A stale generated
artifact must make Repository Integrity non-PASS rather than being repaired into
a passing verdict.

## Engineering work state

GitHub Issue state, Project fields, and native relationships remain the sole live
owners for tracked work state. Issue prose and repository documents may
reference those objects but must not maintain current status, classification,
priority, dependency, parentage, or linked-change dashboards manually.

## Change procedure

For every new or changed Ruu projection, apply the shared contract first, then
add or update the concrete owner mapping and local generator or validator in the
same change. Keep product semantics, accepted decisions, qualification claims,
evidence, manifests, lineage, snapshots, paths, commands, and Project
coordinates local.

Do not duplicate the generic contract in this profile. Regenerate current active
artifacts, run Repository Integrity, and complete the full qualification/replay
sequence before completing a projection-affecting repository change.

## Authority boundary

This binding changes repository governance only. It does not change Ruu product
semantics, accepted ADR content, qualification claims, evidence interpretation,
immutable historical artifacts, or the authority order in `AGENTS.md`.

The separate governed-identity finding remains outside this binding. Projection
Integrity does not resolve identity or canonicalization semantics that current
Ruu authority has not accepted.
