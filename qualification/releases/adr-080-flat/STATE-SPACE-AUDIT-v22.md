# State-Space Audit v22 — ADR-053 durable session-independent review correction

## 1. Scope

This audit extends v21 after ADR-053 closes backlog 30.23. It revalidates every prior finite architecture family and adds explicit coverage for the review-correction boundary after a provider observes `CHANGES_REQUESTED`: durable exact-generation demand identity, idempotent provider-hook/global-sweep discovery, independence from originating/discovering session runtime identity, safe new-ContributionUnit authoring, and immutable PromotionGroup / stable ADR-049 submission continuity.

This remains a finite regression/state-machine audit. It does not claim to interpret arbitrary review prose, prove a particular agent runtime, or enumerate every Development System dispatch policy. No new Git DAG primitive is introduced by ADR-053; the existing ADR-048 materialization, ADR-050 restack, and ADR-052 DIRECT Git smokes remain the relevant concrete Git behavior checks.

## 2. ADR-053 properties exercised

The executable audit checks that:

1. the same exact reviewed submission revision/head + authoritative review generation/fingerprint yields one logical correction demand regardless of provider-hook, global-sweep, or both discovery paths;
2. stale/superseded review generations do not authorize new dispatch;
3. originating coding-session liveness and unrelated discovering-session identity are absent from the dispatch-authorization predicate;
4. a correction may use a restored or new continuation session without changing Git/convergence/publication identity;
5. implementation work uses newly provisioned ContributionUnits; a terminal ContributionUnit is not reopened and the provider submission ref is never an authoring surface;
6. existing PromotionGroup-member state changes keep the immutable group and, with unchanged destination, preserve ADR-049 logical submission/provider PR identity while exact PromotionUnit/head/revision changes;
7. a genuinely new ConvergenceUnit requires a different group; mutating the old closed group is never conforming;
8. ADR-053 remains subordinate to External Control Plane semantic authority, ADR-036 global sweep, ADR-046 immutable grouping, and ADR-049 exact submission-revision guards.

## 3. New finite families

ADR-053 adds:

```text
review_correction_demand_idempotence: 36
review_correction_session_independence: 72
review_correction_authoring_boundary: 18
review_correction_group_submission_continuity: 12
```

Every v21 family is re-run as well.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-053**;
- main §30 marks **30.23 resolved by ADR-053** and the open backlog no longer lists 30.23;
- the External Control Plane contract allows provider-hook or later global-sweep discovery of the same idempotent correction demand;
- original session survival is not required and a new continuation session is explicitly supported;
- main invariants 63A–63D preserve exact-generation identity, session/trigger non-authority, new-ContributionUnit authoring, same-group PR continuity, and new-scope group separation;
- ADR-049 explicitly carries the cross-session correction amendment;
- ADR-046 immutable group membership is not weakened;
- all ADR-052 DIRECT, ADR-051 capability, ADR-050 restack, ADR-049 submission, ADR-048 materialization, and earlier architecture families remain intact.

## 5. Result

Executable result:

```text
Ruu state-space audit v22: PASS
changed/revalidated finite combinations evaluated: 15,582
markdown artifacts statically cross-checked: 78
```

The full per-family counts are recorded in `state-space-audit-v22.txt`.

Retained concrete Git smoke results:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
```

ADR-053 adds no new Git mutation primitive, so no separate Git smoke is required for its control-plane/session-dispatch semantics.

The expected boundary is:

```text
provider CHANGES_REQUESTED generation
  ├─ provider hook
  └─ any later Ruu global sweep
          ↓
Ensure one durable exact ReviewCorrectionDemand
          ↓
External Control Plane fenced/idempotent dispatch
          ↓
restore old coding session OR start new continuation session
          ↓
review feedback becomes development input
          ↓
discover/reactivate required existing ConvergenceUnit scope(s)
          ↓
new ContributionUnit writer work only
          ↓
normal convergence → READY_INTERNAL
          ↓
same immutable PromotionGroup resolves to new exact PromotionUnit(s)
          ↓
ADR-049 same submission/provider PR revision when logical key unchanged
```

A genuinely new ConvergenceUnit leaves this ordinary same-ship correction path and requires a different/superseding PromotionGroup.
