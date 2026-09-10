---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "hostile-architecture-audit"
domain: "ruu"
severity: "strict"
name: "Hostile audit through ADR-081"
status: "final"
---

# Hostile Audit — Ruu architecture through ADR-081

- **Date:** 2026-11-03
- **Mode:** final global scan after integration
- **Authority reviewed:** complete active Ruu specification, External Control Plane contract, accepted ADR history through ADR-081, architecture overview, design backlog/log, and active qualification infrastructure
- **Result:** **NO BLOCKING FINDING; TWO HIGH UNRATIFIED ENGINEERING FOLLOW-UPS REMAIN**
- **Finite evidence:** post-baseline v46 executes 648 new ADR-081 cases; 17,028 cumulative modeled cases including 16,380 retained historical cases
- **Native Git evidence:** dependency-anchor retention smoke PASS on the installed default object format and SHA-256 when supported

## 1. Method and adversarial scope

The audit used two passes.

The conformity pass traced each ADR-081 decision through:

- `docs/specification/ruu-spec.md`;
- `docs/specification/external-control-plane-contract.md`;
- `docs/architecture/overview.md`;
- governing ADRs for identity, handoff, recovery, promotion, disposition, worktrees, observation, and zero-preflight behavior;
- the post-baseline v46 executable/report/output/metadata set.

The omission pass then simulated product, identity, authority, native Git, dependency, convergence, provider, crash/retry, lifecycle, and cleanup interactions across the complete maintained architecture. It included source-first, child-first, concurrent, target-satisfied, abandoned, same-group, separate-group, multi-revision, multi-predecessor, cycle, and late-discovery traces.

The burden of proof remained on the corpus. A behavior was classified `CONFIRMED-SAFE` only when the active authoritative documents supplied identity, authority, exact-state prerequisites, failure state, and recovery/retention semantics.

## 2. Remaining findings

### H081-001 — HIGH — Multiple independently unsatisfied predecessors have no ratified publication model

- **Affected authoritative sources:** ADR-081 §16; Ruu specification §§22.8 and 33.26; ADR-048; ADR-050.
- **Engineering tracking:** [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1) in the Ruu Engineering project.
- **Classification:** genuinely unratified architectural choice exposed by ADR-081; the GitHub item is non-normative work management.
- **Minimal counterexample:**

```text
consumer β explicitly requires α@A and γ@Q
A and Q are exact, retained, and represented by distinct source identities
neither effect is in the authoritative target
α and γ later resolve to different PromotionGroup/repository projections
consumer exact B contains both effects
provider submission exposes only one exact base/parent relation
```

- **Current handling:** the finite AuthoringDependency set is representable. Authoring/checkpointing may continue only when one already-existing exact authoring base canonically contains every selected OID. Realization is locally blocked while more than one external predecessor remains independently unsatisfied. Ruu does not pretend ADR-048 same-PromotionUnit source composition solves cross-group authority and does not invent a provider DAG/stack.
- **Why this is HIGH rather than BLOCKING:** the primary single-predecessor architecture is complete and the unsupported case fails closed without blocking unrelated global progress. A fresh implementer can implement the bounded behavior without guessing.
- **Decision required next:** choose one publication semantics:
  1. wait until all but one predecessor become target-satisfied;
  2. derive a deterministic promotion DAG/linearization and define provider projection for it;
  3. require semantic consolidation into another authoritative source/group;
  4. define multiple provider surfaces or another exact representation.
- **Required decision detail:** identity, cycle rules, base selection, provider capability contract, exact target-satisfaction reduction, restack order, conflict ownership, and crash/retry adoption.
- **Recommendation:** resolve [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1) through an accepted ADR before claiming general dependency-DAG publication support. Retain the current local block until then.

### H081-002 — HIGH — Late dependency discovery has no active-authoring refoundation transition

