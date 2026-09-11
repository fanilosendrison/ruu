# Ruu — Why Agentic Development Needs a Version-Control Coordination Layer

> **Status: non-normative architecture rationale.**
>
> This document explains the problem Ruu exists to solve, why that problem becomes structurally harder as coding agents move from isolated assistants to concurrent autonomous producers, how increasingly autonomous development loops turn manual Git coordination into a throughput bottleneck, and which guarantees appear to follow from that transition.
>
> It does **not** introduce new product requirements, states, identities, or authority rules. The normative sources remain [`../specification/ruu-spec.md`](../specification/ruu-spec.md), [`../specification/external-control-plane-contract.md`](../specification/external-control-plane-contract.md), and the accepted ADRs. If this document conflicts with those sources, the normative sources control.

## 1. The central thesis

Ruu is opinionated, but its core opinion is not:

> "This is our preferred way to use Git."

The stronger claim is:

> **Once software development allows multiple coding agents to author concurrently and independently, while removing the human from routine Git coordination, a minimum set of version-control guarantees becomes necessary.**

Two independent pressures lead to the same conclusion.

The first is **correctness under concurrency**:

> Without explicit isolation, exact state identity, controlled handoff, concurrency-safe reconciliation, and recoverable side effects, independently progressing agents can race, overwrite, duplicate, misattribute, or incorrectly publish state.

The second is **scalability of autonomy**:

> Even where a human could theoretically repair or coordinate those states manually, requiring that intervention makes the human part of the execution engine. As agent throughput grows, the human becomes the serialization point and eventually the throughput ceiling.

This second pressure matters because the direction of agentic development is not merely toward agents that write more code. It is toward **longer autonomous cycles**:

```text
goal
→ plan
→ implement
→ validate
→ review
→ correct
→ revalidate
→ checkpoint
→ converge
→ publish
→ continue
```

A loop is not meaningfully autonomous if an otherwise mechanical version-control transition routinely turns into:

```text
agentic workflow
→ Git state becomes non-trivial
→ STOP
→ human reconstructs branches / repos / freshness / dependencies
→ workflow resumes
```

The human may still be required for semantic judgment. The human should not be required merely because the version-control layer cannot safely determine or progress mechanically decidable state.

Those pressures imply a set of guarantees that include, at least:

- isolated mutable authoring surfaces;
- exact identity of the states being authored, handed off, integrated, and published;
- explicit and durable handoff/checkpoint boundaries;
- safe handling of stale concurrent work;
- mechanical reconciliation whenever semantics do not need to be invented;
- concurrency control for competing reconciliation and publication operations;
- idempotent, recoverable handling of side effects and retries;
- a distinction between mechanically decidable version-control work and semantic decisions that must remain outside the engine;
- correct behavior across all repositories and remote/provider surfaces involved in the work;
- preservation of ordinary Git interoperability.

Ruu chooses concrete mechanisms to provide these guarantees. Those mechanisms are not all logically inevitable. The **guarantees** are the more fundamental claim.

This distinction matters.

For example:

```text
dedicated Git worktrees
    = a concrete Ruu V1 mechanism

isolated mutable authoring surfaces
    = the underlying guarantee
```

Likewise:

```text
ContributionUnit / ConvergenceUnit
    = Ruu's current semantic model

bounded producer state + shared convergence identity
    = the more general problem that must be represented somehow
```

A competing design could use different primitives and still solve the same underlying problem. The question is not whether every implementation must look like Ruu. The question is whether it can remove routine human Git coordination **without providing equivalent guarantees**.

Ruu's architectural bet is that it cannot.

A concise form of the thesis is:

> **Correctness requires the guarantees. Scale requires that software, rather than a human operator, enforce them.**

---

## 2. Why traditional Git workflows worked

Traditional software development assumes humans are the primary producers and coordinators.

A simplified workflow looks like:

```text
developer
    ↓
branch / checkout
    ↓
commits
    ↓
pull request or direct integration
    ↓
human review / CI / merge
```

Git is extremely good at representing distributed history. What it does not attempt to provide is a complete orchestration model for many autonomous producers operating continuously against the same evolving development system.

Historically, humans supplied that missing orchestration.

A developer implicitly decides:

- when to create a branch;
- what work belongs on that branch;
- whether the branch is still current enough to continue;
- when to pull or fetch;
- when to rebase or merge;
- which conflicting change should be integrated first;
- whether a conflict is mechanical or semantic;
- whether a partially completed task should be committed;
- which repository changes belong together;
- whether a PR should be updated, replaced, stacked, or merged;
- when a remote operation should be retried;
- whether an observed state is stale;
- what to do after an interrupted operation.

