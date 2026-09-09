# State-Space Audit v44 — ADR-079 minimal rejection, protection filtering, and exact authoring admission

- **Date:** 2026-09-08
- **Retained baseline:** v43 / 15,868 combinations
- **New ADR-079 combinations:** 256
- **Total:** **16,124 combinations — PASS**

## New dimensions

v44 adds finite coverage for:

1. rejecting only correctness-critical cessation/replacement candidates whose safety cannot be established;
2. conservative `ManagedRefProtectionFilter` negative acceleration and degraded fallback;
3. all-or-nothing crash-durable preparation batches for one native ref transaction;
4. post-PREPARED outcome recovery and advisory delivery loss without retroactive Git rejection;
5. exact `RefAdmissionBarrier` ordering around authoritative binding publication;
6. crash states across filter/barrier/binding/release/handoff phases;
7. exact initial worktree topology and exclusive pre-handoff authority;
8. native-Git → CoordinationStore live-lock ordering;
9. separation of observer coverage gaps, filter degradation, and successfully vetoed critical persistence failure.

## Executable result

```text
ADR-079 minimal-rejection family: 32 PASS
ADR-079 protection-filter family: 32 PASS
ADR-079 preparation-batch family: 32 PASS
ADR-079 outcome-advisory family: 32 PASS
ADR-079 ref-admission family: 32 PASS
ADR-079 admission-crash family: 32 PASS
ADR-079 initial-handoff family: 32 PASS
ADR-079 lock-order family: 16 PASS
ADR-079 failure-classification family: 16 PASS
new combinations: 256 PASS
retained v43 baseline: 15868
v44 total: 16124 PASS
```

## Key assertions

```text
no cessation/replacement candidate
→ allow despite advisory/observation persistence health

trustworthy negative protection-filter result
→ allow without managed-authority lookup

filter untrusted
→ never treat as empty
→ fallback to authoritative classification

current managed critical transition
→ complete crash-durable preparation batch before allow

PREPARED durable + outcome callback/persistence lost
→ allow/reconcile; never retroactive veto

candidate branch/worktree
→ not managed and not producer-writable yet

filter/protection safe
→ exact native RefAdmissionBarrier
→ exact topology revalidation
→ binding CURRENT while barrier held
→ release barrier
→ producer authority handoff
→ first managed write

live lock order
→ Git/native exclusion before CoordinationStore
→ never live CoordinationStore lock while waiting for corresponding Git lock

observer reached + filter degraded
→ coverage still active

observer reached + critical persistence failure + veto
→ coverage worked; not a coverage gap
```

## Verdict

**PASS.** ADR-079 closes 30.54 while reducing the fail-closed surface to the minimal causal class and keeping initial managed-authoring admission race-safe.
