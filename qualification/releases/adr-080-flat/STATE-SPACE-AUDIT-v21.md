# State-Space Audit v21 — ADR-052 exact-old CAS+FF DIRECT target advancement

## 1. Scope

This audit extends v20 after ADR-052 closes backlog 30.22. It revalidates every prior finite architecture family and adds explicit coverage for the DIRECT target-advancement boundary after ADR-048 candidate materialization: exact expected-old comparison, descendant-only target effect, no target-worktree/local-target staging, authoritative-history recovery adoption, and recovery-anchor cleanup eligibility.

This is a finite regression/state-machine audit. It does not claim to enumerate every arbitrary Git DAG/provider implementation or prove a particular remote/provider API. The concrete local Git ref contract is additionally exercised by `git-direct-target-advance-smoke-v1.sh`; ADR-048 materialization and ADR-050 restack Git behavior retain their existing smoke tests.

## 2. ADR-052 properties exercised

The executable audit checks that:

1. `AdvanceTargetFF(target, expected_old=B, new=C)` may mutate only when authoritative target is still exactly `B`;
2. exact ancestry must prove `B` ancestor-or-equal `C`; no non-FF target transition can be authorized;
3. current DIRECT policy, exact-candidate verification, target claim, and contextual backend capability remain independent required guards;
4. a target worktree, merge-into-target stage, or pre-moved local target ref is never a conforming DIRECT correctness path;
5. after an uncertain attempt, exact authoritative target `== C` or a descendant containing `C` proves the promotion effect occurred;
6. target still equal `B`, divergent history, or unknown history cannot be invented as successful adoption;
7. physical recovery-anchor presence is not the truth source once authoritative history proves the effect, but a still-required nonterminal candidate cannot become cleanup-authorized;
8. ADR-052 remains subordinate to ADR-042 Operation→Attempt→Observation→Adoption, ADR-044 immediate freshness, ADR-048 exact candidate materialization, and ADR-051 semantic backend capability normalization.

## 3. New finite families

ADR-052 adds:

```text
direct_target_advance_contract: 810
direct_target_recovery_adoption: 30
direct_target_no_staging_surface: 8
direct_recovery_anchor_cleanup: 18
```

Every v20 family is re-run as well.

## 4. Concrete Git smoke

`git-direct-target-advance-smoke-v1.sh` validates a local-ref realization of the semantic contract:

```text
exact B → descendant C with expected-old B
→ succeeds

current target moved to descendant D after C
→ C is still provably realized

stale expected-old B while current target is D
→ no mutation

B → unrelated candidate
→ rejected before ref mutation

raw git update-ref with stale expected-old
→ CAS rejected

candidate recovery anchor
→ retained until realization/recovery sufficiency, then removable
```

The smoke deliberately tests the semantic contract rather than declaring one remote/provider command normative.

## 5. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-052**;
- main §30 marks **30.22 resolved by ADR-052** and the open backlog no longer lists 30.22;
- ADR-052 fixes `AdvanceTargetFF(target, expected_old=B, new=C)` as the normative DIRECT operation;
- main DIRECT flow/matrix/engine/invariants contain no local-target pre-advancement requirement;
- recovery adoption uses authoritative target history (`C` exact or `C` ancestor current target);
- recovery-anchor cleanup remains separate from durable operation/adoption/audit history;
- the stale pre-ADR-048 statement that multi-source materialization was “not fixed” is removed;
- ADR-026/041/042/044/048/051 carry the corresponding subsequent amendments/clarifications;
- the DIRECT smoke result is present and PASS;
- all ADR-051 provider-capability, ADR-050 restack, ADR-049 submission, ADR-048 materialization, and earlier architecture families remain intact.

## 6. Result

Executable result:

```text
Ruu state-space audit v21: PASS
changed/revalidated finite combinations evaluated: 15,444
markdown artifacts statically cross-checked: 76
```

Concrete Git smoke:

```text
Ruu DIRECT target advance smoke v1: PASS
```

## 7. Resulting DIRECT boundary

```text
ADR-048 exact candidate C
+ exact full-verification evidence
+ authoritative target baseline B
  ↓
record/recover AdvanceTargetFF(target, B, C)
  ↓
keep C reachable with attempt-scoped recovery anchor
  ↓
immediate target/policy/claim/evidence/backend revalidation
  ↓
current target == B
AND B ancestor-or-equal C
AND DIRECT authorized
AND exact C verified/current
AND target claim held
AND backend semantic operation supported
  ↓
atomic exact-old CAS + FF: B → C
  ↓
observe authoritative target
  ├─ target == C            → realized
  ├─ C ancestor target      → realized + later progress
  ├─ target == B            → not realized
  └─ otherwise              → stale/drift, recompute
  ↓
durable Adoption/recovery sufficiency
  ↓
recovery anchor GC_ELIGIBLE
```

No target worktree, merge-into-target stage, pre-moved local target ref, force/non-FF semantic fallback, or blind replay is part of this path.
