# ADR-021: Freeze the exact PR head during external governance and localize PR waits

- **Status:** Accepted — amended by ADR-026, ADR-028, and ADR-032
- **Date:** 2026-09-04
- **Decision order:** 021

## Context

Once a feature has converged internally and is submitted as a PR, the exact feature head is the candidate currently being reviewed, tested, approved, or queued by the repository governance system.

Protected `main` may continue to advance because unrelated PRs are merged. Automatically reconciling every new `main` into a feature already under review would change the PR head, invalidate or restart governance evidence, and may eject the PR from a merge queue.

A feature may also wait on CI/review/provider state for a long time. That wait must not stop safe convergence in unrelated features, contribution units, or repositories.

## Decision

After a PR create/update verifies exact head OID `H`, the feature enters:

```text
REVIEWING_FROZEN(H)
```

While frozen:

```text
main advances
→ observe new main
→ do NOT automatically mutate feature
→ retain H as the exact candidate under governance

checks/review pending or approved
→ wait/observe locally
→ unrelated convergence continues

provider UPDATE_REQUIRED
→ PR_UPDATE_REQUIRED
→ authorize controlled main→feature synchronization
→ invalidate stale state-bound readiness/check/review assumptions
→ revalidate
→ publish new exact feature head H2
→ update the SAME PR
→ verify provider head == H2
→ REVIEWING_FROZEN(H2)

CHANGES_REQUESTED
→ ADR-053 exact ReviewCorrectionDemand
→ External Control Plane restores/starts correction continuation
→ explicit semantic reopen of affected existing convergence scope(s)
→ ACTIVE with contribution membership OPEN
→ old readiness/review assumptions become stale
→ newly provisioned ContributionUnit creation/convergence may resume

provider MERGE_QUEUED
→ MERGE_QUEUED_FROZEN(H)
→ no feature-head mutation until merge or provider release/ejection
```

`UPDATE_REQUIRED` is not a normal feature reopen. It grants only the narrow authority required to update the PR candidate against current protected `main`; it does not implicitly permit new contribution units.

Unexpected movement of the remote feature ref or provider PR head away from bound `H` enters explicit drift/unknown recovery and fails closed.

A PR waiting on an external condition is a localized current-pass stop state for that convergence unit, not a global lock. It remains a nonterminal managed obligation for later invocations.

## Rationale

The exact submitted commit is the object currently under governance. Preserving it avoids unnecessary PR-head churn and avoids invalidating external review/CI due solely to unrelated `main` advancement.

Provider-driven update authority also supports strict repositories where a PR is allowed to remain behind `main` until the platform explicitly requires an update.

Localized waiting preserves the concurrency goal of `ruu`: one feature's governance wait must not serialize unrelated work.

## Consequences

- `main→feature` is lifecycle-authorized rather than unconditional.
- `REVIEWING_FROZEN(H)` and `MERGE_QUEUED_FROZEN(H)` deny automatic feature-head mutation.
- Main movement alone does not replace the submitted candidate.
- `UPDATE_REQUIRED` creates an explicit `PR_UPDATE_REQUIRED` state.
- `PR_UPDATE_REQUIRED` remains contribution unit-frozen by default.
- Authorized PR-head movement invalidates exact state-bound readiness/check/review evidence.
- Unexpected PR-head drift fails closed.
- External waits are current-pass stop states local to the affected convergence unit and remain nonterminal managed obligations for later invocations.
- The same PR identity is preserved across authorized base-update cycles.

## Alternatives considered

- **Always merge latest `main` into every open PR feature:** rejected because it churns the reviewed head unnecessarily.
- **Freeze all of `ruu` while any PR is pending:** rejected because unrelated resources can continue safely.
- **Treat `UPDATE_REQUIRED` as an ordinary semantic reopen:** rejected because base synchronization does not authorize new feature work.
- **Silently accept an externally moved PR head:** rejected because ownership and the exact reviewed candidate become ambiguous.

## Related decisions

Amends ADR-007, ADR-010, ADR-011, ADR-018, and ADR-020.

## Amendment by ADR-026 and ADR-028

Exact-head freeze applies to the **current submission revision**, not universally to the internal convergence-unit ref.

For immutable independent submissions:

```text
REVIEWING_FROZEN(H)
```

remains exact.

For a policy-authorized rewriteable/stacked submission, provider-required restack/rebase enters an explicit submission-revision transition, rebinds the same logical promotion/submission identity to a new exact head, and invalidates/re-reads head-bound evidence. Unexpected movement outside that transition still fails closed.

In `DIRECT` promotion mode there is no PR freeze state.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-032

Provider publication now distinguishes review-request intent:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

An exact submission head may exist at the provider while review is not requested. The ordinary exact reviewed-head freeze semantics apply once `REVIEW_REQUESTED` is asserted for that exact revision/head.

A materially invalidated review-requested proposal may return to `REVIEW_NOT_REQUESTED` during rework without implying an internal contribution unit/convergence-unit `DRAFT` lifecycle state.

## Amendment by ADR-036

A PR/review/check/merge-queue/provider wait is a localized **current-pass stop state**, not a terminal managed lifecycle state. It remains a nonterminal managed obligation and must be refreshed on every later explicit `ruu` invocation. The wait still never blocks unrelated obligations.


## ADR-053 amendment — review correction need not reuse the originating session

`CHANGES_REQUESTED` is now mediated by one durable exact-generation-bound ReviewCorrectionDemand. The External Control Plane may restore the prior coding session or start a new continuation session; authoring always uses newly provisioned ContributionUnits. Ordinary correction of existing PromotionGroup members preserves ADR-049 logical submission identity; it revises the same provider PR only while its PublicationEpisode is nonterminal, with ADR-055 creating a new episode after a terminal PR when the same ship still requires publication.

## ADR-054 amendment — provider-local completion does not prematurely close correction lineage

A locally merged/promoted exact submission snapshot does not by itself retire its source ConvergenceUnit when the same logical PromotionGroup remains nonterminal elsewhere. ADR-053 correction work may still reactivate existing group-member ConvergenceUnits until ADR-054 terminal settlement closes the lineage. Once the ConvergenceUnit itself reaches `PROMOTED`, later semantic work requires a new ConvergenceUnit rather than another reopen.

## Amendment by ADR-055

Provider PR identity is now stable within one PublicationEpisode rather than necessarily for the entire logical submission lifetime. A merged/terminal PR remains immutable; a later exact publication for the same nonterminal logical submission uses a distinct new episode/ref/PR while preserving `submission_id`.

## Amendment — ADR-062 (2026-09-07)

Current reading generalizes “PR head” to the exact **provider submission head** for the current PublicationEpisode. GitHub PR is an adapter realization. Head freezing/exact binding and localized provider waits remain normative. Provider finalization is not inherently a passive human wait: when the exact integration operation is required, supported, authorized, and fully preconditioned, `ruu` may progress it automatically.

