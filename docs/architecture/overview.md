# Ruu — Architecture Overview

> **Status: non-normative architecture map.**
>
> This document explains the current architecture through ADR-081 and is intended to let a new reader build the right mental model before reading the full specification and decision history. It does **not** introduce requirements, states, identities, or authority rules of its own. If this overview conflicts with [`RUU-SPEC.md`](../specification/ruu-spec.md), [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md), or a governing ADR, those normative sources control.

## 1. Product in one sentence

`ruu` is **Git-based version control redesigned for concurrent agentic software development**.

Git remains the native object/history substrate and interoperability boundary. `ruu` adds the version-control semantics needed when several coding agents or sessions may author concurrently, touch the same repositories or files, span multiple repositories, checkpoint independently, crash, retry, and publish through different repository policies without requiring a human to manually serialize Git operations.

Provider systems such as GitHub or GitLab are an optional publication/governance layer over that core. They do not define core version identity or convergence truth.

Normative anchors: [ADR-070](../adr/adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md), [ADR-078](../adr/adr-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md), [ADR-080](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md), [ADR-081](../adr/adr-081-manage-exact-authoring-dependencies-before-promotion.md), specification §0.

---

## 2. The whole system at a glance

The architecture has two very different temporal phases:

1. **pre-edit managed-authoring provisioning**, which must exist before the first managed write; and
2. **checkpoint / reconciliation / promotion**, initiated later when work crosses a Git boundary.

```text
                         DEVELOPMENT SYSTEM
              Pi / Codex / Claude / /go / human
                              │
                    wants to begin authoring
                              │
                              ▼
                  PRE-EDIT PROVISIONING
                              │
                   resolve repository
                              │
              ConvergenceBase + PromotionTarget
                              │
                              ▼
                    ┌──────────────────┐
                    │ ConvergenceUnit  │
                    │ repository-local │
                    └────────┬─────────┘
                             │
                  attach one or more
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ContributionUnit ContributionUnit ContributionUnit
              │              │              │
           worktree        worktree        worktree
              │              │              │
          authoring       authoring       authoring
              │              │              │
              └──────────────┼──────────────┘
                             │
                       ruu
                             │
                 frozen handoff cohort
                             │
                             ▼
                   LogicalInvocation
                     ┌───────┴───────┐
                     │               │
                     │          ConvergenceDemand
                     │               │
                     │               ▼
                     │        GLOBAL RECONCILER
                     │               │
                     │        fixed-point sweep
                     │               │
                     │      internal convergence
                     │               │
                     ▼               ▼
                PromotionGroup   READY_INTERNAL
                     │               │
                     └───────┬───────┘
                             ▼
                   group-local exact state
                             │
                    project by repository
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
     PromotionUnit      PromotionUnit      PromotionUnit
        Repo A             Repo B             Repo C
          │                  │                  │
       policy             policy             policy
          │                  │                  │
      direct/provider   direct/provider   direct/provider
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                      PromotionTarget(s)
```

The most important ordering rule in this picture is:

```text
ConvergenceUnit
    BEFORE
ContributionUnit
    BEFORE
managed worktree / first managed write
```

A ConvergenceUnit is therefore **not created by merging ContributionUnits**. It is the already-established repository-local convergence scope to which ContributionUnits are attached and into which their checkpoints converge.

Normative anchors: [ADR-015](../adr/adr-015-provision-repository-local-convergence-unit-ref-before-first-contribution-unit.md), [ADR-023](../adr/adr-023-separate-contribution-unit-provisioning-from-ruu.md), [ADR-061](../adr/adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md), [ADR-078](../adr/adr-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md).

---

## 3. Authority boundary: who decides what?

The architecture deliberately separates **semantic development authority** from **mechanical version-control progression**.

### Development System / External Control Plane

The Development System knows things such as:

- what the agent is trying to implement;
- which convergence scope new work belongs to;
- when a ContributionUnit may still produce more work (`OPEN`) or is finished for that scope (`CLOSED`);
- when ConvergenceUnit membership is still open to new ContributionUnits or may be sealed;
- when current work is ready to cross a Git boundary;
- which exact ContributionUnits belong to a work-bearing invocation handoff;
- which stable source ContributionUnit and exact native commit a new consumer semantically requires before authoring;
- any semantic correction authority that must be associated with an existing promotion occurrence.

The External Control Plane is an **architectural role**, not necessarily a second product. For supported coding harnesses, Ruu-supplied integration may implement the plumbing automatically while semantic authority remains above the convergence engine.

### Ruu

`ruu` owns the rigorous Git/managed progression after those authoritative facts exist. It:

- observes exact Git/managed state;
- checkpoints managed work under the required handoff rules;
- synchronizes ConvergenceBase, ConvergenceUnits, and ContributionUnits;
- integrates mechanically reconcilable contribution state;
- derives exact ancestry/fast-forward/divergence facts;
- localizes irreducible reconciliation obligations;
- drives all known nonterminal obligations toward a fixed point;
- adopts and retains explicitly selected exact AuthoringDependencies;
- reconciles raw dependencies against target state and later source handoffs;
- derives PromotionGroups from work-bearing invocations;
- adopts group-local exact states;
- materializes repository-local PromotionUnits;
- resolves how an already-bound PromotionTarget may currently be realized;
- performs direct target advancement or provider-submission realization when authorized;
- recovers safely from crashes, ambiguous effects, concurrent movement, and retries.

It does **not** infer product-feature meaning, task completion, business readiness, or semantic correctness from branch names, file overlap, CWD, agent identity, or Git topology.

Normative anchors: [EXTERNAL-CONTROL-PLANE-CONTRACT.md](../specification/external-control-plane-contract.md), [ADR-039](../adr/adr-039-formalize-external-control-plane-contract.md), [ADR-057](../adr/adr-057-externalize-development-verification-and-model-ruu-as-state-dependent-git-progression.md), [ADR-070](../adr/adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md).

---

## 4. Pre-edit authoring topology

### 4.1 ConvergenceBase and PromotionTarget are different concepts

Every ConvergenceUnit has two destination-related bindings:

```text
ConvergenceBase
= repository-local state/ref family from which the ConvergenceUnit
  is provisioned and with which it synchronizes while mutable

PromotionTarget
= immutable final logical destination
  (target_repository_id, target_ref)
```

In a simple same-repository workflow they may both correspond to `main`, but they are architecturally different.

For example, in a fork/upstream workflow:

```text
source repository / local authoring fork
    ConvergenceBase  = local authorized base/tracking state

final destination
    PromotionTarget  = upstream repository / refs/heads/main
```

The PromotionTarget is bound **before the first managed write** and cannot later be rewritten merely because publication policy changes. A genuinely different intended target requires a distinct ConvergenceUnit scope.

Normative anchor: [ADR-061](../adr/adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md).

### 4.2 ConvergenceUnit comes first

The pre-edit sequence is conceptually:

```text
resolve repository identity
→ resolve ConvergenceBase
→ resolve PromotionTarget(target_repository_id, target_ref)
→ create/reuse ConvergenceUnit with immutable target binding
→ create ContributionUnit bound to that ConvergenceUnit
→ create/adopt managed ref + dedicated worktree
→ establish mutation/observer/binding guarantees
→ authorize first managed write
```

A **ConvergenceUnit** is the repository-local shared Git root into which one or more ContributionUnits converge.

Conceptually:

```text
ConvergenceBase
      │
      ▼
ConvergenceUnit ───────────────────► immutable PromotionTarget
      │
      ├── ContributionUnit A
      ├── ContributionUnit B
      └── ContributionUnit C
```

A ConvergenceUnit has stable orchestration identity independent of its human-readable branch/display name. Names such as `fix-login-race` or `refactor-parser` are descriptive only.

Its externally authoritative contribution-membership state is:

```text
OPEN
= additional ContributionUnits may still attach

SEALED
= no additional ContributionUnit is currently expected/authorized
  before the current convergence result may finalize internally
```

`OPEN` does not stop ordinary convergence. It prevents only final internal readiness.

Normative anchors: specification §2.2, [ADR-006](../adr/adr-006-use-target-convergence-unit-contribution-unit-hierarchy.md), [ADR-015](../adr/adr-015-provision-repository-local-convergence-unit-ref-before-first-contribution-unit.md), [ADR-037](../adr/adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md).

### 4.3 ContributionUnit is the isolated production stream

A **ContributionUnit** is a bounded, repository-local stream of contribution to exactly one ConvergenceUnit.

Its core cardinality is:

```text
1 contribution_unit_id
=
exactly 1 repository_id
+
exactly 1 convergence_unit_id membership
+
stable logical identity independent of editing-artifact lifetime
```

While actively authored in V1, it uses a dedicated Git worktree/ref surface.

```text
                    ConvergenceUnit X
                     /            \
                    /              \
              CU-agent-A        CU-agent-B
                  │                 │
             worktree A        worktree B
```

Two concurrent producers in the same repository therefore do not share a mutable checkout.

A ContributionUnit is **not a commit**. While `OPEN`, it may produce several ordinary native commits and several authoritative managed checkpoints over time. Native commits are exact Git versions, but they become managed checkpoints only through exact frozen-handoff adoption. Checkpoints may be integrated upward eagerly while the ContributionUnit remains capable of further contribution. Once `CLOSED`, it cannot reopen; later work uses a new ContributionUnit identity, which may still belong to the same ConvergenceUnit if the convergence scope remains the same.

