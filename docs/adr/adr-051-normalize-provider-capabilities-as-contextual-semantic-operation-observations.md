# ADR-051 — Normalize provider capabilities as contextual semantic-operation observations

- **Status:** Accepted
- **Date:** 2026-09-06
- **Closes:** backlog 30.21
- **Amends:** ADR-026, ADR-043, ADR-044, ADR-050 and the main provider/promotion-policy model

- **Subsequently amended by:** ADR-080 for source-domain local/remote/provider observation authority and webhook evidence semantics

## Context

`ruu` already separates several authorities:

```text
core exact-state semantics
provider/current technical facts
provider/organization governance
trusted repository policy
```

ADR-043 composes authoritative capabilities/facts and governance/policy constraints into an `EffectivePromotionPolicy`. ADR-044 requires immediate re-observation/revalidation before every policy-sensitive promotion mutation. ADR-050 then makes stack shape a derived consequence of an exact unsatisfied promotion dependency and defines restack by a normative exact-state transplant contract.

Backlog 30.21 remained open because provider capability discovery was still described as a feature catalogue such as:

```text
stacked PR support
cross-repository PR support
cross-repository stacks
server-side restack
merge queue
head update rules
review/check invalidation semantics
```

That model is too weak. Provider behavior is contextual: a provider may support one operation only for same-repository branches, only on a particular target, only when a queue/ruleset is enabled, only with particular credentials, or only while a submission is in a compatible state. A boolean such as `supports_stacks=true` cannot express those constraints.

It is also semantically inverted. `ruu` must first determine the transition required by its own exact-state model. Provider vocabulary and marketing features must not decide publication layout or redefine a core mutation contract.

## Decision

Backlog item **30.21 is closed**.

### 1. The core determines the required semantic transition before provider capability resolution

`ruu` first derives the exact transition required by current managed state and normative contracts.

Examples include:

```text
CREATE_PR_SUBMISSION
REPRESENT_PROMOTION_DEPENDENCY
REVISE_SUBMISSION_HEAD
EXECUTE_RESTACK_CONTRACT
ENTER_MERGE_QUEUE
REQUEST_PROVIDER_TARGET_INTEGRATION
```

The versioned operation vocabulary is owned by the core and is derived from operations the engine actually performs. Provider adapters map provider mechanisms onto these semantic operations; they do not invent core semantics.

For ADR-050 specifically:

```text
exact unsatisfied promotion dependency
→ core requires REPRESENT_PROMOTION_DEPENDENCY
```

The provider adapter does not decide whether the work "should be stacked".

### 2. Provider capability is an observation over an exact operation context, not a provider-wide feature boolean

Capability discovery is modeled conceptually as:

```text
ObserveCapability(
  semantic_operation,
  exact_context
) -> CapabilityObservation
```

The exact context includes every provider-relevant fact necessary to decide applicability, for example:

```text
provider/repository identities
target repository/ref
publication/source repository
SAME_REPOSITORY | CROSS_REPOSITORY relation
current submission/provider identity and state
current exact head/base/expected-old identities when relevant
queue/ruleset/protection state when relevant
credential/permission facts when relevant
normative operation-contract identity/version when relevant
```

Therefore the same provider may legitimately return different observations for the same semantic operation in different contexts.

A provider-wide declaration such as:

```text
supports_stacked_pr = true
```

is never sufficient authorization or applicability evidence.

### 3. Capability observations separate technical support, contextual applicability, and current facts

A normalized observation records at least the semantic equivalent of:

```text
CapabilityObservation {
  semantic_operation
  exact_context_fingerprint
  support = SUPPORTED | UNSUPPORTED | UNKNOWN_INCONSISTENT
  provider_mechanism, if any
  normalized applicability constraints/current facts
  normalized mutation effects relevant to evidence/review/check state, when applicable
  provider source identity
  observed revision/version/fingerprint when exposed
  observation identity/method
}
```

The serialization is implementation work; the semantic separation is normative.

Examples:

```text
REPRESENT_PROMOTION_DEPENDENCY + SAME_REPOSITORY
→ SUPPORTED via provider-native stacked/base relationship

REPRESENT_PROMOTION_DEPENDENCY + CROSS_REPOSITORY
→ UNSUPPORTED for a provider/context that cannot represent that dependency
```

No alternative publication structure is inferred from `UNSUPPORTED`.

### 4. Semantic capability names are preferred over provider feature names

The core asks whether a provider can satisfy a semantic contract, not whether the provider exposes a feature with a particular label.

Prefer:

```text
REPRESENT_PROMOTION_DEPENDENCY
REVISE_SUBMISSION_HEAD
EXECUTE_RESTACK_CONTRACT
```

over provider-shaped primitives such as:

```text
STACKED_PR_SUPPORT
SERVER_SIDE_RESTACK
```

A provider with no feature named "stack" may still be able to represent the dependency correctly. Conversely, a provider feature named "stack" is unusable when its observable semantics do not satisfy the required core contract.

### 5. Provider capability is factual; it never authorizes an operation by itself

The execution predicate remains a conjunction of distinct authorities:

```text
core transition is REQUIRED
AND provider/context capability is SUPPORTED
AND EffectivePromotionPolicy says the operation is AUTHORIZED
AND all ordinary exact-state/claim/verification/recovery guards hold
→ operation may execute
```

Equivalently:

```text
required ∩ supported ∩ authorized = executable
```

A technically supported direct push can still be forbidden by governance. A technically supported submission rewrite can still be forbidden by repository policy. A governance-authorized operation that the provider cannot perform in the exact current context remains blocked/waiting.

Capability discovery therefore remains a factual input to ADR-043 composition, never a replacement for governance/policy authorization.

### 6. Derived promotion topology is not an EffectivePromotionPolicy choice

