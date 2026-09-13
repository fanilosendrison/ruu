---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Minimize native Git event observation to managed authoring-binding disposition"
id: "ADR-074"
status: "accepted"
date: "2026-09-08"
decision_body_sha256: "9faf8fa9302ae70b67935d18876329762d7e7083c906c504cd6884a80a6d4652"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-039"
    - "ADR-071"
    - "ADR-073"
  supersedes: []
  confirms: []
governs: []
---

# ADR-074 — Minimize native Git event observation to managed authoring-binding disposition

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.50
- **Amends:** ADR-039, ADR-071, ADR-073, the consolidated specification, and the External Control Plane contract
- **Leaves open after ADR-075:** backlog 30.49 umbrella and 30.52–30.55; ADR-075 closes 30.51

## Context

ADR-071 made native deletion of a currently bound managed authoring ref transactionally durable through Git `reference-transaction`, then interpreted a committed `old_oid -> zero_oid` update as abandonment.

Hostile native-Git testing falsified that interpretation. A normal branch rename such as:

```text
git branch -m foo bar
```

can expose deletion of `refs/heads/foo` to `reference-transaction` before the later native rename/rebinding state is fully visible. Treating the old-ref deletion as immediate abandonment can therefore cancel work that Git merely renamed.

The correction must preserve three existing product constraints:

1. ordinary Git remains directly usable;
2. `ruu` must not infer semantic intent from branch similarity or command guesses;
3. a real abandonment must still causally fence later incompatible realization so withdrawn work cannot be published after the withdrawal linearizes.

A broader hostile sweep then asked which other native Git operations require durable event history rather than exact-state rediscovery.

## Decision

### 1. Native observation is split into state, event, and observation-integrity concerns

The v1 observation model has three conceptually distinct planes:

```text
STATE PLANE
→ exact current Git/remote/provider facts needed by a transition

EVENT PLANE
→ only facts whose occurrence/order cannot safely be reconstructed from later state

OBSERVATION-INTEGRITY PLANE
→ whether required event coverage itself remained continuously trustworthy
```

Hooks are not a general semantic event bus. The available Git hook catalog does not define the observation model.

### 2. The only currently ratified local Git event-semantic family is managed authoring-binding disposition

For a ref currently and durably bound as the managed authoring ref for live managed work, a transaction that removes that ref is not immediately `ABANDON`.

During the Git transaction `prepared` phase, the observer records:

```text
AUTHORING_BINDING_TRANSITION_PREPARED
```

binding at least:

```text
repository_id
ContributionUnit/work-occurrence identity
current binding generation
old managed ref
exact old/preimage OID
ref-transaction preparation identity/fingerprint
associated live ship/group identities when known
```

If the Git transaction aborts, the prepared transition produces no disposition change.

If the Git transaction commits, the binding becomes:

```text
AUTHORING_BINDING_DISPOSITION_UNRESOLVED
```

until exact evidence resolves the committed transition as `CONTINUATION` or `ABANDON`.

While disposition is unresolved, ADR-071's causal authorization fence blocks any new irreversible managed realization whose legality depends on whether the line remains live.

### 3. Continuation is never inferred from OID similarity or arbitrary ancestry

`CONTINUATION` requires a causal proof that the existing managed authoring line was rebound/renamed rather than terminated.

ADR-075 closes the 30.51 proof-strength question: a conforming native-ref adapter must provide a durable pre-linearization normalized witness that the core can classify as `RENAME_CARRY_PREPARED | TERMINAL_REMOVAL_PREPARED | UNKNOWN`. `CONTINUATION` then requires positive successor continuity; a worktree rebind is corroborating topology evidence rather than required identity. The semantic rule remains:

```text
same OID
similar tree
shared ancestry
branch created/copied from old branch
→ NOT proof of continuation
```

A mere `git switch <other-branch>` in the bound worktree is also not a rebind while the managed authoring ref still exists; it is a current editing-topology mismatch until the expected surface is restored or a valid rebind is established.

### 4. Native copy-then-delete is abandonment of the old managed line