- **Affected authoritative sources:** ADR-081 §§7 and 16; Ruu specification §33.4; ADR-050; ADR-064; ADR-073.
- **Engineering tracking:** [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2) in the Ruu Engineering project.
- **Classification:** genuinely unratified architectural choice exposed by ADR-081; the GitHub item is non-normative work management.
- **Minimal counterexample:**

```text
consumer β is provisioned from ordinary baseline M
β authors exact work W under valid consumer authority
only later the Development System discovers required source α@A
```

- **Current handling:** no dependency is inferred from later ancestry. ADR-050 cannot be reused because it changes provider projection after handoff and grants no authority to rewrite an active ContributionUnit worktree/ref. Ruu performs no implicit rebase, merge, reset, or transplant. The Development System receives an exact refoundation/reconciliation need or starts another already-authorized scope.
- **Why this is HIGH rather than BLOCKING:** the accepted pre-first-write path is complete and fail-closed. The gap affects a distinct ordering not ratified by ADR-081.
- **Decision required next:** choose whether late discovery creates:
  1. a new ContributionUnit based at `A` with exact transplant of `M→W`;
  2. an authorized merge into the existing consumer under a new freeze/claim boundary;
  3. a dedicated immutable refoundation object/state machine;
  4. mandatory Development System semantic reconstruction.
- **Required decision detail:** mutation authority, old/new base and owned candidate identity, conflict state, lifecycle, dependency adoption ordering, object retention, rollback prohibition, and crash/retry recovery.
- **Recommendation:** resolve [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2) through an accepted ADR before supported harnesses advertise late dependency adoption.

## 3. Confirmed-safe results

### CS081-001 — CONFIRMED-SAFE — Stable identity is not duplicated

- **Affected sources:** ADR-081 §§1–3; Ruu specification §§2.1–2.1.2; External Control Plane contract §§2.1 and 2.4B.
- **Trace:** identical commit OID `A` appears on source ContributionUnits α and γ. A consumer selects α. Dependency identity includes repository, consumer ContributionUnit, source ContributionUnit, Git object format, and exact OID, so γ cannot later satisfy or own α's relation merely by sharing `A`.
- **Result:** `ContributionUnit` is the sole v1 authoring-occurrence identity. Session, process, task, branch, worktree, OID, and historical `work_occurrence_id` wording do not create competing authority.

### CS081-002 — CONFIRMED-SAFE — Semantic selection and mechanical reconciliation have one owner each

- **Affected sources:** ADR-081 §§2–3; External Control Plane contract §2.4E; Ruu specification §§7.10 and 22.8A.
- **Trace:** `A` is an ancestor of consumer `B`, but the Development System supplied no source/version selection.
- **Result:** no AuthoringDependency exists. Ancestry, recency, file overlap, prompt similarity, names, or execution order cannot create one. After explicit selection, Ruu—not the caller—owns exact Git proof, anchoring, target/same-group/source-handoff reconciliation, and provider-topology derivation.

### CS081-003 — CONFIRMED-SAFE — Dirty producer state cannot become dependency history

- **Affected sources:** ADR-081 §§3–4; Ruu specification Invariants 203 and 205–207; ADR-009; ADR-073.
- **Trace:** source ref identifies exact `A`; source worktree also contains staged, unstaged, untracked, ignored, generated, or secret bytes.
- **Result:** only `A` is consumable. Ruu does not inspect the mutable surface as the dependency version and does not stage, stash, copy, or synthesize a source commit. If no exact commit exists, no exact consumable version exists.

### CS081-004 — CONFIRMED-SAFE — Native commit remains distinct from managed checkpoint

- **Affected sources:** ADR-081 §§4 and 8; Ruu specification §§4.7, 22.1, 33.10; ADR-073/074/075.
- **Trace:** a managed ContributionUnit creates native commits `A1→A2→A3` while remaining `OPEN` and without invoking Ruu.
- **Result:** all commits are exact native Git versions; none implies completion, closure, handoff, group creation, or promotion. A clean current tip becomes a managed checkpoint only through exact frozen-handoff adoption. No duplicate commit is created at that adoption.

