# Ruu — State-Space Audit v34

- **Date:** 2026-09-07
- **Architecture coverage:** through ADR-067
- **Executable:** `state-space-audit-v34.py`
- **Captured output:** `state-space-audit-v34.txt`
- **Result:** PASS

## Purpose

This pass replaces the invalid ADR-065 route-independent realization family exposed by hostile review. It retains the v32 baseline, then explicitly models ADR-066 route-conformant realization and policy-drift/effect-commitment recovery plus ADR-067 PromotionUnit supersession.

The audit is designed to reject the previously missed cases:

```text
provider route required + C appears in target + provider chain absent
→ MUST NOT PROMOTE

restack C0 → H2 + provider finalizes H2 → R + R in target
→ provider proof MUST start at H2, not pretend provider received C0

old policy authorized + no committed effect + current policy forbids
→ MUST NOT cause/retry effect

old policy authorized + effect already committed + later policy drift
→ historical observation/adoption may proceed

old P0 replaced by P1 + unresolved committed old effect
→ P0 MUST NOT disappear from recovery
```

## Retained baseline

State-space audit v32 contained:

```text
14,470 finite combinations
```

The v33 ADR-065 48-case family is **not retained as authoritative coverage** because its ordering encoded the hostile-audit defect: candidate ancestry terminalized provider-route cases before provider governance was considered.

## ADR-066 route-conformant realization family

Dimensions:

```text
route: DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION
candidate relation to target: EXACT | ANCESTOR | ABSENT
C→H projection: IDENTITY | EXACT | MISSING/MISMATCHED
H→R provider finalization: EXACT | MISSING/MISMATCHED | NONE
R relation to target: PRESENT | ABSENT
```

Finite product:

```text
2 × 3 × 3 × 3 × 2 = 108
```

Key assertions:

```text
DIRECT + C exact/ancestor target
→ PROVEN_DIRECT_ROUTE
→ provider attribution irrelevant

PROVIDER + C exact/ancestor target + no exact H→R finalization
→ TARGET_PRESENT_REQUIRED_PROVIDER_ROUTE_UNPROVEN

PROVIDER + exact C→H + exact H→R + R present target
→ PROVEN_PROVIDER_ROUTE

missing/mismatched C→H
→ never provider proof

missing/mismatched H→R or R absent
→ never provider proof
```

## ADR-066 policy-drift / effect-commitment recovery family

Dimensions:

```text
route: DIRECT | PROVIDER
old policy authorized: yes/no
current policy authorized: yes/no
commitment: NONE | ESTABLISHED | UNKNOWN
effect observed: ABSENT | PRESENT
action: OBSERVE/ADOPT | CAUSE_EFFECT
```

Finite product:

```text
2 × 2 × 2 × 3 × 2 × 2 = 96
```

Critical assertions:

```text
old authorization + current authorization absent
+ action may cause effect
→ BLOCK_STALE_AUTHORITY

old authorization + established commitment + effect present
+ current authorization later absent
→ ADOPT_HISTORICAL_COMMITTED_EFFECT

policy drift + commitment UNKNOWN
→ UNKNOWN_INCONSISTENT
```

The family deliberately distinguishes historical proof from future authority.

## ADR-067 supersession family

Dimensions:

```text
old PromotionUnit: PROMOTED | NONTERMINAL
current mapping: SAME | REPLACED_BY_P1
old effect: NONE | COMMITTED_UNRESOLVED | REALIZED_ROUTE_CONFORMANT
```

Finite product:

```text
2 × 2 × 3 = 12
```

Assertions:

```text
old PROMOTED + mapping replaced
→ remains PROMOTED historical fact

old NONTERMINAL + mapping replaced + no unresolved effect
→ SUPERSEDED

old NONTERMINAL + mapping replaced + committed unresolved effect
→ NONCURRENT_RECOVERY_PENDING

old non-current effect later proven realized
→ historical PROMOTED, not silent supersession
```

## Total finite coverage

```text
retained valid v32 baseline                 14,470
ADR-066 route-conformant realization          108
ADR-066 policy-drift/commitment recovery       96
ADR-067 supersession                           12
-------------------------------------------------
v34 total                                  14,686
```

## Static normative checks

The executable verifies, among other things:

- ADR numbering is contiguous `001..067`;
- provider terminal proof is `C → H → R → O`;
- candidate ancestry cannot bypass `PROVIDER_SUBMISSION`;
- DIRECT does not require actor attribution to Ruu;
- old authorization cannot cause a new effect after policy drift;
- `PROMOTED` is historical rather than a perpetual target-membership watch;
- PromotionUnit lifecycle includes `SUPERSEDED` and no longer contains generic `ABANDONED`;
- stale main-spec 30.36 wording is replaced by the ADR-062 no-projection closure;
- the residual ConvergenceUnit abandonment ambiguity is explicitly tracked as open 30.41 rather than hidden by a false no-backlog claim;
- generic development-validation states remain absent;
- Markdown code fences are balanced.

## Concrete Git primitive smokes

Six concrete mechanics are run:

```text
ADR-048 materialization                        PASS
ADR-050 restack                                PASS
DIRECT_TARGET_ADVANCE                          PASS
repository bootstrap                           PASS
canonical checkpoint                           PASS
provider route C→H→R→O                         PASS
```

The provider-route v2 smoke constructs an immutable candidate `C`, moves its base, computes a deterministic restacked provider head `H` with `C != H`, creates a squash-like provider final result `R` with `H != R`, and advances the target to `O` after `R`. It verifies that neither `C` nor `H` is in `O` ancestry while `R` is, matching the exact proof shape that ADR-065 could not represent.

## Conclusion

The hostile-audit defects in final promotion proof and stale PromotionUnit lifecycle are covered by explicit dimensions rather than by static prose alone. The previously passing v33 family is treated as an invalid model rather than accumulated as evidence. One separate hostile-audit issue remains intentionally open as backlog 30.41: ConvergenceUnit abandonment/disposition once an immutable PromotionGroup already references the lineage.
