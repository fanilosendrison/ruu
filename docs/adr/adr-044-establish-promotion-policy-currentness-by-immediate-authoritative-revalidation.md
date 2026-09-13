---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Establish promotion-policy currentness by immediate authoritative revalidation"
id: "ADR-044"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "4f9e06a65d3d78149a7938465b5dfdcbef213b9268916067c27d53acd9084236"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-044: Establish promotion-policy currentness by immediate authoritative revalidation

- **Status:** Accepted; amended by ADR-061
- **Date:** 2026-09-05
- **Decision order:** 044

## Context

ADR-026 requires repository-policy-driven promotion. ADR-043 closed policy authority/composition: authoritative provider capabilities/current facts, provider/organization governance constraints, and trusted target-baseline repository policy compose into an `EffectivePromotionPolicy`; runtime/local overrides cannot bypass it.

Backlog 30.15 remained open because a policy that was valid when resolved can become stale before a policy-sensitive mutation. In particular, provider/org governance and capabilities/current facts can change independently of the local coordination store. A cache TTL cannot prove that such an observation is still current:

```text
T0 observe provider: DIRECT admissible
T1 provider governance changes: PR required
T2 cached policy still says DIRECT
T3 promotion mutation attempted
```

The architecture therefore needs a precise currentness rule that does not pretend a distributed read+mutation can always be transactional.

## Decision

### 1. Policy snapshots are immutable observations

Each resolved `EffectivePromotionPolicy` is represented as an immutable/fingerprinted policy snapshot bound to the authoritative source observations from which it was compiled.

At minimum, the runtime can reconstruct:

```text
policy fingerprint
trusted target OID / repository-policy anchor
provider/org governance source identities and observed revision/version/fingerprint when exposed
provider capability/current-fact source identities and observed revision/version/fingerprint when exposed
observation identity/method for mutable external sources
```

Wall-clock observation time MAY be recorded for diagnostics and operational tuning. It is not authorization evidence by itself.

### 2. Cache is optimization only

Cache entries may retain parsed policy, normalized provider observations, or provider metadata for efficiency.

However:

```text
cache hit
cache age
TTL not expired
previous successful resolution
previous successful mutation
```

never by themselves establish `CURRENT` for a policy-sensitive promotion mutation.

There is no TTL-based authorization fallback.

### 3. Every global sweep refreshes relevant policy state

Every executed ADR-036/ADR-041 global sweep refreshes/revalidates the policy observations needed by the nonterminal managed obligations it evaluates.

This keeps waiting provider/promotion obligations current over time, but sweep-level refresh alone is not sufficient authorization for a later policy-sensitive mutation.

### 4. Every policy-sensitive promotion mutation gets immediate pre-mutation revalidation

Immediately before every policy-sensitive promotion mutation, `ruu` MUST re-observe/revalidate every mutable authoritative policy source required by that mutation.

This includes at minimum policy-governed mutations such as:

```text
direct target-ref advancement/publication
submission-ref publication or rewrite
PR creation/update
formal review-request mutation
stack/restack/update-branch/base mutation
merge or merge-queue entry / equivalent provider target-integration mutation
cross-repository publication
```

Pure local candidate materialization, projection, or verification is not policy-sensitive merely because it precedes promotion; ordinary exact-state/verification invariants still govern it.

### 5. Any authority-anchor change makes the prior snapshot stale

The prior policy snapshot becomes `STALE` if revalidation observes movement/change in any authoritative source used for the relevant policy decision, including:

```text
trusted target OID / repo-policy anchor
provider governance
organization governance
provider capabilities/current facts
other authoritative policy-source revision/fingerprint
```

Then:

```text
prior snapshot → STALE
policy-sensitive mutation → not authorized
recompute EffectivePromotionPolicy from current observations
```

If recomputation is contradictory, ADR-043 applies. If it is valid/current, the mutation may be reconsidered under the new exact snapshot.

No optimization attempts to prove that an anchor change was “irrelevant enough” to keep the old snapshot current.

### 6. Strong provider identities are used when available; fresh observation is required otherwise

If a provider exposes an ETag, version, revision, fingerprint, or equivalent strong observation identity, `ruu` binds/revalidates against it.

If the provider does not expose such an identity, `ruu` MUST perform an immediate fresh normalized observation before the policy-sensitive mutation. Absence of a strong version primitive does not authorize TTL substitution.

### 7. Non-atomic provider check/use is an explicit external boundary

Some providers do not expose an atomic primitive combining:

```text
check governance/current capabilities
+
perform mutation iff those exact observations are unchanged
```

`ruu` does not invent a distributed transaction to hide this limitation.

For such operations:

```text
immediate fresh pre-mutation observation
→ policy resolution/revalidation
→ bounded provider mutation
→ exact provider outcome/current-state observation
```

Provider-side enforcement/rejection plus exact post-operation observation form the final external authority boundary.

If governance/capability changes in the unavoidable interval and the provider rejects or changes the operation outcome, that result is not interpreted as permission and is not automatically repaired. The current factual provider state/rejection is surfaced to the external Development System/operator; later progress requires ordinary re-observation and policy revalidation.

### 8. Freshness evidence is factual, not prescriptive

The persisted/externally exposable freshness provenance records what was observed and why the snapshot became/currently is stale/current. It does not recommend a governance change, retry policy, override, or remediation.

This preserves the ADR-040/ADR-043 boundary:

```text
Ruu
→ observe / classify / prove / expose

external Development System or operator
→ interpret / decide / act
```

## Consequences

### Positive

- `CURRENT` has an exact operational meaning independent of cache age.
- Provider/org drift is detected before each policy-sensitive mutation as late as the provider API permits.
- Target-baseline policy movement invalidates old authorization deterministically.
- Zero-onboarding from ADR-043 remains intact; currentness does not require a local policy file.
- Caching can still optimize reads without acquiring correctness authority.
- The architecture acknowledges unavoidable provider TOCTOU instead of claiming impossible atomicity.

### Costs

- Policy-sensitive promotion mutations may require additional provider/API reads.
- Provider rate limits and observation latency become operational concerns.
- Providers without strong version identities require normalized fresh observations.
- A provider can still change between fresh observation and a non-atomic mutation; correctness then relies on provider enforcement/rejection plus exact observed outcome.

## Rejected alternatives

### TTL establishes currentness

Rejected. A one-second-old observation may already be stale; TTL is a performance knob, not an authorization proof.

### Refresh only once per explicit invocation/global sweep

Rejected. Long-running/retried/waiting promotion lifecycles can outlive the observation that originally authorized them.

### Require a strong ETag/version from every provider or block all promotion

Rejected. This would make correctness depend on provider metadata primitives that may not exist. Immediate fresh observation plus provider enforcement/post-observation is the v1 boundary when strong identities are unavailable.

### Retry/repair provider rejection automatically

Rejected. Concurrent governance drift is factual current-state change. Choosing what to change or whether to retry belongs outside `ruu`.

## Backlog impact

Backlog item **30.15 is closed**.

PromotionUnit definition/identity (30.16) was subsequently closed by ADR-045. PromotionGroup/default-mapping semantics (30.17) were subsequently closed by ADR-046.

Still open beginning with 30.18:

- Repository-local multi-source candidate/head materialization (30.39; structural group projection was subsequently closed by ADR-047; 30.39 was subsequently closed by ADR-048).
- Submission-ref lifecycle.
- Restacking implementation.
- Provider capability discovery details (subsequently closed by ADR-051).
- DIRECT candidate workspace implementation.
- Review `CHANGES_REQUESTED` semantic scope mapping.
- Promotion completion versus ConvergenceUnit retirement.
- Cross-repository compensation.
- New repository creation/provisioning authority (subsequently closed by ADR-056).

## Subsequent clarification by ADR-051

ADR-051 defines provider capability/current-fact observations as contextual semantic-operation observations. These observations are subject to this ADR unchanged: cache/TTL never authorizes them, and every mutable capability/current fact required by a policy-sensitive mutation must be immediately re-observed/revalidated before that mutation.

## Amendment by ADR-052

For DIRECT target advancement, immediate revalidation occurs at the `AdvanceTargetFF` mutation boundary. If authoritative target no longer equals the operation's exact expected-old baseline, the attempt is stale even when the moved target remains an ancestor of the old candidate; trusted-target policy and candidate authorization must be recomputed from the new baseline.

## Amendment by ADR-061

Immediate revalidation applies to mutable target OID/governance/provider facts for the already-bound PromotionTarget. Currentness refresh may change authorization or allowed mechanics, but never the ConvergenceUnit's immutable target repository/ref identity.

## Amendment — ADR-062 (2026-09-07)

Immediate currentness rules apply equally to provider-submission creation/update and to provider target-integration/finalization operations. Automatic finalization is permitted only from freshly revalidated required + supported + authorized state; no stale “authorization to merge” token is introduced.

