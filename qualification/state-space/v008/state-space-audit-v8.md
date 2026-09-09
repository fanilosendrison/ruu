# Ruu — State-Space / Global Consistency Audit v8

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-038
- **Trigger:** ADR-038 removed ContributionUnit `ABANDONED`/`REMOVED` lifecycle semantics and decoupled logical contribution identity/exact managed state from branch/ref/worktree presence.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the current architecture after a particularly cross-cutting boundary change:

```text
ContributionUnit identity
!= local branch/ref existence
!= worktree existence
!= remote branch existence

ContributionUnit lifecycle
= OPEN | CLOSED
```

The audit specifically tests that `ruu` does not accidentally:

- treat editing-artifact absence as semantic closure or abandonment;
- require the producer worktree for upward convergence of an already-created exact checkpoint;
- infer local recreation or remote deletion intent from missing local refs;
- declare internal readiness while a required exact checkpoint is unresolved or unrecoverable;
- lose global fixed-point coverage at later ConvergenceUnit/PromotionUnit/provider layers;
- weaken exact-state verification, claims, review-intent, or provider-facing invariants introduced by ADR-029..ADR-037.

This remains a factorized finite-state audit, not a claim to enumerate the unbounded Git DAG/provider state space.

## 2. New / changed finite families

### 2.1 ContributionUnit identity versus editing artifacts

`contribution_unit_cardinality_identity` enumerates:

```text
lifecycle: OPEN | CLOSED
repository binding: ZERO | ONE | MULTIPLE | UNKNOWN
convergence binding: ZERO | ONE | MULTIPLE | UNKNOWN
local ref: PRESENT | ABSENT
worktree: PRESENT | ABSENT
remote ref: PRESENT | ABSENT
```

Result: **256 combinations**.

Validated:

```text
valid ContributionUnit identity
→ exactly one repository
→ exactly one ConvergenceUnit

local/remote ref presence
worktree presence
→ never participate in identity validity
```

### 2.2 ContributionUnit lifecycle independence

`contribution_unit_lifecycle` cross-checks lifecycle against runtime state, integration state, editing-artifact presence, and later-work intent.

Result: **144 combinations**.

Validated:

```text
OPEN
→ same identity may still produce later contribution

CLOSED
→ same identity may never produce later contribution

runtime/turn/integration/artifact presence
→ never infer OPEN/CLOSED
```

### 2.3 Exact-state continuity after editing-artifact disappearance

`contribution_unit_artifact_exact_state_continuity` enumerates:

```text
lifecycle: OPEN | CLOSED
editing artifacts: PRESENT | ABSENT
checkpoint state: ABSENT | REACHABLE | UNRECOVERABLE
obligation: NONE | RESOLVED | UNRESOLVED
```

Result: **36 combinations**.

Validated:

```text
artifacts absent
+ obligation NONE/RESOLVED
→ no Ruu action required

artifacts absent
+ unresolved exact checkpoint REACHABLE
→ convergence may continue from exact OID

unresolved exact checkpoint UNRECOVERABLE
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss
```

No branch/worktree absence by itself produces recovery state.

### 2.4 Logical checkpoint-record CAS is independent of producer editing-surface presence

`contribution_unit_checkpoint_record_cas` enumerates logical checkpoint-record advance/no-change, exact record claim, expected-old state, verification evidence, durable reachability anchoring, and producer editing-surface presence.

Result: **216 combinations**.

Validated:

```text
logical latest-checkpoint advance
→ exact record claim held
→ expected-old matches
→ exact result verification valid
→ result durably reachable/anchored

producer editing surface PRESENT vs ABSENT
→ does not alter logical checkpoint-record CAS authorization
```

This is the concurrency bridge that allows synchronization/reconciliation to continue in an isolated workspace after the original branch/worktree disappears.

### 2.5 Worktree mutation authority only applies when a worktree exists

`contribution_unit_worktree_mutation_authority` now includes editing-surface presence explicitly and removes ContributionUnit cleanup as a `ruu` worktree operation.

Result: **240 combinations**.

Validated:

```text
editing surface ABSENT
→ no worktree mutation authority can exist

surface PRESENT
+ external transferability valid
+ exact invocation claim held
+ topology known
→ worktree mutation may be authorized
```

### 2.6 Commit verification

`contribution_unit_commit_verification_crosscheck` validates both `OPEN` and `CLOSED` units with absent/clean/dirty surfaces.

Result: **1,350 combinations**.

A commit is possible only for an existing dirty surface under exact mutation authority and stable exact full-verification PASS. An absent surface cannot manufacture a checkpoint.

