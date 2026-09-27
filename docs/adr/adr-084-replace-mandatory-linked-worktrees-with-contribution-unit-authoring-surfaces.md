---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Replace mandatory linked worktrees with ContributionUnit Authoring Surfaces"
id: "ADR-084"
status: "accepted"
date: "2026-09-27"
decision_body_sha256: "0392e8505cc13432026e5efc62c5b7694182396594bc5aa04f1e7c9f1a70ad3a"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-001"
    - "ADR-002"
    - "ADR-009"
    - "ADR-023"
    - "ADR-033"
    - "ADR-038"
    - "ADR-039"
    - "ADR-056"
    - "ADR-064"
    - "ADR-070"
    - "ADR-078"
    - "ADR-079"
    - "ADR-081"
  supersedes:
    - "ADR-073"
  confirms:
    - "ADR-058"
    - "ADR-059"
    - "ADR-071"
    - "ADR-074"
    - "ADR-075"
    - "ADR-076"
    - "ADR-077"
governs:
  - "ContributionUnit authoring-surface contract"
  - "Pre-edit managed-authoring isolation substrate"
  - "Managed authoring ref and authoring-surface binding"
  - "Authoring-surface mutation authority and frozen handoff"
  - "Exact checkpoint capture from active authoring surfaces"
  - "Supported-harness zero-preflight provisioning boundary"
---

# ADR-084 — Replace mandatory linked worktrees with ContributionUnit Authoring Surfaces

- **Status:** Accepted
- **Date:** 2026-09-27
- **Supersedes:** ADR-073 (mandatory linked-worktree substrate only)
- **Amends:** ADR-001, ADR-002, ADR-009, ADR-023, ADR-033, ADR-038, ADR-039, ADR-056, ADR-064, ADR-070, ADR-078, ADR-079, ADR-081, the consolidated specification, the External Control Plane contract, and the architecture overview
- **Confirms:** ADR-058, ADR-059, ADR-071, ADR-074, ADR-075, ADR-076, ADR-077

## Context

ADR-073 made a dedicated linked Git worktree/ref surface mandatory for v1
managed authoring:

```text
ContributionUnit
→ dedicated Git worktree/ref surface
→ external authoring
→ frozen mutation-authority handoff
→ exact whole-surface capture
→ canonical managed checkpoint
```

The rejection of arbitrary immutable ingress in ADR-073 removed a real
correctness hazard: accepting prebuilt commits, `tree + parent` tuples, or
sandbox snapshots as authoring input would let unmanaged post-hoc state become a
managed checkpoint without pre-edit admission, exact base identity, or managed
authority.

The mandatory-substrate half of that decision is now unnecessarily narrow.
Development environments increasingly provide isolation outside Ruu: a coding
harness, orchestrator, or external development system may already run each
repository instance in an isolated execution/development context with its own
private primary Git working tree. An additional linked worktree created purely
for isolation is then redundant plumbing rather than a safety property.

Ruu must also remain usable on its own. Making one concrete outer isolation
mechanism mandatory made the substrate look like a Ruu-owned environment
topology decision rather than one possible realization of a substrate-neutral
contract, and it creates pressure to depend on an external environment or
orchestration product.

The question this decision answers is therefore narrow:

> What must be true of the repository-local surface on which managed
> ContributionUnit authoring happens, independent of the mechanism that
> isolates it?

It answers nothing about semantic authority, native observation,
mutation-authority mechanics, checkpoint capture, promotion, publication, or
qualification, all of which remain as already accepted.

## Discovery classification

```text
decision-required, resolved; authoring-isolation substrate contract only
```

This decision changes the authoring-isolation substrate contract. It does not
change product intent, semantic authority, checkpoint mechanics, promotion,
publication, qualification evidence, or repository governance.

## Decision

### 1. `ContributionUnit Authoring Surface` is the canonical contract

A **`ContributionUnit Authoring Surface`** is the repository-local mutable Git
authoring surface bound to one active `ContributionUnit` for managed authoring
before frozen handoff/checkpoint progression.

It is:

```text
repository-local
mutable
Git-authoring
bound to exactly one active ContributionUnit
subject to the existing Ruu managed-ref binding, observation,
mutation-authority, frozen-handoff, and exact-capture rules
```

It is not:

```text
the ContributionUnit identity
necessarily a linked Git worktree created by `git worktree add`
an artifact accepted from outside the managed Ruu model
an authority token
```

Ruu does not know and does not need to own the outer mechanism that isolates the
surface. VM, container, sandbox, process-isolation, filesystem-isolation, and
comparable outer environments remain outside the Ruu model.

### 2. Ruu remains standalone and independent

Ruu MUST remain usable on its own and MUST NOT depend on another orchestration
product to function. No external management product, domain model, identity
model, or provisioning requirement may become a precondition of Ruu
correctness.

A Ruu distribution MUST always be able to satisfy its own contract for its
supported coding harnesses through the established External Control Plane
boundary. That boundary remains an architectural role, not a second required
product.

