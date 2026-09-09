# ADR-055 — Settle partial cross-repository ships with forward actions and publication episodes

**Status:** Accepted  
**Closes:** backlog 30.25  
**Amends:** ADR-014, ADR-022, ADR-024, ADR-026, ADR-032, ADR-036, ADR-039, ADR-042, ADR-049, ADR-053, ADR-054  

## Context

ADR-014 deliberately rejects an atomic transaction spanning repositories. ADR-047 therefore projects one cross-repository PromotionGroup into independent repository-local PromotionUnits that may complete at different times. ADR-054 further prevents one locally promoted snapshot from prematurely closing its ConvergenceUnit while the logical ship remains nonterminal.

This makes the following state normal:

```text
PromotionGroup G = {XA, XB}

Repo A / PA1 -> PROMOTED
Repo B / PB1 -> REVIEWING

G -> PARTIALLY_PROMOTED
```

`PARTIALLY_PROMOTED` alone is not an incident. Repo B may simply complete later.

The architectural problem begins when the already-visible partial ship cannot finish merely by continuing the original repository-local paths, for example:

```text
Repo A PR-A -> MERGED
Repo B PR-B -> CHANGES_REQUESTED
review correction requires changing Repo A again
```

or when an unpromoted repository-local track becomes terminally unavailable/withdrawn and the external system must decide how to leave the overall product state coherent.

Git cannot atomically roll back the world. A published commit may already have consumers, deployments, generated artifacts, migrations, or later commits. `ruu` can observe exact Git/provider facts but cannot decide whether a semantic revert, forward fix, compatibility layer, data migration, or abandonment of the intended ship is correct.

A second problem follows from ADR-049. Ordinary correction while a PR is still open can revise the same provider PR. Once that PR is terminal/merged, the same provider surface cannot be revised even though the same logical PromotionGroup/repository projection may still need another publication before the group is terminally settled.

## Decision

Backlog item **30.25 is closed**.

### 1. `PARTIALLY_PROMOTED` is nonterminal progress, not automatically a settlement incident

Cross-repository group progress remains mechanically observable as:

```text
NONE_PROMOTED
PARTIALLY_PROMOTED
ALL_PROMOTED
UNKNOWN_INCONSISTENT
```

`PARTIALLY_PROMOTED` does not itself authorize compensation, rollback, new authoring, or a new provider PR.

If every remaining current repository-local promotion obligation can continue through its ordinary nominal path, `ruu` simply continues those obligations.

```text
PARTIALLY_PROMOTED
+ nominal remaining paths still sufficient
-> continue ordinary convergence/promotion
```

### 2. Non-nominal partial progress creates one durable exact-generation settlement demand

When a partial ship requires semantic cross-repository disposition rather than only ordinary remaining-provider progress, the system records one durable idempotent:

```text
CrossRepositorySettlementDemand {
  promotion_group_id
  exact_settlement_generation
  current repository -> PromotionUnit/outcome mapping
  authoritative target/provider observations
  causative review/failure/closure provenance when present
}
```

The exact settlement generation fingerprints the current relevant logical/exact projection and authoritative promotion outcomes. Rediscovery of the same generation through provider hooks, control-plane events, or any later `ruu` global sweep resolves to the same demand rather than spawning duplicate semantic work.

Typical demand conditions include:

```text
- correction of an uncompleted track requires new semantic work in a repository
  whose prior group projection has already been promoted/consumed;
- an unpromoted track reaches a terminal external disposition that prevents the
  intended nominal completion;
- the External Control Plane explicitly declares that nominal completion is no
  longer the intended settlement path for this exact partial generation.
```

Temporary waits, ordinary review latency, pending external development-validation obligations, or merely being `PARTIALLY_PROMOTED` do not by themselves select a settlement action.

A ReviewCorrectionDemand may be the cause of a settlement demand. If the same continuation session already performs the required cross-repository semantic authoring, the settlement demand may reference that work; it MUST NOT create a duplicate coding session merely because two durable obligations describe different aspects of the same current problem.

