---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "package-verification"
domain: "ruu"
severity: "strict"
name: "Ruu package verification through ADR-081"
status: "final"
---

# Ruu — Package Verification through ADR-081

- **Date:** 2026-11-03
- **Current architecture:** ADR-001 through ADR-081
- **Current active finite qualification:** post-baseline v46
- **New ADR-081 cases:** 648 PASS
- **Retained historical cases:** 16,380 PASS
- **Cumulative modeled cases:** 17,028
- **Global hostile audit:** no BLOCKING finding; two HIGH unratified decisions

## Integrated decision

ADR-081 adds one explicit repository-local authoring dependency before promotion identity exists:

```text
Development System selects source ContributionUnit + exact commit A
→ Ruu proves exact source lineage
→ TX-A durably linearizes selection
→ REQUIRED internal anchor retains A
→ TX-B revalidates source generation/disposition and CAS-adopts dependency
→ consumer may author/checkpoint/converge
→ realization waits until target satisfaction, same-group internalization,
  or source-owned checkpoint/handoff compression
```

Native commit creation remains ordinary exact Git state and becomes a managed checkpoint only at exact frozen handoff. Dirty producer state is never consumed or implicitly committed. `ContributionUnit` remains the sole v1 authoring-occurrence identity.

A qualifying source projection requires the source's own frozen pre-sync checkpoint to contain `A`, group-local incorporation of that checkpoint, exact equality of source/consumer immutable PromotionTargets, current disposition, and CAS. Aggregate ancestry alone cannot choose a parent. The immutable consumer anchor remains `(old_base=A, owned_candidate=B)` even when parent current exact state becomes `K`.

Current target containment may satisfy the relation without a fake parent. Same-group relations create no provider edge. Source abandonment before valid realization creates exact reconciliation and never transfers publication authority.

## Retention and recovery

`AUTHORING_DEPENDENCY_OID_ANCHOR` reuses ADR-042 recovery-resource semantics:

```text
REQUIRED
→ every dependent exact use terminal
+ another durable retained root sufficient
→ GC_ELIGIBLE
```

Built-in v1 retention remains `KEEP`. Crash before anchor, after anchor, between TX-A/TX-B, during source handoff, or during compression is recovered through immutable Operation/Attempt, exact Observation, current run fencing, and managed-state CAS. An adopted dependency with a missing object is an integrity/data-loss block, never satisfaction.

## Active qualification

`qualification/state-space/post-baseline/v046/` is the first registered post-ADR-080 state-space evidence and includes:

- `qualification-metadata.json` with `POST_BASELINE` / `ADR-080` provenance;
- `state-space-audit-v46.py`;
- exact recorded stdout;
- a maintained report;
- supporting native Git dependency-anchor retention smoke.

The executable runs 648 new factorized cases covering selection/adoption, dirty-state exclusion, child-first progression, source resolution, source movement, target history, abandonment, crash/GC, competing CAS, clean-tip checkpoint adoption, cardinality, same-group behavior, cycles, and aggregate-lineage laundering.

The native Git smoke proves that exact source commit `A` remains readable after the ordinary source ref resets, reflogs expire, and `git gc --prune=now` runs, while producer-only dirty bytes never enter `A`. It derives OID width from the active object format and additionally exercises SHA-256 when supported by the installed Git.

The cumulative 17,028 figure is arithmetic traceability over 16,380 retained historical PASS cases plus 648 newly executed v46 cases. V46 does not claim to re-execute retained state-space versions.

## Hostile audit result

`qualification/audits/hostile/hostile-audit-adr081.md` performs the final repository-wide pass.

Remaining HIGH engineering follow-ups in the GitHub Project **Ruu Engineering**:

1. [issue #1](https://github.com/fanilosendrison/ruu/issues/1) — publication with more than one independently unsatisfied predecessor;
2. [issue #2](https://github.com/fanilosendrison/ruu/issues/2) — dependency discovery/refoundation after consumer authoring has begun.

Both cases fail closed locally. Project status is non-normative and cannot alter that boundary. No BLOCKING finding remains for the ratified pre-first-write, single-unsatisfied-predecessor path.

## Found-and-fixed regressions

The integration/audit correction loop fixed:

- source-ownership laundering through aggregate ConvergenceUnit ancestry;
- a source-handoff race between dependency TX-A and TX-B;
- missing DIRECT zero-unsatisfied-predecessor guards;
- undefined PromotionTarget compatibility;
- missing TX-B source generation/disposition revalidation;
- missing pre-edit fenced execution ownership;
- missing clean native-tip checkpoint adoption;
- missing consumed-OID reachability retention;
- duplicate `work_occurrence_id` identity in the active contract;
- stale externally declared PromotionGroup/PromotionUnit wording;
- duplicate active invariant labels;
- post-baseline test fixtures hard-coded to v046;
- weak competing-compression and source-laundering qualification families;
- SHA-1-only expected-absent OID construction;
- cumulative evidence wording that could imply retained cases were re-executed.

## Final validation results

```text
retained lineage generation: fixed point / 161 artifacts
active SHA-256 manifest generation: fixed point / 309 entries
immutable ADR-080 snapshot + retained projections: PASS / 282 snapshot entries
active qualification layout: PASS / 1 post-baseline qualification
maintained Markdown links: PASS / 204 local targets
qualification infrastructure tests: PASS / 26 tests
latest retained historical replay v45: PASS / 16,380 retained cases
historical package-scoped v37 replay without source package:
  NON_REPLAYABLE_MISSING_BASELINE / exit 3
post-baseline v46 replay: PASS / exact recorded stdout
installed Git: 2.55.0 / supported
retained Git smokes: PASS / 15 scripts
new shell syntax + Python compilation: PASS
git diff --check: PASS
```

The expected v37 non-replayable result is not counted as a pass. Its exact ADR-070 source package is not present locally.

## Evidence limits

- Ruu has no production implementation yet; the package proves architecture/qualification consistency, not adapter conformance.
- V46 is finite factorized evidence, not proof over arbitrary Git/provider graphs.
- The retention smoke does not protect against out-of-contract destruction of the repository/object database/reserved refs.
- Each supported harness still must demonstrate pre-first-write interception and internal provisioning-demand behavior.
- Provider-specific operations still require contextual adapter qualification.

## Verdict

**PASS for the ADR-081 architecture package, subject to HIGH engineering follow-ups [#1](https://github.com/fanilosendrison/ruu/issues/1) and [#2](https://github.com/fanilosendrison/ruu/issues/2) in the Ruu Engineering project.** Exact intermediate native Git versions can be consumed without invoking their producer first; dirty state cannot be captured implicitly; dependency objects remain anchored; later promotion compression requires source-owned handoff proof; abandonment transfers no authority; and crash/retry reconciliation is idempotent under the current fenced model.
