---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Separate promotion authorization space from non-authorizing UserBehavior"
id: "ADR-087"
status: "accepted"
date: "2026-09-28"
decision_body_sha256: "9fef635965903f0ca242ab999abf6b1583f8976e70e5aa36ff09d73e2f355e7a"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-026"
    - "ADR-043"
    - "ADR-044"
    - "ADR-061"
    - "ADR-062"
  supersedes: []
  confirms:
    - "ADR-032"
    - "ADR-051"
governs:
  - "EffectivePromotionPolicy authorized route-space semantics"
  - "Non-authorizing UserBehavior route preference and requirement semantics"
  - "BuiltInBehavior zero-onboarding route selection"
  - "Promotion policy, behavior, capability, and error-classification boundary"
  - "UserBehavior exclusion boundary"
  - "Promotion realization-route selection and fallback semantics"
---

# ADR-087 — Separate promotion authorization space from non-authorizing UserBehavior

- **Status:** Accepted
- **Date:** 2026-09-28
- **Amends:** ADR-026, ADR-043, ADR-044, ADR-061, and ADR-062
- **Confirms:** ADR-032 and ADR-051

## Context

ADR-026 made promotion repository-policy-driven. ADR-043 then established
constraint composition across authoritative governance sources, trusted
target-baseline repository policy, contradiction detection, zero-onboarding
closure, and the prohibition on runtime authorization bypass. ADR-044 made those
authorizations current only through immediate authoritative revalidation.
ADR-061 separated immutable destination identity from policy mechanics, and
ADR-062 replaced semantic direct-versus-PR modes with two realization routes for
one exact promotion objective.

The current reading nevertheless collapses two distinct questions. It asks
`EffectivePromotionPolicy` to select one scalar realization route and assigns
this default to built-in policy:

```text
if direct is admissible
→ select DIRECT_TARGET_ADVANCE
else
→ select PROVIDER_SUBMISSION
```

A fully known state in which governance permits both routes is therefore treated
as underdetermined until policy chooses one. That makes personal preference look
like governance and makes contextual technical capability appear to participate
in authorization.

The required correction separates four layers:

```text
authoritative governance
→ complete authorized route space

UserBehavior
→ non-authorizing preference or requirement within that space

technical capability + exact current state
→ current technical realizability

transition-local prerequisites
→ progression now or localized wait
```

This decision supersedes only the old **current reading** in which ADR-043
collapsed a multi-route authorized space to one scalar route through a built-in
policy default. ADR-043 is not wholly superseded. Its authoritative constraint
composition, no-silent-precedence rule, trusted target-baseline policy,
contradiction semantics, non-prescriptive diagnostics, and prohibition on
runtime authorization bypass remain controlling.

## Discovery classification

```text
decision-required, resolved; promotion authorization and non-authorizing behavior-selection boundary
```

This decision changes the current promotion authorization/selection boundary.
It does not choose public UserBehavior field names, serialized enum values,
TOML/JSON/CLI representation, profile persistence, repository-scope identity,
binding generations, provider APIs, permission scopes, authentication, or an
implementation language.

## Decision

### 1. EffectivePromotionPolicy returns authorized route space

`EffectivePromotionPolicy` MUST expose the complete currently authorized route
set:

```text
allowed_routes ⊆ {
  DIRECT_TARGET_ADVANCE,
  PROVIDER_SUBMISSION
}
```

The set has no preference ordering. Each of the following is a resolved current
policy result:

```text
{DIRECT_TARGET_ADVANCE}
{PROVIDER_SUBMISSION}
{DIRECT_TARGET_ADVANCE, PROVIDER_SUBMISSION}
```

The two-route set is neither `MISSING` nor underdetermined merely because more
than one route is authorized. Policy determines authorization, not preference.

The immutable `PromotionTarget` remains outside `allowed_routes` exactly as
ADR-061 requires. `SAME_REPOSITORY | CROSS_REPOSITORY` remains derived from
source and target identity. `INDEPENDENT | STACKED` remains derived topology.
Neither derived dimension becomes UserBehavior.

### 2. Authoritative governance composition remains controlling

Authoritative constraints continue to compose without a generic precedence
ladder:

```text
provider / organization governance constraints
+ trusted target-baseline repository policy
+ other authoritative governance facts
→ authorized behavior space
```

A provider governance authorization fact may constrain
`EffectivePromotionPolicy`. Technical provider capability does not grant
authorization and is evaluated separately. This decision does not define the
provider-neutral `KNOWN_ALLOWED | KNOWN_FORBIDDEN | UNKNOWN` adapter contract;
that representation remains separate work.

ADR-051's execution boundary remains:

```text
REQUIRED
∩ SUPPORTED
∩ AUTHORIZED
∩ exact transition guards
→ executable
```

UserBehavior is not a fourth authority in that conjunction.

### 3. Policy, behavior, capability, and state outcomes remain distinct

The normalized outcomes are:

```text
required authoritative information unavailable / unobservable
→ MISSING / UNKNOWN

authoritative governance constraints mutually incompatible
→ POLICY_CONTRADICTION

valid authoritative policy cannot satisfy strict personal behavior
→ BEHAVIOR_UNSATISFIABLE

required semantic mechanism technically not realizable
→ UNSUPPORTED
```

These outcomes MUST NOT collapse into one another:

```text
BEHAVIOR_UNSATISFIABLE != POLICY_CONTRADICTION
UNSUPPORTED != POLICY_CONTRADICTION
```

Technical capability MUST NOT be represented as an
`EffectivePromotionPolicy` authorization state. Historical
`UNSUPPORTED_COMBINATION` wording is not a current policy-authorization outcome
when it denotes technical inability.

### 4. UserBehavior is non-authorizing

The governing invariant is:

```text
UserBehavior ⊆ authorization

UserBehavior never creates authorization.
```

At the semantic level, UserBehavior supports exactly:

```text
SOFT route preference ordering
STRICT route requirement
```

The V1 route domain is exactly:

```text
DIRECT_TARGET_ADVANCE
PROVIDER_SUBMISSION
```

The four semantic intents are:

```text
SOFT: prefer DIRECT_TARGET_ADVANCE, then PROVIDER_SUBMISSION
SOFT: prefer PROVIDER_SUBMISSION, then DIRECT_TARGET_ADVANCE
STRICT: require DIRECT_TARGET_ADVANCE
STRICT: require PROVIDER_SUBMISSION
```

No public names or serialized values are selected by this decision.

### 5. Personal behavior precedence is isolated from governance precedence

Behavior resolves only within personal behavior authority:

```text
applicable repository-specific UserBehavior
→ else global UserBehavior
→ else BuiltInBehavior
```

This ordering MUST NOT be copied into governance-source precedence.
Repository-specific UserBehavior does not override repository governance;
global UserBehavior does not override provider/organization governance; and
BuiltInBehavior authorizes nothing.

Persistence, portable repository-scope identity, profiles, and binding
generations remain outside this decision.

### 6. BuiltInBehavior owns zero-onboarding preference

The V1 built-in behavior is:

```text
SOFT preference order:
1. DIRECT_TARGET_ADVANCE
2. PROVIDER_SUBMISSION
```

This preserves ordinary zero-configuration behavior without treating preference
as governance. When both routes are authorized and positively usable, direct is
preferred. When direct is positively unavailable and provider submission
remains authorized and usable, behavior falls back to provider submission.

BuiltInBehavior MUST NOT enlarge `allowed_routes`, override governance, change
PromotionTarget or topology, alter required checks/reviews, grant provider
permission, or invent capability.

### 7. Route selection starts from current authorization

For a genuine realization-route choice:

```text
A = EffectivePromotionPolicy.allowed_routes
```

Core-derived exact facts then constrain which routes can satisfy the current
semantic obligation. UserBehavior MUST NOT change PromotionTarget, flatten or
invent topology, suppress a derived `REQUIRED` operation, or change the derived
source/target relation. If current core state already requires one semantic
provider operation, UserBehavior does not override that requirement.

Technical support is observed independently for the relevant route/mechanism as:

```text
SUPPORTED
UNSUPPORTED
UNKNOWN_INCONSISTENT
```

Only after current authorization, exact core constraints, and contextual
technical support have been established is behavior applied.

### 8. SOFT and STRICT resolution have different failure behavior

For SOFT behavior, routes are considered in preference order. A route positively
forbidden by policy is skipped. A route positively `UNSUPPORTED` may be skipped
for the next acceptable route. `UNKNOWN` or `UNKNOWN_INCONSISTENT` for a
higher-preference route is not positive unavailability and MUST fail closed or
localize rather than silently fall through.

For STRICT behavior, no fallback exists:

```text
required route not authorized by current policy
→ BEHAVIOR_UNSATISFIABLE

authorized route + required mechanism UNSUPPORTED
→ UNSUPPORTED

required authority or capability unknown
→ MISSING / UNKNOWN as applicable
```

None of these conditions is reclassified as `POLICY_CONTRADICTION` unless the
authoritative governance constraints themselves are mutually incompatible.

### 9. Transition-local waits do not reselect the route

After a route is positively selected, an unmet review, check, queue, exact-state,
or other transition-local prerequisite produces the existing localized wait for
that selected route. A temporary progression wait is not a new behavior
selection event and MUST NOT silently fall back from provider submission to
direct target advancement or conversely.

### 10. UserBehavior has a closed exclusion boundary

UserBehavior MUST NOT contain, select, mutate, or override:

```text
PromotionTarget
ConvergenceBase
source/target repository relation
PromotionGroup membership
ConvergenceUnit membership
promotion dependency topology
stack topology
merge strategy
restack algorithm
FF/non-FF mechanics
rebase mechanics
checkpoint membership
ContributionUnit lifecycle
ConvergenceUnit lifecycle
provider capability
provider governance
organization governance
repository governance
provider execution identity
required checks
required reviews
merge queue requirements
governance bypass
development validation
exact ancestry decisions
REVIEW_REQUESTED assertion
early/draft publication authority
generic manual finalization
executor/backend implementation choice
```

