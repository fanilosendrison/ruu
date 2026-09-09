# Ruu — State-Space Audit v7

- **Date:** 2026-09-05
- **Scope:** main requirements + ADR-001..ADR-037 after eager ContributionUnit integration and sealed ConvergenceUnit readiness
- **Executable audit:** `state-space-audit-v7.py`
- **Recorded output:** `state-space-audit-v7.txt`
- **Result:** **PASS**

## What changed since v6

ADR-037 closes the remaining ContributionUnit→ConvergenceUnit semantic gaps:

```text
external higher layer
→ creates/reuses ConvergenceUnit
→ binds each ContributionUnit to exactly one ConvergenceUnit
→ declares contribution membership OPEN | SEALED

valid non-abandoned managed checkpoint
→ earliest mechanically safe upward integration

ConvergenceUnit membership OPEN
→ ordinary convergence allowed
→ READY_INTERNAL forbidden

ConvergenceUnit membership SEALED
+ all ContributionUnit obligations terminal/resolved
+ no unresolved internal transition/recovery
+ exact full-verification evidence
+ internal fixed point
→ READY_INTERNAL(exact OID)
```

No separate ContributionUnit integration-release/readiness state exists. Experimental or alternative work that must remain isolated is represented by a distinct ConvergenceUnit. Retained terminal/resolved ContributionUnit refs are cleanup/retention state and do not by themselves block readiness.

## Exhaustive finite families

```text
contribution_unit_cardinality_identity:             512
actor_correlation_irrelevance:                       120
contribution_unit_lifecycle:                         144
external_convergence_grouping_authority:              15
eager_contribution_integration:                    5,184
convergence_membership_readiness:                    384
experimental_isolation_level:                        18
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

**Changed/revalidated finite combinations: 9,103.**

## New family: external convergence grouping authority

Crosses grouping source and membership cardinality and establishes that only an externally declared exact one-ConvergenceUnit binding is authoritative. Caller, file overlap, CWD, or unknown inference never creates valid membership.

## New family: eager ContributionUnit integration

Crosses:

```text
ContributionUnit lifecycle
checkpoint validity
known/unknown topology
claim holder
conflict state
ancestry/synchronization relation
verification evidence
legacy release flag ABSENT/PRESENT/STALE
```

The integration candidate/result is intentionally invariant under the legacy release axis. No hidden `RELEASED_EXACT`-style state can suppress an otherwise valid eager convergence transition.

`ABANDONED`/`REMOVED`, invalid/stale checkpoints, unknown topology, missing claim, or conflicts correctly block the edge. A `NEEDS_SYNC` relationship requires downward synchronization before retry rather than unsafe upward mutation.

## New family: ConvergenceUnit membership/readiness

Crosses:

```text
membership: OPEN | SEALED
ContributionUnit aggregate:
  ALL_TERMINAL_RESOLVED
  HAS_OPEN
  HAS_UNRESOLVED_TERMINAL
  UNKNOWN_ORPHAN
internal obligations: CLEAR | BLOCKED
exact full-verification evidence: VALID | MISSING | STALE | FAIL
internal fixed point: YES | NO | UNKNOWN
terminal/resolved ref retention: NONE | RETAINED
```

`READY_INTERNAL` is reachable only for:

```text
SEALED
+ ALL_TERMINAL_RESOLVED
+ CLEAR
+ VALID exact evidence
+ fixed point YES
```

Historical terminal/resolved ref retention does not alter that result.

## New family: experimental isolation level

Experimental/alternative work is valid only when bound to a distinct ConvergenceUnit and ordinary upward integration is not suppressed. This guards against reintroducing a per-checkpoint “commit but do not converge” mode.

## Static architecture cross-check

The static pass verifies:

- contiguous ADR sequence 001..037;
- balanced Markdown fences across all current Markdown artifacts;
- main spec contains externally authoritative ConvergenceUnit grouping/membership;
- main spec contains no separate ContributionUnit integration-release/readiness state;
- main spec requires earliest mechanically safe upward integration;
- `OPEN` membership blocks readiness but not ordinary convergence;
- `SEALED` + terminal/resolved obligations + exact proof + fixed point defines `READY_INTERNAL`;
- physical ContributionUnit ref deletion is not the readiness definition;
- old `exact contribution unit-integration readiness`, `VALID_EXACT` ContributionUnit readiness, and `zero contribution-unit refs` readiness rules are absent from the current main model;
- main §30 marks 30.5–30.7 resolved by ADR-037;
- `OPEN-DESIGN-BACKLOG.md` no longer lists items 5–7 as open;
- ADR-035 bounded ContributionUnit lifecycle, ADR-036 global sweep, ADR-033 mutation authority, and ADR-029/030 exact verification semantics remain intact.

## Interpretation

This audit is exhaustive for the finite factorized state families explicitly modeled here. It does not claim exhaustive enumeration of unbounded Git DAGs, arbitrary provider implementations, or unbounded numbers of managed objects.

Historical v2-v6 reports remain records of earlier ontology/coverage stages but are not the current proof artifact.
