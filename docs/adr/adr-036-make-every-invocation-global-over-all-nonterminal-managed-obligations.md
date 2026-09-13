---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make every invocation global over all nonterminal managed obligations"
id: "ADR-036"
status: "accepted"
date: "2026-09-05"
decision_body_sha256: "682a370ed3524500bfacfbaf454c97af05191352a5bd64711d1fc857fd3d2654"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-036: Make every invocation global over all nonterminal managed obligations

- **Status:** Accepted — reconciliation-obligation coverage clarified by ADR-040; trigger/coalescing semantics amended by ADR-041
- **Date:** 2026-09-05
- **Decision order:** 036

## Context

`ruu` exists to exploit explicit invocations from many concurrent sessions as opportunities to keep all managed Git state as advanced as currently possible.

The previous architecture already required a global fixed-point pass and localized waiting, but ADR-022 still allowed `ACTIVE_CONVERGENCE_SET` to act as the repository-scope source for an invocation. That makes an acceleration structure too authoritative: a stale/incorrect activity classification could cause old or externally-waiting work to be omitted even though a managed responsibility still exists.

The intended semantics are stronger:

```text
caller/repository/task/contribution unit/convergence unit/promotion unit/age
≠ invocation processing scope
```

A PR waiting on review, a check waiting on provider completion, a merge-queue entry, a cross-repository partial promotion, a merged PR awaiting final target-result proof, an old unresolved ContributionUnit, or a recovery/cleanup obligation must remain visible until terminally resolved.

## Decision

Every explicit `ruu` invocation operates over the complete known set of **nonterminal managed obligations** in shared coordination state.

The authoritative obligation universe includes every lifecycle layer owned or observed by `ruu`, including at least:

```text
ContributionUnit checkpoint / verification / commit responsibility
ContributionUnit ↔ ConvergenceUnit synchronization/integration responsibility
ConvergenceUnit reconciliation/readiness responsibility
PromotionUnit responsibility
internal/submission publication responsibility
PR / review / check / provider responsibility
merge-queue / update / restack responsibility
final target-integration observation/proof responsibility
Git recovery / claim / cleanup responsibility
```

For each invocation:

```text
enumerate/reconstruct every known nonterminal managed obligation
→ refresh the authoritative Git/remote/provider/policy facts required by each obligation
→ identify every currently safe + authorized + claimable + fully-preconditioned transition
→ execute non-conflicting progress
→ refresh affected and newly-unlocked obligations
→ repeat
→ stop only at the current global fixed point
```

A waiting or blocked obligation may be a stop state for the **current freshly observed invocation state**, but it is not forgotten or lifecycle-terminal. It remains in the managed-obligation universe and is re-evaluated on every later explicit invocation.

Examples:

```text
WAITING_FOR_REVIEW
WAITING_FOR_CHECKS
MERGE_QUEUED
provider UPDATE_REQUIRED wait
final integration observation pending
external development-validation wait
```

all remain nonterminal managed obligations.

`ACTIVE_CONVERGENCE_SET` may remain as a derived/reconstructible acceleration index of repositories containing recorded nonterminal obligations. It is not a source of truth for processing scope:

```text
managed nonterminal obligations
→ authoritative

ACTIVE_CONVERGENCE_SET
→ optional derived index/cache
```

If the activity index is missing, stale, corrupt, or contradicts authoritative obligation records, it must be reconstructed. Omission from the index never authorizes omission of an authoritative nonterminal obligation.

Repositories with **zero** recorded nonterminal managed obligations do not need deep refresh on every invocation. This is compatible with exhaustive convergence because there is no managed responsibility to advance there.

No whole-disk Git scan is introduced. The universe remains the managed coordination domain, not every `.git` directory on the host.

## Rationale

The caller merely creates an opportunity to converge. It should not determine which work benefits from that opportunity.

This makes concurrent sessions useful as distributed triggers for continuously reducing outstanding Git/convergence debt. Old work cannot be forgotten because of age, caller locality, CWD, repository locality, or a stale activity optimization.

Keeping the authoritative unit as a managed obligation also avoids expensive deep scans of repositories that have genuinely reached terminal quiescence.

## Consequences

- Every executed global sweep that services outstanding convergence demand re-evaluates all known nonterminal managed obligations at every lifecycle layer.
- A waiting PR/check/review/merge-queue/provider state remains nonterminal and is refreshed on each later executed global sweep servicing convergence demand.
- Final provider/target integration observation/proof remains in scope until terminally resolved.
- A blocked object never becomes a global mutex.
- Trigger reason never narrows processing.
- Repository age never narrows processing.
- `ACTIVE_CONVERGENCE_SET` is reconstructible optimization state only.
- A known repository with no nonterminal managed obligations may remain quiescent without deep scanning.
- Creation/admission of new managed work must create/update authoritative obligation records; `ruu` does not discover unmanaged hidden filesystem work by scanning the machine.

## Alternatives considered

- **Use `ACTIVE_CONVERGENCE_SET` as authoritative invocation scope:** rejected because stale optimization metadata could omit valid managed work.
- **Process only caller/current-repository state:** rejected because it defeats global opportunistic convergence.
- **Process only ContributionUnits:** rejected because provider/review/check/merge/final-proof obligations also need repeated progression.
- **Deep-scan every known repository every invocation:** rejected because authoritative managed obligations already identify where responsibility exists.
- **Background polling:** rejected; `ruu` remains explicitly invoked. External waits are refreshed when an invocation occurs.

## Related decisions

Supersedes the scope-authority portion of ADR-022 and amends ADR-004, ADR-007, ADR-013, ADR-021, and ADR-031. It preserves ADR-022's managed repository catalog and no-whole-disk-scan boundary.


## Amendment by ADR-040

`RECONCILIATION_REQUIRED` is a nonterminal managed obligation. It remains globally visible and is re-evaluated on every later invocation until current authoritative state demonstrates that the blocked obligation is resolved/superseded. Waiting for external authoring localizes the stop to the affected resources and never narrows the global sweep.


## Amendment by ADR-041

The global-scope decision is retained but the unit of scheduling changes. Explicit invocations are coalescible convergence-demand signals, not FIFO executions. Every **executed sweep** that services outstanding demand still evaluates the complete known nonterminal managed-obligation universe and reaches the current global fixed point. If newer demand arrived during the sweep, the same current executor performs another global sweep; otherwise it may release ownership and exit.

## Amendment by ADR-055

`CrossRepositorySettlementDemand` is a nonterminal managed obligation and remains globally visible until terminally settled/superseded. A later invocation from an unrelated session may discover/refresh it without assigning that session the semantic settlement work. The External Control Plane contract now states this trigger/scope boundary explicitly.


## Amendment by ADR-057

The global obligation universe includes exact `DevelopmentValidationDemand` dependencies and their current evidence state, not internal test jobs or verification-capacity queues.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
