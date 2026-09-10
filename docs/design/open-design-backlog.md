# Ruu — Open Design Backlog

This backlog records design questions raised during the 2026-09-07/08 architecture review and their closure status. Accepted semantics live in the main requirements document, ADRs, and the normative `EXTERNAL-CONTROL-PLANE-CONTRACT.md`. **ADR-070 / §0 Product intent governs how every open item is resolved: a technically coherent solution is not acceptable if it re-exports avoidable multi-session/repository/concurrency orchestration to the user without explicitly amending ADR-070.** ADR-068 closed the preceding item 30.41. A subsequent hostile falsification pass opened 30.42–30.48; ADR-069 closed 30.42 and 30.43, ADR-071 closed 30.44 and 30.45, v38 closed 30.48, ADR-072 closes 30.46, ADR-073 closes 30.47, and ADR-074 closes 30.50 while correcting ADR-071 native managed-binding classification. The native-Git observation-plane investigation is now closed: ADR-074 closes 30.50, ADR-075 closes 30.51, ADR-076 closes 30.52, ADR-077 closes 30.53, ADR-079 closes 30.54, and ADR-080 closes 30.55 plus umbrella 30.49. ADR-081 closes 30.56 for exact authoring dependencies before promotion. The ADR-081 repository-wide hostile audit opens 30.57 and 30.58 as HIGH unratified decisions: multi-unsatisfied-predecessor publication and late consumer refoundation.

## A. Checkpoint candidate canonical snapshot / identity — closed by ADR-059 (30.27)

ADR-058 fixes whole-editing-surface intent, no v1 partial/path-selected checkpoint mode, staging non-authority, and native-Git equivalence. ADR-059 closes the remaining canonical Git snapshot/identity mechanics:

```text
exact parent P + complete observable editing surface
→ temporary native Git index seeded from P
→ whole-surface native Git update / write-tree
→ exact tree T
→ candidate identity (repository_id, git_object_format, P, T)
```

Tracked modifications/deletions and non-ignored untracked paths are included; ignored untracked paths are excluded; staging/intent-to-add is not selection authority; unmerged/in-progress Git state, dirty/unknown submodules, and incomplete sparse observability block; native Git handles symlink/mode/filter details; `T == tree(P)` is a no-op rather than an empty managed commit.

ADR-060 removes any generic development-validation binding from `ruu`; 30.28 is closed as obsolete. ADR-064 subsequently makes the pre-commit identity bridge explicit: semantic readiness is external, transferability freezes the editing surface against external writes, and `ruu` commits only the exact ADR-059 candidate constructed/revalidated under its exclusive claim.

## B. Generic DevelopmentValidationEvidence contract — closed as obsolete by ADR-060 (30.28)

ADR-060 removes the generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` protocol rather than defining a smaller schema.

`ruu` no longer asks whether development validation is missing. Each transition uses only its own exact Git/managed/policy/provider prerequisites plus the narrow authoritative external fact genuinely owned outside Git when that transition requires one.

Development-quality validation remains fully external and may influence when `/go`, another harness, a script, IDE, agent, or human offers work, changes lifecycle state, or establishes review/governance intent.

## C. Development verification execution — closed/outside Ruu by ADR-057

The Development System owns:

```text
tests / lint / typecheck / build
formatting / codegen / snapshots / lockfiles
security analysis / agentic review
verifier-induced mutation/fixed-point/cycles/cleanup
flaky/infrastructure classification
external-service tests
CPU/RAM/worker scheduling
local/remote validation execution
logs/artifacts/caches
```

These are not `ruu` backlog items anymore (former 30.29, 30.30, 30.31, 30.35, 30.37 and the verifier-orchestration part of 30.27/30.38).

## D. Submission-author / ship-ready process — execution outside Ruu

`REVIEW_REQUESTED` retains its exact-revision semantic assertion under ADR-032.

ADR-057 closes former 30.32 as a core design question: the Development System / repository governance decides what tests, independent reviews, docs checks, architecture checks, security checks, etc. justify the assertion. `ruu` consumes only exact-revision-bound intent/evidence required by current policy.

## E. Provider CI execution policy — outside Ruu

ADR-057 closes former 30.33 as a core design question. Repository/provider governance chooses CI matrices, provider-only E2E, rebuilds, security analysis, deployment previews, coverage, and similar execution policy.

`ruu` still observes exact provider check/review/queue state and uses current provider/promotion policy as an authorization input.

## F. Final target integration / route-conformant realization proof — closed by ADR-065/066 (30.34)

ADR-066 corrects ADR-065's final target-realization proof so that terminal success includes both exact target realization and conformance to the authoritative route.

```text
DIRECT_TARGET_ADVANCE
+ C == observed target O or C ancestor-of O
+ DIRECT compatible with that realization
→ direct realization proof
→ user/agent direct Git progress may satisfy it; Ruu actor attribution is not required

PROVIDER_SUBMISSION
+ exact SubmissionProjectionProof C → H
+ exact ProviderFinalizationObservation H → R on T
+ fresh authoritative Git observation proves R == O or R ancestor-of O
→ provider-route realization proof
```

Candidate ancestry alone cannot bypass a required provider route. Provider `MERGED` / `FINALIZED` alone remains insufficient. ADR-050 restack may legitimately make `C != H`; provider trust begins at exact submitted `H`. No universal diff/patch/program-equivalence proof is required.

Recovery uses route-specific effect commitment. Old policy may justify adoption of an already committed historical effect but never a new causal mutation; indeterminate commitment timing across policy drift fails closed.

## G. REVIEW_NOT_REQUESTED policy fallback — closed by ADR-062 (30.36)

ADR-032 fixes the review-request intent semantics and ADR-057 externalizes the semantic review process. ADR-062 closes the remaining Git/policy fallback question by removing the assumption that every candidate needs a provider submission object.

```text
REVIEW_REQUESTED current
→ nominal provider-submission publication may proceed when its exact policy/provider prerequisites hold