Ruu remains repository-local at the `ContributionUnit` level. Repository
participation remains lazy and dynamic: a producer does not need to predict
every repository it will touch before authoring. Ruu does not acquire a
complete-development-workspace requirement, and no ambient model of "all
repositories that might be involved" becomes a precondition.

### 3. Required guarantees of a conforming surface

#### 3.1 Mutable isolation

Two simultaneously mutable ContributionUnits MUST NOT share the same mutable
authoring surface. In particular they MUST NOT share, as concurrent writing
state:

```text
the same mutable working directory
the same mutable index
the same mutable authoring-state filesystem sufficient to create
overwrite races before Git convergence
```

They MAY address the same logical repository, the same `ConvergenceUnit`, the
same logical paths, and the same logical files. Reconciliation remains
posterior and goes through the ordinary Git/Ruu semantics.

The mechanism that creates the isolation is not normative.

#### 3.2 Exact repository/base state

Before the first managed write, the surface MUST be established from the exact
Git state authorized by existing Ruu rules. Provisioning MUST be able to
establish or revalidate at least:

```text
repository identity
ContributionUnit identity
ConvergenceUnit identity
immutable PromotionTarget
current managed authoring ref
exact authoring base / expected prior authoritative state
exact HEAD/ref OID relationship
surface binding/topology required for this realization
```

Generalizing the substrate MUST NOT authorize adoption of arbitrary ambient
filesystem state. A newly admitted surface MUST NOT contain mutable state
foreign to the ContributionUnit that would silently become part of the
whole-surface checkpoint. For a continuation or reconstruction of an existing
ContributionUnit, the preserved or reconstructed state MUST correspond to the
state Ruu authorizes for that continuation.

#### 3.3 Binding before first write

Before the first managed write:

```text
ContributionUnit identity
+ repository binding
+ ConvergenceUnit binding
+ managed authoring ref
+ authoring-surface binding
+ required native observation capability
+ mutation-authority handoff
```

MUST be established under the existing rules. The later `ruu`
checkpoint/convergence invocation MUST NOT create this isolation retroactively
after code has already been modified. ADR-023 phase separation remains
normative.

#### 3.4 Managed authoring ref remains mandatory

Ruu remains Git-based. Every active `ContributionUnit Authoring Surface` MUST
expose the current managed authoring ref required by the existing architecture.

The following remain unchanged:

```text
current managed binding
binding generation
managed-ref disposition semantics
native reflog/evidence requirements where applicable
ManagedRefProtectionFilter
RefAdmissionBarrier
pre-linearization observation requirements
exact ref/OID revalidation
REBIND / terminal disposition semantics
```

Removing the mandatory linked worktree removes none of the
ADR-071/074/075/076/077/079 managed-ref guarantees.

#### 3.5 Authoring-surface mutation authority remains mandatory

The surface remains subject to exclusive mutation authority. While the External
Control Plane or producer holds mutation authority, Ruu MUST NOT mutate the
surface.

At the handoff:

```text
external mutation authority relinquished
+ frozen handoff current
+ Ruu authoring-surface mutation claim acquired
+ exact state revalidated
→ Ruu may perform the authorized mutation/capture operation
```

The universal term is `ContributionUnit authoring-surface mutation claim`; a
compact internal pseudo-structure uses `authoring_surface_claim`.
`worktree_claim` is no longer the general term. Where a realization actually
uses a linked Git worktree, the claim naturally protects that concrete
worktree.

#### 3.6 Frozen handoff remains mandatory

ADR-064 remains semantically valid, now formulated on the
`ContributionUnit Authoring Surface`. Once a surface is offered as transferable,
no external writer may continue mutating it until legitimate
revocation/reacquisition or release/recovery of the applicable Ruu authority.
This property remains independent of tests and reviews.

#### 3.7 Exact whole-surface capture remains mandatory

ADR-058 and ADR-059 remain normative. Changing the substrate does not make Ruu
a consumer of arbitrary artifacts.

From a dirty surface offered at handoff, Ruu MUST still derive the exact
candidate tree representing the whole managed authoring surface under the
existing rules. From a clean surface with an exact current native commit, Ruu
MAY still adopt that commit at frozen handoff under the existing guards.

The managed event remains:

```text
frozen clean-tip adoption
```

or:

```text
frozen dirty-surface checkpoint adoption
```

and never the mere prior existence of a commit.

### 4. Conforming realizations

Both of the following are conforming realizations of the surface, after
ordinary Ruu pre-edit admission:

```text
dedicated linked Git worktree/ref surface
```

```text
private primary working tree of an already externally isolated repository instance
```

For the second case:

```text
external development environment already provides an isolated
execution/development context
→ repository instance has a private primary Git working tree
→ Ruu pre-edit integration establishes the ContributionUnit identity,
  managed authoring ref, exact bindings, observer coverage,
  RefAdmissionBarrier admission, and mutation authority
→ that primary Git working tree becomes the ContributionUnit Authoring Surface
→ no additional linked Git worktree is required merely for isolation
```

Where no external isolation exists, a dedicated linked Git worktree/ref remains
a conforming Ruu-supplied realization.

The specific outer technology is deliberately not named or selected. Ruu
selects and owns no VM, container, sandbox, runtime, or process topology.

