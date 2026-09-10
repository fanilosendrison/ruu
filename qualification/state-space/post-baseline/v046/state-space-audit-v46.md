# State-Space Audit v46 — ADR-081 exact authoring dependencies

- **Date:** 2026-11-03
- **Provenance:** POST_BASELINE
- **Immutable baseline:** ADR-080 / retained v45
- **Retained historical evidence:** 16,380 combinations — retained PASS
- **New ADR-081 cases executed by v46:** 648 — PASS
- **Cumulative modeled evidence:** **17,028 cases**
- **Supporting native Git smoke:** PASS

## New finite families

v46 adds factorized finite coverage for:

1. explicit Development System source/version selection plus exact source/object/anchor admission;
2. dirty source-state exclusion and rejection of implicit producer snapshotting;
3. child-first handoff/internal progression while raw dependency realization stays blocked;
4. target-first, same-group, source-handoff, abandonment, and ambiguous-attribution reconciliation precedence;
5. immutable consumed OID and no active consumer mutation after source advance/reset/rename;
6. terminal historical target satisfaction with current guards retained for later realization;
7. source abandonment without child publication-authority transfer;
8. dependency-adoption crash windows, required anchors, and Git garbage collection;
9. two competing compression attempts against one expected raw-dependency generation, including both causal orders and stale run fencing;
10. exact clean native-tip checkpoint adoption only at frozen handoff and without a new commit;
11. finite dependency cardinality with fail-closed multi-unsatisfied-predecessor realization;
12. same-group internalization without provider topology;
13. dependency-cycle rejection;
14. rejection of aggregate-lineage laundering when the source's own frozen pre-sync checkpoint omitted the consumed OID.

## Supporting native Git retention smoke

`git-authoring-dependency-retention-smoke-v1.sh` constructs this concrete state:

```text
base M
→ source native commit A
→ producer-only dirty untracked bytes remain outside A
→ Ruu-style internal recovery ref anchors A
→ ordinary source ref resets to M
→ all reflogs expire
→ git gc --prune=now
```

The smoke proves:

```text
A remains an ordinary readable commit through the exact anchor
tree(A) excludes the producer's dirty untracked bytes
source ref no longer reaches A
dirty producer bytes remain only mutable filesystem state
```

The smoke derives the zero OID width from the repository's canonical object format. It always exercises the Git installation's default format and also exercises SHA-256 when that Git supports SHA-256 repository initialization.

This is evidence for Git reachability through an internal ref. It does not prove an implementation's future CoordinationStore/ref-transaction code, reserved-ref protection, or every Git backend profile.

## Executable result

```text
ADR-081 dependency adoption family: 64 PASS
ADR-081 dirty-state exclusion family: 32 PASS
ADR-081 child-first progression family: 32 PASS
ADR-081 dependency resolution family: 128 PASS
ADR-081 source-movement immutability family: 32 PASS
ADR-081 target-satisfaction history family: 16 PASS
ADR-081 abandonment authority family: 32 PASS
ADR-081 anchor crash/GC family: 64 PASS
ADR-081 concurrent compression family: 64 PASS
ADR-081 clean native-tip checkpoint family: 32 PASS
ADR-081 predecessor cardinality family: 24 PASS
ADR-081 same-group family: 32 PASS
ADR-081 dependency-cycle family: 64 PASS
ADR-081 source-attribution laundering family: 32 PASS
ADR-081 dependency anchor retention smoke: PASS
new combinations: 648 PASS
retained v45 baseline: 16380
v46 cumulative modeled cases: 17028
```

## Key assertions

```text
explicit source identity + exact OID selection
+ exact source lineage/object proof
+ REQUIRED recovery anchor
→ AuthoringDependency may be adopted

source worktree dirty
+ exact commit A selected
→ consume A only
→ never synthesize producer checkpoint/commit

raw dependency
→ child may hand off/checkpoint/converge
→ affected realization remains blocked

current authoritative target contains A
→ SATISFIED_BY_TARGET
→ no fake parent group

same immutable group contains source and consumer
→ INTERNAL_TO_SAME_GROUP
→ no provider edge

same source ContributionUnit later hands off frozen pre-sync S containing A
+ group-local K incorporates S
+ immutable PromotionTargets are equal
→ CAS-resolve to stable source group/repository projection
→ consumed A remains immutable

aggregate K contains A only because consumer B reintroduced A
+ source frozen pre-sync S omitted A
→ source attribution not proven
→ no compression

source abandoned + A not target-realized
→ RECONCILIATION_REQUIRED
→ child receives no source publication authority

adopted dependency + anchor missing
→ UNKNOWN_INCONSISTENT
→ never satisfied

more than one independently unsatisfied external predecessor
→ realization blocked
→ provider topology not invented
```

## Qualification limits

The executable runs 648 new ADR-081 cases. It does not re-execute the 16,380 retained historical cases; the cumulative number is arithmetic traceability over independently retained PASS evidence plus the new run.

The finite model does not choose the multi-predecessor publication or late consumer-refoundation designs tracked in Ruu Engineering issues [#1](https://github.com/fanilosendrison/ruu/issues/1) and [#2](https://github.com/fanilosendrison/ruu/issues/2). It asserts only their current fail-closed boundaries. It also does not claim exhaustive coverage over unbounded Git DAGs, all crash interleavings, provider implementations, or malicious deletion of reserved Ruu refs.

## Verdict

**PASS for the 648 newly executed ADR-081 cases and supporting native Git smoke.** Together with 16,380 retained historical PASS cases, the repository records 17,028 cumulative modeled cases. The new evidence supports exact source/version adoption, dirty-state exclusion, child-first progress, crash-safe reachability, source-owned deterministic compression, target satisfaction, same-group handling, and no abandonment authority transfer. [GitHub issues #1](https://github.com/fanilosendrison/ruu/issues/1) and [#2](https://github.com/fanilosendrison/ruu/issues/2) track the intentionally unratified generalizations in the Ruu Engineering project; the affected transitions remain locally blocked.