explicit current authority/need for early provider projection
→ REVIEW_NOT_REQUESTED publication may proceed

neither established
→ no provider submission is created yet
```

There is therefore no implicit draft-PR fallback. Explicit authoritative governance always wins.

## H. Internal synthesized-state progression — closed by ADR-060

A deterministic clean internal merge/materialization/restack result does not wait on a generic validation handoff. It progresses when its transition-local exact Git/topology/claim/policy/provider prerequisites hold.

If semantic authoring is actually required, the existing exact transition-specific obligation (`RECONCILIATION_REQUIRED`, review correction, settlement continuation, policy contradiction, etc.) carries the handoff to the Development System. `ruu` still never runs tests or semantic review itself.

## I. Internal/team/external provider-submission contribution policy

No separate Git ontology is needed. Upstream contribution guidelines, DCO/signoff, PR templates, external CI, fork permissions, presentation/granularity rules, and human-process requirements are repository/provider governance inputs or Development System concerns.

`ruu` consumes their exact authoritative effects where they constrain Git/provider progression.

## J. Stacked provider-submission publication/review policy

Core stack identity/restack architecture is decided by ADR-049/ADR-050. Stack shape is derived from exact unsatisfied promotion dependencies rather than caller intent; restack is exact-state reprojection of immutable owned child state.

Remaining semantics that are truly provider/Git-facing (for example provider-observed review invalidation or queue ordering constraints) are handled as contextual provider facts/policy under ADR-051/ADR-043. Semantic reviewer workflow and review-agent strategy are external under ADR-057. Exceptional `REVIEW_NOT_REQUESTED` defaulting is closed by ADR-062: absent explicit early-publication authority/need, no provider projection is created.

**Submission/ref semantics are closed by ADR-049:** provider-facing submission refs are always distinct from internal refs; stable logical submission identity survives exact revisions; first publish/update uses exact absent/expected-old guards; naming is non-authoritative; physical cleanup is separated from durable audit retention.

**Derived stack/restack semantics are closed by ADR-050:** a stack is the provider representation of an exact dependency not yet satisfied by the target; no caller asks for stack shape. Restack is a versioned exact three-way state transplant from immutable owned `(old_base,candidate)` to the new predecessor/base. A newly produced exact restack head must satisfy the exact transition-local prerequisites of the revision/publication transition before submission adoption. Provider/local/external execution is an adapter choice subject to the same Git result contract.

**Provider capability differences/cross-repository applicability are closed architecturally by ADR-051:** they are exact contextual capability observations over core-defined semantic operations, not a provider-wide stack feature matrix.

## J1. Obsolete PromotionUnit lifecycle — closed by ADR-067

The existing immutable PromotionGroup current-resolution mechanism may replace one repository-local exact PromotionUnit `P0` with `P1` after legitimate ConvergenceUnit reauthoring. No new group-resolution semantic object is needed.

```text
old current (G,R) → P0
new current (G,R) → P1
```

The exact relation `P0.superseded_by = P1` is recorded. If `P0` is unpromoted and has no unresolved committed/uncertain external effect or recovery requirement, it terminalizes as `SUPERSEDED` and leaves the nonterminal PromotionUnit universe. A previously `PROMOTED` `P0` stays historically promoted. If an old external effect may still realize, `P0` becomes non-current and starts no new promotion mutations but remains recovery-visible until observation yields historical `PROMOTED` or safe `SUPERSEDED`.

Generic PromotionUnit `ABANDONED` is removed from v1; group-level partial settlement remains governed by ADR-055 and cannot silently disappear.

## K0. Semantic review findings / deferred backlog — outside Ruu by ADR-063

Agentic or human semantic findings are Development System objects. Their adjudication (`FIX_NOW`, `DEFER`, `ACCEPT`, `REJECT`, or an equivalent external vocabulary), issue/tracker projection, prioritization, and later revalidation are not `ruu` design questions.

A deferred finding should normally become a tracker/backlog object such as a GitHub Issue rather than a long-lived provider submission. It should preserve enough provenance to be revalidated against current code before future implementation. A current authoritative blocking provider `CHANGES_REQUESTED` state remains distinct and continues to create ADR-053 ReviewCorrectionDemand.

## K. ConvergenceUnit PromotionTarget ownership / retargeting — closed by ADR-061 (30.40)

Before first managed write, the External Control Plane resolves and durably binds each ConvergenceUnit to one immutable:

```text
PromotionTarget = (target_repository_id, target_ref)
```

This logical final destination is distinct from the repository-local ConvergenceBase used for internal synchronization. Reusing a ConvergenceUnit requires exact target equality; another intended destination requires a distinct ConvergenceUnit. `EffectivePromotionPolicy` answers **how** current exact state may reach that target (`DIRECT_TARGET_ADVANCE` / `PROVIDER_SUBMISSION` / provider mechanics), not **where** the work should land. SAME/CROSS repository relation is derived from source + target identity, and same-source PromotionGroup projection with conflicting target bindings fails closed rather than splitting or retargeting. Target OID/current governance remain dynamically revalidated.

## O. Merge / rebase / FF policy

Largely decided by ADR-016, ADR-017, ADR-026, ADR-028:

```text
internal contribution-unit/convergence-unit refs
→ append-only
→ FF or merge where matrix permits
→ never rebase/history-rewrite

contribution-unit → convergence unit
→ FF only

DIRECT_TARGET_ADVANCE target
→ descendant-only FF

PROVIDER_SUBMISSION target
→ read-only to direct Ruu ref mutation; provider-governed finalization may realize it

rewriteable submission ref
→ policy/provider-authorized exact revision only
→ dependency restack uses ADR-050 exact state transplant
→ exact expected-old protection
→ never rewrite internal source OIDs
```

Remaining work is implementation detail/recovery validation, not a major unresolved architectural choice.

---

## P. ContributionUnit → ConvergenceUnit progression and internal readiness

**Semantic decision fixed by ADR-037:**

```text
External Control Plane chooses/creates ConvergenceUnit membership

