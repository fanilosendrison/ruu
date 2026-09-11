---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "historical-record"
domain: "ruu-design-history"
severity: "guideline"
name: "Ruu design backlog through ADR-081"
---

# Ruu design backlog through ADR-081

> **Archive status:** Retired after ADR-081. This file is not an active backlog
> and receives no new findings or work items.

## Purpose

This record summarizes the disposition of the design questions formerly kept
in `docs/design/open-design-backlog.md`. That evolving backlog accumulated
several numbering systems, closure notes, review findings, and partial design
summaries. All of its product questions were closed, superseded, externalized,
or transferred to durable GitHub Issues by ADR-081.

The accepted specifications and ADRs remain authoritative. The detailed
integration chronology remains available in the
[decision integration log](../design/decision-integration-log.md) and in Git
history. This archive must not be used to infer current product behavior.

New durable engineering work belongs in the private
[Ruu Engineering Project](https://github.com/users/fanilosendrison/projects/3)
according to the
[Ruu Engineering profile](../repository-governance/ruu-engineering.md).

## Historical disposition index

Each entry below uses one form: **topic — disposition**. References identify the
accepted decision that controls the current model.

### Product and external-responsibility questions

- **Whole-surface checkpoint candidate and identity — closed.**
  [ADR-059](../adr/adr-059-canonicalize-whole-surface-checkpoints-with-native-git-tree-construction.md)
  defines native-Git tree construction and exact candidate identity.
- **Generic development-validation evidence — removed as obsolete.**
  [ADR-060](../adr/adr-060-use-transition-local-prerequisites-instead-of-generic-development-validation-evidence.md)
  replaces it with transition-local prerequisites.
- **Development verification execution — externalized.**
  [ADR-057](../adr/adr-057-externalize-development-verification-and-model-ruu-as-state-dependent-git-progression.md)
  assigns tests, linting, review execution, and related development processes to
  the Development System.
- **Ship-ready and provider CI processes — externalized.**
  ADR-057 leaves their semantic execution to the Development System and
  repository/provider governance.
- **Final target realization proof — closed and corrected.**
  [ADR-065](../adr/adr-065-prove-final-promotion-realization-by-native-git-or-exact-provider-result-binding.md)
  introduced the proof, and
  [ADR-066](../adr/adr-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md)
  made it route-conformant.
- **`REVIEW_NOT_REQUESTED` publication fallback — closed.**
  [ADR-062](../adr/adr-062-make-promotion-route-independent-and-provider-submissions-projections.md)
  requires explicit authority or need for early provider projection.
- **Internal synthesized-state progression — closed.** ADR-060 applies exact
  transition-local prerequisites without a generic validation handoff.
- **Contribution policy for internal, team, and external submissions — placed
  outside the Git ontology.** Repository and provider governance own those
  requirements; Ruu consumes only their authoritative effects.
- **Stacked publication and restack — closed.**
  [ADR-049](../adr/adr-049-separate-stable-submission-identity-and-refs-from-internal-exact-state.md),
  [ADR-050](../adr/adr-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md),
  and
  [ADR-051](../adr/adr-051-normalize-provider-capabilities-as-contextual-semantic-operation-observations.md)
  define submission identity, derived stack shape, restack, and capability
  observation.
- **Obsolete PromotionUnit lifecycle — closed.**
  [ADR-067](../adr/adr-067-terminalize-obsolete-unpromoted-promotion-units-by-current-resolution-supersession.md)
  defines supersession without a generic abandonment state.
- **Semantic review findings and deferred work — externalized.**
  [ADR-063](../adr/adr-063-keep-findings-and-backlog-outside-ruu.md) keeps
  findings out of the Ruu engine and permits durable tracker projection.
- **PromotionTarget ownership and retargeting — closed.**
  [ADR-061](../adr/adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md)
  fixes immutable pre-authoring target binding.
- **Merge, rebase, and fast-forward policy — closed.** ADR-016, ADR-017,
  ADR-026, and ADR-028 define append-only internal history, exact ancestry,
  policy-driven promotion, and rewrite boundaries.
- **ContributionUnit to ConvergenceUnit progression — closed.**
  [ADR-037](../adr/adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md)
  defines eager mechanical convergence and sealed internal readiness.

### Numbered findings after ADR-068

- **30.41, ConvergenceUnit disposition after PromotionGroup binding — closed.**
  ADR-068 introduced cancellation, ADR-071 added the current-disposition causal
  fence, and ADR-074/ADR-075 corrected the native Git observation model.
- **30.42, PromotionGroup occurrence identity — closed.**
  [ADR-069](../adr/adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md)
  binds ordinary group occurrence identity to a work-bearing logical
  invocation.
- **30.43, terminal PromotionGroup resolution freeze — closed.** ADR-069 makes
  exact resolution group-local and freezes terminal group resolution.
- **30.44, semantic disposition as causal authorization — closed.**
  [ADR-071](../adr/adr-071-make-managed-branch-deletion-durable-abandonment-and-fence-realization-by-current-disposition.md)
  establishes the current-disposition causal fence.
- **30.45, cancellation linearization and unmanaged Git progress — closed and
  corrected.** ADR-071 establishes the fence; ADR-074 corrects native rename
  classification.
- **30.46, run-lock descriptor inheritance — closed.**
  [ADR-072](../adr/adr-072-make-host-run-lock-handles-non-inheritable-across-subprocess-boundaries.md)
  requires non-inheritable top-level run-lock handles.
- **30.47, authoring ingress independent of the Development System — closed for
  V1.**
  [ADR-073](../adr/adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md)
  retains dedicated Git worktrees as the V1 authoring substrate.
- **30.48, hostile state-space extension — closed.** State-space v39 and later
  cumulative evidence supersede the old direct-deletion classifier coverage.
- **30.49, native Git observation-plane umbrella — closed.**
  [ADR-080](../adr/adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md)
  completes the source-scoped local, remote, and provider model.
- **30.50, minimal correctness-relevant Git observation set — closed.**
  [ADR-074](../adr/adr-074-minimize-native-git-event-observation-to-managed-authoring-binding-disposition.md)
  narrows transactional local observation to current managed-authoring binding
  disposition.
- **30.51, transactional capture versus exact-state rediscovery — closed.**
  [ADR-075](../adr/adr-075-require-pre-linearization-native-ref-witnesses-and-state-rediscovery-by-observation-class.md)
  defines transactional, rediscovery, and best-effort observation classes.
- **30.52, observation provenance, replay, and idempotency — closed.**
  [ADR-076](../adr/adr-076-separate-native-witness-provenance-from-managed-effect-identity-and-make-semantic-adoption-idempotent.md)
  separates native evidence from managed-effect identity.
- **30.53, observer ownership, installation, and coexistence — closed.**
  [ADR-077](../adr/adr-077-require-attested-repository-common-observer-coverage-without-owning-foreign-git-mutation-infrastructure.md)
  requires attested coverage without taking over foreign hook infrastructure.
- **30.54, observation persistence failure — closed.**
  [ADR-079](../adr/adr-079-minimize-native-git-rejection-with-conservative-protection-filtering-and-exact-binding-admission.md)
  limits rejection to the smallest correctness-required set.
- **30.55, local Git versus remote/provider observation — closed.** ADR-080
  separates the three authority domains.
- **30.56, exact managed authoring dependency before source promotion —
  closed.**
  [ADR-081](../adr/adr-081-manage-exact-authoring-dependencies-before-promotion.md)
  defines exact pre-authoring dependency adoption and its fail-closed limits.

## Transition to Ruu Engineering

The hostile review of ADR-081 identified two intentionally unratified
generalizations. They became the first durable records in Ruu Engineering:

- [Issue #1 — Define publication semantics for multiple unsatisfied authoring predecessors](https://github.com/fanilosendrison/ruu/issues/1)
- [Issue #2 — Define late authoring-dependency refoundation after consumer writes](https://github.com/fanilosendrison/ruu/issues/2)

They remain work-management records, not accepted semantics. The Project now
owns all new durable specification, formal-verification, qualification, and
implementation work. No review finding or future design question is appended
to this archive.

## Current authority

Use the following sources for current behavior:

1. [Ruu specification](../specification/ruu-spec.md)
2. [External Control Plane contract](../specification/external-control-plane-contract.md)
3. [Accepted ADR index](../adr/README.md)
4. [Architecture overview](../architecture/overview.md)
5. [Problem statement](../architecture/problem-statement.md)

Use the shared GitHub Engineering Projects operational protocol together with
the [Ruu Engineering profile](../repository-governance/ruu-engineering.md) for
current work discovery, Issue handling, Project fields, and new finding
projection.
