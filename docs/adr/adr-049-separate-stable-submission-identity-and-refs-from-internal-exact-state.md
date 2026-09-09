# ADR-049 — Separate stable submission identity and refs from internal exact state

**Status:** Accepted  
**Closes:** backlog 30.19  
**Amends:** ADR-021, ADR-028, ADR-045, ADR-047, ADR-048  

## Context

ADR-045 makes PromotionUnits immutable exact-state sets. ADR-047 gives every logical PromotionGroup exactly one repository-local projection per represented source repository, and ADR-048 materializes each exact PromotionUnit into one exact candidate/head.

PR publication nevertheless needs a provider-facing branch/ref whose lifecycle differs from internal exact-state refs. A submission may receive a new exact candidate because semantic development changed the PromotionUnit, because a dependent submission was restacked, or because a provider-authorized update produced a new exact revision. Internal ConvergenceUnit refs/OIDs are evidence-bearing exact-state sources and must never gain this rewrite authority.

The architecture already had stable `submission_id`, monotonic `submission_revision`, and rewriteable submission semantics, but backlog 30.19 still left open when a submission ref is created, whether it may alias an internal ref, its stable identity/naming, update guards, and cleanup.

## Decision

Backlog item **30.19 is closed**.

### 1. Internal refs and submission refs are always distinct refs

For PR publication, `ruu` MUST create/use a provider-facing submission ref distinct from every ContributionUnit/ConvergenceUnit/internal candidate ref.

```text
internal ref      -> exact candidate C
submission ref    -> exact candidate C
```

The two refs MAY initially point to the same OID, but they MUST NOT be the same ref name/authority object.

This supersedes the earlier ADR-028 allowance that an immutable one-to-one submission could safely alias an internal convergence ref.

Reason:

```text
internal ref
→ preserves exact managed source/history
→ no submission rewrite authority

submission ref
→ provider-facing mutable representation
→ may advance/revise/restack only under submission rules
```

No force/rewrite authority attached to a submission ref propagates to internal refs.

### 2. Stable submission identity is logical, not exact-PromotionUnit identity

A submission represents one stable repository-local PromotionGroup projection toward one canonical publication destination.

Define a logical submission key conceptually as:

```text
SubmissionLogicalKey {
  promotion_group_id
  source_repository_id
  publication_destination
}
```

where `publication_destination` canonically identifies the policy-selected provider/target repository + target ref and, for cross-repository publication, the configured source-publication repository relation required to identify the logical publication lineage. ADR-055 later scopes concrete provider PR/ref identity to PublicationEpisodes within that lineage.

`submission_id` is a stable opaque/content-derived identity for that logical key.

Therefore a new exact PromotionUnit/candidate revision for the same logical projection/destination does not create a new submission identity:

```text
same submission_id
revision r   -> PromotionUnit P1 -> head H1
revision r+1 -> PromotionUnit P2 -> head H2
```

A materially different publication destination/relation is not silently treated as the same provider submission merely because the PromotionGroup is the same.

### 3. Submission revision is the exact provider-facing generation

Each bound revision records at least:

```text
submission_id
submission_revision
promotion_unit_id
current_submission_head
submission_ref
publication_episode_id
provider_pr_identity (when created; scoped to that publication episode)
publication destination/relation identity
```

`submission_revision` increases only through an authorized revision transition. Exact head movement without such a transition is drift.

### 4. Submission ref is created only for a current verified PR candidate

The ref is not predeclared merely because a PromotionGroup/PromotionUnit exists.

Nominal first-publication prerequisites include:

```text
current effective policy = PR
exact repository-local PromotionUnit eligible
exact ADR-048 candidate C current
valid exact development-validation evidence bound to C when required by current policy
current publication destination/relation known
submission operation claim held
```

Then:

```text
create/bind logical submission identity
create/bind current PublicationEpisode
create distinct episode submission ref -> C
publish with expected remote = ABSENT
observe remote ref == C
create/adopt provider PR identity for that episode
bind first logical submission revision of the episode @ C
```

A pre-existing unexpected remote ref at the intended name is not overwritten; the operation fails closed/reconciles naming/identity state.

### 5. Submission-ref naming is descriptive, collision-safe, and non-authoritative

Correctness depends on `submission_id` plus stored exact ref/repository/provider identity, never parsing a branch name.

For newly created publication episodes, the preferred v1 namespace is:

```text
refs/heads/Ruu/submissions/<submission_id>/episodes/<publication_episode_id>
```

A previously durably bound first-episode ref using the historical `refs/heads/Ruu/submissions/<submission_id>` namespace remains valid; naming is presentation, not identity.

A repository-approved alternative naming template MAY be used when required by provider/repository constraints, provided the exact chosen ref is durably bound to `submission_id`, is collision-safe, and is never parsed to infer promotion semantics.

### 6. Revision publication uses exact expected-old protection

For an authorized submission revision:

```text
current bound revision = r @ H
new verified exact head = H2
```

