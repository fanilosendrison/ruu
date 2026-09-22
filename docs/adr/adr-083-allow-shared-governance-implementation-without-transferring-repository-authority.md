---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Allow shared governance implementation without transferring repository authority"
id: "ADR-083"
status: "accepted"
date: "2026-09-22"
decision_body_sha256: "cc9d5b828a778dd5e5092ca70f660c19873274a7c5789f6c254a2dd9e37953d4"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-082"
  supersedes: []
  confirms: []
governs:
  - "Ownership boundary between repository authority and shared governance implementation"
  - "Use of proto-ring as a reusable governance implementation provider"
  - "Immutable pinning and local bindings for shared governance tooling"
---

# ADR-083 — Allow shared governance implementation without transferring repository authority

## Context

ADR-082 required Ruu's adopted OKF Architecture Decision Record profile to use
repository-owned validation, rendering, regression tests, and CI checks. That
boundary was appropriate while Ruu needed to establish an independently
validated migration and the reusable asset shared with other repositories was
only the generalized metadata schema.

TURNLOCK independently adopted the same OKF profile and implemented the same
class of ADR validation and rendering machinery. A cross-repository extraction
audit preserved in `fanilosendrison/proto-ring` at
`a5c42454530aa90e82caa4d6904e699450cb3359` identifies this duplicated
governance implementation while preserving the distinction between shared
governance rules and repository-specific authority. The audit is non-normative;
it is evidence for this repository-governance decision, not authority over Ruu.

Keeping equivalent reusable governance mechanisms repository-owned now creates a
different integrity risk: fixes and strengthened checks can diverge between
repositories even when the intended governance contract is the same. Ruu
therefore needs to permit a shared implementation owner without transferring
ownership of its product semantics, accepted decisions, qualification evidence,
local governance bindings, or immutable historical artifacts.

This is a repository-governance change only. It does not change Ruu product
semantics, the specification authority order, qualification claims, external
control-plane semantics, or implementation architecture.

## Discovery classification

```text
decision-required, resolved; repository-governance-only
```

## Decision

### Shared governance implementation may be external

ADR-082's requirement for repository-owned validation, rendering, regression
tests, and CI checks is amended.

Ruu MUST continue to own and govern whether a shared governance mechanism is
adopted and how it is bound locally, but the reusable implementation of that
mechanism MAY be owned outside this repository.

`fanilosendrison/proto-ring` is the initial intended shared implementation
provider for governance mechanisms demonstrated to be common to Ruu and
TURNLOCK. This decision does not define the complete scope or Product Intent of
a future Ring product.

### Repository authority remains local

Externalizing reusable implementation MUST NOT externalize Ruu authority.

Ruu continues to own:

* its normative specifications and accepted product meaning;
* its accepted ADR corpus and decision history;
* its repository-local ADR profile and local schema overlay;
* its repository-specific authority bindings and governance configuration;
* its ADR migration and preservation evidence;
* its qualification evidence, manifests, lineage, retained snapshots, and
  immutable historical artifacts;
* its generated repository projections; and
* every Ruu-specific validation obligation.

A shared implementation consumes those local authorities and bindings. It does
not replace them.

### Shared implementation owns mechanism, not repository facts

A shared governance provider MAY own reusable:

* validation and rendering engines;
* generic governance contracts;
* generic schemas whose canonical ownership has been explicitly assigned to
  that provider;
* generic regression tests for those mechanisms; and
* validation orchestration that is independent of Ruu product semantics.

It MUST NOT silently create, infer, amend, or become canonical owner of
Ruu-specific product facts, accepted decisions, local bindings, qualification
evidence, historical snapshots, or generated outputs.

Repository-specific overlays and checks remain admissible and MUST compose
without weakening the shared contract.

### Consumption must be immutable and reproducible

When Ruu consumes governance implementation from another repository, the
consumed implementation MUST be pinned to an immutable identity sufficient to
reproduce the exact validation semantics used by the repository.

Validation MUST NOT depend on fetching mutable provider state such as an
unpinned `main` branch at validation time.

