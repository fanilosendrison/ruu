---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "product-rationale"
domain: "ruu"
severity: "informational"
name: "Ruu Product Rationale"
---

# Ruu — Product Rationale

> **Status and authority:** This document is non-normative. It explains user
> value, motivation, and product rationale behind Ruu's existing Product Intent.
> It creates no product promise, invariant, obligation, architecture, mechanism,
> interface, representation, implementation requirement, or verification claim.
> The normative [Ruu specification](../specification/ruu-spec.md), the
> [External Control Plane contract](../specification/external-control-plane-contract.md),
> and accepted [ADRs](../adr/README.md), including their amendments, remain
> authoritative for their respective responsibilities. If this rationale
> conflicts with those sources, the authoritative sources control. This
> rationale is not an independent input to normative derivation and does not
> claim that described capabilities are already implemented or shipped.

## Intended user and unresolved problem

Ruu is intended for users building software with coding agents or agentic
development systems that can produce multiple concurrent streams of code.

A user may already be able to launch several agents, give them separate
workspaces, create branches or worktrees, and ask them to implement different
parts of a system in parallel.

The unresolved problem is what happens to version-control coordination as the
number and independence of those producers increase.

Without a system taking responsibility for that coordination, the user, the
main coding agent, or a bespoke orchestration layer must still reason about
questions such as:

```text
which producer may mutate which checkout?
which branch or workspace owns which work?
which work must wait for other work?
which state is stale?
which state should another contribution consume?
in what order should branches be integrated?
which repositories belong to the same logical handoff?
what happened if a push or provider operation timed out?
what should be retried after a crash?
which mechanically compatible changes can be composed automatically?
which conflict actually requires semantic authoring?
```

The problem is therefore not simply concurrent code generation.

It is making concurrent code production compatible with trustworthy,
recoverable, low-supervision version progression.

## Current pain

Without Ruu or an equivalent coordination layer, aggressive agentic concurrency
usually pushes the user toward one of two compensating strategies.

The first is preventive coordination:

```text
agent A owns this area
agent B should wait
do not touch that file yet
base this branch on that branch
merge this work before starting the next work
```

This reduces the amount of concurrency in order to keep Git manageable.

The second is bespoke orchestration:

```text
create workspaces
track branch ownership
track dependencies
refresh stale branches
choose merge order
handle retries
coordinate multiple repositories
publish exact heads
recover from partial effects
clean up after completion
```

The work can be implemented in scripts or in a larger agent framework, but the
coordination responsibility still exists. The user or system builder has
effectively begun constructing a specialized concurrent version-control layer.

At small scale this burden can remain tolerable. At larger agent counts it can
grow with the number of simultaneous producers, overlaps, repositories,
dependencies, crashes, retries, and publication boundaries.

The intended reduction is in this version-coordination burden.

## Intended user outcome

The Product Intent establishes a different responsibility split:

```text
user / Development System
→ decides what software should be produced
→ performs semantic development work
→ decides when a block of work is ready to cross a Git boundary

Ruu
→ owns rigorous version-control progression after the boundary
→ checkpoints exact managed work
→ integrates mechanically compatible state
→ reconciles stale state
→ progresses global managed obligations
→ publishes through the applicable Git/provider route
→ recovers from crashes, retries, and ambiguous effects

user / Development System
→ resumes semantic authorship only where mechanical progression is insufficient
```

For supported coding harnesses, the intended ordinary experience remains
approximately:

```text
install Ruu once

open the coding harness
→ ask the agent to implement
→ author normally

when the current work should cross a Git boundary:
    ruu
```

The user should not need to reconstruct Ruu's internal topology in order to
obtain that result.

> **Ruu lets the user increase the number of concurrent code producers without
> requiring a proportional increase in human Git coordination.**

This sentence explains the existing Product Intent. It does not replace it.

## Example: several coding agents working at once

Consider one user running several concurrent coding agents.

```text
agent A
→ changes parser code

agent B
→ changes the same parser code and the CLI

agent C
→ changes tests

agent D
→ changes another repository required by the same broader work
```

The useful concurrency is real. Preventing all overlap would throw much of it
away.

