---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu-architecture-decisions"
severity: "guideline"
name: "Ruu annotated architectural decision history"
---

# Ruu annotated architectural decision history

This maintained history records chronological narrative and nuanced qualifications. It is not a generated relationship authority. Canonical structured metadata is governed by [`adr-profile.yaml`](adr-profile.yaml); the [generated ADR index](index.md) projects recorded outgoing relations and derives their incoming direction mechanically.

ADR-001 through ADR-081 were migrated under ADR-082 with exact H1-to-EOF preservation evidence in [`metadata-migration-evidence.yaml`](metadata-migration-evidence.yaml). All active ADRs now carry canonical structured frontmatter. Retained Markdown metadata remains historical presentation only, and the generated relation graph remains intentionally incomplete while migrated records are `legacy-partial`.

Architectural decisions remain in chronological order. Filenames and decision numbers are stable identities; topic-based navigation should be provided by indexes rather than by moving decisions between directories.

## ADR-001 through ADR-020

- [ADR-001: Isolate concurrent work production with Git worktrees](adr-001-isolate-concurrent-work-production-with-git-worktrees.md) — Accepted — terminology clarified by ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- [ADR-002: Use repository-local contribution units as the isolation unit](adr-002-use-repository-local-contribution-units-as-the-isolation-unit.md) — Accepted — clarified by ADR-022, ADR-023, ADR-033, ADR-034, ADR-035, and ADR-038
- [ADR-003: Base commit collection on contribution-unit eligibility, not task completion](adr-003-base-commit-collection-on-contribution-unit-eligibility-not-task-completion.md) — Accepted — amended by ADR-024, ADR-029, ADR-033, ADR-034, ADR-035, and ADR-041
- [ADR-004: Make convergence scope independent of CWD and support multi-repository work](adr-004-make-convergence-global-across-registered-repositories.md) — Accepted — clarified by ADR-022, ADR-023, and ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- [ADR-005: Coordinate simultaneous `ruu` invocations with fine-grained claims and expected-ref checks](adr-005-coordinate-simultaneous-convergers-with-fine-grained-claims-and-cas.md) — Accepted — top-level simultaneous-converger arbitration superseded by ADR-041; resource-claim/CAS core retained
- [ADR-006: Use the internal hierarchy `target/base → convergence unit → contribution unit`](adr-006-use-target-convergence-unit-contribution-unit-hierarchy.md) — Accepted — terminology/current abstraction clarified by ADR-025 and ADR-034; bounded contribution-unit lifecycle clarified by ADR-035; eager integration/sealed readiness amended by ADR-037; amended by ADR-061
- [ADR-007: Check both directions of every hierarchy edge on every invocation and converge to a fixed point](adr-007-converge-every-edge-bidirectionally-to-a-fixed-point.md) — Accepted — amended by ADR-021, ADR-025, ADR-029, ADR-030, ADR-033, ADR-036, and ADR-057
- [ADR-008: Track ContributionUnit obligations explicitly until exact terminal resolution](adr-008-treat-existing-contribution-unit-refs-as-unresolved-work.md) — Accepted — terminology/lifecycle clarified by ADR-025, ADR-034, ADR-035, and ADR-038; readiness/ref semantics amended by ADR-037/ADR-038
- [ADR-009: Require exclusive contribution-unit-worktree mutation authority](adr-009-require-exclusive-worktree-mutation-authority.md) — Accepted — authorization model amended by ADR-024, ADR-033, ADR-034, ADR-038, ADR-040, and ADR-041; bounded contribution-unit lifecycle clarified by ADR-035
- [ADR-010: Bind integration/promotion readiness and validation evidence to exact Git state](adr-010-bind-readiness-and-validation-to-exact-git-state.md) — Accepted — broader exact-state binding retained; generic development-validation amendments superseded by ADR-060
- [ADR-011: Use an atomic convergence-unit readiness/promotion barrier](adr-011-use-an-atomic-convergence-unit-readiness-promotion-barrier.md) — Accepted — transition semantics amended by ADR-018, ADR-025, ADR-026, ADR-027, ADR-034, ADR-035, and ADR-037
- [ADR-012: Isolate feature/main integration workspaces and model conflicts as recoverable blocked states](adr-012-isolate-integration-workspaces-and-model-conflicts-as-blocked-states.md) — Accepted — amended by ADR-027, ADR-029, ADR-030, ADR-038, and ADR-040
- [ADR-013: Fail closed on unknown or inconsistent Git/orchestration state](adr-013-fail-closed-on-unknown-or-inconsistent-git-orchestration-state.md) — Accepted — extended by ADR-022, ADR-023, ADR-026, ADR-027, ADR-028, ADR-029, ADR-030, ADR-032, ADR-036, ADR-038, and ADR-040
- [ADR-014: Represent cross-repository promotion as non-atomic, recoverable partial progress](adr-014-represent-cross-repository-promotion-as-non-atomic-partial-progress.md) — Accepted — amended by ADR-018, ADR-026, and ADR-027
- [ADR-015: Provision the repository-local convergence-unit ref before the first contribution unit](adr-015-provision-repository-local-convergence-unit-ref-before-first-contribution-unit.md) — Accepted — provisioning ownership clarified by ADR-023, terminology by ADR-025/034, authority boundary by ADR-033, brand-new repository bootstrap clarified by ADR-056; amended by ADR-061
- [ADR-016: Use an append-only, no-rebase V1 reconciliation strategy](adr-016-use-an-append-only-no-rebase-v1-reconciliation-strategy.md) — Accepted for internal refs — promotion portions superseded/amended by ADR-018, ADR-026, and ADR-028
- [ADR-017: Derive fast-forward/merge selection mechanically from exact Git ancestry](adr-017-derive-fast-forward-and-divergence-from-exact-git-ancestry.md) — Accepted — scope clarified by ADR-018, ADR-025, ADR-026, and ADR-028
- [ADR-018: Require PR-mediated promotion to protected main](adr-018-require-pr-mediated-promotion-to-protected-main.md) — Accepted as strict PR-policy case — universal PR requirement superseded by ADR-026; publication intent amended by ADR-032
- [ADR-019: Keep `contribution-unit→convergence-unit` integration internal and PR-free](adr-019-keep-contribution-unit-to-convergence-unit-integration-internal-and-pr-free.md) — Accepted — terminology clarified by ADR-025/027/034/035, verification by ADR-029/030, eager integration by ADR-037
- [ADR-020: Publish internal refs at stable boundaries when direct push is enabled](adr-020-publish-internal-refs-at-stable-boundaries.md) — Accepted — amended by ADR-021, ADR-026, ADR-027, ADR-028, ADR-029, and ADR-030