The workflow may use automation, but the human remains the implicit coordination plane.

That is easy to overlook because Git does not label the human as a distributed-systems component.

But functionally, the human often is one.

---

## 3. Single-agent development does not force the problem

A coding agent does not by itself require a new version-control architecture.

Consider:

```text
human
  ↓
one coding agent
  ↓
one repository
  ↓
one branch
  ↓
human reviews and integrates
```

The coding agent may write thousands of lines, run tests, create commits, or open a pull request. Yet the surrounding coordination model can remain almost identical to the human-centric workflow.

The human still decides when the agent runs and often remains responsible for integration.

In that regime, ordinary Git plus a coding harness can be sufficient.

This is why it would be incorrect to claim:

> "Every use of a coding agent requires Ruu."

It does not.

The architectural pressure appears when **agentic development becomes concurrent and autonomous**.

---

## 4. The phase transition: from one producer to many

The important transition is not:

```text
human writes code
→ agent writes code
```

It is:

```text
one coordinated producer
→ many independently progressing producers
```

Suppose three coding sessions operate concurrently:

```text
Agent A ── state A
Agent B ── state B
Agent C ── state C
```

If all three share one mutable checkout, the first obvious problem is immediate: one agent can change the filesystem underneath another.

The natural response is isolation:

```text
Agent A ── isolated state A
Agent B ── isolated state B
Agent C ── isolated state C
```

That solves the **shared mutable filesystem** problem.

But it creates the next problem more clearly:

> **How do A, B, and C become one coherent evolving version-control state again?**

Isolation does not remove convergence. It makes convergence explicit.

This is the key architectural step.

---

## 5. Why isolation alone is not enough

Once producers are isolated, their states can advance independently.

While Agent A is working, Agent B may integrate new work. Agent C may advance another repository. A remote target may move. A review may complete. A provider submission may be merged. An earlier operation may fail halfway through and later be retried.

Therefore:

```text
state observed when authoring started
≠
state that necessarily exists when authoring finishes
```

Staleness becomes normal.

This is not an exceptional error condition. It is an ordinary consequence of concurrency.

A system can respond in two broad ways.

### 5.1 Serialize the agents

```text
A works
A integrates

B works
B integrates

C works
C integrates
```

This preserves a relatively simple Git model.

But it also discards much of the value of multi-agent execution.

### 5.2 Allow real concurrency

```text
A ────────┐
B ────────┼── independent progress
C ────────┘
```

Then the system must deal with independently evolving states.

At that point, convergence is no longer optional infrastructure. It is part of the execution model.

---

## 6. The guarantees that follow from real concurrency

The following chain is the core rationale behind Ruu.

### 6.1 Concurrent producers require isolated mutation

If two independent producers may edit the same mutable surface at the same time, neither can reason reliably about what state it owns.

Therefore concurrent authoring needs isolated mutation domains.

The implementation may be Git worktrees, virtual machines, containers, copy-on-write workspaces, or another mechanism. The implementation choice can vary.

The guarantee cannot:

> **One active producer must not have its mutable editing state silently changed by another producer or by background convergence.**

Ruu V1 realizes this through dedicated managed Git worktrees and mutation authority.

### 6.2 Isolation requires exact identity

Once several states coexist, "the current branch" is no longer enough as a system-wide truth.

The system must know exactly which state was:

- authored;
- validated;
- handed off;
- integrated;
- published;
- observed remotely.

Names are insufficient because names move.

Exact Git object identity, expected-state guards, and durable managed identity become necessary if the system is expected to reason mechanically.

The general guarantee is:

> **Every consequential transition must be bound to the exact state it is acting on, not merely to a mutable human-readable label.**

### 6.3 Independent progress requires a handoff boundary

A coding agent can be actively editing while the version-control engine wants to checkpoint or integrate its work.

Without a controlled boundary, the engine may capture one state while the producer continues mutating another.

Therefore the system needs a moment at which an exact editing state becomes transferable to the convergence engine.

This is the deeper purpose of a checkpoint/handoff boundary.

The particular Ruu protocol is specific. The requirement it serves is general:

> **The system must be able to identify exactly what work a producer is handing off without racing that producer's continued mutation.**

### 6.4 Concurrency makes stale work normal

If Agent A and Agent B begin from the same base, and B progresses first, A is stale relative to newer managed state.

Requiring the human to notice this and manually refresh A before every integration is equivalent to keeping the human as the coordination system.

If the goal is autonomous agentic development, routine stale-state handling must therefore move into software.

The guarantee becomes:

> **Staleness that is mechanically reconcilable must be treated as a normal convergence input, not as a routine reason to return coordination work to the human.**

### 6.5 Stale states require reconciliation

