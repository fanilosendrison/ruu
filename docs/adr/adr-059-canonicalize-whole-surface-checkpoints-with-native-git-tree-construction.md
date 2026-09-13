---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Canonicalize whole-surface checkpoints with native Git tree construction"
id: "ADR-059"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "5f96eb34821be7e75cf129c525aba2c93c55e09bfbde5a4b7c2e5e78ab75f100"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-059 — Canonicalize whole-surface checkpoints with native Git tree construction

- **Status:** Accepted
- **Date:** 2026-09-06
- **Decision order:** 059

## Context

ADR-057 moves semantic development validation outside `ruu`. ADR-058 then fixes two checkpoint-level principles: checkpoint intent covers the whole transferable ContributionUnit editing surface, not an implicit partial selection, and the caller's current staged/unstaged partition is not checkpoint-membership authority.

Backlog 30.27 therefore reduces to one Git-level question: given an exclusively claimed dirty ContributionUnit editing surface and its exact authoritative parent checkpoint `P`, what exact pre-commit Git candidate is being proposed, how is it constructed deterministically, and which Git edge conditions make that construction invalid or a no-op?

The solution must preserve ADR-058 native-Git equivalence. `ruu` must not invent a second filesystem-to-tree representation, must not require a proprietary index format, and must not silently omit state merely because a human or agent did not stage it.

## Decision

### 1. The canonical candidate is a native Git tree derived from the exact parent plus the whole observable editing surface

For one dirty transferable ContributionUnit under exclusive mutation authority, `ruu` constructs the checkpoint candidate from:

```text
exact authoritative parent checkpoint P
+ complete observable Git-relevant editing surface
→ canonical native Git tree T
```

The normative construction is semantically equivalent to:

```text
temporary index := exact tree of P
apply the complete current editing surface using native whole-tree Git add semantics
T := git write-tree(temporary index)
```

A concrete implementation may use `GIT_INDEX_FILE`, a temporary worktree/index, plumbing commands, or an equivalent native Git mechanism, but the caller's real index is never checkpoint-membership authority.

The construction must be deterministic with respect to the Git semantics/configuration that govern the repository at that exact observation. Any non-repeatable filter/configuration behavior that yields a different re-snapshot is ordinary exact-state drift: previous validation evidence is stale and no checkpoint is adopted.

### 2. Tracked modifications/deletions and non-ignored untracked paths are included

The whole-surface candidate includes:

```text
tracked file modification          INCLUDE
tracked file deletion              INCLUDE
tracked path matched by ignore     INCLUDE according to normal tracked-file Git semantics
untracked non-ignored path         INCLUDE
```

A new non-ignored file does not require a prior `git add` by the Development System, agent, or human to become part of checkpoint intent.

### 3. Ignored untracked paths are excluded

An untracked path ignored by the current applicable native Git ignore rules is not part of the candidate.

`ruu` does not invent semantic classifications such as "test artifact", "debug output", or "temporary generator output". If a non-ignored path remains in the transferable editing surface, it is part of the checkpoint subject. Cleanup/classification before transfer belongs to the Development System under ADR-057.

A change to ignore configuration is itself ordinary repository state. Native Git rules at canonical snapshot time determine whether then-untracked paths are included.

### 4. Intent-to-add and caller staging are normalized away as selection signals

`intent-to-add`, staged-only state, unstaged state, and partial staging do not select membership.

The temporary canonical index is reconstructed from `P` and the whole observable editing surface, so incidental real-index versions cannot cause `ruu` to checkpoint an intermediate staged subset instead of the final editing-surface state.

The real index remains relevant only as part of Git structural integrity and post-success normalization, not as a path-selection API.

### 5. Unmerged/in-progress Git state blocks ordinary checkpoint collection

If the repository/worktree is in a structural Git state whose meaning cannot safely be represented as one ordinary single-parent checkpoint over `P`, ordinary checkpoint collection fails closed.

This includes at least:

```text
unmerged index entries
unresolved merge conflict state
in-progress merge whose parent semantics are not the ordinary checkpoint contract
in-progress cherry-pick/rebase/revert or equivalent sequencer state
unknown/inconsistent structural Git operation state
```

`ruu` does not silently turn an unfinished native Git operation into a normal managed checkpoint. The operation must first be completed/aborted/reconciled through the applicable native Git/recovery path, after which the resulting state may be re-observed and checkpointed normally.

### 6. Submodules use native gitlink semantics; dirty/unknown submodule state blocks

A parent repository can represent a submodule only by its exact gitlink commit OID.

Therefore:

```text
clean, exactly observable submodule at commit S
→ candidate tree may contain gitlink(S)

submodule with uncommitted tracked/untracked state
→ BLOCK ordinary parent checkpoint

submodule state required for the candidate but unknown/unobservable
→ BLOCK fail closed
```

If the Development System intentionally changes the contents of the submodule repository, that repository's authoring/checkpoint progression must be represented by its own repository-local managed work. The parent may then checkpoint the exact resulting gitlink OID.

### 7. Symlinks, executable bits, Git filters, EOL normalization, LFS pointers, and other representable details use native Git semantics

`ruu` defines no private normalization layer.

The canonical tree is whatever ordinary Git object construction produces from the exact editing surface under the applicable repository Git semantics. This naturally captures ordinary Git tree entry modes, symlink targets, blob content, gitlinks, and repository-configured clean/filter behavior.

If those mechanics cannot be re-observed deterministically enough to reproduce the same exact tree, exact-state validation fails rather than being approximated.

### 8. V1 checkpoint collection requires a fully observable editing surface

A checkpointable ContributionUnit editing surface must allow `ruu` to distinguish absence-as-deletion from absence caused by sparse materialization or equivalent hidden-worktree semantics.

In v1, sparse-checkout/sparse-index/`skip-worktree` or equivalent conditions that prevent complete observation of the Git-relevant surface make ordinary checkpoint collection non-checkpointable until full observability is restored.

This does not prohibit humans or agents from using sparse Git generally. It only prevents `ruu` from guessing checkpoint membership from an incomplete editing surface.

### 9. Tree equality with the parent is a no-op, not an empty managed commit

After canonical construction:

```text
T == tree(P)
→ NOOP checkpoint progression
→ do not manufacture an empty managed commit
```

This includes cases where filesystem activity ultimately reproduces the exact parent tree after native Git normalization.

Where `ruu` has accepted checkpoint ownership of the surface, it may normalize the real index/worktree bookkeeping into a coherent native-Git state consistent with the unchanged parent, but it does not create a content-empty checkpoint solely to record invocation.

### 10. Exact pre-commit checkpoint-candidate identity is repository + object format + parent OID + tree OID

The Git-state identity of a checkpoint candidate is:

```text
CheckpointCandidateIdentity = {
    repository_id,
    git_object_format,
    parent_oid,
    tree_oid
}
```

A canonical fingerprint is a versioned domain-separated hash over that tuple, for example:

```text
HASH(
  "Ruu/checkpoint-candidate/v1",
  repository_id,
  git_object_format,
  parent_oid,
  tree_oid
)
```

The exact serialization/hash encoding is an implementation-level wire-format detail so long as it is canonical, versioned, collision-safe for the supported Git object formats, and round-trips the same semantic tuple.

`ContributionUnit_id` is **not** part of the Git-state identity. It is attribution/governance metadata that records which authorized ContributionUnit boundary produced the candidate. Two observations in the same repository with the same exact parent and tree denote the same Git candidate state even if reached through different attribution metadata.

Tests, development-gate profile, validation context, evidence identity, commit message, author/committer, and timestamps are also not part of checkpoint-candidate identity. 30.28 separately binds `DevelopmentValidationEvidence` to this exact candidate identity plus the applicable validation profile/context.

### 11. Commit materialization must preserve the exact candidate tree and parent

After any policy-required current exact `DevelopmentValidationEvidence` has been accepted for the candidate, the managed checkpoint commit `K` must satisfy:

```text
tree(K)   == T
parent(K) == P
```

Commit metadata remains ordinary Git metadata and determines `K`'s final commit OID in the normal Git way.

After successful materialization, the real ContributionUnit editing surface/index must be left in coherent native-Git state corresponding to the committed result under ADR-058.

## Consequences

- Backlog **30.27 is closed**.
- Checkpoint membership no longer depends on staged/unstaged state, pathspec selection, or a caller-side `git add` ritual.
- Non-ignored work left in the transferable editing surface is intentionally part of checkpoint intent; semantic cleanup stays in the Development System.
- Git itself remains the filesystem-to-object canonicalization authority.
- Ambiguous structural Git states, dirty/unknown submodules, and incomplete/sparse observability fail closed rather than producing guessed commits.
- No-op editing does not create empty managed history.
- 30.28 now has an exact candidate subject to bind validation evidence to: `(repository_id, git_object_format, parent_oid, tree_oid)`.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-064

ADR-064 replaces the obsolete pre-ADR-060 phrase “after validation evidence has been accepted” with a frozen-handoff identity rule. `ruu` constructs `(P,T)` only after transferable authority plus exclusive claim, immediately revalidates the candidate/authority assumptions under that claim, and materializes only a commit `K` with `parent(K)=P` and `tree(K)=T`. Semantic test/review evidence remains outside the engine.
