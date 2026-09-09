# Ruu — State-Space Audit v28

- **Date:** 2026-09-06
- **Architecture through:** ADR-059
- **Result:** PASS

## 1. Purpose

This pass revalidates the complete retained finite architecture state-space after ADR-059 closes backlog 30.27 by defining the canonical whole-editing-surface checkpoint snapshot and exact pre-commit candidate identity.

ADR-058 already fixed whole-surface intent, staging non-authority, and native-Git equivalence. ADR-059 adds the remaining mechanical rules:

```text
exact parent P + complete observable Git-relevant editing surface
→ temporary native Git index seeded from P
→ native whole-surface canonicalization / write-tree
→ exact tree T
→ checkpoint candidate identity (repository_id, git_object_format, P, T)
```

It also fixes untracked/ignored membership, structural Git blockers, submodule handling, native symlink/mode/filter semantics, sparse-observability blocking, and no-op behavior.

## 2. New ADR-059 finite families

### 2.1 Canonical membership is independent of staging

The audit varies:

```text
tracked = UNCHANGED | MODIFIED | DELETED
untracked = NONE | NONIGNORED | IGNORED
staging = NONE | PARTIAL | ALL | INTENT_TO_ADD
```

Tracked modifications/deletions and non-ignored untracked paths are reflected in the candidate independently of the caller's staging state. Ignored untracked paths are excluded.

Finite combinations: **36**.

### 2.2 Structural Git / submodule / observability guard

The audit varies representative structural Git state, submodule state, and worktree observability:

```text
Git state = NORMAL | UNMERGED | MERGE_IN_PROGRESS | CHERRY_PICK_IN_PROGRESS |
            REBASE_IN_PROGRESS | REVERT_IN_PROGRESS | UNKNOWN
submodule = CLEAN_OR_NONE | DIRTY | UNKNOWN_REQUIRED
observability = FULL | SPARSE_HIDDEN
```

Only `NORMAL + CLEAN_OR_NONE + FULL` is ordinarily checkpointable. All ambiguous or incompletely observable combinations fail closed.

Finite combinations: **42**.

### 2.3 Exact candidate identity is separate from ContributionUnit attribution

The audit varies equality of:

```text
repository_id
git_object_format
parent_oid
tree_oid
ContributionUnit_id
```

Candidate Git-state identity is unchanged only when the first four exact fields are unchanged. Changing only `ContributionUnit_id` does not create a different Git candidate; it changes attribution/governance metadata.

Finite combinations: **32**.

### 2.4 No-op behavior

The audit enforces:

```text
T == tree(P)  → NOOP
T != tree(P)  → checkpoint materialization may proceed subject to ordinary guards
```

An empty managed commit is not a valid substitute for the no-op case.

Finite combinations: **4**.

### 2.5 Native Git tree representation

Representative Git entry classes are checked against the canonicalizer choice:

```text
regular blob
executable blob
symlink
gitlink
filtered blob
```

Only native Git object/tree semantics conform; a private normalization layer does not.

Finite combinations: **10**.

ADR-059 adds **124** finite combinations to the v27 total of **14,598**, producing **14,722** total.

## 3. Static integration checks

The static pass verifies among other things that:

- ADR numbering is contiguous through **ADR-059**;
- main section 30.27 is explicitly **resolved by ADR-059**;
- backlog 30.27 is closed while 30.28, 30.34, and 30.36 remain open;
- invariants 135–139 encode native canonical tree construction, untracked membership, fail-closed observability, no-op semantics, and candidate identity/attribution separation;
- ADR-057's Development System validation boundary and ADR-058 native-Git equivalence remain intact;
- no partial/path-selected checkpoint mode or staging-membership authority is reintroduced;
- the new canonical checkpoint Git smoke exists and passes;
- Markdown code fences and accepted ADR numbering remain structurally consistent.

## 4. Git smoke validation

All concrete Git primitive smokes pass:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
Ruu repository bootstrap smoke v1: PASS
Ruu canonical checkpoint smoke v1: PASS
```

The new checkpoint smoke demonstrates that a temporary index seeded from the exact parent and updated from the whole worktree:

- uses the final worktree version rather than an intermediate staged version;
- includes non-ignored untracked files;
- excludes ignored untracked files;
- reproduces the same exact tree on re-snapshot;
- leaves the caller's real staging untouched during candidate construction;
- yields parent-tree equality for a no-op surface; and
- mechanically exposes native unmerged/in-progress merge state.

## 5. Result

Executable result:

```text
Ruu state-space audit v28: PASS
changed/revalidated finite combinations evaluated: 14,722
markdown artifacts statically cross-checked: 90
```

**Verdict:** ADR-059 closes 30.27 without contradicting the retained architecture. Checkpoint intent is whole-surface, Git itself remains the canonical filesystem-to-object authority, structurally ambiguous or incompletely observable states fail closed, and the exact pre-commit candidate now has a stable Git-state identity that 30.28 can bind external development-validation evidence to.