Once independent states exist, they must eventually be combined or rejected.

Where Git ancestry and content semantics determine a safe mechanical operation, the version-control system can perform it.

Where the correct result depends on product intent or authored meaning, the engine must not guess.

Therefore a reliable system needs a sharp boundary:

```text
mechanically decidable reconciliation
    → version-control engine

semantic choice
    → development system / authorized human or agent
```

This distinction prevents two opposite failures:

- escalating every ordinary Git divergence to the human;
- letting infrastructure invent product semantics.

### 6.6 Concurrent reconciliation requires coordination

Now suppose Agent A and Agent B both invoke convergence at almost the same time.

If the convergence engine itself has no concurrency protocol, the coordination problem has merely moved down one layer.

Competing operations may:

- read the same old target;
- both attempt to advance it;
- duplicate remote effects;
- overwrite managed metadata;
- race on internal refs;
- make contradictory conclusions from stale observations.

Therefore:

> **The convergence layer itself must be concurrency-safe.**

This is where mechanisms such as claims, compare-and-swap, fencing, exact expected state, and serialization of specific critical effects become necessary.

The user cannot be the mutex if the product promise is that the user need not coordinate concurrent sessions.

### 6.7 Real systems crash, retry, and lose observations

A version-control coordination engine performs effects across multiple failure domains:

```text
local filesystem
Git refs / object database
managed coordination state
remote Git transport
provider API
CI / review / merge queue state
```

A process may crash after the external effect occurred but before local metadata records success.

A network response may be lost.

An observation may arrive twice.

A retry may occur after partial progress.

Without explicit recovery and idempotence semantics, "just retry" can duplicate irreversible or provider-visible operations.

Therefore:

> **A production-grade agentic version-control layer must treat crash recovery, ambiguous outcomes, retries, and duplicate observations as normal system states.**

This is distributed-systems territory because the development workflow has become a distributed system.

### 6.8 Multi-repository work removes repository-local orchestration as the whole truth

Agents increasingly work across repository boundaries:

```text
frontend
backend
schema
infrastructure
SDK
```

One logical block of implementation may affect several of them.

If every repository is coordinated independently by the human, the human again becomes responsible for reconstructing the global work unit and publication order.

Therefore, once cross-repository agentic work is supported:

> **The system needs a durable way to relate repository-local version states to a larger work occurrence without pretending that Git itself provides atomic cross-repository commits.**

Ruu models cross-repository promotion as explicit grouped but repository-local progression rather than inventing false atomicity.

### 6.9 Publication must not become core version identity

GitHub, GitLab, and other providers expose useful workflow objects:

- pull requests;
- checks;
- reviews;
- merge queues;
- protected branches;
- provider-side merge results.

Those objects are important, but they are not the same thing as the exact source version-control state.

If provider objects become the fundamental identity of internal work, the system becomes unnecessarily coupled to one realization layer.

The more durable dependency direction is:

```text
agentic version-control semantics
        ↓
exact Git state
        ↓
optional provider realization
```

This lets a bare Git remote remain meaningful while still supporting rich provider workflows when required by policy.

### 6.10 Removing human coordination requires preserving semantic authority elsewhere

Automation is not the same as omniscience.

A version-control engine can determine facts such as:

- exact ancestry;
- whether a fast-forward is possible;
- whether an expected ref still points to an exact OID;
- whether a known merge can be constructed mechanically;
- whether a provider check passed;
- whether a target contains an exact promoted result.

It cannot infer, purely from Git state:

- whether a feature is conceptually complete;
- whether the implementation is good enough;
- whether a product requirement changed;
- which side of an ambiguous semantic conflict is correct.

Therefore the minimum architecture for autonomous Git coordination still requires an external semantic authority boundary.

This is why Ruu is hands-off about Git progression without trying to become the entire development system.

---

## 7. The key distinction: minimum guarantees versus Ruu mechanisms

The strongest defensible claim is **not** that every Ruu mechanism is inevitable.

Some current Ruu choices are deliberately opinionated implementation or architecture decisions, including:

- Git worktrees as the V1 isolated authoring substrate;
- ContributionUnit and ConvergenceUnit as first-class semantic identities;
- append-only/no-rebase behavior for internal managed history;
- particular managed-ref observation requirements;
- specific promotion-group and promotion-unit semantics;
- specific recovery and evidence models.

These choices may be replaced in another architecture by different mechanisms.

What should remain comparable is the guarantee each mechanism provides.

A useful review test for every Ruu invariant is therefore:

> **Which necessary property of concurrent autonomous agentic development does this invariant protect?**

If an invariant has no convincing answer, it may be accidental complexity rather than essential architecture.

