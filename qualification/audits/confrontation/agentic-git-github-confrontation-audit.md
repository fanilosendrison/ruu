# Ruu — Confrontation audit against the agentic Git/GitHub model

- **Date:** 2026-09-07
- **Input architecture:** through ADR-061
- **Resulting architecture:** through ADR-063
- **Primary question:** what remains correct in `ruu` once Git is treated as the mechanical history/convergence substrate and GitHub Pull Requests are no longer assumed to be a fundamental unit of agentic development?

## Executive conclusion

The ADR-061 architecture does **not** need to be redesigned from scratch. Its deepest abstractions already align well with an agent-native workflow:

- Git state is exact and authoritative;
- semantic development/testing/review execution is above `ruu`;
- ContributionUnit / ConvergenceUnit / PromotionGroup / PromotionUnit are independent of PR boundaries;
- candidate materialization is exact and repository-local;
- policy/capability/currentness are separate from Git mechanics;
- `Submission` and `PublicationEpisode` already separate provider-facing identity from internal refs;
- final target realization is already distinct from internal convergence.

The primary mismatch was **terminological and architectural elevation of the Pull Request**. The current specification still modeled:

```text
promotion_mode = DIRECT | PR
```

and therefore made PR look like a semantic kind of promotion.

That is the wrong abstraction under the new model.

The corrected model is:

```text
exact candidate C
+ immutable PromotionTarget T
→ RealizePromotion(C,T)

HOW:
  DIRECT_TARGET_ADVANCE
  PROVIDER_SUBMISSION
```

A GitHub Pull Request is now only one provider adapter realization of `ProviderSubmission`.

This change is captured by ADR-062. ADR-063 separately prevents semantic review findings / deferred backlog work from leaking back into the provider-submission lifecycle.

---

# 1. Confrontation with the four enduring Git responsibilities

The new analysis of Git identified four enduring functions:

1. preserve history;
2. support parallel work;
3. transport/synchronize states;
4. compose histories and expose mechanical conflicts.

`ruu` remains strongly aligned with all four.

## 1.1 History

The architecture keeps ordinary Git commits, OIDs, trees, refs and ancestry as the durable state model. ADR-058/059 reinforce native-Git equivalence rather than replacing Git with a proprietary history representation.

**Verdict: retain.**

## 1.2 Parallel work

ContributionUnits, isolated worktrees, ConvergenceUnits, claims, CAS guards, repository-local projections and multi-repository PromotionGroups all address parallel development/convergence directly.

**Verdict: retain.**

## 1.3 Transport / synchronization

Remote refs, provider-facing submission refs, exact expected-old publication, remote observation and recovery remain useful whether producers are humans or agents.

**Verdict: retain.**

## 1.4 Composition / mechanical conflict detection

Internal bidirectional convergence, ADR-048 exact multi-source materialization, ADR-050 restacking, ancestry rules and `RECONCILIATION_REQUIRED` all remain core Git mechanics.

**Verdict: retain.**

The new Git analysis therefore does not undermine `ruu`; it clarifies why the Git-mechanical parts are the durable core.

---

# 2. Confrontation with the broader agentic model

The useful higher-level model is:

```text
Work
Candidate
Evidence
Finding
Authorization
Promotion
```

The audit explicitly tested whether `ruu` should add these as six first-class entities. The answer is **no**.

## Work

Owned by the Development System / External Control Plane.

A Work object may correspond to a user intent, issue, session ship, feature, bugfix or another semantic development unit. Git correctness does not require `ruu` to understand it.

## Candidate

`ruu` already has exact transition candidates. At promotion time the relevant candidate is the ADR-048 exact materialized candidate for one immutable PromotionUnit and current base.

No generic duplicate `Candidate` super-object is required.

## Evidence

Development-quality evidence belongs outside `ruu` under ADR-057/060. Provider checks/reviews/queue state are narrow transition-specific provider facts, not a generic evidence ontology.

No generic Evidence store should be reintroduced.

## Finding

Semantic findings belong outside `ruu`. ADR-063 makes this boundary explicit.

