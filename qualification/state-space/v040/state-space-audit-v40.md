# State-Space Audit v40 — ADR-075 observation strength and native-ref capability contract

- **Date:** 2026-09-08
- **Retained baseline:** v39 / 15,140 combinations
- **New ADR-075 combinations:** 284
- **Total:** **15,424 combinations — PASS**

## New dimensions

v40 adds finite coverage for:

1. the three observation-strength classes (`PRE_LINEARIZATION`, exact-state rediscovery, best-effort notification);
2. native-ref adapter/core preparation classification under managed/non-managed refs, mutation impact, observer coverage, witness strength and persistence;
3. independent positive `ABANDON | CONTINUATION | UNRESOLVED` proofs rather than `!continuation => abandon`;
4. capability-based ref-backend admissibility as a conjunction of pre-linearization coverage, veto/serialization, exact preimage, rename evidence, durable normalized witness and recovery;
5. `ReflogBaselineV1 = ENTRY(anchor) | EMPTY_PRESENT` versus absent evidence and coverage gaps;
6. canonical ancestry handling for replace refs, grafts and shallow boundaries.

## Executable result

```text
ADR-075 observation-strength family: 36 PASS
ADR-075 adapter/core preparation family: 96 PASS
ADR-075 positive-disposition-proof family: 54 PASS
ADR-075 backend-capability family: 64 PASS
ADR-075 reflog-baseline family: 18 PASS
ADR-075 canonical-ancestry family: 16 PASS
new combinations: 284 PASS
retained v39 baseline: 15140
v40 total: 15424 PASS
```

## Key safety assertions

```text
managed binding-ending mutation + no pre-linearization adapter coverage
→ backend nonconforming

managed binding-ending mutation + UNKNOWN witness
→ veto

TERMINAL_REMOVAL_PREPARED + committed outcome + intact observation integrity
→ ABANDON

RENAME_CARRY_PREPARED + committed outcome + valid successor + intact observation integrity
→ CONTINUATION

!ContinuationProof
→ never automatically ABANDON

non-disposition notification loss
→ rediscover exact current state
```

## Verdict

**PASS.** ADR-075 adds no state-space contradiction to the retained v39 baseline.
