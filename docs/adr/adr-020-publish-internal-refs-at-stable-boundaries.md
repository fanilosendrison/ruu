---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Publish internal refs at stable boundaries when direct push is enabled"
id: "ADR-020"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "d9dd5d135e0e995dbf22fa459eb841a71183065ec7a5f1a05eb987c4d88c1d99"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-020: Publish internal refs at stable boundaries when direct push is enabled

- **Status:** Accepted — amended by ADR-021, ADR-026, ADR-027, ADR-028, ADR-029, and ADR-030
- **Date:** 2026-09-04
- **Decision order:** 020

## Context

The system needs a deterministic point at which locally created checkpoints/convergence results are published. Pushing after every tiny intermediate ref movement creates unnecessary network churn, while waiting until the very end weakens remote durability and cannot support PR creation against an exact feature head.

## Decision

When direct publication is enabled for internal refs:

```text
contribution unit checkpoint commit / contribution unit synchronization
→ validate stable contribution unit tip for that operation
→ ordinary push of contribution-unit ref

multiple feature advancements while one safe feature-ref operation/claim is active
→ coalesce locally
→ publish latest stable feature tip

feature PR create/update
→ requires remote feature tip == exact local feature tip

protected main
→ never pushed by Ruu
```

Publication uses ordinary expected-state/fast-forward semantics only. Push failure never rolls back valid local convergence; it creates explicit push-pending state that is recovered from actual remote facts.

## Rationale

This provides durable contribution unit checkpoints, avoids redundant feature pushes, and gives PR creation an exact published head while preserving the protected-main boundary.

## Consequences

- Remote contribution-unit refs may contain intermediate agent checkpoints without becoming PR units.
- Feature publication can be coalesced within a controlled local convergence sequence.
- PR submission is impossible until the exact feature tip is remotely visible.
- Push failures are orthogonal to local Git success and recoverable.
- `main` publication is exclusively the result of external governed PR merge.

## Alternatives considered

- **Push all refs only at end of the whole invocation:** rejected because PR exact-head publication and checkpoint durability can be delayed unnecessarily.
- **Push feature after every intermediate advancement:** rejected because coalescing preserves history while reducing redundant pushes.
- **Push main after local promotion:** rejected by ADR-018.

## Related decisions

Refines ADR-005 push race-safety and ADR-018 protected-main governance.

## Amendment by ADR-021

Once feature head `H` has been published and verified as the exact PR head, ordinary review freezes that head.

A later feature push changing the PR candidate is authorized only through an explicit lifecycle transition such as `PR_UPDATE_REQUIRED` or semantic reopen. During `MERGE_QUEUED_FROZEN(H)`, no feature-head publication is permitted.

## Amendment by ADR-026, ADR-027, and ADR-028

Publication now distinguishes ref classes:

```text
contribution unit/convergence-unit refs
→ internal stable-boundary publication, FF/expected-state only

submission refs
→ publication according to promotion policy;
  rewriteable only when explicitly authorized

target ref
→ direct publication only in DIRECT mode;
  read-only to Ruu in PR mode
```

Exact PR publication binds the current submission revision/head, which may differ from the convergence-unit ref.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-029 and ADR-030

A stable publication boundary now also requires that the exact locally produced state being published/adopted have valid development-validation evidence when that state was produced by a managed state-producing transition.

Publication itself is not a new development-validation execution boundary. If the exact state already has still-valid external evidence required by current policy, the push engine reuses that eligibility; `ruu` never reruns tests merely because a push occurs.

A newly produced merge/projection/restack state must obtain evidence before becoming authoritative/publishable.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
