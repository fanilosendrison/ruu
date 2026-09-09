# Ruu — State-Space Audit v30

- **Date:** 2026-09-07
- **Architecture through:** ADR-061
- **Result:** PASS

## 1. Purpose

This pass revalidates the retained finite architecture state-space after ADR-061 separates the repository-local **ConvergenceBase** from the immutable logical **PromotionTarget** and removes destination selection from `EffectivePromotionPolicy`.

The intended boundary is now explicit:

```text
WHERE should this ConvergenceUnit ultimately land?
→ External Control Plane
→ immutable PromotionTarget(target_repository_id, target_ref)
→ bound before first managed write

HOW may current exact state reach that target now?
→ Ruu + current EffectivePromotionPolicy + provider/current state
→ DIRECT | PR + authorized provider/governance mechanics
```

This pass also closes residual current-spec wording left from ADR-060 so the normative requirements no longer contain obsolete generic development-validation prerequisite states.

## 2. ADR-061 state-space change

### 2.1 PromotionTarget binding family

The new regression family varies:

```text
stage
= BEFORE_FIRST_WRITE | AFTER_FIRST_WRITE | PROMOTION

PromotionTarget binding/request relation
= MATCH_REQUEST | DIFFERENT_REQUEST | MISSING

promotion mode
= DIRECT | PR

policy target behavior
= SAME | DIFFERENT

same-source PromotionGroup target coherence
= COHERENT | INCOHERENT

current target OID state
= CURRENT | MOVED
```

Finite combinations:

```text
3 × 3 × 2 × 2 × 2 × 2 = 144
```

The family enforces:

- target identity is resolved before first managed write;
- missing target after authoring is inconsistent managed state, never an invitation to infer a destination;
- a different requested target requires a distinct ConvergenceUnit rather than retargeting;
- policy cannot substitute a different target;
- same-source PromotionGroup projection with differing immutable PromotionTargets fails closed as `TARGET_INCOHERENT_PROMOTION_GROUP`;
- a moved target OID triggers exact-state/currentness refresh without changing target repository/ref identity;
- DIRECT/PR progression uses the already-bound target.

No state transition in the family permits implicit retargeting.

## 3. Static integration checks

The static pass verifies among other things that:

- ADR numbering is contiguous through **ADR-061**;
- main section **30.40** is explicitly resolved by ADR-061;
- the backlog contains only **30.34** and **30.36** as genuine open core questions;
- `ConvergenceUnit` carries an externally authoritative immutable `PromotionTarget = (target_repository_id, target_ref)`;
- pre-edit provisioning resolves the repository-local ConvergenceBase and the PromotionTarget before managed authoring;
- the External Control Plane contract owns PromotionTarget resolution/binding and forbids late retargeting;
- current requirements no longer use the legacy `target/base` phrase for the internal synchronization source;
- `EffectivePromotionPolicy` treats target identity as input/context and does not select `target_repository_id` / `target_ref`;
- `SAME_REPOSITORY | CROSS_REPOSITORY` is derived from source repository identity + PromotionTarget rather than policy-selected;
- policy observations/fingerprints are context-bound to the immutable PromotionTarget while target OID/provider/governance facts remain freshly revalidated;
- same-source PromotionGroup projection is target-coherent or fails closed with `TARGET_INCOHERENT_PROMOTION_GROUP`;
- historical ADRs whose target/policy wording is superseded carry explicit ADR-061 amendments;
- residual current-spec ADR-060 generic validation states (`development-validation-blocked`, generic `VALID_EXACT` prerequisite family, development-validation demand/wait states) are absent except where explicitly described as retired/removed;
- Markdown code fences remain balanced.

## 4. Git smoke validation

ADR-061 changes topology/authority/state binding rather than introducing a new Git primitive, so no sixth Git smoke is required. All five retained concrete Git primitive smokes pass:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance v1 smoke: PASS
Ruu repository bootstrap v1 smoke: PASS
Ruu canonical checkpoint v1 smoke: PASS
```

## 5. Result

The v29 retained finite total is **14,222**. ADR-061 adds/revalidates **144** target-binding combinations:

```text
14,222 + 144 = 14,366
```

Executable result:

```text
Ruu state-space audit v30: PASS
changed/revalidated finite combinations evaluated: 14,366
markdown artifacts statically cross-checked: 94
5 Git primitive smokes: PASS
```

**Verdict:** a Development System no longer needs to transmit a late `merge main`/`PR to X` decision. The destination is an immutable pre-authoring ConvergenceUnit fact; `ruu` deterministically decides only the currently authorized path toward that destination. Target identity cannot drift with policy/config/provider changes, while current target state continues to be revalidated exactly.
