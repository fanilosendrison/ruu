# ADR-039: Formalize the external control-plane boundary as a normative contract

- **Status:** Accepted — external diagnostic/interfaces amended by ADR-040, ADR-043, ADR-055, ADR-056, and ADR-057; amended by ADR-061 and clarified by ADR-078
- **Date:** 2026-09-05
- **Decision order:** 039

## Context

ADR-023/027/033/034/035/037/038 progressively moved several responsibilities outside `ruu`: pre-edit provisioning, ContributionUnit identity/lifecycle, ConvergenceUnit grouping/membership, external mutation authority, editing-artifact lifecycle, and promotion grouping and (historically) topology intent.

Those decisions were individually coherent, but the requirements had accumulated phrases such as “higher-level subsystem”, “contribution-unit subsystem”, “higher layer”, and “higher-level principal”. Without one explicit interface, future changes could silently add external preconditions without a single place defining what `ruu` is allowed to assume.

## Decision

Create the normative companion document:

```text
EXTERNAL-CONTROL-PLANE-CONTRACT.md
```

and define **External Control Plane** as an abstract architectural role, not a required concrete component.

The External Control Plane contract consolidates external ownership of:

```text
ContributionUnit creation + stable repository/ConvergenceUnit binding
ContributionUnit lifecycle OPEN | CLOSED
ConvergenceUnit creation/reuse + contribution membership OPEN | SEALED
pre-edit editing-surface provisioning
external producer/runtime mutation-authority transferability
promotion grouping; ADR-050 later removes stack-layout intent from this external responsibility
semantic mapping that reactivates ConvergenceUnit scopes after feedback
```

It also makes explicit that:

```text
Git/remotes/provider remain authoritative for their own facts
external declarations do not manufacture Git/provider truth
Ruu retains exact-state verification/convergence/promotion/provider/recovery mechanics
every invocation remains global over all nonterminal managed obligations
```

The External Control Plane may be implemented by one component or several cooperating components, including user/agent tooling, an orchestrator, a provisioner, or repository policy. `ruu` depends only on the contract.

### Interface-discipline rule

Any future normative dependency on a “higher-level subsystem”, orchestrator, provisioner, agent runtime, caller, or comparable external actor must either:

1. map to an existing External Control Plane Contract clause; or
2. amend that contract explicitly through an ADR.

This prevents hidden upstream assumptions from accumulating in the main `ruu` specification.

## Non-decisions

This ADR does **not** decide currently open policy/implementation questions merely because they touch the External Control Plane. In particular it does not close:

```text
30.16 promotion-unit declaration API (subsequently closed by ADR-045)
30.17 promotion-group/default-mapping semantics (subsequently closed by ADR-046)
30.18 multi-source promotion projection algorithm (subsequently closed by ADR-047; repository-local candidate composition moved to 30.39 and subsequently closed by ADR-048)
30.23 semantic CHANGES_REQUESTED continuation policy (subsequently closed by ADR-053)
30.24 PromotionUnit completion versus ConvergenceUnit retirement/retention (subsequently closed by ADR-054)
30.25 cross-repository settlement/compensation (subsequently closed by ADR-055)
30.26 brand-new repository/provider-repository creation authority (subsequently closed by ADR-056)
```

It also does not select a storage technology, runtime architecture, single-host/multi-host implementation, heartbeat mechanism, or particular orchestrator.

## Rationale

The external boundary is now a first-class architecture interface. Consolidating it:

- keeps the main `ruu` requirements focused on convergence mechanics;
- prevents repeated vague “higher-level subsystem” wording;
- makes upstream obligations auditable as one contract;
- permits multiple runtimes/tooling implementations without coupling `ruu` to any of them;
- preserves the distinction between logical intent supplied externally and exact Git/provider truth revalidated by `ruu`.

## Consequences

- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` is normative.
- ADR-023/027/033/034/035/037/038 are interpreted through this consolidated contract where they describe external responsibility.
- The main requirements reference the contract rather than redefining the upstream interface ad hoc.
- Future external dependencies require an explicit contract clause/ADR amendment.
- No existing global-sweep, exact-state, verification, claim, readiness, promotion, or recovery invariant is weakened.

## Amendment effect

This ADR consolidates and clarifies the external boundary of ADR-023, ADR-027, ADR-033, ADR-034, ADR-035, ADR-037, and ADR-038. It does not supersede their substantive safety decisions.


## Amendment by ADR-040

The External Control Plane contract now includes delivery of exact `RECONCILIATION_REQUIRED` obligations to an external Development System capable of semantic code authoring. This does not transfer conflict detection, exact Git truth, validation, or adoption authority out of `ruu`: authored results must re-enter the ordinary current-state revalidation + claims/CAS pipeline and satisfy any current exact external development-validation prerequisite required by policy.


## Amendment by ADR-041

The External Control Plane mutation-authority contract is now durable and trigger-independent: `PROTECTED_EXTERNAL | TRANSFERABLE_TO_RUU | TRANSFERABLE_GENERAL | UNKNOWN`. A caller's convergence trigger carries no authority and may be coalesced with other triggers. Any authority change must become authoritative through the External Control Plane separately from signaling convergence demand.


## Amendment by ADR-043

The external boundary now also carries first-class promotion-policy contradiction diagnostics. `ruu` exposes exact incompatible authoritative constraints/facts and their source revisions/fingerprints; the External Control Plane makes that factual blocking state available to the external Development System/operator. `ruu` does not infer, recommend, rank, or apply a remediation.


## Amendment by ADR-046

The External Control Plane promotion-grouping contract is now durable and pre-exact. Before signaling convergence demand, it declares a closed immutable content-addressed `PromotionGroup(Set<CanonicalConvergenceUnitRef>)`, where each canonical ref includes repository identity plus repository-local ConvergenceUnit identity. `ruu` resolves the group mechanically to current exact `READY_INTERNAL` states. ADR-047 then partitions the complete exact snapshot by authoritative source repository and materializes one ADR-045 PromotionUnit per represented repository under snapshot/CAS. No implicit singleton/default mapping and no mid-sweep callback merely to learn exact OIDs remain.


## Amendment by ADR-047

The External Control Plane still declares one closed logical PromotionGroup before convergence demand. For the intended session-scoped workflow, all ConvergenceUnits emitted by the same development session for the ship are in that group. ADR-047 changes only `ruu`'s downstream resolution: a completely ready group is partitioned mechanically by authoritative source repository into one PromotionUnit per represented repository. Session identity remains upstream provenance and is excluded from content addressing.


## Amendment by ADR-050

The External Control Plane no longer declares stacked-vs-independent provider layout as publication intent. It remains authoritative for PromotionGroup membership and other external logical/runtime declarations. Current promotion dependency/PromotionTopology is derived inside `ruu` from exact managed effective-base/predecessor/target facts among already-distinct promotion obligations. Branch/task/session names and arbitrary ancestry remain non-authoritative.

## Amendment by ADR-055

ADR-055 adds durable exact-generation `CrossRepositorySettlementDemand` delivery/semantic disposition to the External Control Plane contract and introduces forward-only roll-forward/compensation settlement semantics. It also performs the required retrospective interface audit: accepted pre-ADR-039 boundaries from ADR-022 (repository admission/derived active index), ADR-024/036 (trigger identity is not mutation authority/work ownership/sweep scope), ADR-026 (runtime requests cannot manufacture promotion authorization), and ADR-032 (review-request intent is exact-revision publication/governance intent rather than inferred readiness) are now explicit clauses of the companion contract. The open PR-author gate and REVIEW_NOT_REQUESTED policy questions remain open under 30.32/30.36.


## Amendment by ADR-056

ADR-056 closes the previously open new-repository boundary and adds it to the normative companion contract. Repository creation remains external to `ruu`: the External Control Plane resolves creation authority/policy, a Repository Provisioner creates/reconciles local/provider resources, and a brand-new repository is admitted to managed authoring only after its configured target exists at exact non-null bootstrap OID `B0`. Local creation and provider attachment may be decoupled; provider-sensitive progression waits for required provider binding. Names/paths do not establish identity, unknown collisions fail closed, and partial provisioning failure does not authorize destructive deletion.

## Amendment by ADR-057

ADR-057 corrects the development-verification boundary. Repository tests/lint/build/formatters/generators/security analysis/agentic review, their execution capacity, flaky/external-service handling, mutation/fixed-point loops, and validation artifacts/caches are External Control Plane / Development System concerns, not `ruu` execution responsibilities.

`ruu` retains exact-state safety by consuming current externally produced `DevelopmentValidationEvidence` bound to the exact candidate/gate/context required by policy. When deterministic Git mechanics synthesize a new exact candidate without such evidence, `ruu` records/refreshes an exact `DevelopmentValidationDemand`, leaves the authoritative destination unchanged, and continues unrelated obligations. Semantic changes discovered during validation re-enter through normal Development System authoring rather than mutating a `ruu` candidate in place.

This also makes the invocation boundary explicit: a convergence trigger expresses demand to progress current managed Git state, while the specific next legal transitions are derived from durable External Control Plane state + exact Git/provider/coordination facts + current policy/evidence. `ruu` is not a test orchestrator or workflow-stage executor.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-061

The normative companion contract now explicitly assigns pre-authoring ConvergenceUnit PromotionTarget resolution/binding to the External Control Plane. The binding is immutable for that ConvergenceUnit identity; `ruu` consumes it as logical destination intent while continuing to re-observe current target OID/provider facts.

## Amendment by ADR-069

For ordinary new work, the External Control Plane no longer separately declares a PromotionGroup member set. It supplies the exact closed ContributionUnit cohort of a durable work-bearing logical invocation; `ruu` derives the group ConvergenceUnit membership mechanically. The External Control Plane remains authoritative for correction/reconciliation binding to an existing group and all semantic dispositions.



## Amendment by ADR-074

The External Control Plane contract now includes one narrow exceptional authoring-binding recovery authority for irretrievable native causal-proof loss. `AuthoringBindingRecovery` is bound to the existing ContributionUnit/work occurrence, expected old binding and binding generation, and resolves only `REBIND(new_ref) | ABANDON`. It expresses logical continuity/disposition; it cannot manufacture Git history. `ruu` independently revalidates actual ref/worktree/OID topology and mutation authority before adopting a rebind. Pre-edit provisioning also guarantees a native reflog for the managed authoring ref. ADR-075 further requires that live managed authoring not begin until the selected ref backend/adapter has established the required pre-linearization managed-binding observation capability; this remains a Git capability fact, not an External Control Plane declaration.


## Clarification by ADR-078

"External" in **External Control Plane** denotes an architectural authority boundary relative to the convergence engine, not a mandatory packaging or installation boundary. A Ruu distribution may ship coding-harness adapters/provisioning primitives that implement this role for supported harnesses, provided semantic authority remains governed by this contract and all required pre-edit guarantees are established before first managed write. The ordinary supported-harness UX must not require a second control-plane product or explicit start/create-CU/provision preflight.
