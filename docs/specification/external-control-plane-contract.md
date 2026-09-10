# Ruu — External Control Plane Contract

- **Status:** Normative companion contract
- **Introduced by:** ADR-039
- **Date:** 2026-09-05
- **Current amendments:** ADR-062 through ADR-081, as applicable (through 2026-11-03)

## 1. Purpose

`ruu` deliberately does not own the semantic/runtime decisions that create and operate development work. Those decisions are represented through an abstract **External Control Plane** contract.

The External Control Plane is a **role**, not a required product, daemon, service, database, agent harness, or single process. It may be implemented by any combination of user-facing tooling, an orchestrator, an agent runtime, a provisioner, repository policy, or another component, provided the contract below is satisfied. **Architectural externality does not imply a second user-installed product:** under ADR-078, a Ruu distribution may supply integrations for supported coding harnesses that implement this role and its pre-edit provisioning automatically.

`ruu` depends on this contract, not on Turnlock, `/go`, Pi, Claude Code, any particular agent, or any particular storage/backend implementation. A particular product distribution may nevertheless ship adapters for those harnesses so the user-facing workflow remains zero-preflight.

The boundary is:

```text
External Control Plane
  → establishes semantic/logical work topology and safe editing authority
  → exposes authoritative declarations required by Ruu

Git / remotes / provider
  → remain authoritative for Git/provider facts they own

                    ↓

Ruu
  → observes/revalidates exact Git/provider state
  → checkpoints, synchronizes, integrates, promotes, publishes,
    refreshes transition-specific waits, recovers owned operations
  → advances all known nonterminal managed obligations to the
    current global fixed point
```

The External Control Plane MUST NOT manufacture Git/provider truth merely by declaring it. Exact refs/OIDs, worktrees, remote refs, provider state, merge results, and similar facts remain subject to `ruu` observation/revalidation rules.

### 1.1 Product-intent conformance

This contract is interpreted under ADR-070, ADR-078 and §0 of `RUU-SPEC.md`.

For a supported coding harness, ordinary managed authoring MUST be zero-preflight from the user's perspective: after one-time product installation/integration, asking the agent to implement work is sufficient to trigger the required pre-edit provisioning before first managed write. The user MUST NOT be required to issue a separate `start`, `create-cu`, or `provision` command, install observer plumbing per repository, or operate another control-plane product merely to begin ordinary managed coding. Administrative/testing/recovery interfaces may expose those primitives.

This product requirement changes **who may implement the role**, not what the role is authoritative for. Semantic work topology, lifecycle, target/grouping intent and readiness remain externally authoritative; the convergence engine still MUST NOT infer them from code/task/session/Git shape.

The identities and declarations below are system/ECP contracts, not a requirement that the human user manually reconstruct orchestration state before ordinary invocation. In particular, the Development System is expected to carry/generate the durable `invocation_id`, sealed ContributionUnit cohort, target/group bindings, any explicit exact authoring-source selections, and other authoritative metadata required for safe progression behind the user-facing `ruu` action.

For already-managed work, neither the caller's CWD nor the identity of the session that happens to raise convergence demand narrows the global sweep. Multiple coding sessions and simultaneous invocations are normal. External components MUST NOT require a human mutex, caller-authored global repository list, caller-authored PromotionGroup membership, or caller-authored stack topology when those facts are already known or mechanically derivable.

This simplicity does not relax authority boundaries: the External Control Plane still owns semantic decisions and mutation handoff; `ruu` still fails closed on genuinely unknown/inconsistent authority or irreducible semantic conflict.

ADR-070 also governs the dependency direction between core version control and provider publication. Provider submissions, review state, merge queues, protected-target APIs, and other hosting-specific objects are realization/projection facts over core exact Git/version state; they are not the source of core version identity or convergence truth when those facts can be established provider-independently.

## 2. Responsibilities owned by the External Control Plane

### 2.1 ContributionUnit creation and stable binding

Before new managed work is produced, the External Control Plane establishes a repository-local ContributionUnit with stable opaque identity and stable bindings:

```text
contribution_unit_id
→ exactly one repository_id
→ exactly one convergence_unit_id for this identity
```

`ruu` does not infer ContributionUnit identity from actor/session/process/model, branch name, worktree path, CWD, task, or invocation principal.

A different convergence scope requires a new `contribution_unit_id`; an existing ContributionUnit is not rebound to another ConvergenceUnit.

`ContributionUnit` is also the sole v1 stable authoring-occurrence identity. Historical `ContributionUnit/work occurrence` wording names this same object. The contract defines no second `work_occurrence_id`; a binding generation identifies a generation of the ContributionUnit's current authoring-surface binding, not another work identity.

### 2.2 ContributionUnit lifecycle authority

The External Control Plane is authoritative for:

```text
ContributionUnit lifecycle = OPEN | CLOSED
```

with normative meanings:

```text
OPEN
= this ContributionUnit may still produce additional contribution
  to its current convergence scope

CLOSED
= this ContributionUnit will produce no further contribution
  to its current convergence scope;
  later work requires a new ContributionUnit
```

`CLOSED → OPEN` is forbidden for the same ContributionUnit identity.

The lifecycle MUST NOT be inferred from agent/runtime state, turn completion, waiting for user input, clean/dirty state, commit, verification, integration, branch/worktree presence, or producer inactivity.

### 2.3 ConvergenceUnit creation, grouping, and contribution membership

The External Control Plane creates or reuses ConvergenceUnits and binds each newly created ContributionUnit to exactly one ConvergenceUnit.

It is authoritative for ConvergenceUnit contribution-membership state:

```text
OPEN
= additional ContributionUnits may still be attached to this
  convergence scope

SEALED
= no additional ContributionUnit is expected for the current
  finalization attempt
```

`ruu` MUST NOT infer grouping or sealing from caller identity, task semantics, file overlap, branch names, ancestry alone, commit count, CWD, or the currently visible set of ContributionUnits.

If later semantic/review work requires new contribution after sealing/readiness, the External Control Plane explicitly reactivates the affected convergence scope and returns membership to `OPEN` before creating/binding new ContributionUnits. Live ConvergenceUnit readiness/current-source bindings are invalidated according to the main specification; exact states already adopted into unrelated older PromotionGroups remain group-local historical/current bindings under ADR-069.

Experimental, competing, or alternative work that must remain isolated from a primary result is represented by a distinct ConvergenceUnit.

### 2.3A ConvergenceUnit PromotionTarget authority

Before the first managed write in any ContributionUnit attached to a ConvergenceUnit, the External Control Plane MUST resolve and durably bind exactly one canonical final destination:

```text
PromotionTarget {
  target_repository_id
  target_ref
}
```

This is logical destination intent owned outside `ruu`; it is distinct from the repository-local `ConvergenceBase` used to provision/synchronize the ConvergenceUnit during authoring. In a simple same-repository workflow the two commonly designate the same branch; in a cross-repository contribution the source-local ConvergenceBase and upstream PromotionTarget may differ.

The binding is immutable for the ConvergenceUnit lifetime. Reusing an existing ConvergenceUnit requires exact PromotionTarget equality. A request for another destination requires a distinct ConvergenceUnit / convergence scope; the External Control Plane MUST NOT retarget an existing ConvergenceUnit after managed authoring begins.

