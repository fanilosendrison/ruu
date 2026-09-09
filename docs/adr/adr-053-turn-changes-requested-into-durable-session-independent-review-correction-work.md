# ADR-053 — Turn `CHANGES_REQUESTED` into durable session-independent review-correction work

- **Status:** Accepted
- **Date:** 2026-09-06
- **Closes:** backlog 30.23
- **Amends:** ADR-021, ADR-039, ADR-046, ADR-049 and the External Control Plane contract

## Context

A provider review may request semantic changes long after the coding session that produced the reviewed PR has ended. Keeping that original runtime/session open until review completes is neither required nor realistic. A later provider hook may discover the review immediately, or an unrelated future `ruu` invocation may discover the same `CHANGES_REQUESTED` state during its global sweep.

The prior model correctly said that `ruu` must not interpret review prose to decide source-code changes, but backlog 30.23 still framed the open question as an up-front mapping from review feedback to affected ConvergenceUnits. That framing is too narrow. The Development System can start a correction continuation from the exact reviewed submission context and let the new coding session discover which existing convergence scopes need writes, just as an initial implementation discovers its required repositories/scopes while working.

The architecture must therefore answer four questions:

1. how one exact `CHANGES_REQUESTED` generation becomes durable development work even when the originating session is gone;
2. how webhook discovery and global-sweep discovery avoid creating duplicate correction sessions;
3. how a new/resumed correction session obtains safe write topology without reopening terminal ContributionUnits or directly editing the provider submission branch;
4. how ordinary corrections preserve logical submission continuity without mutating immutable PromotionGroups/PromotionUnits, revising the same PR while its PublicationEpisode is open and using ADR-055 continuation episodes after a terminal PR.

## Decision

Backlog item **30.23 is closed**.

### 1. `CHANGES_REQUESTED` creates/refreshes a durable exact-state-bound review-correction demand

A current authoritative provider observation requiring semantic authoring is normalized into a durable external development demand, conceptually:

```text
ReviewCorrectionDemand {
  review_correction_id
  submission_id
  submission_revision
  reviewed_head_oid
  promotion_group_id
  reviewed_promotion_unit_id
  source_repository_id
  provider_submission_identity
  provider_review_generation_or_fingerprint
  exact_feedback_payload/provenance
}
```

The exact storage/API shape is an External Control Plane concern, but identity MUST be stable/idempotent for the same exact reviewed submission revision + authoritative review generation/fingerprint. Re-observing the same `CHANGES_REQUESTED` fact MUST NOT mint independent semantic work items.

The feedback payload is carried as factual input. `ruu` MUST NOT interpret its meaning, infer files/scopes from prose, or author code.

### 2. Provider hooks and `ruu` sweeps are coequal discovery paths for the same demand

Nominal low-latency path:

```text
provider review/webhook
→ EnsureReviewCorrectionDemand(exact review observation)
→ External Control Plane dispatch
```

Reconciliation/backstop path:

```text
any later Ruu invocation
→ global sweep observes the same current CHANGES_REQUESTED generation
→ EnsureReviewCorrectionDemand(exact review observation)
→ External Control Plane dispatch
```

The caller/session that happened to trigger the sweep does not acquire the correction work. It continues its own work; correction dispatch is a separate External Control Plane responsibility.

Webhook/event delivery is therefore an accelerator, not the sole truth source. The global reconciler can recover missed events, and durable idempotent demand identity prevents duplicate semantic obligations when both paths fire.

### 3. The original coding session need not remain alive or be literally reopened

The External Control Plane MAY:

```text
restore/resume the prior development session/runtime
```

or:

```text
start a new continuation session
```

Both are equivalent to `ruu`. Session/process/model/context-window identity is provenance/runtime state, not Git/convergence/publication identity.

A correction session is launched with the exact review-correction demand as development input, including the review feedback and exact reviewed submission/group context. It may additionally receive prior session history/artifacts when the Development System can restore them, but such restoration is not a correctness requirement.

The External Control Plane MUST fence/claim dispatch so one durable correction demand does not cause multiple concurrent authoritative correction continuations merely because it was rediscovered or redelivered. Crash/retry/replacement policy for the semantic session remains external, but it must preserve the one logical demand identity.