ContributionUnit identity also survives loss/removal of its editing artifacts after durable checkpoint continuity exists. Branch/worktree existence is not the semantic identity. `ContributionUnit` is also the sole v1 stable authoring-occurrence identity; session, process, branch, worktree, and a separate `work_occurrence_id` do not compete with it.

Normative anchors: [ADR-001](../adr/adr-001-isolate-concurrent-work-production-with-git-worktrees.md), [ADR-002](../adr/adr-002-use-repository-local-contribution-units-as-the-isolation-unit.md), [ADR-035](../adr/adr-035-use-bounded-contribution-units-with-external-lifecycle-authority.md), [ADR-038](../adr/adr-038-decouple-contribution-unit-identity-from-editing-artifacts.md), [ADR-073](../adr/adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md), [ADR-081](../adr/adr-081-manage-exact-authoring-dependencies-before-promotion.md).

### 4.4 Exact authoring dependencies before promotion

A consumer ContributionUnit may need an exact native commit from another still-active ContributionUnit before the source has any Ruu checkpoint or PromotionGroup.

```text
source α: native commit A; authoring may continue
consumer β: explicitly consumes α@A; authors B; invokes Ruu first
```

The Development System explicitly selects both **who** and **what**:

```text
source = (repository_id, contribution_unit_id)
consumed version = exact commit OID A
```

Ruu then proves exact source lineage, creates a REQUIRED recovery anchor for `A`, and adopts an immutable AuthoringDependency before consumer authoring. A supported harness submits this as an internal provisioning demand to the existing fenced reconciler and waits before first write; no user-facing preflight or work-bearing checkpoint is created. The source may be dirty, but only commit `A` is consumed. Ruu never snapshots the producer's mutable worktree and never infers dependency from ancestry, names, file overlap, recency, or session order.

The consumer may author, checkpoint, converge, form a PromotionGroup, and materialize exact owned state while the relation remains raw. Realization waits locally because consumer ancestry does not transfer source publication authority.

A raw dependency can later resolve in three ways:

```text
current authoritative target contains A
→ SATISFIED_BY_TARGET

source and consumer are already in the same immutable group
→ INTERNAL_TO_SAME_GROUP
→ no provider edge

same source ContributionUnit later hands off its own exact pre-sync checkpoint S containing A
+ group-local exact K incorporates S
+ source/consumer PromotionTargets are exactly equal
→ resolve to stable (source PromotionGroup, repository) projection
→ retain consumed A
→ Restack(old_base=A, owned_candidate=B, new_base=K) when needed
```

Source advancement never changes `A` or mutates an active consumer worktree. Aggregate group ancestry cannot launder `A` back from the consumer when the source's own frozen pre-sync checkpoint omitted it. If the source loses its realization path before `A` is validly target-realized, the consumer remains blocked with exact reconciliation work; it does not inherit authority to publish `A`. An already-adopted valid target-satisfaction proof remains historical authority after later target drift, while every later consumer realization still revalidates current route/policy/CAS guards.

The exact anchor remains retained through source reset/amend/ref deletion and Git GC. Multiple independently unsatisfied predecessors and dependency discovery after consumer authoring has already begun remain explicit open design questions; Ruu invents neither provider topology nor active-worktree refoundation.

Normative anchor: [ADR-081](../adr/adr-081-manage-exact-authoring-dependencies-before-promotion.md).

---

## 5. Internal Git convergence

The internal topology is not a one-shot merge pipeline. It is a continuously re-evaluated convergence graph.

The important relationships are conceptually:

```text
ConvergenceBase  ─────► ConvergenceUnit

ConvergenceUnit  ─────► ContributionUnit

ContributionUnit ─────► ConvergenceUnit
```

This lets:

- a mutable ConvergenceUnit absorb relevant movement from its base;
- ContributionUnits receive shared converged state as mechanically allowed;
- exact ContributionUnit checkpoints advance toward the shared ConvergenceUnit as early as mechanically safe.

The system repeatedly uses exact Git ancestry and append-only/no-rebase V1 reconciliation. Fast-forward is preferred when ancestry permits it; non-fast-forward reconciliation is controlled rather than silently rewriting internal history.

A mechanically resolvable conflict remains version-control work and is handled by the convergence engine. A conflict requiring semantic understanding becomes an explicit reconciliation obligation for the Development System rather than guessed resolution.

