# Ruu — Decision Integration Log (2026-09-04..2026-09-07 chat replay)

This file records the chronological architecture decisions replayed from the design discussion and where each was integrated. It is traceability material, not a replacement for normative ADRs.

> **ADR-057 architectural correction (2026-09-06).** Historical decisions 4–16 below were made while development-verification execution was still modeled too low in the stack. ADR-057 preserves their exact-state safety intent but moves tests, lint, build, formatters/codegen, security analysis, agentic review, flaky/external-service handling, retries/fixed-point mutation handling, and compute scheduling to the Development System. `ruu` is a state-dependent governed super-Git operation: it consumes exact external development-validation evidence when policy requires it and emits exact `DevelopmentValidationDemand`s for synthesized candidates it cannot safely advance without such evidence. Historical wording below is annotated rather than erased so the decision evolution remains auditable.

> **ADR-060 correction (2026-09-07).** ADR-060 subsequently removes the generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` protocol altogether. Historical ADR-057/earlier wording about a generic evidence handoff is retained only as decision history; the current model uses transition-local prerequisites and keeps semantic development validation entirely outside `ruu`.

## 1. Gates follow semantic transitions, not Git command names

Decision: `commit`, `push`, PR publication, review, integration, and rebase/history transformation represent different authority boundaries. A universal preflight attached mechanically to every Git command is the wrong abstraction.

Integrated into the main transition/eligibility model and existing ADR-005/016/017/026/027/028.

## 2. A real PR review request means the candidate is already ship-ready

Decision: reviewers should challenge a candidate already considered ready, not finish obvious implementation/testing/cleanup work.

Integrated by ADR-032. Exact PR-author gate remains open.

## 3. Agentic review is not assumed to be a scarce bottleneck

Decision: independent agent reviews may occur earlier/more often/parallel; exact policy remains open.

Recorded in main §30 and `OPEN-DESIGN-BACKLOG.md` L.

## 4. Agents should inherit the cleanest possible codebase

Historical decision: WIP worktrees may be red, but durable managed states should not knowingly propagate state lacking the development assurance required by policy to subsequent agents.

ADR-057 retains that safety intent but externalizes the execution. The Development System produces the relevant validation evidence; `ruu` exact-binds/consumes it where policy requires.

## 5. Tests are agent feedback instruments, not only downstream CI gates

Decision: relevant unit/integration/E2E tests should be usable during implementation; E2E is not categorically delayed to GitHub.

Integrated as architectural guidance in the main document. Runtime test-selection during implementation remains outside `ruu`'s core mutation authority.

## 6. Full repository-required verification before managed checkpoints

Historical decision: full repository-required development validation was preferred over impact-only selection at the managed checkpoint boundary. Later empirical inspection confirmed the predecessor Development System already ran the repo-declared test contract before requesting commit-like progression.

ADR-057 supersedes only the execution ownership: those tests are orchestrated by the Development System, while `ruu` consumes exact evidence if current policy requires it.

## 7. Required baseline verification categories

Decided baseline:

```text
tests
lint
typecheck
build
secret scan
generated-artifact consistency
custom verification
```

General deep security scanning remains separate/open.

Historical validation-policy guidance retained for the Development System; ADR-057 removes these categories from `ruu` execution ownership.

## 8. Commit verification does not imply completion/readiness

Decision: `COMMITTED → VERIFIED checkpoint`, but `COMMITTED` does not imply `READY`, closed, semantically complete, or promotable.

Integrated by amendments to ADR-003 and main §§4/26/33.

## 9. Existing worktree ownership already provides the local logical freeze

Decision after spec inspection: no new local `FREEZE_CANDIDATE` business state is needed. `CONVERGE_OWNS_WORKTREE` plus revalidation/stability protects contribution unit/converger TOCTOU.

Integrated by amendments to ADR-009 and main ownership/commit algorithms.

## 10. Verification-induced mutation requires stable fixed point — execution ownership superseded by ADR-057

Historical decision: tests/generators may transform `X → X'`; evidence for `X` never proves `X'`. ADR-057 retains that exact-state rule but moves mutation/fixed-point handling entirely to the Development System. `ruu` does not classify formatter/codegen/parasite outputs or loop tests.

## 11. Verification applies to all locally produced managed states, not only dirty-contribution unit commits

Corrected by ADR-057: internal Git mechanics may synthesize a new exact candidate that the Development System has never validated. `ruu` must keep that candidate immutable/recoverable and, when current policy requires development validation, emit an exact `DevelopmentValidationDemand`; it may adopt/publish only after matching external evidence is available. It does not run the validation itself.

## 12. Evidence-oriented verification, not invocation-count-oriented reruns

Decision:

```text
exact result has valid policy-required external development-validation evidence

same exact result + same policy + same relevant context
→ reuse

state/policy/context changed
→ rerun
```

The retained invariant is exact-state evidence binding, not internal suite execution. ADR-057 makes validation orchestration external.

Integrated by ADR-030.

## 13. Verification compute capacity is outside `ruu` — corrected by ADR-057

Historical ADR-031 modeled validation capacity beside Git claims. ADR-057 supersedes that component: the Development System owns test/review/security compute capacity, queues, workers, and backpressure. Git/provider claims remain wholly separate in `ruu`.

## 14. Development-validation executor technology is external

Bazel/Docker/GitHub/VM/local shell remain Development System implementation choices. They are not `ruu` components after ADR-057; only exact evidence/provenance required by policy crosses the boundary.

## 15. Push remains publication, not a generic quality boundary

Decision as amended by ADR-057: push checks remote/ref/authorization/CAS/publication policy and may consume/reuse matching exact external development-validation evidence. `ruu` does not push merely to run its own validation job.

Integrated by amendments to ADR-020 and main §15/22.

## 16. A verified PR still needs fresh integration reasoning

Decision: PR validity and exact target integration validity are distinct; target movement can create a new combined state. Existing ADR-010/021/provider queue semantics already cover much of this. Final merge-result verification details remain open.

Recorded in backlog H.

## 17. Draft PR is not a `ruu` business state

Decision: internal WIP already has `OPEN/NOT_READY`; draft is provider representation only.

Integrated by ADR-032.

## 18. Review publication intent is `REVIEW_NOT_REQUESTED` / `REVIEW_REQUESTED`

Decision: GitHub adapter maps these to draft/ready-for-review. Nominal path publishes `REVIEW_REQUESTED` directly; `REVIEW_NOT_REQUESTED` is exceptional for provider-only checks, stack exposure, or code-level early feedback.

Integrated by ADR-032 and submission/provider state model.

## 19. Stack/rebase nuance remains ref-class specific

Decision confirmed against current ADRs: no rebase for internal contribution unit/CU refs; provider-facing rewriteable submission refs may be restacked under narrow policy/expected-old guards.

Already normative in ADR-016/028; main spec retained.

## 20. Full state-space audit must be rerun after verification/review-intent additions

Decision: new verification state, evidence reuse, capacity, and review-request axes cannot be patched locally without re-enumerating state combinations.

Implemented by `state-space-audit-v2.py`, `STATE-SPACE-AUDIT-v2.md`, and updated main §34.

## 21. Producer/runtime liveness is not a `ruu` responsibility

Decision: `ruu` must not classify external producer/runtime liveness through heartbeat, timeout, process/session state, turn lifecycle, or an internal lease. The contribution-unit subsystem owns external mutation rights and determines when a repository-local contribution unit is safely transferable.

Integrated by ADR-033 and main §§2/4/8/9/10/26/27/30/33.

## 22. Contribution-unit identity is opaque and repository-local

Decision: `contribution_unit_id` is the stable opaque repository-local isolation identity supplied by the contribution-unit subsystem. `ruu` does not infer it from principal, process, session, branch name, worktree path, model, or CWD. No global actor identity is required by `ruu`.

Integrated by ADR-033 and finalized by ADR-034.

## 23. Transferability and `ruu` claim are distinct

Decision:

```text
external contribution-unit subsystem says context is transferable
≠
Ruu already owns mutation authority
```

`ruu` may mutate only after the context is transferable to this invocation (or generally transferable) **and** this exact invocation has acquired the exclusive worktree claim. Protected/other/unknown external authority fails closed.

Integrated by ADR-033 and the revised main contribution-unit-worktree state model.

## 24. Global audit rerun after authority-boundary change

Decision: the old 14,220 v2 aggregate cannot be carried forward blindly because some historical baseline families encoded the retired ACTIVE/INACTIVE + delegation ontology. The new audit must re-enumerate the changed authority families, rerun all v2 verification/review families, and statically cross-check the complete artifact set.

Implemented by `state-space-audit-v3.py`, `STATE-SPACE-AUDIT-v3.md`, `state-space-audit-v3.txt`, and updated main §34.


## 25. Replace Git-level writer identity with repository-local contribution units

Decision: the normative isolation object is a repository-local `contribution_unit_id`; no global producer identity remains in the `ruu` model. A contribution unit may represent greenfield/from-scratch creation or modification of existing content. Higher-level work spanning repositories uses multiple independent contribution units and any actor correlation stays above `ruu`.

Integrated by ADR-034, terminology/cardinality updates across the main requirements and current ADRs, and `STATE-SPACE-AUDIT-v4.md`.

## 26. Replace reusable work-context terminology with bounded contribution units

Decision: the repository-local isolation object is a bounded `contribution_unit_id`, not a reusable `work_context`. A contribution unit carries one bounded stream of contribution to its current convergence scope and remains compatible with greenfield/from-scratch work.

Lifecycle is externally authoritative and independent of agent/process/session/turn state:

```text
OPEN
→ may still contribute to current convergence scope

