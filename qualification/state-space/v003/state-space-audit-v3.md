# Ruu — Global State-Space Consistency Audit v3

- **Date:** 2026-09-05
- **Scope:** main requirements + ADR-001..ADR-033 after removing writer-liveness/lease semantics from the `ruu` authority model
- **Result:** **PASS with open design backlog; no contradictory authorized transition found in the revalidated finite families or static global cross-check**

## 1. Why the audit was rerun

ADR-033 changes a foundational authorization axis.

The previous model used:

```text
writer ACTIVE / INACTIVE
+ exact delegation
+ worktree claim
```

The revised model uses:

```text
external mutation-access contract
+ exclusive worktree claim by the exact Ruu invocation
```

with:

```text
PROTECTED_EXTERNAL
TRANSFERABLE_TO_THIS_INVOCATION
TRANSFERABLE_GENERAL
TRANSFERABLE_TO_OTHER_INVOCATION
UNKNOWN
```

Writer runtime liveness, heartbeat, lease renewal/expiry, process/session death, and writer resume mechanics are now explicitly outside `ruu`.

Because this affects commit collection, writer synchronization, cleanup, simultaneous invocations, provisioning boundaries, and recovery assumptions, a local text patch was insufficient.

## 2. Reproducible finite enumeration

`state-space-audit-v3.py` exhaustively enumerates the changed authority families and reruns every finite verification/review family introduced by v2.

Observed result:

```text
Ruu state-space audit v3: PASS
writer_worktree_mutation_authority: 150
writer_commit_verification_crosscheck: 900
state_producing_transition_verification: 432
verification_evidence_reuse: 72
verification_fixed_point: 108
verification_capacity_scheduler: 180
review_request_intent: 108
review_revision_invalidation: 24
internal_integration_evidence: 240
changed/revalidated finite combinations evaluated: 2,214
markdown artifacts statically cross-checked: 38
```

The old v2 total of 14,220 combinations is retained only as a historical audit result. It is **not** carried forward as a current global numeric total because its baseline ownership families encoded the retired `ACTIVE/INACTIVE + delegation` ontology and the original baseline generator is not present in this artifact set. The v3 audit therefore avoids pretending that an unchanged historical number proves the revised authority model.

## 3. Writer-worktree mutation authority

The affected finite family checks every combination of:

```text
mutation_access
× worktree claim owner
× topology known/unknown
× writer-worktree mutation class
```

across commit, synchronization, conflict mutation, checkout/reset movement, and cleanup.

Verified:

- `PROTECTED_EXTERNAL` never authorizes mutation;
- `TRANSFERABLE_TO_OTHER_INVOCATION` never authorizes the current invocation;
- `UNKNOWN` fails closed;
- `TRANSFERABLE_TO_THIS_INVOCATION` and `TRANSFERABLE_GENERAL` permit only a claim attempt;
- mutation requires `claim == THIS_INVOCATION` and known topology;
- transferability alone never becomes mutation authority;
- transferability must remain valid through claim acquisition and external writer reacquisition must be excluded while the claim is held;
- principal identity is absent from the authorization predicate.

Result: **PASS**.

## 4. Commit + verification crosscheck

The commit family additionally crosses:

```text
writer lifecycle present/removed
mutation access
claim owner
dirty/clean
verification evidence
candidate stability
```

Verified:

- dirty state alone is insufficient;
- transferability alone is insufficient;
- claim alone is insufficient;
- protected/other/unknown external authority cannot be bypassed by verification evidence;
- `REMOVED` is never committable;
- only exact valid evidence for a stable candidate can authorize the managed checkpoint after authority preconditions hold.

Result: **PASS**.

## 5. Writer lifecycle remains independent

The revised spec keeps:

```text
OPEN
CLOSED
ABANDONED
REMOVED
```

as contribution lifecycle, while mutation access is a separate external input.

The audit/static cross-check confirms no rule now implies:

```text
OPEN → PROTECTED_EXTERNAL
CLOSED → TRANSFERABLE_GENERAL
commit → CLOSED
integration → CLOSED
```

Writer close/abandonment semantics therefore remain higher-level lifecycle signals rather than reconstructed liveness signals.

Result: **PASS**.