Normative anchors: [ADR-007](../adr/adr-007-converge-every-edge-bidirectionally-to-a-fixed-point.md), [ADR-012](../adr/adr-012-isolate-integration-workspaces-and-model-conflicts-as-blocked-states.md), [ADR-016](../adr/adr-016-use-an-append-only-no-rebase-v1-reconciliation-strategy.md), [ADR-017](../adr/adr-017-derive-fast-forward-and-divergence-from-exact-git-ancestry.md), [ADR-037](../adr/adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md).

### READY_INTERNAL

`READY_INTERNAL(OID)` is a **mechanical exact-state assertion**, not a statement that the product feature is semantically complete or approved for business release.

Among its guards, the ConvergenceUnit contribution membership must be `SEALED`, there must be no `OPEN` ContributionUnit in that convergence scope, and the required exact checkpoint/reconciliation obligations must be resolved under the race-safe readiness barrier.

Provider review, merge queue, publication policy, and other later governance facts do not belong inside this internal readiness fact.

Normative anchors: [ADR-010](../adr/adr-010-bind-readiness-and-validation-to-exact-git-state.md), [ADR-011](../adr/adr-011-use-an-atomic-convergence-unit-readiness-promotion-barrier.md), [ADR-037](../adr/adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md).

---

## 6. What `ruu` invocation means

The ordinary user experience is intentionally simple:

```text
install Ruu once
launch a supported coding harness
ask the agent to implement
work normally

ruu
```

The later `ruu` command is **not** allowed to retroactively invent the pre-edit isolation that should already have existed. Supported harness integration is responsible for making the required managed-authoring state exist before first managed write.

When new work is handed off, the invocation has two separable meanings:

1. a durable **work-bearing LogicalInvocation** records which new work belongs to this checkpoint occurrence; and
2. a **ConvergenceDemand** wakes or adds demand to the global reconciler.

These are not the same object.

### 6.1 LogicalInvocation: the occurrence boundary

A work-bearing LogicalInvocation contains a sealed, immutable, non-empty cohort of exact ContributionUnit handoffs.

Conceptually:

```text
LogicalInvocation I42

handoffs = {
    CU-A handoff,
    CU-B handoff,
    CU-C handoff
}
```

The same opaque invocation identity is reused when retrying the **same** logical occurrence; redefining it with a different immutable cohort is an integrity failure.

The handoff cohort answers:

> **Which new work belongs to this checkpoint occurrence?**

It is independent of the shell's current working directory. A session that touched `frontend`, `backend`, and `schema` can invoke from any managed repository from which the coordination domain is discoverable.

Normative anchors: [ADR-064](../adr/adr-064-bind-pre-commit-readiness-by-frozen-mutation-handoff.md), [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md), [ADR-070](../adr/adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md).

### 6.2 ConvergenceDemand: wake the global engine

A ConvergenceDemand does **not** mean "process the current repository" or "process only this invocation's cohort".

It means, conceptually:

```text
there is convergence work to reconsider
```

Several simultaneous explicit invocations may therefore contribute/coalesce demand behind the same host-level executor while their distinct LogicalInvocations remain distinct durable work occurrences.

Normative anchors: [ADR-036](../adr/adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md), [ADR-041](../adr/adr-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md), [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md).

---

## 7. The global reconciler

Every sweep is global over known nonterminal managed obligations in the coordination domain, not caller-local.

An invocation from Repo A may therefore progress:

- the new handoff created by that invocation;
- an older ContributionUnit checkpoint in Repo B;
- a ConvergenceUnit that became mechanically advanceable in Repo C;
- an earlier PromotionUnit waiting on current policy or target state;
- a provider submission whose required external fact is now satisfied;
- an operation whose process died after a side effect but before durable adoption;
- unrelated cleanup/retirement obligations that are now safe.

The conceptual execution loop is:

```text
observe authoritative current state
        ↓
classify legal next transitions
        ↓
claim / fence the affected resource
        ↓
revalidate exact prerequisites
        ↓
perform one authorized effect
        ↓
re-observe result
        ↓
adopt/journal exact outcome
        ↓
repeat until no currently legal progress remains
```

This is why invocation order is not supposed to become a user-level mutex.

The host-level executor is fenced/recoverable, while fine-grained claims/CAS allow independent resources to progress safely without treating the whole system as one giant repository lock.

Normative anchors: [ADR-004](../adr/adr-004-make-convergence-global-across-registered-repositories.md), [ADR-005](../adr/adr-005-coordinate-simultaneous-convergers-with-fine-grained-claims-and-cas.md), [ADR-036](../adr/adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md), [ADR-041](../adr/adr-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md), [ADR-042](../adr/adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md), [ADR-072](../adr/adr-072-make-host-run-lock-handles-non-inheritable-across-subprocess-boundaries.md).

---

## 8. From invocation to PromotionGroup

