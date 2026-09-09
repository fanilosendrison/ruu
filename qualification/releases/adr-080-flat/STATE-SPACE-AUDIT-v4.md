# Ruu — Global State-Space Consistency Audit v4

- **Date:** 2026-09-05
- **Scope:** main requirements + ADR-001..ADR-034 after replacing the Git-level writer/global-actor model with repository-local work contexts
- **Result:** **PASS with open design backlog; no contradictory authorized transition found in the changed/revalidated finite families or static global cross-check**

## 1. Why the audit was rerun

ADR-034 changes a foundational identity/cardinality assumption:

```text
old model
→ global/logical writer identity
→ repository-local writer_context

current model
→ repository-local work_context_id only
```

It also replaces the narrower `editing context` terminology with a neutral work context that supports both greenfield/from-scratch creation and modification of existing content.

This affects isolation cardinality, cross-repository reasoning, topology bindings, worktree/ref identity, lifecycle terminology, mutation-authority inputs, examples, and the state model. A text-only rename would therefore be insufficient.

## 2. Reproducible finite enumeration

`state-space-audit-v4.py` exhaustively enumerates the new identity/cardinality and actor-correlation families, then reruns the current mutation-authority and verification/review families.

Expected result:

```text
Ruu state-space audit v4: PASS
work_context_cardinality_identity: 128
actor_correlation_irrelevance: 120
work_context_worktree_mutation_authority: 150
work_context_commit_verification_crosscheck: 900
state_producing_transition_verification: 432
verification_evidence_reuse: 72
verification_fixed_point: 108
verification_capacity_scheduler: 180
review_request_intent: 108
review_revision_invalidation: 24
internal_integration_evidence: 240
changed/revalidated finite combinations evaluated: 2,462
markdown artifacts statically cross-checked: 40
```

Historical v2/v3 audit artifacts are retained as historical results for the earlier ontologies. Their old totals are not reused as proof of the ADR-034 model.

## 3. Work-context identity/cardinality

The new finite family checks:

```text
context provisioning/removal state
× repository binding cardinality
× worktree binding cardinality
× active ref binding cardinality
```

Verified:

```text
PROVISIONED
→ exactly one repository
→ exactly one isolated worktree
→ exactly one active work-context ref

REMOVED
→ repository identity remains known
→ zero active worktrees
→ zero active work-context refs
```

Any zero/multiple/unknown repository binding is invalid for a managed work context. A work context therefore cannot span repositories.

Result: **PASS**.

## 4. Global actor correlation is irrelevant to `ruu` authority

A separate family injects hypothetical higher-level correlation metadata:

```text
NONE
SAME_EXTERNAL_ACTOR
DIFFERENT_EXTERNAL_ACTOR
UNKNOWN
```

across every combination of:

```text
mutation_access
× worktree claim owner
× topology known/unknown
```

The authorization result is required to remain identical regardless of that actor-correlation value.

Verified: no mutation-authority predicate depends on a global producer/actor identity.

Result: **PASS**.

## 5. Work-context-worktree mutation authority

Verified across commit, synchronization, conflict mutation, reset/move, and cleanup:

- `PROTECTED_EXTERNAL` never authorizes mutation;
- `TRANSFERABLE_TO_OTHER_INVOCATION` never authorizes the current invocation;
- `UNKNOWN` fails closed;
- transferable states permit only a claim attempt;
- mutation requires `claim == THIS_INVOCATION` and known topology;
- actor/principal correlation is absent from the predicate;
- transferability must remain valid through race-safe claim acquisition.

Result: **PASS**.

## 6. Commit + verification crosscheck

The commit family crosses:

```text
work-context lifecycle present/removed
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
- protected/other/unknown authority cannot be bypassed by verification evidence;
- removed contexts are never committable;
- only exact valid evidence for a stable candidate can authorize the managed checkpoint after authority preconditions hold.

Result: **PASS**.

## 7. Cross-repository model

The current model no longer permits one work context to span repositories.

Instead:

```text
higher-level work spanning RepoA + RepoB + RepoC
→ work_context_A in RepoA
→ work_context_B in RepoB
→ work_context_C in RepoC
```

No `ruu` safety/convergence/promotion transition requires proof that these contexts share an external producer/session/task.

Cross-repository promotion remains non-atomic exactly as before; ADR-034 changes identity cardinality, not repository-local Git atomicity.

Result: **PASS**.

## 8. Greenfield/from-scratch compatibility

Static cross-check verifies that the normative definition of work context does not require pre-existing content.

The same repository-local isolation object may represent:

```text
greenfield/from-scratch creation
addition
modification
deletion
refactor
generation/migration
```

New-repository creation/provisioning authority remains a separate open design question; once a repository exists/has been provisioned into the managed Git domain, `work_context` remains the correct isolation abstraction.

Result: **PASS**.

## 9. ADR-033 authority boundary remains intact

ADR-034 does not weaken the prior authority split:

```text
work-context subsystem
→ owns external producer/runtime mutation rights
→ makes exact context safely transferable

Ruu
→ consumes transferability
→ acquires exact exclusive claim
→ mutates/revalidates/recovers its owned operation
```

No heartbeat, process/session identity, or global producer ID is introduced into the authorization predicate.

Result: **PASS**.

## 10. Verification/review regressions

All current finite families remain valid under the work-context terminology/cardinality:

- state-producing result verification;
- exact evidence reuse/invalidation;
- verification fixed point;
- verification-capacity admission;
- review-request intent;
- review revision invalidation;
- internal integration evidence.

No identity rename grants verification capacity, changes append-only ref authority, manufactures readiness, or weakens exact-state evidence requirements.

Result: **PASS**.

## 11. Static global consistency checks

The v4 script checks the current architecture for:

- balanced Markdown code fences;
- exact ADR sequence `ADR-001..ADR-034`;
- current work-context definition and one-repository cardinality;
- absence of `writer_context_id`, `writer_id`, and `editing-context` from the current main requirements;
- absence of Git-level writer terminology from ADR-001..ADR-033;
- ADR-034 as the explicit migration/supersession record;
- absence of the old `{work_context, repository}` cardinality in the current main spec;
- absence of `LEASE_ESTABLISHED` as a normative provisioning state;
- presence of `EXTERNAL_MUTATION_AUTHORITY_ESTABLISHED` instead;
- continued separation of transferability and exclusive `ruu` claim;
- explicit retirement of liveness/actor-identity/handoff questions from the `ruu` backlog.

Historical audit v2/v3 artifacts intentionally retain their original terminology and are not treated as current normative language.

Result: **PASS**.

## 12. Open questions are not contradictions

ADR-034 closes the Git-level identity question:

```text
work_context_id
→ stable opaque repository-local identity

global producer identity
→ outside Ruu / not required
```

Still open are policy/implementation questions already listed in `OPEN-DESIGN-BACKLOG.md`, including claim contention, coordination-store implementation, work-context close/abandonment semantics, convergence-unit readiness, verification persistence/scheduling/flakiness/external services, PR-author gate, provider CI, final integration proof, agentic review, promotion mechanics, and new-repository creation authority.

## 13. Audit conclusion

The ADR-034 model is coherent with the existing architecture:

```text
external actor/runtime
        ↓ outside Ruu
repository-local work_context_id
        ↓
work-context ref/worktree
        ↓
convergence unit
        ↓
promotion unit / submission / target
```

No modeled path was found where:

- one work context validly spans multiple repositories;
- global actor correlation changes mutation authorization;
- invocation-principal identity substitutes for work-context authority;
- transferability without a claim authorizes mutation;
- a protected/unknown context becomes committable because verification passed;
- the terminology change weakens append-only Git, exact-state verification, promotion-policy, provider-state, or recovery invariants.

**Verdict: PASS for ADR-001..ADR-034 under the current factorized/static audit model.**
