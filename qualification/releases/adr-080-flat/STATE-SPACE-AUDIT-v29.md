# Ruu — State-Space Audit v29

- **Date:** 2026-09-06
- **Architecture through:** ADR-060
- **Result:** PASS

## 1. Purpose

This pass revalidates the retained finite architecture state-space after ADR-060 closes backlog 30.28 by removing the generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` gate from `ruu`.

ADR-057's core boundary remains: development-quality execution stays outside `ruu`. ADR-060 tightens that boundary further:

```text
Development System
→ may test/review/validate however it chooses
→ decides when to expose lifecycle/governance/authoring intent it owns

Ruu
→ does not ask whether generic development validation is missing
→ evaluates each transition from exact Git/managed/provider state
  + only the transition-specific authoritative external facts it genuinely needs
```

The audit specifically checks that removing the generic certificate does not weaken exact-state, provider, review, policy, CAS, lifecycle, conflict, settlement, or recovery guards.

## 2. ADR-060 state-space change

### 2.1 Removed obsolete generic validation families

The following v28 finite families are retired from the core because their states no longer exist in `ruu`:

```text
development_validation_ownership_boundary
checkpoint_external_validation_guard
synthesized_candidate_validation_handoff
external_validation_evidence_binding
validation_demand_localization
```

Corresponding core states such as generic `VALID_EXACT`, missing/stale development-validation waits, and validation-demand obligations are no longer modeled.

### 2.2 Transition-local prerequisite separation

A replacement regression family varies:

```text
transition = CHECKPOINT | INTEGRATION | READY_INTERNAL | PUBLICATION | FINALIZATION
Git/managed transition state = VALID | INVALID
required transition-specific external fact = PRESENT | MISSING
generic development-validation certificate = PRESENT | ABSENT
```

Eligibility is intentionally invariant to the generic certificate dimension and depends only on the exact transition-local prerequisites.

Finite combinations: **40**.

## 3. Static integration checks

The static pass verifies among other things that:

- ADR numbering is contiguous through **ADR-060**;
- main section 30.28 is explicitly **closed by ADR-060 as obsolete**;
- the backlog now contains only **30.34** and **30.36** as genuine open core questions;
- the External Control Plane contract no longer defines `DevelopmentValidationDemand` or `DevelopmentValidationEvidence`;
- the current requirements no longer contain generic validation-wait states such as `DEVELOPMENT_VALIDATION_REQUIRED`, `STALE_DEVELOPMENT_VALIDATION`, `CANDIDATE_AWAITING_DEVELOPMENT_VALIDATION`, or `SUBMISSION_AWAITING_DEVELOPMENT_VALIDATION`;
- checkpoint creation depends on offered/transferable editing state + mutation authority + ADR-059 canonical Git guards, not on a generic validation certificate;
- clean synthesized internal/materialization/restack states use their transition-local exact prerequisites;
- review-request intent, provider checks/reviews/queue observations, promotion policy, lifecycle declarations, CAS guards, reconciliation descriptors, and final target proof remain exact-bound where applicable;
- historical ADRs that still describe the superseded generic evidence model carry an explicit ADR-060 amendment note;
- Markdown code fences remain balanced.

## 4. Git smoke validation

ADR-060 introduces no new Git primitive, so no sixth Git smoke is required. All five retained concrete Git primitive smokes still pass:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
Ruu repository bootstrap smoke v1: PASS
Ruu canonical checkpoint smoke v1: PASS
```

## 5. Result

Executable result:

```text
Ruu state-space audit v29: PASS
changed/revalidated finite combinations evaluated: 14,222
markdown artifacts statically cross-checked: 92
```

The lower finite-combination count versus v28 is intentional: ADR-060 deletes obsolete generic development-validation states rather than replacing them with another gate protocol.

**Verdict:** 30.28 is closed without adding a new authorization/evidence layer. `ruu` remains neutral to semantic development quality while still failing closed on the exact Git/managed/policy/provider prerequisites that belong to each concrete transition.
