---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Preserve internal convergence OIDs while allowing policy-authorized submission rewrites"
id: "ADR-028"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "7dc95e193ad0128d6796df1943bf2391c9ddbf363f23317c9846ad26de696a1a"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-028: Preserve internal convergence OIDs while allowing policy-authorized submission rewrites

- **Status:** Accepted — amended by ADR-029, ADR-030, ADR-032, ADR-038, ADR-049, and ADR-050
- **Date:** 2026-09-04
- **Decision order:** 028

## Context

ADR-016 prohibited rebase/history rewrite because stable OIDs dramatically simplify concurrent contribution units, exact readiness, CAS, recovery, and shared convergence.

That remains desirable for internal contribution unit and convergence-unit refs.

However, stacked PR workflows may require restacking/rebasing provider-facing branches as lower layers or the target move. A universal no-rebase/no-force-push rule would make those workflows impossible or unnecessarily awkward.

The key distinction is between Git history used as internal working/convergence state and Git history used as a provider-facing submission representation.

## Decision

Ref classes have different rewrite authority.

### Internal refs

```text
CONTRIBUTION_UNIT_REF
CONVERGENCE_UNIT_REF
```

MUST NOT be rebased, amended, backward-reset, or non-fast-forward rewritten by `ruu`.

Internal refs mutated by `ruu` advance only to descendants. ADR-038 removes ContributionUnit branch/ref deletion from `ruu` lifecycle responsibility; any deletion of editing refs is performed by user/agent/External-Control-Plane tooling outside this rule.

### Target refs

A target ref follows repository promotion policy:

```text
PR mode
→ target ref is governance-controlled/read-only to Ruu

DIRECT mode
→ target ref may advance only through the policy-authorized direct-promotion algorithm
→ no history rewrite/force-push of target
```

### Submission refs

```text
SUBMISSION_REF
```

MAY be rewritten/restacked only when all of the following hold:

```text
repository promotion policy permits it
provider/topology requires or permits it
the exact submission ref is classified rewriteable
the rewrite is owned/claimed by the current authoritative executor/operation
expected-old remote/local state is revalidated
underlying convergence-unit source identities/OIDs remain exact and unchanged
the resulting projection is revalidated before further governance actions
```

A rewriteable submission has stable logical identity plus mutable revision:

```text
promotion_unit_id / submission_id = stable
current_submission_head           = exact OID, mutable by authorized revision
submission_revision               = monotonic logical generation
```

Ordinary independent immutable PRs remain exact-head frozen.

For rewriteable/stacked submissions, a provider-authorized restack is an explicit head-revision transition, not unexpected drift. Previous head-bound checks/reviews/readiness are re-read or invalidated according to provider semantics.

Unexpected head movement outside an authorized rewrite transition remains `DRIFTED`/`UNKNOWN_INCONSISTENT`.

Force-push capability, if needed for a rewriteable submission ref, is restricted to that ref and must use exact expected-old/CAS semantics (for example force-with-lease-equivalent protection). It never generalizes to contribution-unit refs, convergence-unit refs, or target refs.

## Rationale

This keeps the high-value safety properties where agents actually work while allowing modern provider-facing stacked workflows.

The stable identity boundary becomes:

```text
internal source state
→ stable exact OIDs

submission projection
→ stable logical identity + exact current revision OID
```

## Consequences

- ADR-016 remains authoritative for internal refs, not for all refs.
- ADR-021 exact-head freeze remains the normal immutable-submission case.
- Stacked/restackable submissions use explicit revision transitions.
- Submission rewrite invalidates stale head-bound evidence and requires exact rebinding.
- Provider-side authorized restack is recoverable/idempotent using logical submission identity plus current head/revision.
- `--force` remains forbidden globally; a force-with-lease-equivalent expected-old update may exist only for a policy-authorized rewriteable submission ref.
- Internal recovery never starts rebase on contribution unit/convergence-unit refs.
- Recovery may resume/inspect a known owned submission rebase/restack operation.

## Alternatives considered

- **Allow rebase everywhere:** rejected because it destroys the internal OID-stability model.
- **Forbid rebase everywhere:** rejected because it blocks legitimate stacked/restacked submission workflows.
- **Let provider rewrite internal convergence-unit refs directly:** rejected because provider-facing representation must not mutate internal source-of-truth refs.
- **Treat any provider head movement as acceptable:** rejected because only explicitly authorized rewrite transitions are safe.

## Related decisions

Narrows ADR-016 and amends ADR-010, ADR-017, ADR-020, and ADR-021.

## Amendment by ADR-029 and ADR-030

An authorized submission restack/rewrite that creates a new exact submission result is a managed state-producing transition. The new revision must have valid development-validation evidence before authoritative publication/governance proceeds.

The previous revision's development-validation evidence is not reused for the new result unless the resulting exact candidate identity is actually unchanged and the ADR-030 policy/context validity conditions hold.

## Amendment by ADR-032

Submission revision identity is independent of review-request intent. A current revision may be published `REVIEW_NOT_REQUESTED` or `REVIEW_REQUESTED` according to policy.

Restacking/revising a review-requested submission rebinds the exact head and may require returning publication intent to `REVIEW_NOT_REQUESTED` until the ship-ready/review-request gate is re-established.

## Amendment by ADR-038

ContributionUnit branch/ref deletion is not a `ruu` convergence transition. The append-only/no-rewrite rule continues to govern ContributionUnit ref advances while such a ref exists and is mutated by `ruu`; artifact deletion lifecycle is external.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-049

ADR-049 strengthens the ref-separation rule: a provider-facing submission ref is **always a distinct ref** from every internal ContributionUnit/ConvergenceUnit ref, even for an immutable one-to-one submission whose ref initially points to the same OID. Stable submission identity persists across exact PromotionUnit/head revisions under one canonical publication destination; only the submission ref carries revision rewrite authority.

## Amendment by ADR-050

ADR-050 replaces generic narrative rebase/restack semantics with exact state reprojection for dependency-driven stacks. A stack is derived from an unsatisfied exact promotion dependency, not requested by the caller. Restack uses the immutable owned `(old_base_oid, owned_candidate_oid)` anchor and transplants that aggregate exact effect onto the new predecessor/base via a versioned full three-way merge semantic; repeated restacks never use a prior restacked provider head as semantic source.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
