---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Use transition-local prerequisites instead of generic development-validation evidence"
id: "ADR-060"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "0b9016938a97fe74527447b647f3a4d52acd2daa41d247e3952c47bf8a984249"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-060 — Use transition-local prerequisites instead of generic development-validation evidence

- **Status:** Accepted
- **Date:** 2026-09-06
- **Decision order:** 060

## Context

ADR-057 correctly moved tests, review, security checks, validation retries, formatter/codegen loops, and related development-quality orchestration out of `ruu`. It nevertheless retained a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` protocol as a prerequisite that could gate managed checkpoints and other locally synthesized Git states.

Further analysis exposed a boundary problem. `ruu` is intentionally a state-dependent governed Git reconciler/super-command that may be triggered at any stage. If it must decide whether development validation is missing, it must understand or duplicate Development System policy about when code is sufficiently tested/reviewed/ready. That makes the Git engine non-neutral and creates a second orchestration/policy plane.

The architecture already contains narrower authoritative facts for transitions whose prerequisites genuinely belong outside Git: ContributionUnit lifecycle, ConvergenceUnit membership sealing, PromotionGroup declaration, review-request intent, promotion policy, provider checks/reviews/queue state, settlement intent, and similar transition-specific declarations.

## Decision

### 1. No generic development-validation gate exists in `ruu`

`ruu` MUST NOT require, interpret, persist, refresh, or emit a generic:

```text
DevelopmentValidationEvidence
DevelopmentValidationDemand
validation_basis_fingerprint
```

as a universal prerequisite for checkpointing, internal synthesis, promotion materialization, submission revision, or publication.

Tests, lint, typecheck, builds, semantic/agentic review, security validation, flaky-test policy, and other development-quality processes remain entirely Development System / repository-governance concerns.

### 2. Every transition is governed by its own minimal prerequisites

A `ruu` transition may proceed only from facts that are mechanically observable inside the Git/managed/provider domain plus the minimal authoritative external facts that genuinely belong to the owner of that transition boundary.

Examples:

```text
checkpoint
→ offered/transferable dirty ContributionUnit editing surface
+ exclusive mutation authority
+ ADR-059 canonical snapshot is structurally valid

ContributionUnit → ConvergenceUnit integration
→ authoritative managed checkpoint exists
+ exact topology/membership/ancestry/claim/conflict guards hold

ContributionUnit closure
→ external lifecycle authority declares CLOSED

ConvergenceUnit READY_INTERNAL
→ membership SEALED
+ every member/lifecycle/checkpoint/reconciliation requirement resolved
+ internal Git fixed point holds

PromotionGroup / PromotionUnit formation
→ explicit closed PromotionGroup declaration
+ complete exact READY_INTERNAL member set
+ deterministic repository-local projection/materialization

publication
→ exact PromotionUnit/dependencies
+ current promotion policy/capability/provider facts
+ exact review-request intent where that specific publication transition requires it

provider finalization
→ exact current provider/target facts and transition-specific policy guards
```

No transition may infer a higher-level development stage such as `READY_TO_COMMIT`, `READY_FOR_PR`, or `VALIDATED` merely from agent/session/runtime state.

### 3. Development quality controls when the Development System exposes intent/facts, not a Git-side validation certificate

A Development System, human, script, IDE, or agent may run whatever quality process it chooses before making work transferable, closing a ContributionUnit, declaring publication intent, or taking another externally owned lifecycle/governance action.

Those reasons do not cross the `ruu` boundary unless the transition itself needs a specific authoritative fact already defined by the architecture.

Invocation/convergence demand is still not a general authority token and does not grant mutation authority, semantic ownership, grouping authority, or policy override. Existing transition-specific authority boundaries remain in force.

### 4. Deterministically synthesized clean Git states do not wait for generic validation evidence

If `ruu` can deterministically construct a clean exact Git result and every transition-local Git/managed/policy/provider prerequisite holds, that result may be adopted/progressed without a generic development-validation handoff.

If semantic authoring is required, the result remains blocked through the existing exact `RECONCILIATION_REQUIRED`, review-correction, settlement, policy-contradiction, or other transition-specific mechanism. A later authored result re-enters ordinary current-state revalidation; it gains no special authority from the external authoring process.

### 5. Exact-state binding remains mandatory where evidence/facts genuinely exist

ADR-060 does **not** weaken exact-state/TOCTOU protections. Exact bindings remain required for transition-specific state such as:

```text
provider review/check/queue observations
review-request intent tied to exact submission revision
promotion source bindings
policy snapshots/fingerprints
expected-old / CAS guards
reconciliation descriptors
settlement generations
final target-integration observations
```

The removed concept is only the generic development-quality certificate that previously sat in front of many unrelated Git transitions.

### 6. 30.28 is closed as obsolete

Backlog 30.28 is not solved by designing a smaller `DevelopmentValidationEvidence` schema. The generic schema is unnecessary and is removed from the `ruu` contract.

## Supersession / amendments

This ADR supersedes:

- ADR-029's universal development/full-verification prerequisite for authoritative managed-state adoption;
- ADR-030's generic `DevelopmentValidationEvidence` binding/reuse requirement as a `ruu` concern;
- ADR-057 sections 3–7 and 10 insofar as they define/consume `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` or hold synthesized candidates awaiting such evidence;
- ADR-010 amendments that applied exact-state binding specifically to generic external development-validation evidence.

ADR-057's central execution boundary remains accepted: development verification execution is outside `ruu`. ADR-010's broader exact-state principle remains accepted for the transition-specific evidence/facts that still exist.

## Consequences

- `ruu` is usable with `/go`, another harness, scripts, IDEs, or humans without emulating a validation-certificate service.
- Development System policy is not duplicated inside the Git engine.
- A successful Git transition is justified by its own explicit state predicate rather than a generic `VALIDATED` notion.
- Provider/review/policy governance remains enforceable because those are transition-specific facts, not development-quality inference.
- The engine state space loses generic validation-demand/evidence wait states.

## Amendment — ADR-062 / ADR-063 (2026-09-07)

The transition-local prerequisite model is preserved. Provider submission existence itself is not a generic validation prerequisite; it is created only when the provider route currently needs projection. Semantic findings/backlog remain external. Provider blocking governance and target-finalization facts remain narrow transition-specific inputs.

## Amendment — ADR-064 (2026-09-07)

ADR-064 does not reintroduce generic validation evidence. It clarifies how a Development System that validates before commit can bind that decision to the eventual Git checkpoint: durable transferability freezes external mutation, and the exact ADR-059 candidate is constructed/revalidated/committed under `ruu`'s exclusive claim. The transition-local prerequisite model remains unchanged.
