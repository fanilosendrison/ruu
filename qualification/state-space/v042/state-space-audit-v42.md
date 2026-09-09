# State-Space Audit v42 — ADR-077 observer ownership, mutation-engine boundary, and coverage epochs

- **Date:** 2026-09-08
- **Retained baseline:** v41 / 15,588 combinations
- **New ADR-077 combinations:** 152
- **Total:** **15,740 combinations — PASS**

## New dimensions

v42 adds finite coverage for:

1. repository-common versus worktree-local observer scope for shared managed refs;
2. non-destructive hook/config ownership and supported composition surfaces;
3. functional attestation as a prerequisite to managed-authoring admission;
4. Git-core V1 mutation-engine conformance versus alternative/direct writers;
5. unwitnessed managed-binding mutation and explicit ECP recovery boundaries;
6. coverage gaps/repair as distinct epochs rather than retroactive trust;
7. clone/recreation/reactivation requiring re-attestation;
8. expected-state/CAS install/upgrade/remove of owned observer artifacts;
9. hook ordering/veto outcomes without allowing missing required persistence to commit silently.

## Executable result

```text
ADR-077 repository-common-coverage family: 16 PASS
ADR-077 ownership-composition family: 20 PASS
ADR-077 admission-attestation family: 12 PASS
ADR-077 mutation-engine-boundary family: 20 PASS
ADR-077 unwitnessed-recovery family: 16 PASS
ADR-077 coverage-epoch family: 24 PASS
ADR-077 recreation-reattestation family: 16 PASS
ADR-077 owned-install-CAS family: 12 PASS
ADR-077 hook-order-persistence family: 16 PASS
new combinations: 152 PASS
retained v41 baseline: 15588
v42 total: 15740 PASS
```

## Key safety assertions

```text
worktree-local observer + shared managed ref
→ insufficient coverage

foreign hook/config surface
→ never overwritten merely to obtain coverage

managed write + no ACTIVE functional attestation
→ admission blocked

conforming Git-core/adapter + witness
→ normal native managed-ref path

unwitnessed managed-binding change
→ integrity failure
→ no synthesized CONTINUATION/ABANDON

explicit generation-bound ECP recovery + compatible exact state
→ exceptional recovery may proceed

coverage gap + later repair
→ new epoch
→ old gap remains untrusted

clone/recreate/reactivate
→ prior ACTIVE coverage not inherited without re-attestation

owned observer install/upgrade/remove
→ expected-state guarded

transaction commit lacking required observer call/persistence
→ coverage/persistence violation, never valid disposition
```

## Verdict

**PASS.** ADR-077 adds no state-space contradiction to the retained v41 baseline.