Native-Git versus provider-native execution of the same semantic operation is
RuntimeConfig or implementation plumbing, not UserBehavior. Ref-update
mechanics/governance is likewise not UserBehavior; a later decision may add an
authoritative ref-update policy dimension without turning it into personal
behavior.

### 11. Review and finalization semantics remain unchanged

`REVIEW_REQUESTED` remains an exact proposal/publication-governance assertion,
not a standing preference. `REVIEW_NOT_REQUESTED` early publication continues
to require explicit current authority or need; UserBehavior cannot create it.

ADR-062 remains controlling:

```text
provider target integration
REQUIRED ∩ SUPPORTED ∩ AUTHORIZED
+ fully preconditioned
→ Ruu progresses mechanically
```

No always-ask-before-merge, manual-merge default, or manual-finalization
preference is introduced. Human finalization remains relevant only when actual
governance requires it.

### 12. Runtime requests are not UserBehavior

An ad hoc caller request, invocation flag, or local operational configuration
cannot alter `EffectivePromotionPolicy`. Resolved durable/personal UserBehavior
may prefer or restrict only within current authorization. Neither can enlarge
authorization.

A runtime request such as `--force-direct` is not UserBehavior and carries no
promotion authority. Exact UserBehavior profile/store representation remains
outside this decision.

### 13. Policy and capability currentness remain immediate

Before each policy-sensitive mutation, all authoritative governance facts needed
for authorization, all technical capability/current facts needed for execution,
and exact Git/managed state MUST be current/revalidated.

A stale policy snapshot never authorizes mutation. A stale capability
observation never establishes support. Cache/TTL remains optimization only. When
atomic external check-and-mutation is unavailable, provider enforcement plus
exact post-operation observation remains the final external boundary.

The correction is solely:

```text
technical support != policy authorization
```

No detailed provider-observation contract is introduced here.

## Rationale

The correction lets governance state every route it authorizes without encoding
a user's preference as policy. It preserves zero-onboarding direct preference,
but moves that preference to a non-authorizing layer. It also keeps factual
technical capability from silently becoming governance authority.

A valid policy can therefore authorize both routes while different users express
different soft orderings or strict requirements, all without changing the
immutable destination, derived topology, governance requirements, or exact
mutation guards.

## Consequences

- `EffectivePromotionPolicy.allowed_routes` is the authoritative route-space
  result and may contain both routes without becoming missing or underdetermined.
- Built-in route selection moves from policy to `BuiltInBehavior`.
- UserBehavior is limited to non-authorizing soft ordering or strict requirement.
- Runtime requests and local operational config remain non-authorizing.
- Policy contradiction, behavior unsatisfiability, technical unsupported state,
  and unknown/missing authority remain separate outcomes.
- Provider governance facts may constrain policy while provider technical
  capability remains a separate execution guard.
- PromotionTarget, repository relation, dependency topology, review intent,
  finalization authority, and exact Git mechanics remain unchanged.
- Public UserBehavior vocabulary, profiles, persistence, migrations, and provider
  adapter details remain downstream work.

## Rejected alternatives

### Keep one scalar route in EffectivePromotionPolicy

Rejected. It conflates authorization with preference and misclassifies a complete
two-route authorization result as underdetermined.

### Let built-in policy choose direct

Rejected. The zero-onboarding ordering is personal/product behavior, not an
authoritative governance fact.

### Treat UserBehavior as another authorization source

Rejected. Personal behavior may only select or restrict inside current
authorization and may never create permission.

### Fall through on unknown capability

Rejected. Unknown is not positive unavailability and cannot safely justify a
lower-preference route.

### Reselect after a transition-local wait

Rejected. Pending checks, review, queue, or exact-state prerequisites are waits
on the selected route, not proof that another route should replace it.

### Add public fields, profiles, or persistence now

Rejected. This decision fixes semantics only; downstream work owns public names,
serialization, scope identity, profile binding, migration, and settings UX.

## Verification obligation

No new state-space package is created by this decision. Existing formal-
verification work owns future model coverage. The accepted specification and
this ADR are the oracle; existing v46 evidence does not prove ADR-087.

Future coverage MUST include at least:

```text
policy authorizes both routes
soft direct preference
soft provider preference
strict direct
strict provider
strict behavior incompatible with valid policy
policy contradiction
technical unsupported
unknown authority/capability
policy drift
capability drift
negative tests for every UserBehavior exclusion
```

The model must keep policy authorization, personal behavior, contextual support,
exact state, and transition-local prerequisites as separate axes and must include
falsifying cases for authorization enlargement, topology mutation, review-intent
creation, manual-finalization preference, unknown-as-unavailable fallback, and
route reselection caused only by a temporary progression wait.
