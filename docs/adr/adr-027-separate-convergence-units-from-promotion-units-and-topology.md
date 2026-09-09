# ADR-027: Separate convergence units from promotion/submission units and promotion topology

- **Status:** Accepted — amended by ADR-029, ADR-030, ADR-032, ADR-037, ADR-039, ADR-045, ADR-046, ADR-047, ADR-049, and ADR-050
- **Date:** 2026-09-04
- **Decision order:** 027

## Context

A repository-local convergence unit is a technical aggregation root for contribution units. It does not necessarily have the same granularity as what should be directly pushed or submitted for human/upstream review.

This matters especially for external contributions and stacked PRs:
- several internal convergence units may belong in one coherent upstream PR;
- several promotion units may form a dependency stack;
- `ruu` must not invent semantic PR granularity merely because internal units are individually mergeable.

## Decision

Distinguish three concepts:

```text
CONVERGENCE_UNIT
= repository-local technical convergence state for contribution units

PROMOTION_UNIT
= explicitly declared set of exact convergence-unit inputs
  intended to be promoted as one independently governed unit

PROMOTION_TOPOLOGY
= relationship between promotion units as they enter the target
  (for example INDEPENDENT or STACKED)
```

For PR mode, a promotion unit may materialize a distinct:

```text
SUBMISSION_REF
```

which is the provider-facing Git representation of that promotion unit.

PromotionGroup membership/granularity is supplied by the External Control Plane. ADR-050 supersedes the earlier assumption that stack/dependency layout is human/orchestrator publication intent: current promotion dependency topology is derived by `ruu` from exact managed effective-base/predecessor/target facts among already-distinct promotion obligations. `ruu` still does not infer semantic granularity from code, branch names, task names, or commit count.

ADR-046 removes implicit/default mapping from `ruu`. The External Control Plane instead predeclares a closed immutable `PromotionGroup` over canonical ConvergenceUnit refs; a singleton is explicitly `{CX}` and a multi-source ship is `{CX,CY,...}`. ADR-047 amends the materialization boundary: after the whole group has current exact `READY_INTERNAL` states, `ruu` partitions the exact set by authoritative source repository and materializes exactly one ADR-045 PromotionUnit per represented repository.

For a stack:

```text
target
  ↑
promotion-unit A / PR-A
  ↑
promotion-unit B / PR-B
  ↑
promotion-unit C / PR-C
```

the dependency edges are derived managed state under ADR-050 while the predecessor is not yet realized in the authoritative target. `ruu` executes and maintains the Git/provider topology mechanically; no caller chooses `STACKED_PR` as a preference.

## Rationale

The technical frequency of convergence should not dictate the social/review granularity of promotion.

This permits:
- frequent internal convergence;
- tiny direct promotions in solo trunk-based repositories;
- coherent external PRs without micro-PR spam;
- stacked PRs when review latency would otherwise serialize dependent work.

## Consequences

- A convergence unit can be ready internally without a promotion unit yet being declared.
- `ruu` does not ask “is this a complete product feature?”
- In PR mode, promotion readiness is evaluated at the promotion-unit/submission level.
- One promotion unit may reference one or more exact convergence-unit states, but all members are from exactly one authoritative source repository.
- One convergence unit may participate only according to explicit promotion bindings; ambiguous/multiple incompatible bindings fail closed.
- Stack dependencies are exact-state-derived and state-bound; stack shape is a provider representation of an unsatisfied dependency, not caller intent.
- Repository-level group projection is deterministic under ADR-047. Exact Git candidate/head composition for a same-repository PromotionUnit containing multiple convergence units was tracked under 30.39 and is subsequently closed by ADR-048 with deterministic canonical pairwise materialization.

## Alternatives considered

- **One convergence unit always equals one PR:** rejected because upstream contribution granularity can differ from internal convergence granularity.
- **Let `ruu` use an LLM to decide PR grouping:** rejected because semantic packaging belongs above the Git convergence layer.
- **Wait for a complete product feature before any PR:** rejected because it conflicts with trunk-based, small-reviewable-change practice.
- **Require every contribution unit to become a PR:** rejected because contribution-unit refs are technical isolation units.

## Related decisions

