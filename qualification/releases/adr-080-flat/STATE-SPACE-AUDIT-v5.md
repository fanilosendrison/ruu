# Ruu — State-Space Audit v5

- **Date:** 2026-09-05
- **Scope:** main requirements + ADR-001..ADR-035 after adopting bounded repository-local contribution units and externally authoritative terminal lifecycle
- **Executable audit:** `state-space-audit-v5.py`
- **Recorded output:** `state-space-audit-v5.txt`
- **Result:** **PASS**

## What changed since v4

ADR-035 changes both terminology and lifecycle semantics:

```text
work_context / work_context_id
→ contribution_unit / contribution_unit_id
```

The new object is a bounded repository-local stream of contribution to one current convergence scope. `CLOSED` and `ABANDONED` are terminal with respect to future contribution production; later work always uses a new contribution unit. Producer/runtime/turn state is explicitly orthogonal to contribution-unit lifecycle, and lifecycle declarations are externally authoritative.

This is not a text-only rename, so v4 cannot serve as proof of the current ontology.

## Exhaustive finite families

```text
contribution_unit_cardinality_identity: 512
actor_correlation_irrelevance: 120
contribution_unit_lifecycle: 144
contribution_unit_worktree_mutation_authority: 150
contribution_unit_commit_verification_crosscheck: 900
state_producing_transition_verification: 432
verification_evidence_reuse: 72
verification_fixed_point: 108
verification_capacity_scheduler: 180
review_request_intent: 108
review_revision_invalidation: 24
internal_integration_evidence: 240
```

**Changed/revalidated finite combinations: 2,990.**

## Lifecycle properties checked

The lifecycle family exhaustively crosses:

```text
lifecycle:
  OPEN | CLOSED | ABANDONED | REMOVED

producer/runtime state:
  RUNNING | WAITING_FOR_USER | TURN_FINISHED | INACTIVE

integration observation:
  NOT_INTEGRATED | INTEGRATED_EXACT | UNKNOWN

requested future contribution:
  NO_NEW_WORK | SAME_UNIT_NEW_CONTRIBUTION | NEW_UNIT_CONTRIBUTION
```

The audit establishes:

1. Runtime/turn state does not determine contribution-unit lifecycle.
2. `OPEN` may remain `OPEN` while waiting for the user or after a turn ends.
3. Current integration does not imply closure.
4. Same-identity future contribution is possible only while the contribution unit is `OPEN`.
5. `CLOSED`, `ABANDONED`, and `REMOVED` never authorize later contribution under the same `contribution_unit_id`.
6. Later work after terminal contribution lifecycle requires another contribution unit.

## Static architecture cross-check

The static pass checks:

- balanced Markdown code fences;
- contiguous ADR sequence 001..035;
- current main document contains the bounded contribution-unit definition and external lifecycle-authority contract;
- no current main-model `work_context_id`, `WORK_CONTEXT_REF`, writer identity, editing-context, or internal liveness/lease ontology remains;
- ADR-001..ADR-033 use current contribution-unit terminology;
- ADR-034 is explicitly retained as the historical removal of writer identity/intermediate naming decision and marked superseded in naming/lifecycle by ADR-035;
- ADR-035 contains the terminal lifecycle/no-reopen rule and runtime-independence rule;
- backlog no longer lists the contribution-unit close signal as an unresolved `ruu` semantic question;
- current ADRs do not authorize reopening a terminal contribution unit.

## Interpretation

This audit is exhaustive for the **finite factorized state families explicitly modeled here**. It does not claim exhaustive enumeration of an unbounded number of repositories, contribution units, convergence units, promotion units, Git DAGs, provider states, or external events.

Historical v2/v3/v4 reports remain useful as records of earlier ontologies but are not current proof artifacts.