CLOSED
→ no further contribution to current convergence scope
→ unresolved contribution remains intended for convergence
→ later work requires a new contribution_unit_id

```

ADR-038 later supersedes the former `ABANDONED` branch: current ContributionUnit lifecycle is `OPEN | CLOSED` only. `CLOSED` never returns to `OPEN`. Waiting for user input, ending an agent turn, committing, verification PASS, or current integration does not close a contribution unit. `ruu` consumes the lifecycle declaration from the external contribution-unit subsystem and never originates semantic closure.

`CHANGES_REQUESTED` may cause a convergence unit to return to `ACTIVE`; implementation changes use a newly provisioned contribution unit rather than reopening a terminal one.

Recorded in ADR-035, main §§2.1, 8, 22, 26, 30, 33, and `OPEN-DESIGN-BACKLOG.md`.

## 27. Every invocation is global over all nonterminal managed obligations

Decision: the caller only triggers an opportunity to converge; it never narrows processing by current repo, ContributionUnit, ConvergenceUnit, PromotionUnit, task, age, or invocation reason. Every explicit invocation re-evaluates every known nonterminal managed obligation from contribution checkpoints through convergence/promotion and PR/review/check/provider/merge-queue state to final target-integration proof, recovery, and cleanup.

`ACTIVE_CONVERGENCE_SET` is retained only as a derived/reconstructible acceleration index. A stale/missing index cannot suppress authoritative managed obligations. External waits are current-pass stop states but remain nonterminal and are refreshed on every later invocation.

Integrated by ADR-036 and amendments to ADR-004/007/013/021/022/031, main §§1/4/7/21/33, and the v6 global audit.


## 28. Contribution checkpoints converge eagerly; ConvergenceUnit readiness requires sealed membership

Decision: ConvergenceUnit creation/reuse, ContributionUnit membership, and contribution-membership `OPEN | SEALED` are externally authoritative. `ruu` never infers semantic grouping from caller/task/files/names/CWD.

There is no separate ContributionUnit integration-release/readiness state:

```text
valid authoritative managed checkpoint
+ mechanically safe edge
→ MUST attempt earliest safe upward integration
```

Experimental/alternative work is isolated by assigning it to a distinct ConvergenceUnit, not by suppressing integration within a ContributionUnit.

ConvergenceUnit membership `OPEN` allows ordinary convergence but blocks `READY_INTERNAL`. `SEALED` allows readiness evaluation only when all ContributionUnit obligations are terminal/resolved, internal sync/integration/reconciliation/conflict/recovery obligations are clear, the exact result has valid policy-required external development-validation evidence, and the internal fixed point is reached. Physical ContributionUnit branch/ref/worktree presence or absence is not readiness by itself; ADR-038 later makes artifact lifecycle external to `ruu`.

Integrated by ADR-037, amendments to ADR-006/008/010/011/019/027/030/035, main §§2/5/18/22/30/33, backlog closure of 30.5–30.7, and the v7 global audit.


## 29. ContributionUnit identity is exact-state based, not editing-artifact based

Decision: `ContributionUnit` lifecycle is reduced to `OPEN | CLOSED`. `ABANDONED` and `REMOVED` are removed from the normative ContributionUnit model. Unwanted code is changed/deleted through later development state; branch/worktree/remote-ref lifecycle is owned by user/agent/higher-level tooling, not by `ruu`.

ContributionUnit identity is durable independently of branch/worktree existence. For convergence, the important durable fact is the latest authoritative managed checkpoint OID when one exists.

```text
editing artifacts absent + no unresolved exact checkpoint
→ no Ruu action required

editing artifacts absent + unresolved exact checkpoint OID recoverable
→ continue convergence from exact OID