Amends ADR-010, ADR-011, ADR-014, ADR-019, ADR-020, and ADR-021.

## Amendment by ADR-029 and ADR-030

Promotion projection/materialization is also a verification boundary when it creates a new exact candidate state.

A multi-source projection, stack projection, or other materialization that creates a new tree/commit must obtain valid development-validation evidence for that exact result before authoritative promotion/submission use.

If the promotion representation is exactly an already-verified state under the same verification policy/context, ADR-030 permits evidence reuse.

## Amendment by ADR-032

Promotion-unit readiness and PR review-request intent remain separate dimensions.

A promotion/submission may be provider-published with `REVIEW_NOT_REQUESTED` only under explicit policy; `REVIEW_REQUESTED` carries the stronger configured ship-ready/PR-author assertion for the exact submission revision.


## Amendment by ADR-037

ContributionUnit checkpoints converge eagerly into their bound ConvergenceUnit and do not wait for promotion-unit semantics. Experimental/alternative isolation is represented by distinct ConvergenceUnits. A ConvergenceUnit becomes eligible for `READY_INTERNAL` only after externally authoritative contribution membership is `SEALED` and the exact internal mechanical fixed-point conditions hold; promotion grouping remains a later, separate decision.


## Amendment by ADR-039

External responsibilities described in this ADR are consolidated under the normative [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The External Control Plane is an abstract role; this amendment does not change the substantive Git-safety decision of this ADR.


## Amendment by ADR-045

PromotionUnit identity/declaration semantics are now exact and closed:

```text
PromotionUnit
= immutable non-empty unordered unique Set<ExactConvergenceStateRef>
= content-addressed from canonical member-set bytes
```

V1 derives `promotion_unit_id` with domain-separated/versioned SHA-256. ADR-046 supersedes the normal exact-set declaration handoff: the External Control Plane declares the logical PromotionGroup, and `ruu` mechanically materializes/reuses the exact member set once all group members are current `READY_INTERNAL`. Same exact set remains idempotently the same PromotionUnit, while any changed exact member state yields a different PromotionUnit.

Promotion topology is a separate relationship among PromotionUnit refs and does not participate in PromotionUnit identity. Target/mode/publication-policy input, lifecycle, provider-facing submission revision, higher-level semantic identity, and a separate semantic-readiness token are not PromotionUnit definition fields. Structural declaration validity is distinct from current promotion eligibility.


## ADR-046 amendment

Promotion grouping is now a two-stage boundary: durable pre-exact `PromotionGroup(Set<CanonicalConvergenceUnitRef>)` from the External Control Plane, followed by mechanical exact-state resolution/materialization into the ADR-045 PromotionUnit. There is no implicit one-ConvergenceUnit singleton default and no mid-sweep callback required merely to learn exact OIDs.


## Amendment by ADR-047

The semantic ship boundary and Git promotion boundary are now separated explicitly:

```text
PromotionGroup
= closed logical ship; may span repositories

PromotionUnit
= exact independently governed source set from exactly one repository
```

A fully exact-resolved PromotionGroup is partitioned mechanically by authoritative `repository_id`; there is exactly one PromotionUnit per represented repository and `ruu` never splits a same-group/same-repository projection into multiple PromotionUnits to create a stack. PromotionTopology remains separate from PromotionUnit identity and, under ADR-050, is derived managed state from exact promotion-base/predecessor/target facts rather than caller-authored stack intent.


## Amendment by ADR-049 and ADR-050

ADR-049 makes every provider-facing submission ref physically distinct from internal refs and binds stable `submission_id` to the repository-local logical promotion projection/publication destination rather than to one exact PromotionUnit OID. ADR-050 further amends PromotionTopology semantics: a stacked provider representation is derived only when an already-distinct child promotion has an exact predecessor dependency not yet satisfied by the authoritative target. Restacking rewrites only the submission projection through exact three-way state transplant over the immutable owned child anchor.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment — ADR-062 (2026-09-07)

Promotion topology remains independent of provider UI objects. A Pull Request is not a PromotionUnit and is not the semantic promotion itself; it is a provider projection of one logical Submission/PublicationEpisode when the target-realization route requires it.