### CS081-005 — CONFIRMED-SAFE — Child may invoke before source

- **Affected sources:** ADR-081 §§7–9; Ruu specification §§22.1, 22.8A, 33.26; ADR-036/042/069.
- **Trace:** source α exposes `A` and remains active/uninvoked; consumer β adopts α@A, authors `B`, and invokes first.
- **Result:** β may checkpoint, converge, form its own PromotionGroup/PromotionUnit, and materialize its exact owned candidate. The raw relation remains a globally visible nonterminal obligation. Only realization that would publish α's effect is blocked; unrelated work continues.

### CS081-006 — CONFIRMED-SAFE — Source advancement does not make the consumer follow a live tip

- **Affected sources:** ADR-081 §§6, 9, 11–12; ADR-050; Ruu specification Invariants 208 and 212.
- **Trace:** β consumes α@A; α later advances to `A'`/`K`.
- **Result:** the dependency continues to record `A`. Active β is not mutated. After valid promotion resolution, ADR-050 computes from immutable `(old_base=A, owned_candidate=B)` onto current parent `K`; it never replaces the consumed OID or chains from a prior restacked head.

### CS081-007 — CONFIRMED-SAFE — Aggregate ancestry cannot launder source ownership

- **Affected sources:** ADR-081 §11; Ruu specification §§22.8A and 33.26; ADR-069 amendment by ADR-081; v46 source-attribution family.
- **Trace:** α originally exposed `A`, then reset to a source checkpoint `S` that omits `A`; β's work containing `A` advances a shared ConvergenceUnit, so aggregate group state `K` later contains `A`.
- **Result:** α's projection cannot claim the dependency. Compression requires α's own exact frozen checkpoint `S` to contain `A` before downward synchronization and group-local `K` to incorporate `S`. Aggregate `A≤K` alone is insufficient.

### CS081-008 — CONFIRMED-SAFE — Source handoff compression is deterministic and crash-safe

- **Affected sources:** ADR-081 §§5 and 11; ADR-042/069 amendments; Ruu specification §§27.14A, 33.26, and 33.39.
- **Trace:** TX-A persists selection; source handoff is accepted before dependency TX-B; another executor retries after a crash.
- **Result:** TX-A is the durable ordering boundary. TX-B/recovery may adopt directly as resolved after anchor, source pre-sync checkpoint, group-local incorporation, exact target equality, disposition, run-fence, and row-version/CAS checks. Two competing group attempts share one expected dependency generation; at most one wins.

### CS081-009 — CONFIRMED-SAFE — Target satisfaction needs no fake parent and remains historical

- **Affected sources:** ADR-081 §§10 and 14–15; Ruu specification §§22.8A and 33.26; ADR-066/080 terminal-history rules.
- **Trace:** authoritative consumer target contains `A` before source promotion; later target drift removes `A`, then source is abandoned.
- **Result:** exact canonical containment may be durably adopted as terminal `SATISFIED_BY_TARGET` without a synthetic group. That valid historical realization permanently establishes dependency authority, while any later consumer realization still revalidates its current route, target, policy, expected-old, and causal guards.

### CS081-010 — CONFIRMED-SAFE — Abandonment cannot transfer publication authority

- **Affected sources:** ADR-081 §14; ADR-071 amendment by ADR-081; Ruu specification Invariant 214; External Control Plane contract §2.8.1.
- **Trace:** β contains α@A; α is abandoned before `A` is target-realized and before an authorized parent effect is committed.
- **Result:** β receives no authority to publish `A`. The relation becomes `RECONCILIATION_REQUIRED(SOURCE_REALIZATION_PATH_LOST)`. Causally committed or already realized history is recovered under existing rules; proven-absent incompatible effects are not retried.

