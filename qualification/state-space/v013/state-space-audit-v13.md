# Ruu — State-Space / Global Consistency Audit v13

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-043
- **Trigger:** ADR-043 closes backlog 30.14 by replacing promotion-policy source precedence with authoritative constraint composition, trusted-target repo-policy baselines, zero-onboarding built-in closure, and factual contradiction signaling without remediation advice.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete current architecture after promotion-policy authority/composition semantics were fixed.

ADR-043 adds four correctness questions to the prior ADR-042 baseline:

```text
1. Can provider/org/repo policy inputs be composed without a silent precedence winner?
2. Can local config or a caller/human/agent/orchestrator bypass the resulting policy?
3. Can a candidate change the repository policy that governs its own promotion?
4. Does a contradiction expose enough exact factual evidence externally without Ruu prescribing the remedy?
```

The audit remains a factorized finite-state consistency check. It does not claim to enumerate the unbounded Git DAG/provider state space.

## 2. Revalidated ADR-042 runtime baseline

The v13 executable reruns all ADR-042 families unchanged, including:

```text
OS physical ownership versus SQLite durable fencing
ACTIVE→IDLE release / concurrent-demand handshake
Operation→Attempt→Observation→Adoption eligibility
external-effect crash windows and exact recovery
no external work inside SQLite transactions
live-but-hung process behavior
recovery-resource GC eligibility
stable repository identity across locator relocation
schema initialization/migration fail-closed behavior
current-state reconciliation independent of old workflow position
```

The previously accepted single-host reconciler/CoordinationStore model therefore remains intact.

## 3. Authoritative promotion-policy constraint composition

`promotion_policy_constraint_composition` varies:

```text
provider capability space:
  DIRECT_ONLY | PR_ONLY | BOTH

provider governance:
  NONE | REQUIRE_DIRECT | REQUIRE_PR

organization governance:
  NONE | REQUIRE_DIRECT | REQUIRE_PR

trusted repo policy:
  NONE | REQUIRE_DIRECT | REQUIRE_PR
```

Result: **81 combinations**.

For every combination, the audit intersects the authoritative admissible sets rather than selecting a source by precedence.

Validated:

```text
non-empty intersection
→ policy dimension is satisfiable
→ built-in rule may choose only within the remaining admissible set

empty intersection
→ CONTRADICTORY
→ no EffectivePromotionPolicy for that dimension
→ no promotion authorization
```

In particular:

```text
provider {DIRECT, PR} + repo REQUIRE_PR
→ PR

provider REQUIRE_PR + repo REQUIRE_DIRECT
→ CONTRADICTORY
→ no silent "provider wins" normalization
```

## 4. Runtime/local policy bypass irrelevance

`promotion_policy_runtime_bypass_irrelevance` varies:

```text
authoritative policy result:
  DIRECT | PR | CONTRADICTORY

explicit local config:
  NONE | DIRECT | PR

runtime request:
  NONE | DIRECT | PR

caller class:
  HUMAN | AGENT | ORCHESTRATOR
```

Result: **81 combinations**.

The authoritative policy result is invariant under all local/runtime/caller combinations.

Validated:

```text
repo/provider authority says PR
+ human asks DIRECT
→ policy remains PR

repo/provider authority is CONTRADICTORY
+ any local/runtime input
→ remains CONTRADICTORY
```

Changing promotion behavior requires changing an authoritative policy/governance source and revalidating it. There is no per-invocation promotion-policy bypass.

## 5. Trusted target policy baseline / no candidate self-authorization

`trusted_target_policy_baseline` varies:

```text
current target policy:
  DIRECT | PR

candidate policy content:
  UNCHANGED | DIRECT | PR

candidate authoritative on target:
  false | true
```

Result: **12 combinations**.

Validated:

```text
current promotion
→ governed by policy from current trusted target baseline
→ candidate-only policy content is irrelevant to its own authorization

candidate later becomes authoritative target state
→ its policy may govern a subsequent promotion after refresh/revalidation
```

This closes the self-escalation path in which a candidate could otherwise change `PR → DIRECT` and use that same unadopted change to authorize itself.

## 6. Policy-contradiction signal boundary

`policy_contradiction_signal_boundary` varies:

```text
policy state:
  CURRENT | CONTRADICTORY

factual provenance:
  COMPLETE | INCOMPLETE

remediation advice:
  ABSENT | PRESENT
```

Result: **8 combinations**.

A valid externally actionable contradiction signal requires:

```text
CONTRADICTORY
+ complete factual provenance
+ no remediation advice
```

Validated:

```text
exact conflicting facts/constraints + source revisions
→ valid diagnostic surface

recommended_fix / resolution_candidates / ranked remediation present
→ invalid Ruu responsibility boundary
```

The external Development System/operator decides what, if anything, should change.

## 7. Zero-onboarding default closure

ADR-043's built-in policy rule is exercised inside the constraint-composition family.

The baseline property is:

```text
no explicit repo policy
+ DIRECT admissible
+ no authoritative constraint requiring indirect promotion
→ built-in rule resolves promotion_mode = DIRECT
```

while:

```text
provider/governance leaves only PR admissible
→ effective promotion_mode = PR
```

Therefore:

```text
no repo policy file
≠ MISSING policy
```

`MISSING` means a complete effective policy cannot be derived from authoritative inputs plus built-in rules.

## 8. Revalidated prior architecture families

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
- ADR-042 external-effect recovery, repository relocation, schema, and GC invariants.

Total finite combinations evaluated: **12,452**.

## 9. Static architecture consistency checks

The static audit verifies at least:

1. ADR numbering is contiguous from **001 through 043**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.14 resolved by ADR-043**.
4. `OPEN-DESIGN-BACKLOG.md` no longer lists item 14 as open and explicitly records ADR-043 closure.
5. Main §4.16/§7.3/§28.10/§33.3 use authoritative constraint composition rather than a generic precedence model.
6. Main invariants include explicit no-runtime-bypass, trusted-target-policy, visible-contradiction, and zero-onboarding-default rules.
7. ADR-043 states that local config and human/agent/orchestrator runtime input cannot change promotion authorization.
8. ADR-043 binds repo-committed policy to the trusted authoritative target baseline.
9. ADR-043 and the External Control Plane contract explicitly reject `recommended_fix` / `resolution_candidates` as `ruu` output responsibility.
10. ADR-026 and ADR-039 are amended consistently.
11. All ADR-042 coordination/recovery invariants remain present and unchanged.

## 10. Result

The executable v13 audit reports **PASS** with **12,452 finite combinations**.

The final static audit cross-checks **59 Markdown artifacts**.

## 11. Interpretation

The promotion-policy path is now:

```text
provider capabilities/current facts
+ provider governance
+ organization governance
+ trusted target-baseline repository policy
        ↓
compose authoritative constraints
        ↓
unsatisfiable?
  yes → CONTRADICTORY
        → promotion blocked
        → exact factual external diagnostic
        → no remediation advice from Ruu

  no  → built-in rules fill only unresolved dimensions
        ↓
EffectivePromotionPolicy
        ↓
fingerprint + CURRENT revalidation
        ↓
promotion may proceed subject to all other guards
```

And:

```text
local config / human flag / agent request / orchestrator request
→ cannot alter promotion authorization

candidate-only policy change
→ cannot govern that candidate's promotion

no explicit repo policy file
→ does not require onboarding
→ deterministic built-in rules can still derive a complete current policy
```

Backlog 30.14 is closed without weakening fail-closed behavior or moving governance decisions into `ruu`.
