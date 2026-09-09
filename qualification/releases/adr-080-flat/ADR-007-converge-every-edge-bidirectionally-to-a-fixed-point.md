# ADR-007: Check both directions of every hierarchy edge on every invocation and converge to a fixed point

- **Status:** Accepted — amended by ADR-021, ADR-025, ADR-029, ADR-030, ADR-033, ADR-036, and ADR-057
- **Date:** 2026-09-04
- **Decision order:** 007

## Context

Integrating one contribution unit can make another contribution unit stale. Promoting another feature can advance `main` and make active features stale. A single static reconciliation scan can therefore create new convergence obligations that it never notices.

## Decision

Every `ruu` invocation checks every currently relevant graph edge represented by known nonterminal managed obligations:

```text
target/base → convergence unit      synchronization
convergence unit → promotion flow   promotion check

convergence unit → contribution unit     synchronization
contribution unit → convergence unit     integration check
```

After any successful mutation, authoritative Git state is refreshed and the graph is re-evaluated. The invocation continues until no additional operation is simultaneously safe and currently authorized.

`nothing to commit` is never equivalent to `nothing to converge`.

## Rationale

This minimizes accumulated divergence and makes `ruu` actually converge the current graph rather than merely process one snapshot of it.

## Consequences

- `target/base → convergence unit` is reconsidered while the convergence unit is mutable.
- `convergence unit → contribution unit` is reconsidered whenever the convergence unit advances.
- Safe operations unlocked by previous operations in the same invocation are performed.
- Blocked/protected/not-ready states count as temporarily unavailable, preventing infinite spin.

## Alternatives considered

- **One reconciliation pass per invocation:** rejected because earlier mutations can invalidate later observations.
- **Reconcile only after creating a new commit:** rejected because already-committed refs may have become convergable.

## Supersession / amendment note

References to the upward main/feature responsibility now mean evaluation/progress of the PR-governed promotion workflow, not a direct `feature→main` Git mutation. The fixed-point requirement remains unchanged.

## Amendment by ADR-021

The fixed-point rule remains global, but `main→feature` is only actionable when the feature lifecycle grants mutation authority.

`REVIEWING_FROZEN(H)` and `MERGE_QUEUED_FROZEN(H)` are localized external-wait states. Main advancement is observed but does not itself authorize feature mutation. Unrelated currently-authorized convergence must continue.

Provider `UPDATE_REQUIRED` explicitly transitions the feature to `PR_UPDATE_REQUIRED`, reauthorizing the narrow base-update workflow.

## Amendment by ADR-022

Superseded by ADR-036: the global fixed point is evaluated over all known nonterminal managed obligations. `ACTIVE_CONVERGENCE_SET` is only a derived/reconstructible acceleration index. A repository with zero nonterminal obligations may remain quiescent; any PR/provider/review/check/merge/final-proof obligation remains globally visible and is refreshed on every later invocation.

## Amendment by ADR-023

The global fixed point is evaluated only after an explicit `ruu` invocation over already-managed contexts from shared coordination state. Contribution-unit provisioning is outside this fixed-point operation.

## Amendment by ADR-024/ADR-033

Contribution-unit-facing edges are actionable only when the external mutation-access contract makes the exact context `TRANSFERABLE_TO_RUU` (or `TRANSFERABLE_GENERAL`) and the current authoritative executor/operation acquires the exclusive worktree claim. Invocation-principal identity by itself does not make the edge actionable.

## Amendment by ADR-026, ADR-027, and ADR-028

The fixed-point engine is now promotion-policy aware.

For every repository referenced by nonterminal managed obligations it revalidates the required policy/facts, advances internal `target/base→convergence-unit↔contribution unit` state, then advances declared promotion/provider obligations according to DIRECT/PR, INDEPENDENT/STACKED, SAME/CROSS_REPOSITORY rules and provider capabilities.

A waiting or blocked promotion unit remains a localized current-pass stop state; it stays nonterminal for later invocations and unrelated actionable work continues.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-029 and ADR-030

ADR-029/030 added a safety requirement that newly produced exact states cannot become authoritative merely because Git can construct them. **That safety requirement remains normative, but ADR-057 supersedes the historical internal verification-execution/fixed-point interpretation.**

Current reading: a graph edge that synthesizes a new exact internal/promotion/submission candidate may require exact external `DevelopmentValidationEvidence` before adoption. When that evidence is absent, `ruu` records/refreshes a localized `DevelopmentValidationDemand` and continues unrelated Git/convergence work. Any formatter/generator/test mutation loop needed to obtain the evidence belongs to the Development System, not to this fixed-point engine.

## Amendment by ADR-033

Contribution unit-facing edges are actionable only when the External Control Plane has made the exact contribution unit `TRANSFERABLE_TO_RUU` (or `TRANSFERABLE_GENERAL`) and the current authoritative executor/operation can acquire the exclusive worktree claim. `ruu` does not classify external producer/runtime liveness.

## Amendment by ADR-036

The fixed-point universe is the complete known set of nonterminal managed obligations across every lifecycle layer, including external/provider waits and final target-integration proof. Waiting is terminal only for the current freshly observed pass; it is not lifecycle terminal and must be re-evaluated on every later explicit invocation.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](EXTERNAL-CONTROL-PLANE-CONTRACT.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-041

Concurrent explicit invocations are coalescible demand signals. The fixed-point semantics in this ADR are executed by the one current fenced top-level executor; invocation identity is not a mutation-authority dimension.


## Amendment by ADR-057

ADR-057 narrows the fixed-point semantics to **Git/convergence progression**, not Development System verification execution. The historical ADR-029/030 amendment above must no longer be read as an internal formatter/generator/test fixed-point loop.

Current normative reading:

```text
exact Git/convergence transition can synthesize candidate C
        ↓
if current policy requires development validation for C
        ↓
record/refresh exact DevelopmentValidationDemand(C)
        ↓
that edge is locally waiting
        ↓
Development System validates/authors externally
        ↓
later invocation consumes exact DevelopmentValidationEvidence(C)
        ↓
Git/convergence fixed-point progression resumes
```

`ruu` does not run or iterate tests, formatters, generators, flaky retries, or other development-validation work. A validation demand/evidence change can make a Git edge newly progressable, so such waits remain part of the **global managed-obligation recheck universe**, but the validation computation itself is not part of the `ruu` fixed-point algorithm.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