required unresolved exact checkpoint OID unrecoverable
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss
```

No local-branch absence implies remote deletion, local recreation, or semantic closure.

Integrated by ADR-038, amendments to ADR-002/005/008/009/012/013/023/034/035/037, main §§2/5/8/18/22/27/30/33, backlog retirement of 30.9, and the v8 global audit.


## 30. Formalize the External Control Plane contract

Decision: upstream logical/runtime responsibilities that had accumulated across ADR-023/027/033/034/035/037/038 are consolidated into a single normative interface:

```text
EXTERNAL-CONTROL-PLANE-CONTRACT.md
```

The External Control Plane is an abstract role, not a required concrete service. It owns the explicit logical/runtime declarations that `ruu` cannot infer safely: ContributionUnit creation/binding/lifecycle, ConvergenceUnit grouping/membership, pre-edit provisioning, external mutation transferability, and promotion grouping/topology intent as originally captured by ADR-039 (topology intent is subsequently removed by ADR-050). Git/remotes/provider remain authoritative for their own facts, while `ruu` retains exact-state convergence/promotion/provider/recovery mechanics and the global fixed-point sweep.

Future normative dependencies on any “higher-level subsystem”, orchestrator, provisioner, caller, or agent runtime must map to this contract or explicitly amend it through an ADR.

Integrated by ADR-039, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §7.10/invariants, current ADR terminology normalization, backlog annotation, and the v9 global audit.



## 31. Emit exact reconciliation obligations; scope candidate attribution to mutation authority

Decision: `ruu` performs deterministic clean reconciliation when Git/repository mechanics can construct an unambiguous candidate, but it does not author semantic conflict resolution. An authoring-required conflict leaves authoritative refs unchanged and emits a durable exact-state-bound `RECONCILIATION_REQUIRED` obligation containing sufficient mechanical conflict evidence for the external Development System.

The obligation is diagnostic, not adoption authority. Any authored result is re-evaluated against current Git/topology/policy state, current claims/CAS are required, and the exact candidate/result must satisfy any policy-required exact external development-validation prerequisite before adoption. Stale historical conflict descriptors are superseded by current-state proof rather than externally marked resolved.

Contribution candidate ownership is mutation-boundary scoped rather than process scoped: hooks, generators, formatters, package managers, and subordinate tooling operating inside a valid ContributionUnit mutation-authority boundary contribute to that ContributionUnit candidate. A known mutation outside the authorized boundary is an integrity/staleness condition and fails closed; no actor attribution guess is made.

Integrated by ADR-040, amendments to ADR-009/012/013/033/036/037/039, the External Control Plane contract, main §§7/8/16/21/22/26/30/33, backlog closure of 30.10 and 30.12, and the v10 global audit.

## 32. Coalesce concurrent convergence demands under one single-host fenced executor

Decision: `ruu` v1 has a single-host coordination domain. Simultaneous explicit invocations are not durable FIFO work items and are not replayed one by one. They are coalescible convergence-demand signals recorded through a durable monotonic demand relation equivalent to:

```text
requested_generation
processed_generation
```

At most one top-level executor is authoritative at a time. It performs the ADR-036 global fixed-point sweep over current state, marks the covered demand generation processed only after reaching the current fixed point, then rechecks whether newer demand arrived. If so it sweeps again; otherwise it releases ownership and exits. Internal independent Git/provider work may still run in parallel; development-validation work is external under ADR-057.

Executor ownership is transactionally fenced by a monotonic generation/token or equivalent. Liveness may justify takeover but does not itself confer correctness authority; once a newer generation is established, older executors cannot authoritatively adopt new managed progression.

The exact-invocation authority states are retired:

```text
TRANSFERABLE_TO_THIS_INVOCATION
TRANSFERABLE_TO_OTHER_INVOCATION
```

Current External Control Plane mutation access is trigger-independent durable state:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

A convergence trigger carries no mutation authority. Any upstream authority change must become durably visible through the External Control Plane separately from signaling convergence demand.

Fine-grained claims/CAS remain for actual mutable resources, internal parallel operations, exact transfer arbitration, and recovery; they no longer schedule several simultaneous top-level convergers.

The v1 coordination-store semantic core is now fixed as single-host, durable, transactional, demand-aware, fenced-executor-aware, and recoverable. SQLite is the preferred/reference v1 backend. ADR-042 subsequently closes the concrete schema/run-ownership/journal/transaction/repository-relocation questions that ADR-041 intentionally left under backlog 30.13.

Integrated by ADR-041, amendments to ADR-003/005/007/009/022/024/028/031/033/034/036/039, the External Control Plane contract, main §§2/4/5/7–13/22/24/26/30/33, backlog closure of 30.1 and 30.11, narrowing of 30.13, and the v11 global audit.

## 33. Close 30.13 with a reconciler-driven CoordinationStore and append-only recoverable-effect journal

Decision: `ruu` is not a persisted workflow engine. Its top-level runtime is a current-state `ConvergenceEngine`/reconciler that repeatedly re-observes the complete known nonterminal obligation universe, progresses mechanically safe work, exactly observes/adopts results, and repeats to the current global fixed point.

The concrete v1 coordination backend is host-local SQLite. Physical top-level run ownership is a dedicated OS process-lifetime exclusive advisory lock; durable authority is a monotonic `run_generation` plus unique `run_token`. Demand release uses a durable `ACTIVE → IDLE` handshake: a caller that already recorded new demand and sees `OS lock BUSY + IDLE` retries ownership acquisition instead of returning, preventing the release-window lost-wakeup race. A live-but-hung process is not automatically taken over by TTL/heartbeat in v1; long Git/provider work is bounded; Development System validation execution is external and waiting provider state is localized rather than slept on under the run lock.

Recoverable external effects use the append-only success path:

```text
Operation
→ Attempt(s)
→ exact Observation
→ Adoption atomically with successful managed-state CAS
```

The logical `operation_id` survives retries; physical attempts are separately fenced. Attempt metadata never proves an external effect. No SQLite transaction spans Git/provider/network/long-filesystem work. Operations that become terminal without adoption receive immutable observation-bound closure/disposition.

Repository identity is opaque and stable across path relocation; the current host-local locator is a separately CAS-updatable binding. Correctness-critical temporary refs/workspaces use non-recycled operation/attempt/incarnation namespaces. Recovery resources are `REQUIRED` until independent durable reachability/recovery sufficiency is proven, then become `GC_ELIGIBLE`; physical cleanup thereafter is best-effort and outside the business Operation journal.

Integrated by ADR-042, amendments to ADR-041/main §7/§27/§30/§33/invariants, External Control Plane repository-binding clarification, backlog closure of 30.13, and the v12 global audit.


## 34. Compile promotion policy from authoritative constraints; expose contradictions without remediation advice

Decision: backlog 30.14 is closed without introducing a source-precedence ladder. Promotion authorization is derived by composing provider capabilities/current facts, provider/organization governance constraints, and trusted repository-committed policy. Explicit incompatible authoritative constraints produce `CONTRADICTORY` and block only the affected promotion; one source is never silently selected as the winner.

Runtime human/agent/orchestrator input and explicit local config cannot bypass or mutate promotion authorization. Repository policy governing a promotion is read from the trusted exact target baseline, so candidate-only policy changes cannot authorize their own promotion. Deterministic built-in rules fill only still-underdetermined dimensions, allowing zero-onboarding `DIRECT` operation when direct promotion is admissible and no authoritative constraint requires an indirect path.

A policy contradiction is emitted as a first-class machine-readable factual signal containing exact incompatible constraints and source provenance. `ruu` does not generate `recommended_fix`, `resolution_candidates`, ranked remediation, or governance mutations; interpretation and action belong to the external Development System/operator.

Integrated by ADR-043, amendments to ADR-026/ADR-039, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§4/7/28/30/33/invariants, backlog closure of 30.14, and the v13 global audit.


## 35. Make promotion-policy currentness depend on immediate authoritative revalidation, never cache age

Decision: backlog 30.15 is closed. Policy snapshots are immutable/fingerprinted observations, but cache/TTL is optimization only and never establishes `CURRENT`. Every executed global sweep refreshes relevant policy state, and every policy-sensitive promotion mutation additionally requires an immediately preceding re-observation/revalidation of all mutable authoritative policy sources needed by that mutation.

Any movement of the trusted target/repo-policy anchor or provider/organization governance/capability/current-fact observation invalidates the snapshot and forces recomputation before mutation. Strong provider versions/fingerprints/ETags are used when exposed; otherwise a fresh normalized observation is required. No TTL fallback substitutes for unavailable versioning.

When the provider cannot atomically combine governance check and mutation, `ruu` accepts the unavoidable external TOCTOU boundary: it re-observes immediately before the operation, then provider enforcement/rejection and exact post-operation observation are the final authority boundary. Concurrent drift/rejection is emitted factually to the external Development System/operator and is never auto-repaired or interpreted as permission.

Integrated by ADR-044, amendments to ADR-026/ADR-042/ADR-043, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§4/7/22/30/invariants, backlog closure of 30.15, and the v14 global audit.


## 36. Make PromotionUnits immutable content-addressed exact-state sets

Decision: backlog 30.16 is closed. A PromotionUnit is no longer a caller-named mutable declaration carrying target intent, dependency parent, or semantic-readiness metadata. It is exactly one immutable non-empty unordered unique set of canonical `ExactConvergenceStateRef` members.

V1 derives `promotion_unit_id` deterministically with domain-separated/versioned SHA-256 over an unambiguous canonical encoding of the sorted member refs. The same exact member set therefore resolves idempotently to the same PromotionUnit; changing any exact member state creates a different PromotionUnit. A stored ID/definition mismatch fails closed as an integrity/unknown-inconsistent condition.

Promotion topology is a separate relationship among PromotionUnit refs. EffectivePromotionPolicy controls target/mode/publication authorization. Lifecycle and provider-facing submission revisions may evolve without changing the immutable PromotionUnit identity. The declaration itself is the External Control Plane semantic grouping assertion; there is no separate semantic-readiness token. Structural declaration validity and current promotion eligibility remain separate predicates.

Integrated by ADR-045, amendments to ADR-027/ADR-039/ADR-042/ADR-044, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§2/7/27/30/32/33/invariants, backlog closure of 30.16, and the v15 global audit.


## 37. Predeclare closed PromotionGroups and resolve them without mid-sweep handoff

Decision: backlog 30.17 is closed. The External Control Plane no longer waits for exact READY_INTERNAL OIDs and then declares grouping, and `ruu` no longer has any implicit/policy-driven singleton mapping. Before convergence demand, the Development System durably declares a closed immutable non-empty unordered unique `PromotionGroup` over canonical `(repository_id, convergence_unit_id)` refs.

V1 content-addresses that logical member set using domain-separated/versioned SHA-256. Explicit invocations remain coalescible demand signals; grouping is durable trigger-independent state. During a sweep, `ruu` resolves the group only when every member has one current exact `READY_INTERNAL` state, adopts the complete exact set under coherent snapshot/CAS checks, and materializes/reuses the ADR-045 PromotionUnit. A singleton is explicitly `{CX}`; multi-repo grouping uses the same mechanism. No partial resolution and no mid-sweep callback merely to learn exact OIDs.

PromotionGroup is distinct from PromotionUnit, PromotionTopology, and EffectivePromotionPolicy. ConvergenceUnit is the indivisible promotion-grouping boundary; independent work requiring separate promotion must remain in distinct ConvergenceUnits upstream.

Integrated by ADR-046, amendments to ADR-027/ADR-039/ADR-041/ADR-042/ADR-045, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§2/18/27/30/invariants, backlog closure of 30.17, and the v16 global audit.


## 38. Project PromotionGroups deterministically into repository-local PromotionUnits

Decision: backlog 30.18 is closed. A PromotionGroup remains the closed pre-exact logical ship and may span repositories, but ADR-046's original one-group→one-PromotionUnit mapping is superseded. After every group member has one current exact `READY_INTERNAL` state in a coherent snapshot, `ruu` partitions that complete exact set by authoritative source `repository_id` and materializes/reuses exactly one ADR-045 PromotionUnit per represented repository. The complete repository→PromotionUnit mapping is adopted under expected-state/CAS guards.

PromotionUnit source membership is therefore repository-local. Same PromotionGroup + same source repository always maps to one PromotionUnit; `ruu` does not split it to manufacture stacked PRs and does not infer alternate proposal partitions. PromotionTopology remains separate explicit state. Cross-repository PR publication relation remains a policy dimension and is not confused with PromotionUnit source locality.

For the intended v1 session-scoped workflow, all ConvergenceUnits emitted by the same development session for the ship belong to the same PromotionGroup; session identity is upstream provenance and remains outside the content address. Cross-repository group progress may be `NONE_PROMOTED`, `PARTIALLY_PROMOTED`, or `ALL_PROMOTED` while each resulting PromotionUnit has its own repository-local lifecycle/policy.

Repository-local composition of several exact source states into one exact candidate/head is deliberately separated from structural projection and was left open as new backlog item 30.39; ADR-048 subsequently closes it.

Integrated by ADR-047, amendments to ADR-014/027/045/046, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§2/18/30/33/invariants, backlog closure of 30.18, and the v17 global audit.


## 39. Materialize repository-local multi-source PromotionUnits by canonical pairwise merging

Decision: backlog 30.39 is closed. After ADR-047 has produced one exact repository-local PromotionUnit, `ruu` materializes its single publication candidate from one exact effective base plus the immutable exact source set. Execution-only ancestry reduction removes sources already contained by the base/another retained source, then a versioned canonical source order drives a pairwise fold using full `ort`-class two-head three-way merge semantics (or a proven-equivalent implementation). Native multi-head octopus does not define semantics.

The fold's transient commits are computational artifacts. Ancestor/descendant steps reuse exact existing commits; if the base or one source already contains the complete unit, that exact commit is the candidate. Otherwise the final fold tree is condensed into one canonical synthetic multi-parent candidate commit with the exact effective base as first parent and the canonical retained source heads as the remaining unique direct parents. OID-affecting metadata is deterministic and wall-clock-independent under a versioned MaterializationContract. The exact base and every original PromotionUnit source OID must be ancestors of the final candidate.

A merge step requiring semantic authoring stops materialization and emits/refreshes ADR-040 `RECONCILIATION_REQUIRED` with exact materialization evidence; authoritative refs are not modified to force a result. Candidate computation is isolated from producer worktrees and follows ADR-042 `Operation → Attempt → Observation → Adoption` recovery. Only the exact final candidate becomes promotion-adoptable, and a newly produced final candidate must satisfy any policy-required exact external development-validation prerequisite bound to its exact candidate identity before authoritative submission/DIRECT progression.

Integrated by ADR-048, amendments to the main materializer/state-space/invariants, External Control Plane boundary clarification, backlog closure of 30.39, and the v18 global audit.


## 40. Separate stable submission identity/ref lifecycle from internal exact-state refs

Decision: backlog 30.19 is closed. Every PR-mode logical submission uses a provider-facing submission ref physically distinct from all internal ContributionUnit/ConvergenceUnit refs even when the exact OID is initially the same. Stable `submission_id` identifies one repository-local PromotionGroup projection toward one canonical publication destination, while exact `promotion_unit_id`, current head, and monotonic `submission_revision` may change. First publication requires a current exact PR candidate with any policy-required external development-validation prerequisite satisfied and expected-remote-absent protection; revisions require exact expected-old/force-with-lease-equivalent guards and post-mutation local/remote/provider agreement. Branch/ref naming is descriptive and durably bound, never parsed for semantics. Physical submission-ref cleanup becomes eligible only after terminal provider/target/recovery state; durable revision/audit history is independent.

Integrated by ADR-049, amendments to ADR-021/028/045/047/048 and main §§18/19/28/29/30/33/invariants, backlog closure of 30.19, and the v19 global audit.

## 41. Derive stacked publication from exact unsatisfied promotion dependency; restack by exact state transplant

Decision: backlog 30.20 is closed. Users/agents/callers do not choose stacked PR publication. `ruu` derives a current promotion dependency when exact managed effective-base/predecessor/target facts establish that a child promotion is represented on a predecessor promotion not yet realized in the authoritative target. If target-satisfied, the child is ordinary; if unsatisfied and supported/authorized, the provider representation is stacked; otherwise the child waits.

When the predecessor exact head changes, restack never rewrites internal state and never replays arbitrary commit narrative. It reprojects the child's immutable owned `(old_base_oid, owned_candidate_oid)` aggregate state onto the new base using a versioned full three-way state-transplant semantic (`base=old base`, `ours=new base`, `theirs=owned candidate`). Each restack is recomputed from the immutable owned anchor, not the prior provider rewrite; conflict routes to `RECONCILIATION_REQUIRED`; every new exact head satisfies any policy-required external development-validation prerequisite and only the ADR-049 submission ref/revision is expected-old rewritten. Local/provider-native/external execution is pluggable only if exact observed output conforms to the same contract.

Integrated by ADR-050, amendments to ADR-027/028/039/047/048/049, the External Control Plane contract, main §§4/5/18/22/28/30/33/invariants, backlog closure of 30.20, and the v19 global audit.

## 42. Normalize provider capabilities as contextual semantic-operation observations

Decision: backlog 30.21 is closed. `ruu` core first derives the semantic transition required by current exact managed state. Provider adapters then observe whether that exact operation is technically supported in its exact provider/repository/target/submission context; provider-wide feature labels such as “stack support” are not sufficient semantic facts. Capability observations normalize support, applicability/current facts, relevant evidence/review/check effects, provider mechanism, and freshness provenance.

Capability and policy authority remain distinct: execution requires `REQUIRED ∩ SUPPORTED ∩ AUTHORIZED` plus all ordinary exact-state, verification, claim, and recovery guards. ADR-050 stack shape remains derived from exact unsatisfied promotion dependency rather than policy/provider choice. Provider-native or external executors never become semantic authority; their exact observed outputs are adopted only when they conform to the same normative core contract. ADR-044 immediate pre-mutation revalidation applies to all mutable capability/current-fact observations.

Integrated by ADR-051, amendments to ADR-026/043/044/050, the main provider/promotion-policy model, backlog closure of 30.21, and the v20 global audit.

## 43. Make DIRECT target advancement a pure exact-old CAS+FF ref effect

Decision: backlog 30.22 is closed. Once ADR-048 has materialized exact candidate `C` and any policy-required external development-validation prerequisite for `C` is satisfied from exact authoritative target baseline `B`, DIRECT promotion does not check out/merge into a target worktree and does not pre-advance a local target ref. The core records/reconciles `AdvanceTargetFF(target, expected_old=B, new=C)`, whose only permitted successful effect is atomic `B → C` when authoritative target is still exactly `B` and immutable ancestry proves `B` ancestor-or-equal `C`. Expected-old mismatch causes no mutation and forces fresh target/policy/candidate resolution.

Exact `C` is protected while nonterminal by an attempt-scoped non-business recovery anchor under ADR-042. Recovery observes authoritative target history: target equal `C` or containing `C` as an ancestor proves the promotion effect occurred (even if later target progress followed); target still equal `B` proves it has not occurred; divergent history is stale/drift rather than invented success. Physical recovery-anchor cleanup becomes eligible only after durable adoption/recovery sufficiency. The core contract is semantic and backend-neutral; provider/Git mechanisms are conforming only if they preserve exact-old comparison and descendant-only target effect.

Integrated by ADR-052, amendments to ADR-026/041/042/044/048/051, main DIRECT flow/matrix/engine/invariants/state-space model, backlog closure of 30.22, and the v21 global audit.


## 44. Turn CHANGES_REQUESTED into durable session-independent correction work

Decision: backlog 30.23 is closed. A current exact `CHANGES_REQUESTED` generation becomes one durable idempotent ReviewCorrectionDemand keyed/bound to the exact reviewed submission revision/head, immutable PromotionGroup/repository projection, authoritative provider review generation/fingerprint, and factual feedback payload. Provider webhook/event delivery and any later `ruu` global sweep are coequal discovery paths for the same demand; rediscovery cannot create unrelated correction obligations, and the session that happened to trigger a sweep does not inherit the work.

The coding session that originally produced the PR may already be closed. The External Control Plane may restore it or start a new continuation session with the review feedback/context as new development input. The correction session may discover affected existing ConvergenceUnit scope(s) while working; those scopes are explicitly reactivated as needed, and every new authoring surface uses a new ContributionUnit/writer branch/worktree. Terminal ContributionUnits never reopen and the provider submission branch is never the coding workspace.

Ordinary corrections preserve the immutable PromotionGroup, later resolve to new immutable exact PromotionUnits/candidates, and—under ADR-049—advance the same logical submission/provider PR when the logical key is unchanged. Genuinely new ConvergenceUnit scope cannot be appended to the old closed group and requires a different/superseding PromotionGroup workflow.

Integrated by ADR-053, amendments to ADR-021/039/046/049, the External Control Plane contract, main §§30/33, backlog closure of 30.23, and the v22 global audit.

## 45. Separate PromotionUnit completion from ConvergenceUnit closure and retirement

Decision: backlog 30.24 is closed. `PromotionUnit PROMOTED` is now explicitly only an exact repository-local snapshot outcome; it cannot by itself close or retire any source ConvergenceUnit. A ConvergenceUnit reaches `PROMOTED` only when every relevant PromotionGroup/promotion obligation is terminally settled and no current ReviewCorrectionDemand/authoring/reconciliation obligation can still reactivate the lineage. Cross-repository `PARTIALLY_PROMOTED` therefore keeps member ConvergenceUnits semantically open even when one local projection is already promoted.

ConvergenceUnit `PROMOTED` is the semantic no-more-authoring boundary. `RETIRED` is later and additionally requires terminal effects to be durably adopted and all correctness-critical recovery/resource dependencies to be clear. Retirement only makes historical internal refs eligible for GC subject to other reachability guards; physical deletion is separate, and built-in v1 historical internal-ref retention is `KEEP`. Durable logical/audit history remains independent, while verification-evidence retention remains open under 30.28.

Integrated by ADR-054, amendments to ADR-014/021/039/042/046/049/053, the External Control Plane contract, main lifecycle/invariants/state-space/backlog sections, backlog closure of 30.24, and the v23 global audit.

## ADR-055 integration

Decision: backlog 30.25 is closed. Cross-repository `PARTIALLY_PROMOTED` is ordinary nonterminal progress; only non-nominal semantic disposition creates one durable exact-generation `CrossRepositorySettlementDemand`. The External Control Plane/Development System chooses roll-forward versus compensation, while every Git/provider effect remains forward-only and independently observed/adopted. Normal terminal settlement is `ALL_PROMOTED`; explicit `COMPENSATED` requires semantic compensation completion plus all declared forward effects. Stable ADR-049 logical submissions now support sequential PublicationEpisodes so a later exact state can open a new provider PR after an earlier episode is terminal without changing `submission_id`. The pass also retroactively enriches `EXTERNAL-CONTROL-PLANE-CONTRACT.md` with accepted ADR-022/024/026/032/036 boundaries that had remained scattered.

Integrated by ADR-055, amendments to ADR-014/022/024/026/032/036/039/042/049/053/054, the External Control Plane contract, main §§2/22/30/33/invariants, backlog closure of 30.25, and the v24 global audit.


## ADR-056 integration

Decision: backlog 30.26 is closed. Brand-new repository creation stays entirely outside `ruu`. A coding agent/session/orchestrator may request a repository, but External Control Plane `RepositoryCreationPolicy` supplies authority and a Repository Provisioner executes/reconciles local/provider creation. V1 requires every new managed repository to be admitted with its configured target at a real exact bootstrap commit `B0`; unborn/null targets never enter ordinary ConvergenceUnit/ContributionUnit, policy-baseline, ancestry, verification, materialization, or DIRECT CAS+FF semantics.

Local repository creation and provider repository creation are separate: provider attachment may be eager or lazy and missing provider binding blocks only provider-sensitive progression. Provider/account/organization/namespace/visibility cannot be self-authorized by the agent; if provider creation is authorized and only visibility remains underdetermined, the safe built-in default is `PRIVATE`. Provisioning is durable/idempotent and adopts exact already-realized effects on retry; path/name collisions do not imply identity, unknown conflicts fail closed, and failure does not authorize destructive repository deletion.

Integrated by ADR-056, amendments to ADR-015/023/039, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, main §§4/7/30/invariants, backlog closure of 30.26, a repository-bootstrap Git smoke, and the v25 global audit.

## 57. State-dependent super-Git progression and external development verification

Decision: `ruu` is invoked when a Development System, agent, user, or orchestrator asks to progress existing managed Git state that it considers ready to cross its next Git boundary. The invocation is a demand signal, not a caller-authored stage command. `ruu` derives the legal transitions from durable workflow intent plus exact Git/provider/coordination state, policy/capability, and exact external development-validation evidence when required.

All semantic development-quality execution — tests, lint, typecheck, build, formatting, codegen/snapshots, security analysis, agentic review, flaky/external-service handling, retries/fixed points, compute scheduling, logs/artifacts/caches — belongs to the Development System. `ruu` retains only mechanical Git/convergence validation and exact evidence binding. If it synthesizes a new exact candidate that requires semantic validation, it preserves the candidate, emits `DevelopmentValidationDemand`, localizes the wait, and later resumes from matching external `DevelopmentValidationEvidence`.

Integrated by ADR-057, amendments to ADR-003/005/007/010/012/013/019/020/026/027/028/029/030/031/032/035/036/037/039/040/041/048/050/052/053/055, the main requirements, the External Control Plane contract, and backlog reclassification.

## 58. Preserve native Git equivalence and whole-editing-surface checkpoint intent

Decision: ADR-058 establishes a global native-Git equivalence invariant. `ruu` remains a governance/recovery overlay over ordinary Git rather than a proprietary Git dialect: successful mutations produce ordinary Git commits/trees/refs and coherent native index/worktree state that humans, agents, IDEs, providers, and scripts can inspect and subsequently manipulate with normal Git semantics. Native operability does not itself authorize bypass of managed governance; externally produced Git movement is still handled through exact observation/adoption, drift/reconciliation, policy/evidence, claims/CAS, and recovery rules.

ADR-058 also partially closes 30.27. A v1 checkpoint progression for one dirty transferable ContributionUnit has whole-editing-surface intent, no partial/path-selected managed checkpoint mode, and no authority derived from the caller's current staged/unstaged partition. The remaining 30.27 work is limited to canonical Git-relevant snapshot mechanics and exact pre-commit candidate identity: untracked/ignored state, structural index edge cases, submodules, symlink/file-mode normalization, empty/no-op behavior, and fingerprint construction. The minimal external evidence-binding contract remains 30.28.

Integrated by ADR-058, amendments to the main requirements §§2.7/8.5/22.1/30.12/30.27/invariants, the open-design backlog, and the v27 global audit.

## 59. Canonical whole-surface checkpoint tree and exact pre-commit identity

Decision: ADR-059 closes 30.27. Once a dirty ContributionUnit editing surface is exclusively claimed, `ruu` reconstructs the checkpoint candidate using native Git semantics from the exact authoritative parent `P` plus the complete observable Git-relevant editing surface, with a temporary canonical index rather than the caller's staging partition as the membership source. Tracked modifications/deletions and non-ignored untracked paths are included; ignored untracked paths are excluded.

Structural ambiguity fails closed: unmerged/in-progress Git operations, dirty or required-but-unknown submodules, and sparse/skip-worktree conditions that prevent full observation are not guessed into a checkpoint. Clean exact submodules use ordinary gitlinks; symlink/mode/filter/EOL/LFS details follow native Git object semantics. A candidate tree equal to the parent tree is a no-op, not an empty managed commit.

The exact pre-commit checkpoint-candidate Git-state identity is `(repository_id, git_object_format, parent_oid, tree_oid)` under a versioned canonical fingerprint. ContributionUnit identity is separate attribution/governance metadata, while development-gate profile/context/evidence remain the separate 30.28 authorization binding. After required exact evidence is accepted, the resulting ordinary Git commit must have exactly the candidate parent and tree.

Integrated by ADR-059, amendments to the main requirements §§2.7/8.5/22.1/26 invariants/30.12/30.27/33.10, closure of backlog 30.27, a canonical-checkpoint Git smoke, and the v28 global audit.


## ADR-060 — transition-local prerequisites replace generic development-validation evidence

ADR-060 closes backlog 30.28 as obsolete. `ruu` no longer consumes or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` gate. Development-quality validation remains external; each transition is governed by its own exact Git/managed/policy/provider prerequisites and only the narrow authoritative external facts genuinely owned outside Git. The broader exact-state/TOCTOU rules remain for transition-specific evidence/facts. This supersedes the generic validation-gate portions of ADR-010/029/030/057 and related downstream amendments without weakening provider/review/policy/CAS guards.

