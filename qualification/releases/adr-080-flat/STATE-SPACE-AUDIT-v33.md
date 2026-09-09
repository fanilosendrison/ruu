# Ruu — State-Space Audit v33

> **Superseded audit model:** hostile review found that this pass encoded route-independent candidate ancestry and therefore missed provider-route bypass plus `C != H` restack cases. Retained only as historical evidence; current normative audit is v34.

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-065
- **Executable:** `state-space-audit-v33.py`
- **Captured output:** `state-space-audit-v33.txt`
- **Result:** PASS

## Purpose

This pass retains the complete v32 regression model and adds an explicit finite family for ADR-065 final target-realization proof. It verifies that `PromotionUnit PROMOTED` cannot be inferred merely from provider `MERGED` / `PROVIDER_FINALIZED`, while preserving native Git proof whenever exact candidate ancestry survives and allowing provider-authorized history rewriting without importing semantic diff-equivalence into `ruu`.

The audit also rechecks ADR-062 route-independent promotion/provider projection, ADR-063 semantic finding/backlog separation, ADR-064 frozen mutation handoff, ADR-060 removal of obsolete generic development-validation state, ADR-061 immutable PromotionTarget binding, Markdown consistency, contiguous ADR numbering, and concrete Git mechanics.

## Retained baseline

State-space audit v32 contained:

```text
14,470 finite combinations
```

This already included:

```text
ADR-062 provider projection/finalization     72
ADR-063 finding/backlog boundary             16
ADR-064 frozen handoff/checkpoint identity   16
```

## ADR-065 final target-realization family

Dimensions:

```text
target-realization route:
  DIRECT_TARGET_ADVANCE
  PROVIDER_SUBMISSION

candidate relation to freshly observed target O:
  EXACT
  ANCESTOR
  ABSENT

provider submitted-revision/result binding:
  EXACT_C_TO_R
  MISSING_OR_MISMATCHED

provider finalization state:
  not finalized
  finalized

provider result relation to target:
  PRESENT
  ABSENT
```

Finite product:

```text
2 × 3 × 2 × 2 × 2 = 48
```

Key assertions:

```text
C == O
or C ancestor-of O
→ PROVEN_NATIVE_GIT
→ provider rewrite attestation not required

DIRECT_TARGET_ADVANCE
+ C absent from target history
→ TARGET_REALIZATION_UNPROVEN

PROVIDER_SUBMISSION
+ C absent from target history
+ provider finalized
+ exact C → R binding
+ R present in target history
→ PROVEN_PROVIDER_RESULT

provider finalized
+ missing/mismatched exact C → R binding
→ TARGET_REALIZATION_UNPROVEN

exact C → R binding
+ R absent from authoritative target history
→ TARGET_REALIZATION_UNPROVEN
```

Provider success state therefore cannot become a hidden terminal shortcut.

Result:

```text
PASS — 48 combinations
```

## Total changed/revalidated finite combinations

```text
retained v32                           14,470
ADR-065 added                              48
--------------------------------------------
v33 total                              14,518
```

## Static normative checks

The executable verifies among other things:

- ADR numbering is contiguous `001..065`;
- `target_realization_route = DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION` remains the current route model;
- PR/MR remains provider projection rather than semantic promotion mode;
- no generic manual Merge-click state exists;
- no obsolete generic development-validation wait/evidence state has returned;
- semantic review findings/backlog remain outside `ruu`;
- backlog 30.36 remains closed by ADR-062;
- backlog 30.34 is closed by ADR-065 and no genuine core design item remains open;
- ADR-065 contains `PromotionRealizationProof` and canonical `ProviderFinalizationObservation` semantics;
- invariants 148..151 require exact target proof, native ancestry when available, exact provider `C → R` binding when ancestry is lost, and no universal semantic-diff equivalence requirement;
- the External Control Plane contract records the provider transformation/final realization trust boundary;
- Markdown code fences remain balanced.

Result:

```text
PASS
```

## Concrete Git primitive smokes

Six concrete mechanics are executed:

```text
ADR-048 materialization smoke          PASS
ADR-050 restack smoke                  PASS
DIRECT_TARGET_ADVANCE smoke            PASS
repository bootstrap smoke             PASS
canonical checkpoint smoke             PASS
provider-result realization smoke      PASS
```

The new provider-result smoke constructs a candidate `C`, then materializes a squash-like provider result `R` with the same final tree but different commit identity/history. It verifies:

```text
C != R
C is not an ancestor of R
```

Then it places `R` in the authoritative target and advances the target once more to `O`, proving:

```text
R ancestor-of O
C not ancestor-of O
```

This is the concrete Git shape for the ADR-065 provider rewrite proof: native candidate ancestry is unavailable, but exact provider `C → R` binding plus independent Git observation of `R` in target history remains sufficient.

## Resulting boundary

The final promotion path is now explicit:

```text
exact PromotionUnit candidate C
+ immutable PromotionTarget T
        ↓
DIRECT or provider-mediated finalization
        ↓
fresh authoritative target observation O
        ↓
if C == O or C ancestor-of O:
    PromotionRealizationProof(NATIVE_EXACT | NATIVE_ANCESTRY)
else:
    exact ProviderFinalizationObservation(C → R on T)
    + R == O or R ancestor-of O
    → PromotionRealizationProof(PROVIDER_RESULT)
        ↓
durable ADR-042 Adoption
        ↓
PromotionUnit PROMOTED
```

Provider `MERGED` / `FINALIZED` without an exact result chain remains nonterminal. `ruu` does not implement a generic patch/tree/program-equivalence checker for rewritten provider results.

## Conclusion

ADR-065 closes backlog 30.34 while preserving the architecture's responsibility boundary: provider transformations are trusted only for the exact transformation they were delegated to perform, and authoritative Git observation independently proves that the exact result actually reached the target.

After this pass, no genuine core design item remains open in `OPEN-DESIGN-BACKLOG.md`.
