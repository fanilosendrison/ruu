---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Bind integration/promotion readiness and validation evidence to exact Git state"
id: "ADR-010"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "6c50028fcd91643c3c973b6028eb79231d0a5470c049ae3763dd87d295a77693"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-010: Bind integration/promotion readiness and validation evidence to exact Git state

- **Status:** Accepted — broader exact-state binding retained; generic development-validation amendments superseded by ADR-060
- **Date:** 2026-09-04
- **Decision order:** 010

## Context

Concurrent synchronization can move contribution-unit, convergence-unit, target/base, submission, or provider-visible refs after tests/review/readiness were computed. Reusing an approval for a different exact Git state would let stale evidence authorize unvalidated code.

## Decision

Every readiness or validation result that authorizes an upward transition is state-specific. It must identify the exact Git state and policy/context dimensions it validated.

Immediately before mutation or adoption:

- `contribution-unit → convergence-unit` revalidates the expected contribution-unit tip/commit set and convergence-unit tip;
- `target/base → convergence-unit` synchronization revalidates the exact source and convergence-unit tips;
- promotion-unit source binding revalidates the exact bound convergence-unit state;
- submission create/update/revision transitions revalidate the exact current submission revision/head and its source binding;
- provider-governed completion re-reads authoritative provider/target facts rather than assuming an earlier head relation still holds.

Relevant ref, policy, or declared verification-context movement invalidates or requires regeneration/re-reading of stale evidence according to the evidence class involved.

## Rationale

OID-exact/state-exact evidence closes time-of-check/time-of-use races between validation and concurrent Git movement.

## Consequences

- `convergence-unit → contribution-unit` synchronization that creates a new contribution-unit tip invalidates readiness/evidence tied to the old contribution-unit state.
- `target/base → convergence-unit` synchronization that creates a new convergence-unit tip invalidates convergence-unit readiness tied to the old tip.
- Reopening/changing a bound convergence unit makes an exact promotion-unit source binding stale.
- A submission head/revision change invalidates exact-head review/check/readiness assertions unless the applicable provider evidence is explicitly re-read/rebound for that exact revision.
- Where readiness/evidence classes remain, exact-state binding is mandatory. ADR-037 removes the former separate ContributionUnit integration-readiness evidence class.

## Alternatives considered

- **Readiness as a branch-level boolean:** rejected because branch contents can change after the boolean is set.
- **Trust orchestration metadata without re-reading refs/provider state:** rejected under concurrent movement.

## Supersession / amendment note

Exact-state binding covers internal contribution-unit/convergence-unit OIDs, promotion-unit source bindings, submission revisions/heads, provider checks/reviews, and resulting target observation. Readiness for PR publication never grants authority to mutate a protected target directly.

## Amendment by ADR-021

A protected-target movement that does **not** move a frozen exact PR submission head does not automatically erase the fact that the exact head is under review. Provider checks/reviews remain provider-governed until the provider reports that an update is required.

If `PR_UPDATE_REQUIRED` causes the submission head/revision to move, readiness/check/review evidence tied to the previous head becomes stale and must be regenerated or re-read.

## Amendment by ADR-027 and ADR-028

Readiness/evidence binds separately to:
- exact contribution-unit/convergence-unit internal OIDs;
- exact promotion-unit source bindings;
- exact current submission revision/head.

Authorized submission restacking creates a new submission revision and invalidates/re-reads head-bound evidence without rewriting the underlying convergence-unit OIDs.

## Amendment by ADR-029 and ADR-030

Exact-state binding also applies to **full managed-state verification evidence**, not only upward readiness/promotion evidence.

The invariant is state/evidence-oriented:

```text
exact resulting state has valid development-validation evidence
```

Existing evidence may be reused only when the exact result, verification-policy fingerprint, and relevant declared verification context are unchanged. State/policy/context changes make that evidence stale and require renewed external development validation.

Externally produced validation evidence for candidate `X` never authorizes a different candidate `X'`. Any candidate mutation performed during Development System validation is external authoring/validation work; the changed state must later re-enter the normal managed-work path with its own exact-bound evidence. `ruu` does not run the mutation/fixed-point loop.

Full-verification evidence remains distinct from ConvergenceUnit readiness evidence, promotion evidence, and provider review/check evidence. ADR-037 removes the former separate ContributionUnit integration-readiness evidence class: a valid managed checkpoint is integrated upward at the earliest mechanically safe opportunity.

## Amendment by ADR-032

PR review-request intent is also exact-head/revision-bound.

`REVIEW_NOT_REQUESTED` versus `REVIEW_REQUESTED` is publication/governance intent, not branch-level readiness. Transitioning to `REVIEW_REQUESTED` requires the configured PR-author/quality gate to hold for the exact current submission revision/head.

A material head revision invalidates any prior exact-head ship-ready/review-request assertion until rebound/revalidated.

## Terminology integration

ADR-025 replaced the earlier repository-local `feature` Git parent with **convergence unit**. ADR-034 replaced the earlier actor-oriented repository-context vocabulary with **contribution unit**. This ADR's operative wording now uses the current normative terminology.


## Amendment by ADR-037

ConvergenceUnit `READY_INTERNAL` evidence is bound not only to the exact ConvergenceUnit OID and required development-validation evidence, but also to the authoritative `SEALED` contribution-membership observation/binding and the terminal/resolution state of the bound ContributionUnits. Membership reopen/change or terminal-resolution change invalidates prior readiness even if the Git OID has not yet moved.

ADR-037 also removes the former separate ContributionUnit integration-readiness evidence class; eager upward integration revalidates exact checkpoint/topology/lifecycle/claim/conflict/verification preconditions instead.


## Amendment by ADR-057

Exact-state binding applies to externally produced `DevelopmentValidationEvidence`; `ruu` consumes/revalidates that evidence but no longer executes the development-verification process.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-069

Live ConvergenceUnit `READY_INTERNAL` evidence remains exact-tip-bound. However, once an exact state has been durably adopted into a PromotionGroup's **group-local resolution**, later unrelated reopen/movement of the live ConvergenceUnit does not stale that historical/current group binding. Only a current explicit same-group revision authority can replace it.

