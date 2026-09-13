---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Bind promotion success to route-conformant Candidate→Submission→Result→Target chains"
id: "ADR-066"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "37f1f181d6348710f7d27b75ee939d235a5e9cadcfb1570e04d0ba3b8e5f59f8"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-042"
    - "ADR-050"
    - "ADR-052"
    - "ADR-054"
    - "ADR-055"
    - "ADR-062"
    - "ADR-065"
  supersedes: []
  confirms: []
governs: []
---

# ADR-066 — Bind promotion success to route-conformant Candidate→Submission→Result→Target chains

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 066
- **Amends:** ADR-042, ADR-050, ADR-052, ADR-054, ADR-055, ADR-062, ADR-065 and the final promotion/recovery model
- **Reopens and recloses:** the proof semantics previously closed as backlog 30.34 by ADR-065
- **Subsequently amended by:** ADR-071 for cancellation/abandonment causal ordering and post-cancel external realization classification; ADR-080 for source-domain local/remote/provider observation authority and webhook evidence semantics

## Context

The hostile review of ADR-065 exposed two conflations.

First, ADR-065 treated native ancestry of candidate `C` in the target as terminal proof even when the authoritative route required provider mediation. That allows a direct target update to satisfy a promotion whose governance required provider submission/finalization.

Second, ADR-065 asked the provider to bind exact candidate `C` directly to final result `R`. ADR-050 already permits an exact provider-facing restack head `H` that differs from immutable owned candidate `C`:

```text
owned candidate C over B0
        ↓ exact ADR-050 state transplant onto B1
submitted revision H
```

The provider actually receives `H`, not necessarily `C`.

The architecture also needs exact recovery semantics when policy changes after an effect was already legitimately engaged. A stale policy snapshot must never authorize a new mutation, but a later policy change must not retroactively erase a previously committed effect.

Finally, none of these rules may turn `ruu` into an exclusive gateway for ordinary Git use. Users and agents may continue to use Git normally; correctness is about route conformance and exact observed state, not about proving that the `ruu` process personally caused every ref update.

## Decision

### 1. Promotion success requires both target realization and route conformance

For exact candidate `C`, immutable PromotionTarget `T`, and authoritative target observation `O`:

```text
PROMOTED
=
exact target realization proof
+
proof that the realization conforms to the authoritative target-realization route
```

The final Git graph alone does not always prove the route.

A provider-required promotion is not successful merely because `C` somehow appears in the target. Conversely, a DIRECT route does not require attribution to the `ruu` process itself; a legitimate user/agent direct fast-forward may satisfy the same direct realization obligation when the route/policy is compatible.

### 2. Provider-mediated realization uses four exact identities: C, H, R, O

The provider path is:

```text
PromotionCandidate C
        ↓ SubmissionProjectionProof
SubmittedRevision H
        ↓ ProviderFinalizationObservation
ProviderResult R
        ↓ authoritative Git observation
ObservedTarget O
```

The identities have distinct meanings:

```text
C = immutable repository-local promotion candidate produced from the exact PromotionUnit
H = exact provider-facing submitted revision for the current submission revision
R = exact final Git result produced/adopted by provider finalization
O = freshly observed current authoritative target OID
```

Any equalities are incidental:

```text
simple publication: C == H may hold
restack:            C != H may hold
squash/rebase:      H != R may hold
target later moves: R != O may hold while R ancestor-of O
```

### 3. C→H is owned/proven by Ruu projection mechanics

A canonical `SubmissionProjectionProof` binds the immutable candidate to the exact submitted revision:

```text
SubmissionProjectionProof {
  promotion_unit_id
  candidate_oid = C
  submitted_revision_oid = H
  projection_kind
  exact projection inputs / contract fingerprint
}
```

Canonical projection classes include at least:

```text
IDENTITY
ADR050_EXACT_RESTACK
```

For `IDENTITY`, `C == H`.

For ADR-050 restack, proof is the exact deterministic state transplant from immutable owned `(old_base_oid, candidate_oid)` onto the exact new base. Every later restack is recomputed from the immutable owned anchor, never from a prior restacked head.

If projection requires semantic code authoring, there is no valid automatic `H`. The conflict yields the existing reconciliation boundary; Development System authoring produces a new exact candidate / PromotionUnit rather than smuggling semantic edits into a submission projection.

### 4. H→R is the provider trust boundary

For `PROVIDER_SUBMISSION`, terminal route proof requires an exact `ProviderFinalizationObservation` bound to:

```text
provider / authoritative target binding
logical submission identity
PublicationEpisode identity when applicable
exact submitted revision OID = H
exact PromotionTarget = T
finalization status = COMPLETED
exact final result OID = R
```

The provider is trusted only for the bounded statement:

> exact submitted revision `H` on this exact provider submission/episode and target was finalized as exact result `R`.

The provider is not asked to know or attest the internal candidate `C`; `ruu` already proves `C → H`.

### 5. R→O is independently proven from authoritative Git

Provider finalization is not sufficient by itself. `ruu` freshly observes the authoritative target and requires:

```text
O == R
or
git-is-ancestor(R, O)
```

Thus the complete provider proof is:

```text
SubmissionProjectionProof(C → H)
+
ProviderFinalizationObservation(H → R on T)
+
GitTargetObservation(R == O or R ancestor-of O)
→ route-conformant provider realization proven
```

Provider `MERGED` / `FINALIZED` without the exact chain is not terminal proof.

### 6. Native candidate ancestry cannot bypass a required provider route