A blocking provider `CHANGES_REQUESTED` state remains core-visible because it is not merely prose/finding semantics; it is a current provider-governance fact that blocks progression.

## Authorization

The conceptual authorization boundary already exists as a fresh conjunction:

```text
REQUIRED
∩ SUPPORTED
∩ AUTHORIZED
∩ exact transition-local prerequisites
```

plus policy/provider currentness.

A durable generic Authorization token would be dangerous because it could stale. ADR-043/044's immediate revalidation remains the stronger design.

## Promotion

Promotion is now stated explicitly as:

```text
RealizePromotion(exact candidate, immutable PromotionTarget)
```

This is route-independent.

---

# 3. The Pull Request was the main conceptual mismatch

Before this audit, the main document still exposed:

```text
promotion_mode = DIRECT | PR
```

This encoded a historical GitHub workflow assumption into the semantic promotion model.

The problem is not that PRs are useless. The problem is that a PR combines many responsibilities that the agentic architecture already separates:

```text
candidate representation
+ diff
+ publication
+ CI
+ review
+ comments/findings
+ approval
+ queue
+ merge/finalization
+ human discussion
```

`ruu` already has independent abstractions for most of these concerns. Keeping `PR` as a fundamental promotion mode therefore made the model less coherent than the actual architecture.

## Decision

Replace:

```text
promotion_mode:
  DIRECT | PR
```

with:

```text
target_realization_route:
  DIRECT_TARGET_ADVANCE
  PROVIDER_SUBMISSION
```

The semantic promotion remains one operation regardless of route.

---

# 4. What a ProviderSubmission is now

`ProviderSubmission` is a **projection of a concrete exact candidate into an external provider workflow**.

Provider examples:

```text
GitHub → Pull Request
GitLab → Merge Request
other provider → native change/submission object
```

The canonical core identity remains the ADR-049/055 model:

```text
submission_id
publication_episode_id
submission_revision
submission_ref
provider_submission_identity
current_submission_head
```

This is important: ADR-049 was not a mistake to remove. It had already found the correct abstraction under the PR terminology.

The audit therefore **retains and strengthens Submission/PublicationEpisode**, while demoting PR to provider-adapter vocabulary.

---

# 5. Provider submission is not internal readiness

The architecture now explicitly rejects:

```text
open PR
→ use PR existence to discover whether work is ready
```

Instead:

```text
Development System work
→ tests / semantic reviews / corrections
→ internal Git convergence
→ exact promotion candidate
→ provider projection when current route/governance requires it
```

Provider-side CI or review can still add independent governance facts after projection. This does not make the PR the source of internal candidate readiness.

---

# 6. No automatic draft PR merely because a candidate exists

This closes old backlog item 30.36.

Previously, `REVIEW_NOT_REQUESTED` existed as an exceptional path but the deterministic fallback was unresolved.

Under the projection model the answer becomes simple:

```text
REVIEW_REQUESTED established
→ nominal provider projection may occur

explicit current authority/need for early publication
→ REVIEW_NOT_REQUESTED provider projection may occur

neither
→ no provider submission yet
```

There is no reason to create a draft PR just to give an internal candidate a GitHub object.

This is both fail-closed and conceptually cleaner.

---

# 7. PRs remain mandatory where the external protocol requires them

Demoting PR from core ontology does not remove practical PR support.

## Team repository

If branch protection / organizational governance requires GitHub PR + reviews + required checks + merge queue, `PROVIDER_SUBMISSION` projects the exact candidate as a GitHub PR and obeys those facts.

## External contribution

If contribution to an upstream repository requires fork → Pull Request, the cross-repository ProviderSubmission adapter does exactly that.

## Solo repository

If policy permits direct target advancement, no PR is required:

```text
DIRECT_TARGET_ADVANCE
→ ADR-052 exact-old CAS+FF
```

The provider surface is therefore conditional on governance rather than universal.

---

# 8. Automatic merge/finalization after authorization

The audit adopts the new distinction:

```text
AUTHORIZED
≠
MERGED
```

But `ruu` does not add a stale durable generic Authorization token.

Instead, current authorization is reconstructed immediately before effect from:

```text
operation REQUIRED
+ capability SUPPORTED
+ policy AUTHORIZED
+ provider/governance prerequisites satisfied
+ exact submission/head/target currentness
+ claim/fencing/recovery guards
```

When all of those hold, `ruu` should progress provider finalization automatically as part of fixed-point reconciliation.

Possible provider mechanisms include:

```text
enter merge queue
enable auto-merge
request provider target integration
merge provider submission
other provider-native finalization operation
```

## Important boundary

On `PROVIDER_SUBMISSION`, direct target-ref mutation by the Git ref engine remains forbidden.

Automatic provider merge is **not** the same as direct `git push main`.

The provider is still the governance/enforcement surface and ultimately performs the target mutation.

## Human finalizer

A human wait still exists when governance actually requires one:

```text
required maintainer approval/finalizer missing
→ localized wait
```

But the architecture no longer invents:

```text
all gates green
→ wait for arbitrary human Merge click
```

as a universal state.

---

# 9. One important problem remained at this stage: final target-integration proof

Automatic finalization makes backlog 30.34 more important, not less.

A provider may integrate a submission using:

```text
merge commit
squash
rebase-style merge
merge queue/batch topology
another provider-supported mechanism
```

The final target OID may therefore differ from the submission head.

`ruu` must still define exact proof that the intended logical promotion was realized in the authoritative target.

At the ADR-062/063 stage this was the genuine remaining core question. ADR-065 subsequently closes it by accepting native Git ancestry when preserved, otherwise exact provider `C → R` binding plus independent authoritative Git observation of `R`.

---

# 10. GitHub / PR as backlog: refined conclusion

The original intuition — use GitHub to make deferred agentic-review work durable and reinjectable — is retained.

The adjustment is:

```text
GitHub as backlog: YES
Pull Request as backlog object: NO
GitHub Issue / tracker object: YES
```

A PR represents a concrete current integration proposal with:

- head;
- base;
- diff;
- checks;
- mergeability;
- review/finalization lifecycle.

Keeping it open merely because “this should be fixed later” produces stale candidate semantics.

A deferred finding is a different object.

---

# 11. Finding boundary introduced by ADR-063

Semantic review may produce decisions such as:

```text
FIX_NOW
DEFER
ACCEPT
REJECT
```

These are Development System semantics.

## FIX_NOW

External development continues before the relevant ship-ready/governance intent is established.

## DEFER

The finding may be projected to a tracker item, ideally with:

```text
finding identity
origin review/reviewer/tool
exact candidate/commit/tree provenance
repository/path/symbol
observation
risk/severity
reason deferred
recommended action
acceptance conditions
```

The current ship may continue if all real provider/governance conditions are satisfied.

## ACCEPT / REJECT

No automatic Git/provider blocker exists merely because the finding was recorded.

---

# 12. Deferred backlog work must be revalidated

A later agent should not blindly implement an old ticket.

The correct path is:

```text
backlog finding
→ revalidate against current target/code
→ still applicable?
   ├── yes → ordinary new Work / authoring
   └── no  → close/supersede stale backlog item
```

This logic remains above `ruu`.

---

# 13. Blocking provider review is different from a semantic finding

ADR-053 remains necessary.

If GitHub/provider says the exact current submission is in authoritative blocking:

```text
CHANGES_REQUESTED
```

then the provider route cannot progress.

`ruu` creates/refreshes the durable exact-generation `ReviewCorrectionDemand`.

ADR-063 narrows the interpretation:

```text
blocking provider governance
→ ReviewCorrectionDemand

ordinary comment / suggestion / nonblocking finding
→ no automatic ReviewCorrectionDemand
```

External `DEFER` cannot override a provider state that is still actually blocking. Governance must be legitimately changed/satisfied.

---

# 14. Tests / CI confrontation

The architecture already mostly matched the new view after ADR-057/060.

The audit makes the intended ordering more explicit:

```text
agent edits
→ relevant tests / lint / typecheck / build / semantic review
→ corrections
→ Development System offers work for next Git boundary
→ Ruu materializes checkpoint/commit when mechanically eligible
```

