# ADR-050 — Derive stacked publication from unsatisfied promotion dependencies and restack by exact-state transplant

**Status:** Accepted  
**Closes:** backlog 30.20  
**Amends:** ADR-027, ADR-028, ADR-039, ADR-047, ADR-048, ADR-049  

## Context

A development session/PromotionGroup does not choose “stacked PR” as a publication preference. A stack appears naturally when a repository-local promotion is authored/materialized on top of another promotion that is not yet realized in the authoritative target.

Example:

```text
target M
Session S1 -> candidate A -> PR1 still open
Session S2 is built on A -> candidate B

M -- A -- B
```

Publishing B independently against M would expose/include the still-unrealized A changes again. The natural provider representation is therefore:

```text
PR1: M -> A
PR2: A -> B
```

If A later changes to A', the descendant provider representation B is stale and must be reprojection/restacked without rewriting S2's immutable internal exact state.

Earlier wording treated PromotionTopology/stack dependencies as explicit external/caller input. That is too strong for v1: the dependency is an exact state fact derivable from the promotion's recorded effective-base lineage and the current unresolved predecessor promotion, not a user/agent publication decision.

## Decision

Backlog item **30.20 is closed**.

### 1. Stacked publication is a derived representation, not caller intent

`ruu` MUST NOT require the user, coding agent, invocation caller, or External Control Plane to request `STACKED_PR` as a publication preference.

For one repository-local promotion `Pchild`, `ruu` derives an unsatisfied predecessor dependency when current exact facts establish that the effective base on which the child promotion is represented is supplied by another known promotion `Pparent` whose effect is not yet realized in the authoritative target.

The authoritative derivation uses exact managed facts such as:

```text
child exact_effective_base_oid
parent current exact candidate/submission head
parent logical submission/promotion identity
current authoritative target ancestry/state
```

Branch names, task names, session names, caller identity, completion order, or arbitrary/incidental ancestry alone are not semantic authority.

PromotionTopology remains useful as **derived managed topology state** recording these current dependency relations; it is not a caller-authored PR-layout preference.

### 2. A stack exists only while a dependency is unsatisfied by the target

For child `P2` and predecessor `P1`:

```text
P2 independent of any unresolved predecessor
→ ordinary independent promotion

P2 depends on P1
AND P1 effect already realized in authoritative target
→ ordinary promotion against current target

P2 depends on P1
AND P1 not yet realized in target
AND policy/provider can represent the dependency
→ stacked provider publication

P2 depends on P1
AND P1 not yet realized in target
AND no supported/authorized stacked representation exists
→ child publication waits/blocks locally; correctness is preserved
```

Stack capability is therefore a concurrency/non-blocking capability, not a correctness requirement.

### 3. Repository projection never invents a stack

ADR-047 remains valid that one `(promotion_group_id, repository_id)` projection is never split merely to create stacked PRs.

Stacks relate already-distinct repository-local promotion obligations produced by distinct logical promotion boundaries. Dependency derivation does not change PromotionGroup membership or PromotionUnit exact identity.

### 4. Every dependent submission revision has an immutable owned-state anchor

For a dependent promotion, the currently verified internal candidate records the exact base on which its owned effect was materialized:

```text
owned_base_oid = B0
owned_candidate_oid = C0
```

`C0` is the exact verified candidate representing the child promotion over `B0`. This pair is immutable evidence for that exact child incarnation; provider restacking never rewrites it.

When the predecessor changes, the old provider head is not used as the semantic source for the next restack. Restack always starts from the current immutable owned anchor for the child promotion.

### 5. Restack semantics are exact three-way state transplant

When the predecessor base changes:

```text
old owned base  = B0
owned candidate = C0
new parent/base = B1
```

`ruu` computes the restacked tree by a versioned full three-way merge/state-transplant semantic equivalent to:

```text
merge-base = B0
ours       = B1
theirs     = C0
```

This means:

```text
preserve predecessor evolution B0 -> B1
+
reapply only the aggregate child-owned effect B0 -> C0
```

The algorithm works on exact aggregate states, not an arbitrary replay of the child commit sequence. Internal ConvergenceUnit/PromotionUnit histories may contain several sources/merges; ADR-048 has already condensed that promotion incarnation into the exact verified `owned_candidate_oid` over its exact base.