ADR-050 already establishes:

```text
promotion dependency/topology
= derived managed state from exact base/predecessor/target facts
```

Therefore `INDEPENDENT | STACKED` is not a caller preference and is not a policy-selected publication-layout dimension.

Policy may constrain/authorize whether the **required dependency representation operation** may be used, and provider capability may establish whether that exact operation is technically realizable in the current context. Neither source selects the topology itself.

The policy model continues to resolve normative dimensions such as:

```text
promotion_mode: DIRECT | PR
publication_relation: SAME_REPOSITORY | CROSS_REPOSITORY
target/publication destination
submission rewrite authorization
provider/governance operation constraints
```

Current derived dependency state is then combined with those policy results and current capability observations when selecting an executable transition.

### 7. Provider-native execution never becomes semantic authority

When a provider offers a native mechanism for an operation whose result is normatively defined by `ruu`, the provider mechanism is only an executor.

For ADR-050 restack:

```text
RestackContract(old_base, owned_candidate, new_base)
→ normative exact expected result
```

A provider-native restack is usable only when the current contextual capability observation says it can execute the required contract and the exact observed result satisfies the same normative contract. Provider feature identity or successful API status is not enough.

If a conforming local executor exists, it may be used instead subject to the same provider publication/update constraints. If no conforming executable path exists, the obligation waits/blocks rather than changing semantics.

### 8. Review/check/evidence effects are normalized current facts, not guessed from provider labels

Provider mutations can affect reviews, checks, merge-queue state, approval validity, or similar evidence.

Where such effects matter to safe progression, the adapter exposes normalized contextual facts/effects tied to the exact operation/revision. Unknown or inconsistent effect semantics cannot be treated as preservation of evidence.

Existing exact-head evidence rules remain authoritative: stale or invalidated evidence is re-read/re-established according to the main specification. Provider-specific defaults are not silently assumed.

### 9. Capability observations obey ADR-044 freshness rules

Capability observations are immutable observations and may be cached only as an optimization.

Immediately before a policy-sensitive provider mutation, every mutable capability/current-fact observation required by that operation is re-observed/revalidated under ADR-044.

```text
changed capability/context/provider fact
→ prior observation/policy snapshot STALE
→ recompute before mutation
```

Strong provider versions/fingerprints/ETags are used when exposed; otherwise an immediate fresh normalized observation is required. No TTL establishes capability currentness.

### 10. Unsupported or unknown capability blocks only the affected obligation

For one exact required operation:

```text
SUPPORTED + AUTHORIZED
→ may progress if all other guards hold

UNSUPPORTED
→ affected operation waits / UNSUPPORTED_TOPOLOGY or equivalent exact blocked state

UNKNOWN_INCONSISTENT
→ affected operation fails closed pending fresh/consistent observation
```

`ruu` MUST NOT respond by silently flattening a stack, combining promotions, switching from PR to DIRECT, changing repositories, or asking an agent to choose another publication layout.

Other unrelated obligations in the global sweep continue normally.

## Consequences

- Provider-specific branches are isolated behind adapters rather than leaking throughout the core.
- Capability discovery is precise enough for same-repository/cross-repository, target-specific, queue-specific, permission-specific, and current-state-specific constraints.
- ADR-050 dependency derivation remains independent of provider feature naming.
- Provider-native restack/merge/update mechanisms can be exploited without delegating semantic authority.
- `EffectivePromotionPolicy` no longer treats `INDEPENDENT | STACKED` as a policy-selected topology; current topology is derived state and policy only constrains the operations required to represent it.
- Provider capability/current-fact observations remain subject to ADR-044 immediate pre-mutation freshness.
- Unsupported provider contexts localize waiting instead of causing semantic fallback.

## Rejected alternatives

### Provider-wide boolean feature matrix

Rejected. Capabilities are contextual and operation-specific; a single provider-wide boolean loses exact applicability constraints and current state.

### Let the provider choose publication structure

Rejected. Provider mechanisms are implementation facts, not semantic authority. Core exact-state rules determine the required transition.

### Treat capability support as policy authorization

Rejected. Technical realizability and normative authorization are distinct authorities and must both hold.

### Use provider-native operation result as authoritative because the API succeeded

Rejected. Normatively defined operations require exact post-operation observation and contract conformance before adoption.

### Fall back to another topology when the required operation is unsupported

Rejected. This changes the meaning/exposure of the promotion. The affected obligation waits while unrelated obligations continue.

## Amendment by ADR-052

DIRECT target advancement supplies another core-defined semantic operation: `ADVANCE_TARGET_FF_EXPECTED_OLD` / `AdvanceTargetFF(target, expected_old, new)`. A local Git, remote Git, provider-native, or other backend is usable only when its exact-context capability satisfies the atomic expected-old + descendant-only contract. Provider mechanism names or generic force/update capability never become target-mutation authority.

## Amendment — ADR-062 (2026-09-07)

Current semantic operation names should be provider-neutral. Historical `CREATE_PR_SUBMISSION` maps to `CREATE_PROVIDER_SUBMISSION`; merge/queue/button-specific provider actions map to the exact `REQUEST_PROVIDER_TARGET_INTEGRATION` / queue / auto-merge / finalization operation required by current state. Capability still reports mechanism support and never defines core semantics.

## Amendment — ADR-065 (2026-09-07)

Provider adapters also normalize finalization output when candidate ancestry is lost. The canonical finalization observation must bind the exact logical submission/PublicationEpisode, exact submitted revision `C`, exact target `T`, completed finalization, and exact final result OID `R`. The adapter may derive this from several provider API facts; no cryptographic attestation primitive is required. Core adoption still independently observes Git target history. Provider capability/finalization success alone never substitutes for this exact result contract.