## ADR-061 — immutable pre-authoring PromotionTarget and HOW/WHERE separation

Decision: each ConvergenceUnit now has two explicitly distinct destination-related concepts. Its repository-local **ConvergenceBase** is the Git ref/state used for provisioning and downward synchronization during mutable authoring; its **PromotionTarget** is the immutable logical final destination `(target_repository_id, target_ref)`. The External Control Plane resolves and durably binds that PromotionTarget before the first managed write. Reusing a ConvergenceUnit requires exact target equality; a genuinely different destination requires a distinct ConvergenceUnit rather than retargeting historical authored work.

`EffectivePromotionPolicy` therefore answers **how** the current exact state may reach the already-bound target, not **where** it should land. Policy may authorize DIRECT/PR, provider/governance mechanics, rewrite/review/queue constraints, and publication surfaces, while SAME_REPOSITORY versus CROSS_REPOSITORY is derived from authoritative source repository identity plus the immutable PromotionTarget. Policy/provider drift may block or change mechanics but never substitute another target. Current target OID/governance facts remain dynamically revalidated under the existing ancestry, policy-currentness, stack, and exact-old CAS rules.

Because ADR-047 projects exactly one PromotionUnit per source repository, same-source members of one PromotionGroup must have one coherent PromotionTarget. Conflicting immutable targets yield `TARGET_INCOHERENT_PROMOTION_GROUP`; `ruu` neither chooses one nor silently splits the group by target.

