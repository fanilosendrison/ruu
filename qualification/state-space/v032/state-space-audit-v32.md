# Ruu — State-Space Audit v32

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-064
- **Executable:** `state-space-audit-v32.py`
- **Captured output:** `state-space-audit-v32.txt`
- **Result:** PASS

## Purpose

This pass retains the complete v31 regression model and adds an explicit finite family for ADR-064's pre-commit frozen mutation handoff. It verifies that early Development System validation can remain outside `ruu` while the exact surface offered for checkpoint cannot legitimately drift before commit.

The audit also rechecks the route-independent promotion/provider-submission model from ADR-062, the semantic finding/backlog boundary from ADR-063, the absence of obsolete generic development-validation wait/evidence state, the immutable PromotionTarget model, Markdown consistency, ADR numbering, and the retained concrete Git primitive smokes.

## Retained baseline

State-space audit v31 contained:

```text
14,454 finite combinations
```

This includes the retained architecture through ADR-061 plus:

```text
ADR-062 provider projection/finalization    72
ADR-063 finding/backlog boundary            16
```

## ADR-064 frozen checkpoint-offer family

Dimensions:

```text
mutation_access:
  PROTECTED_EXTERNAL
  TRANSFERABLE

exclusive claim:
  NONE
  CURRENT_EXECUTOR

external write while handoff current:
  false
  true

candidate state at same-claim revalidation:
  STABLE
  CHANGED
```

Finite product:

```text
2 × 2 × 2 × 2 = 16
```

Key assertions:

```text
PROTECTED_EXTERNAL
→ no Ruu checkpoint authority

TRANSFERABLE
+ no exclusive claim
+ no external write
→ wait for exclusive claim

TRANSFERABLE
+ any external write while handoff remains current
→ External Control Plane contract violation
→ never authorize a commit from the stale/ambiguous surface

TRANSFERABLE
+ CURRENT_EXECUTOR claim
+ no external write
+ candidate changed at same-claim revalidation
→ abort old candidate / re-observe

TRANSFERABLE
+ CURRENT_EXECUTOR claim
+ no external write
+ candidate stable
→ commit exact frozen candidate
```

This family deliberately contains **no dimension for `TESTS_PASSED`, `REVIEW_PASSED`, or `DevelopmentValidationEvidence`**. ADR-064's purpose is to bind the external readiness decision to exact Git state by immobility across the handoff, not to re-import semantic validation into the Git engine.

Result:

```text
PASS — 16 combinations
```

## Total changed/revalidated finite combinations

```text
retained v31                           14,454
ADR-064 added                              16
--------------------------------------------
v32 total                              14,470
```

## Static normative checks

The executable verifies among other things:

- ADR numbering is contiguous `001..064`;
- the current main spec uses `target_realization_route = DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION`;
- obsolete `promotion_mode`, `provider_pr_identity`, `PR_SUBMITTING`, and `CREATE_PR_SUBMISSION` current vocabulary remain absent from the main spec;
- no default manual Merge-click state exists;
- the External Control Plane keeps semantic findings/backlog outside `ruu`;
- backlog 30.36 remains closed and the only current open core item is 30.34;
- ADR-064 is present;
- current invariants explicitly state that a transferable checkpoint offer is frozen against external mutation and that the managed checkpoint commit is exactly the frozen canonical candidate;
- the External Control Plane contract contains the frozen checkpoint-offer boundary;
- obsolete generic development-validation waiting states remain absent;
- Markdown code fences are balanced across the package.

Result:

```text
PASS
```

## Concrete Git primitive smokes

The following implementation-level Git mechanics were executed again:

```text
ADR-048 materialization smoke      PASS
ADR-050 restack smoke              PASS
DIRECT_TARGET_ADVANCE smoke        PASS
repository bootstrap smoke         PASS
canonical checkpoint smoke         PASS
```

The canonical checkpoint smoke continues to verify that the managed tree is constructed from the complete observable surface rather than the caller's staged partition, includes non-ignored untracked work, excludes ignored untracked work, leaves the real index untouched during candidate construction, and produces the same tree for the same exact surface.

## Resulting boundary

The current pre-commit path is now explicit:

```text
Development System edits / tests / reviews / corrects
→ decides current surface S may checkpoint
→ durable transferable mutation handoff
→ external writes forbidden while handoff current
→ Ruu acquires exclusive claim
→ constructs ADR-059 candidate (P,T)
→ revalidates exact parent/surface/authority under same claim
→ commits only K where parent(K)=P and tree(K)=T
```

If semantic authoring resumes before claim acquisition, transferability must first be revoked and the prior readiness decision is stale. If `ruu` already holds the claim, external authoring waits for a safe release/recovery boundary.

## Conclusion

ADR-064 closes the pre-commit exactness ambiguity without undoing ADR-060. Tests and semantic reviews can occur before commit, but `ruu` remains a Git progression engine rather than a development-validation service.

The remaining genuine open core item is still **30.34 — exact final target-integration / merge-result proof**, especially for provider finalization paths where squash, rebase, merge queue, or other provider transformations make the authoritative target result differ from the submitted head OID.
