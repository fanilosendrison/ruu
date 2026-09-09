# Ruu architecture package

This archive contains a non-normative architecture overview, the current consolidated specification, architectural decisions, External Control Plane contract, design backlog/history, and executable/static verification artifacts for `ruu` through **ADR-080**.

This is the **qualification-lineage-restored, project-rename-migrated revision** of the ADR-080 package. The complete historical qualification chain remains present, but files that contained the former project-name token were mechanically rename-migrated and therefore have new current hashes recorded in `QUALIFICATION-LINEAGE.json`.

## Start here

1. **`ARCHITECTURE-OVERVIEW.md`** — non-normative architecture map and recommended first read for building the correct mental model before the normative specification/ADR history.
2. **`RUU-SPEC.md`** — primary normative consolidated specification: requirements, invariants, state model, responsibilities, and architectural implications.
3. **`EXTERNAL-CONTROL-PLANE-CONTRACT.md`** — normative boundary between `ruu` and the Development System / External Control Plane.
4. **`ADR-070-make-hands-off-concurrent-invoke-anywhere-convergence-the-governing-product-intent.md`** — governing product-intent decision.
5. **`ADR-080-separate-local-git-causality-remote-git-state-and-provider-workflow-evidence.md`** — closes 30.55 and the 30.49 umbrella by separating local causal observation, authoritative remote Git state, and optional provider workflow evidence.
6. **`ADR-079-minimize-native-git-rejection-with-conservative-protection-filtering-and-exact-binding-admission.md`** — closes 30.54 and fixes the minimal veto set, conservative protection filter, exact ref-admission barrier, and initial worktree authority handoff.
7. **`ADR-078-make-zero-preflight-coding-harness-integration-part-of-the-governing-product-intent.md`** — makes one-time install + supported-harness automatic pre-edit plumbing + later simple `ruu` invocation normative.
8. **`ADR-077-require-attested-repository-common-observer-coverage-without-owning-foreign-git-mutation-infrastructure.md`** — closes 30.53 and fixes observer ownership/composition, V1 mutation-engine boundary, functional attestation, and coverage epochs.
9. **`ADR-076-separate-native-witness-provenance-from-managed-effect-identity-and-make-semantic-adoption-idempotent.md`** — closes 30.52 and fixes provenance/replay/exactly-once semantics.
10. **`ADR-075-require-pre-linearization-native-ref-witnesses-and-state-rediscovery-by-observation-class.md`** — closes 30.51 and fixes the native-ref capability/capture-strength contract.
11. **`ADR-074-minimize-native-git-event-observation-to-managed-authoring-binding-disposition.md`** — closes 30.50 and corrects native rename-vs-abandonment classification.
12. **`ADR-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md`** — closes 30.47 and fixes the concrete v1 authoring substrate.
13. **`ADR-072-make-host-run-lock-handles-non-inheritable-across-subprocess-boundaries.md`** — closes 30.46 and hardens ADR-042 host ownership.
14. **`ADR-071-make-managed-branch-deletion-durable-abandonment-and-fence-realization-by-current-disposition.md`** — closes 30.44/30.45; native binding classification is corrected by ADR-074.
15. **`OPEN-DESIGN-BACKLOG.md`** — design history/backlog. The native-Git observation-plane cluster is closed: ADR-074..080 close 30.50–30.55 and ADR-080 closes umbrella 30.49.
16. **`PACKAGE-VERIFICATION-ADR080.md`**, **`HOSTILE-AUDIT-ADR080.md`**, and **`STATE-SPACE-AUDIT-v45.md`** — current verification evidence.
17. **`QUALIFICATION-LINEAGE.md`**, **`QUALIFICATION-LINEAGE.json`**, **`verify-qualification-lineage.py`**, and **`QUALIFICATION-REPLAY-ADR080.txt`** — restored qualification lineage, rename-migrated hashes, and anti-disappearance verification.
18. **`RENAME-MIGRATION-RUU.md`** — project-wide naming migration record; architectural semantics unchanged.
19. **`ADR-001...ADR-080`** — full architectural decision history.

## ADR-070 in one paragraph

