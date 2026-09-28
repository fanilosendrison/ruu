---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Separate logical submission revision from ref effect"
id: "ADR-090"
status: "accepted"
date: "2026-09-28"
decision_body_sha256: "dc8a179eee6dfe7ccde683bdd82689f21ef6272fae639b0fa929cc29ba3d12a0"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-089"
  supersedes: []
  confirms:
    - "ADR-042"
    - "ADR-048"
    - "ADR-049"
    - "ADR-066"
governs:
  - "Logical submission-revision need versus physical submission-ref effect classification"
  - "Same-head logical revision adoption"
  - "Exactly-once recovery for no-ref-effect revision transitions"
  - "Per-revision projection history when successive revisions share one head"
---

# ADR-090 — Separate logical submission revision from ref effect

## Context

ADR-089 correctly separates semantic `REVISE_SUBMISSION_HEAD`, exact Git ref-effect classification, and backend transport. It classifies equal heads as `NOOP` and currently states that equality retains the existing bound logical revision.

That last implication conflicts with the exact binding model already established by ADR-048, ADR-049, and ADR-066.

ADR-048 may reuse an existing exact candidate commit when ancestry reduction proves that a newly materialized immutable PromotionUnit is already represented by that commit. Therefore distinct exact PromotionUnits can legitimately materialize the same candidate and provider head:

```text
PromotionUnit P1
→ candidate C
→ submitted head H

later:

PromotionUnit P2 where P2 != P1
→ candidate C
→ submitted head H
```

ADR-049 makes `promotion_unit_id`, `submission_revision`, exact current head, episode/ref identity, and provider identity part of the exact bound revision. ADR-066 requires the applicable exact `SubmissionProjectionProof(C,H)` in each route-conformant revision history.

The physical relation is:

```text
H1 == H2
```

so no Git ref mutation is required. The logical binding nevertheless changes from the revision for `P1` to the revision for `P2`. Retaining the old revision would either lose the current `P2` binding or require mutation of immutable historical revision state.

The material discovery is therefore an authority conflict in the current reading:

```text
ADR-048 / ADR-049 / ADR-066
→ a changed exact revision binding must remain representable and immutable

ADR-089 equality branch
→ unconditionally retains the old revision
```

The correction must preserve every ref-role, authorization, expected-old, recovery, restack, and route-proof boundary established by ADR-089 while separating logical revision adoption from physical ref movement.

## Decision

### 1. Determine logical revision need before classifying the ref effect

Ruu first determines whether the current exact bound revision and the newly required exact binding are the same logical revision state.

Conceptually, the revision binding includes the existing exact revision-bound identities and proofs, including:

```text
submission_id
promotion_unit_id
applicable exact candidate C
current_submission_head H
SubmissionProjectionProof(C,H)
publication_episode_id
submission_ref
provider_submission_identity when applicable
publication destination/relation identity
```

The bound revision record also carries the monotonic `submission_revision` ordinal. That ordinal is the result of adoption, not an input to the comparison that determines whether a new binding is required. This list does not replace the canonical schemas owned by their existing decisions. It identifies why exact head equality alone cannot decide logical revision identity.

```text
required exact binding == current exact binding
→ no new logical revision required

required exact binding != current exact binding
→ one new logical revision required
```

A repeated request or observation of the same exact binding never creates another revision.

### 2. Classify only the physical ref effect from exact heads

After the semantic revision requirement and required exact head are known, exact Git state classifies only the physical submission-ref effect:

```text
H1 == H2
→ REF_NOOP

git-is-ancestor(H1,H2)
→ FF_SUBMISSION_REF_ADVANCE

otherwise
→ NON_FF_SUBMISSION_PROJECTION_REPLACEMENT
```

`REF_NOOP` replaces ADR-089's ambiguous bare `NOOP` wording where that wording was read as both a physical classification and a logical-revision decision.

The exact equality/ancestry classification remains solely a Git fact. Policy, UserBehavior, provider terminology, and the changed logical binding cannot relabel it.

### 3. Allow one new logical revision with `REF_NOOP`

When a new exact logical binding is required and `H1 == H2 == H`:

```text
BOUND(r, binding1, H)
+ newly required binding2 where binding2 != binding1
+ required exact head H
→ REVISING
→ physical ref effect = REF_NOOP
→ no local, remote, or provider ref mutation
→ authoritative observation confirms applicable heads remain H
→ adopt binding2 exactly once
→ BOUND(r+1, binding2, H)
```

The adopted revision records the new exact `promotion_unit_id`, applicable candidate/projection binding, and immutable per-revision proof history even though the provider head OID is unchanged.

`REF_NOOP` means exactly:

```text
no submission-ref mutation
```

It does not mean:

```text
no logical submission-revision transition
```

### 4. Preserve the true no-op case

When the newly required exact logical binding equals the current binding and the required head is already `H`:

```text
BOUND(r, binding, H)
+ same required binding
+ H1 == H2 == H
→ REF_NOOP
→ remain BOUND(r, binding, H)
```

No new Operation, revision, or proof-history entry is invented merely because reconciliation repeats.

### 5. Make same-head adoption durable and exactly once

A same-head new-binding transition uses ADR-042's existing durable operation and fenced adoption model. Its immutable semantic intent distinguishes:

```text
current logical binding
required new logical binding
current exact head H
required exact head H
required physical effect = REF_NOOP
```

The transition performs no external Git mutation. Adoption still requires current run fencing, exact current managed-state CAS, the applicable new `SubmissionProjectionProof(C,H)`, and authoritative observation that the relevant local/remote/provider head remains exact `H`.