### 5. ADR-073 is superseded only on the mandatory substrate

ADR-073 is superseded.

Its rejection of arbitrary immutable ingress remains correct and is preserved.
What changes is only:

```text
safe pre-edit managed Git authoring
does not require
a dedicated linked Git worktree as the isolation mechanism
```

ADR-001, ADR-002, ADR-009, ADR-023, ADR-033, ADR-038, ADR-039, ADR-056,
ADR-064, ADR-070, ADR-078, ADR-079, and ADR-081 are amended only where they
assume a linked worktree as the universal authoring surface. ADR-058, ADR-059,
ADR-071, ADR-074, ADR-075, ADR-076, and ADR-077 are confirmed in full.

### 6. Still forbidden

This decision does not authorize:

```text
Ruu accepts arbitrary external commits
Ruu accepts arbitrary tree + parent tuples
Ruu accepts arbitrary filesystem snapshots
Ruu accepts opaque sandbox outputs after authoring
Ruu may register a ContributionUnit after unmanaged edits already happened
```

A development system that uses another isolation mechanism MUST still have a
conforming `ContributionUnit Authoring Surface` admitted before the first
managed write.

### 7. No performance requirement

This decision introduces no provisioning threshold, maximum time, cost target,
"sufficiently fast" requirement, or any other performance rule. It concerns
correctness guarantees and the removal of the linked worktree as the sole
mandatory isolation substrate.

## Explicit conclusions

```text
ADR-073 is superseded.

Dedicated linked Git worktrees remain a conforming authoring realization but
are no longer the mandatory authoring isolation substrate.

Every actively authored ContributionUnit still requires a conforming
ContributionUnit Authoring Surface before first managed write.

The surface remains a mutable managed Git authoring surface with a current
managed authoring ref and the existing Ruu binding/observation/authority/handoff
requirements.

A private primary working tree of an already isolated repository instance may
serve as the ContributionUnit Authoring Surface after normal Ruu pre-edit
admission; an extra linked worktree is not required solely for isolation.

Arbitrary post-hoc commit/tree/snapshot ingress remains unsupported.

Ruu remains standalone and zero-preflight for supported harnesses.

The External Control Plane remains a role, not a required external product.

No outer sandbox/VM/container/runtime topology is selected or owned by Ruu.

Repository participation remains dynamically provisioned repository-by-repository;
Ruu does not acquire a complete-workspace requirement.
```

## Rationale

The correctness properties Ruu needs are properties of the surface, not of the
command that created it: mutable isolation, exact base identity, a current
managed authoring ref, pre-write admission, exclusive mutation authority,
freezeable handoff, and exact whole-surface capture.

Naming the substrate instead of the contract forced Ruu to own or require an
outer topology it does not need, and made an already-isolated repository
instance pay for a second redundant checkout. Conversely, dropping the
mandatory-substrate requirement without restating those properties would risk
losing the isolation and admission guarantees ADR-073 existed to protect.

This decision keeps the contract and removes only the unnecessary mechanism.

## Consequences

- `ContributionUnit Authoring Surface` becomes the canonical substrate-neutral term.
- Dedicated linked Git worktrees remain supported and conforming.
- An already externally isolated repository instance may use its private primary
  working tree as the surface after ordinary Ruu admission.
- Managed refs, admission barriers, observation coverage, mutation authority,
  frozen handoff, and whole-surface capture are unchanged.
- Arbitrary prebuilt commit/tree/snapshot ingress remains unsupported.
- No external management product, domain model, or dependency is imported into Ruu.
- Ruu remains standalone and zero-preflight for supported harnesses.
- No outer isolation technology is selected or qualified by this decision; a
  future concrete implementation MUST prove that it satisfies the contract.
- Historical accepted ADR bodies remain unchanged; the new contract is projected
  through the active specification, the External Control Plane contract, and the
  architecture documents.

## Alternatives considered

### Keep the mandatory linked worktree

Rejected. It makes Ruu own an outer isolation topology it does not need, and it
forces an already-isolated repository instance to create a redundant second
checkout for isolation alone.

### Accept arbitrary commits, trees, or snapshots as authoring input

Rejected. It would let unmanaged post-hoc state become a managed checkpoint
without pre-edit admission, exact base identity, or managed authority.

### Make Ruu depend on an external managed-development product

Rejected. Ruu MUST remain standalone. An external development system may satisfy
the Ruu contract, but a Ruu distribution must always be able to satisfy it
itself for its supported harnesses.

### Define a concrete authoring-surface binding schema

Rejected as premature. The exact locator/binding representation is an
implementation architecture not decided here. The normative requirement is only
that the current exact surface can be identified and revalidated sufficiently
for the applicable Ruu guards.

### Introduce provisioning or performance thresholds

Rejected. Performance is out of scope; only correctness guarantees and substrate
neutrality are decided.

## Projection obligations

Where the consolidated specification, the External Control Plane contract, or
the architecture documents referred universally to a worktree as the authoring
surface, the substrate-neutral `ContributionUnit Authoring Surface` now
applies. Native Git worktree behavior, worktree-backed realizations, and
historical accepted ADR wording remain valid and unchanged.
