# State-Space Audit v23 — ADR-054 PromotionUnit completion / ConvergenceUnit closure-retirement separation

## 1. Scope

This audit extends v22 after ADR-054 closes backlog 30.24. It revalidates every prior finite architecture family and adds explicit coverage for the distinction between exact repository-local PromotionUnit completion, ConvergenceUnit semantic closure, operational retirement, GC eligibility, and physical retention.

This remains a finite regression/state-machine audit. It does not define backlog 30.25 compensation semantics, arbitrary future terminal dispositions, or verification-evidence retention policy. ADR-054 introduces no new Git DAG mutation primitive; the existing ADR-048 materialization, ADR-050 restack, and ADR-052 DIRECT CAS+FF smokes remain the concrete Git behavior checks.

## 2. ADR-054 properties exercised

The executable audit checks that:

1. `PromotionUnit PROMOTED` alone never authorizes ConvergenceUnit closure when its relevant PromotionGroup remains `PARTIALLY_PROMOTED`/otherwise nonterminal;
2. a current review-correction/authoring obligation blocks ConvergenceUnit semantic closure even when every local promotion snapshot is otherwise terminal;
3. every relevant PromotionGroup referencing a ConvergenceUnit must be terminally settled before ConvergenceUnit `PROMOTED` is eligible;
4. ConvergenceUnit `PROMOTED` is distinct from `RETIRED`;
5. `RETIRED` requires terminal effects/adoption plus zero correctness-critical recovery/resource dependency;
6. retirement only establishes possible GC eligibility and never implies physical deletion;
7. v1 `KEEP` retention forbids automatic deletion even after GC eligibility;
8. the new retirement guard composes with ADR-053 correction continuation, ADR-042 recovery-resource lifecycle, ADR-046 immutable grouping, and ADR-014 cross-repository partial progress without pre-deciding 30.25.

## 3. New finite families

ADR-054 adds:

```text
promotion_unit_completion_vs_convergence_closure: 16
convergence_closure_all_relevant_groups: 12
convergence_retirement_recovery_barrier: 24
retired_ref_gc_retention_separation: 24
```

Every v22 family is re-run as well.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-054**;
- main §30 marks **30.24 resolved by ADR-054** and the open backlog no longer lists 30.24;
- main invariants 63E–63G preserve exact-snapshot completion vs lineage closure vs retirement/retention separation;
- cross-repository `PARTIALLY_PROMOTED` is explicitly nonterminal for ConvergenceUnit semantic closure;
- ADR-053 same-ship review correction remains possible until terminal settlement;
- ConvergenceUnit `PROMOTED` forbids later same-lineage ContributionUnit attachment/reopen;
- `RETIRED → GC_ELIGIBLE` remains distinct from physical deletion and built-in v1 retention is `KEEP`;
- ADR-049/provider submission refs remain non-authoritative audit identity and verification-evidence retention remains separately open under 30.28;
- ADR-014/021/039/042/046/049/053 and the External Control Plane contract carry the ADR-054 amendment consistently;
- all ADR-053 review-correction, ADR-052 DIRECT, ADR-051 capability, ADR-050 restack, ADR-049 submission, ADR-048 materialization, and earlier architecture families remain intact.

## 5. Result

Executable result:

```text
Ruu state-space audit v23: PASS
changed/revalidated finite combinations evaluated: 15,658
markdown artifacts statically cross-checked: 80
```

The full per-family counts are recorded in `state-space-audit-v23.txt`.

Retained concrete Git smoke results:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
```

ADR-054 adds no new Git mutation primitive, so no separate Git smoke is required for its lifecycle/retention semantics.

The expected boundary is:

```text
repository-local exact PromotionUnit P
        ↓ terminal publication
P = PROMOTED
        ↓
DO NOT infer ConvergenceUnit closure
        ↓
all relevant PromotionGroups terminally settled
+ no current ReviewCorrectionDemand/authoring/reconciliation reopen path
        ↓
ConvergenceUnit = PROMOTED
        ↓ semantic lineage closed; later work needs new CU
terminal effects durably adopted
+ no correctness-critical recovery/resource dependency
        ↓
ConvergenceUnit = RETIRED
        ↓
historical internal ref may be GC_ELIGIBLE
        ↓
built-in v1 retention KEEP → no automatic deletion
```

Detailed cross-repository compensation/roll-forward terminal outcomes remain backlog 30.25 and can later plug into the `terminally settled` predicate without changing this retirement boundary.
