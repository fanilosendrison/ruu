---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Externalize development verification and model `ruu` as state-dependent Git progression"
id: "ADR-057"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "da291db28d2c424712a7504b2c23d1ce9677f40be7f4d56a42e16e929bfd4e71"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-057 — Externalize development verification and model `ruu` as state-dependent Git progression

- **Status:** Accepted — development-verification execution boundary retained; generic validation evidence/demand model superseded by ADR-060
- **Date:** 2026-09-06
- **Decision order:** 057

## Context

The architecture progressively gave `ruu` responsibilities for running repository test/lint/build contracts, scheduling verification capacity, handling verifier-induced mutation, retrying to a fixed point, and classifying flaky/infrastructure failures. Those responsibilities were introduced to preserve a valuable safety goal: exact managed Git states should not become authoritative merely because a Git operation can construct them.

The accumulated execution model, however, crossed the intended system boundary.

The actual development workflow is:

```text
Development System / coding agent
→ understands the task
→ authors code
→ runs/coordinates tests, lint, formatters, generators, reviews, security checks, etc.
→ decides that current work is sufficiently clean/ready for a Git progression boundary
→ signals convergence demand / makes the relevant durable intent transferable

                           ↓

                    Ruu
→ observes current managed Git/control/provider state
→ determines which Git transitions are currently required + legal
→ checkpoints / synchronizes / integrates / promotes / publishes / recovers
→ stops on semantic authoring or missing external development-validation obligations
```

`ruu` is therefore best understood as a **state-dependent, governed super Git operation**, not as a development orchestrator or local CI system.

At the same time, `ruu` can deterministically synthesize exact states that the Development System has not yet validated, such as a divergent internal merge result, promotion materialization candidate, or restacked submission revision. Publishing/adopting such a state without any development-side validation would weaken the original exact-state safety objective.

The architecture needs to keep the exact-state proof boundary while moving verification **execution and semantic quality policy** to the Development System.

## Decision

### 1. `ruu` is a state-dependent Git progression command

An invocation/trigger means only:

> **there is demand to make currently declared/transferable managed work progress through its next legal Git boundaries.**

The caller may invoke because it considers its current work ready to checkpoint, publish, refresh, recover, or otherwise progress, but the trigger itself is not a free-form workflow-stage command and does not manufacture state or authority.

`ruu` derives behavior from:

```text
current durable External Control Plane intent/lifecycle declarations
+ exact current Git/provider/coordination state
+ current policy/capability facts
+ exact development-validation evidence where required
→ currently legal Git transitions
```

There is no authoritative caller field such as:

```text
development_stage = READY_FOR_PR
```

that overrides current managed state. The same `ruu` invocation may checkpoint one ContributionUnit, integrate another, update an existing PR, refresh a provider wait, create a continuation PublicationEpisode, and recover an unrelated interrupted operation during the same global sweep.

### 2. Development verification execution belongs outside `ruu`

The External Control Plane / Development System owns orchestration and policy for development-quality work, including as applicable:

```text
tests
lint
typecheck
build
formatting
code generation
snapshot/golden updates
generated-artifact consistency
secret/security analysis
SAST / dependency / supply-chain analysis
agentic review
human review preparation
flaky-test handling
external-service test handling
verification retries
verification fixed-point / mutation handling
CPU/RAM/test-worker scheduling
local vs remote test execution
logs/artifacts/cache retention
```

`ruu` MUST NOT contain a built-in test runner, verification-capacity scheduler, retry-until-green loop, formatter/codegen loop, flaky-test policy, external-service test policy, or verifier-output cleanup policy.

ADR-031 verification-capacity scheduling is therefore superseded as a `ruu` responsibility. The operational concerns it described may still exist in the Development System, but they are not part of the `ruu` state machine or coordination domain.

### 3. Exact-state development-validation evidence remains a Git-progression precondition

The exact-state safety principle from ADR-010/029/030 is retained but reinterpreted through an **external development-validation contract**.

When current policy requires development validation for a Git transition, `ruu` consumes an externally produced exact-bound record conceptually equivalent to:

```text
DevelopmentValidationEvidence {
  evidence_id
  exact_candidate_identity
  development_gate_profile_identity_or_fingerprint
  relevant_declared_context_identity_or_fingerprint
  issuer/provenance
  result = VALID | REJECTED
}
```

The concrete schema may differ, but authorization requires at least enough identity to establish:

```text
this evidence
applies to this exact candidate
under this currently applicable external development gate/context
```

`ruu` does not need to know whether `VALID` was produced by one test, a thousand tests, an agent review quorum, a human assertion, a signed policy service, or a composite Development System pipeline.

Repository/organization policy may define the required external gate profile. A caller assertion may count only when current policy explicitly allows that form of attestation. Invocation alone is not silently promoted into stronger evidence than policy permits.

### 4. Exact binding/reuse remains, execution-count semantics disappear

Evidence reuse is state-oriented:

```text
same exact candidate
+ same applicable development-gate profile
+ same relevant declared validation context
+ current valid evidence
→ evidence may be reused

candidate/profile/relevant context changed
or evidence missing/stale/unknown/rejected
→ evidence cannot authorize the transition
```

