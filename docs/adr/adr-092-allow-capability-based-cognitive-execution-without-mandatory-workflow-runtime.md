---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Allow capability-based cognitive execution without mandatory workflow runtime"
id: "ADR-092"
status: "accepted"
date: "2026-10-16"
decision_body_sha256: "50812dc30f07c68a64db66c99292dc6a437c838b777facbf64cba9a99468bdb2"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-039"
    - "ADR-042"
    - "ADR-070"
    - "ADR-078"
  supersedes: []
  confirms:
    - "ADR-041"
    - "ADR-064"
governs:
  - "Cognitive capability requirements without engine/vendor mandate"
  - "External execution and Ruu current-state convergence authority separation"
  - "Session continuity, asynchronous waits, and headless progression"
  - "Exact state recovery and cross-runtime conformance"
---

# ADR-092 — Allow capability-based cognitive execution without mandatory workflow runtime

## Context

Ruu's product outcome is hands-off Git-based version control for concurrent
agentic development. ADR-042 deliberately made its authoritative progression
a current-state reconciler rather than a step-workflow cursor. That decision
protects single-host fenced ownership, exact effects, global fixed-point
discovery, and crash recovery.

A new authored checkpoint may need semantic assistance to describe its work.
The relevant interactive main agent may be available for continuation, while
other installations or users may select an independent agent, a raw model
call, or a different external message-producing system (ADR-093).

Turnlock offers useful workflow and session-continuation primitives. However,
availability of one compatible realization does not establish that Turnlock
is uniquely required, or even that Ruu needs a general workflow engine.
A conforming harness may implement continuation itself; a direct model or
external service may handle a bounded request. Mandating Turnlock as part
of Ruu's Product Intent would prematurely prescribe implementation.

## Decision

### 1. Specify required cognitive capabilities, not a named runtime

Ruu MUST support the externally realized cognitive capabilities expressly
needed by its governed operations, initially the user-selectable
commit-message production contract of ADR-093.

Ruu MUST NOT require Turnlock, any other named workflow runtime, or a
general-purpose workflow engine as a universal prerequisite for ordinary
convergence or message generation. A deployment MAY use Turnlock, native
capabilities of a supported coding harness, another conforming execution
runtime, an eligible external service, or combinations of these mechanisms.
A runtime is a realization, not a normative Ruu product identity.

Supported ordinary invocation remains zero-preflight from the user's
perspective under ADR-078. The user does not have to manually operate a
separate orchestrator merely to checkpoint/converge work. An explicitly
selected external provider may of course require its own authorized setup.

### 2. Retain Ruu-owned reconciliation and authority

Ruu's ConvergenceEngine remains the authoritative top-level current-state
reconciler. It owns discovery/classification of the complete nonterminal
managed obligation universe, current Git/provider state observation,
transition legality, mutation claims/CAS, run fencing, journaled effects,
and exact-state adoption through the current global fixed point.

External execution mechanisms may schedule a request, perform an
admitted main-agent continuation, execute independent cognition, return
a result, or raise a convergence demand. They MUST NOT provide a second
Git reconciliation authority, reinterpret current exact state, or infer
semantic task/lifecycle/promotion authority from session or workflow
metadata. An external workflow's step position or replay is never
an authoritative Ruu recovery or adoption fact.

Simultaneous external requests still coalesce through the existing
single-host fenced Ruu reconciler. This ADR neither introduces a second
top-level scheduler nor requires Ruu to implement generic workflow
primitives solely because one runtime would have provided them.

### 3. Preserve real session continuity and user provider choice

When the contract calls for the main agent, the selected realization
MUST resume the actual admissible main-agent cognitive lineage of the
associated interactive authoring session, not substitute a new model
call or an independently spawned agent. The applicable session's
harness/integration supplies reachability and authorization;
the session triggering a global sweep is not assumed to own other work.

For other selected message producers, ADR-093 governs the open provider
contract and the absence of Git mutation authority. Ruu MUST NOT
silently downgrade an unavailable main-agent request to a different
provider or guess a substitute. Inadmissible or unavailable resources
remain localized obligations while unrelated legal progress continues.

### 4. Cognitive waits do not change exact Git recovery

A potentially unbounded model, main-agent, subagent, or service wait
MUST NOT retain the Ruu global run lock, a SQLite transaction, or an
unbounded ref-mutation claim. The exact request remains recoverable
and its result re-enters the reconciler through fresh exact-state,
handoff, policy, and expected-old revalidation.

Crash/retry reconstructs Ruu obligations and effects from authoritative
managed state plus Git/remote/provider observations. ADR-042's
Operation -> Attempt -> Observation -> Adoption semantics remain
normative. A workflow cursor, agent memory, timeout response, or
replayed completion MUST NOT replace those facts. ADR-093 separately
fixes OID-affecting message metadata before commit materialization.

Headless and unrelated mechanically legal obligations do not depend on
the reachability of any main agent or the availability of a workflow
engine. A missing selected cognitive resource cannot turn global
convergence into a session-owned mutex or universal wait.

### 5. Conformance is capability- and outcome-based

Any selected realization MUST demonstrate the relevant contract:
genuine session continuity when requested; explicit source-session
attribution; correct user-selected provider execution; bounded or
localized waits; no unauthorized ref/code mutation; one authoritative
Ruu reconciler; fresh exact-state adoption; and crash/retry recovery
without duplicate effects.

The existence of a Turnlock API, harness-native skill, agent-spawn API,
or model endpoint alone is not evidence of conformance.

## Consequences

- Turnlock is a candidate implementation/integration, not an
  obligatory Ruu runtime or product dependency.
- ADR-042's state-based reconciler, single-host run fence, effect journal,
  and exact-Git recovery remain intact. Its rejection of a step-workflow
  as *authoritative convergence truth* does not forbid an optional
  conforming workflow engine used as an execution mechanism.
- The External Control Plane remains a semantic authority role and may
  be realized by supported harness integrations without becoming a
  separately user-operated system.
- Selecting or changing an execution mechanism does not change Ruu's
  checkpoint, convergence, promotion, publication, or Git metadata truth.
- Qualification must cover at least a conforming session-continuation
  mechanism, an independent/headless message provider, unreachable
  cognitive resources, concurrent invocations, and recovery after
  workflow or process failure.

## Alternatives considered

### Mandate Turnlock for every Ruu installation

Rejected. It confuses a promising realization with the minimum
capabilities and invariants required by Ruu, and forecloses potentially
simpler conforming mechanisms.

### Require an abstract workflow engine regardless of implementation

Rejected. State-based reconciliation and a bounded external message
request do not by themselves prove the need for a workflow engine.

### Give an external workflow engine authoritative Git progression

Rejected. External workflow history cannot prove exact non-atomic
Git/SQLite/provider effects and cannot replace Ruu's state-based
reconciliation or managed adoption.
