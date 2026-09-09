# ADR-006: Use the internal hierarchy `target/base → convergence unit → contribution unit`

- **Status:** Accepted — terminology/current abstraction clarified by ADR-025 and ADR-034; bounded contribution-unit lifecycle clarified by ADR-035; eager integration/sealed readiness amended by ADR-037; amended by ADR-061
- **Date:** 2026-09-04
- **Decision order:** 006

## Context

Repository-local isolated contribution units are temporary/parallel sources of work. A longer-lived shared Git state is needed so several contribution units can converge before repository promotion.

## Decision

Use the internal hierarchy:

```text
target/base ref
  └── convergence-unit ref
        ├── contribution-unit A ref/worktree
        ├── contribution-unit B ref/worktree
        └── contribution-unit C ref/worktree
```

Rules:

- contribution-unit refs are provisioned from the convergence-unit ref;
- `target/base → convergence unit` is downward synchronization while the unit is mutable;
- `convergence unit → contribution unit` is downward synchronization;
- `contribution unit → convergence unit` is upward internal integration;
- promotion from convergence state to the configured target is a separate policy-controlled domain.

## Rationale

The convergence-unit layer provides a durable shared repository-local convergence point without forcing concurrently produced work to share a mutable checkout.

## Consequences

- Multiple contribution units may converge incrementally into one convergence unit.
- A contribution unit can be integrated without making the convergence unit semantically/promotion ready.
- Contribution-unit lifetime and convergence-unit lifetime are distinct.
- No product-feature meaning is inferred from the convergence-unit abstraction.

## Alternatives considered

- **`target/base → contribution unit` only:** rejected because it lacks a durable shared convergence root for unfinished parallel work.
- **Shared convergence-unit checkout for all producers:** rejected because it reintroduces edit-time collision.

## Amendment by ADR-061

The historical `target/base` label is split into two concepts. Internal downward synchronization uses the repository-local **ConvergenceBase**. Separately, each ConvergenceUnit is bound before first managed write to one immutable **PromotionTarget** `(target_repository_id, target_ref)`. Promotion is policy-controlled toward that already-bound target; policy does not choose the target.