This preserves ADR-030's exact-state/TOCTOU protection without requiring `ruu` to run anything.

There is no `ruu` concept of:

```text
VERIFYING
WAITING_VERIFICATION_CAPACITY
MUTATED_REVERIFY
NON_CONVERGENT_VERIFICATION
```

Those are Development System execution concerns.

### 5. Editing-surface checkpoint path

For a dirty ContributionUnit editing surface, the Development System may run any desired authoring/verification loop before transfer and invocation.

When `ruu` acquires the exclusive worktree claim, it snapshots/revalidates the exact commit candidate according to the still-open checkpoint candidate-membership contract. If current policy requires development-validation evidence, the evidence MUST bind to that exact candidate.

```text
candidate changed since external validation
or evidence refers to another candidate/profile/context
→ no commit
→ localized DEVELOPMENT_VALIDATION_REQUIRED / STALE_DEVELOPMENT_VALIDATION
```

`ruu` does not rerun tests to repair that mismatch. The Development System regains/creates authoring work, stabilizes the candidate, and later signals convergence demand again.

### 6. Ruu-synthesized candidates are immutable validation subjects

When deterministic Git mechanics synthesize a **new exact candidate** not already covered by valid current development-validation evidence, for example:

```text
target/base + ConvergenceUnit divergent merge result
ConvergenceUnit + ContributionUnit divergent synchronization result
repository-local PromotionUnit materialization result
submission restack/revision result
```

`ruu` MUST NOT silently publish/adopt it and MUST NOT run semantic tests itself.

Instead it:

```text
materializes exact immutable candidate C in an isolated/recoverable resource
→ records/refreshes DevelopmentValidationDemand(C, transition/context)
→ leaves the authoritative destination ref/provider surface unchanged
→ continues unrelated global-sweep work
```

The External Control Plane exposes that exact candidate to the Development System. When valid exact evidence for `C` later exists, a subsequent/reawakened sweep may continue from current-state revalidation and ordinary claims/CAS/policy guards.

A validation process that discovers required source changes does not mutate the `ruu` candidate in place as an authoring surface. Semantic changes re-enter through ordinary Development System authoring/provisioning (new ContributionUnit work, semantic reconciliation, review correction, settlement continuation, etc.). A different exact state `C'` is not evidence for `C`.

### 7. Pure state-preserving transitions may reuse evidence

If a transition merely points an authoritative managed ref at an exact state that already carries applicable valid development-validation evidence, no extra Development System execution is required merely because another Git boundary is crossed.

Examples include some exact fast-forwards or reuse of an already validated ADR-048 candidate, subject to all ordinary current-state/policy/claim/CAS guards.

### 8. Git/convergence validation remains inside `ruu`

Moving development verification outward does **not** move mechanical Git correctness upward.

`ruu` still owns and performs exact mechanical validation such as:

```text
repository/ref/worktree identity checks
exact OID observation
ancestry classification
expected-old / CAS validation
merge-base calculation
conflict detection
MaterializationContract / RestackContract checks
PromotionGroup / PromotionUnit exact resolution
provider capability/current-fact observation
provider head/check/review/queue observation
DIRECT CAS+FF proof
final target-integration observation/proof
recovery observation/adoption
```

This should be described as **Git/convergence validation**, not “running the repository tests”.

### 9. Review-request/ship-ready quality is external intent/evidence

`REVIEW_REQUESTED` remains an exact-revision publication/governance assertion under ADR-032, but the semantic composition of “ship-ready” belongs to the Development System / repository governance policy.

The Development System may use tests, independent agents, architecture review, documentation checks, security review, or any other process. `ruu` only consumes the exact-revision-bound review intent/evidence required by current policy and then performs/observes provider operations.

Similarly, provider CI execution policy belongs to provider/repository governance. `ruu` observes the exact provider check state required by current policy; it does not become the CI executor.

### 10. Core validation state becomes demand/evidence oriented

The canonical core state for externally supplied development validation is reduced to:

```text
NOT_REQUIRED
REQUIRED_MISSING
VALID_EXACT
STALE
REJECTED
UNKNOWN_INCONSISTENT
```

A missing/stale/rejected external development-validation condition is a localized nonterminal/blocking prerequisite, not an internal test job.

`DevelopmentValidationDemand` is part of the global managed-obligation universe only as an **external dependency to refresh/consume**, analogous to other external semantic obligations. `ruu` does not own the downstream test/review job lifecycle.

### 11. Backlog reclassification

The previous verification-heavy backlog mixed `ruu` questions with Development System concerns. It is reclassified as follows:

- **30.27** remains open only for the genuinely Git-level **checkpoint candidate snapshot/membership contract** (staged/tracked/untracked membership and exact pre-commit candidate identity). Verifier mutation/fixed-point/cycle/cleanup mechanics move outside `ruu`.
- **30.28** remains open only for the minimal exact external `DevelopmentValidationEvidence` reference/binding/persistence contract required by `ruu`; test logs/cache/executor equivalence/retention policy belong outside.
- **30.29** verification executor/capacity scheduling — closed as outside `ruu`.
- **30.30** flaky/infrastructure test policy — closed as outside `ruu`.
- **30.31** external-service test policy — closed as outside `ruu`.
- **30.32** semantic PR-author/ship-ready gate composition — closed as outside `ruu`; exact-revision intent/evidence consumption remains core and is already defined.
- **30.33** which CI/tests/security matrices execute at the provider — closed as repository/provider governance; exact provider-state observation remains core.
- **30.34** final integration / merge-result proof is closed by ADR-065 with native ancestry or exact provider-result binding plus authoritative Git observation.
- **30.35** agentic review policy — closed as outside `ruu`.
- **30.36** exact repository/provider policy for exceptional `REVIEW_NOT_REQUESTED` remains open only insofar as a deterministic built-in fallback/under-determined policy rule may still be needed; actual review workflow composition is external.
- **30.37** security-check placement — closed as outside `ruu`.
- **30.38** test/verification orchestration for internal integration — closed as outside `ruu`; a newly synthesized exact integration state may instead create an external `DevelopmentValidationDemand`.

## Rationale

The new boundary matches actual use:

```text
Development System decides "this is ready enough for Git progression"
→ Ruu is invoked
→ Ruu reacts to where the managed process currently is
```

This keeps `ruu` small in semantic scope while retaining the strongest part of the previous verification design: no evidence for one exact state may silently authorize another exact state.

It also avoids duplicating a Development System inside a Git convergence engine. Tests are feedback instruments for coding agents and belong where code is authored and corrected. `ruu` should communicate exact Git obstacles and exact validation subjects, not schedule test runners or fix source code.

## Consequences

- `ruu` becomes more clearly a governed, recoverable super Git command.
- Test/build/review execution can evolve independently (local agents, CI, remote workers, Temporal, etc.) without changing Git convergence semantics.
- Long test runs no longer hold or require `ruu` verification-capacity state.
- A clean deterministic Git merge may still pause before authoritative adoption if external development validation is required for the synthesized exact result.
- Global sweeps remain exhaustive; a validation wait localizes only the affected transition.
- External validation evidence must be exact-state-bound; stale evidence fails closed.
- Candidate-mutating development tools run in Development System authoring/validation loops, not inside the `ruu` candidate engine.
- Provider CI remains externally executed/provider-owned while its exact observed state remains relevant to publication governance.

## Supersession / amendments

- **ADR-029:** safety intent retained, execution ownership amended. The core no longer defines/runs a universal `tests/lint/typecheck/build/...` contract; it requires current exact external development-validation evidence where policy requires it.
- **ADR-030:** exact-state evidence binding/reuse retained; verifier-induced fixed-point execution is superseded as a `ruu` responsibility.
- **ADR-031:** superseded as a `ruu` architectural component. Verification compute scheduling is a Development System concern.
- **ADR-005/010/012/013/019/020/026/027/028/036/037/040/041/048/050/052/053/055:** terminology/guards are amended from internally executed “full verification” to exact external development-validation prerequisites while preserving their Git safety semantics.
- **ADR-039 / `EXTERNAL-CONTROL-PLANE-CONTRACT.md`:** amended to add `DevelopmentValidationDemand` delivery and external validation-evidence ownership.

## Related decisions

ADR-003, ADR-005, ADR-007, ADR-010, ADR-012, ADR-013, ADR-019, ADR-020, ADR-021, ADR-026, ADR-027, ADR-028, ADR-029, ADR-030, ADR-031, ADR-032, ADR-036, ADR-037, ADR-039, ADR-040, ADR-041, ADR-042, ADR-048, ADR-050, ADR-052, ADR-053, ADR-055.
## Current normative reading after ADR-059

The 30.27 item that ADR-057 reclassified as a Git-level checkpoint question is now closed by ADR-058/ADR-059. ADR-057's Development System / `ruu` validation-ownership boundary remains unchanged.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment — ADR-060 / ADR-062 / ADR-063 (current reading)

ADR-060 supersedes this ADR's temporary generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` handoff: current `ruu` uses only transition-local prerequisites and owns no generic development-validation state. ADR-062 further makes provider submissions projections rather than semantic promotion modes. ADR-063 keeps semantic review findings/backlog entirely in the Development System.

## Amendment by ADR-064

Pre-commit semantic validation may and preferably should occur before the Development System offers dirty work for checkpointing, but no validation certificate re-enters `ruu`. Exact identity across that boundary is preserved by ADR-064's frozen mutation-authority handoff: semantic validation/decision occurs externally, then external writes stop, then `ruu` constructs/revalidates/commits the exact ADR-059 candidate under exclusive claim.

## Amendment — ADR-065 (2026-09-07)

Backlog 30.34 is closed. Final target realization is a narrow Git/provider exact-state responsibility: native candidate ancestry proves realization when preserved; otherwise exact provider `C → R` binding plus independent `R`-in-target Git observation proves a provider rewrite. This does not reintroduce semantic development validation or diff-equivalence checking.
