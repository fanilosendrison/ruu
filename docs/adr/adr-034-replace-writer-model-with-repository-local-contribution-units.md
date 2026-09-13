---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Replace the Git-level writer model with repository-local contribution units"
id: "ADR-034"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "ac5b8563a70cf7a431c28497f8a4a51ad6fcce36c7d3838fdb8ca8b761a34c20"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-034: Replace the Git-level writer model with repository-local contribution units

- **Status:** Accepted — object identity/artifact semantics amended by ADR-038 core decision — current object name/lifecycle superseded by ADR-035
- **Date:** 2026-09-05
- **Decision order:** 034

## Context

The architecture originally modeled a global/logical **writer** plus a repository-local `writer_context`.

After ADR-023 and ADR-033, `ruu` no longer creates writer runtimes, determines writer liveness, or derives mutation authority from actor identity. It consumes already-existing repository-local isolated contexts plus an external mutation-access contract.

A global `writer_id` is therefore not required by any `ruu` safety, convergence, verification, promotion, recovery, or provider invariant. Keeping it in the normative model would preserve an actor identity that the engine neither needs nor has authority to interpret.

The term **editing context** was also unnecessarily narrow: the same isolation construct may be used for greenfield/from-scratch creation as well as modification, deletion, generation, migration, or refactoring of existing content.

## Decision

### 1. Repository-local isolation object (name later superseded by ADR-035)

A **contribution unit** is:

> a repository-local isolated Git context in which work may be produced before convergence.

The term is intentionally neutral about whether the repository/content existed before the work began.

A contribution unit may be used for:

```text
greenfield/from-scratch creation
adding new content
modifying existing content
deleting content
refactoring
generation/migration
other repository-local work
```

The normative identity is:

```text
contribution_unit_id
```

It is stable, opaque, repository-local, and supplied by the External Control Plane.

### 2. Global writer identity is removed from the `ruu` model

`ruu` does not require or define:

```text
writer_id
global writer identity
actor-to-context identity correlation
```

A higher-level runtime may maintain its own agent/human/script/session identity and may associate one logical activity with several contribution units across repositories, but that correlation is outside `ruu` and is not a safety or authorization primitive.

Therefore:

```text
higher-level actor identity
≠ contribution_unit_id
≠ invocation_principal
```

and no `ruu` transition may depend on proving that two repository-local contribution units belong to the same external actor.

### 3. One contribution unit belongs to exactly one repository

The previous `{writer_context, repository}` cardinality becomes intrinsic to the contribution-unit object:

```text
1 contribution_unit_id
→ exactly 1 repository_id
→ exactly 1 convergence_unit_id membership for that identity
→ logical identity independent of editing-artifact presence

while active editing is externally provisioned:
  isolated worktree/ref surfaces may exist
```

Higher-level work spanning three repositories uses three repository-local contribution units.

This does not require `ruu` to know whether those contexts were produced by the same agent, session, task, or orchestrator run.

### 4. Current Git-level terminology is renamed consistently

Normative terminology becomes:

```text
writer_context_id        → contribution_unit_id
writer context           → contribution unit
writer ref/branch        → contribution-unit ref
writer worktree          → contribution-unit worktree
writer lifecycle         → contribution-unit lifecycle
writer readiness         → no corresponding current state; ADR-037 removes separate ContributionUnit integration-readiness
writer→convergence-unit  → contribution-unit→convergence-unit
convergence-unit→writer  → convergence-unit→contribution-unit
editing-context subsystem/provisioner → External Control Plane/provisioner
```

`writer` may still exist as a concept in an external runtime, but it is not a `ruu` entity.

### 5. Mutation authority remains unchanged semantically

ADR-033 remains authoritative for transferability and exclusive mutation claims.

For an exact invocation and exact `contribution_unit_id`:

```text
external mutation-access contract
+ exclusive current-executor/operation worktree claim
+ exact topology/state guards
→ possible contribution-unit-worktree mutation
```

Actor identity does not participate in that authorization predicate.

### 6. Contribution-unit lifecycle remains distinct from producer/runtime and editing-artifact lifecycle

Under ADR-035/ADR-038, `ruu` consumes only:

```text
OPEN
CLOSED
```

These states describe whether the bounded ContributionUnit may still produce future contribution to its convergence scope. They do not model whether an external agent/process/session is alive, nor whether a local/remote branch or worktree currently exists.

`ContributionUnit` identity is therefore independent of producer identity **and** editing-artifact existence.

## Rationale

This removes an unused identity layer and makes the Git control-plane boundary match the object `ruu` actually manipulates.

The model becomes:

```text
external actor/runtime (outside Ruu)
        ↓ produces work through
repository-local contribution unit
        ↓ converges into
repository-local convergence unit
        ↓ participates in
promotion unit / target or submission flow
```

The name also handles greenfield work without implying that pre-existing content is being edited.

## Consequences

- `writer_id` disappears from the normative `ruu` model.
- `contribution_unit_id` becomes the only context identity needed at the work-production/convergence boundary.
- A contribution unit cannot span repositories.
- Cross-repository correlation, if useful, belongs to higher-level orchestration.
- Existing authority, claim, verification, append-only ref, convergence, readiness, promotion, and recovery invariants remain unchanged except for terminology/cardinality cleanup.
- Current requirements, ADR terminology, backlog labels, diagrams, and state-space audit must use the contribution-unit model.

## Rejected alternatives

- **Keep `writer_id` only for correlation inside `ruu`:** rejected because no current invariant requires that correlation and retaining an unused identity invites future authorization coupling.
- **Rename only `writer_context` but keep global writer ontology:** rejected because it preserves a distinction with no current Git-control-plane purpose.
- **Use `editing_context`:** rejected because it suggests modification of existing content and is awkward for greenfield/from-scratch work.
- **Use `authoring_context`:** viable but actor/content-oriented. ADR-035 later adopts `contribution_unit` because the object is a bounded contribution incarnation rather than a reusable context.

## Supersession / terminology effect

This ADR established the repository-local cardinality and removal of global writer identity. ADR-035 supersedes its intermediate object naming while preserving those decisions. This ADR updates the cardinality interpretation of ADR-001, ADR-002, ADR-003, ADR-004, ADR-006, ADR-008, ADR-009, ADR-011, ADR-015, ADR-019, ADR-023, ADR-024, ADR-025, ADR-027, ADR-029, ADR-030, ADR-031, and ADR-033 wherever those decisions previously used Git-level `writer` or `editing-context` terminology.

No higher-level runtime is forbidden from using the word **writer** for its own actor model; that actor identity is simply outside `ruu`.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-041

ContributionUnit authority is no longer indexed by exact invocation. The trigger is coalescible; durable External Control Plane mutation access plus current fenced-executor resource ownership defines the mutation boundary.