Policy/config/provider changes may alter whether `DIRECT_TARGET_ADVANCE`, `PROVIDER_SUBMISSION`, or a particular provider operation is currently authorized/supported, but they do not alter the PromotionTarget identity. The current target OID and provider/governance facts remain dynamic facts that `ruu` observes/revalidates.

### 2.4 Pre-edit provisioning and editing-artifact lifecycle

The External Control Plane (or tooling acting on its behalf, including a Ruu-supplied supported-harness integration under ADR-078) ensures that safe repository-local editing topology exists before the first managed write that requires it. This provisioning is a pre-edit phase and MUST NOT be deferred until the later `ruu` checkpoint/convergence invocation. In the ordinary supported-harness product path it is automatic and invisible to the user. It includes as applicable:

```text
repository registration/reactivation
ConvergenceBase identity/ref resolution
immutable ConvergenceUnit PromotionTarget resolution/binding
convergence-unit identity/ref establishment
contribution-unit identity/ref establishment
isolated worktree provisioning
attested repository-common native-ref observation coverage for the admitted mutation-engine/backend/adapter profile
write authorization / external mutation-authority mechanism
```

ADR-073 makes the v1 substrate requirement explicit: every actively authored managed ContributionUnit MUST have its own dedicated Git worktree/ref surface before its first managed write. V1 does not define an alternative direct authoring contract that bypasses this topology by supplying arbitrary prebuilt commits, trees, or external sandbox/filesystem snapshots. Ordinary native Git activity inside the managed worktree remains supported. A future sandbox substrate requires a separate ADR proving equivalent isolation/base/freeze/exact-capture guarantees.

Repository identity and repository location are distinct under ADR-042. The External Control Plane may explicitly relocate the current host-local locator bound to an existing opaque `repository_id`; relocation MUST NOT mint a new repository identity merely because the path changed, and a locator MUST NOT be authoritatively bound to multiple repository identities in the same coordination domain. `ruu` records such locator changes through exact expected-state/CAS semantics and still revalidates the Git facts found at the declared locator.

Users/agents/tooling may later create or delete contribution branches, worktrees, and remote refs outside `ruu`.

Editing-artifact presence is not ContributionUnit identity or lifecycle. The External Control Plane MUST NOT require `ruu` to infer semantic intent from artifact disappearance.

### 2.4A Work-bearing logical invocation and cohort authority

When the Development System invokes `ruu` to checkpoint newly produced work, it supplies one durable work-bearing logical invocation:

```text
LogicalInvocation {
  invocation_id
  handoffs: non-empty closed Set<ContributionUnitHandoffRef>
  promotion_binding:
      NEW_GROUP
    | REVISE_EXISTING_GROUP(promotion_group_id, authority_ref)
}
```

The External Control Plane/Development System is authoritative for **which ContributionUnits belong to this invocation cohort**. It does not separately choose the resulting PromotionGroup ConvergenceUnit member set; `ruu` derives that set mechanically from the stable ContributionUnit→ConvergenceUnit bindings.

The same `invocation_id` MUST be reused for retry of the same logical invocation and MUST NOT be reused for a later distinct cohort or different promotion binding. The exact id-generation/storage mechanism is external to `ruu`, but it must survive caller crash/restart sufficiently to preserve this idempotency contract.

Every listed editing surface MUST have a current frozen mutation handoff bound to this invocation before the invocation is sealed/accepted. Partial handoff preparation before seal is not an accepted checkpoint cohort. Once sealed, the cohort is immutable; subsequent new authoring belongs to a later logical invocation.

`NEW_GROUP` means ordinary new implementation work and causes one new PromotionGroup occurrence. `REVISE_EXISTING_GROUP` is valid only with current durable correction/reconciliation authority explicitly bound to the named existing group; all ConvergenceUnits touched by that revision must already be members of that group.

Demand-only `ruu` triggers remain valid and create no LogicalInvocation. The convergence-demand signal emitted by a work-bearing invocation is still coalescible under ADR-041/042 and does not scope the global sweep.

ADR-056 closes brand-new repository/provider-repository creation as an External Control Plane + Repository Provisioner responsibility. A session/agent/orchestrator may request a repository but does not self-authorize creation. Before the first managed write in a brand-new repository, the control plane/provisioner MUST satisfy a durable `RepositoryBootstrapContract`:

```text
current RepositoryCreationPolicy authorizes creation
+ stable repository_id allocated/bound
+ authorized local locator contains the intended valid Git repository
+ configured target ref exists at exact non-null bootstrap OID B0
+ required bootstrap/governance profile is established
+ provider binding exists/valid if required for the current phase
+ exact observed facts match the durable provisioning intent
→ REPOSITORY_ADMITTED
```

V1 MUST NOT hand an unborn/null target to ordinary managed authoring. After admission, ADR-015/023 create the ConvergenceUnit/ContributionUnit/worktree exactly as for any existing repository.

The creation policy is external/pre-repository and may authorize/resolve local locator, provider/account/organization/namespace, canonical name, visibility, repository bootstrap/configured target ref, bootstrap profile, governance requirements, and eager-vs-lazy provider attachment. That repository-bootstrap target establishes a non-null admitted Git base; ADR-061 separately requires each ConvergenceUnit's immutable PromotionTarget to be bound before managed authoring. Agent suggestions are non-authoritative. If provider creation is authorized and visibility alone remains genuinely underdetermined, the built-in safe default is `PRIVATE`; `PUBLIC` is never inferred. Missing authority for provider/account/organization/namespace blocks rather than guesses.

Local repository creation and provider repository creation are distinct. Provider attachment may be deferred until a provider-sensitive operation requires it. Until then, provider-dependent governance/publication/check/review/queue operations remain blocked/localized without invalidating otherwise-authorized local managed work.

Repository provisioning is a durable idempotent external reconciliation concern. Retries observe/adopt already-realized local/provider objects using durable identity/bindings and exact facts; filesystem paths and provider names are not identity. Unknown locator/name/provider-ID collisions fail closed. Failure after object creation does not authorize destructive repository deletion; deletion requires separate explicit destructive authority. This external provisioning operation is not implicitly moved into the ADR-042 `ruu` CoordinationStore.

ADR-022's pre-ADR-039 registry boundary is explicit here: before the first managed write, repository admission/reactivation MUST create durable shared-coordination identity/bindings and the authoritative nonterminal obligation records that make the work discoverable. The External Control Plane may request/admit/reactivate managed work, but it does not own Git truth and it cannot use a stale `ACTIVE_CONVERGENCE_SET` to hide obligations. That index is derived/reconstructible acceleration state only; repository inactivity means zero authoritative nonterminal managed obligations, not merely absence from an external runtime/session.

### 2.4B Managed authoring-binding continuity and exceptional recovery authority

ADR-074 distinguishes physical Git ref history from the durable logical identity of an existing ContributionUnit. The External Control Plane does not normally explain native branch operations to `ruu`; native rename/rebind continuity is resolved from Git-native evidence.

Before first managed write, the provisioning path MUST ensure that the current managed authoring ref has a native reflog. The reflog is causal-evidence infrastructure, not logical identity. ADR-075 additionally requires the selected repository ref backend/adapter to satisfy the native-ref observation capability contract for live managed authoring before the surface is admitted: every native mutation capable of terminating/replacing the current managed binding must be observable at a vetoable/equivalently serialized pre-linearization point with exact preimage and durable normalized witness support. The External Control Plane does not manufacture this Git capability; it ensures managed authoring does not begin on a surface for which the capability cannot be established.