An upgrade of the shared implementation is an explicit repository change. Any
upgrade that changes accepted ADR metadata semantics, lifecycle rules,
preservation boundaries, authority boundaries, qualification boundaries, or
another accepted governance contract requires an appropriate later governance
decision rather than being treated as a tooling-only update.

### Generated and qualification artifacts remain Ruu artifacts

A shared renderer MAY produce repository projections such as
`docs/adr/index.md`, but the generated file remains a Ruu repository artifact
derived from Ruu-owned canonical sources.

Ruu's active qualification manifest continues to bind the exact repository
artifacts required by the qualification contract. Shared tooling does not own
that manifest, retained lineage, release snapshots, or the evidence they bind.

The shared provider does not acquire authority merely because its implementation
produces or validates a projection.

### Existing external OKF schema authority is unchanged

This decision does not transfer canonical ownership of the generalized OKF ADR
schema currently pinned by `docs/adr/adr-profile.yaml`.

That schema remains governed by its existing pinned canonical source until a
separate explicit decision changes that ownership.

### Extraction requires parity before local implementation removal

This decision authorizes later extraction of demonstrated reusable governance
implementation into proto-ring and pinned consumption from Ruu.

Local implementation MUST NOT be removed merely because an external replacement
exists. Before replacement, the repository MUST establish that the shared
implementation preserves the accepted local governance contract, Ruu-specific
overlay behavior, migration boundaries, qualification integration, and all
other applicable local constraints.

The extraction itself MUST remain semantics-neutral with respect to Ruu product
meaning, accepted decision history, and immutable qualification evidence.

## Rationale

The repository should own its authority and evidence, not necessarily every byte
of generic machinery used to enforce them.

Separating local authority from reusable enforcement removes duplicated
maintenance while preserving Ruu's ability to bind, extend, reject, or upgrade
shared governance explicitly.

Immutable consumption prevents a shared repository from becoming mutable
ambient authority. Local profiles and overlays preserve repository autonomy,
while shared engines make generic governance fixes available to multiple
consumers without manual reimplementation.

Only governance already demonstrated as reusable is authorized for extraction.
This decision does not authorize speculative generalization of Ruu product
semantics or its qualification model.

## Consequences

* ADR-082's `repository-owned validation, rendering, regression tests, and CI
  checks` requirement now means repository-governed adoption and enforcement,
  not mandatory repository-local ownership of reusable implementation bytes.
* Ruu may consume pinned proto-ring governance tooling once parity is
  established.
* Ruu-specific profiles, overlays, decisions, qualification evidence,
  historical artifacts, generated outputs, and semantic authority remain in
  this repository.
* Shared tooling upgrades cannot silently change accepted governance or
  qualification semantics.
* The current ADR tooling remains valid until a separately validated extraction
  replaces it.
* No Ruu product invariant or qualification claim changes as a consequence of
  this decision.

## Alternatives considered

### Keep all governance implementation duplicated per repository

Rejected. It preserves local code ownership at the cost of systematic drift and
duplicated strengthening work for rules that are intentionally shared.

### Move repository authority or qualification evidence into proto-ring

Rejected. Shared implementation is not a reason to centralize product meaning,
decision history, local evidence, immutable snapshots, or repository-specific
governance facts.

### Consume mutable proto-ring `main`

Rejected. Mutable external state would become ambient validation authority and
would make historical repository validation semantics non-reproducible.

### Specify the complete Ring product before factorization

Rejected. The current need is narrower: factor governance already demonstrated
to be shared. Future Ring scope must continue to be derived from concrete
problems rather than assumed here.

## Verification obligation

Before Ruu removes any local implementation in favor of proto-ring, the
repository must demonstrate that:

1. the consumed shared implementation is pinned to an immutable identity;
2. Ruu-owned profiles, overlays, authority bindings, qualification evidence,
   historical snapshots, and generated outputs remain local;
3. the shared implementation validates the same accepted ADR corpus and local
   constraints without semantic weakening;
4. repository-specific validation can extend the shared mechanism without
   redefining its generic contract;
5. generated projections remain reproducible from Ruu-owned canonical sources;
6. active qualification generation and verification remain current;
7. validation does not consult mutable provider state; and
8. the complete repository qualification suite passes after the replacement.
