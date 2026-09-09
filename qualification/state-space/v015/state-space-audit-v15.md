# Ruu — State-Space / Global Consistency Audit v15

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-045
- **Trigger:** ADR-045 closes backlog 30.16 by making PromotionUnit definitions immutable, exact-state-bound, content-addressed sets whose identity excludes topology, policy, lifecycle, submission revision, and higher-level semantic identity.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete architecture after the concrete PromotionUnit declaration/identity contract was fixed.

ADR-045 adds the following correctness questions to the ADR-044 baseline:

```text
1. Is PromotionUnit identity independent of member ordering?
2. Does the same exact member set always produce the same identity, including retries and later redeclarations?
3. Does any exact member-state change necessarily produce a different PromotionUnit identity?
4. Can lifecycle, topology, target/mode/policy, provider revision, or semantic labels accidentally change PromotionUnit identity?
5. Can a structurally valid immutable PromotionUnit exist while current promotion eligibility is blocked/stale/waiting?
6. Does any stored identity/definition mismatch fail closed rather than mutate/rebind the object?
```

The audit remains a factorized finite-state consistency check. It does not claim to enumerate the unbounded Git DAG/provider state space or solve the still-open multi-source projection algorithm of backlog 30.18.

## 2. Revalidated ADR-044 baseline

The v15 executable reruns every v14 family unchanged, including:

```text
promotion-policy authoritative constraint composition
no runtime/local policy bypass
trusted-target policy baseline
factual contradiction signaling
immediate pre-mutation policy currentness
cache/TTL non-authority
non-atomic provider drift boundary
```

It also reruns all earlier ContributionUnit, ConvergenceUnit, verification, review, provider, coordination, recovery, and global fixed-point families.

## 3. Content-addressed PromotionUnit identity

`promotion_unit_content_address_identity` exercises canonical exact member sets against lifecycle, topology, policy mode, semantic labels, member permutations, and exact-state changes.

Reference v1 identity in the executable audit uses the ADR-045 rule:

```text
promotion_unit_id
= SHA-256(
    "Ruu:PromotionUnit:v1" domain
    + unambiguous length-delimited canonical(sorted(exact_member_refs))
  )
```

Validated:

```text
[A@x, B@y]
[B@y, A@x]
→ same identity

same exact members
+ different lifecycle/topology/policy/semantic label
→ same identity

[A@x, B@y]
[A@x, B@z]
→ different identity

empty set
or duplicate-member declaration
→ invalid declaration
```

Result: **218 combinations/cases**.

## 4. Structural declaration validity versus current eligibility

`promotion_unit_structural_vs_eligibility` varies:

```text
member-set form: valid | invalid
exact refs: valid | invalid
stored content identity: match | mismatch
member readiness: yes | no
verification evidence: valid | missing
EffectivePromotionPolicy: CURRENT | STALE
topology prerequisites: compatible | blocked
other blocker/recovery state: clear | blocked
```

Result: **256 combinations**.

Validated:

```text
structurally invalid declaration
→ never eligible

valid immutable declaration
+ stale/not-ready/blocked current conditions
→ object remains valid
→ promotion is not currently eligible

valid definition
+ exact ready members
+ valid evidence
+ CURRENT policy
+ compatible topology
+ no blocker
→ may become READY_FOR_PROMOTION subject to the rest of the architecture guards
```

This verifies that exact identity is not overloaded with current workflow/readiness state.

## 5. Redeclaration idempotence and lifecycle independence

`promotion_unit_redeclaration_idempotence` varies the original PromotionUnit lifecycle, redeclaration timing, and whether the exact member set is unchanged or contains a new exact member state.

Result: **16 combinations**.

Validated:

```text
same exact member set
→ same PromotionUnit
→ even after PROMOTED

changed exact member state
→ different PromotionUnit
```

Therefore retries do not need a caller-supplied PromotionUnit UUID/idempotency key, and a completed exact promotion object cannot be duplicated merely by redeclaring the same exact state set.

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
- ADR-043 promotion-policy authority/composition/contradiction/baseline invariants;
- ADR-044 immediate policy-currentness/cache/provider-drift invariants.

Total finite combinations evaluated: **13,082**.

## 7. Static architecture consistency checks

The static audit verifies at least:

1. ADR numbering is contiguous from **001 through 045**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.16 resolved by ADR-045**.
4. `OPEN-DESIGN-BACKLOG.md` begins its remaining numbered promotion items at **30.17**.
5. Main/core contract define PromotionUnit as a non-empty immutable exact-state set with content-addressed identity.
6. Main invariants require deterministic identity, immutability, idempotent redeclaration, topology separation, and structural-validity/eligibility separation.
7. `target intent`, dependency/stack parent, and semantic-readiness-token fields are absent from the current main PromotionUnit schema.
8. `EXTERNAL-CONTROL-PLANE-CONTRACT.md` exposes `DeclarePromotionUnit(members)` and keeps topology declarations separate.
9. ADR-027, ADR-039, ADR-042, and ADR-044 are amended consistently with ADR-045.
10. ADR-043/ADR-044 policy authority/currentness remains separate from PromotionUnit identity.
11. Backlog 30.17–30.26 remains open; ADR-045 does not accidentally resolve default mapping, projection, restacking, provider capability discovery, retirement, compensation, or repository provisioning.

## 8. Result

The executable v15 audit reports **PASS** with **13,082 finite combinations**.

The final static audit cross-checks all current Markdown architecture artifacts.

## 9. Interpretation

The resulting identity boundary is now:

```text
External Control Plane
  decides semantic grouping
  ↓
DeclarePromotionUnit(Set<ExactConvergenceStateRef>)
  ↓
canonical immutable exact member set
  ↓
versioned/domain-separated SHA-256
  ↓
PromotionUnit identity
```

Separately:

```text
PromotionTopology
→ relationships among PromotionUnit refs

EffectivePromotionPolicy
→ target/mode/publication authorization

Promotion lifecycle / submission revision
→ current progression/provider representation

Development System semantic identity
→ task/feature/work-package correlation outside Ruu
```

And explicitly:

```text
same exact state set
= same PromotionUnit

new exact source state
= new PromotionUnit

policy/topology/lifecycle change
≠ new PromotionUnit

structurally valid PromotionUnit
≠ currently eligible promotion
```

Backlog 30.16 is therefore closed without coupling Ruu identity to external task semantics or reopening the promotion-policy bypass problem solved by ADR-043.
