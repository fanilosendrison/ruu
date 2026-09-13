---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Preserve native Git equivalence and whole-surface checkpoint intent"
id: "ADR-058"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "5e26101b792c343e45cd58ed07af09ec569804d8f227bbcd21f00923fd73d5ed"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-058 — Preserve native Git equivalence and whole-surface checkpoint intent

- **Status:** Accepted
- **Date:** 2026-09-06
- **Decision order:** 058

## Context

ADR-057 clarifies that `ruu` is a state-dependent governed super-Git progression command. The next checkpoint-design question (30.27) asks what exact dirty ContributionUnit editing state is proposed when a Development System, agent, user, or orchestrator asks `ruu` to cross a commit/checkpoint boundary.

Two architectural ambiguities must be removed before the remaining low-level snapshot rules are designed.

First, `ruu` must not create a proprietary Git dialect. A human, coding agent, IDE, provider, hook, or ordinary Git script must be able to inspect the repository after a successful `ruu` operation using normal Git semantics. Managed metadata may govern, attest, recover, or reject later progression, but it must not redefine the meaning of Git commits, trees, refs, index state, or worktree state.

Second, the Development System has no real use case in which it declares one ContributionUnit editing surface ready for checkpoint while intending only an implicit subset of that surface to become the managed checkpoint. Treating the incidental current Git index/staging selection as checkpoint intent would therefore introduce an unnecessary hidden API and could make the committed state differ from the state the Development System considered complete and validated.

## Decision

### 1. Native-Git equivalence is a global invariant

Every successful `ruu` Git mutation MUST leave the affected repository in an ordinary Git state whose Git-observable result is representable by native Git objects and semantics.

At minimum:

```text
commits are ordinary Git commits
trees/blobs/gitlinks are ordinary Git objects
refs are ordinary Git refs with ordinary OID meaning
the real index is left in an ordinary coherent Git state
worktrees are ordinary Git worktrees
Git ancestry retains ordinary Git meaning
```

A user or tool that knows Git but knows nothing about `ruu` MUST be able to inspect the resulting Git state using ordinary commands such as:

```text
git status
git log
git show
git diff
git branch
git merge-base
git cat-file
```

and may subsequently perform ordinary Git operations without requiring `ruu` merely to make Git function.

`ruu` MAY maintain side metadata such as CoordinationStore records, evidence, claims, recovery anchors, internal refs, PromotionUnits, or ContributionUnit records. Such metadata is an **overlay of governance/recovery**, not a replacement Git object model.

### 2. Native operability does not imply managed authorization

Ordinary Git mutations performed manually or by external tools remain technically possible.

That compatibility does not mean every such mutation is authorized managed progression. A later `ruu` sweep may classify externally produced movement through the already-defined exact observation/adoption, drift, unknown/inconsistent, reconciliation, or policy paths.

Therefore:

```text
native Git compatibility
!=
permission to bypass managed governance
```

The architecture protects governed progression by observation, exact-state binding, claims/CAS, policy, evidence, and recovery rules rather than by making the repository unusable without `ruu`.

### 3. Checkpoint invocation has whole-editing-surface intent

For checkpoint collection of one transferable dirty ContributionUnit, there is no partial-checkpoint selection semantics in v1.

Conceptually, the request means:

> **the complete current Git-relevant state of this ContributionUnit editing surface is the state the Development System asks `ruu` to checkpoint.**

The caller does not provide an include/exclude path list, partial-commit selection, or staged-only mode as managed checkpoint intent.

### 4. Existing staging is non-authoritative for checkpoint membership

The current real Git index MAY have been used by a human/agent during development, but its staged/unstaged partition does not select managed checkpoint membership.

In particular, `ruu` MUST NOT interpret incidental partial staging as an implicit request to commit only that staged subset.

This decision does not make the index semantically irrelevant to Git integrity. Structural index states such as unresolved/unmerged entries may still block canonical checkpoint construction under the remaining 30.27 rules.

### 5. Canonical construction may use temporary Git mechanics but must normalize the real surface

`ruu` MAY use a temporary index, temporary worktree, plumbing commands, or equivalent native Git mechanics to construct/verify the canonical checkpoint candidate without treating the caller's current staging selection as authority.

A successful checkpoint MUST materialize an ordinary Git commit and leave the affected real editing surface/index in a coherent native-Git state corresponding to the committed result, except for state explicitly outside the eventual checkpoint-membership contract (for example ignored paths if that remains the applicable rule).

No private index format or `ruu`-only interpretation may be required to understand the post-success repository.

### 6. 30.27 remains open only for canonical snapshot details

ADR-058 resolves these parts of 30.27:

```text
partial checkpoint selection: NO in v1
staging as membership authority: NO
whole editing-surface checkpoint intent: YES
native-Git postcondition/equivalence: REQUIRED
```

30.27 remains open for the exact mechanical definition of the canonical Git-relevant snapshot, including at least:

```text
untracked non-ignored membership
ignored-path treatment
intent-to-add structural handling
unmerged/conflict index handling
submodule / dirty-submodule handling
symlink and Git file-mode normalization details
empty/no-op checkpoint behavior
exact pre-commit candidate identity/fingerprint
```

External `DevelopmentValidationEvidence` remains a separate 30.28 binding contract. Its candidate reference must eventually bind to whatever exact canonical candidate identity 30.27 defines.

## Consequences

- `ruu` remains removable from the *interpretation* path: repositories do not become opaque or proprietary merely because it managed them.
- Humans, agents, IDEs, providers, and Git tooling retain native observability and ordinary Git operability.
- Managed guarantees are enforced by the governance overlay rather than by altering Git semantics.
- The checkpoint API loses staged-only/partial/path-selection modes and their combinatorial state.
- External validation cannot accidentally attest the complete editing surface while `ruu` silently commits only an incidental staged subset.
- The remaining 30.27 design can focus on canonical snapshot construction and identity rather than user-intent selection.
## Current normative reading after ADR-059

ADR-059 closes the canonical details that this ADR intentionally left open. Whole-surface intent and staging non-authority from ADR-058 remain unchanged; canonical membership/construction/identity now follow ADR-059.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-064

Whole-surface checkpoint intent is now explicitly coupled to the frozen transferability boundary. The Development System may run all semantic validation before checkpoint, but after it durably offers the surface for Git progression no external writer may mutate it until legitimate authority reacquisition or safe release/recovery. This prevents the native whole-surface commit from drifting away from the surface the Development System actually offered.