### 3. Settlement semantics belong to the External Control Plane / Development System

`ruu` supplies exact facts and keeps the settlement demand current. It MUST NOT decide:

```text
ROLL_FORWARD
vs
COMPENSATE
```

The External Control Plane/Development System interprets product/code/runtime semantics and chooses the required semantic path.

The nominal architecture is forward completion: if no explicit compensation intent exists and ordinary completion remains possible, the existing ship continues toward `ALL_PROMOTED`.

Compensation requires explicit external semantic intent. `ruu` never invents a revert merely because one repository was promoted before another.

### 4. All settlement Git effects are forward-only

Both roll-forward and compensation are implemented as ordinary new development state followed by ordinary `ruu` progression.

```text
published A1
-> later forward fix A2

or

published A1
-> later semantic compensation A2_comp
```

Target refs retain their existing descendant-only/FF/CAS rules. Compensation MUST NOT mean moving an authoritative target ref backward or force-resetting it to a historical OID.

A `git revert` may be authored by the Development System when semantically appropriate, but to `ruu` it is simply new forward Git state requiring the same verification, convergence, promotion, policy, provider, and recovery checks as any other change.

### 5. Existing ConvergenceUnits remain the same ship only while ADR-054 permits semantic continuation

While the PromotionGroup remains nonterminal, the External Control Plane may reactivate existing member ConvergenceUnits and create new ContributionUnits under ADR-053/054.

```text
G = {XA, XB}
PA1 already promoted
correction requires A + B

XA -> ACTIVE/OPEN -> XA2
XB -> ACTIVE/OPEN -> XB2

G remains immutable {XA, XB}
```

A genuinely new ConvergenceUnit remains scope expansion and requires a different/superseding PromotionGroup under ADR-046/053. Settlement never mutates historical PromotionGroup membership.

### 6. Stable logical submission identity may contain multiple publication episodes

ADR-049 `submission_id` remains the stable logical identity for:

```text
(promotion_group_id, source_repository_id, publication_destination)
```

but provider PR identity and provider-facing submission ref are now scoped to a **PublicationEpisode**.

Conceptually:

```text
logical submission SA

PublicationEpisode 1
  submission_ref E1
  provider PR #10
  revisions r1..rN
  -> terminal MERGED/CLOSED

same logical submission SA still needs a later exact repo state

PublicationEpisode 2
  distinct submission_ref E2
  provider PR #27
  later revisions
```

Rules:

```text
open current episode
+ new authorized exact candidate
-> revise same episode / same provider PR

terminal current episode
+ same logical submission still has a new current promotion obligation
+ PromotionGroup itself remains nonterminal
-> create a new publication episode / distinct provider PR surface
```

A terminal provider episode is never reopened or mutated.

Each episode has at least:

```text
submission_id
publication_episode_id / monotonic episode generation
distinct submission_ref
provider_pr_identity
first/last logical submission revision range
exact publication destination/relation
terminal provider/target outcome when known
```

`submission_revision` remains monotonic for the logical submission; every revision is bound to exactly one publication episode. Provider PR identity is stable across revisions **within an episode**, not necessarily across the entire lifetime of the logical submission.

The reference namespace is descriptive/non-authoritative. The preferred v1 shape for newly created episode refs is:

```text
refs/heads/Ruu/submissions/<submission_id>/episodes/<publication_episode_id>
```

A previously durably bound ADR-049 episode-1 ref using the historical single-ref namespace remains valid; migration/naming presentation never changes logical identity.

### 7. Episode creation uses ordinary publication safety, not continuation privilege

A new episode is not allowed merely because an older PR existed.

It requires the same current prerequisites as first PR publication for its exact candidate, including:

```text
current PR-mode EffectivePromotionPolicy
current exact PromotionUnit/candidate
valid exact development-validation evidence
current destination/relation
current provider capability/policy authorization
submission/publication claim
expected new remote ref = ABSENT
```

The provider PR is created/adopted only after exact ref publication/observation. Later revisions of that episode use ADR-049 exact expected-old guards.

