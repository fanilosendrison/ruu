---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require nonempty current promotion authorization route space"
id: "ADR-088"
status: "accepted"
date: "2026-09-28"
decision_body_sha256: "fac5923317084e3e3dac1c12159cc97b40cab9430e7af2a874f80afc13cc28c9"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-087"
  supersedes: []
  confirms:
    - "ADR-043"
governs:
  - "Nonempty current EffectivePromotionPolicy route-space invariant"
  - "Zero-route authoritative-composition classification"
  - "Policy-contradiction boundary before behavior resolution"
---

# ADR-088 — Require nonempty current promotion authorization route space

- **Status:** Accepted
- **Date:** 2026-09-28
- **Amends:** ADR-087
- **Confirms:** ADR-043

## Context

ADR-087 separates authoritative promotion authorization from non-authorizing
UserBehavior and defines `EffectivePromotionPolicy.allowed_routes` as a subset
of the two V1 realization routes. It identifies both singleton sets and the
two-route set as resolved current policy results.

Subset notation also admits the empty set. ADR-087 does not explicitly state
that `CURRENT(policy_fingerprint, allowed_routes = ∅)` is invalid. That omission
permits a reading in which behavior resolution receives an empty current policy
space and a strict route requirement is then classified as
`BEHAVIOR_UNSATISFIABLE`.

That reading conflicts with the governing classification boundary:
authoritative constraint composition with zero admissible routes is a policy
contradiction. UserBehavior is non-authorizing and cannot classify, repair, or
select within an invalid authoritative result. ADR-087 is accepted and
immutable, so a later decision must make the cardinality and ordering explicit.

## Discovery classification

```text
derived-from-existing-authority; explicit nonempty current route-space invariant
```

Issue #4 already requires an empty intersection between authoritative
requirements to produce `POLICY_CONTRADICTION`. ADR-043 likewise defines an
empty jointly admissible promotion space as `CONTRADICTORY`. This decision
introduces no additional route, preference, capability rule, or realization
mechanism; it closes the corresponding representation and classification gap in
ADR-087.

## Decision

### 1. A current route space is nonempty

A current effective promotion policy MUST contain one of exactly three nonempty
V1 route sets:

```text
CURRENT(policy_fingerprint, allowed_routes)
⇒ allowed_routes ∈ {
    {DIRECT_TARGET_ADVANCE},
    {PROVIDER_SUBMISSION},
    {DIRECT_TARGET_ADVANCE, PROVIDER_SUBMISSION}
  }
```

Therefore:

```text
CURRENT(policy_fingerprint, allowed_routes = ∅)
→ invalid / nonconforming
```

### 2. Zero authorized routes is a policy contradiction

If zero realization routes satisfy all current authoritative governance
constraints:

```text
authoritative composition has no admissible route
→ policy_state = CONTRADICTORY
→ POLICY_CONTRADICTION
→ EffectivePromotionPolicy is absent
```

The empty route space MUST NOT be materialized as a `CURRENT`
`EffectivePromotionPolicy` result.

### 3. Behavior resolution is not entered

Policy resolution precedes personal behavior resolution. When authoritative
composition has no admissible route:

```text
POLICY_CONTRADICTION
→ behavior resolution is not entered
→ no behavior source is selected
→ BEHAVIOR_UNSATISFIABLE is not evaluated
```

`BEHAVIOR_UNSATISFIABLE` is possible only after a valid nonempty `CURRENT`
policy result exists and a strict personal requirement names a route outside
that authorized set.

### 4. Downstream axes remain separate

This rule applies only to authoritative route-space composition. Exact core
constraints, contextual technical capability, and transition-local
prerequisites remain separate downstream axes.

An inability to realize an authorized route due to capability or exact current
state does not retroactively empty the authoritative policy set and does not
create `POLICY_CONTRADICTION`. Existing `UNSUPPORTED`, `MISSING / UNKNOWN`, and
localized-wait classifications remain unchanged.

### 5. ADR-087 otherwise remains unchanged

This decision amends ADR-087 only by closing its route-space cardinality and
classification boundary. ADR-087's non-authorizing UserBehavior,
BuiltInBehavior, fallback, currentness, exclusions, review/finalization, and
capability-separation semantics remain controlling.

It confirms ADR-043's rule that incompatible authoritative constraints remain a
visible contradiction rather than being repaired by a default or downstream
preference.

## Rationale

A `CURRENT` policy state asserts that authoritative composition has produced a
complete satisfiable authorization result. For the fixed two-route V1 domain,
that result has exactly three possible values. Treating the empty set as current
would move an authority failure into the personal behavior layer and would make
the error taxonomy dependent on which UserBehavior happened to be resolved.

Closing the domain preserves one classification regardless of behavior:

```text
zero authoritatively admissible routes
→ POLICY_CONTRADICTION
```

## Consequences

- `CURRENT(..., allowed_routes = ∅)` is explicitly nonconforming.
- Policy contradiction remains prior to and distinct from behavior
  unsatisfiability.
- UserBehavior and BuiltInBehavior never observe an empty current policy space.
- Capability and exact-state failures remain downstream execution facts rather
  than policy contradictions.
- Downstream profile, formal-model, and submission-policy work receives a closed
  current-policy domain.

## Rejected alternatives

### Permit an empty current route set

Rejected. A current policy result must represent a satisfiable authoritative
route space.

### Let behavior classify or repair the empty set

Rejected. UserBehavior is downstream and non-authorizing.

### Classify the empty set as behavior unsatisfiable

Rejected. No valid current policy exists against which strict personal behavior
can be evaluated.

### Edit ADR-087 directly

Rejected. Accepted decision bodies, outgoing relations, and governed scope are
immutable.

## Verification obligation

No new state-space package is created by this decision. Existing formal-
verification work owns future model coverage. The accepted specification and
this ADR are the oracle; existing qualification evidence does not prove
ADR-088.

Future coverage MUST include at least:

```text
authoritative composition yields zero admissible routes
→ POLICY_CONTRADICTION
→ no CURRENT EffectivePromotionPolicy
→ behavior resolution not entered
```

It MUST distinguish that case from a valid nonempty current policy that cannot
satisfy a strict UserBehavior requirement and from an authorized route whose
required mechanism is technically unsupported.