For ordinary new work, Ruu does not ask the caller to manually declare a PromotionGroup.

It mechanically maps the sealed LogicalInvocation handoff cohort through the already-authoritative ContributionUnit → ConvergenceUnit bindings:

```text
LogicalInvocation I42
    │
    ├── CU-A ──► Repo A / ConvergenceUnit X
    ├── CU-B ──► Repo B / ConvergenceUnit Y
    └── CU-C ──► Repo C / ConvergenceUnit Z
                     │
                     ▼
              PromotionGroup G42
              members = {X, Y, Z}
```

A **PromotionGroup** is therefore the durable promotion obligation for one logical occurrence. It may span repositories.

Two later invocations that happen to touch the same set of ConvergenceUnits still create distinct ordinary PromotionGroups because they are distinct work occurrences:

```text
Invocation I42 → PromotionGroup G42
Invocation I43 → PromotionGroup G43
```

The PromotionGroup's exact state is **group-local**. It is not an alias for the forever-moving live state of its ConvergenceUnits. Once the group adopts an exact state attributable to its occurrence, later unrelated authoring on the same lineage does not silently rewrite that earlier group.

Explicit group-bound correction has separate authority rules and can revise an existing group only under those rules.

Normative anchors: [ADR-046](../adr/adr-046-predeclare-closed-promotion-groups-and-resolve-them-to-exact-promotion-units.md) as amended, [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md).

---

## 9. PromotionUnit: repository-local exact shipment state

A PromotionGroup may be cross-repository, but native Git state is repository-local. Once the group's required exact states are available, Ruu partitions the complete group-local exact set by authoritative source repository.

```text
PromotionGroup G42
│
├── Repo A
│    ├── exact state of ConvergenceUnit X
│    └── exact state of ConvergenceUnit Y
│             │
│             ▼
│      PromotionUnit PA
│
└── Repo B
     └── exact state of ConvergenceUnit Z
              │
              ▼
       PromotionUnit PB
```

A **PromotionUnit** is:

- non-empty;
- immutable;
- content-addressed;
- an unordered exact set;
- from exactly one authoritative source repository;
- target-coherent: members projected into the same repository-local PromotionUnit must carry the same immutable PromotionTarget.

If several ConvergenceUnits from one source repository belong to the same PromotionGroup, Ruu does not arbitrarily split them into several PromotionUnits. They form the single repository-local projection boundary for that group/source repository when target-coherent. If one candidate must materialize several exact member states, the canonical pairwise merge rules define that composition.

Normative anchors: [ADR-045](../adr/adr-045-make-promotion-units-immutable-content-addressed-exact-state-sets.md), [ADR-047](../adr/adr-047-project-promotion-groups-deterministically-into-repository-local-promotion-units.md), [ADR-048](../adr/adr-048-materialize-repository-local-multi-source-promotion-units-by-canonical-pairwise-merging.md), [ADR-061](../adr/adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md).

---

## 10. PromotionTarget says **where**; policy says **how**

The final destination was already bound on each ConvergenceUnit before authoring:

```text
PromotionTarget = (target_repository_id, target_ref)
```

When promotion becomes possible, repository policy does **not** choose another destination. It determines how the current exact state may legally reach the existing PromotionTarget.

The major route distinction is:

```text
DIRECT_TARGET_ADVANCE
        or
PROVIDER_SUBMISSION
```

### Direct target advancement

Conceptually:

```text
immutable PromotionUnit
        ↓
exact candidate
        ↓
expected-old / ancestry / current-policy guards
        ↓
atomic exact-old target update
        ↓
PromotionTarget
```

The target is not mutated by a blind force-push. Current exact state and expected-old authority are part of the transition.

Normative anchor: [ADR-052](../adr/adr-052-advance-direct-targets-by-atomic-exact-old-cas-fast-forward.md).

### Provider-submission route

Conceptually:

```text
immutable PromotionUnit
        ↓
stable logical submission
        ↓
provider-facing publication episode / submission ref
        ↓
PR / MR / checks / review / queue / governance
        ↓
exact provider finalization
        ↓
authoritative target Git realization
```

The provider-facing representation is a projection of already-defined exact managed/Git state. It is not core identity.

Normative anchors: [ADR-049](../adr/adr-049-separate-stable-submission-identity-and-refs-from-internal-exact-state.md), [ADR-062](../adr/adr-062-make-promotion-route-independent-and-provider-submissions-projections.md), [ADR-065](../adr/adr-065-prove-final-promotion-realization-by-native-git-or-exact-provider-result-binding.md), [ADR-066](../adr/adr-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md).

---

## 11. Authoring dependency becomes derived stacked publication only after resolution