## 6. Provisioning and runtime boundary

Global cross-check confirms:

```text
editing-context subsystem
→ creates isolated writer context
→ owns writer-runtime mutation rights
→ owns stop/crash/resume semantics
→ makes context safely transferable

Ruu
→ consumes opaque writer_context_id + mutation-access state
→ acquires its own exclusive claim
→ mutates/revalidates/recovers its owned convergence operation
→ releases claim
```

No normative main-spec path asks `ruu` to infer transferability from heartbeat, process/session state, timeout, or model identity.

Result: **PASS**.

## 7. Simultaneous invocations

Checked the two transferable modes separately:

```text
TRANSFERABLE_TO_THIS_INVOCATION
→ only the designated invocation may attempt the worktree claim

TRANSFERABLE_GENERAL
→ authorized invocations may race
→ only the exclusive claim winner may mutate
```

A context transferred to another invocation is protected from the current one.

This remains compatible with fine-grained claims and does not introduce a global mutex.

Result: **PASS**.

## 8. Crash/recovery responsibility split

The spec now distinguishes:

```text
external writer/runtime crash
→ editing-context subsystem decides when/if context becomes safely transferable

Ruu crash after it owns a claim/operation
→ Ruu recovery reconciles its owned Git/control-plane state
```

Unknown external authority remains fail-closed. Unknown ownership of an in-progress `ruu` operation also remains fail-closed/recovery-only.

Result: **PASS**.

## 9. Verification/review regressions

All v2 finite verification/review families were rerun under the revised writer authority predicate:

- state-producing result verification;
- exact evidence reuse/invalidation;
- verification fixed point;
- verification-capacity admission;
- review-request intent;
- review revision invalidation;
- internal integration evidence.

No revised writer-authority state grants verification capacity, changes append-only ref authority, manufactures readiness, or weakens exact-state evidence requirements.

Result: **PASS**.

## 10. Static global consistency checks

The v3 script cross-checks the complete Markdown artifact set for:

- balanced Markdown code fences;
- exact ADR sequence `ADR-001..ADR-033`;
- presence of the five external mutation-access states in the main spec;
- presence of the opaque `writer_context_id` rule;
- absence from the main spec of the retired `Exact writer liveness mechanism` backlog item;
- absence from the main spec of the retired `Active-writer delegation state` model;
- absence from the main spec of normative `writer lease = active/inactive` authorization rules;
- explicit backlog retirement by ADR-033;
- explicit distinction `transferability ≠ exclusive Ruu claim`.

Historical ADRs may retain superseded wording in their original decision text, but ADR-033 is explicitly recorded as the later amendment/supersession and the current main requirements contain only the revised model.

Result: **PASS**.

## 11. Open questions are not contradictions

ADR-033 closes/removes from the `ruu` backlog:

- exact writer-liveness mechanism;
- heartbeat/lease renewal/expiry policy;
- writer-context identity format beyond stable opaque identity;
- writer-runtime handoff/stop/resume mechanics.

Still open are the existing policy/implementation questions unrelated to writer-runtime liveness, including claim contention/backoff, coordination-store implementation, writer close/abandonment semantics, convergence-unit readiness, verification persistence/scheduling/flakiness/external services, PR-author gate, provider CI, final integration proof, agentic review, and promotion mechanics listed in `OPEN-DESIGN-BACKLOG.md`.

## 12. Audit conclusion

The revised authority boundary is coherent with the rest of the architecture:

```text
external editing authority says protected
→ Ruu cannot touch the worktree

external editing authority says transferable
→ Ruu may attempt its exact exclusive claim

claim held by this invocation
+ exact topology/state/policy/verification guards
→ mutation may proceed
```

No modeled path was found where:

- a heartbeat or timeout creates `ruu` authority;
- principal identity creates writer-worktree authority;
- transferability without a claim authorizes mutation;
- another invocation's transfer/claim authorizes this invocation;
- protected/unknown writer state becomes committable because verification passed;
- writer lifecycle is silently inferred from mutation access;
- the new boundary weakens append-only Git, promotion-policy, verification-evidence, or provider-state invariants.

**Verdict: PASS for ADR-001..ADR-033 under the current factorized/static audit model.**
