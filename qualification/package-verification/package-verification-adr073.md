# Ruu — Package Verification through ADR-073

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-073
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v38.md` / **14,992 combinations**
- **Current open design cluster:** 30.49–30.55 (30.49 umbrella; 30.50–30.55 distinct subproblems)

## Integrated decisions

### ADR-072 / backlog 30.46

The host OS run-lock handle is exclusively owned by the top-level executor process and is non-inheritable across subprocess execution boundaries.

```text
executor dies
+ child/helper survives
→ child cannot retain physical host fence
→ successor can acquire run lock
```

POSIX uses `O_CLOEXEC` where available or a race-safe `FD_CLOEXEC` fallback; other platforms use an equivalent non-inheritable handle. No heartbeat/TTL takeover is added.

### ADR-073 / backlog 30.47

V1 actively authored managed ContributionUnits use dedicated Git worktrees as the normative authoring isolation substrate.

```text
active v1 authoring
→ dedicated worktree/ref surface
→ frozen handoff
→ exact whole-surface capture
```

No direct v1 contract accepts arbitrary prebuilt commit/tree/snapshot inputs that bypass the managed worktree topology. Ordinary Git commits inside the managed worktree remain supported. Post-capture worktree disappearance does not erase durable identity/checkpoints. Future sandbox authoring requires a new ADR proving equivalent guarantees.

## Concrete run-lock regression

`git-run-lock-noninheritable-smoke-v1.sh` executes the required process-lifetime scenario:

```text
parent acquires host lock
→ spawn long-lived child
→ kill parent
→ child remains alive
→ successor acquires same lock
```

Result:

```text
successor acquisition with surviving child: PASS
run-lock non-inheritance smoke: PASS
```

## Finite state-space status

ADR-072 is subprocess-handle conformance/liveness hardening and ADR-073 fixes the v1 authoring substrate boundary. Neither introduces a new managed lifecycle transition dimension. Therefore the current finite state-space model remains v38 and is re-run unchanged as part of package verification rather than incremented merely for numbering.

Current finite audit:

```text
STATE-SPACE-AUDIT-v38: PASS
14,992 combinations
```

## Backlog status

```text
30.44 CLOSED — ADR-071
30.45 CLOSED — ADR-071
30.46 CLOSED — ADR-072
30.47 CLOSED — ADR-073
30.48 CLOSED — v38 verification
30.49 OPEN — native Git observation plane scope/invariant (umbrella)
30.50 OPEN — minimal correctness-relevant Git observation set
30.51 OPEN — transactional capture vs exact-state rediscovery
30.52 OPEN — provenance / replay / idempotency
30.53 OPEN — hook ownership / installation / coexistence
30.54 OPEN — observation persistence failure semantics
30.55 OPEN — local native-Git / remote-provider boundary
```

## Static/package checks

The final packaging pass verifies:

```text
ADR numbering 001..073
spec / legacy alias byte equality
Markdown fence balance
Python audit compilation
shell syntax
ADR-072 run-lock non-inheritance anchors
ADR-073 worktree-only-v1 anchors
backlog 30.46/30.47 closed
30.49–30.55 are the current open observation-plane cluster; 30.49 is umbrella and 30.50–30.55 are explicitly separated
run-lock long-lived-child smoke PASS
v38 finite audit remains PASS / 14,992
```

## Verdict

**VERIFIED / PASS.**