Therefore the commit is not intended as the first quality-discovery point.

Provider CI remains useful as **independent recertification/environmental governance**, for example:

- fresh checkout;
- canonical environment;
- provider-only checks;
- security/dependency policy;
- deployment preview;
- merge-queue candidate checks.

This avoids treating local development tests and provider CI as the same responsibility.

---

# 15. Residual inconsistency found and corrected

The ADR-061 package still contained a few current lifecycle states such as:

```text
DIRECT_AWAITING_DEVELOPMENT_VALIDATION
AWAITING_DEVELOPMENT_VALIDATION
```

These contradicted ADR-060, which had already removed the generic DevelopmentValidationEvidence/Demand protocol.

They were removed in this pass and replaced with transition-local prerequisite language.

This correction is independent of PR semantics but necessary for a coherent final state-space.

---

# 16. Before / after architecture

## Before

```text
PromotionUnit
   ↓
promotion_mode
   ├── DIRECT
   └── PR
        ↓
     PR lifecycle
        ↓
     provider merge
        ↓
      target
```

This makes PR appear to be one of two semantic promotion types.

## After

```text
PromotionUnit
   ↓
exact candidate C
   ↓
RealizePromotion(C, immutable PromotionTarget T)
   ↓
target_realization_route
   ├── DIRECT_TARGET_ADVANCE
   │      ↓
   │   ADR-052 exact-old CAS+FF
   │
   └── PROVIDER_SUBMISSION
          ↓
       Submission / PublicationEpisode
          ↓
       provider projection
       (GitHub PR / GitLab MR / ...)
          ↓
       checks / reviews / queue / governance
          ↓
       provider finalization when current authorization permits
          ↓
       authoritative target observation/proof
```

This is the main architectural correction.

---

# 17. Broader agentic layering after the adjustment

```text
DEVELOPMENT SYSTEM
  Work
  semantic implementation
  tests / review
  Findings
  FIX_NOW / DEFER / ACCEPT / REJECT
  backlog reinjection/revalidation
          │
          ▼
EXTERNAL CONTROL / GOVERNANCE
  topology intent
  PromotionTarget binding
  lifecycle intent
  review-request intent
  semantic settlement intent
          │
          ▼
Ruu
  exact Git observation
  checkpoint / convergence
  exact candidate construction
  policy/capability currentness
  Submission projection when required
  provider progression/finalization
  exact target proof/recovery
          │
          ▼
GIT / REMOTE / PROVIDER
  commits / refs / ancestry
  remote transport
  PR/MR surface when needed
  required checks/reviews/queue
  authoritative target
```

The PR now sits in the provider layer where it naturally belongs.

---

# 18. Changes made in this pass

## New ADRs

- `ADR-062-make-promotion-route-independent-and-provider-submissions-projections.md`
- `ADR-063-keep-findings-and-backlog-outside-ruu.md`

## Main requirements

Updated to:

- replace current `promotion_mode` with `target_realization_route`;
- define `RealizePromotion(C,T)`;
- use provider-neutral Submission terminology;
- make no-provider-projection the default when review/early-publication intent is absent;
- permit automatic machine-authorized provider finalization;
- represent explicit human finalizer only as real governance;
- separate deferred findings/backlog from provider review correction;
- map the broader `Work/Candidate/Evidence/Finding/Authorization/Promotion` model without duplicating ontology;
- remove residual obsolete generic development-validation wait states;
- add current invariants for projection/finalization/findings.

## External Control Plane contract

Updated to:

- generalize PR review intent to ProviderSubmission review intent;
- close 30.36;
- distinguish blocking provider review from semantic/nonblocking findings;
- make semantic finding adjudication/backlog/revalidation explicitly external;
- generalize PublicationEpisode provider surfaces.

## Backlog

- 30.36 closed by ADR-062;
- semantic finding/backlog management explicitly outside core by ADR-063;
- at the ADR-062/063 stage, 30.34 remained open; ADR-065 now closes it.

## Historical ADRs

Current-reading amendments were appended to the PR/promotion/provider ADR chain rather than rewriting history.

