# Ruu — Package Verification through ADR-068

- **Date:** 2026-09-07
- **Baseline:** ADR-067 verified package
- **Current architecture:** ADR-001..ADR-068
- **Current finite audit:** `STATE-SPACE-AUDIT-v36.md`

## Integrated decision

```text
ADR-068
→ ordinary authoring branch/ref/worktree deletion remains semantically neutral
→ still-unrealized PromotionGroup may terminally settle as CANCELLED
→ cancellation requires explicit current External Control Plane authority
→ zero realized + zero unresolved still-realizing group effects required
→ realized partial effects remain ADR-055 settlement, never cancellation
→ membership change = cancel old immutable group + declare new immutable group
→ ConvergenceUnit ABANDONING gated by higher-level terminal disposition
```

Backlog 30.41 was closed at ADR-068 verification time. A subsequent hostile falsification pass opened backlog items 30.42–30.48. Those later findings are unresolved backlog entries and do not retroactively change the ADR-068 verification result.

## Executable verification

`state-space-audit-v36.py`:

```text
14,818 finite combinations: PASS
ADR numbering 001..068: PASS
current-doc static checks: PASS
Markdown fence balance: PASS
```

Concrete mechanics:

```text
ADR-048 materialization: PASS
ADR-050 restack: PASS
DIRECT target advancement: PASS
repository bootstrap: PASS
canonical checkpoint: PASS
provider-route C→H→R→O: PASS
ordinary branch deletion / managed checkpoint neutrality: PASS
```

All packaged shell scripts pass `bash -n` syntax validation. All packaged Python audit/smoke files pass Python bytecode compilation.

## Important interpretation

The branch-deletion rule does **not** prevent or redirect normal Git usage. It states the opposite: deleting an ordinary branch is not a hidden lifecycle/cancellation command. `ruu` reconciles durable exact managed state above those ordinary artifacts.

`CANCELLED` is historical terminal disposition of one managed PromotionGroup, not a permanent prohibition on future Git history containing the same or overlapping content.

`PASS` means the package is internally consistent for the semantics it currently specifies and the explicit finite families tested. It is not a proof over arbitrary future provider/Git behavior or future architecture changes.


## H4 ratification / verification revision

The original hostile-audit H4 decision is explicitly ratified without a redundant ADR: `PromotionUnit PROMOTED` remains a terminal historical completion fact after later target drift. State-space audit v36 adds 12 explicit combinations and raises current finite coverage from 14,806 to 14,818 combinations. The seven concrete Git primitive smokes remain unchanged and are rerun.


## Post-verification hostile backlog note

After this verification artifact was produced, a hostile falsification pass identified unresolved items 30.42–30.48 in `OPEN-DESIGN-BACKLOG.md`: PromotionGroup occurrence identity, terminal resolution freezing, semantic disposition causal fencing, cancellation linearization against ordinary Git progress, run-lock descriptor inheritance, Development-System-independent ingress, and corresponding state-space coverage. No new ADR semantics are ratified by that backlog-only update.

## Packaging / navigation revision

The consolidated specification is now exposed at the human-facing root filename `RUU-SPEC.md`. The historical filename `ruu-requirements-v1-merge-policy.md` is retained byte-for-byte identically for compatibility with packaged audit scripts. `README.md` identifies the intended reading order. This packaging-only change does not alter ratified semantics.
