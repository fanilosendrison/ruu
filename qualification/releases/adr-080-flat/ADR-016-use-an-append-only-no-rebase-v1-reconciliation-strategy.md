# ADR-016: Use an append-only, no-rebase V1 reconciliation strategy

- **Status:** Accepted for internal refs — promotion portions superseded/amended by ADR-018, ADR-026, and ADR-028
- **Date:** 2026-09-04
- **Decision order:** 016

## Context

Merge and rebase can both reconcile Git histories, but rebase replaces commit identities. This system relies heavily on exact OIDs for concurrency, readiness, crash recovery, remote expectations, and auditability. Repository-local convergence-unit refs may also be parents of active contribution-unit refs.

## Decision

V1 never initiates rebase or another history rewrite on internal contribution-unit or convergence-unit refs.

Internal reconciliation policy:

```text
target/base → convergence unit
→ no-op if equal
→ fast-forward if convergence-unit tip is ancestor of target/base tip
→ otherwise merge target/base into convergence unit

convergence unit → contribution unit
→ no-op if equal
→ fast-forward if contribution-unit tip is ancestor of convergence-unit tip
→ otherwise merge convergence unit into contribution unit

contribution unit → convergence unit
→ fast-forward only
→ if not possible, synchronize contribution unit first and retry
```

Promotion is a separate concern:

```text
DIRECT
→ target may advance only to a descendant under the guarded direct-promotion protocol

PR
→ internal refs remain append-only
→ submission projection/rewrite follows explicit repository/provider policy
→ target is read-only to Ruu
```

Except guarded ref deletion during cleanup and explicitly policy-authorized submission-ref rewrites, every V1 mutation of a `CONTRIBUTION_UNIT_REF` or `CONVERGENCE_UNIT_REF` advances to a descendant of its previous tip.

Because V1 never rewrites internal history, normal internal publication never uses `--force` or `--force-with-lease`.

## Rationale

Stable commit identities substantially simplify concurrent expected-OID checks, readiness invalidation, remote state, observability, and crash recovery. The small cost is a potentially non-linear internal history with explicit merge commits where synchronization diverges.

## Consequences

- Existing internal commit OIDs are preserved.
- Downward synchronization may create merge commits.
- `contribution-unit → convergence-unit` has a deterministic fast-forward-only gate.
- Direct target promotion is descendant-only and separately governed.
- PR submission topology is owned by promotion/provider policy, not by internal reconciliation.
- A non-fast-forward push rejection on append-only internal refs means refresh/reconcile/revalidate, never overwrite.
- Legacy/external rebase state on internal refs is recovery-only.

## Alternatives considered

- **Rebase private contribution-unit refs:** rejected for V1 despite cleaner history because it expands OID invalidation/recovery state.
- **Rebase shared convergence-unit refs:** rejected because contribution units and evidence may depend on their OIDs.
- **Merge a contribution unit upward into its convergence unit when FF fails:** rejected; the contribution unit must first absorb the current convergence unit, then FF upward.
- **Mandate one final target merge topology here:** rejected; DIRECT and PR promotion are governed separately by ADR-018/026/028.

## Supersession / amendment note

The no-rebase/no-history-rewrite policy remains authoritative for contribution-unit/convergence-unit refs controlled by `ruu`, as do `target/base→convergence-unit`, `convergence-unit→contribution-unit`, and FF-only `contribution-unit→convergence-unit`.

The earlier design in which `ruu` itself performed a universal shared-branch-to-`main` `merge --no-ff` is superseded. Protected targets are read-only in PR mode; final PR topology is chosen by external governance. DIRECT mode uses the descendant-only guarded target-advance path.

## Amendment by ADR-028

The append-only/no-rebase rule is scoped to `CONTRIBUTION_UNIT_REF` and `CONVERGENCE_UNIT_REF`.

Submission refs may be explicitly classified rewriteable by repository policy/provider topology and may then be restacked/rebased under exact expected-old coordination. Target refs are never history-rewritten by `ruu`; direct target promotion is descendant-only.

## Terminology integration

ADR-025 replaced the earlier repository-local `feature` Git parent with **convergence unit**. ADR-034 replaced the earlier actor-oriented repository-context vocabulary with **contribution unit**. This ADR's operative wording now uses the current normative terminology; the decision history remains represented by the supersession notes above.