If native causal evidence is irretrievably insufficient to resolve a committed managed-authoring binding transition, the External Control Plane MAY provide one explicit generation-bound recovery declaration:

```text
AuthoringBindingRecovery {
  contribution_unit_id
  expected_binding_generation
  expected_old_ref
  resolution = REBIND(new_ref) | ABANDON
}
```

This declaration is authoritative only for the **logical recovery decision** that the same existing managed occurrence continues on a new editing surface or is authoritatively abandoned. It does not manufacture Git truth and MUST NOT claim that a particular Git command (for example `git branch -m`) occurred.

`ruu` adopts `REBIND` only after fresh exact observation proves that the declared repository/ref/worktree state is real and compatible, mutation authority is current, and no conflicting binding exists. Expected-old/binding-generation mismatch or contradictory Git state fails closed.

A stale recovery declaration cannot resurrect already-abandoned work. This recovery path is exceptional and does not replace ordinary native Git rename/deletion semantics.

### 2.4C Native observation coverage admission and mutation-engine boundary

ADR-077 makes the ADR-075 observer prerequisite an explicit pre-authoring admission contract.

Before the first managed write, and again before reactivation after clone/recreation/new locator or another coverage-invalidating profile change, the provisioning path MUST establish a functionally attested repository-common native observation binding for the admitted ref-mutation engine/adapter profile:

```text
NativeObservationCoverage.status = ACTIVE
```

The coverage binding is shared repository infrastructure, not session/invocation ownership. The External Control Plane ensures authoring does not begin while coverage is absent/broken; it does not manufacture the Git capability or require the user to manually compose hooks for each session.

V1 requires a conforming Git core mutation-engine family. A tool/IDE that delegates every correctness-relevant managed-ref mutation to a conforming engine inherits that conformance. An alternative embedded Git/ref engine requires its own separately demonstrated adapter; generic Git compatibility is not sufficient.

`ruu`/its adapter may establish or repair only observer registrations/artifacts it exactly owns or is authorized to create. Existing `core.hooksPath`, foreign traditional hooks, configured hooks and third-party dispatchers are not implicitly owned and MUST NOT be overwritten or silently wrapped. Where no native/explicitly-supported composition surface exists, managed-authoring admission blocks while ordinary unmanaged Git remains usable.

Coverage is tracked through trustworthy epochs. A later repair/re-attestation does not retroactively cover an earlier gap. An unwitnessed exact-state change to a currently managed binding is an observation-integrity failure and MUST NOT be converted to `REBIND`/`ABANDON` from topology alone; the exceptional generation-bound `AuthoringBindingRecovery` above remains the only external logical recovery authority when native causal evidence is irretrievably insufficient.

### 2.4D Persistence-failure admission, protection filtering, and initial authoring handoff

ADR-079 closes 30.54 by making failure handling proportional to the exact managed risk rather than to observer availability in general.

The pre-edit provisioning/harness integration MUST treat a newly created branch/worktree as a **candidate authoring surface**, not yet as managed producer-owned work. Before the first managed write it ensures:

```text
repository-common observation coverage ACTIVE
→ conservative ManagedRefProtectionFilter protection established or negative fast-path durably disabled/degraded-safe
→ exact RefAdmissionBarrier acquired for the candidate ref
→ candidate worktree/ref topology revalidated while provisioning retains exclusive mutation authority
→ authoritative current binding committed while the barrier remains held
→ barrier released
→ initial authoring authority handed to the producer
→ first managed write permitted
```

`RefAdmissionBarrier` is a native-ref adapter capability: exact candidate-ref preimage is verified under exclusion with conforming native mutation until authoritative binding publication commits. Candidate branch/worktree creation alone does not create a managed binding. A Ruu-supplied harness integration performs these steps invisibly under ADR-078; the user does not orchestrate them.

The repository-common `ManagedRefProtectionFilter` is conservative acceleration only. A trustworthy negative answer may skip authoritative lookup. Positive/stale entries merely cause extra lookup. Missing/corrupt/untrusted filter state disables negative acceleration; it is not treated as empty and is not by itself a native-observation coverage gap. Binding identity/generation/currentness remains authoritative only in the CoordinationStore.

For native ref transactions:

```text
no cessation/replacement candidate
→ allow; exact-state rediscovery

candidate proven outside protected set by trustworthy filter
→ allow

candidate may affect a current managed binding
→ complete crash-durable NativeBindingPreparation batch required before allow

required authoritative classification or preparation persistence unavailable
→ bounded retry if useful
→ veto

PREPARED already durable but committed/aborted outcome recording unavailable
→ allow; reconcile later

wakeup/log/telemetry/diagnostic failure
→ allow; advisory loss tolerated
```

Filter degradation, critical persistence failure, and actual observer coverage loss are distinct. A successfully vetoed critical persistence failure demonstrates that the observer path worked. An actual bypass/gap closes the coverage epoch and cannot be repaired by inferring history from final topology.

The live lock order for admission/observation is native Git/ref exclusion before a short authoritative CoordinationStore transaction. The External Control Plane/provisioner MUST NOT keep a live CoordinationStore transaction/mutex/write lock while waiting to acquire the corresponding Git/native ref lock.

`git worktree lock` may be used as defense-in-depth but does not substitute for the pre-handoff authority boundary or exact worktree/HEAD topology revalidation.

### 2.4E Exact authoring-dependency selection and pre-edit adoption

ADR-081 adds one semantic selection owned by the Development System. Before a consumer ContributionUnit's first managed write, the Development System MAY explicitly declare that it requires an exact native commit from another still-active managed ContributionUnit:

```text
AuthoringDependencySelection {
  consumer: (repository_id, contribution_unit_id)
  source: (repository_id, contribution_unit_id)
  git_object_format
  consumed_exact_oid
}
```

The source and consumer are distinct ContributionUnits in one authoritative repository. A commit in another repository is not a Git authoring base; cross-repository semantic coordination continues through work-bearing invocation and PromotionGroup semantics.

This declaration answers only:

> Which stable managed source and exact native Git version does this consumer semantically require?

It does not choose PromotionGroup membership, PromotionUnit identity, a provider parent, stack shape, or publication route. The External Control Plane MUST NOT derive the selection from session/process order, branch names, file overlap, task similarity, recency, ancestry alone, or "latest pending work". Absence of a declaration means no authoring dependency is inferred.

The declaration also does not manufacture Git truth. Ruu independently verifies the source's current unambiguous managed binding/lineage, exact commit object and object format, strict descent from the source's admitted authoring base, canonical raw ancestry without unnoticed replace/graft overlays, and source disposition. A dirty source worktree MAY coexist with the selected commit, but the declaration identifies only the commit. The External Control Plane MUST NOT ask Ruu to snapshot, commit, stage, stash, or copy the producer's mutable surface to make it consumable.

The declaration is accepted only after an ADR-042 recoverable adoption operation has created and observed a Ruu-owned `REQUIRED` recovery anchor for the consumed OID. The supported harness submits this as an authorized internal provisioning demand to the existing single-host OS-owned and SQLite-fenced ConvergenceEngine and waits before first consumer write; it is not a work-bearing checkpoint invocation and creates no PromotionGroup. TX-A durably linearizes the exact selection/expected source generation, and TX-B revalidates source row version, binding generation/continuity, lineage, and disposition before CAS adoption. Adoption is idempotent by immutable repository/consumer/source/object-format/OID identity. A finite set of dependencies may be retained, but the consumer authoring surface must start from one already-existing exact base that canonically contains every selected OID; ADR-081 creates no synthetic authoring-base merge.