valid authoritative managed checkpoint
+ mechanically safe edge
→ earliest safe upward integration MUST be attempted

ConvergenceUnit membership OPEN
→ more ContributionUnits may still attach
→ ordinary convergence continues
→ READY_INTERNAL forbidden

ConvergenceUnit membership SEALED
+ all ContributionUnits CLOSED
+ every still-required exact managed checkpoint resolved
+ zero missing-managed-state/internal sync/integration/reconciliation/conflict/recovery obligations
+ internal fixed point
→ READY_INTERNAL(exact OID)
```

No separate ContributionUnit integration-release/readiness state exists. Experimental/alternative isolation uses a distinct ConvergenceUnit. ContributionUnit branch/ref/worktree presence or absence is not readiness by itself.

The concrete External Control Plane API/policy for choosing `create` versus `reuse` of a ConvergenceUnit is outside `ruu`.

# Existing specification questions — closure status

After ADR-068, the preceding review backlog had been closed. A subsequent hostile falsification pass opened **30.42–30.48** below. ADR-069 closes 30.42/30.43; ADR-071 closes 30.44/30.45; v38 closes 30.48; ADR-072 closes 30.46; ADR-073 closes 30.47. The native-Git observation-plane investigation is closed: ADR-074 closes 30.50, ADR-075 closes 30.51, ADR-076 closes 30.52, ADR-077 closes 30.53, ADR-079 closes 30.54, and ADR-080 closes 30.55 plus umbrella 30.49.

**Retired from this backlog by ADR-033/ADR-034/ADR-035/ADR-036/ADR-037/ADR-038:** external producer/runtime liveness, heartbeat/lease semantics, actor identity, runtime handoff mechanics, invocation-scope selection by caller/repository/age/active-set membership, ContributionUnit abandonment/disposition, and ContributionUnit branch/worktree cleanup semantics. `ruu` consumes a stable opaque repository-local `contribution_unit_id`, exact managed checkpoint state, the external mutation-access contract, and the externally authoritative `OPEN | CLOSED` lifecycle. A global producer identity is not part of the `ruu` model. `CLOSED` never reopens; later work uses a new contribution unit.

**Global sweep semantics are closed by ADR-036/ADR-060 and scheduling semantics by ADR-041:** every executed sweep that services outstanding convergence demand re-evaluates all known nonterminal managed obligations across ContributionUnit, ConvergenceUnit, PromotionUnit, publication, provider-submission/review/check/provider, merge-queue/finalization/update/restack, final target-integration proof, transition-specific external facts, recovery, and cleanup layers. No generic development-validation demand/evidence layer exists. Concurrent explicit triggers may coalesce; `ACTIVE_CONVERGENCE_SET` may exist only as a reconstructible acceleration index and cannot suppress an obligation.

**Contribution-to-convergence semantics are closed by ADR-037/ADR-038:** ConvergenceUnit creation/membership is externally authoritative; every valid managed ContributionUnit checkpoint converges upward at the earliest mechanically safe opportunity; experiments/alternatives use distinct ConvergenceUnits; ConvergenceUnit contribution membership is `OPEN | SEALED`; `READY_INTERNAL` is exact-state based; and ContributionUnit editing-artifact presence is not lifecycle/readiness.

**ContributionUnit artifact/continuity semantics are closed by ADR-038:** ContributionUnit lifecycle is `OPEN | CLOSED`; `ABANDONED`/`REMOVED` are not normative states; logical identity is independent of local/remote branch/ref/worktree existence; already-created exact managed checkpoints may continue from recoverable OIDs without the producer worktree; only a still-required exact OID that becomes unrecoverable creates localized recovery/data-loss state. User/agent/External-Control-Plane tooling owns branch/worktree/remote-ref lifecycle.

**External boundary consolidation is closed by ADR-039:** all normative upstream dependencies are consolidated in `EXTERNAL-CONTROL-PLANE-CONTRACT.md`. The External Control Plane is an abstract role, not a mandated component. Future external dependencies must map to that contract or amend it explicitly. Concrete questions subsequently closed by later ADRs are reflected below.

**Conflict/reconciliation and mutation-attribution semantics are closed by ADR-040/ADR-060:** deterministic clean reconciliation remains in `ruu`; authoring-required conflicts emit exact-state-bound `RECONCILIATION_REQUIRED` obligations to the external Development System, and authored results always re-enter current-state revalidation plus the exact transition-local Git/managed/policy/provider prerequisites of the transition they later attempt. Candidate ownership is scoped to the valid ContributionUnit mutation-authority boundary, not process identity; authority violations are integrity/staleness conditions. ADR-059 closes candidate membership/identity; generated-output cleanup/classification remains a Development System concern under ADR-057.

**Concurrent-trigger / single-executor semantics are closed by ADR-041:** v1 is single-host; simultaneous explicit invocations are coalescible convergence-demand signals rather than FIFO work items; at most one fenced top-level executor is authoritative; exact-invocation transferability is retired in favor of durable trigger-independent External Control Plane mutation-access state. Fine-grained claims remain for actual resources/internal parallelism/recovery.

**CoordinationStore / top-level run / recoverable-effect semantics are closed by ADR-042:** v1 uses host-local SQLite, a current-state ConvergenceEngine/reconciler, a process-lifetime OS exclusive lock for physical run ownership, monotonic `run_generation + run_token` fencing, a race-safe `ACTIVE → IDLE` release handshake, and an append-only `Operation → Attempt → Observation → Adoption` success path. No SQLite transaction spans an external effect; live-but-hung takeover is not automatic; normal long work is bounded; repository identity is opaque/stable across locator relocation; correctness-critical recovery resources become `GC_ELIGIBLE` before best-effort cleanup.

**Promotion-policy authority/composition semantics are closed by ADR-043/061:** the effective policy is compiled for an already-bound immutable PromotionTarget from provider capabilities/current facts, provider/organization governance constraints, and trusted repo-committed policy without a generic precedence ladder. Explicit contradictions block and are surfaced with exact factual provenance; repo policy is read from the trusted target baseline; local config/runtime overrides cannot bypass it; built-in rules fill only underdetermined mechanics. Policy cannot retarget a ConvergenceUnit.

**Promotion-policy currentness/refresh semantics are closed by ADR-044:** policy snapshots are immutable/fingerprinted observations, cache/TTL is never authorization, and every policy-sensitive promotion mutation requires immediate re-observation/revalidation of all mutable authoritative sources. Any changed authority anchor makes the snapshot stale and forces recomputation. Where a provider lacks an atomic check+mutation primitive, provider enforcement/rejection is the final external authority boundary; concurrent drift is surfaced factually and never auto-repaired.

**PromotionUnit declaration/identity semantics are closed by ADR-045/061:** a PromotionUnit is an immutable non-empty unordered unique exact-state set with content-addressed identity. V1 derives the ID from a domain-separated/versioned canonical encoding using SHA-256. Same exact set is idempotently the same unit; any exact member change produces a different unit. Target remains outside the PromotionUnit content address because it is already immutable on each member ConvergenceUnit; all members of one same-source projection must share that target.

**PromotionGroup pre-resolution/default-mapping semantics are closed by ADR-046 as amended by ADR-069:** a work-bearing `NEW_GROUP` invocation supplies a sealed immutable ContributionUnit handoff cohort. Ruu mechanically derives one occurrence-bound closed PromotionGroup through stable ContributionUnit→ConvergenceUnit bindings. Distinct invocation occurrences remain distinct groups even with equal member sets. `READY_INTERNAL` never implies an implicit singleton.

**Multi-source PromotionGroup projection semantics are closed by ADR-047/061 as amended by ADR-069:** the whole group first adopts a complete group-local exact state attributable to its originating invocation or authorized same-group revision. Later unrelated live ConvergenceUnit movement does not refresh it. Ruu partitions that exact mapping deterministically by authoritative source repository and verifies one coherent immutable PromotionTarget per same-source partition before materializing/reusing exactly one repository-local PromotionUnit per represented repository. Same group + same repository is never split by target; conflicting targets fail closed. Cross-repository aggregate progress remains at PromotionGroup level.

**Repository-local multi-source candidate/head materialization is closed by ADR-048:** exact materialization uses one exact effective base, ancestry-maximal source reduction, an ancestry-aware versioned canonical pairwise full two-head (`ort`-class) fold, exact-state reuse when ancestry already suffices, and otherwise one deterministic synthetic multi-parent final candidate. Native octopus does not define semantics. Exact base and every original PromotionUnit source must be ancestors of the final candidate; semantic conflicts reuse `RECONCILIATION_REQUIRED`; the exact final candidate may be adopted only when its transition-local exact prerequisites hold; `ruu` never executes the development validation process. Materialization is isolated/recoverable under ADR-042.

**Submission-ref identity/naming/retention semantics are closed by ADR-049:** every PROVIDER_SUBMISSION-route submission ref is physically distinct from internal refs even when OIDs match. Stable `submission_id` follows one repository-local logical projection + canonical publication destination across exact PromotionUnit/head revisions; first publish uses expected-absent, revisions use exact expected-old guards, branch naming is non-authoritative, and physical branch cleanup is separated from durable revision/audit history.

**PromotionUnit completion / ConvergenceUnit closure-retirement semantics are closed by ADR-054:** one exact `PromotionUnit PROMOTED` does not close its source ConvergenceUnit. ConvergenceUnit `PROMOTED` requires terminal settlement of every relevant PromotionGroup/promotion obligation plus zero current authoring/reconciliation demand; `RETIRED` additionally requires correctness-critical recovery/resource sufficiency. Retirement only makes historical internal refs GC-eligible; built-in v1 retention is `KEEP`, while durable audit history remains separate. ADR-060 removes the generic development-validation evidence contract; validation logs/cache/retention remain external Development System concerns.

**Cross-repository settlement/compensation semantics are closed by ADR-055:** `PARTIALLY_PROMOTED` is ordinary nonterminal progress, not automatic failure. Semantic roll-forward vs compensation belongs to the External Control Plane/Development System; all resulting Git effects are forward-only. Exact-generation settlement demands are durable/idempotent/global; `ALL_PROMOTED` is normal terminal success and explicit `COMPENSATED` is terminal only after semantic compensation completion plus exact observed/adopted forward effects. Stable logical submissions may open a new PublicationEpisode/provider submission after a prior episode is terminal. ADR-055 also retroactively makes ADR-022/024/026/032/036 responsibilities explicit in `EXTERNAL-CONTROL-PLANE-CONTRACT.md`.

**New-repository creation/bootstrap authority is closed by ADR-056:** agents/sessions may request a repository but do not self-authorize it; External Control Plane RepositoryCreationPolicy authorizes and a Repository Provisioner executes/reconciles creation. A brand-new repo is admitted only with configured target at exact non-null bootstrap OID `B0`, after which ordinary ADR-015/023 provisioning applies. Local creation and provider attachment are distinct; provider creation may be lazy, unknown identity/name/path collisions fail closed, underdetermined provider visibility defaults safely to `PRIVATE`, and provisioning failure never implies destructive repository deletion.

**Derived stack/restack semantics are closed by ADR-050/061:** no caller/agent chooses stacked publication. Stack shape is the provider representation of an exact predecessor dependency not yet satisfied by the immutable PromotionTarget's current state. A predecessor revision restacks by exact three-way state transplant from the immutable owned `(old_base_oid, owned_candidate_oid)` anchor onto the new base, never from a previous restacked provider head; conflicts route to `RECONCILIATION_REQUIRED`, every new exact head satisfies its transition-local revision/publication prerequisites, and only the ADR-049 submission ref/revision may be rewritten.

**Provider capability discovery semantics are closed by ADR-051:** the core determines the required semantic transition first; provider adapters expose fresh contextual `SUPPORTED | UNSUPPORTED | UNKNOWN_INCONSISTENT` observations for that exact operation/context, while policy independently determines authorization. Provider feature names never select topology or redefine core semantics; provider-native execution is accepted only when exact observed output conforms to the normative contract. Capability/current-fact observations inherit ADR-044 freshness rules.

**DIRECT target-advancement mechanics are closed by ADR-052/061:** once ADR-048 has produced exact candidate `C` for the immutable PromotionTarget and the DIRECT transition-local prerequisites are satisfied, target advancement is a pure semantic `AdvanceTargetFF(PromotionTarget.ref, expected_old=B, new=C)` operation. It has no target worktree/merge staging or pre-advanced local target ref; success is one atomic exact-old CAS+FF effect. An attempt-scoped non-business recovery anchor keeps `C` reachable until authoritative target observation proves `C` is realized (equal or ancestor of the current target), after which physical cleanup is separately eligible. Backend mechanisms are subordinate to this contract.

**Semantic review continuation is closed by ADR-053:** `CHANGES_REQUESTED` becomes one durable exact-generation-bound idempotent ReviewCorrectionDemand discoverable by provider hooks or any later global sweep. The original coding session need not stay open; the External Control Plane may restore it or start a new continuation session with review feedback as development input. Affected existing ConvergenceUnits may be discovered/reactivated while that session works; all new writes use new ContributionUnits. Same-group corrections reconverge into new exact PromotionUnits while preserving ADR-049 logical submission identity: an open PublicationEpisode revises the same provider submission, whereas a terminal prior provider submission is followed by a new ADR-055 episode if the nonterminal ship still needs publication. Real new ConvergenceUnit scope requires a new/superseding PromotionGroup.

ADR-057 substantially narrowed the Ruu backlog; ADR-058/ADR-059 close **30.27 checkpoint candidate membership/snapshot/identity**, ADR-060 closes **30.28** as obsolete by removing the generic validation-evidence contract, ADR-061 closes **30.40 immutable pre-authoring PromotionTarget ownership/retargeting**, ADR-062 closes **30.36 exceptional REVIEW_NOT_REQUESTED fallback**, ADR-063 explicitly places semantic findings/backlog outside the engine, and ADR-064 closes the remaining pre-commit identity ambiguity by frozen mutation handoff without creating a new generic validation gate. ADR-065/066 close **30.34 final target integration proof** with route-conformant `C → H → R → O` semantics; ADR-067 closes obsolete PromotionUnit supersession; ADR-068 closes **30.41 ConvergenceUnit abandonment/disposition after PromotionGroup binding**. Development test/review/security/finding-adjudication execution concerns remain outside this backlog.

## L. ConvergenceUnit abandonment/disposition after PromotionGroup binding — CLOSED by ADR-068/071, corrected by ADR-074/075 (30.41)

ADR-068 introduced exact pre-promotion cancellation and immutable-group settlement. ADR-071 adds the current-disposition causal fence; ADR-074/075 define the native Git withdrawal mechanics:

```text
unmanaged branch/ref deletion or worktree deletion
→ ordinary Git artifact lifecycle