When the current/historically applicable route for the realization is `PROVIDER_SUBMISSION`, the following is insufficient by itself:

```text
O == C
or
C ancestor-of O
```

It proves candidate inclusion, but not provider-route conformance.

Therefore:

```text
provider route required
+ candidate/result appears in target
+ no exact provider finalization chain for the current submission
→ TARGET_REALIZED_WITHOUT_REQUIRED_ROUTE_PROOF / fail closed
→ not PROMOTED
```

`ruu` does not retroactively invent provider governance or silently adopt an out-of-route target mutation.

### 7. DIRECT realization is route compatibility, not actor exclusivity

For `DIRECT_TARGET_ADVANCE`, native Git proof remains the terminal realization proof:

```text
O == C
or
C ancestor-of O
```

provided DIRECT was the route applicable to that realization.

The actor is not part of the semantic proof:

```text
user/agent performs a legitimate direct FF to C
+ DIRECT route is applicable
+ exact target realization is observed
→ may satisfy the same DIRECT promotion obligation
```

`ruu` must coexist with normal Git use and reconcile legitimate external Git progress. Its own coordination claims fence its own competing operations; they do not make `ruu` the exclusive global author of Git history.

### 8. Policy authorizes effect commitment; old policy never grants future mutation authority

A policy snapshot may justify a historical effect only if the exact effect reached its route-specific **effect commitment point** while that authorization was applicable.

Route-specific commitment points are:

```text
DIRECT_TARGET_ADVANCE
→ the exact target ref mutation itself (for Ruu's own operation: atomic expected-old B → C CAS+FF)

PROVIDER_SUBMISSION
→ durable provider acceptance/ownership of the exact finalization operation for exact H/T,
   identified strongly enough to recover the accepted operation
```

The provider may autonomously complete an already accepted operation after a later policy change; recovery may observe/adopt that historical effect if it remains exactly attributable to the accepted provider operation.

An old authorization never permits a new causal action:

```text
effect absent / provider operation not accepted / prior queue entry cancelled
→ any action capable of causing or re-causing the effect
→ requires freshly current policy and ordinary exact guards
```

A network retry carrying the same idempotency token is still policy-sensitive if it could be the first request that actually causes provider acceptance/effect.

### 9. Recovery distinguishes observation/adoption from causing a new effect

After crash or uncertainty:

```text
observe/poll an already accepted provider operation
→ not a new mutation authorization

adopt an already realized route-conformant effect
→ historical recovery

send/re-send an action that may newly cause the effect
→ fresh current policy required
```

If policy drift occurred and the system cannot establish whether the exact effect/commitment happened while the relevant route was authorized, recovery fails closed as `UNKNOWN_INCONSISTENT` rather than using the old policy as an eternal capability.

### 10. DIRECT recovery preserves ordinary Git reconciliation

ADR-052's ordinary no-drift recovery remains state-based:

```text
current target == expected old B
→ effect not realized; any retry uses fresh current guards

current target == C
or C ancestor-of current target
+ DIRECT route is currently applicable
→ direct realization may be adopted regardless of whether Ruu or another legitimate Git actor performed it
```

If DIRECT ceased to be applicable between an earlier observation/attempt and recovery, candidate inclusion alone does not prove that the realization happened before that route drift. Historical adoption then requires enough authoritative chronology/provenance to establish route compatibility at the actual direct effect; otherwise fail closed.

This is a proof/adoption restriction, not a ban on users or agents using Git.

### 11. `PROMOTED` remains a historical completion fact, not a permanent target watch

ADR-054 already defines `PromotionUnit PROMOTED` as the fact that one exact snapshot reached/adopted its terminal promotion outcome. ADR-066 makes that historical reading explicit.

After terminal adoption:

```text
later force rewrite / target drift
≠ retroactive mutation of the historical PromotionUnit state
```

V1 does not continuously resweep every terminal PromotionUnit solely to prove that its result remains in current target history forever. If an external observer or later managed operation discovers target-history corruption/drift, that discovery may create a new integrity/reconciliation obligation under the applicable higher-level policy; it does not rewrite historical `PROMOTED` into nonterminal state.

### 12. No universal semantic-equivalence proof is introduced

The corrected chain remains provenance/exact-state based:

```text
C → H   exact deterministic projection provenance
H → R   exact provider finalization provenance
R → O   authoritative Git inclusion
```

`ruu` still does not define universal patch, tree, textual, or program-semantic equivalence between rewritten objects.

## Consequences

- Provider governance cannot be bypassed by candidate ancestry accidentally appearing in the target.
- ADR-050 restacks fit the final proof model without pretending the provider received internal candidate `C`.
- DIRECT remains compatible with ordinary user/agent Git usage.
- Recovery no longer conflates old authorization with future mutation authority.
- Policy drift after an already committed effect does not retroactively falsify history.
- Terminal PromotionUnit success is historical; continuous post-terminal target-integrity monitoring is not silently introduced.

## Superseded wording

This ADR supersedes ADR-065 wording that:

```text
- makes native candidate ancestry sufficient independent of route;
- requires provider rewrite proof to bind C → R directly;
- treats the provider submitted revision as necessarily equal to C.
```

Current reading is route-conformant `C → H → R → O` for provider realization and native target realization for DIRECT.

## Related decisions

ADR-042, ADR-043, ADR-044, ADR-048, ADR-049, ADR-050, ADR-051, ADR-052, ADR-054, ADR-055, ADR-061, ADR-062, ADR-065.