The ordinary supported-harness path performs selection, anchoring, adoption, and exact consumer-base provisioning invisibly before first write. The human user does not construct the declaration manually or invoke the source first.

This contract does not authorize late refoundation after consumer authoring has already started from another base. It also does not choose publication topology for more than one independently unsatisfied predecessor. Those cases remain explicit open design items and fail closed only for the affected authoring/refoundation or realization transition.

### 2.5 External mutation-authority declaration

For an existing ContributionUnit editing surface, the External Control Plane provides durable mutation-access state independent of any particular `ruu` trigger:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

It owns producer/runtime quiescence and safe transfer/reacquisition semantics. Under ADR-064, when the Development System uses transferability to offer a dirty editing surface for checkpoint progression, that declaration is also a **frozen checkpoint-offer boundary**: no external writer retains mutation authority while the handoff remains current. This expresses immobility, not test/review success.

The declaration MUST satisfy the race-safety contract defined by ADR-033 as amended by ADR-041/064:

```text
transferable
+ no Ruu exclusive claim
↛ Ruu may mutate

transferable
+ exclusive claim held by the current authoritative executor/operation
+ revalidated state
→ mutation may proceed
```

While transferability remains current, the External Control Plane MUST prevent external mutation of the editing surface. If semantic authoring must resume before `ruu` obtains the claim, it MUST first revoke transferability / restore external mutation authority and only then permit writes; any prior semantic checkpoint-readiness decision is thereby stale. While `ruu` holds the exclusive worktree claim, the External Control Plane MUST prevent external reacquisition/mutation until the claim/effect reaches a safe release/recovery boundary.

A convergence trigger is not an authority token. If a caller or upstream workflow changes ContributionUnit mutation authority, that authority change MUST become durably authoritative through the External Control Plane separately from signaling `ruu` convergence demand. Concurrent triggers may therefore be coalesced without losing or merging authority semantics.

No heartbeat, TTL, process-liveness, session-liveness, or producer identity is normative to `ruu`.

ADR-024/ADR-036's trigger boundary is also explicit: an invocation principal, webhook, hook, user action, agent session, or orchestrator signal may create/coalesce convergence demand, but the trigger carries no ContributionUnit mutation authority, no semantic work ownership, and no authority to narrow the executed sweep. A session that happens to trigger discovery of unrelated review/reconciliation/settlement work does not inherit that work.

### 2.6 Promotion grouping, group-local resolution, and topology

ADR-069 removes the former separate `DeclarePromotionGroup(members)` authority for ordinary new work. Promotion grouping now follows the work-bearing logical invocation boundary from §2.4A.

For:

```text
LogicalInvocation I
  promotion_binding = NEW_GROUP
  handoffs = {CU1, CU2, ...}
```

`ruu` derives:

```text
ConvergenceMembers(I)
  = distinct(convergence_unit_of(CU) for CU in I.handoffs)
```

and creates one distinct occurrence-bound PromotionGroup. The External Control Plane does not separately decide which resulting ConvergenceUnits "go together". Distinct work-bearing invocations remain distinct PromotionGroups even when their derived member sets are identical.

The member set is immutable, unordered, unique, closed, and non-empty. `promotion_group_id` is bound to the durable logical invocation occurrence within the coordination domain; a separate canonical membership fingerprint records the member-set value. Session, branch, task, caller, policy, topology, and exact OIDs do not define PromotionGroup occurrence identity.

A PromotionGroup adopts exact **group-local** member state under expected-state/CAS guards. The exact binding is attributable to the originating invocation or to a later current `REVISE_EXISTING_GROUP(G, authority_ref)` continuation. Later unrelated ordinary authoring/reopen of the same live ConvergenceUnit does not stale or refresh an already-adopted group binding. Untouched members retain their prior exact group state during a legitimate same-group revision. A terminal PromotionGroup cannot adopt a newer resolution.

`READY_INTERNAL` alone never creates an implicit singleton. A one-member ordinary work-bearing invocation mechanically creates a one-member PromotionGroup; a multi-repository invocation may create a group spanning several repository-local ConvergenceUnits. ADR-047 partitions the adopted group-local exact mapping by authoritative source repository and materializes/reuses exactly one ADR-045 PromotionUnit per represented repository.

A valid PromotionUnit is source-repository-local: all exact member refs share one authoritative `repository_id`. Under ADR-061, all members in that same-source projection MUST also share one immutable PromotionTarget. Same PromotionGroup plus same source repository yields one projection/PromotionUnit only when target binding is coherent; conflicting same-source targets fail closed as `TARGET_INCOHERENT_PROMOTION_GROUP`.

Promotion dependency/topology is not a caller-authored publication-layout declaration under ADR-050. ADR-081 adds an earlier explicit semantic source/version selection before promotion exists; once TX-A durably records that selection, Ruu—not the caller—reconciles it against current target state or a qualifying source handoff accepted after TX-A. Promotion resolution requires the source's own exact frozen checkpoint to contain the consumed OID before downward synchronization, group-local incorporation of that checkpoint, exact equality of source/consumer immutable PromotionTargets, current source disposition, and stable `(PromotionGroup, source repository)` projection. A qualifying handoff with unequal targets yields target-incoherent reconciliation unless the consumer target independently satisfies the consumed OID; it never authorizes retargeting or a cross-target stack. Aggregate candidate ancestry alone is insufficient. A handoff accepted between TX-A and TX-B may be adopted directly as resolved during TX-B/recovery after all exact guards. Repository projection never splits one PromotionGroup projection to manufacture a stack; Ruu derives current dependency topology from adopted source provenance plus exact managed promotion-base/candidate/target lineage among already-distinct promotion obligations. When a predecessor group revision moves a parent exact state, ADR-050 restacks/reprojects descendant provider state from the child's immutable owned anchor. A clean restack does not rewrite the child group's internal exact state; semantic transplant conflict creates explicit reconciliation authority before any same-group child revision.

Promotion grouping/default mapping originates in ADR-046 but is amended by ADR-069; deterministic repository-local group projection remains ADR-047, exact repository-local multi-source candidate/head materialization ADR-048, submission identity/ref lifecycle ADR-049, derived dependency/restack semantics ADR-050, contextual provider capability discovery ADR-051, DIRECT target advancement ADR-052, review-correction continuation ADR-053, and PromotionUnit/ConvergenceUnit closure-retirement separation ADR-054.

### 2.7 Review-correction demand and semantic continuation

ADR-053 closes backlog 30.23. A current authoritative `CHANGES_REQUESTED` generation is represented as one durable idempotent review-correction demand bound to the exact reviewed submission revision/head, logical PromotionGroup/repository projection, provider review generation/fingerprint, and factual feedback payload/provenance.

Under ADR-063 this applies only to an authoritative **blocking provider-governance state**. Ordinary comments, suggestions, advisory findings, or other nonblocking provider feedback do not automatically create a ReviewCorrectionDemand, reopen a ConvergenceUnit, or block promotion. Semantic interpretation/adjudication of such findings remains external.

