# Ruu — State-Space Audit v31

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-063
- **Executable:** `state-space-audit-v31.py`
- **Captured output:** `state-space-audit-v31.txt`
- **Result:** PASS

## Purpose

This pass revalidates the retained finite regression model through ADR-061 and adds explicit boundary families for the architectural changes introduced by ADR-062 and ADR-063:

1. route-independent promotion / conditional ProviderSubmission projection / automatic provider finalization;
2. semantic finding vs blocking provider-governance / external backlog boundary.

It also statically checks the current Markdown architecture and reruns the five concrete Git primitive smokes retained from v30.

## Retained baseline

State-space audit v30 contained:

```text
14,366 finite combinations
```

covering the retained architecture through ADR-061.

Those combinations remain regression baseline rather than being discarded after the terminology/abstraction change.

## ADR-062 provider-projection/finalization family

Dimensions:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE
  PROVIDER_SUBMISSION

review/publication intent:
  NOT_ESTABLISHED
  REVIEW_NOT_REQUESTED
  REVIEW_REQUESTED

early-publication authority:
  false
  true

provider governance:
  PENDING
  SATISFIED
  HUMAN_FINALIZER_REQUIRED

provider target-integration capability:
  SUPPORTED
  UNSUPPORTED
```

Finite product:

```text
2 × 3 × 2 × 3 × 2 = 72
```

Key assertions include:

```text
PROVIDER_SUBMISSION
+ no REVIEW_REQUESTED
+ no explicit early-publication authority
→ NO_PROVIDER_PROJECTION

PROVIDER_SUBMISSION
+ projection permitted
+ provider governance PENDING
→ WAIT_PROVIDER_GOVERNANCE

PROVIDER_SUBMISSION
+ explicit HUMAN_FINALIZER_REQUIRED
→ WAIT_EXPLICIT_HUMAN_FINALIZER

PROVIDER_SUBMISSION
+ projection permitted
+ governance SATISFIED
+ integration capability SUPPORTED
→ AUTO_PROGRESS_PROVIDER_FINALIZATION

no state
→ WAIT_FOR_MANUAL_MERGE_CLICK merely by convention
```

Result:

```text
PASS — 72 combinations
```

## ADR-063 finding/backlog boundary family

Dimensions:

```text
provider governance blocking:
  false
  true

semantic finding adjudication:
  FIX_NOW
  DEFER
  ACCEPT
  REJECT

backlog finding applicability:
  CURRENT
  STALE
```

Finite product:

```text
2 × 4 × 2 = 16
```

Key assertions include:

```text
blocking provider governance
→ ReviewCorrectionDemand
→ external DEFER cannot bypass it

nonblocking DEFER + CURRENT
→ external backlog track

nonblocking DEFER + STALE
→ external close/supersede

no semantic finding state
→ PR_BACKLOG core object
```

Result:

```text
PASS — 16 combinations
```

## Total changed/revalidated finite combinations

```text
retained v30                         14,366
ADR-062 added                            72
ADR-063 added                            16
------------------------------------------
v31 total                            14,454
```

## Static normative checks

The executable verifies among other things:

- ADR numbering is contiguous `001..063`;
- current main spec uses `target_realization_route`;
- current main spec contains `DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION`;
- `promotion_mode` is absent from the current main normative vocabulary;
- `provider_pr_identity`, `PR_SUBMITTING`, and `CREATE_PR_SUBMISSION` are absent from the current main spec;
- `provider_submission_identity` is present;
- `RealizePromotion(exact candidate, immutable PromotionTarget)` is explicit;
- ADR-062 no-projection rule is present;
- no default manual-Merge-click state is modeled;
- the External Control Plane contract contains the semantic finding/backlog boundary;
- backlog 30.36 is closed;
- the only `open (30.x)` heading in the current backlog is 30.34;
- obsolete generic development-validation wait states remain absent;
- Markdown code fences are balanced across the current package.

Result:

```text
PASS
```

## Concrete Git primitive smokes

The following retained implementation-level Git primitives were executed again:

```text
ADR-048 materialization smoke      PASS
ADR-050 restack smoke              PASS
DIRECT_TARGET_ADVANCE smoke        PASS
repository bootstrap smoke         PASS
canonical checkpoint smoke         PASS
```

These are regression checks for the Git mechanics underlying the architecture; ADR-062/063 do not weaken them.

## Conclusion

The new provider-projection model is state-space coherent with the retained architecture:

- provider submission absence is a valid state;
- provider finalization can be automatically progressed when all real authorities are satisfied;
- human finalization waits are explicit governance states rather than default ceremony;
- semantic deferred findings remain outside `ruu`;
- blocking provider review remains an exact provider-governance obligation;
- the existing Git safety invariants continue to hold.

The remaining open core item is 30.34 exact final target-integration proof.