The desired relationship is instead:

```text
independent isolated authoring
        ↓
exact managed handoff
        ↓
Ruu observes current state
        ↓
mechanically compatible work converges
        ↓
unrelated progress continues
        ↓
only genuinely semantic incompatibility returns to authored work
```

The example does not establish a particular workspace substrate, number of
ContributionUnits, conflict algorithm, scheduling policy, or implementation
mechanism.

Its purpose is to explain the user-level difference:

```text
concurrency
≠
manual Git scheduling obligation
```

## Concurrent overlap becomes a normal input

Traditional workflows often reduce Git difficulty by reducing overlap in
advance.

Ruu's Product Intent instead allows overlapping work to exist and treats stale
or concurrent managed state as ordinary convergence input.

This changes the default question from:

```text
Can another agent safely start here?
```

toward:

```text
Can its resulting exact state later be mechanically reconciled?
```

If the answer is mechanically determinable, Ruu should perform the required
version-control work.

If the answer depends on product meaning or semantic authorship, Ruu must not
guess. The Development System receives the exact unresolved obligation.

The product value is therefore not the elimination of real semantic conflicts.

It is the elimination of avoidable human coordination around conflicts that do
not require semantic judgment.

## Stale work stops being an exceptional workflow failure

Concurrent producers naturally become stale relative to one another.

For example:

```text
M0
├── agent A starts
└── agent B starts

agent A progresses first
→ shared managed state advances

agent B finishes later
→ B is now stale relative to newer managed state
```

Without a convergence layer, the user or orchestrator often has to restore
freshness explicitly before B can progress.

Ruu's intended model treats this situation as expected. Exact Git ancestry,
managed state, current authority, and applicable policy determine what can be
advanced mechanically.

The user should not have to act as a manual refresh service for concurrent
agents merely because their starting points aged while useful work was being
done elsewhere.

## Continuous convergence keeps concurrent work fresh

Ruu's concurrency value is not limited to allowing several producers to work
safely at the same time.

A second source of value is how quickly useful progress from one producer can
become part of the exact version state available to later work.

A batch-oriented concurrent workflow can look like:

```text
agent A starts from S0
agent B starts from S0
agent C starts from S0

A works for a long period
B works for a long period
C works for a long period

only later:
A + B + C
→ integration
```

The producers execute concurrently, but the states they consume increasingly
diverge from one another while useful work remains isolated.

Ruu's accepted semantics support a different progression.

A valid authoritative checkpoint does not wait for its ContributionUnit to be
closed merely because more work may arrive later. It is advanced toward its
bound ConvergenceUnit at the earliest mechanically safe opportunity.

Conceptually:

```text
shared exact state S0

agent A produces A1
        ↓
A1 converges as early as mechanically safe
        ↓
shared exact state S1

agent B later checkpoints B1
        ↓
B1 is reconciled against the newer managed reality
        ↓
shared exact state S2

agent A remains active and later produces A2
        ↓
A2 converges
        ↓
shared exact state S3

agent C later crosses a managed boundary
        ↓
its work is reconciled against the latest applicable exact state
```

The important property is that contribution histories may therefore become
interleaved through convergence:

```text
A1
  ↓
    B1
      ↓
A2
  ↓
      C1
        ↓
    B2
```

rather than remaining isolated until one final integration event.

This reduces avoidable divergence between concurrently produced work.

The shorter the delay between:

```text
useful authoritative checkpoint exists
```

and:

```text
that checkpoint has been incorporated into the applicable converged state
```

the sooner subsequent authoring can benefit from work that has already been
safely produced elsewhere.

The intended causal chain is:

```text
useful intermediate checkpoints
        ↓
earlier mechanical convergence
        ↓
newer exact state becomes available sooner
        ↓
subsequent work can consume fresher safe state
        ↓
less avoidable divergence accumulates
        ↓
less late reconciliation is required
```

This is why eager checkpoint integration is part of the product value rather
than merely an internal implementation detail.

> **Ruu aims to minimize avoidable version-state staleness between concurrent
> producers by converging authoritative checkpoints as early as mechanically
> safe.**