One logical revision Operation has at most one Adoption. A crash or retry:

```text
before Adoption
→ re-observe exact binding/head/proof state
→ adopt once if still current and fully proven

after Adoption
→ observe the required binding already current
→ no second increment
```

A state scan without durable matching semantic revision intent cannot invent a new revision merely because another PromotionUnit can map to the same head.

### 6. Do not require mutation-only guards for `REF_NOOP`

Because `REF_NOOP` performs no ref mutation:

```text
no expected-old ref update executes
no FF transport capability is consumed
no non-FF replacement authorization is consumed
no force-like backend mechanism exists
no previous-head reachability root is removed
no SUBMISSION_REVISION_OID_ANCHOR is required solely by this no-ref effect
```

All semantic revision, exact binding, current episode, policy, provider, proof, claim, fence, and transition-local prerequisites that apply independently of ref mutation remain controlling. This decision grants no authorization and weakens no existing guard.

### 7. Keep per-revision projection history exact when heads repeat

Successive logical revisions may share one provider head:

```text
revision r:
P1
→ C
→ SubmissionProjectionProof(C,H)
→ H

revision r+1:
P2
→ C
→ SubmissionProjectionProof(C,H)
→ H
```

The historical records are distinct because their logical revision bindings differ. Git ancestry or OID inequality between successive provider heads is not required.

ADR-066's terminal provider chain for the current revision remains:

```text
C
→ SubmissionProjectionProof(C,H)
→ ProviderFinalizationObservation(H,R)
→ authoritative target observation R→O
```

No synthetic `H1 → H2` movement or synthetic candidate commit is introduced.

### 8. Re-evaluate facts by their complete existing binding

A same-head logical revision does not imply blanket invalidation or blanket inheritance of provider facts.

```text
fact bound only to exact H and other unchanged dimensions
→ may remain reusable only under its existing currentness contract

fact also bound to changed promotion_unit_id, candidate, projection proof,
submission revision, policy, episode, or another changed dimension
→ must be rebound, re-observed, invalidated, or re-established as its
  existing contract requires
```

Equality of `H` alone never authorizes reuse beyond the complete binding of the fact.

### 9. Preserve every other ADR-089 boundary

This decision changes only the implication from equal heads to logical revision adoption. It does not change:

```text
REVISE_SUBMISSION_HEAD semantic vocabulary
FF expected-old effect contract
non-FF exact expected-old replacement contract
non-FF current-episode ref-role confinement
fresh policy authorization and contextual capability
blind-force prohibition
same-open-episode continuity
no-topology-fallback rule
SUBMISSION_REVISION_OID_ANCHOR retention when a non-FF effect removes H1 as a root
ADR-050 immutable-source restack semantics
ADR-066 exact route-conformance proof
unexpected-movement drift classification
```

### 10. Amend the downstream qualification oracle

Issue #52 remains the owner of dedicated provider-neutral state-space and native-Git qualification. Before execution, its oracle must include at least:

```text
new required logical binding + H1 == H2
→ REF_NOOP
→ no ref mutation
→ adopt revision r+1 exactly once

unchanged required logical binding + H1 == H2
→ REF_NOOP
→ remain at revision r

crash/retry before or after same-head Adoption
→ at most one revision increment

distinct successive revisions sharing H
→ preserve distinct immutable promotion-unit/candidate/C→H bindings

REF_NOOP
→ no non-FF authority, replacement capability, or old-head anchor consumed
```

Existing ADR-089 qualification obligations remain unchanged for FF and non-FF effects. No qualification package is created by this decision.

## Alternatives considered

- **Retain the old logical revision whenever heads are equal:** Rejected because a changed `promotion_unit_id` or candidate/projection binding could not be recorded as the current exact immutable revision.
- **Mutate the existing revision binding in place:** Rejected because it destroys immutable exact revision/projection history and makes retry/adoption identity ambiguous.
- **Manufacture a distinct Git commit or ref movement:** Rejected because Git equality is an exact fact and architecture must not create synthetic object identity merely to signal a logical generation.
- **Increment on every repeated request for the same head:** Rejected because head equality alone does not establish a new logical binding and would violate exactly-once adoption.

## Consequences

### Benefits

- ADR-048 can reuse an exact commit without losing the identity of a later PromotionUnit.
- ADR-049's revision-bound `promotion_unit_id` remains immutable and current.
- ADR-089's physical Git classification remains exact.
- ADR-066 preserves one exact projection/finalization/target chain per applicable revision even when heads repeat.
- #52 receives an unambiguous exactly-once oracle.

### Costs and obligations

- Revision state and durable Operations must identify exact old and required logical bindings, not only `H1` and `H2`.
- Recovery must distinguish a genuinely new same-head binding from replay of an already-adopted binding.
- Current-reading specifications must replace equality-implies-no-revision wording with `REF_NOOP` effect semantics.
- Issue #52 qualification must cover same-head new-binding adoption, crash/retry windows, duplicate observations, and the unchanged-binding true no-op case.

## References

- `docs/specification/ruu-spec.md`
- `docs/adr/adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md`
- `docs/adr/adr-048-materialize-repository-local-multi-source-promotion-units-by-canonical-pairwise-merging.md`
- `docs/adr/adr-049-separate-stable-submission-identity-and-refs-from-internal-exact-state.md`
- `docs/adr/adr-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md`
- `docs/adr/adr-089-confine-non-fast-forward-submission-updates-to-exact-expected-old-projection-replacement.md`
- GitHub Issue #51
- GitHub Issue #52
