# Ruu — STATE-SPACE-AUDIT v39

- **Date:** 2026-09-08
- **Technical finite-state families:** through ADR-074
- **Baseline retained:** v38 = 14,992 finite combinations
- **New ADR-074 combinations:** 148
- **Current total:** **15,140 finite combinations — PASS**

## A. Managed authoring-binding transition classifier — 72 combinations

Dimensions:

```text
binding: UNMANAGED | MANAGED
prepared persistence: FAILED | DURABLE
Git transaction outcome: ABORT | COMMIT
causal disposition evidence: RENAME | TERMINAL_DELETE | AMBIGUOUS
associated group state: UNREALIZED | PROMOTED | PARTIAL
```

Required properties:

```text
UNMANAGED
→ semantically neutral

MANAGED + prepared persistence FAILED
→ ref removal cannot be validly committed under current ADR-071 contract

MANAGED + durable prepare + ABORT
→ no disposition change

MANAGED + durable prepare + COMMIT + RENAME
→ CONTINUATION
→ no CANCEL

MANAGED + durable prepare + COMMIT + TERMINAL_DELETE + UNREALIZED
→ ABANDON → CANCEL

... + PROMOTED
→ historical success unchanged; cleanup only

... + PARTIAL
→ abandonment cannot erase realized history; ADR-055 settlement remains controlling

MANAGED + durable prepare + COMMIT + AMBIGUOUS
→ BLOCK_UNRESOLVED
→ no incompatible irreversible realization
```

Result: **PASS (72)**.

## B. Exceptional binding recovery — 36 combinations

Dimensions:

```text
native proof: RENAME | DELETE | NONE
ECP recovery: NONE | REBIND | ABANDON
current Git state compatible: no | yes
expected binding generation matches: no | yes
```

Required properties:

```text
native RENAME proof
→ CONTINUATION

native DELETE proof
→ ABANDON

no native proof + no recovery
→ BLOCK

no native proof + ECP recovery
+ exact Git state compatible
+ expected binding generation current
→ adopt declared logical REBIND/ABANDON

stale generation or contradictory Git state
→ BLOCK_STALE_OR_CONTRADICTORY
```

The ECP recovery declaration never manufactures Git history; it supplies only current logical recovery authority.

Result: **PASS (36)**.

## C. Minimal observation taxonomy — 24 combinations

Classes:

```text
AUTHORING_BINDING_DISPOSITION
AUTHORING_TIP_MOVE
WORKTREE_TOPOLOGY
INTERNAL_REF
SUBMISSION_REF
TARGET_REF
INDEX_STRUCTURAL
SUBMODULE_SPARSE
TAG_STASH_NOTES
REMOTE_REF
PROVIDER_STATE
ANCESTRY_ENV
```

Each class is evaluated with and without an intermediate-history gap.

Required classification:

```text
AUTHORING_BINDING_DISPOSITION
→ EVENT semantic family
→ coverage gap requires recovery/coverage proof

all other listed classes
→ STATE observation
→ current exact state / drift / recovery rules remain authoritative
```

Result: **PASS (24)**.

## D. Ancestry-environment state — 16 combinations

Dimensions:

```text
ancestry environment: NONE | REPLACE | GRAFT | SHALLOW
current transition needs ancestry: no | yes
normalized/proven ancestry available: no | yes
```

Required properties:

```text
ancestry not required by current transition
→ overlay/completeness state is not an authorization input for that transition

ancestry required + no overlay
→ ordinary exact native ancestry

ancestry required + overlay/shallow + normalized/proven view available
→ use proven normalized ancestry

ancestry required + overlay/shallow + proof unavailable
→ BLOCK_ANCESTRY_UNKNOWN
```

Result: **PASS (16)**.

## Native Git observation regressions

`git-native-observation-smoke-v2.sh` was executed with the container Git implementation and verifies five concrete behaviors on Git 2.47.3.

### 1. Native rename continuity

```text
foo checked out in linked worktree
→ git branch -m foo bar
→ old ref removal visible to reference-transaction
→ bar points at same exact preimage OID
→ same linked worktree HEAD is rebound to refs/heads/bar
→ bar reflog records native rename continuity
```

Result: **PASS**.

This regression is the falsifier for the old ADR-071 shortcut: observing removal of `foo` is insufficient to classify abandonment.

### 2. Copy then delete is not rename

```text
git branch -c foo bar
→ bar reflog records copy
→ bar may point at the same OID
→ git branch -D foo
→ foo gone, bar survives
→ no native rename evidence foo → bar
```

Result: **PASS**.

Same OID is therefore not authoring-line continuity authority.

### 3. `prepared` persistence failure can reject ref removal

A `reference-transaction` hook returning non-zero during `prepared` for the protected ref deletion prevents the deletion and leaves the ref present.

Result: **PASS**.

This retains ADR-071's existing write-ahead safety primitive while 30.54 remains open on broader persistence-failure policy.

### 4. Ancestry interpretation environment is observable and material

The smoke demonstrates:

```text
refs/replace/*
→ changes effective object/parent view for normal Git commands
→ GIT_NO_REPLACE_OBJECTS restores native object view for replace refs

.git/info/grafts
→ changes parent view
→ remains effective even with GIT_NO_REPLACE_OBJECTS in the tested Git

shallow clone
→ .git/shallow exists as an explicit history-completeness boundary
```

Result: **PASS**.

ADR-074 therefore treats replace refs, grafts, and shallow boundaries as correctness-relevant **state**, not event-semantic history.

### 5. Missing reflog can be re-baselined for future rename evidence

With repository-wide automatic reflog creation disabled, the smoke establishes an empty branch-specific reflog baseline for `foo`, then runs native `git branch -m foo bar`. Git writes the rename record to `bar`'s reflog.

Result: **PASS**.

This proves the architectural distinction: a repaired baseline can support **future** causal evidence without pretending to reconstruct missing past history. The exact repair/bootstrap mechanism remains an implementation/conformance detail under 30.51/30.53/30.54.

## Retained architecture properties

The v38 baseline remains retained except for the directly superseded classifier:

```text
old v38 shortcut:
committed managed old-ref deletion → abandonment

ADR-074 correction:
committed managed old-ref deletion
→ unresolved binding disposition
→ causal proof CONTINUATION | ABANDON
```

ADR-071 current-disposition causal fencing, provider-race fail-closed behavior, ADR-069 invocation/group identity, ADR-066 route-conformant realization, and all older exact-state recovery families remain retained.

## Backlog impact

- **30.50 CLOSED** by ADR-074.
- 30.49 remains the umbrella.
- 30.51–30.55 remain open.
- 30.53/30.54 must address continuous event-observation coverage and persistence health; v39 does not pretend current ref equality proves that no event occurred during a coverage gap.

## Total

```text
retained v38:       14,992
ADR-074 new:           148
--------------------------
v39 total:          15,140
```

**Verdict: PASS.**
