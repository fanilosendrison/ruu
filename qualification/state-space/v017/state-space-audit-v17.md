# State-Space Audit v17 — ADR-047 Repository-Local PromotionGroup Projection

## 1. Scope

This audit extends v16 after ADR-047 closes backlog 30.18. It revalidates all prior finite architecture families and adds explicit coverage for deterministic projection of one completely resolved logical PromotionGroup into exactly one repository-local PromotionUnit per represented authoritative source repository.

This is a finite regression/state-machine audit, not a proof over arbitrary Git DAGs, provider implementations, or the still-open repository-local multi-source candidate/head composition algorithm of backlog 30.39.

## 2. ADR-047 properties exercised

The executable audit checks:

1. PromotionGroup remains a non-empty immutable closed logical member set and may span repositories.
2. PromotionGroup identity remains independent of exact OIDs, trigger identity, and session identity.
3. Complete `READY_INTERNAL` resolution is still required for every group member before current group resolution may be adopted.
4. A completely resolved group is partitioned deterministically by authoritative source `repository_id`.
5. The number of projected PromotionUnits equals the number of distinct source repositories represented in the group.
6. Every projected PromotionUnit is non-empty and contains members from exactly one source repository.
7. A cross-repository exact member set is structurally invalid as a PromotionUnit.
8. Same PromotionGroup + same repository is never split into several PromotionUnits by the repository projection rule.
9. The current PromotionGroup resolution is a complete repository→PromotionUnit mapping and remains snapshot/CAS guarded.
10. Repository-local PromotionUnits may progress independently after resolution, allowing higher-level `NONE_PROMOTED | PARTIALLY_PROMOTED | ALL_PROMOTED` aggregate states.
11. Changing exact source states changes the relevant repository-local PromotionUnit content address without changing PromotionGroup identity.
12. No implicit singleton/default mapping is reintroduced.

## 3. Integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-047**.
- main §30 marks **30.18 resolved by ADR-047**.
- repository-local multi-source candidate/head composition is retained explicitly as **30.39**, rather than being accidentally declared solved.
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` states the intended session-scoped grouping rule while keeping session identity out of content addressing and out of Ruu inference.
- current PromotionUnit structural validity requires exactly one authoritative source repository.
- `CROSS_REPOSITORY` PR publication remains a separate policy dimension and is not confused with source membership locality.
- current PromotionGroup resolution is represented as a complete `repository_id → PromotionUnitRef` mapping.
- same-group/same-repository projection cannot be fragmented into a stack by `ruu`.
- PromotionTopology remains separate explicit state.
- ADR-014 cross-repository partial-progress semantics now apply at PromotionGroup/logical-ship aggregate level.
- ADR-045 content-addressing remains unchanged for structurally valid repository-local PromotionUnits.
- ADR-046 is explicitly amended rather than silently left as the current one-group→one-unit rule.

## 4. New/changed finite families

The ADR-047-specific/reworked families are:

```text
promotion_group_repository_partition: 8
same_group_same_repo_not_split: 12
promotion_group_complete_resolution_map: 24
cross_repository_group_partial_progress: 4
group_revision_to_repository_local_units: 4
```

PromotionUnit content-address testing was also tightened so cross-repository exact member sets are rejected as structurally invalid.

All prior v16 families are re-run as well.

## 5. Result

Executable result:

```text
Ruu state-space audit v17: PASS
changed/revalidated finite combinations evaluated: 13,296
markdown artifacts statically cross-checked: 67
```

## 6. Resulting boundary

The current promotion pipeline is:

```text
External Development System / Control Plane
  same-session ship membership established upstream
  ↓ durable closed declaration before convergence demand
PromotionGroup
  = immutable logical ship; may span repositories
  ↓ wait for every member's current exact READY_INTERNAL state
complete coherent exact group snapshot
  ↓ deterministic GROUP BY authoritative repository_id
one projected exact member set per represented repository
  ↓ ADR-045 content-addressed materialization
repository-local PromotionUnit(s)
  ↓ separate PromotionTopology + EffectivePromotionPolicy
repository-local candidate/submission/direct-promotion mechanics
```

For:

```text
G = {
  RepoA/CX,
  RepoA/CY,
  RepoB/CZ
}
```

the only valid structural projection is:

```text
RepoA → PromotionUnit {CX@x, CY@y}
RepoB → PromotionUnit {CZ@z}
```

The unresolved downstream question is no longer how to partition the logical multi-repository ship. It is how a same-repository multi-source PromotionUnit is deterministically materialized into one exact candidate/head; that is backlog 30.39.
