---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Bind pre-commit semantic readiness by frozen mutation handoff, not validation evidence"
id: "ADR-064"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "9336efe89c24849d3821c3d3ca74809cbf61caf9d2f9864022e140d7af53f906"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-033"
    - "ADR-057"
    - "ADR-058"
    - "ADR-059"
    - "ADR-060"
  supersedes: []
  confirms: []
governs: []
---

# ADR-064 — Bind pre-commit semantic readiness by frozen mutation handoff, not validation evidence

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 064
- **Amends:** ADR-033, ADR-057, ADR-058, ADR-059, ADR-060 and the External Control Plane mutation-access contract

## Context

The agent-native development model prefers semantic validation as early as possible:

```text
edit
→ tests / lint / typecheck / build / semantic review
→ correction fixed point
→ checkpoint / commit
```

This is desirable because commit should not be the first moment when an agent discovers that its own work is broken.

ADR-057 moved development-quality execution outside `ruu`, and ADR-060 correctly removed the generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` protocol. `ruu` must therefore not re-import test/review semantics merely to prove that the Development System performed them.

At the same time, the higher-level property still matters:

> when the Development System decides that a dirty editing surface is ready to become a managed checkpoint, `ruu` must commit that exact offered state, not a later silently changed state.

ADR-033 already separates external editing authority from `ruu` mutation authority, and ADR-058/059 already make the managed checkpoint a whole-surface canonical Git tree. The missing clarification is how these two mechanisms establish the pre-commit identity boundary without reintroducing generic validation evidence.

## Decision

### 1. Semantic validation remains entirely outside `ruu`

Tests, lint, typecheck, build, code generation, semantic review and their fixed-point/retry logic remain Development System responsibilities.

`ruu` does not consume:

```text
TESTS_PASSED
REVIEW_PASSED
DevelopmentValidationEvidence
validation profile
validation logs/artifacts
```

as a generic checkpoint prerequisite.

### 2. The Development System's checkpoint decision is represented by mutation-authority handoff

While semantic authoring/validation is still active, the ContributionUnit editing surface remains:

```text
PROTECTED_EXTERNAL
```

When the Development System decides that the **current observable editing surface** may cross the checkpoint boundary, it durably relinquishes external mutation authority by publishing an appropriate transferable state:

```text
TRANSFERABLE_TO_RUU
or
TRANSFERABLE_GENERAL
```

That transition is not a claim that tests passed. It is the authority statement:

> this current editing surface may now be consumed by the Git progression domain, and no external producer retains the right to mutate it while the handoff remains current.

### 3. Transferability creates a frozen no-external-mutation interval

From the durable transferability transition until one of the following occurs:

```text
A. Ruu finishes/releases its owned checkpoint attempt
B. transferability is legitimately revoked before Ruu obtains a conflicting claim
C. recovery establishes another exact authoritative state
```

no external writer may mutate the ContributionUnit worktree.

If semantic development needs to resume before `ruu` has claimed the worktree, the External Control Plane must first revoke transferability / restore external mutation authority, then permit new writes. Any earlier semantic readiness decision is thereby stale and must be re-established by the Development System before a later handoff.

If `ruu` already holds the exclusive worktree claim, external mutation-authority reacquisition waits until that claim/effect reaches a safe release/recovery boundary.

### 4. `ruu` constructs and commits the exact frozen whole-surface candidate

After observing transferable mutation access and acquiring the exclusive worktree claim, `ruu` uses ADR-059 to construct:

```text
CheckpointCandidate =
  (repository_id,
   git_object_format,
   parent_oid=P,
   tree_oid=T)
