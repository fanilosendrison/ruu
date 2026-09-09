# State-Space Audit v41 — ADR-076 native witness provenance and semantic idempotency

- **Date:** 2026-09-08
- **Retained baseline:** v40 / 15,424 combinations
- **New ADR-076 combinations:** 164
- **Total:** **15,588 combinations — PASS**

## New dimensions

v41 adds finite coverage for:

1. separation of native witness evidence from managed `Operation` identity;
2. optional Attempt correlation that never becomes authorization;
3. duplicate delivery versus genuinely distinct active native occurrences;
4. one unresolved correctness-critical preparation per current binding generation;
5. lost/duplicate outcome delivery with exact-state recovery;
6. repeated scans that cannot synthesize missing causal preparation;
7. coalesced/lost/reordered wakeups as non-semantic signals;
8. exactly-once authoritative adoption/disposition under logical current-state guards.

## Executable result

```text
ADR-076 witness-vs-operation family: 16 PASS
ADR-076 non-authoritative-provenance family: 16 PASS
ADR-076 active-occurrence-idempotency family: 16 PASS
ADR-076 outcome-replay-recovery family: 48 PASS
ADR-076 scan-nonmanufacture family: 36 PASS
ADR-076 wakeup-coalescing family: 16 PASS
ADR-076 logical-exactly-once family: 16 PASS
new combinations: 164 PASS
retained v40 baseline: 15424
v41 total: 15588 PASS
```

## Key safety assertions

```text
native witness
→ never manufactures managed Operation

originating_attempt_id present or absent
→ never changes current authorization result

same active native occurrence delivered repeatedly
→ same effective preparation/decision

distinct competing preparation for same current binding generation
→ veto/serialize until current preparation resolves

exact-state scan without causal preparation
→ cannot synthesize TERMINAL_REMOVAL_PREPARED or RENAME_CARRY_PREPARED

lost outcome callback
→ exact-state recovery from durable PREPARED when proof is sufficient
→ otherwise UNRESOLVED

wakeup duplication/loss/reordering
→ no semantic transition

Operation/binding-generation stale replay
→ current CAS/generation guards prevent duplicate authoritative adoption
```

## Verdict

**PASS.** ADR-076 adds no state-space contradiction to the retained v40 baseline.
