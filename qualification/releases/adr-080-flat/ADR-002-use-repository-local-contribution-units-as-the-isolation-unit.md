# ADR-002: Use repository-local contribution units as the isolation unit

- **Status:** Accepted — clarified by ADR-022, ADR-023, ADR-033, ADR-034, ADR-035, and ADR-038
- **Date:** 2026-09-04
- **Decision order:** 002

## Context

A Git worktree belongs to exactly one repository. The original model represented a global actor plus a repository-local context, but `ruu` ultimately needs only the repository-local isolation object.

## Decision

The isolation object is a stable opaque repository-local `contribution_unit_id`:

```text
1 contribution_unit_id
→ exactly 1 repository_id
→ exactly 1 convergence_unit_id membership for that identity
→ stable logical identity independent of editing-artifact presence
→ an isolated Git worktree/ref while externally provisioned for active editing
```

An editing worktree/ref topology must exist before a new managed filesystem write in that contribution unit, but its later absence does not erase the logical ContributionUnit or an already-created exact managed checkpoint.

A higher-level activity that spans three repositories uses three distinct contribution units. `ruu` does not require an actor identity linking them.

## Rationale

This is the smallest object that matches both physical Git isolation and the actual boundary consumed by `ruu`. Making repository locality intrinsic removes an unnecessary global identity layer.

## Consequences

- One repository may contain many concurrent contribution units.
- One contribution unit never spans repositories or changes its convergence-unit membership; a different convergence scope uses a new contribution unit.
- Under ADR-035/ADR-038 it is also a bounded contribution incarnation: once `CLOSED`, later work uses a new `contribution_unit_id`.
- Higher-level multi-repository work is represented by several repository-local contribution units.
- `contribution_unit_id` is independent of branch/ref existence or names, worktree existence or paths, sessions, models, processes, and invocation principals.
- `ruu` consumes already-provisioned contribution units; it does not retroactively isolate dirty shared edits.

## Alternatives considered

- **One worktree per session/agent:** rejected because session/agent identity is not the repository-local isolation boundary.
- **A global contribution-unit identity plus repository pair:** rejected by ADR-034 because no `ruu` invariant requires the global identity.
- **Create worktrees only during convergence:** rejected because isolation is needed before the first write.