native mutation can terminate/replace current managed authoring binding
→ pre-linearization normalized native witness
→ TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN
→ UNKNOWN vetoed
→ committed terminal proof: ABANDON / CANCEL if still unrealized
→ committed rename + successor proof: CONTINUATION
```

No second ordinary `Ruu cancel` command is required. Later absence alone is insufficient, and failure to prove continuation is not abandonment. If promotion was already historically realized, branch deletion cannot erase it; partial progress remains under ADR-055 settlement and post-promotion deletion is ordinary cleanup. PromotionGroup membership remains immutable.



# Hostile falsification findings opened after ADR-068

The following items were opened by a post-ratification hostile audit of the ADR-068 package. They deliberately distinguish architectural defects from missing invariants, specification ambiguities, implementation conformance requirements, and verification gaps. None of these entries is a ratified solution.

## 30.42 PromotionGroup definition identity vs ship-occurrence identity — CLOSED by ADR-069 — REAL BUG

ADR-069 confirms the hostile-audit finding and removes member-set-only PromotionGroup occurrence identity. Ordinary new work is now bounded by one durable work-bearing logical `ruu` invocation with an opaque idempotent `invocation_id` and a sealed ContributionUnit handoff cohort. `ruu` derives the ConvergenceUnit member set mechanically and creates one PromotionGroup occurrence bound to that invocation.

```text
I1 != I2
members(G1) == members(G2)
→ G1 != G2
```

A separate `membership_fingerprint = H(canonical members)` remains useful as a value but no longer defines occurrence identity. Retry of one logical invocation reuses the same id; reuse with a different immutable cohort/binding fails closed. No artificial ConvergenceUnit churn is required.

## 30.43 Terminal PromotionGroup resolution freeze — CLOSED by ADR-069 — MISSING INVARIANT

ADR-069 replaces unqualified live-current ConvergenceUnit resolution with a durable **group-local exact resolution**. Unrelated later authoring/reopen of a shared ConvergenceUnit does not refresh or invalidate an older group's exact binding. A nonterminal group may revise its mapping only under current explicit group-bound correction/reconciliation authority, and untouched members retain their prior group-local state.

Terminal PromotionGroups are resolution-frozen:

```text
G1 terminal with G1[X] = A
G2 remains live
X later -> B

