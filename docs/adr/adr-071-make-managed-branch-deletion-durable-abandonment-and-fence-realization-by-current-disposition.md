---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make managed authoring disposition durable and fence realization by current disposition"
id: "ADR-071"
status: "accepted"
date: "2026-09-08"
decision_body_sha256: "e22f78d89759ef3b412daa44ccce881f75a26b85d9b052c423563f56b95916a7"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-038"
    - "ADR-042"
    - "ADR-055"
    - "ADR-066"
    - "ADR-068"
    - "ADR-070"
  supersedes: []
  confirms: []
governs: []
---

# ADR-071 — Make managed authoring disposition durable and fence realization by current disposition

- **Status:** Accepted — native binding-disposition mechanics corrected by ADR-074 and capture strength refined by ADR-075
- **Date:** 2026-09-08
- **Closes:** backlog 30.44 and 30.45
- **Amends:** ADR-038, ADR-042, ADR-055, ADR-066, ADR-068, ADR-070 §0.8, the consolidated specification, and the External Control Plane contract
- **Corrected/refined by:** ADR-074 (backlog 30.50) and ADR-075 (backlog 30.51)

## Context

ADR-068 introduced terminal pre-promotion `CANCELLED`, but deliberately kept ordinary Git artifact deletion semantically neutral and required an explicit external cancellation declaration. Product review exposed that this was one abstraction too many for the intended user experience: ordinary authoring abandonment should remain expressible through native Git rather than a second PromotionGroup RPC.

At the same time, two safety problems must be solved.

First, a previously persisted promotion `Operation/Attempt` cannot retain perpetual authority. After semantic disposition changes to `CANCEL` or `COMPENSATE`, crash recovery must not replay a previously authorized but still-absent nominal effect merely because its historical attempt exists.

Second, later ref absence alone is insufficient causal evidence. ADR-074 further proved that even a transactionally observed old-ref deletion is not by itself enough: native `git branch -m old new` can remove the old ref as part of a continuing authoring line.

The architecture therefore needs both:

```text
current causal authorization for every new managed realization effect
+
transactionally durable capture of removal of the currently bound managed authoring ref
+
post-commit disposition resolution: CONTINUATION | ABANDON
```

## Decision

### 1. Historical operation knowledge is never durable future authority

A persisted `Operation`, `Attempt`, prior policy observation, or prior semantic disposition may explain/recover an effect that was already causally committed, but it does not authorize a new effect after authority changes.

Normative principle:

> **Reconciliation may recover knowledge without recovering authority.**

Before every managed Git/provider action capable of newly realizing a PromotionGroup projection, `ruu` MUST establish that the **current** semantic disposition authorizes that exact causal effect.

Therefore:

```text
CANCEL + old ATTEMPT whose effect is proven absent
→ MUST NOT retry nominal realization

COMPENSATE + old nominal ATTEMPT whose effect is proven absent
→ MUST NOT retry nominal realization
  unless the current compensation plan explicitly authorizes that exact effect class

historically committed/uncertain effect
→ observe/recover/adopt before inventing a new effect
```

### 2. The causal authorization fence covers current-disposition validation and the managed effect

A mere read-then-write check is insufficient:

```text
read NORMAL
... CANCEL linearizes ...
perform old nominal effect
```

would still violate current semantic authority.

For effects under `ruu` control, disposition transition and realization must therefore share a causal serialization boundary. Conceptually:

```text
acquire causal authorization fence
→ re-observe current exact semantic disposition
→ verify exact effect is authorized
→ perform/commit the managed Git/provider effect
→ durably record enough outcome/recovery state
→ release fence
```

A transition to `CANCEL` or `COMPENSATE` MUST NOT linearize through a managed realization effect already inside this fence. Conversely, once the semantic transition has linearized, no old incompatible absent effect may begin/retry afterward.

The fence is not permission to hold long SQLite transactions across network/Git effects. ADR-042 short-transaction and effect-journal rules remain controlling.

### 3. Removal of the currently bound managed authoring ref opens a disposition transition

Deletion of an unmanaged Git branch remains ordinary Git with no `ruu` lifecycle meaning. Deletion of a worktree alone also does not mean abandonment.

When the exact ref currently registered as the managed authoring ref for live managed work is removed through a Git ref transaction, the removal is a correctness-critical causal event, but after ADR-074 it is **not immediately an abandonment event**.

```text
managed authoring ref exists and is durably bound to CU/work occurrence
+
Git transaction removes that exact ref
→ managed authoring binding transition
→ resolve as CONTINUATION | ABANDON
```