## ADR-021 through ADR-040

- [ADR-021: Freeze the exact PR head during external governance and localize PR waits](adr-021-freeze-exact-pr-head-and-localize-external-waits.md) — Accepted — amended by ADR-026, ADR-028, and ADR-032
- [ADR-022: Keep managed repository discovery/registry and a derived active-convergence index](adr-022-own-repository-registry-and-active-convergence-set.md) — Accepted — ownership/provisioning amended by ADR-023, terminology/policy amended by ADR-025–ADR-027, verification responsibility amended by ADR-031, invocation-scope authority superseded by ADR-036, and brand-new repository admission clarified by ADR-056
- [ADR-023: Separate pre-edit contribution-unit provisioning from `ruu`](adr-023-separate-contribution-unit-provisioning-from-ruu.md) — Accepted — terminology/lifecycle clarified by ADR-034/ADR-035/ADR-038; external boundary consolidated by ADR-039; brand-new repository bootstrap clarified by ADR-056; amended by ADR-061, ADR-078 and ADR-079
- [ADR-024: Separate invocation principal from contribution-unit mutation authority](adr-024-separate-invocation-principal-from-contribution-unit-authority.md) — Accepted — delegation mechanics superseded by ADR-033/ADR-041; terminology clarified by ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- [ADR-025: Replace the Git-level “feature” abstraction with a repository-local convergence unit](adr-025-replace-feature-with-repository-local-convergence-unit.md) — Accepted
- [ADR-026: Make promotion repository-policy-driven instead of universally PR-mediated](adr-026-make-promotion-repository-policy-driven.md) — Accepted — amended by ADR-029, ADR-032, and ADR-043; amended by ADR-061
- [ADR-027: Separate convergence units from promotion/submission units and promotion topology](adr-027-separate-convergence-units-from-promotion-units-and-topology.md) — Accepted — amended by ADR-029, ADR-030, ADR-032, ADR-037, ADR-039, ADR-045, ADR-046, ADR-047, ADR-049, and ADR-050
- [ADR-028: Preserve internal convergence OIDs while allowing policy-authorized submission rewrites](adr-028-preserve-internal-oids-and-allow-policy-authorized-submission-rewrites.md) — Accepted — amended by ADR-029, ADR-030, ADR-032, ADR-038, ADR-049, and ADR-050
- [ADR-029: Require full verification before authoritative adoption of managed state-producing results](adr-029-require-full-verification-before-authoritative-managed-state-adoption.md) — Accepted historically — universal development-validation prerequisite superseded by ADR-060
- [ADR-030: Bind full-verification evidence to exact state and reuse it when still valid](adr-030-bind-full-verification-evidence-to-exact-state-and-reuse-it-when-valid.md) — Accepted historically — generic development-validation evidence semantics superseded by ADR-060; broader exact-state binding retained
- [ADR-031: Separate verification execution capacity from Git mutation claims](adr-031-separate-verification-capacity-from-git-mutation-claims.md) — Superseded as a Ruu component by ADR-057
- [ADR-032: Model PR review request as publication intent, not as a Ruu business-readiness state](adr-032-model-pr-review-request-as-publication-intent-not-business-readiness.md) — Accepted
- [ADR-033: Consume an external contribution-unit mutation-authority contract; do not own producer/runtime liveness](adr-033-consume-external-contribution-unit-mutation-authority.md) — Accepted — terminology/cardinality/lifecycle clarified by ADR-034/ADR-035; external boundary consolidated by ADR-039; candidate-boundary semantics clarified by ADR-040; invocation-relative authority superseded by ADR-041
- [ADR-034: Replace the Git-level writer model with repository-local contribution units](adr-034-replace-writer-model-with-repository-local-contribution-units.md) — Accepted — object identity/artifact semantics amended by ADR-038 core decision — current object name/lifecycle superseded by ADR-035
- [ADR-035: Use bounded contribution units with external lifecycle authority](adr-035-use-bounded-contribution-units-with-external-lifecycle-authority.md) — Accepted — integration/readiness semantics amended by ADR-037; abandonment/removal semantics superseded by ADR-038; external boundary consolidated by ADR-039
- [ADR-036: Make every invocation global over all nonterminal managed obligations](adr-036-make-every-invocation-global-over-all-nonterminal-managed-obligations.md) — Accepted — reconciliation-obligation coverage clarified by ADR-040; trigger/coalescing semantics amended by ADR-041
- [ADR-037: Eagerly integrate contribution checkpoints and seal convergence membership before internal readiness](adr-037-eagerly-integrate-contribution-checkpoints-and-seal-convergence-before-readiness.md) — Accepted — artifact/lifecycle semantics amended by ADR-038
- [ADR-038: Decouple ContributionUnit identity from editing artifacts and remove abandonment semantics](adr-038-decouple-contribution-unit-identity-from-editing-artifacts.md) — Accepted — conflict/attribution follow-up resolved by ADR-040 — external boundary consolidated by ADR-039
- [ADR-039: Formalize the external control-plane boundary as a normative contract](adr-039-formalize-external-control-plane-contract.md) — Accepted — external diagnostic/interfaces amended by ADR-040, ADR-043, ADR-055, ADR-056, and ADR-057; amended by ADR-061 and clarified by ADR-078
- [ADR-040: Emit exact reconciliation obligations and attribute candidate mutations by authorized ContributionUnit boundary](adr-040-emit-exact-reconciliation-obligations-and-attribute-candidate-mutations-by-authorized-boundary.md) — Accepted

