---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make commit-message providers user-selectable with main-agent default"
id: "ADR-093"
status: "accepted"
date: "2026-10-16"
decision_body_sha256: "ed888630f348371b46c41a58b4c30160ecb3a901e222eb25f058d9e5592a781e"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-042"
    - "ADR-048"
    - "ADR-078"
  amends:
    - "ADR-059"
    - "ADR-064"
    - "ADR-070"
  supersedes: []
  confirms: []
governs:
  - "Main-agent-first commit-message generation"
  - "Open external message provider capability and user selection"
  - "Candidate-bound metadata freezing and retry recovery"
  - "Deterministic technical-commit and existing-commit preservation"
---

# ADR-093 — Make commit-message providers user-selectable with main-agent default

## Context

Ruu materializes ordinary Git commits for frozen dirty-surface
checkpoints; it can adopt an existing clean native commit unchanged,
and also synthesize mechanical reconciliation and promotion commits.
ADR-059 deliberately excludes commit metadata from pre-commit
candidate identity. The existing commit-engine contract only says
an LLM may generate a message and has no ref-mutation authority.

Users should not manually write routine messages. The actual
main agent of a supported interactive authoring session is the
preferred default because it has relevant development context,
but users must be free to select another generator, including
an unrelated external service.

## Decision

### 1. Open, user-configurable provider capability

When creating a new authored dirty-surface checkpoint commit,
Ruu obtains the message from a selected commit-message-producing
capability. Compatible realizations include continuation of the
main coding agent, an independent subagent, a bounded raw LLM
inference, or ANY user-connected external service/system able
to return the required message. This is an open capability
contract, not a closed provider taxonomy or vendor/model list.

Users MUST be able to select and configure a non-default
provider without changing Ruu products. The precise storage,
wire protocol, and preference-scope precedence remain
implementation design. Selection grants no Git mutation,
semantic code authoring, provider governance, or publication
authority.

### 2. The associated main agent is the interactive default

For a dirty checkpoint associated with an admitted and
reachable supported interactive authoring session, Ruu MUST
use that session's actual continuing main agent by default,
unless the user has chosen another provider. A conforming
harness-native continuation, Turnlock handoff, or another
mechanism may realize this default; no named runtime is
required. Spawning a fresh agent or model is not equivalent.

A global sweep may be triggered by another session. Trigger
origin, CWD, Git ancestry, or branch names MUST NOT silently
reassign a candidate's session association or use the
triggering session's main agent to describe unrelated work.
The supported integration/ECP owns contextual association.

For headless work or an unreachable/prohibited main-agent
continuation, Ruu uses an explicitly user-selected eligible
alternative/fallback when one is configured. Otherwise
it records a localized recoverable missing-message
prerequisite and progresses unrelated work. It MUST NOT
fabricate a main-agent continuation or silently switch
to an unrelated default model.

### 3. Provider receives context, not authority

The request is bound to ADR-059's exact repository identity,
object format, parent OID, tree OID, and checkpoint candidate
identity. Ruu can expose read-only exact diff/tree facts and
only work-intent context authorized/supplied by the ECP.
The provider returns message text, not file mutations,
parents, target selection, author/committer identity,
ref updates, or proof of code correctness/completion.

Ruu may enforce required message representation/format.
The generated text is never authoritative semantic
validation, source authorship evidence, or Git truth.

### 4. Freeze OID-affecting metadata before effect

The selected message and all other OID-affecting checkpoint
commit metadata MUST be durably fixed for the exact
candidate/operation before commit creation. A retry of
that operation MUST NOT re-query a stochastic provider
to replace the decision. After a crash, Ruu first
observes/reconciles previously caused commit effects
under ADR-042 before any new causal attempt.

Message generation MUST NOT hold the global Ruu run lock
or an unbounded Git mutation claim. The authoring surface
remains under the ADR-064 frozen handoff; on return,
Ruu reacquires/revalidates exact parent/tree, current
claim, and mutation authority. A drifted candidate
cannot be committed with stale message binding.

Provider failure, refusal, timeout, invalid response,
or absence remains a localized nonterminal prerequisite.
It does not silently change providers, produce an empty
commit, or block unrelated mechanically progressable work.

### 5. Preserve native and deterministic metadata

Clean native-tip checkpoint adoption reuses the existing
commit with its original OID, message, and metadata;
Ruu does not rewrite it for prose quality.

Mechanical reconciliation commits and canonical synthetic
PromotionUnit commits retain their own deterministic
versioned metadata contracts, including ADR-048's
wall-clock-independent message format. Their message
is NOT generated by a nondeterministic agent/provider.
No commit means no message request.

## Consequences

- The associated continuing main agent is the default
  generator for eligible interactive authored checkpoints.
- An independent agent, raw LLM, or arbitrary compatible
  external system can be selected without Git authority.
- Message output is candidate-bound, durable, and frozen
  for safe exact-Git retries and crash recovery.
- ADR-059 checkpoint membership, ADR-048 synthetic
  determinism, native Git equivalence, and Ruu-owned
  reconciliation authority remain unchanged.
- Qualification must cover overrides, arbitrary provider
  adapters, unavailable main agent, concurrent unrelated
  work, exact-state drift, and retry without OID changes.

## Alternatives considered

### Require coding agents to call git commit themselves

Rejected. It transfers a governed Git boundary and
manual version-control burden back to the producer.

### Generate every technical commit message with a LLM

Rejected. Existing commits must be preserved and
synthetic canonical OIDs must be reproducible.

### Use the main agent that happened to trigger the sweep

Rejected. That session might not own the unrelated
checkpoint and must not inherit its provenance.
