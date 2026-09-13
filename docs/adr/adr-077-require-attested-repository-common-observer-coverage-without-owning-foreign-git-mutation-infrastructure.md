---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Require attested repository-common observer coverage without owning foreign Git mutation infrastructure"
id: "ADR-077"
status: "accepted"
date: "2026-09-08"
decision_body_sha256: "074e6a574a898c04e2f75f0a6149042ff04ff503f2bc92a41e6fa1756ff2c8fb"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-070"
    - "ADR-073"
    - "ADR-074"
    - "ADR-075"
    - "ADR-076"
  supersedes: []
  confirms: []
governs: []
---

# ADR-077 — Require attested repository-common observer coverage without owning foreign Git mutation infrastructure

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.53
- **Amends:** ADR-070, ADR-073, ADR-074, ADR-075, ADR-076, the consolidated specification, the External Control Plane contract, and the observation backlog
- **Leaves open:** backlog 30.49 umbrella and 30.54–30.55

## Context

ADR-075 requires every native ref mutation capable of terminating/replacing a currently bound managed authoring ref to cross a conforming pre-linearization observation point. ADR-076 then makes the resulting native witness/preparation durable causal evidence distinct from managed `Operation` identity and forbids later exact-state scans from manufacturing missing causal history.

That leaves an installation and ownership problem. A live repository may already have project hooks, user hooks, Development-System hooks, `core.hooksPath`, linked worktrees, or a future backend-native observer. Several tools may legitimately need the same Git hook event. Blindly replacing any of those surfaces would violate native-Git coexistence, while silently failing to establish the ADR-075 observer would create an unprovable causal gap.

There is a second, deeper problem: observer correctness is not a property of repository files alone. A repository whose ordinary Git CLI path invokes the observer may still be mutated by another engine or direct ref-store writer that does not traverse the required primitive. No post-hoc scan, reflog inspection, filesystem watcher, OID comparison, or ancestry test can recreate a missing vetoable pre-linearization event or reliably classify `RENAME` versus terminal removal after the fact.

30.53 therefore decides both:

1. how `ruu` establishes and composes observer coverage without taking ownership of foreign Git configuration; and
2. the V1 mutation-engine boundary under which ordinary native Git effects receive the ADR-075 guarantees.

## Decision

### 1. Observer coverage is repository-common for shared managed refs

For a repository with linked worktrees, ordinary `refs/*` are repository-common even though `HEAD`, index and selected pseudo/worktree refs are worktree-local. A managed authoring binding under `refs/*` can therefore be changed from another linked worktree or another Git invocation against the common repository.

The required observer coverage MUST consequently protect the **repository-common ref mutation surface**, not merely the managed worktree that currently follows the binding.

A conforming installation MUST resolve Git paths/configuration through Git-aware repository APIs/commands rather than assuming that a linked worktree's `$GIT_DIR` is the common directory. Traditional hook lookup for linked worktrees resolves through the common hook surface; implementations must not create worktree-private copies and mistake them for repository-wide coverage.

### 2. Coverage is a property of an admitted native mutation path, not of hook presence alone

The core concept is logically:

```text
NativeObservationCoverage {
  repository_id
  adapter_capability_id
  adapter_version
  mutation_engine_profile
  installation_profile
  coverage_epoch
  attestation
  status = ACTIVE | BROKEN
}
```

The exact schema is implementation-defined. The normative property is:

```text
ACTIVE
=
for the admitted native ref-mutation engine/profile,
the repository-common ADR-075 observation path has been
functionally established and remains trustworthy
```

The mere existence of a hook file, config key, process, or expected pathname MUST NOT by itself establish `ACTIVE`.

### 3. Git core is the required V1 native ref-mutation engine family

V1 requires a conforming **Git core** mutation path for ordinary native managed-ref operations.

This is an implementation support boundary, not a permanent core semantic dependency on one Git version or backend. ADR-075 remains capability-based. A future libgit2, JGit, custom ref database, or other engine may become conforming only through a separately demonstrated adapter that satisfies the same pre-linearization, veto/causal-serialization, exact-preimage, rename-versus-terminal, durable-witness, recovery-consistency and ADR-076 active-occurrence-idempotency properties.

A user-facing tool or IDE that delegates every correctness-relevant ref mutation to a conforming engine inherits that engine's conformance. Generic claims of "Git compatibility" do not imply conformance.

### 4. Uninstrumented/direct ref-store writers are outside the managed native-mutation contract

A program that changes the ref store without traversing an admitted conforming mutation engine remains physically possible. V1 does not attempt to sandbox all programs with filesystem access to the repository or to make `ruu` the privileged owner of Git storage.

If such a writer changes an unmanaged ref, ordinary Git semantics remain outside `ruu` business state.

