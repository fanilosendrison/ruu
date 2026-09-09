# State-Space Audit v26 — ADR-057 state-dependent Git progression / external development validation

## 1. Scope

This audit extends v25 after ADR-057 corrects the architectural boundary between the Development System and `ruu`.

The normative model is now:

```text
Development System / agent
→ authors code
→ runs/coordinates tests, lint, build, formatters, generators,
  security analysis, review agents, retries, flaky/external-service handling
→ decides current work is ready enough to request Git progression

explicit convergence demand
        ↓

Ruu
→ observes current durable Git/coordination/provider state
→ performs the legal Git/convergence transitions for that state
→ consumes exact external DevelopmentValidationEvidence when policy requires it
→ emits/refreshes exact DevelopmentValidationDemand for synthesized candidates
  when required evidence is absent
→ never runs the development test/review pipeline itself
```

The audit intentionally removes verification-executor/capacity/fixed-point dimensions that no longer belong to the core. It retains exact-state evidence binding and adds explicit finite families for the external validation handoff.

A final retrospective static pass also removes stale normative wording that could still imply `verification jobs`, a verification-capacity queue, or an internal formatter/generator fixed-point loop.

## 2. ADR-057 properties exercised

The executable audit checks that:

1. invocation is a state-dependent Git progression demand, not a caller-supplied workflow-stage command;
2. tests/lint/build/formatters/generators/security/review execution belongs to the external Development System;
3. Git/convergence validation, exact refs/OIDs/ancestry/CAS/conflict/provider facts and owned-effect recovery remain inside `ruu`;
4. a dirty ContributionUnit checkpoint can advance only when the exact re-snapshotted candidate satisfies any current policy-required external development-validation prerequisite;
5. evidence for candidate `C1` never authorizes a different candidate `C2`;
6. a synthesized merge/materialization/restack candidate lacking required evidence remains immutable/recoverable and creates/refreshes `DevelopmentValidationDemand(C)` rather than causing internal test execution;
7. a validation wait blocks only the affected transition and remains globally re-evaluable on later sweeps;
8. ship-ready/review-agent/security/test composition belongs to the Development System/repository governance;
9. provider CI execution policy is external/provider-governed while exact provider check/review/queue observations remain core inputs;
10. ADR-031 verification-capacity scheduling is superseded as a `ruu` component;
11. no `WAITING_VERIFICATION_CAPACITY`, internal test-worker queue, flaky-test state, or verification fixed-point loop remains in the current core state machine;
12. the current main spec and ADR-005/007/029/030/031/039/040/048/057 use the corrected boundary consistently.

## 3. New/reframed finite families

ADR-057 adds or reframes these current core families:

```text
state_dependent_progression_invocation: 120
development_validation_ownership_boundary: 38
checkpoint_external_validation_guard: 240
synthesized_candidate_validation_handoff: 160
external_validation_evidence_binding: 90
validation_demand_localization: 12
ship_ready_external_ownership: 24
provider_ci_execution_observation_boundary: 10
```

Every still-applicable prior finite architecture family through ADR-056 is rerun as well.

The v25 verification-executor/capacity/fixed-point families are deliberately not part of the v26 total because ADR-057 places those dimensions outside the `ruu` state space.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-057**;
- the main definition calls `ruu` a **state-dependent governed super Git command**;
- the External Control Plane contract defines `DevelopmentValidationDemand` and `DevelopmentValidationEvidence`;
- ADR-029 retains exact-state safety but no longer means `ruu` runs a universal verification suite;
- ADR-030 retains exact evidence binding/reuse while its historical verifier-mutation fixed-point loop is superseded;
- ADR-031 is explicitly superseded as a `ruu` verification-capacity component;
- ADR-007's global fixed point is explicitly a Git/convergence fixed point, not a formatter/test fixed point;
- ADR-005 no longer treats a historical verification queue as a live core coordination mechanism;
- the current main spec contains no live `verification jobs`, queued/running verification workflow, verification-capacity admission, or internal verification-policy command matrix;
- 30.27 is narrowed to checkpoint candidate snapshot/membership semantics;
- 30.28 is narrowed to the minimal external evidence reference/binding contract;
- 30.29–30.33, 30.35, 30.37 and 30.38 are closed/reclassified outside the core;
- 30.34 and 30.36 remain genuine Git/provider-policy questions.

## 5. Result

Executable result:

```text
Ruu state-space audit v26: PASS
changed/revalidated finite combinations evaluated: 14,548
markdown artifacts statically cross-checked: 86
```

The lower finite-combination count than v25 is intentional. It reflects removal of invalid core state dimensions (test-worker capacity, flaky/external-service execution, verifier mutation/fixed-point state), not reduced checking of Git/convergence semantics.

Concrete Git smoke results remain:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
Ruu repository bootstrap smoke v1: PASS
```

No new Git primitive is introduced by ADR-057, so no additional Git smoke is required. The new boundary is exercised by state-space and static-contract checks.
