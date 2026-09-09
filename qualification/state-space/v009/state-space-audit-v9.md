# Ruu — State-Space / Global Consistency Audit v9

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-039
- **Trigger:** ADR-039 consolidated distributed upstream dependencies into a single normative External Control Plane contract.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete current architecture after introducing:

```text
EXTERNAL-CONTROL-PLANE-CONTRACT.md
```

as the normative interface for logical/runtime responsibilities outside `ruu`.

The audit specifically checks that consolidation does not accidentally:

- move exact Git/provider truth into the External Control Plane;
- let external declarations bypass `ruu` claims, verification, CAS, or recovery rules;
- narrow ADR-036 global sweep semantics;
- weaken ADR-037 eager ContributionUnit integration or sealed `READY_INTERNAL` conditions;
- re-couple ADR-038 ContributionUnit identity to branch/worktree lifecycle;
- close still-open policy/API questions merely by naming the External Control Plane;
- leave vague current “external subsystem” dependencies outside the consolidated contract.

This remains a factorized finite-state audit, not a claim to enumerate the unbounded Git DAG/provider state space.

## 2. New finite family: External Control Plane responsibility boundary

`external_control_plane_responsibility_boundary` enumerates 15 representative responsibilities against four possible claimed owners:

```text
owner:
  EXTERNAL_CONTROL_PLANE
  RUU
  INFERRED
  UNKNOWN
```

Responsibilities expected on the External Control Plane side include:

```text
CREATE_CONTRIBUTION_UNIT
BIND_CONTRIBUTION_TO_CONVERGENCE
SET_CONTRIBUTION_LIFECYCLE
SET_CONVERGENCE_MEMBERSHIP
PROVISION_EDITING_SURFACE
DECLARE_EXTERNAL_MUTATION_ACCESS
DECLARE_PROMOTION_GROUPING_TOPOLOGY
MAP_SEMANTIC_REVIEW_FEEDBACK
```

Responsibilities expected on the `ruu` side include:

```text
OBSERVE_EXACT_GIT_PROVIDER_STATE
CREATE_MANAGED_CHECKPOINT
INTEGRATE_CONTRIBUTION_CHECKPOINT
COMPUTE_READY_INTERNAL
MATERIALIZE_PROMOTION_SUBMISSION
REFRESH_PROVIDER_WAIT
RECOVER_RUU_OWNED_OPERATION
```

Result: **60 combinations**.

Validated:

```text
logical/runtime intent declarations
→ External Control Plane

exact Git/provider progression mechanics
→ Ruu

INFERRED / UNKNOWN ownership
→ never a valid substitute for the required side of the boundary
```

## 3. Revalidated state families

The v9 executable reruns every current v8 finite family unchanged:

- ContributionUnit identity/cardinality: **256**;
- actor-correlation irrelevance: **120**;
- ContributionUnit lifecycle: **144**;
- exact-state continuity after artifact disappearance: **36**;
- ContributionUnit checkpoint-record CAS: **216**;
- external ConvergenceUnit grouping authority: **15**;
- eager ContributionUnit integration: **6,912**;
- ConvergenceUnit membership/readiness: **720**;
- experimental isolation level: **18**;
- global managed-obligation coverage: **432**;
- external-wait recheck: **80**;
- ContributionUnit worktree mutation authority: **240**;
- commit/full-verification cross-check: **1,350**;
- state-producing transition verification: **432**;
- verification evidence reuse: **72**;
- verification fixed point: **108**;
- verification capacity scheduling: **180**;
- review-request intent: **108**;
- review-revision invalidation: **24**;
- internal integration evidence: **240**.

Together with the new boundary family, v9 evaluates **11,763 finite combinations**.

## 4. Static architecture consistency checks

The static audit verifies:

1. ADR numbering is contiguous from **001 through 039**.
2. Markdown fences are balanced across the current architecture artifacts.
3. `EXTERNAL-CONTROL-PLANE-CONTRACT.md` exists and is referenced by the main requirements.
4. Main §7.10 defines the External Control Plane as the normative upstream boundary.
5. The contract explicitly contains:
   - ContributionUnit creation/binding/lifecycle authority;
   - ConvergenceUnit creation/membership authority;
   - external mutation-access classification;
   - promotion grouping/topology intent;
   - semantic review-feedback mapping responsibility;
   - the rule that Git/provider facts remain independently authoritative;
   - the ADR-036 global-sweep non-narrowing rule;
   - the interface-discipline rule forbidding hidden external preconditions.
6. Current normative boundary ADRs do not retain vague `external subsystem` / `external contribution-unit subsystem` ownership wording.
7. Backlog 30.16–30.18, 30.23, and 30.26 remain open despite contract consolidation.
8. ADR-038 exact-state/artifact-independence invariants and ADR-037 readiness semantics remain present.
9. Retired writer/work-context/lease ontology remains absent from the current main model.

## 5. Result

The executable audit reports:

```text
Ruu state-space audit v9: PASS

contribution_unit_cardinality_identity: 256
actor_correlation_irrelevance: 120
contribution_unit_lifecycle: 144
contribution_unit_artifact_exact_state_continuity: 36
contribution_unit_checkpoint_record_cas: 216
external_convergence_grouping_authority: 15
external_control_plane_responsibility_boundary: 60
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

changed/revalidated finite combinations evaluated: 11,763
```

After inclusion of this report, the complete package contains **51 Markdown artifacts** subject to static cross-checking.

## 6. Interpretation

ADR-039 is a boundary-consolidation decision, not a transfer of Git authority upward.

The architecture now has an explicit two-sided contract:

```text
External Control Plane
→ declares logical topology/lifecycle/transferability/semantic grouping intent

Git/remotes/provider
→ authoritative external facts

                    ↓

Ruu
→ revalidates exact facts
→ advances every safe authorized managed transition
→ current global fixed point
```

This makes upstream assumptions visible and auditable without coupling `ruu` to any particular orchestrator or runtime.
