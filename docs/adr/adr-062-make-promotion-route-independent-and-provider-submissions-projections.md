---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make promotion route-independent and treat provider submissions as projections"
id: "ADR-062"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "71cd209b6da509edc5b90f9f3022dcc355c2cfb30b3195fe42598db236453afc"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-018"
    - "ADR-021"
    - "ADR-026"
    - "ADR-027"
    - "ADR-032"
    - "ADR-043"
    - "ADR-044"
    - "ADR-049"
    - "ADR-050"
    - "ADR-051"
    - "ADR-052"
    - "ADR-053"
    - "ADR-055"
    - "ADR-061"
  supersedes: []
  confirms: []
governs: []
---

# ADR-062 — Make promotion route-independent and treat provider submissions as projections

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 062
- **Closes:** backlog 30.36
- **Amends:** ADR-018, ADR-021, ADR-026, ADR-027, ADR-032, ADR-043, ADR-044, ADR-049, ADR-050, ADR-051, ADR-052, ADR-053, ADR-055, ADR-061 and the main promotion/provider model

## Context

The architecture progressively separated internal Git convergence from semantic development validation, promotion grouping, exact candidate identity, policy authorization, provider capability, and final target realization. ADR-049 already introduced a generic logical `submission_id` and distinct provider-facing submission refs; ADR-051 already requires the core to derive semantic operations before provider adapters map them to provider mechanisms.

However, the current normative vocabulary still exposes:

```text
promotion_mode = DIRECT | PR
```

and many current-state sections describe a separate “PR promotion” branch.

That wording gives the Pull Request more architectural weight than it should have. A PR is not a distinct semantic kind of promotion. It is one provider-specific representation of an indirect/provider-mediated path by which an exact candidate may eventually be realized in its already-bound `PromotionTarget`.

This matters in a development system designed natively for agents:

- tests/reviews/findings may already have happened before publication;
- promotion grouping exists independently of PR boundaries;
- promotion authorization exists independently of the PR UI;
- provider checks/reviews/queues may be mandatory governance facts, but they remain external/provider mechanics;
- GitHub calls the provider surface a Pull Request, GitLab calls the analogous surface a Merge Request, and other providers may expose another submission/change object entirely;
- when every required authorization is satisfied, a separate ceremonial “click Merge” should not be modeled as a new semantic decision unless governance explicitly requires a distinct human finalizer.

The intended conceptual model is therefore:

```text
exact candidate
      ↓
current authorization / policy / provider facts
      ↓
PROMOTION
      ↓
realize candidate in immutable PromotionTarget
```

with different **realization routes**, not different meanings of promotion.

## Decision

### 1. Promotion has one semantic objective

For one exact repository-local PromotionUnit candidate `C` and immutable `PromotionTarget T`, the semantic objective is always:

```text
RealizePromotion(C, T)
```

The route used to reach `T` does not change the meaning of promotion.

The core therefore no longer treats `DIRECT` and `PR` as two semantic promotion modes.

### 2. Replace `promotion_mode = DIRECT | PR` with a target-realization route

The current normative policy dimension becomes:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE
  PROVIDER_SUBMISSION
```

Historical mappings are:

```text
promotion_mode = DIRECT
→ target_realization_route = DIRECT_TARGET_ADVANCE

promotion_mode = PR
→ target_realization_route = PROVIDER_SUBMISSION
```

The distinction is mechanical/governance-facing:

```text
DIRECT_TARGET_ADVANCE
→ the exact target ref may be advanced only through ADR-052
  AdvanceTargetFF(expected_old, new) semantics