### CS081-011 — CONFIRMED-SAFE — Same-group dependency creates no artificial provider topology

- **Affected sources:** ADR-081 §13; ADR-047/048/069; Ruu specification Invariant 213.
- **Trace:** source and consumer handoffs are already members of one immutable group; source's pre-sync checkpoint contains `A`; group-local state incorporates both.
- **Result:** the relation becomes `INTERNAL_TO_SAME_GROUP`. Canonical repository projection/materialization handles it. Ruu does not add members, split the projection, or create a parent/child provider edge.

### CS081-012 — CONFIRMED-SAFE — Required dependency objects remain reachable

- **Affected sources:** ADR-081 §§5 and 15; ADR-042 amendment by ADR-081; Ruu specification Invariant 207; v46 native Git smoke.
- **Trace:** after dependency selection, the source resets/amends/deletes or renames its ordinary ref; reflogs expire and Git GC runs.
- **Result:** the exact commit remains reachable from a non-reused Ruu `AUTHORING_DEPENDENCY_OID_ANCHOR`. Adoption cannot succeed before anchor observation. The anchor stays `REQUIRED` for every dependent use and built-in v1 retention is `KEEP`. Conforming Ruu cleanup cannot delete it. Unauthorized destructive mutation of reserved refs/repository storage is an integrity/data-loss event, not a valid lifecycle transition.

### CS081-013 — CONFIRMED-SAFE — DIRECT and provider routes cannot leak unresolved source authority

- **Affected sources:** Ruu specification §§22.8–22.11, 28.3–28.7, 33.21–33.27; ADR-050/051/052/066/081.
- **Trace:** source projection resolves to current `K`, but `K`/`A` is not in the target.
- **Result:** DIRECT requires zero unsatisfied predecessors. PROVIDER_SUBMISSION may represent exactly one unsatisfied predecessor only when current policy/capability authorizes the exact stack operation. Unsupported or multi-predecessor topology waits locally; no route fallback occurs.

### CS081-014 — CONFIRMED-SAFE — PromotionTarget authority is exact

- **Affected sources:** ADR-061; ADR-081 §11; Ruu specification §22.8A; External Control Plane contract §§2.3A and 2.6.
- **Trace:** source targets `release`; consumer targets `main`.
- **Result:** the source projection cannot become the consumer's ADR-050 parent. Exact target equality is required. Without independent consumer-target satisfaction, the relation becomes `RECONCILIATION_REQUIRED(TARGET_INCOHERENT_AUTHORING_DEPENDENCY)`; Ruu neither retargets a ConvergenceUnit nor invents a cross-target stack.

### CS081-015 — CONFIRMED-SAFE — Cycles and ambiguous ownership fail closed

- **Affected sources:** ADR-081 §§6 and 11; Ruu specification §§18.4 and 33.26; v46 cycle family.
- **Trace:** semantic selections form α→β→γ→α or several candidate groups appear without one source-handoff/CAS owner.
- **Result:** the relation is invalid/`UNKNOWN_INCONSISTENT`; no ordering, topology, mutation, or realization is guessed. Independent obligations continue.

### CS081-016 — CONFIRMED-SAFE — Zero-preflight remains conceptually intact

- **Affected sources:** ADR-078 amendment by ADR-081; ADR-081 §17; Ruu specification §0.2A; External Control Plane contract §§1.1 and 2.4E.
- **Trace:** a user installs Ruu once, launches Pi/Codex/Claude Code, and requests implementation that consumes pending α@A.
- **Result:** the supported harness explicitly selects the source/version and submits an internal provisioning demand to the existing fenced engine. It waits for anchor/adoption/consumer-base provisioning before first write. The user creates no CU, worktree, dependency record, group, stack, or repository list and need not invoke α first.

### CS081-017 — CONFIRMED-SAFE — Crash, retry, stale executor, and lost wakeup preserve logical result