The same demand may be discovered either by provider webhook/event delivery or by a later `ruu` global sweep. Discovery channel/caller identity is not semantic ownership: rediscovery MUST NOT duplicate the logical correction obligation, and a session that merely triggered the sweep does not inherit unrelated review work.

The External Control Plane may restore the originating coding session or start a new continuation session. Session/runtime identity is provenance only and is not required to persist across review latency. The correction session receives the exact feedback/context as development input and may discover affected existing ConvergenceUnit scope(s) while working; no separate up-front semantic router is required.

When new implementation writes are needed, the External Control Plane explicitly reactivates the relevant existing ConvergenceUnit(s), returns contribution membership to `OPEN`, and provisions new ContributionUnits/writer surfaces. `CLOSED` ContributionUnits never reopen, and provider submission refs are not authoring workspaces. `ruu` MUST NOT infer semantic scope from review prose/blame/provenance.

Ordinary corrections of existing PromotionGroup members leave the closed immutable group unchanged. The correction Development System creates a work-bearing invocation bound as `REVISE_EXISTING_GROUP(G, authority_ref)` and authors from the exact reviewed/group-local state rather than blindly from the live current ConvergenceUnit tip. Untouched group members retain their prior exact bindings. After reconvergence, the ADR-049 logical `submission_id` remains stable when its key is unchanged: new exact PromotionUnit/candidate revisions update the same provider submission only while the current PublicationEpisode is nonterminal; ADR-055 creates a distinct later episode/provider submission if the prior episode is terminal and the same nonterminal ship still requires publication. A genuinely new ConvergenceUnit is scope expansion and cannot be appended to the old PromotionGroup.

ADR-054 closes backlog 30.24. Repository-local PromotionUnit completion does not itself retire its source ConvergenceUnit. The External Control Plane may continue ADR-053 semantic authoring on existing group members while any relevant logical ship remains nonterminal. Once every relevant PromotionGroup/promotion obligation is terminally settled and no current authoring/reconciliation demand may reopen a ConvergenceUnit, `ruu` may adopt that ConvergenceUnit's semantic `PROMOTED` boundary; operational `RETIRED` still waits for correctness-critical recovery/resource sufficiency. Later semantic work after ConvergenceUnit `PROMOTED` uses a new ConvergenceUnit identity rather than reopening historical lineage.


### 2.8 Cross-repository settlement and continuation publication

ADR-055 closes backlog 30.25. `PARTIALLY_PROMOTED` is ordinary nonterminal aggregate progress and does not itself authorize rollback or semantic work. If remaining repository-local tracks can still complete nominally, they continue normally.

When a partial ship requires semantic disposition beyond ordinary remaining-provider progress, one durable exact-generation-bound `CrossRepositorySettlementDemand` is recorded/refreshed. Provider hooks/control-plane events and later `ruu` sweeps are coequal discovery paths for the same demand; rediscovery MUST be idempotent and the discovering caller/session does not inherit the work.

The External Control Plane/Development System decides semantic `ROLL_FORWARD` versus `COMPENSATE`. `ruu` supplies exact repository/PromotionUnit/provider/target facts and never invents a revert. All resulting Git effects are ordinary **forward** development/promotion effects; authoritative targets are never reset backward to simulate rollback.

While the PromotionGroup remains nonterminal and ADR-054 permits continuation, existing member ConvergenceUnits may be reactivated and new ContributionUnits provisioned. A genuinely new ConvergenceUnit remains scope expansion and requires a different/superseding PromotionGroup.

For the `PROVIDER_SUBMISSION` target-realization route, one ADR-049 logical `submission_id` may contain multiple **PublicationEpisodes**. Revisions inside an open episode update the same provider submission. If that provider submission is terminal/consumed while the same logical submission still has a later current exact promotion obligation and the PromotionGroup remains nonterminal, `ruu` creates a new episode with a distinct submission ref/provider surface. Terminal episodes are immutable historical provider surfaces.

Normal terminal settlement is `ALL_PROMOTED` over the current exact repository projection mapping. Explicit compensation may terminalize the group as `COMPENSATED` only after the External Control Plane supplies current semantic compensation intent/completion for the exact settlement generation and `ruu` independently observes/adopts every exact forward Git/provider effect declared required by that plan. Partial promotion is never silently abandoned merely because a remaining track is difficult.

### 2.8.1 Managed authoring-binding disposition and PromotionGroup cancellation

ADR-068 introduces pre-promotion `CANCELLED`; ADR-071 establishes current-disposition causal fencing; ADR-074 corrects the classifier for native branch rename; ADR-075 fixes observation strength and backend capability. No separate ordinary `CancelPromotionGroup(G)` command/API is required.

For a ref already durably registered as the current managed authoring binding for live managed work, every native mutation capable of terminating/replacing that binding MUST cross a conforming native-ref adapter point before causal linearization. The adapter establishes exact native facts and the core durably records:

```text
AUTHORING_BINDING_TRANSITION_PREPARED
+ TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED
```

If normalized evidence is `UNKNOWN`, the ambiguous managed binding mutation does not silently linearize. `reference-transaction` is one implementation primitive used by the currently demonstrated `files` adapter, not the normative architecture.

After a proven committed outcome, exact causal evidence establishes one of:

```text
CONTINUATION
→ RENAME_CARRY_PREPARED + native successor continuity
→ update the managed binding generation/ref
→ no CANCEL

ABANDON
→ TERMINAL_REMOVAL_PREPARED + terminal binding cessation committed
→ current CANCEL disposition for still-unrealized associated ship obligations
```

Failure to prove continuation never implies abandonment.

OID equality, tree similarity, ancestry, or another branch created/copied from the old branch is never continuity authority. `git branch -c foo bar` followed by deletion of `foo` abandons the managed line bound to `foo`; `bar` remains an ordinary separate branch unless a valid explicit binding/recovery decision later says otherwise.

Unmanaged branch/ref deletion remains ordinary Git. Worktree deletion alone remains ordinary artifact lifecycle and is not cancellation. A plain worktree `HEAD` switch while the managed ref still exists is a topology mismatch, not an automatic rebind. Deletion after the associated ship is already successfully promoted does not rewrite historical success.

While a committed managed-binding transition is unresolved, ADR-071's causal authorization fence forbids new irreversible managed realization whose legality depends on whether the line remains live.

Managed authoring refs require native reflog evidence infrastructure before first managed write. A later missing reflog may be repaired only when no unresolved transition requires lost historical evidence; recreating it never reconstructs the past. If native evidence is irretrievably insufficient, §2.4B provides the exceptional generation-bound `AuthoringBindingRecovery` path.

ADR-076 keeps native causal provenance internal to `ruu`/the native-ref adapter. A native witness does not require human/agent/IDE actor attribution. Optional trusted correlation to a managed `Attempt` is explanatory only and never substitutes for current authority, exact Git facts, binding generation, or CAS. The External Control Plane is not required to identify who issued an ordinary native Git command merely so the resulting Git fact can be reconciled.

If a promotion effect was already causally committed before a resolved abandonment, recovery observes/adopts that history. If one or more effects were already realized, ADR-055 partial/successful settlement remains authoritative and abandonment cannot erase them or invent compensation. If an unmanaged external realization races with abandonment and authoritative causal ordering is genuinely unprovable, terminal semantic classification fails closed rather than using independent wall clocks to invent order.

