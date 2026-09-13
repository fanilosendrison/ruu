---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make promotion repository-policy-driven instead of universally PR-mediated"
id: "ADR-026"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "46acd771792650d64435bad108f649e81c52fef1c2b1b5fc0ef35fe1932c1da2"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-026: Make promotion repository-policy-driven instead of universally PR-mediated

- **Status:** Accepted — amended by ADR-029, ADR-032, and ADR-043; amended by ADR-061
- **Date:** 2026-09-04
- **Decision order:** 026

## Context

ADR-018 deliberately made protected `main` read-only so the system would work inside strict teams. That is a valid policy for protected repositories, but it became an architectural universal.

The system must also support:
- solo repositories where direct promotion/push to the target branch is intentionally allowed;
- strict team repositories requiring PR/CI/review/merge queue;
- contributions where the publication repository differs from the upstream target repository.

The correct invariant is not “always PR” or “always direct”. It is “respect the repository's current promotion policy”.

## Decision

Every managed repository has a resolved promotion policy that `ruu` refreshes/revalidates on every executed global sweep. Under ADR-044, every policy-sensitive promotion mutation additionally requires an immediately preceding re-observation/revalidation of all mutable authoritative policy sources; cache age/TTL alone never establishes `CURRENT`.

The policy is modeled along separate dimensions:

```text
promotion_mode:
  DIRECT
  PR

promotion_topology:
  INDEPENDENT
  STACKED

publication_relation:
  SAME_REPOSITORY
  CROSS_REPOSITORY
```

with repository/provider capability constraints determining which combinations are valid.

The policy also resolves at least:

```text
target_repository
target_ref
publication_repository / remote when needed
provider/governance capabilities
submission-history rewrite permissions
```

Semantics:

```text
DIRECT
→ Ruu may advance/push the configured target ref
  only through the policy-authorized direct-promotion algorithm

PR
→ Ruu publishes submission ref(s), creates/updates/observes PR(s),
  and never bypasses target governance
```

`STACKED` is meaningful for PR promotion and requires provider/policy support.

`CROSS_REPOSITORY` means the PR source publication repository differs from the target repository (for example a fork → upstream contribution). Provider capability determines whether stacked cross-repository submission is supported.

An invalid, missing, stale, or internally contradictory policy fails closed for promotion while unrelated convergence may continue.

## Rationale

The architecture should adapt to repository governance rather than hard-code one governance model.

This preserves:
- aggressive trunk-based direct integration for repositories that explicitly permit it;
- strict PR-based team compatibility;
- external/fork contribution workflows;
- one convergence engine with policy-driven promotion behavior.

## Consequences

- ADR-018 remains valid as the `promotion_mode=PR` protected-target case, not as a universal rule.
- `main` is no longer globally read-only; the configured target ref is read-only in PR mode and policy-authorized mutable in DIRECT mode.
- Direct promotion does not bypass a protected target. If protection/policy says PR, direct mutation is forbidden.
- Repository policy is first-class shared coordination state and a state-bound input to promotion authorization.
- Policy movement invalidates stale promotion intentions and requires recomputation.
- A single `ruu` invocation may process different repositories under different policies.
- Cross-repository publication and target identity are modeled separately.

## Alternatives considered

- **Universal PR mode:** rejected because it unnecessarily changes solo trunk-based semantics.
- **Universal direct mode with “try PR on failure”:** rejected because branch protection/governance must be an authorization input, not a fallback.
- **One global user policy:** rejected because repositories can have different governance requirements simultaneously.
- **Infer permission only from a failed push:** rejected because destructive/unauthorized attempts should not be used as policy discovery.

## Related decisions

Partially supersedes ADR-018 and amends ADR-014, ADR-017, ADR-020, ADR-021, and ADR-022.

## Amendment by ADR-029

Promotion policy must also resolve/authorize the required verification contract for locally produced promotion candidates.

In `DIRECT` mode, the exact candidate that would advance the target must have valid development-validation evidence before guarded target advancement. If the promotion candidate is an exact already-verified state and ADR-030 evidence remains valid, evidence may be reused.

In `PR` mode, newly materialized/revised submission candidates must satisfy required managed-state verification before authoritative publication; provider-specific governance/checks may add further evidence.

## Amendment by ADR-032

PR-mode publication policy also governs whether the current submission is published with:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

The default/nominal path requests review only after the configured PR-author quality gate holds. Explicit policy may permit `REVIEW_NOT_REQUESTED` publication for bounded provider-specific verification, stack exposure, or code-level early feedback.


## Amendment by ADR-043

The effective promotion policy is no longer derived by a generic source-precedence ladder. Provider capabilities/current facts, provider/organization governance, and trusted repository-committed policy are composed as authoritative constraints. Incompatible explicit constraints produce `CONTRADICTORY` and block promotion rather than silently falling back.

Repository-committed policy governing a candidate is read from the trusted exact target baseline, never from policy changes that exist only in that candidate. Runtime human/agent/orchestrator requests and explicit local config cannot bypass or alter promotion authorization. Deterministic built-in rules fill only still-underdetermined dimensions, including zero-onboarding `DIRECT` resolution when direct promotion is admissible and no authoritative constraint requires an indirect path.

Policy contradictions are surfaced externally with exact factual provenance and no remediation recommendation; deciding how to react remains outside `ruu`.

## Amendment by ADR-051

Current `INDEPENDENT | STACKED` promotion topology is no longer a policy-selected layout dimension. ADR-050 derives dependency/topology from exact managed base/predecessor/target state; ADR-051 makes provider capability a contextual semantic-operation observation over the exact required transition. Repository/provider policy may authorize or forbid the operation needed to represent that derived dependency, but does not select stack shape. Execution requires the transition to be required, contextually supported, and authorized.

## Amendment by ADR-052

In `DIRECT` mode, policy authorization applies to the semantic target mutation `AdvanceTargetFF(target, expected_old=B, new=C)`. ADR-048 has already materialized/verified exact `C`; ADR-052 forbids target-worktree/merge staging and requires one exact-old CAS+FF effect. Backend implementation mechanisms do not weaken the policy/currentness or descendant-only target contract.

## Amendment by ADR-055

The External Control Plane companion contract now explicitly records the accepted authority boundary: user/agent/session/orchestrator/runtime requests cannot manufacture promotion authorization or bypass current authoritative provider/organization governance, trusted target-baseline repository policy, contextual capability facts, or ADR-044 currentness checks.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-061

`target_repository` and `target_ref` are no longer outputs selected by EffectivePromotionPolicy. They come from the immutable pre-authoring ConvergenceUnit PromotionTarget. Likewise SAME_REPOSITORY versus CROSS_REPOSITORY is derived from authoritative source repository identity + PromotionTarget; policy/provider capability authorizes or blocks the required relation and resolves the permitted mechanics, but never retargets the work.

## Amendment — ADR-062 (2026-09-07)

Repository policy still determines **how** an exact candidate may reach its already-bound target, but the current policy dimension is `target_realization_route = DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION`, not semantic `DIRECT | PR` promotion modes. Provider submission is a projection route; GitHub PR is one adapter surface. Policy/governance may also authorize or require the exact provider target-integration/finalization operation.