The restack contract records all determinism-relevant merge backend/version/configuration just as ADR-048 does for candidate materialization.

### 6. Restacked submission head is a provider projection, not a new internal source state

For a clean transplant producing tree `T1`, `ruu` creates/materializes one exact submission head `H1` whose provider-visible base/parent relation is the new exact predecessor/base `B1` and whose tree is exactly `T1` under the versioned RestackContract.

`H1` is not a new ConvergenceUnit state and does not rewrite `C0` or its sources.

```text
INTERNAL OWNED STATE
B0 -> C0       immutable

SUBMISSION PROJECTION
B1 -> H1       rewriteable under ADR-049 revision rules
```

### 7. Restacks do not accumulate projection drift

If the predecessor moves repeatedly:

```text
B0 -> B1 -> B2
```

future restacks are recomputed from the current immutable owned child anchor, not by transplanting the previously restacked provider head again:

```text
Restack(B0,C0,B1) -> H1
Restack(B0,C0,B2) -> H2
```

not:

```text
H1 -> H2 -> H3 ... as semantic source
```

If the child itself receives new authored semantic code, ordinary convergence/ADR-048 produces a new exact PromotionUnit/candidate and therefore a new owned `(base,candidate)` anchor for subsequent restacks.

### 8. Conflict requires semantic reconciliation; Ruu does not author it

If the exact state transplant conflicts in a way requiring semantic code authoring:

```text
→ RESTACK_BLOCKED / RECONCILIATION_REQUIRED
```

with exact old-base, owned-candidate, new-base, conflict-path/kind, contract, and current dependency evidence.

`ruu` does not choose a conflict resolution, switch algorithms/order to force success, or mutate internal refs. The Development System authors new code through the ordinary pipeline if needed.

### 9. Every new exact restacked head is development-validated

A clean restack result is not authoritative merely because both old states were verified.

```text
new exact restacked head H1
→ valid development-validation evidence bound to H1
→ submission-specific validation
→ expected-old guarded ADR-049 ref/provider rewrite
→ provider head observation == H1
→ submission_revision++
```

Exact-equal results may reuse evidence only under the ordinary ADR-030 exact-state/context contract.

### 10. Local semantics are normative; executor is pluggable

The normative restack result is defined by the exact state-transplant contract above.

Execution MAY be:

```text
LOCAL_RUU
PROVIDER_NATIVE
EXTERNAL_TOOL_ADAPTER
```

provided current policy/provider capabilities authorize it and the exact observed result satisfies the same contract.

For provider/external execution, the executor is not semantic authority. `ruu` observes the produced exact head/tree, validates it mechanically against the expected exact transplant result/invariants, requires current exact external development-validation evidence when policy requires it, and only then adopts the new submission revision.

If provider capability cannot guarantee/produce a conforming result, Ruu uses a conforming local path or leaves the dependent promotion waiting rather than silently changing publication structure.

### 11. Dependency satisfaction collapses the stack naturally

When the predecessor's effect becomes part of the authoritative target, the dependency is `SATISFIED_BY_TARGET`.

The child no longer needs a stacked provider base merely because it was previously stacked. It is reconciled as an ordinary promotion against the current target, rematerialized/restacked if exact base currentness requires it.

Thus stack membership is current-state-derived and may appear/disappear as the target evolves.

### 12. Restack remains an ADR-042 recoverable external effect

Restack uses:

```text
Operation
→ Attempt
→ exact Observation
→ Adoption
```

and is fenced by logical submission identity, exact current revision/head, exact owned anchor, exact new base, policy/capability fingerprint, RestackContract, and expected-old guards.

Crash/retry/recovery adopts already-produced provider/local state only when all these facts still match current authoritative state. Otherwise the attempt is stale and current state is reconciled afresh.

## Consequences

- Users/agents never need to decide “stacked PR” before invoking Ruu.
- A stack is the provider projection of a real unresolved promotion dependency.
- Providers without stack support remain correct; dependent publication simply waits.
- Restacking preserves immutable internal exact state and rewrites only the submission layer.
- Aggregate exact-state transplant avoids replaying arbitrary commit narratives and handles multi-ConvergenceUnit child promotions naturally.
- Repeated predecessor revisions do not accumulate projection drift.
- Provider-native restack can be used as an optimization/executor without becoming semantic authority.