PROVIDER_SUBMISSION
→ Ruu MUST NOT directly push/update the target ref
→ it creates/updates/observes a provider-facing submission projection
→ provider-governed target-integration operations eventually realize the target
```

Policy still answers **HOW**, not **WHERE**. ADR-061 remains unchanged: `PromotionTarget` is immutable and pre-authoring.

### 3. `ProviderSubmission` is the core-facing projection; PR/MR is adapter terminology

The core concept is the already-existing logical `Submission` / `PublicationEpisode` model.

A provider adapter may materialize one publication episode as:

```text
GitHub     → Pull Request
GitLab     → Merge Request
other      → provider-native change/submission object
```

Therefore current core state should prefer:

```text
provider submission
provider submission identity
provider submission head
provider submission review/check state
provider target-integration state
```

over provider-specific terms such as `PR` except in explicit adapter examples or historical ADR text.

ADR-049's stable logical `submission_id`, exact `submission_revision`, distinct submission ref, and ADR-055 `PublicationEpisode` remain valid and become the canonical core abstraction.

### 4. Provider submission is a projection, not the source of internal readiness

The existence of a provider submission does not define:

```text
Work
Candidate
Evidence
Finding
Authorization
internal readiness
semantic completion
```

A provider submission is created only because the current target-realization route or provider workflow requires an external representation of the already-existing exact promotion candidate.

The ordering is conceptually:

```text
internal development/convergence
→ exact candidate
→ current promotion authorization facts
→ provider submission projection when required
```

not:

```text
open PR
→ discover whether the work is ready
```

Provider-only CI/review may still add independent governance evidence after projection.

### 5. Target direct mutation remains forbidden on the provider-submission route

`PROVIDER_SUBMISSION` means:

```text
direct target ref push/update by Ruu
→ forbidden
```

It does **not** mean that `ruu` must remain passive forever while another human presses a provider button.

A provider target-integration operation such as:

```text
REQUEST_PROVIDER_TARGET_INTEGRATION
ENTER_MERGE_QUEUE
ENABLE_AUTO_MERGE
MERGE_PROVIDER_SUBMISSION
```

may be executed by `ruu` when all of the following are current:

```text
operation REQUIRED by current state
AND capability SUPPORTED in the exact context
AND EffectivePromotionPolicy AUTHORIZES it
AND all provider/governance prerequisites are satisfied
AND exact submission/head/target/currentness guards hold
AND required claim/fencing/recovery guards hold
```

The resulting target mutation is provider-governed finalization, not a direct target-ref mutation by the Git ref engine.

### 6. No ceremonial merge gate exists by default

When all current required conditions for provider target integration are satisfied, `ruu` SHOULD progress the provider integration operation automatically as part of ordinary fixed-point reconciliation.

There is no additional generic state:

```text
WAIT_FOR_SOMEONE_TO_CLICK_MERGE
```

merely because historical human workflows commonly used a manual button.

If current authoritative governance genuinely requires a distinct human finalizer, maintainer action, deployment approval, or other non-automatable authority, that requirement appears as an explicit current provider/governance prerequisite or lack of authorization/capability. In that case the obligation waits.

Thus:

```text
all required current authorization satisfied
+ machine-authorized provider integration operation available
→ integrate automatically
```

while:

```text
explicit human-finalizer requirement remains unsatisfied
→ localized wait
```

### 7. Review request remains provider-facing publication intent only

ADR-032 remains valid after terminology generalization:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

are provider-submission publication/governance intents, not internal development lifecycle states.

A GitHub adapter may still map:

```text
REVIEW_NOT_REQUESTED → draft Pull Request
REVIEW_REQUESTED     → ready-for-review Pull Request
```

The semantic review process that justifies `REVIEW_REQUESTED` remains outside `ruu` under ADR-057/060.

### 8. Close backlog 30.36 with a fail-closed/no-projection default

The previously open question asked what deterministic fallback should apply when exceptional `REVIEW_NOT_REQUESTED` publication eligibility remains underdetermined.

The new answer is:

```text
explicit current authority/need for early provider submission
→ REVIEW_NOT_REQUESTED publication may occur

REVIEW_REQUESTED current
→ nominal provider submission publication may occur

