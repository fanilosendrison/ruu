# Ruu — Package Verification through ADR-079

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-079
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v44.md` / **16,124 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.50–30.54 closed; only 30.55 open

## Integrated decision

ADR-079 closes backlog 30.54 with four coupled rules:

```text
minimal rejection
→ only unresolved correctness-critical cessation/replacement candidates fail closed

ManagedRefProtectionFilter
→ repository-common conservative negative acceleration
→ never binding-generation/CURRENT authority
→ degraded filter falls back to authoritative state

RefAdmissionBarrier
→ exact candidate-ref preimage under native exclusion
→ binding CURRENT published while barrier held

initial authoring handoff
→ exact worktree topology revalidated
→ producer receives authority only after protected admission completes
```

PREPARED is the pre-linearization durability boundary. Post-PREPARED outcome persistence is recoverable; wakeup/log/telemetry failure is advisory. Coverage gaps, filter degradation and successfully vetoed persistence failure are distinct states.

## Retained finite-model regressions

```text
state-space-audit-v43.py: 15,868 PASS
```

ADR-078 zero-preflight product semantics remain unchanged.

## New finite-model regression

`state-space-audit-v44.py` adds 256 ADR-079 combinations:

```text
ADR-079 minimal-rejection family: 32 PASS
ADR-079 protection-filter family: 32 PASS
ADR-079 preparation-batch family: 32 PASS
ADR-079 outcome-advisory family: 32 PASS
ADR-079 ref-admission family: 32 PASS
ADR-079 admission-crash family: 32 PASS
ADR-079 initial-handoff family: 32 PASS
ADR-079 lock-order family: 16 PASS
ADR-079 failure-classification family: 16 PASS
new combinations: 256 PASS
retained v43 baseline: 15868
v44 total: 16124 PASS
```

## Native Git regression

`git-native-observation-smoke-v5.sh` reruns the ADR-077 v4 regressions and demonstrates the new Git-core/files admission assumptions on Git 2.47.3:

```text
retained_v4_regressions: PASS
existing_ref_noop_admission_barrier: PASS
absent_ref_admission_barrier: PASS
worktree_lock_is_not_authoring_topology_fence: PASS
git-native observation smoke v5: PASS
```

The existing-ref smoke holds a prepared exact `X → X` ref transaction, proves a concurrent mutation fails while the barrier is held, aborts the barrier, and proves the ref remains unchanged. The absent-ref smoke verifies/locks an absent ref under a prepared transaction and proves concurrent creation fails. The worktree smoke proves administrative worktree locking does not freeze HEAD, validating the separate authority-handoff invariant.

## Static package checks

Required final checks:

```text
ADR numeric continuity 001..079
RUU-SPEC.md == ruu-requirements-v1-merge-policy.md byte-for-byte
30.54 CLOSED by ADR-079
30.55 remains OPEN
ADR-079/Spec/ECP agree that the protection filter is non-authoritative
ADR-079/Spec/ECP agree that binding publication occurs while RefAdmissionBarrier is held
ADR-079/Spec/ECP distinguish binding CURRENT from producer write authorization
Markdown fence parity
state-space v43 retained PASS
state-space v44 PASS
Git native observation smoke v5 PASS
MANIFEST.sha256 regenerated after final content freeze
ZIP extraction + manifest verification PASS
```

## Verdict

**PASS.** Final package verification includes a regenerated 175-entry SHA-256 manifest, ZIP integrity check, clean re-extraction, manifest verification, spec-alias equality, ADR-001..079 continuity, state-space v44 PASS, and Git native observation smoke v5 PASS. 30.55 is the next and only remaining native-observation subproblem before closing umbrella 30.49.