## ADR-041 through ADR-060

- [ADR-041: Coalesce convergence demands under a single-host fenced executor](adr-041-coalesce-convergence-demands-under-a-single-host-fenced-executor.md) — Accepted
- [ADR-042: Use a reconciler-driven CoordinationStore with OS-owned runs and an append-only effect journal](adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md) — Accepted — AuthoringDependency recovery anchoring amended by ADR-081
- [ADR-043: Resolve promotion policy by authoritative constraint composition](adr-043-resolve-promotion-policy-by-authoritative-constraint-composition.md) — Accepted; amended by ADR-061
- [ADR-044: Establish promotion-policy currentness by immediate authoritative revalidation](adr-044-establish-promotion-policy-currentness-by-immediate-authoritative-revalidation.md) — Accepted; amended by ADR-061
- [ADR-045: Make PromotionUnits immutable content-addressed exact-state sets](adr-045-make-promotion-units-immutable-content-addressed-exact-state-sets.md) — Accepted; amended by ADR-061
- [ADR-046: Predeclare closed PromotionGroups and resolve them to exact PromotionUnits](adr-046-predeclare-closed-promotion-groups-and-resolve-them-to-exact-promotion-units.md) — Accepted — ordinary grouping identity/resolution superseded in part by ADR-069
- [ADR-047: Project PromotionGroups deterministically into repository-local PromotionUnits](adr-047-project-promotion-groups-deterministically-into-repository-local-promotion-units.md) — Accepted — group-local state amended by ADR-069; same-group AuthoringDependency handling clarified by ADR-081
- [ADR-048: Materialize repository-local multi-source PromotionUnits by canonical pairwise merging](adr-048-materialize-repository-local-multi-source-promotion-units-by-canonical-pairwise-merging.md) — Accepted — raw exact authored-base provenance clarified by ADR-081
- [ADR-049 — Separate stable submission identity and refs from internal exact state](adr-049-separate-stable-submission-identity-and-refs-from-internal-exact-state.md) — Accepted
- [ADR-050 — Derive stacked publication from unsatisfied promotion dependencies and restack by exact-state transplant](adr-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md) — Accepted — pre-promotion AuthoringDependency provenance added by ADR-081
- [ADR-051 — Normalize provider capabilities as contextual semantic-operation observations](adr-051-normalize-provider-capabilities-as-contextual-semantic-operation-observations.md) — Accepted
- [ADR-052 — Advance DIRECT targets by atomic exact-old CAS fast-forward](adr-052-advance-direct-targets-by-atomic-exact-old-cas-fast-forward.md) — Accepted; amended by ADR-061
- [ADR-053 — Turn `CHANGES_REQUESTED` into durable session-independent review-correction work](adr-053-turn-changes-requested-into-durable-session-independent-review-correction-work.md) — Accepted
- [ADR-054 — Separate PromotionUnit completion, ConvergenceUnit closure, and retirement](adr-054-separate-promotion-unit-completion-convergence-unit-closure-and-retirement.md) — Accepted
- [ADR-055 — Settle partial cross-repository ships with forward actions and publication episodes](adr-055-settle-partial-cross-repository-ships-with-forward-actions-and-publication-episodes.md) — Accepted
- [ADR-056: Bootstrap new repositories before managed authoring and keep provider creation external](adr-056-bootstrap-new-repositories-before-managed-authoring-and-keep-provider-creation-external.md) — Accepted; amended by ADR-061 and clarified by ADR-078
- [ADR-057 — Externalize development verification and model `ruu` as state-dependent Git progression](adr-057-externalize-development-verification-and-model-ruu-as-state-dependent-git-progression.md) — Accepted — development-verification execution boundary retained; generic validation evidence/demand model superseded by ADR-060
- [ADR-058 — Preserve native Git equivalence and whole-surface checkpoint intent](adr-058-preserve-native-git-equivalence-and-whole-surface-checkpoint-intent.md) — Accepted
- [ADR-059 — Canonicalize whole-surface checkpoints with native Git tree construction](adr-059-canonicalize-whole-surface-checkpoints-with-native-git-tree-construction.md) — Accepted
- [ADR-060 — Use transition-local prerequisites instead of generic development-validation evidence](adr-060-use-transition-local-prerequisites-instead-of-generic-development-validation-evidence.md) — Accepted