ADR-070 defines `ruu` as **Git-based version control redesigned for agentic software development** and makes that definition a governing architectural contract. Its core is concurrent agentic version control over native Git: users may run several coding sessions concurrently, invoke from any already-managed repository, and avoid manually serializing sessions, enumerating repositories, choosing PromotionGroups, declaring topology, or repairing mechanically reconcilable staleness. Remote hosting and provider publication (PRs, stacks, merge queues, protected-target APIs) are an extended feature layer that projects/realizes core exact state, analogous to GitHub/GitLab extending Git rather than defining it. Earlier technical rules are interpreted under this product definition, and a future regression requires an explicit ADR-070 amendment.


## ADR-080 in one paragraph

ADR-080 closes 30.55 and the 30.49 observation-plane umbrella by separating three source-authority domains. `LOCAL_GIT` owns local exact state and the narrow pre-linearization managed-binding causal observer; `REMOTE_GIT` owns current authoritative remote refs/OIDs and exact-preconditioned remote mutation/re-observation; optional `PROVIDER` owns forge-specific submission/review/check/queue/governance/finalization facts. Local remote-tracking refs are caches. Bare Git remotes are first-class for provider-free routes. Webhook delivery is an unreliable/reorderable transport: it may wake reconciliation and may carry positive authenticated provider evidence when exact adapter semantics are demonstrated, but absence never proves non-occurrence, delivery identity is not semantic identity, and cross-source causality is never inferred from wall clocks. Remote publication artifact topology never manufactures local managed-binding `CONTINUATION | ABANDON`.

## ADR-079 in one paragraph

ADR-079 closes 30.54 by making native-Git rejection proportional to causal necessity. Non-cessation ref/tip movement remains exact-state observed and advisory telemetry/wakeups never become veto authority. A repository-common conservative `ManagedRefProtectionFilter` accelerates safe negative decisions without duplicating binding authority; degraded filter state falls back to the CoordinationStore rather than becoming a coverage gap. Any current managed-binding cessation/replacement requires the complete crash-durable preparation batch before linearization. Initial managed binding admission is serialized with native ref mutation through a capability-based `RefAdmissionBarrier`; the binding becomes CURRENT while exclusion is held, exact worktree topology is revalidated, then authoring authority is handed to the producer. The current Git-core/files profile uses a prepared exact no-op ref transaction as the demonstrated barrier implementation.

## ADR-078 in one paragraph

ADR-078 makes the pre-edit half of the hands-off product promise explicit. For a supported coding harness, the normative path is one-time Ruu installation (including any supported-harness adapter registration), ordinary agent authoring, then `ruu` when the user/agent wants a checkpoint. Required ContributionUnit/ConvergenceUnit/ref/worktree/observer/binding/handoff plumbing is automatic before first managed write; the user does not run `start/create-cu/provision` or operate a second control-plane product. ADR-023 remains a phase/authority separation: provisioning is still pre-edit and cannot be retroactively performed by the later convergence invocation, but it may be implemented by a Ruu-supplied harness integration. Semantic authority remains outside the convergence engine.


## ADR-072/073 in one paragraph

ADR-072 closes the subprocess-inheritance hole in ADR-042: the host run-lock descriptor/handle belongs only to the top-level executor and must be non-inheritable, so a surviving Git/provider/helper child cannot keep the host fence alive after the executor dies. ADR-073 closes the speculative authoring-ingress question by requiring dedicated Git worktrees as the concrete v1 authoring isolation substrate while keeping durable ContributionUnit/checkpoint identity independent of post-capture worktree lifetime. V1 adds no direct arbitrary commit/tree/snapshot input contract; a future sandbox substrate requires a new ADR proving equivalent guarantees.

## ADR-071/074/075/076/077 in one paragraph

