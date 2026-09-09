# Hostile Audit — Ruu ADR-065

**Date:** 2026-09-07  
**Target:** `Ruu-architecture-decisions-final-verified-adr065.zip`  
**Method:** adversarial/falsification pass. The objective is not to confirm the architecture but to find minimal counterexamples, ambiguous authority boundaries, unreachable or under-specified states, and cases omitted from the finite audit dimensions.

## Executive conclusion

The ADR-065 package is not yet architecturally closed.

The hostile pass found:

- **2 high-confidence core counterexamples**
- **1 high-confidence temporal/recovery ambiguity**
- **1 post-terminal observability gap**
- **2 specification/lifecycle inconsistencies**

The two most important findings are related to the provider-submission path:

1. **Native candidate ancestry can currently bypass provider governance.**
2. **ADR-065 binds the wrong object through provider rewrites when the submission head has been restacked or otherwise projected.**

These two findings show that the terminal model should distinguish at least:

```text
PromotionCandidate C
        ↓
SubmissionProjection
        ↓
SubmittedRevision H
        ↓
ProviderFinalization
        ↓
ProviderResult R
        ↓
AuthoritativeTarget O
```

rather than trying to use the direct relation:

```text
C → R
```

for every provider-mediated promotion.

A second, orthogonal distinction is also needed:

```text
realization proof
≠
governance/authorization provenance
```

The fact that code is present in the target does not itself prove that it arrived through the route required by repository governance.

---

# H1 — HIGH — Native ancestry can bypass provider governance

## Current rule

ADR-065 / the main spec currently says that if:

```text
O == C
or
C ancestor-of O
```

then the promotion is natively proven regardless of whether DIRECT or provider mechanics produced that history.

The v33 finite realization model implements exactly that ordering:

```python
if c_rel in ('EXACT','ANCESTOR'):
    outcome='PROVEN_NATIVE_GIT'
```

before checking provider finalization.

## Minimal counterexample

Repository policy says:

```text
target_realization_route = PROVIDER_SUBMISSION
PR / provider governance required
reviews required
checks required
```

`ruu` has exact candidate:

```text
C
```

but no provider finalization has happened.

An administrator or external tool bypasses the expected route and places `C` into `main` directly.

Now:

```text
C ancestor-of main
```

The current ADR-065 realization function concludes:

```text
PROVEN_NATIVE_GIT
```

even though:

```text
provider_finalized = false
provider binding = absent
required PR/reviews/checks may never have happened
```

The current v33 decision function was reproduced with:

```text
route              = PROVIDER_SUBMISSION
candidate relation = ANCESTOR
provider finalized = false
provider binding   = MISSING_OR_MISMATCHED

outcome             = PROVEN_NATIVE_GIT
```

## Why this matters

Git ancestry proves only:

> the candidate is present in target history.

It does **not** prove:

> the candidate entered the target through the governance route that was required.

Therefore:

```text
TargetRealizationProof
```

and:

```text
PromotionGovernanceProof / authorized finalization provenance
```

must not be conflated.

## Suggested direction

For a `PROVIDER_SUBMISSION` route, native ancestry may still be the strongest **Git realization** evidence, but it should not by itself terminalize the PromotionUnit.

At minimum the provider route should also require exact provider-governance completion for the exact submitted revision, or an explicitly defined external adoption/settlement authority for an already-realized out-of-band effect.

Potential state:

```text
TARGET_REALIZED_OUTSIDE_AUTHORIZED_ROUTE
```

when Git proves the code is present but the required provider finalization provenance is absent.

---

# H2 — HIGH — ADR-065 binds PromotionCandidate C directly to R, but restack submits H ≠ C

## Existing restack semantics

ADR-050 intentionally preserves immutable internal candidate state while rewriting only the provider-facing representation.

Conceptually:

```text
old base     = B0
owned candidate = C0

new predecessor/base = B1

Restack(B0, C0, B1)
        ↓
provider-facing head H2
```

and explicitly:

```text
C0 remains unchanged
H2 is the new provider-facing submitted revision
```

This is essential to the existing stack design.

## Current ADR-065 assumption

The provider rewrite proof currently requires the provider to establish:

```text
exact submitted revision OID = C
C → R
```

where `C` is the exact PromotionUnit candidate.

That is only correct when:

```text
submission head H == PromotionCandidate C
```

It is false after a valid restack/update projection.

## Concrete Git reproduction

A real Git shape was constructed:

```text
B0 = 840354f854aa0c59cafd0e392059f32d10a98373
C0 = 90b004957f8469f1f2c731056dddb1e781a2f659
B1 = 2aa03d2079c909cdf11ab8f39bf41af469621aed
H2 = 59f9f379f91159092e15163e3e7deed007a0755b
```