If it changes a currently bound managed authoring ref without the required causal preparation:

```text
exact managed binding state changed
+ no conforming durable pre-linearization witness/preparation
→ UNWITNESSED_MANAGED_BINDING_MUTATION
→ observation-integrity failure
→ fail closed
```

The reconciler MUST NOT reinterpret final topology alone as `CONTINUATION` or `ABANDON`. ADR-074's exceptional generation-bound `AuthoringBindingRecovery` remains available when the External Control Plane has explicit recovery authority and exact state can be revalidated; that recovery supplies logical authority, never invented Git history.

### 5. `ruu` owns only exact observer registrations/artifacts that it created or previously adopted as its own

Observer installation, upgrade, repair and removal use expected-state/CAS semantics over `ruu`-owned artifacts.

`ruu` MUST NOT implicitly own or overwrite:

```text
core.hooksPath
an entire hook directory
an unrelated traditional hook
another configured hook entry
a third-party dispatcher configuration
```

An install/upgrade/removal operation may modify an observer registration only when the current exact state is absent where creation is authorized, or exactly matches an expected `ruu`-owned predecessor. Unexpected modification or replacement is an integrity/composition conflict, not permission to overwrite.

Uninstall likewise removes only exact owned registrations; foreign or unexpectedly modified state is left untouched and reported as conflict.

### 6. Composition must use a native or explicitly supported composition surface

When the selected Git/runtime exposes a multi-hook composition mechanism, `ruu` SHOULD use a uniquely named configured hook registration for `reference-transaction` rather than taking over the traditional hook slot. Current Git documentation from Git 2.54 describes configured `hook.<friendly-name>.event` / `.command` hooks and permits multiple configured hooks for the same event while retaining the traditional hook from the hook directory.

This modern path is preferred but is **not** the architectural definition of conformance and Git 2.54 is not made a universal V1 minimum by this ADR.

For a traditional single hook slot, V1 may establish coverage when the effective `reference-transaction` slot is absent or already exactly owned by `ruu`.

If the effective traditional hook or `core.hooksPath` is foreign and no explicitly supported composition adapter exists:

```text
foreign observer surface
+ no proven composition mechanism
→ do not overwrite / rename / wrap implicitly
→ observer coverage cannot become ACTIVE
→ managed-authoring admission blocks
```

`ruu` MUST NOT create a generic dispatcher whose purpose is to take custody of arbitrary foreign hooks. A third-party dispatcher may be supported only through an explicit adapter with demonstrated ordering/input/exit-status and lifecycle semantics sufficient for ADR-075.

### 7. Hook ordering is not managed authorization

Correctness MUST NOT require `ruu` to be the first or last participant in a composed hook event.

For a conforming composition surface:

- if another participant vetoes the transaction, the managed preparation resolves/recovers as aborted;
- if the transaction is able to commit, the `ruu` observer must have received the required pre-linearization occurrence and persisted the required preparation before commit;
- another participant's success cannot authorize a managed transition;
- another participant's failure cannot be misclassified as a committed managed disposition.

ADR-076's durable preparation plus exact-state recovery handles lost/duplicate outcome callbacks without relying on hook order.

### 8. Managed authoring admission requires functional observer attestation

Before the first managed write on a live authoring surface, repository provisioning/reactivation MUST establish `NativeObservationCoverage.status = ACTIVE` for the admitted mutation profile.

Attestation is functional rather than path-based. The implementation MUST have evidence sufficient to establish that the effective mutation path actually reaches the selected adapter and that the rejection-capable pre-linearization primitive can prevent a safe probe ref update when instructed to veto. Backend/adapter properties that cannot safely be proven by each runtime probe may be satisfied by versioned conformance evidence/smokes plus exact runtime profile matching.

The attestation may use reserved non-managed probe refs and MUST NOT create semantic ContributionUnit transitions.

The observer binding is repository-scoped shared infrastructure, not session/invocation ownership. Concurrent sessions and invocations observe/adopt the same already-correct binding rather than installing session-specific observers.

### 9. Clone, recreation, relocation/reactivation and relevant profile changes require re-establishment

Observer coverage is not Git history and MUST NOT be assumed to survive clone, repository recreation, a newly admitted locator, or another environment merely because the logical `repository_id` is unchanged.

Before live managed authoring resumes, the effective observer surface is re-established and re-attested idempotently.

A change that can invalidate the admitted path — including relevant Git/config scope, hook enablement/registration, effective hook path, ref backend, adapter binary/version, or mutation-engine capability profile — invalidates the current attestation until revalidated.

### 10. Continuous coverage is represented by coverage epochs

An `ACTIVE` attestation opens a coverage epoch. Discovery of observer loss, ambiguity, incompatible profile change, or another reason the admitted path can no longer be trusted closes/breaks that epoch. Repair plus successful re-attestation opens a new epoch.