`ruu` MUST revalidate the current local/remote/provider head as `H` immediately before mutation, hold the submission claim, then update the submission ref with expected-old/force-with-lease-equivalent protection.

After mutation:

```text
local ref == H2
remote ref == H2
provider PR head == H2
→ submission_revision := r+1
```

Unexpected movement enters `DRIFTED/UNKNOWN_INCONSISTENT`; global blind force is forbidden.

### 7. Provider submission identity persists across exact revisions within one publication episode

Ordinary semantic corrections and authorized restacks update the same persistent PR/submission **while the current PublicationEpisode remains nonterminal**.

```text
submission_id stable
publication_episode_id stable
provider PR identity stable within episode
promotion_unit_id/head may change
submission_revision increases monotonically across the logical submission
```

ADR-055 adds the post-terminal continuation rule: if the current provider episode is terminal/consumed while the same logical submission still has a later current exact promotion obligation and the PromotionGroup remains nonterminal, the terminal episode is never reopened. A new PublicationEpisode with a distinct submission ref/provider PR is created under first-publication safety rules while preserving the same logical `submission_id`.

### 8. Ref retention and audit retention are separate

Durable audit/recovery metadata keeps the submission identity, provider PR identity, revision history, exact heads, exact publication destination, target result, operation/attempt/observation/adoption records, and relevant evidence references according to retention policy.

The physical submission branch/ref MAY become cleanup-eligible only after all of the following are true:

```text
this publication episode is terminal
that episode's target outcome has been exactly observed/adopted
no active revision/restack/merge-queue/recovery operation requires the episode ref
no recovery reachability requirement still depends on it
```

ADR-054 subsequently closes backlog 30.24 for ConvergenceUnit historical internal-ref lifecycle: retirement and GC eligibility are distinct from deletion, built-in v1 historical internal-ref retention is `KEEP`, and durable logical/audit history is separate. Verification-evidence persistence/retention remains governed by backlog 30.28. This ADR still fixes that the provider submission branch itself is not the durable identity/evidence record.

## Consequences

- Internal exact-state refs can never be accidentally rewritten by PR/restack machinery.
- One provider PR may survive multiple exact PromotionUnit/candidate revisions within one PublicationEpisode.
- One stable logical submission may have multiple sequential provider PublicationEpisodes when an earlier PR is terminal while the same nonterminal ship later requires another repository-local publication.
- Submission identity is stable before any particular candidate OID but is still bound to a concrete publication destination.
- Recovery can compare logical identity + revision + expected exact head rather than guessing from branch names.
- Branch cleanup no longer destroys the durable submission audit trail.

## Rejected alternatives

### Alias immutable submission refs to internal convergence refs

Rejected. It creates an authority coupling that becomes unsafe as soon as the same logical submission later becomes rewriteable/restackable or policy/provider behavior changes.

### Bind `submission_id` to `promotion_unit_id`

Rejected. PromotionUnit identity changes whenever its exact member state changes, which would force unnecessary new PR identities for ordinary revisions.

### Use branch name as submission identity

Rejected. Naming is provider/repository presentation and may change; correctness requires stable logical identity plus exact stored ref facts.

## ADR-053 amendment — review-correction continuation across sessions

ADR-053 makes explicit that the coding/runtime session which originally produced a submission may be gone when `CHANGES_REQUESTED` arrives. A restored or new correction continuation session may reactivate existing ConvergenceUnit members and produce new ContributionUnits; when the same PromotionGroup projection/publication destination later resolves to a new exact PromotionUnit/candidate, this section's stable logical key intentionally preserves the same `submission_id` while `submission_revision` advances. Provider PR identity is preserved only within the current nonterminal PublicationEpisode under ADR-055. Session identity is not part of the logical submission key.

## ADR-055 amendment — terminal PR continuation uses publication episodes

ADR-055 refines the earlier phrase “provider PR identity stable” to mean stable **within one PublicationEpisode**. Stable `submission_id` still identifies the repository-local PromotionGroup projection + canonical publication destination across the life of the logical ship, and `submission_revision` remains monotonic. A terminal/consumed provider PR is immutable historical state; if the same nonterminal logical submission later has a new exact repository-local promotion obligation, `ruu` creates a distinct new PublicationEpisode/submission ref/provider PR rather than mutating the terminal episode or minting a new logical submission identity. Episode creation uses ordinary first-publication verification/policy/capability/expected-absent guards.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-061

The canonical publication destination in stable submission identity is the immutable PromotionTarget inherited from the source ConvergenceUnit(s), not a late policy-selected target. Submission revisions may change exact heads/provider episodes but never retarget the logical submission lineage.

## Amendment — ADR-062 (2026-09-07)

This ADR becomes the canonical core abstraction for provider projection. `Submission` / `PublicationEpisode` is provider-neutral; historical `provider_pr_identity` should be read as `provider_submission_identity`. GitHub PR or GitLab MR identity is adapter-specific surface identity for one episode. The submission is not the semantic promotion and is not a backlog object.

