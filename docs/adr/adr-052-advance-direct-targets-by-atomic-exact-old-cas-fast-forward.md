---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Advance DIRECT targets by atomic exact-old CAS fast-forward"
id: "ADR-052"
status: "accepted"
date: "2026-09-06"
decision_body_sha256: "5c95383a23436da81b5f5c1f6a3ff866086a81147da62fab61bbaab97793fa9a"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-026"
    - "ADR-041"
    - "ADR-042"
    - "ADR-044"
    - "ADR-048"
    - "ADR-051"
  supersedes: []
  confirms: []
governs: []
---

# ADR-052 — Advance DIRECT targets by atomic exact-old CAS fast-forward

- **Status:** Accepted; amended by ADR-061
- **Date:** 2026-09-06
- **Closes:** backlog 30.22
- **Amends:** ADR-026, ADR-041, ADR-042, ADR-044, ADR-048, ADR-051 and the main DIRECT-promotion model

- **Subsequently amended by:** ADR-080 for source-domain local/remote/provider observation authority and webhook evidence semantics

## Context

ADR-048 already fixes how a repository-local PromotionUnit becomes one exact candidate `C` from an exact authoritative target/effective-base baseline `B`, and requires valid development-validation evidence for exact `C` before DIRECT target advancement. The remaining 30.22 question was the final target-mutation envelope: whether a local target worktree/ref is staged first, what exact mutation primitive is normative, how a crash between external effect and metadata adoption is recovered, which physical anchors must survive, and when they may be cleaned.

The naive model is misleading:

```text
checkout target
→ merge candidate
→ move local target
→ push
```

There is nothing left to merge at this stage. ADR-048 has already selected/materialized the exact state that should become authoritative. Introducing a target worktree or pre-advancing a local target ref would create a false intermediate state and unnecessary crash/recovery surface.

A second problem is stale target movement. A candidate authorized from target baseline `B` cannot be published merely because a later target `D` still happens to be an ancestor of `C`; the trusted target/policy baseline changed. The target mutation must therefore compare the exact authoritative old OID, not merely ask whether some current fast-forward remains possible.

Finally, a crash may occur after the authoritative target accepted `C` but before the CoordinationStore adopts the effect. Recovery must infer truth from current authoritative history rather than replaying from a stale journal cursor.

## Decision

Backlog item **30.22 is closed**.

### 1. DIRECT advancement begins only after exact candidate materialization and verification

ADR-052 consumes:

```text
exact target/effective baseline B
exact current PromotionUnit P
exact ADR-048 candidate C
valid development-validation evidence bound to C
current DIRECT authorization
```

It does not change candidate-tree/materialization semantics.

### 2. The normative operation is `AdvanceTargetFF(target, expected_old=B, new=C)`

The core semantic contract is:

```text
REQUIRE:
  authoritative current(target) == B
  B ancestor-or-equal C
  current EffectivePromotionPolicy authorizes DIRECT
  exact C remains the current verified candidate for the promotion obligation
  current target-operation claim/fence is held
  any contextually required backend capability/current facts are fresh

EFFECT:
  atomically change target B → C

FORBID:
  any target mutation when current(target) != B
  any non-fast-forward target transition
  any history rewrite/rebase/reset semantics
```

`B == C` is already-realized/no-op state, not a new mutation.

The target mutation is one exact-old compare-and-swap **and** fast-forward effect. Either guard failing means no target mutation.

### 3. There is no target worktree/merge staging step

After ADR-048, target advancement is a pure ref operation. The correctness path MUST NOT require:

```text
checkout of the target
merge into a target worktree
pre-advancement of a local target branch/ref
re-materialization of C during target advancement
```

A backend may use implementation-private plumbing, but no local target ref moved ahead of the authoritative target is considered semantic staging or success evidence.

### 4. Exact expected-old mismatch makes the attempt stale even if a fast-forward would still be possible

Immediately before mutation, the authoritative target is re-observed.

```text
observed target == B
→ exact-old guard may proceed

observed target != B
→ no mutation
→ current operation attempt is stale
→ refresh/re-resolve target baseline, policy, candidate/materialization and evidence as required
```

This rule is stricter than “current target remains an ancestor of C” because repository policy authorization is bound to the authoritative target baseline.

### 5. The core is backend-neutral; backends must satisfy the semantic CAS+FF contract

The core does not encode a particular Git CLI/provider mechanism. Conceptually:

```text
TargetAdvanceBackend.can_execute(AdvanceTargetFF, exact_context)
TargetAdvanceBackend.execute(AdvanceTargetFF)
```

Local Git, remote Git, provider-native, or another backend is conforming only if the exact observed effect satisfies the same expected-old + descendant-only contract. A generic ability to force/update a ref is not evidence that DIRECT target advancement is supported.

No backend mechanism may turn capability into authorization or weaken the no-non-FF target invariant.

### 6. The candidate uses an attempt-scoped non-business recovery anchor

Before an external/authoritative mutation can become uncertain, exact `C` MUST remain durably reachable through a correctness-critical attempt/incarnation-scoped anchor, conceptually:

```text
refs/Ruu/operations/<operation>/<attempt>/candidate → C
```

The exact physical namespace is implementation-specific but must obey ADR-042 non-reuse/fencing rules. This anchor is not a ContributionUnit ref, ConvergenceUnit ref, target, submission ref, or semantic branch. Names are never parsed for identity/meaning.

The logical operation durably records at least:

```text
target_ref
expected_old_oid = B
candidate_oid = C
promotion_unit_id
policy/capability fingerprint(s) required for the attempt
verification evidence identity
operation/attempt identities
```

