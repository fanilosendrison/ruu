---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Resolve promotion policy by authoritative constraint composition"
id: "ADR-043"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "76ff2ac39568375abfe55fa0d63a4831fb47b5d606a6f8adcd98230760a46fcf"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-043: Resolve promotion policy by authoritative constraint composition

- **Status:** Accepted; amended by ADR-061
- **Date:** 2026-09-05
- **Decision order:** 043

## Context

ADR-026 made promotion repository-policy-driven and required a current effective policy before any promotion mutation, but backlog item 30.14 still left open how that effective policy is derived when several sources can influence promotion behavior.

The former open-source list mixed fundamentally different concepts:

```text
explicit local config
repo-committed config
provider branch/ruleset state
organization policy
human/orchestrator override
defaults
```

A linear precedence rule would be unsafe and semantically misleading. For example, a repository that explicitly requires `DIRECT` while provider governance requires `PR` is not a case where one source should silently “win”; the declarations are jointly unsatisfiable and indicate governance drift or misconfiguration.

The architecture also requires zero mandatory repository onboarding for ordinary repositories, while preserving fail-closed promotion semantics and preventing a candidate from changing the rules that authorize its own promotion.

Finally, a policy contradiction must not collapse into an opaque error. External agent/orchestrator/human systems need exact factual evidence of the contradiction, while `ruu` must not cross the boundary into recommending or applying a semantic/governance remedy.

## Decision

### 1. Effective promotion policy is compiled from authoritative facts and constraints, not from a precedence ladder

For promotion authorization, the authoritative inputs are:

```text
provider capabilities/current provider facts
provider governance constraints
organization governance constraints, when applicable
trusted repository-committed policy, when present
built-in policy rules for still-underdetermined dimensions only
```

These inputs have different semantics but are composed into one `EffectivePromotionPolicy`.

Provider capabilities bound what is technically realizable. Provider/organization governance and trusted repository policy contribute normative constraints. No source is granted a general “wins over” precedence that silently rewrites another authoritative constraint.

For every policy dimension, `ruu` computes the jointly admissible space. Examples:

```text
provider permits {DIRECT, PR}
repo requires PR
→ admissible = {PR}

provider requires PR
repo requires DIRECT
→ admissible = ∅
→ CONTRADICTORY

provider permits {DIRECT, PR}
repo says nothing
→ dimension remains underdetermined until a built-in rule resolves it
```

For monotonic dimensions, constraints compose according to their semantics rather than scalar overwrite. For example, two minimum-review constraints compose to the stricter minimum. An explicit requirement and an explicit incompatible prohibition are contradictory.

### 2. Explicit authoritative contradictions block; they are never silently normalized

When authoritative constraints have no common satisfying assignment:

```text
policy_state = CONTRADICTORY
EffectivePromotionPolicy = absent
promotion on the affected repository/obligation = blocked
unrelated global obligations = continue
```

`ruu` MUST NOT silently replace an explicit repository requirement with provider behavior merely because the provider is operationally stronger. A contradiction is itself authoritative information that must remain visible until one of its source facts changes.

This also applies to governance drift. Example:

```text
trusted repo policy requires DIRECT
provider ruleset later changes to require PR
→ CONTRADICTORY
→ no promotion until authoritative inputs become satisfiable again
```

### 3. Repository policy cannot be bypassed per invocation

There is no promotion-policy runtime override.

The following MUST NOT alter `EffectivePromotionPolicy` or weaken its constraints:

```text
human invocation flags
agent preference
orchestrator preference
caller identity
explicit local user config
```

If an operator or external system wants different promotion semantics, it must change an appropriate authoritative policy/governance source through that source's normal mechanism. The resulting changed source is then observed and compiled on a later/current revalidation.

A caller may supply non-authorizing assertions or operational inputs, but these cannot enlarge the set of policy-authorized actions.

Local configuration may still control non-policy runtime plumbing such as logging, local paths, credentials/provider access plumbing, caches, or executor settings. It has no authority over promotion semantics.

### 4. Repository-committed policy is read from the trusted target baseline, never from the candidate it governs

For a promotion whose target currently resolves to exact target state `T`, the repository-committed policy governing that promotion is the policy from the trusted authoritative target baseline associated with `T`, not a policy modification contained only in the candidate/submission being promoted.

Therefore:

```text
target policy P0
candidate changes P0 → P1

promotion of that candidate
→ governed by P0

candidate later becomes authoritative target state
→ P1 may govern subsequent promotions after ordinary refresh/revalidation
```

A candidate can never authorize its own promotion by modifying promotion policy in the same candidate.

### 5. Built-in rules provide zero-onboarding closure, not override authority

Absence of an explicit repository policy file is not equivalent to missing effective policy.

After authoritative capabilities/governance/repository constraints are composed, deterministic built-in policy rules may fill only dimensions that remain underdetermined. They MUST NOT contradict or weaken an explicit authoritative constraint.

The baseline default for `promotion_mode` is:

```text
if DIRECT is admissible and no authoritative constraint requires indirect promotion
→ DIRECT

if only PR is admissible
→ PR
```

This allows a newly encountered ordinary personal repository with no explicit `ruu` policy and no PR requirement to resolve to `DIRECT` without onboarding, while a protected repository naturally resolves to `PR`.

`MISSING` therefore means that a complete effective policy cannot be derived from the available authoritative inputs and built-in rules; it does not mean merely “no repo policy file exists”.

### 6. Policy contradiction is a first-class factual external signal

A contradiction MUST surface as a typed, machine-readable blocking outcome with enough factual provenance for an external Development System/operator to understand exactly why promotion is impossible.

The descriptor MUST include, as applicable:

```text
repository_id
blocked obligation/operation identity
policy_state = CONTRADICTORY
conflicting policy dimension(s)
for each incompatible constraint/fact:
  source kind
  source identity
  exact source revision/version/fingerprint when available
  normalized factual constraint/value
relevant exact target/provider observation identity
```

The descriptor is diagnostic only.

`ruu` MUST NOT include or compute:

```text
recommended_fix
resolution_candidates
ranked remediation
suggested policy/governance mutation
```

and MUST NOT autonomously mutate governance/policy in response to the contradiction.

The external Development System/operator interprets the factual signal and decides whether any external action is appropriate.

### 7. Current-state/fingerprint rules still apply

The compiled `EffectivePromotionPolicy` remains exact-state-bound and fingerprinted.

```text
CURRENT(policy_fingerprint)
→ may authorize promotion subject to all other guards

policy source/fact changes
→ previous fingerprint stale
→ recompute before mutation

MISSING | STALE | CONTRADICTORY | UNSUPPORTED_COMBINATION | UNKNOWN_INCONSISTENT
→ no promotion authorization
```

ADR-026's refresh-before-critical-action requirement remains in force. ADR-044 subsequently closes backlog 30.15 by making immediate pre-mutation revalidation authoritative and cache/TTL non-authorizing.

## Rationale

This decision preserves several important properties simultaneously:

- repository governance is real policy, not a preference that a caller can bypass;
- provider/org facts cannot be ignored, but also do not silently rewrite repository intent;
- drift and misconfiguration are visible rather than hidden by fallback;
- a candidate cannot self-escalate by editing its own promotion rules;
- ordinary repositories require no mandatory onboarding;
- identical authoritative repository/provider state produces the same promotion authorization regardless of local machine preferences or caller identity;
- `ruu` reports exact mechanical/policy facts while leaving semantic/governance decisions to the external system.

## Consequences

- Backlog item **30.14 is closed**.
- The former phrase “policy source precedence” is replaced by authority classification, constraint composition, contradiction detection, and deterministic default completion.
- Explicit local config and runtime human/agent/orchestrator overrides are not promotion-policy sources.
- Repository policy changes become effective for later promotions only after they are authoritative on the trusted target baseline.
- Governance drift can intentionally stop promotion until the authoritative sources are reconciled externally.
- `POLICY_CONTRADICTION`/`CONTRADICTORY` outcomes must expose exact factual provenance but no remediation advice.
- Exact constraint-schema representation remains implementation/schema work where not already fixed; this ADR fixes semantics, not one serialization.
- Policy refresh/currentness semantics are closed by ADR-044; cache/TTL is optimization only and cannot establish `CURRENT`.

## Amendments

This ADR amends ADR-026 and ADR-039, the External Control Plane contract, and the main promotion-policy state/invariant sections where they previously left policy-source precedence or contradiction signaling unspecified.

## Subsequent clarification by ADR-051

ADR-051 closes provider capability discovery and clarifies one dimension boundary without changing this ADR's authority-composition rule: current `INDEPENDENT | STACKED` promotion topology is derived managed state under ADR-050, not a policy-selected layout. Provider capability observations are contextual semantic-operation facts; effective policy authorizes/constrains the operations required to represent current derived topology. Technical support and policy authorization remain independent conjunctive guards.


## Amendment by ADR-056

For a brand-new repository, repository-committed promotion policy cannot govern creation because the repository does not yet exist. ADR-056 therefore uses External Control Plane `RepositoryCreationPolicy` only for creation/bootstrap authority. After `RepositoryBootstrapContract` admission, the configured target exists at exact `B0`; from that point onward this ADR applies normally, and any trusted repository-committed promotion policy is read from the authoritative `B0`/later target baseline rather than from an unpromoted candidate.

## Amendment by ADR-061

Policy composition is evaluated **for** an immutable already-bound PromotionTarget; it no longer resolves the target identity itself. Trusted repository policy is still read from the current exact target baseline, but target repository/ref identity cannot change merely because policy/config/provider facts change. Contradiction blocks the promotion instead of causing target substitution.

## Amendment — ADR-062 (2026-09-07)

The policy-composition model is unchanged, but the current route dimension is `DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION`. Built-in closure must not invent a PR/provider projection when neither formal review publication nor explicitly authorized early publication is currently required. Provider target-integration/finalization operations are separate contextual policy/capability dimensions.