For example:

```text
git branch -c foo bar
git branch -D foo
```

means:

```text
bar = ordinary separate Git branch
foo = managed authoring ref actually terminated
→ ABANDON for the managed line bound to foo
```

`ruu` does not ask whether the user "probably meant" `bar` to continue the line.

### 5. Managed authoring surfaces require a native reflog as causal evidence infrastructure

Before first managed write on a v1 authoring surface, the provisioning path MUST ensure that the managed authoring ref has a native Git reflog. If absent, it MUST be created before the surface is admitted for managed authoring.

On a later `ruu` invocation, if the expected managed binding is still intact, exact current state is coherent, and there is no unresolved binding transition or other evidence gap requiring historical proof, `ruu` MAY create/repair a missing reflog and establish the current exact state as the new future observation baseline.

Creating a reflog never reconstructs missing history retroactively.

Therefore:

```text
reflog absent + no historical proof required
→ repair baseline is allowed

reflog absent + unresolved transition needs causal history
→ do not invent history
→ use other sufficient proof or recovery
```

The reflog is evidence infrastructure, not ContributionUnit identity and not by itself a semantic authority object.

### 6. Definitive loss of native causal evidence has an explicit External Control Plane recovery route

ADR-039 is amended to permit one narrow recovery declaration for an already-existing ContributionUnit/work occurrence when native causal evidence can no longer resolve the binding disposition.

Conceptually:

```text
AuthoringBindingRecovery {
  contribution_unit_id
  work_occurrence_id
  expected_binding_generation
  expected_old_ref
  resolution = REBIND(new_ref) | ABANDON
}
```

This declaration is generation-bound and expected-old guarded. Stale or conflicting recovery declarations fail closed.

The External Control Plane is authoritative only for the logical recovery decision:

```text
same managed occurrence continues on new editing surface
or
that occurrence is authoritatively abandoned
```

It MUST NOT manufacture Git history such as claiming that `git branch -m` occurred. `ruu` independently re-observes/revalidates the actual repository, ref/worktree topology, exact OIDs, mutation authority, and absence of conflicting bindings before adopting `REBIND`.

This recovery path is exceptional. Normal native rename is resolved from Git-native evidence without requiring the Development System to explain ordinary Git commands.

### 7. All other currently identified local Git mutations remain state-observed

The minimal correctness-relevant state set includes, when required by a current transition:

```text
local refs and exact OIDs
objects/trees and reachability
worktree identity/path, HEAD/symref and current checked-out topology
index and structural in-progress Git state
submodule and sparse/skip-worktree observability state
contribution/convergence/internal refs
remote publication refs
submission refs + exact local/remote/provider heads/revisions
authoritative target ref/OID and ancestry
current policy/provider facts already required by the transition
```

The following operations do not acquire business semantics merely because they are observable:

```text
commit
reset
merge
rebase
ordinary ref tip movement
branch creation/copy
worktree add/remove/move
HEAD switch/detach
stash/tag/notes operations
```

Their current exact consequences are re-observed when relevant.

### 8. The ancestry interpretation environment is correctness-relevant state

Managed ancestry must not silently depend on an unnoticed ambient interpretation overlay.

The observation set therefore includes detection/current treatment of at least:

```text
refs/replace/*
$GIT_DIR/info/grafts
shallow repository boundaries / $GIT_DIR/shallow
```

`refs/replace/*` and grafts can alter the effective parent/object view used by Git commands; shallow boundaries can make required history unavailable. Their historical creation events are not semantic events, but their current presence/effect is correctness-relevant state.

ADR-075 defines the conforming reconstruction rule: managed ancestry proofs must use the raw canonical object graph without silently inheriting replace/graft overlays; an implementation may disable/ignore them through an exact reader or block. Shallow history is deepened/fetched when authorized and possible or remains ancestry-unknown. Intermediate overlay-creation events remain non-semantic.

### 9. No second irreducibly causal local Git event is currently identified

