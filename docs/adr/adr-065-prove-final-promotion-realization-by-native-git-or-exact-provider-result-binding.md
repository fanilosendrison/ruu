---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Prove final promotion realization by native Git ancestry or exact provider-result binding"
id: "ADR-065"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "271bc8b04f3f8094f1f797fc04ccf572b6e89915d8ebbf3e7bf10d3cc1da89a2"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-029"
    - "ADR-042"
    - "ADR-051"
    - "ADR-052"
    - "ADR-054"
    - "ADR-055"
    - "ADR-057"
    - "ADR-062"
  supersedes: []
  confirms: []
governs: []
---

# ADR-065 — Prove final promotion realization by native Git ancestry or exact provider-result binding

- **Status:** Accepted — final proof semantics corrected/superseded in part by ADR-066
- **Date:** 2026-09-07
- **Decision order:** 065
- **Closes:** backlog 30.34
- **Amends:** ADR-029, ADR-042, ADR-051, ADR-052, ADR-054, ADR-055, ADR-057, ADR-062 and the final target-realization/adoption model

> **Current reading:** ADR-066 supersedes the route-independent native-ancestry shortcut and direct provider `C → R` binding below. Current provider proof is route-conformant `C → H → R → O`; DIRECT native proof remains actor-neutral.

## Context

ADR-062 established that a provider Pull Request / Merge Request is only a projection used when the target-realization route requires provider mediation. The semantic objective remains:

```text
RealizePromotion(exact candidate C, immutable PromotionTarget T)
```

ADR-052 already gives DIRECT target advancement a strong native Git proof. If exact candidate `C` is atomically fast-forwarded into target `T`, then later observation can prove success when the authoritative target is exactly `C` or when `C` is an ancestor of the current target.

The remaining ambiguity appears on `PROVIDER_SUBMISSION` routes. A provider may legally transform the submitted exact candidate before it reaches the target:

```text
squash merge
rebase-style merge
merge queue / merge group finalization
provider-native rewritten merge result
```

In those cases the final authoritative result `R` may have a different OID and may not contain `C` in its ancestry, even though the provider correctly integrated the submitted change.

The architecture therefore needs an exact answer to backlog 30.34:

> what evidence is sufficient for `ruu` to adopt the final target realization and mark the PromotionUnit promoted when provider finalization rewrites Git identity?

Two extremes are rejected:

```text
provider says MERGED
→ trust blindly
```

and:

```text
provider says C → R
→ Ruu must independently prove semantic diff equivalence between C and R
```

The first is too weak because provider UI/API state is not itself authoritative Git-target observation. The second would force `ruu` to define semantic equivalence of rewritten changes across rebases, conflict resolutions, refactors, and queue integration, which belongs outside a Git progression engine.

## Decision

### 1. Promotion completion requires an exact realization proof

A repository-local PromotionUnit may become `PROMOTED` only after `ruu` durably adopts a `PromotionRealizationProof` for its exact candidate `C` and immutable target `T`.

Conceptually:

```text
PromotionRealizationProof {
  promotion_unit_id
  candidate_oid = C
  promotion_target = T
  proof_kind
  realized_result_oid = R
  authoritative_target_observation_oid = O
  provider_finalization_observation?   # required only for provider rewrite proof
}
```

`R` is the exact Git result whose realization is being proven. `O` is the freshly observed current authoritative target OID used to prove that `R` is actually in target history.

The proof is an Observation→Adoption fact under ADR-042, not a semantic review verdict.

### 2. Prefer native Git proof whenever candidate ancestry survives

If fresh authoritative Git observation proves:

```text
O == C
or
git-is-ancestor(C, O)
```

then the promotion is natively proven.

This proof is valid regardless of whether the route was DIRECT or provider-mediated. Examples include:

```text
DIRECT fast-forward
provider fast-forward
ordinary merge commit preserving C ancestry
an externally completed equivalent integration that leaves C in authoritative history
```

The provider does not need to attest a rewrite mapping when Git itself already proves that exact candidate `C` is in target history.

Canonical proof kinds are:

```text
NATIVE_EXACT
NATIVE_ANCESTRY
```

### 3. When ancestry is lost, trust the authorized provider for the exact C → R transformation

If `C` is not an ancestor of the authoritative target because provider finalization rewrote Git identity, `ruu` may still prove realization through an exact provider-result binding.