Integrated by ADR-061, amendments to ADR-006/015/023/026/039/043/044/045/046/047/049/050/052/056, the External Control Plane contract, main ConvergenceUnit/policy/provisioning/promotion/invariant/state-space sections, closure of 30.40, and the v30 global audit. The same pass also removes residual current-spec generic development-validation wait/evidence wording left behind after ADR-060.

## ADR-062 — route-independent promotion and provider submissions as projections

Decision: the prior current vocabulary `promotion_mode = DIRECT | PR` gave the provider Pull Request too much semantic weight. Promotion now has one meaning: realize one exact promotion candidate in its already-bound immutable `PromotionTarget`. Policy chooses only the **target realization route**:

```text
DIRECT_TARGET_ADVANCE
PROVIDER_SUBMISSION
```

`ProviderSubmission` / ADR-049 `Submission` + ADR-055 `PublicationEpisode` is the generic core abstraction. GitHub Pull Requests and GitLab Merge Requests are provider-adapter projections. A provider submission does not define Work, Candidate, development Evidence, semantic Finding, or Authorization; it exists only when the provider/governance route needs an external representation of the exact candidate.

On the provider-submission route, direct target-ref mutation by the Git ref engine remains forbidden. However, once the exact provider target-integration operation is REQUIRED, contextually SUPPORTED, policy AUTHORIZED, and all current prerequisites hold, `ruu` progresses that provider finalization automatically (queue entry, enable auto-merge, merge/finalization operation, etc.). There is no generic manual-Merge-click ceremony. If governance genuinely requires a distinct human finalizer, that becomes an explicit unsatisfied authority/prerequisite and the obligation waits locally.

ADR-062 also closes backlog 30.36: `REVIEW_NOT_REQUESTED` early/draft publication is allowed only when explicit current authority/need exists. If neither that authority nor `REVIEW_REQUESTED` exists, no provider submission is created merely to manufacture a PR object.

Integrated by ADR-062, amendments/current-reading rules for ADR-018/021/026/027/032/043/044/049/050/051/052/053/055/061, the main policy/lifecycle/state model, the External Control Plane contract, backlog closure of 30.36, and the v31 global audit.

## ADR-063 — semantic review findings and backlog stay outside Ruu

Decision: semantic review findings are Development System objects, not provider-submission lifecycle objects. External review governance may adjudicate them as `FIX_NOW`, `DEFER`, `ACCEPT`, or `REJECT` (or equivalent external states). `DEFER` should normally project to a tracker/backlog object such as a GitHub Issue, preserving provenance sufficient for later revalidation; it must not keep a stale PR/provider submission alive merely as a reminder.

When backlog work is later re-injected, the Development System first revalidates the finding against current code. `ruu` does not interpret review prose, create/prioritize Issues, or schedule future coding work.

The existing ADR-053 `CHANGES_REQUESTED` path remains deliberately narrower: an authoritative **blocking provider-governance state** creates a durable exact-generation ReviewCorrectionDemand. Nonblocking comments/suggestions do not automatically reopen ConvergenceUnits or block promotion. An external `DEFER` cannot bypass provider governance that is actually still blocking.

Integrated by ADR-063, amendments/current-reading rules for ADR-032/053/055/057/060, the main review/backlog boundary, the External Control Plane contract, and the v31 global audit.

## 64. Bind pre-commit semantic readiness by frozen mutation handoff

