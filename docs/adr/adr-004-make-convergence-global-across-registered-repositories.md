---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make convergence scope independent of CWD and support multi-repository work"
id: "ADR-004"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "f06a2f046a5b66c41968b7cc1c5a6705f65d469aa254aaa1236c560c3c958fa5"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-004: Make convergence scope independent of CWD and support multi-repository work

- **Status:** Accepted — clarified by ADR-022, ADR-023, and ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- **Date:** 2026-09-04
- **Decision order:** 004

## Context

Higher-level work may involve several repositories, and `ruu` may be invoked from a session whose current directory is unrelated to other eligible managed state.

## Decision

The caller's CWD does not define `ruu` scope.

The tool operates over every known nonterminal managed obligation from shared coordination state, across contribution units, convergence units, promotion units, publication/provider workflows, final integration proof, verification, recovery, and cleanup. One invocation may progress multiple repositories.

Every Git commit/ref mutation remains repository-local.

Higher-level work spanning several repositories is represented by distinct `contribution_unit_id` values in those repositories; `ruu` does not require a global actor identity linking them.

## Rationale

CWD is an execution convenience, not orchestration truth. Restricting convergence to CWD would strand eligible state and make correctness depend on where a caller happened to invoke the command.

## Consequences

- One invocation may commit/converge/promote several repositories.
- Cross-repository logical work remains a set of independent repository-local Git operations.
- Git provides no native atomic transaction across repositories.

## Alternatives considered

- **Only process the current repository:** rejected because it cannot progress managed work elsewhere.
- **Recursively discover Git repositories from disk:** rejected because scope must come from managed coordination state, not filesystem scanning.

## Amendment by ADR-036

Global operation is defined over all known nonterminal managed obligations, not a caller/repository/task-specific scope. Repository age, caller identity, CWD, ContributionUnit, ConvergenceUnit, PromotionUnit, and invocation reason never narrow the fixed-point universe. `ACTIVE_CONVERGENCE_SET` is only a derived acceleration index.
