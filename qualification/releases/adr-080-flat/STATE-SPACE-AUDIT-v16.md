# State-Space Audit v16 — ADR-046 PromotionGroup Resolution

## 1. Scope

This audit extends v15 after ADR-046 closes backlog 30.17. It revalidates the existing finite architecture families and adds explicit coverage for the durable pre-exact PromotionGroup boundary between logical ConvergenceUnits and ADR-045 exact-state PromotionUnits.

This is a finite regression/state-machine audit, not a proof over arbitrary Git DAGs or provider implementations.

## 2. ADR-046 properties exercised

The executable audit checks:

1. `PromotionGroupDefinition` is a non-empty unordered unique closed set of canonical `(repository_id, convergence_unit_id)` refs.
2. V1 PromotionGroup identity is domain-separated/versioned SHA-256 over canonical member-set bytes.
3. Member order, exact OIDs, trigger identity, and session identity cannot change `promotion_group_id`.
4. Changed logical membership creates a different PromotionGroup; empty/duplicate definitions are invalid.
5. A group is resolvable only when **all** declared members have current exact `READY_INTERNAL` states.
6. No partial PromotionUnit is materialized from an incomplete group.
7. Exact-state resolution/adoption is snapshot/CAS guarded; movement, reopen, lost readiness, or CAS mismatch prevents adoption.
8. Durable PromotionGroup presence—not the caller/trigger—determines whether grouping can resolve.
9. The same logical PromotionGroup remains stable across exact-state revisions while ADR-045 produces a different PromotionUnit when exact member states change.
10. No implicit singleton exists: a one-member PromotionUnit can arise only from an explicit singleton PromotionGroup.

## 3. Integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-046**.
- main §30 marks **30.17 resolved by ADR-046** and the remaining promotion backlog begins at **30.18**.
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` exposes `DeclarePromotionGroup(Set<CanonicalConvergenceUnitRef>)` rather than requiring a mid-sweep exact-OID handoff.
- PromotionGroup declarations are durable and trigger-independent, consistent with ADR-041/ADR-042 coalesced-demand semantics.
- the CoordinationStore schema includes durable PromotionGroup definitions/member rows and CAS-guarded current resolution.
- ADR-045 PromotionUnit exact-state identity remains unchanged.
- PromotionTopology and EffectivePromotionPolicy remain separate from PromotionGroup and PromotionUnit identity.
- no current main-spec text retains a policy-driven/default `READY_INTERNAL → singleton PromotionUnit` rule.
- no current fixed-point class waits for an explicit PromotionUnit declaration; absence of semantic grouping is represented as absence of a PromotionGroup declaration.
- ConvergenceUnit remains indivisible at the PromotionGroup boundary; ContributionUnit provenance is not split during promotion grouping.

## 4. New finite families

The new v16 families are:

```text
promotion_group_content_address_identity: 56
promotion_group_closed_completeness: 64
promotion_group_snapshot_cas_resolution: 16
promotion_group_trigger_independence: 16
promotion_group_to_promotion_unit_materialization: 4
explicit_singleton_no_implicit_default: 9
```

All prior v15 families are re-run as well.

## 5. Result

Executable result:

```text
Ruu state-space audit v16: PASS
changed/revalidated finite combinations evaluated: 13,247
markdown artifacts statically cross-checked: 65
```

## 6. Resulting boundary

The current promotion-grouping pipeline is:

```text
External Development System / Control Plane
  knows which logical ConvergenceUnits belong to one ship
  ↓ durable declaration before convergence demand
PromotionGroup
  = immutable closed content-addressed
    Set<CanonicalConvergenceUnitRef>
  ↓ global reconciler progresses all managed state
current exact READY_INTERNAL state for every member
  ↓ coherent snapshot + expected-state/CAS
Resolve(PromotionGroup)
  = Set<ExactConvergenceStateRef>
  ↓ ADR-045 canonical exact-set content address
PromotionUnit
  ↓
PromotionTopology + EffectivePromotionPolicy + provider state
  ↓
promotion mechanics
```

A singleton follows the same path:

```text
PromotionGroup {CX}
→ CX@x READY_INTERNAL
→ PromotionUnit {CX@x}
```

There is no semantic inference from `READY_INTERNAL`, no repository-name grouping, no invocation-local grouping marker, and no forced mid-sweep handoff solely to obtain exact OIDs.