Decision: ADR-064 preserves the agent-native preference for tests/lint/typecheck/build/semantic review before checkpoint while keeping all such semantic validation outside `ruu`. The Development System's decision that the current dirty surface may cross the checkpoint boundary is represented by durable mutation-authority transferability, not by a `DevelopmentValidationEvidence` certificate.

Once `TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL` is current for that checkpoint offer, no external writer may mutate the ContributionUnit editing surface. Semantic authoring can resume only after legitimate revocation/reacquisition before claim, or after a current `ruu` claim/effect reaches safe release/recovery. `ruu` then acquires the exclusive claim, constructs the ADR-059 exact whole-surface candidate `(P,T)`, revalidates the same assumptions under that claim, and commits only `K` with `parent(K)=P` and `tree(K)=T`.

This establishes exact pre-commit identity by immobility across the handoff rather than by importing test/review semantics. Provider CI remains a separate downstream recertification/governance layer.

Integrated by ADR-064, amendments/current-reading rules for ADR-033/057/058/059/060, the main mutation/checkpoint/audit sections and invariants, `EXTERNAL-CONTROL-PLANE-CONTRACT.md`, backlog closure wording, and the v32 global audit.

## 65. Prove final promotion realization by native Git ancestry or exact provider-result binding

Decision: ADR-065 closes backlog 30.34. `PromotionUnit PROMOTED` now requires a durable exact `PromotionRealizationProof` for candidate `C` and immutable target `T`; provider `MERGED` / `PROVIDER_FINALIZED` alone is never terminal proof.

The proof is hierarchical. Fresh authoritative target observation `O == C` or `C ancestor-of O` is sufficient native Git proof for either DIRECT or provider-mediated history-preserving integration. When provider rewriting destroys candidate ancestry, the provider adapter must bind the exact submitted revision `C` for the exact logical submission/PublicationEpisode and target to an exact final result OID `R`; `ruu` then independently observes Git and requires `O == R` or `R ancestor-of O`. Target advancement after finalization is therefore harmless, while unknown/mismatched revision/result or absent `R` fails closed as unproven.

The provider is accepted as the bounded authority for the transformation it was authorized to perform. `ruu` does not reimplement squash/rebase/queue semantics and does not require universal diff/patch/program-equivalence between `C` and `R`; such comparisons may only enrich audit/diagnostics. Queue synthetic commits are not final proof unless they are the exact final `R`. Observation/adoption remains crash-safe/idempotent under ADR-042, and a later force rewrite after durable adoption is a new drift event rather than retroactive erasure of the historical promotion fact.

Integrated by ADR-065, amendments/current-reading rules for ADR-029/042/051/052/054/055/057/062, main §§28.11/30.34/33.31 and invariants 148..151, the External Control Plane contract, backlog closure of 30.34, and the v33 global audit.

## 66. Bind promotion success to route-conformant C→H→R→O chains

Decision: ADR-066 corrects ADR-065 after hostile review. Promotion success is now target realization **plus route conformance**. DIRECT keeps native exact/ancestry target proof and does not require `ruu` process attribution, preserving ordinary Git use by users/agents. PROVIDER_SUBMISSION requires an exact `SubmissionProjectionProof(C→H)`, exact provider finalization `H→R`, and fresh authoritative Git proof `R→O`; candidate ancestry cannot bypass provider governance. ADR-050 restack is therefore first-class in the proof because `C != H` may legitimately hold.

Recovery distinguishes historical effect commitment from future mutation authority. Old policy may justify adoption of an effect proven committed while that authorization applied, but every action capable of newly causing/re-causing the effect requires freshly current policy. Provider commitment is durable provider acceptance of exact `H/T` finalization; DIRECT commitment is the direct target mutation itself. `PROMOTED` remains a historical completion fact and does not silently introduce perpetual terminal target monitoring.

## 67. Terminalize obsolete PromotionUnits by current-resolution supersession

Decision: ADR-067 reuses ADR-046/047's existing mutable **current resolution mapping** over immutable PromotionGroups and immutable content-addressed PromotionUnits. When `(G,Repo)` changes from `P0` to `P1`, the exact `P0.superseded_by=P1` relation is recorded. An unpromoted old unit becomes terminal `SUPERSEDED` only when no unresolved committed/uncertain external effect or recovery obligation can still realize it. A previously promoted old snapshot remains `PROMOTED`; an in-flight old effect remains recovery-visible until exact observation decides `PROMOTED` versus `SUPERSEDED`.

PromotionUnit `ABANDONED` is removed as vague v1 lifecycle wording. This does not create group-level silent abandonment; ADR-055 forward settlement remains unchanged.


## 2026-09-07 — ADR-068 / backlog 30.41 closed

Decision: ordinary authoring branch/ref/worktree deletion by a user or agent remains ordinary Git artifact management and has no hidden `ruu` lifecycle semantics. It does not itself close a ContributionUnit, put a ConvergenceUnit into `ABANDONING`, or cancel a PromotionGroup.

Once immutable PromotionGroup `G` has been declared, withdrawal of that still-unrealized ship is a group-scoped semantic decision: the External Control Plane explicitly supplies current cancellation intent, and `ruu` may adopt terminal `G=CANCELLED` only after zero realized group promotion effects and zero unresolved committed/uncertain or otherwise still-realizing managed effects/surfaces are established. Any realized partial cross-repository state remains under ADR-055 forward settlement and cannot be cancelled.

Changing desired ship membership is represented as cancel-old + declare-new immutable group, never mutation of historical membership. `ABANDONING` is consequently a mechanically gated ConvergenceUnit lineage-disposition state after applicable higher-level terminal dispositions, not a meaning inferred from `git branch -D`. This closes backlog 30.41 without requiring normal Git mutation to pass through `ruu`.


## 2026-09-07 — Hostile-audit H4 explicitly ratified (no new ADR)

Decision: the existing ADR-066 / Invariant 154 semantics are explicitly confirmed. `PromotionUnit PROMOTED` is a terminal historical fact meaning that the exact promotion obligation was correctly realized and durably adopted at least once. A later force rewrite, target divergence, or removal of the realized result does not reopen, demote, or otherwise mutate that historical PromotionUnit state. If later target drift is independently discovered, it is a distinct new integrity/reconciliation fact under whatever higher-level policy applies. V1 therefore does not permanently resweep terminal PromotionUnits merely to prove ongoing target inclusion.

At the time of this H4 ratification, no new ADR was created because the decision merely reaffirmed ADR-066 semantics. A later, unrelated architecture decision is now numbered ADR-069. State-space audit v36 added the H4 coverage.


## 2026-09-07 — ADR-069 / hostile backlog 30.42 and 30.43 closed

Decision: ordinary new implementation work is grouped by the **work-bearing logical `ruu` invocation** that closes the current ContributionUnit cohort. The invocation has a durable idempotent `invocation_id` and sealed ContributionUnit handoffs, distinct from the coalescible `ConvergenceDemand` and from any global `ReconcilerRun`. `ruu` derives the immutable ConvergenceUnit membership mechanically from the ContributionUnit bindings and creates one occurrence-bound PromotionGroup. Distinct invocations therefore remain distinct PromotionGroups even with identical member sets; the member-set hash becomes a fingerprint rather than occurrence identity.

PromotionGroup exact resolution is now **group-local**. Later unrelated ordinary authoring may advance the same live ConvergenceUnit without refreshing an older group's exact binding. Same-group review/reconciliation continuation requires explicit `REVISE_EXISTING_GROUP(G, authority_ref)` authority, starts from the exact reviewed/group state rather than blindly from the live tip, and preserves untouched member bindings. Terminal PromotionGroups freeze their exact resolution.

ADR-050 remains the descendant mechanism: a clean predecessor correction restacks/reprojects a child's immutable owned effect without automatically rewriting the child group's internal state; transplant conflict emits group-bound reconciliation authority before any authored child revision. ADR-067 `SUPERSEDED` is correspondingly limited to legitimate newer resolutions of the same nonterminal PromotionGroup.

Integrated through ADR-069 amendments to ADR-010/011/015/023/037/039/041/046/047/050/053/054/064/067, the consolidated spec, External Control Plane contract, backlog closures 30.42/30.43, `STATE-SPACE-AUDIT-v37`, and a concrete group-local correction + descendant restack smoke.


## 2026-09-07 — ADR-070 / governing product intent made explicit

Decision: the user-facing reason for `ruu` is now normative architecture rather than an implication scattered across lower-level ADRs. A user may run several coding sessions concurrently, from any already-managed repository in the coordination domain. Sessions may touch one or many repositories and may overlap ConvergenceUnits/files. When one session's current block is ready, the ordinary interaction is simply `ruu`; the user is not required to serialize sessions, enumerate repositories, choose PromotionGroups, declare dependency/stack topology, manually order invocations, or repair routine stale bases merely because other managed sessions advanced concurrently.

CWD remains discovery/entry context rather than semantic scope. Work-bearing invocation identity/cohort is supplied behind the user-facing action by the Development System under ADR-069, while the resulting demand still drives the global fixed-point sweep. Mechanically resolvable staleness/collisions are internal convergence work; irreducible semantic conflict or missing external authority is localized as an exact obligation rather than guessed through. Hands-off concurrency does not authorize mutation of producer-owned active worktrees; ADR-009/033/064 isolation and mutation-authority rules remain controlling. Native Git remains ordinary under ADR-058/068.

