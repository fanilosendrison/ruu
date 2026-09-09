# ADR-019: Keep `contribution-unit→convergence-unit` integration internal and PR-free

- **Status:** Accepted — terminology clarified by ADR-025/027/034/035, verification by ADR-029/030, eager integration by ADR-037
- **Date:** 2026-09-04
- **Decision order:** 019

## Context

Contribution-unit refs are technical isolation sources. They may contain frequent verified checkpoints and are not automatically the unit that should be externally reviewed/promoted.

## Decision

`contribution-unit→convergence-unit` remains an internal `ruu` transition and does not require a PR by default.

The upward edge is FF-only after exact synchronization/topology checks. ADR-037 removes a separate ContributionUnit integration-readiness gate: every valid authoritative managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit must be advanced toward its bound ConvergenceUnit at the earliest mechanically safe opportunity. The exact resulting convergence-unit state must have valid development-validation evidence; exact still-valid evidence for the authoritative ContributionUnit checkpoint OID/result may be reused when all evidence bindings remain valid.

External review/promotion is performed through explicit **promotion units**, which are distinct from contribution units and convergence units.

## Rationale

This keeps high-frequency technical isolation/convergence separate from human/provider governance and avoids multiplying PR objects merely because work was produced concurrently.

## Consequences

- Contribution-unit refs are not PR units by default.
- Many contribution units may feed one convergence unit.
- One or more convergence units may later be grouped into a promotion unit according to higher-level intent/repository policy.
- Internal ref append-only/no-rebase rules remain unchanged.

## Alternatives considered

- **PR for every contribution-unit integration:** rejected as operationally heavy and ontologically wrong.
- **Direct contribution-unit PRs to target:** rejected because they bypass the repository-local convergence layer and promotion-unit policy.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
