# ADR-014: Represent cross-repository promotion as non-atomic, recoverable partial progress

- **Status:** Accepted — amended by ADR-018, ADR-026, and ADR-027
- **Date:** 2026-09-04
- **Decision order:** 014

## Context

One logical feature may span several Git repositories, but Git provides no atomic transaction across repositories. Some repository-local promotions or pushes may succeed before another fails.

## Decision

Cross-repository promotion is an orchestrated state machine, not an atomic Git transaction:

```text
READY
→ PROMOTING
→ PARTIALLY_PROMOTED
→ PROMOTED
```

Before promotion begins, capture exact per-repo feature tips and block new contribution units for the logical feature. If only some repos advance, record that partial state and recover/roll forward from authoritative Git/remote facts.

## Rationale

Pretending multi-repo promotion is atomic would make already-performed irreversible Git updates disappear from the orchestration model.

## Consequences

- Partial success is explicit.
- Recovery can resume repo by repo.
- Roll-forward vs rollback policy remains an open decision, but silent partial state is forbidden.

## Alternatives considered

- **Pretend all-or-nothing:** rejected because Git cannot guarantee it.
- **Silently leave partial promotion:** rejected because future invocations would not know what already happened.

## Supersession / amendment note

ADR-018 changes each repository-local promotion from a direct main mutation into an externally governed PR. The non-atomic conclusion remains, but the concrete logical partial state is now normally `PARTIALLY_MERGED` across multiple repository-local PRs rather than `PARTIALLY_PROMOTED` local Git updates.

## Amendment by ADR-026 and ADR-027

Cross-repository logical work remains non-atomic, but each repository-local promotion track now follows that repository's own promotion policy.

A track may be `DIRECT` or `PR`; PR publication may be same-repository or cross-repository. Higher-level work spanning repositories can therefore reach explicit partial-promotion states without assuming “one PR per repo” universally.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Further clarification by ADR-025 and ADR-027

The old sentence requiring a global “logical feature” contribution unit freeze before multi-repository promotion is superseded.

Current semantics are:

```text
repo-local convergence units
→ exact promotion-unit source bindings
→ repo-local policy-driven promotion tracks
```

There is no `ruu`-level product-feature barrier spanning repositories. If a bound convergence unit is reopened/changed, that exact promotion binding becomes stale; higher-level orchestration decides broader cross-repository coordination.


## Amendment by ADR-047

A cross-repository PromotionGroup now resolves to one repository-local PromotionUnit per represented source repository. Aggregate `NONE_PROMOTED | PARTIALLY_PROMOTED | ALL_PROMOTED | UNKNOWN_INCONSISTENT` state therefore belongs to the higher-level PromotionGroup/logical ship, while each PromotionUnit follows its own repository-local lifecycle and EffectivePromotionPolicy. There is no cross-repository PromotionUnit pseudo-transaction.

## Amendment by ADR-054

Cross-repository `PARTIALLY_PROMOTED` is explicitly nonterminal for ConvergenceUnit semantic closure. A repository-local PromotionUnit may already be `PROMOTED` while its source ConvergenceUnit remains reactivable because another repository projection in the same PromotionGroup is still nonterminal. Only terminal settlement of every relevant group/promotion obligation, plus absence of current authoring/reconciliation demands, permits ConvergenceUnit `PROMOTED`; `RETIRED` is later and also requires recovery/resource sufficiency.

## Amendment by ADR-055

`PARTIALLY_PROMOTED` remains ordinary nonterminal aggregate progress, not automatic failure. ADR-055 defines durable exact-generation cross-repository settlement demands only when semantic disposition beyond ordinary remaining-provider progress is required. `ruu` never performs atomic rollback. Forward completion reaches `ALL_PROMOTED`; explicit External Control Plane compensation may reach terminal `COMPENSATED` only after required forward effects are observed/adopted. Partial promotion is never silently abandoned.
