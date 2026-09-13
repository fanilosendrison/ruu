---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Define Ruu as Git-based version control redesigned for agentic development"
id: "ADR-070"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "16e94271f4c9af60d161427021411371a9b693d76f89fb92df4f297a7ab549da"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-004"
    - "ADR-005"
    - "ADR-009"
    - "ADR-022"
    - "ADR-024"
    - "ADR-033"
    - "ADR-036"
    - "ADR-041"
    - "ADR-042"
    - "ADR-058"
    - "ADR-064"
    - "ADR-069"
governs:
  - "interpretation of ADR-001 through ADR-069 and the consolidated specification"
---

# ADR-070 — Define Ruu as Git-based version control redesigned for agentic development

**Status:** Accepted — 2026-09-07  
**Governs:** interpretation of ADR-001 through ADR-069 and the consolidated specification  
**Confirms:** ADR-004, ADR-005, ADR-009, ADR-022, ADR-024, ADR-033, ADR-036, ADR-041, ADR-042, ADR-058, ADR-064, ADR-069  
**Clarified by:** ADR-071 for the explicit managed-authoring-ref exception to ordinary deletion neutrality; ADR-078 for zero-preflight supported-harness authoring and the role-vs-product distinction

## Context

The architecture has accumulated a large number of individually coherent technical decisions about isolated authoring, global convergence, exact-state adoption, crash recovery, provider publication, PromotionGroups, and reconciliation. Those decisions can nevertheless be read or implemented in a way that is locally correct while silently drifting from the intended product.

The intended product is not a Git workflow that asks the user to coordinate concurrent coding sessions more carefully. It exists specifically so the user **does not have to perform that coordination**.

A normal user may have several coding sessions active at once. They may have been started from different repositories, may touch one or many repositories, and may eventually overlap the same ConvergenceUnits or files. The user should be able to continue working in those sessions independently and invoke `ruu` when each session's current block of work is ready, without first reasoning about the global order of sessions, manually refreshing every branch, enumerating repositories, choosing PromotionGroups, or acquiring a human mutex around Git publication.

Without writing this product contract normatively, later technical work can optimize the wrong interface while remaining internally consistent. This ADR therefore makes the intended user experience an architectural decision with explicit precedence.

## Decision

### 1. Product definition and architectural center of gravity

`ruu` is **Git-based version control redesigned for agentic software development**.

Git remains the storage/history substrate and native interoperability boundary: commits, trees, refs, ancestry, merges, object identity, and ordinary Git operations retain their native meaning. `ruu` does not replace Git with an incompatible VCS. It replaces the human-coordination assumptions of conventional Git workflows with a version-control model built for many concurrent coding agents/sessions, potentially spanning several repositories, advancing shared managed lineages, surviving retries/crashes, and reconciling exact state mechanically whenever possible.

The architectural center of gravity is therefore **agentic version control**, including at least:

```text
isolated concurrent work production
durable work-bearing checkpoint/invocation boundaries
repository-independent discovery of managed work
convergence of concurrent contributions into exact Git history
group-local historical version state
mechanical stale-state reconciliation
conflict localization and exact semantic handoff
crash/retry-safe observation and progression
coexistence with ordinary native Git
```

Remote hosting and provider-facing publication are an **extended feature layer over that core**, not the definition of the product. Pull requests, stacked pull requests, merge queues, protected-branch APIs, provider review state, and provider-specific publication topology extend the core version-control model in the same architectural sense that GitHub/GitLab extend Git rather than define Git itself. Native Git remote transport may of course be used as a transport primitive, but provider publication semantics MUST NOT become the source of core version identity or convergence truth.

Accordingly, removing GitHub/GitLab/provider APIs from a deployment would remove important publication features, but it MUST NOT erase the conceptual core of `ruu`: concurrent agentic work can still be checkpointed, versioned, integrated, reconciled, and made to converge as exact native Git state. Provider publication projects that already-established exact state outward.

This separation is normative. Technical mechanisms for PRs, stacks, merge queues, or remote settlement are first-class supported features, but architectural choices MUST NOT redefine `ruu` primarily as a GitHub/PR orchestration system.

### 2. Governing product promise

`ruu` exposes a hands-off convergence/checkpoint interaction for concurrent agentic development as part of its broader agentic version-control model.

The governing product promise is:

> **A user may run multiple coding sessions concurrently, from any already-managed repository in the coordination domain. Each session may touch one or several repositories and may overlap work produced by other sessions. When that session considers its current work ready to cross a Git boundary, it invokes `ruu` from whichever managed repository it is currently in. The user does not manually coordinate repositories, session ordering, stale bases, PromotionGroups, dependency topology, or mechanically resolvable collisions. `ruu` discovers/re-observes durable managed state, reconciles what can be reconciled mechanically, and advances the global Git/provider state safely. Only a genuinely semantic incompatibility or missing external authority is returned to the Development System for authored/semantic action.**

This promise is normative, not marketing prose.

### 3. `ruu` is invoke-anywhere within the managed coordination domain

