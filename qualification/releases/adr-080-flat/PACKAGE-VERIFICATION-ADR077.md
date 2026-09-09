# Ruu — Package Verification through ADR-077

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-077
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v42.md` / **15,740 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.50 closed by ADR-074; 30.51 closed by ADR-075; 30.52 closed by ADR-076; 30.53 closed by ADR-077; 30.54–30.55 open

## Integrated decision

ADR-077 closes backlog 30.53.

```text
live managed authoring
→ repository-common NativeObservationCoverage
→ admitted mutation-engine/adapter profile
→ functional attestation ACTIVE before first managed write

observer ownership
→ exact Ruu registrations only
→ expected-state/CAS install/upgrade/remove
→ no foreign core.hooksPath / hook / dispatcher takeover

V1 ordinary native ref mutation
→ Git core conforming path

alternative/direct writer bypass
→ no implicit managed semantics
→ unwitnessed managed-binding change = integrity failure

coverage repair
→ new coverage epoch
→ never retroactively bless a gap
```

Git 2.54+ configured multiple hooks are recorded as a preferred composition implementation profile, not a universal V1 version minimum. The architecture remains capability-based.

## Official Git documentation cross-check

Checked against current official Git documentation/release notes during ADR-077 integration:

- `reference-transaction` is invoked by Git commands performing reference updates and currently documents `preparing | prepared | committed | aborted` phases;
- Git 2.54 release notes introduce configured hook commands with multiple hooks for one event and the earlier `reference-transaction preparing` phase;
- Git 2.54 `git hook` documentation states configured hooks are discovered from config and the traditional hookdir hook is run as well;
- linked worktrees share ordinary `refs/*`, use `$GIT_COMMON_DIR`, and repository layout documents common hookdir resolution.

These facts inform available adapter/installation profiles; normative conformance remains property-based.

## Concrete Git regression status

`git-native-observation-smoke-v4.sh` on the package runtime Git 2.47.3/files retains all ADR-075 regressions and adds 30.53-specific checks:

```text
retained_v3_regressions: PASS
linked_worktree_common_hook_visible: PASS
functional_attestation_veto_effective: PASS
foreign_core_hookspath_detected_without_takeover: PASS
git-native observation smoke v4: PASS
```

The retained v3 suite still includes:

```text
files_rename_carry_prepared: PASS
files_terminal_removal_prepared: PASS
files_force_rename_two_bindings: PASS
prelinearization_veto_effective: PASS
reftable_delete_callback_visible: PASS
reftable_rename_bypass_detected: PASS
reftable_force_rename_bypass_detected: PASS
```

Configured multi-hook Git 2.54+ behavior is documentation-grounded in this package but not claimed as locally runtime-smoked by the Git 2.47.3 test binary.

## Finite state-space status

`state-space-audit-v42.py`:

```text
ADR-077 repository-common-coverage family: 16 PASS
ADR-077 ownership-composition family: 20 PASS
ADR-077 admission-attestation family: 12 PASS
ADR-077 mutation-engine-boundary family: 20 PASS
ADR-077 unwitnessed-recovery family: 16 PASS
ADR-077 coverage-epoch family: 24 PASS
ADR-077 recreation-reattestation family: 16 PASS
ADR-077 owned-install-CAS family: 12 PASS
ADR-077 hook-order-persistence family: 16 PASS
new combinations: 152 PASS
retained v41 baseline: 15588
v42 total: 15740 PASS
```

## Static package checks

Required final checks for the generated package:

```text
ADR numeric continuity 001..077
RUU-SPEC.md == ruu-requirements-v1-merge-policy.md byte-for-byte
30.53 current marker CLOSED BY ADR-077
30.54/30.55 remain OPEN
README current pointers through ADR-077
Markdown fence parity
state-space v42 executable PASS
Git native observation smoke v4 PASS
MANIFEST.sha256 regenerated after final content freeze
ZIP extraction + manifest verification PASS
```

## Verdict

**PASS**, subject only to the explicitly open architectural items 30.54 and 30.55 under umbrella 30.49.