`H2` was built as an exact restack/state-transplant of the child-owned effect `B0 → C0` onto `B1`.

After provider-style target integration:

```text
C0 ancestor-of main = NO
H2 ancestor-of main = YES
```

The actually submitted revision is:

```text
H2
```

not:

```text
C0
```

Therefore a real provider can truthfully attest:

```text
H2 → R
```

but cannot truthfully attest:

```text
"exact submitted revision = C0"
C0 → R
```

because it never received `C0` as the final submitted revision.

The workflow is valid under ADR-050, yet ADR-065's current proof contract can become impossible to satisfy.

## Root cause

The architecture is missing an explicit proof edge between the immutable promotion candidate and the provider-facing revision:

```text
PromotionCandidate C
        ↓
SubmissionProjectionProof
        ↓
SubmittedRevision H
```

ADR-050 already contains most of the mechanics necessary to prove that edge; it simply has not been incorporated into the terminal realization model.

## Suggested direction

General provider proof chain:

```text
PromotionCandidate C
        ↓
exact authorized projection
        ↓
SubmittedRevision H
        ↓
exact provider finalization
        ↓
Result R
        ↓
fresh Git observation
        ↓
AuthoritativeTarget O
```

For an ordinary non-restacked submission:

```text
H == C
```

so the projection edge is identity.

For a restack:

```text
C != H
```

but ADR-050's exact state-transplant contract proves the relationship.

Provider finalization should bind:

```text
H → R
```

not universally:

```text
C → R
```

Possible proof forms on the provider route:

```text
ProjectionProof(C,H)
+ ProviderFinalized(exact H, exact T)
+ H ancestor-of O
```

when submitted ancestry survives,

or:

```text
ProjectionProof(C,H)
+ ProviderFinalized(exact H → R, exact T)
+ R ancestor-of O
```

when provider finalization also rewrites the submitted revision.

This handles ordinary PRs, stacks, restacks, squash, rebase, and merge queues with one chain.

---

# H3 — HIGH / ARCHITECTURAL AMBIGUITY — Authorization time and adoption time are conflated

## Scenario

At `t0`:

```text
policy P0 authorizes provider finalization
```

`ruu` freshly revalidates policy and starts/requests the external effect.

At `t1`:

```text
provider performs the merge/result R
```

At `t2`:

```text
Ruu crashes before Observation/Adoption
```

At `t3`:

```text
repository/provider policy changes to P1
```

At `t4` recovery observes:

```text
R is already in the authoritative target
```

ADR-042 says old observations do not stay fresh and that current policy/fingerprint is revalidated before mutation/adoption.

This creates an unresolved question:

### Interpretation A

Require current `P1` to authorize the already-completed effect before adoption.

Problem:

```text
effect happened validly under P0
+
policy changed after effect
→ recovery can become permanently unable to adopt a real completed effect
```

### Interpretation B

Ignore policy at adoption and adopt from target realization alone.

Problem:

That collapses into H1 and permits out-of-band unauthorized target entry to be treated as a normal successful promotion.

## Required distinction

A durable **historical authorization provenance** for an effect is not the same thing as a reusable stale authorization token.

The effect journal already has:

```text
Operation
Attempt
exact preconditions
exact request/effect fingerprint
```

The architecture likely needs to say:

> a completed external effect may be adopted after crash based on the exact authorization/precondition provenance under which that effect was legitimately initiated/finalized, even if current policy has since changed; current policy governs any new mutation, not whether a historically completed authorized effect actually happened.

Conversely:

> target realization with no acceptable authorization/finalization provenance is an externally realized drift/bypass, not ordinary `PROMOTED`.

This distinction should also cover DIRECT target effects.

---

# H4 — MEDIUM — Post-PROMOTED target drift is declared, but may be undiscoverable

ADR-065 says:

```text
a valid realization proof is adopted
→ later force-rewrite removes R
→ this is a new authoritative-target drift event
```

However, ADR-036 defines the global sweep over **nonterminal managed obligations** and explicitly allows repositories with zero nonterminal obligations to remain quiescent without deep refresh.

After:

```text
PromotionUnit = PROMOTED
ConvergenceUnit = PROMOTED / RETIRED
all recovery obligations = terminal
```

there may be no nonterminal obligation left that causes the target to be observed again.

Therefore the statement:

```text
later drift is handled separately
```

currently has no obvious discovery mechanism.

## Design choice required

Either:

### A. Historical semantics only

Define `PROMOTED` strictly as:

> this promotion was successfully realized at least once.

Then later force rewrite is outside the responsibility of the completed promotion unless another subsystem creates a new explicit monitoring obligation.