G1[X] remains A
```

This applies to `ALL_PROMOTED`, `COMPENSATED`, `CANCELLED`, and future terminal settlement states. ADR-067 `SUPERSEDED` now arises only from a legitimate newer resolution of the same nonterminal PromotionGroup, not from unrelated live ConvergenceUnit movement.

## 30.44 Semantic disposition as a causal authorization fence — CLOSED BY ADR-071

ADR-071 ratifies the unifying rule:

```text
reconciliation may recover knowledge without recovering authority
```

A persisted Operation/Attempt is historical recovery evidence, never perpetual future authorization. Every managed effect capable of newly realizing a PromotionGroup projection must cross a current-disposition causal authorization fence. `CANCEL`/`COMPENSATE` prevent incompatible new retries/effects once linearized; already causally committed effects are observed/adopted rather than denied.

## 30.45 Cancellation linearization vs ordinary unmanaged Git progress — CLOSED BY ADR-071, CLASSIFIER CORRECTED BY ADR-074

ADR-071 replaces the earlier explicit-cancellation-only assumption with native managed-authoring disposition capture. ADR-074 corrects the classifier after proving that `git branch -m old new` may expose deletion of the old ref to `reference-transaction`. Therefore the hook durably records `AUTHORING_BINDING_TRANSITION_PREPARED`; commit opens an unresolved disposition instead of immediately producing abandonment.

```text
proven native rename/rebind → CONTINUATION
proven terminal deletion    → ABANDON → CANCEL if still unrealized
```

Same OID/tree/ancestry or a copied branch never proves continuation. Existing provider surfaces are not residual authorization after `CANCEL`; pre-abandonment committed/realized effects are recovered/adopted. If external causal order cannot be proven, terminal classification fails closed rather than being fabricated from clocks.

The v1 implementation requires Git >= 2.28 for `reference-transaction` (or a future proven-equivalent native ref-transaction primitive).

## 30.46 OS run-lock descriptor inheritance — CLOSED BY ADR-072

ADR-072 makes the host run-lock descriptor/handle exclusively owned by the top-level `ruu` executor process and non-inheritable across all subprocess execution boundaries. POSIX implementations use `O_CLOEXEC` atomically where available or a race-safe `FD_CLOEXEC` fallback before any subprocess may spawn; other platforms use an equivalent non-inheritable handle.

Normative liveness property:

```text
parent executor dies
+ long-lived child survives
→ child cannot retain host run lock
→ successor executor can acquire physical ownership
```

A concrete smoke is required and included in the ADR-073 package. No heartbeat/TTL takeover model is introduced.

## 30.47 Development-System-independent authoring ingress — CLOSED BY ADR-073

ADR-073 rejects speculative v1 authoring generalization. V1 requires a dedicated Git worktree/ref surface for every actively authored managed ContributionUnit before its first managed write. There is no normative direct v1 authoring contract for arbitrary prebuilt commits, `tree + parent`, or external filesystem/sandbox snapshots.

This is a v1 substrate decision, not a claim that ContributionUnit identity is permanently a worktree:

```text
active v1 managed authoring
→ dedicated Git worktree required