ADR-070 governs interpretation of prior technical ADRs. If an earlier clause admits several readings, the product-conformant reading is required; a direct conflict is superseded only to the minimum extent necessary. Any future intentional change to this product promise must explicitly `Amends: ADR-070`, name the user-visible tradeoff, and update §0 `Product intent` in the consolidated spec in the same decision.

Integrated by adding normative §0 to `RUU-SPEC.md` / its legacy byte-identical alias, ADR-070, an ADR-070 product-intent hostile audit, the External Control Plane conformance note, README entry-point changes, and package verification. No new Git/state-machine transition dimension is introduced; the current finite technical audit remains v37 through ADR-069 and is re-run under the ADR-070 package pass.


## ADR-070 product-definition refinement — 2026-09-07

ADR-070 and the governing `Product intent` section were refined to state the architectural center of gravity explicitly: `ruu` is Git-based version control redesigned for agentic software development. The hands-off concurrent invoke-anywhere experience is a defining consequence of that model. Remote-hosting/provider publication workflows (PRs, stacks, merge queues, protected-target/provider APIs) are first-class extended features projected from core exact Git/version state, not the source of product identity or core convergence truth. No new ADR number was introduced because this refines the same governing product-intent decision rather than adding an independent decision.


## 2026-09-08 — ADR-071 — current-disposition causal fence + native managed-branch abandonment

Accepted after product-level review of backlog 30.44/30.45. The key correction is that the Development System may simply be a human or agent using Git, so ordinary abandonment must not require a second PromotionGroup RPC.

Integrated decisions:

```text
Reconciliation may recover knowledge without recovering authority.

Before any managed effect capable of newly realizing a PromotionGroup projection:
  acquire current causal authorization fence
  revalidate current semantic disposition
  cause/commit only an effect authorized by that disposition

CANCEL / COMPENSATE linearized first
  → old incompatible proven-absent attempt cannot retry

pre-existing causally committed effect
  → recover / observe / adopt; do not rewrite history
```

ADR-068 deletion neutrality is narrowed:

```text
unmanaged branch deletion / worktree deletion
  → ordinary Git

currently bound managed authoring ref deleted through Git
  → reference-transaction prepared write-ahead capture
  → successful Git transaction commit
  → durable authoring abandonment
  → CANCEL disposition for still-unrealized associated ship
```

`reference-transaction` prepared persistence is correctness-critical: failure aborts the managed ref deletion rather than losing the lifecycle event. `committed|aborted` settle the prepared record; crash recovery uses exact ref state. The semantic point is the Git transaction commit, not the prepare record. Git >= 2.28 is the current v1 minimum.

Provider surfaces already created do not retain residual authority. `CHANGES_REQUESTED` remains correction work; PR closed/rejected without merge is a non-realizing publication fact, not automatic abandonment. Cross-system external ordering not provable from authoritative causal evidence remains fail-closed; independent timestamps are not treated as causal proof.

Backlog 30.44/30.45 closed. v38 verification closes 30.48. 30.46/30.47 remain open.

### Backlog discovery after ADR-071 — native Git observation plane

The ADR-071 `reference-transaction` abandonment mechanism revealed a broader possible architecture: selected Git-native hooks/transaction points may durably report correctness-relevant ref mutations performed outside the managed executor, while the reconciler remains the sole interpreter of managed semantics. This is recorded as **OPEN-DESIGN-BACKLOG 30.49** only; no general hook-observation architecture is ratified yet. Per review scheduling, 30.49 is deferred until 30.46 and 30.47 are resolved.


## 2026-09-08 — ADR-072 — host run-lock handles are non-inheritable

Accepted to close backlog 30.46. ADR-042's process-lifetime OS host fence is now made subprocess-safe: the run-lock descriptor/handle belongs exclusively to the top-level `ruu` executor and MUST NOT survive into executed child processes. POSIX implementations use atomic `O_CLOEXEC` where available or a race-safe `FD_CLOEXEC` fallback before any subprocess can spawn; non-POSIX platforms use the equivalent non-inheritable handle. A surviving Git/provider/helper descendant must never keep the physical host fence alive after the owning executor dies.

No heartbeat/TTL takeover is introduced. The decision preserves the stronger ADR-042 equivalence between executor process lifetime and OS physical ownership. A concrete long-lived-child smoke is part of the package verification.

## 2026-09-08 — ADR-073 — Git worktrees remain the normative v1 authoring substrate

Accepted to close backlog 30.47. V1 does not generalize authoring to arbitrary prebuilt commit/tree/snapshot inputs. Every actively authored managed ContributionUnit is provisioned with its own dedicated Git worktree/ref surface before first managed write, then crosses the existing frozen mutation-authority handoff and exact whole-surface capture boundary.

This is deliberately a substrate decision rather than a redefinition of durable identity. A worktree is required while v1 authoring is active; after exact managed state is captured, later worktree disappearance does not erase ContributionUnit identity or checkpoints under ADR-038/071. Ordinary native Git commits made inside the managed worktree remain supported. Future sandbox-based authoring is left to a future ADR that must prove equivalent isolation, exact-base, authority/freeze, and deterministic-capture properties; no speculative generic authoring-ingress/adapter layer is introduced now.

Backlog 30.46/30.47 are closed. The remaining native-Git observation-plane investigation begins at 30.49.

## 2026-09-08 — backlog refinement after ADR-073 — decompose native Git observation-plane investigation

No architectural semantics are ratified by this refinement. The previously monolithic open item 30.49 is retained as the governing umbrella and decomposed so that independent decisions cannot be silently bundled into one ADR:

```text
30.49 observation-plane scope and invariant — umbrella
30.50 minimal correctness-relevant observation set
30.51 transactional capture vs exact-state rediscovery
30.52 provenance / replay / idempotency
30.53 hook ownership / installation / coexistence
30.54 observation persistence failure semantics
30.55 local native-Git / remote-provider boundary
```

The investigation order is intentionally state-machine-first: 30.50 determines what facts correctness actually requires before 30.51–30.54 choose mechanisms. Portability/minimum-Git-version evidence is a conformance consequence of the selected primitives rather than a separate design objective. ADR-070/ADR-058 remain governing: ordinary native Git use must not be replaced by a `ruu` command proxy.



## 2026-09-08 — ADR-074 — minimize native Git event observation to managed authoring-binding disposition

Accepted after hostile native-Git testing disproved ADR-071's direct `old managed ref -> zero == abandonment` classifier. A normal `git branch -m old new` may expose old-ref deletion before the full rename/rebind state is visible.

Ratified correction:

```text
currently bound managed authoring ref removed
→ reference-transaction prepared
→ AUTHORING_BINDING_TRANSITION_PREPARED

transaction aborts
→ no disposition change

transaction commits
→ AUTHORING_BINDING_DISPOSITION_UNRESOLVED
→ proven native rename/rebind → CONTINUATION
→ proven terminal deletion    → ABANDON → CANCEL when still unrealized
```

Continuation is never inferred from same OID/tree/ancestry, branch similarity, branch copy, or plain worktree HEAD switching. `git branch -c foo bar` followed by deletion of `foo` abandons the managed line bound to `foo`; `bar` remains an ordinary separate Git branch.

The state-machine sweep closes 30.50 with three planes: broad exact **state observation**, one currently ratified local **event-semantic** family (managed authoring-binding disposition), and a separate **observation-integrity** concern for continuous coverage. Internal refs, submission refs, targets, worktrees, HEAD, index/in-progress state, tags/stash/notes, and ordinary ref movement remain state-observed. `refs/replace/*`, `info/grafts`, and shallow boundaries are added to correctness-relevant ancestry state.

V1 authoring provisioning now guarantees a native reflog for the managed authoring ref before first managed write. A later `ruu` invocation may repair a missing reflog only when no unresolved transition requires lost historical evidence; reflog creation never reconstructs the past.

If native causal evidence is irretrievably insufficient, the ECP contract gains an exceptional expected-old/binding-generation guarded `AuthoringBindingRecovery(REBIND(new_ref) | ABANDON)`. This supplies logical recovery authority only; Ruu independently revalidates actual Git/ref/worktree/OID state and mutation authority.

Backlog 30.50 is closed. 30.49 remains the umbrella; 30.51–30.55 remain open for proof strength, provenance/idempotency, hook coexistence/coverage, persistence failure, and local/remote composition.


## 2026-09-08 — ADR-075 — pre-linearization native-ref witnesses and exact-state rediscovery

Accepted to close backlog 30.51. Observation strength is now deliberately asymmetric: only native mutations capable of terminating/replacing the currently bound managed authoring ref require correctness-critical pre-linearization durable capture. Every other currently identified Git/remote/provider fact is reconstructed from exact current state; additional notifications are best-effort wakeups/diagnostics.