### 2.7 Eager upward integration is artifact-independent

`eager_contribution_integration` now enumerates `OPEN | CLOSED`, exact checkpoint reachability, editing-surface presence, topology, convergence claim, conflict state, ancestry relation, verification evidence, and the retired legacy release flag.

Result: **6,912 combinations**.

Validated:

```text
valid authoritative checkpoint REACHABLE
+ mechanically safe edge
→ eager upward-convergence candidate

producer editing surface PRESENT vs ABSENT
→ does not change upward-integration eligibility

checkpoint UNRECOVERABLE
→ cannot advance

legacy integration-release state
→ remains irrelevant
```

### 2.8 Sealed readiness is exact-obligation based

`convergence_membership_readiness` includes:

```text
membership OPEN | SEALED
ContributionUnit aggregate:
  ALL_CLOSED_RESOLVED
  HAS_OPEN
  HAS_CLOSED_UNRESOLVED
  HAS_MISSING_MANAGED_STATE
  UNKNOWN_ORPHAN
internal state CLEAR | BLOCKED
verification evidence
fixed-point state
editing-artifact layout ALL_PRESENT | SOME_ABSENT | ALL_ABSENT
```

Result: **720 combinations**.

Validated:

```text
SEALED
+ ALL_CLOSED_RESOLVED
+ internal CLEAR
+ exact verification VALID
+ fixed point YES
→ READY_INTERNAL
```

Editing-artifact layout does not change readiness once all exact contribution obligations are resolved.

## 3. Revalidated pre-existing families

The audit also reruns the current finite families for:

- actor-correlation irrelevance: **120**;
- external ConvergenceUnit grouping authority: **15**;
- experimental isolation level: **18**;
- global managed-obligation coverage: **432**;
- external wait recheck: **80**;
- state-producing transition verification: **432**;
- verification evidence reuse: **72**;
- verification fixed point: **108**;
- verification capacity scheduler: **180**;
- review-request intent: **108**;
- review-revision invalidation: **24**;
- internal integration evidence: **240**.

The global sweep invariant remains unchanged:

```text
every explicit invocation
→ every known nonterminal managed obligation at every layer
→ advance every currently safe/authorized transition
→ blocked object remains localized
→ repeat to current global fixed point
```

## 4. Static architecture consistency checks

The static audit verifies:

1. ADR numbering is contiguous from **001 through 038**.
2. Markdown fences are balanced across all current Markdown artifacts.
3. The main requirements contain the ADR-038 exact-state/artifact-independence contract.
4. Current normative main-spec text does not retain:
   - ContributionUnit lifecycle `ABANDONED`;
   - ContributionUnit lifecycle `REMOVED`;
   - `non-abandoned ContributionUnit` integration gating;
   - abandonment disposition readiness clauses;
   - ContributionUnit cleanup lifecycle as a `ruu` responsibility.
5. ADR-035 explicitly records that its former abandonment/removal semantics are superseded by ADR-038.
6. ADR-037 eager integration applies to both `OPEN` and `CLOSED` ContributionUnits.
7. Backlog item 30.9 is retired and no abandonment residue policy remains open.
8. Retired writer/work-context/lease ontology remains absent from the current main model.

## 5. Result

The executable audit reports:

```text
Ruu state-space audit v8: PASS

contribution_unit_cardinality_identity: 256
actor_correlation_irrelevance: 120
contribution_unit_lifecycle: 144
contribution_unit_artifact_exact_state_continuity: 36
contribution_unit_checkpoint_record_cas: 216
external_convergence_grouping_authority: 15
eager_contribution_integration: 6,912
convergence_membership_readiness: 720
experimental_isolation_level: 18
global_managed_obligation_coverage: 432
external_wait_recheck: 80
contribution_unit_worktree_mutation_authority: 240
contribution_unit_commit_verification_crosscheck: 1,350
state_producing_transition_verification: 432
verification_evidence_reuse: 72
verification_fixed_point: 108
verification_capacity_scheduler: 180
review_request_intent: 108
review_revision_invalidation: 24
internal_integration_evidence: 240

changed/revalidated finite combinations evaluated: 11,703
```

After inclusion of this report, the complete package contains **48 Markdown artifacts** subject to static cross-checking.

## 6. Interpretation

ADR-038 does not weaken convergence safety. It moves the safety boundary to the object that actually matters:

```text
exact managed Git state still required?
```

instead of:

```text
does the original producer branch/worktree still exist?
```

The model remains fail-closed exactly where destructive guessing would be required, while no longer manufacturing false recovery obligations from ordinary user/agent branch or worktree lifecycle actions.