The provider adapter must establish a canonical `ProviderFinalizationObservation` containing at least:

```text
provider identity / authoritative repository binding
logical submission identity
publication episode identity when applicable
exact submitted revision OID = C
exact PromotionTarget identity = T
finalization status = COMPLETED
exact final result OID = R
```

The observation may be assembled from several provider API facts. No special cryptographic attestation feature is required.

The provider is trusted only for the bounded statement:

> the exact submitted revision `C` for this exact submission/episode and target was finalized by the provider as exact Git result `R`.

This trust is valid only for provider-mediated finalization permitted by the applicable repository/provider governance. Provider capability does not itself authorize a forbidden transformation.

### 4. `ruu` independently verifies that R is really in the authoritative target

Provider binding `C → R` is not sufficient by itself.

After finalization, `ruu` must freshly observe the authoritative Git target and prove:

```text
O == R
or
git-is-ancestor(R, O)
```

The ancestor form deliberately allows the target to advance again after the provider integrated `R` but before `ruu` completed observation/adoption.

Only the conjunction is sufficient when candidate ancestry was lost:

```text
provider exact binding: C → R on T
+
independent Git observation: R ∈ history(T)
=
PROVIDER_RESULT realization proven
```

The canonical proof kind is:

```text
PROVIDER_RESULT
```

### 5. Provider `MERGED` / `FINALIZED` state alone never proves promotion

The following is insufficient:

```text
submission status = MERGED
```

or:

```text
provider finalization operation returned success
```

without an exact result mapping or native ancestry proof.

`PROVIDER_FINALIZED` remains an external/provider lifecycle observation. Promotion becomes terminal only after exact target realization proof is adopted.

### 6. Exact submitted revision binding is mandatory for provider rewrite proof

If the PromotionUnit expects candidate `C1` but the provider finalization observation is bound to `C2`:

```text
C1 != C2
```

then that observation cannot prove the promotion of `C1`.

Likewise, ambiguous provider state such as:

```text
submission merged
but exact submitted revision unknown
```

or:

```text
submitted revision = C
but exact result OID unknown
```

cannot terminalize the PromotionUnit when native ancestry is absent.

The affected realization remains unproven and fails closed pending fresh/recoverable observation.

### 7. Target-result absence remains nonterminal/unproven

If provider binding says:

```text
C → R
```

but fresh authoritative target observation does not contain `R`, `ruu` does not infer success.

Conceptually:

```text
TARGET_REALIZATION_UNPROVEN
```

The reconciler may refresh provider/remote state and recover according to ADR-042. It must not manufacture a new result OID, reinterpret an unrelated target commit as `R`, or mark the PromotionUnit `PROMOTED` merely because the provider submission is closed.

If a valid realization proof was already durably adopted before a later force-rewrite removes `R`, that later rewrite is a new authoritative-target drift event; it does not retroactively erase the historical fact that the promotion had previously been proven and adopted.

### 8. Merge-queue synthetic states are not final realization proof

A merge-group or queue synthetic commit used for testing is not automatically the final `R`.

Only:

```text
native candidate ancestry in the authoritative target
```

or:

```text
exact provider finalization C → final R
+ final R observed in authoritative target history
```

may prove terminal realization.

Queue IDs, merge-group OIDs, effective bases, actor IDs, timestamps, review IDs, check IDs, and provider request IDs are useful audit metadata but are not substitutes for the final proof.

### 9. Independent diff/patch semantic equivalence is not a general prerequisite

`ruu` does not require a universal proof such as:

```text
patch(B,C) == patch(B',R)
```

or semantic-program equivalence between `C` and `R`.

Such comparisons may be recorded opportunistically as diagnostics or stronger auxiliary evidence when mechanically meaningful, for example exact tree equality in a simple squash case. They do not define the general correctness contract and do not replace exact provider binding when ancestry is lost.

The reason is structural: a correct provider rewrite may legitimately adapt a change to a moved target, resolve provider-governed integration state, or otherwise produce a different textual patch while still being the provider-authoritative realization of the exact submitted candidate.

### 10. The provider transformation is a bounded trust boundary

Once repository/provider governance permits a provider to perform squash/rebase/queue/finalization semantics, that provider is part of the trusted computing base for the mapping from exact submitted revision `C` to exact result `R`.

`ruu` does not reimplement the provider's transformation engine in order to distrust it after delegating that transformation.