The native-ref abstraction is capability-based rather than backend-named. A conforming adapter must expose every binding-ending deletion/replacement/forced-rename overwrite before causal linearization, establish the exact preimage, distinguish terminal removal from native rename transport, durably emit a normalized witness, and permit veto/causal serialization on ambiguity. The adapter reports Git/backend facts only; the core combines them with managed binding generation and derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`. `UNKNOWN` cannot silently commit.

`ABANDON` and `CONTINUATION` are independently positive proofs. `!ContinuationProof` never implies abandonment. Managed `ReflogBaselineV1` is `ENTRY(anchor_entry_fingerprint) | EMPTY_PRESENT`; fingerprints refer to logical reflog entries, never physical reflog/reftable files or whole-history hashes. Opaque backend witness digests are non-normative.

Concrete Git 2.47.3 hostile testing demonstrates a candidate conforming `files` path: `branch -m` moves the managed reflog evidence into native rename transport before the source-ref prepared callback, while terminal delete leaves it attached to the old ref; forced `-M` over an existing destination exposes separate source and destination removals. The tested stock `reftable` path allows `branch -m/-M` to complete with zero `reference-transaction` callbacks, so it is not currently conforming for live managed authoring. This is not a permanent reftable prohibition: any future Git/backend adapter that satisfies the same pre-linearization capability contract becomes admissible without core changes.

Backlog 30.51 is closed. 30.49 remains the umbrella; 30.52–30.55 remain open.


## 2026-09-08 — ADR-076 — separate native witness provenance from managed effect identity and make semantic adoption exactly-once

Accepted to close backlog 30.52. ADR-042's `Operation → Attempt → Observation → Adoption` journal remains a journal of recoverable effects owned/caused by `ruu`; an ADR-075 native Git witness/preparation is causal evidence and never becomes a synthetic Operation merely because it affects managed state.

When a managed Attempt launches the physical Git operation, a witness may retain trusted optional `originating_attempt_id` correlation. That provenance is explanatory only: it never authorizes current mutation/adoption, and unattributed native Git remains valid evidence. Human/agent/IDE actor identity is not inferred for correctness.

The exactly-once boundary is moved explicitly to logical managed state:

```text
operation_id
→ at most one Adoption or mutually-exclusive terminal Closure

current binding_generation
→ at most one unresolved correctness-critical cessation/rebind preparation
→ at most one committed disposition out of that generation
```

Duplicate/replayed native deliveries and outcomes are idempotent. The native-ref adapter must correlate the same active pre-linearization occurrence sufficiently to reuse one effective preparation/permit-veto decision, but core semantics require no globally unique permanent Git transaction ID. Distinct later transactions may have identical transition content, so `(old,new,ref)` fingerprints are evidence rather than universal identity.

Lost outcome callbacks recover from durable PREPARED evidence plus exact state/coverage when proof is sufficient and otherwise remain unresolved. Repeated scans may resolve existing evidence but never manufacture missing `TERMINAL_REMOVAL_PREPARED` / `RENAME_CARRY_PREPARED` history. Wakeups remain non-semantic, coalescible, replayable, reorderable and loss-tolerant.

Backlog 30.52 is closed. 30.49 remains the umbrella; 30.53–30.55 remain open.

## 2026-09-08 — ADR-077 — attested repository-common observer coverage without foreign-hook takeover

Accepted to close backlog 30.53. ADR-075's pre-linearization native-ref capability is now given an explicit installation/admission boundary: live managed authoring begins only after a repository-common observer binding for the admitted mutation-engine/adapter profile is functionally attested `ACTIVE`.

The observer is shared repository infrastructure, not session ownership. `ruu` owns only exact registrations/artifacts it created or previously adopted and mutates them under expected-state/CAS. It does not overwrite `core.hooksPath`, foreign traditional/configured hooks, whole hookdirs, or arbitrary third-party dispatchers. Composition must use a Git-native or explicitly supported composition surface. Git 2.54+ configured multiple hooks are the preferred modern path but are not made a universal V1 version minimum; a legacy traditional slot may be used only when absent/already exactly owned or via a demonstrated composition adapter.

V1 guarantees the Git core mutation-engine family rather than every implementation capable of reading/writing a Git repository. Tools that delegate relevant ref mutation to a conforming engine inherit conformance; libgit2/JGit/custom/direct ref writers require separately proven adapters. A writer that bypasses the admitted pre-linearization path can remain physically possible, but an unwitnessed change to a currently managed binding is an observation-integrity failure and is never reclassified from final topology alone.

Clone/recreation/reactivation and relevant engine/config/backend/adapter changes require re-establishment/re-attestation. Continuous trust is represented by coverage epochs; repair opens a new epoch and cannot retroactively erase a gap. The concrete persistence/retry consequences of failure/gaps remain 30.54.

Backlog 30.53 is closed. 30.49 remains the umbrella; 30.54–30.55 remain open.


## 2026-09-08 — ADR-078 — zero-preflight coding-harness integration as governing product intent

Accepted to make explicit that the ordinary user installs Ruu once, launches a supported coding harness, asks the agent to implement, and later invokes `ruu` when a checkpoint/convergence boundary is desired. Required CU/ConvergenceUnit/ref/worktree/observer/binding/handoff plumbing must be triggered automatically before first managed write and remain invisible to the user.

ADR-023 is clarified as a phase/authority separation, not a packaging requirement: the later convergence invocation still cannot retroactively provision missing isolation, but a Ruu-supplied harness integration may implement the pre-edit provisioner/External-Control-Plane role. Semantic authority remains outside the convergence engine.

No explicit ordinary `start`, `create-cu`, `provision`, per-repository observer-install workflow, internal-ID reconstruction, or separately operated control-plane product is product-conformant for supported harnesses.

30.54–30.55 remain the next open observation-plane decisions; ADR-078 is cross-cutting product clarification rather than a new observation backlog node.

## 2026-09-08 — ADR-079: minimize native Git rejection and serialize initial managed binding admission

Accepted to close 30.54. Only cessation/replacement candidates that cannot be authoritatively proven safe, or current managed-binding transitions whose complete preparation batch cannot be made crash-durable before linearization, may be vetoed for observation correctness. Outcome callbacks after durable PREPARED and all wakeup/log/telemetry delivery are recoverable/advisory and never rollback authority.

A repository-common conservative `ManagedRefProtectionFilter` is introduced solely as negative acceleration. It never stores binding-generation/currentness authority; stale positives are safe, while missing/corrupt/untrusted filter state disables negative fast-path decisions and falls back to the CoordinationStore. Filter degradation is distinct from observer coverage loss.

Initial managed binding admission is now explicitly serialized with native ref mutation by a capability-based `RefAdmissionBarrier`. Candidate branch/worktree creation remains ordinary provisioning state; the authoritative binding becomes CURRENT while exact native exclusion is held, exact worktree/ref topology is revalidated, then the barrier is released and authoring authority is handed to the producer. The current Git-core/files candidate uses a prepared exact no-op `update-ref` transaction and treats `old_oid == new_oid` as semantically empty. Live lock order is Git/native exclusion before CoordinationStore, never the inverse.

30.55 is now the only remaining subproblem under the 30.49 native-observation umbrella.

## 2026-09-08 — ADR-080 / backlog 30.55 + 30.49 closure

Accepted source-domain observation boundary:

```text
LOCAL_GIT
→ local exact state + narrow managed-binding causal observer

REMOTE_GIT
→ current authoritative remote refs/OIDs + exact-preconditioned remote mutation/re-observation

PROVIDER
→ optional provider-owned workflow/governance/finalization facts
```

Local remote-tracking refs are caches, not remote authority. Bare Git remotes are first-class and provider-free routes require no forge API/webhook. Webhook delivery is non-complete/reorderable transport: authenticated payloads may add positive provider-scoped historical evidence when adapter semantics are demonstrated, but absence never proves non-occurrence, delivery identity is not semantic identity, and cross-source causality is never inferred from wall clocks. Remote publication artifact deletion/rename never invokes local managed-authoring `CONTINUATION | ABANDON`. ADR-080 closes 30.55 and the 30.49 umbrella.

## 2026-11-03 — ADR-081 — exact authoring dependencies before promotion

Accepted to close 30.56. The Development System may explicitly select a stable repository-local source ContributionUnit and exact native commit for a consumer before the source has any Ruu checkpoint or PromotionGroup. ContributionUnit remains the sole v1 authoring-occurrence identity; no separate WorkOccurrence object is introduced.

```text
source α creates native commit A
consumer β adopts α@A before first write
β authors B and may invoke Ruu first
```

Ruu proves exact source lineage, durably linearizes semantic selection in TX-A, creates a REQUIRED operation-owned recovery anchor before dependency adoption, revalidates source generation/disposition in TX-B, and keeps `A` immutable/reachable through source advancement, reset/amend/ref deletion, restart, and Git GC. A qualifying source handoff between TX-A and TX-B may be adopted directly as resolved rather than stranding a raw dependency. Dirty producer state is never a version and is never silently snapshot-committed. Native commit creation remains exact-state rediscovery; a clean native tip becomes a managed checkpoint only at a frozen work-bearing handoff.

A raw dependency blocks unauthorized realization rather than otherwise legal authoring/checkpointing/convergence. Current target containment may satisfy it without a fake parent. A qualifying handoff accepted after durable selection may CAS-resolve it to `(PromotionGroup, source repository)` only when the source's own frozen pre-sync checkpoint contains `A`, group-local state incorporates that checkpoint, and source/consumer immutable PromotionTargets are exactly equal. This prevents aggregate lineage from laundering `A` back through the consumer. The relation retains consumed `A`; if parent current exact state is `K`, ADR-050 uses `Restack(A,B,K)`. Same-group dependencies create no provider edge. Source abandonment without valid realization creates reconciliation and never transfers authority to the consumer.

The accompanying global hostile audit records two HIGH engineering follow-ups rather than inventing semantics: [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1) for more than one independently unsatisfied predecessor over a one-base provider model, and [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2) for late dependency discovery/refoundation after consumer authoring has begun. They are tracked in the GitHub Project **Ruu Engineering**; accepted repository semantics remain fail-closed until amended by a later ADR.