```text
epoch E ACTIVE
     │
     X coverage becomes untrustworthy
     │
     └── E BROKEN/CLOSED

repair + re-attestation
     │
     └── epoch E+1 ACTIVE
```

A later healthy observer does not retroactively make the gap trustworthy. ADR-076 recovery may rely on continuous coverage only across an interval proven to belong to a trustworthy epoch.

A coverage epoch does **not** claim that no privileged/direct filesystem writer exists. It attests the admitted mutation path. An unwitnessed managed-ref change while the observer profile otherwise appears intact is a mutation-domain/integrity violation, not evidence that the missing causal event may be synthesized.

30.54 remains responsible for the exact failure/retry behavior when a required persistence step or coverage property fails during a native transaction.

### 11. Failure to establish coverage blocks managed authoring, not ordinary Git

If the required composition/attestation cannot be established:

```text
managed authoring admission/reactivation
→ BLOCKED_OBSERVER_COVERAGE
```

`ruu` MUST NOT obtain safety by silently replacing user/project hooks and MUST NOT require the human to maintain a recurring manual hook choreography.

The repository remains an ordinary Git repository. Existing unmanaged Git activity is not globally prohibited. The blocked state means only that `ruu` cannot promise live managed-authoring binding semantics on that surface until a conforming path exists.

## Consequences

- Backlog **30.53 is closed**.
- Observer coverage is repository-common for shared managed refs and is established before first managed write.
- Hook/config ownership remains non-destructive and expected-state guarded.
- Native/configured multi-hook composition is preferred where available; no minimum Git version is hard-coded merely for this convenience.
- Git core is the required V1 mutation-engine family; alternative engines need separately demonstrated adapters.
- IDEs/tools inherit conformance only by delegating relevant ref mutation to a conforming engine or by providing their own conforming adapter.
- Direct/uninstrumented ref writers are not prevented by fiction; unwitnessed mutation of a managed binding is an integrity failure and never silently acquires semantic meaning.
- Clone/recreation/reactivation re-establish observer coverage rather than trusting prior installation state.
- Continuous trust is recorded as coverage epochs; later repair does not erase a gap.
- 30.54 remains the concrete persistence/retry and coverage-gap failure-semantics decision; 30.55 remains the local-versus-remote/provider observation-boundary decision.

## Rejected alternatives

### Require Git >=2.54 as the architecture

Rejected. Git 2.54's configured multi-hook surface is a strong preferred implementation path, but ADR-075 deliberately defines capabilities rather than backend/version names. Older Git paths can be conforming when an uncontested traditional hook surface and the required adapter properties are demonstrated.

### Always wrap an existing traditional hook in a `ruu` dispatcher

Rejected. That makes `ruu` the lifecycle/order/error owner of arbitrary foreign hooks and silently expands the product into a generic hook manager.

### Overwrite `core.hooksPath` to force coverage

Rejected. It can bypass project/user tooling and assumes ownership of configuration outside the managed contract.

### Treat hook/config presence as sufficient coverage

Rejected. The effective mutation engine/configuration may ignore or bypass that surface. Coverage requires functional attestation of the admitted path.

### Support every Git implementation because it manipulates Git repositories

Rejected. Git core, libgit2, JGit and direct ref-store writers do not automatically expose identical hook/transaction semantics. Conformance is demonstrated per mutation engine/adapter profile.

### Prevent every nonconforming writer by owning the ref store

Rejected for V1. That would require a sandbox, privileged mediator, filesystem virtualization or equivalent storage-ownership boundary and would change `ruu` from a Git-coexisting reconciler into a Git storage authority.

### Reconstruct an unwitnessed managed-ref transition after the fact

Rejected by ADR-074/075/076. Final topology cannot reliably prove the missing causal distinction and must not manufacture `RENAME_CARRY_PREPARED` or `TERMINAL_REMOVAL_PREPARED` history.

## Git implementation references used by this decision

- Git `githooks` documentation: `reference-transaction`, including preparing/prepared/committed/aborted phases and hookdir/core.hooksPath behavior: https://git-scm.com/docs/githooks
- Git 2.54 release notes: configured multiple hooks and earlier `reference-transaction` preparing phase: https://github.com/git/git/blob/master/Documentation/RelNotes/2.54.0.adoc
- Git 2.54 `git-hook` documentation: configured hook discovery and traditional-hook composition: https://git-scm.com/docs/git-hook/2.54.0.html
- Git repository/worktree layout: shared `refs/*`, `$GIT_COMMON_DIR`, common hookdir for linked worktrees: https://git-scm.com/docs/git-worktree and https://git-scm.com/docs/gitrepository-layout
