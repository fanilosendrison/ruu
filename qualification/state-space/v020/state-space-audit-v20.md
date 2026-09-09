# State-Space Audit v20 — ADR-051 Contextual Semantic Provider Capability Observations

## 1. Scope

This audit extends v19 after ADR-051 closes backlog 30.21. It revalidates every prior finite architecture family and adds explicit coverage for provider capability normalization, exact-context applicability, separation of technical support from policy authorization, normalized provider review/check effects, and provider-native/external executor semantic non-authority.

This is a finite regression/state-machine audit. It does not claim to enumerate every arbitrary Git DAG/provider implementation or prove provider API behavior. Exact Git restack semantics selected by ADR-050 remain additionally exercised by `git-restack-smoke-v1.sh`.

## 2. ADR-051 properties exercised

The executable audit checks that:

1. the core's semantic operation and exact context, rather than provider identity/feature naming, determine the normalized capability question;
2. `REQUIRED`, `SUPPORTED`, and `AUTHORIZED` remain independent conjunctive guards;
3. unsupported, unknown, forbidden, non-required, or otherwise failed-guard operations cannot execute;
4. one provider can support a semantic operation in one context and not another, proving that a global provider feature boolean is insufficient;
5. unknown/invalidated review/check effects cannot be treated as preserved evidence;
6. local, provider-native, and external-tool executors have identical adoption predicates for normatively defined operations;
7. provider/API success alone cannot authorize adoption without exact observation, contract conformance, and required verification.

## 3. New finite families

ADR-051 adds:

```text
provider_semantic_capability_context: 576
contextual_capability_not_global_boolean: 6
provider_effect_unknown_fails_closed: 18
provider_executor_semantic_non_authority: 48
```

Every v19 family is re-run as well.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-051**;
- main §30 marks **30.21 resolved by ADR-051**;
- the open backlog no longer lists 30.21;
- ADR-051 fixes `ObserveCapability(semantic_operation, exact_context)` as the normalized abstraction;
- provider-wide stack/restack feature booleans are not sufficient semantic capability evidence;
- `required ∩ supported ∩ authorized = executable` is explicit;
- provider-native/external execution remains subordinate to normative core contracts;
- `promotion_topology: INDEPENDENT | STACKED` is no longer modeled as an EffectivePromotionPolicy-selected dimension in the current main specification;
- the current main specification no longer assigns promotion-dependency selection to the External Control Plane;
- the External Control Plane contract recognizes ADR-051 capability discovery;
- ADR-043/044/050 include the corresponding subsequent clarifications;
- all prior ADR-049/050 submission/ref/dependency/restack invariants and all earlier architecture families remain intact.

## 5. Result

Executable result:

```text
Ruu state-space audit v20: PASS
changed/revalidated finite combinations evaluated: 14,578
markdown artifacts statically cross-checked: 74
```

## 6. Resulting capability/promotion decision boundary

```text
current exact managed Git/promotion state
  ↓
core derives REQUIRED semantic transition
  ↓
Provider Capability Adapter
  ObserveCapability(operation, exact_context)
  → SUPPORTED | UNSUPPORTED | UNKNOWN_INCONSISTENT
  ↓
ADR-043/044 EffectivePromotionPolicy
  → AUTHORIZED | forbidden/blocked
  ↓
REQUIRED ∩ SUPPORTED ∩ AUTHORIZED
+ exact-state / verification / claim / recovery guards
  ↓
execute
  ↓
exact post-operation observation
  ↓
for normatively defined operations:
observed result conforms to core contract
  ↓
adopt
```

For ADR-050 dependency publication specifically:

```text
exact unsatisfied predecessor dependency
→ REPRESENT_PROMOTION_DEPENDENCY is REQUIRED

SUPPORTED + AUTHORIZED
→ stacked provider representation

UNSUPPORTED / UNKNOWN / FORBIDDEN
→ child waits locally
→ no flattening, regrouping, DIRECT fallback, or caller topology choice
```
