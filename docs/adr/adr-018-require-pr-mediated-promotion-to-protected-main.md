---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require PR-mediated promotion to protected main"
id: "ADR-018"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "e611bdf18d2c769fbaceaa60ea1efb7cb5b84a56ccd53cffe1c257841d363dc3"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-018: Require PR-mediated promotion to protected main

- **Status:** Accepted as strict PR-policy case — universal PR requirement superseded by ADR-026; publication intent amended by ADR-032
- **Date:** 2026-09-04
- **Decision order:** 018

## Context

The system must work unchanged inside a strict team where `main` is protected and contributors are expected to go through pull requests, CI, review, branch protection, and possibly a merge queue. A design in which `ruu` locally merges into or directly pushes `main` would conflict with that governance model.

The platform may also use merge commit, squash, rebase-style merge, or merge queue semantics, so the final `main` topology cannot be assumed by the internal orchestrator.

## Decision

Protected `main` is read-only to `ruu`.

`ruu` may:

```text
fetch/read/compare protected main
use it as source for main → feature synchronization
publish an exact feature ref
create/update a PR targeting protected main
observe checks/reviews/merge queue
observe the resulting protected main after provider merge
```

It may not:

```text
commit on main
locally merge feature into main
directly update main
push main
force-push main
```

Feature promotion is therefore:

```text
READY_FOR_PR
→ publish exact feature head
→ create/update PR
→ CI/review/branch protection/merge queue
→ provider/team policy merges
→ observe resulting protected main
```

A PR is considered merged from authoritative provider state plus observation of the resulting protected-main ref. Original feature-tip ancestry is not required.

## Rationale

This makes the default architecture compatible with strict branch protection from day one and prevents a future migration from “solo direct-main” semantics to “team PR” semantics.

## Consequences

- The old `feature→main = merge --no-ff by Ruu` decision is superseded.
- `main→feature` remains internal synchronization from a freshly fetched protected-main tip.
- Feature readiness becomes readiness for PR submission/update, not authority to mutate main.
- PR/provider state becomes first-class persistent/recovery state.
- Squash/rebase-style external merges are valid even when original feature OIDs are absent from main.
- Multi-repo logical promotion means several independent repository-local PRs and may be partially merged.

## Alternatives considered

- **Direct push/merge to main in solo mode, PR mode later:** rejected because it creates two different architectures and a migration path.
- **Force one final merge topology such as `--no-ff`:** rejected because strict team/repository policy owns the final merge method.
- **Treat PR as optional decoration after local main merge:** rejected because it bypasses the governance boundary.

## Related decisions

Supersedes the `feature→main` portion of ADR-016 and amends the barrier semantics of ADR-011 and cross-repo semantics of ADR-014.

## Amendment by ADR-021

An open PR does not imply continuous automatic `main→feature` synchronization.

After exact head `H` is bound to the PR, the feature is `REVIEWING_FROZEN(H)`. Main movement is observed but the feature remains unchanged unless the provider explicitly reports `UPDATE_REQUIRED`, the feature is semantically reopened, or external finalization ownership is released as applicable.

## Amendment by ADR-026

ADR-018 is no longer universal.

Its protected-target behavior remains normative when repository policy resolves to:

```text
promotion_mode = PR
```

When policy resolves to `DIRECT`, `ruu` may advance/push the configured target ref through the guarded descendant-only direct-promotion path. A protected target or PR-required policy can never be bypassed by selecting `DIRECT`.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-032

PR-mode publication no longer assumes that every created PR immediately requests review.

The provider-facing submission may be published as:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

`REVIEW_REQUESTED` is the normal governed-promotion path and carries the configured ship-ready/PR-author assertion for the exact submission revision. `REVIEW_NOT_REQUESTED` is an explicit exceptional publication mode, not an internal `DRAFT` state.

## Amendment — ADR-062 (2026-09-07)

The safety intent remains: a protected target that requires provider-mediated governance MUST NOT be directly advanced by `ruu`. The current core terminology is no longer a semantic `PR` promotion mode. Historical `PR` here maps to `target_realization_route = PROVIDER_SUBMISSION`; GitHub Pull Request is one provider adapter projection. Once all actual provider/governance prerequisites are current and machine-authorized, provider finalization may be progressed automatically rather than waiting for a ceremonial manual Merge click.