exact managed checkpoint already captured
→ worktree may later disappear without erasing durable identity/state
```

A future sandbox-based v2 remains possible only through a new ADR proving equivalent isolation/base/freeze/exact-capture properties. No generic `AuthoringIngress`/adapter abstraction is introduced now.

## 30.48 Extend hostile state-space coverage beyond ADR-068 v36 dimensions — CLOSED; v39 SUPERSEDES THE OLD DELETION CLASSIFIER

`STATE-SPACE-AUDIT-v38.md` historically verified ADR-071's direct managed-deletion classifier. The later native-Git rename regression falsified only that classifier, not the current-disposition causal fence or the need for transactional write-ahead capture. ADR-074 corrects the model and `STATE-SPACE-AUDIT-v39.md` adds disposition-resolution/recovery dimensions while retaining the previous finite baseline.

Concrete regressions now distinguish native rename from copy+delete, verify reflog/worktree rename evidence, retain prepared-hook rejection behavior, and check ancestry-overlay hazards.

30.48 remains closed as the verification work item; v39 is the current dedicated regression for the corrected native binding-disposition classifier, while later cumulative state-space evidence continues through active post-baseline v46.

## 30.49 Native Git observation plane: scope and invariant — CLOSED BY ADR-080 — UMBRELLA

ADR-071 established one narrow use of Git's native hook surface and ADR-074 corrected its semantics: `reference-transaction` makes removal of the currently bound managed authoring ref durable as a binding-disposition transition rather than forcing later inference from ref absence. This raises the broader architectural question of how the selected correctness-relevant native observation points compose into a **native Git observation plane** without turning Git into a proxied command protocol.

The governing product constraint is already fixed by ADR-070/ADR-058: ordinary Git commands remain ordinary Git commands. The observation plane, if adopted, may observe and durably report facts but must not turn `ruu` into an exclusive proxy in front of Git.

Candidate separation:

```text
native Git operation
→ selected native Git observation point
→ durable factual observation where required
→ ordinary Ruu reconciliation
```

```text
hooks observe and durably report
≠
hooks interpret managed semantics or perform convergence
```

30.49 was intentionally an umbrella item and is now closed by ADR-080 after coherent resolution of 30.50–30.55. The resulting architecture keeps causal transactional observation minimal/local, exact-state rediscovery source-owned across local/remote/provider domains, advisory delivery non-authoritative, native-Git equivalence intact, and fail-closed behavior limited to correctness-required ambiguity.

Do **not** resolve this cluster by simply enabling every Git hook. Derive required observations from the state machine first; mechanisms come second.

## 30.50 Minimal correctness-relevant Git observation set — CLOSED BY ADR-074

The state-machine-first hostile sweep found a deliberately small taxonomy:

```text
EVENT PLANE
→ one currently ratified local business-event family:
   disposition of the currently bound managed authoring ref

STATE PLANE
→ exact current refs/OIDs/trees/worktrees/HEAD/index/structural state
→ internal/remote/submission/target/provider facts as required by current transitions
→ submodule/sparse observability
→ ancestry interpretation/completeness: refs/replace, info/grafts, shallow boundaries