The trust boundary remains narrow:

```text
provider
→ authoritative for exact transformation relation C → R that it performed

Ruu / Git observation
→ authoritative for whether R is actually present in target T
```

### 11. Observation and adoption are crash-safe and idempotent

The provider finalization operation, provider finalization observation, authoritative Git target observation, `PromotionRealizationProof`, and terminal PromotionUnit adoption remain separate recoverable facts under ADR-042.

Crash examples therefore resolve by observation rather than blind retry:

```text
provider integrated R, process crashed before response
→ rediscover exact provider finalization C → R
→ fetch target
→ prove R in target
→ adopt proof

provider reports completed but result cannot be exactly recovered
→ do not invent success
→ realization remains unproven
```

Once the exact proof is durably adopted, retries are idempotent.

## Rationale

The semantic objective of promotion is not that the final target commit OID must always equal the candidate OID. It is that the exact authorized candidate must be realized in the authoritative target through an allowed route.

Native Git ancestry gives the strongest and simplest proof whenever history is preserved. Provider rewrites necessarily break that identity, so the architecture must either forbid common provider merge modes or trust the provider for the transformation it was explicitly delegated. The latter is more compatible with team repositories, external contributions, squash-only projects, rebase merge policies, and merge queues.

Requiring independent semantic patch equivalence would make `ruu` responsible for answering whether two different code transformations are semantically equivalent. That conflicts with ADR-057/060/063's separation of development semantics from Git progression.

The composite provider proof keeps the boundary narrow and auditable:

```text
exact candidate C
→ exact provider result R
→ independent authoritative target observation
```

## Consequences

- Backlog 30.34 is closed.
- `PR merged` / `ProviderSubmission finalized` is never by itself a terminal PromotionUnit condition.
- DIRECT promotion continues to use ADR-052 native exact/ancestry proof.
- Provider merge commits that preserve candidate ancestry may also use native Git proof.
- Squash/rebase/merge-queue rewrites use exact provider `C → R` binding plus independent `R`-in-target observation.
- Provider finalization observations must bind the exact submitted revision, exact target and exact result OID when ancestry is lost.
- No universal diff/patch/semantic-equivalence engine is introduced into `ruu`.
- Target advancement after `R` is allowed because `R` ancestor-of current target is sufficient.
- Missing/mismatched provider result data fails closed as unproven.
- A durably adopted realization proof remains historical truth even if later target history is force-rewritten; later drift is handled separately.

## Rejected alternatives

### Require final target OID to equal candidate OID

Rejected. It would forbid ordinary merge commits and all provider history rewriting.

### Require candidate ancestry for every provider promotion

Rejected. It would make squash and rebase-style provider workflows unsupported even when repository governance intentionally requires them.

### Treat provider `MERGED=true` as sufficient

Rejected. It does not bind the exact submitted revision to an exact final Git result and does not independently establish the authoritative target state.

### Recompute provider merge/rebase/squash semantics inside Ruu

Rejected. It duplicates the provider transformation engine and still does not solve general semantic equivalence after target movement or conflict adaptation.

### Require patch-id/tree equality for every rewritten result

Rejected. Such checks are useful only in narrower contexts and are not a universal definition of logical realization.

## Amendment by ADR-066 — route-conformant C→H→R→O proof supersedes direct C→R wording

ADR-066 supersedes this ADR's route-independent native-ancestry shortcut and its provider `C → R` binding assumption.

Current reading is:

```text
DIRECT_TARGET_ADVANCE
→ exact candidate C realized in target under a DIRECT-compatible route
→ native exact/ancestry target proof may terminalize the PromotionUnit

PROVIDER_SUBMISSION
→ SubmissionProjectionProof(C → H)
→ ProviderFinalizationObservation(H → R on T)
→ fresh authoritative Git observation proves R == O or R ancestor-of O
→ only then may the PromotionUnit become PROMOTED
```

Candidate ancestry in target does not bypass a required provider route. Provider finalization binds the exact submitted revision `H`, which may differ from immutable internal candidate `C` after ADR-050 restack. ADR-066 also defines route-specific effect commitment and policy-drift recovery: old policy may justify adoption of an already committed historical effect but never a new causal mutation. DIRECT remains compatible with ordinary user/agent Git operations; `ruu` need not prove it personally authored a legitimate direct target advancement.
