# State-Space Audit v45 — ADR-080 local/remote/provider observation authority

- **Date:** 2026-09-08
- **Retained baseline:** v44 / 16,124 combinations
- **New ADR-080 combinations:** 256
- **Total:** **16,380 combinations — PASS**

## New dimensions

v45 adds finite coverage for:

1. strict source-domain authority between `LOCAL_GIT`, `REMOTE_GIT`, and optional `PROVIDER`;
2. remote-tracking refs as non-authoritative caches versus direct current remote observation;
3. exact expected-old remote mutation and ambiguous-ack recovery by re-observation;
4. provider optionality and provider-required capability blocking;
5. webhook delivery as wakeup/positive evidence without negative/completeness authority;
6. duplicate/redelivered/delayed provider occurrence idempotency;
7. cross-source chronology from exact source-owned identities rather than wall clocks;
8. remote publication topology never manufacturing local managed-binding `CONTINUATION | ABANDON`.

## Executable result

```text
ADR-080 source-domain authority family: 32 PASS
ADR-080 remote-cache/currentness family: 32 PASS
ADR-080 remote-CAS/recovery family: 32 PASS
ADR-080 provider-optionality family: 32 PASS
ADR-080 webhook-positive-evidence family: 32 PASS
ADR-080 delivery-idempotency family: 32 PASS
ADR-080 cross-source-causality family: 32 PASS
ADR-080 remote-artifact-semantics family: 32 PASS
new combinations: 256 PASS
retained v44 baseline: 16124
v45 total: 16380 PASS
```

## Key assertions

```text
LOCAL_GIT causal observer
→ local managed-binding mutations only
→ never remote/provider authority

refs/remotes/*
→ local cache only
→ current remote-required transition uses direct remote authority

provider-free route + bare Git remote
→ valid REMOTE_GIT-only progression

provider-required route + no provider capability
→ BLOCKED/UNSUPPORTED
→ never emulate PR/review/queue semantics with Git refs

webhook absent
→ no negative inference

webhook authenticated + exact adapter semantics
→ may persist positive provider-scoped historical evidence

webhook duplicate/late/redelivery
→ evidence idempotent
→ never duplicate semantic Adoption

cross-source chronology required
+ no exact source-owned order proof
→ fail closed

current-state-only transition
+ exact current facts sufficient
→ no historical chronology requirement

remote delete/create/rename-like topology
→ publication/submission reconciliation only
→ never local managed-binding ABANDON/CONTINUATION authority
```

## Verdict

**PASS.** ADR-080 closes 30.55 and the 30.49 umbrella while keeping local causal observation narrow, remote Git provider-independent, provider workflow authority optional/source-scoped, and webhook transport non-authoritative for completeness.
