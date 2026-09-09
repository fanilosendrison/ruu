# Ruu — State-Space Audit v27

- **Date:** 2026-09-06
- **Architecture through:** ADR-058
- **Result:** PASS

## 1. Purpose

This pass revalidates the complete retained finite architecture state-space after ADR-058 introduced two related constraints:

1. **native-Git equivalence / Git transparency** — `ruu` is a governance and recovery overlay over ordinary Git, never a proprietary Git dialect; and
2. **whole-editing-surface checkpoint intent** — a v1 checkpoint for one dirty transferable ContributionUnit has no partial/path-selected managed checkpoint mode and does not use the caller's current staging partition as checkpoint-selection authority.

ADR-058 intentionally does **not** close the remaining canonical checkpoint snapshot/identity question. 30.27 still owns exact handling of untracked/ignored paths, structural index edge cases, submodules, symlink/file-mode normalization, empty/no-op checkpoints, and exact pre-commit candidate identity.

## 2. New ADR-058 finite families

### 2.1 Native-Git equivalence

The audit varies representative successful Git progression classes:

```text
CHECKPOINT
INTERNAL_MERGE
SUBMISSION_REVISION
DIRECT_TARGET_FF
```

against result representation and metadata role:

```text
NATIVE_GIT | PROPRIETARY_GIT_SEMANTICS
OVERLAY_ONLY | REQUIRED_TO_INTERPRET_GIT
```

Only ordinary Git semantics with governance metadata as an overlay conform to ADR-058.

Finite combinations: **16**.

### 2.2 Native operability vs managed authorization

The audit distinguishes mutations originating from:

```text
Ruu
human native Git
agent native Git
external Git tooling
```

and explicitly keeps technical Git operability separate from later managed authorization/adoption. Ordinary Git use is not prohibited merely to preserve governance; externally produced movement is instead handled by the existing exact observation/adoption, drift/reconciliation, policy/evidence, claims/CAS, and recovery machinery.

Finite combinations: **16**.

### 2.3 Whole-surface checkpoint intent and staging non-authority

The audit varies:

```text
staging = NONE | PARTIAL | ALL
requested selection = WHOLE_SURFACE | STAGED_ONLY | PATH_SELECTED
membership basis = CANONICAL_SURFACE | CURRENT_INDEX
```

The only conforming v1 checkpoint intent is:

```text
WHOLE_SURFACE + CANONICAL_SURFACE
```

and the result is deliberately independent of whether the caller happened to have nothing, some, or everything staged.

Finite combinations: **18**.

## 3. Regression coverage retained

Every finite family retained by v26 is rerun, including:

- ContributionUnit identity/lifecycle/exact-checkpoint continuity;
- mutation-authority, claim and fenced-executor semantics;
- global convergence-demand coalescing and current-state reconciliation;
- CoordinationStore / Operation → Attempt → Observation → Adoption recovery;
- promotion policy authority/currentness;
- immutable PromotionUnit/PromotionGroup identity and projection;
- ADR-048 candidate materialization;
- submission identity and ADR-050 restack;
- provider capability normalization;
- DIRECT exact-old CAS+FF target advancement;
- review-correction continuation;
- ConvergenceUnit closure/retirement;
- cross-repository partial-progress settlement and PublicationEpisodes;
- ADR-056 repository bootstrap/admission;
- ADR-057 state-dependent invocation and external DevelopmentValidationEvidence boundary.

The retained v26 count was **14,548** combinations. ADR-058 adds **50** new finite combinations, producing **14,598** total.

## 4. Static integration checks

The static pass verifies among other things that:

- ADR numbering is contiguous through **ADR-058**;
- the main requirements contain invariants 131–134 for native Git interpretation, governance separation, whole-surface checkpoint intent, and staging non-authority;
- 30.27 is explicitly only **partially resolved** and still lists the unresolved canonical snapshot/identity edge cases;
- the backlog no longer lists staged-vs-unstaged selection or partial-staging support as open architectural choices;
- 30.28 remains the separate minimal `DevelopmentValidationEvidence` binding contract;
- ADR-057's external validation boundary remains intact;
- no internal CI/test executor state is reintroduced;
- Markdown code fences and accepted ADR numbering remain structurally consistent.

## 5. Git smoke validation

All existing concrete Git primitive smokes pass:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
Ruu repository bootstrap smoke v1: PASS
```

ADR-058 adds a semantic compatibility invariant and checkpoint-selection rule; it introduces no new Git merge/ref/bootstrap primitive requiring an additional smoke fixture.

## 6. Result

Executable result:

```text
Ruu state-space audit v27: PASS
changed/revalidated finite combinations evaluated: 14,598
markdown artifacts statically cross-checked: 88
```

**Verdict:** ADR-058 integrates without contradiction into the existing architecture. The system remains ordinary Git at its observable Git layer while retaining `ruu` governance as external managed-state semantics. 30.27 remains intentionally open only for canonical checkpoint snapshot construction and exact candidate identity.