Conversely, replacing a Ruu mechanism is safe only if the replacement preserves the guarantee the mechanism existed to provide.

This gives Ruu an important discipline:

```text
do not defend mechanisms because they are Ruu
defend guarantees because the product promise requires them
```

---

## 8. Why this problem is appearing now

The first generation of coding-agent workflows largely preserved the shape of human development:

```text
task
→ one agent
→ one branch
→ one PR
→ human integrates
```

That model can produce impressive coding results while leaving version-control coordination almost unchanged.

The next stage is different:

```text
one human
→ several coding agents
→ several isolated environments
→ concurrent implementation
```

The immediate tooling response is naturally to improve **parallel authoring**:

- isolated workspaces;
- worktrees;
- virtual machines;
- remote development environments;
- background agents;
- multiple simultaneous coding sessions.

Those are necessary advances.

But parallel authoring exposes the next bottleneck:

> **Independent production is useful only if its results can be reconciled reliably.**

At the same time, agentic systems are moving from isolated one-shot tasks toward **loops and workflows** in which the human intervenes less often:

```text
plan
→ implement
→ test
→ inspect
→ repair
→ re-test
→ integrate
→ continue
```

The more of that cycle becomes autonomous, the more damaging every mandatory manual Git transition becomes.

The industry can therefore automate production and local execution faster than it automates convergence. For a transitional period, the workflow may look like:

```text
agents are autonomous inside their work
Git coordination is still human-shaped
```

That is plausible temporarily.

It is much less plausible as the steady state if the number, speed, and autonomy of agents keep increasing.

The problem appears now because the bottleneck is moving. Once code generation and local task execution become cheap and parallel, the scarce resource shifts toward **safe integration, verification, and coordination of the resulting state**.

---

## 9. Autonomous loops and the human throughput ceiling

The decisive scaling problem is not simply that agents can work in parallel.

It is that the development system increasingly aims to run **without stopping for the human at every transition**.

Consider an autonomous development loop:

```text
objective
    ↓
planning
    ↓
implementation
    ↓
tests
    ↓
agentic review
    ↓
correction
    ↓
revalidation
    ↓
version-control handoff
    ↓
convergence / publication
    ↓
next work
```

If the version-control handoff routinely requires a human, then the loop is only partially autonomous:

```text
objective
→ implementation
→ validation
→ review
→ correction
→ Ruu-equivalent boundary
→ HUMAN
→ continue
```

The system's autonomy is bounded by that transition.

A useful general principle is:

> **The autonomy of an agentic development system is bounded by its least-autonomous required transition. If routine version-control convergence still requires a human, the human remains part of the execution engine and becomes the scaling bottleneck.**

### 9.1 Legitimate human judgment versus infrastructure-induced human work

"Human in the loop" can mean two very different things.

The first is legitimate semantic authority:

```text
Is this the product behavior we want?
Are these two implementations semantically compatible?
Should this architectural tradeoff be accepted?
Has the intended scope changed?
```

Those questions may deserve human or higher-level Development System judgment.

The second is operational work created by incomplete infrastructure:

```text
Which branch is stale?
Which session produced this state?
Did this merge already happen?
Which repository must move first?
Can this push be retried?
Which PR represents the current exact candidate?
Did another session advance the target?
```

Those are not inherently human questions.

If exact state and policy make them mechanically decidable, sending them to the human is not "keeping necessary judgment in the loop." It is exposing a missing coordination capability.

Ruu's role is not to eliminate semantic authority. It is to make sure the human does not re-enter the loop **only because Git progression itself cannot proceed safely**.

### 9.2 At scale, the human cannot maintain the global development state

With a handful of agents, a developer may still mentally track:

- which agent is working on which task;
- which worktree or branch belongs to which session;
- which base each session started from;
- which repository moved while another session was working;
- which changes belong together across repositories;
- what has been checkpointed;
- what has been integrated;
- what is stale;
- what is waiting on a provider;
- what failed and was retried;
- what was actually published.

With dozens of independently progressing sessions, this stops being a reasonable human responsibility.

The problem is not merely memory capacity. The required coordination state has properties that human working memory does not:

```text
durable
exact
queryable
causally attributable
race-aware
recoverable
transactionally guarded where necessary
```

A human can supervise such a system.

A human should not be its authoritative state store.

This is the same architectural transition seen elsewhere in computing: once concurrency and event volume exceed what an operator can reliably track, the state and coordination rules must become explicit machine-managed data.

### 9.3 The same bottleneck appears in code review

Agentic code production creates a parallel scalability problem in review.

If code output increases by an order of magnitude while every generated change still requires proportional human inspection, then human review throughput becomes the ceiling of the system.