PromotionGroup membership never changes. A replacement ship is represented by a distinct later group occurrence; historical terminal groups remain immutable. PR `CHANGES_REQUESTED` continues under ADR-053 correction semantics, and a provider PR closed/rejected without merge is only a terminal non-realizing publication fact.

### 2.9 Development-quality validation and transition-local fact boundary

ADR-057/060 make development-quality verification execution entirely an External Control Plane / Development System concern. `ruu` does not run or schedule repository tests, lint, builds, formatters, generators, security analysis, agentic review, flaky-test retries, external-service tests, or validation-worker capacity, and it does not consume a generic development-validation certificate afterward.

The external system may use any such process before it offers dirty work for checkpointing, closes a ContributionUnit, seals/declares higher-level lifecycle state it owns, or establishes exact review-request intent. The reasons for those decisions remain outside `ruu` unless a particular Git/provider transition already has a narrow authoritative external fact defined by this contract.

`ruu` evaluates each transition from its own exact Git/managed/provider state plus only the transition-specific External Control Plane facts it genuinely needs. Examples include mutation-access transferability, ContributionUnit `CLOSED`, ConvergenceUnit membership `SEALED`, PromotionGroup membership, review-request intent, settlement intent, and other explicitly defined declarations.

When `ruu` deterministically synthesizes a clean exact Git candidate, it does not create a generic validation demand. The candidate may progress when the exact transition-local topology/claim/conflict/policy/provider prerequisites hold. If semantic authoring is actually required, the existing transition-specific obligation (`RECONCILIATION_REQUIRED`, review correction, settlement continuation, policy contradiction, etc.) is exposed to the Development System.

A later externally authored result receives no inherited authority merely because an external tool claims to have fixed or validated it. It re-enters ordinary exact current-state observation and transition-local claims/CAS/policy/provider guards.

### 2.10 Reconciliation obligation delivery to the Development System

When `ruu` encounters a conflict that cannot be resolved by deterministic Git/repository mechanics without semantic code authoring, it emits a durable exact-state-bound:

```text
RECONCILIATION_REQUIRED
```

The **Development System** is the external authoring capability able to modify code (for example an agent runtime, coding agent, human, or tooling). It is a role and may be implemented by the same components as the External Control Plane or by separate tooling.

The External Control Plane MUST make active `RECONCILIATION_REQUIRED` obligations visible/actionable to the Development System, including the exact conflict descriptor supplied by `ruu`. The External Control Plane/Development System chooses how authoring is performed; `ruu` does not choose a resolver or author the semantic fix.

The reconciliation descriptor is diagnostic only. A claimed/resolved status from external tooling MUST NOT authorize adoption. Any authored state returns through ordinary current-state observation/revalidation and claims/CAS plus the transition-local prerequisites for the resulting state.

### 2.11 Promotion-policy contradiction delivery to the external system

When authoritative promotion-policy inputs are jointly unsatisfiable, `ruu` emits a first-class machine-readable `POLICY_CONTRADICTION` / `policy_state=CONTRADICTORY` blocking diagnostic.

The External Control Plane MUST make the active contradiction visible/actionable to the external Development System/operator. The diagnostic contains factual provenance sufficient to reconstruct the contradiction, including the affected repository/obligation, conflicting dimension(s), normalized incompatible constraint/fact values, and exact source identities/revisions/fingerprints where available.

The diagnostic MUST NOT contain a recommended fix, candidate remediation set, ranked next action, or suggested governance/policy mutation. `ruu` and the External Control Plane do not decide how the contradiction should be resolved merely from the diagnostic; the external Development System/operator interprets the facts and independently decides what, if anything, to do.

A downstream claim that the contradiction is “resolved” is not authorization. `ruu` re-observes current authoritative policy/provider facts and reconstructs a `CURRENT` effective policy before any promotion can proceed.

### 2.12 Promotion-policy staleness / concurrent provider-drift delivery

If immediate pre-mutation revalidation detects changed authoritative policy/provider inputs, the prior policy snapshot becomes `STALE` and the affected mutation does not proceed until policy is recomputed. If a provider changes concurrently after revalidation and rejects or otherwise changes the exact outcome of a non-atomic provider mutation, `ruu` exposes the exact observed rejection/current provider state as factual machine-readable evidence.

The External Control Plane makes that blocking/current-state evidence available to the external Development System/operator. As with policy contradiction delivery, neither `ruu` nor this contract infers a remediation or treats a retry/override request as authorization; later progress requires ordinary current-state re-observation and policy revalidation.

### 2.13 Provider-submission review-request publication-intent boundary

ADR-032's pre-ADR-039 boundary is explicit here and generalized by ADR-062. `REVIEW_REQUESTED` is an exact-submission-revision publication/governance assertion, not something `ruu` may infer merely from `READY_INTERNAL`, provider-submission existence, or an agent/session becoming idle. When the configured submission-author/ship-ready gate requires non-Git authoring/governance facts, the external system/policy establishes the exact-revision-bound intent/facts required by current policy before formal review-request mutation.

ADR-057/060 move the exact composition/execution of the ship-ready gate outside `ruu`: repository governance / the Development System decides what tests, reviews, security checks, documentation checks, or other semantic processes justify the assertion. ADR-062 closes former backlog 30.36: exceptional `REVIEW_NOT_REQUESTED` publication requires explicit current authority/need; if neither that authority nor `REVIEW_REQUESTED` is established, no provider submission is created merely to manufacture a draft/provider object.

### 2.14 Runtime requests cannot manufacture promotion authorization

ADR-026's repository-policy boundary, as strengthened by ADR-043/044/061, is explicit here. A user, agent, session, orchestrator, local config, or later External Control Plane request may express workflow intent but cannot override current authoritative provider/organization governance, trusted target-baseline repository policy, contextual capability facts, or the immutable PromotionTarget already bound to an authored ConvergenceUnit. The External Control Plane may surface contradictions/drift and may arrange semantic remediation, but promotion authorization is reconstructed from current authoritative sources by `ruu`; a runtime declaration such as “push direct”, “skip review”, “force this provider submission/PR”, or “send this existing ConvergenceUnit to another branch” is never sufficient authority by itself.

### 2.15 Semantic review findings and backlog projection

ADR-063 makes semantic review findings and backlog management explicit External Control Plane / Development System responsibilities. A semantic finding may be adjudicated externally as `FIX_NOW`, `DEFER`, `ACCEPT`, or `REJECT` (exact external vocabulary is not normative to `ruu`).

For `DEFER`, the external system may project the finding to a durable tracker object such as a GitHub Issue, GitLab Issue, Jira/Linear item, Notion task, or internal backlog record. The tracker object SHOULD preserve provenance such as origin review, exact candidate/commit/tree context, repository/path/symbol when relevant, observation/risk, reason deferred, and acceptance conditions. A provider submission/PR is not kept open merely as a backlog reminder.

When deferred work is later re-injected into coding, the Development System revalidates the finding against current code before authoring. Stale/resolved findings may be closed/superseded without creating Git work; still-applicable findings enter ordinary new Work/ContributionUnit authoring.

`ruu` does not interpret review prose, decide finding severity, create/prioritize tracker issues, schedule future coding work, or treat a deferred semantic finding as a hidden provider approval requirement. A genuinely blocking current provider `CHANGES_REQUESTED` state remains governed by §2.7/ADR-053 regardless of external `DEFER` intent until provider/repository governance is legitimately satisfied.

