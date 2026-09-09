# ADR-072 — Make host run-lock handles non-inheritable across subprocess boundaries

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.46
- **Amends:** ADR-042 and the consolidated specification

## Context

ADR-042 uses a process-lifetime OS exclusive lock to ensure that at most one top-level `ruu` executor is physically active in one host coordination domain. Its liveness model intentionally avoids heartbeat/TTL takeover:

```text
executor process alive
↔ OS run lock held

executor process dead
↔ OS run lock released
```

That equivalence is false if the run-lock file descriptor/handle is inherited by a spawned Git/provider/helper process. With `flock`-class/open-file-description locking, a surviving descendant that still owns the inherited descriptor can keep the lock busy after the actual `ruu` executor has died.

A realistic failure is:

```text
Ruu acquires host run lock
→ spawns git/provider/helper child
→ child inherits run-lock handle
→ Ruu crashes
→ child survives or hangs
→ host run lock remains BUSY
→ every later invocation believes an executor still owns the host
```

This violates ADR-042's physical-ownership/liveness model without requiring any semantic state-machine error.

## Decision

### 1. The host run-lock handle belongs only to the executor process

The OS run-lock descriptor/handle MUST be non-inheritable across every subprocess execution boundary.

A child process MUST NOT be capable of retaining the host executor fence after the owning `ruu` process has terminated.

Normative property:

```text
surviving descendant
+
owning Ruu executor dead
→ descendant cannot keep host run lock held
```

### 2. POSIX implementations use close-on-exec semantics

On POSIX, the preferred implementation is to create/open the lock descriptor atomically with `O_CLOEXEC` where available.

If the platform/API cannot set close-on-exec atomically at open time, the implementation MUST establish `FD_CLOEXEC` before any subprocess can be created that could inherit the descriptor. A multithreaded implementation MUST synchronize that fallback so no concurrent spawn can race between descriptor creation and non-inheritable marking.

The architecture requires the property, not a particular syscall spelling.

### 3. Non-POSIX platforms use an equivalent non-inheritable handle

On platforms where file descriptors/`O_CLOEXEC` are not the process-handle model, the run-lock handle MUST be created/configured as non-inheritable using the platform-equivalent mechanism.

The conformance requirement is portable:

```text
host run-lock ownership must not propagate into subprocesses
```

### 4. Every spawn path is covered

The guarantee applies to every subprocess launch path reachable from the top-level executor, including Git commands, provider helpers, credential helpers under executor control, and other child tools.

Implementations SHOULD centralize subprocess construction so this property is enforced once rather than relying on individual call sites.

Descendants launched by a Git child or hook are automatically outside the run-lock ownership chain once the first exec boundary has correctly closed the descriptor.

### 5. The bounded fork-before-exec interval does not redefine ownership

On fork/exec implementations a freshly forked child may transiently share the descriptor before `exec`. This launch interval MUST remain bounded and MUST NOT become a durable child ownership path.

The implementation MUST NOT intentionally keep a pre-exec helper alive while it retains the run-lock descriptor after the parent executor can terminate.

### 6. No lease/heartbeat workaround is introduced

This ADR does not add heartbeat expiry, TTL takeover, PID-file correctness, or a watchdog lease protocol.

ADR-042's stronger model remains:

```text
OS process/handle lifetime provides physical exclusion
+
SQLite run_generation + run_token provides durable adoption authority
```

ADR-072 only ensures subprocess inheritance cannot break the intended OS-lifetime equivalence.

## Conformance test

A v1 implementation MUST include a smoke equivalent to:

```text
1. executor parent acquires host run lock
2. parent launches a long-lived child
3. parent is killed abruptly
4. child remains alive
5. a new executor process attempts the same host run lock
6. new executor MUST acquire it successfully
```

A direct child-descriptor inspection test MAY additionally verify that the run-lock descriptor is absent after exec.

## Consequences

- Crashed executors cannot leave zombie host ownership through surviving helpers.
- ADR-042's no-heartbeat physical ownership model remains valid.
- Subprocess/hook depth does not multiply run-lock ownership.
- The requirement is a conformance/liveness hardening, not a new managed semantic state.
