# Hostile Audit — ADR-072

- **Date:** 2026-09-08
- **Target:** host run-lock lifetime vs subprocess inheritance
- **Verdict:** **PASS**

## Attacks exercised

### H1 — executor dies while long-lived child survives

Attack: parent owns the OS host run lock, spawns a long-lived child, then is killed abruptly.

Expected: the child does not inherit/retain the lock handle across exec; a successor executor can acquire the same host lock while the child is still alive. Concrete smoke: **PASS.**

### H2 — deep descendant chain through Git/hook/helper

Attack: executor launches Git, Git launches a hook, hook launches another process.

Expected: the run-lock handle is already closed at the first exec boundary, so deeper descendants cannot regain it by inheritance. **PASS by construction.**

### H3 — fallback sets CLOEXEC after open in a multithreaded runtime

Attack: another thread spawns a child between `open()` and `fcntl(FD_CLOEXEC)`.

Expected: unsafe unsynchronized fallback is non-conformant. ADR-072 requires atomic `O_CLOEXEC` when available or synchronization that makes the fallback race-free before any spawn. **PASS.**

### H4 — use heartbeat/TTL to repair inherited-lock liveness

Expected: rejected. The physical host fence remains OS-lifetime based; no timeout may revoke a live holder. **PASS.**

### H5 — child intentionally retains pre-exec fork state indefinitely

Expected: non-conformant. The fork-before-exec interval may be transient/bounded only; a helper cannot become a durable run-lock owner. **PASS.**

## Adversarial conclusion

ADR-072 restores the exact physical-lifetime premise ADR-042 already relied on:

```text
executor process death
→ no surviving descendant owns the run-lock handle
→ OS physical ownership becomes acquirable by a successor
```

No managed semantic state is changed.

**Verdict: PASS.**