- **Affected sources:** ADR-042/072/076/081; Ruu specification §§17, 27.21, 33.39–33.41; v46 crash/CAS families.
- **Trace:** crash before anchor, after anchor, after source handoff, during compression, or after an external effect; duplicate observations and simultaneous reconcilers follow.
- **Result:** one OS-owned/SQLite-fenced executor, immutable Operation intent, non-reused attempts/resources, exact Observation, CAS Adoption, `BUSY+IDLE` retry, and global obligation rediscovery converge on one dependency identity/OID and at most one source projection. Recovery observes current facts and does not invent causal history.

## 4. Issues discovered and fixed during this audit

The following defects existed during the integration draft and were corrected before this final report.

### FF081-001 — BLOCKING fixed — Source ownership laundering through aggregate ConvergenceUnit state

The draft allowed `A≤K` on aggregate group state to identify the source. It now requires the source's own exact frozen checkpoint `S` to contain `A` before downward synchronization and requires group-local incorporation of `S`.

### FF081-002 — BLOCKING fixed — Handoff between dependency TX-A and TX-B could strand a valid raw relation

TX-A now durably linearizes semantic selection. A qualifying handoff accepted after TX-A but before TX-B may be adopted directly as resolved during TX-B/recovery under all exact guards.

### FF081-003 — BLOCKING fixed — DIRECT route lacked an explicit zero-unsatisfied-predecessor guard

All DIRECT entry points now require every AuthoringDependency to be target-satisfied/internal and zero unsatisfied promotion predecessors.

### FF081-004 — HIGH fixed — PromotionTarget compatibility was prose-only

Compression now requires exact equality of immutable source/consumer PromotionTargets. Mismatch produces explicit target-incoherent reconciliation unless the consumer target independently satisfies the dependency.

### FF081-005 — HIGH fixed — TX-B did not explicitly revalidate source disposition/binding generation

TX-B now CAS-revalidates source row version, binding generation/continuity, lineage proof, and non-abandoned disposition.

### FF081-006 — HIGH fixed — Pre-edit dependency adoption had no explicit fenced execution envelope

Supported harnesses now submit an internal provisioning demand to the existing single-host fenced ConvergenceEngine and wait before first write. No second authority domain or work-bearing checkpoint is introduced.

### FF081-007 — HIGH fixed — Clean native commits had no explicit managed-checkpoint adoption transition

The specification now adopts an exact clean current tip only at a frozen work-bearing handoff without creating another commit. Ordinary commit creation remains exact-state rediscovery.

### FF081-008 — HIGH fixed — Required consumed OIDs could have depended on moving refs/reflog grace

Dependency adoption now requires an operation-owned `REQUIRED` recovery anchor before CAS adoption, with built-in `KEEP` retention through all dependent obligations.

### FF081-009 — MEDIUM fixed — Duplicate authoring identities and stale grouping language

The active corpus canonicalizes `ContributionUnit` as the sole v1 authoring occurrence, removes `work_occurrence_id` from the active contract, corrects stale externally declared PromotionGroup/PromotionUnit wording, and fixes duplicate active invariant labels.

### FF081-010 — MEDIUM fixed — Qualification fixtures and model claims were stale

Infrastructure tests now derive the next unused post-baseline version. v46 models two competing CAS attempts, source-attribution laundering, dynamic Git object-format OID width, and separates 648 newly executed cases from 16,380 retained historical cases.

## 5. Cross-document coherence verdict

The final authoritative chain is singular:

```text
Development System explicit source/version selection
→ TX-A durable semantic-selection identity
→ exact source/object proof + REQUIRED Git anchor
→ TX-B fenced/CAS AuthoringDependency adoption
→ raw localized obligation
→ target satisfaction
   or same-group internalization
   or source-owned pre-sync checkpoint + handoff compression
→ stable (PromotionGroup, repository) predecessor projection
→ ADR-050 exact-state restack/provider projection when still unsatisfied
→ route-conformant realization
```