### 8. Roll-forward terminal settlement is `ALL_PROMOTED` over the current exact group resolution

If settlement authoring produces new exact group-member states, the immutable PromotionGroup may resolve to new repository-local PromotionUnits.

Normal successful terminal settlement is reached only when every **current exact repository projection** required by the group has its current promotion outcome realized/adopted:

```text
current exact mapping all promoted
-> PromotionGroup settlement = ALL_PROMOTED
```

Historical earlier promoted snapshots/episodes remain audit history but do not substitute for an unfulfilled newer current exact projection.

### 9. Compensation is an explicit terminal semantic settlement, not an inferred rollback

The External Control Plane may choose a compensation plan for an exact settlement demand. The plan identifies the logical partial ship and the semantic forward work/dispositions required to neutralize or safely close it.

`ruu` may adopt:

```text
PromotionGroup settlement = COMPENSATED
```

only when all of the following hold:

```text
explicit current compensation intent/plan from the External Control Plane
all exact Git/provider effects that the plan declares required have been
  observed/adopted through ordinary Ruu mechanics
no remaining correctness-critical settlement/recovery operation is pending
External Control Plane declares the semantic compensation obligation complete
for that exact settlement generation
```

The external declaration supplies semantic meaning; it does not manufacture Git/provider facts. `ruu` still observes every claimed forward effect independently.

`COMPENSATED` means the original ship was not delivered as an `ALL_PROMOTED` success, but the explicitly required forward compensating disposition has been completed and the partial state is terminally settled.

### 10. Partial promotion is never silently abandoned

For a PromotionGroup with already-promoted repository effects, there is no built-in transition:

```text
PARTIALLY_PROMOTED -> ABANDONED -> done
```

merely because remaining progress is inconvenient or blocked.

The group remains nonterminal until it reaches `ALL_PROMOTED`, `COMPENSATED`, or another future terminal settlement form introduced by an explicit ADR with equivalent semantic-authority and exact-effect guards.

This ADR does not define a general pre-promotion cancellation model for a ship with no externally realized effects.

### 11. Settlement demands are global nonterminal managed obligations

An active `CrossRepositorySettlementDemand` remains in the ADR-036 global managed-obligation universe. It may be discovered/refreshed by a later invocation from an unrelated session; that caller does not inherit the semantic work.

The External Control Plane may restore/start a settlement continuation session, exactly as ADR-053 permits for review correction. Work uses newly provisioned ContributionUnits/writer surfaces and re-enters normal convergence.

### 12. ADR-039 contract is retroactively consolidated for accepted pre-039 boundaries

The audit performed while closing 30.25 found several accepted pre-ADR-039 external-boundary decisions that were only implicit or scattered in the companion contract. This ADR amends `EXTERNAL-CONTROL-PLANE-CONTRACT.md` to make them explicit without changing their semantics:

- ADR-022: repository admission/reactivation must create durable managed coordination/obligation state before managed writes; `ACTIVE_CONVERGENCE_SET` is derived acceleration only;
- ADR-024 and ADR-036: invocation/trigger identity is only convergence demand, never mutation authority, work ownership, or sweep scope;
- ADR-026 as later constrained by ADR-043/044: runtime/user/orchestrator requests cannot manufacture promotion authorization or bypass authoritative repository/provider governance;
- ADR-032: `REVIEW_REQUESTED` is exact-revision publication/governance intent and is not inferred from internal readiness; any non-Git PR-author/governance evidence required by the configured gate must enter through an explicit exact-bound external/policy contract.

The still-open exact composition of the PR-author/ship-ready gate (30.32) and exceptional `REVIEW_NOT_REQUESTED` eligibility (30.36) remain open. This consolidation does not decide them.

## Consequences