## ADR-061 through ADR-080

- [ADR-061 — Bind each ConvergenceUnit to an immutable pre-authoring PromotionTarget](adr-061-bind-each-convergence-unit-to-an-immutable-pre-authoring-promotion-target.md) — Accepted
- [ADR-062 — Make promotion route-independent and treat provider submissions as projections](adr-062-make-promotion-route-independent-and-provider-submissions-projections.md) — Accepted
- [ADR-063 — Keep review findings and backlog outside `ruu`](adr-063-keep-findings-and-backlog-outside-ruu.md) — Accepted
- [ADR-064 — Bind pre-commit semantic readiness by frozen mutation handoff, not validation evidence](adr-064-bind-pre-commit-readiness-by-frozen-mutation-handoff.md) — Accepted
- [ADR-065 — Prove final promotion realization by native Git ancestry or exact provider-result binding](adr-065-prove-final-promotion-realization-by-native-git-or-exact-provider-result-binding.md) — Accepted — final proof semantics corrected/superseded in part by ADR-066
- [ADR-066 — Bind promotion success to route-conformant Candidate→Submission→Result→Target chains](adr-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md) — Accepted
- [ADR-067 — Terminalize obsolete unpromoted PromotionUnits by current-resolution supersession](adr-067-terminalize-obsolete-unpromoted-promotion-units-by-current-resolution-supersession.md) — Accepted
- [ADR-068 — Cancel unrealized PromotionGroups explicitly and keep Git artifact deletion semantically neutral](adr-068-cancel-unrealized-promotion-groups-explicitly-and-keep-git-artifact-deletion-semantically-neutral.md) — Accepted
- [ADR-069 — Bind PromotionGroups to work-bearing Ruu invocations and group-local exact state](adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md) — Accepted — source-handoff dependency compression clarified by ADR-081
- [ADR-070 — Define Ruu as Git-based version control redesigned for agentic development](adr-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md) — Accepted
- [ADR-071 — Make managed authoring disposition durable and fence realization by current disposition](adr-071-make-managed-branch-deletion-durable-abandonment-and-fence-realization-by-current-disposition.md) — Accepted — native binding-disposition mechanics corrected by ADR-074 and capture strength refined by ADR-075
- [ADR-072 — Make host run-lock handles non-inheritable across subprocess boundaries](adr-072-make-host-run-lock-handles-non-inheritable-across-subprocess-boundaries.md) — Accepted
- [ADR-073 — Require Git worktrees as the v1 authoring isolation substrate](adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md) — Accepted — authoring-surface evidence requirement amended by ADR-074; initial handoff/admission clarified by ADR-079; exact native authoring versions clarified by ADR-081
- [ADR-074 — Minimize native Git event observation to managed authoring-binding disposition](adr-074-minimize-native-git-event-observation-to-managed-authoring-binding-disposition.md) — Accepted
- [ADR-075 — Require pre-linearization native-ref witnesses only for managed authoring disposition; rediscover all other Git facts from exact state](adr-075-require-pre-linearization-native-ref-witnesses-and-state-rediscovery-by-observation-class.md) — Accepted
- [ADR-076 — Separate native witness provenance from managed effect identity and make semantic adoption exactly-once](adr-076-separate-native-witness-provenance-from-managed-effect-identity-and-make-semantic-adoption-idempotent.md) — Accepted
- [ADR-077 — Require attested repository-common observer coverage without owning foreign Git mutation infrastructure](adr-077-require-attested-repository-common-observer-coverage-without-owning-foreign-git-mutation-infrastructure.md) — Accepted
- [ADR-078 — Make zero-preflight coding-harness integration part of the governing product intent](adr-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md) — Accepted
- [ADR-079 — Minimize native Git rejection with conservative protection filtering and exact binding admission](adr-079-minimize-native-git-rejection-with-conservative-protection-filtering-and-exact-binding-admission.md) — Accepted
- [ADR-080 — Separate local Git causality, remote Git state, and provider workflow evidence](adr-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md) — Accepted

## ADR-081 onward

- [ADR-081 — Manage exact authoring dependencies before promotion](adr-081-manage-exact-authoring-dependencies-before-promotion.md) — Accepted — exact source-attributed native commits, crash-safe retention, raw-to-promotion reconciliation, target satisfaction, and no source-authority transfer
- [ADR-082 — Adopt validated OKF Architecture Decision Record metadata](adr-082-adopt-validated-okf-architecture-decision-record-metadata.md) — Accepted — pin the generalized OKF ADR profile, authorize an active-corpus payload-preserving migration, preserve immutable qualification snapshots, and separate generated projections from this annotated history