OBSERVATION-INTEGRITY PLANE
→ whether required event coverage remained continuously trustworthy
```

A managed old-ref removal is captured as `AUTHORING_BINDING_TRANSITION_PREPARED`, then a committed transition resolves `CONTINUATION | ABANDON`. Same OID/tree/ancestry, branch copy, or plain worktree `HEAD` switching never establishes continuation. Native reflog is provisioned as causal evidence infrastructure, not identity.

No second irreducibly causal local Git business-event family was found. Intermediate history for commit/reset/merge/rebase/internal refs/submission refs/targets/worktrees/tags/stash/notes can be reconstructed or safely failed closed from current exact state.

ADR-075 closes 30.51 capture/reconstruction proof strength. ADR-076 closes 30.52 provenance/replay/idempotency. ADR-077 closes 30.53 observer ownership/admission/continuous-coverage establishment. ADR-079 closes 30.54 persistence-failure/admission behavior. ADR-080 closes 30.55 local/remote/provider composition and thereby closes the 30.49 umbrella.

## 30.51 Transactional capture versus exact-state rediscovery — CLOSED BY ADR-075

ADR-075 fixes three observation-strength classes:

```text
PRE-LINEARIZATION TRANSACTIONAL
→ only native mutations capable of terminating/replacing a currently-bound managed authoring ref
→ normalized witness must be durable before the binding change may linearize

EXACT-STATE REDISCOVERY
→ all other currently identified correctness-relevant Git/remote/provider state
→ current authoritative state is re-read when a transition needs it

BEST-EFFORT SIGNAL
→ wake-up/diagnostic only; loss/duplication/reordering cannot affect correctness
```

For live managed authoring, conformance is capability-based rather than backend-name-based. Every deletion/replacement/forced-rename destination overwrite capable of ending a current managed binding must expose a vetoable or equivalently causally serialized pre-linearization adapter point. The adapter reports normalized Git/backend facts; the core derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`. `UNKNOWN` cannot silently commit.

`ABANDON` and `CONTINUATION` are positive proofs; `!ContinuationProof` never implies abandonment. The managed reflog baseline is `ENTRY(anchor_entry_fingerprint) | EMPTY_PRESENT`; the anchor fingerprints a logical reflog entry, never a physical file or complete reflog. Opaque backend witness hashes are non-normative.

The tested stock Git 2.47.3 `files` path supplies a demonstrated pre-linearization evidence route. The tested stock `reftable` path allows `branch -m/-M` to complete without `reference-transaction` callbacks and is therefore not currently conforming for live managed authoring; a future adapter/upstream primitive satisfying the same capability contract becomes conforming without changing core semantics.

Managed ancestry reconstruction is state-based: replace/graft overlays may not silently influence canonical ancestry, while shallow history must be deepened/fetched when authorized and possible or remain ancestry-unknown.

ADR-077 closes installation/coexistence and continuous-coverage establishment under 30.53. ADR-079 closes 30.54 persistence-failure behavior, conservative protection filtering, exact binding admission and initial handoff; ADR-076 closes durable witness provenance/replay/idempotency under 30.52.

## 30.52 Observation provenance, replay, and idempotency — CLOSED BY ADR-076

ADR-076 separates managed effect intent, native causal evidence, and authoritative managed transition identity.

```text
Operation → Attempt → Observation → Adoption
= effects owned/caused by Ruu

NativeRefWitness / NativeBindingPreparation
= physical/causal Git evidence

native witness
≠ managed Operation
```

A witness may carry optional trusted `originating_attempt_id` correlation when a managed Attempt launched the Git operation, but provenance is never authorization and actor identity is not inferred for correctness. Native deliveries/outcomes may duplicate or replay; nonsemantic wakeups may be lost/coalesced/reordered. Exactly-once applies instead to authoritative logical adoption: at most one Adoption per `operation_id` and at most one committed disposition out of one current managed `binding_generation`, guarded by current expected-state/CAS.

A conforming native-ref adapter must correlate duplicate delivery of the same **active** pre-linearization occurrence sufficiently to reuse the same effective preparation/decision; the core does not require a globally unique permanent Git transaction ID. One current binding generation admits at most one unresolved correctness-critical cessation/rebind preparation. A later exact-state scan may resolve an existing durable preparation or Operation but may never synthesize missing causal history (`TERMINAL_REMOVAL_PREPARED` / `RENAME_CARRY_PREPARED`) merely from final topology.

## 30.53 Hook ownership, installation, and coexistence — CLOSED BY ADR-077

ADR-077 makes observer coverage a functionally attested property of the **repository-common managed ref mutation surface plus an admitted mutation-engine/adapter profile**, not of hook-file presence alone.

For V1, Git core is the required native ref-mutation engine family. Tools/IDEs that delegate all relevant ref mutation to a conforming Git core path inherit conformance; alternative engines (libgit2/JGit/custom refdb/etc.) require separately demonstrated adapters. A direct or uninstrumented writer remains physically possible, but if it changes a current managed binding without the required causal preparation the result is `UNWITNESSED_MANAGED_BINDING_MUTATION` / observation-integrity failure and cannot be reclassified from final topology alone.

Observer installation is repository-common for shared `refs/*` and must be `ACTIVE` before first managed write. `ruu` owns only exact registrations/artifacts it created/adopted and uses expected-state/CAS semantics for install/upgrade/remove. It never implicitly owns or overwrites `core.hooksPath`, an entire hookdir, a foreign traditional hook, another configured hook, or a third-party dispatcher.

Composition must use a Git-native or explicitly supported composition surface. Git 2.54+ configured multiple hooks are the preferred modern path but are not made the architectural V1 minimum. A legacy traditional `reference-transaction` slot may be used when absent/already exactly owned; a foreign slot/path without a proven composition adapter blocks **managed-authoring admission**, not ordinary Git. No generic takeover dispatcher is introduced.

Coverage is functionally attested and tracked by `coverage_epoch`. Clone/recreation/reactivation or relevant engine/config/backend/adapter changes require idempotent re-establishment. A later repaired epoch never retroactively proves a prior gap. ADR-079/30.54 owns the concrete transaction/persistence consequences of such failure/gap states.

