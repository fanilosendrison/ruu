# ADR-025: Replace the Git-level “feature” abstraction with a repository-local convergence unit

- **Status:** Accepted
- **Date:** 2026-09-04
- **Decision order:** 025

## Context

The existing specification used `feature` for the shared parent of contribution-unit refs. That name accidentally suggests a product feature, task, ticket, or other higher-level semantic unit.

`ruu` does not need to know whether the work is a complete product feature, one bug fix, one refactor slice, one migration step, or part of a larger objective. It only needs a repository-local Git aggregation root for contribution-unit contributions that can later participate in promotion.

The concrete Git branch name may still be task-specific and human/agent-friendly.

## Decision

Replace the normative Git-level concept `feature` with:

```text
CONVERGENCE_UNIT
```

Definition:

> A convergence unit is a repository-local Git convergence root that aggregates one or more contribution-unit contributions and can participate as an exact input to a promotion decision.

The internal hierarchy is:

```text
target/base ref
  └── convergence unit
        ├── contribution unit-A
        ├── contribution unit-B
        └── contribution unit-C
```

A convergence unit has a durable internal identity independent of its branch name:

```text
convergence_unit_id = stable orchestration identity
convergence_ref     = actual Git ref
display/branch name = descriptive label chosen/generated for the work
```

The branch name is never authoritative identity.

Higher-level systems may associate one or more convergence units with a product feature, task, issue, `/go` work package, Turnlock run, or other intent, but `ruu` does not interpret those semantics.

## Rationale

The shared parent branch is a Git convergence mechanism, not a product ontology.

Removing `feature` from the Git-level model:
- keeps `ruu` trunk-based and semantically small;
- avoids accidental “wait until the whole feature is done” behavior;
- lets higher-level systems choose whatever task/feature decomposition they need;
- preserves descriptive branch naming without coupling correctness to branch text.

## Consequences

- All normative `feature` terminology in the main specification becomes `convergence unit`.
- Contribution-unit refs are created from a convergence-unit ref.
- `contribution-unit→convergence-unit` remains the internal upward integration edge.
- Convergence-unit readiness means internal Git/promotion readiness for an exact state, not product-feature completion.
- A convergence unit may be tiny and short-lived.
- A product feature may correspond to zero, one, or many convergence units.
- Stable IDs, not branch names, are used for registry, claims, readiness, recovery, and promotion bindings.

## Alternatives considered

- **Keep `feature` and define it narrowly:** rejected because the word continues to imply product semantics.
- **Use `change`:** rejected as too generic and overloaded with diff/change-set meanings.
- **Use `promotion unit`:** rejected for this layer because promotion grouping is a separate concept.
- **Use branch name as identity:** rejected because branch names may be descriptive, renamed, or collide across repositories.

## Related decisions

Terminologically supersedes ADR-006 and ADR-015; amends ADR-008, ADR-010, ADR-019, ADR-022, and ADR-023.
