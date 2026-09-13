---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Model PR review request as publication intent, not as a Ruu business-readiness state"
id: "ADR-032"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "6cca04eedb6ea46dcca628acf2d2afe5d2c3d28ed6bd21d03b27144fd45f4fa6"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-032: Model PR review request as publication intent, not as a Ruu business-readiness state

- **Status:** Accepted
- **Date:** 2026-09-04
- **Decision order:** 032

## Context

The internal model already represents WIP through contribution unit/convergence/promotion readiness. Making every PR pass through a mandatory `DRAFT` business state would duplicate that state and import provider UI terminology into the core domain.

At the same time, provider publication sometimes needs to occur before review is formally requested: to run provider-only CI, materialize a stack layer, or obtain code-level external feedback. A PR can also be internally ready/verified yet intentionally published without asking reviewers to act immediately.

When review is actually requested, the desired semantic assertion is strong: the author/system considers the exact candidate ship-ready in its current declared context, and review is an independent attempt to falsify that assertion rather than delegated implementation finishing.

## Decision

Represent PR publication/review intent with:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

This is a **publication/governance intent**, orthogonal to:

```text
VERIFIED / NOT_VERIFIED
READY / NOT_READY
PROMOTABLE / NOT_PROMOTABLE
OPEN / CLOSED
```

It is not a contribution unit or convergence-unit lifecycle state named `DRAFT`.

A GitHub adapter maps:

```text
REVIEW_NOT_REQUESTED
→ GitHub draft pull request

REVIEW_REQUESTED
→ GitHub ready-for-review pull request
```

Other providers map the same domain intent to their equivalent semantics/capabilities.

### Nominal path

The normal path is:

```text
internal Development System work + validation
→ managed Git progression
→ promotion candidate
→ explicit exact-revision PR-author/ship-ready intent/evidence
→ publish REVIEW_REQUESTED
```

There is no mandatory `draft → ready` lifecycle step.

### Exceptional `REVIEW_NOT_REQUESTED` publication

Policy may permit publication without review request for bounded reasons such as:

```text
provider/GitHub-specific verification needed before requesting review
explicit stack-layer exposure/materialization
code-level early external feedback
```

`REVIEW_NOT_REQUESTED` does not itself assert semantic incompleteness, nor does it imply readiness.

### Material invalidation after review request

If the exact proposal is materially changed such that the ship-ready assertion is no longer valid, the publication intent may return to `REVIEW_NOT_REQUESTED` while rework occurs. Exact head/revision evidence is rebound/revalidated before returning to `REVIEW_REQUESTED`.

### Review semantics

`REVIEW_REQUESTED` means the publishing principal/system asserts, according to the configured PR-author gate:

> **This exact proposal is considered ready to ship/integrate in its current declared context.**

ADR-057 places the semantic composition and execution of that ship-ready/agentic/human/specialist review process outside `ruu`. This ADR fixes only the exact-revision publication-intent boundary.

## Rationale

This keeps provider UI state out of the core convergence ontology while still exposing the operational capability needed to publish without formally soliciting review.

It also preserves the strong meaning of a real review request.

## Consequences

- Internal `NOT_READY` is not automatically a provider draft, and internal `READY` is not automatically review-requested.
- Provider-only checks may run on a `REVIEW_NOT_REQUESTED` submission when policy allows.
- Stack layers may be published without review request without weakening the quality semantics of layers that are actually review-requested.
- Exact current submission head/revision remains state-bound regardless of review-request intent.
- Provider checks/reviews are re-read after head revision as already required by ADR-010/ADR-021/ADR-028.
- The PR/provider state model must add review-request intent explicitly.

## Alternatives considered

- **Make `DRAFT` a core contribution unit/convergence state:** rejected because it duplicates existing WIP/readiness state and is provider terminology.
- **Always create a draft PR first:** rejected because the normal flow already has internal WIP representation and a strong ready submission boundary.
- **Allow REVIEW_REQUESTED on knowingly unfinished candidates:** rejected because it weakens review into an implementation-finishing mechanism.

## Related decisions

Amends ADR-010, ADR-021, ADR-026, ADR-027, and ADR-028.

## Amendment by ADR-055

The External Control Plane companion contract now explicitly consolidates ADR-032's pre-ADR-039 boundary. `REVIEW_REQUESTED` is exact-revision publication/governance intent and is not inferred from `READY_INTERNAL`, development-validation evidence, provider PR existence, or runtime/session completion. Any external/non-Git evidence required by the configured PR-author gate must be explicit and exact-revision-bound. ADR-057 moves the semantic ship-ready gate composition/execution outside `ruu`; only the deterministic fallback for exceptional `REVIEW_NOT_REQUESTED` eligibility (30.36) remains open.


## Amendment by ADR-057

The PR-author/ship-ready process is external Development System / repository-governance work. `ruu` consumes exact-revision-bound intent/evidence and provider state; it does not run the tests/reviews that justify the assertion.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment — ADR-062 / ADR-063 (2026-09-07)

The decision remains valid but is generalized from PR-specific vocabulary to **provider-submission review-request intent**. `REVIEW_REQUESTED` is provider-facing publication/governance intent, not internal readiness. `REVIEW_NOT_REQUESTED` early publication now requires explicit current authority/need; absent that and absent `REVIEW_REQUESTED`, no provider submission is created merely to manufacture a draft object. Semantic review findings remain external under ADR-063; nonblocking feedback is not automatically a core correction demand.