```

from the complete observable Git-relevant editing surface.

Before materializing the commit, `ruu` revalidates under the same exclusive claim that the exact parent/surface candidate assumptions still hold. The resulting ordinary Git commit must satisfy:

```text
parent(K) = P
tree(K)   = T
```

If the candidate changes or any authority/structural guard becomes stale, the attempt does not commit the old candidate.

### 5. Exact validated-state identity is obtained by immobility, not by importing test evidence

The Development System may internally record whatever proof it needs that the current surface passed its semantic checks.

For the `ruu` boundary, the key correctness chain is instead:

```text
Development System validates/decides on current surface S
→ no further external mutation
→ durable transferability handoff
→ exclusive Ruu claim
→ ADR-059 canonical candidate T from that frozen surface
→ revalidate T/current authority
→ commit exactly T
```

Thus the state offered for commit cannot legitimately drift between the Development System's handoff decision and `ruu` materialization.

No generic test certificate is needed inside `ruu` to preserve this identity property.

### 6. Validation tools that mutate files must converge before handoff

Formatters, code generators, snapshot updaters, dependency lockfile writers, review-fix agents, or tests that intentionally mutate repository files are part of the Development System's authoring loop.

They must reach their external fixed point before transferability is established.

After handoff they are external writers and therefore may not mutate the surface until authority is legitimately reacquired.

### 7. Provider CI remains a separate later recertification layer

A provider-hosted CI system may require a commit/ref/provider submission and therefore naturally runs after a Git checkpoint/publication boundary.

This does not contradict pre-commit semantic validation.

The intended distinction is:

```text
Development System validation
→ early feedback before checkpoint when practical

provider CI
→ independent recertification / provider governance on a published exact state
```

The two layers may overlap in checks without owning the same architectural responsibility.

## Rationale

Reintroducing generic validation evidence into `ruu` would undo ADR-060 and make the Git convergence engine understand semantic development policy that belongs above it.

Ignoring exact handoff identity would create the opposite problem: tests/review could run on one dirty surface while a different surface is later committed.

The existing mutation-access boundary supplies a cleaner solution. The Development System owns **why** the surface is ready; `ruu` owns **what exact Git state** is committed. A frozen authority handoff joins the two without conflating them.

This also matches the broader agentic model:

```text
Work / semantic Evidence
→ external

checkpoint Candidate identity
→ exact Git tree constructed by Ruu from a frozen offered surface
```

The higher-level “validated candidate” need not become a duplicate core entity so long as the offered surface cannot mutate during the boundary crossing.

## Consequences

- Pre-commit tests/reviews remain encouraged and entirely external.
- Commit is not intended to be the first semantic feedback point.
- `ruu` still consumes no generic development-validation evidence.
- Transferability has a stronger explicit meaning: no external writer retains mutation authority while the handoff is current.
- Resuming semantic authoring requires legitimate mutation-authority reacquisition before any new write.
- ADR-059 canonical candidate construction plus same-claim revalidation guarantees the exact Git state that is committed.
- Validation tools that mutate repository state must finish before handoff.
- Provider CI remains independent downstream recertification/governance.

## Rejected alternatives

### Reintroduce `DevelopmentValidationEvidence(candidate_hash)` into Ruu

Rejected. It would make Git progression depend again on a generic semantic-development certificate and undo ADR-060's responsibility separation.

### Let the Development System pass a commit command after tests but allow the worktree to continue mutating

Rejected. It does not guarantee that the committed state is the state the Development System actually decided was ready.

### Have the Development System create the managed commit itself after tests

Rejected as the normative path because it would bypass the existing ADR-058/059 canonical managed-checkpoint construction and the mutation-authority/claim/recovery model. Ordinary externally created Git movement may still be observed/reconciled according to existing rules, but it is not the canonical `ruu` checkpoint path.

### Freeze by branch name or staging state

Rejected. Branch names and the caller's staged/unstaged partition are not exact candidate identity or authority under ADR-058/059.

## Amendment by ADR-069

For a work-bearing logical invocation, each frozen ContributionUnit mutation handoff is durably bound to that `invocation_id` before the invocation cohort is sealed. Partial preparation is not an accepted checkpoint cohort. After seal, physical checkpoint/integration work may proceed and recover incrementally; the convergence-demand signal remains independently coalescible.



## Clarification by ADR-079 — initial handoff is the mirror boundary

ADR-064 governs producer → Ruu handoff at checkpoint. ADR-079 makes the initial provisioning → producer handoff symmetrical: before the first managed write, provisioning retains exclusive authority over the candidate worktree, exact ref/worktree topology and observer protection are established under a native admission barrier, the current binding is durably published, and only then is authoring authority transferred to the producer. `binding CURRENT` alone is not permission for the producer to write before that handoff completes.