### 7. Recovery adopts from authoritative target history

After crash, timeout, transport ambiguity, or lost response, recovery observes the authoritative target rather than assuming the last attempted step.

For operation `(B → C)`:

```text
current target == B
→ effect not realized
→ retry only after all current guards are freshly satisfied

current target == C
→ effect realized
→ adopt

C ancestor current target
→ effect realized, followed by later target advancement
→ adopt the promotion effect without rolling target back

otherwise
→ effect not proven
→ stale/drift/recomputation path; never invent success
```

Because Git commit ancestry is immutable, `C ancestor current target` is durable evidence that the target history incorporated `C`, even if another actor advanced the target after the successful promotion but before recovery.

### 8. Physical cleanup is separate from durable adoption/audit retention

While the target-advancement obligation is nonterminal and recovery may require exact `C`, its recovery anchor remains `REQUIRED`.

After durable Adoption records that the promotion effect is realized and no recovery obligation requires the physical anchor:

```text
recovery anchor → GC_ELIGIBLE
```

Best-effort physical cleanup occurs later under ADR-042. Removing the anchor never deletes durable operation/adoption/audit history.

### 9. DIRECT target advancement remains localized and idempotent

An expected-old mismatch or backend refusal blocks/stales only that exact target obligation. Unrelated obligations in the global sweep continue. A retry/recovery converges on current authoritative target truth and never replays a target mutation blindly.

## Consequences

- DIRECT target advancement is simpler than a checkout/merge workflow: candidate creation and target mutation are cleanly separated.
- The target baseline used for policy/candidate derivation is protected by exact-old CAS.
- A local target branch is not a correctness-critical staging artifact.
- Crash after successful publication is recoverable even when the target advances again before restart.
- Recovery anchors protect exact candidate reachability without becoming business refs.
- Backend/provider optimizations remain possible without allowing provider mechanics to redefine target semantics.
- `ruu` still never rolls back later valid target advancement merely to make its metadata look current.

## Rejected alternatives

### Checkout/merge into a local target then push

Rejected. ADR-048 already produced the exact candidate; this duplicates composition work and creates misleading local-target intermediate state.

### Pre-advance local target as staging

Rejected. A crash can leave local target at `C` while the authoritative target remains `B`, making local branch position an unreliable success signal.

### Publish whenever the current target still fast-forwards to the old candidate

Rejected. If target moved from `B`, the trusted target/policy baseline changed. Exact-old equality, not merely ancestry, is required before mutation.

### Blind retry after an uncertain push/provider response

Rejected. ADR-042 requires exact Observation before Adoption/retry. Current target history determines whether the effect occurred.

### Let a backend's generic force/ref-update feature define correctness

Rejected. Backends implement a core-defined semantic operation; capability does not authorize non-FF or weaken exact-old requirements.

## Relationship to prior ADRs

Builds on ADR-005 exact-state/CAS coordination, ADR-017 descendant classification, ADR-026 DIRECT policy, ADR-029/030 exact external development-validation evidence, ADR-041 target-operation claims, ADR-042 recoverable-effect journaling/fencing/GC, ADR-043/044 promotion-policy authority/currentness, ADR-048 exact candidate materialization, and ADR-051 semantic backend capability normalization.

Closes backlog **30.22**. ADR-053 subsequently closes 30.23, ADR-054 closes 30.24, ADR-055 closes 30.25, ADR-056 closes 30.26, ADR-057 reclassifies development-validation execution, and ADR-058/ADR-059 close 30.27; the remaining genuine open core items are 30.28, 30.34, and 30.36; 30.39 is already closed by ADR-048.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-061

`AdvanceTargetFF` always acts on the immutable ConvergenceUnit/PromotionUnit PromotionTarget. Policy authorizes DIRECT for that target but does not choose it. Expected-old CAS continues to guard the mutable current target OID; target identity itself is stable.

## Amendment — ADR-062 (2026-09-07)

Historical `DIRECT` now means `target_realization_route = DIRECT_TARGET_ADVANCE`. This ADR remains the only direct target-ref mutation semantic. On `PROVIDER_SUBMISSION`, the Git ref engine cannot use ADR-052 against the target; provider-governed finalization may nevertheless realize the target when separately required/supported/authorized.

## Amendment — ADR-065 (2026-09-07)

ADR-052's recovery observation (`target == C` or `C ancestor-of target`) is now the `NATIVE_EXACT | NATIVE_ANCESTRY` branch of the general ADR-065 `PromotionRealizationProof`. DIRECT behavior is unchanged; ADR-065 generalizes terminal proof to provider rewrites without weakening ADR-052 exact-old CAS+FF mutation semantics.

## Amendment by ADR-066 — DIRECT success is route-compatible realization, not process attribution

The exact-old CAS+FF operation remains the normative mutation performed by `ruu` when it itself advances a DIRECT target. However, terminal DIRECT realization is not restricted to effects personally authored by the `ruu` process.

If fresh target observation proves `C` equal to or ancestor of the current target and DIRECT is the applicable route for that realization, a legitimate user/agent direct Git advancement may satisfy the same promotion obligation. `ruu` reconciles ordinary Git progress rather than monopolizing target writes.

If policy/route drift occurred between earlier planning and recovery, old DIRECT authorization is not a future mutation capability. Candidate inclusion may be historically adopted under an old DIRECT route only when enough authoritative chronology/provenance establishes that the direct effect occurred while DIRECT was applicable; otherwise recovery fails closed. Target still at expected-old `B` always means any new CAS attempt requires fresh current guards.