No active normative source grants semantic selection to ancestry, publication authority to a consumer, dirty-state snapshot authority to Ruu, or provider-topology selection to the caller. Historical ADR bodies retain their original decisions and carry later amendment/clarification sections where current reading changed.

## 6. Unverified areas and evidence limits

- No production implementation exists, so no claim is made that a real CoordinationStore schema, harness adapter, provider adapter, or reserved-ref protection code conforms yet.
- The v46 model is factorized finite evidence, not proof over arbitrary Git graphs or every crash interleaving.
- The native retention smoke proves current Git ref reachability/GC behavior, not resistance to malicious deletion of `.git`, object databases, or reserved Ruu refs.
- Concrete supported-harness pre-first-write interception remains an implementation conformance obligation for each Pi/Codex/Claude integration.
- Provider-specific stack, queue, and finalization behavior remains subject to contextual adapter qualification.
- Multi-predecessor publication and late refoundation are intentionally unverified because their architecture is not ratified; work is tracked in GitHub issues [#1](https://github.com/fanilosendrison/ruu/issues/1) and [#2](https://github.com/fanilosendrison/ruu/issues/2).

## 7. Required final answers

### Does the repository now contain one coherent authoritative model?

**Yes for the ratified domain.** The active specification and External Control Plane contract agree, and older ADRs are read through explicit ADR-081 amendments. The two unratified orderings are represented as fail-closed HIGH backlog items rather than contradictory implied behavior.

### Can a fresh implementer derive the intended behavior without relying on the task prompt?

**Yes for exact dependency adoption before first consumer write, child-first convergence, target/same-group/source-handoff resolution, retention, abandonment, and single-predecessor promotion.** The two unsupported cases are explicit and include minimal traces and decision questions.

### Are there remaining BLOCKING/HIGH architectural decisions?

**No BLOCKING finding remains. Two HIGH engineering follow-ups remain:** H081-001 / [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1) and H081-002 / [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2).

### Does zero-preflight naked-harness usage still work conceptually?

**Yes.** The supported harness performs explicit semantic selection and internal fenced provisioning before first write without user topology commands.

### Can an exact intermediate native Git version be consumed safely without invoking its producer first?

**Yes.** It is source-attributed, exact, anchored, and adopted before consumer authoring; the producer may remain active and dirty without its mutable state being consumed.

### Can that dependency later become an ordinary PromotionGroup dependency without semantic guessing?

**Yes.** Compression requires the same source ContributionUnit's own exact pre-sync checkpoint/handoff, group-local incorporation, exact target equality, current disposition, canonical ancestry, and CAS.

### Can dirty producer state ever accidentally become history?

**No through a conforming ADR-081 flow.** Only an existing exact commit is consumable; implicit source snapshotting is forbidden.

### Can source abandonment accidentally transfer publication authority to a child?

**No.** Without prior valid target satisfaction or causally committed realization, source path loss creates reconciliation and blocks consumer realization.

### Can required exact dependency objects disappear?

**Not through conforming Ruu lifecycle/GC.** A REQUIRED internal anchor precedes adoption and v1 retains it with `KEEP` while any exact use remains. Out-of-contract destructive repository mutation is detected as integrity/data loss, not accepted as progression.

### Do crashes, retries, and concurrent invocations preserve the same logical result?

**Yes within the ratified model.** Immutable intent, exact Observation, run/row fencing, CAS adoption, non-reused recovery resources, and fixed-point rediscovery preserve one dependency identity/OID and at most one owning source projection.

## 8. Final verdict

> **Ruu is coherent through ADR-081 for the ratified pre-authoring exact-dependency path. No BLOCKING architecture defect remains. General multi-unsatisfied-predecessor publication and late consumer refoundation remain explicit HIGH engineering follow-ups in the Ruu Engineering project and must not be implemented by guesswork.**