Stacked PRs/submissions are not a primary authoring structure and are not requested merely because several ContributionUnits or ConvergenceUnits exist.

Before promotion identity exists, the Development System may explicitly select an exact AuthoringDependency. That semantic selection still does not select a stack. A stack appears only after Ruu maps the durable source identity through a qualifying source-owned pre-sync checkpoint and handoff to a stable promotion projection with the same immutable PromotionTarget and current exact promotion state requires one provider-facing publication to depend on another result that is not yet satisfied by the authoritative target.

Conceptually:

```text
PromotionTarget
      ↑
submission A
      ↑
submission B
```

If the predecessor becomes satisfied by the target, the dependent publication may be reprojected/restacked against the new exact state without rewriting the internal ContributionUnit/ConvergenceUnit owned history.

Therefore:

```text
stacked publication
≠ ContributionUnit hierarchy
≠ ConvergenceUnit hierarchy
≠ caller-selected permanent topology

stacked publication
= provider-facing representation derived from exact dependency state
```

Normative anchor: [ADR-050](../adr/adr-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md).

---

## 12. Three observation authority domains

Through ADR-080 the observation model has three deliberately separate source-authority domains:

```text
LOCAL_GIT
REMOTE_GIT
PROVIDER
```

### LOCAL_GIT

Owns local exact Git state and the narrow causal observation required for managed local authoring-binding cessation/replacement.

The local native observer is intentionally small. It does not become a distributed transaction coordinator or provider proxy.

### REMOTE_GIT

Owns current authoritative remote refs/OIDs and exact-preconditioned remote mutation/re-observation.

A local remote-tracking ref such as:

```text
refs/remotes/origin/main
```

is only a **local cache** of what the clone last learned. It is not authoritative current remote state.

Bare Git remotes are first-class. Provider APIs are not required merely to observe or advance native remote Git state where the route needs only Git semantics.

### PROVIDER

Owns provider-specific facts such as submission objects, review/check state, merge queues, governance rules, or exact provider finalization facts when those semantics are actually required by the route.

Generic webhook delivery is not treated as a complete event log. Webhooks may wake reconciliation and, under demonstrated adapter semantics, may provide positive authenticated evidence; absence does not prove non-occurrence and delivery identity is not semantic transition identity.

Cross-domain composition uses exact source-owned identities and documented semantics, not wall-clock arrival order.

Normative anchors: [ADR-074](../adr/adr-074-minimize-native-git-event-observation-to-managed-authoring-binding-disposition.md), [ADR-075](../adr/adr-075-require-pre-linearization-native-ref-witnesses-and-state-rediscovery-by-observation-class.md), [ADR-076](../adr/adr-076-separate-native-witness-provenance-from-managed-effect-identity-and-make-semantic-adoption-idempotent.md), [ADR-077](../adr/adr-077-require-attested-repository-common-observer-coverage-without-owning-foreign-git-mutation-infrastructure.md), [ADR-079](../adr/adr-079-minimize-native-git-rejection-with-conservative-protection-filtering-and-exact-binding-admission.md), [ADR-080](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md).

---

## 13. Crash/retry model

The system assumes that processes, networks, providers, and acknowledgements can fail at awkward boundaries.

A managed operation may reach a situation conceptually like:

```text
observe old state
→ persist intent / claim
→ perform Git or provider effect
→ process or network dies
→ outcome initially UNKNOWN
```

Recovery does not guess from process history. It re-observes the authoritative source and determines whether the exact intended effect is present, absent, or contradicted by concurrent drift, then adopts/retries/blocks under current authority.

The CoordinationStore and append-only effect journal preserve durable workflow knowledge, but persisted historical intent is not unlimited future authority: new realization effects are fenced by current state/disposition/policy prerequisites.

AuthoringDependency adoption uses the same pattern. The consumed commit is anchored before managed adoption; crash before or after anchor creation is recovered from Operation/Attempt plus exact Git state. Compression to a source promotion projection is CAS-guarded and duplicate reconciliation cannot select a second parent.

This is also why observation delivery itself is not required to be exactly once. Semantic adoption is idempotent under logical identity and exact current guards.

Normative anchors: [ADR-005](../adr/adr-005-coordinate-simultaneous-convergers-with-fine-grained-claims-and-cas.md), [ADR-042](../adr/adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md), [ADR-065](../adr/adr-065-prove-final-promotion-realization-by-native-git-or-exact-provider-result-binding.md), [ADR-071](../adr/adr-071-make-managed-branch-deletion-durable-abandonment-and-fence-realization-by-current-disposition.md), [ADR-076](../adr/adr-076-separate-native-witness-provenance-from-managed-effect-identity-and-make-semantic-adoption-idempotent.md), [ADR-080](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md).

---

