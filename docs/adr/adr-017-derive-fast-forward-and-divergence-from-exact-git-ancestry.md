# ADR-017: Derive fast-forward/merge selection mechanically from exact Git ancestry

- **Status:** Accepted — scope clarified by ADR-018, ADR-025, ADR-026, and ADR-028
- **Date:** 2026-09-04
- **Decision order:** 017

## Context

The V1 policy initially used the phrase “fast-forward if the case is trivial”. That phrase has no precise operational meaning and could lead different agents/implementations to classify the same Git graph differently.

## Decision

Remove vague graph labels from the normative algorithm. For two tips `A` and `B`, derive the relation mechanically from Git:

```text
A == B
→ same tip / no-op

A is ancestor of B
→ A can fast-forward to B

B is ancestor of A
→ B can fast-forward to A

neither is ancestor of the other
→ diverged
```

Use authoritative Git ancestry, e.g. conceptually:

```bash
git merge-base --is-ancestor A B
```

`ruu` decides whether the transition is authorized; Git determines the graph relationship and whether a merge attempt conflicts.

## Rationale

An exact ancestor predicate is deterministic, mechanically checkable, and maps directly onto V1's no-op/fast-forward/merge state machine.

## Consequences

- The word “trivial” is removed from the specification.
- `PARENT_AHEAD`, `CHILD_AHEAD`, and `DIVERGED` have exact graph definitions.
- No orchestration metadata or heuristic decides whether fast-forward is possible.
- The whole-system state audit includes the ancestry classifier.

## Alternatives considered

- **Human/agent interpretation of “trivial”:** rejected as ambiguous.
- **Infer branch relation from orchestration metadata:** rejected because Git itself can answer the graph question authoritatively.

## Related decisions

Clarifies and makes executable the graph-selection rules adopted in ADR-016.

## Supersession / amendment note

Exact ancestry remains authoritative for internal Git-controlled reconciliation (`main→feature`, `feature↔contribution unit`). It is not a completion test for PR→main promotion, because a valid squash or rebase-style platform merge may produce a main history that does not contain the original feature tip.

## Amendment by ADR-025, ADR-026, and ADR-028

Exact ancestry remains authoritative for internal `target/base→convergence-unit` and `convergence-unit↔contribution unit` graph facts and for descendant-only direct target promotion.

Submission-projection rewrites/restacks are separate policy-authorized operations and are not classified as ordinary internal convergence.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.