This does not mean that Ruu continuously rewrites every active producer's
authoring surface to the latest shared state.

Active authoring surfaces remain protected by their existing mutation-authority
boundaries. Ruu does not surprise-rebase or otherwise mutate producer-owned
work merely to maximize freshness.

The distinction is:

```text
maximize the freshness of safely available exact state
!=
silently make every active producer follow a moving tip
```

Freshness is therefore constrained by the same exactness, authority, isolation,
dependency, and reconciliation rules that govern the rest of Ruu.

Where a Development System selects an exact authoring dependency, that exact
dependency remains authoritative for the consumer; a later source checkpoint
does not silently replace it. A newer safe state may become available for a
later authorized authoring boundary or dependency choice, but availability is
not implicit rebinding.

The intended result is not merely more parallel work.

It is concurrent work whose independently produced progress can repeatedly
re-enter the shared version state, so later work spends less time developing
against avoidably stale versions of what the other producers have already made
safe.

## Invocation order stops being the user's correctness mechanism

A user with several coding sessions should not need to answer:

```text
Which session must invoke first?
Is another convergence already running?
Should I wait before invoking?
Will the calls collide?
```

Ruu separates the work-bearing occurrence from convergence demand and drives a
global reconciliation sweep over known nonterminal managed obligations.

The user-level consequence is that invocation order need not become a human
mutex.

This does not mean every operation can execute simultaneously or that internal
serialization disappears. It means the system, rather than the user, owns the
coordination required by the accepted semantics.

## Multi-repository work no longer requires caller-managed Git choreography

A single logical development occurrence may touch several repositories.

Without a system-level model, the caller often has to retain and coordinate a
relationship such as:

```text
frontend branch
+
backend branch
+
schema branch
=
one logical piece of work
```

and then decide how each branch should advance.

Ruu keeps repository-local Git state repository-local while giving the
coordination domain explicit identities for the logical handoff, convergence,
promotion grouping, and repository-local shipment state.

The intended user benefit is that multi-repository work can remain one logical
development occurrence without requiring the user to manually script a global
Git transaction or force all repositories through the same publication route.

A blocked repository need not automatically freeze unrelated progress.

## Useful in-flight work does not have to mean completed work

A producer may create an exact useful native version before its broader
contribution is complete.

Where the Development System explicitly selects an exact supported dependency,
Ruu's AuthoringDependency model allows another ContributionUnit to consume the
selected exact commit without silently following the producer's later mutable
state.

Conceptually:

```text
producer creates A1
producer continues toward A2, A3, ...

consumer explicitly requires producer @ A1
        ↓
A1 remains the consumed version
        ↓
consumer can author against that exact version
```

This separates:

```text
an exact version exists and is usable
```

from:

```text
the producing contribution is finished
```

The distinction becomes increasingly important as agentic workflows become more
parallel.

Ruu does not infer semantic dependencies from timing, ancestry, filenames, or
agent identity. The Development System retains authority for selecting the
dependency.

## Crash and retry stop requiring conversational reconstruction

Git and provider effects cross process, filesystem, network, and remote-system
boundaries.

A process can therefore fail after an effect occurred but before the caller
learned or durably adopted its outcome.

For example:

```text
request remote mutation
        ↓
remote effect succeeds
        ↓
acknowledgement is lost or process crashes
```

The next execution must not rely on a conversational guess about whether the
operation happened.

Ruu's accepted architecture distinguishes managed operation intent, physical
attempt, authoritative observation, and semantic adoption. Exactly-once
correctness applies to authoritative managed adoption rather than requiring
exactly-once delivery of every observation.

The intended user outcome is that process death, duplicate wakeups, replayed
observations, and ambiguous network outcomes can be reconciled from durable
identity and exact current state instead of routinely becoming manual recovery
work.

## Industrialization: version coordination becomes infrastructure

A coding-agent workflow can be viewed as producing two classes of work:

```text
semantic software-development work
+
version-coordination work created by concurrent production
```

The first requires the Development System and its agents.

The second includes recurring mechanics such as isolation, exact checkpoint
identity, synchronization, convergence, stale-state handling, publication,
recovery, and retry.