The caller's current working directory is a discovery/entry context, not orchestration truth.

For an already-managed coordination domain:

```text
CWD != work-bearing invocation cohort
CWD != repository convergence scope
CWD != global reconciler sweep scope
```

If one session has produced a work-bearing cohort spanning repositories `A`, `B`, and `C`, invocation from `A`, `B`, or `C` MUST NOT require the user to enumerate the other repositories or change to a special root directory. The Development System / External Control Plane supplies the durable session-local handoff cohort required by ADR-069 behind the user-facing invocation.

The work-bearing logical invocation records the new cohort occurrence. The convergence demand raised by that invocation still causes the ordinary global fixed-point sweep over **all known nonterminal managed obligations**, including unrelated older work.

An arbitrary unknown/unmanaged repository is not silently admitted merely because the command was run there; repository admission remains governed by ADR-022/056. "Invoke anywhere" means that no particular repository participating in already-managed work is privileged as the semantic command scope.

### 4. Concurrent coding sessions are the normal case, not an exceptional mode

The product MUST remain correct when several sessions are authoring concurrently, including when they ultimately contribute to the same ConvergenceUnit or touch overlapping files.

The user MUST NOT be required to serialize sessions merely to keep `ruu` correct. Simultaneous explicit invocations may safely coalesce as convergence demand under ADR-041 while distinct ADR-069 work-bearing LogicalInvocations remain distinct durable cohort occurrences.

The system therefore absorbs operational concurrency internally through isolation, exact state, claims/CAS, observation, recovery, reconciliation, and fixed-point progression rather than exporting a global locking protocol to the user.

### 5. No human mutex and no routine manual orchestration

A conforming ordinary workflow MUST NOT require the user to answer questions such as:

```text
Which other session is currently converging?
Which repository must I run the command from?
Which repositories did this cohort touch?
Which PromotionGroup should these changes belong to?
Which invocation must go first?
Do I need to wait for another session before invoking?
Do I need to pull/rebase only because another managed session advanced the lineage?
Which stack/PR topology should I declare up front?
Which stale base generation should I name?
```

Nor should the ordinary CLI require user-authored equivalents such as:

```text
ruu --repos A,B,C
             --group G
             --depends-on ...
             --base-generation ...
```

when those facts are already available or mechanically derivable from durable managed state and the Development System's current work-bearing handoff.

Explicit diagnostic/recovery tooling may expose such identities for inspection or exceptional operator action, but those details are not the ordinary product interaction model.

### 6. Staleness and mechanical collisions are convergence inputs, not routine user failures

A coding session may have started from an exact state that is no longer globally current when it later invokes `ruu`. That is expected under concurrency.

Therefore:

```text
stale relative to newer managed work
!= ordinary product failure
```

When exact Git mechanics can preserve the relevant owned effects and reconcile them onto current authoritative state, `ruu` MUST do so through the architecture's existing append-only integration, exact merge/materialization, restack/transplant, observation, and retry machinery.

The system MUST NOT guess through a genuinely semantic conflict. When Git mechanics cannot determine a unique authorized result, `ruu` emits/localizes the exact reconciliation obligation and returns semantic authoring to the Development System. The product promise is **no avoidable manual coordination**, not "conflicts can never exist".

### 7. "Keep it updated" does not mean mutating producer-owned work behind its back

Hands-off concurrency is achieved through isolated ContributionUnits and reconciliation, not through a shared mutable checkout or surprise background rebases.

While an external producer owns mutation authority over an active ContributionUnit, `ruu` MUST respect ADR-009/033/064 and MUST NOT silently rewrite that producer's mutable editing surface merely to make it appear current with another session.

Instead, stale/divergent work is reconciled at authorized handoff/convergence boundaries. When semantic authoring must resume, the Development System receives an exact state/obligation from which to continue.

### 8. Native Git remains usable and semantically ordinary

The simplified user experience is not achieved by turning Git into a proprietary command language.

Users and agents remain free to use ordinary Git operations. Branch/worktree/ref creation or deletion, ordinary commits, and route-conformant external Git progress retain their native meaning unless an explicit managed authority boundary says otherwise. `ruu` observes, adopts, reconciles, or reports such facts under the existing exact-state rules.

In particular, the product MUST NOT require all normal Git mutation to pass through `ruu` merely to preserve internal orchestration assumptions.

### 9. Semantic authority stays above `ruu`

`ruu` does not decide whether code is good, whether a feature is semantically complete, whether review feedback is satisfied, or whether product intent changed. The Development System / External Control Plane owns those decisions.

The user-facing simplicity begins **after** the Development System has determined that a current block of work is ready for the next Git boundary and invokes `ruu`.

`ruu` then owns the mechanically rigorous progression of Git/provider state until it reaches a fixed point or an exact external/semantic obligation is required.

### 10. Product-intent conflict rule

This ADR governs interpretation of the technical architecture.

If an earlier technical ADR or consolidated-spec clause admits more than one interpretation, implementations MUST choose the interpretation that preserves this ADR's product promise while satisfying the applicable safety invariants.