## Superseded wording

This ADR supersedes current-v1 wording that says stack dependencies/PromotionTopology must be caller/External-Control-Plane-declared as a publication-layout intent. The External Control Plane remains authoritative for logical PromotionGroup membership and development/runtime declarations, while `ruu` derives current promotion dependency topology from exact managed Git/promotion facts.

## Rejected alternatives

### Caller chooses stacked versus independent publication

Rejected. Stack shape is a consequence of current dependency state, not a publication preference in v1.

### Rebase/replay the child's arbitrary commit sequence

Rejected. It couples publication correctness to narrative commit history, merge preservation, and replay ordering rather than exact managed state.

### Restack from the previous restacked provider head

Rejected. Repeated rewrites can accumulate drift; every restack is derived from the immutable owned child anchor.

### Trust provider-native restack output by identity alone

Rejected. Provider/external tooling is an executor; exact result observation, semantic-contract validation, verification, and adoption remain Ruu responsibilities.

## Subsequent clarification by ADR-051

ADR-051 closes the `supported` side of this ADR's `supported/authorized` guard. The core derives `REPRESENT_PROMOTION_DEPENDENCY` from the exact unsatisfied dependency; the provider adapter reports contextual technical support, while effective policy separately supplies authorization. A provider-native restack mechanism is only an executor for this ADR's exact RestackContract and never semantic authority.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-061

Target facts used to derive predecessor satisfaction/stack representation are observations of the immutable PromotionTarget's current state. Stack/restack derivation may react to target OID movement but cannot change target repository/ref identity.

## Amendment — ADR-062 (2026-09-07)

All stack semantics remain normative, but “stacked PR” is current-reading shorthand for a **stacked provider-submission projection**. Stack shape remains mechanically derived from an unsatisfied exact promotion dependency; GitHub stacked PRs are one adapter realization and never caller-selected workflow intent.

## Amendment by ADR-066 — restack head is the explicit C→H submission projection

ADR-050's existing distinction between immutable owned candidate `C` and restacked provider head `H` now participates directly in terminal promotion proof.

Every provider-facing revision has an exact `SubmissionProjectionProof(C → H)`. Identity publication uses `C == H`; restack uses this ADR's deterministic exact state-transplant contract from immutable `(old_base_oid, owned_candidate_oid)` onto the current new base. Provider finalization binds `H → R`, not `C → R`.

If restack requires semantic authoring, there is no valid automatic `H`; Development System authoring produces a new exact candidate/PromotionUnit through ordinary convergence.

## Clarification by ADR-069

ADR-050 is the normative descendant mechanism when an older PromotionGroup revision changes a predecessor exact state. A clean exact-state transplant updates only the dependent provider/submission projection and does not automatically rewrite the descendant group's immutable owned exact state. Only transplant conflict that creates explicit semantic `RECONCILIATION_REQUIRED` authority may lead to a `REVISE_EXISTING_GROUP` invocation and a new exact descendant PromotionUnit.

## Amendment by ADR-081 — predecessor provenance may begin before promotion

ADR-050 still governs only after a stable parent promotion projection is known. ADR-081 adds the earlier durable AuthoringDependency `(source ContributionUnit, consumed exact OID A)`. A qualifying source handoff accepted after durable dependency-selection TX-A may map that relation to `(source PromotionGroup, repository)` only when the same source ContributionUnit's exact frozen checkpoint `S` contained `A` before downward synchronization, group-local `K` incorporates `S`, source/consumer immutable PromotionTargets are exactly equal, current disposition permits the path, and CAS succeeds. Aggregate `A ancestor-or-equal K` alone is insufficient. Arbitrary candidate ancestry remains non-authoritative.

The child's immutable owned anchor remains `(old_base=A, owned_candidate=B)` even when the parent projection's current exact state is `K`; restack uses `Restack(A,B,K)`. Raw dependencies and more than one independently unsatisfied external predecessor do not invent provider topology and block only affected realization.