### 4. Up-front semantic ConvergenceUnit routing is not required

The correction session may begin bound to the reviewed submission/PromotionGroup/PromotionUnit context without first selecting one exact affected ConvergenceUnit.

As the coding agent analyzes the feedback and codebase, the External Control Plane may explicitly reactivate whichever **existing** ConvergenceUnit scope(s) of the logical ship require new writes:

```text
existing ConvergenceUnit
PROMOTION_BOUND / READY state
→ ACTIVE
→ contribution membership OPEN
```

For every new authoring surface, the External Control Plane provisions a **new ContributionUnit** and its isolated writer branch/worktree. A `CLOSED` ContributionUnit never returns to `OPEN`, and the correction agent never gains authoring authority by directly editing the provider submission ref/PR branch.

Thus semantic scope discovery can occur during the correction session rather than in a separate pre-dispatch “review router”. `ruu` still never infers the semantic mapping.

### 5. Ordinary correction of existing group members preserves the PromotionGroup and persistent PR

If correction work only changes existing ConvergenceUnit members of immutable PromotionGroup `G`, `G` itself is unchanged. Example:

```text
G = {X, Y}
reviewed exact projection P1 = {X@X1, Y@Y1}

correction session reactivates X
new ContributionUnit contributes to X
X converges to X2

same G = {X, Y}
new exact projection P2 = {X@X2, Y@Y1}
```

`P1` and `P2` are distinct immutable PromotionUnits. Because ADR-049 stable submission identity is keyed by the same `promotion_group_id`, source repository, and publication destination, the new verified candidate remains the **same logical submission**. While the current PublicationEpisode is open it becomes a revision of the same provider PR:

```text
same submission_id
same provider PR identity
revision r   -> P1 -> H1
revision r+1 -> P2 -> H2
```

The correction coding session does not work on the submission branch. `ruu` alone revises the provider-facing submission ref under ADR-049 exact expected-old guards after reconvergence/verification.

### 6. A genuinely new ConvergenceUnit is scope expansion, not mutation of the old ship

PromotionGroup membership is closed and immutable under ADR-046. Therefore a newly created ConvergenceUnit `Z` cannot be appended retroactively to existing group `G` merely to preserve a PR identity.

```text
G = {X, Y}
new semantic scope Z required

FORBIDDEN: mutate G -> {X, Y, Z}
```

If the correction discovers genuinely new logical convergence scope outside the existing group, the External Control Plane must declare a different PromotionGroup/superseding ship according to its higher-level publication workflow. Whether that results in a separate/superseding provider submission is then determined by the normal immutable group + ADR-049 logical submission rules; `ruu` does not silently graft the new scope into the old PR.

### 7. Review-correction demands are exact-generation-bound and may become stale/superseded

Before initial dispatch or redispatch, mutable provider/submission facts are re-observed sufficiently to establish that the exact reviewed revision/generation still represents an outstanding semantic correction need.

For example:

```text
reviewed revision/head changed
review was dismissed/superseded
submission closed/merged
newer correction revision already replaced the reviewed generation
```

may make the old demand stale/superseded. The External Control Plane owns cancellation/replacement of semantic sessions; `ruu` only reports/refreshes exact provider facts and never invents semantic continuation from stale review state.

### 8. Correction completion re-enters the ordinary convergence loop

Once the correction session has produced/closed its new ContributionUnits and the affected ConvergenceUnits are sealed as appropriate, no special “review correction merge” path exists:

```text
new/resumed correction session
→ new ContributionUnit writer work
→ normal checkpoint/integration/convergence
→ READY_INTERNAL exact states
→ same PromotionGroup resolves to new exact PromotionUnit(s)
→ ADR-048 exact candidate materialization + verification
→ preserve ADR-049 logical submission identity; revise same open episode/PR or use ADR-055 new episode after a terminal PR
→ provider review lifecycle continues
```

A later `CHANGES_REQUESTED` generation repeats the same durable idempotent cycle.

## Consequences