The long-term response is not necessarily "remove humans from review." It is to move repeatable work toward:

```text
tests
static analysis
formal or property checks where applicable
independent review agents
specialized verification agents
policy gates
risk-based escalation
```

and reserve human attention for the decisions where human judgment has the highest value.

Version-control coordination has the same shape:

```text
human reviews every mechanically checkable detail
→ machine / agent verification + human escalation

human tracks every branch / repo / session / stale base
→ durable coordination + human escalation
```

The shared principle is:

> **Any required human activity whose workload grows approximately with agent output eventually limits the throughput of the agentic development system.**

Code review and version-control coordination are different responsibilities, but they face the same scaling law.

Ruu addresses the second one.

### 9.4 Human role: from operating the process to governing it

The target is not a development system with no human authority.

It is a system in which human attention moves upward.

Instead of routinely operating:

```text
merge this
refresh that
check which branch moved
repair this stale base
work out which PR depends on which
remember whether the remote effect already happened
```

the human can focus on:

```text
Is this the right architecture?
Is this behavior intended?
Is this risk acceptable?
Which product direction should we take?
Does this semantic conflict require a deliberate choice?
```

The transition can be summarized as:

```text
human as coordination plane
        ↓
machine-managed durable coordination

human as process operator
        ↓
human as semantic governor / supervisor
```

This is not merely ergonomic. It is necessary if one human is expected to supervise a development system whose production capacity substantially exceeds one human developer's own throughput.

### 9.5 The scaling argument

Consider the progression:

```text
1 human
↓
1 coding agent
```

Manual Git coordination is easy.

Then:

```text
1 human
↓
5 coding agents
```

The human begins to spend more time tracking:

- which agent changed what;
- which branch is stale;
- which PR depends on which;
- which repository needs to move first;
- which conflict is real;
- what can safely be retried.

Then:

```text
1 human
↓
20–50 coding agents
↓
many repositories
↓
continuous loops
```

At this point, asking the human to remain the Git scheduler defeats a major part of the automation.

Even a low manual-intervention rate becomes expensive when multiplied by many transitions.

Conceptually:

```text
100 version-control transitions / hour
× 5% requiring human intervention
= 5 human interruptions / hour
```

At 1,000 transitions per hour, the same rate becomes:

```text
1,000
× 5%
= 50 human interruptions / hour
```

The exact numbers are illustrative, not predictions. The important property is multiplicative: **the tolerated rate of mechanically unnecessary human intervention must fall as autonomous transition volume rises.**

The scarce resource is no longer merely code generation. It is **safe integration of independently produced state without proportional human coordination**.

This yields a qualitative scaling law:

> **As agent production parallelism and autonomous loop frequency increase, manual coordination cost grows until coordination itself must become software.**

Ruu is an attempt to build that software at the version-control layer.

---

## 10. The minimum viable autonomy criterion for Ruu

This rationale changes how a first usable Ruu should be scoped.

The wrong question is:

> "What is the smallest subset of the architecture that can perform a commit and push?"

A more useful question is:

> **What is the minimum set of guarantees required for an agentic development workflow to cross the version-control boundary and continue autonomously whenever the situation is mechanically resolvable?**

This is a stricter and more product-relevant criterion.

A capability can reasonably remain unsupported in an early release if the product does not yet claim that scenario.

But within the scenarios Ruu **does** claim to support, a missing guarantee is V1-critical when its absence routinely turns a mechanically resolvable state into:

```text
agentic workflow
→ Ruu
→ manual Git reconstruction or coordination
→ human intervention
```

The first usable release therefore does not need every future feature. It needs a coherent **autonomy envelope**.

Inside that envelope:

- supported concurrent authoring must be safely isolated;
- supported handoffs must bind exact state;
- supported stale-state cases must reconcile mechanically when possible;
- simultaneous supported invocations must not require a user mutex;
- supported retries and crashes must not create ambiguous duplicate progression;
- supported repository/provider routes must have enough observation and recovery to progress safely;
- semantic conflicts must be localized and escalated rather than guessed;
- the user must not reconstruct internal topology that Ruu can know durably.

Outside that envelope, Ruu may explicitly report an unsupported capability.

This distinction is important:

```text
UNSUPPORTED
= product does not yet claim this scenario

HUMAN REQUIRED FOR ROUTINE MECHANICS
= claimed autonomous scenario is missing a necessary guarantee
```

That gives the implementation effort a practical ordering principle:

> **Prioritize the guarantees that close the autonomous loop for the supported product path before expanding the number of supported paths.**

In other words, a narrow Ruu that is genuinely hands-off inside its declared envelope is more faithful to the product thesis than a broad Ruu that supports many workflows but frequently falls back to human Git coordination.

