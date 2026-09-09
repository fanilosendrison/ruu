# Ruu — Package Verification through ADR-076

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-076
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v41.md` / **15,588 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.50 closed by ADR-074; 30.51 closed by ADR-075; 30.52 closed by ADR-076; 30.53–30.55 open

## Integrated decision

ADR-076 closes backlog 30.52.

```text
managed intent
→ Operation → Attempt → Observation → Adoption

native causal fact
→ NativeRefWitness / generation-bound preparation

native witness
≠ Operation

optional originating_attempt_id
→ correlation only
→ never authorization

observation/wakeup delivery
→ may duplicate/replay; noncritical signals may be lost

authoritative managed transition
→ exactly-once per operation_id / current binding_generation under CAS
```

A current-state scan may resolve an existing durable preparation or an existing managed Operation, but may never invent historical native causal preparation from final topology alone.

The ADR-075 adapter contract is refined with active-occurrence correlation sufficient to make duplicate in-flight delivery idempotent. No global permanent Git transaction identifier is required by core semantics.

## Concrete Git regression status

ADR-076 adds no new Git-behavior assumption beyond ADR-075. The retained `git-native-observation-smoke-v3.sh` remains the concrete backend/capture regression and is re-run unchanged:

```text
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

`state-space-audit-v41.py`:

```text
ADR-076 witness-vs-operation family: 16 PASS
ADR-076 non-authoritative-provenance family: 16 PASS
ADR-076 active-occurrence-idempotency family: 16 PASS
ADR-076 outcome-replay-recovery family: 48 PASS
ADR-076 scan-nonmanufacture family: 36 PASS
ADR-076 wakeup-coalescing family: 16 PASS
ADR-076 logical-exactly-once family: 16 PASS
new combinations: 164 PASS
retained v40 baseline: 15424
v41 total: 15588 PASS
```

## Backlog status

```text
30.49 OPEN   — native Git observation plane umbrella
30.50 CLOSED — ADR-074 minimal correctness-relevant observation set
30.51 CLOSED — ADR-075 capture strength / backend capability / positive proofs
30.52 CLOSED — ADR-076 provenance / replay / semantic idempotency
30.53 OPEN   — observer ownership / installation / coexistence / continuous coverage
30.54 OPEN   — observation persistence failure semantics / coverage-gap handling
30.55 OPEN   — local native-Git / remote-provider boundary
```

## Required final static/package checks

```text
ADR numbering 001..076 exactly once
spec / legacy alias byte equality
Markdown fence balance
Python audit compilation + v41 execution
shell syntax + retained concrete native-Git v3 smoke execution
current normative docs do not equate native witness with managed Operation
current normative docs do not use actor identity as native correctness authority
current normative docs do not allow scans to manufacture causal preparation
30.50/30.51/30.52 closed; 30.53–30.55 open
v41 finite audit PASS / 15,588
manifest generated after all content is frozen
```

## Verdict

Final verdict is recorded after the package-wide static, executable and manifest pass.

## Final static/executable pass results

```text
ADR count / numbering 001..076: PASS
Markdown fence balance: PASS
spec / legacy alias byte equality: PASS
ADR-076 normative anchors + invariants 181..185 exactly once: PASS
30.52 CLOSED; 30.53–30.55 OPEN current markers: PASS
current normative stale 30.52-open scan: PASS
Python compile for v39/v40/v41: PASS
retained v40 execution: 15,424 PASS
v41 execution: 15,588 PASS
shell syntax for native-observation smokes: PASS
retained concrete Git v3 smoke on Git 2.47.3: PASS
files rename/delete/-M classification + pre-linearization veto: PASS
reftable delete callback visibility + rename/-M bypass detection: PASS
```

The targeted current-normative scan finds only the required **negative guards**: native witnesses do not manufacture Operations, Attempt provenance is non-authoritative, and scans may not synthesize missing causal preparation. Historical ADRs/audits/package-verification files intentionally retain the status and wording that were current when they were written.

## Final verdict

**VERIFIED / PASS.**