If an earlier technical ADR directly conflicts with this product promise, ADR-070 supersedes the conflicting clause **to the minimum extent necessary**. The affected technical rule must be amended rather than silently forcing the user into manual coordination that this ADR forbids.

Provider-facing publication rules are subordinate to the core version-control model in the same way: where exact core version/convergence state can be defined without provider concepts, provider objects MUST be projections/realizations of that state rather than the source of its identity.

A future ADR may intentionally change this product promise only if it:

1. explicitly states `Amends: ADR-070`;
2. identifies the exact product promise being changed;
3. explains the user-visible regression/tradeoff being accepted; and
4. updates the `Product intent` section at the head of `RUU-SPEC.md` in the same decision.

Silence, implementation convenience, or a technically coherent lower-level model does not override ADR-070.

### 11. Product conformance test

When evaluating a proposed architecture or implementation, ask whether the following ordinary scenario remains valid without extra user orchestration:

```text
Session A starts in repo frontend and keeps authoring.
Session B starts in repo backend and keeps authoring.
Session C starts in repo schema and keeps authoring.

Their work may span or overlap repositories/ConvergenceUnits.

A invokes Ruu from whatever managed repo A is in.
C invokes Ruu while B is still working.
B invokes Ruu later from another managed repo.

No user-level mutex is taken.
No caller enumerates the global repository set.
No caller declares PromotionGroup membership or stack topology.
No caller manually orders the invocations for correctness.
Stale managed bases are mechanically reconciled when possible.
Only irreducible semantic conflicts/missing authority become explicit obligations.
The global managed Git/provider state eventually converges by repeated safe reconciliation.
```

A design that cannot support this scenario without requiring avoidable manual coordination is not product-conformant even if its internal state machine is otherwise coherent.

## Consequences

- The product is architecturally centered on agentic version control; convergence/promotion are mechanisms within that product, not a narrower replacement definition.
- Remote-hosting and provider-publication workflows are extended projections over core exact Git/version state. Removing provider APIs must leave a meaningful local/native-Git core.
- The simple `ruu` invocation is the intended ordinary interface; technical identity/state needed for safety is carried or derived behind that interface.
- Complexity inside the engine is justified when it removes concurrency/orchestration burden from the user while preserving exactness and recoverability.
- CWD-scoped convergence, session-serialization requirements, caller-authored group membership, caller-authored publication topology, or routine stale-base failure are product regressions unless explicitly ratified by a future ADR that amends ADR-070.
- Fail-closed behavior remains correct for unknown/inconsistent authority or irreducible semantic conflict. Fail-closed MUST NOT be used as a substitute for implementing mechanical reconciliation that the architecture can determine safely.
- ADR-004/022/036 global scope, ADR-041 demand coalescing, ADR-058 native-Git equivalence, ADR-064 mutation handoff, and ADR-069 invocation-bound grouping are now explicitly understood as mechanisms serving this product contract.

## Rejected alternatives

### Define `ruu` primarily as GitHub/PR orchestration

Rejected. Provider publication is an important feature layer, but the product still has a coherent identity and substantial behavior without PRs, merge queues, or provider APIs. Making provider objects the semantic center would invert the dependency direction and silently narrow the intended version-control model.

### Leave product intent implicit across technical ADRs

Rejected. A technically consistent architecture can silently drift toward an interaction model that requires the user to coordinate sessions manually.

### Make the caller's repository/CWD the semantic scope

Rejected. It strands multi-repository and unrelated recoverable obligations and makes correctness depend on where the command happened to be invoked.

### Require users to serialize concurrent coding sessions

Rejected. Concurrency is a primary use case and one of the main reasons the product exists.

### Require explicit repository/group/dependency flags for ordinary invocation

Rejected. Those are internal/durable topology facts or Development-System handoff facts, not routine user orchestration inputs.

### Keep active worktrees automatically rebased in the background

Rejected. It violates isolated mutation authority and turns hands-off coordination into hidden concurrent mutation. Reconciliation occurs at controlled exact-state boundaries instead.

## Verification obligation

Future architecture/package verification MUST include a product-intent conformance pass in addition to technical state-space checks. At minimum it must scan for new current normative rules that accidentally require:

```text
CWD-scoped correctness
manual session serialization
caller-declared repository/group scope
caller-declared stack/dependency topology
routine stale-base failure when exact mechanical reconciliation exists
mutation of externally owned active worktrees
provider objects becoming the source of core version identity/convergence truth
```

Any such rule requires explicit ADR-070 amendment or is a regression.


## Clarification by ADR-078 — zero-preflight supported-harness authoring

ADR-070's hands-off promise includes the period **before the first managed write**, not only the later convergence invocation. A conforming ordinary workflow for a supported coding harness requires one-time product installation/integration, then ordinary agent authoring, then `ruu` when the user/agent wants a checkpoint. Required ContributionUnit/worktree/ref/observer/binding plumbing is automatic and invisible. The External Control Plane remains an architectural authority role and may be implemented by a Ruu-supplied harness integration; this does not make the convergence engine the source of semantic work intent.