- Cross-repository promotion remains non-atomic and forward-only.
- A partially promoted group may remain healthy/nonterminal for ordinary review latency.
- Semantic settlement work is durable, idempotent, session-independent, and external-authority owned.
- `ruu` never chooses compensation or automatically reverts code.
- The same logical submission can survive a terminal PR by opening a later provider publication episode when the same nonterminal ship needs another repository-local publication.
- Ordinary corrections before a provider PR becomes terminal still revise the same episode/PR.
- Provider episode history is preserved independently from logical submission identity and exact PromotionUnit history.
- `ALL_PROMOTED` and `COMPENSATED` are terminal settlements understood by ADR-054's ConvergenceUnit closure guard.
- A partial group cannot disappear merely because one remaining track is hard to complete.
- The External Control Plane companion contract now explicitly consolidates additional pre-ADR-039 responsibilities that had previously remained distributed across older ADRs.

## Rejected alternatives

### Treat `PARTIALLY_PROMOTED` as automatic failure

Rejected. Independent repository-local PR/review latency naturally produces partial progress.

### Automatically revert already-promoted repositories

Rejected. Git ancestry cannot determine whether a revert is semantically safe, and external side effects may be irreversible/non-Git.

### Force-reset a target to simulate rollback

Rejected. It violates descendant-only authoritative target semantics and destroys externally visible history.

### Reopen a merged provider PR

Rejected. A terminal provider publication surface has been consumed. Later publication of the same logical ship requires a new episode while preserving logical submission lineage.

### Create a completely new logical submission for every post-merge correction

Rejected. The logical PromotionGroup/repository/destination identity has not changed; only the provider publication episode has.

### Let a settlement demand silently terminalize the group

Rejected. Semantic intent alone cannot manufacture exact Git/provider effects. Terminal `COMPENSATED` requires both explicit external semantic completion and observed/adopted forward effects required by that plan.

## Related decisions

- ADR-014 — cross-repository promotion is non-atomic partial progress;
- ADR-036 — every invocation sweeps all nonterminal managed obligations;
- ADR-039 — normative External Control Plane boundary;
- ADR-042 — durable reconciler/Operation→Attempt→Observation→Adoption semantics;
- ADR-046/047 — immutable PromotionGroup and repository-local projections;
- ADR-049 — stable logical submission identity and exact revisions;
- ADR-053 — session-independent semantic continuation;
- ADR-054 — PromotionUnit completion vs ConvergenceUnit closure/retirement.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment — ADR-062 / ADR-063 (2026-09-07)

`PublicationEpisode` is provider-neutral; historical “provider PR” means the provider submission surface for that episode. A later episode is created only for a later concrete publication need, not to preserve deferred backlog work. Semantic deferred findings are external tracker objects under ADR-063.

## Amendment — ADR-065 (2026-09-07)

A PublicationEpisode/provider submission may become provider-terminal before the corresponding PromotionUnit is proven promoted. Cross-repository settlement counts a local promotion as completed only after ADR-065 target realization proof is durably adopted; provider terminality alone does not satisfy `ALL_PROMOTED`.

## Amendment by ADR-067 — repository-local supersession does not silently settle a ship

`SUPERSEDED` is a precise repository-local disposition for an obsolete unrealized PromotionUnit after the same PromotionGroup/repository projection has adopted a newer exact PromotionUnit. It does not mutate PromotionGroup membership, does not erase previously promoted effects, and does not create a group-level abandonment path.

A partially promoted group remains governed by this ADR's forward settlement rules. Historical old effects still require exact recovery/settlement accounting even when a newer repository-local PromotionUnit is current.

## Amendment by ADR-068 — CANCELLED is strictly pre-realization and never a partial-promotion escape hatch

ADR-068 adds `PromotionGroup CANCELLED` only for a still-unrealized group with explicit current External Control Plane withdrawal intent and no unresolved committed/uncertain or otherwise still-realizing managed promotion effect. The instant any repository-local group effect is route-conformantly realized, `CANCELLED` is unavailable. A cross-repository `PARTIALLY_PROMOTED` group remains governed by this ADR and must continue toward `ALL_PROMOTED` or explicit `COMPENSATED` settlement. Cancellation cannot erase already-realized history.