A compact formulation is:

> **The minimum viable Ruu is the smallest coherent implementation that removes the human from routine mechanically decidable version-control transitions for its explicitly supported workflow envelope.**

This criterion does not redefine the normative specification. It is a rationale for prioritizing implementation work against the existing product promise.

---

## 11. What is likely to happen to developer tooling

There is no guarantee that the future product called "Ruu" is inevitable.

There is a much stronger case that **Ruu-like guarantees** will appear somewhere if concurrent autonomous coding becomes normal.

Several architectural outcomes are plausible.

### 11.1 Coding harnesses absorb the coordination layer

A coding-agent platform could integrate:

- isolated authoring;
- exact handoff;
- stale-state reconciliation;
- Git operation fencing;
- publication;
- recovery.

From the user's perspective, the version-control layer might become nearly invisible inside the harness.

The semantics would still exist even if they were not sold as a separate VCS tool.

### 11.2 Git hosting providers absorb it

A provider could evolve from:

```text
host Git + manage PRs
```

toward:

```text
coordinate fleets of autonomous producers
+ reconcile their version states
+ govern publication
```

In that case, some Ruu-like semantics could move into GitHub-, GitLab-, or forge-native infrastructure.

The risk is coupling core version identity to provider objects. A well-factored implementation would still benefit from separating exact Git truth from provider workflow truth.

### 11.3 Agent-oriented Git tools evolve upward

Tools focused initially on worktrees, parallel branches, stacks, or agent sandboxes may progressively encounter the same next-order problems:

```text
parallel authoring
→ stale state
→ reconciliation
→ concurrent integration
→ recovery
→ provider realization
```

They may grow into a broader coordination layer.

### 11.4 A new VCS emerges

A future version-control system could be designed directly around autonomous producers instead of extending Git.

That is technically possible.

But Git has enormous interoperability value, mature object semantics, ubiquitous tooling, and existing repository history. A Git-based semantic layer therefore has a strong migration advantage.

Ruu explicitly takes that path:

> preserve Git as the native history/interoperability substrate, redesign the coordination semantics around it.

### 11.5 An independent agentic version-control layer becomes standard infrastructure

A tool like Ruu could remain independent of any one coding harness or hosting provider:

```text
Pi / Codex / Claude / future harnesses
                │
                ▼
      agentic version-control layer
                │
                ▼
               Git
                │
                ▼
 GitHub / GitLab / bare remote / others
```

This has an important architectural advantage: coding agents and providers can change without redefining the core convergence semantics.

That is the role Ruu currently aims to occupy.

---

## 12. Why the current gap is not evidence that the problem is unnecessary

It can appear strange that such a layer is not already standard if its guarantees are so fundamental.

But the timing is explainable.

Infrastructure usually follows the bottleneck that has become operationally painful.

For early coding agents, the dominant challenge was:

> Can an agent understand a codebase and produce useful code?

Then:

> Can it operate tools, run tests, and complete longer tasks?

Then:

> Can several agents run independently and in parallel?

Only after that succeeds at scale does the next question become unavoidable:

> How do all of those independently produced exact states converge safely without continuous human Git orchestration?

In other words, the absence of a mature standard coordination layer can be interpreted as evidence that the ecosystem is **early in the transition**, not that the coordination problem will disappear.

The tooling stack is moving upward through layers of the problem.

---

## 13. Why the eventual layer may initially look smaller than Ruu

The first widely adopted solution may not present itself as a full "agentic version-control system."

It may arrive as a series of apparently separate features:

```text
automatic worktree creation
automatic branch tracking
automatic refresh
conflict agents
merge queues
stack maintenance
retry-safe PR updates
cross-repo task grouping
agent session recovery
```

At low scale, these can look like independent conveniences.

As they accumulate, however, they begin to require shared semantics:

- What exact work occurrence do these changes belong to?
- Which producer owns this mutable state?
- Which observed version is authoritative?
- What may be retried?
- What is already durably completed?
- What changed externally?
- What may be reconciled mechanically?
- What requires semantic intervention?

At that point, a collection of conveniences has become a version-control coordination model, whether or not it is named as such.

Ruu makes that model explicit from the start.

---

## 14. The alternative: keep the human in the loop

There is one coherent future in which a Ruu-like layer remains unnecessary:

> Agentic development remains mostly serialized or human-coordinated.

For example:

```text
agent produces candidate
human reviews
human chooses next agent
human integrates
repeat
```

That workflow may remain useful for many teams indefinitely.

Ruu is not predicated on its disappearance.

The stronger need for Ruu appears under a more specific future:

```text
many agents
+ real concurrency
+ long-running independent sessions
+ overlapping repositories and code
+ minimal manual Git coordination
+ production-grade reliability
```

If that future does not materialize, the architectural pressure is weaker.

If it does, the pressure is structural.

---

## 15. Ruu's product bet

Ruu's bet can be stated compactly:

> **Coding agents turn software authoring into a concurrent production system. Autonomous development loops then make every routine manual version-control transition a break in that autonomy. Once production becomes sufficiently parallel and continuous, version control must evolve from a history tool plus implicit human coordination into a machine-managed coordination system that can safely converge independently produced Git state.**

The bet has both a correctness and a scalability component:

```text
Correctness:
without the guarantees, concurrent agents are unsafe.

Scalability:
without mechanizing those guarantees, humans become the throughput ceiling.
```

Ruu does not replace Git's object model.

It builds on it.

The intended layering is:

```text
Development System
(Pi / Codex / Claude / /go / human)
        │
        │ semantic authority + authoring
        ▼
Ruu
(agentic version-control semantics)
        │
        │ exact state / convergence / recovery
        ▼
Git
(native objects, refs, ancestry, merges)
        │
        ▼
remote / provider realization
```

The human may still make product decisions, review architecture, resolve genuinely semantic conflicts, or set repository policy.

What should disappear is the human as the routine mechanism that keeps concurrent Git state coherent.

That is the governing shift.

---

## 16. Design consequences for Ruu

This rationale suggests several useful tests for future Ruu decisions.

### 16.1 Every hard invariant should trace to a product guarantee

For any proposed invariant:

```text
invariant
→ protected guarantee
→ failure mode if removed
→ user-visible consequence
```

If that chain cannot be made explicit, the invariant deserves scrutiny.

### 16.2 Do not confuse current mechanisms with eternal semantics

A mechanism may be V1-specific.

The architecture should distinguish:

```text
required property
from
current realization
```

This keeps Ruu evolvable without weakening its guarantees.

### 16.3 Do not push routine coordination back to the user

A design that solves internal complexity by asking the user to:

- order sessions;
- select stale bases;
- enumerate all affected repositories;
- manually reconstruct work groups;
- act as a lock around Ruu;
- repeatedly repair mechanically resolvable divergence;

has violated the reason the layer exists.

### 16.4 Do not automate semantic judgment accidentally

The opposite failure is equally dangerous.

Hands-off Git convergence does not authorize Ruu to guess:

- task meaning;
- code quality;
- product intent;
- ambiguous conflict semantics.

Removing Git coordination from the human must not remove legitimate semantic authority.

### 16.5 Treat reliability properties as product properties

Crash recovery, idempotence, fencing, exact-state binding, and durable observation can look like implementation details.

For a concurrent autonomous system, they directly determine whether the user's work is safe.

They are therefore part of the product's effective correctness envelope.

### 16.6 Optimize first-release scope for closed autonomous loops

Implementation prioritization should distinguish feature breadth from autonomy depth.

Adding another provider, repository topology, or workflow shape is less important than making the already-supported path reliably progress without mechanically unnecessary human intervention.

For each supported path, ask:

```text
Can the Development System hand off exact work?
Can Ruu determine current state?
Can it reconcile what is mechanically resolvable?
Can it survive races, retries, and crashes?
Can it publish through the supported route?
Can the calling workflow continue without a human Git operator?
```

If the answer fails for a normal, mechanically decidable case, the supported autonomy loop is not yet closed.

This gives Ruu a useful release discipline:

> **Expand the autonomy envelope only after the existing envelope is coherent enough that humans supervise it rather than operate its routine Git transitions.**

---

## 17. What Ruu does not claim

This rationale should not be read as claiming that:

1. every developer using a coding agent needs Ruu;
2. every team must run many agents concurrently;
3. every concrete Ruu mechanism is logically unavoidable;
4. Git itself is obsolete;
5. pull requests or merge queues are obsolete;
6. semantic conflicts can always be resolved automatically;
7. repository policy should be replaced by one universal workflow;
8. Ruu's present architecture is the only possible implementation of these guarantees;
9. the future of agentic development is certain;
10. humans should be removed from semantic review or product governance;
11. an early Ruu release must support every conceivable repository, provider, or topology before it can be useful.

The narrower claim is stronger because it is testable:

> **If concurrent autonomous coding agents are allowed to produce overlapping Git state without routine human coordination, the system must provide the guarantees required to isolate, identify, hand off, reconcile, coordinate, recover, and safely publish that state.**

Ruu is one explicit architecture for doing so.

---

## 18. The long-term question

The important strategic question is therefore not:

> "Will every developer eventually use Ruu?"

