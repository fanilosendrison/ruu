# Ruu — Package Verification through ADR-078

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-078
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v43.md` / **15,868 combinations**
- **Current open observation cluster:** 30.49 umbrella; 30.50–30.53 closed; 30.54–30.55 open

## Integrated decision

ADR-078 strengthens the governing product intent:

```text
one-time install (including any installation-time supported-harness adapter registration)
→ launch supported coding harness
→ tell agent what to implement
→ automatic pre-edit CU/worktree/ref/observer/binding plumbing
→ agent authors normally
→ user or agent invokes `ruu` when a checkpoint is desired
```

The ordinary supported-harness path requires no explicit `start`, `create-cu`, `provision`, `init/register`, per-repository observer-install workflow, internal-ID reconstruction, or separately operated control-plane product.

ADR-023 remains a strict phase/authority separation: required isolation/observer state still exists before first managed write and cannot be retroactively created by the later convergence invocation. ADR-039's External Control Plane remains a semantic authority role; a Ruu-supplied harness adapter may implement its runtime/provisioning mechanics without moving semantic authority into the convergence engine.

## Retained technical regressions

The prior current regressions were rerun unchanged after ADR-078 integration:

```text
state-space-audit-v42.py: 15,740 PASS
git-native-observation-smoke-v4.sh on Git 2.47.3: PASS
  retained_v3_regressions: PASS
  linked_worktree_common_hook_visible: PASS
  functional_attestation_veto_effective: PASS
  foreign_core_hookspath_detected_without_takeover: PASS
```

ADR-078 changes product/phase packaging semantics, not the ADR-077 native-observer behavior.

## Finite state-space status

`state-space-audit-v43.py` adds 128 product-boundary combinations:

```text
ADR-078 zero-preflight-supported-harness family: 16 PASS
ADR-078 pre-edit-safety-timing family: 16 PASS
ADR-078 authority-vs-packaging family: 16 PASS
ADR-078 checkpoint-simplicity family: 16 PASS
ADR-078 lazy-multi-repo-first-touch family: 32 PASS
ADR-078 admin-vs-ordinary-interface family: 32 PASS
new combinations: 128 PASS
retained v42 baseline: 15740
v43 total: 15868 PASS
```

## Static package checks

Required final checks:

```text
ADR numeric continuity 001..078
RUU-SPEC.md == ruu-requirements-v1-merge-policy.md byte-for-byte
Product intent contains zero-preflight supported-harness contract
ADR-023 explicitly distinguishes phase separation from product separation
ADR-039/ECP explicitly permit Ruu-supplied harness integration while preserving authority
30.54/30.55 remain OPEN
README current pointers through ADR-078
Markdown fence parity
state-space v42 retained PASS
state-space v43 PASS
Git native observation smoke v4 retained PASS
MANIFEST.sha256 regenerated after final content freeze
ZIP extraction + manifest verification PASS
```

## Verdict

**PASS**, with 30.54 and 30.55 remaining the next open observation-plane decisions under umbrella 30.49.