A native branch rename is `CONTINUATION` when Git-native causal continuity is proven. A genuine terminal deletion is `ABANDON`. OID equality, branch similarity, arbitrary ancestry, or a copied branch never proves continuation.

### 4. No separate ordinary cancellation command is required

The normal user/agent interface remains native Git. A true native deletion of the currently bound managed authoring ref is the ordinary abandonment gesture once the committed transition is resolved as terminal deletion.

The human/agent does not need to name a PromotionGroup, locate an internal cancellation identifier, or invoke a second ordinary control-plane cancellation command.

A provider PR being closed/rejected without merge does **not** by itself cancel the ship. `CHANGES_REQUESTED` continues under ADR-053 correction semantics. A terminal non-merged provider submission is a non-realizing publication fact.

ADR-074 adds a narrow explicit External Control Plane recovery declaration only for irretrievable causal-proof loss. That exceptional recovery path is not the normal user-facing cancellation interface.

### 5. Managed authoring-binding cessation/replacement MUST be captured before linearization, not inferred later

ADR-075 supersedes the assumption that `reference-transaction` support alone defines conformance. Any native mutation capable of deleting, replacing, or force-overwriting a currently bound managed authoring ref MUST pass through a conforming native-ref adapter with a vetoable or equivalently causally serialized observation point **before** that binding change may linearize.

The adapter establishes the actual preimage and emits a backend-independent normalized native witness. The core combines that witness with the current managed binding generation and durably records:

```text
AUTHORING_BINDING_TRANSITION_PREPARED
+ TERMINAL_REMOVAL_PREPARED

or

AUTHORING_BINDING_TRANSITION_PREPARED
+ RENAME_CARRY_PREPARED
```

If the adapter/core cannot prove which safe preparation class applies, the result is `UNKNOWN` and the ambiguous managed-binding mutation MUST NOT silently linearize.

The durable record binds at least repository identity, managed binding generation, affected ref, actual exact preimage OID, ContributionUnit/work occurrence identity, normalized native witness, and the core-derived preparation classification. Backend-specific transient paths/tables remain inside the adapter.

The currently demonstrated stock-Git `files` adapter uses `reference-transaction` plus native rename-carrier evidence; the tested stock reftable rename path does not currently expose the required pre-linearization callback and is therefore not conforming for live managed authoring until an equivalent capability exists. Hook coexistence/continuous-coverage and detailed persistence-failure UX remain under 30.53/30.54.

### 6. Native outcome delivery is recorded when available; disposition uses positive proofs

For a durable preparation, a delivered native `committed` / `aborted` outcome SHOULD be recorded. Correctness MUST nevertheless survive a crash or lost outcome callback by re-observing exact state under the selected adapter's recovery and observation-integrity contract.

```text
prepared + abort proven
→ no binding disposition change

TERMINAL_REMOVAL_PREPARED + commit proven
→ ABANDON

RENAME_CARRY_PREPARED + commit proven + successor continuity proven
→ CONTINUATION

RENAME_CARRY_PREPARED + incomplete/crashed successor establishment
→ AUTHORING_BINDING_DISPOSITION_UNRESOLVED

insufficient/contradictory proof
→ unresolved / recovery; never guess
```

`!ContinuationProof` is not abandonment. `ABANDON` and `CONTINUATION` are independently positive causal conclusions. While disposition remains unresolved, no new incompatible managed realization may cross the current-disposition fence.

### 7. Native reflog continuity is evidence infrastructure, not identity

ADR-074 requires every actively managed v1 authoring ref to have a native reflog provisioned before first managed write. `ruu` may repair a missing reflog on later invocation only when the current binding is intact and no unresolved historical transition requires missing causal evidence.

A new reflog establishes a future baseline; it never reconstructs deleted history.

### 8. Resolved pre-promotion abandonment selects `CANCEL`; partial realization cannot be erased

For an associated PromotionGroup with zero realized promotion effects:

```text
managed authoring binding transition
→ resolved ABANDON
→ current disposition CANCEL
```

From that point, §1–2 prevent `ruu` from causing any new nominal realization effect for the withdrawn group.

If one or more group promotion effects were already realized or were causally committed before the authoritative abandonment resolution, that history is recovered/adopted. ADR-055 partial settlement remains controlling and the abandonment cannot erase prior reality or invent compensation.

### 9. Rename/rebind continuation does not cancel or reopen the logical objects

When the committed transition is proven as a native continuation/rebind:

```text
old managed authoring binding → new ref
→ same ContributionUnit/work occurrence continues
→ no CANCEL
```

The durable ContributionUnit, ConvergenceUnit, PromotionGroup, exact checkpoints, and historical OIDs remain independent of branch-name identity.

A copied/independently created branch is not adopted merely because it points at the same OID.

### 10. Existing provider/publication surfaces are settlement obligations, not residual authorization

Once `CANCEL` is current, already-created provider surfaces may need closure/revocation where still revocable. They never become residual authority to continue nominal realization.

Pre-abandonment causally committed/realized effects remain recoverable historical facts.

### 11. Unmanaged/provider external races use proof, never wall-clock invention

If a provider/remote effect and authoring abandonment race across systems, authoritative causal evidence controls. Independent wall clocks do not manufacture ordering.

If required ordering is genuinely unprovable, terminal semantic classification fails closed while unrelated obligations may continue.

### 12. `CANCELLED` is terminal managed disposition, not perpetual exclusion from Git

After terminal cancellation, later unrelated native Git movement does not resurrect the cancelled PromotionGroup. Replacement delivery intent requires a distinct later group occurrence under ADR-069.

### 13. Minimum native-ref capability

ADR-075 makes backend capability rather than backend name or hook name normative. Live managed authoring requires pre-linearization coverage, veto/causal serialization, exact preimage capture, rename-versus-terminal evidence, durable normalized witness persistence, and crash-consistent recovery for every native mutation capable of ending/replacing a current managed binding.

The currently demonstrated `files` adapter uses Git `reference-transaction` (available from Git 2.28) plus backend-specific rename evidence. Git >=2.28 or presence of `reference-transaction` alone does **not** prove that another ref backend satisfies the full capability contract.

## Consequences

- ADR-068's blanket deletion-neutrality remains narrowed only at a currently bound managed authoring ref.
- ADR-074 corrects the classification: managed old-ref removal opens a durable disposition transition rather than directly creating abandonment.
- True terminal deletion remains the ordinary native-Git abandonment gesture.
- Native rename/rebind remains ordinary Git and does not cancel the work when continuity is causally proven.
- Current-disposition causal fencing remains fully normative.
- ADR-075 closes proof-strength/capture mechanics under 30.51; provenance/coverage/persistence/remote composition continue under 30.52–30.55.

## Rejected alternatives

### Keep explicit `CancelPromotionGroup(G)` as the ordinary user/agent gesture

Rejected. It unnecessarily exposes internal orchestration when native Git already expresses ordinary branch abandonment.

### Infer abandonment from later branch absence

Rejected. Later absence lacks the required transaction/ordering proof.

### Treat every `old -> zero` managed-ref transaction as abandonment

Rejected by ADR-074. Native rename can remove the old ref while preserving the authoring line.

### Infer continuation from same OID/ancestry

Rejected. Copy/create and independent branches may share exact Git state without being the same authoring binding.

### Let an old persisted Attempt retry after cancellation because it was once authorized

Rejected. Historical knowledge is not future authority.

### Compare independent local/provider timestamps to force an ordering

Rejected. Clock order is not causal proof.

## Backlog impact

ADR-071 closes 30.44 and 30.45. ADR-074 later closes 30.50 and corrects the native managed-binding deletion classifier while preserving ADR-071's causal authorization fence and transactional write-ahead requirement.


## Amendment by ADR-076 — binding-disposition idempotency is generation-scoped

Native binding evidence is not a second managed Operation. For one `(repository, work occurrence, binding_generation)`, at most one correctness-critical cessation/rebind preparation may remain unresolved and at most one committed `CONTINUATION | ABANDON` disposition may transition out of that generation. Duplicate delivery of the same active native occurrence is idempotent; a genuinely distinct competing transition must wait/fail/veto until the current preparation is resolved. After `ABORTED`, the same generation may admit a later distinct preparation; after committed disposition, stale deliveries cannot re-dispose the old generation. Optional correlation to a managed Attempt is explanatory only and cannot bypass the current-disposition causal fence.

## Clarification by ADR-081 — dependency consumers inherit no source authority

Current v1 reads `work occurrence` above as the existing ContributionUnit; no separate `work_occurrence_id` exists. If another ContributionUnit has consumed an exact commit from this source, resolved source `ABANDON` or group `CANCEL` does not authorize the consumer to publish that commit. Current target satisfaction is checked first; otherwise the AuthoringDependency becomes exact `RECONCILIATION_REQUIRED` and remains realization-blocking. Already committed/realized history keeps the existing ADR-071 recovery treatment.