This is simple and probably acceptable.

Or:

### B. Current-inclusion semantics

If `ruu` promises that promoted state continues to exist in target, a persistent target-integrity watch/obligation is needed after terminal promotion.

That would materially change the global quiescence model.

The current spec appears to say A for history but casually promises B-style "later drift handling". It should choose one explicitly.

---

# H5 — SPEC CONTRADICTION — 30.36 is both closed and "still open"

The main spec says in its closure summary that ADR-062 closes 30.36.

`OPEN-DESIGN-BACKLOG.md` also marks 30.36 closed.

But the main requirements still contains:

```text
## 30.36 REVIEW_NOT_REQUESTED eligibility policy

Still open only at the Git/policy layer...
```

This is a direct normative-document contradiction.

It did not fail state-space audit v33 because the static assertion checks the companion backlog's closure marker, not the contradictory section in the main requirements.

Fix is straightforward: replace the stale main-spec section with the ADR-062 no-projection default.

---

# H6 — LOW/MEDIUM — Abandonment states remain under-specified

The PromotionUnit generic lifecycle still contains:

```text
ABANDONED
```

but there is no current defined PromotionUnit transition that safely produces that terminal state.

Elsewhere the spec explicitly says partial cross-repository promotion cannot silently become `ABANDONED` and future terminal forms require an ADR.

The ConvergenceUnit lifecycle also exposes:

```text
READY_INTERNAL → explicit abandonment → ABANDONING → RETIRED
PROMOTION_BOUND → abandon/disposition → ABANDONING
```

while ADR-054 says terminal abandonment/disposition semantics require governing decisions and group settlement participates in retirement guards.

Potential dead-end:

```text
PromotionGroup already declares ConvergenceUnit X
X is explicitly abandoned before group settlement
X cannot reopen
PromotionGroup is immutable and still references X
group may never obtain a current READY_INTERNAL resolution
retirement guard still references the unresolved group
```

This may be only stale lifecycle text, but it should be removed or fully specified.

---

# Audit blind spot in STATE-SPACE-AUDIT-v33

The ADR-065 finite family varies only:

```text
route
candidate relation to target
provider C→R binding
provider finalized
R relation to target
```

It does **not** vary:

```text
required provider governance satisfied / bypassed
PromotionCandidate C vs SubmittedRevision H
submission projection kind: identity / restack / update
policy at effect vs policy at recovery/adoption
post-terminal target drift
```

Therefore the 14,518-combination PASS is valid for the tested dimensions but cannot justify the claim that the provider terminal model is closed.

The next state-space revision should explicitly add these missing dimensions.

---

# Recommended next order

## 1. Fix the provider realization model first

Unify H1 and H2 around:

```text
PromotionCandidate C
        ↓
SubmissionProjectionProof
        ↓
SubmittedRevision H
        ↓
ProviderFinalizationProof
        ↓
ProviderResult R (when rewrite destroys H ancestry)
        ↓
AuthoritativeTarget O
```

And separate:

```text
Realization
```

from:

```text
Governance/authorization provenance
```

This should become a new ADR, not a small textual patch to ADR-065.

## 2. Resolve authorization/adoption temporal semantics

Specify what proof allows recovery to adopt a completed effect after policy drift, without turning current target ancestry into governance bypass.

Likely reuse the ADR-042 Operation/Attempt journal as **historical effect authorization provenance**, while keeping current policy revalidation mandatory for any new mutation.

## 3. Decide post-terminal drift semantics

Preferably define `PROMOTED` as historical terminal realization and state explicitly that continuous target-integrity monitoring is outside v1 unless a new nonterminal watch is created.

## 4. Clean stale lifecycle/doc contradictions

- close main-spec 30.36 text;
- remove or define PromotionUnit `ABANDONED`;
- constrain/remove ConvergenceUnit abandonment arrows unless a governing disposition contract exists.

## 5. Add adversarial state-space dimensions and concrete smokes

At minimum:

```text
provider route + C ancestor target + provider governance absent
→ MUST NOT become normal PROMOTED

restack C0→H2 + H2 integrated + C0 absent from target ancestry
→ MUST be provable through projection chain

authorized external effect completes + crash + policy changes
→ deterministic recovery outcome

terminal promotion + later force rewrite
→ behavior matches the chosen historical/current-inclusion semantics
```

---

# Bottom line

The architecture remains strong, but ADR-065 closed 30.34 one abstraction too early.

The missing central distinction is:

```text
PromotionCandidate
≠
SubmittedRevision
≠
ProviderResult
```

and the missing orthogonal distinction is:

```text
"the code is in target"
≠
"the required governance route authorized that target entry"
```

Those two distinctions should be fixed before implementation.