### 2.16 Provider transformation / route-conformant final target realization trust boundary

Provider-governed finalization may legally rewrite Git identity through squash, rebase-style merge, merge queue, or equivalent provider mechanics. The External Control Plane does not need to provide a semantic diff-equivalence certificate for that rewrite.

The authoritative provider path is:

```text
repository/provider governance
→ authorizes the provider-mediated route/mechanism

Ruu projection mechanics
→ bind immutable PromotionCandidate C to exact submitted revision H

provider adapter
→ bind exact submitted revision H to exact final result R on exact target T

Ruu Git observation
→ independently prove R is equal to or an ancestor of current authoritative target O
```

Candidate ancestry in target is not a substitute for provider-route provenance when `PROVIDER_SUBMISSION` is required. Conversely, DIRECT promotion remains compatible with ordinary user/agent Git use: Ruu need not prove that its own process personally caused a legitimate direct target fast-forward.

For policy drift/recovery, old authorization may explain/adopt an effect proven committed while that authorization applied; it never authorizes a new action capable of causing/re-causing the effect. Provider commitment is durable provider acceptance of the exact finalization operation; DIRECT commitment is the direct target mutation itself. Indeterminate commitment timing across route/policy drift fails closed.

The External Control Plane may retain richer governance/audit metadata, but it is not responsible for interpreting code semantics or proving patch/program equivalence across `C`, `H`, and `R`.

### 2.17 Local Git, remote Git, and provider observation authority boundary

ADR-080 keeps observation authority source-scoped. The External Control Plane MUST NOT treat a local native-Git hook, a local remote-tracking ref, a provider webhook, or a provider API response as interchangeable proof.

```text
LOCAL_GIT
→ local repository/worktree/ref/object truth
→ managed authoring-binding causal observation only on the admitted local mutation surface

REMOTE_GIT
→ current authoritative remote refs/OIDs and exact-preconditioned remote effects

PROVIDER
→ optional provider-owned workflow/governance/finalization facts
```

`refs/remotes/*` are local cache state. Current remote-ref authority comes from a direct admitted remote observation. A provider endpoint is not required for provider-free Git routes; if policy requires a provider-owned semantic operation and no provider capability exists, that transition is unsupported/blocked rather than inferred from Git refs.

Webhook/event delivery is not a completeness or global-ordering authority. Authenticated provider payloads MAY be retained as positive provider-scoped historical evidence when exact semantics are demonstrated, but absence of delivery proves nothing, delivery identity is not managed semantic identity, and correctness MUST NOT generically depend on receiving a particular webhook. Cross-source chronology is established only from source-owned exact identities/revisions/operation results with documented semantics; wall-clock ordering is insufficient.

Remote publication/submission artifact deletion or rename-like topology never directly causes local managed-authoring `ABANDON | CONTINUATION`. Historical provider finalization evidence and current remote/target Git topology remain separate facts.

## 3. Guarantees consumed by `ruu`

When `ruu` consumes External Control Plane state, it may rely on the following declarations as normative **logical intent**, subject to ordinary exact-state revalidation where Git/provider facts are involved:

```text
managed repository admission/reactivation is durable before managed writes; ACTIVE_CONVERGENCE_SET is non-authoritative derived acceleration only
v1 active ContributionUnit authoring is provisioned on one dedicated Git worktree/ref surface before first managed write; no direct arbitrary commit/tree/snapshot authoring substrate bypasses that topology
ContributionUnit identity is opaque, stable, and the sole v1 authoring-occurrence identity; work_occurrence_id is not a second domain key
an AuthoringDependency exists only from explicit pre-edit Development System selection of stable source ContributionUnit + exact commit OID, followed by Ruu exact Git proof and durable anchor adoption; no selection means no inferred dependency
ordinary native commit creation is exact Git state, not managed checkpoint/handoff/completion; a clean tip becomes a managed checkpoint only through exact frozen-handoff adoption
dirty producer state is never an exact dependency version or an implicit snapshot
repository identity binding is singular and stable; the current host-local locator may be explicitly relocated without changing repository_id
ConvergenceUnit binding is singular and stable
ConvergenceUnit PromotionTarget is bound before first managed write and immutable for that identity
ConvergenceBase and PromotionTarget are distinct concepts; current target OID may advance without changing target identity
ContributionUnit CLOSED never reopens under the same identity
ConvergenceUnit membership OPEN/SEALED changes are explicit
mutation-access state is authoritative for external ownership and is independent of convergence-trigger identity
exceptional AuthoringBindingRecovery is expected-old/generation-bound logical recovery authority only; Git facts remain independently revalidated
demand/discovery trigger identity carries no mutation authority, semantic work ownership, or sweep-scope authority; a work-bearing LogicalInvocation separately carries one durable sealed ContributionUnit cohort and promotion binding
ordinary PromotionGroup membership is closed/immutable and mechanically derived from the sealed LogicalInvocation cohort through stable ContributionUnit→ConvergenceUnit bindings; distinct logical invocations remain distinct group occurrences even with identical members; every same-source projection is PromotionTarget-coherent; current PromotionTopology/dependency is mechanically derived from adopted authoring provenance plus exact promotion-base/predecessor/target facts under ADR-050/081, not caller publication intent
review-request intent/facts are explicit and exact-revision-bound; internal readiness alone never manufactures REVIEW_REQUESTED; absence of both REVIEW_REQUESTED and explicit early-publication authority means no provider projection yet
settlement semantic intent is external while every claimed Git/provider effect remains independently observed/adopted
```

Unknown, contradictory, missing, or multiply-bound logical state that is required for a transition MUST fail closed for that obligation.

Failure or ambiguity in one obligation MUST remain localized and MUST NOT stop unrelated progress during the global sweep.

## 4. Responsibilities retained by `ruu`

The External Control Plane contract does **not** move Git convergence mechanics upward. `ruu` remains responsible for the Git/provider side of progression, including:

```text
global discovery/re-evaluation of known nonterminal managed obligations
exact local-Git / remote-Git / provider observation and revalidation under source-domain authority
fine-grained resource claims / CAS guards under the current fenced executor
transition-local external-fact binding/currentness checks
managed checkpoint adoption of an exact clean native tip, or checkpoint creation for a dirty surface, only at a frozen safely claimable handoff
AuthoringDependency exact-object/source-lineage verification, recoverable anchor creation, durable adoption, target/same-group/source-handoff reconciliation, and localized realization blocking
ContributionUnit candidate attribution by valid mutation-authority boundary (not process identity)
ContributionUnit ↔ ConvergenceUnit synchronization/integration
conflict detection, exact `RECONCILIATION_REQUIRED` recording/refresh, and deterministic clean reconciliation
ConvergenceUnit READY_INTERNAL computation for the live convergence lineage
LogicalInvocation acceptance/seal validation and mechanical NEW_GROUP membership derivation
PromotionGroup group-local exact-state adoption/revision under snapshot/CAS and explicit group-bound continuation authority
content-addressed PromotionUnit materialization/reuse after same-source PromotionTarget coherence validation
ADR-048 exact repository-local promotion-candidate materialization from current base + exact sources toward the immutable PromotionTarget
promotion/submission publication materialization, including ADR-055 per-episode provider surfaces for one stable logical submission
remote publication under repository policy
provider-submission/check/review/merge-queue/finalization state refresh
provider target-integration/finalization effect progression when REQUIRED ∩ SUPPORTED ∩ AUTHORIZED and fully preconditioned; explicit human authority waits only when governance actually requires it
exact cross-repository partial-progress/settlement-demand recording and refresh
final target-integration observation/proof
recovery of operations already owned by Ruu
transactional ingestion/recovery of managed-authoring binding transitions under ADR-071/074
localized BLOCKED_MISSING_MANAGED_STATE when a still-required exact OID is unrecoverable
```