## 30.54 Observation persistence failure semantics — CLOSED by ADR-079

ADR-079 chooses the smallest correctness-required rejection set.

```text
no cessation/replacement candidate
→ allow + exact-state rediscovery

trustworthy ManagedRefProtectionFilter proves candidate outside protected set
→ allow without authoritative lookup

filter degraded
→ disable negative fast-path; classify candidate from authoritative managed state

current managed binding affected
→ complete NativeBindingPreparation batch crash-durable before allow
→ unavailable classification/persistence after bounded retry = veto

PREPARED already durable but final committed/aborted recording fails
→ allow + reconcile later

wakeup/log/telemetry/diagnostic failure
→ allow + advisory loss tolerated
```

`ManagedRefProtectionFilter` is repository-common conservative acceleration, never binding authority. Missing/corrupt/untrusted filter state is not empty and is not by itself a coverage gap. Initial managed binding admission is serialized against native ref mutation through a capability-based `RefAdmissionBarrier`; authoritative binding publication occurs while the barrier is held, exact candidate worktree topology is revalidated, then the barrier is released and authoring authority is handed to the producer. The current Git-core/files candidate realizes the barrier through a prepared exact no-op ref transaction; backend-private lock emulation is not normative.

Coverage gap, filter degradation and critical persistence failure remain distinct failure classes. Final topology never repairs missing causal coverage.

## 30.55 Local native-Git versus remote/provider observation boundary — CLOSED BY ADR-080

ADR-080 fixes three source-scoped factual domains feeding one reconciler without creating a distributed transaction:

```text
LOCAL_GIT
→ exact local state + the narrow managed-binding causal observer

REMOTE_GIT
→ authoritative current remote refs/OIDs + exact-preconditioned remote mutation/re-observation

PROVIDER
→ optional provider-owned submission/review/check/queue/governance/finalization facts
```

Local hooks have no authority over remote/provider mutations. Local `refs/remotes/*` are caches, never authoritative current remote state. Bare Git remotes are first-class: provider-free routes use direct remote-Git observation and exact expected-old mutation/recovery without any forge API.

Webhook delivery is an unreliable/reorderable transport. It may wake reconciliation and an authenticated payload may contribute positive provider-scoped historical evidence when the adapter demonstrates exact semantics, but absence is never negative proof, delivery identity is not semantic operation identity, and correctness cannot generically depend on receiving one particular webhook. Cross-source composition uses exact identities/source revisions, never wall-clock ordering.

Remote publication artifact deletion/rename never inherits the local managed-authoring `CONTINUATION | ABANDON` classifier. Historical provider finalization evidence remains distinct from current remote/target topology.

ADR-080 therefore closes both 30.55 and umbrella 30.49. The native-Git observation-plane cluster 30.50–30.55 is complete.

## 30.56 Exact managed authoring dependency before source promotion — CLOSED BY ADR-081

ADR-081 ratifies an immutable repository-local AuthoringDependency selected explicitly by the Development System:

```text
consumer ContributionUnit
→ source ContributionUnit + consumed exact native commit OID
```

ContributionUnit is the sole v1 authoring-occurrence identity. Ruu independently proves exact source lineage, creates a REQUIRED recovery anchor before adoption, permits otherwise legal consumer authoring/checkpointing/convergence, and blocks only unauthorized realization. Dirty producer state is never a version or an implicit synthetic commit. Native commit creation remains exact-state rediscovery and becomes a managed checkpoint only through later exact frozen-handoff adoption.

A current authoritative target may satisfy the dependency directly. Otherwise a qualifying source handoff accepted after durable selection may resolve it to stable `(PromotionGroup, source repository)` identity only when the source's own frozen pre-sync checkpoint contains the consumed OID, group-local state incorporates that checkpoint, and source/consumer immutable PromotionTargets are exactly equal. This preserves the consumed OID and uses ADR-050 `Restack(old_base, owned_candidate, current_parent)` semantics without laundering source ancestry back through the consumer. Same-group dependencies create no provider edge. Source abandonment without prior realization produces reconciliation and never transfers publication authority.

## 30.57 Multiple independently unsatisfied authoring predecessors — OPEN — HIGH

Minimal counterexample:

```text
consumer β requires source α@A and source γ@Q
A and Q are both exact and durably retained
neither source effect is target-realized
α and γ later resolve to different PromotionGroups
```

The durable relation model can retain both obligations, and consumer authoring may proceed only if one already-existing exact base canonically contains both. The current publication model cannot represent the general remaining case: ADR-050 has one `parent_submission_id`, while an ordinary Git/provider submission has one base. ADR-048 composes sources inside one PromotionUnit but does not grant cross-group source publication authority.

Decision required: choose whether publication waits for all but one dependency to become target-satisfied, derives a deterministic promotion DAG/linearization, creates multiple provider surfaces, requires semantic consolidation into another authoritative source, or adopts another exact model. No option is ratified. Until then, realization with more than one independently unsatisfied external predecessor is locally blocked.

## 30.58 Late authoring-dependency discovery and consumer refoundation — OPEN — HIGH

Minimal counterexample:

```text
consumer β starts from M
β authors exact work W
only then the Development System discovers required source α@A
```

ADR-081's accepted path adopts dependencies before β's first write. Later Git ancestry cannot manufacture semantic selection. ADR-050 restacks a provider projection after managed handoff and grants no mutation authority over β's active worktree. Current ADRs do not choose whether to create a new ContributionUnit from `A`, exact-transplant `M→W` onto `A`, perform an ordinary semantic merge, or retain another explicit refoundation object/freeze protocol.

Decision required: define the authority, exact inputs, conflict state, lifecycle, and retry/retention semantics of late refoundation. Until then, Ruu performs no implicit active-worktree rewrite and exposes the condition for Development System action.
