---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Separate pre-edit contribution-unit provisioning from `ruu`"
id: "ADR-023"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "0453aa509f60f1725dac1c3fd4c71084eae0dead4788d82c0107d992dc199cda"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-023: Separate pre-edit contribution-unit provisioning from `ruu`

- **Status:** Accepted — terminology/lifecycle clarified by ADR-034/ADR-035/ADR-038; external boundary consolidated by ADR-039; brand-new repository bootstrap clarified by ADR-056; amended by ADR-061, ADR-078 and ADR-079
- **Date:** 2026-09-04
- **Decision order:** 023

## Context

Safe concurrent work requires repository/contribution-unit/worktree topology to exist before the first managed write. `ruu`, however, is explicitly invoked later to advance already-existing managed Git state.

Combining these responsibilities would make convergence responsible for creating the very isolation that should already have protected earlier writes.

## Decision

The **External Control Plane**, typically through a pre-edit contribution-unit provisioner, owns lazy establishment of:

```text
repository registration/reactivation
convergence-unit identity/ref
contribution_unit_id
contribution-unit ref
isolated worktree
external mutation-authority mechanism
write authorization
authoritative contribution-unit lifecycle declaration (`OPEN | CLOSED`)
```

It may be triggered by an agent, orchestrator, script, `/go`, or another runtime when new repository-local work is about to begin.

`ruu` consumes these existing contribution units; it does not create missing contribution units/worktrees as a convergence side effect.

ADR-033 assigns external producer/runtime mutation rights, stop/crash/resume semantics, and safe transferability to the External Control Plane boundary. ADR-035/ADR-038 assign authoritative `OPEN | CLOSED` lifecycle declaration to the same boundary; `ruu` consumes rather than infers it. ADR-038 also makes later branch/worktree creation/deletion a user/agent/External-Control-Plane tooling concern rather than a convergence cleanup responsibility.

## Rationale

Pre-edit safety and post-edit convergence are different lifecycle phases and should have a narrow explicit interface rather than circular ownership.

## Consequences

- `/go` is not required for Git safety; any compatible producer can request provisioning.
- Provisioning can happen lazily when a new repository is first needed.
- Missing editing topology blocks only operations that actually require that editing surface. Already-created exact checkpoints may still converge from their OIDs without the original branch/worktree under ADR-038.
- ADR-056 closes completely new repository creation: the External Control Plane authorizes it, a Repository Provisioner creates/reconciles it, and ordinary ContributionUnit provisioning starts only after exact `B0` bootstrap admission.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-056

Repository creation is a distinct precondition to the provisioning described here. An agent/session may request a new repository, but the External Control Plane resolves RepositoryCreationPolicy and a Repository Provisioner establishes/adopts the repository. V1 requires a real exact configured-target bootstrap commit `B0` and `REPOSITORY_ADMITTED` before this ADR creates the first ConvergenceUnit/ContributionUnit/worktree. Local repository creation and provider attachment may be decoupled; provider-sensitive operations wait for any required provider binding.

## Amendment by ADR-061

The External Control Plane/pre-edit provisioner additionally owns resolution and durable binding of each ConvergenceUnit's immutable PromotionTarget before first managed write. This remains pre-edit topology, not a `ruu` side effect or a late `merge-main` command.

## Amendment by ADR-069

Pre-edit provisioning remains external. For group-bound correction/reconciliation work, the provisioner may seed the new ContributionUnit from the exact authorized PromotionGroup/submission state rather than only the current live ConvergenceUnit tip. `ruu` still does not create the editing surface.



## Amendment by ADR-074

For v1 managed authoring, the pre-edit provisioning contract additionally ensures that the currently bound managed authoring ref has a native Git reflog before first managed write. This is causal-evidence infrastructure for later native binding-disposition resolution, not a new ContributionUnit identity. ADR-075 further requires the selected native-ref backend/adapter to satisfy the pre-linearization managed-binding observation capability contract before the surface is admitted for live authoring. The provisioner does not declare the capability by fiat; the Git/native-ref layer must establish it. A later `ruu` invocation may repair a missing reflog only when current exact state is coherent and no unresolved historical transition depends on the missing evidence.


## Amendment by ADR-078

The separation in this ADR is a **lifecycle/authority boundary between pre-edit provisioning and the later convergence invocation**. It MUST NOT be interpreted as requiring a second user-installed product or an explicit user-facing provisioning command.

For supported coding harnesses, a Ruu distribution MAY supply the harness integration/provisioner implementation that automatically establishes the required ContributionUnit/ref/worktree/observer/binding state before first managed write. The later `ruu` invocation still consumes already-managed work and MUST NOT retroactively create missing isolation as a checkpoint side effect. Semantic creation/grouping/lifecycle/readiness authority remains with the External Control Plane role; packaging the role's adapter with Ruu does not authorize the convergence engine to infer those semantics.

## Amendment by ADR-079

Pre-edit provisioning now has an explicit race-safe admission boundary. Creating the candidate branch/worktree does not yet create a current managed binding and does not authorize producer writes. The provisioner first establishes conservative observer protection, acquires an exact native `RefAdmissionBarrier`, revalidates the candidate worktree/ref topology while retaining exclusive pre-handoff mutation authority, commits the authoritative current binding while the barrier is held, releases the barrier, and only then hands authoring authority to the producer. This remains automatic supported-harness plumbing under ADR-078 and does not move semantic authority into the convergence engine.
