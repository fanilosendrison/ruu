# Ruu — Package Verification through ADR-074

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-074
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v39.md` / **15,140 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.51–30.55 open; 30.50 closed by ADR-074

## Integrated decision

ADR-074 corrects ADR-071's native managed-ref classifier and closes backlog 30.50.

```text
currently bound managed authoring ref old → zero
→ prepared: AUTHORING_BINDING_TRANSITION_PREPARED
→ abort: no disposition change
→ commit: disposition unresolved
   → proven rename/rebind → CONTINUATION
   → proven terminal delete → ABANDON
   → insufficient proof → recovery/fail-closed
```

Same OID/tree/ancestry, branch copy, or worktree HEAD switching is never continuity authority.

The minimal observation architecture is:

```text
STATE PLANE
EVENT PLANE: managed authoring-binding disposition only
OBSERVATION-INTEGRITY PLANE
```

Managed authoring refs have native reflogs provisioned before first managed write. Exceptional proof-loss recovery uses generation-bound ECP `AuthoringBindingRecovery`, always with independent exact Git revalidation.

`refs/replace/*`, `info/grafts`, and shallow boundaries are explicit correctness-relevant ancestry state.

## Concrete Git regression results

`git-native-observation-smoke-v2.sh`:

```text
git version: 2.47.3
native_rename_continuity: PASS
copy_then_delete_not_rename: PASS
prepared_failure_aborts_removal: PASS
ancestry_environment_detectable: PASS
reflog_baseline_supports_future_rename_evidence: PASS
git-native observation smoke v2: PASS
```

## Finite state-space status

`state-space-audit-v39.py`:

```text
ADR-074 binding-transition family: 72 PASS
ADR-074 recovery family: 36 PASS
ADR-074 observation-taxonomy family: 24 PASS
ADR-074 ancestry-environment family: 16 PASS
new combinations: 148 PASS
retained v38 baseline: 14992
v39 total: 15140 PASS
```

## Backlog status

```text
30.44 CLOSED — ADR-071
30.45 CLOSED — ADR-071, classifier corrected by ADR-074
30.46 CLOSED — ADR-072
30.47 CLOSED — ADR-073
30.48 CLOSED — verification item; v39 supersedes old direct-deletion classifier
30.49 OPEN   — native Git observation plane umbrella
30.50 CLOSED — ADR-074 minimal correctness-relevant observation set
30.51 OPEN   — transactional capture vs exact-state rediscovery
30.52 OPEN   — provenance / replay / idempotency
30.53 OPEN   — hook ownership / installation / coexistence / coverage
30.54 OPEN   — observation persistence failure semantics / coverage-gap handling
30.55 OPEN   — local native-Git / remote-provider boundary
```

## Static/package checks

The final packaging pass must verify:

```text
ADR numbering 001..074 exactly once
spec / legacy alias byte equality
Markdown fence balance
Python audit compilation + execution
shell syntax + concrete native-Git smoke execution
current docs contain no direct managed-old-ref-delete == abandonment shortcut
ADR-074/ECP reflog + generation-bound recovery anchors present
30.50 closed; 30.51–30.55 open
v39 finite audit PASS / 15,140
manifest generated after all content is frozen
```

## Final static pass results

```text
ADR count / numbering 001..074: PASS
Markdown fence balance: PASS
spec / legacy alias byte equality: PASS
ADR-074 binding-transition anchor: PASS
ADR-074 generation-bound recovery anchor: PASS
ECP reflog pre-write requirement: PASS
Python compile + v39 execution: PASS
shell syntax + five concrete Git smokes: PASS
current-doc stale direct-delete classifier scan: PASS (no hits)
30.50 CLOSED / 30.51–30.55 OPEN: PASS
```

## Verdict

**VERIFIED / PASS.**
