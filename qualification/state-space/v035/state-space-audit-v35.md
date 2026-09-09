# Ruu — State-Space Audit v35

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-068
- **Executable:** `state-space-audit-v35.py`
- **Captured output:** `state-space-audit-v35.txt`
- **Result:** PASS

## Purpose

This pass retains the corrected v34 model and adds explicit ADR-068 coverage for pre-promotion PromotionGroup cancellation, ConvergenceUnit disposition after cancellation, immutable membership replacement, and the semantic neutrality of ordinary authoring branch/ref/worktree deletion.

It is designed to reject the following newly formalized failures:

```text
user/agent deletes ordinary authoring branch
→ MUST NOT imply ContributionUnit CLOSED
→ MUST NOT imply ConvergenceUnit ABANDONING
→ MUST NOT imply PromotionGroup CANCELLED

explicit cancellation intent + realized group effect
→ MUST NOT CANCEL

explicit cancellation intent + committed/unknown effect may still realize
→ MUST remain recovery-visible / nonterminal

explicit cancellation intent + zero realized effect
+ zero unresolved still-realizing effect
+ provider surface terminally non-realizing
→ group may become CANCELLED

cancelled G1 + member X also belongs to replacement/nonterminal G2
→ X MUST NOT enter ABANDONING

membership changes from {XA,XB} to {XA}
→ cancel old G1 + declare new G2
→ MUST NOT mutate G1
```

## Retained v34 baseline

The valid v34 pass contains:

```text
retained v32 baseline                            14,470
ADR-066 route-conformant realization                108
ADR-066 policy-drift/commitment recovery              96
ADR-067 PromotionUnit supersession                     12
---------------------------------------------------------
v34 total                                          14,686
```

The invalid v33 route-independent provider proof remains historical only and is not accumulated as authoritative evidence.

## ADR-068 PromotionGroup cancellation family

Dimensions:

```text
current cancellation intent: absent | present
realized group effect: false | true
unresolved realization: NONE | COMMITTED | UNKNOWN
managed promotion surface: TERMINAL_NONREALIZING | CAN_STILL_REALIZE
authoring artifact: PRESENT | DELETED
```

Finite product:

```text
2 × 2 × 3 × 2 × 2 = 48
```

Critical assertions:

```text
no current cancellation authority
→ no cancellation

realized effect
→ CANCEL_FORBIDDEN_REALIZED_EFFECT

committed/unknown realizing effect
→ RECOVERY_PENDING_EFFECT_MAY_REALIZE

managed surface can still realize
→ terminal non-realizing surface required before cancellation

zero realized + zero unresolved + terminal non-realizing surface
→ GROUP_CANCELLED

authoring artifact PRESENT vs DELETED
→ identical semantic cancellation outcome
```

## ADR-068 ConvergenceUnit disposition family

Dimensions:

```text
relevant group terminal state:
  CANCELLED | ALL_PROMOTED | COMPENSATED | NONTERMINAL
replacement/nonterminal group: false | true
current authoring/reconciliation demand: false | true
explicit lineage-disposal authority current: false | true
authoring artifact: PRESENT | DELETED
```

Finite product:

```text
4 × 2 × 2 × 2 × 2 = 64
```

Critical assertions:

```text
replacement group or current authoring demand
→ LINEAGE_REMAINS_LIVE

NONTERMINAL group
→ LINEAGE_REMAINS_LIVE

ALL_PROMOTED / COMPENSATED with no live demand
→ ordinary ADR-054 PROMOTED closure

CANCELLED + no live demand + current disposal authority
→ ABANDONING_ELIGIBLE

CANCELLED without required disposal authority
→ WAIT_LINEAGE_DISPOSITION_AUTHORITY

artifact PRESENT vs DELETED
→ identical ConvergenceUnit disposition
```

## ADR-068 immutable membership-change family

Dimensions:

```text
old group effect: ZERO_REALIZED | REALIZED
desired membership: SAME | CHANGED
current cancellation authority: absent | present
```

Finite product:

```text
2 × 2 × 2 = 8
```

Assertions:

```text
changed membership + zero realized + cancellation authority
→ CANCEL_OLD_DECLARE_NEW_GROUP

changed membership + realized effect
→ settlement required; old group remains immutable

changed membership without cancellation authority
→ wait; old group remains immutable

no case
→ MUTATE_EXISTING_GROUP
```

## Total finite coverage

```text
v34 retained                                        14,686
ADR-068 PromotionGroup cancellation                    48
ADR-068 ConvergenceUnit disposition                    64
ADR-068 immutable membership change                     8
---------------------------------------------------------
v35 total                                          14,806
```

## Static normative checks

The executable verifies, among other things:

- ADR numbering is contiguous `001..068`;
- backlog 30.41 is closed by ADR-068 and there is no current open 30.x core item;
- ordinary Git artifact deletion has no hidden lifecycle/cancellation semantics;
- current group settlement includes `CANCELLED` with zero-realized/zero-still-realizing-effect guards;
- `CANCELLED` cannot erase a realized effect;
- membership change is cancel-old + declare-new, never mutation;
- `ABANDONING` is gated by higher-level terminal disposition and absence of replacement/nonterminal obligations;
- ADR-066 route-conformant `C → H → R → O` proof remains intact;
- ADR-067 PromotionUnit `SUPERSEDED` remains distinct from group cancellation;
- generic development-validation states remain absent;
- Markdown code fences are balanced.

## Concrete Git primitive smokes

Seven concrete mechanics are run:

```text
ADR-048 materialization                               PASS
ADR-050 restack                                       PASS
DIRECT_TARGET_ADVANCE                                 PASS
repository bootstrap                                  PASS
canonical checkpoint                                  PASS
provider route C→H→R→O                               PASS
ordinary branch deletion / managed-checkpoint anchor  PASS
```

The new branch-deletion smoke creates an exact managed checkpoint, anchors it under a managed ref, deletes the ordinary authoring branch, and verifies that the exact checkpoint remains reachable and unchanged. This tests the Git primitive underlying ADR-038/068's separation between editing-artifact existence and durable managed state; the semantic no-cancellation rule is covered by the finite families/static checks.

## Conclusion

ADR-068 closes the last open item from the current hostile-review backlog without making `ruu` own normal Git usage. A user/agent can still delete an ordinary branch directly; semantic cancellation exists only as an explicit higher-level disposition of an already-declared still-unrealized PromotionGroup.