Ruu's industrialization opportunity is to make the second class a reusable
system capability instead of rebuilding it inside every agentic workflow.

```text
coding workflow
→ produces software

Ruu
→ provides the reusable version-control substrate
  for concurrent production
```

A workflow builder can therefore spend more design effort on how useful software
is produced and less on reconstructing concurrent Git mechanics.

## Scalability: agent count without proportional coordination work

### Human-attention scalability

If each additional producer requires the user to coordinate one more branch,
workspace, refresh cycle, merge order, and retry path, increasing agent count
also increases supervisory work.

Ruu is intended to absorb the mechanically governable part of that increase.

This does not remove human or agent attention from genuinely semantic
incompatibilities, product decisions, review judgments, or other external
responsibilities.

### Concurrency scalability

Several producers may work concurrently against overlapping repository state
without sharing one mutable checkout.

The number of producers can therefore grow without requiring preventive file
reservation or branch ownership to be the principal correctness mechanism.

Concurrency scalability is therefore not only the ability to run more
producers simultaneously. It also depends on limiting how far those producers
unnecessarily drift apart while they run. Eager convergence lets independently
produced safe progress re-enter the managed state repeatedly, so increasing
parallelism does not inherently require waiting until the end of each
contribution before other work can benefit from it.

This is not a promise of unlimited throughput or conflict-free development.
Real semantic incompatibilities and physical resource limits remain.

### Workflow-complexity scalability

As a workflow spans more repositories, dependencies, publication routes, or
concurrent sessions, version progression does not have to be reimplemented as a
new caller-specific sequence.

The same state-dependent convergence semantics can continue to operate over the
larger managed domain.

## Capabilities requiring Ruu or an equivalent system

The necessity here concerns system capability, not the Ruu brand.

Individual pieces of the problem can be addressed with Git branches, worktrees,
scripts, locks, queues, provider APIs, databases, workflow engines, or bespoke
agent orchestration.

But a system that promises the complete user outcome must provide equivalent
responsibilities somewhere.

### Safe aggressive concurrency without preventive ownership

If several producers may independently modify overlapping repository state,
correctness cannot depend solely on users agreeing in advance who owns each file
or branch.

There must be an isolation, identity, authority, and reconciliation model.

An equivalent system may implement those responsibilities differently. Merely
launching several workers does not provide them.

### Continuous interleaving of concurrent contribution progress

Isolation alone can let several producers work at once while their version
states become increasingly stale relative to one another.

A system that wants concurrent producers to benefit repeatedly from one
another's completed safe increments must additionally provide an equivalent
mechanism for:

```text
authoritative intermediate checkpoints
+
early safe convergence
+
exact current-state reconciliation
+
continued production after earlier checkpoints have integrated
```

Without that capability, concurrent work can still be safe, but its integration
remains substantially batch-oriented: useful progress from one producer stays
unavailable to the others until a later branch, task, PR, or final merge
boundary.

The necessity concerns the capability, not the Ruu name. Another system that
provides equivalent continuous exact-state convergence can provide the same
property.

### State-dependent global convergence

A caller-local script can perform a known sequence.

A continuously changing coordination domain requires something able to
re-observe current authoritative state, determine which obligations are now
progressable, safely apply effects, and repeat until the current fixed point.

Without an equivalent reconciler, this responsibility falls back to callers,
workflow code, or users.

### Durable exact logical boundaries

Branches, processes, sessions, worktrees, tasks, commits, handoffs, convergence
scopes, and publication occurrences are not interchangeable identities.

A system that must recover and coordinate concurrent work needs durable exact
identities and authority boundaries for the semantic distinctions it relies on.

Git object identity alone does not establish those higher-level relationships.

### Recovery across non-atomic Git and provider effects

Once local state, remote Git, provider APIs, durable coordination state, and
process lifetime participate in one logical progression, no single transaction
covers all effects.

Crash-safe operation therefore requires explicit recovery semantics,
authoritative re-observation, fencing, and idempotent adoption or an equivalent
mechanism.

This property cannot be obtained merely by retrying every failed command.

