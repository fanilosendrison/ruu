---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require full verification before authoritative adoption of managed state-producing results"
id: "ADR-029"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "e2368cd504b59f935f54ff6c1faaa0e03b2987d056f942ce6c18c498a044aa43"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-029: Require full verification before authoritative adoption of managed state-producing results

- **Status:** Accepted historically — universal development-validation prerequisite superseded by ADR-060
- **Date:** 2026-09-04
- **Decision order:** 029

## Current normative reading after ADR-057

The original Decision/Rationale sections below record the historical safety reasoning that led to exact-state validation. **Where they describe tests, lint, build, secret scan, generators, validation workspaces, or a universal full-verification suite as executed by `ruu`, that execution ownership is superseded by ADR-057.**

The current normative rule is only:

```text
current policy requires development validation for exact candidate C
+ matching current DevelopmentValidationEvidence(C, gate_profile, context) exists
→ this development-validation prerequisite is satisfied

required evidence missing/stale/rejected/for another candidate
→ do not cross the affected Git boundary
→ emit/refresh exact DevelopmentValidationDemand when Ruu synthesized/holds C
```

The Development System decides and executes the semantic quality process. `ruu` performs only mechanical Git/convergence validation plus exact evidence binding.

## Context

The previous architecture made commit collection depend on contribution unit authority/liveness and made integration/promotion readiness exact-state-bound, but it did not require a full repository verification contract before every managed checkpoint or newly produced internal/submission candidate became authoritative.

The existing `git-commits-push` workflow already operationally runs the repository-declared test contract and secret scan before commit, often accepting multi-minute validation latency. The intended agentic model is stronger: contribution units may have mutable/WIP worktrees, but durable managed Git states inherited by other agents should be known-good under the repository's required verification policy.

This applies not only to dirty-contribution unit checkpoint commits. `ruu` can also produce new states through internal reconciliation, promotion projection, and submission revision/restack operations.

## Decision

Every exact state-producing result created under `ruu` authority MUST have valid **full-verification evidence** before that result becomes the authoritative state of the managed ref or promotion candidate that other transitions may consume.

The baseline repository **required commit-verification policy** contains these check classes:

```text
tests
lint
typecheck
build
secret scan
generated-artifact consistency
custom verification
```

A repository MAY declare a category explicitly not applicable when that category has no meaningful operation for that repository. Absence/unknown configuration is not silently treated as success when policy says the category applies.

General security analysis such as deep SAST, dependency vulnerability analysis, CodeQL-equivalent analysis, container/image scanning, or other provider-heavy security checks is **not** made a universal pre-commit requirement by this ADR. Repositories may add such checks through policy/custom verification; their general placement remains a separate design question.

Managed state-producing paths include at least:

```text
dirty contribution unit checkpoint

target/base → convergence-unit divergent reconciliation
(convergence-unit merge candidate)

convergence-unit → contribution unit divergent synchronization
(contribution unit merge candidate)

promotion projection/materialization that creates a new candidate state

submission revision/restack that creates a new candidate state

DIRECT promotion candidate before target advancement
```

A state-producing operation MUST materialize and verify its exact result before authoritative ref movement whenever `ruu` controls that movement. Implementations may use an isolated integration/materialization workspace, a no-commit merge state, an immutable temporary candidate, or another equivalent mechanism; the semantic requirement is that the authoritative ref is not advanced to an unverified newly produced result.

A pure state-preserving transition such as a fast-forward to an exact state that already has valid full-verification evidence does not, by itself, require redundant execution. Evidence validity/reuse is governed by ADR-030.

Provider-created final merge commits/results are not retroactively classified as locally created managed commits. PR/provider finalization remains governed by provider checks, merge-queue/final integration policy, and exact target observation.

## Rationale

The important invariant is not that a particular command named `git commit` always runs a particular script immediately beforehand. The invariant is:

> **An exact state that becomes an authoritative managed checkpoint or locally produced integration/promotion candidate must be fully verified.**

This keeps agents from inheriting knowingly unverified locally produced states while preserving a mutable WIP worktree during implementation.

## Consequences

- `commit != done`, `commit != ready`, and `commit != promotable` remain true.
- A checkpoint may be semantically incomplete while still fully verified.
- Internal merge commits/results are no longer exempt merely because they were produced by reconciliation rather than direct dirty-work collection.
- `contribution unit → convergence unit` fast-forward may reuse existing exact evidence when valid; a newly produced synchronization/reconciliation state needs evidence for the new result.
- Promotion/submission materialization must not publish a newly produced result before required verification succeeds.
- Existing contribution-unit-worktree ownership and isolated convergence workspaces are the natural critical sections/workspaces in which candidate verification occurs.
- Verification failure blocks only the affected state-producing path; unrelated fixed-point work continues.
- Push remains a publication mechanism; this ADR does not make every push an independent full-verification boundary.

## Alternatives considered

- **Full verification only before PR/merge:** rejected because agents would inherit unverified intermediate managed commits.
- **Full verification only for dirty-contribution unit commits:** rejected because internal merge/projection operations can create new unverified states too.
- **Only targeted/impacted tests before commit:** rejected as the baseline because the existing workflow already accepts full repository-declared verification and the desired invariant is stronger than impact-analysis confidence.
- **Make all security analysis universally pre-commit:** deferred/rejected as a universal rule because security checks have materially different cost/environment/provider characteristics; secret scanning is the certain baseline requirement.

## Related decisions

Amends ADR-003, ADR-007, ADR-009, ADR-010, ADR-012, ADR-020, ADR-026, ADR-027, and ADR-028.


## Amendment by ADR-057 — development verification execution is external

ADR-057 retains this ADR's safety objective but changes the execution boundary. `ruu` no longer defines or runs a universal repository `tests/lint/typecheck/build/secret-scan/...` suite. Those checks and their composition belong to the External Control Plane / Development System.

For `ruu`, the retained invariant is:

```text
if current policy requires development validation for an exact candidate
→ authoritative adoption/publication requires current DevelopmentValidationEvidence bound to that exact candidate/profile/context
```

A dirty ContributionUnit may arrive with such evidence after the Development System has completed its own authoring/validation loop. A new exact state synthesized by `ruu` (for example a divergent merge, promotion materialization, or restack result) is held as an immutable validation subject and causes an exact external `DevelopmentValidationDemand` when no valid evidence exists. `ruu` does not run tests to satisfy that demand.

The baseline check-class list in the original Decision section is therefore historical Development System policy guidance, not a current `ruu`-owned universal execution contract.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-065 — provider-created final result adoption

Provider-created final results remain outside local state-production semantics, but terminal promotion adoption now has an exact proof contract. If candidate ancestry survives, fresh target Git ancestry proves realization. If provider rewriting removes candidate ancestry, the provider must bind exact submitted candidate `C` to exact final result `R`, and `ruu` independently proves `R` is in authoritative target history. Provider `MERGED` alone is insufficient; no generic semantic diff-equivalence validation is added.