ADR-071 closes 30.44/30.45: persisted operations are historical knowledge, never durable future authority, and every new managed realization effect is fenced by current semantic disposition. ADR-074 corrects the native-binding classifier. ADR-075 closes 30.51 by requiring pre-linearization vetoable normalized witnesses only for native mutations that can terminate/replace a current managed binding; adapters report backend facts and the core derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`. ADR-076 closes 30.52 by keeping those native witnesses separate from managed `Operation` intent, making optional Attempt provenance non-authoritative, and enforcing exactly-once at logical Adoption/binding-generation disposition rather than observation delivery. Duplicate/replayed evidence is idempotent and scans never manufacture missing causal history. Backend capabilities remain normative rather than backend names; all non-disposition Git observations remain exact-state rediscovery. ADR-077 closes 30.53 by making observer coverage repository-common and functionally attested for an admitted mutation-engine/adapter profile, forbidding silent takeover of foreign hooks/config, requiring Git core as the V1 engine family, and representing continuous trust as coverage epochs. Unwitnessed mutation of a managed binding by a bypass writer is an integrity failure, never inferred semantic history.

## ADR-069 in one paragraph

Ordinary new implementation work is bounded by one durable work-bearing logical `ruu` invocation. Its sealed ContributionUnit cohort mechanically creates one distinct PromotionGroup occurrence; the group is no longer identified solely by its ConvergenceUnit member set. Exact PromotionGroup state is group-local rather than an alias of live current ConvergenceUnit state. Same-group corrections require explicit group-bound authority and start from the group's exact reviewed/prior state; terminal groups freeze their resolution. ADR-050 remains the descendant restack mechanism.

## Specification filename compatibility

`RUU-SPEC.md` and `ruu-requirements-v1-merge-policy.md` are intentionally byte-for-byte identical in this package.

The latter is a legacy filename retained because historical and current state-space audit scripts reference it directly. It is not a second specification and must not diverge from `RUU-SPEC.md`.

## Qualification-lineage preservation

The ADR-080 package has been revised to repair a packaging traceability regression discovered on 2026-09-08. Exact historical executable/result artifacts were restored from previously verified ADR-070 and ADR-073 packages; no historical evidence was regenerated from Markdown prose. The package now retains the complete executable/result state-space chain **v2..v45**, the eight retained ADR-070 Git smoke suites, the ADR-073 reference-transaction/run-lock smokes, and the current native/remote observation smokes.

`QUALIFICATION-LINEAGE.json` records per-artifact SHA-256 values and provenance. `verify-qualification-lineage.py` fails on silent disappearance, silent byte mutation, gaps in v2..v45, or unregistered audit/smoke artifacts. A future physical removal requires an explicit archive record rather than simple package omission. See `QUALIFICATION-LINEAGE.md`.

Historical state-space executables may contain package-context assertions tied to their original ADR baseline; they are intentionally not patched forward. `QUALIFICATION-REPLAY-ADR080.txt` distinguishes immutable historical recorded outputs from current-environment replay results and records exact source-baseline replay of v37/v38 plus the current v45 checkpoint.

## Other artifacts

- `DECISION-INTEGRATION-LOG.md` records decision integration history.
- `HOSTILE-AUDIT-*` and `AGENTIC-GIT-GITHUB-CONFRONTATION-AUDIT.md` are audit evidence, not substitutes for the consolidated specification.
- `state-space-audit-v2..v45.py` plus their reports/recorded outputs are retained as the contiguous finite-model qualification lineage; v38 preserves its historical uppercase output filename `STATE-SPACE-AUDIT-v38.txt`.
- `git-*-smoke-v*.sh/.txt` are concrete Git behavior checks; historical suites remain retained even after newer observation smokes supersede them operationally.
- `git-native-observation-smoke-v3.sh/.txt` is the current ADR-075 native-ref capability/capture-strength regression, including stock `files` and `reftable` behavior.
- `state-space-audit-v45.py/.txt` is the executable current ADR-080 source-domain finite-model extension; v44 remains the ADR-079 baseline.
- `git-native-observation-smoke-v5.sh/.txt` remains the ADR-079 admission-barrier/worktree-handoff Git regression.
- `git-remote-observation-smoke-v1.sh/.txt` is the ADR-080 bare-remote regression for stale tracking refs, direct remote currentness, exact-old CAS, deletion observation, and provider-free operation.
- `MANIFEST.sha256` authenticates the files in this archive (excluding the manifest itself).

When reading the package as a new contributor, begin with the `Product intent` section at the head of `RUU-SPEC.md`, then ADR-070 and ADR-078, then ADR-080/079/077/076/075/074/073/072/071, ADR-069 and the older ADRs to understand how the current mechanisms evolved under that governing product contract.
