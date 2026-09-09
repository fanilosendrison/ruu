# Hostile Audit — ADR-079 minimal rejection, protection filtering, and exact binding admission

- **Date:** 2026-09-08
- **Target:** ADR-079 / backlog 30.54
- **Verdict:** **PASS**
- **Remaining observation backlog:** 30.49 umbrella with only 30.55 open

## Attack surface tested

### 1. CoordinationStore outage must not make every Git ref transaction fail

Attack: observer cannot reach authoritative managed state while an ordinary ref/tip update occurs.

Resolution: the adapter first derives cessation/replacement candidates. No candidate means immediate allow/exact-state rediscovery. A trustworthy negative `ManagedRefProtectionFilter` result also permits a candidate without authoritative lookup. Only unresolved candidate safety fails closed.

**PASS.** Failure domain is narrower than repository-wide Git availability.

### 2. Protection filter must not become a second binding database

Attack: cache stores `binding_generation/CURRENT` and diverges from SQLite, allowing a stale generation to authorize a native deletion.

Resolution: filter semantics are strictly conservative `ABSENT proven safe / PRESENT maybe relevant`; authoritative CU/work-occurrence/generation/currentness remains in the CoordinationStore.

**PASS.** No second semantic authority introduced.

### 3. Missing/corrupt filter accidentally treated as empty

Attack: delete/corrupt the local filter so every candidate appears absent and managed refs fail open.

Resolution: negative answers require trusted repository/profile/generation/integrity. Missing/corrupt/untrusted disables negative acceleration and falls back to authoritative classification.

**PASS.** No false-negative-by-missing-file path.

### 4. Filter outage mislabeled as observer coverage gap

Attack: filter repair closes/reopens coverage epochs unnecessarily or incorrectly claims missed causal history.

Resolution: observer reached + filter degraded remains coverage ACTIVE. Actual bypass/non-invocation is a distinct coverage gap. Successfully vetoed persistence failure likewise proves interception worked.

**PASS.** Failure taxonomy is causal rather than component-name based.

### 5. Partial preparation of a multi-binding Git transaction

Attack: one native transaction affects several current bindings but only some preparation rows commit; Git is still allowed.

Resolution: complete required `NativeBindingPreparation` set is one permission batch. Partial persistence never permits the transaction.

**PASS.** Native atomicity is not semantically split.

### 6. Lost final callback after durable PREPARED

Attack: Git commits but `committed` callback/persistence is lost; system waits forever or attempts rollback.

Resolution: PREPARED is the pre-linearization durability boundary. Final outcome delivery is replayable/recoverable from exact state and trustworthy coverage; no retroactive veto/rollback authority exists.

**PASS.** Compatible with Git hook lifecycle and ADR-076 recovery semantics.

### 7. Hook-caused veto depends on a guaranteed later `aborted` callback

Attack: observer vetoes then waits for `aborted` cleanup that Git need not deliver when the hook itself caused the abort.

Resolution: architecture never requires that callback. Durable PREPARED may remain unresolved and later reconcile/abort by evidence.

**PASS.** No impossible callback guarantee.

### 8. Admission race: native transaction passes observer while ref is unmanaged, commits after binding becomes CURRENT

Attack:

```text
T1 sees foo unmanaged and passes observer
T2 publishes foo as managed
T1 commits deletion/rename
```

Resolution: binding publication occurs while a `RefAdmissionBarrier` verifies exact preimage under native exclusion. Release-before-publication is forbidden.

**PASS.** Managed-state transition has a native serialization boundary.

### 9. Barrier creates its own false abandonment event

Attack: using Git plumbing to acquire ref exclusion appears to the observer as deletion.

Resolution: current Git-core/files candidate uses exact no-op `old_oid == new_oid` for existing refs; no-op updates are normatively semantically empty. Concrete smoke proves hook sees the no-op and concurrent mutation fails while prepared.

**PASS.** Barrier does not manufacture managed disposition.

### 10. Ref does not exist yet

Attack: admission requires locking a future ref, creating an unprotected race during creation.

Resolution: current Git also supports exact absence verification under prepared transaction, demonstrated by smoke. Ordinary V1 path is simpler: create candidate branch/worktree first while still unmanaged/unhanded-off, then admit the existing exact ref under barrier.

**PASS.** No durable `CURRENT but ref unborn` state required.

### 11. Direct backend `.lock` emulation leaks backend assumptions

Attack: avoid hook-visible no-op by directly manipulating files/reftable locks.

Resolution: rejected. `RefAdmissionBarrier` is adapter capability and current implementation uses supported Git transaction plumbing rather than taking ownership of backend-private lock formats.

**PASS.** ADR-075/077 capability boundary preserved.

### 12. `git worktree lock` falsely assumed to freeze authoring topology

Attack: candidate worktree is `--lock`ed, then a conforming/foreign process switches/detaches HEAD before handoff.

Concrete smoke on Git 2.47.3 proves a locked worktree can detach HEAD.

Resolution: worktree lock is defense-in-depth only. Provisioning retains exclusive pre-handoff mutation authority and revalidates repository/worktree/path/HEAD/ref/OID before current-binding publication/handoff.

**PASS.** Correctness does not rely on an invalid Git-lock assumption.

### 13. Binding CURRENT confused with producer write authorization

Attack: producer begins writing immediately when binding row commits while provisioning is still completing/releasing barrier.

Resolution: `binding CURRENT != producer authorized to write`. Initial authoring-authority handoff is a separate boundary after exact topology and barrier release.

**PASS.** First managed write remains after all pre-edit guarantees.

### 14. Deadlock by lock-order inversion

Attack:

```text
observer: Git lock → waits SQLite
provisioner: SQLite live lock → waits Git lock
```

Resolution: normative order is `Git/native exclusion → short CoordinationStore transaction`; inverse live-lock acquisition is forbidden. Durable claims without live locks remain allowed.

**PASS.** No architecture-sanctioned cycle.

### 15. Product intent regression through visible preflight

Attack: safe filter/barrier/handoff machinery becomes user commands (`init`, `protect`, `start`, `provision`).

Resolution: ADR-078 remains governing. The entire admission sequence is automatic supported-harness pre-edit plumbing.

**PASS.** Stronger safety does not re-export orchestration to the user.

## Residual risk intentionally accepted

- A stale positive protection-filter entry may cause an unnecessary authoritative lookup or, during simultaneous filter+authority outage, a conservative veto.
- A composed third-party `reference-transaction` observer may see the Git-core no-op admission transaction. Avoiding all such visibility by emulating backend-private locks was judged more invasive and fragile.
- An arbitrary filesystem/ref-store writer outside the admitted mutation-engine contract can still bypass Git-native exclusion; ADR-077 treats resulting managed-state drift as an integrity violation rather than pretending universal OS-level enforcement.

None of these residual risks invalidates the ADR-079 correctness contract.

## Verdict

**PASS.** 30.54 is closed. The minimal fail-closed set, degraded-filter behavior, preparation durability boundary, exact native binding admission, initial worktree handoff, and lock ordering are mutually coherent with ADR-042/064/073/075/076/077/078.
