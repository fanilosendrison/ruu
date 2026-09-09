# Ruu — State-Space / Global Consistency Audit v14

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-044
- **Trigger:** ADR-044 closes backlog 30.15 by making immediate authoritative pre-mutation revalidation the basis of promotion-policy currentness, while making cache/TTL non-authorizing and explicitly modeling the non-atomic provider drift boundary.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete architecture after promotion-policy currentness/refresh semantics were fixed.

ADR-044 adds three correctness questions to the ADR-043 baseline:

```text
1. Can a policy-sensitive promotion mutation ever rely on cache age/TTL instead of immediate authoritative revalidation?
2. Does any movement of an authoritative policy anchor invalidate the old policy snapshot before mutation?
3. When provider governance check + mutation cannot be atomic, is concurrent drift handled as exact provider outcome/current-state evidence rather than hidden retry/repair authority?
```

The audit remains a factorized finite-state consistency check. It does not claim to enumerate the unbounded Git DAG/provider state space.

## 2. Revalidated ADR-043 policy baseline

The v14 executable reruns all ADR-043 policy families unchanged:

```text
authoritative promotion-policy constraint composition
runtime/local/caller bypass irrelevance
trusted target policy baseline / no candidate self-authorization
policy-contradiction signal boundary
zero-onboarding built-in closure
```

It also reruns all earlier current runtime, convergence, verification, review, provider, coordination, and recovery families.

## 3. Policy-sensitive pre-mutation currentness

`policy_pre_mutation_currentness` varies:

```text
trusted target/repo-policy anchor: UNCHANGED | CHANGED
provider governance observation: UNCHANGED | CHANGED
provider capability/current-fact observation: UNCHANGED | CHANGED
immediate pre-mutation revalidation: DONE | NOT_DONE
cache state: MISS | TTL_FRESH | TTL_EXPIRED
operation class: POLICY_SENSITIVE | LOCAL_NON_POLICY
```

Result: **96 combinations**.

Validated for policy-sensitive promotion mutations:

```text
revalidation DONE
+ every authoritative anchor unchanged
→ current policy snapshot may authorize, subject to all other guards

revalidation NOT_DONE
→ no promotion authorization

any authoritative anchor CHANGED
→ old snapshot STALE
→ no promotion authorization from the old snapshot
```

The result is invariant under cache state.

Local candidate materialization/verification does not acquire promotion authorization merely by possessing a current policy snapshot; its own exact-state/verification rules remain separate.

## 4. Cache/TTL non-authority

`policy_cache_non_authority` varies:

```text
cache age: NEW | WITHIN_TTL | EXPIRED
authoritative source state: UNCHANGED | CHANGED
fresh revalidation: DONE | NOT_DONE
```

Result: **12 combinations**.

Validated:

```text
TTL fresh + no fresh revalidation
→ NOT CURRENT

source changed + any cache age
→ NOT CURRENT

fresh revalidation + unchanged authoritative source
→ may be CURRENT subject to the rest of the policy snapshot
```

Therefore cache/TTL remains a performance mechanism only.

## 5. Non-atomic provider drift boundary

`nonatomic_provider_drift_boundary` varies:

```text
provider primitive: ATOMIC | NON_ATOMIC
drift after pre-check: NO | YES
provider outcome: ACCEPTED | REJECTED
exact post-operation observation: YES | NO
automatic repair/remediation: ABSENT | PRESENT
```

Result: **32 combinations**.

Validated:

```text
provider ACCEPTED
+ exact post-operation observation
+ no automatic repair layer
→ result may enter ordinary exact adoption checks

provider REJECTED
+ exact post-operation observation
+ no automatic repair layer
→ factual blocking/current-state evidence

missing exact post-operation observation
→ neither success adoption nor authoritative factual blocking classification is complete

automatic repair/remediation present
→ violates the Ruu responsibility boundary
```

For the specific non-atomic race:

```text
fresh pre-check
→ governance/capability drifts
→ provider rejects
→ exact rejection/current-state observation
→ factual external signal
→ no autonomous policy/governance repair
```

## 6. Revalidated prior architecture families

The executable audit reruns all current prior families, including:

- ContributionUnit identity/cardinality/lifecycle and artifact independence;
- managed checkpoint CAS and exact-state continuity;
- External Control Plane responsibility boundary;
- exact `RECONCILIATION_REQUIRED` semantics;
- mutation-boundary candidate attribution;
- convergence-demand coalescing, fencing, and release race handling;
- ConvergenceUnit grouping, eager integration, sealing/readiness;
- global managed-obligation coverage and external wait refresh;
- state-producing full verification, evidence reuse/fixed point/capacity;
- review request/revision invalidation;
- internal integration verification;
- ADR-042 external-effect recovery, repository relocation, schema, and GC invariants;
- ADR-043 promotion-policy authority/composition/contradiction/baseline invariants.

Total finite combinations evaluated: **12,592**.

## 7. Static architecture consistency checks

The static audit verifies at least:

1. ADR numbering is contiguous from **001 through 044**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.15 resolved by ADR-044**.
4. `OPEN-DESIGN-BACKLOG.md` begins its remaining open promotion items at 30.16.
5. Main §4.16, §7.3, §22.7, §30.15, and invariants use immediate authoritative revalidation rather than TTL-based authorization.
6. ADR-044 explicitly states that cache/TTL cannot establish `CURRENT`.
7. ADR-044 invalidates a policy snapshot on movement of the trusted target/repo-policy anchor or mutable provider/org authoritative observations.
8. ADR-044 and the External Control Plane contract surface concurrent provider drift/rejection factually and forbid autonomous remediation.
9. ADR-026/ADR-042/ADR-043 are amended consistently.
10. All ADR-043 and ADR-042 correctness families remain present.

## 8. Result

The executable v14 audit reports **PASS** with **12,592 finite combinations**.

The final static audit cross-checks **61 Markdown artifacts**.

## 9. Interpretation

The current promotion-policy path is now:

```text
authoritative source observations
        ↓
ADR-043 constraint composition
        ↓
EffectivePromotionPolicy snapshot + fingerprint
        ↓
ordinary global-sweep refresh
        ↓
policy-sensitive promotion mutation pending
        ↓
IMMEDIATE re-observation/revalidation of every mutable authoritative source
        ↓
source anchor changed?
  yes → old snapshot STALE
        → recompute
        → contradiction? ADR-043 factual block

  no  → mutation may proceed subject to all other guards
        ↓
provider check+mutation atomic?
  yes → provider primitive supplies the boundary
  no  → bounded mutation
        → provider enforcement/rejection
        → exact post-operation observation
        → factual current-state result
```

And explicitly:

```text
TTL fresh
≠ CURRENT

cache hit
≠ authorization

provider rejection after concurrent drift
≠ permission to retry differently
≠ instruction to change governance
```

The architectural decision is therefore closed without requiring impossible distributed atomicity or weakening the fail-closed policy model.
