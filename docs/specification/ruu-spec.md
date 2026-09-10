# Ruu — Requirements, Invariants, and Architectural Implications

# 0. Product intent — governing user experience

This section is normative, ratified by **ADR-070**, and strengthened by **ADR-078** and **ADR-081**. It states the product outcome that the technical invariants below exist to serve. If a lower-level architectural rule admits several interpretations, the interpretation that preserves this product intent while satisfying the applicable safety invariants is required. If a prior technical clause directly conflicts, ADR-070 supersedes that clause to the minimum extent necessary. A future change to this product promise must explicitly amend ADR-070 and update this section in the same decision.

## 0.1 Product definition: agentic version control built on Git

`ruu` is **Git-based version control redesigned for agentic software development**.

Git remains the native object/history substrate and interoperability boundary. Commits, trees, refs, ancestry, merges, object identity, and ordinary Git operations keep their native meaning; `ruu` does not replace Git with an incompatible VCS. What it redesigns is the version-control model around Git for a world in which many coding agents/sessions can author concurrently, from different repositories, across several repositories, against shared logical lineages, without a human continuously coordinating branch order, freshness, collisions, retries, or publication topology.

The core product is therefore **agentic version control**, not merely a GitHub/PR orchestrator and not merely a commit/push wrapper. Its core concerns include isolated concurrent work production, durable checkpoint/invocation boundaries, exact version identity, cross-session/cross-repository convergence, mechanical stale-state reconciliation, conflict localization, crash/retry recovery, and coexistence with ordinary Git.

Remote hosting and provider-facing publication are an **extended feature layer over that core**. Pull requests, stacked pull requests, merge queues, protected-branch APIs, provider review state, and provider-specific publication topology project or realize already-defined exact version/convergence state outward. They are important supported capabilities, but they do not define the identity of `ruu`, just as GitHub/GitLab extend Git rather than define Git itself. Native Git remote transport may still be used as a transport primitive.

This dependency direction is normative:

```text
agentic version-control semantics
        ↓
exact native Git state / history
        ↓
optional route/provider realization
(PR, stack, merge queue, protected target, etc.)
```

A deployment with no provider API must still retain a meaningful `ruu` core that can checkpoint, version, integrate, reconcile, and converge concurrent managed work as native Git state. Conversely, provider objects MUST NOT become the source of core version identity or convergence truth when those facts can be established independently in Git/managed state.

ADR-080 further separates observation authority: local Git causality, current remote Git refs, and provider workflow/finalization facts are distinct source domains. A bare Git remote is a first-class remote endpoint; provider APIs/webhooks are optional capabilities used only by transitions whose semantics actually belong to a provider.

## 0.2 The product promise

`ruu` exists so that **concurrent agentic development does not require the user to manually orchestrate Git convergence**.

The target experience is literally:

```text
Session A starts coding from one managed repository.
Session B starts coding from another managed repository.
Session C starts coding from a third managed repository.

Any session may touch one repository or several.
Different sessions may eventually touch the same repository,
the same ConvergenceUnit, or overlapping files.

When one session considers its current block of work ready:
  ruu

The user keeps working in the other sessions.
They may invoke ruu too, in any order.
```

The governing promise is:

> **A user may run multiple coding sessions concurrently, from any already-managed repository in the coordination domain. Each session may touch one or several repositories and may overlap work produced by other sessions. When that session considers its current work ready to cross a Git boundary, it invokes `ruu` from whichever managed repository it is currently in. The user does not manually coordinate repositories, session ordering, stale bases, PromotionGroups, dependency topology, or mechanically resolvable collisions. `ruu` discovers/re-observes durable managed state, reconciles what can be reconciled mechanically, and advances the global Git/provider state safely. Only a genuinely semantic incompatibility or missing external authority is returned to the Development System for authored/semantic action.**

At the ordinary interaction boundary, `ruu` behaves like a **hands-off, state-dependent super Git command**: the Development System decides when work is ready to cross a Git boundary; `ruu` owns the rigorous version-control progression after that boundary, including provider publication when the selected route requires it. This describes the invocation experience, not a narrower definition of the product.

## 0.2A Zero-preflight harness-integrated authoring is normative

The ordinary product experience MUST NOT require the user to initialize each unit of work with a separate `ruu` start/provisioning workflow. For a **supported coding harness** (for example Pi, Claude Code, Codex, or another integrated agent runtime), the normative experience is:

```text
install Ruu once
(the installation may register supported-harness adapters)

launch the supported coding harness
→ tell the agent what to implement
→ author normally

when the user or agent wants the current block to cross the Git boundary:
  ruu
```

Before the first managed write in each repository touched by that coding session, the harness integration MUST automatically cause the required pre-edit managed-authoring state to exist. Depending on current durable state, this includes creating/adopting the appropriate ContributionUnit/ConvergenceUnit bindings, any explicitly selected exact authoring dependencies, managed ref/worktree, mutation authority, repository-common observer coverage, and opaque coordination identities/handoffs required by the architecture. These mechanisms are internal product plumbing, not user-facing workflow steps.

When new work needs an exact native commit from another still-active managed ContributionUnit, the Development System/harness selects the exact source ContributionUnit and commit. The user does not construct an AuthoringDependency or invoke the source first. Ruu adopts and retains that exact relation before consumer authoring; it never substitutes the producer's dirty worktree or follows a later moving source tip.

The **External Control Plane / Development System remains an architectural authority role**, not necessarily a separately installed product. A conforming Ruu distribution MAY implement that role in part through Ruu-supplied integrations for supported coding harnesses. Semantic authority is unchanged: the integration may materialize declared work topology safely, but it MUST NOT make Ruu infer task meaning, semantic completion, grouping, or validation intent that belongs to the Development System.

The phase boundary remains strict:

```text
pre-edit integration/provisioning
→ must complete before first managed write

ordinary later `ruu` invocation
→ checkpoints/converges already-managed work
→ MUST NOT retroactively create the isolation/observer guarantees that should have existed before editing
```

Therefore a design is non-conformant if its ordinary supported-harness workflow requires the user to run commands such as `ruu start`, `ruu create-cu`, or `ruu provision`, manually install observer hooks per repository, operate a second control-plane product, or understand internal CU/ConvergenceUnit/binding identities before asking an agent to implement work. Administrative, diagnostic, recovery, or testing interfaces MAY expose such primitives, but they are not the ordinary authoring contract.

## 0.3 Invoke anywhere: CWD is not orchestration truth

For already-managed work:

```text
CWD != work-bearing invocation cohort
CWD != repository convergence scope
CWD != global reconciler sweep scope
```

If a session has touched repositories `frontend`, `backend`, and `schema`, the user must be able to invoke `ruu` while currently located in any managed repository from which the coordination domain is discoverable. The user does not first change to a privileged root repository and does not enumerate the other repositories manually.

The Development System / External Control Plane supplies the durable ADR-069 work-bearing LogicalInvocation and its sealed ContributionUnit handoff cohort behind the ordinary invocation. That cohort records **which new work belongs to this checkpoint occurrence**. The resulting convergence demand still drives a global fixed-point sweep over all known nonterminal managed obligations, including unrelated older work.

An unknown/unmanaged repository is not silently registered merely because the **later `ruu` command** is run there; repository admission remains an explicit authoritative transition under ADR-022/056. Under ADR-078, a supported harness integration may perform that transition automatically before first managed authoring when an existing repository is admissible. No separate user-facing `Ruu init/register` step is implied. The product requirement is that **no already-managed repository is privileged as the semantic command scope**.

## 0.4 Several coding sessions may run concurrently without a human mutex

Concurrent sessions are not an exceptional mode. They are a primary use case.

The user must not have to reason:

```text
"Is another session already converging?"
"Should I wait for it?"
"Which invocation must go first?"
"Will these sessions collide?"
"Do I have to lock this repository before I run Ruu?"
```

Simultaneous explicit invocations may safely coalesce as ADR-041 convergence demand while distinct ADR-069 work-bearing LogicalInvocations remain distinct durable work occurrences.

The internal architecture absorbs operational concurrency using isolated ContributionUnits, exact state, claims/CAS, durable observations, append-only integration, recovery, and fixed-point reconciliation. **The user is not the concurrency-control mechanism.**

## 0.5 The ordinary invocation does not ask the user to reconstruct internal topology

The intended ordinary interaction is approximately:

```text
implement
implement
implement

ruu
```

not:

```text
ruu --repos frontend,backend,schema \
             --group ... \
             --depends-on ... \
             --base-generation ...
```

The user must not ordinarily have to declare facts that the Development System already knows or that `ruu` can derive from durable managed/Git/provider state, including:

```text
which repositories the current work cohort touched
which ConvergenceUnits go together in the new PromotionGroup
which other session must converge first
which stale base generation to use
which raw authoring-dependency object or later dependency/stack topology should exist
which PR/submission shape should be created
whether another invocation is currently executing
```

Diagnostic and exceptional recovery commands may expose internal identities, but those identities are not the normal product-level orchestration interface.

## 0.6 Stale work and collisions are normal convergence inputs

A session may begin from an exact state that is no longer globally current when it later invokes `ruu`. Another session may have advanced the same ConvergenceUnit in the meantime.

That is expected:

```text
stale relative to newer managed work
!= ordinary product failure
```

The user should not have to pre-emptively pull/rebase/refresh merely because another managed session exists. At the authorized handoff/convergence boundary, `ruu` re-observes current reality and mechanically preserves/reconciles owned effects whenever exact Git semantics make that possible.

Depending on the state, that may use ordinary append-only merge/integration, exact candidate materialization, provider reprojection/restack, exact-state transplant, target CAS/fast-forward, or another already-defined deterministic mechanism.

If two changes are mechanically compatible, they converge without user orchestration.

If they are genuinely semantically incompatible, `ruu` does **not** guess. It emits/localizes an exact reconciliation obligation and returns authored/semantic work to the Development System. The promise is:

> **no avoidable manual coordination**, not "semantic conflicts cannot exist".

## 0.7 "Keep everything updated" does not authorize surprise mutation of active sessions

The hands-off experience must not be implemented by secretly rebasing or rewriting a producer-owned active worktree behind the producer's back.

While a Development System owns mutation authority over an active ContributionUnit, ADR-009/033/064 remain controlling: `ruu` does not mutate that editing surface without the explicit frozen handoff/claim boundary.

Concurrency is handled by **isolation plus reconciliation at exact controlled boundaries**, not by sharing mutable checkouts. When semantic authoring must resume after a conflict or correction, the Development System receives an exact state/obligation from which to continue.

## 0.8 Native Git remains ordinary and usable

`ruu` must coexist with normal Git rather than replace Git with a proprietary hidden protocol.

Users and agents may still create/delete branches and worktrees, make ordinary commits, inspect refs, and perform legitimate Git operations. Those actions retain their native meaning unless an explicit managed authority boundary says otherwise. `ruu` observes, adopts, reconciles, or reports resulting state according to the exact-state rules.

ADR-071/074/075 make one deliberate product-level specialization: when a branch/ref is already registered as the **current managed authoring ref** for live managed work, any native mutation capable of terminating or replacing that binding is a correctness-critical **binding-disposition transition**. A conforming native-ref adapter must expose a vetoable/equivalently causally serialized pre-linearization point and durably normalize the native evidence before the binding change may commit. The core derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`; `UNKNOWN` cannot silently linearize. Proven native rename/rebind means `CONTINUATION`; positively proven terminal removal means `ABANDON`. OID/ancestry similarity never substitutes for continuity proof. Unmanaged branch deletion and worktree deletion remain ordinary artifact operations with no cancellation meaning.

ADR-079 additionally constrains failure behavior: only native transactions whose cessation/replacement candidates cannot be proven safe or whose required current-binding preparation cannot be made crash-durable may be vetoed for observation correctness. Ordinary non-cessation ref/tip movement remains fail-open to exact-state rediscovery; outcome callbacks and advisory wakeup/log/telemetry persistence never become a reason to retroactively reject Git. A repository-common conservative `ManagedRefProtectionFilter` may accelerate the negative case but never replaces the authoritative managed binding state.

## 0.9 Semantic authority remains outside the engine

The product does not become hands-off by making `ruu` guess semantic intent.

`ruu` does not decide:

```text
whether the code is good enough
whether a feature/task is semantically complete
whether review feedback has been satisfied
whether product scope should change
whether an ambiguous conflict should prefer one authored meaning
```

Those decisions remain with the Development System / External Control Plane / authorized human or policy source.

The product boundary is:

```text
Development System:
  implement + validate + decide "this block is ready"

                ↓ Ruu

Ruu:
  checkpoint + integrate + reconcile + publish + recover
  until fixed point or exact semantic/external obligation
```

## 0.10 Product-intent conformance rule

A proposed architecture or implementation is not product-conformant if ordinary safe use requires the user to perform avoidable orchestration such as:

```text
run an explicit start/create-CU/provision command before ordinary supported-harness authoring
operate a second control-plane/provisioner product merely to begin managed coding
manually install or maintain Ruu observer plumbing per repository
reconstruct internal ContributionUnit/ConvergenceUnit/binding identities before implementation
serialize otherwise-independent coding sessions
choose a privileged repository from which correctness depends
manually enumerate every repository in the cohort
manually construct PromotionGroup membership
manually declare stack/dependency topology already derivable from exact state
manually order invocations for correctness
repair routine stale bases before invoking when mechanical reconciliation exists
act as a mutex around concurrent Ruu calls
```

Fail-closed behavior remains required for unknown/inconsistent authority and irreducible semantic conflict. But **fail-closed is not a substitute for implementing mechanical reconciliation that the architecture can safely determine**.

The reference product-conformance scenario is:

```text
A, B, and C are coding concurrently.
They may touch overlapping managed state.
A invokes Ruu from its current managed repo.
C invokes while B continues authoring.
B invokes later from another managed repo.

No user-level mutex.
No caller-authored global repo list.
No caller-authored PromotionGroup/stack topology.
No correctness dependency on invocation order.
Mechanically resolvable staleness/collisions converge automatically.
Only irreducible semantic work is escalated.
Repeated reconciliation drives managed Git/provider state to a safe fixed point.
```

A design is also non-conformant if it makes provider objects such as pull requests or merge queues the source of core version identity/convergence truth where those facts can be established provider-independently. Provider publication extends and realizes the core; it does not define the core.

The technical sections and ADRs that follow are mechanisms for satisfying this contract, not substitutes for it.

# 1. Purpose

The governing user-visible contract is §0 / ADR-070 as strengthened by ADR-078. The purpose and mechanisms below MUST be interpreted in service of that contract.

`ruu` is the replacement for the former `git-commits-push` concept.

It is **not** merely a wrapper around:

```bash
git add .
git commit
git push
```

The ordinary **`ruu` convergence invocation** is also **not** the pre-edit contribution-unit provisioner: it must not create missing isolation retroactively as a checkpoint side effect. This phase separation does not require provisioning to be a separately installed product. Under ADR-078, a Ruu distribution may supply coding-harness integrations and provisioning primitives that implement the External Control Plane/provisioner role automatically before first managed write.

`ruu` is an **explicitly invoked Git-based version-control engine for agentic development**, whose current feature set includes convergence, exact-state promotion, and provider publication. An authorized invocation principal — human, coding agent, script, Turnlock, `/go`, automation, or another orchestrator — invokes it when that principal wants existing managed Git state to progress.

Operationally, its ordinary checkpoint/progression interface is a **state-dependent governed super Git command**. The Development System/agent performs semantic development work and decides when current work is sufficiently clean/ready to cross another Git boundary. When new work is being handed off, that call is a durable **work-bearing logical invocation** whose sealed ContributionUnit cohort defines the checkpoint/promotion occurrence boundary; it independently raises ordinary convergence demand. Demand-only triggers remain possible. The demand signal asks `ruu` to inspect current durable workflow/Git/provider state and perform whichever Git transitions are now legal; it does not prescribe a caller-local workflow stage and does not make tests/review policy part of `ruu`.

Its purpose is to coordinate and advance Git state across:

- multiple Pi sessions;
- multiple external work producers operating through isolated contribution units;
- multiple repositories;
- multiple concurrent contribution-producing contexts;
- potentially overlapping edits to the same logical files;
- simultaneous `ruu` invocation demands that safely coalesce;
- repository-specific promotion policies;
- direct-target and provider-submission-mediated, same-repository, cross-repository, independent, and stacked promotion workflows.

The core objective is:

> **allow concurrent work to proceed aggressively in isolated repository-local contribution units while making each global sweep that services outstanding convergence demand exhaustively re-evaluate every known nonterminal managed obligation across the full Git/convergence/promotion/provider lifecycle and advance every transition that is currently safe, authorized, claimable, and fully satisfied by its transition-local Git/managed/policy/provider prerequisites.**

The desired system should make it possible for:

- several external producers to work on the same logical file concurrently through distinct contribution units without sharing a mutable checkout;
- work from a contribution unit to be checkpointed/committed without declaring any broader task complete;
- work in a contribution unit made generally transferable by the External Control Plane to be collected later by another authorized invocation principal;
- repository-local contribution-unit states to converge into **convergence units**;
- every ConvergenceUnit to have its final PromotionTarget resolved before managed authoring, so later invocation does not need a `merge-main`/retarget command;
- repository promotion to follow current policy for **how** the already-bound PromotionTarget may be reached rather than a global hard-coded direct-vs-provider-submission workflow rule;
- small trunk-based direct promotions where explicitly allowed;
- strict provider-submission workflows (for example GitHub PR + CI/review/merge queue) where required;
- coherent external/fork contributions without forcing internal convergence granularity to equal upstream provider-submission granularity;
- exact native authoring commits to be selected as durable source-attributed dependencies before their producer has a PromotionGroup, without consuming dirty producer state;
- stacked provider submission refs to appear naturally when an exact authoring dependency later resolves to an unsatisfied promotion dependency, and to be restacked/reprojected under one exact state-transplant contract without rewriting internal contribution-unit/convergence-unit refs;
- simultaneous invocation demands to coalesce safely behind one recoverable fenced executor;
- development-quality validation to remain a Development System concern, while each Git transition is governed only by its own exact Git/managed/policy/provider prerequisites and any transition-specific external facts.

`ruu` does not decide what a product feature, task, ticket, or complete contribution means semantically. Those meanings belong above the Git convergence layer.

The normative interface to those external responsibilities is defined in [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](external-control-plane-contract.md), introduced by ADR-039. The **External Control Plane** is an abstract role and may be implemented by one or several upstream/user-facing components, including a Ruu-supplied coding-harness integration. Its architectural separateness is an authority/phase boundary, not a requirement for a second user-installed product.

# 2. Core mental model

The system must not treat:

```text
Pi session == task == contribution_unit_id == repository == branch == promotion unit
```

as equivalent concepts.

They are distinct entities.

At minimum, the architecture distinguishes:

```text
Invocation principal
Work-bearing LogicalInvocation (when new/correction work is handed off)
ConvergenceDemand / ReconcilerRun
Contribution unit
Authoring dependency (when one ContributionUnit explicitly consumes an exact version from another)
Repository
Repository promotion policy
Target repository/ref
Convergence unit
Convergence-unit ref
Contribution-unit ref
Contribution-unit worktree
Contribution-unit mutation-access contract / worktree claim
Promotion unit
Promotion topology
Submission ref (PROVIDER_SUBMISSION route)
submission/provider identity/state (PROVIDER_SUBMISSION route)
HEAD / exact OIDs
Claims / recovery state
```

Higher-level systems may additionally know:

```text
product feature
task / issue
/go run
Turnlock work package
semantic completion
review intent
```

but those are not Git-level identities required by `ruu`.

## 2.1 Contribution unit

A **contribution unit** is a repository-local isolated Git unit that carries one **bounded stream of contribution to its current convergence scope**. It is not a durable actor/session workspace and does not identify the producer behind it.

The term is neutral about whether content already existed: the same construct covers greenfield/from-scratch creation, additions, modifications, deletions, refactors, generation, migrations, and mixtures of those operations.

Its isolation cardinality is intrinsic:

```text
1 contribution_unit_id
=
exactly 1 repository_id
+
exactly 1 convergence_unit_id membership for this contribution-unit identity
+
stable logical identity independent of editing-artifact presence

while externally provisioned for active editing:
  isolated Git worktree/ref surfaces may exist
```

Higher-level work spanning three repositories therefore uses three distinct repository-local contribution units. `ruu` does not need to know whether those units came from the same agent, session, task, or orchestrator run.

Two concurrent producers operating in the same repository still require distinct contribution units/worktrees. A `contribution_unit_id` is not reassigned to another convergence unit; a different convergence scope requires a new contribution unit.

### 2.1.1 Contribution-unit lifecycle and exact-state continuity

Lifecycle is scoped to the contribution unit's **current convergence scope**:

```text
OPEN
= this contribution unit may still produce additional contribution
  to its current convergence scope.

CLOSED
= this contribution unit will produce no further contribution
  to its current convergence scope;
  any later work requires a new contribution_unit_id;
  its latest authoritative managed checkpoint, if any, remains subject
  to ordinary convergence until resolved.
```

`CLOSED` is terminal for future contribution production and never returns to `OPEN`.

Contribution-unit lifecycle is not inferred from producer/runtime state, Git checkpoint state, or editing-artifact presence. None of the following implies closure:

```text
agent/process inactive
agent waiting for user
agent turn finished
conversation waiting for user
checkpoint committed
worktree clean
development-quality validation PASS
current contribution integrated
contribution-unit tip equal convergence-unit tip
local contribution branch/ref absent
worktree absent
remote contribution ref absent/present
```

Therefore:

```text
producer/runtime lifecycle
≠ contribution-unit lifecycle
≠ Git/convergence state
≠ editing-artifact lifecycle
```

The authoritative `OPEN | CLOSED` declaration belongs to the **External Control Plane**. `ruu` consumes/revalidates it and does not infer semantic closure.

Under ADR-038, ContributionUnit identity and convergence continuity are independent of local branch/ref/worktree existence. For convergence purposes the durable fact is the latest authoritative managed checkpoint OID, when one exists. Missing editing artifacts alone create no closure, recreation, remote-deletion, or abandonment intent.

Contribution-unit lifecycle remains separate from upward integration. There is no separate ContributionUnit integration-release/readiness state: every valid authoritative managed checkpoint is advanced toward its bound ConvergenceUnit at the earliest mechanically safe opportunity. An `OPEN` ContributionUnit may deliver multiple integrated checkpoints and continue contributing later before closure.

### 2.1.2 Exact native authoring versions and AuthoringDependency

A native commit on a current managed ContributionUnit lineage is an exact Git version. Its creation is not itself a managed checkpoint, handoff, completion, PromotionGroup, or PromotionUnit event. At an exact frozen work-bearing handoff, Ruu may adopt the clean current managed-ref tip as the latest authoritative managed checkpoint without creating another commit; the handoff adoption, not the earlier native commit, is the managed event.

A repository-local consumer may explicitly depend on an exact commit from another ContributionUnit before the source has any PromotionGroup:

```text
AuthoringDependency {
  authoring_dependency_id
  consumer: (repository_id, contribution_unit_id)
  source: (repository_id, contribution_unit_id)
  git_object_format
  consumed_exact_oid
  state
  required recovery-anchor identity
}
```

`ContributionUnit` is the sole v1 stable authoring-occurrence identity. Historical `ContributionUnit/work occurrence` wording names the same object; `work_occurrence_id` is not a second domain identity. Source and consumer are distinct ContributionUnits in one repository. Cross-repository semantic coordination remains PromotionGroup-level because a commit in one repository is not a Git base in another.

The Development System explicitly selects source identity plus exact OID. Ruu proves current source binding/lineage and canonical raw-object ancestry, anchors the OID before adoption, and then reconciles the durable relation. OID alone, ancestry alone, names, sessions, processes, task similarity, recency, or dirty worktree state never create the relation.

The immutable consumed OID remains separate from both the source's later current exact state and any later `(PromotionGroup, source repository)` projection that owns realization. An unresolved AuthoringDependency blocks unauthorized realization, not otherwise legal authoring, checkpointing, internal convergence, or unrelated global progress.

`authoring_dependency_id` is SHA-256 over the UTF-8 RFC 8785 JCS encoding of an exact closed object containing `schema="Ruu/authoring-dependency/v1"`, canonical repository ID, canonical consumer/source ContributionUnit IDs, canonical Git object-format name, and lowercase full-width consumed OID. Abbreviated/uppercase OIDs, unknown algorithms/fields, or alternate opaque-ID normalization are non-canonical.

## 2.2 Convergence unit

A **convergence unit** is the repository-local shared Git root to which one or more contribution-unit contributions converge.

Conceptually, internal Git convergence and final promotion destination are distinct:

```text
ConvergenceBase ref/state
  └── convergence unit ───────────────► immutable PromotionTarget
        ├── contribution unit-A          (target_repository_id, target_ref)
        ├── contribution unit-B
        └── contribution unit-C
```

The term says nothing about product semantics.

A convergence unit has:

```text
convergence_unit_id
= stable orchestration identity

convergence_ref
= actual repository-local Git ref

convergence_base_ref
= repository-local ref/state family from which the unit is provisioned
  and with which it synchronizes while mutable

promotion_target
= immutable logical final destination
  (target_repository_id, target_ref)

branch/display name
= descriptive task-related label; not authoritative identity
```

The `ConvergenceBase` and `PromotionTarget` commonly designate the same logical branch in a simple same-repository workflow, but they are not the same architectural concept. In cross-repository publication, the repository-local ConvergenceBase may live in the source repository while the PromotionTarget names an upstream repository/ref.

The concrete branch may be named by a human/agent according to the task, for example:

```text
fix-login-race
refactor-parser
oauth-callback
turnlock-lease-recovery
```

`ruu` never derives correctness or semantic meaning from that text.

ConvergenceUnit creation/reuse, immutable PromotionTarget binding, and ContributionUnit membership are externally authoritative. Before the first managed write in any attached ContributionUnit, the External Control Plane binds the ConvergenceUnit to exactly one canonical `(target_repository_id, target_ref)`. Reuse requires that target binding to match exactly; an intended different destination requires a distinct ConvergenceUnit rather than retargeting the existing one. The External Control Plane binds each new `contribution_unit_id` to exactly one `convergence_unit_id`; `ruu` never infers grouping or target from caller/task/file overlap/name/CWD. Experimental or alternative approaches that must remain isolated use a **distinct ConvergenceUnit**.

A ConvergenceUnit also carries an externally authoritative contribution-membership state:

```text
OPEN
= additional ContributionUnits may still be attached to this convergence scope.

SEALED
= no additional ContributionUnit is currently expected/authorized to attach
  before the current convergence result may be finalized internally.
```

`OPEN` membership permits ordinary checkpointing, Git/convergence validation, synchronization, reconciliation, and ContributionUnit→ConvergenceUnit integration; it blocks only `READY_INTERNAL`. `ruu` consumes/revalidates this state and does not infer sealing from the currently visible membership.

## 2.2A Work-bearing invocation and PromotionGroup

A work-bearing logical invocation of `ruu` is the durable checkpoint boundary for one closed implementation cohort. It is distinct from the coalescible `ConvergenceDemand` and from any particular `ReconcilerRun` (ADR-069). Demand-only triggers remain valid and do not create a work-bearing invocation.

```text
LogicalInvocation {
  invocation_id
  handoffs: Set<ContributionUnitHandoffRef>
  promotion_binding:
      NEW_GROUP
    | REVISE_EXISTING_GROUP(promotion_group_id, authority_ref)
}
```

The non-empty handoff set is sealed and immutable once accepted. Every listed ContributionUnit must already be durably frozen/bound to that invocation under the mutation-handoff rules before the invocation seal is adopted. The caller preserves the same opaque `invocation_id` across retry of the same logical invocation; reuse of an invocation id with a different immutable definition is an integrity failure.

For an ordinary `NEW_GROUP` invocation, `ruu` mechanically derives the closed PromotionGroup membership from the already-authoritative ContributionUnit→ConvergenceUnit bindings:

```text
ConvergenceMembers(I) =
  distinct(convergence_unit_of(CU) for CU in I.handoffs)
```

A **PromotionGroup** is the durable occurrence-bound promotion obligation created from that invocation. A group may span repositories.

```text
PromotionGroup {
  promotion_group_id
  origin_invocation_id
  members: Set<CanonicalConvergenceUnitRef>
  membership_fingerprint
  group-local exact resolution
}

CanonicalConvergenceUnitRef = (repository_id, convergence_unit_id)

promotion_group_id
  = SHA-256(
      "Ruu/promotion-group/v2"
      || coordination_domain
      || invocation_id
    )

membership_fingerprint
  = SHA-256(canonical(sorted(members)))
```

The member set is non-empty, unordered, unique, closed, and immutable. Distinct logical invocations create distinct PromotionGroups even when their canonical member sets are identical. Session identity, branch identity, task identity, topology, policy, and exact OIDs do not define PromotionGroup occurrence identity.

A PromotionGroup does not alias the live current state of its ConvergenceUnits. It adopts a **group-local exact resolution** under snapshot/CAS guards. Later unrelated authoring or later ordinary invocations may advance the same ConvergenceUnit lineages without refreshing or invalidating an already-adopted group-local exact binding. An existing group may adopt a newer resolution only under current explicit group-bound correction/reconciliation authority. A terminal group cannot adopt a newer resolution.

For `REVISE_EXISTING_GROUP(G, authority_ref)`, the invocation creates no new group; all touched ConvergenceUnits must already belong to `G`, and the authority must explicitly bind the semantic continuation to `G`. Unchanged members retain their prior exact group-local state.

## 2.3 Promotion unit

A **PromotionUnit** is an immutable, content-addressed, non-empty unordered set of canonical exact ConvergenceUnit-state references from exactly one authoritative source repository.

```text
PromotionUnitDefinition {
  members: Set<ExactConvergenceStateRef>
}

promotion_unit_id
  = SHA-256(domain + schema_version + canonical(sorted(members)))
```

Member order has no semantic meaning; duplicate members are invalid/non-canonical. All members MUST share the same authoritative source `repository_id`; a cross-repository exact member set is structurally invalid as a PromotionUnit. All members projected into the same repository-local PromotionUnit MUST also carry the same immutable ConvergenceUnit PromotionTarget. A same-source projection with conflicting target bindings is `TARGET_INCOHERENT_PROMOTION_GROUP` and fails closed; `ruu` does not split it by target. This source-locality rule does not prohibit a policy-authorized `CROSS_REPOSITORY` operation toward the already-bound target repository. The definition is immutable: changing any exact member state creates a different PromotionUnit identity. Lifecycle, provider submission revision, target/mode, and promotion topology do not participate in the content address because target identity is already an immutable binding of each member ConvergenceUnit rather than a caller-supplied PromotionUnit field.

ADR-046/ADR-069 insert an immutable-membership, occurrence-bound `PromotionGroup` between work-bearing logical invocations and repository-local exact PromotionUnits. Ordinary group membership is derived mechanically from the sealed invocation's ContributionUnit cohort rather than separately declared by the External Control Plane.

For each group member, `ruu` adopts an exact **group-local** state attributable to the originating invocation or to a later explicitly group-bound revision. It then deterministically partitions the complete group-local exact set by authoritative source repository. For each represented repository `R`, exactly one non-empty set `Project(G,R)` is materialized/reused as the PromotionUnit defined above. The complete repository→PromotionUnit mapping is adopted under expected-state/CAS checks.

Movement of a live ConvergenceUnit after that adoption does not by itself refresh the group. A later ordinary work-bearing invocation using the same ConvergenceUnits creates a distinct PromotionGroup. A group-bound correction may revise only the explicitly authorized existing group, and untouched members retain their prior exact group-local state.

`READY_INTERNAL` never implies an implicit singleton/default mapping. A one-member ordinary invocation mechanically yields a singleton PromotionGroup; multiple ConvergenceUnits use the same mechanism. Same PromotionGroup plus same source repository always maps to the same repository-local projection boundary when the immutable member PromotionTargets agree; `ruu` does not split that projection into multiple PromotionUnits, retarget it, or infer stacked-provider-submission granularity. `ruu` does not accept caller-supplied target/mode/policy override fields in the PromotionUnit definition.

## 2.4 Promotion topology and submission representation

Repository policy determines the authorized promotion path, while current promotion topology is derived mechanically from exact managed Git/promotion state.

The canonical publication destination is already fixed by the member ConvergenceUnit `PromotionTarget`. The source/target repository relation is therefore derived managed context:

```text
PromotionTarget:
  (target_repository_id, target_ref)   # immutable ConvergenceUnit binding

publication_relation:
  SAME_REPOSITORY | CROSS_REPOSITORY   # derived from source repository + PromotionTarget
```

Core policy outputs/constraints include:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION

submission rewrite authorization
provider/governance operation constraints
publication repository/remote mechanics when needed
```

Policy answers **how** the current exact state may reach its already-bound target; it never chooses **where** the work should land.

Separately:

```text
current promotion dependency/topology
= derived managed state
= INDEPENDENT or dependency-derived STACKED representation need
```

Provider capability observations determine whether the exact semantic operation required by that derived state is technically realizable in the current context; policy determines whether it is authorized. Unsupported/forbidden operations fail closed without topology fallback.

In PROVIDER_SUBMISSION route, one stable logical submission may have a current provider-facing **PublicationEpisode**, and each episode has its own **submission ref** + provider submission identity. Exact candidate changes while an episode is open become monotonic submission revisions on that same episode; ADR-055 permits a later distinct episode when the previous provider submission is terminal but the same nonterminal logical submission still requires another repository-local publication.

Every episode submission ref is distinct conceptually from internal convergence-unit refs and from refs of other episodes, even when some initially point at the same OID.

## 2.5 Internal source state versus provider-facing representation

Internal refs:

```text
CONTRIBUTION_UNIT_REF
CONVERGENCE_UNIT_REF
```

preserve exact OIDs and are never rebased/history-rewritten by `ruu`.

Provider-facing submission refs may be explicitly rewriteable/restackable when repository policy/provider topology permits it.

This gives the system two identity layers:

```text
internal source state
→ stable exact OIDs

submission representation
→ stable logical promotion/submission identity
   + current PublicationEpisode/provider submission surface
   + exact current submission-head revision
```

A target ref is never history-rewritten by `ruu`.

## 2.6 Invocation principal, logical work-bearing invocation, convergence trigger, and mutation authority are distinct

An invocation principal may be:

```text
coding agent
human
script
Turnlock
/go
automation
another authorized orchestrator
```

The ability to invoke `ruu` does not grant authority over ContributionUnit worktrees. ADR-041/ADR-069 distinguish two invocation forms:

```text
demand-only invocation
→ coalescible convergence-demand trigger only

work-bearing logical invocation
→ durable sealed ContributionUnit cohort + promotion binding
→ independently raises the same coalescible convergence demand
```

The **demand signal** carries no caller-local work scope, Git snapshot, or worktree authority and may be coalesced with other demands. The durable logical invocation receipt is not coalesced: retry of the same `invocation_id` resolves to the same immutable invocation definition, while a later genuine work-bearing invocation has a distinct identity. Neither kind of invocation owns a reconciler run or narrows the ADR-036 global sweep.

ContributionUnit identity and external mutation authority are supplied by the External Control Plane. `ruu` treats `contribution_unit_id` as opaque and does not infer identity or mutation authority from process/session/model/principal/branch/path/CWD. For a work-bearing invocation, the External Control Plane/Development System explicitly supplies the closed set of ContributionUnit handoffs being checkpointed; `ruu` then derives PromotionGroup membership mechanically through their existing ConvergenceUnit bindings.

For each existing repository-local ContributionUnit editing surface, `ruu` consumes durable external mutation-access state:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_RUU
TRANSFERABLE_GENERAL
UNKNOWN
```

Only a transferable state plus a race-safe exclusive worktree claim held by the current authoritative executor/operation can authorize contribution-unit-worktree mutation.

Under ADR-064, transferability at a checkpoint boundary is also a **frozen mutation handoff**. Once the Development System has decided that the current observable editing surface may be checkpointed and durably publishes `TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL`, no external writer retains the right to mutate that surface while the handoff remains current. Resuming semantic authoring requires legitimate revocation/reacquisition of external mutation authority before any new write; if `ruu` already owns the exclusive claim, reacquisition waits for a safe release/recovery boundary.

Exact-**demand-trigger** transferability states remain retired. For a work-bearing logical invocation, ADR-069 permits each frozen handoff to be durably bound to the logical `invocation_id`; this does not make the coalescible convergence-demand signal an authority token. Authority state is still published durably before/independently of executor wake-up.

`ruu` does not own external work-producer/runtime liveness, heartbeat, lease renewal/expiry, process supervision, or stop/resume semantics.

## 2.7 Development-system neutrality and transition-local prerequisite boundary

`ruu` distinguishes semantic development quality from mechanical Git/convergence/provider progression.

```text
Development System / repository governance
→ owns tests, lint, typecheck, build, formatting, codegen, security checks,
  agentic/human review preparation, flaky/external-service handling,
  validation retries/fixed points, executor capacity, logs/artifacts/caches

Ruu
→ owns exact Git/provider observation, candidate construction, ancestry/CAS,
  conflict detection, transition-local policy/capability guards,
  ref/provider effects, recovery and final target-integration proof
```

There is no generic `DevelopmentValidationEvidence` or `DevelopmentValidationDemand` protocol in the current architecture. Development-quality reasoning controls when the external system offers work, changes lifecycle/governance intent, or otherwise establishes facts it owns; `ruu` does not ask why those facts were established.

Each transition is evaluated from only its own mechanically observable Git/managed/provider state plus the minimum authoritative external facts that genuinely belong to another owner. Examples include ContributionUnit lifecycle, ConvergenceUnit membership sealing, explicit authoring-source selection, work-bearing invocation cohort/promotion binding, review-request intent, promotion policy, provider checks/reviews/queue state, and settlement intent.

For a dirty ContributionUnit checkpoint, ADR-058/059 define the offered whole editing-surface checkpoint and its canonical native-Git identity. ADR-064 binds the Development System's pre-commit readiness decision to that exact Git checkpoint by a frozen mutation-authority handoff rather than by importing test/review evidence. The intended chain is:

```text
Development System validates/decides on current surface S
→ no further external mutation
→ durable transferable handoff
→ exclusive Ruu worktree claim
→ canonical ADR-059 candidate (P,T)
→ same-claim revalidation
→ ordinary commit K with parent(K)=P and tree(K)=T
```

No test/review certificate is consumed by `ruu` before commit. If semantic authoring is needed again before `ruu` has claimed the surface, transferability must first be revoked and external mutation authority legitimately reacquired; the previous readiness decision is then stale. If semantic authoring is needed at any later Git boundary, existing transition-specific obligations such as `RECONCILIATION_REQUIRED`, review correction, settlement, or policy contradiction carry that boundary; no generic development-validation wait is introduced.

## 2.8 Provider-submission review-request intent

Provider-submission publication has a provider-facing review-request intent:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

This intent is orthogonal to:

```text
VERIFIED
READY
PROMOTABLE
OPEN/CLOSED
```

It is not a contribution-unit/convergence-unit business state named `DRAFT`.

A GitHub adapter maps:

```text
REVIEW_NOT_REQUESTED → draft pull request
REVIEW_REQUESTED     → ready-for-review pull request
```

The nominal path requests review only after the configured submission-author/quality gate holds for the exact current submission revision/head.

`REVIEW_NOT_REQUESTED` exists only as an explicitly authorized exceptional publication capability for bounded cases such as provider-only verification, stack-layer exposure, or code-level early external feedback. If neither `REVIEW_REQUESTED` nor explicit current authority/need for early publication exists, no provider submission is created merely to manufacture a provider object.

## 2.9 Relationship to the broader agentic-development model

The higher-level agentic-development vocabulary:

```text
Work
Candidate
Evidence
Finding
Authorization
Promotion
```

is useful conceptually but does not imply six new `ruu` entities. The boundary maps as follows:

```text
Work
→ Development System / External Control Plane semantic object

Candidate
→ exact Git-state candidate appropriate to the current transition; at promotion time,
  the ADR-048 exact materialized candidate for one immutable PromotionUnit

Evidence
→ semantic development evidence remains external under ADR-057/060;
  provider checks/reviews/queue/currentness remain narrow transition-specific facts

Finding
→ semantic review object outside Ruu; ADR-063 defines deferred/backlog handling;
  only blocking provider governance such as exact CHANGES_REQUESTED becomes a core-visible correction obligation

Authorization
→ current conjunction of required ∩ supported ∩ authorized ∩ exact transition-local prerequisites;
  never a stale generic bypass token

Promotion
→ RealizePromotion(exact candidate, immutable PromotionTarget), regardless of realization route
```

This mapping preserves the conceptual separation without duplicating the existing Git/convergence ontology.

# 3. Git facts that the design relies on

## 3.1 Commits are repository-local

A Git commit belongs to exactly one repository.

If an agent modifies files in:

```text
Repo1
Repo2
```

then a commit executed in `Repo1` cannot commit changes from `Repo2`.

Each repository has its own:

- `.git` metadata;
- branches;
- HEAD;
- index;
- working tree;
- commit history.

Therefore `ruu` must reason about repositories independently.

---

## 3.2 HEAD is repository-local

Within a repository, `HEAD` points either:

- indirectly to a branch; or
- directly to a commit in detached-HEAD state.

If:

```text
HEAD -> branch A1 -> commit C
```

then a new commit normally advances `A1`.

Another repository may simultaneously have:

```text
HEAD -> main -> commit Z
```

There is no session-wide Git HEAD.

---

## 3.3 Uncommitted changes do not belong to a branch intrinsically

A modified working tree can exist before a branch is created.

Example:

```text
main -> C
working tree contains changes
```

Then:

```bash
git switch -c fix-example
```

preserves those changes.

The eventual commit can then land on `fix-example`.

Git technically permits branch creation after uncommitted edits already exist.

However, the managed Git control plane must **not rely on that capability for normal work produced in a contribution unit**. The pre-edit provisioner must create the isolated contribution-unit worktree/ref from the convergence-unit ref **before the first write** in that repository, because branch creation after editing cannot retroactively provide edit-time isolation.

---

## 3.4 Git diff is based on comparing states

Git commits store snapshots.

A diff is calculated by comparing states such as:

```text
HEAD <-> index
index <-> working tree
commit A <-> commit B
```

For example:

```bash
git diff HEAD
```

compares the current working tree with the commit referenced by `HEAD`.

A recorded base commit can therefore be useful for measuring divergence or reconstructing what changed during a contribution unit.

---

# 4. Primary user requirements

## 4.1 Concurrent editing of the same repository

Multiple external producers in different sessions must be able to work in the same repository concurrently through isolated contribution units without serializing all work.

## 4.2 Concurrent editing of the same logical file

Two concurrent contribution units may contain changes to the same logical path only through physically isolated worktrees.

```text
Contribution unit A → worktree-A/src/foo.ts
Contribution unit B → worktree-B/src/foo.ts
```

Reconciliation occurs later through Git, not through concurrent writes to one checkout.

## 4.3 Repository-local hierarchy: ConvergenceBase → convergence unit → contribution unit, with immutable PromotionTarget

The internal Git hierarchy is:

```text
configured ConvergenceBase ref
  └── convergence-unit ref
        ├── contribution unit-A
        ├── contribution unit-B
        └── contribution unit-C
```

Separately, before managed authoring begins, that ConvergenceUnit is durably bound to:

```text
PromotionTarget = (target_repository_id, target_ref)
```

`ConvergenceBase` controls repository-local synchronization ancestry. `PromotionTarget` controls the logical final destination. They are often the same branch in same-repository workflows but MUST NOT be conflated.

Every contribution-unit ref is provisioned from its convergence-unit ref, never directly from the ConvergenceBase ref.

Internal edge semantics:

```text
ConvergenceBase → convergence unit
= downward synchronization while that convergence unit is mutable

convergence unit → contribution unit
= downward synchronization

contribution unit → convergence unit
= upward internal integration
```

Promotion is a separate domain governed by repository policy.

## 4.4 Pre-edit provisioning is lazy and outside the convergence invocation

Before the first managed write in a contribution unit, the contribution-unit provisioner / External Control Plane must establish:

```text
repository identity
→ ConvergenceBase identity/ref
→ immutable PromotionTarget(target_repository_id, target_ref)
→ convergence_unit_id/ref bound to that PromotionTarget
→ candidate contribution_unit_id/ref
→ candidate isolated worktree
→ repository-common native observation coverage ACTIVE
→ conservative managed-ref protection established (or degraded-safe negative fast-path disabled)
→ exact RefAdmissionBarrier acquired for the candidate ref
→ exact candidate worktree/ref topology revalidated while producer still lacks authoring authority
→ authoritative current binding committed while the RefAdmissionBarrier is held
→ barrier released
→ contribution-unit mutation-authority handoff to the producer
→ authorized write root
→ first managed write
```

Creating the candidate branch/worktree does **not** itself make it managed. Until authoritative binding publication and the initial authority handoff complete, it is an ordinary provisioning artifact unavailable to a conforming coding producer. The binding becomes current while the native ref admission barrier is still held; the producer receives authoring authority only after exact topology revalidation and barrier release. A crash before current-binding publication leaves no managed binding; a crash after publication leaves an already-protected current binding that provisioning recovery may later hand off or retire.

The selected native-ref adapter must provide `RefAdmissionBarrier` as a capability: it verifies the exact candidate-ref preimage under exclusion with every conforming native mutation of that ref and holds that exclusion through authoritative binding publication. The current Git-core/files candidate realizes an existing-ref barrier with a prepared exact no-op ref transaction (`old_oid == new_oid`) and aborts it after publication. That concrete mechanism is adapter evidence, not the permanent core abstraction; exact no-op ref updates have no managed event semantics.

Reusing an existing ConvergenceUnit requires the requested PromotionTarget to match its durable binding exactly. A different intended target requires a distinct ConvergenceUnit; target mismatch never causes implicit retargeting.

A higher-level producer does not need to predict every repository it will touch before implementation starts.

If it discovers Repo-B later:

```text
discover need to modify Repo-B
→ request/trigger contribution-unit provisioning
→ provisioning succeeds
→ first edit
```

This is not the later checkpoint/convergence invocation. Under ADR-078, for supported coding harnesses this request/trigger is ordinarily automatic and may be implemented by a Ruu-supplied harness integration; the user does not run a separate start/provision command.

For a completely new repository, ADR-056 inserts an external bootstrap step before this ordinary provisioning path:

```text
agent/session requests new repository
→ External Control Plane resolves RepositoryCreationPolicy
→ Repository Provisioner creates/adopts the authorized local repository
→ configured target is bootstrapped at exact non-null B0
→ RepositoryBootstrapContract observed/adopted
→ REPOSITORY_ADMITTED
→ ordinary ConvergenceUnit/ContributionUnit provisioning above
→ first managed write
```

The convergence engine never creates the repository as a convergence side effect. A Ruu distribution may bundle a Repository Provisioner acting under External Control Plane authority; V1 still admits no unborn/null target into the managed model. Local repository creation and provider-repository creation are distinct; provider attachment may be deferred until a provider-sensitive operation actually requires it.

## 4.5 Worktree cardinality

Normative rule:

```text
1 actively authored contribution_unit_id
=
exactly 1 repository_id + 1 dedicated current worktree/ref authoring surface

The durable ContributionUnit identity and exact adopted checkpoints/dependencies survive later editing-surface disappearance under the applicable lifecycle and retention rules.
```

The following are not valid general identities:

```text
1 Pi session = 1 worktree
1 agent = 1 worktree
1 task = 1 worktree
```

## 4.6 No edit-time collisions

The system must transform:

```text
two concurrent producers mutating one physical checkout
```

into:

```text
two isolated contribution units
→ explicit Git reconciliation
```

## 4.7 Native commit, managed checkpoint, and completion are distinct

An ordinary native commit made inside a managed ContributionUnit worktree is an exact Git version. It may be an intermediate, partial, or final authored state, but creation alone is not a Ruu business event.

A **managed checkpoint** exists only after an exact frozen handoff adopts a clean native tip or Ruu materializes/adopts the ADR-059 whole-surface candidate for a dirty surface under current authority, claim, ancestry, and CAS guards. Development-quality validation is not a generic `ruu` checkpoint prerequisite.

Therefore:

```text
native commit → exact Git version
native commit alone != managed checkpoint
managed checkpoint != ContributionUnit CLOSED
managed checkpoint != ConvergenceUnit READY_INTERNAL
managed checkpoint != promotion requested
managed checkpoint != semantic completion
```

A ContributionUnit may remain `OPEN` after several native versions or managed checkpoints and receive further work later.

## 4.8 `ruu` is explicitly invoked when managed state should progress

`ruu` runs only after an explicit authorized convergence demand is signaled, or while an already-authorized executor is draining newer coalesced demand that arrived during its run.

In the ordinary coding path, the Development System/agent signals demand after it considers current authored work sufficiently clean/ready to cross a Git boundary. It may also signal demand for push/publication/status/recovery reasons.

The principal may invoke because it wants:

```text
checkpoint
push
synchronization
integration
direct promotion
provider submission create/update
submission/provider status refresh
recovery
cleanup
or simply all actionable managed Git state to progress
```

This is **intent to progress**, not an authoritative caller-local stage command. In particular, the Development System does not need to issue a late `merge main`/`create provider submission toward X` command: ADR-061 requires the destination to have been bound as the ConvergenceUnit PromotionTarget before authoring. Durable External Control Plane state expresses lifecycle/grouping/review intent; exact Git/provider/coordination state and current policy determine the actual legal transitions toward that fixed destination.

The same invocation can therefore have different effects depending on where the managed process currently is. The immediate invocation reason never narrows the global fixed-point sweep.

## 4.9 Contribution-unit-worktree mutation requires durable external transferability plus an exclusive claim

For each repository-local contribution unit, `ruu` consumes external mutation-access state:

```text
PROTECTED_EXTERNAL
→ protected

TRANSFERABLE_TO_RUU
→ External Control Plane has durably relinquished external mutation authority to the Ruu coordination domain
→ current authoritative executor may attempt claim

TRANSFERABLE_GENERAL
→ no external producer retains mutation authority
→ current authoritative executor may attempt claim under ordinary authorization/policy

UNKNOWN
→ fail closed
```

Transferability never substitutes for the exclusive worktree claim. `ruu` does not infer these states from process/session/heartbeat/liveness signals or from the convergence trigger.

## 4.10 Simultaneous invocation demands coalesce behind one top-level executor

Several principals may invoke `ruu` simultaneously, but v1 does not run several independent top-level convergers.

Each accepted trigger advances durable convergence demand. Multiple demands may coalesce into one later global sweep. At most one authoritative top-level executor owns progression in the local coordination domain at a time.

Independent resources may still proceed in parallel **inside** that executor when their typed claims, exact-state guards, transition-local prerequisites, and repository/provider policies permit it.

Executor takeover/recovery is fenced so an older executor cannot authoritatively adopt new managed state after a newer executor generation has taken ownership.

## 4.11 Generally transferable contribution-unit work is collectible

`ruu` may collect work from a contribution unit that the External Control Plane has marked `TRANSFERABLE_GENERAL`, without requiring principal identity to identify/own that contribution unit or requiring semantic task completion.

## 4.12 Task/product-feature completion is not a Git primitive

`ruu` must not depend on:

```text
task.status == DONE
product_feature.status == DONE
```

for commit collection or internal convergence.

Higher-level semantics control the work-bearing invocation cohort, exact authoring-source selection, lifecycle, and other declared semantic authority. Ruu mechanically derives PromotionGroup membership, repository-local PromotionUnits, and their readiness from those facts; no higher-level actor may override Git-safety guards.

## 4.13 Multi-repository operation

Higher-level work may span multiple repositories by using one repository-local contribution unit per repository. `ruu` does not require a global actor identity to correlate those contribution units.

Every commit/ref/promotion operation remains repository-local even when one global sweep spans many repositories.

## 4.14 CWD does not define scope or cause provisioning

The invocation's current directory:

```text
≠ complete convergence scope
≠ implicit request to register/provision that repository
```

`ruu` processing scope is the complete known set of nonterminal managed obligations in shared coordination state, including unresolved recovery obligations. Caller, CWD, repository, contribution/convergence/promotion identity, age, and invocation reason do not narrow that universe.

## 4.15 Every executed convergence sweep exhaustively re-evaluates all nonterminal managed obligations

Every global sweep performed to satisfy outstanding convergence demand must operate over the complete known **nonterminal managed-obligation universe**, across all lifecycle layers:

```text
contribution-unit checkpoint/Git-validation/commit state and its transition-local authority/claim prerequisites
authoring-dependency adoption, object-retention, resolution, satisfaction, and reconciliation state
contribution-unit ↔ convergence-unit synchronization/integration state
convergence-unit readiness/reconciliation state
promotion-unit state
submission/publication state
submission/review/check/provider state
merge-queue/update/restack state
final target-integration observation/proof state
recovery/cleanup state
```

For each sweep:

```text
enumerate/reconstruct all known nonterminal managed obligations
→ refresh the authoritative Git/remote/provider/policy facts needed by each obligation
→ discover all safe+authorized+claimable+fully-preconditioned transitions
→ perform non-conflicting transitions
→ refresh affected obligations and any newly unlocked obligations
→ repeat
→ stop only at the current global fixed point
```

Concurrent explicit invocations do not create narrower or caller-specific sweeps. They only advance the durable requested convergence generation. Once a sweep reaches its fixed point, the executor compares processed demand with the latest requested demand and performs another global sweep only if newer demand arrived.

Therefore:

```text
nothing to commit
≠ nothing to converge
≠ nothing to publish
≠ nothing to observe

old repository
≠ ignorable repository when a nonterminal managed obligation remains

WAITING_FOR_REVIEW / waiting CI / merge queue / provider wait
→ remains a nonterminal managed obligation
```

`ACTIVE_CONVERGENCE_SET` remains only a derived acceleration index; caller, CWD, repository, age, trigger identity, and trigger reason never define processing scope.

## 4.16 Repository promotion policy is authoritatively composed for an immutable PromotionTarget and revalidated

Each promotion obligation has a resolved `EffectivePromotionPolicy` evaluated in the context of its already-bound ConvergenceUnit/PromotionUnit PromotionTarget. The target identity is not a policy output. Policy is compiled from authoritative current facts/constraints rather than selected by a generic source-precedence ladder.

Immutable/derived promotion context is:

```text
PromotionTarget = (target_repository_id, target_ref)
publication_relation = SAME_REPOSITORY | CROSS_REPOSITORY
  derived from authoritative source repository + PromotionTarget
```

Authoritative policy inputs are:

```text
provider capabilities/current provider facts
provider governance constraints
organization governance constraints, when applicable
trusted repository-committed policy, when present
built-in policy rules for still-underdetermined dimensions only
```

At minimum the resulting policy resolves/authorizes:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION

publication repository/remote mechanics when applicable
provider/governance operation constraints
submission rewrite permissions
review/queue requirements when applicable
```

It MUST NOT select or mutate `target_repository_id` / `target_ref`. If the derived SAME/CROSS repository relation is unsupported or forbidden under current provider/governance facts, the affected promotion blocks; policy does not obtain a satisfiable result by changing the destination.

The effective-policy observation/fingerprint is target-context-bound: it includes the immutable PromotionTarget identity plus the exact mutable target-policy baseline/provider-governance source identities required for that authorization. A policy result for one target repository/ref can never authorize another target.

`promotion_topology` is not selected by policy: ADR-050 derives current dependency/topology from exact managed base/predecessor/target facts. ADR-051 then asks whether the semantic operation required to represent that derived dependency is currently supported by the provider/context and authorized by the effective policy.

Explicit authoritative constraints compose according to their field semantics. If they have no common satisfying assignment, the policy is `CONTRADICTORY`; `ruu` never silently chooses one authoritative source over another. Runtime human/agent/orchestrator requests and local config cannot bypass or alter promotion authorization.

Repository-committed policy governing a promotion is read from the trusted exact target baseline, never from a policy change that exists only in the candidate/submission being promoted. A candidate therefore cannot authorize its own promotion by editing policy.

Built-in rules close only still-underdetermined dimensions. In particular, lack of a repo policy file does not imply `MISSING`: when direct promotion is admissible and no authoritative constraint requires an indirect path, the baseline built-in route resolves to `DIRECT_TARGET_ADVANCE`; when only provider-mediated submission is admissible, it resolves to `PROVIDER_SUBMISSION`.

`ruu` revalidates the effective policy on every executed global sweep. Policy snapshots are immutable/fingerprinted observations, but cached age/TTL is never proof that a snapshot is `CURRENT`. Immediately before every **policy-sensitive promotion mutation**, `ruu` MUST re-observe/revalidate every mutable authoritative policy source needed by that mutation. A changed target-policy anchor, provider/org governance observation, capability/fact observation, or other authoritative source identity/fingerprint makes the prior snapshot `STALE` and forces policy recomputation before mutation.

Policy-sensitive promotion mutations include, at minimum, direct target-ref advancement/publication, submission-ref publication/rewrite, provider submission creation/update, formal review-request mutation, stack/restack/update-branch/base mutation, merge/merge-queue entry or equivalent provider target-integration mutation, and cross-repository publication governed by promotion policy. Pure local candidate materialization/Git validation that does not itself exercise promotion authority is not made policy-sensitive merely because it precedes promotion.

Where a provider exposes a strong version/fingerprint/ETag or equivalent source identity, revalidation binds to it. Where it does not, an immediate fresh provider observation is required. If the provider offers no atomic governance-check+mutation primitive, the unavoidable check/use window is not papered over with TTL: provider-side enforcement and exact post-operation observation/rejection form the final external authority boundary. A rejection caused by concurrent governance/capability drift is surfaced as factual machine-readable current-state evidence and is never automatically repaired or reinterpreted as permission.

Missing, stale, unsupported, contradictory, or otherwise inconsistent effective policy blocks only affected promotion actions. Contradictions are emitted as factual machine-readable diagnostics with exact source provenance; `ruu` does not recommend or apply remediation.

## 4.17 Promotion-group boundaries come from work-bearing invocation cohorts, not semantic submission guessing

Internal convergence frequency and external provider-submission representation remain separate. For ordinary new work, the Development System closes one implementation cohort by making a work-bearing logical invocation. The invocation supplies the exact ContributionUnit handoff set; `ruu` derives the closed PromotionGroup ConvergenceUnit membership mechanically from the already-authoritative ContributionUnit bindings.

```text
sealed work-bearing invocation cohort
→ distinct ConvergenceUnit member set
→ one new PromotionGroup occurrence
```

The External Control Plane does not separately decide that X/Y/Z “look like one ship”. Conversely, `ruu` does not infer cohort membership from code semantics, branch/task/session names, file overlap, or ancestry. A later ordinary invocation creates a distinct PromotionGroup even when it maps to the same ConvergenceUnit member set.

`ruu` adopts exact group-local states, projects each group repository-locally under ADR-047, and materializes exact candidates under ADR-048. Current promotion dependency topology is then derived mechanically from exact managed base/candidate/target facts: a stack is not a user/agent/caller publication preference.

## 4.18 Direct and PROVIDER_SUBMISSION routes preserve trunk-based intent

For a repository whose policy permits direct promotion:

```text
small independently promotable state
→ promote as soon as safe/ready
→ target ref
```

For a strict repository:

```text
small independently promotable state
→ provider submission (for example PR) / CI / review / merge queue
→ target ref
```

The provider-submission boundary changes governance, not the desired integration cadence.

## 4.19 Concrete branch naming is descriptive, not semantic

Humans/agents may choose task-specific convergence-unit branch names.

Correctness uses durable IDs and exact refs/OIDs, never branch-name parsing.

## 4.20 Managed state-producing results use transition-local prerequisites

Whenever `ruu` creates or adopts a new exact managed Git state, authority comes from the exact predicate for that transition rather than from a generic development-validation certificate.

Examples include:

```text
dirty ContributionUnit checkpoint
→ offered/transferable whole editing surface + claim + ADR-059 snapshot validity

internal merge/reconciliation result
→ deterministic clean Git result + exact topology/claim/conflict guards

promotion projection/materialization result
→ exact PromotionGroup/PromotionUnit/base/source/policy guards

submission restack/revision result
→ ADR-050 state-transplant contract + exact revision/publication guards
```

Semantic development validation remains external and may influence when the Development System exposes work/lifecycle/governance intent, but it is not a universal `ruu` precondition.

## 4.21 Development-validation execution is outside Git mutation authority

Fine-grained worktree/ref/promotion claims protect Git/provider correctness. Tests/review/security validation execution and its CPU/RAM/worker scheduling belong to the external Development System under ADR-057/060.

`ruu` has no development-validation worker queue, evidence cache, validation-demand state, retry-until-green loop, or generic development-quality gate.

## 4.22 Review request is publication intent, not internal WIP state

The nominal provider-submission flow publishes `REVIEW_REQUESTED` only after the exact candidate satisfies the configured submission-author quality gate.

`REVIEW_NOT_REQUESTED` is an explicitly authorized publication mode, not a mandatory lifecycle stage and not a synonym for `NOT_READY`.

## 4.23 Tests are also implementation-time agent feedback

The repository test system is not only a terminal CI gate.

During implementation, agents may and should execute the most relevant tests — including integration/E2E tests when they are the useful behavioral control — as part of their edit/observe/reason loop. When practical, this semantic development validation should happen **before** the Development System asks `ruu` to materialize the next managed checkpoint/commit boundary, so the commit operation is not the first discovery point for basic correctness.

```text
edit
→ relevant test/E2E
→ observe
→ correct
```

This iterative development loop belongs entirely to the Development System. `ruu` does not consume a generic development-validation certificate at managed Git boundaries.

Test category alone (`unit`, `integration`, `E2E`) does not determine whether feedback is local or provider-only.

## 4.24 Provider CI is an independent provider-governance layer

Passing local/agentic development validation does not make provider CI redundant.

Provider CI may intentionally repeat checks and add:

```text
fresh checkout/environment
canonical repo configuration
different runtime/OS
provider-only checks
deep security/dependency analysis
deployment/staging checks
merge-queue candidate checks
```

The exact provider gate is open, but the architectural role is independent recertification/environmental coverage rather than being the first place an agent could reasonably discover basic breakage in its own change.


## 4.25 Deferred review findings and backlog remain outside `ruu`

Agentic/human semantic reviews may produce findings that are fixed now, deferred, accepted, or rejected. That adjudication belongs to the Development System. A deferred finding is not represented by keeping a provider submission open merely as a reminder. It should be projected to an external backlog/tracker object when desired (for example a GitHub Issue) with enough provenance to revalidate it later.

A later coding agent must revalidate deferred work against current code before treating it as actionable. `ruu` does not create/prioritize tracker issues or interpret review prose.

Provider review state is different: an exact current blocking governance state such as `CHANGES_REQUESTED` still creates/refreshes ADR-053 `ReviewCorrectionDemand`. Nonblocking provider comments/advisories do not automatically reopen ConvergenceUnits, create correction demands, or block promotion unless current authoritative governance classifies them as blocking or the external Development System independently chooses to act on them.

Therefore:

```text
semantic finding DEFER
→ external backlog item
→ current promotion may continue if all actual governance requirements are satisfied

provider CHANGES_REQUESTED
→ blocking provider fact
→ durable review-correction demand
```

# 5. Mandatory per-demand global convergence and promotion-evaluation requirement

Every executed global sweep that services outstanding `ruu` demand evaluates both:

```text
INTERNAL CONVERGENCE
+
POLICY-DRIVEN PROMOTION / PROVIDER PROGRESS
```

even if no new commit was created.

## 5.1 Internal Git-controlled edges

For a mutable convergence unit:

```text
ConvergenceBase → convergence unit

convergence unit → contribution unit

contribution unit → convergence unit
```

V1 internal graph policy:

```text
ConvergenceBase → convergence unit
  equal tips                              → no-op
  convergence-unit tip ancestor target    → FF convergence unit
  otherwise diverged                      → merge ConvergenceBase into convergence unit

convergence unit → contribution unit
  equal tips                              → no-op
  contribution unit tip ancestor convergence-unit tip→ FF contribution unit
  otherwise diverged                      → merge convergence unit into contribution unit

contribution unit → convergence unit
  convergence-unit tip ancestor contribution unit tip→ FF convergence unit
  otherwise                               → synchronize contribution unit first, revalidate, retry
```

Internal contribution-unit/convergence-unit refs are never rebased/history-rewritten by `ruu`.

## 5.2 Promotion is repository-policy-driven

After internal readiness and explicit promotion-unit binding, promotion follows the repository's current policy.

### `target_realization_route = DIRECT_TARGET_ADVANCE`

Conceptually:

```text
refresh authoritative target + policy
→ verify exact promotion-unit source binding
→ ADR-048 materialize/reuse the exact candidate C
→ require all transition-local exact prerequisites for C
→ create/recover AdvanceTargetFF(target, expected_old=B, new=C)
→ keep C durably reachable through an attempt-scoped recovery anchor
→ immediately revalidate target/policy/claim/evidence
→ execute one atomic compare-and-swap fast-forward B → C
→ observe authoritative target
→ adopt only from exact observed target history
→ make recovery anchor cleanup-eligible after durable adoption
```

DIRECT target advancement is a pure ref operation after candidate materialization. It does not check out or merge into a local target worktree, does not pre-advance a local target ref as staging, and never authorizes target history rewrite or non-fast-forward semantics.

### `target_realization_route = PROVIDER_SUBMISSION`

Conceptually:

```text
refresh target + policy/provider
→ verify exact promotion-unit source binding
→ materialize/update submission ref
→ publish exact current submission revision when current publication intent permits
→ create/update/observe provider submission
→ observe provider checks/reviews/queue/governance
→ when provider target integration is REQUIRED ∩ SUPPORTED ∩ AUTHORIZED
   and all exact current prerequisites hold:
     execute/request the required provider finalization operation
     (for example queue entry, enable auto-merge, or merge submission)
→ observe resulting authoritative target
→ adopt only from exact provider/target evidence
```

On this route, `ruu` MUST NOT directly push/update the target ref. The provider may nevertheless mutate the target as the result of an authorized provider-governed integration operation initiated by `ruu`. There is no generic ceremonial “wait for someone to click Merge” state: if a distinct human finalizer is genuinely required, that requirement must appear as an unsatisfied authoritative provider/governance prerequisite.

## 5.3 Independent versus stacked promotion

For independent promotion:

```text
promotion-unit A → target independently
promotion-unit B → target independently
```

A stacked provider representation appears only when a real promotion dependency is currently unsatisfied by the authoritative target:

```text
target
  ↑
promotion-unit A / submission-A / provider-surface-A
  ↑
promotion-unit B / submission-B / provider-surface-B
  ↑
promotion-unit C / submission-C / provider-surface-C
```

The dependency is derived from exact managed facts such as the child candidate's recorded effective-base lineage, the predecessor's current exact promotion/submission head, and current target ancestry/state. The user, agent, invocation caller, and External Control Plane do not choose `STACKED` as a publication preference. Branch names, task/session names, arrival order, and arbitrary/incidental ancestry are never sufficient authority.

If the predecessor is already realized in the target, the child is an ordinary promotion against the target. If the predecessor is not realized and provider/policy can represent the dependency, the provider projection is stacked. Otherwise the child publication waits rather than silently changing structure.

## 5.4 Same-repository versus cross-repository provider-submission publication

In PROVIDER_SUBMISSION route:

```text
SAME_REPOSITORY
→ submission source and target belong to the same repository/provider namespace

CROSS_REPOSITORY
→ submission source is published from a different repository
  (for example fork → upstream)
```

Provider capability discovery evaluates the exact semantic operation required by the current derived dependency/publication relation in its exact context. It does not choose topology.

`ruu` must not silently convert an unsupported dependency representation in a cross-repository context into another submission structure.

## 5.5 Fixed-point execution

Repeatedly:

```text
refresh shared coordination state
→ refresh effective repo/promotion policy
→ refresh Git + remotes + provider + transition-specific external facts
→ classify currently actionable transitions
→ claim non-conflicting Git/provider resources
→ revalidate exact state/policy/transition-local facts
→ materialize exact candidate result where required
→ if a required transition-specific external fact is missing/unknown: localize that transition
→ execute authoritative Git/provider mutation/publication only when all current guards are satisfied
→ validate Git/provider effect + persist/adopt
→ release
→ refresh/re-evaluate
```

The global fixed point is a **Git/convergence fixed point**, not a formatter/test fixed point. Development System validation loops occur outside `ruu` and may later change the externally owned lifecycle/governance facts relevant to future transitions.

Stop only when every remaining item is:

```text
already complete/converged
protected
claimed by incompatible internal/recovery operation
waiting for a transition-specific external prerequisite
not ready
missing higher-level promotion binding
conflict-blocked
externally waiting
policy/provider unsupported
UNKNOWN_INCONSISTENT
already terminal/resolved
```

Do not spin while waiting on external governance or another transition-specific prerequisite.

## 5.6 Unresolved contribution obligations block internal convergence-unit readiness

Physical ContributionUnit branch/ref/worktree existence is not itself the readiness criterion. A ConvergenceUnit may become internally ready only when contribution membership is `SEALED`, every ContributionUnit is `CLOSED`, and every still-required exact managed checkpoint obligation in that scope is resolved into the exact ConvergenceUnit result.

```text
CLOSED ContributionUnit
+ latest authoritative managed checkpoint absent or fully resolved into exact result
→ no remaining contribution obligation from that unit
```

Any `OPEN`, unknown/orphan, missing-required-managed-state, conflict/recovery, or otherwise unresolved exact contribution obligation blocks `READY_INTERNAL`. Editing-artifact deletion/retention is outside the readiness meaning. Integrating current ContributionUnit commits does not itself close the ContributionUnit.

## 5.7 Promotion readiness is not product-feature completion

A convergence unit or promotion unit may be promoted while a broader product feature/task continues through later independent units.

This preserves trunk-based incremental integration.

# 6. Work-production isolation requirement

## 6.1 Shared working trees are insufficient

If two concurrent producers use the same physical checkout:

```text
Producer A ─┐
            ├── /repo
Producer B ─┘
```

then they may overwrite each other's files before Git has any opportunity to help.

Git cannot safely reconcile concurrent filesystem writes that already happened destructively.

---

## 6.2 Separate Git worktrees are the isolation primitive

The required isolation object is repository-local:

```text
1 contribution_unit_id
=
exactly 1 repository_id
+
exactly 1 convergence_unit_id

while externally provisioned for active editing:
  one isolated Git worktree/ref surface for that producer context
```

For one repository with two concurrent contribution units:

```text
                 Git repository
                      │
             ┌────────┴────────┐
             │                 │
       contribution-unit A    contribution-unit B
       worktree-A         worktree-B
```

Both contribution units may contain concurrent changes to the same logical path, for example:

```text
src/foo.ts
```

because the physical files/checkouts are distinct.

If one higher-level activity needs Repo1 and Repo2, it uses two repository-local contribution units:

```text
higher-level work
├── Repo1 / contribution-unit A1 / worktree-A1
└── Repo2 / contribution-unit A2 / worktree-A2
```

`ruu` does not require an actor identity proving that A1 and A2 came from the same producer/session/task.

No worktree or contribution unit spans multiple Git repositories.

Reconciliation is deferred to Git:

```text
contribution-unit ref ────────┐
                         ├── reconcile through V1 merge/fast-forward policy
convergence-unit ref ────┘
```

This converts unsafe work-time collisions into explicit, detectable Git conflicts.

---

# 7. Shared Git coordination state and repository convergence registry

Because contribution-unit provisioning and later convergence may be performed by different processes/sessions/principals, the system needs durable Git-orchestration state outside ephemeral conversational context.

This durable state is a **shared Git coordination substrate** used by:

```text
contribution-unit provisioner
Ruu
higher-level orchestrators that attach semantic/promotion declarations
```

No single command owns all of it.

## 7.1 `KNOWN_REPOSITORIES`

```text
KNOWN_REPOSITORIES
=
durable catalog of repositories admitted into managed Git coordination
```

A repository record must provide enough durable identity/location/remote information to re-resolve the actual Git repository.

Path alone is not durable identity.

## 7.2 `ACTIVE_CONVERGENCE_SET` is a derived acceleration index

```text
ACTIVE_CONVERGENCE_SET
=
derived/reconstructible index of known repositories that currently have
at least one recorded nonterminal managed obligation
```

It is **not** the authoritative processing boundary. The authoritative universe is the set of nonterminal managed obligations themselves. A stale, missing, or corrupt activity index must be repaired/reconstructed from authoritative managed records and MUST NOT cause an obligation to be skipped.

Indexed obligations include at least:

```text
ContributionUnit with a nonterminal lifecycle or unresolved exact managed checkpoint obligation
convergence unit not terminal/retired
promotion unit not terminal
pending/inconsistent contribution-unit or convergence-unit publication
pending DIRECT target advancement
nonterminal submission/review/check/provider workflow
merge-queue/update/restack obligation
final target-integration observation/proof obligation
missing/stale/nonterminal transition-specific external prerequisite
Git merge/conflict/in-progress operation
incomplete cleanup/claim
UNKNOWN_INCONSISTENT topology/policy/provider state
crash-recovery obligation
```

A waiting submission/review/check/merge queue/provider state remains a nonterminal managed obligation even when no local mutation is currently authorized. It is therefore refreshed on every later global sweep that services convergence demand.

## 7.3 Shared repository policy state

Shared coordination state records the **effective promotion-policy observation** used by `ruu` and enough exact provenance to reconstruct its authoritative inputs or a contradiction.

At minimum the runtime must be able to reason about:

```text
policy identity/version/fingerprint
immutable PromotionTarget(target_repository_id, target_ref)
derived publication_relation
target_realization_route
publication remote/repository mechanics
current exact target OID / trusted policy-baseline OID
current derived promotion dependency/topology identity/fingerprint
normalized provider semantic-operation capability/current-fact observations
provider/organization governance source identities + revisions/fingerprints
trusted repository-policy target-baseline OID + policy fingerprint when present
submission rewrite permission/class
last refresh observation identity
per-mutable-source freshness evidence: source kind/identity, observed revision/version/fingerprint when exposed, observation method, and observation identity
current trusted target OID/policy anchor used for the snapshot
contradictory dimension(s) + normalized incompatible constraint provenance when applicable
```

ADR-043 fixes policy authority/composition semantics:

```text
authoritative capabilities/facts + governance constraints + trusted repo constraints
→ compose without silent precedence fallback
→ contradiction if unsatisfiable
→ otherwise built-in rules fill only underdetermined dimensions
→ EffectivePromotionPolicy
```

Under ADR-051, provider capabilities/facts are normalized as semantic-operation observations bound to exact context. Provider feature labels do not select topology or authorize mutations. Current derived topology is separate managed state; when it requires a provider operation, progression requires `REQUIRED ∩ SUPPORTED ∩ AUTHORIZED` plus the ordinary transition guards.

Local config and runtime caller/human/agent/orchestrator preferences are not promotion-policy authority. Policy is an exact authorization input, not a stale static assumption. Cache entries may retain parsed/normalized observations for efficiency, but cache presence, cache age, TTL, or a previously successful policy resolution never by themselves establish `CURRENT` for a policy-sensitive promotion mutation.

## 7.4 Convergence-unit and contribution unit mappings

Shared state records:

```text
repository_id
convergence_unit_id ↔ convergence_ref
convergence_unit_id → ConvergenceBase identity/ref
convergence_unit_id → immutable PromotionTarget(target_repository_id, target_ref)
contribution_unit_id → exactly one convergence_unit_id membership for its identity
contribution_unit_id → authoritative lifecycle OPEN | CLOSED
contribution_unit_id → latest authoritative managed checkpoint OID, if any
contribution_unit_id → exact authoring base at admission
contribution_unit_id ↔ observations of currently present editing ref/worktree/remote-ref surfaces, if any
AuthoringDependency immutable source/consumer/OID definitions and current lifecycle
AUTHORING_DEPENDENCY_OID_ANCHOR recovery-resource bindings
external mutation-access state/handle for present editing surfaces
exact relevant OIDs
claims/recovery metadata
```

Concrete branch names are descriptive only.

## 7.5 Promotion-unit/submission mappings

When promotion is declared, shared state records:

```text
promotion_unit_id = content address of immutable canonical PromotionUnitDefinition
exact ConvergenceUnit-state member set
current promotion lifecycle
separate current promotion-topology relationship/edges derived from adopted dependency provenance and exact predecessor/target state
submission_id / provider submission identity when applicable
submission_ref
current_submission_head
submission_revision
immutable PromotionTarget inherited from member ConvergenceUnits + current target/provider state observed outside PromotionUnit identity
```

The persisted definition MUST reproduce the canonical `promotion_unit_id`; mismatch is an integrity/`UNKNOWN_INCONSISTENT` condition. Topology, lifecycle, target/mode, provider-facing revision, and semantic task identity are not fields of the immutable PromotionUnit definition.

`ruu` never invents semantic grouping to fill missing PromotionUnit definitions.

## 7.6 Pre-edit provisioning

Before first managed edit:

```text
resolve/register repository
→ activate repository
→ resolve ConvergenceBase + immutable PromotionTarget
→ create/resolve convergence unit with exact target binding
→ create contribution-unit ref/worktree
→ establish contribution-unit mutation authority
→ authorize first edit
```

This is lazy and belongs to the pre-edit provisioner role, not to the later `ruu` convergence invocation. The role may be implemented by a Ruu-supplied coding-harness integration; this does not move semantic authority into the convergence engine or permit retroactive provisioning after writes.

If a brand-new repository is required, repository-creation authorization belongs to the External Control Plane and authorized creation is executed by a Repository Provisioner under ADR-056. The convergence engine never creates the repository as a convergence side effect; ADR-078 permits that provisioner to be bundled with the Ruu product. The repository MUST satisfy the `RepositoryBootstrapContract` and reach `REPOSITORY_ADMITTED` before the pre-edit provisioning sequence above may proceed.

## 7.7 `ruu` global obligation universe and convergence demand

The authoritative processing universe is the complete known set of nonterminal managed obligations recorded in the shared coordination substrate. This includes obligations at every layer through provider governance, final target-integration observation/proof, recovery, and cleanup.

```text
AUTHORITATIVE GLOBAL OBLIGATION UNIVERSE
=
all known nonterminal managed obligations
```

Explicit invocations are coalescible demand signals, not persistent caller-scoped work items. The coordination substrate durably records a monotonic demand relation equivalent to:

```text
requested_generation
processed_generation
```

A sweep services current demand by operating over the entire obligation universe. `ACTIVE_CONVERGENCE_SET` may be used only as a reconstructible acceleration index for locating affected repositories; it cannot normatively exclude an obligation.

CWD does not expand or narrow the universe and does not trigger implicit provisioning. Age, caller identity, invocation reason, contribution unit, convergence unit, promotion unit, repository, or individual demand generation do not narrow it either.

The executor refreshes each obligation's required authoritative facts independently. Repositories with no recorded nonterminal managed obligation need not be deeply scanned.

No normal whole-disk `.git` scan occurs.

## 7.8 Deactivation / quiescence of the derived repository index

A repository may become known-inactive in the derived acceleration index only after authoritative managed records show:

```text
zero unresolved contribution units
zero nonterminal convergence units
zero nonterminal promotion units
zero pending internal publications
zero pending DIRECT target advancement
zero nonterminal submission/review/check/provider workflows
zero merge-queue/update/restack obligations
zero final target-integration observation/proof obligations
zero missing/stale/nonterminal transition-specific external prerequisites
zero in-progress Git recovery
zero unresolved claims/cleanup
zero relevant UNKNOWN_INCONSISTENT state
```

Quiescence is only an orchestration/indexing optimization, not deletion and not a scope decision. Any newly created or newly discovered nonterminal managed obligation immediately makes the repository relevant again. If the index disagrees with authoritative obligation records, the obligation records win and the index is repaired.

## 7.9 Authority: shared metadata versus Git/provider truth

Shared coordination state is authoritative for system relationships such as:

```text
managed membership
contribution-unit/convergence-unit identity mappings
authority/claims
work-bearing invocation and PromotionGroup occurrence/group-local resolution records
content-addressed PromotionUnit projection records
policy observations/fingerprints
submission logical identity/revision tracking
recovery ownership
```

Git/remotes/provider are authoritative for facts they own:

```text
local refs/OIDs/worktrees/index/conflicts
remote refs
target ref
submission ref
submission/provider head/state
merge result
provider capability observations
```

Material disagreement triggers refresh/reconstruction and `UNKNOWN_INCONSISTENT` while ambiguity remains.

Shared metadata never manufactures Git/provider truth.

## 7.10 External Control Plane boundary

The complete normative upstream interface is defined in [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](external-control-plane-contract.md) and ADR-039.

The **External Control Plane** is an abstract role, not a required daemon/service/orchestrator or separately installed product. Under ADR-078, a Ruu-supplied integration for a supported coding harness may implement this role and its pre-edit provisioner plumbing automatically while preserving the same authority boundary. It owns the logical/runtime declarations that the convergence engine cannot infer safely, including ContributionUnit creation/binding/lifecycle, ConvergenceUnit creation/membership, pre-edit provisioning (including ADR-056 new-repository bootstrap admission), explicit selection of any exact source ContributionUnit/version required before consumer authoring, external mutation transferability, the exact ContributionUnit cohort of each work-bearing logical invocation, and explicit same-group correction/reconciliation authority. Ordinary PromotionGroup ConvergenceUnit membership is then derived mechanically by `ruu`; after semantic authoring-dependency selection is adopted, Ruu mechanically derives its target satisfaction, source projection, and ADR-050 promotion topology rather than accepting caller-authored stack layout.

`ruu` retains Git/provider mechanics: exact-state observation/revalidation, claims/CAS, Git/convergence validation, transition-local prerequisite evaluation, checkpointing, synchronization/integration, readiness computation, promotion/publication, provider refresh, final integration proof, and recovery of operations it owns.

Git/remotes/provider remain authoritative for facts they own; External Control Plane declarations do not manufacture Git/provider truth. Missing/contradictory required external declarations fail closed only for the affected obligation and do not stop the global sweep.

Any future normative dependency on a “External Control Plane”, orchestrator, provisioner, caller, agent runtime, or external Development System must map to the External Control Plane Contract or explicitly amend it through an ADR.

Authoring-required Git conflicts cross this boundary as exact-state-bound `RECONCILIATION_REQUIRED` obligations. The external Development System may author a solution, but all resulting Git state returns through ordinary `ruu` current-state and transition-local prerequisite revalidation before adoption.

The system remains Git-safe without `/go` or any particular runtime.

## 7.11 V1 CoordinationStore, convergence-run ownership, and recoverable-effect journal

ADR-042 fixes the concrete v1 coordination runtime.

`ruu` is a current-state reconciler. The one top-level `ConvergenceEngine` repeatedly observes current authoritative state, derives all nonterminal obligations, schedules non-conflicting progressable work, exactly observes/adopts results, and repeats to the current global fixed point. It does not persist or resume workflow-step position.

The host-local SQLite CoordinationStore includes or semantically represents:

```text
schema_meta
coordination_domain(requested_generation, processed_generation,
                    run_generation, run_state, run_token)
repositories + current repository locator bindings
ContributionUnit / AuthoringDependency / ConvergenceUnit / PromotionUnit managed rows
managed obligations + typed resource claims
policy/submission/provider logical records
transition-specific external-fact references
Operation / Attempt / Observation / Adoption journal records
recovery-resource records
```

Every authoritative mutable row uses exact expected-state/CAS guards. Zero-row CAS is stale/lost authority, never success. Unknown schema/state fails closed.

Physical top-level run ownership is a dedicated OS-backed process-lifetime exclusive lock. Durable adoption authority is the current SQLite `run_generation + run_token`. A trigger that finds `OS lock BUSY + run_state ACTIVE` may return after recording demand; `OS lock BUSY + run_state IDLE` MUST retry ownership acquisition because the old process is in the release window and is already fenced from further authoritative work.

ADR-072 makes that physical-ownership lifetime requirement explicit at the subprocess boundary: the host run-lock descriptor/handle MUST belong only to the top-level executor process and MUST be non-inheritable across every subprocess execution boundary. On POSIX, use atomic `O_CLOEXEC` where available or a race-safe `FD_CLOEXEC` fallback established before any subprocess may spawn; other platforms use the equivalent non-inheritable handle. A surviving Git/provider/helper descendant MUST NOT keep the host run lock alive after the owning `ruu` executor dies.

At fixed point the current run transactionally advances only the demand snapshot it covered. If current `requested_generation` remains larger, it stays `ACTIVE` and sweeps again. Otherwise the same transaction sets `run_state = IDLE` and clears `run_token`; from that commit onward the old run may perform only physical lock release/exit.

Recoverable non-atomic effects use immutable logical `Operation` identity across one or more fenced physical `Attempt`s. Current exact Git/provider state is captured in append-only `Observation`s. An `Adoption` exists only when inserted atomically with a successful managed-state CAS. No SQLite transaction spans Git/provider/network/transition-local/long-filesystem work.

ADR-076 keeps native-ref causal witnesses/preparations separate from that managed effect journal. A native witness is evidence of a physical Git occurrence and MUST NOT manufacture an `Operation` for an ordinary native Git action. When a managed Attempt launched the Git operation, the witness MAY carry trusted optional `originating_attempt_id` correlation; this is explanatory only and never current authorization. Exactly-once applies to authoritative logical transitions — at most one Adoption per Operation and at most one committed disposition out of one current managed authoring binding generation — while witness/outcome delivery and exact-state observation may duplicate/replay. State rediscovery may resolve existing durable evidence but never invent a missing causal preparation from final topology.

Correctness-critical temporary refs/workspaces use non-recycled operation/attempt/incarnation namespaces. Their managed lifecycle is `REQUIRED → GC_ELIGIBLE`; only the eligibility transition is correctness-significant. Physical cleanup after eligibility is best-effort and is not journaled as a business effect.

Repository identity is opaque/stable and is not path-derived. Explicit relocation CAS-updates only the current locator binding.

# 8. Contribution-unit lifecycle, exact-state continuity, and mutation access

`ruu` does not own external work-producer/runtime liveness or editing-artifact lifecycle. It separately consumes:

```text
contribution-unit lifecycle
= OPEN | CLOSED

latest authoritative managed checkpoint
= exact OID or absent

exact native authoring versions / AuthoringDependencies
= native commit facts plus explicitly adopted source identity and consumed OID

external mutation access for an existing editing surface
= PROTECTED_EXTERNAL
| TRANSFERABLE_TO_RUU
| TRANSFERABLE_GENERAL
| UNKNOWN
```

Lifecycle answers only whether this bounded ContributionUnit may still produce future contribution to its current convergence scope. The External Control Plane owns that declaration under `EXTERNAL-CONTROL-PLANE-CONTRACT.md`.

The exact checkpoint OID answers what durable managed Git state, if any, still participates in convergence. Branch/ref/worktree presence is not the logical identity.

Mutation access answers only whether `ruu` may attempt to obtain exclusive mutation authority over a currently existing ContributionUnit worktree.

Neither dimension implies another. `CLOSED` never returns to `OPEN`; later work uses a new `contribution_unit_id`.

## 8.0A V1 authoring substrate is a dedicated Git worktree

ADR-073 closes the v1 authoring-substrate boundary. Before the first managed write of every actively authored ContributionUnit, v1 requires one dedicated Git worktree/ref editing surface provisioned for that ContributionUnit. Concurrent ContributionUnits MUST NOT share one mutable checkout.

The normative v1 path is:

```text
ContributionUnit
→ dedicated Git worktree/ref surface
→ external authoring
→ frozen mutation-authority handoff
→ exact whole-surface capture
→ canonical managed checkpoint
```

V1 does not define a second direct authoring contract for arbitrary prebuilt commit OIDs, `tree + parent` tuples, or external filesystem/sandbox snapshots that bypass this managed worktree topology. Ordinary native Git commits made by the human/agent inside the managed worktree remain ordinary Git and are reconciled from that managed topology.

The worktree is the concrete **v1 authoring isolation substrate**, not the permanent identity of the ContributionUnit. After exact managed state has been captured, later worktree disappearance does not erase durable identity/checkpoints under ADR-038/071. A future sandbox substrate requires a new ADR proving equivalent isolation, exact-base, authority/freeze, and deterministic capture properties; no speculative generic authoring-adapter API is defined in v1.

## 8.1 Protected contribution editing surface

```text
mutation_access = PROTECTED_EXTERNAL
```

means an external producer/control-plane owner still retains mutation authority over the existing editing surface. `ruu` MUST NOT mutate it.

## 8.2 Transferability to the `ruu` coordination domain

```text
mutation_access = TRANSFERABLE_TO_RUU
```

means the External Control Plane has durably relinquished external mutation authority over that editing surface to the `ruu` coordination domain. The current authoritative executor may attempt the ordinary exclusive worktree claim.

This state is independent of whichever caller/trigger caused a sweep. It remains subject to the External Control Plane's explicit release/reacquisition contract; a convergence trigger never creates it.

## 8.3 General transferability

```text
mutation_access = TRANSFERABLE_GENERAL
```

means no external work producer retains mutation authority over that editing surface. The current authoritative executor may attempt the ordinary exclusive worktree claim under normal authorization/policy.

`UNKNOWN` fails closed for worktree mutation.

## 8.4 Editing-artifact presence is not ContributionUnit identity; managed-ref removal opens one explicit disposition transition

A local contribution/authoring branch/ref, remote contribution ref, or worktree may be created or deleted by user/agent tooling outside the `ruu` process. Mere later absence remains non-authoritative:

```text
artifact absent by observation alone
↛ CLOSED
↛ remote deletion intent
↛ local recreation intent
↛ proven semantic abandonment
```

ADR-071/074/075 amend ADR-068 for one explicit managed authority boundary: any native mutation capable of terminating/replacing the ref already registered as the current managed authoring binding is captured before linearization through a conforming native-ref adapter. The adapter reports normalized facts; the core derives terminal-removal versus rename-carry preparation. Proven native rename/rebind yields `CONTINUATION`; positively proven terminal removal yields `ABANDON`. Unmanaged ref deletion and worktree removal remain ordinary artifact lifecycle. Users/agents still use native Git; no separate ordinary `Ruu cancel` operation is required.

For an already-created authoritative managed checkpoint:

```text
exact checkpoint already resolved
→ artifact absence is irrelevant to convergence

exact checkpoint unresolved + OID recoverable
→ continue convergence from exact OID, using isolated workspace if needed

exact checkpoint unresolved + OID unrecoverable from every valid managed source
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss condition
```

A dirty/uncommitted filesystem state is actionable only while the editing surface exists and can be safely claimed; it is not a durable managed checkpoint merely because it was once observed.

## 8.5 Contribution candidate attribution is boundary-scoped, not process-scoped

For convergence purposes, the exact candidate belongs to the ContributionUnit whose valid mutation-authority boundary produced it. `ruu` does not require per-process or per-file actor provenance.

```text
valid ContributionUnit mutation-authority boundary
+ exact candidate state produced inside that boundary
→ candidate attributed to that ContributionUnit
```

Hooks, formatters, generators, package managers, migration/code-generation tools, and other subordinate tooling invoked inside that authorized boundary do not create separate contribution ownership merely because another process wrote some files.

ADR-058 fixes whole-editing-surface intent, rejects partial/path-selected managed checkpoints in v1, and makes the current staged/unstaged partition non-authoritative for membership. ADR-059 closes the remaining canonical snapshot mechanics: the exact checkpoint candidate is the native Git tree reconstructed from the exact parent plus the complete observable Git-relevant editing surface; non-ignored untracked paths are included, ignored untracked paths are excluded, structural Git ambiguity/dirty submodules/incomplete sparse observability block, and tree-equal-to-parent is a no-op. Verifier parasite/generated-output handling is a Development System concern under ADR-057.

A known/observed mutation that violates the external/exclusive mutation-authority contract is an integrity/staleness condition, not an attribution ambiguity. The candidate MUST NOT be adopted until valid authority/exact state are re-established and any current transition-local exact prerequisite is satisfied.

---

# 9. Contribution-unit mutation-authority boundary

The External Control Plane owns the right to edit a ContributionUnit worktree and is responsible for making that editing surface safely transferable when convergence should be allowed.

The durable external contract is classified as:

```text
PROTECTED_EXTERNAL
→ an external work producer still retains mutation authority
→ Ruu MUST NOT mutate

TRANSFERABLE_TO_RUU
→ external mutation authority has been relinquished to the Ruu coordination domain
→ the current authoritative executor may attempt the exclusive worktree claim

TRANSFERABLE_GENERAL
→ no external work producer retains mutation authority
→ the current authoritative executor may attempt the exclusive claim under ordinary authorization/policy

UNKNOWN
→ fail closed
```

The trigger that requests convergence is not part of this authority state.

`ruu` owns only its side of the boundary:

```text
observe/revalidate durable external mutation access
→ atomically acquire exclusive worktree claim for the current authoritative executor/operation
→ revalidate exact topology/Git/candidate state under that authority
→ perform only authorized convergence mutations
→ release claim
```

Transferability is not mutation authority by itself. The External Control Plane MUST prevent external reacquisition/mutation while `ruu` holds the exclusive claim. Unknown, contradictory, or stale authority fails closed.

Candidate attribution under ADR-040 follows this valid ContributionUnit mutation-authority boundary, not process identity.

# 10. Atomic acquisition of an existing contribution unit

`ruu` may mutate an existing contribution-unit worktree for operations such as:

```text
commit collection from dirty files
convergence unit → contribution unit synchronization
conflict resolution that changes the contribution-unit checkout/index
contribution-unit-ref movement affecting checked-out state
cleanup/removal
```

The system distinguishes:

```text
invocation_principal
= authorized human, agent, script, Turnlock, /go, automation, or orchestrator
  that explicitly invokes Ruu

contribution_unit_id
= opaque stable identity of one repository-local contribution unit
  supplied by the External Control Plane

mutation_access
= external statement of whether this exact contribution unit is protected or safely transferable

worktree_claim
= Ruu's own exclusive current-executor/operation claim for mutation
```

Therefore:

```text
invocation principal ≠ contribution unit
transferability ≠ exclusive Ruu claim
```

## 10.1 Protected external contribution unit

```text
PROTECTED_EXTERNAL
UNKNOWN
```

are not claimable. `ruu` leaves the ContributionUnit worktree unchanged and continues unrelated work.

A clean worktree does not weaken this protection.

## 10.2 Transferable contribution unit

```text
TRANSFERABLE_TO_RUU
OR
TRANSFERABLE_GENERAL
```

allows the current authoritative executor to attempt the ordinary exclusive worktree claim.

The transfer state itself is not mutation authority:

```text
transferable + claim absent
→ do not mutate

transferable + incompatible internal/recovery claim already held
→ defer/recover

transferable + exact exclusive claim held by the current authoritative executor/operation
→ revalidate exact state and proceed if all other guards pass
```

## 10.3 Transfer boundary

Conceptually:

```text
EXTERNAL_MUTATION_AUTHORITY
        ↓ External Control Plane durably relinquishes authority
TRANSFERABLE_TO_RUU
        ↓ current authoritative executor atomically acquires exclusive claim
RUU_CLAIMED
        ↓ commit/sync/reconcile as authorized
RELEASED / RETURNED ACCORDING TO EXTERNAL CONTRACT
```

The External Control Plane owns how external mutators become quiescent before transfer and how/when external work production may resume after claim release. `ruu` does not reactivate, resume, heartbeat, or lease external producers.

## 10.4 No implicit authority transfer

None of these imply transferability:

```text
principal invoked Ruu
→ therefore principal may mutate every contribution unit          [FALSE]

principal is a privileged orchestrator
→ therefore external mutation protection may be ignored         [FALSE]

external producer/runtime appears absent
→ therefore Ruu may declare the worktree transferable  [FALSE]

convergence demand was accepted
→ therefore mutation authority moved to Ruu             [FALSE]

transferable state observed
→ therefore mutation may occur without an exclusive claim       [FALSE]
```

The External Control Plane establishes durable transferability; `ruu` establishes its own exact exclusive claim.

This worktree mutation authority is distinct from claims on convergence-unit refs, promotion units, submission refs/revisions, DIRECT target advancement, remote publication targets, and submission/provider operations.

# 11. Concurrent convergence demands and single-run ownership

Multiple authorized principals may invoke `ruu` simultaneously. Principals may be humans, coding agents, scripts, Turnlock, `/go`, automations, or other authorized orchestrators.

ADR-041/ADR-069 separate durable logical work intake from executor wake-up. **Every demand signal is coalescible**, but a work-bearing logical invocation also has its own durable immutable `invocation_id` + sealed ContributionUnit cohort before it raises that demand. Demand-only calls create no logical invocation.

```text
work-bearing I17 ─┐
demand-only call ─┼─→ durable requested_generation advances
work-bearing I18 ─┘

at most one authoritative top-level convergence run
→ OS process-lifetime lock provides physical ownership
→ SQLite run_generation + run_token provide durable fencing
→ global fixed-point sweep over current state, including I17 and I18 state
→ processed_generation catches the demand snapshot covered by that sweep
→ if newer demand arrived, remain ACTIVE and sweep again
→ else transactionally publish IDLE, then release OS ownership and exit
```

There is no normative FIFO queue of executor work and no requirement to replay each demand separately. Coalescing the wake-up signals does not merge, erase, or identify distinct work-bearing logical invocations.

The coordination substrate must make the following race-safe:

```text
accept new demand
acquire process-lifetime OS run ownership
establish the next ACTIVE run_generation + run_token
mark a demand generation processed
publish IDLE before physical release when caught up
```

ADR-042 fixes the release handshake: `OS BUSY + durable ACTIVE` permits a trigger to return after recording demand; `OS BUSY + durable IDLE` requires the trigger to retry ownership acquisition because the old run is already fenced and is only releasing its physical handle.

Once a newer `run_generation + run_token` is established—or the current run publishes `IDLE` and clears its token—an older run cannot authoritatively create/adopt new managed progression.

This top-level serialization does **not** imply a global resource mutex. Independent work may still run concurrently inside the ConvergenceEngine where typed resource claims, expected-state/CAS guards, transition-local prerequisites, and repository/provider policy permit it.

Concurrent demands must not cause:

```text
lost convergence demand
duplicate top-level convergers with simultaneous adoption authority
unauthorized external work-producer mutation
stale ref overwrite
duplicate provider-submission creation
duplicate direct promotion
duplicate submission revision/restack
policy-bypass fallback
inconsistent shared coordination metadata
```

Target-ref mutation remains policy-dependent:

```text
PROVIDER_SUBMISSION route
→ target read-only to Ruu

DIRECT_TARGET_ADVANCE route
→ guarded target-promotion claim + descendant-only expected-state update
```

# 12. Atomic operation claims

Claims are fine-grained and typed. A single global mutex is not the baseline.

## 12.1 Contribution-unit-worktree mutation claim

Required for:

```text
commit collection
convergence-unit→ContributionUnit synchronization on an existing editing surface
ContributionUnit conflict resolution on an existing editing surface
checkout/index-affecting reset/movement
```

Exactly one incompatible current executor/operation may own the worktree claim.

External mutation-access eligibility is revalidated before and during claim acquisition.

## 12.2 Internal ref / ContributionUnit managed-state claim

Shared internal mutations require exact coordination on:

```text
convergence-unit ref
contribution-unit ref when a producer/editing ref exists and is synchronized
ContributionUnit latest_authoritative_managed_checkpoint_oid record when exact-state progression occurs without that ref/worktree
```

Expected-old OIDs/record versions are revalidated immediately before mutation. A logical-checkpoint update produced in an isolated workspace must keep the exact result durably reachable until ConvergenceUnit adoption or recovery recording; it does not recreate a deleted producer branch/worktree.

## 12.3 Promotion-unit claim

Materializing/advancing one promotion unit requires exclusive ownership of the incompatible promotion operation.

This protects exact source bindings, candidate materialization, and lifecycle transition.

## 12.4 Submission-ref/revision claim

provider submission/update/restack requires a claim on:

```text
promotion/submission logical identity
submission ref
current submission revision/head
```

A rewriteable submission revision also requires exact expected-old local/remote/provider state.

## 12.5 DIRECT target-promotion claim

In `target_realization_route=DIRECT_TARGET_ADVANCE`, target advancement is a shared mutation resource.

Only one incompatible direct promotion may own the exact target operation at a time.

The claim does not authorize non-FF target mutation; descendant-only/expected-old rules still apply.

## 12.6 submission/provider operation claim

provider submission create/update/queue-related operation identity is coordinated so retries, internal parallel operations, and recovered executions converge on one persistent provider object rather than creating duplicates.

## 12.7 Remote publication claim/expected-state guard

Remote publication is coordinated by exact remote ref and expected-old state.

A claim never authorizes blind overwrite.

# 13. Lock/claim granularity

ADR-041 intentionally serializes **top-level convergence execution ownership**, but this is not a global mutex over every Git/provider resource.

Independent repositories, contribution units, convergence units, promotion units, authoring-dependency waits, and provider waits should remain parallel inside the authoritative executor whenever their mutable resources do not overlap and capacity/policy permits.

Likely coordination scopes include:

```text
repository-local contribution-unit worktree
convergence-unit ref
contribution-unit ref when synchronized
promotion_unit_id
submission_id/ref/revision
DIRECT_TARGET_ADVANCE target ref
remote publication ref
submission/provider operation identity
integration/projection workspace
cleanup object
```

Coordination hierarchy must prevent deadlocks and preserve exact-state revalidation.

A blocked/waiting claim on one resource never grants or removes authority on another unrelated resource.

Repository policy determines whether a target ref is even a mutable claim target:

```text
DIRECT_TARGET_ADVANCE
→ yes, under guarded promotion

PROVIDER_SUBMISSION
→ no direct target-ref mutation claim exists; target realization occurs through provider-governed finalization
```

## 13.1 Development-validation execution capacity is outside the Git claim model

Git/provider claims protect correctness of managed effects. External Development System compute/test/review capacity neither grants nor consumes `ruu` mutation authority.

`ruu` has no development-validation worker queue/capacity/evidence state after ADR-057/060. It observes only the transition-specific facts required by the current Git/provider transition.

# 14. Protection against stale Git, policy, and provider state

Locks alone are insufficient.

Every critical action must be based on freshly revalidated exact state.

Relevant state can include:

```text
contribution-unit ref/OID
convergence-unit ref/OID
target ref/OID
effective repository-policy fingerprint
promotion-unit source OIDs
submission ref/head/revision
remote expected-old OID
submission/provider identity/state
stack parent/current head
claim/mutation-access ownership
```

Example internal race:

```text
convergence-unit-X observed at C
another authorized/recovered operation or external Git update advances it to D
→ stale operation expecting C must abort/recompute
```

Example policy race:

```text
current executor observes target_realization_route = DIRECT_TARGET_ADVANCE
repository policy changes to provider-submission-required
→ stale direct-promotion authorization/state is invalid
→ refresh/recompute
→ direct target mutation forbidden
```

Example submission race:

```text
submission-S expected at H1
provider-authorized restack produces H2
→ operation expecting H1 cannot continue blindly
→ refresh revision/provider state
→ rebind or fail closed according to authorized transition
```

## 14.1 Target movement has mode-dependent meaning

### DIRECT_TARGET_ADVANCE route

Target movement before direct promotion invalidates stale candidate/readiness assumptions.

`ruu` refreshes target, recomputes/reconciles as required, then revalidates before attempting descendant-only target advancement.

### PROVIDER_SUBMISSION route

Target movement does not automatically mutate internal convergence-unit refs.

For an immutable submitted revision:

```text
target advances
→ observe
→ keep current submitted head
→ wait unless provider/policy requires update
```

For a provider-authorized update/restack:

```text
enter explicit submission-update/revision transition
→ rebuild/rebase/restack submission representation as authorized
→ invalidate/re-read head-bound evidence
→ bind new exact submission head/revision
```

Internal convergence-unit source OIDs remain unchanged unless a separate semantic reopen explicitly produces new internal state.

## 14.2 Compare-and-swap reasoning

Before every critical mutation/publication:

```text
assert actual state == expected state
assert effective policy == expected policy
assert operation ownership/claim still valid
```

If not:

```text
refresh
→ recompute authorization
→ retry/defer/fail closed
```

Atomic ref updates, expected-old remote updates, authority/claims, and provider-side exact-head checks are implementation primitives for this requirement.

# 15. Remote publication and push safety

Publication rules depend on **ref class** and **repository promotion policy**.

Ref classes:

```text
CONTRIBUTION_UNIT_REF
CONVERGENCE_UNIT_REF
SUBMISSION_REF
TARGET_REF
```

## 15.1 Contribution unit and convergence-unit refs

These are internal source-of-truth refs.

Normal publication:

```text
EQUAL
→ no-op

LOCAL_AHEAD + expected remote
→ ordinary FF push

expected remote mismatch / REMOTE_AHEAD / DIVERGED
→ refresh/reconcile/revalidate

UNKNOWN
→ fail closed
```

They are never force-pushed or history-rewritten by `ruu`.

A failed push does not roll back valid local convergence; it becomes explicit `PUSH_PENDING`.

## 15.2 Submission refs

Submission refs exist in PROVIDER_SUBMISSION route.

They have two policy classes.

### Immutable submission ref

```text
ordinary FF/expected-state publication only
exact provider submission head binding
unexpected non-FF movement → DRIFTED/UNKNOWN
```

### Rewriteable/restackable submission ref

A non-fast-forward submission revision is allowed only when:

```text
repo policy permits rewrite
AND provider/topology permits/requires it
AND exact submission ref is classified rewriteable
AND the current authoritative executor owns the submission operation
AND expected-old local/remote/provider state is freshly verified
AND underlying convergence-unit source bindings remain exact
```

Any required force-style remote update must use force-with-lease-equivalent exact expected-old protection.

This authority is confined to that submission ref.

## 15.3 Target refs

### PROVIDER_SUBMISSION route

```text
TARGET_REF
→ read/fetch/compare/observe only
→ never directly updated/pushed by Ruu
```

### DIRECT_TARGET_ADVANCE route

```text
TARGET_REF
→ may advance only through guarded direct promotion
→ new target must be a descendant of exact expected target
→ exact expected remote state required
→ ordinary FF push only
→ never rebase/force-push target
```

If the actual target is protected or policy requires provider-mediated submission, direct target mutation is forbidden.

## 15.4 Stable-boundary publication

Contribution unit checkpoint/synchronization may be published at validated stable boundaries.

Convergence-unit advances may be coalesced within one safely owned convergence sequence before publishing the latest stable exact tip.

Submission publication follows promotion-unit lifecycle.

Target publication follows DIRECT promotion lifecycle only.

## 15.5 State-bound transition facts

Publication and other externally governed transitions remain exact-state-bound, but there is no generic development-validation evidence class.

Exact bindings apply to the facts that genuinely govern the transition, for example:

```text
promotion source OIDs + policy fingerprint + target observation
submission identity + exact revision/head + review-request intent
provider checks/reviews/queue observations for the exact revision
expected-old / CAS values for the exact mutation
```

A push is not itself a semantic-development validation boundary. Before any provider/ref-visible effect, `ruu` revalidates the exact transition-local facts and policy/current-state guards.

Remote expected-state/CAS guards remain ordinary transition-local correctness guards.

# 16. Idempotency and localized blocked states

`ruu` must be safely rerunnable.

A crash may happen during:

```text
scope/policy refresh
claim acquisition
contribution-unit commit
internal synchronization/integration
internal push
promotion-unit materialization
DIRECT target advancement/push
submission publication
provider submission create/update
submission revision/restack
provider/merge-queue interaction
merge observation
cleanup
metadata persistence
```

A later recovery execution/global sweep must reconstruct actual Git/remote/provider state before replaying an operation.

Examples:

```text
commit exists but metadata stale
→ do not create duplicate equivalent commit

provider submission exists but metadata stale
→ discover persistent provider submission identity

DIRECT target already advanced remotely
→ observe success; do not replay stale promotion

submission revision already published/provider head moved as authorized
→ reconstruct current revision/head before retry
```

Operations should be:

```text
naturally idempotent
or
recoverable through exact observable state + persistent logical identity
```

## 16.1 Conflict-blocked states and reconciliation obligations

A low-level owned Git operation that encounters a conflict may enter an isolated `BLOCKED_CONFLICT` operation state. If the conflict can be resolved deterministically by Git/repository-configured mechanics without semantic authoring, `ruu` may construct the exact candidate and continue only after ordinary exact-state and transition-local prerequisite revalidation.

If safe progress instead requires semantic code authoring, `ruu` MUST leave authoritative managed refs unchanged and record a durable nonterminal:

```text
RECONCILIATION_REQUIRED
```

bound to the exact conflict-producing facts. The descriptor records enough mechanical evidence for the external Development System to act, including as applicable exact input/destination OIDs, merge-base OID(s), logical resource identities, conflicting paths, and conflict kinds.

Possible conflict domains include:

```text
internal ConvergenceBase→convergence-unit merge
convergence-unit→contribution-unit merge
promotion-unit multi-source materialization
submission revision/restack
```

While reconciliation is required:

```text
authoritative affected refs remain unchanged
the blocked exact obligation is not considered successful
dependent readiness/evidence is stale/insufficient
RECONCILIATION_REQUIRED remains globally visible
unrelated resources continue
fixed-point loop does not spin
```

The reconciliation descriptor is diagnostic, not adoption authority. Any authored result must re-enter the normal pipeline against **current** Git/topology/policy state, acquire current claims/CAS guards, and satisfy the exact transition-local prerequisites for the resulting state before adoption. If the current state has moved, the historical conflict snapshot may become stale/superseded and is re-evaluated rather than trusted.

No external `mark resolved` assertion bypasses current-state proof. Internal contribution-unit/convergence-unit conflicts never authorize rebase/history rewrite. Submission restack conflicts remain subject to the submission-ref rewrite policy.

# 17. Crash recovery

Claims/locks/operation records must not become permanently orphaned after crashes.

Recovery prefers authoritative Git/remote/provider/policy observations over stale shared metadata.

Recognized recovery cases include:

```text
expired/dead operation claim
contribution-unit commit exists / metadata stale
internal merge/conflict in progress
legacy/external rebase touching internal refs
internal ref advanced / push pending
push completed / metadata stale
promotion materialization in progress
DIRECT target advancement attempted/completed / metadata stale
submission ref materialized / metadata stale
immutable submission push completed / metadata stale
owned submission rebase/restack in progress
submission revision published / metadata stale
provider-side authorized restack occurred / local metadata stale
provider submission created/updated / metadata stale
merge queue state changed / metadata stale
provider reports MERGED / target observation pending
branch/worktree cleanup partially complete
repo promotion policy changed while operation was in flight
UNKNOWN
```

Recovery rule:

```text
known owned operation
→ inspect exact state
→ resume/finalize/abort safely

operation owned elsewhere
→ defer

unknown owner or incompatible ambiguous state
→ UNKNOWN_INCONSISTENT / fail closed
```

`ruu` never starts a rebase on contribution-unit/convergence-unit refs.

A rebase/restack may be resumed/inspected only when it is an explicitly recognized policy-authorized submission-ref revision operation.

Recovery must never duplicate an irreversible/provider-visible operation merely because metadata lagged behind reality.

# 18. Repository, contribution-unit, convergence-unit, promotion, and submission identity

Paths and branch names are not sufficient durable identities.

The same Git repository may appear through:

```text
different absolute paths
symlinks
multiple worktrees
moved directories
different remotes/forks
```

The architecture therefore separates:

```text
repository_id
worktree_id
contribution_unit_id
convergence_unit_id
promotion_unit_id
submission_id
actual Git refs/OIDs
provider submission identity
```

A descriptive branch name is metadata, not identity.

## 18.1 Convergence-unit lifecycle and contribution-membership state

A convergence unit is repository-local internal source state. Its processing lifecycle and its contribution-membership state are distinct.

Conceptual processing lifecycle:

```text
ABSENT
  ↓ pre-edit provisioning
ACTIVE
  ↓ membership SEALED + all contribution obligations resolved + exact internal fixed point
READY_INTERNAL(OID)
  ├── explicit semantic/new internal work → ACTIVE + membership OPEN
  ├── explicit External-Control-Plane lineage disposal while not bound to any live PromotionGroup
  │     → ABANDONING → RETIRED after recovery/resource guards
  └── member of an invocation-derived PromotionGroup whose complete group-local resolution
      adopts this exact state into one/more valid PromotionUnit obligations
        → PROMOTION_BOUND(OID)

PROMOTION_BOUND(OID)
  ├── explicit semantic reopen/new contribution scope while any relevant ship remains nonterminal
  │     → ACTIVE + membership OPEN
  │     → existing immutable PromotionUnit definitions remain unchanged
  │     → their readiness/eligibility against the newly current source becomes stale
  ├── every relevant PromotionGroup/promotion obligation terminally settled by the ordinary
  │   delivered/compensated closure path
  │   + no current authoring/reconciliation demand can still reopen this lineage
  │     → PROMOTED
  ├── every relevant ship that would otherwise require delivery has terminally settled in a
  │   non-delivery disposition such as ADR-068 CANCELLED
  │   + no replacement/nonterminal PromotionGroup and no authoring/reconciliation demand remains
  │   + required explicit higher-level lineage disposal is current
  │     → ABANDONING → RETIRED after recovery/resource guards
  └── generic member-local abandon request while a relevant PromotionGroup remains nonterminal
        → forbidden / fail closed; disposition belongs to the PromotionGroup, not to X alone

PROMOTED
  → semantic no-more-authoring boundary for this ConvergenceUnit lineage
  → new ContributionUnits/reopen forbidden; later semantic work requires a new ConvergenceUnit
  → RETIRED only after terminal effects are durably adopted and no correctness-critical recovery/resource obligation still requires the lineage

RETIRED
  → no longer a live operational/recovery resource
  → historical internal ref may become GC_ELIGIBLE, but physical deletion is separate and v1 built-in retention is KEEP
```

Contribution membership:

```text
OPEN
→ new ContributionUnits may still be attached
→ ordinary internal convergence continues
→ READY_INTERNAL forbidden

SEALED
→ no new ContributionUnit attachment for the current readiness attempt
→ existing ContributionUnits continue to synchronize/integrate/resolve
→ READY_INTERNAL may be evaluated when all other conditions hold
```

`READY_INTERNAL(OID)` means the exact sealed internal convergence result is mechanically complete and internally resolved:

```text
membership SEALED
zero OPEN ContributionUnits in this convergence scope
for every CLOSED ContributionUnit, its latest authoritative managed checkpoint (if any) is fully resolved into OID
zero unknown/orphan ContributionUnit membership/state
zero BLOCKED_MISSING_MANAGED_STATE or unresolved internal synchronization/integration/reconciliation/conflict/recovery obligation
transition-local exact prerequisites for that OID
internal fixed point reached: no currently authorized internal state-producing transition can further change OID
```

Physical deletion of terminal/resolved ContributionUnit refs is not itself the readiness meaning. `READY_INTERNAL` does **not** mean product/task semantic completion, ship readiness, review approval, provider-CI completion, or mergeability.

## 18.1A Promotion-group group-local exact resolution

PromotionGroup membership is immutable and occurrence-bound under ADR-069. A group's **group-local exact resolution** is durable managed state, not an alias of each member ConvergenceUnit's live current `READY_INTERNAL` tip.

```text
UNRESOLVED
= the originating/revision invocation has not yet produced/adopted a complete exact group-local member boundary

RESOLVED(Map<CanonicalConvergenceUnitRef, ExactConvergenceStateRef>,
         Map<repository_id, PromotionUnitRef>)
= the complete group-local exact member mapping and its repository-local PromotionUnit projection were adopted under expected-state/CAS

TERMINAL_FROZEN
= the PromotionGroup has terminally settled; its adopted exact resolution cannot change
```

For an ordinary `NEW_GROUP` invocation, initial exact member bindings must be attributable to that invocation's handed-off ContributionUnits. A later ordinary invocation may advance the same live ConvergenceUnits but does not stale, refresh, or supersede this group's resolution.

A nonterminal group may adopt a newer exact resolution only from current explicit `REVISE_EXISTING_GROUP(G, authority_ref)` continuation authority. Untouched members retain their prior exact group binding. Terminal PromotionGroups never adopt a newer resolution.

## 18.2 Promotion-unit lifecycle

A PromotionUnit is mechanically materialized/reused by `ruu` from one repository-local projection of a PromotionGroup's adopted **group-local exact resolution**. One resolved group yields exactly one current PromotionUnit per represented source repository. The PromotionUnit itself remains the immutable content-addressed exact ConvergenceUnit-state member set defined by ADR-045 and is structurally repository-local under ADR-047. Repository policy governs promotion authorization, not work-cohort grouping/default mapping and not intrinsic PromotionUnit identity.

Generic lifecycle:

```text
UNDECLARED
DEFINED
WAITING_FOR_SOURCES
READY_FOR_PROMOTION
PROMOTING
PROMOTED
SUPERSEDED
BLOCKED_CONFLICT
BLOCKED_POLICY
UNKNOWN_INCONSISTENT
```

`SUPERSEDED` is the terminal no-success disposition for an obsolete exact PromotionUnit after the same `(PromotionGroup, source repository)` projection adopts a newer exact PromotionUnit and no unresolved committed/uncertain external effect can still realize the old unit. An old unit with such an unresolved effect becomes non-current and initiates no new promotion mutation, but remains recovery-visible until exact observation yields historical `PROMOTED` or safe terminal `SUPERSEDED`. A previously `PROMOTED` old unit is never retroactively superseded.

Route-specific `PROMOTING` branches:

```text
DIRECT_TARGET_ADVANCE
→ DIRECT_PREPARING
→ DIRECT_TARGET_ADVANCING
→ PROMOTED

PROVIDER_SUBMISSION
→ SUBMISSION_PREPARING
→ SUBMISSION_PUBLISHING
→ REVIEWING / UPDATE_REQUIRED / RESTACKING / MERGE_QUEUED / TARGET_INTEGRATION_REQUESTING
→ PROMOTED
```

A PromotionUnit may reference one or more ConvergenceUnits only through its immutable exact member refs, and all such refs MUST share one authoritative source repository.

If a referenced ConvergenceUnit is advanced by unrelated later ordinary work, an existing group's PromotionUnit does **not** become stale merely because the live ConvergenceUnit tip changed. A different PromotionUnit under the same PromotionGroup is selected/materialized only when that same nonterminal group legitimately adopts a newer group-local exact resolution under explicit group-bound continuation authority. Older unpromoted PromotionUnits may then terminalize as `SUPERSEDED` under ADR-067; previously `PROMOTED` exact snapshots remain historical completion facts.

ADR-054 distinction: `PromotionUnit PROMOTED` means only that this exact repository-local snapshot reached/adopted its terminal promotion outcome. It does not by itself close or retire any referenced ConvergenceUnit. A referenced ConvergenceUnit reaches its own `PROMOTED` boundary only after every relevant PromotionGroup/promotion obligation is terminally settled and no current authoring/reconciliation demand can still reactivate that lineage; `RETIRED` is later and additionally requires recovery/resource sufficiency.

## 18.3 Submission identity and revision lifecycle

In PROVIDER_SUBMISSION route, the provider-facing representation has stable logical identity plus exact current revision:

```text
submission_id = stable for one repository-local PromotionGroup projection + canonical publication destination
publication_episode_id = current provider publication surface generation
submission_revision = monotonic logical generation across episodes
current promotion_unit_id = exact current PromotionUnit incarnation
current_submission_head = exact OID
submission_ref = provider-facing ref for current episode; always distinct from internal refs and other episodes
provider_submission_identity = stable within current episode
```

The same logical submission may survive changed exact PromotionUnit/candidate revisions. While the current PublicationEpisode is nonterminal, those revisions preserve the same provider submission. If that episode is terminal and the same nonterminal logical submission later requires another exact publication, ADR-055 creates a distinct new PublicationEpisode/provider submission without changing `submission_id`; `promotion_unit_id` is therefore revision-bound, not the stable submission identity.

Possible revision states:

```text
UNMATERIALIZED
MATERIALIZING
BOUND_IMMUTABLE(rev,H)
BOUND_REWRITEABLE(rev,H)
UPDATE_REQUIRED
RESTACK_REQUIRED
REVISING
DRIFTED
UNKNOWN_INCONSISTENT
```

For immutable submissions:

```text
BOUND_IMMUTABLE(rev,H)
→ exact head H remains frozen during ordinary review
```

For authorized rewriteable submissions:

```text
BOUND_REWRITEABLE(rev,H)
→ authorized exact revision/update/restack
→ REVISING
→ derive exact H2 under the applicable candidate/update/ADR-050 RestackContract
→ expected-old guarded ADR-049 submission-ref/provider update
→ observe local/remote/provider head == H2
→ increment revision
→ BOUND_REWRITEABLE(rev+1,H2)
```

For dependency restack specifically, H2 is derived by three-way state transplant from the immutable owned `(old_base_oid, owned_candidate_oid)` anchor onto the current new predecessor/base. A previous restacked provider head is never the semantic source for the next restack.

Unexpected movement outside an authorized revision transition:

```text
→ DRIFTED / UNKNOWN_INCONSISTENT
→ fail closed
```

## 18.4 Unknown/orphan/inconsistent state fails closed

Examples include:

```text
contribution-unit worktree exists but mapping/ownership is unknown
unresolved authoritative checkpoint OID is known but no valid managed source can recover it
convergence-unit identity maps ambiguously to refs
promotion unit has ambiguous source bindings or target-incoherent member bindings
required promotion policy is missing/stale/contradictory
derived dependency requires provider topology/capability that is unsupported
submission head moved without authorized revision transition
rewrite operation has unknown owner
target/provider result cannot be attributed consistently
```

While ambiguity can affect ownership or promotion:

```text
do not invent mappings
do not delete unknown work
do not integrate/promote
do not overwrite refs
do not silently alter topology
```

Reconstruct authoritative Git/remote/provider/policy facts or require explicit recovery.

# 19. Branch/ref hierarchy and ownership implications

For each repository-local internal work graph:

```text
ConvergenceBase ref
  └── convergence-unit ref
        ├── contribution unit-A ref → worktree-A
        ├── contribution unit-B ref → worktree-B
        └── contribution unit-C ref → worktree-C
```

The contribution-unit provisioner establishes this graph before the first managed write in each contribution unit.

For each repository-local `contribution_unit_id`, shared coordination state must know/derive:

```text
repository_id
contribution_unit_id
worktree_id/path
contribution_unit_ref
convergence_unit_id
convergence_ref
current exact OIDs
expected internal base
external mutation-access state/handle as supplied by the External Control Plane
```

Before committing or synchronizing a contribution unit, `ruu` verifies:

```text
worktree belongs to expected repository
checked-out ref is expected contribution-unit ref
contribution unit maps to the expected convergence unit
contribution-unit topology/ref was provisioned from that convergence unit
external mutation-access state and exclusive claim authority are valid
actual Git state matches exact assumptions
```

Before `contribution-unit→convergence-unit`, exact checkpoint/source OID, immutable membership/topology, claims/conflict state, exact-state recoverability where relevant,  is revalidated. No separate integration-release/readiness flag exists.

Promotion adds another graph that is **not necessarily identical** to the internal branch hierarchy.

Examples:

```text
DIRECT_TARGET_ADVANCE:
exact convergence-unit source(s)
→ promotion unit
→ target ref

provider submission independent:
exact convergence-unit source(s)
→ promotion unit
→ submission ref
→ provider submission
→ target ref

provider submission stacked:
promotion unit A / submission A
  ↑
promotion unit B / submission B
  ↑
promotion unit C / submission C
```

Internal convergence refs and provider-facing submission refs are always distinct refs/authority objects under ADR-049, even when they currently point to the same exact OID. Submission rewrite authority never aliases or propagates to an internal convergence-unit ref.

Stable IDs are authoritative; branch names are not.

# 20. Cross-repository work, publication relation, and non-atomic promotion

Two different “cross-repository” concepts must not be conflated.

## 20.1 Higher-level work spanning multiple repositories

A higher-level objective may produce repository-local convergence/promotion units in several repositories:

```text
higher-level work
├── Repo-A convergence/promotions
├── Repo-B convergence/promotions
└── Repo-C convergence/promotions
```

Git commits and promotion operations remain repository-local.

There is no native atomic cross-repository promotion transaction.

Therefore higher-level state may legitimately become:

```text
NOT_STARTED
IN_PROGRESS
PARTIALLY_PROMOTED
PROMOTED
UNKNOWN_INCONSISTENT
```

If Repo-A promotion completes while Repo-B remains blocked, the partial state is explicit. Already-promoted repositories are not silently rolled back.

Roll-forward/compensation policy belongs above the repository-local Git mechanics.

## 20.2 Cross-repository provider-submission publication

Separately, one repository-local promotion may have:

```text
publication_relation = CROSS_REPOSITORY
```

meaning:

```text
submission source repository
≠
target repository
```

Typical shape:

```text
fork/submission-ref
→ provider submission
→ upstream/target-ref
```

This does not mean the underlying logical work spans multiple repositories.

The source/publication repository and immutable PromotionTarget are explicit identities. `publication_relation` is derived from those identities; policy/provider facts authorize or block the resulting required operation.

## 20.3 Provider semantic-capability constraints

The core first determines the exact required transition. For example, an unsatisfied ADR-050 dependency in a cross-repository publication context may require:

```text
REPRESENT_PROMOTION_DEPENDENCY(
  publication_relation = CROSS_REPOSITORY,
  exact predecessor/submission/target context
)
```

ADR-051 requires a fresh normalized contextual capability observation for that semantic operation. Execution requires:

```text
REQUIRED by core exact-state semantics
+ SUPPORTED by provider/context
+ AUTHORIZED by EffectivePromotionPolicy
+ ordinary exact-state/Git-validation/transition-local/claim guards
```

Unsupported/unknown operations are localized as:

```text
BLOCKED_POLICY / UNSUPPORTED_TOPOLOGY / UNKNOWN_INCONSISTENT
```

and are not silently transformed into independent provider submissions, one giant provider submission, direct push, or another fallback.

# 21. What `ruu` conceptually does

`ruu` is explicitly invoked to advance **existing managed Git state**.

The later convergence invocation does not provision a missing ContributionUnit/ConvergenceUnit editing surface as a side effect; any required pre-edit provisioning belongs to the earlier integration/provisioner phase and may be supplied by the installed Ruu product under ADR-078.

Invocation principals may include:

```text
coding agent
human
script
Turnlock
/go
automation
another authorized orchestrator
```

The immediate reason for signaling convergence demand may be checkpoint/push/merge/provider-submission/status/recovery, but the authoritative executor services that demand only through the full global fixed-point pass.

Core responsibilities:

```text
A. collect eligible work from contribution units into commits
B. converge ConvergenceBase ↔ convergence-unit ↔ contribution unit internal state
C. publish internal refs safely
D. resolve/revalidate repo promotion policy
E. advance mechanically projected exact PromotionUnits according to that policy
F. publish/revise submission refs where applicable
G. create/update/observe submission/review/check/provider/merge-queue state where applicable
H. observe/establish final target-integration result/proof where required
I. emit/refresh exact `RECONCILIATION_REQUIRED` obligations when semantic authoring is needed
J. evaluate transition-local external facts only where the affected transition requires them
K. perform recovery/cleanup
```

Normative execution rule:

> **Each executed global sweep that services outstanding convergence demand exhaustively re-evaluates every known nonterminal managed obligation across all lifecycle layers, performs every transition that is currently possible, safe, authorized by current policy, claimable, and fully preconditioned, then refreshes and repeats until the current global fixed point is reached. Explicit triggers may coalesce and never narrow that sweep.**

Conceptual flow:

```text
1 authenticate/accept explicit convergence demand and durably advance requested generation
2 establish/revalidate current fenced executor ownership
3 load/revalidate current external ContributionUnit mutation-access state
4 enumerate/reconstruct every known nonterminal managed obligation
5 use/rebuild repository activity indexes only as acceleration structures
6 resolve existing managed identities
7 refresh effective policy and required Git/remote/provider facts for every obligation
8 collect/commit eligible work from contribution units when the ADR-059 checkpoint predicate and current mutation-authority/claim prerequisites hold
9 publish stable contribution unit checkpoints when policy allows
10 fixed-point internal edges:
    ConvergenceBase→convergence-unit while mutable
    convergence-unit→contribution-unit
    contribution-unit→convergence-unit
    semantic conflict → exact-state-bound RECONCILIATION_REQUIRED; authoritative refs unchanged
11 expose/refresh exact reconciliation and other transition-specific external obligations for the external Development System
12 evaluate current transition-local prerequisites and internal convergence-unit readiness
13 evaluate PromotionGroups and their mechanically projected exact PromotionUnits
14 for DIRECT_TARGET_ADVANCE realization:
    refresh/revalidate target+policy
    materialize/revalidate candidate
    descendant-only exact-old CAS+FF target advance
15 for PROVIDER_SUBMISSION realization:
    materialize/update submission refs only when provider projection is currently required/authorized
    preserve or revise heads according to immutable/rewriteable policy
    create/update/observe provider submissions
    react to UPDATE_REQUIRED / RESTACK_REQUIRED / CHANGES_REQUESTED / MERGE_QUEUED / provider finalization
    automatically progress machine-authorized provider target integration once all actual prerequisites are satisfied
16 observe promotion results
17 observe/establish final target-integration result/proof where required
18 retire/cleanup convergence-unit/promotion/provider state whose lifecycle is owned here; resolved ContributionUnit editing-artifact cleanup remains external
19 recompute derived active/quiescent repository indexes
20 continue unrelated work despite blocked/waiting/reconciliation-required items
21 stop only at current global fixed point
```

If required internal topology is missing at convergence time, the convergence engine fails closed/reports the missing pre-edit invariant; it does not retroactively provision the surface. A bundled harness integration/provisioner may repair future authoring before subsequent writes under ADR-078.

If a required work-bearing invocation, PromotionGroup group-local resolution, or exact repository projection is missing/unknown, Ruu does not invent semantic work membership. Internal convergence may still continue.

# 22. Eligibility algorithms

## 22.1 Managed checkpoint adoption and commit collection

For every exact frozen work-bearing handoff, Ruu first observes the current managed ref, worktree, prior checkpoint/admitted base, and canonical ancestry under the current binding/claim/CAS guards.

```text
clean current managed-ref tip K
+ K is an exact ordinary commit
+ K canonically descends the prior authoritative checkpoint or admitted base
+ exact frozen handoff and all authority/topology guards hold
→ adopt K as latest authoritative managed checkpoint
→ create no new commit
```

For an offered/transferable dirty ContributionUnit editing surface, Ruu acquires exclusive mutation authority and reconstructs the exact whole-surface candidate under ADR-058/059.

```text
construct/revalidate canonical checkpoint candidate
(the caller's staged/unstaged partition is not checkpoint-selection authority)

if structural/observability/authority guards fail:
    do not commit or adopt
    localize the exact Git/authority blocker

if candidate tree == parent tree:
    adopt/reuse the exact current parent only when the frozen handoff
    independently satisfies clean-tip adoption guards

otherwise:
    commit exactly that candidate
    record exact authoritative managed checkpoint OID
```

Native commit creation remains exact-state rediscovery. The managed event is clean-tip handoff adoption or dirty-candidate checkpoint adoption. Ruu runs no tests/formatters/generators here and consumes no generic development-validation certificate. The Development System decides when to offer/transfer the surface for Git progression.

## 22.2 ContributionUnit editing-artifact absence, managed-ref abandonment, and exact-state continuity

`ruu` does not decide when a user/agent should delete a ContributionUnit branch/worktree. ADR-071/074/075 nevertheless make a native mutation that terminates/replaces the already-bound managed authoring ref a pre-linearization binding-disposition transition. Terminal removal becomes abandonment only from a positive terminal-removal proof.

```text
OPEN or CLOSED
+ editing branch/worktree exists
→ ordinary checkpoint/synchronization work may proceed when authority permits

OPEN or CLOSED
+ editing branch/worktree absent
+ no unresolved exact managed checkpoint obligation
→ no action required

OPEN or CLOSED
+ editing branch/worktree absent
+ unresolved exact managed checkpoint OID recoverable
→ continue exact-state convergence from OID using isolated workspace where needed

OPEN or CLOSED
+ unresolved exact managed checkpoint OID unrecoverable
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery required
```

Missing local artifacts never imply automatic remote deletion or local recreation. User/agent tooling owns artifact lifecycle. `ruu` does not infer `CLOSED` from inactivity, turn completion, mere artifact absence, clean state, commit, verification, or integration. Only an exact ADR-071 committed managed-ref deletion event carries abandonment meaning.

## 22.3 Convergence-unit reconciliation

For each active ConvergenceUnit:

```text
refresh ConvergenceBase + convergence-unit ref
refresh every ContributionUnit lifecycle, latest authoritative checkpoint OID, exact adopted AuthoringDependencies, and any current editing-surface state
refresh dependency anchors, source handoff/projection attribution, source disposition, and authoritative target satisfaction
refresh exact transition-specific external prerequisite state

evaluate ConvergenceBase→convergence-unit synchronization

for each ContributionUnit:
    evaluate convergence-unit→contribution-unit synchronization
    evaluate contribution-unit→convergence-unit integration

perform all currently safe/authorized non-conflicting Git transitions
semantic conflict requiring authoring → record/refresh exact RECONCILIATION_REQUIRED
new deterministic exact result → continue only if its transition-local exact prerequisites hold
refresh/repeat
```

Whenever reconciliation would create a new exact merge/result state, `ruu` materializes that result as an immutable exact candidate. The authoritative destination changes only when the exact transition-local Git/managed/policy/provider prerequisites hold; no generic development-validation wait exists.

`RECONCILIATION_REQUIRED` is exposed through the External Control Plane contract to the Development System. The Development System authors code; `ruu` never treats the resolver's report as proof. Later sweeps reclassify current Git state and adopt only under current claims/CAS plus any current transition-local exact prerequisite.

Already-committed clean ContributionUnits remain relevant.

## 22.4 `convergence-unit → contribution unit` synchronization

Synchronization has two mechanically equivalent exact-state paths depending on whether a producer editing surface still exists.

### Existing editing surface

If the ContributionUnit branch/worktree is present and synchronization mutates that checked-out state, exclusive ContributionUnit-worktree mutation authority is required.

### Editing surface absent

If the producer branch/worktree is absent but the latest authoritative managed checkpoint OID is still reachable, `ruu` MUST NOT recreate the producer branch/worktree merely to synchronize it. It may materialize the exact descendant/merge result in an isolated integration workspace. A newly synthesized clean result may advance the logical `latest_authoritative_managed_checkpoint_oid` when its exact transition-local topology/claim/conflict/expected-old guards hold.

An operation-owned temporary reachability anchor or equivalent recovery-safe mechanism must keep the new exact OID recoverable until adoption/recovery disposition.

For either path:

```text
UP_TO_DATE
→ no-op

CONTRIBUTION_UNIT_AHEAD
→ no downward sync

CONVERGENCE_UNIT_AHEAD
→ intended synchronized result is exact convergence-unit OID
→ reuse current transition-local exact prerequisites/available
→ if a transition-specific prerequisite is missing/unknown: no authoritative movement
→ otherwise advance existing contribution ref if present, else logical managed-checkpoint record

DIVERGED
→ materialize exact merge candidate without authoritative adoption
→ semantic conflict: RECONCILIATION_REQUIRED
→ deterministic result + missing transition-local prerequisite: no authoritative movement
→ deterministic result + required evidence satisfied: adopt exact merge result under CAS

editing surface dirty
→ checkpoint exact ContributionUnit state first under §22.1, then re-evaluate

required source OID unrecoverable
→ BLOCKED_MISSING_MANAGED_STATE / recovery

UNKNOWN_INCONSISTENT
→ block affected edge
```

No rebase/history rewrite.

## 22.5 `contribution unit → convergence unit` integration

There is no separate ContributionUnit integration-readiness/release state. Every valid authoritative managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit MUST be advanced toward its bound ConvergenceUnit at the earliest mechanically safe opportunity.

Requires:

```text
exact ContributionUnit tip representing a valid authoritative managed checkpoint
exact ConvergenceUnit tip
known immutable ContributionUnit→ConvergenceUnit membership
ConvergenceUnit ref claim
no unresolved conflict
```

Then:

```text
ConvergenceUnit tip ancestor exact ContributionUnit tip
→ exact resulting ConvergenceUnit state = ContributionUnit tip
→ reuse current transition-local exact prerequisites
→ if a required transition-local fact is missing/stale: leave ConvergenceUnit unchanged
→ when satisfied, FF ConvergenceUnit

otherwise
→ synchronize ContributionUnit first
→ revalidate tips/topology/evidence
→ retry
```

An `OPEN` ContributionUnit may be integrated repeatedly as it produces later checkpoints. Experimental/alternative isolation is represented by binding that work to another ConvergenceUnit, not by suppressing integration within the ContributionUnit.

No upward merge into ConvergenceUnit and no rebase.

## 22.6 Convergence-unit internal readiness

A ConvergenceUnit can enter `READY_INTERNAL(OID)` only when:

```text
contribution membership SEALED
zero OPEN ContributionUnits in the convergence scope
for every CLOSED ContributionUnit, latest authoritative managed checkpoint (if any) fully resolved into exact OID
zero orphan/unknown ContributionUnit membership/state
zero BLOCKED_MISSING_MANAGED_STATE or unresolved internal synchronization/integration/reconciliation/conflict/recovery obligation
current transition-local exact prerequisite satisfied for OID when policy requires it
internal Git/convergence fixed point reached for exact OID
```

No second repository-specific semantic-readiness token is required inside `ruu`. Code-state correctness/testing belongs to the Development System; it controls when work is offered and which externally owned lifecycle/governance facts it establishes. There is no generic development-validation evidence object inside `ruu`. Product/governance/submission-author/review/provider requirements belong to later promotion/provider layers.

This state is not semantic product completion.

## 22.7 Repository-policy resolution

Before promotion evaluation, resolve the current effective repository policy from authoritative inputs. Immediately before each policy-sensitive promotion mutation:

```text
re-observe every mutable authoritative policy source required by the mutation
verify trusted target OID / repository-policy anchor
verify provider/org governance observation
verify normalized provider semantic-operation capabilities/current facts
compare exact source identities/revisions/fingerprints when exposed
recompute policy if any authoritative observation changed
verify every exact semantic operation required by current derived topology/publication relation remains contextually supported
```

Cache/TTL cannot satisfy this pre-mutation revalidation requirement. If any authoritative source changed:

```text
prior policy snapshot → STALE
invalidate stale promotion authorization/evidence
→ recompute before mutation
```

If no atomic provider check+mutation primitive exists, perform the fresh observation immediately before the mutation and treat provider enforcement plus exact post-operation observation/rejection as the final external authority boundary.

If unknown/contradictory:

```text
BLOCKED_POLICY / UNKNOWN_INCONSISTENT
```

Internal convergence can continue if unaffected.

## 22.8 Promotion-unit eligibility

A promotion unit is eligible for mechanical promotion only when:

```text
promotion_unit_id known
exact source convergence-unit IDs/OIDs declared
all required source states exact/ready/current
every carried AuthoringDependency is SATISFIED_BY_TARGET,
  INTERNAL_TO_SAME_GROUP, or resolved to a currently valid promotion projection
current promotion dependency/topology known from adopted authoring provenance
  plus exact managed predecessor/target facts
repo policy current
target observation current
no ambiguous source binding
promotion operation claim available
required semantic/higher-level readiness signal valid if configured
```

`RAW_AUTHORING_SOURCE`, `RECONCILIATION_REQUIRED`, an invalidated parent disposition, or more than one independently unsatisfied external predecessor blocks realization only for the affected projection. It does not block candidate materialization, internal convergence, or unrelated obligations.

If ADR-048 materializes a new exact candidate state, DIRECT_TARGET_ADVANCE or provider-submission publication/finalization depends only on the exact promotion/policy/provider prerequisites of that transition.

Ruu never invents source grouping or provider topology.

## 22.8A AuthoringDependency reconciliation

For each adopted AuthoringDependency `(consumer, source, A)`:

```text
required exact anchor missing/unreachable
→ UNKNOWN_INCONSISTENT / BLOCKED_MISSING_MANAGED_STATE

fresh authoritative consumer target O contains A under canonical ancestry
→ adopt SATISFIED_BY_TARGET(exact proof)

same immutable PromotionGroup contains authoritative source and consumer handoffs
+ exact frozen source checkpoint S contained A before downward synchronization
+ exact group-local state incorporates S and the consumer handoff
→ adopt INTERNAL_TO_SAME_GROUP
→ no provider dependency edge

first qualifying source handoff accepted after durable dependency-selection TX-A
+ same source ContributionUnit identity
+ exact frozen/adopted source checkpoint S contained A before downward synchronization
+ exact group-local source state K attributable to that handoff incorporates S
+ source and consumer immutable PromotionTargets exactly equal
+ current source/group disposition authorizes the path
→ CAS-adopt RESOLVED_PROMOTION_PROJECTION(group_id, source_repository_id)
→ retain A separately from K

source realization path lost before target satisfaction
→ RECONCILIATION_REQUIRED(SOURCE_REALIZATION_PATH_LOST)

qualifying source handoff exists but immutable PromotionTargets differ
→ RECONCILIATION_REQUIRED(TARGET_INCOHERENT_AUTHORING_DEPENDENCY)
→ no retargeting or cross-target stack inference

identity/attribution ambiguous or several candidate groups without one
source-handoff owner
→ UNKNOWN_INCONSISTENT

qualifying source handoff accepted after TX-A but before dependency-adoption TX-B
→ TX-B/recovery may adopt directly as resolved after all exact guards
→ never strand the dependency solely because anchor/adoption overlapped handoff
```

For a resolved separate-group dependency, ADR-050 receives immutable owned `(old_base=A, owned_candidate=B)` plus current parent `K`. It never derives source identity from candidate ancestry alone and never mutates an active consumer worktree.

## 22.9 DIRECT_TARGET_ADVANCE realization

Direct promotion requires:

```text
target_realization_route = DIRECT_TARGET_ADVANCE
zero raw or resolved-but-target-unsatisfied external AuthoringDependencies
zero unsatisfied promotion predecessors
target ref policy-authorized mutable
exact authoritative expected target OID B
exact promotion-unit source binding
exact ADR-048 candidate C
all transition-local exact prerequisites for C
B ancestor-or-equal C
no conflict
current target operation claim
current policy/capability facts required by the target backend
```

The normative target mutation is:

```text
AdvanceTargetFF(
  target_ref,
  expected_old = B,
  new = C
)
```

with one atomic semantic effect:

```text
current(target_ref) == B
AND B ancestor-or-equal C
→ target_ref := C

otherwise
→ no target mutation
```

The candidate is already materialized before this operation and must satisfy the exact transition-local prerequisites of this operation. DIRECT_TARGET_ADVANCE therefore performs no checkout, merge, rebase, target-worktree staging, or pre-advancement of a local target branch. An attempt-scoped recovery anchor keeps exact C durably reachable until Observation/Adoption makes that anchor disposable.

Immediately before the mutation, `ruu` revalidates the authoritative target, policy/capability facts, exact candidate and its transition-local prerequisites, and target-operation claim. If the target is no longer exactly B, the attempt is stale even when the new target would still be an ancestor of C; the governing target baseline changed and the promotion must be recomputed/revalidated.

Recovery observes the authoritative target:

```text
current target == B
→ effect not yet realized; retry only after fresh guards

current target == C
→ effect realized; adopt

C ancestor current target
→ effect realized and later target progress occurred; adopt

otherwise
→ effect not proven; mark stale/drifted as appropriate and recompute
```

The core depends on this semantic CAS+FF contract, not on a specific Git/provider command. A backend is conforming only if it preserves exact expected-old comparison and the descendant-only effect; capability to perform a force-style update does not authorize or weaken the target contract.

No force-push/rebase of target.

## 22.10 Independent provider-submission promotion

Requires:

```text
target_realization_route = PROVIDER_SUBMISSION
promotion_dependency = NONE | SATISFIED_BY_TARGET
all AuthoringDependencies terminally target-satisfied or internal to the same group
valid SAME/CROSS_REPOSITORY publication relation
exact source binding
submission identity/ref known or safely creatable
target/provider state current
submission operation claim
```

Then:

```text
materialize exact submission revision
→ establish/revalidate the exact transition-specific publication prerequisites for the revision
→ choose publication intent:
     REVIEW_NOT_REQUESTED
     REVIEW_REQUESTED
→ if REVIEW_REQUESTED:
     configured submission-author/ship-ready gate must hold for exact revision
→ publish according to immutable/rewriteable class
→ create/update current PublicationEpisode provider submission
→ if prior episode is terminal and ADR-055 continuation is required, create a distinct new episode/provider submission rather than reopening it
→ verify provider head == exact current submission head
→ bind review-request intent + provider state to exact revision/head
```

`REVIEW_NOT_REQUESTED` is exceptional policy-authorized publication, not a mandatory precursor to `REVIEW_REQUESTED`.

The target ref remains read-only to `ruu`.

## 22.11 Stacked provider-submission promotion

Requires:

```text
target_realization_route = PROVIDER_SUBMISSION
current promotion_dependency = UNSATISFIED(parent_submission_id,parent_exact_head)
that predecessor was resolved from durable authoring provenance or another already-authoritative promotion relation
exactly one external predecessor remains unsatisfied for this submission revision
provider/policy supports representing the dependency as a stack
all predecessor identity/head/base requirements current
exact submission revision ownership
```

Conceptually:

```text
target
  ↑
submission-A / provider-surface-A
  ↑
submission-B / provider-surface-B
  ↑
submission-C / provider-surface-C
```

Every exact submission revision newly produced by stack materialization/restacking must satisfy the exact revision/publication/policy/provider prerequisites before authoritative publication.

A lower-layer change/merge/provider event may create `RESTACK_REQUIRED` for dependent submissions.

If the dependency predecessor changes and the submission is authorized to revise:

```text
claim exact submission
→ revalidate old owned anchor (B0,C0), current predecessor/base B1, current bound head H
→ derive exact state-transplant result: base=B0, ours=B1, theirs=C0
→ create/observe exact new provider-facing head H2 over B1
→ keep all internal source refs/OIDs and C0 unchanged
→ validate RestackContract/dependency/current policy+capabilities
→ publish only submission ref with expected-old H protection
→ observe provider head == H2
→ increment submission revision
→ re-read head-bound evidence
```

Each layer independently carries:

```text
REVIEW_NOT_REQUESTED
or
REVIEW_REQUESTED
```

according to publication policy. A layer whose review is requested carries the configured ship-ready assertion for its exact dependency context.

Internal contribution-unit/convergence-unit refs remain unchanged.

## 22.12 Provider-required base update / restack

Do not conflate:

```text
semantic changes requested
provider UPDATE_REQUIRED
stack RESTACK_REQUIRED
unexpected head drift
```

Semantics:

```text
CHANGES_REQUESTED
→ ensure/refresh one exact ADR-053 ReviewCorrectionDemand
→ External Control Plane may restore/start a correction continuation session
→ that session may explicitly reactivate affected existing convergence unit(s) while discovering required scope
→ source binding becomes stale once such semantic reopen occurs until explicit new state is ready
→ if ship-ready assertion no longer holds, publication intent may return to REVIEW_NOT_REQUESTED

UPDATE_REQUIRED
→ provider-facing update workflow only
→ no implicit new contribution unit authority
→ any newly produced submission result requires exact transition-local publication prerequisites

RESTACK_REQUIRED
→ exact predecessor/base has changed for a child with an unsatisfied dependency
→ reproject immutable owned `(old_base_oid, owned_candidate_oid)` onto current new base by ADR-050 three-way state transplant
→ no internal source rewrite and no chained restack from prior provider head
→ conflict requiring authoring → RECONCILIATION_REQUIRED / RESTACK_BLOCKED
→ clean exact new revision requires ADR-049 exact expected-old/publication guards

unexpected movement
→ DRIFTED/UNKNOWN
→ fail closed
```

## 22.13 Cross-repository provider-submission publication

For `publication_relation = CROSS_REPOSITORY`:

```text
exact submission revision satisfies current publication prerequisites
→ publish submission ref to configured source/fork repository
→ choose/preserve REVIEW_NOT_REQUESTED or REVIEW_REQUESTED intent
→ create/update the current PublicationEpisode provider submission toward exact target repository/ref
→ if the prior episode is terminal but the same nonterminal logical submission needs another exact publication, create a new ADR-055 episode/provider submission
→ verify provider head/revision/episode binding
→ observe upstream provider state
```

Cross-repository transport does not weaken exact-state binding, transition-local policy guards, or review-request semantics.

Ruu does not infer whether several internal ConvergenceUnits belong to one upstream contribution; that membership is encoded by the accepted work-bearing invocation and immutable PromotionGroup, then projected mechanically into the PromotionUnit.

## 22.14 Unsupported policy/topology

Examples:

```text
DIRECT_TARGET_ADVANCE route + unresolved dependency requiring provider-submission dependency representation
required REPRESENT_PROMOTION_DEPENDENCY operation unsupported in current provider context
cross-repository dependency representation unsupported in current provider context
required submission revision forbidden/unsupported for an immutable submission ref
DIRECT target advancement forbidden by current provider-submission-required governance
```

Result:

```text
BLOCKED_POLICY / UNSUPPORTED_TOPOLOGY
```

Never silently fallback to a different governance model.

## 22.15 Transition-local external facts and exact-state reuse

For every transition, `ruu` re-reads the exact state and only the external facts specific to that transition.

```text
checkpoint
→ mutation access / transferable offered surface

internal integration
→ lifecycle/membership/topology + exact Git ancestry/conflict state

review-request mutation
→ exact-revision review-request intent + current publication policy

provider-governed completion
→ exact current provider checks/reviews/queue/target facts
```

Where a transition-specific fact/evidence is reusable, reuse is allowed only while its exact subject and relevant policy/context remain current. Never reuse authority solely by ContributionUnit ID, branch/ref name, ConvergenceUnit ID, PromotionUnit ID, provider submission number/identity, caller identity, session state, or prior generic `PASS`.

## 22.16 Development-verification execution capacity — external

ADR-057/060 leave all development-quality execution and capacity management outside `ruu`. The engine does not maintain validation queues, worker reservations, validation-demand obligations, or evidence-cache state. If external semantic authoring is required, an existing transition-specific obligation such as `RECONCILIATION_REQUIRED`, review correction, or settlement carries the handoff.

# 23. Example scenario

Initial managed state:

```text
Repo1 contribution-unit A:
  dirty; transferable to Ruu

Repo2 contribution-unit B:
  dirty; transferable to Ruu

Repo1 contribution-unit C:
  dirty; protected externally

Repo3 contribution-unit D:
  dirty; generally transferable
```

All contribution units were already provisioned before the convergence invocation; in the ordinary supported-harness path this may have been done automatically by Ruu-supplied integration.

An explicit authorized principal signals convergence demand after the current External Control Plane authority state is visible:

```text
invocation_principal = coding agent / Turnlock / human / script / other
external mutation_access includes:
  Repo1 / contribution-unit A = TRANSFERABLE_TO_RUU
  Repo2 / contribution-unit B = TRANSFERABLE_TO_RUU
  Repo1 / contribution-unit C = PROTECTED_EXTERNAL
  Repo3 / contribution-unit D = TRANSFERABLE_GENERAL
```

Commit eligibility:

```text
Repo1 / contribution-unit A
→ transferable to Ruu
→ claimable subject to ordinary guards

Repo2 / contribution-unit B
→ transferable to Ruu
→ claimable subject to ordinary guards

Repo1 / contribution-unit C
→ protected externally
→ protected

Repo3 / contribution-unit D
→ generally transferable
→ claimable subject to ordinary guards
```

After commit collection, the current global sweep continues:

```text
Repo1 contribution-unit A ↔ convergence-unit-X
Repo2 contribution-unit B ↔ convergence-unit-X
Repo3 contribution-unit D ↔ convergence-unit-Y
plus every other actionable managed repo/unit/promotion/provider state
```

Now suppose immutable targets/derived repository relations and current policies differ:

```text
Repo1:
  PromotionTarget = Repo1/main
  publication_relation = SAME_REPOSITORY   # derived
  policy.target_realization_route = DIRECT_TARGET_ADVANCE

Repo2:
  PromotionTarget = Repo2/main
  publication_relation = SAME_REPOSITORY   # derived
  policy.target_realization_route = PROVIDER_SUBMISSION
  promotion_dependency = NONE | SATISFIED_BY_TARGET

Repo3:
  PromotionTarget = upstream3/main
  publication_relation = CROSS_REPOSITORY  # derived from source Repo3 + target upstream3
  policy.target_realization_route = PROVIDER_SUBMISSION
  promotion_dependency = NONE | SATISFIED_BY_TARGET
```

The same global sweep may therefore:

```text
Repo1
→ internal convergence
→ direct target promotion if exact promotion unit is ready

Repo2
→ internal convergence
→ publish/update submission ref
→ create/update/check provider submission

Repo3
→ internal convergence
→ publish submission ref to configured source/fork
→ create/update/check upstream provider submission
```

A blocked provider submission in Repo3 does not stop Repo1/Repo2.

The invocation principal's identity does not replace contribution-unit identity, external mutation-access state, repository policy, or fenced executor ownership.

# 24. Simultaneous convergence-demand example

Suppose one global sweep is already running while three callers invoke `ruu` after making different current-state changes visible:

```text
current executor targets requested_generation = 41

caller A signals demand → requested_generation = 42
caller B signals demand → requested_generation = 43
caller C signals demand → requested_generation = 44
```

The current executor does **not** replay three caller-specific invocations. After it reaches the fixed point for its current sweep, it observes:

```text
processed_generation = 41
requested_generation = 44
```

and performs one new global sweep over the then-current managed universe. That sweep may cover all state made visible before generations 42, 43, and 44.

If the new sweep reaches its fixed point with no newer demand:

```text
processed_generation = 44
requested_generation = 44
→ release executor ownership and exit
```

If another caller signals generation 45 before release, the race-safe demand/ownership transition guarantees either the current executor observes the newer demand and continues or the new caller establishes a new executor after the previous ownership is released. Demand cannot be stranded between "queue empty" observation and executor exit.

## 24.1 Authority changes are separate from demand triggers

Suppose the External Control Plane makes two editing surfaces transferable while a sweep is already running:

```text
ContributionUnit A → TRANSFERABLE_TO_RUU
ContributionUnit B → TRANSFERABLE_TO_RUU
```

Those authority changes are durable External Control Plane state. Callers may then signal one or more convergence demands.

The next global sweep sees the **current authority state** for both A and B regardless of which trigger followed which authority update. It may claim/process A and B concurrently only if their exact resource/external-evidence prerequisites are independent.

The trigger never acts as the authority token:

```text
convergence demand generation 44
≠ authority for ContributionUnit A
≠ authority for ContributionUnit B
```

## 24.2 Crash recovery and fenced successor establishment

Suppose run generation 7 crashes. Its process-lifetime OS lock is released automatically, while SQLite may still durably show the old generation as `ACTIVE`.

The next caller that acquires the OS lock transactionally establishes generation 8 with a fresh `run_token`:

```text
generation 8 ACTIVE established
→ generation 7 loses authoritative scheduling/observation/adoption authority
```

A late worker result from generation 7 may physically exist and may be considered as input by recovery, but it cannot by itself mutate authoritative coordination state. Generation 8 re-observes exact current Git/provider facts and revalidates expected-state/CAS rules before any Adoption.

If generation 7 is alive but genuinely hung, it retains the OS lock and generation 8 is not automatically established by TTL/heartbeat. Normal long operations are bounded; provider/CI waits are localized as nonterminal obligations rather than slept on while holding top-level ownership.

# 25. Convergence-unit and promotion examples

## 25.1 Two contribution units converge internally

Initial:

```text
target/main        → C
convergence-unit-X → C
contribution unit-A           → C
contribution unit-B           → C
```

Contribution unit A commits:

```text
contribution unit-A → A1
```

Contribution unit B commits independently:

```text
contribution unit-B → B1
```

A convergence pass may first advance:

```text
convergence-unit-X → A1
```

Contribution unit B is now behind/diverged relative to the convergence unit.

After safe `convergence-unit→contribution-unit-B` synchronization:

```text
contribution unit-B → B1'
```

and exact revalidation, upward integration may FF:

```text
convergence-unit-X → ... → B1'
```

ContributionUnit branch/worktree deletion is external and unrelated to whether the current exact state has integrated.

When both ContributionUnits are explicitly `CLOSED`, their latest authoritative managed checkpoints are fully resolved, ConvergenceUnit membership is `SEALED`, and exact internal Git/convergence guards  are satisfied:

```text
convergence-unit-X
→ READY_INTERNAL(XH)
```

This does not imply a product feature is complete.

## 25.2 Solo trunk-based direct promotion

Suppose Repo1 policy is:

```text
target_realization_route = DIRECT_TARGET_ADVANCE
target_ref = main
```

and higher-level/default policy declares:

```text
promotion-unit P1
sources = {convergence-unit-X@XH}
```

Then `ruu` may:

```text
refresh main + policy
→ reconcile/revalidate candidate
→ ensure exact expected main
→ advance main descendant-only
→ ordinary FF/expected-old push
→ observe remote main
→ PROMOTED
```

If main changed concurrently, the stale direct promotion is discarded/recomputed.

## 25.3 Strict team independent provider submission (GitHub PR example)

Repo2 target/context + policy:

```text
PromotionTarget = Repo2/main
publication_relation = SAME_REPOSITORY   # derived
promotion_dependency = NONE | SATISFIED_BY_TARGET
policy.target_realization_route = PROVIDER_SUBMISSION
```

Promotion-unit P2 becomes:

```text
exact convergence-unit source(s)
→ submission ref
→ provider submission
→ target/main
```

`ruu` publishes/binds the exact current submission head, then provider CI/review/merge governance owns target entry.

## 25.4 External fork provider submission (GitHub PR example)

Repo3 target/context + policy:

```text
PromotionTarget = upstream3/main
publication_relation = CROSS_REPOSITORY  # derived
promotion_dependency = NONE | SATISFIED_BY_TARGET
policy.target_realization_route = PROVIDER_SUBMISSION
```

Then:

```text
source-fork/submission-ref
→ provider submission
→ upstream/target-ref
```

The External Control Plane has already declared which exact convergence units belong to this one upstream contribution. `ruu` does not split/combine them semantically.

## 25.5 Stacked PRs

Derived unsatisfied dependency:

```text
P1
↓
P2 depends on P1
↓
P3 depends on P2
```

Provider-facing topology:

```text
target
  ↑
submission-P1 / PR1
  ↑
submission-P2 / PR2
  ↑
submission-P3 / PR3
```

If a lower-layer predecessor exact head changes, the dependent submission becomes `RESTACK_REQUIRED`; only the ADR-049 submission ref may be revised, using ADR-050 exact state-transplant semantics.

Underlying contribution-unit/convergence-unit refs retain stable OIDs.

# 26. Important invariants

## Invariant 1 — No shared mutable checkout between concurrent contribution units
Two concurrently active contribution units never write the same physical worktree.

---
## Invariant 1A — V1 managed authoring requires a dedicated Git worktree substrate
Every actively authored v1 ContributionUnit is provisioned with a dedicated Git worktree/ref surface before its first managed write. V1 defines no alternative direct authoring substrate that bypasses this topology with arbitrary prebuilt commit/tree/snapshot input. Post-capture worktree absence does not erase durable ContributionUnit identity or exact managed checkpoints.

---
## Invariant 2 — Every contribution unit has one stable repository-local convergence scope
Each `contribution_unit_id` maps to exactly one `repository_id` and exactly one `convergence_unit_id` membership for that identity. While active editing is provisioned, isolation uses a dedicated worktree/ref surface; that surface may later disappear without erasing the ContributionUnit identity or any already-created exact managed checkpoint. Changing convergence scope requires a new ContributionUnit.

---
## Invariant 3 — Pre-edit provisioning happens before first managed write
Repository/convergence-unit/contribution-unit/worktree topology and its safe mutation-authority mechanism must be established before the first managed write.

---
## Invariant 4 — Pre-edit provisioning is not a convergence side effect
The later `ruu` convergence invocation never silently creates a missing ContributionUnit/editing surface as part of convergence. A Ruu-supplied harness integration may perform the distinct pre-edit provisioner role before first managed write under ADR-078.

---
## Invariant 5 — Convergence unit is Git-level, not product-level
`ruu` assigns no product-feature/task semantics to a convergence unit.

---
## Invariant 6 — Convergence-unit identity is independent of branch name
Stable `convergence_unit_id` and exact refs/OIDs, not descriptive branch text, drive correctness.

---
## Invariant 7 — Contribution-unit refs branch from convergence-unit refs
Contribution-unit refs are provisioned from their convergence-unit ref, never directly from ConvergenceBase.

---
## Invariant 8 — External producer/runtime liveness is outside `ruu`
`ruu` never infers safe worktree transferability from heartbeat, timeout, process/session state, turn lifecycle, or model identity.

---
## Invariant 9 — Invocation principal, trigger, and contribution-unit identity are distinct
Human/agent/script/Turnlock/`/go`/automation identity and the convergence trigger it emits do not imply contribution-unit-worktree mutation authority.

---
## Invariant 10 — External mutation protection is absolute
`PROTECTED_EXTERNAL` or `UNKNOWN` never authorizes contribution-unit-worktree mutation.

---
## Invariant 11 — Transferability still requires a race-safe exclusive claim
`TRANSFERABLE_TO_RUU` or `TRANSFERABLE_GENERAL` permits only an attempt to claim. Mutation requires the current authoritative executor/operation to hold the exclusive worktree claim, with transferability revalidated under the same authority arbitration and external reacquisition prevented while the claim is held.

---

## Invariant 12 — Contribution-unit identity is opaque
`ruu` does not derive `contribution_unit_id` or mutation authority from principal, process, session, branch name, worktree path, or CWD.

---
## Invariant 13 — Commit does not imply contribution-unit closure
Checkpoint commit, eager upward integration, contribution-unit closure, convergence-unit membership sealing/readiness, and promotion readiness are separate states.

---
## Invariant 14 — Contribution-unit lifecycle is externally authoritative and runtime-independent
`ruu` never infers `CLOSED` from agent/process inactivity, waiting for user input, turn completion, clean state, commit, external development-validation PASS/attestation, current integration state, or branch/worktree presence/absence.

---
## Invariant 15 — Terminal contribution units never reopen
`CLOSED` never transitions back to `OPEN`. Any later contribution to the same or another convergence scope requires a new `contribution_unit_id`.

---
## Invariant 16 — Valid ContributionUnit checkpoints converge upward eagerly
Every valid authoritative managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit MUST be advanced toward its bound ConvergenceUnit at the earliest mechanically safe opportunity. An `OPEN` ContributionUnit may integrate multiple checkpoints and later contribute again before terminal closure.

---
## Invariant 17 — `READY_INTERNAL` requires sealed membership and zero unresolved contribution obligations
A ConvergenceUnit cannot become internally ready while contribution membership is `OPEN`, any ContributionUnit remains `OPEN`, any CLOSED ContributionUnit has an unresolved exact managed checkpoint, any unknown/orphan membership/state exists, any required exact managed checkpoint is unrecoverable, or any internal synchronization/integration/reconciliation/conflict/recovery transition remains unresolved. The internal Git/convergence fixed point and all transition-local prerequisites are also required. Physical historical ref retention alone does not block readiness.

---
## Invariant 17A — Convergence grouping is External-Control-Plane authoritative
The External Control Plane creates/reuses ConvergenceUnits, binds each new ContributionUnit to exactly one ConvergenceUnit, and declares membership `OPEN` or `SEALED`. `ruu` never infers grouping/sealing from caller, task, file overlap, branch name, CWD, or actor identity.

---
## Invariant 17B — ContributionUnit identity survives editing-artifact absence; managed-ref deletion is a separate lifecycle event
A ContributionUnit is not its local/remote branch or worktree. Mere editing-artifact absence creates no automatic closure, recreation, or remote-deletion intent, and exact managed checkpoints remain independently recoverable. Separately, ADR-071/074/075 capture native cessation/replacement of the currently bound managed authoring ref before linearization and classify terminal abandonment only from positive causal proof. Only a still-required OID that becomes unrecoverable creates localized `BLOCKED_MISSING_MANAGED_STATE`/recovery.

---
## Invariant 17C — External dependencies are explicit contract clauses
Any logical/runtime declaration required from outside `ruu` must be defined by `EXTERNAL-CONTROL-PLANE-CONTRACT.md` or an ADR that amends it. External declarations never manufacture exact Git/provider truth.

---
## Invariant 18 — Internal refs are append-only
Contribution unit and convergence-unit refs never rebase/amend/backward-reset/non-fast-forward rewrite under `ruu`.

---
## Invariant 19 — Internal ref mutation is descendant-only
Except guarded deletion, contribution-unit/convergence-unit ref updates advance to descendants.

---
## Invariant 20 — `convergence-unit→contribution-unit` uses merge/FF, never rebase
Downward synchronization is no-op, FF, or descendant merge after exact classification.

---
## Invariant 21 — `contribution-unit→convergence-unit` is FF-only
Upward integration requires exact convergence-unit tip to be ancestor of exact contribution unit tip.

---
## Invariant 22 — Diverged contribution unit synchronizes downward before upward integration
`ruu` never merges a diverged contribution unit directly upward.

---
## Invariant 23 — Exact Git ancestry determines internal graph relation
Equal/ancestor/diverged classification comes from authoritative Git, not heuristics/metadata.

---
## Invariant 24 — Contribution-unit-worktree mutation requires exclusive claim
Commit, synchronization candidate mutation, reset/check-out effects, and any other `ruu` mutation of an existing ContributionUnit worktree require exact worktree authority. Semantic conflict authoring is outside `ruu`.

---
## Invariant 25 — Shared ref mutations require exact expected-state coordination
Competing convergence-unit/target/submission operations cannot act on stale refs.

---
## Invariant 26 — Conflicts are blocked states
A conflicted operation never counts as successful convergence/promotion.

---
## Invariant 26A — Semantic conflicts emit exact reconciliation obligations
If deterministic Git/repository mechanics cannot construct a safe result without semantic authoring, authoritative refs remain unchanged and an exact-state-bound `RECONCILIATION_REQUIRED` obligation is exposed to the external Development System. The obligation is diagnostic, not adoption authority.

---
## Invariant 26B — Candidate attribution is mutation-boundary scoped
Process identity does not determine contribution ownership. State produced inside a valid ContributionUnit mutation-authority boundary is attributed to that ContributionUnit candidate; known authority violations fail closed as integrity/staleness conditions.

---
## Invariant 27 — Integration/projection work never hijacks externally protected contribution-unit worktrees
Shared merges and ADR-048 promotion-candidate materialization use isolated owned state.

---
## Invariant 28 — Shared Git coordination state spans provisioner and converger
Registry/authority/claims/promotion/provider/recovery state is a common substrate, not owned solely by one command.

---
## Invariant 29 — Git/remote/provider facts outrank stale coordination metadata
Material disagreement is reconstructed or fails closed.

---
## Invariant 30 — Repository activity is a derived acceleration index, not processing authority
Known/quiescent repository metadata may optimize discovery, but authoritative nonterminal managed obligations define what must be re-evaluated. An activity index may never make an existing obligation disappear from a global sweep.

---
## Invariant 31 — Every nonterminal managed obligation remains globally visible
Any unresolved contribution-unit, convergence-unit, promotion, publication, submission/review/check/provider, merge-queue/update/restack, final-integration-proof, recovery, claim, or cleanup responsibility remains part of the authoritative global managed-obligation universe until terminally resolved.

---
## Invariant 32 — Repository quiescence requires zero authoritative nonterminal obligations
A repository may leave the derived active index only when authoritative managed records contain no nonterminal obligation for it. A stale/missing index is reconstructed rather than trusted.

---
## Invariant 33 — Caller, CWD, age, trigger generation, and local workflow identity do not define scope
`ruu` evaluates the full known nonterminal managed-obligation universe. Invocation directory, caller identity, trigger reason/generation, repository age, ContributionUnit, ConvergenceUnit, or PromotionUnit identity do not narrow it.

---
## Invariant 34 — No whole-disk Git discovery
`ruu` never recursively scans arbitrary `.git` repositories as normal scope construction.

---
## Invariant 35 — `ruu` is explicitly invoked
No background/implicit convergence starts merely because a contribution unit needs a worktree.

---
## Invariant 36 — Every serviced convergence demand is satisfied only by a global managed-obligation sweep
Explicit triggers may coalesce, but every executed sweep used to service outstanding demand evaluates the complete known nonterminal managed-obligation universe. Trigger reason does not narrow scope; external waits remain nonterminal and are refreshed on every later global sweep.

---
## Invariant 37 — Fixed-point convergence is iterative
Mutation/publication/provider/policy changes trigger refresh and re-evaluation until current fixed point.

---
## Invariant 38 — Localized blocking never becomes a global mutex
Blocked/waiting work on one resource does not stop unrelated actionable resources.

---
## Invariant 39 — Repository promotion policy is repository-local
Different repos in one global sweep may legitimately use different target-realization routes/topologies/relations.

---
## Invariant 40 — Promotion policy is revalidated
Effective policy is refreshed on every executed global sweep, and every policy-sensitive promotion mutation requires an immediately preceding re-observation/revalidation of all mutable authoritative policy sources needed by that mutation.

---
## Invariant 40A — Promotion authorization has no runtime/local bypass
Caller identity, human/agent/orchestrator request, and explicit local config cannot enlarge or replace the `EffectivePromotionPolicy`. Different behavior requires a change to an authoritative policy/governance source followed by ordinary revalidation.

---
## Invariant 40B — Repository policy cannot self-authorize from the candidate it governs
Repo-committed policy for a promotion is taken from the trusted exact target baseline. A candidate-only policy change becomes eligible to govern later promotions only after it becomes authoritative target state.

---
## Invariant 40C — Authoritative promotion constraints compose; contradictions remain visible
Provider capabilities/current facts, provider/org governance, and trusted repository policy are jointly composed according to their constraint semantics. No generic precedence silently repairs incompatible explicit constraints.

---
## Invariant 40D — Built-in policy rules only close underdetermined dimensions
Built-in rules may derive a complete policy without repository onboarding, but cannot weaken or contradict an explicit authoritative constraint. Absence of a repo policy file alone is not `MISSING`.

---
## Invariant 40E — Policy contradiction diagnostics are factual, not prescriptive
A `CONTRADICTORY` policy exposes machine-readable incompatible constraints and exact source provenance to the external system. `ruu` does not recommend, rank, or apply remediation.

---
## Invariant 40F — Cache/TTL never establishes promotion-policy currentness
Cached policy/observation data may optimize resolution, but cache presence, age, TTL, or prior success never authorizes a policy-sensitive promotion mutation.

---
## Invariant 40G — Authority-anchor movement invalidates the policy snapshot
Any changed trusted target OID/repo-policy anchor or mutable provider/org governance/capability/fact observation used by the policy makes the prior snapshot `STALE`; mutation waits for recomputation.

---
## Invariant 40H — Non-atomic provider freshness ends at provider enforcement and exact observation
When the provider exposes no atomic governance-check+mutation primitive, `ruu` performs immediate pre-mutation re-observation. Provider enforcement/rejection and exact post-operation observation are the final external authority boundary; concurrent drift is surfaced factually and never auto-repaired.

---
## Invariant 41 — Stale/unknown/contradictory policy fails closed for promotion
Policy ambiguity cannot authorize direct push, provider-submission rewrite, or topology fallback.

---
## Invariant 42 — Policy mode, derived repository relation, and derived topology are distinct
`DIRECT_TARGET_ADVANCE|PROVIDER_SUBMISSION` is a target-realization-route authorization dimension. `SAME_REPOSITORY|CROSS_REPOSITORY` is derived from authoritative source repository identity plus the immutable PromotionTarget. `INDEPENDENT|STACKED` is current derived promotion topology under ADR-050. Neither relation nor topology is a caller/policy-selected publication-layout preference.

---
## Invariant 43 — Unsupported required operations never silently fallback
If the semantic operation required by current exact state/topology is unsupported, unknown, or forbidden, the affected obligation blocks/waits explicitly rather than changing topology, target-realization route, repository relation, or grouping.

---
## Invariant 43A — Provider capability is semantic and contextual
The core queries a versioned semantic operation against an exact provider context. Provider-wide feature labels/booleans are never sufficient applicability or authorization evidence.

---
## Invariant 43B — Required, supported, and authorized are separate guards
A provider operation may execute only when it is required by core exact-state semantics, supported in the current provider context, authorized by current effective policy, and all ordinary exact-state/transition-local/claim/recovery guards hold.

---
## Invariant 43C — Provider-native executors never own normative semantics
Provider-native or external mechanisms may execute a core operation only if their exact observed result conforms to the same normative contract. API success or feature identity alone is not adoption evidence.

---
## Invariant 44 — Promotion unit is distinct from convergence unit
A PromotionUnit is an immutable non-empty set of canonical exact ConvergenceUnit-state references from exactly one authoritative source repository, mechanically materialized from one repository projection of a complete adopted PromotionGroup group-local exact resolution.

---
## Invariant 44A — PromotionUnit identity is content-addressed and deterministic
The v1 `promotion_unit_id` is SHA-256 over a domain-separated/versioned unambiguous canonical encoding of the sorted exact member refs. Same exact member set has one identity; any member-state change has a different identity.

---
## Invariant 44B — PromotionUnit definition never mutates
There is no update-in-place of PromotionUnit members. Lifecycle/provider state may progress while the immutable exact member definition and content address remain unchanged.

---
## Invariant 44C — PromotionUnit declaration is intrinsically idempotent
Redeclaring the same canonical member set returns/reuses the same PromotionUnit. Stored ID/definition mismatch fails closed as an integrity/unknown-inconsistent condition.

---
## Invariant 44D — PromotionUnit identity excludes policy, topology, lifecycle, and semantic identity
Target/mode/publication relation, runtime/local policy input, topology edges/parents, lifecycle, submission revision, semantic task identity, and semantic-readiness tokens do not participate in the PromotionUnit definition or content address.

---
## Invariant 44E — Structural declaration validity and promotion eligibility are distinct
A mechanically valid immutable PromotionUnit may exist while its exact members, topology, policy, provider state, transition-local policy/provider facts, conflict, or recovery guards make it currently ineligible.

---
## Invariant 45 — Ordinary PromotionGroup membership is derived from the sealed work-bearing invocation cohort
For ordinary new work, the Development System supplies the closed ContributionUnit handoff set of one work-bearing logical invocation. `ruu` derives the distinct ConvergenceUnit member set mechanically from the already-authoritative ContributionUnit bindings. It never invents cohort membership from code semantics, branch/task/session names, ancestry, caller identity, or silence; a later ordinary invocation remains a distinct PromotionGroup occurrence even when the derived member set is identical.

---
## Invariant 46 — Promotion source bindings are exact-state-bound and group-local
Movement/reopen/current-state change of a live ConvergenceUnit cannot mutate an existing PromotionUnit and does not by itself stale an older PromotionGroup's adopted exact member state. A different PromotionUnit under the same PromotionGroup arises only from a legitimate newer group-local exact resolution authorized for that same nonterminal group.

---
## Invariant 46A — Promotion topology is a separate object
Dependency/stack relations connect PromotionUnit refs and are not intrinsic fields of the immutable PromotionUnit nodes; topology changes do not change node identity.

---
## Invariant 47 — PromotionGroup completeness is explicit; no implicit one-to-one default exists
A PromotionGroup is one occurrence-bound non-empty immutable closed set of canonical ConvergenceUnit refs derived from an accepted work-bearing invocation. `READY_INTERNAL` alone never manufactures a singleton PromotionGroup or PromotionUnit; a one-member ordinary invocation mechanically yields a singleton group and its repository projection.

---
## Invariant 47A — PromotionGroup identity is occurrence-bound and exact-OID-independent
`promotion_group_id` is deterministically bound to the durable logical invocation occurrence within the coordination domain, while a separate membership fingerprint hashes the canonical ConvergenceUnit member set. Distinct invocations remain distinct groups even with identical members. Exact OIDs, lifecycle, topology, policy, agent, branch, and session identity do not define occurrence identity.

---
## Invariant 47B — Work-bearing invocation state is durable while its convergence demand remains coalescible
The logical invocation identity, sealed ContributionUnit cohort, and promotion binding are durable before/with acceptance. Its wake-up signal is the ordinary coalescible convergence demand. Losing/coalescing that signal cannot merge or erase distinct logical invocation/group semantics.

---
## Invariant 47C — PromotionGroup resolution is complete and group-local
No partial group-local resolution is adopted. Every member must have one exact invocation/group-authorized state in the coherent adoption snapshot before the corresponding complete repository-local PromotionUnit mapping is adopted. Later unrelated live ConvergenceUnit movement does not refresh that mapping.

---
## Invariant 47D — PromotionGroup resolution/materialization is snapshot/CAS guarded
If any exact member attribution/generation needed for the pending originating or group-bound revision moves before adoption, the stale set is not adopted. After successful group-local adoption, unrelated later movement of the live ConvergenceUnit does not invalidate the historical/current group binding.

---
## Invariant 47E — ConvergenceUnit is indivisible at the promotion-group boundary
PromotionGroup logic never splits one ConvergenceUnit by ContributionUnit provenance. Work requiring independent promotion must be represented by distinct ConvergenceUnits upstream.

---
## Invariant 47F — PromotionGroup projection is deterministic by source repository
For every completely exact-resolved PromotionGroup `G` and every authoritative source repository `R` represented in `G`, exactly one repository-local projected member set exists: `Project(G,R) = { ExactState(C) | C ∈ G.members ∧ repository(C)=R }`. No other partition is valid.

---
## Invariant 47G — PromotionUnit source membership is repository-local
Every valid PromotionUnit contains exact ConvergenceUnit-state refs from exactly one authoritative source repository. Cross-repository provider-submission publication relation is a separate policy dimension and does not weaken this source-locality invariant.

---
## Invariant 47H — Group resolution is complete while promotion progress may be partial
A PromotionGroup is not current-resolved until its complete exact member snapshot has produced/adopted the complete repository→PromotionUnit mapping. After resolution, the resulting repository-local PromotionUnits may progress independently; cross-repository aggregate progress may therefore be `NONE_PROMOTED | PARTIALLY_PROMOTED | ALL_PROMOTED | UNKNOWN_INCONSISTENT` without creating a cross-repository PromotionUnit.

---
## Invariant 47I — Repository projection never splits to manufacture stack shape
One `(promotion_group_id, repository_id)` projection is never split into several PromotionUnits merely to create a stack. Promotion dependency/topology is a separate derived managed relation among already-distinct promotion obligations. It is established only from exact promotion-base/candidate/target lineage under ADR-050, never from common group/session provenance, repository co-membership, arrival order, branch/task names, or arbitrary/incidental ancestry.

---
## Invariant 47J — Multi-source candidate materialization uses exact base + exact sources
A repository-local PromotionUnit candidate is materialized only from one exact effective promotion base, the immutable exact PromotionUnit source set, and one versioned MaterializationContract. Internal source refs/OIDs are never rewritten to manufacture the candidate.

---
## Invariant 47K — Materialization order is canonical and runtime-order-independent
Ancestry reduction affects only execution, never PromotionUnit provenance. Remaining ancestry-maximal source heads are processed in a versioned canonical order; agent completion, arrival, branch enumeration, provider order, and process scheduling cannot select merge order.

---
## Invariant 47L — Canonical materialization uses ancestry-aware full pairwise two-head merge semantics
V1 candidate-tree semantics are an ancestry-aware canonical pairwise fold: ancestor/equal steps reuse the already-containing exact commit; only divergent steps invoke `ort`-class full two-head three-way merge behavior or an implementation proven equivalent under the exact MaterializationContract. Native multi-head octopus is not the normative semantic algorithm.

---
## Invariant 47M — Final materialization candidate has exact ancestry closure
For final candidate `C` over effective base `B`, `B` and every original exact PromotionUnit source OID are ancestors-or-equal of `C`. The final candidate tree is exactly the canonical pairwise-fold result.

---
## Invariant 47N — Final materialization candidate identity is deterministic
If ancestry already yields an existing exact commit containing `B` and every source, that commit is reused. Otherwise the final synthetic multi-parent candidate uses `B` as first parent, canonical retained source heads as remaining unique direct parents, and canonical wall-clock-independent OID-affecting metadata under the versioned MaterializationContract. Same exact inputs + same contract reproduce the same candidate OID.

---
## Invariant 47O — Materialization conflicts reuse RECONCILIATION_REQUIRED
A pairwise fold conflict requiring semantic code authoring stops materialization and emits/refreshes exact ADR-040 `RECONCILIATION_REQUIRED` evidence. `ruu` does not change merge order/backend, invoke semantic authoring, or mutate authoritative refs merely to force a clean result.

---
## Invariant 47P — Only the exact final materialization candidate is promotion-adoptable
Transient pairwise fold commits are attempt-scoped computational artifacts. A newly produced final candidate must satisfy the exact promotion/submission transition-local prerequisites before authoritative adoption; source readiness alone does not authorize the combined candidate.

---
## Invariant 48 — DIRECT_TARGET_ADVANCE is allowed only by current policy
Direct target mutation is forbidden unless the current effective policy authorizes it.

---
## Invariant 49 — DIRECT_TARGET_ADVANCE is descendant-only
The target may advance only from exact expected target `B` to exact candidate `C` where `B` is ancestor-or-equal `C`; no target history rewrite.

---
## Invariant 50 — DIRECT_TARGET_ADVANCE is one atomic exact-old CAS+FF effect
`AdvanceTargetFF(target, expected_old=B, new=C)` succeeds only when the authoritative target is still exactly `B` and the immutable ancestry relation proves `B` ancestor-or-equal `C`. Any expected-old mismatch performs no target mutation. The core never authorizes force/non-FF target semantics.

---
## Invariant 50A — DIRECT_TARGET_ADVANCE has no target worktree or pre-advanced local-target staging
After ADR-048 candidate materialization, target advancement is a pure ref operation. A local target checkout, merge-into-target step, or pre-advancement of a local target ref cannot be correctness-critical staging for the authoritative mutation.

---
## Invariant 50B — DIRECT_TARGET_ADVANCE recovery adopts from authoritative target history
After an uncertain attempt for exact candidate `C`, authoritative target `== C` or `C` ancestor-of authoritative target proves the promotion effect is realized. Authoritative target still `== expected_old` proves it is not yet realized; any other history requires stale/drift reconciliation rather than invented success.

---
## Invariant 50C — DIRECT_TARGET_ADVANCE candidate recovery anchors outlive attempts but not durable adoption
An attempt-scoped non-business recovery anchor keeps exact candidate `C` reachable while target advancement is nonterminal. It becomes cleanup-eligible only after durable adoption/recovery sufficiency; audit/history retention is independent of physical ref cleanup.

---
## Invariant 51 — Protected/provider-submission-required target cannot be bypassed
If current governance resolves to `PROVIDER_SUBMISSION`, a direct-target fallback is forbidden.

---
## Invariant 52 — PROVIDER_SUBMISSION route makes target read-only to direct Git-ref mutation by `ruu`
The target may be fetched/read/observed but not directly advanced/pushed by the Git ref engine. Provider-governed target integration may nevertheless realize the target through a separately authorized provider operation.

---
## Invariant 52A — Provider submission existence is conditional projection, not promotion identity
An exact candidate does not automatically require a provider submission. On the `PROVIDER_SUBMISSION` route, projection occurs only when current review/publication/provider/governance intent requires or explicitly authorizes it. Absence of both `REVIEW_REQUESTED` and explicit early-publication authority leaves the provider submission absent.

---
## Invariant 52B — Fully authorized provider finalization progresses mechanically
When the exact provider target-integration operation is REQUIRED, SUPPORTED, AUTHORIZED, and all current exact prerequisites hold, ordinary fixed-point reconciliation progresses that operation automatically. There is no generic ceremonial manual-Merge gate.

---
## Invariant 52C — Human finalization is a real authority only when governance says so
A human-finalizer wait exists only when current authoritative governance explicitly requires a distinct human/maintainer authority that is still unsatisfied. Historical UI convention alone cannot create such a wait.

---
## Invariant 53 — Submission refs are provider-facing representations and never alias internal refs
Every provider-submission-route logical submission uses a submission ref distinct from all internal ContributionUnit/ConvergenceUnit refs, even when both point to the same OID.

---
## Invariant 54 — Submission identity is logical while revisions are exact
`submission_id` is stable for one repository-local PromotionGroup projection toward one canonical publication destination; `promotion_unit_id`, exact head OID, and monotonic `submission_revision` may change across authorized revisions.

---
## Invariant 55 — Immutable submission heads are exact-frozen
Ordinary immutable provider-submission review binds an exact submission head until an authorized update transition.

---
## Invariant 56 — Rewriteable submission authority is explicit and narrow
Only a policy/provider-authorized submission-ref revision may perform a non-FF expected-old guarded update.

---
## Invariant 57 — Submission rewrite never rewrites internal sources
ContributionUnit/ConvergenceUnit OIDs and immutable owned promotion anchors remain stable through submission revision/restacking.

---
## Invariant 58 — Authorized restack is an exact state reprojection, not drift
A predecessor-base change may authorize a revision only through the ADR-050 exact state-transplant contract, exact result validation and ADR-049 revision binding.

---
## Invariant 59 — Unexpected submission-head movement fails closed
Movement outside an authorized revision transition enters DRIFTED/UNKNOWN recovery.

---
## Invariant 60 — Submission force-style update requires exact expected-old protection
Force-with-lease-equivalent semantics are confined to authorized submission refs.

---
## Invariant 61 — Global `--force` remains forbidden
Rewrite authority never generalizes to contribution-unit/convergence-unit/target refs.

---
## Invariant 62 — Head-bound evidence is revision-specific
Checks/reviews/readiness tied to an old exact submission head are invalidated/re-read after authorized revision.

---
## Invariant 63 — Semantic reopen and provider restack are distinct
`CHANGES_REQUESTED` enters the ADR-053 review-correction continuation path and may cause the External Control Plane to reactivate relevant existing convergence scope(s) and provision new ContributionUnits; predecessor movement/`RESTACK_REQUIRED` creates no semantic authoring authority by itself.

---
## Invariant 63A — Review-correction demand identity is exact-generation-bound and discovery-channel-independent
The same exact reviewed submission revision/head plus authoritative `CHANGES_REQUESTED` generation/fingerprint yields one durable logical ReviewCorrectionDemand whether first observed by provider hook or by any `ruu` global sweep. Rediscovery cannot create duplicate semantic obligations.

---
## Invariant 63B — Coding-session liveness and discovering caller identity are non-authoritative
The session that produced the provider submission may be closed/gone, and the session that triggers a later global sweep may be unrelated. The External Control Plane may restore the original runtime or start a new continuation session; neither runtime identity nor trigger identity changes Git/convergence/publication identity or assigns unrelated correction work.

---
## Invariant 63C — Review correction uses new ContributionUnits from the exact reviewed/group state, never the submission ref as an authoring surface
Affected existing ConvergenceUnits may be reactivated while the correction session discovers the needed scope, but every new implementation write is performed through a newly provisioned ContributionUnit/writer branch/worktree seeded from the exact group/review state authorized by the correction. A `CLOSED` ContributionUnit never reopens, the provider-facing submission ref is never a coding workspace, and unrelated later live ConvergenceUnit work is not silently absorbed.

---
## Invariant 63C1 — Nonblocking semantic findings are not provider correction demands
Review comments, suggestions, or semantic findings that are not authoritative blocking provider-governance state do not automatically create `ReviewCorrectionDemand`, reopen ConvergenceUnits, or block promotion.

---
## Invariant 63C2 — Deferred findings are external backlog, not dormant submissions
A semantic finding adjudicated `DEFER` may be projected to an external tracker/backlog object and later revalidated by the Development System. `ruu` does not preserve the finding by keeping a provider submission open, and a deferred finding does not block an otherwise authorized current promotion.

---
## Invariant 63D — Same-group semantic correction preserves logical submission identity; new logical scope does not mutate the old group
A current `ReviewCorrectionDemand` authorizes a `REVISE_EXISTING_GROUP(G, authority_ref)` work-bearing invocation. Only touched existing members may receive new group-local exact states; untouched members retain their prior bindings. The same group may therefore materialize new immutable PromotionUnits/candidates and preserves the same ADR-049 logical `submission_id` when destination is unchanged. If its current PublicationEpisode is nonterminal, the same provider submission is revised; if that episode is terminal and the nonterminal ship still needs publication, ADR-055 creates a new episode/provider submission. A genuinely new ConvergenceUnit cannot be appended to the old closed group.

---
## Invariant 63E — PromotionUnit completion does not retire a ConvergenceUnit
`PromotionUnit PROMOTED` proves only the terminal outcome of one immutable exact repository-local snapshot. A referenced ConvergenceUnit remains semantically reactivable while any relevant PromotionGroup/ship is nonterminal or any current review-correction/authoring/reconciliation demand may still require new writes.

---
## Invariant 63F — ConvergenceUnit `PROMOTED` is the semantic closure boundary
A ConvergenceUnit may become `PROMOTED` only after every relevant PromotionGroup/promotion obligation is terminally settled and no current authoring/reconciliation demand can reopen it. Once `PROMOTED`, new ContributionUnit attachment/reopen is forbidden and later semantic work requires a new ConvergenceUnit identity.

---
## Invariant 63G — `RETIRED`, GC eligibility, and physical deletion are distinct
A `PROMOTED`/terminally disposed ConvergenceUnit becomes `RETIRED` only after correctness-critical recovery/resource obligations are durably clear. Retirement may make historical internal refs `GC_ELIGIBLE`; it never itself deletes durable logical history, and v1 built-in historical internal-ref retention is `KEEP`.

---
## Invariant 63H — Partial cross-repository progress is not automatic failure or rollback authority
`PARTIALLY_PROMOTED` remains nonterminal ordinary progress while remaining repository-local paths can continue. It never by itself authorizes compensation, target reset, semantic authoring, or a new provider-submission episode.

---
## Invariant 63I — Cross-repository settlement intent is external; Git/provider effects remain observed facts
`ruu` may record/refresh one exact-generation `CrossRepositorySettlementDemand`, but only the External Control Plane/Development System chooses roll-forward versus compensation. Semantic declarations do not manufacture Git/provider success; every required forward effect is independently observed/adopted.

---
## Invariant 63J — Compensation is forward-only
No cross-repository settlement resets/force-moves an authoritative target backward. A semantic revert/fix/compatibility change is ordinary new development Git state and must traverse the normal development/convergence/promotion pipeline.

---
## Invariant 63K — Logical submission identity outlives provider publication episodes
`submission_id` remains stable for one PromotionGroup/repository/destination lineage. Revisions update one nonterminal PublicationEpisode/provider submission; a terminal provider episode is never reopened. If the same nonterminal logical submission later requires a new exact publication, a distinct new episode/ref/provider submission is created under first-publication guards.

---
## Invariant 63L — Partial promotion has no silent terminal abandonment
A group with already-realized repository effects remains nonterminal until `ALL_PROMOTED`, explicit `COMPENSATED`, or a future ADR-defined terminal settlement with equivalent semantic-authority/exact-effect guards.

---
## Invariant 64 — Stack shape is derived from exact unsatisfied promotion dependency
`ruu` never asks the caller to choose a stack. It derives current dependency from exact managed effective-base/predecessor/target facts and never from branch names, task/session names, completion order, or arbitrary/incidental ancestry alone.

---
## Invariant 65 — Restack mutates submission projection only and never accumulates projection drift
Every restack is recomputed from the immutable owned `(old_base_oid, owned_candidate_oid)` anchor onto the current new base. Previous restacked provider heads are not the semantic source for later restacks.

---
## Invariant 66 — Merge queue/finalization ownership is respected
Provider-owned finalization blocks incompatible local submission mutation until explicit release/update transition.

---
## Invariant 67 — submission/provider waits are localized fixed-point states
Checks/review/queue waiting does not stop unrelated convergence/promotion.

---
## Invariant 68 — Same-repository and cross-repository publication are distinct
Provider-submission source publication repository and target repository are explicit identities.

---
## Invariant 69 — Cross-repository provider-submission granularity is externally declared
`ruu` does not decide whether several internal units form one upstream contribution.

---
## Invariant 70 — Cross-repository logical work remains non-atomic
Higher-level work spanning repositories may be partially promoted and must expose that state.

---
## Invariant 71 — Already-promoted repositories are not silently rolled back
Cross-repo compensation/roll-forward belongs above repository-local Git mechanics.

---
## Invariant 72 — Push failure never rolls back valid local convergence
Publication failure becomes explicit pending/recovery state.

---
## Invariant 73 — provider submission creation/update is idempotent
Concurrent internal operations and recovered executions converge on persistent provider-submission identity rather than duplicating it.

---
## Invariant 74 — Direct promotion is idempotent/recoverable
Crash/timeout after a target-advancement attempt is reconciled from exact authoritative target history and the durable `expected_old/new` operation record. A later descendant of the exact candidate proves the earlier promotion effect occurred; stale journal position alone never causes blind replay.

---
## Invariant 75 — Submission rewrite/restack is idempotent/recoverable
Recovery uses logical submission identity, revision, expected-old state, and actual provider head.

---
## Invariant 76 — Internal recovery never starts rebase
Contribution unit/convergence-unit refs treat legacy/external rebase as recovery-only.

---
## Invariant 77 — Owned submission rebase/restack may be recovered
Known policy-authorized submission revision state may be resumed/finalized/aborted safely.

---
## Invariant 78 — Unknown/inconsistent ownership/topology fails closed
Destructive integration/promotion/cleanup never proceeds from ambiguous identity or owner state.

---
## Invariant 79 — Every operation is repository-local
One global sweep may span repositories, but each commit/ref/push/provider-submission operation has explicit repository identities.

---
## Invariant 80 — Independent resources remain parallel inside the single top-level executor
Fine-grained typed Git/provider claims preserve safe internal parallelism; external Development System validation scheduling is independent and top-level single-executor ownership is not a global mutex over all resources.

---
## Invariant 81 — No-commit global sweep still progresses state
Pushes, internal sync/integration, direct promotion, submission/provider updates, recovery, and cleanup are still evaluated even when the serviced demand yields no new commit.

---
## Invariant 82 — Higher-level workflow is optional for Git safety
`/go` may supply semantics/promotion declarations but cannot override or be required for core Git-safety invariants.

---
## Invariant 83 — Branch names are never parsed as semantic authority
Task-descriptive names do not define convergence identity, promotion grouping, or stack dependencies.

---
## Invariant 84 — Provider merge topology is not assumed
Provider-submission completion may result from merge/squash/rebase-style provider behavior; resulting target observation is authoritative.

---
## Invariant 85 — Provider capabilities are explicit authorization inputs
A topology/rewrite workflow proceeds only when current provider/policy capability supports it.

---
## Invariant 86 — Policy changes invalidate in-flight promotion assumptions
An in-flight direct/provider-submission/rewrite intention must revalidate policy before irreversible/ref-visible steps.

---
## Invariant 87 — Promotion target is not universally `main`
The External Control Plane binds the exact PromotionTarget repository/ref before authoring; `main` is only a common default. Policy governs how that target may be reached.

## Invariant 88 — Managed state-producing results require transition-local exact prerequisites

A newly produced managed checkpoint/internal merge/promotion/submission result becomes authoritative only when the exact predicate for that transition holds.

## Invariant 89 — Development-quality gate composition is external

`ruu` does not define or consume a universal tests/lint/typecheck/build/security validation certificate. The Development System / repository governance owns semantic-development quality policy.

## Invariant 90 — Development quality and Git/convergence validation are distinct

Tests/review/security/code-quality execution belongs outside; exact OIDs, ancestry, CAS, conflict detection, provider facts, ref effects, and recovery remain inside `ruu`.

## Invariant 91 — Development lifecycle facts are explicit and transition-specific

Development-quality success never implicitly closes a ContributionUnit, seals membership, manufactures `READY_INTERNAL`, supplies a work-bearing invocation cohort/promotion binding, or requests provider review. Those facts remain explicit under their existing owners; Ruu mechanically creates the ordinary PromotionGroup from the accepted cohort.

## Invariant 92 — ContributionUnit checkpoint mutation still requires exclusive worktree authority

While `ruu` holds the exclusive ContributionUnit worktree claim, no external producer may mutate that worktree.

## Invariant 93 — Invocation is convergence demand, not universal authority

Signaling convergence demand does not grant mutation authority, semantic ownership, grouping authority, lifecycle state, review-request intent, or policy override. Each transition revalidates the specific authority/facts it needs.

## Invariant 94 — Authored replacements gain no inherited authority

If external semantic authoring changes candidate `X` into `X'`, `X'` re-enters ordinary current-state observation and transition-local guards. No approval or diagnostic for `X` authorizes `X'` merely by provenance.

## Invariant 95 — Transition-specific evidence/facts are exact-bound

Branch names, ContributionUnit IDs, ConvergenceUnit IDs, Promotion IDs, provider submission IDs, caller identity, or session state alone cannot authorize reuse of an exact-state fact whose subject has changed.

## Invariant 96 — Exact still-current transition-specific facts may be reused

A later Git boundary may reuse a provider/policy/review/target fact only when the complete binding relevant to that evidence class remains current.

## Invariant 97 — Relevant state/context movement invalidates affected facts

Changed source OIDs, policy, target basis, submission revision/head, provider state, or other binding dimensions require re-observation/rebinding for the affected transition.

## Invariant 98 — Deterministic clean synthesis is not a generic validation wait

A new deterministic clean Git result may progress when its transition-local exact prerequisites hold. If semantic authoring is required, the existing transition-specific blocked/obligation mechanism carries the handoff.

## Invariant 99 — Development-validation compute scheduling is not a Ruu state

CPU/RAM/worker admission, flaky retries, external-service tests, and local/remote validation workers belong to the Development System.

## Invariant 100 — Validation executor technology is not Ruu domain semantics

Bazel, Docker, VMs, GitHub Actions, local shells, remote workers, or agent runtimes may implement development-quality validation without entering the Git coordination domain.

## Invariant 101 — Review-request intent is orthogonal to internal readiness

`REVIEW_NOT_REQUESTED` / `REVIEW_REQUESTED` do not replace `READY` / `NOT_READY`, completion, or promotion state.

## Invariant 102 — Draft is not a mandatory business lifecycle state

A provider draft is the adapter representation of `REVIEW_NOT_REQUESTED`, not a required stage traversed by every provider submission.

## Invariant 103 — REVIEW_REQUESTED carries a ship-ready assertion

The configured submission-author/quality gate must hold for the exact current submission revision/head before formal review is requested.

## Invariant 104 — REVIEW_NOT_REQUESTED is bounded publication intent

Policy may allow it for provider-only verification, stack exposure, or code-level early feedback without asserting readiness or requesting review.

## Invariant 105 — Material submission revision invalidates stale review-request assertion

A changed exact submission revision/head must re-establish the submission-author/ship-ready gate before returning to `REVIEW_REQUESTED`.

## Invariant 106 — Push is not a semantic-development validation boundary

Publication safety is determined by exact publication/policy/provider guards, not by a generic development-validation certificate.

## Invariant 107 — Internally produced merge states use their own Git/convergence guards

A deterministic clean state created by internal reconciliation may become authoritative when its exact topology/ancestry/claim/conflict/expected-old prerequisites hold; no generic development-validation handoff is required.

---
## Invariant 108 — V1 coordination is single-host
The current architecture guarantees one coordinated `ruu` domain per host; distributed multi-host convergence ownership is not a v1 requirement.

---
## Invariant 109 — Explicit invocations are coalescible demand signals
A trigger advances durable convergence demand; it is not a durable FIFO work item and carries no caller-local Git scope or mutation authority.

---
## Invariant 110 — At most one top-level executor is authoritative
Only the current fenced executor generation may schedule/adopt new top-level managed progression in the local coordination domain.

---
## Invariant 111 — Demand catch-up and executor release are race-safe
A concurrent new convergence demand cannot be stranded between an executor observing itself caught up and releasing ownership.

---
## Invariant 112 — Durable fencing outranks liveness observations
Physical successor establishment follows ADR-042: process death/OS-lock release permits a new owner; a live-but-hung process is not automatically superseded by heartbeat/TTL. Once a newer run generation/token is transactionally established—or the old run publishes `IDLE` and clears its token—older generations cannot authoritatively adopt new managed state.

---
## Invariant 113 — Trigger identity never carries External Control Plane mutation authority
ContributionUnit mutation access is durable External Control Plane state independent of the caller/trigger; exact-trigger transferability states are retired.

---
## Invariant 114 — Physical recovery namespaces cannot alias across fenced executor generations
Temporary mutable workspaces/anchors must be generation-specific or equivalently non-aliasing so late cleanup from an older fenced execution cannot destroy newer physical state.

---
## Invariant 115 — The top-level runtime is a current-state reconciler, not a durable step workflow
Crash recovery reconstructs current managed/external state and unresolved Operations, then reconciles again; no workflow-step position is adoption authority.

---
## Invariant 116 — Physical run ownership and durable adoption authority are separate
The process-lifetime OS exclusive lock establishes physical single-host ownership; only the current SQLite `ACTIVE` `run_generation + run_token` authorizes managed progression.

---
## Invariant 117 — `IDLE` publication closes the demand-release race
A caught-up run publishes `IDLE` and clears its token transactionally before releasing the OS lock. A caller that has recorded demand and sees `OS BUSY + IDLE` must retry ownership acquisition rather than return.

---
## Invariant 118 — Live-but-hung takeover is not automatic in v1
A live process retains the OS run lock. Correctness does not depend on heartbeat/TTL expiry; bounded subprocess/network work and localized waiting obligations provide normal liveness hardening.

---
## Invariant 118A — Host run-lock ownership is not inheritable by subprocesses
The OS run-lock descriptor/handle belongs exclusively to the top-level `ruu` executor and MUST be non-inheritable across subprocess execution boundaries. A surviving descendant MUST NOT keep the physical host fence alive after the owning executor process terminates.

---
## Invariant 119 — Recoverable logical intent is distinct from physical attempts
One immutable Operation may have multiple immutable Attempts across fenced run generations; retry/recovery does not require a new logical operation identity when the exact intent is unchanged.

---
## Invariant 120 — External-effect truth requires exact Observation
Attempt metadata never proves an external effect. The current fenced run must observe the exact Git/remote/provider/current physical state before managed adoption or terminal disposition.

---
## Invariant 121 — Adoption is atomic with the managed-state CAS it claims
An Adoption record exists only in the same SQLite transaction that successfully performs its exact managed-state transition. CAS miss means no Adoption and no progression.

---
## Invariant 122 — No CoordinationStore transaction spans external work
SQLite transactions contain only short store operations; Git/provider/network/test/long-filesystem effects occur outside them and are recovered through journal + exact observation.

---
## Invariant 123 — Correctness-critical temporary resources become disposable before cleanup
A recovery resource remains `REQUIRED` until independent durable reachability/recovery sufficiency is proven. Only after `GC_ELIGIBLE` may physical cleanup occur, and cleanup failure cannot invalidate correctness.

---
## Invariant 124 — Repository identity survives locator relocation
`repository_id` is opaque and stable. Path/remote/inode/CWD are not identity; relocation changes only the current locator binding through exact expected-state/CAS semantics.

---
## Invariant 125 — New-repository requests carry no creation authority
An agent/session/orchestrator may request repository creation, but only the External Control Plane's current RepositoryCreationPolicy can authorize local/provider creation and externally sensitive choices such as provider namespace and visibility. `ruu` never gains repository-creation authority from a trigger or request.

---
## Invariant 126 — Managed authoring never starts from an unborn/null target
A brand-new repository must be admitted with its configured target at a real exact bootstrap OID `B0` before any managed ConvergenceUnit/ContributionUnit write surface is provisioned. V1 has no managed null/unborn target state.

---
## Invariant 127 — Repository bootstrap is an admission boundary, not a partial managed state
Filesystem/provider object existence alone is insufficient. Stable repository identity/binding, exact non-null target `B0`, required bootstrap/governance, and any phase-required provider binding must be observed/adopted before `REPOSITORY_ADMITTED`; only then does ordinary ADR-015/023 managed authoring begin.

---
## Invariant 128 — Local repository identity does not require eager provider creation
Local repository creation/admission and provider repository creation/attachment are separate. A missing provider binding blocks only provider-sensitive operations that require it; it does not invent provider facts or retroactively invalidate otherwise-authorized local managed authoring.

---
## Invariant 129 — Repository names and locators are never sufficient identity for provisioning adoption
Provisioning retries may adopt an existing local/provider repository only when durable provisioning identity/binding plus exact observed facts prove it is the intended repository. Unknown path/name/provider collisions fail closed rather than silently adopting an unrelated repository.

---
## Invariant 130 — Partial repository provisioning does not authorize destructive rollback
Provisioning recovery is observe/adopt/continue-or-block. Failure after local/provider creation does not itself authorize deleting or force-resetting the created repository; destructive repository deletion requires separate explicit authority.

---
## Invariant 131 — Managed Git state remains natively interpretable
Every successful `ruu` Git mutation yields ordinary Git objects/refs/index/worktree semantics. `ruu` metadata may govern or attest the state but never redefines native Git object or ancestry meaning.

---
## Invariant 132 — Native Git operability is not governance bypass
Humans/agents/tools may technically perform ordinary Git operations without `ruu`; such external mutations remain subject to exact observation/adoption, drift, reconciliation, policy, evidence, claim/CAS, and recovery rules before later managed progression.

---
## Invariant 133 — Checkpoint intent is whole-editing-surface, not partial selection
A v1 checkpoint progression for one dirty transferable ContributionUnit has no partial/path-selected managed checkpoint semantics. The complete canonical Git-relevant editing-surface state is the checkpoint subject.

---
## Invariant 134 — Staging does not select managed checkpoint membership
The caller's current staged/unstaged partition is not managed checkpoint-selection authority. ADR-059 defines structural index/in-progress Git conditions that block canonical checkpoint construction.

---
## Invariant 135 — Canonical checkpoint trees come from the exact parent plus the complete observable surface
For a claimed dirty ContributionUnit, the checkpoint tree is reconstructed using native Git semantics from the exact authoritative parent and the complete observable Git-relevant editing surface; the caller's real index is not a selection source.

---
## Invariant 136 — Non-ignored untracked work is checkpoint work
All tracked modifications/deletions and non-ignored untracked paths belong to the whole-surface candidate. Ignored untracked paths do not; tracked paths remain governed by ordinary tracked-file Git semantics even if ignore rules later match them.

---
## Invariant 137 — Ambiguous or incompletely observable Git state is not guessed
Unmerged/in-progress structural Git state, dirty or required-but-unknown submodule state, and sparse/skip-worktree conditions that prevent complete observation block ordinary v1 checkpoint collection until exact observability/recovery is restored.

---
## Invariant 138 — Tree-equal checkpoint progression is a no-op
If the canonical candidate tree equals the exact parent tree, `ruu` does not manufacture an empty managed commit.

---
## Invariant 139 — Checkpoint candidate identity is exact Git state, attribution is separate
Checkpoint Git-state identity is `(repository_id, git_object_format, parent_oid, tree_oid)` under a versioned canonical fingerprint. ContributionUnit identity and future commit metadata are separate attribution/materialization data; no generic development-validation profile/evidence participates in candidate identity or checkpoint authorization.

---
## Invariant 140 — PromotionTarget is established before managed authoring
Every ConvergenceUnit has one canonical `(target_repository_id, target_ref)` binding before any attached ContributionUnit receives first managed write authorization.

---
## Invariant 141 — ConvergenceUnit PromotionTarget is immutable
No invocation, policy/config refresh, provider observation, review state, or runtime request may retarget an existing ConvergenceUnit. A genuinely different destination requires a distinct convergence scope / ConvergenceUnit identity.

---
## Invariant 142 — Policy answers HOW, never WHERE
`EffectivePromotionPolicy` authorizes the operations permitted toward the already-bound PromotionTarget; it never selects or substitutes `target_repository_id` / `target_ref`.

---
## Invariant 143 — Publication relation is derived from source and target identity
`SAME_REPOSITORY | CROSS_REPOSITORY` is derived from authoritative source repository identity plus the immutable PromotionTarget. Policy/provider capability may authorize or block the required relation but may not choose a different relation by changing the destination.

---
## Invariant 144 — Same-source PromotionGroup projection is target-coherent
All ConvergenceUnits projected into one repository-local PromotionUnit must share one immutable PromotionTarget. Conflicting same-source target bindings fail closed and are never silently split.

---
## Invariant 145 — Target identity is immutable while target state remains current-state data
The PromotionTarget repository/ref identity is stable, while its current OID and provider/governance facts are freshly observed/revalidated according to existing ancestry, policy-currentness, stack, and CAS rules.

---
## Invariant 146 — A transferable checkpoint offer is frozen against external mutation
Once the Development System durably transfers a ContributionUnit editing surface for checkpoint progression, no external writer may mutate that surface while the transferability handoff remains current. Semantic authoring may resume only after legitimate revocation/reacquisition of external mutation authority, subject to any already-held `ruu` claim/recovery boundary.

---
## Invariant 147 — The managed checkpoint commit is exactly the frozen canonical candidate
For a checkpoint attempt that reaches materialization, `ruu` constructs the ADR-059 whole-surface candidate under exclusive claim, revalidates the same parent/surface assumptions immediately before commit, and materializes only `K` such that `parent(K)=P` and `tree(K)=T`. Generic test/review evidence is neither required nor sufficient to relax this identity rule.

---
## Invariant 148 — Promotion is terminal only after exact route-conformant target realization proof
A provider submission becoming `MERGED` / `PROVIDER_FINALIZED` is not itself `PromotionUnit PROMOTED`. Terminal adoption requires a durable exact realization proof for the immutable PromotionTarget **and** proof that the realized effect conforms to the authoritative `target_realization_route` applicable to that effect.

---
## Invariant 149 — DIRECT native realization does not require Ruu actor attribution
For a DIRECT-compatible realization, fresh authoritative observation `O == C` or `C ancestor-of O` is sufficient native target realization proof. A legitimate user/agent direct Git fast-forward may satisfy the same obligation; `ruu` does not monopolize ordinary Git mutation merely to prove that its own process caused the ref update.

---
## Invariant 150 — Provider submission projection binds immutable C to exact submitted H
For `PROVIDER_SUBMISSION`, terminal proof includes an exact `SubmissionProjectionProof(C → H)`. Identity publication may have `C == H`; ADR-050 restack may have `C != H` and must derive `H` deterministically from the immutable owned candidate/base anchor. Semantic conflict authoring cannot be hidden inside this projection.

---
## Invariant 151 — Provider finalization binds exact H to exact R and independently observes R in target history
Provider-route terminal proof requires exact finalization of submitted revision `H` to result `R` on the expected target plus fresh Git observation proving `O == R` or `R ancestor-of O`. Provider `MERGED` alone, missing/mismatched `H → R`, or absent `R` fails closed.

---
## Invariant 152 — Native candidate ancestry cannot bypass a required provider route
When `PROVIDER_SUBMISSION` is the applicable route, `O == C` or `C ancestor-of O` proves inclusion but not route conformance. Without the exact current `C → H → R → O` provider chain, the PromotionUnit is not `PROMOTED`.

---
## Invariant 153 — Historical authorization may explain committed effects but never authorize future causal mutation
An old policy fingerprint may justify adoption of an effect proven committed while that policy/route applied. It cannot authorize a retry or action capable of newly causing/re-causing the effect. Such causal actions require freshly current policy. If commitment timing/provenance across policy drift is indeterminate, recovery fails closed.

---
## Invariant 154 — PromotionUnit PROMOTED is historical completion, not perpetual target-membership monitoring
A durably adopted route-conformant realization remains a historical fact even if later external target history is rewritten. V1 does not continuously resweep terminal PromotionUnits solely to prove ongoing inclusion; later discovered target drift is a new integrity/reconciliation fact rather than retroactive mutation of historical `PROMOTED`.

---
## Invariant 155 — Rewritten-result semantic equivalence is not a Ruu prerequisite
`ruu` does not require universal diff, patch-id, tree, or program-semantic equivalence between candidate `C`, submitted revision `H`, and provider result `R`. Such comparisons may be auxiliary diagnostics but cannot replace exact projection/finalization/target provenance.

---
## Invariant 156 — Unmanaged deletion is neutral; managed old-ref removal opens a durable disposition transition
Deleting an unmanaged branch/ref or a worktree does not by itself mean ContributionUnit `CLOSED`, ConvergenceUnit `ABANDONING`, PromotionGroup `CANCELLED`, remote-deletion intent, local-recreation intent, or semantic abandonment. Any native mutation capable of terminating/replacing the exact ref already registered as the current managed authoring binding MUST be durably captured before linearization under ADR-071/074/075 as an `AUTHORING_BINDING_TRANSITION_PREPARED` plus a normalized preparation classification; committed old-ref absence is not itself abandonment. Mere later absence never substitutes for the causal transition record.

---
## Invariant 157 — Managed authoring disposition resolves to continuation or abandonment without mutating PromotionGroup membership
A committed managed-binding transition resolves `CONTINUATION` only from sufficient positive causal rename/rebind proof, never from same OID/tree/ancestry or branch similarity. `ABANDON` independently requires durable `TERMINAL_REMOVAL_PREPARED` plus a proven committed terminal binding cessation; failure to prove continuation never implies abandonment. A resolved terminal removal establishes `ABANDON` and current `CANCEL` for still-unrealized associated ship obligations. Neither outcome edits immutable PromotionGroup membership; replacement delivery intent uses a distinct later group occurrence.

---
## Invariant 158 — Cancellation cannot erase pre-abandonment realization or unresolved causal commitment
`G = CANCELLED` may not erase any promotion effect proven realized before the authoritative resolved-abandonment point, nor may it bypass an unresolved effect causally committed before that point. Such history is recovered/adopted first and partial realization remains under ADR-055. After `CANCEL` is current, no new incompatible managed realization authority exists; provider surfaces are revoked/closed where required and later unrelated/manual external movement does not resurrect a terminal cancelled group. Genuinely unprovable cross-system ordering fails closed.

---
## Invariant 159 — Ship-membership change is cancel-old plus a new group occurrence, never mutation
If the desired ship changes from `G1={X_A,X_B}` to `{X_A}` before any `G1` effect is realized, the architecture records terminal `G1=CANCELLED` and a later ordinary work-bearing invocation creates a distinct immutable `G2={X_A}`. It never edits `G1` membership.

---
## Invariant 160 — ConvergenceUnit ABANDONING is gated by higher-level terminal disposition
A group-bound ConvergenceUnit may enter `ABANDONING` only after every relevant ship that would require its delivery has a terminal non-delivery disposition, no replacement/nonterminal group or current authoring/reconciliation demand still requires the lineage, and required semantic disposal authority is current. One cancelled group alone never forces abandonment of a member still used elsewhere.

---
## Invariant 161 — Work-bearing invocation identity is durable and distinct from convergence demand
A work-bearing Ruu invocation has one durable immutable `invocation_id`, sealed ContributionUnit handoff cohort, and promotion binding. Its wake-up signal is the ordinary coalescible convergence demand; coalescing demands never coalesces logical invocation occurrences.

---
## Invariant 162 — Ordinary work-bearing invocation creates one PromotionGroup occurrence
Every accepted `NEW_GROUP` invocation creates exactly one distinct PromotionGroup whose immutable ConvergenceUnit membership is mechanically derived from the invocation's handed-off ContributionUnits.

---
## Invariant 163 — Identical members do not imply identical PromotionGroup occurrence
Distinct logical invocation occurrences remain distinct PromotionGroups even when their canonical ConvergenceUnit member sets and membership fingerprints are identical.

---
## Invariant 164 — PromotionGroup exact resolution is group-local
A group's adopted exact member mapping is not the unqualified live current `READY_INTERNAL` state of its ConvergenceUnits. Unrelated later authoring does not refresh or invalidate that mapping.

---
## Invariant 165 — Ordinary later work never revises an older PromotionGroup
A later `NEW_GROUP` invocation cannot revise an existing PromotionGroup merely because it reuses one or more of the same ConvergenceUnits.

---
## Invariant 166 — Same-group revision requires explicit current group-bound authority
A nonterminal PromotionGroup may adopt a newer exact resolution only from a `REVISE_EXISTING_GROUP` invocation carrying current durable correction/reconciliation authority for that exact group. Untouched members retain their prior exact group-local bindings.

---
## Invariant 167 — Group-bound correction starts from the group's exact state
Correction/reconciliation authoring for an existing group is based on that group's exact prior/reviewed state, not blindly on the globally current ConvergenceUnit tip, and must not silently absorb effects belonging to later independent invocations.

---
## Invariant 168 — Terminal PromotionGroup resolution is frozen
Once a PromotionGroup reaches terminal settlement, its adopted group-local exact resolution cannot change. Later evolution of shared ConvergenceUnits is unrelated historical/future work.

---
## Invariant 169 — Parent movement restacks descendants without automatic internal rewrite
When an ancestor group's exact state changes, ADR-050 reprojects/restacks a dependent child's immutable owned effect onto the new predecessor. Only an explicit semantic reconciliation conflict may authorize a new exact child-group revision.

---
## Invariant 170 — Native Git event semantics are minimal and state-machine-derived
The only currently ratified local Git event-semantic family is disposition of the currently bound managed authoring ref. Other native Git mutations are interpreted from exact current state when a managed transition needs them; hook availability never creates business semantics by itself.

---
## Invariant 171 — Managed authoring reflog is causal evidence infrastructure, not identity
Every actively authored managed v1 ref has a native reflog before first managed write. A later missing reflog may be repaired only when the current binding is intact and no unresolved transition depends on missing historical evidence. Reflog recreation establishes a future baseline and never reconstructs deleted history.

---
## Invariant 172 — Copy/similarity never proves authoring-line continuation
A different ref pointing at the same OID/tree or sharing ancestry with the old managed ref is not continuation authority. Native copy/create followed by deletion of the managed ref abandons the old managed line; only sufficient causal rename/rebind proof or current generation-bound recovery authority may rebind the same occurrence.

---
## Invariant 173 — Exceptional authoring-binding recovery is generation-bound and Git-revalidated
When native causal evidence is irretrievably insufficient, the External Control Plane may resolve the current ambiguous occurrence only through an expected-old/binding-generation guarded `AuthoringBindingRecovery(REBIND(new_ref) | ABANDON)`. `ruu` independently validates actual Git/ref/worktree state and mutation authority; the declaration cannot manufacture Git history or allow stale metadata to resurrect abandoned work.

---
## Invariant 174 — Ancestry interpretation environment is correctness-relevant state
`refs/replace/*`, `$GIT_DIR/info/grafts`, shallow boundaries, and any equivalent mechanism capable of changing or truncating the Git ancestry/object view are part of exact ancestry observability. Ancestry-dependent progression blocks until the authoritative normalized ancestry required by the current transition is provable; intermediate creation events of those mechanisms have no separate business semantics.

---
## Invariant 175 — Managed-binding cessation/replacement requires a pre-linearization vetoable witness
Every native mutation capable of deleting, replacing, or force-overwriting a currently bound managed authoring ref must cross a native-ref adapter point before causal linearization where the actual preimage and a normalized witness can be durably recorded and the mutation can be vetoed or equivalently serialized. Purely post-commit observation is insufficient.

---
## Invariant 176 — Native-ref adapters report facts; the core derives disposition semantics
Backend-specific paths/tables/temporary rename carriers never enter core business semantics. The adapter normalizes affected ref, exact preimage, baseline match and native relation; the core combines them with managed binding generation to derive `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`. `UNKNOWN` cannot silently linearize.

---
## Invariant 177 — Backend admissibility is capability-based
A ref backend is admissible for live managed authoring only when its adapter proves pre-linearization coverage, veto/causal serialization, exact preimage capture, rename-versus-terminal evidence, durable normalized witness persistence and crash-consistent recovery for every native operation capable of ending/replacing a current managed binding. Backend name is never normative.

---
## Invariant 178 — Reflog baseline fingerprints logical evidence, not storage
`ReflogBaselineV1` is `ENTRY(anchor_entry_fingerprint) | EMPTY_PRESENT`. An entry fingerprint covers a versioned canonical representation of logical reflog entry fields and excludes ref name, physical file/table location, reflog ordinal and backend storage metadata. Missing expected history cannot be repaired retroactively during an unresolved transition.

---
## Invariant 179 — All non-disposition Git observations are exact-state rediscovery
Ordinary authoring tip movement, worktree/HEAD state, index/in-progress state, internal/submission/target/remote refs, tags/stash/notes, provider heads and ancestry-environment state require no durable local event history. Current authoritative state is re-observed when the transition needs it; optional notifications are best-effort latency/diagnostic signals only.

---
## Invariant 180 — Canonical managed ancestry excludes unnoticed mutable overlays
Managed ancestry proofs use the raw repository object graph rather than silently inheriting `refs/replace/*` or graft overlays. An implementation may disable/ignore those overlays through an exact reader or block the proof. Shallow history that could affect the answer is deepened/fetched when authorized and possible or remains ancestry-unknown.

---
## Invariant 181 — Native causal witness is not managed effect intent
An ADR-075 native-ref witness/preparation records physical causal evidence and never manufactures a managed `Operation`. The ADR-042 journal remains reserved for effects owned/caused by `ruu`; one physical Git fact may support both an existing Operation Observation and a distinct binding-generation disposition without double-counting either logical transition.

---
## Invariant 182 — Native provenance is optional and non-authoritative
A native witness may carry trusted attempt-scoped `originating_attempt_id` correlation when a managed Attempt launched the Git operation, but absence of such correlation is valid and no human/agent/IDE actor identity is required for correctness. Provenance never bypasses current policy/disposition, exact-preimage, claim/fence, expected-state or CAS checks.

---
## Invariant 183 — Binding-disposition exactly-once is generation-scoped
For one current `(repository_id, contribution_unit_id, binding_generation)`, at most one correctness-critical cessation/rebind preparation may remain unresolved and at most one committed disposition may transition out of that generation. Duplicate delivery of the same active occurrence is idempotent; a distinct competitor must wait/fail/veto until the current preparation resolves. After abort the generation remains eligible for a later distinct preparation; after committed disposition stale deliveries cannot re-dispose it.

---
## Invariant 184 — Exact-state rediscovery never manufactures causal preparation
Repeated scans may observe an existing Operation result or resolve the outcome of an already-durable native preparation when authoritative proof is sufficient. They may not synthesize `TERMINAL_REMOVAL_PREPARED`, `RENAME_CARRY_PREPARED`, or equivalent historical causal evidence from ref absence, successor similarity, OID/tree/ancestry, or final topology alone.

---
## Invariant 185 — Observation delivery is replayable; semantic adoption is exact
Native witness/outcome delivery and exact-state observations may duplicate/replay; best-effort wakeups may additionally be lost, coalesced or reordered. Correctness is enforced at authoritative adoption/disposition through immutable logical identity plus current-generation/expected-state/CAS guards, not by requiring globally exactly-once delivery or a globally unique permanent Git transaction identifier.

---
## Invariant 186 — Native Git rejection is limited to unresolved correctness-critical cessation/replacement
A native ref transaction with no cessation/replacement candidate is never rejected merely because Ruu observation persistence, wakeups, logs or telemetry are unhealthy. A transaction that may affect a current managed binding is vetoed only when authoritative safety classification or the complete required crash-durable preparation batch cannot be established before linearization.

---
## Invariant 187 — Durable PREPARED is the pre-linearization persistence boundary
For every native transaction affecting one or more current managed bindings, all required `NativeBindingPreparation` records become crash-durable as one permission batch before the transaction may linearize. Failure or bounded-retry exhaustion vetoes the entire native transaction; partial preparation persistence never authorizes partial causal coverage.

---
## Invariant 188 — Final outcome persistence and advisory delivery never become Git rollback authority
Once the required preparation is durable and Git is permitted to proceed, failure/loss/duplication of `COMMITTED | ABORTED` recording is recovered from exact state and trustworthy coverage. Wakeups, diagnostics, logs, metrics and traces are advisory and may be lost/coalesced without rejecting native Git.

---
## Invariant 189 — ManagedRefProtectionFilter is conservative acceleration, never managed authority
A trustworthy negative filter answer may prove that a cessation candidate needs no managed-state lookup. Positive/stale entries are safe false positives. Filter absence/corruption/untrusted generation is never interpreted as an empty filter; it disables negative acceleration and falls back to authoritative managed binding classification.

---
## Invariant 190 — Filter degradation is distinct from observation coverage loss
If the pre-linearization observer still runs but its protection filter is unavailable/untrusted, observation coverage remains active and the observer classifies cessation candidates through authoritative state. Only an actual bypass/loss of the required observer path closes the coverage epoch. If both negative filter proof and authoritative classification are unavailable for a cessation candidate, the transaction fails closed.

---
## Invariant 191 — Managed binding admission is serialized with native ref mutation
A candidate ref becomes a current managed binding only while a conforming `RefAdmissionBarrier` verifies its exact preimage under native-ref exclusion and keeps that exclusion held through authoritative binding commit. Releasing the barrier before binding publication is forbidden. Candidate branch/worktree creation alone has no managed-binding semantics.

---
## Invariant 192 — Initial authoring handoff requires exact topology and exclusive pre-handoff authority
Before first managed write, the provisioning path retains exclusive authority over the candidate worktree, revalidates repository/worktree identity, registered path, symbolic HEAD/ref relationship and exact OID, publishes the protected current binding, releases the ref barrier, then transfers authoring authority to the producer. `git worktree lock` may be defense-in-depth but is not the correctness fence for HEAD/topology.

---
## Invariant 193 — Observation authority is source-domain scoped
Local Git, remote Git and provider workflow facts are distinct authority domains. A local native observer is authoritative only for the local mutation surface on which coverage is established; it never proves a remote/provider mutation merely because a local cache later changes.

---
## Invariant 194 — Remote-tracking refs are caches, not authoritative remote state
`refs/remotes/*` and equivalent tracking state record what the local clone last observed. A transition requiring current remote Git truth re-observes an admitted authoritative remote endpoint/ref surface; a local remote-tracking update is only local cache movement.

---
## Invariant 195 — Remote Git is independently usable without a provider
A conforming remote Git endpoint may support exact observation, publication and recovery without any provider API/webhook. If a transition requires a provider-owned semantic operation and no provider capability exists, only that transition is unsupported/blocked; Ruu never emulates provider workflow semantics with ordinary Git refs.

---
## Invariant 196 — Owned remote mutations retain exact-old/current-state recovery
Remote ref mutations owned by Ruu use exact expected-old/currentness guards or an equivalent admitted CAS semantic and are followed/recovered through authoritative remote re-observation. Lost acknowledgements produce an unknown Attempt outcome, not blind replay or inferred success.

---
## Invariant 197 — Webhook delivery is not completeness authority
Webhook/event deliveries may be lost, duplicated, redelivered or reordered. Their arrival may wake reconciliation and authenticated payloads may add positive provider-scoped evidence when exact semantics are demonstrated, but absence of delivery never proves absence of an event and generic webhook delivery is never a required complete event log.

---
## Invariant 198 — Observation occurrence identity is not semantic transition identity
Provider delivery/event occurrence IDs, local hook occurrence IDs and transport attempt IDs may support authentication/deduplication/provenance but never automatically become managed Operation/Promotion/Adoption identity. Duplicate or delayed evidence cannot re-run an already-adopted semantic transition.

---
## Invariant 199 — Cross-source causality requires exact source-owned identities, not wall-clock order
Local Git timestamps, remote observation time, provider webhook/API timestamps and policy observation times are diagnostic/freshness metadata, not generic cross-system causal ordering. When a transition genuinely depends on chronology, documented source revisions/operation identities/exact before-after bindings must establish it or the transition fails closed.

---
## Invariant 200 — Remote publication artifacts do not control local managed-binding disposition
Remote branch/submission deletion, remote-tracking deletion, provider branch rename-like topology or equivalent remote drift never directly yields local managed-authoring `CONTINUATION | ABANDON`. That causal classifier remains scoped to the currently bound local managed authoring ref.

---
## Invariant 201 — Historical provider realization and current target topology are separate facts
A positively established provider finalization fact may remain historically true after later remote/target drift. Current target containment/state is independently re-observed when required; later drift does not erase an already-valid historical realization fact or reopen terminal `PROMOTED` semantics.

---
## Invariant 202 — Live lock order is native Git before CoordinationStore
Any protocol that needs both a live native ref exclusion and a live CoordinationStore write uses `Git/native ref lock → CoordinationStore`. No conforming path holds a live CoordinationStore transaction/mutex/write lock while waiting for the corresponding Git/native ref lock. Durable claims that do not keep a live lock are unaffected.

---
## Invariant 203 — Dirty authoring state is not an exact dependency version
A dependency may identify only an exact native commit. Ruu never consumes or implicitly commits another producer's mutable worktree/index/untracked/ignored state.

---
## Invariant 204 — ContributionUnit is the sole v1 authoring-occurrence identity
Canonical authoring source identity is `(repository_id, contribution_unit_id)`. Session, process, task, branch, worktree, and a separate `work_occurrence_id` are not competing domain identities.

---
## Invariant 205 — AuthoringDependency requires semantic selection plus exact Git proof
The Development System explicitly selects source identity and consumed OID; Ruu independently proves the exact object and source lineage. Ancestry, recency, names, or selection alone never manufacture the relation.

---
## Invariant 206 — Native commit creation is not checkpoint or completion
An ordinary managed-ref commit creates an exact Git version. Only exact frozen-handoff adoption makes a clean tip a managed checkpoint; neither event implies lifecycle closure or promotion readiness.

---
## Invariant 207 — Durable dependency implies durable object reachability
Before AuthoringDependency adoption, a REQUIRED Ruu recovery anchor must retain the consumed commit. No adopted dependency may depend on reflog grace or an ordinary moving source ref for object survival.

---
## Invariant 208 — Consumed exact OID never follows the source
The immutable consumed OID remains distinct from the source's later current exact state and from any stable source promotion projection.

---
## Invariant 209 — Raw dependency blocks realization, not independent progression
A raw dependency permits otherwise legal authoring, handoff, checkpointing, convergence, group resolution, and candidate materialization. It blocks only realization that would publish an effect without established authority; unrelated global obligations continue.

---
## Invariant 210 — Current target containment can satisfy without a fake parent
Canonical authoritative target containment of the consumed OID may terminally satisfy the dependency. Ruu creates no synthetic PromotionGroup merely to represent that fact.

---
## Invariant 211 — Promotion compression needs source-handoff attribution
Mapping to `(PromotionGroup, source repository)` requires the same source ContributionUnit's qualifying causally later handoff and exact group-local attribution plus canonical ancestry. Candidate ancestry alone never chooses a parent.

---
## Invariant 212 — Source advancement never mutates active consumer authoring
Later source movement does not change the selected consumed OID or rewrite a producer-owned consumer worktree. Reprojection occurs only at an authorized handoff/promotion boundary.

---
## Invariant 213 — Same-group dependency creates no stack edge
A dependency internal to one immutable PromotionGroup/repository projection is handled by ADR-047/048 materialization and never splits that projection or changes closed membership.

---
## Invariant 214 — Abandonment never transfers publication authority
If the source loses its realization path before valid target satisfaction, the consumer remains blocked with exact reconciliation work. Source ancestry in the consumer is not authority to publish it.

---
## Invariant 215 — Clean native tip checkpoint adoption requires exact frozen handoff
An ordinary native commit remains only exact Git state until a frozen work-bearing handoff, current binding/claim/topology, canonical ancestry, run fence, and managed-state CAS adopt the clean current tip as the authoritative checkpoint without creating another commit.

---
## Invariant 215A — Multi-predecessor provider topology is not invented
The record model may retain a finite dependency set, but more than one independently unsatisfied external predecessor remains locally blocked until a separate ratified representation exists or existing semantics reduce the set.

---
## Invariant 216 — Dependency adoption and reconciliation are idempotent
Crash, retry, duplicate observation, concurrent compression, and repeated sweeps preserve one immutable dependency identity/OID and at most one authoritative source projection under current run and row-version fences.

# 27. Architectural implications

## 27.1 Repository/bootstrap and contribution-unit provisioners — outside the convergence engine

For an existing admitted repository, the contribution-unit provisioner owns pre-edit lazy establishment of convergence-unit/contribution-unit/worktree topology, adoption of any explicitly selected exact AuthoringDependencies and their initial bases/anchors, the native reflog required for the managed authoring ref, repository-common observer/protection-filter readiness, the exact `RefAdmissionBarrier`, and the initial external mutation-authority handoff. Candidate worktree/ref creation precedes managed admission; the candidate is not producer-writable until exact binding publication and handoff complete.

For a brand-new repository, ADR-056 places a Repository Provisioner one step earlier: it executes current External Control Plane creation authority, establishes/adopts the exact `B0` bootstrap target and `RepositoryBootstrapContract`, and only then hands the `REPOSITORY_ADMITTED` repository to ordinary ADR-015/023 contribution-unit provisioning. Provider attachment may be later/lazy.

These provisioners run because development needs a safe managed editing surface or repository, not because Git convergence was requested. The convergence engine does not create either surface as a convergence side effect. Under ADR-078 the installed Ruu product may supply the harness integration/provisioner implementation that performs this work automatically before first managed write.

## 27.2 CoordinationStore

The concrete v1 backend is host-local SQLite under ADR-042. It persists the authoritative managed coordination state, demand/run fence, stable repository identities and current locator bindings, AuthoringDependency definitions/lifecycle/anchor references, domain entities/obligations/claims, exact policy/submission/provider logical records, evidence references, correctness-critical native binding preparations, and the append-only recoverable-effect journal. ADR-079's repository-common `ManagedRefProtectionFilter` is only conservative acceleration and never a second authoritative binding database.

At minimum it semantically separates:

```text
current mutable managed state with exact row/OID/fingerprint CAS
from
immutable Operation / Attempt / Observation / Adoption history
```

It does not replace Git/remotes/provider as authority for the external facts those systems own.

## 27.3 Repository policy resolver

Resolves/revalidates the effective repo-local promotion policy and provider capabilities.

It must expose a state fingerprint/version suitable for exact authorization checks.

## 27.4 Worktree manager — provisioning side

Provides isolated ContributionUnit worktree provisioning/removal for the External Control Plane. These editing-artifact lifecycle actions are outside the convergence engine's semantics but may be implemented by a Ruu-supplied harness/provisioning component.

## 27.5 Convergence-demand admission / mutation-access boundary

Authenticates explicit `ruu` invocation principals, admits/coalesces convergence demand, and consumes the durable external ContributionUnit mutation-access contract. Trigger admission and mutation authority remain distinct; this boundary does not infer ContributionUnit identity or producer liveness.

## 27.6 Contribution-unit authority subsystem — outside the convergence engine

Owns external work-producer/runtime mutation rights, stop/crash/resume semantics, and the mechanism that makes a repository-local ContributionUnit editing surface safely transferable to the `ruu` coordination domain. The convergence engine consumes this contract and does not infer it; a Ruu-supplied harness integration may implement the external runtime side under ADR-078.

## 27.7 Convergence claimant

Coordinates fine-grained claims for:

```text
contribution-unit worktree
convergence-unit ref
promotion unit
submission ref/revision
target direct-promotion op
remote publication target
submission/provider operation identity
integration/projection workspace
cleanup
```

## 27.8 Git state validator

Reads authoritative Git graph/worktree/index/ref facts and classifies exact ancestry/conflict state.

## 27.9 Commit engine

Commits only the exact ContributionUnit checkpoint candidate selected by the checkpoint candidate-membership contract, under current mutation authority/claim/CAS and ADR-059 exact-state guards.

An LLM may generate commit messages but receives no ref-mutation authority.

The commit engine never runs repository tests/lint/build/review. It commits only when the ADR-059 candidate and current mutation-authority/claim predicate is satisfied; development validation is not a Git-side prerequisite.

## 27.10 Internal convergence workspace manager

Provides isolated merge/conflict state for `ConvergenceBase→convergence-unit` and other shared internal operations without hijacking contribution-unit checkouts.

## 27.11 ConvergenceEngine / global reconciler

Owns the top-level current-state reconciliation loop. Every sweep re-enumerates the complete known nonterminal managed-obligation universe, refreshes the exact state needed by those obligations, delegates classification to specialized reconcilers, schedules non-conflicting progressable operations, and repeats until the current global fixed point.

The internal Git graph remains:

```text
ConvergenceBase → convergence unit
convergence unit → contribution unit
contribution unit → convergence unit
```

using append-only/no-rebase internal semantics, but this graph is one family of obligations inside the global reconciler rather than the complete orchestration model.

The ConvergenceEngine does not persist workflow-step position. Crash recovery is current-state reconstruction + operation recovery + another reconciliation pass.

## 27.12 ContributionUnit lifecycle / exact-state continuity consumer

Consumes externally authoritative `OPEN | CLOSED`, exact latest managed checkpoint identity, and current editing-surface availability. It keeps checkpoint/integration orthogonal to lifecycle and does not own branch/worktree deletion or semantic abandonment.

When an unresolved exact checkpoint remains recoverable, it can continue convergence without the producer worktree; when the required exact state is unrecoverable it records/localizes recovery-data-loss state.

## 27.13 Convergence-unit lifecycle engine

Determines exact `READY_INTERNAL(OID)`, promotion binding, semantic reopen invalidation, and eventual retirement.

It does not interpret product-feature semantics.

## 27.14 Logical-invocation / PromotionGroup resolver / PromotionUnit registry

Consumes durable accepted work-bearing logical invocations and their already-authoritative ContributionUnit→ConvergenceUnit bindings. For `NEW_GROUP`, it derives one immutable closed ConvergenceUnit member set and creates one occurrence-bound PromotionGroup. For `REVISE_EXISTING_GROUP`, it verifies current explicit group-bound continuation authority and that all touched ConvergenceUnits are existing members.

The resolver adopts exact **group-local** member states attributable to the originating invocation or authorized same-group revision. Resolution is complete and snapshot/CAS guarded, but once adopted it is not invalidated merely because the live ConvergenceUnit later reopens or advances for another ordinary invocation. A terminal group is resolution-frozen.

When a complete group-local exact mapping is adopted, it canonicalizes the repository-local `Set<ExactConvergenceStateRef>` projections, verifies that every same-source partition has one coherent immutable PromotionTarget, derives/reuses one ADR-045 content-addressed repository-local `promotion_unit_id` for each represented repository, and records/adopts the complete repository→PromotionUnit mapping. A legitimate later revision of the **same** group may produce newer PromotionUnits for changed projections; unrelated ConvergenceUnit movement cannot. Conflicting immutable targets inside one same-source partition yield `TARGET_INCOHERENT_PROMOTION_GROUP`; the resolver fails closed and does not split the group by target.

There is no implicit singleton/default mapping and no mid-sweep semantic callback to choose group membership. Same PromotionGroup + same repository is not split into several PromotionUnits. Promotion topology is a separate relationship among PromotionUnit refs/obligations and is never synthesized by repository projection. Target is not a group/unit definition field because it is already immutable on each ConvergenceUnit and must be coherent across the projection; mode/policy inputs remain outside the immutable PromotionUnit content address.

## 27.14A AuthoringDependency reconciler

Consumes explicit Development System source/version selections and exact local Git facts. Supported-harness provisioning submits an authorized internal provisioning demand to the existing fenced ConvergenceEngine and waits before first consumer write; this creates no work-bearing checkpoint or PromotionGroup. TX-A durably linearizes the selection and expected source generation, then the reconciler adopts an immutable repository-local dependency only after an operation-owned REQUIRED anchor retains the consumed commit and TX-B revalidates source row/binding generation/continuity/disposition. It then re-evaluates raw dependencies against current target containment, same-group source checkpoints, qualifying source handoffs/group-local exact state, source disposition, and exact canonical ancestry.

Resolution may produce `SATISFIED_BY_TARGET`, `INTERNAL_TO_SAME_GROUP`, or a stable `(PromotionGroup, source repository)` predecessor projection. It retains the consumed OID separately from the parent's current exact state and supplies ADR-050 with the immutable consumer owned anchor. Ambiguity, lost object reachability, source abandonment without realization, and unsupported multi-predecessor publication remain localized blockers.

## 27.15 Promotion candidate materializer

Materializes/rebuilds the exact repository-local candidate/head from one exact repository-local PromotionUnit and one exact effective promotion base.

ADR-047 closes logical group→repository-local PromotionUnit projection. ADR-048 closes repository-local multi-source candidate/head materialization with:

```text
exact PromotionUnit sources
+ exact effective base derived for the immutable PromotionTarget
→ ancestry reduction
→ canonical source order
→ ancestry-aware canonical pairwise full two-head merge fold
→ reuse exact existing candidate when ancestry already suffices, otherwise one deterministic synthetic multi-parent final candidate
→ adopt/progress only under the exact transition-local Git/managed/policy/provider prerequisites of the next transition
```

Materialization never rewrites internal ConvergenceUnit refs. Native multi-head octopus does not define the semantics. Conflicts requiring semantic authoring emit/refresh ADR-040 `RECONCILIATION_REQUIRED`. Candidate computation is isolated from producer worktrees and participates in ADR-042 Operation→Attempt→Observation→Adoption recovery.

## 27.16 Direct promotion engine

For `target_realization_route=DIRECT_TARGET_ADVANCE`, consumes an already materialized ADR-048 candidate for the immutable PromotionTarget and requires every AuthoringDependency/promotion predecessor to be target-satisfied or internal to the same group. When the DIRECT_TARGET_ADVANCE transition-local prerequisites are satisfied, it performs the ADR-052 semantic operation `AdvanceTargetFF(PromotionTarget.ref, expected_old, new)`: one atomic exact-old compare-and-swap whose only successful effect is descendant-only advancement of that already-bound target. It owns no target worktree/merge staging, keeps an attempt-scoped candidate recovery anchor while nonterminal, and adopts success only from authoritative target observation/history.

## 27.17 Submission revision engine

For PROVIDER_SUBMISSION route, owns logical submission identity and exact current revision/head.

It distinguishes immutable submission from policy-authorized rewriteable/restackable submission refs.

## 27.18 Push engine

Publishes ref classes according to their authority:

```text
contribution-unit/convergence-unit → FF/expected-state only
submission immutable    → FF/expected-state only
submission rewriteable  → exact expected-old non-FF only when explicitly authorized
target DIRECT            → ADR-052 exact-old CAS+FF contract only
target on PROVIDER_SUBMISSION route → never directly pushed
```

## 27.19 Submission / provider governance adapter

Creates/updates/observes PRs and provider states, including:

```text
checks
reviews
UPDATE_REQUIRED
CHANGES_REQUESTED
stack/restack state
merge queue
merged/closed state
provider head movement
capabilities
```

It never bypasses target governance.

## 27.20 Dependency and stack coordinator

Consumes already-adopted semantic AuthoringDependencies and already-authoritative promotion relations, then mechanically reconciles them with exact source handoffs, predecessor state, target state, and provider capabilities. It computes which resolved single-predecessor submission revisions require stacking/restacking after lower-layer/target/provider movement.

It never invents semantic dependency from ancestry and never accepts caller-authored provider stack layout. Raw or multi-unsatisfied dependencies remain localized realization waits.

## 27.21 Recovery engine / effect journal consumer

Consumes unresolved immutable Operations and their Attempts, re-observes exact current Git/remote/provider/recovery-resource state, appends current fenced Observations, and either performs exact CAS Adoption, records a non-adopting terminal disposition, or returns the obligation to ordinary reconciliation.

It reconstructs at least:

```text
commits/checkpoints, AuthoringDependency adoption/compression, and recovery refs/anchors
internal merges/conflicts
pushes
direct target promotion
promotion materialization
submission revision/restack
submission/provider operations
policy changes in flight
```

It never resumes from in-process workflow position and never treats "attempted" metadata as proof that an external effect happened.

Cleanup after a recovery resource has become `GC_ELIGIBLE` is best-effort and is not itself a recoverable business Operation.

## 27.22 Higher-level semantic control boundary

Human/Turnlock/`/go`/other systems may invoke `ruu` and may decide semantic intent outside it, including:

```text
what work means
which exact source ContributionUnit/version a consumer semantically requires
which ContributionUnits form a work-bearing invocation cohort
semantic completion/readiness requirements
```

They do not own or resume the internal `ruu` reconciliation control flow and cannot override Git/policy safety.

## 27.23 Provider capability adapter

Implements ADR-051 by mapping provider-specific APIs/mechanisms onto the core's versioned semantic-operation vocabulary. The adapter observes an exact operation context and emits normalized immutable capability/current-fact observations such as:

```text
ObserveCapability(semantic_operation, exact_context)
→ SUPPORTED | UNSUPPORTED | UNKNOWN_INCONSISTENT
→ provider mechanism + applicability constraints/current facts/evidence effects
```

It does not decide publication topology, semantic dependency, or policy authorization. The core determines the required transition; provider/context support and `EffectivePromotionPolicy` authorization are independent conjunctive guards. Provider-native execution is acceptable only when the exact observed result satisfies the same normative core contract.

## 27.24 Transition-local prerequisite evaluator

For every candidate transition, evaluates only the exact Git/managed/policy/provider facts that transition requires. It does not own a generic development-validation gateway or infer development stage.

Examples include lifecycle/membership facts, exact OIDs/ancestry, mutation authority, promotion policy/capability, review-request intent, provider checks/reviews/queue state, and expected-old/CAS guards.

## 27.25 Transition-specific external-fact reference store

Persists only the durable references/bindings needed by the transition-specific external facts already defined by the architecture (for example review-request intent, provider observations, policy snapshots, settlement generations, and reconciliation descriptors). There is no generic development-validation evidence/demand store.

## 27.26 Development-verification executor/scheduler — intentionally absent

ADR-057/060 keep repository tests, validation workers, flaky-test policy, and semantic review orchestration outside the core model.

## 27.27 Review-request publication controller

Carries provider-facing publication intent:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

and ensures `REVIEW_REQUESTED` cannot be applied to an exact submission revision unless the configured submission-author/ship-ready gate holds.

The provider adapter maps that intent to provider-specific draft/ready semantics.

# 28. V1 Git reconciliation and policy-driven promotion rules

`ruu` has two authority domains:

```text
INTERNAL CONVERGENCE DOMAIN
ConvergenceBase → convergence unit ↔ contribution unit

PROMOTION DOMAIN
promotion unit → target directly
OR
promotion unit → submission ref(s) → submission/provider → target
```

The repository promotion policy selects the authorized promotion path.

## 28.1 Internal reconciliation matrix

For exact current tips:

```text
ConvergenceBase → convergence unit

equal
→ no-op

convergence-unit tip ancestor target tip
→ FF convergence unit to target

neither ancestor
→ merge target into convergence unit

target tip ancestor convergence-unit tip
→ no downward sync needed
```

```text
convergence unit → contribution unit

equal
→ no-op

contribution unit tip ancestor convergence-unit tip
→ FF contribution unit

neither ancestor
→ merge convergence unit into contribution unit

convergence-unit tip ancestor contribution unit tip
→ no downward sync needed
```

```text
contribution unit → convergence unit

convergence-unit tip ancestor contribution unit tip
→ FF convergence unit

otherwise
→ synchronize contribution unit first
→ revalidate
→ retry
```

## 28.2 Internal history strategy

For:

```text
CONTRIBUTION_UNIT_REF
CONVERGENCE_UNIT_REF
```

allowed mutations are:

```text
NOOP
FF_EXISTING_DESCENDANT
FF_NEW_MERGE_DESCENDANT
guarded delete on retirement
```

Forbidden:

```text
rebase
amend
backward reset
non-fast-forward update
history rewrite
force-push
force-with-lease push
```

## 28.3 DIRECT_TARGET_ADVANCE realization matrix

Preconditions:

```text
effective target realization route = DIRECT_TARGET_ADVANCE
promotion unit exact and ready
zero raw or resolved-but-target-unsatisfied external AuthoringDependencies
zero unsatisfied promotion predecessors
target repository/ref exact and current
target mutation allowed by current policy
promotion candidate exact and all transition-local prerequisites satisfied
target promotion claim held
```

Allowed:

```text
expected authoritative target T
candidate C

T == C
→ already promoted/no-op

T ancestor C
→ AdvanceTargetFF(target, expected_old=T, new=C)
→ success only as atomic exact-old CAS + FF

otherwise
→ stale/not directly promotable
→ refresh/reconcile/rebuild/revalidate
→ retry only with a newly current expected target/candidate contract
```

Forbidden:

```text
merge blindly into stale target
non-fast-forward target update
target rebase/rewrite
target force push
fallback to direct because provider submission failed
```

## 28.4 Provider-submission promotion matrix

Preconditions:

```text
effective target_realization_route = PROVIDER_SUBMISSION
promotion unit exact and ready
target read-only to Ruu
publication relation valid
provider capabilities valid
submission operation claim held
```

Then, only when current publication intent/need authorizes projection:

```text
materialize exact submission representation
→ publish exact current revision
→ create/update/observe persistent provider submission identity
→ observe provider checks/reviews/queue/governance
→ derive the exact provider target-integration operation required by current state
→ require REQUIRED ∩ SUPPORTED ∩ AUTHORIZED + exact current prerequisites
→ execute/request provider finalization automatically when machine-authorized
→ observe resulting authoritative target
→ adopt only from exact provider + target evidence
```

If neither `REVIEW_REQUESTED` nor explicit current authority/need for exceptional early publication exists, the provider submission remains absent; `ruu` does not manufacture a draft provider object. `ruu` never directly mutates the target ref in PROVIDER_SUBMISSION route. A distinct human finalizer causes a wait only when authoritative governance explicitly requires that authority.

## 28.5 Immutable submission history

For an immutable submission ref:

```text
EQUAL remote/local
→ no push

LOCAL_AHEAD + expected remote
→ ordinary FF push

provider/head update required
→ create explicit submission-update workflow
→ only descendant/FF submission update is allowed

unexpected non-FF movement
→ DRIFTED/UNKNOWN
```

The exact provider submission head remains frozen during ordinary review/queue ownership.

## 28.6 Rewriteable/restackable submission history

A submission ref may be non-fast-forward rewritten only when:

```text
current policy/provider capabilities authorize the exact revision operation
current logical submission identity is known
current exact revision/head is known
expected-old local/remote/provider head is revalidated
rewrite claim is held
underlying exact internal owned state remains unchanged/valid
for RESTACK: current exact unsatisfied dependency and new predecessor/base are known
```

Allowed transition:

```text
submission S
revision r @ H

authorized revise/restack
→ derive exact H2 under current candidate/update or ADR-050 RestackContract
→ mechanically validate exact projection/dependency + require exact H2 transition-local publication prerequisites
→ ADR-049 expected-old guarded submission-ref/provider update
→ submission revision r+1 @ H2
→ local/remote/provider head verified
→ re-read head-bound checks/reviews
```

This rewrite authority never propagates to internal refs or target refs.

## 28.7 Derived promotion dependency and stacked provider representation

For already-distinct repository-local promotion obligations, a previously adopted AuthoringDependency may resolve through exact source-handoff attribution, or another already-authoritative promotion relation may establish:

```text
P1
P2 depends_on=P1
P3 depends_on=P2
```

while those predecessor effects are not yet realized in the authoritative target, the provider-facing representation may naturally be:

```text
target
  ↑
S1 / PR1
  ↑
S2 / PR2
  ↑
S3 / PR3
```

Rules:

```text
semantic source/version selection is explicit before authoring and never inferred from ancestry
after adoption, dependency resolution/topology derives from the source's exact pre-sync handed-off checkpoint, equal immutable PromotionTarget, group-local incorporation, and exact effective-base/predecessor/target facts
caller/user/agent does not request stack shape
predecessor realized in target → dependency SATISFIED_BY_TARGET / ordinary child promotion
predecessor revision may make upper submission RESTACK_REQUIRED
restack authority is submission-layer only
provider capability/policy must support representing the dependency or child waits
merge-queue/finalization state may temporarily freeze restack
```

## 28.8 Cross-repository publication

For:

```text
publication_relation = CROSS_REPOSITORY
```

explicit identities are:

```text
authoritative source repository
source publication repository/ref
immutable PromotionTarget(target_repository_id, target_ref)
derived SAME_REPOSITORY | CROSS_REPOSITORY relation
provider submission identity
```

`ruu` may publish only through the configured/authorized source surface and may not infer permissions against the immutable target. Policy/provider facts authorize or block the required relation; they do not select another target.

Unsupported cross-repository stack topology blocks explicitly.

## 28.9 Promotion-unit source composition

A repository-local PromotionUnit may reference one or more exact convergence-unit inputs. ADR-048 fixes exact candidate materialization: exact effective base + ancestry-maximal reduction + canonical ancestry-aware pairwise full two-head merge semantics, with exact-state reuse when possible and otherwise one deterministic synthetic multi-parent final candidate.

Candidate computation is isolated from ContributionUnit producer worktrees, conflict-detecting, recoverable/idempotent, exact-state-bound, and contains no hidden semantic grouping. Semantic conflicts route to ADR-040 `RECONCILIATION_REQUIRED`; the exact final candidate may be adopted only when its transition-local exact prerequisites hold.

## 28.10 Repository promotion policy is authoritatively composed, target-bound, and current-state-bound

The immutable PromotionTarget comes from ConvergenceUnit topology established before authoring. Before any direct target update, submission rewrite, provider submission create/update, or provider topology mutation:

```text
refresh/revalidate authoritative policy inputs
→ compose constraints
→ apply built-in rules only to underdetermined dimensions
→ require CURRENT(EffectivePromotionPolicy fingerprint)
```

No generic precedence or runtime override exists. Explicit incompatible provider/org/trusted-repo constraints produce `CONTRADICTORY` and block the affected promotion. Policy contradiction or provider limitation never causes implicit target substitution/retargeting.

The trusted repository-committed policy is read from the exact authoritative target baseline that governs the promotion. Candidate-only policy changes cannot govern that same candidate.

If policy sources/facts changed after earlier planning:

```text
old promotion authorization becomes stale
→ do not execute
→ recompute under new authoritative state
```

The system never “tries the old operation and sees whether the server rejects it”, never silently normalizes a contradiction, and never accepts a caller/local-config bypass.

## 28.11 Route-conformant provider target-integration result

For `PROVIDER_SUBMISSION`, internal candidate projection, provider finalization, target realization, and terminal adoption are separate facts. A provider `MERGED` / `FINALIZED` observation is never by itself sufficient to adopt `PromotionUnit PROMOTED`, and candidate ancestry in target cannot bypass the required provider route.

ADR-066 defines the terminal provider chain:

```text
immutable PromotionCandidate C
→ exact SubmissionProjectionProof(C → H)
→ exact ProviderFinalizationObservation(H → R on immutable PromotionTarget T)
→ fresh authoritative Git observation O with O == R or R ancestor-of O
→ route-conformant provider realization proven
```

`H` is the exact provider-facing submitted revision. It may equal `C` for identity projection or differ after ADR-050 deterministic restack. The provider is authoritative only for exact `H → R`; it is not asked to know internal `C`. `ruu` independently proves `C → H` and target inclusion of `R`.

The resulting target history may use merge commit, squash, rebase-style merge, merge queue/batch result, or another authorized provider topology. Universal patch/tree/program-semantic equivalence across `C`, `H`, and `R` is not required.

A fresh observation that `C` itself is present in target is still useful Git evidence, but on a required provider route it is not terminal without the exact provider finalization chain.

## 28.12 Transition-local prerequisite rule

For every locally controlled managed transition:

```text
observe the exact current Git/managed/provider state
+ consume only the narrow externally authoritative fact(s) that transition genuinely requires
+ require current claims/CAS/policy/capability guards
→ transition may proceed when its exact predicate is satisfied
```

There is no generic development-validation evidence state. Development System test/review/security execution may influence when externally owned lifecycle/governance facts are established, but `ruu` neither requests a universal certificate nor holds deterministic Git candidates in a generic validation wait.

## 28.13 Provider-submission review-request publication rule

provider submission publication intent is:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

Nominal promotion requests review only after the exact current revision satisfies the configured submission-author/ship-ready gate.

Provider draft/ready terminology is adapter-level representation only.

# 29. Branch/ref naming is descriptive; identity is separate

Concrete naming is intentionally not a correctness primitive.

A convergence-unit branch may be named by a human/agent according to the work:

```text
fix-login-race
refactor-parser
oauth-callback
turnlock-lease-recovery
```

Contribution unit/submission refs may use any repository-approved naming convention.

The architecture requires separate stable identities:

```text
convergence_unit_id
contribution_unit_id
promotion_unit_id
submission_id
```

and stores the actual ref name explicitly.

Therefore:

```text
branch renamed
→ identity may remain the same after authoritative update

same text in two repositories
→ distinct identities

descriptive branch text
→ never parsed to infer product semantics
→ never parsed to infer promotion grouping
→ never parsed to infer stack dependency
```

A naming convention may still improve observability, but correctness depends on durable identity + exact Git facts.

# 30. Open design questions

The companion `OPEN-DESIGN-BACKLOG.md` tracks these questions plus the verification/review topics introduced by ADR-029..ADR-032. ADR-033/ADR-034/ADR-035 retire the former producer-liveness/actor-identity/runtime-handoff questions. ADR-036 fixes global sweep scope over all known nonterminal managed obligations across every lifecycle layer; repository activity indexes are non-authoritative acceleration state only. ADR-037 closes ConvergenceUnit creation/membership authority, removes a separate ContributionUnit integration-release signal, and defines sealed mechanical `READY_INTERNAL`. ADR-038 reduces ContributionUnit lifecycle to `OPEN | CLOSED`, removes abandonment/cleanup semantics, and makes exact managed checkpoint state—not branch/worktree existence—the continuity boundary. ADR-039 consolidates every normative upstream dependency into `EXTERNAL-CONTROL-PLANE-CONTRACT.md`. ADR-041 fixes v1 single-host scheduling: explicit invocations are coalescible convergence-demand triggers serviced by at most one fenced top-level run. ADR-042 closes 30.13 with the concrete reconciler-driven SQLite CoordinationStore, OS-owned run/fencing handshake, append-only recoverable-effect journal, transaction boundaries, stable repository relocation binding, and recovery-resource GC rules. ADR-043 closes 30.14 by fixing promotion-policy authority/constraint composition, trusted-target policy baselines, zero-onboarding built-in closure, and factual contradiction signaling without remediation advice. ADR-044 closes 30.15 by making immediate authoritative revalidation—not cache/TTL—the basis of policy currentness. ADR-045 closes 30.16 with immutable content-addressed PromotionUnit exact-state identity semantics. ADR-046 closes 30.17 by predeclaring durable closed content-addressed PromotionGroups over logical ConvergenceUnits without mid-sweep handoff or implicit singleton defaults. ADR-047 closes 30.18 by projecting each completely exact-resolved group deterministically into exactly one repository-local PromotionUnit per represented source repository. ADR-048 closes 30.39 by materializing a repository-local multi-source PromotionUnit through deterministic ancestry reduction, ancestry-aware canonical pairwise full two-head merge semantics, exact-state reuse when ancestry already suffices, otherwise one synthetic multi-parent final candidate, exact conflict/recovery boundaries, with no generic development-validation handoff for the final candidate after ADR-060. ADR-049 closes 30.19 with always-distinct submission refs, stable logical submission identity, exact revision guards, naming, and cleanup semantics. ADR-050 closes 30.20 by deriving stack shape from exact unsatisfied promotion dependencies and defining restack as an exact three-way state transplant over immutable owned child state. ADR-051 closes 30.21 by normalizing provider capability as contextual semantic-operation observation. ADR-052 closes 30.22 by making DIRECT target advancement a pure exact-old CAS+FF ref effect with recovery anchoring and authoritative-history adoption. ADR-053 closes 30.23 by turning exact `CHANGES_REQUESTED` generations into durable idempotent session-independent review-correction demands whose ordinary same-group corrections reconverge into new revisions of the same ADR-049 submission/PR. ADR-054 closes 30.24 by separating exact PromotionUnit completion from ConvergenceUnit semantic closure, operational retirement, GC eligibility, and physical retention; cross-repository partial promotion cannot prematurely close a lineage, and v1 historical internal-ref retention defaults to `KEEP`. ADR-055 closes 30.25 with durable exact-generation cross-repository settlement demands, external roll-forward/compensation authority, forward-only settlement effects, `ALL_PROMOTED | COMPENSATED` terminal settlement semantics, and sequential PublicationEpisodes for a stable logical submission whose earlier provider submission is already terminal. ADR-055 also retroactively makes the ADR-022/024/026/032/036 External Control Plane boundaries explicit in the companion contract. ADR-056 closes 30.26 by keeping new-repository creation outside the convergence engine/invocation, requiring an externally authoritative RepositoryCreationPolicy + recoverable Repository Provisioner (which ADR-078 permits the installed product to bundle), bootstrapping every newly admitted repository to a real exact target OID `B0` before managed authoring, separating local creation from optional/lazy provider attachment, and failing closed on unknown identity/collision rather than admitting unborn/null targets or guessing external authority. ADR-057 moves development verification execution outside `ruu`; ADR-060 further removes the generic development-validation evidence/demand protocol and replaces it with transition-local prerequisites. ADR-058 adds native-Git equivalence and fixes whole-editing-surface checkpoint intent with no v1 partial/path-selected checkpoint and no staging-based membership authority. ADR-059 closes 30.27 by canonicalizing the whole observable surface through native Git tree construction and fixing membership, structural blockers, submodule/sparse guards, no-op behavior, and exact pre-commit candidate identity. 30.29–30.33, 30.35, 30.37, and 30.38 are closed/reclassified outside the engine; ADR-061 closes 30.40 target-binding ownership/immutability; ADR-062 closes 30.36 by making early provider projection explicitly authorized and otherwise absent; ADR-063 keeps semantic findings/backlog outside the engine; ADR-064 makes pre-commit semantic-readiness identity a frozen mutation-handoff property rather than a generic validation-evidence gate. ADR-065 originally closed 30.34; ADR-066 corrects that proof to be route-conformant with explicit `C → H → R → O` provider lineage and historical-effect commitment semantics, while ADR-067 closes obsolete PromotionUnit supersession. ADR-068 originally closed 30.41 with explicit pre-promotion PromotionGroup `CANCELLED` settlement and deletion-neutrality; ADR-071 makes currently bound managed-authoring ref removal transactionally durable and ADR-074 corrects its classification to CONTINUATION-versus-ABANDON while unmanaged branch/worktree deletion remains neutral. ADR-069 closes hostile-audit items 30.42 and 30.43 by binding ordinary PromotionGroup occurrence identity to work-bearing logical invocations, making exact resolution group-local, and freezing terminal group resolution. ADR-071 closes 30.44 and 30.45 with current-disposition causal authorization fencing and transactional `reference-transaction` deletion capture. ADR-071 verification/v38 closes 30.48. ADR-072 closes 30.46 and ADR-073 closes 30.47. The native-Git observation-plane cluster under 30.49 is closed. ADR-074 closes 30.50, ADR-075 closes 30.51, ADR-076 closes 30.52, ADR-077 closes 30.53, ADR-079 closes 30.54, and ADR-080 closes 30.55 plus the umbrella with source-scoped local/remote/provider observation authority.

The following implementation/policy details are intentionally not fixed by the accepted architecture.

## 30.1 Resolved by ADR-041 — single-host coordination domain

V1 supports many simultaneous local callers/processes but one coordinated `ruu` domain is guaranteed only on a single host.

```text
many local invokers
→ supported through coalesced demand + one fenced executor

one coordination domain spanning several hosts
→ outside v1 requirements
```

Ordinary Git activity from other hosts is not forbidden; it simply does not gain the local coordination-domain correctness guarantee.

## 30.2–30.4 Resolved/retired by ADR-033

The former open questions for producer/runtime liveness, actor identity, and runtime handoff are no longer `ruu` backlog items. `contribution_unit_id` is the stable opaque repository-local bounded contribution identity under ADR-034/ADR-035/ADR-038; current lifecycle is externally authoritative `OPEN | CLOSED` under ADR-038.

Decided:

```text
contribution_unit_id
→ stable opaque repository-local identity supplied externally

external work-producer/runtime liveness / heartbeat / lease / stop / crash / resume
→ External Control Plane responsibility, outside Ruu

external mutation-access contract
→ PROTECTED_EXTERNAL
 | TRANSFERABLE_TO_RUU
 | TRANSFERABLE_GENERAL
 | UNKNOWN

transferable state
+ exclusive Ruu worktree claim held by current authoritative executor/operation
→ necessary mutation-authority boundary
```

The concrete external authority mechanism and the concrete claim/storage primitive remain implementation concerns of their respective subsystems, not unresolved contribution unit-liveness semantics in `ruu`.

## 30.5 Resolved by ADR-037 — ConvergenceUnit creation/membership authority

The External Control Plane creates or reuses ConvergenceUnits and binds every new ContributionUnit to exactly one `convergence_unit_id`. `ruu` never infers semantic grouping. The External Control Plane also owns the ConvergenceUnit contribution-membership declaration `OPEN | SEALED`.

The concrete External Control Plane API/policy for choosing create versus reuse remains outside `ruu`, not an open semantic question in this engine.

## 30.6 Resolved by ADR-037 — Eager ContributionUnit→ConvergenceUnit integration

There is no separate ContributionUnit integration-readiness/release signal. Every valid authoritative managed checkpoint of an `OPEN` or `CLOSED` ContributionUnit MUST be advanced toward its bound ConvergenceUnit at the earliest mechanically safe opportunity. `OPEN` ContributionUnits may integrate multiple checkpoints before closure. Experimental/alternative isolation uses a distinct ConvergenceUnit.

## 30.7 Resolved by ADR-037 — Mechanical sealed `READY_INTERNAL`

`READY_INTERNAL(OID)` requires, under the race-safe readiness barrier:

```text
ConvergenceUnit membership SEALED
zero OPEN ContributionUnits
for every CLOSED ContributionUnit, latest authoritative managed checkpoint (if any) fully resolved
zero unknown/orphan ContributionUnit membership/state
zero BLOCKED_MISSING_MANAGED_STATE or unresolved internal synchronization/integration/reconciliation/conflict/recovery obligation
transition-local exact prerequisites for that OID
internal fixed point reached
```

No additional repository-specific semantic-readiness token is required at this layer. Code-state-specific custom checks belong to the Development System; ship/review/provider governance belongs at its specific transition boundary. Physical ContributionUnit branch/ref/worktree presence or absence is not itself the readiness criterion.

## 30.8 Resolved by ADR-035/ADR-038 — ContributionUnit lifecycle and artifact independence

The semantic core is closed:

```text
OPEN
→ may still contribute to current convergence scope

CLOSED
→ no further contribution to current convergence scope
→ latest authoritative managed checkpoint, if any, remains subject to ordinary convergence until resolved
→ any later work requires a new contribution_unit_id
```

The External Control Plane owns ContributionUnit lifecycle declaration. `ruu` never infers closure from producer/runtime/turn state or branch/worktree presence/absence.

ContributionUnit identity is independent of local/remote contribution branch/ref and worktree existence. Already-created exact managed checkpoints are tracked by OID/state, not by editing-artifact existence.

## 30.9 Resolved/retired by ADR-038 — no ContributionUnit abandonment disposition

`ABANDONED`, preserve/discard residue policy, and automatic ContributionUnit branch/worktree cleanup are not part of the `ruu` model.

Unwanted code is modified/deleted through subsequent development Git state. Users/agents/External-Control-Plane tooling own contribution branch/worktree/remote-ref lifecycle. `ruu` only handles the exact managed Git obligations that remain:

```text
no unresolved exact checkpoint
→ nothing to advance

unresolved exact checkpoint OID recoverable
→ continue ordinary convergence from exact state

unresolved exact checkpoint OID unrecoverable
→ localized BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss condition
```

## 30.10 Resolved by ADR-040 — exact reconciliation obligations, external semantic authoring

`ruu` may complete only deterministic reconciliation that does not require semantic code authoring. An authoring-required conflict leaves authoritative state unchanged and creates a durable exact-state-bound `RECONCILIATION_REQUIRED` managed obligation.

The obligation exposes mechanical conflict evidence to the external Development System through the External Control Plane. It is diagnostic only: any authored result must later be revalidated against current Git/topology/policy state, protected by current claims/CAS, and any policy-required transition-local exact prerequisite must be satisfied before authoritative adoption. Unrelated work always continues.

## 30.11 Resolved by ADR-041 — concurrent invocation coalescing

There is no v1 policy of wait/retry/backoff/skip between several independent top-level `ruu` instances because such instances do not run concurrently as authoritative convergers.

```text
simultaneous explicit invocations
→ durable convergence demand advances
→ demands coalesce
→ at most one authoritative top-level executor
→ global fixed-point sweep
→ if newer demand arrived, sweep again
```

Fine-grained claims/CAS remain for actual mutable resources, internal parallelism, race-safe External Control Plane transfer, and recovery; they no longer arbitrate simultaneous top-level convergers.

## 30.12 Resolved by ADR-040 — candidate attribution follows the authorized ContributionUnit boundary

Per-process/per-file actor provenance is not normative. Mutations produced inside a valid ContributionUnit mutation-authority boundary belong to that ContributionUnit's exact candidate regardless of whether they were written by the coding agent, hook, formatter, generator, package manager, migration tool, or other subordinate tooling.

Candidate attribution remains separate from candidate Git-state identity. ADR-058 fixes whole-surface intent and staging non-authority; ADR-059 closes 30.27 by defining native Git tree construction, untracked/ignored membership, structural index/in-progress blocking, submodule/sparse-observability guards, no-op behavior, and the exact `(repository_id, git_object_format, parent_oid, tree_oid)` candidate identity. Verifier parasite-output policy is external to `ruu` under ADR-057.

A mutation that violates the required mutation-authority boundary is an integrity/staleness condition, not an attribution ambiguity. No affected candidate may be authoritatively adopted until valid authority/exact state are re-established and the resulting state satisfies all transition-local exact prerequisites.

## 30.13 Resolved by ADR-042 — reconciler-driven v1 CoordinationStore and recoverable-effect journal

The v1 runtime is now fixed at the architecture level:

```text
single-host SQLite CoordinationStore
+ current-state ConvergenceEngine/reconciler
+ process-lifetime OS exclusive lock for physical top-level run ownership
+ monotonic run_generation + unique run_token for durable fencing
+ append-only Operation → Attempt → Observation → Adoption effect journal
+ short exact-state/CAS SQLite transactions
+ exact re-observation across Git/provider/filesystem effect boundaries
```

`ruu` is not a persisted step workflow. A crash is recovered by loading current managed state, unresolved Operations, and current Git/provider facts, then reconciling again.

The CoordinationStore has explicit schema/version authority, a singleton demand/run-fence row, stable opaque repository identities with separately CAS-updatable host-local locator bindings, authoritative managed domain rows with exact expected-state guards, append-only effect-journal records, and recovery-resource references.

An authorized trigger first advances `requested_generation`. Physical run ownership is an OS-backed process-lifetime advisory lock; after acquiring it, a process establishes a fresh fenced `run_generation + run_token`. The durable run state is `ACTIVE | IDLE`. Release is race-safe: the fixed-point accounting transaction either remains `ACTIVE` because newer demand exists or commits `IDLE` and clears the token before physical lock release. `BUSY + IDLE` means a caller must retry ownership acquisition rather than return, preventing a lost wakeup in the release window.

No heartbeat/TTL lease performs automatic takeover of a live-but-hung process in v1. Normal long operations require timeout/cancellation; provider/CI/review waits are represented as nonterminal waiting obligations and do not keep the run alive merely to sleep; SQLite transactions remain short.

For a recoverable external effect:

```text
TX-A: persist/resolve immutable Operation + append fenced Attempt
COMMIT

perform bounded external effect with no SQLite transaction held
observe exact current external state

TX-B: verify current run fence + append Observation
      + attempt exact managed-state CAS
      + append Adoption atomically iff CAS succeeds
COMMIT
```

A failed CAS never adopts. An unresolved Operation survives process death and may receive a new Attempt under a newer fenced run. When supported, the stable logical `operation_id` is also the provider/client idempotency identity. Operations that become terminal without adoption receive an immutable observation-bound closure/disposition.

Temporary recovery refs/workspaces use non-recycled operation/attempt/incarnation namespaces. A correctness-critical recovery resource is `REQUIRED` until another durable reachability root and all recovery dependencies are proven; it then becomes `GC_ELIGIBLE`. Physical cleanup after that transition is best-effort, idempotent, unjournaled, and never a correctness prerequisite.

Repository identity is opaque and stable; path/remote/inode are not identity. Explicit relocation updates only the current repository locator binding through exact expected-state/CAS semantics.

Unknown/incompatible schema/state fails closed. Known schema migrations are explicit, ordered, store-only, short SQLite transactions. Multi-host evolution remains outside v1 and requires a new ADR.

## 30.14 Resolved by ADR-043 — promotion-policy authority, composition, contradiction, and default resolution

The effective promotion policy is compiled from authoritative provider capabilities/current facts, provider/organization governance constraints, and trusted repo-committed policy. There is no generic source-precedence ladder and no runtime/local-config bypass.

Explicit incompatible authoritative constraints produce `CONTRADICTORY` and block the affected promotion without silent fallback. Repo-committed policy is read from the trusted exact target baseline, so a candidate cannot change the rules governing its own promotion. Deterministic built-in rules fill only still-underdetermined dimensions and provide zero-onboarding behavior, including default `DIRECT_TARGET_ADVANCE` when direct target advancement is admissible and no authoritative constraint requires an indirect path.

Contradictions surface as first-class factual machine-readable blocking diagnostics containing exact incompatible constraints and source provenance. `ruu` does not infer, recommend, rank, or apply remediation; the external Development System/operator decides what to do with the signal.

## 30.15 Resolved by ADR-044 — policy currentness, refresh, and cache non-authority

Policy snapshots are immutable/fingerprinted observations anchored to exact authoritative source identities when available. Cache is an optimization only: cache hit, age, TTL, prior resolution, or prior successful mutation never establishes `CURRENT`.

Every executed global sweep refreshes the policy state needed by managed obligations. In addition, immediately before every policy-sensitive promotion mutation, `ruu` MUST re-observe/revalidate every mutable authoritative source needed by that mutation. Exact target OID/repository-policy anchor movement or any provider/org governance/capability/fact observation change invalidates the prior policy snapshot and forces recomputation before mutation.

When a provider exposes version/fingerprint/ETag-equivalent identities, revalidation uses them; otherwise an immediate fresh normalized observation is required. No TTL fallback substitutes for a missing strong version primitive. Where no atomic governance-check+mutation API exists, provider enforcement/rejection and exact post-operation observation form the final external authority boundary. Concurrent drift/rejection is surfaced factually to the external Development System/operator and is not autonomously repaired.

The minimal persisted freshness provenance includes the policy fingerprint, trusted target/policy anchor, and for each mutable authoritative external source its source identity plus observed revision/version/fingerprint when exposed, observation method, and observation identity. Wall-clock observation time may be recorded for diagnostics/operations but is not authorization evidence by itself.

## 30.16 Resolved by ADR-045 — immutable content-addressed PromotionUnit definition/identity

ADR-045 fixes the exact object that results from promotion grouping:

```text
PromotionUnitDefinition {
  members: Set<ExactConvergenceStateRef>
}
```

The immutable `promotion_unit_id` is derived from a versioned/domain-separated canonical encoding of the sorted member refs; v1 uses SHA-256. Same exact member set yields the same identity intrinsically; any changed exact member state yields a different PromotionUnit.

ADR-046 originally inserted a pre-exact PromotionGroup between ConvergenceUnits and PromotionUnits. ADR-069 amends its origin/identity/resolution semantics: ordinary groups are occurrence-bound to sealed work-bearing logical invocations, membership is mechanically derived from the invocation's ContributionUnits, and exact resolution is group-local rather than an alias of live current `READY_INTERNAL`. ADR-047 still partitions each adopted group-local exact mapping by authoritative source repository and materializes/reuses one ADR-045 PromotionUnit per represented repository.

Lifecycle, topology, target/mode/publication policy, provider-facing submission revision, semantic task identity, and any semantic-readiness token are outside the PromotionUnit definition and outside its content address. Structural definition validity is separate from current promotion eligibility.

## 30.17 Resolved by ADR-046 as amended by ADR-069 — closed PromotionGroups resolve mechanically to exact PromotionUnits

There is no implicit/default `READY_INTERNAL → singleton PromotionUnit` mapping inside `ruu`. ADR-069 changes how the group boundary is established for ordinary work: one sealed work-bearing logical invocation carries a non-empty closed ContributionUnit handoff cohort, and `ruu` mechanically derives the distinct ConvergenceUnit member set through the already-authoritative ContributionUnit bindings.

```text
LogicalInvocation I
  handoffs = {CU-A, CU-B, ...}
  binding = NEW_GROUP

ConvergenceMembers(I)
  = distinct(convergence_unit_of(CU) for CU in I.handoffs)

→ one occurrence-bound PromotionGroup G(I)
```

The work-bearing invocation receipt is durable/idempotent and distinct from its coalescible convergence-demand signal. Distinct invocation occurrences create distinct PromotionGroups even when their member sets are identical. A one-member cohort yields a singleton group mechanically.

Exact group resolution is group-local. Initial exact member bindings are attributable to the originating invocation; a later ordinary invocation may advance the same live ConvergenceUnits without refreshing the earlier group. An existing nonterminal group may adopt a newer exact resolution only under current explicit `REVISE_EXISTING_GROUP(G, authority_ref)` correction/reconciliation authority, and untouched members retain their previous exact group state.

## 30.18 Resolved by ADR-047 as amended by ADR-069 — deterministic repository-local projection of group-local exact resolutions

A completely adopted PromotionGroup exact mapping is projected by authoritative source repository:

```text
Project(G,R)
  = { GExactState(C) | C ∈ G.members ∧ repository(C)=R }
```

Exactly one non-empty projection/PromotionUnit exists per represented repository. Same PromotionGroup plus same source repository therefore yields one current repository-local PromotionUnit; `ruu` does not invent an alternate partition or split that projection to create stacked provider submissions. A valid PromotionUnit cannot contain exact source refs from multiple repositories.

The complete group-local member mapping and repository→PromotionUnit mapping are adopted under expected-state/CAS guards. Later unrelated live ConvergenceUnit movement does not invalidate that mapping. A legitimate same-group correction/reconciliation may adopt a newer mapping and thereby supersede older unpromoted PromotionUnits under ADR-067. A terminal group cannot adopt a newer mapping.

This preserves ADR-047's structural multi-source projection rule while removing ADR-046's obsolete dependency on each member's unqualified live current `READY_INTERNAL` state. ADR-048 continues to close repository-local composition of several exact source states into one concrete candidate/head.

## 30.19 Resolved by ADR-049 — stable submission identity/ref lifecycle

ADR-049/055 close submission-ref creation/naming/retention and provider-episode semantics. provider-submission publication always uses provider-facing episode refs distinct from internal refs. `submission_id` is stable for one repository-local PromotionGroup projection toward one canonical publication destination while exact PromotionUnit/head and monotonic logical revision may change. One nonterminal PublicationEpisode owns one provider submission; revisions use exact expected-old guards. If that provider submission becomes terminal while the same nonterminal logical submission later needs another exact publication, a distinct new PublicationEpisode/ref/provider submission is created under first-publication expected-absent/policy/provider guards. Preferred new-episode namespace is `refs/heads/Ruu/submissions/<submission_id>/episodes/<publication_episode_id>` with repository-approved compatible alternatives. Physical episode-ref cleanup is allowed only after that episode's terminal provider/target/recovery state and never carries durable identity/audit authority. ADR-054 closes ConvergenceUnit historical internal-ref lifecycle with `RETIRED → GC_ELIGIBLE` separation and v1 built-in `KEEP`; ADR-060 closes 30.28 by removing the generic development-validation evidence contract.

## 30.20 Resolved by ADR-050 — derived stacked publication and exact-state restacking

ADR-050 closes the restacking semantic core. A stacked provider submission is not requested by a caller: it is the provider projection of an exact promotion dependency that is not yet satisfied by the authoritative target. If the dependency is already target-satisfied, publication is ordinary; if unsatisfied and stack representation is supported/authorized, it is stacked; otherwise the child waits.

When the predecessor exact head moves, restack reprojects the child's immutable owned state `(old_base_oid, owned_candidate_oid)` onto the new exact base with a versioned full three-way state-transplant semantic (`base=old base`, `ours=new base`, `theirs=owned candidate`). Internal refs never move, repeated restacks never chain from prior provider rewrites, conflicts route to `RECONCILIATION_REQUIRED`, every new exact head satisfies the exact transition-local prerequisites of the revision/publication transition, and only the ADR-049 submission ref/revision is rewritten under expected-old guards. Local/provider-native/external-tool execution is pluggable only if the observed result conforms to the same normative transplant contract.

## 30.21 Resolved by ADR-051 — contextual semantic provider capability observations

ADR-051 closes provider capability discovery by making capability a fresh normalized observation over a **core-defined semantic operation + exact provider context**, not a provider-wide feature matrix. The core first determines the required transition; the adapter reports whether that exact operation is `SUPPORTED | UNSUPPORTED | UNKNOWN_INCONSISTENT`, with provider mechanism, applicability/current facts, evidence/review/check effects when relevant, and freshness provenance.

Execution requires independent conjunction of:

```text
REQUIRED by core exact-state semantics
+ SUPPORTED by provider/context
+ AUTHORIZED by EffectivePromotionPolicy
+ ordinary exact-state/transition-local/claim/recovery guards
```

Provider-native/external executors never become semantic authority: exact observed output must conform to the same normative core contract. ADR-050 promotion topology remains derived state rather than a policy/provider choice, and ADR-044 immediate pre-mutation revalidation applies to capability/current-fact observations.

## 30.22 Resolved by ADR-052 — exact-old CAS+FF DIRECT target advancement

ADR-052 closes the DIRECT-specific target-advancement envelope after ADR-048 has already produced exact candidate `C` and the DIRECT transition-local prerequisites for `C` are satisfied. No target worktree, merge-into-target step, or pre-advanced local target ref is part of the correctness path.

The core operation is `AdvanceTargetFF(target, expected_old=B, new=C)`: success requires the authoritative target still equal exact `B` and immutable ancestry proof `B` ancestor-or-equal `C`; its only permitted effect is atomic `B → C`. Any expected-old mismatch performs no target mutation and forces fresh target/policy/candidate re-resolution.

Exact `C` remains durably reachable through an attempt-scoped recovery anchor until the ADR-042 Observation/Adoption path proves the effect. Recovery adopts when authoritative target equals `C` or has advanced to a descendant containing `C`; target still at `B` means not yet realized, while divergent history is stale/drift rather than success. Physical anchor cleanup is separated from durable operation/audit retention. Backend/provider mechanisms are pluggable only when they satisfy this semantic CAS+FF contract.

## 30.23 Resolved by ADR-053 — durable session-independent review correction

A current exact `CHANGES_REQUESTED` generation becomes one durable idempotent `ReviewCorrectionDemand` bound to the reviewed `submission_id`, exact `submission_revision`/head, PromotionGroup/repository projection, authoritative review generation/fingerprint, and factual feedback payload/provenance. Provider hooks and `ruu` global sweeps are coequal discovery paths for the same demand; rediscovery MUST NOT duplicate semantic work, and an unrelated session that triggered the sweep never inherits the correction.

The originating coding session need not remain alive. The External Control Plane may restore it or start a new continuation session with the review feedback as new development input. Up-front mapping to one ConvergenceUnit is not required: while analyzing/implementing the correction, the Development System identifies whichever **existing** member ConvergenceUnits require writes and provisions new ContributionUnits from the exact reviewed/group-local state authorized for `G`, not blindly from the live current tip. The resulting work-bearing invocation uses `REVISE_EXISTING_GROUP(G, authority_ref)`. `CLOSED` ContributionUnits never reopen, and authoring never occurs directly on the provider submission ref.

If only existing PromotionGroup members change, the immutable group membership remains the same and the authorized revision may adopt new group-local exact states only for touched members; untouched members retain their prior bindings. The ADR-049 logical `submission_id` remains stable when its logical key is unchanged: an open PublicationEpisode is revised in place, while a terminal episode is followed by a new ADR-055 episode/provider submission if the nonterminal ship still needs publication. A genuinely new ConvergenceUnit is scope expansion and cannot be added to the closed old group.

## 30.24 Resolved by ADR-054 — PromotionUnit completion versus ConvergenceUnit closure/retirement

ADR-054 separates three completion boundaries. `PromotionUnit PROMOTED` means only that one immutable exact repository-local snapshot reached/adopted its terminal promotion outcome. It does not close or retire the referenced ConvergenceUnit, including during cross-repository `PARTIALLY_PROMOTED` progress.

A ConvergenceUnit reaches `PROMOTED` only after every relevant PromotionGroup/promotion obligation referencing that lineage is terminally settled and no current durable ReviewCorrectionDemand or other authoring/reconciliation obligation can still reactivate it. Once ConvergenceUnit `PROMOTED`, ordinary same-lineage reopen/new ContributionUnit creation is forbidden; later semantic work uses a new ConvergenceUnit/new ship lineage.

`RETIRED` is later still: terminal effects must be durably adopted and no correctness-critical recovery/resource dependency may require the ConvergenceUnit as a live operational resource. Retirement may make historical internal refs `GC_ELIGIBLE`, but physical deletion is separate. V1 built-in historical internal-ref retention is `KEEP`; durable logical/audit history remains independent, and no generic development-validation evidence retention requirement remains after ADR-060. ADR-055 supplies the cross-repository terminal settlement forms consumed by this guard.

## 30.25 Resolved by ADR-055 — cross-repository settlement/compensation

`PARTIALLY_PROMOTED` is nonterminal ordinary progress and does not automatically trigger failure or rollback. If ordinary remaining repository-local paths can continue, they do. When semantic cross-repository disposition is required, one durable exact-generation `CrossRepositorySettlementDemand` is recorded/refreshed and remains in the global managed-obligation universe.

The External Control Plane/Development System alone chooses roll-forward versus compensation; `ruu` never invents a revert. Every settlement effect is forward-only ordinary development/promotion state. Normal successful settlement is `ALL_PROMOTED` over the current exact repository projection mapping. Explicit compensation may terminalize the group as `COMPENSATED` only after current external semantic compensation intent/completion plus independent observation/adoption of every exact forward effect required by the plan. No silent partial `ABANDONED` terminal path exists.

ADR-055 also amends ADR-049: one stable logical `submission_id` can contain multiple sequential PublicationEpisodes. Exact revisions update the same nonterminal episode/provider submission; a terminal provider submission is never reopened. If the same nonterminal logical submission later requires another exact repository-local publication, a distinct episode/ref/provider submission is created under ordinary first-publication safety guards.

## 30.26 Resolved by ADR-056 — new repository creation/bootstrap authority

A coding agent/session/orchestrator may request a new repository, but request identity is not creation authority. The convergence engine never creates local repositories or provider repositories as a convergence side effect; a bundled Repository Provisioner may do so only under External Control Plane authority. The External Control Plane resolves standing/explicit `RepositoryCreationPolicy`, and a Repository Provisioner performs authorized creation/reconciliation. Provider/account/organization/namespace/visibility are not self-authorized by the agent; if provider creation is authorized and visibility alone is truly underdetermined, the built-in safe default is `PRIVATE`, never `PUBLIC`.

V1 does not admit an unborn/null target. Before any first managed write, a brand-new repository must satisfy the `RepositoryBootstrapContract` and have its configured target at a real exact bootstrap commit `B0`:

```text
new repository
→ stable repository_id + authorized locator
→ valid Git repository
→ configured target → exact non-null B0
→ required bootstrap/governance established
→ provider binding validated if required for the current phase
→ REPOSITORY_ADMITTED
→ ordinary ADR-015/023 ConvergenceUnit/ContributionUnit provisioning
```

`B0` may be a minimal root commit or an authorized bootstrap/template commit. Once admitted, the repository is ordinary to `ruu`; no new-repository/null-OID special case exists in the convergence engine.

Local repository creation and provider repository creation are separate. Provider creation/attachment may be eager or deferred; missing provider binding blocks only provider-sensitive operations that require it. Provisioning intent/recovery is durable and idempotent outside the convergence engine's state machine (even when implemented by a bundled product component): retries observe/adopt exact already-realized local/provider effects, names/paths are never identity, unknown collisions fail closed, and a partial provisioning failure does not authorize destructive repository deletion.

## 30.27 Resolved by ADR-059 — canonical whole-editing-surface checkpoint snapshot and identity

ADR-058 fixes whole-editing-surface checkpoint intent and staging non-authority. ADR-059 closes the remaining Git-level mechanics.

For exact authoritative parent checkpoint `P`, `ruu` reconstructs a temporary canonical index from `P` and applies the complete observable Git-relevant editing surface using native whole-tree Git semantics, then writes exact tree `T`:

```text
P + fully observable claimed editing surface
→ temporary native Git index seeded from P
→ native whole-surface update equivalent to `git add -A`
→ `git write-tree`
→ exact candidate tree T
```

Membership/guards are fixed:

```text
tracked modifications/deletions        INCLUDE
untracked non-ignored paths            INCLUDE
untracked ignored paths                EXCLUDE
tracked paths later matched by ignore  remain ordinary tracked Git state
staged/unstaged/intent-to-add          NOT membership authority
unmerged/in-progress structural Git    BLOCK / recover first
dirty or required-but-unknown submodule BLOCK
clean exact submodule                   native gitlink OID
symlink/file-mode/filter/EOL/LFS        native Git semantics
sparse/skip-worktree preventing full observation BLOCK in v1
T == tree(P)                            NOOP; no empty managed commit
```

Exact checkpoint-candidate Git-state identity is the canonical tuple:

```text
(repository_id, git_object_format, parent_oid=P, tree_oid=T)
```

with a versioned domain-separated canonical fingerprint. ContributionUnit identity remains attribution/governance metadata rather than part of the Git-state identity. Tests, development-validation profiles/context, and commit metadata are not part of candidate identity; ADR-060 removes any generic development-validation binding from `ruu`.

The ordinary Git checkpoint commit must satisfy `parent(K)=P` and `tree(K)=T`, and successful materialization leaves the real index/worktree in coherent native-Git state under ADR-058. ADR-064 supplies the pre-commit identity bridge: the Development System's semantic readiness remains external, while durable transferability freezes external writes until the exact claimed whole-surface candidate is constructed/revalidated and either committed or safely released/recovered.

## 30.28 Closed by ADR-060 — generic DevelopmentValidationEvidence contract is obsolete

ADR-060 removes the generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` concept from the `ruu` contract rather than defining a smaller schema.

Development-quality validation remains owned by the Development System. Each `ruu` transition is governed by its own exact Git/managed/policy/provider prerequisites and, where genuinely needed, the narrow authoritative external fact specific to that transition. Exact-state binding remains mandatory for those transition-specific facts/evidence.

## 30.29 Closed by ADR-057 — verification executor/capacity scheduling

Development System concern. No `ruu` validation scheduler/capacity state exists.

## 30.30 Closed by ADR-057 — flaky-test and infrastructure-failure policy

Development System concern. `ruu` has no generic flaky-test or development-validation evidence state.

## 30.31 Closed by ADR-057 — external-service test policy

Development System concern.

## 30.32 Closed by ADR-057 — semantic submission-author / ship-ready gate composition

The Development System / repository governance defines and executes the semantic ship-ready process. `ruu` consumes exact-revision-bound `REVIEW_REQUESTED` intent/evidence required by current policy; it does not decide which tests/review agents/docs/security checks constitute ship-ready.

## 30.33 Closed by ADR-057 — provider CI execution policy

Which tests/build matrices/security analyses execute at the provider is repository/provider governance. `ruu` still observes exact provider check/review/queue state and enforces the current provider/promotion policy.

## 30.34 Resolved by ADR-065 as corrected by ADR-066 — exact route-conformant final target realization proof

ADR-066 corrects the ADR-065 proof model so terminal success depends on both exact target realization and conformance to the applicable route.

```text
DIRECT_TARGET_ADVANCE
  fresh authoritative target O == C
  OR C ancestor-of O
  + DIRECT route compatible with the realization
  → direct realization proven
  → actor need not be Ruu itself

PROVIDER_SUBMISSION
  exact SubmissionProjectionProof binds C → submitted H
  + exact ProviderFinalizationObservation binds H → final result R on T
  + fresh authoritative Git observation proves O == R or R ancestor-of O
  → provider-route realization proven
```

Candidate ancestry cannot bypass a required provider route. Provider `MERGED` / `FINALIZED` alone remains insufficient. Restack is represented explicitly by `C != H` when ADR-050 projection requires it. No universal semantic diff/patch equivalence is required.

Recovery also follows ADR-066 effect-commitment semantics: old policy may justify adoption of an already committed historical effect but cannot authorize a new causal mutation after policy drift.

## 30.35 Closed by ADR-057 — agentic review policy

Development System / repository-governance concern.

## 30.36 Resolved by ADR-062 — REVIEW_NOT_REQUESTED no-projection default

ADR-032 fixes review-request intent semantics and ADR-057 externalizes semantic review execution. ADR-062 closes the remaining Git/policy fallback: `REVIEW_NOT_REQUESTED` permits early/draft provider projection only when explicit current authority/need exists. If neither that authority nor `REVIEW_REQUESTED` is current, no provider submission is created merely to manufacture a PR/MR object. Explicit authoritative repository/provider governance always wins.

## 30.37 Closed by ADR-057 — general security-check placement

Development System / provider-governance concern. `ruu` does not define where SAST/CodeQL/dependency/supply-chain/image scans execute.

## 30.38 Closed by ADR-057 — internal integration test orchestration

A newly synthesized exact internal merge/synchronization result may advance when its exact transition-local Git/topology/claim/conflict guards hold. `ruu` does not run or schedule integration tests.

## 30.39 Resolved by ADR-048 — repository-local multi-source candidate materialization

ADR-048 fixes the downstream materialization semantics for a repository-local PromotionUnit containing several exact source states.

Given exact effective base `B` and exact immutable PromotionUnit source set `S`, `ruu`:

```text
1. removes from the execution fold only sources already contained by B or another retained source;
2. canonicalizes the ancestry-maximal retained source heads in a versioned deterministic order;
3. folds them in canonical order, reusing ancestor/descendant states and invoking full Git two-head three-way merge semantics (`ort`-class or proven-equivalent) only for divergent steps;
4. reuses `B` or an existing source as the final candidate when ancestry already contains the whole unit, otherwise condenses the fold tree into one canonical synthetic multi-parent commit;
5. stops and emits/refreshes ADR-040 RECONCILIATION_REQUIRED if any fold step needs semantic conflict authoring;
6. for synthesized candidates, uses B as first parent, canonical retained source heads as remaining unique direct parents, and the fold result as the tree;
7. uses deterministic wall-clock-independent synthetic commit metadata under a versioned MaterializationContract;
8. requires B and every original exact source OID to be ancestors of the final candidate;
9. requires the exact transition-local promotion/submission prerequisites for that final candidate before authoritative adoption;
10. executes/retries/recoveries through ADR-042 Operation→Attempt→Observation→Adoption with isolated attempt-scoped recovery resources.
```

Native multi-head `octopus` is not the normative merge algorithm because it is less general than the normal full two-head merge engine. Internal ConvergenceUnit refs are never rebased/rewritten to manufacture the candidate. Pairwise transient commits are computational artifacts, not provider-visible promotions or separately verified managed states.

DIRECT-specific target advancement is closed by ADR-052 as an exact-old CAS+FF ref effect with recovery anchoring; submission-ref identity/ref lifecycle is closed by ADR-049 and dependency/restack semantics by ADR-050.



## 30.40 Resolved by ADR-061 — immutable pre-authoring PromotionTarget binding

ADR-061 closes the destination-ownership ambiguity exposed by real Development System invocation semantics. Each ConvergenceUnit is bound before first managed write to one immutable `(target_repository_id, target_ref)` PromotionTarget owned by the External Control Plane. The repository-local ConvergenceBase is distinct from that logical final destination.

`EffectivePromotionPolicy` no longer selects `target_repository/ref`; it answers how current exact state may reach the fixed target. The SAME/CROSS repository relation is derived from source + target identity, and same-source PromotionGroup projections with conflicting immutable targets fail closed rather than being split or retargeted. Target OID/current governance remain dynamically revalidated.

## 30.41 Resolved by ADR-068/071, corrected by ADR-074/075 — pre-promotion cancellation and native managed-authoring disposition

ADR-068 introduced exact terminal pre-promotion cancellation while preserving immutable PromotionGroup membership. ADR-071 made managed-authoring binding cessation causally durable and introduced the current-disposition authorization fence. ADR-074 corrects the classifier; ADR-075 fixes the capture-strength mechanism: a conforming native-ref adapter records a normalized pre-linearization witness and the core derives terminal-removal versus rename-carry preparation before the binding mutation may commit.

```text
unmanaged branch/ref deletion
→ ordinary Git artifact event

worktree deletion alone
→ ordinary Git artifact event

native mutation can terminate/replace current managed authoring binding
→ pre-linearization normalized witness
→ TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN
→ UNKNOWN: veto ambiguous mutation
→ committed rename + successor proof: CONTINUATION
→ committed terminal-removal proof: ABANDON → CANCEL for still-unrealized ship
```

The user/agent still uses ordinary Git and does not name a PromotionGroup or issue a second ordinary cancellation command. Same OID/tree/ancestry or a copied branch never proves continuation. Immutable PromotionGroup membership remains unchanged; already-realized/causally committed history remains under ADR-055/071 settlement and cannot be erased by later abandonment.

## 30.44 Resolved by ADR-071 — current semantic disposition is a causal authorization fence

A persisted operation is replayable as historical knowledge/observation, never as durable future authority. Immediately before every managed effect capable of newly realizing a PromotionGroup projection, `ruu` must establish current semantic authorization for that exact effect under a causal fence covering disposition validation through causal effect commitment. `CANCEL` or `COMPENSATE` cannot linearize through an incompatible managed realization already under the same fence; after the disposition transition linearizes, an old proven-absent nominal attempt cannot be retried. Already-committed historical effects are observed/adopted rather than denied.

Normative summary:

```text
reconciliation may recover knowledge without recovering authority
```

## 30.45 Resolved by ADR-071, corrected by ADR-074/075 — transactional native binding disposition and external-race classification

ADR-075 replaces hook-name conformance with a capability contract. Any native mutation capable of ending/replacing a currently bound managed authoring ref must expose a vetoable/equivalently serialized pre-linearization adapter point; the normalized witness is durable before causal commit. The tested `files` adapter uses `reference-transaction` plus backend-specific rename evidence. Native causal rename/rebind proof yields `CONTINUATION`; positive terminal-removal preparation plus committed outcome yields `ABANDON`; insufficient proof remains unresolved.

Provider/publication surfaces created before a resolved abandonment are not residual authorization. `ruu` closes/revokes still-revocable paths under current authority and may not perform new nominal realization after `CANCEL`. A realization already causally committed before abandonment is recovered/adopted. If relative order between an unmanaged external realization and the abandonment event is genuinely unprovable from authoritative causal evidence, terminal classification fails closed rather than inventing wall-clock order.

The currently demonstrated `files` adapter relies on Git `reference-transaction` support (Git >=2.28), but version/hook presence alone is not backend conformance. Backend admissibility is established by ADR-075 capabilities.

ADR-077 additionally makes effective observer coverage a repository-common, functionally attested property of an admitted mutation-engine/adapter path. V1 guarantees Git core rather than every Git-compatible implementation. A foreign/direct writer that bypasses the admitted pre-linearization path cannot acquire managed semantics from final topology; if it changes a current managed binding the result is an observation-integrity failure. Observer install/upgrade/remove is non-destructive and expected-state guarded; foreign `core.hooksPath`/hook registrations are never silently taken over.

## 30.46 Resolved by ADR-072 — host run-lock handles are non-inheritable

ADR-072 closes the surviving-child host-fence hole by requiring the top-level executor's host run-lock descriptor/handle to be non-inheritable across every subprocess boundary. A descendant may not keep the physical executor fence alive after the owning `ruu` process dies.

## 30.47 Resolved by ADR-073 — Git worktrees are the v1 authoring isolation substrate

ADR-073 requires a dedicated Git worktree/ref surface for every actively authored managed ContributionUnit in v1. Durable ContributionUnit/checkpoint identity remains independent of later worktree lifetime; arbitrary prebuilt commit/tree/snapshot ingress is not a v1 authoring contract.

## 30.48 Closed by v38 / ADR-071 verification — extended hostile state-space coverage

`STATE-SPACE-AUDIT-v38.md` historically covered the ADR-071 pre-correction classifier. ADR-074 supersedes the direct `committed old-ref deletion → abandonment` inference; `STATE-SPACE-AUDIT-v39.md` re-runs the retained baseline and adds rename/rebind/disposition and recovery dimensions. 30.48 remains closed as a verification item rather than reopening the old classifier.

## 30.49 CLOSED BY ADR-080 — native Git observation plane scope and invariant

This umbrella investigation opened by ADR-071's narrow transactional abandonment mechanism is closed by ADR-080 after coherent resolution of 30.50–30.55. Native Git remains directly usable; causal transactional capture is limited to current managed-binding disposition, all other exact facts are re-observed from their source-owned local/remote/provider authority, and hooks remain observers rather than a semantic convergence executor.

## 30.50 CLOSED BY ADR-074 — minimal correctness-relevant Git observation set

ADR-074 derives a three-plane taxonomy from the managed state machine:

```text
STATE PLANE
→ exact current Git/remote/provider facts required by the current transition

EVENT PLANE
→ only managed-authoring binding disposition is presently irreducibly causal locally

OBSERVATION-INTEGRITY PLANE
→ whether required event coverage remained continuously trustworthy
```

Ordinary commit/reset/merge/rebase/ref-tip/worktree/HEAD/submission/target mutations remain state-observed. Same OID/tree/ancestry never proves authoring continuation. Native managed reflog is required causal-evidence infrastructure. `refs/replace/*`, grafts, and shallow boundaries are explicit ancestry-state concerns. No second local business-event family was found in the hostile sweep. ADR-075 closes 30.51 capture strength, ADR-076 closes 30.52 provenance/replay/idempotency, ADR-077 closes 30.53 observer ownership/admission/coverage establishment, ADR-079 closes 30.54 persistence-failure/admission behavior, and ADR-080 closes 30.55 local/remote/provider composition plus the 30.49 umbrella.

## 30.51 CLOSED BY ADR-075 — transactional capture versus exact-state rediscovery

Only native mutations capable of terminating/replacing a currently bound managed authoring ref require correctness-critical pre-linearization durable capture. A conforming backend adapter supplies a normalized vetoable witness before causal commit; the core derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`, and `UNKNOWN` cannot silently linearize. `ABANDON` and `CONTINUATION` are separate positive proofs.

All other retained Git/remote/provider observations are exact-state rediscovery. Additional hook/watcher notifications are best-effort wakeups only. Backend admissibility is capability-based rather than `files`/`reftable`-named; the tested stock `files` path is a demonstrated candidate while the tested stock Git 2.47.3 reftable `branch -m/-M` path lacks the required pre-linearization callback and is not currently conforming for live managed authoring.

## 30.52 CLOSED BY ADR-076 — observation provenance, replay, and idempotency

Native causal witnesses/preparations are distinct from managed `Operation` intent and never manufacture a second Operation. Optional trusted `originating_attempt_id` is explanatory correlation only. Exactly-once applies to authoritative logical Adoption/disposition by `operation_id` / current `binding_generation`; observation delivery may duplicate/replay and best-effort wakeups may be lost/coalesced/reordered. The adapter correlates duplicate delivery of the same active native occurrence sufficiently to reuse one effective preparation/decision; no global permanent Git transaction ID is required. Repeated scans may resolve existing durable evidence but never synthesize missing causal preparation from final topology.

## 30.53 CLOSED BY ADR-077 — attested repository-common observer coverage without foreign-hook takeover

Live managed authoring requires one functionally attested repository-common observer binding for the admitted native ref-mutation engine/adapter profile before first managed write. Git core is the required V1 mutation-engine family; tools that delegate relevant ref writes to a conforming engine inherit conformance, while alternative engines require separately demonstrated adapters. Direct/uninstrumented ref-store writes remain physically possible but an unwitnessed change to a managed binding is an observation-integrity failure, never implicit `CONTINUATION` or `ABANDON`.

`ruu` owns only exact observer registrations/artifacts it created or previously adopted and mutates them under expected-state/CAS. It never silently overwrites `core.hooksPath`, a foreign traditional hook, an entire hookdir, another configured hook, or a third-party dispatcher. Composition uses a Git-native or explicitly supported adapter surface. Git 2.54+ configured multiple hooks are the preferred modern path but not a universal V1 version floor; a legacy traditional `reference-transaction` slot is admissible only when absent/already exactly owned or explicitly composed by a demonstrated adapter. Failure to establish coverage blocks managed-authoring admission, not ordinary Git.

Coverage is functionally attested, repository-scoped rather than session-scoped, and tracked through coverage epochs. Clone/recreation/reactivation and relevant mutation-engine/config/backend/adapter changes require re-establishment. A later healthy epoch cannot retroactively prove a prior gap; ADR-079/30.54 defines the concrete persistence/retry semantics when required capture or coverage fails.

## 30.54 CLOSED BY ADR-079 — minimal persistence failure semantics, protection filtering, and exact binding admission

ADR-079 makes native Git rejection proportional to causal necessity. Transactions with no cessation/replacement candidate remain exact-state observed and are allowed; advisory wakeups/logs/telemetry never become rejection authority. For a candidate that affects a current managed binding, the complete `NativeBindingPreparation` batch must be crash-durable before permission to linearize; unavailable classification or persistence fails closed after any bounded retry. Lost/failed post-preparation `COMMITTED | ABORTED` recording remains recoverable and never retroactively rolls Git back.

A repository-common conservative `ManagedRefProtectionFilter` allows trustworthy negative fast-path decisions without duplicating binding authority. Filter degradation disables negative acceleration and falls back to the CoordinationStore rather than creating a coverage gap; double uncertainty on a cessation candidate fails closed. Initial binding admission is itself serialized with native ref mutation through a capability-based `RefAdmissionBarrier`; the binding becomes current while the barrier is held, exact worktree topology is revalidated, and only then is authoring authority handed to the producer. The current Git-core/files candidate uses a prepared exact no-op ref transaction as the admission barrier while the architecture remains capability-based.

## 30.55 CLOSED BY ADR-080 — local native-Git versus remote/provider observation boundary

ADR-080 separates `LOCAL_GIT`, `REMOTE_GIT`, and optional `PROVIDER` authority. Local hooks never witness remote/provider mutations; local remote-tracking refs are caches; current remote refs come from admitted direct remote observation; provider-owned workflow/finalization facts come from provider surfaces only when that capability exists. Bare Git remotes remain first-class for provider-free routes.

Webhook delivery is an unreliable/reorderable transport: it may wake reconciliation and authenticated payloads may add positive provider-scoped historical evidence, but absence proves nothing, delivery identity is not semantic identity, and correctness does not generically depend on receiving a particular webhook. Cross-source composition uses exact identities/revisions rather than wall-clock order. Remote publication artifacts never inherit local managed-binding `CONTINUATION | ABANDON` semantics.

## 30.56 CLOSED BY ADR-081 — exact authoring dependency before promotion

ADR-081 permits one managed ContributionUnit to consume an exact native commit from another before the source has a PromotionGroup. The Development System explicitly selects `(source ContributionUnit, consumed OID)`; Ruu proves exact local Git lineage, anchors the object, adopts an immutable AuthoringDependency, permits otherwise legal consumer progression, and blocks unauthorized realization. Current target containment may satisfy it directly. A later qualifying source handoff may resolve it to `(PromotionGroup, source repository)` while retaining the consumed OID and entering ADR-050 restack semantics. Dirty state, ancestry-only inference, source abandonment authority transfer, and fake same-group/provider topology are forbidden.

## 30.57 OPEN — more than one independently unsatisfied authoring predecessor

The durable record can retain a finite dependency set, but an ordinary Git/provider submission has one base and ADR-050 defines one parent submission relation. The architecture has not ratified whether several unresolved source projections must wait, form a deterministic promotion DAG, use a sequence of provider surfaces, or require semantic consolidation. ADR-048 same-PromotionUnit multi-source materialization does not decide cross-group publication authority.

Until resolved, authoring/checkpointing may continue when one exact containing authoring base exists, but realization with more than one independently unsatisfied external predecessor is locally blocked.

## 30.58 OPEN — late dependency discovery and consumer refoundation

If a consumer has already authored `W` from ordinary base `M` and only then discovers that it requires `source α@A`, no accepted ADR authorizes rewriting its active worktree/ref or choosing merge/rebase/transplant/new-ContributionUnit semantics. ADR-050 applies to provider projection after handoff, not to active authoring authority.

Until resolved, later ancestry never manufactures the dependency. The Development System must surface exact reconciliation/refoundation work or start another already-authorized scope; Ruu performs no implicit rewrite.

# 31. Non-goals / things not to assume

Do not assume:

```text
convergence unit == product feature
convergence unit == task
convergence unit == provider submission
contribution unit == agent globally
invocation-principal identity matches an external producer
CWD == scope
commit == completion
native commit == managed checkpoint or handoff
exact commit OID alone == semantic authoring source identity
dirty producer worktree == consumable exact version
integration == contribution unit closure
zero commits created == nothing to do
main == universal target ref
invocation chooses/retargets the ConvergenceUnit PromotionTarget
EffectivePromotionPolicy chooses the PromotionTarget
every repo requires provider submission
every repo permits direct push
every provider-submission source is in the target repository
every promotion unit contains exactly one convergence unit
every promotion unit may contain source states from multiple repositories
every stack can be supported by every provider
every provider submission head is forever immutable
submission rewrite authority applies to internal refs
provider merge preserves source ancestry
provider draft == internal NOT_READY
review request == branch existence
development-validation execution capacity == Git mutation authority
same branch/ref identity != transition authority; re-read exact transition-local facts
security scan == secret scan
```

Do not let `ruu`:

```text
provision missing contribution-unit worktrees as a side effect
infer product semantics from branch names
infer provider-submission granularity using an LLM
silently fallback from provider submission to direct target advance
silently flatten an unsupported stack
infer an AuthoringDependency from ancestry/recency or snapshot another producer's dirty worktree
publish an abandoned source effect through its consumer
release a required dependency OID anchor while any exact obligation needs it
force-push target
rebase contribution-unit/convergence-unit refs
mutate a contribution-unit worktree that is externally protected, unknown, or not exclusively claimed by the current authoritative executor/operation
treat stale repo policy as authorization
globally block because one provider-submission/review/conflict is waiting
```

The system is a Git control plane, not a product-planning ontology.

# 32. Desired end-state

The desired system has a small number of explicit layers.

```text
HIGHER-LEVEL INTENT / ORCHESTRATION
human / agent / Turnlock / /go / script
  │
  ├── decides semantic work
  ├── may choose/reuse convergence units
  ├── explicitly selects exact source ContributionUnit/version dependencies before consumer authoring when required
  ├── closes each work-bearing implementation cohort by invoking Ruu with its exact ContributionUnit handoffs
  ├── supplies explicit authority when a later invocation revises an existing PromotionGroup
  └── does not choose stack layout; exact promotion dependency/topology is derived downstream from managed Git/promotion base facts
  │
  ▼
PRE-EDIT WORK-CONTEXT PROVISIONER
  │
  ├── repo registration/reactivation
  ├── convergence-unit ref
  ├── contribution-unit ref
  ├── isolated worktree
  └── contribution-unit mutation-authority mechanism
  │
  ▼
CONTRIBUTION UNITS EDIT IN ISOLATION
  │
  │ explicit Ruu convergence demand by any authorized principal
  ▼
COALESCED DURABLE DEMAND → ONE FENCED TOP-LEVEL Ruu EXECUTOR
  │
  ├── commit eligible contribution units
  ├── ConvergenceBase → convergence unit
  ├── convergence unit → contribution unit
  ├── contribution unit → convergence unit
  ├── internal Git/convergence validation + readiness
  ├── repo-policy refresh
  ├── promotion-unit mechanics
  ├── direct target promotion OR submission/provider-submission workflows
  ├── stack/restack mechanics on submission refs only
  ├── provider observation
  ├── recovery/cleanup
  └── fixed point across all known nonterminal managed obligations
```

Internal source-of-truth graph:

```text
ConvergenceBase
   │
   ├── convergence-unit A
   │      ├── contribution unit A1
   │      └── contribution unit A2
   │
   └── convergence-unit B
          └── contribution unit B1
```

Possible solo policy:

```text
promotion unit
→ DIRECT_TARGET_ADVANCE
→ target/main
```

Possible strict team policy:

```text
promotion unit
→ submission ref
→ provider submission
→ CI/review/merge queue
→ target/main
```

Possible stacked team policy:

```text
target
  ↑
submission P1 / PR1
  ↑
submission P2 / PR2
  ↑
submission P3 / PR3
```

Possible external contribution:

```text
source fork/submission
→ provider submission
→ upstream target
```

Critical identity boundary:

```text
contribution unit + convergence-unit refs
→ stable exact OIDs / no rewrite

submission refs
→ stable logical identity
→ exact current revision OID
→ rewrite only when policy/provider explicitly authorize

target ref
→ descendant-only direct mutation in DIRECT_TARGET_ADVANCE route
→ read-only to Ruu in PROVIDER_SUBMISSION route
```

The target state is **continuous safe progress**, not one universal branch workflow.


The desired end-state additionally guarantees:

```text
mutable WIP worktree
→ exact candidate
→ required transition-specific external fact, if any
→ authoritative managed checkpoint/state

state-preserving transition
→ exact transition-specific facts may be reused when still current

state-producing transition
→ new exact result requires its transition-local exact prerequisites

fine-grained Git claims
≠ external Development System validation compute capacity

provider-submission publication intent
→ REVIEW_NOT_REQUESTED | REVIEW_REQUESTED
```

`REVIEW_REQUESTED` carries the configured ship-ready assertion; provider draft terminology remains adapter-level.

# 33. Complete state-space consistency model

The runtime is modeled as finite per-entity/per-edge state machines plus cross-invariants.

Repository/convergence-unit/contribution unit/promotion-unit cardinality is unbounded, so this section defines **factorized local state families** rather than claiming a finite total of all possible Git graphs.

Any runtime state not representable safely by the model is `UNKNOWN_INCONSISTENT` and fails closed for destructive/promotion actions.

## 33.1 Shared repository catalog state

```text
catalog:
  UNSEEN
  KNOWN_RESOLVED
  KNOWN_LOCATION_UNRESOLVED
  UNKNOWN_INCONSISTENT
```

Transitions:

```text
UNSEEN
→ admitted by provisioning/shared-control-plane path
→ KNOWN_RESOLVED

KNOWN_RESOLVED + moved path recoverable
→ update location
→ KNOWN_RESOLVED

known identity but location unavailable
→ KNOWN_LOCATION_UNRESOLVED

ambiguous duplicate identity / contradictory repository facts
→ UNKNOWN_INCONSISTENT
```

`ruu` itself does not recursively discover `UNSEEN` repositories.

## 33.2 Derived active-convergence index membership

This state is an acceleration/cache view only; it does not define the normative global managed-obligation universe.

```text
activity_index:
  KNOWN_INACTIVE
  ACTIVE
  QUIESCENCE_CHECKING
  STALE_REBUILD_REQUIRED
```

Repository must index as `ACTIVE` if ANY recorded nonterminal managed obligation exists:

```text
contribution unit
convergence unit
promotion unit
internal push
DIRECT_TARGET_ADVANCE target advancement
provider-submission/review/check/provider workflow
merge-queue/stack/restack/update workflow
final target-integration observation/proof workflow
missing/stale/nonterminal transition-specific external prerequisite
Git in-progress/conflict
cleanup/claim
policy inconsistency
authoring-dependency adoption/resolution/object-retention/reconciliation obligation
recovery obligation
relevant UNKNOWN_INCONSISTENT state
```

Transitions:

```text
KNOWN_INACTIVE + new responsibility
→ ACTIVE

ACTIVE + apparently zero responsibilities
→ QUIESCENCE_CHECKING

QUIESCENCE_CHECKING + any responsibility found
→ ACTIVE

QUIESCENCE_CHECKING + every authoritative obligation record terminal/absent
→ KNOWN_INACTIVE

index missing/stale/inconsistent with managed obligations
→ STALE_REBUILD_REQUIRED
→ reconstruct from authoritative managed obligations
→ ACTIVE or KNOWN_INACTIVE
```

`KNOWN_INACTIVE` never suppresses an authoritative nonterminal obligation. If one exists, the index is wrong and must be repaired.

## 33.3 Effective repository promotion-policy state

```text
policy_state:
  CURRENT(policy_fingerprint)
  STALE
  MISSING
  CONTRADICTORY
  UNSUPPORTED_COMBINATION
  UNKNOWN_INCONSISTENT
```

Interpretation under ADR-043 + ADR-044:

```text
CURRENT(policy_fingerprint)
→ fingerprint is bound to the immutable PromotionTarget identity + authoritative policy-source identities/baseline
→ authoritative inputs are jointly satisfiable and all required policy dimensions are resolved for that target context
→ for a policy-sensitive promotion mutation, every mutable authoritative source needed by that mutation has just been re-observed/revalidated
→ cache age/TTL/prior success is not sufficient currentness evidence

MISSING
→ a complete effective policy cannot be derived from available authoritative inputs + built-in rules
→ merely lacking a repo policy file is NOT sufficient for MISSING

CONTRADICTORY
→ explicit authoritative constraints/facts have no common satisfying assignment
→ no silent provider/org/repo precedence fallback
→ emit exact factual contradiction descriptor outward
```

Core policy authorization includes:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION
```

Promotion context independently contains the immutable PromotionTarget and derived `SAME_REPOSITORY | CROSS_REPOSITORY` relation. Current dependency/topology is separately derived by ADR-050. ADR-051 classifies the semantic operation required by that current state. Validity examples:

```text
DIRECT_TARGET_ADVANCE + no unresolved promotion dependency
→ potentially valid if target direct mutation is supported/authorized

PROVIDER_SUBMISSION + no unresolved dependency + SAME/CROSS relation
→ provider-submission flow only if CREATE_PROVIDER_SUBMISSION is supported in that exact context and authorized

PROVIDER_SUBMISSION + exact unsatisfied predecessor dependency
→ REPRESENT_PROMOTION_DEPENDENCY is REQUIRED
→ stacked provider representation only if that operation is SUPPORTED + AUTHORIZED
→ otherwise child waits

submission revision/restack required
→ exact semantic revision/restack operation must be SUPPORTED + AUTHORIZED
→ provider-native executor result must conform to the normative core contract
```

For `CONTRADICTORY`, the externally visible diagnostic is factual and machine-readable. It contains the affected repository/obligation, conflicting dimension(s), normalized incompatible constraints/facts, and source identities/revisions/fingerprints where available. It contains no `recommended_fix`, `resolution_candidates`, ranked remediation, or suggested governance/policy mutation.

Only `CURRENT(...)` policy may authorize promotion mutation.

## 33.4 Contribution-unit provisioning state

Provisioning is outside the later convergence engine/invocation state machine. Under ADR-078, a Ruu-supplied harness/provisioner component may implement this state automatically before first managed write.

```text
REQUESTED
→ REPO_RESOLVED
→ CONVERGENCE_BASE_RESOLVED
→ PROMOTION_TARGET_BOUND
→ CONVERGENCE_UNIT_RESOLVED
→ CONTRIBUTION_UNIT_IDENTITY_RESOLVED
→ internal provisioning demand obtains the existing fenced executor when dependencies exist
→ durable selection TX-A + exact anchor + source-generation/disposition revalidation TX-B
→ AUTHORING_DEPENDENCIES_ADOPTED_OR_NONE
→ CONTRIBUTION_UNIT_REF_RESOLVED_AT_EXACT_BASE
→ WORKTREE_RESOLVED
→ EXTERNAL_MUTATION_AUTHORITY_ESTABLISHED
→ WRITE_AUTHORIZED
```

Any ambiguity:

```text
→ PROVISIONING_BLOCKED / UNKNOWN_INCONSISTENT
```

First managed edit is forbidden before `WRITE_AUTHORIZED`.

## 33.5 `ruu` convergence demand and global sweep scope

Durable demand state is conceptually:

```text
requested_generation: monotonic
processed_generation: monotonic, <= requested_generation

requested_generation > processed_generation
→ outstanding convergence demand exists
```

The scope of an executed sweep is not an active-repository list:

```text
scope = all known nonterminal managed obligations
```

`ACTIVE_CONVERGENCE_SET` may accelerate repository lookup but cannot exclude an authoritative obligation. For each relevant obligation/repository, the executor resolves managed identity and refreshes the exact policy/Git/remote/provider facts required by that obligation.

CWD, caller identity, trigger generation, age, repository activity-index membership, ContributionUnit, ConvergenceUnit, PromotionUnit, or invocation reason never narrow the sweep.

At the current fixed point, the executor may advance `processed_generation` only through the demand snapshot covered by that sweep, then MUST re-read `requested_generation` before releasing top-level ownership.

## 33.6 Invocation principal / convergence-trigger state

```text
principal_kind:
  HUMAN
  CODING_AGENT
  SCRIPT
  TURNLOCK
  GO
  AUTOMATION
  OTHER_AUTHORIZED
  UNAUTHORIZED
```

```text
UNAUTHORIZED
→ convergence demand rejected

authorized kind
→ may signal/advance convergence demand
→ does not own a caller-specific queued job
→ does not acquire ContributionUnit mutation authority by invoking
```

Concurrent authorized triggers may coalesce. External Control Plane authority changes are durable state independent of the trigger.

## 33.7 External ContributionUnit mutation-access state

For each existing ContributionUnit editing surface:

```text
mutation_access:
  PROTECTED_EXTERNAL
  TRANSFERABLE_TO_RUU
  TRANSFERABLE_GENERAL
  UNKNOWN
```

Authorization:

```text
PROTECTED_EXTERNAL
→ protected

TRANSFERABLE_TO_RUU
→ durable External Control Plane handoff to the Ruu coordination domain
→ no external writer may mutate while the handoff remains current
→ current authoritative executor may attempt exclusive claim

TRANSFERABLE_GENERAL
→ no external producer retains mutation authority
→ no external writer may mutate while the handoff remains current
→ current authoritative executor may attempt exclusive claim under ordinary authorization/policy

UNKNOWN
→ fail closed
```

No heartbeat/process/session/liveness inference is performed by `ruu`. Mutation access is not indexed by invocation/trigger identity. Under ADR-064, transferability used to offer dirty work for checkpointing establishes a frozen no-external-mutation interval until safe release/revocation/recovery.

## 33.8 Repository-local ContributionUnit state

```text
lifecycle:
  OPEN
  CLOSED

topology/membership:
  KNOWN
  UNKNOWN_INCONSISTENT

latest_authoritative_managed_checkpoint:
  ABSENT
  EXACT_OID_REACHABLE
  EXACT_OID_UNRECOVERABLE

editing_surface:
  PRESENT_CLEAN
  PRESENT_DIRTY
  PRESENT_CONFLICT_OR_IN_PROGRESS
  ABSENT

worktree_claim (only when editing surface exists):
  NONE
  CURRENT_EXECUTOR_OPERATION
  INCOMPATIBLE_OTHER_OPERATION_OR_RECOVERY

convergence-unit↔ContributionUnit exact-state relation:
  UP_TO_DATE
  CONVERGENCE_UNIT_AHEAD
  CONTRIBUTION_UNIT_AHEAD
  DIVERGED
  CONFLICT_BLOCKED
  UNKNOWN_INCONSISTENT
```

ContributionUnit lifecycle is distinct from mutation access, producer/runtime/turn state, trigger state, and editing-artifact presence. The External Control Plane is authoritative for `OPEN | CLOSED`; `ruu` consumes/revalidates those states.

```text
OPEN   → may still contribute to current convergence scope
CLOSED → no further contribution; later work requires a new ContributionUnit
```

An absent branch/worktree does not close or erase the logical unit. If an unresolved authoritative checkpoint OID remains reachable, upward convergence can continue from that exact state without the producer worktree. If a still-required OID is unrecoverable, the path becomes `BLOCKED_MISSING_MANAGED_STATE`/recovery.

## 33.9 Contribution-unit-worktree mutation authority

```text
topology UNKNOWN
→ blocked

claim INCOMPATIBLE_OTHER_OPERATION_OR_RECOVERY
→ defer/recover

mutation_access PROTECTED_EXTERNAL
→ protected

mutation_access UNKNOWN
→ fail closed

mutation_access TRANSFERABLE_TO_RUU / TRANSFERABLE_GENERAL
+ claim NONE
→ claimable by the current authoritative executor

claim CURRENT_EXECUTOR_OPERATION
+ mutation_access transferable
+ transferability revalidated under the same authority arbitration
→ exclusive ContributionUnit-worktree mutation authority
```

A clean worktree does not weaken external mutation protection. A Development System that needs to resume semantic authoring before claim acquisition must first revoke transferability and restore external mutation authority; after a current executor has acquired the exclusive claim, external reacquisition waits until that claim/effect has reached a safe release or recovery boundary. Any prior semantic readiness decision is stale after legitimate resumed mutation.

## 33.10 Managed checkpoint adoption and commit collection

```text
editing_surface ABSENT
→ no filesystem checkpoint can be created
→ evaluate any already-existing exact managed checkpoint obligation instead

UNKNOWN topology
→ blocked

PRESENT_CONFLICT_OR_IN_PROGRESS
→ recover first

PRESENT_CLEAN + no frozen work-bearing handoff
→ no managed checkpoint adoption

PRESENT_CLEAN + exact frozen handoff + current exact tip K
+ K canonically descends prior checkpoint/admitted base
+ current binding/claim/topology/CAS guards hold
→ adopt K as authoritative managed checkpoint
→ create no commit

PRESENT_DIRTY + PROTECTED_EXTERNAL
→ protected

PRESENT_DIRTY + mutation_access UNKNOWN
→ fail closed

PRESENT_DIRTY + TRANSFERABLE_TO_RUU / TRANSFERABLE_GENERAL
→ frozen external-write interval is already in force
→ acquire exclusive worktree claim
→ construct exact ADR-059 whole-surface CheckpointCandidate (P,T)
→ immediately revalidate parent/surface/authority/structural assumptions under the same claim
→ if stale/changed: do not commit the old candidate; re-observe/recover as required
→ otherwise commit K with parent(K)=P and tree(K)=T
→ record resulting exact authoritative managed checkpoint OID
```

The Development System decides when the current editing surface is semantically ready to be offered/transferred for Git progression. That decision is not represented by a generic validation certificate inside `ruu`; its identity is preserved mechanically by the ADR-064 frozen handoff. If semantic authoring resumes before claim acquisition, transferability is revoked first and readiness must be re-established before a later offer. If `ruu` already owns the claim, external mutation waits for safe release/recovery.

## 33.11 ContributionUnit lifecycle / exact-state continuity

```text
OPEN
→ may continue producing later contribution

CLOSED
→ no further contribution production
→ latest authoritative managed checkpoint, if unresolved, still converges normally

editing artifacts absent + no unresolved exact checkpoint
→ no-op

editing artifacts absent + unresolved exact checkpoint reachable
→ continue exact-state convergence without producer worktree

editing artifacts absent + unresolved exact checkpoint unrecoverable
→ BLOCKED_MISSING_MANAGED_STATE / recovery-data-loss
```

No transition from `CLOSED` to `OPEN` exists. `ruu` does not perform branch/worktree deletion or infer remote deletion/local recreation from artifact absence.

## 33.12 Convergence-unit lifecycle and contribution membership

Processing lifecycle:

```text
ABSENT
→ ACTIVE
→ READY_INTERNAL(OID)
→ PROMOTION_BOUND(OID)
→ PROMOTED        # only after all relevant ship obligations are terminally settled and semantic reopen is no longer possible
→ RETIRED         # only after correctness-critical recovery/resource obligations are clear
```

ADR-054 explicitly forbids deriving either ConvergenceUnit `PROMOTED` or `RETIRED` from one repository-local `PromotionUnit PROMOTED`. During cross-repository partial progress, a locally promoted exact snapshot may coexist with a still-reactivatable `PROMOTION_BOUND` ConvergenceUnit because the higher-level PromotionGroup remains nonterminal.

Contribution membership while the convergence scope is mutable:

```text
OPEN
→ new ContributionUnits may be attached
→ checkpointing/synchronization/integration continue
→ READY_INTERNAL forbidden

SEALED
→ no new ContributionUnit attachment for the current readiness attempt
→ existing contribution obligations continue resolving
→ READY_INTERNAL may be evaluated
```

Side transitions:

```text
ACTIVE / READY_INTERNAL
+ explicit current External-Control-Plane lineage disposal
+ no live PromotionGroup requires the lineage
→ ABANDONING → RETIRED after recovery/resource guards

PROMOTION_BOUND
+ every relevant ship that would otherwise require delivery has an applicable terminal non-delivery disposition
+ no replacement/nonterminal group or current authoring/reconciliation demand remains
+ required lineage-disposal authority is current
→ ABANDONING → RETIRED after recovery/resource guards

READY_INTERNAL / PROMOTION_BOUND
+ explicit semantic/new internal work while the lineage is still semantically open
→ ACTIVE + membership OPEN
→ prior exact readiness/source binding stale

PROMOTED / RETIRED
+ later semantic work
→ existing ConvergenceUnit MUST NOT reopen
→ declare a new ConvergenceUnit/new ship lineage
```

`READY_INTERNAL(OID)` requires:

```text
membership SEALED
zero OPEN ContributionUnits
for every CLOSED ContributionUnit, latest authoritative managed checkpoint (if any) fully resolved into exact OID
zero unknown/orphan ContributionUnit membership/state
zero BLOCKED_MISSING_MANAGED_STATE or unresolved internal synchronization/integration/reconciliation/conflict/recovery obligation
transition-local exact prerequisites for that OID
internal fixed point reached for exact OID
```

No second semantic-readiness evidence class exists at this layer. Historical terminal/resolved ContributionUnit ref retention alone does not block readiness.

## 33.13 Convergence-unit provisioning

```text
ABSENT_EXPECTED + provisioning claim
→ create convergence-unit ref from freshly observed configured ConvergenceBase
→ ACTIVE + membership OPEN

ABSENT_EXPECTED + competing provisioning
→ loser refreshes/reuses authoritative unit

PRESENT
→ reuse exact identity/ref

AMBIGUOUS/UNKNOWN
→ provisioning blocked
```

This state machine belongs to the pre-edit provisioner.

## 33.14 Contribution unit creation

Creation/membership authority belongs to the External Control Plane. `ruu` consumes the declared topology.

```text
convergence unit ABSENT
→ provision convergence unit first

convergence unit ACTIVE + membership OPEN
→ External Control Plane may create/bind a new ContributionUnit if topology/authority valid

convergence unit ACTIVE + membership SEALED
→ new ContributionUnit attachment forbidden until explicit membership reopen to OPEN

READY_INTERNAL / PROMOTION_BOUND
→ explicit semantic reopen to ACTIVE + membership OPEN before new ContributionUnit
→ prior exact readiness becomes stale
→ existing immutable PromotionUnit definition remains unchanged; any new exact member selection has a different content address

PROMOTED / RETIRED / ABANDONING
→ ContributionUnit creation forbidden; later semantic work requires a new ConvergenceUnit identity/new ship lineage

UNKNOWN
→ fail closed
```

A ContributionUnit's `convergence_unit_id` membership never changes for that identity. Experimental/alternative work that must remain isolated is provisioned against a distinct ConvergenceUnit.

## 33.15 `ConvergenceBase → convergence-unit` synchronization

Allowed only while internal convergence unit is mutable (`ACTIVE`, or another explicitly authorized internal-reopen/update state).

Graph relation:

```text
UP_TO_DATE
→ no-op

TARGET_AHEAD
→ intended result = exact target OID
→ require all exact transition-local prerequisites
→ reuse/re-read transition-specific exact facts as applicable
→ FF convergence unit to target

CONVERGENCE_UNIT_AHEAD
→ no downward sync

DIVERGED
→ materialize exact merge ConvergenceBase + convergence-unit in isolated integration state
→ deterministic clean result with a missing transition-local prerequisite: authoritative convergence-unit ref unchanged
→ deterministic clean result with current exact required evidence: advance convergence-unit ref under ordinary guards
→ semantic conflict: authoritative convergence-unit ref unchanged + RECONCILIATION_REQUIRED(exact inputs/conflict evidence)

UNKNOWN
→ fail closed
```

Internal convergence-unit ref remains descendant-only/no-rebase.

After `READY_INTERNAL(OID)` is bound as promotion source, ordinary target movement does not silently rewrite that source.

## 33.16 `convergence-unit → contribution unit` synchronization

Requires contribution-unit-worktree mutation authority.

```text
UP_TO_DATE / CONTRIBUTION_UNIT_AHEAD
→ no-op downward

CONVERGENCE_UNIT_AHEAD
→ intended result = exact convergence-unit OID
→ require all exact transition-local prerequisites
→ reuse/re-read transition-specific exact facts as applicable
→ FF contribution unit

DIVERGED
→ materialize no-authoritative-move exact merge candidate under exclusive authority
→ deterministic clean result with a missing transition-local prerequisite: authoritative managed checkpoint unchanged
→ deterministic clean result with current exact required evidence: commit/adopt exact merge result
→ semantic conflict: authoritative state unchanged + RECONCILIATION_REQUIRED(exact inputs/conflict evidence)

DIRTY
→ §33.10 checkpoint first

CONFLICT
→ RECONCILIATION_REQUIRED; no authoritative adoption

UNKNOWN
→ fail closed
```

No rebase.

## 33.17 `contribution unit → convergence unit` integration

No separate integration-readiness/release state exists. A valid authoritative managed checkpoint of any `OPEN` or `CLOSED` ContributionUnit is an eager upward-convergence candidate.

Requires:

```text
convergence unit ACTIVE
exact contribution unit tip = valid authoritative managed checkpoint
exact convergence-unit tip
immutable known ContributionUnit→ConvergenceUnit membership
convergence-unit claim
known topology
no conflict
```

Then:

```text
convergence-unit tip ancestor contribution unit tip
→ exact resulting state = contribution unit tip
→ require all exact transition-local prerequisites
→ if exact evidence current: reuse
→ else leave convergence-unit ref unchanged and surface the missing transition-local prerequisite
→ when satisfied, FF convergence unit

otherwise
→ synchronize contribution unit first
→ refresh tips/topology/evidence
→ retry
```

An `OPEN` ContributionUnit may integrate repeatedly as later checkpoints are produced. No upward merge/non-FF update.

## 33.18 Exact internal ancestry relation

For parent `P`, child `C`:

```text
P == C
→ UP_TO_DATE

P ancestor C
→ CHILD_AHEAD

C ancestor P
→ PARENT_AHEAD

neither
→ DIVERGED

merge conflict
→ CONFLICT_BLOCKED

unknown facts
→ UNKNOWN_INCONSISTENT
```

Git determines relation mechanically; orchestration determines authorization.

## 33.19 Internal history mutation state

For contribution-unit/convergence-unit refs:

```text
NOOP
FF_EXISTING_DESCENDANT
FF_NEW_MERGE_DESCENDANT
DELETE_RETIRED_REF   # only after ADR-054 GC eligibility + explicit retention policy; built-in v1 policy KEEP does not auto-delete
```

are the only normal mutation classes. `RETIRED` never itself implies physical deletion.

Forbidden:

```text
REBASE
AMEND
BACKWARD_RESET
NON_FAST_FORWARD_UPDATE
HISTORY_REWRITE
FORCE_PUSH
FORCE_WITH_LEASE_PUSH
```

## 33.20 Promotion-unit declaration/source binding

```text
promotion_definition:
  ABSENT
  DEFINED_EXACT
  INVALID_REFERENCE
  IDENTITY_MISMATCH
  UNKNOWN_INCONSISTENT
```

`DEFINED_EXACT` means:

```text
members = non-empty unique unordered Set<ExactConvergenceStateRef>
all members share exactly one authoritative source repository_id
promotion_unit_id = content address of the canonical immutable member set
stored definition exactly reproduces that identity
```

Same canonical repository-local member set always resolves to the same PromotionUnit; changing any exact member state creates a different PromotionUnit. A cross-repository member set is structurally invalid. Lifecycle/topology/target/mode/submission revision/semantic task identity are not part of the definition. Promotion topology is represented separately.

`ruu` does not synthesize `DEFINED_EXACT` from code semantics.

## 33.21 Promotion-unit readiness

```text
WAITING_FOR_SOURCES
READY_FOR_PROMOTION
BLOCKED_CONFLICT
BLOCKED_POLICY
STALE
UNKNOWN_INCONSISTENT
```

`READY_FOR_PROMOTION` requires:

```text
definition DEFINED_EXACT
all exact member ConvergenceUnit states internally ready/bound
effective policy CURRENT
target/provider observations current
all carried AuthoringDependencies resolved/internal/target-satisfied
current derived topology dependencies compatible
no conflict/unknown binding/recovery condition
```

## 33.21A Repository-local candidate materialization

For a repository-local PromotionUnit `P`:

```text
MATERIALIZATION_WAITING_BASE
MATERIALIZATION_READY
MATERIALIZING
MATERIALIZATION_CONFLICT
CANDIDATE_READY
STALE
UNKNOWN_INCONSISTENT
```

Exact inputs:

```text
promotion_unit_id = immutable exact repository-local source set
exact_effective_base_oid = B
raw authoring dependency may supply immutable consumed base B for owned-state materialization but never realization authority
materialization_contract_fingerprint = V
```

Execution semantics:

```text
source set S
→ ancestry-maximal reduction relative to B
→ canonical retained-source order
→ ancestry-aware pairwise full two-head merge fold under V
→ reuse exact existing commit if the fold requires no synthesis
  OR final tree T → canonical synthetic final commit C
```

Final candidate guards:

```text
B ancestor-or-equal C
∀ s ∈ S: exact_source_oid(s) ancestor-or-equal C
tree(C) == canonical fold result under V
candidate OID/metadata reproduce from exact inputs under V
```

If a fold step requires semantic conflict authoring:

```text
→ MATERIALIZATION_CONFLICT
→ ADR-040 RECONCILIATION_REQUIRED bound to exact P/B/V/current fold evidence
→ no authoritative candidate adoption
```

A newly created `C` remains an attempt-scoped exact candidate until its promotion/submission transition-local prerequisites hold; no generic development-validation wait state exists. Transient pairwise fold commits are not separately authoritative managed states.

If `B`, any PromotionUnit source binding, or any correctness-relevant MaterializationContract factor changes before adoption/progression, the prior materialization is stale and is recomputed/revalidated from current state.

## 33.21B DIRECT target advancement

After exact candidate `C` satisfies the current DIRECT_TARGET_ADVANCE transition-local prerequisites, DIRECT_TARGET_ADVANCE route records/reconciles:

```text
DirectTargetAdvanceOperation {
  promotion_target_repository_id
  target_ref
  expected_old_oid = B
  candidate_oid = C
  promotion_unit_id
  current policy/capability fingerprint(s)
  operation/attempt identity
}
```

An attempt-scoped recovery ref/anchor in a non-business `ruu` namespace keeps `C` reachable. The anchor is not a target, submission, ConvergenceUnit, or ContributionUnit ref and is never parsed for semantics.

Execution is permitted only after immediate current-state revalidation and the semantic backend operation:

```text
AdvanceTargetFF(PromotionTarget.ref, expected_old=B, new=C)
```

which must be atomic with respect to the exact-old comparison and may succeed only as a fast-forward. Candidate ancestry is immutable Git object truth; target expected-old/policy/claim facts are current observations/authority and are revalidated at the mutation boundary.

Observation/adoption truth table:

```text
target == B              → not realized
target == C              → realized
C ancestor target        → realized, followed by later target advancement
anything else            → not proven; stale/drift reconciliation
```

Only after durable adoption/recovery sufficiency may the physical recovery anchor become cleanup-eligible.

## 33.22 Promotion policy + contextual capability validation

Canonical classification under ADR-050/ADR-051:

```text
no unsatisfied predecessor + DIRECT_TARGET_ADVANCE policy path
→ DIRECT_TARGET_ADVANCE_FLOW if exact target-advancement operation is supported/authorized

no unsatisfied predecessor + provider-submission policy path
→ PROVIDER_SUBMISSION_FLOW if CREATE_PROVIDER_SUBMISSION is supported/authorized in the exact SAME/CROSS repository context

unsatisfied predecessor + provider-submission policy path
→ REPRESENT_PROMOTION_DEPENDENCY is REQUIRED
→ STACK_FLOW only if the exact contextual operation is SUPPORTED + AUTHORIZED
→ otherwise localized wait / UNSUPPORTED_TOPOLOGY / policy block

required submission revision/restack
→ exact revision/restack semantic operation must be SUPPORTED + AUTHORIZED
→ executor output must satisfy the normative contract before adoption
```

Derived topology is never changed merely to make an unsupported provider operation executable.

Any `MISSING/STALE/CONTRADICTORY` policy:

```text
→ promotion blocked
```

## 33.23 DIRECT_TARGET_ADVANCE realization

State:

```text
READY_FOR_PROMOTION
→ DIRECT_PREPARING
→ DIRECT_TARGET_ADVANCING
→ PROMOTED
```

Guards:

```text
policy CURRENT + target_realization_route = DIRECT_TARGET_ADVANCE
every AuthoringDependency target-satisfied or internal to the same group
zero unsatisfied promotion predecessors
target mutation authorized
exact target T
exact candidate C
promotion claim held
all transition-local exact prerequisites for C
promotion-specific candidate validation exact
```

Transition:

```text
ADR-048 materialize exact C from exact PromotionUnit + effective target base T
→ re-read/reuse any transition-specific exact facts and stop only if a required local prerequisite is missing

T == C
→ already promoted

T ancestor C
→ create/retain attempt-scoped recovery anchor for exact C
→ execute ADR-052 AdvanceTargetFF(target, expected_old=T, new=C)
→ observe authoritative target history proving C realized
→ PROMOTED

otherwise
→ stale/not directly promotable
→ refresh/rebuild/revalidate/rebind evidence
```

Forbidden:

```text
non-FF target update
target rewrite/rebase
target force push
provider-submission-policy bypass
candidate missing a required transition-local prerequisite
```

## 33.24 Submission identity/ref class

Provider-submission promotion uses:

```text
submission_id
publication_episode_id
submission_ref               # scoped to current episode
provider_submission_identity # scoped to current episode
submission_class:
  IMMUTABLE
  REWRITEABLE
submission_revision          # monotonic across logical submission
current_submission_head
```

```text
IMMUTABLE
→ ordinary FF publication only

REWRITEABLE
→ policy/provider-authorized exact revision transitions may be non-FF
```

Internal source refs remain distinct in authority.


Review-request intent is an independent submission/publication axis:

```text
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

It does not change internal convergence-unit identity or ref class.

## 33.25 Independent provider-submission lifecycle

Nominal review-requested path:

```text
READY_FOR_PROMOTION
→ ADR-048 exact candidate
→ validate exact submission/review-intent/policy/provider prerequisites
→ SUBMISSION_PREPARING
→ SUBMISSION_PUBLISHING
→ REVIEWING_BOUND(rev,H,REVIEW_REQUESTED)
```

Exceptional no-review-request publication:

```text
policy-authorized publication need
→ ADR-048 exact candidate
→ validate exact submission/review-intent/policy/provider prerequisites
→ SUBMISSION_PREPARING
→ SUBMISSION_PUBLISHING
→ PUBLISHED_BOUND(rev,H,REVIEW_NOT_REQUESTED)
```

The exact submission revision must satisfy the current transition-local submission/review-intent/policy/provider prerequisites before either provider-visible publication state.

No-projection default under ADR-062:

```text
REVIEW_REQUESTED not established
+ no explicit current authority/need for early REVIEW_NOT_REQUESTED publication
→ provider submission lifecycle remains NONE
→ no draft/provider object is created merely as an internal workflow marker
```

PublicationEpisode rule:

```text
current episode nonterminal + authorized new exact revision
→ update same episode/provider submission under exact expected-old guards

current episode terminal + same logical submission still requires a new exact publication
+ PromotionGroup remains nonterminal
→ create distinct ADR-055 PublicationEpisode/ref/provider submission under first-publication guards
```

A terminal episode is never reopened or revised.

Provider transitions may include:

```text
OPEN_CHECKS_PENDING
OPEN_REVIEW_PENDING
APPROVED
UPDATE_REQUIRED
CHANGES_REQUESTED
MERGE_QUEUED
MERGED
CLOSED_UNMERGED
UNKNOWN_INCONSISTENT
```

`OPEN_REVIEW_PENDING`/approval semantics apply only when review is actually requested.

Ordinary review/check waits are localized.

## 33.26 Authoring and promotion-dependency lifecycle

For each exact selected authoring relation:

```text
authoring_dependency:
  RAW_AUTHORING_SOURCE(source_contribution_unit_id, consumed_exact_oid)
  RESOLVED_PROMOTION_PROJECTION(parent_group_id, source_repository_id, consumed_exact_oid)
  INTERNAL_TO_SAME_GROUP(group_id, source_repository_id, consumed_exact_oid)
  SATISFIED_BY_TARGET(consumed_exact_oid, proof_ref)
  RECONCILIATION_REQUIRED(reason, consumed_exact_oid)
  UNKNOWN_INCONSISTENT
```

Adoption requires one immutable source/consumer/OID identity plus a reachable REQUIRED anchor. `consumed_exact_oid` never changes. Dirty state is not representable.

Reconciliation precedence is:

```text
fresh authoritative target contains consumed_exact_oid
→ SATISFIED_BY_TARGET

same immutable group authoritatively contains source + consumer handoffs
+ source exact frozen checkpoint S contained A before downward synchronization
+ group-local state incorporates S and consumer handoff
→ INTERNAL_TO_SAME_GROUP

first qualifying handoff of the same source ContributionUnit after durable selection TX-A
+ exact frozen/adopted source checkpoint S contained A before downward synchronization
+ group-local K incorporates S
+ source and consumer immutable PromotionTargets exactly equal
+ source/group disposition authorizes realization
→ RESOLVED_PROMOTION_PROJECTION while retaining A

source loses realization path before satisfaction
→ RECONCILIATION_REQUIRED

qualifying source handoff exists but immutable PromotionTargets differ
→ RECONCILIATION_REQUIRED(TARGET_INCOHERENT_AUTHORING_DEPENDENCY)

ambiguous attribution, cycle, missing object, or contradictory identity
→ UNKNOWN_INCONSISTENT
```

For repository-local promotion `P`, the later ADR-050 projection state is:

```text
promotion_dependency:
  NONE
  UNSATISFIED(parent_submission_id, parent_exact_head, authoring_dependency_id)
  SATISFIED_BY_TARGET
  STALE
  UNKNOWN
```

`UNSATISFIED` is derived only after durable semantic provenance identifies the source projection, or from another already-authoritative promotion relation. It is then reconciled from exact effective-base/predecessor/target state; it is not caller-authored stack intent. A valid adopted `SATISFIED_BY_TARGET` proof is terminal historical authority even after later target drift or source abandonment, while every later consumer realization still revalidates its own current route/target/policy/CAS guards. Eligibility for provider exposure requires `NONE | SATISFIED_BY_TARGET`, or exactly one current supported/authorized representation of the unsatisfied dependency. More than one independently unsatisfied predecessor remains locally blocked under open item 30.57.

Predecessor change/merge may produce:

```text
RESTACK_NOT_REQUIRED
RESTACK_REQUIRED
RESTACK_BLOCKED
DEPENDENCY_SATISFIED_BY_TARGET
```

Dependency is never inferred from branch/task/session names or arbitrary ancestry detached from adopted source identity and exact base lineage.

## 33.27 Submission revision/restack lifecycle

```text
UNMATERIALIZED
→ MATERIALIZING
→ require only the exact transition-local prerequisites of the revision/publication transition
→ BOUND_IMMUTABLE(rev,H)
or
→ BOUND_REWRITEABLE(rev,H)
```

For an authorized dependency restack:

```text
BOUND_REWRITEABLE(rev,H)
+ RESTACK_REQUIRED
+ immutable owned anchor (B0,C0)
+ current new predecessor/base B1
→ REVISING
→ exact three-way state transplant: base=B0, ours=B1, theirs=C0
→ produce exact H2 over B1 under RestackContract
→ promotion/submission-specific validate
→ expected-old guarded ADR-049 submission-ref publication
→ provider head == H2
→ revision := rev + 1
→ BOUND_REWRITEABLE(rev+1,H2)
```

A later restack uses the current immutable owned child anchor again, not the prior restacked provider head as semantic input.

If the old revision was `REVIEW_REQUESTED` and the revision change invalidates the ship-ready/submission-author gate:

```text
new revision intent
→ REVIEW_NOT_REQUESTED
until exact gate is re-established
```

For immutable:

```text
authorized update that can be FF/descendant
→ exact new result must satisfy current transition-local publication prerequisites
→ publish new exact head
→ new bound revision

required non-FF restack
→ BLOCKED_POLICY unless submission class can explicitly transition under policy
```

Internal convergence-unit OIDs do not change.

## 33.28 submission/provider lifecycle

```text
NONE
CREATING_OR_UPDATING
OPEN_CHECKS_PENDING
OPEN_REVIEW_PENDING
APPROVED
UPDATE_REQUIRED
CHANGES_REQUESTED
RESTACK_REQUIRED
MERGE_QUEUED
MERGED
CLOSED_UNMERGED
UNKNOWN_INCONSISTENT
```

Canonical meanings:

```text
UPDATE_REQUIRED
→ provider-facing update workflow
→ no implicit contribution unit creation

RESTACK_REQUIRED
→ exact dependency-restack workflow under ADR-050
→ no internal source rewrite; reproject immutable owned child state onto current new predecessor/base

CHANGES_REQUESTED
→ ADR-053 durable review-correction demand
→ External Control Plane correction continuation may provision new ContributionUnits from the exact reviewed/group state
→ resulting work-bearing invocation is `REVISE_EXISTING_GROUP(G, authority_ref)`

MERGE_QUEUED
→ provider-governed finalization is in progress/frozen; Ruu continues observation and may drive any machine-authorized queue/finalization operation

MERGED
→ observe target result
→ current PublicationEpisode becomes terminal when exact outcome/recovery is adopted
→ promotion may complete; later same-logical-submission work uses a new ADR-055 episode rather than reopening this provider submission
```


Review-request intent gates provider review semantics:

```text
REVIEW_NOT_REQUESTED
→ provider submission may exist and checks may run
→ no formal ship-ready review request is asserted

REVIEW_REQUESTED
→ exact current revision/head must satisfy configured submission-author gate
→ provider review lifecycle may proceed

material exact-head revision that invalidates ship-ready assertion
→ REVIEW_NOT_REQUESTED until gate re-established, unless provider/policy semantics explicitly prove continued validity
```

## 33.29 Exact submission-head binding and drift

For current revision:

```text
BOUND(rev,H)
```

requires applicable exact agreement:

```text
local submission ref == H
remote submission ref == H
provider submission head == H
```

Ordinary immutable review:

```text
target moves
→ H remains candidate
→ no automatic head mutation
```

Authorized rewriteable revision:

```text
H → H2
only through explicit REVISING transition
```

Unexpected movement:

```text
remote/provider head != expected H
without authorized transition
→ DRIFTED
→ fail closed/recover
```

## 33.30 Semantic reopen versus provider update/restack

Distinct events:

```text
CHANGES_REQUESTED
→ ensure/refresh one exact ADR-053 ReviewCorrectionDemand
→ provider hook or any global sweep may discover the same demand idempotently
→ External Control Plane restores or starts a correction continuation session
→ session may discover affected existing ConvergenceUnit scope(s) while working
→ relevant existing ConvergenceUnit(s) may return to ACTIVE with membership OPEN
→ every implementation write uses a newly provisioned ContributionUnit/writer surface
→ same immutable PromotionGroup may later resolve to a new exact PromotionUnit
→ if current PublicationEpisode is open, revise the same ADR-049 provider submission
→ if prior episode is terminal and the same logical submission still needs publication, ADR-055 creates a new episode/provider submission

UPDATE_REQUIRED
→ provider-facing base/update workflow
→ no implicit contribution unit authority

RESTACK_REQUIRED
→ exact provider-facing dependency reprojection under ADR-050
→ no internal contribution unit authority; conflict requiring authoring routes to RECONCILIATION_REQUIRED

unexpected drift
→ recovery, not update authorization
```

## 33.31 Provider target-integration / merge-queue finalization

Provider finalization is a mechanical/governance progression toward the immutable PromotionTarget, not a second semantic promotion decision.

Conceptual states include:

```text
INTEGRATION_NOT_YET_ALLOWED
INTEGRATION_READY
INTEGRATION_REQUESTING
QUEUED_FROZEN(rev,H)
AWAITING_EXPLICIT_HUMAN_FINALIZER
RELEASED
PROVIDER_FINALIZED
TARGET_REALIZATION_UNPROVEN
TARGET_REALIZATION_PROVEN
UNKNOWN
```

Rules:

```text
actual current provider/governance prerequisite missing
→ INTEGRATION_NOT_YET_ALLOWED

all required current prerequisites satisfied
+ provider target-integration operation REQUIRED
+ operation SUPPORTED
+ operation AUTHORIZED for machine execution
→ INTEGRATION_READY
→ Ruu requests/enables/executes the provider finalization operation
→ INTEGRATION_REQUESTING / QUEUED_FROZEN / PROVIDER_FINALIZED as provider reports

explicit authoritative human-finalizer requirement unsatisfied
→ AWAITING_EXPLICIT_HUMAN_FINALIZER
→ localized wait
```

There is no default `WAIT_FOR_MANUAL_MERGE_CLICK` state.

While queued/finalizing:

```text
incompatible local submission mutation forbidden
```

Provider release/ejection may transition to:

```text
REVIEWING_BOUND
UPDATE_REQUIRED
RESTACK_REQUIRED
```

as reported/derived from current provider state.

`PROVIDER_FINALIZED` is not terminal promotion proof. ADR-066 requires the complete provider route chain for exact candidate `C`:

```text
1. prove exact current submission projection:
     C → H
   where H is the exact submitted revision/head

2. provider finalization observation must bind:
     exact submission / PublicationEpisode
     exact submitted revision = H
     exact PromotionTarget = T
     status = COMPLETED
     exact final result OID = R

3. fresh Git observation must prove:
     O == R
     OR R ancestor-of O

   → TARGET_REALIZATION_PROVEN(PROVIDER_ROUTE, C→H→R→O)

4. candidate ancestry in O without steps 1..3
   → inclusion observed but required provider route unproven
   → no PromotionUnit terminal adoption

5. any projection/finalization mismatch, missing exact H/R, or R absent from T history
   → TARGET_REALIZATION_UNPROVEN
```

Provider queue/merge-group synthetic commits are not final result proof unless they are the exact final `R` established by the provider and observed in target. `ruu` does not require generic diff/patch/program-semantic equivalence across `C`, `H`, and `R`.

## 33.32 Remote publication by ref class

### CONTRIBUTION_UNIT / CONVERGENCE_UNIT

```text
EQUAL
→ no-op

LOCAL_AHEAD + expected remote
→ FF push

REMOTE_AHEAD/DIVERGED/expectation mismatch
→ refresh/reconcile

UNKNOWN
→ fail closed
```

### SUBMISSION IMMUTABLE

```text
FF/expected-state only
```

### SUBMISSION REWRITEABLE

```text
FF normally
authorized revision may use exact expected-old guarded non-FF update
```

### TARGET

```text
PROVIDER_SUBMISSION route
→ direct push forbidden

DIRECT_TARGET_ADVANCE route
→ FF/expected-old only
```

## 33.33 Cross-repository provider-submission publication

State includes exact:

```text
source_repository
source_submission_ref
PromotionTarget.target_repository_id
PromotionTarget.target_ref
provider submission identity
submission revision/head
review-request intent
```

Provider-visible publication requires the exact current submission revision to satisfy its current publication-intent/policy/provider rules.

If source/target relationship changes unexpectedly:

```text
→ UNKNOWN_INCONSISTENT
```

Cross-repo does not change internal convergence-unit semantics.

## 33.34 Higher-level multi-repository promotion

For one PromotionGroup/logical ship spanning N repositories, ADR-047 yields one repository-local PromotionUnit track per represented source repository. Each track can be:

```text
NOT_READY
READY
IN_PROGRESS
PROMOTED
BLOCKED
UNKNOWN
```

Higher-level aggregate:

```text
NONE_PROMOTED
PARTIALLY_PROMOTED
ALL_PROMOTED
UNKNOWN_INCONSISTENT
```

No atomic cross-repository rollback is implied. `PARTIALLY_PROMOTED` is ordinary nonterminal progress for ADR-054 ConvergenceUnit semantic closure: a locally successful repository projection does not by itself promote/retire its source ConvergenceUnit or authorize compensation. ADR-055 adds a separate logical settlement dimension:

```text
OPEN / NONTERMINAL
ALL_PROMOTED       # terminal successful settlement of current exact mapping
COMPENSATED        # explicit terminal semantic compensation after required forward effects
CANCELLED          # terminal managed withdrawal after authoritative managed-branch abandonment; no pre-abandon realized effect may be erased
```

Active `CrossRepositorySettlementDemand` remains nonterminal managed work. A partial group with already-realized pre-abandonment effects cannot erase that history by becoming `CANCELLED`; ADR-055 settlement applies. ADR-071/074/075 make a positively proven terminal cessation of the currently bound managed authoring line the ordinary withdrawal authority for still-unrealized work, with a normalized native witness durably captured before binding-change linearization. Current-disposition causal fencing prevents new incompatible managed realization, while unresolved pre-abandonment committed/uncertain effects remain recovery-visible until classified.

## 33.35 Exact binding of transition-specific facts/evidence

Evidence/fact classes that remain in the architecture are transition-specific:

```text
convergence-unit readiness evidence
→ exact convergence-unit OID
  + authoritative SEALED contribution-membership binding/observation
  + terminal/resolution status of the bound ContributionUnits

promotion evidence
→ exact promotion source set + policy fingerprint + target observation

submission/provider evidence
→ promotion/submission identity + exact revision/head + provider semantics

review-request/submission-author evidence
→ exact submission revision/head + configured external ship-ready/gate identity/result
```

Invalidation follows the binding of the affected class:

```text
bound source OID changes
ConvergenceUnit membership reopens/changes or terminal-resolution status changes
policy fingerprint changes
target basis changes where relevant
submission revision/head changes
provider semantics/state changes
submission-author gate identity/result changes
→ affected evidence/fact stale or re-read
```

Reuse is allowed only for the exact evidence/fact class whose complete binding remains current. There is no generic development-validation evidence class.

## 33.36 Promotion/provider-submission operation barriers and claims

While a critical promotion operation is held, incompatible operations against the same logical resources are prevented.

Examples:

```text
two direct target promotions
two provider submission create/update operations for same promotion unit
two restacks of same submission
new submission publication racing exact head binding
promotion materialization racing source-binding update
```

All exact guards are re-read under the claim/barrier.

## 33.37 Conflict/in-progress and reconciliation-required states

```text
owned Git operation conflict
→ isolated BLOCKED_CONFLICT operation state while being classified/recorded

semantic authoring required for internal merge/synchronization
→ RECONCILIATION_REQUIRED(exact conflict-producing facts)

semantic authoring required for promotion materialization
→ RECONCILIATION_REQUIRED(exact sources/destination/conflict facts)

semantic authoring required for owned submission restack/rebase
→ RECONCILIATION_REQUIRED(exact submission/base/conflict facts)

legacy/external internal-ref rebase
→ recovery-only; do not start another rewrite

unknown owner / ambiguous facts
→ UNKNOWN_INCONSISTENT
```

For `RECONCILIATION_REQUIRED`, authoritative refs remain unchanged. The exact descriptor is exposed to the external Development System and remains a nonterminal managed obligation. A later authored state receives no special authority: current state/topology/policy is re-read and current claims/CAS/transition-local guards are required before adoption.

Affected resources stop; unrelated resources continue.

## 33.38 Unknown/orphan/policy/provider-inconsistent state

Examples:

```text
orphan worktree/ref
ambiguous convergence-unit identity
ambiguous promotion sources
stale/contradictory policy
unsupported topology requested
unknown submission rewrite owner
provider head drift
provider says merged but target observation unavailable
detached HEAD where topology requires branch
```

All fail closed for destructive/promotion actions until reconstructed.

## 33.39 Crash/recovery state

Recovery handles:

```text
orphan fine-grained resource claim
stale/fenced top-level executor generation
requested_generation > processed_generation after executor loss
commit exists / managed-checkpoint metadata stale
authoring-dependency anchor exists / adoption metadata stale
authoring dependency adopted / source ref advanced, reset, renamed, or deleted
dependency compression or target-satisfaction observation / metadata stale
internal merge/conflict in progress
internal ref advanced / push pending
push complete / metadata stale
DIRECT target advanced / metadata stale
promotion materialization candidate/transient objects created / metadata stale
provider submission created/updated / metadata stale
submission revision published / metadata stale
provider restack happened / local metadata stale
merge queued / local metadata stale
provider merged / target observation pending
Ruu-owned temporary integration/workspace/anchor cleanup partially complete
policy changed during operation
UNKNOWN
```

Recovery first establishes a current OS-owned and SQLite-fenced convergence run when outstanding convergence demand remains, then loads unresolved Operations/Attempts and reconstructs actual coordination/Git/remote/provider/recovery-resource state before observing, adopting, closing, retrying, or superseding recognized effects. Durable coordination metadata never substitutes for exact external-state observation, and recovery never blindly duplicates irreversible effects. A fenced run generation cannot regain adoption authority merely because its old process or worker is still alive.

A live-but-hung process keeps the OS lock in v1; there is no automatic lease takeover. Normal Git/provider work is bounded by timeout/cancellation. Development System validation execution is external, and provider/CI/review waits become ordinary nonterminal waiting obligations rather than sleeps that retain top-level ownership.

## 33.40 Convergence-demand / top-level-executor lifecycle

```text
EXPLICIT AUTHORIZED CONVERGENCE TRIGGER
→ prerequisite External Control Plane changes already durable/authoritative as applicable
→ transactionally advance requested_generation
→ attempt dedicated OS process-lifetime exclusive run lock
→ BUSY + durable ACTIVE: current run remains responsible for demand; caller may return
→ BUSY + durable IDLE: caller must retry/complete ownership acquisition; do not strand demand
→ lock acquired: transactionally increment run_generation and publish ACTIVE + fresh run_token

CURRENT OS-OWNED + SQLITE-FENCED CONVERGENCE RUN
→ snapshot target_generation = requested_generation
→ recover unresolved Operations by exact observation
→ enumerate/reconstruct all nonterminal managed obligations
→ use/rebuild activity indexes only as acceleration structures
→ resolve managed identities
→ refresh repo policies + Git/remotes/providers
→ classify through current-state reconcilers
→ claim/schedule non-conflicting progressable resources
→ revalidate exact state + policy + current run_generation/run_token
→ persist Operation/Attempt before non-atomic effects where required
→ perform bounded Git/provider/filesystem effects outside SQLite transactions
→ exactly observe results
→ CAS-adopt current results and append Adoption atomically
→ refresh/repeat until current global fixed point
→ in one short transaction advance processed_generation through target_generation
→ if newer demand exists: remain ACTIVE and sweep again
→ else publish IDLE + clear run_token, becoming immediately fenced
→ release OS lock and exit without further authoritative mutation
```

If the process crashes, OS ownership disappears automatically; the next successful owner increments the durable generation before recovery. A live-but-hung process is not auto-fenced by a lease in v1. A stale run/late worker cannot authoritatively append new current-run observations or adopt managed progression after fencing.

Missing ContributionUnit editing topology routes to the external provisioning requirement, not implicit creation.

Missing work-bearing invocation acceptance or unresolved PromotionGroup group-local state prevents promotion materialization for that logical ship but does not stop unrelated internal convergence.

## 33.41 Fixed-point stop classes

A global sweep may reach its current fixed point only when every obligation enumerated or created during that sweep is either terminally resolved, or—if still nonterminal—has been freshly re-evaluated in the current sweep and is currently one of:

```text
currently protected
claimed by incompatible internal/recovery operation
waiting for a transition-specific external prerequisite
waiting on raw authoring-dependency source handoff, target satisfaction, or semantic reconciliation
waiting because more than one independently unsatisfied predecessor has no ratified provider representation
not ready
waiting for work-bearing invocation/PromotionGroup resolution
waiting for exact PromotionUnit member eligibility/topology prerequisites
conflict-blocked
policy-blocked/unsupported
UNKNOWN_INCONSISTENT
external submission/check/review wait
merge-queue wait
update/restack prerequisite wait
final target-integration observation/proof wait
```

External waits on transition-specific prerequisites do not cause spinning within one global sweep after their authoritative state has been freshly observed. They remain localized nonterminal prerequisites and are re-evaluated on later global sweeps servicing convergence demand.

A no-commit global sweep can still perform publication, direct promotion, submission/review/check/provider progression, merge-queue progression, restacking, final target-integration observation/proof, recovery, cleanup, or unrelated convergence.

## 33.42 No generic development-validation prerequisite state

ADR-060 retires the former generic `NOT_REQUIRED | REQUIRED_MISSING | VALID_EXACT | STALE | REJECTED | UNKNOWN_INCONSISTENT` development-validation state family from `ruu`. Each transition owns only its typed exact prerequisites. Missing externally owned facts remain localized on the concrete obligation that requires them; no universal validation-demand/evidence state is created.

## 33.43 Development-validation executor/capacity state — external

No test/verification executor, queue, capacity, flaky-test, retry, or external-service-test state is part of the `ruu` core after ADR-057/060. Such state belongs to the External Control Plane / Development System and may be implemented independently of the single-host `ruu` coordination domain.

## 33.44 Provider-submission review-request intent

```text
NONE
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

Canonical rules:

```text
no provider submission
→ NONE

provider submission exists without formal review request
→ REVIEW_NOT_REQUESTED

formal review requested
→ REVIEW_REQUESTED
→ exact current submission revision/head has valid configured submission-author evidence
```

Internal `READY/NOT_READY`, exact review-request intent, and promotion states are independent; no generic development-validation prerequisite state exists.

A material submission revision that invalidates submission-author evidence cannot remain `REVIEW_REQUESTED` without explicit revalidation.

# 34. Exhaustive modeled-state consistency audit

The latest finite technical state-space pass is post-baseline `STATE-SPACE-AUDIT-v46.md`, through ADR-081. It executes 648 new ADR-081 combinations and carries forward 16,380 retained historical combinations for 17,028 cumulative modeled cases. The new families cover exact source/version adoption, dirty-state exclusion, clean native-tip checkpoint adoption, crash-safe dependency anchoring, child-first handoff, source-owned checkpoint compression, source advancement, target satisfaction, abandonment, same-group handling, and competing CAS/retry behavior. ADR-070/078 remain the governing product-intent layer and ADR-081 preserves zero-preflight selection behind supported harness integration.

The executable v46 model adds the recorded ADR-081 finite families and invokes a supporting native Git retention smoke. That smoke creates exact source commit `A`, leaves producer-only dirty state outside `A`, anchors `A`, moves the ordinary source ref away, expires reflogs, runs pruning GC, and proves `A` remains an ordinary reachable commit through the Ruu dependency anchor while the dirty bytes never entered its tree. Exact dimensions/results are recorded under `qualification/state-space/post-baseline/v046/`.

The audit does **not** claim that arbitrary Git/provider graphs, semantic test pipelines, tracker backlogs, Development System behavior, multi-predecessor provider topology, late authoring refoundation, or cross-system distributed ordering are finite. It combines static cross-checks of the current architecture with exhaustive finite families for owned/boundary states. Historical reports remain immutable regression checkpoints for their respective revisions; v46 is the current active finite technical pass.

The current audit establishes in particular:

```text
Development System / repository governance
→ owns tests, lint, typecheck, build, formatters/codegen, security analysis,
  semantic/agentic review, finding adjudication, backlog scheduling/revalidation,
  flaky/external-service handling, retries/fixed points,
  validation compute scheduling, logs/artifacts/caches

External Control Plane before first managed write
→ resolves ConvergenceBase
→ binds immutable PromotionTarget(target_repository_id, target_ref)
→ provisions dedicated managed authoring worktree/ref + native reflog evidence

managed authoring ref removal
→ transactional binding transition prepared
→ committed transition is unresolved until causal proof
→ rename/rebind proof = CONTINUATION
→ terminal delete proof = ABANDON
→ same OID/tree/ancestry or branch copy never proves continuation

Ruu checkpoint boundary
→ consumes frozen mutation handoff
→ adopts an exact clean native tip without a new commit, or constructs the dirty canonical whole-surface candidate
→ records exactly that managed checkpoint

promotion exact candidate C + immutable PromotionTarget T
→ one semantic objective RealizePromotion(C,T)
→ route is DIRECT_TARGET_ADVANCE or PROVIDER_SUBMISSION

DIRECT realization
→ native proof when C == authoritative target O or C ancestor-of O
→ legitimate user/agent direct Git progress is reconcilable; Ruu actor attribution is not required

PROVIDER_SUBMISSION realization
→ exact SubmissionProjectionProof C → H
→ exact provider finalization H → R on T
→ independent Git proof R == O or R ancestor-of O
→ candidate ancestry cannot bypass required provider route
→ MERGED / PROVIDER_FINALIZED alone never terminalizes promotion
→ universal diff/patch/program-semantic equivalence is not required

PROVIDER_SUBMISSION
+ neither REVIEW_REQUESTED nor explicit current early-publication authority
→ no provider projection is created

PROVIDER_SUBMISSION
+ provider projection exists
+ final integration operation REQUIRED ∩ SUPPORTED ∩ AUTHORIZED
+ all exact current prerequisites satisfied
→ provider finalization is progressed automatically
→ no generic manual-Merge-click gate

explicit authoritative human-finalizer requirement
→ localized wait for that actual authority

semantic review finding DEFER
→ external tracker/backlog projection
→ current promotion is not blocked merely by the deferred finding

blocking provider CHANGES_REQUESTED
→ ADR-053 exact ReviewCorrectionDemand
→ external DEFER cannot bypass provider governance

same-source PromotionGroup projection
+ coherent immutable PromotionTarget across members
→ one repository-local PromotionUnit

same-source PromotionGroup projection
+ conflicting immutable PromotionTargets
→ TARGET_INCOHERENT_PROMOTION_GROUP
→ fail closed; never split or retarget

policy/provider refresh
→ may change DIRECT_TARGET_ADVANCE/PROVIDER_SUBMISSION eligibility or block mechanics
→ may change current target OID/governance observations
→ never changes PromotionTarget repository/ref identity

ship-ready semantic process / provider CI execution policy
→ external Development System / repository-provider governance responsibility

no internal test runner / verification scheduler / flaky-test state /
verification fixed-point loop / generic DevelopmentValidationEvidence state
→ present in the Ruu core
```

`OPEN-DESIGN-BACKLOG.md` records the native-Git observation-plane umbrella 30.49 as closed by ADR-080. ADR-074 closes 30.50, ADR-075 closes 30.51, ADR-076 closes 30.52, ADR-077 closes 30.53, ADR-079 closes 30.54, and ADR-080 closes 30.55; 30.44/30.45 remain closed by ADR-071 as corrected, 30.46 by ADR-072, 30.47 by ADR-073, and 30.48 remains closed with later observation-plane audits superseding the old direct-deletion classifier verification.