Nor even:

> "Will the industry build a product with the same architecture and name?"

The more fundamental question is:

> **If coding becomes massively multi-agent, where will the missing coordination semantics live?**

They may live:

- inside coding harnesses;
- inside Git hosting providers;
- inside an evolved Git tool;
- inside a new VCS;
- inside an independent layer such as Ruu.

But if the system must support real parallelism while removing the human as the Git scheduler, those semantics cannot simply be absent.

Something has to own them.

Ruu's position is that they deserve to be treated as a coherent version-control problem rather than as a growing collection of unrelated agent-workflow patches.

---

## 19. Summary

The progression can be reduced to two connected causal chains.

The first is about **correctness**:

```text
coding agents
    ↓
multiple coding agents
    ↓
concurrent independent authoring
    ↓
isolated mutable states
    ↓
routine divergence and staleness
    ↓
need for exact handoff
    ↓
need for mechanical reconciliation
    ↓
competing convergence operations
    ↓
need for CAS / fencing / idempotence / recovery
    ↓
multi-repository and remote/provider effects
    ↓
need for durable global coordination semantics
    ↓
agentic version control
```

The second is about **autonomy and scale**:

```text
faster agentic production
    ↓
more concurrent sessions
    ↓
more repositories / branches / exact states
    ↓
more development loops and transitions
    ↓
human can no longer track or operate every transition
    ↓
manual coordination becomes the throughput ceiling
    ↓
mechanically decidable coordination must move into software
```

This is analogous to the pressure appearing in code review.

As agent output rises, exhaustive proportional human review becomes a bottleneck, so verification increasingly needs tests, tools, review agents, policy gates, and selective human escalation.

Version-control coordination faces the same scaling constraint:

```text
review bottleneck
→ do not require a human to inspect every mechanically checkable fact

coordination bottleneck
→ do not require a human to track every mechanically decidable state transition
```

The two responsibilities remain distinct. Ruu addresses version-control coordination, not semantic code review.

The core architectural argument behind Ruu is therefore not that Git is inadequate as a history substrate.

It is that **Git plus implicit human coordination is not the final coordination model for large-scale concurrent autonomous agentic development**.

A human may remain the semantic governor of the system. The human should not remain its branch tracker, stale-state detector, retry coordinator, merge scheduler, or authoritative memory of what happened across dozens of concurrent sessions.

If agentic development remains mostly sequential and human-operated, ordinary Git workflows may continue to be sufficient.

If agentic development becomes genuinely concurrent, loop-driven, autonomous, multi-repository, and production-grade, then a coordination layer with Ruu-like guarantees becomes increasingly difficult to avoid.

The exact mechanisms may change.

The strategic requirement is that mechanically decidable version-control progression no longer scale linearly with human attention.

A compact formulation is:

> **Correctness requires explicit guarantees for concurrent state. Autonomy requires those guarantees to be enforced by software. Scale requires the human to supervise the system rather than operate every transition.**

That is the problem Ruu is designed to solve.

---

## Normative anchors

This document is explanatory. The current architecture is defined by the normative corpus, especially:

- [`../specification/ruu-spec.md`](../specification/ruu-spec.md), especially Product Intent §0;
- [`../specification/external-control-plane-contract.md`](../specification/external-control-plane-contract.md);
- [ADR-001 — isolate concurrent work production with Git worktrees](../adr/adr-001-isolate-concurrent-work-production-with-git-worktrees.md);
- [ADR-005 — coordinate simultaneous convergers with claims and CAS](../adr/adr-005-coordinate-simultaneous-convergers-with-fine-grained-claims-and-cas.md);
- [ADR-016 — append-only/no-rebase V1 reconciliation](../adr/adr-016-use-an-append-only-no-rebase-v1-reconciliation-strategy.md);
- [ADR-036 — make every invocation global over nonterminal managed obligations](../adr/adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md);
- [ADR-041 — coalesce convergence demands under a fenced executor](../adr/adr-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md);
- [ADR-057 — externalize development verification and model Ruu as Git progression](../adr/adr-057-externalize-development-verification-and-model-ruu-as-state-dependent-git-progression.md);
- [ADR-064 — bind pre-commit readiness by frozen mutation handoff](../adr/adr-064-bind-pre-commit-readiness-by-frozen-mutation-handoff.md);
- [ADR-070 — governing hands-off concurrent product intent](../adr/adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md);
- [ADR-073 — Git worktrees as the V1 authoring isolation substrate](../adr/adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md);
- [ADR-078 — zero-preflight coding-harness integration](../adr/adr-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md);
- [ADR-080 — separate local Git causality, remote Git state, and provider workflow evidence](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md).