Every global sweep that services outstanding convergence demand remains global over the complete known set of nonterminal managed obligations as defined by ADR-036/ADR-041. Explicit invocations may coalesce; External Control Plane grouping, caller identity, or trigger origin MUST NOT narrow that sweep.

## 5. Responsibilities explicitly outside `ruu`

`ruu` does not decide:

```text
what a task/feature/product intent means
which agent/session/process is the producer identity
whether an agent turn is finished
why a ContributionUnit should exist
when semantic work is complete, except by consuming declared lifecycle
which experiment should be preferred
whether unwanted code should be kept, modified, or deleted
when a user/agent should create/delete a branch or worktree
whether local branch absence means remote deletion
why an unmanaged branch/worktree was deleted; ADR-071/074/075 assign managed disposition semantics only after a currently bound managed-authoring transition is pre-linearization captured and positively resolved
how producer-runtime liveness/quiescence is implemented
how semantic conflict code is authored/resolved inside the Development System
whether/why a new repository is semantically needed beyond consuming the current RepositoryCreationPolicy request/result
which ContributionUnits the Development System includes in one work-bearing invocation cohort (that is supplied explicitly; Ruu does not infer it)
which exact source ContributionUnit/version a consumer semantically requires (that is explicitly selected; Ruu does not infer it from ancestry or other incidental facts)
why a newly created ConvergenceUnit should target one repository/ref rather than another (the External Control Plane owns that pre-authoring intent)
which ConvergenceUnit review feedback semantically refers to
whether a partially promoted logical ship should roll forward or compensate
what semantic code/data/runtime action constitutes a safe compensation
how tests/lint/build/formatters/codegen/security checks/agentic review are executed or retried
how development-validation compute capacity, flaky tests, external-service tests, or validation artifacts/caches are managed
how semantic review findings are interpreted/adjudicated, projected into backlog issues, prioritized, revalidated, or scheduled for future coding
```

Unwanted code is represented by subsequent development Git state. Development-artifact lifecycle actions remain user/agent/External-Control-Plane tooling concerns unless a separate accepted ADR explicitly moves a specific mechanism into `ruu`.

## 6. Interface discipline

Any future architecture decision that says a “higher-level subsystem”, “orchestrator”, “provisioner”, “caller”, “agent runtime”, or similar external actor **MUST** provide information or guarantees to `ruu` must do one of the following:

1. map that requirement to an existing clause in this contract; or
2. amend this contract explicitly through an ADR.

No vague external dependency may become a hidden precondition of `ruu` correctness.

Implementation mechanisms remain intentionally unspecified unless correctness requires otherwise. Under ADR-041, v1 `ruu` coordination is single-host; a future multi-host design would require an explicit new coordination decision while preserving this logical contract.

## 7. Related decisions

This contract consolidates the external boundary established across:

- ADR-014 — non-atomic cross-repository promotion and higher-level coordination;
- ADR-022 — managed repository registry/admission and derived active-set boundary;
- ADR-023 — pre-edit provisioning;
- ADR-024 — invocation principal distinct from mutation authority;
- ADR-026 — repository-policy-driven promotion authority;
- ADR-027 — convergence, promotion-unit, and topology separation (ordinary group membership is later derived from the externally supplied ADR-069 handoff cohort; topology is mechanically derived by ADR-050/081);
- ADR-032 — provider-submission review-request publication-intent boundary (historically PR terminology);
- ADR-033 — external mutation authority;
- ADR-034 — opaque repository-local ContributionUnit identity;
- ADR-035 — bounded ContributionUnit lifecycle authority;
- ADR-036 — global sweep scope independent of caller/trigger;
- ADR-037 — ConvergenceUnit grouping/membership authority;
- ADR-038 — editing-artifact lifecycle outside `ruu`;
- ADR-046 — historical PromotionGroup introduction, with ordinary declaration/identity/resolution amended by ADR-069;
- ADR-047 — deterministic repository-local PromotionGroup projection;
- ADR-048 — deterministic repository-local multi-source candidate materialization;
- ADR-053 — durable session-independent review-correction continuation;
- ADR-054 — PromotionUnit completion / ConvergenceUnit semantic closure-retirement separation;
- ADR-055 — partial cross-repository settlement and publication-episode continuation;
- ADR-061 — immutable pre-authoring ConvergenceUnit PromotionTarget binding and policy HOW/WHERE separation;
- ADR-062 — route-independent promotion and provider-submission projection semantics;
- ADR-063 — semantic findings/backlog boundary;
- ADR-064 — frozen pre-commit mutation handoff and exact checkpoint identity bridge;
- ADR-071 — transactional managed-authoring-ref abandonment ingress and current-disposition causal authorization fencing;
- ADR-073 — dedicated Git worktree/ref surface as the normative v1 active-authoring substrate;
- ADR-079 — minimal native observation rejection, conservative protection filtering, and exact initial binding admission;
- ADR-080 — source-scoped local Git / remote Git / optional provider observation authority;
- ADR-081 — explicit exact authoring-source selection, durable OID retention, pre-promotion dependency reconciliation, and no authority transfer;
- ADR-056 — new-repository creation authorization, bootstrap admission, provider attachment, and provisioning recovery.

ADR-039 makes this file the normative consolidated interface for those external responsibilities without changing the underlying Git safety rules. ADR-081 adds only semantic selection of a stable source ContributionUnit and exact native commit before consumer authoring; Ruu retains responsibility for exact proof, object anchoring, dependency adoption/compression, target satisfaction, and publication blocking. ADR-080 further makes local Git, remote Git and provider workflow evidence separate source-authority domains; provider capability remains optional for provider-free remote Git routes and generic webhook delivery is never completeness authority. ADR-075 adds pre-authoring native-ref observation-capability admissibility without making the External Control Plane the source of Git truth. ADR-077 makes that admissibility repository-common and functionally attested for an admitted mutation-engine/adapter profile, with non-destructive hook/config ownership and coverage epochs. ADR-055 performs a retrospective contract audit and makes explicit several already-accepted pre-ADR-039 boundaries that had remained only implicit/scattered; it does not change their underlying semantics. ADR-056 adds the previously open repository-creation/bootstrap boundary without making `ruu` a repository provisioner. ADR-062/063 further separate provider projection/finalization from semantic promotion and keep review findings/backlog outside the Git convergence core. ADR-064 makes pre-commit semantic-readiness identity a mutation-authority immobility contract rather than a generic validation-evidence dependency. ADR-065 introduced final target-realization proof; ADR-066 supplies the current controlling provider chain `C → H → R → O`, requiring exact candidate-to-submission projection, exact provider finalization, and independent Git observation of `R` in the authoritative target.

- ADR-057 — external development-validation execution and state-dependent Git progression boundary;
- ADR-060 — transition-local prerequisites replace generic development-validation evidence/demand.