neither is currently established
→ do not publish a provider submission yet
```

No draft/early PR is created merely because the system wants every candidate to have a PR object.

This is fail-closed and matches the projection model: provider submission is optional until some current target/provider/governance requirement actually needs it.

Backlog **30.36 is closed**.

### 9. Stacked and cross-repository semantics remain unchanged, but are submission semantics

ADR-050 remains normative:

```text
stack shape
= derived from exact unsatisfied promotion dependency
```

The provider representation may be stacked provider submissions. On GitHub those happen to be stacked PRs.

ADR-047 still does not split one same-repository PromotionGroup projection merely to manufacture a stack.

Cross-repository publication likewise becomes:

```text
CROSS_REPOSITORY provider submission
```

with GitHub fork→upstream PR as one adapter realization.

### 10. Map the broader agentic-development model without duplicating ontology

The broader development model:

```text
Work
Candidate
Evidence
Finding
Authorization
Promotion
```

maps onto the current architecture as follows.

#### Work

Owned above `ruu` by the Development System / External Control Plane.

It may correspond to a task, user intent, session-level ship, or another semantic unit. `ruu` does not need a `Work` entity for Git safety.

#### Candidate

At promotion time, the closest exact core object is the ADR-048 exact materialized promotion candidate bound to one exact immutable PromotionUnit and current effective base.

Checkpoint candidates and other exact transition candidates remain narrower Git-level candidates.

#### Evidence

Development-quality evidence remains external under ADR-057/060. Provider checks/reviews/queue/currentness observations remain transition-specific provider facts where the provider route requires them.

No generic Evidence super-object is introduced into `ruu` merely to match the conceptual model.

#### Finding

Semantic review findings remain outside `ruu`; ADR-063 defines the backlog boundary. Blocking provider `CHANGES_REQUESTED` remains a specific provider-governance state that may generate an exact ReviewCorrectionDemand.

#### Authorization

The conceptual authorization boundary is represented by the current conjunction:

```text
required
∩ supported
∩ authorized
∩ exact transition-local prerequisites
```

plus ADR-043/044 immediate currentness rules.

A durable generic authorization token is deliberately **not** added because stale authorization must never bypass fresh policy/provider revalidation.

#### Promotion

Promotion is `RealizePromotion(exact candidate, immutable PromotionTarget)` regardless of target-realization route.

### 11. Historical PR terminology remains valid only as history or adapter example

Prior ADRs are not rewritten to erase decision history. Their current normative reading is amended as follows:

```text
PR mode
→ PROVIDER_SUBMISSION target-realization route

PR identity
→ provider submission identity / provider-specific surface identity

PR head
→ provider submission head

PR create/update
→ provider submission create/update

provider PR merge
→ provider target-integration/finalization outcome
```

GitHub-specific behavior may still be documented explicitly as a concrete adapter example.

## Rationale

This change preserves every Git/provider safety property already designed while correcting the abstraction boundary.

The Pull Request remains operationally important when team or external-repository governance requires it, but it is no longer treated as a universal workflow primitive or a semantic kind of promotion.

The result is closer to the actual responsibility split:

```text
Development System
→ semantic work, tests, agentic review, findings

Ruu
→ exact Git state, convergence, candidate materialization,
  current policy/capability guards, promotion progression

Provider adapter
→ external submission projection and provider governance mechanics
```

It also removes a human-era ceremony from the normative model: once all actual authorities are satisfied, target integration is a mechanical consequence rather than another unexplained decision.

## Consequences

- `promotion_mode = DIRECT | PR` is removed from the current normative vocabulary.
- Current policy resolves a target-realization route, not a semantic PR-vs-direct promotion mode.
- PR/MR terminology moves to provider-adapter/examples; generic core state uses Submission/PublicationEpisode.
- ADR-049/050/055 become more central, not less: they already contain the correct provider-projection abstraction.
- Strict GitHub team workflows still create PRs and respect reviews/checks/branch protection/merge queue.
- External GitHub contributions still create fork→upstream PRs.
- Solo repositories may continue to use ADR-052 direct target advancement when policy permits it.
- Provider finalization is automatically progressed when it is current, supported, authorized, and fully preconditioned.
- Explicit human finalization remains possible only as an actual governance requirement, not a default ceremony.
- Exceptional early/draft provider submission has no implicit fallback; absence of explicit authority/need means no submission yet.
- Backlog 30.36 is closed.

## Rejected alternatives

### Remove provider submissions entirely

Rejected. Team governance and external contribution workflows genuinely require them.

### Keep `PR` as the core indirect-route name because GitHub is the primary provider

Rejected. It leaks one provider's UI/protocol term into the semantic core and obscures the fact that promotion exists independently of the PR object.

### Treat all provider integration as passive external action

Rejected. It would preserve an unnecessary human-era merge ceremony and prevent `ruu` from progressing a fully authorized provider workflow to its fixed point.

### Add a durable generic `PromotionAuthorization` token

Rejected. ADR-043/044 intentionally require current authoritative revalidation. A stale token must not authorize a later mutation after policy/provider movement.

### Always create a draft submission as soon as a candidate exists

Rejected. A provider submission is a projection, not a required internal lifecycle object. Early publication requires explicit current need/authorization.

## Amendment — ADR-065 (2026-09-07)

Provider submission projection/finalization remains non-semantic, but provider `MERGED` / `PROVIDER_FINALIZED` is not itself terminal promotion. `RealizePromotion(C,T)` completes only after ADR-065 exact target realization proof: native Git ancestry where preserved, otherwise exact provider result binding `C → R` plus independent authoritative target observation containing `R`.