## 14. Scope of the major entities

| Entity / concept | Scope | What it answers |
|---|---|---|
| Repository | repository-local | Which native Git object/ref namespace owns this state? |
| ConvergenceBase | repository-local | From which mutable base family does this ConvergenceUnit synchronize? |
| ConvergenceUnit | repository-local | Into which shared lineage should these contributions converge? |
| ContributionUnit | repository-local | Which isolated bounded contribution stream is authoring toward that ConvergenceUnit? |
| AuthoringDependency | repository-local relation | Which stable source ContributionUnit and exact commit did this consumer explicitly adopt before promotion? |
| Managed worktree/ref | repository-local artifact | Where is active V1 authoring physically isolated? |
| LogicalInvocation | coordination-domain occurrence | Which frozen new/correction work belongs to this checkpoint occurrence? |
| ConvergenceDemand | coordination-domain signal | Should the global reconciler re-evaluate progress now? |
| ReconcilerRun / host executor | host/coordination execution | Which fenced process currently performs reconciliation? |
| PromotionGroup | potentially cross-repository | Which ConvergenceUnit results belong to this promotion occurrence? |
| PromotionUnit | exactly one source repository | Which immutable exact repository-local state set is being promoted? |
| PromotionTarget | exact target repository/ref | Where must this ConvergenceUnit's result ultimately land? |
| Effective promotion policy | exact current promotion context | How may the already-bound target currently be realized? |
| Provider submission/episode | provider-facing projection | How is one exact promotion represented in a provider workflow? |

This table is a map only; the exact identity/state schemas remain normative in the specification and ADRs.

---

## 15. A complete nominal scenario

Assume one coding session changes three repositories: `frontend`, `backend`, and `schema`.

### Before authoring in each repository

The harness integration automatically ensures:

```text
repository admitted/resolved
→ ConvergenceBase resolved
→ immutable PromotionTarget resolved
→ appropriate ConvergenceUnit created/reused
→ new ContributionUnit attached
→ dedicated managed worktree/ref prepared
→ observer/binding/mutation authority established
→ first managed write authorized
```

So the session may have:

```text
frontend: CU-F → ConvergenceUnit F
backend:  CU-B → ConvergenceUnit B
schema:   CU-S → ConvergenceUnit S
```

No cross-repository ContributionUnit exists; cross-repository semantic work is represented by several repository-local units.

### During authoring

The agent edits normally inside the isolated worktrees. Other sessions may simultaneously have different ContributionUnits in the same repositories and may even target the same ConvergenceUnits.

Valid exact checkpoints can be integrated toward their ConvergenceUnits as soon as mechanically safe; ContributionUnits do not need to be closed merely to contribute an intermediate checkpoint.

### When this session invokes `ruu`

The Development System freezes the current handoffs and records one work-bearing LogicalInvocation:

```text
I42 = {CU-F handoff, CU-B handoff, CU-S handoff}
```

This produces convergence demand. The host executor performs a **global** sweep, not merely a three-repository private transaction for I42.

### Promotion occurrence

For `NEW_GROUP`, Ruu mechanically maps the handoffs to their ConvergenceUnits:

```text
I42
→ {ConvergenceUnit F, ConvergenceUnit B, ConvergenceUnit S}
→ PromotionGroup G42
```

As each group member obtains/adopts the exact group-local state required for this occurrence, the group is projected by source repository:

```text
G42
├── frontend → PromotionUnit PF
├── backend  → PromotionUnit PB
└── schema   → PromotionUnit PS
```

Each PromotionUnit then follows its own current route/policy toward its already-bound PromotionTarget. One repository could advance directly, another could require a PR/merge queue, and another could temporarily block. Cross-repository progress is not assumed atomic.

An external wait in one repository does not freeze unrelated progress elsewhere.

Normative anchors: [ADR-014](../adr/adr-014-represent-cross-repository-promotion-as-non-atomic-partial-progress.md), [ADR-036](../adr/adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md), [ADR-047](../adr/adr-047-project-promotion-groups-deterministically-into-repository-local-promotion-units.md), [ADR-055](../adr/adr-055-settle-partial-cross-repository-ships-with-forward-actions-and-publication-episodes.md), [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md).

---

## 16. Important non-equivalences

A large part of the architecture exists to prevent convenient but incorrect identity collapses.

Do **not** read the system as if any of these were equivalent:

```text
coding session
≠ task / issue
≠ ContributionUnit
≠ ConvergenceUnit
≠ repository
≠ branch
≠ worktree
≠ LogicalInvocation
≠ PromotionGroup
≠ PromotionUnit
≠ provider submission
```

Likewise:

```text
native commit exists
≠ managed checkpoint
≠ handoff
≠ completion

managed checkpoint exists
≠ ContributionUnit CLOSED

ContributionUnit tip integrated
≠ ConvergenceUnit READY_INTERNAL

READY_INTERNAL
≠ business approval
≠ provider review success
≠ promoted

PromotionTarget
≠ pull request

PromotionTarget
≠ policy-selected destination

refs/remotes/origin/main
≠ current authoritative remote main

webhook delivery
≠ semantic transition identity

branch/worktree deletion
≠ generic semantic cancellation

dirty source worktree
≠ exact consumable version

exact commit OID
≠ semantic source identity

source abandonment
≠ consumer publication authority

CWD
≠ invocation cohort
≠ global sweep scope
```

These separations are not terminology for its own sake. They are what make concurrency, retries, cross-repository work, provider independence, and exact recovery coherent.

---

## 17. Recommended reading path after this overview

For a new reader, the shortest path from product intent to detailed mechanics is:

1. **[`RUU-SPEC.md`](../specification/ruu-spec.md)** — normative consolidated model.
2. **[`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md)** — authority boundary with the Development System.
3. **[ADR-070](../adr/adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md)** and **[ADR-078](../adr/adr-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md)** — governing product experience.
4. **[ADR-015](../adr/adr-015-provision-repository-local-convergence-unit-ref-before-first-contribution-unit.md), [ADR-035](../adr/adr-035-use-bounded-contribution-units-with-external-lifecycle-authority.md), [ADR-037](../adr/adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md), [ADR-061](../adr/adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md), [ADR-073](../adr/adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md)** — pre-edit topology and authoring lifecycle.
5. **[ADR-036](../adr/adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md), [ADR-041](../adr/adr-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md), [ADR-042](../adr/adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md), [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md)** — invocation and reconciler model.
6. **[ADR-045](../adr/adr-045-make-promotion-units-immutable-content-addressed-exact-state-sets.md) through [ADR-050](../adr/adr-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md), plus [ADR-062](../adr/adr-062-make-promotion-route-independent-and-provider-submissions-projections.md)** — promotion model and provider projection.
7. **[ADR-074](../adr/adr-074-minimize-native-git-event-observation-to-managed-authoring-binding-disposition.md) through [ADR-080](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md)** — local/remote/provider observation and native-Git coexistence.
8. **[ADR-081](../adr/adr-081-manage-exact-authoring-dependencies-before-promotion.md)** — exact source-attributed native versions consumed before source promotion.
9. **[`OPEN-DESIGN-BACKLOG.md`](../design/open-design-backlog.md)** only after the current model is understood; it contains design history and remaining open nodes rather than the primary architecture description.

---

## 18. Compact reference model

If only one picture is retained, use this one:

```text
                     SEMANTIC LAYER
                           │
                   Development System
                           │
              decides scope / lifecycle / handoff
                           │
                           ▼
               ═══ PRE-EDIT BOUNDARY ═══

                    ConvergenceUnit
             repository-local shared root
                  /        |        \
                 /         |         \
               CU-A       CU-B       CU-C
                │          │          │
             worktree   worktree   worktree
                │          │          │
                └──── authoring ──────┘
                           │
                           ▼
                  ═ Ruu ═
                           │
                   LogicalInvocation
                   exact handoff cohort
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       PromotionGroup            ConvergenceDemand
       occurrence logic               │
              │                        ▼
              │                 Global Reconciler
              │                        │
              │                internal fixed point
              │                        │
              │                 READY_INTERNAL
              │                        │
              └────────────┬───────────┘
                           ▼
                 group-local exact state
                           │
                project by repository
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       PromotionUnit   PromotionUnit  ...
              │            │
          repo policy   repo policy
              │            │
          direct / provider
              │            │
              └──────┬─────┘
                     ▼
               PromotionTarget
```

In one line per object:

```text
ConvergenceUnit
= repository-local convergence scope established before its ContributionUnits

ContributionUnit
= isolated bounded contribution stream into one ConvergenceUnit

AuthoringDependency
= explicit stable source ContributionUnit + immutable consumed commit, retained before source promotion and reconciled without authority transfer

LogicalInvocation
= durable occurrence boundary for an exact frozen handoff cohort

ConvergenceDemand
= wake/progress signal for the global reconciler

PromotionGroup
= occurrence-bound logical grouping of ConvergenceUnit results, possibly cross-repo

PromotionUnit
= immutable exact repository-local shipment state

PromotionTarget
= final destination bound before authoring

Promotion policy
= current rules for HOW that already-bound target may be realized

Global reconciler
= recoverable engine that advances every currently legal nonterminal obligation to fixed point
```

That is the architectural shape. The specification and ADRs define the exact contracts.
