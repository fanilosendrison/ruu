# Ruu — Package Verification through ADR-075

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-075
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v40.md` / **15,424 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.50 closed by ADR-074; 30.51 closed by ADR-075; 30.52–30.55 open

## Integrated decision

ADR-075 closes backlog 30.51.

```text
binding-ending/replacing native mutation
→ pre-linearization native-ref adapter witness
→ durable normalized witness
→ core derives:
     TERMINAL_REMOVAL_PREPARED
   | RENAME_CARRY_PREPARED
   | UNKNOWN

UNKNOWN
→ veto ambiguous managed mutation

TERMINAL_REMOVAL_PREPARED + committed outcome
→ ABANDON

RENAME_CARRY_PREPARED + committed outcome + successor continuity
→ CONTINUATION

!ContinuationProof
→ never automatically ABANDON
```

All other currently identified local Git observations are exact-state rediscovery. Additional notifications are best-effort only.

Backend admissibility is capability-based. The tested stock `files` path is a demonstrated candidate implementation. The tested stock Git 2.47.3 reftable `branch -m/-M` path is nonconforming for live managed authoring because those operations complete without the required `reference-transaction` callback in the tested implementation; future equivalent vetoable capability is automatically admissible.

## Concrete Git regression results

`git-native-observation-smoke-v3.sh`:

```text
git version: 2.47.3
retained_v2_regressions: PASS
files_rename_carry_prepared: PASS
files_terminal_removal_prepared: PASS
files_force_rename_two_bindings: PASS
prelinearization_veto_effective: PASS
reftable_delete_callback_visible: PASS
reftable_rename_bypass_detected: PASS
reftable_force_rename_bypass_detected: PASS
git-native observation smoke v3: PASS
```

## Finite state-space status

`state-space-audit-v40.py`:

```text
ADR-075 observation-strength family: 36 PASS
ADR-075 adapter/core preparation family: 96 PASS
ADR-075 positive-disposition-proof family: 54 PASS
ADR-075 backend-capability family: 64 PASS
ADR-075 reflog-baseline family: 18 PASS
ADR-075 canonical-ancestry family: 16 PASS
new combinations: 284 PASS
retained v39 baseline: 15140
v40 total: 15424 PASS
```

## Backlog status

```text
30.44 CLOSED — ADR-071
30.45 CLOSED — ADR-071, classifier/capture corrected by ADR-074/075
30.46 CLOSED — ADR-072
30.47 CLOSED — ADR-073
30.48 CLOSED — verification item; v40 retains/supersedes later classifier audits
30.49 OPEN   — native Git observation plane umbrella
30.50 CLOSED — ADR-074 minimal correctness-relevant observation set
30.51 CLOSED — ADR-075 capture strength / backend capability / positive proofs
30.52 OPEN   — provenance / replay / idempotency
30.53 OPEN   — observer ownership / installation / coexistence / continuous coverage
30.54 OPEN   — observation persistence failure semantics / coverage-gap handling
30.55 OPEN   — local native-Git / remote-provider boundary
```

## Required final static/package checks

```text
ADR numbering 001..075 exactly once
spec / legacy alias byte equality
Markdown fence balance
Python audit compilation + v40 execution
shell syntax + concrete native-Git v3 smoke execution
current normative docs contain no direct managed-delete == abandonment shortcut
current normative docs do not require a backend name as architecture
30.50/30.51 closed; 30.52–30.55 open
v40 finite audit PASS / 15,424
manifest generated after all content is frozen
```

## Final static pass results

```text
ADR count / numbering 001..075: PASS
Markdown fence balance: PASS
spec / legacy alias byte equality: PASS
ADR-075 normative anchors: PASS
current normative stale direct-delete classifier scan: PASS
30.50/30.51 CLOSED; 30.52–30.55 current: PASS
Python compile + v40 execution: PASS
shell syntax + concrete v3 Git smokes: PASS
files rename/delete/-M carrier classification: PASS
reftable delete callback visibility: PASS
reftable rename/-M coverage-gap detection: PASS
```

Historical ADRs/audits may intentionally quote the superseded `old→zero == abandonment` rule while documenting its falsification; the stale-classifier scan is therefore scoped to current normative surfaces (`RUU-SPEC.md`, `OPEN-DESIGN-BACKLOG.md`, and `EXTERNAL-CONTROL-PLANE-CONTRACT.md`).

## Verdict

**VERIFIED / PASS.**