The hostile sweep tested internal refs, submission refs, targets, worktrees, HEAD, structural index/in-progress state, reflog loss, branch copy/creation, tags/stash/notes, and ancestry-environment mutations.

For these classes, losing intermediate local command history can at worst require fresh state reconstruction, drift handling, or recovery; it does not itself authorize a later irreversible action that would otherwise be forbidden.

The managed authoring-binding disposition family is different because missing a real abandonment can leave stale nominal realization authority alive.

### 10. Continuous observation coverage is a separate correctness prerequisite

This ADR closes the **what must be observed** question, not the hook-installation/persistence mechanisms.

A final state such as:

```text
foo exists at old OID
```

cannot prove that no abandonment occurred if required event coverage was absent during an interval in which `foo` could have been deleted and recreated.

Therefore 30.53/30.54 MUST define how continuous coverage and persistence health are established, and how a coverage gap is handled. A gap may force fail-closed recovery even when current ref state looks familiar.

## Consequences

- Backlog **30.50 is closed**.
- 30.49 remains open until ADR-075 and 30.52–30.55 are coherently resolved; ADR-075 closes 30.51.
- ADR-071's `old_oid -> zero_oid == abandonment` shortcut is superseded.
- `reference-transaction prepared` records a generic managed-authoring binding transition, not an abandonment decision.
- Native branch rename remains ordinary Git and preserves the managed authoring line when causal continuity is proven.
- Copy/create of another branch followed by deletion of the managed ref remains abandonment of the old managed line.
- Managed authoring reflogs are provisioned causal-evidence infrastructure, but are neither identity nor the only possible recovery source.
- Explicit generation-bound ECP recovery prevents permanent dead-end when causal Git evidence is irretrievably lost without allowing stale metadata to resurrect abandoned work.
- Exact current state remains the dominant observation model for every other presently identified local Git mutation.
- Ancestry overlays/completeness become explicit state-plane concerns.
- ADR-075 closes capture-versus-rediscovery strength; hook coexistence/coverage, detailed persistence failure, provenance/idempotency, and local/remote composition remain open under 30.52–30.55.

## Rejected alternatives

### Treat every committed `old -> zero` as abandonment

Rejected. Native `git branch -m` can expose the old ref removal during a larger rename sequence.

### Infer continuation from another branch pointing at the same OID

Rejected. Many independent branches may share an OID, and copy-then-delete is not rename.

### Make the worktree path or branch name the durable ContributionUnit identity

Rejected by ADR-038/073. They are editing surfaces, not durable logical identity.

### Add a proprietary lineage token as the first-line rename proof

Not required for v1 at this point. Git-native reflog/worktree/ref evidence plus durable CU identity is stronger and avoids inventing a parallel branch identity protocol. A future ADR may add another marker only if a concrete proof gap cannot be closed otherwise.

### Let `UNKNOWN_INCONSISTENT` be a permanent terminal dead-end

Rejected. Fail-closed is the immediate safety response; an explicit current generation-bound recovery authority exists for irretrievable proof loss.

### Turn every observable Git hook into durable semantic state

Rejected. Observation is derived from correctness obligations, not hook availability.


## Amendment by ADR-076 — event evidence is replayable; causal history is not reconstructed from state

The event plane does not require exactly-once delivery or actor attribution. Native witnesses/preparations may be replayed or duplicated, while authoritative binding disposition remains exactly-once per current binding generation. State-plane rediscovery may resolve an already-durable preparation when proof is sufficient, but it MUST NOT synthesize a missing terminal-removal or rename-carry preparation from current ref topology, same OID/tree/ancestry, or repeated scans. Best-effort wakeups remain non-semantic and freely coalescible/loss-tolerant.

## Clarification by ADR-081 — native commit observation and canonical identity

Ordinary commit creation and managed authoring ref-tip movement remain exact-state rediscovery. Ruu journals the later semantic AuthoringDependency adoption, not each commit event. Current v1 also canonicalizes historical `ContributionUnit/work occurrence` wording to the existing ContributionUnit identity and removes `work_occurrence_id` as a separate field from the active External Control Plane contract.
