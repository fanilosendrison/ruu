# Ruu — State-Space Audit v36

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-068, hostile-audit H4 explicitly ratified
- **Executable:** `state-space-audit-v36.py`
- **Captured output:** `state-space-audit-v36.txt`
- **Result:** PASS

## Purpose

This pass retains the valid v35 model and adds an explicit finite family for the remaining hostile-audit H4 question: whether a terminal `PromotionUnit PROMOTED` is historical completion or a perpetual current-target-membership predicate.

The already-normative ADR-066 / Invariant 154 answer is now mechanically tested:

```text
route-conformant realization durably adopted
→ PromotionUnit PROMOTED

later force rewrite / target drift removes the realized result
→ PromotionUnit remains PROMOTED historical fact
→ MUST NOT reopen / un-promote / demote the historical PromotionUnit

if later drift is independently discovered
→ a distinct new integrity/reconciliation fact may be emitted
→ historical PROMOTED remains unchanged
```

## Retained v35 baseline

```text
v34 corrected baseline                              14,686
ADR-068 group cancellation                              48
ADR-068 ConvergenceUnit disposition                      64
ADR-068 immutable membership change                       8
-----------------------------------------------------------
v35 total                                            14,806
```

## Hostile-audit H4 historical-PROMOTED family

Dimensions:

```text
durably adopted promotion: false | true
later target state:
  RESULT_PRESENT | RESULT_REMOVED_BY_REWRITE | TARGET_DIVERGED
later drift independently discovered: false | true
```

Finite product:

```text
2 × 3 × 2 = 12
```

Critical assertions:

```text
not durably adopted
→ no historical PROMOTED fact exists yet

durably adopted + result still present
→ PROMOTED_HISTORICAL

durably adopted + result later removed/diverged
→ PROMOTED_HISTORICAL

durably adopted + later drift independently discovered
→ PROMOTED_HISTORICAL + separate new drift fact

no case after durable adoption
→ REOPEN_PROMOTION_UNIT / UNPROMOTE / DEMOTE_TO_NONTERMINAL
```

## Total finite coverage

```text
v35 retained                                        14,806
H4 historical-PROMOTED family                           12
-----------------------------------------------------------
v36 total                                            14,818
```

## Static normative checks

The executable rechecks the current specification, including:

- contiguous ADR numbering `001..068`;
- route-conformant `C → H → R → O` proof;
- historical-authorization/fresh-mutation distinction;
- Invariant 154: `PROMOTED` is historical completion, not perpetual target-membership monitoring;
- PromotionUnit `SUPERSEDED`;
- PromotionGroup `CANCELLED`;
- neutral ordinary Git artifact deletion;
- no current open 30.x core backlog item;
- balanced Markdown fences.

## Concrete Git primitive smokes

All seven v35 concrete Git mechanics are rerun unchanged:

```text
ADR-048 materialization                               PASS
ADR-050 restack                                       PASS
DIRECT_TARGET_ADVANCE                                 PASS
repository bootstrap                                  PASS
canonical checkpoint                                  PASS
provider route C→H→R→O                               PASS
ordinary branch deletion / managed-checkpoint anchor  PASS
```

H4 itself is a lifecycle/proof-history property rather than a new Git primitive, so it is exercised by the finite semantic family and static normative assertions rather than by inventing a fake Git transport mechanism.

## Conclusion

The original hostile-audit findings H1..H6 are now all both architecturally resolved and explicitly represented in the current verification package. `PROMOTED` is terminal historical completion. Later target drift is a new external integrity fact and never retroactively rewrites the completed PromotionUnit.