---

# 19. State-space audit result

`STATE-SPACE-AUDIT-v31` retains the 14,366 finite regression combinations through ADR-061 and adds:

```text
ADR-062 provider projection/finalization: 72
ADR-063 finding/backlog boundary:         16
```

Total changed/revalidated finite combinations:

```text
14,454
```

It also reruns the five retained concrete Git primitive smokes:

- ADR-048 materialization;
- ADR-050 restack;
- DIRECT_TARGET_ADVANCE;
- repository bootstrap;
- canonical checkpoint.

All pass.

---

# 20. Final assessment

The new agentic Git/GitHub vision does **not** invalidate the current `ruu` architecture. It actually validates much of the separation already achieved in ADR-045..061.

The largest correction is conceptual:

> **A Pull Request is not a kind of promotion. It is a provider projection used when the environment requires one.**

That leads naturally to three additional conclusions:

1. no PR should be created merely because a candidate exists;
2. if every real provider/governance requirement is satisfied, finalization should progress automatically unless an actual human authority is explicitly required;
3. deferred semantic review work belongs in a backlog/tracker object, not in a dormant PR.

After ADR-062/063, the architecture is substantially better aligned with an agent-native development process while retaining full compatibility with human teams and external repositories that still require Pull Requests.

At this point the remaining Git/provider problem was **30.34 exact final target-integration proof**; ADR-065 now closes it with the exact realization model recorded below.

# 21. ADR-064 completion — tests before commit without importing semantic validation

A final confrontation point concerned the preferred agentic order:

```text
edit
→ tests / lint / typecheck / build / semantic review
→ correction fixed point
→ checkpoint / commit
```

The architecture must preserve the property that the state semantically accepted by the Development System is the state actually committed, while ADR-060 forbids reintroducing a generic validation-certificate protocol into `ruu`.

ADR-064 closes that boundary by using the existing mutation-authority protocol as a **frozen handoff**:

```text
Development System validates/decides on surface S
→ durable transferability
→ no external writer may mutate S
→ Ruu exclusive claim
→ ADR-059 exact candidate (P,T)
→ same-claim revalidation
→ commit exactly (P,T)
```

If semantic authoring resumes before the claim, transferability must be revoked first and the earlier readiness decision becomes stale. If `ruu` already owns the claim, external authoring waits for safe release/recovery. Provider CI remains a separate downstream recertification/governance layer.

This preserves all three architectural goals simultaneously:

1. semantic feedback can happen before commit;
2. `ruu` remains ignorant of test/review semantics;
3. the commit cannot legitimately drift from the offered state during the boundary crossing.

The v32 state-space audit adds 16 explicit frozen-handoff combinations on top of the 14,454 v31 regression combinations, for 14,470 changed/revalidated finite combinations.

# 22. ADR-065 completion — exact Candidate → authoritative target realization

The final unresolved issue was what counts as proof after provider finalization when the provider rewrites Git history.

The accepted boundary is deliberately simple:

```text
if candidate C is still visible in authoritative target history
→ Git proves realization directly

else
→ provider must bind exact submitted C to exact final result R
→ Ruu independently observes R in authoritative target history
→ realization proven
```

This means GitHub/GitLab is trusted for the transformation it was explicitly delegated to perform (for example squash/rebase/merge-queue rewriting), but not for the final target fact itself. `ruu` still fetches/observes the authoritative target and requires `R == O` or `R ancestor-of O`.

The architecture explicitly rejects a universal independent diff-equivalence requirement. Correct provider integration after target movement may legitimately produce a different textual patch, and deciding semantic equivalence would pull development semantics back into `ruu`. Tree/patch comparisons remain optional auxiliary diagnostics only.

The resulting terminal chain is:

```text
Candidate C
→ provider/direct finalization
→ exact realization result R
→ fresh authoritative target observation O
→ PromotionRealizationProof(C,R,O)
→ durable Adoption
→ PromotionUnit PROMOTED
```

`PR merged` / `PROVIDER_FINALIZED` therefore remains an intermediate provider fact, not the fundamental terminal condition. Backlog 30.34 is closed.