### Exact consumption of in-flight versions

If downstream work may safely consume an exact version from work that is still
active, the system must distinguish:

```text
selected exact version
```

from:

```text
whatever the producer happens to contain later
```

and must preserve the required object and authority relationship.

A branch name or "latest" pointer alone cannot provide that invariant.

### Hands-off invocation without hidden caller topology

An interface such as:

```text
implement
→ ruu
```

is trustworthy only if the hidden topology, concurrency, stale-state,
publication, and recovery responsibilities are actually owned somewhere.

Otherwise the simplicity is superficial and the caller still has to reconstruct
those concerns when something diverges.

## Why Git, worktrees, branches, and pull requests are not sufficient by themselves

Git provides the essential native substrate used by Ruu.

It can establish exact objects, refs, ancestry, merges, and repository history.

Worktrees can provide useful local isolation.

Branches can provide named lines of history.

GitHub, GitLab, and other providers can provide remote hosting, submissions,
review, checks, queues, permissions, and governance.

Those capabilities remain valuable and Ruu is designed to coexist with them.

By themselves, however, they do not establish Ruu's managed relationships such
as:

```text
which isolated contribution belongs to which convergence scope
which exact handoff belongs to one logical invocation
which durable dependency was semantically selected
which current authority permits a managed mutation
which effect has been semantically adopted
which nonterminal managed obligations still exist
which stale state can be mechanically reconciled now
which semantic conflict must return to the Development System
```

The distinction is one of responsibility.

Git supplies exact version-control primitives.

Ruu supplies the additional coordination semantics required by the accepted
agentic-concurrency Product Intent.

## Relationship to Ruu Cloud

Ruu Core's responsibility is complete at single-host coordination-domain scale.

The separate Ruu Cloud Product Intent expands the coordination domain across
multiple independent hosts and a development team.

Cloud value must not be created by withholding fundamental correctness,
evidence, inspection, or recovery properties from Core.

Ruu Cloud is maintained as a separate product repository with its own Product
Intent and Product Rationale. This Core rationale does not derive Cloud
architecture or make Cloud a requirement for Core use.

Ruu Cloud extends the same continuous-convergence value across independent
hosts. Core reduces avoidable version-state staleness inside one host-local
coordination domain; Cloud extends the domain in which safely converged state
can become available, while preserving the same rule that freshness remains
subordinate to exactness, authority, and explicit dependency semantics.

## Explicit boundaries and non-goals

This rationale does not imply that Ruu:

- decides product intent;
- determines whether code is semantically correct;
- decides whether a feature is good enough;
- replaces the Development System;
- replaces coding agents;
- chooses task priority;
- provides project management;
- eliminates genuine semantic conflicts;
- makes all concurrent changes mergeable;
- guarantees unlimited parallelism;
- replaces Git;
- replaces GitHub, GitLab, or provider governance;
- requires a particular authoring-surface realization;
- requires worktrees, VMs, containers, or another particular isolation
  substrate;
- supplies a general security sandbox;
- guarantees bug-free software;
- automatically rebases active producer-owned authoring surfaces;
- automatically moves every active producer to the newest available state;
- silently replaces an exact AuthoringDependency when its producer advances;
- guarantees that every checkpoint is immediately consumable; or
- turns provider objects into core version identity.

This rationale selects no implementation language, storage engine, scheduler,
protocol, provider, public API, CLI layout, database topology, or deployment
architecture.

## Reading basis

The explanatory basis is the existing Product Intent in
[`ruu-spec.md`](../specification/ruu-spec.md), the External Control Plane
contract, and the accepted ADRs, especially the decisions governing hands-off
concurrent invocation, eager checkpoint integration, zero-preflight harness
integration, authoring surfaces, global convergence, exact dependencies,
observation authority, recovery, and promotion.

> **Ruu aims to make aggressive concurrent agentic software production a normal
> version-control workload rather than a Git-coordination problem the user must
> manually schedule and repair. Its continuous-convergence model additionally
> makes safely produced progress available for reuse as early as the governing
> exactness, authority, isolation, and dependency boundaries permit.**