- Coding sessions can end immediately after publication; review latency does not pin agent/runtime resources.
- Missed provider hooks are recovered by ordinary global reconciliation.
- An unrelated session can trigger discovery without inheriting unrelated review work.
- Session restoration is an optimization/context feature rather than a correctness dependency.
- Review feedback remains semantic input to the Development System, never a Git-derived scope inference in `ruu`.
- Ordinary corrections reuse existing logical ConvergenceUnits but always use new ContributionUnits/writer branches for new authoring.
- ADR-046 immutable PromotionGroups and ADR-049 persistent submission identity fit naturally: exact source state changes, logical ship/submission identity need not.
- Real scope expansion remains explicit and cannot be hidden inside a supposedly unchanged ship.

## Rejected alternatives

### Keep the original coding session open until provider review completes

Rejected. Provider review may take hours/days and runtime/session liveness is not a `ruu` correctness primitive.

### Make the session that happens to invoke the discovering sweep perform the correction

Rejected. Global sweep discovery is trigger-independent; unrelated caller identity conveys no semantic work ownership.

### Require `ruu` to parse review prose/blame and choose affected ConvergenceUnits

Rejected. File/line/provenance attribution is not semantic authoring authority and cannot reliably infer cross-cutting review intent.

### Reopen the old terminal ContributionUnit or edit the PR branch directly

Rejected. `CLOSED` ContributionUnits are terminal, and provider submission refs are publication surfaces rather than authoring workspaces.

### Add newly discovered ConvergenceUnits to the old PromotionGroup

Rejected. PromotionGroup membership is closed/content-addressed/immutable; new logical scope requires a different group.

## Relationship to prior ADRs

Builds on ADR-021 semantic reopen behavior, ADR-035 terminal ContributionUnit lifecycle, ADR-036 global sweep semantics, ADR-039 External Control Plane authority, ADR-041/042 durable reconciler/claim/recovery discipline, ADR-046 immutable PromotionGroups, ADR-047 repository-local projection, ADR-049 stable submission identity/revision, and ADR-051 provider observation normalization.

Closes backlog **30.23**. ADR-054 subsequently closes 30.24, ADR-055 closes 30.25, ADR-056 closes 30.26, ADR-057 reclassifies development-validation execution, and ADR-058/ADR-059 close 30.27; the remaining genuine open core items are 30.28, 30.34, and 30.36; 30.39 is already closed by ADR-048.

## ADR-054 amendment — review correction remains available until ship settlement

ADR-053 semantic continuation remains valid for existing PromotionGroup-member ConvergenceUnits while the relevant logical ship is nonterminal, even when one repository-local PromotionUnit has already promoted. ADR-054 defines ConvergenceUnit `PROMOTED` as the no-more-authoring boundary; after that boundary, later semantic work uses a new ConvergenceUnit/new ship lineage rather than reopening the historical one.

## Amendment by ADR-055

A ReviewCorrectionDemand that requires semantic work in a repository whose prior group projection/provider PR is already promoted/terminal may also induce an ADR-055 `CrossRepositorySettlementDemand`. The same continuation session may satisfy both obligations; the system MUST NOT duplicate authoring merely because both durable demand types exist. After reconvergence, an open provider PublicationEpisode is revised normally, while a terminal prior PR requires a new PublicationEpisode under the same logical submission identity.

## Amendment — ADR-062 / ADR-063 (2026-09-07)

Current reading uses generic provider-submission terminology rather than assuming a PR surface. More importantly, `CHANGES_REQUESTED` here means an authoritative **blocking provider-governance state** for the exact submission revision. Ordinary nonblocking comments, suggestions, or semantic review findings do not automatically create `ReviewCorrectionDemand`. Deferred semantic findings belong to the external backlog and may coexist with successful current promotion once actual provider governance is satisfied.

## Amendment by ADR-069

A review-correction continuation invokes `ruu` as `REVISE_EXISTING_GROUP(G, authority_ref)`. Correction authoring starts from the exact reviewed/group-local state for `G`, not blindly from the current live ConvergenceUnit tip, so later independent work is not absorbed. Untouched members retain their prior exact group binding. The correction effect is separately reconciled forward into the live ConvergenceUnit lineage.

