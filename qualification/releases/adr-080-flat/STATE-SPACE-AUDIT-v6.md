# Ruu — State-Space Audit v6

- **Date:** 2026-09-05
- **Scope:** main requirements + ADR-001..ADR-036 after making every invocation global over all known nonterminal managed obligations
- **Executable audit:** `state-space-audit-v6.py`
- **Recorded output:** `state-space-audit-v6.txt`
- **Result:** **PASS**

## What changed since v5

ADR-036 strengthens global convergence semantics.

The authoritative invocation universe is no longer a repository activity set. It is the complete known set of **nonterminal managed obligations** across every lifecycle layer:

```text
ContributionUnit
→ ConvergenceUnit
→ PromotionUnit
→ publication/submission
→ PR/review/check/provider
→ merge queue/update/restack
→ final target-integration observation/proof
→ recovery/cleanup
```

`ACTIVE_CONVERGENCE_SET` may remain as a derived/reconstructible acceleration index, but index membership, caller relation, repository age, invocation reason, or local workflow identity cannot suppress an authoritative obligation.

External waits are current-pass stop states only. They remain nonterminal and are refreshed again on every later explicit invocation.

## Exhaustive finite families

```text
contribution_unit_cardinality_identity:             512
actor_correlation_irrelevance:                       120
contribution_unit_lifecycle:                         144
global_managed_obligation_coverage:                  432
external_wait_recheck:                                80
contribution_unit_worktree_mutation_authority:       150
contribution_unit_commit_verification_crosscheck:    900
state_producing_transition_verification:             432
verification_evidence_reuse:                          72
verification_fixed_point:                            108
verification_capacity_scheduler:                     180
review_request_intent:                               108
review_revision_invalidation:                         24
internal_integration_evidence:                       240
```

**Changed/revalidated finite combinations: 3,502.**

## Global managed-obligation coverage family

The audit crosses:

```text
layer:
  CONTRIBUTION_UNIT
  CONVERGENCE_UNIT
  PROMOTION_UNIT
  SUBMISSION_PR_REVIEW_CHECK
  MERGE_QUEUE_UPDATE_RESTACK
  FINAL_INTEGRATION_PROOF
  VERIFICATION
  RECOVERY_CLEANUP

lifecycle:
  NONTERMINAL_ACTIONABLE
  NONTERMINAL_WAITING
  TERMINAL

activity index:
  ACTIVE_INDEXED
  NOT_INDEXED
  STALE_UNKNOWN

age:
  RECENT
  OLD

caller relation:
  RELATED
  UNRELATED
  NONE
```

For every nonterminal obligation, re-evaluation is mandatory regardless of activity-index membership, age, caller relation, or lifecycle layer.

## External-wait recheck family

The audit separately crosses:

```text
WAITING_FOR_REVIEW
WAITING_FOR_CHECKS
MERGE_QUEUED
PROVIDER_WAIT
FINAL_INTEGRATION_PROOF_PENDING
```

against changed/unchanged/blocked/unknown observations and unrelated invocation reasons.

It establishes that every such state is refreshed on each explicit invocation, while an unchanged external wait may stop locally for that invocation without causing spin or blocking unrelated progress.

## Static architecture cross-check

The static pass checks:

- balanced Markdown code fences;
- contiguous ADR sequence 001..036;
- current main document defines the complete known nonterminal managed-obligation universe;
- all lifecycle layers through final target-integration observation/proof are included;
- `ACTIVE_CONVERGENCE_SET` is explicitly non-authoritative and reconstructible;
- old `load ACTIVE_CONVERGENCE_SET + recovery references` scope construction is absent from the current main execution flow;
- caller/CWD/age/repository/local unit identity cannot narrow invocation processing;
- external waits remain nonterminal across invocations;
- ADR-022's no-whole-disk-scan boundary is preserved;
- ADR-035 bounded ContributionUnit lifecycle and ADR-033 mutation-authority boundaries remain intact.

## Interpretation

This audit is exhaustive for the finite factorized state families explicitly modeled here. It does not claim exhaustive enumeration of an unbounded Git DAG, arbitrary provider implementation, or an unbounded count of managed obligations.

Historical v2-v5 reports remain records of earlier ontology/coverage stages but are not the current proof artifact.
