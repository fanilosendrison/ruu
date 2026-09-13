---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Minimize native Git rejection with conservative protection filtering and exact binding admission"
id: "ADR-079"
status: "accepted"
date: "2026-09-08"
decision_body_sha256: "449fb5b6992e6a711ba1fad8e5ba4dfb21f87b481e7b71b53c29e64cdfbb0c23"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-023"
    - "ADR-039"
    - "ADR-042"
    - "ADR-064"
    - "ADR-073"
    - "ADR-074"
    - "ADR-075"
    - "ADR-076"
    - "ADR-077"
    - "ADR-078"
  supersedes: []
  confirms: []
governs: []
---

# ADR-079 — Minimize native Git rejection with conservative protection filtering and exact binding admission

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.54
- **Amends:** ADR-023, ADR-039, ADR-042, ADR-064, ADR-073, ADR-074, ADR-075, ADR-076, ADR-077, ADR-078, the consolidated specification, the External Control Plane contract, and the observation backlog
- **Leaves open:** backlog 30.49 umbrella and 30.55

## Context

ADR-074 minimizes local event semantics to disposition of the currently bound managed authoring ref. ADR-075 requires a vetoable/equivalently serialized pre-linearization witness for every native mutation capable of ending/replacing that binding. ADR-076 makes the resulting preparation durable/replayable without pretending observation delivery is exactly once. ADR-077 requires attested repository-common coverage for the admitted native mutation path. ADR-078 requires all of that pre-edit plumbing to remain invisible behind supported coding-harness integration.

30.54 decides what happens when observation/persistence infrastructure is unhealthy. Two failures must be avoided simultaneously:

1. **fail-open correctness loss:** allowing a managed binding to terminate/replace when its required causal preparation could not be durably established; and
2. **over-broad Git fragility:** rejecting unrelated ordinary Git operations merely because optional telemetry, wakeups, a local acceleration structure, or even the managed CoordinationStore is unavailable.

The review also exposed a race at initial managed-binding admission. A native transaction may begin while a candidate ref is still ordinary/unmanaged, pass the observer on that basis, and commit only after the ref is declared managed unless admission is itself serialized with native ref mutation. The same initial handoff must establish exact worktree topology and exclusive authoring authority before the first managed write.

## Decision

### 1. Rejection is limited to the smallest correctness-critical pre-linearization class

For each admitted native ref transaction `T`, the adapter first derives a backend-normalized set of **cessation/replacement candidates**: ref effects capable of deleting, replacing, force-overwriting, or causally carrying away a ref name that might currently be a managed authoring binding.

If `T` contains no such candidate:

```text
CessationCandidateSet(T) = ∅
→ ALLOW
```

No durable local event record is required merely because ordinary authoring tips, tags, unrelated refs, worktree state, or other state-observed facts changed. They remain exact-state rediscovery under ADR-074/075.

For a candidate that is proven to affect a **current managed binding**, the complete correctness-critical `NativeBindingPreparation` batch required for the native transaction MUST be durably committed before the adapter permits the native transaction to linearize.

```text
all required preparations crash-durable
→ ALLOW

classification/authority/persistence remains unknown
→ bounded retry if useful
→ VETO native transaction
```

A timeout/retry-budget exhaustion never silently converts this class to fail-open.

If one atomic native ref transaction affects several current managed bindings, its required preparation set is all-or-nothing for permission purposes. Partial preparation persistence does not authorize partial semantic coverage of an otherwise atomic native transaction.

### 2. Outcome persistence after a durable preparation is recoverable and never a reason to retroactively reject Git

Once the required `PREPARED` evidence is durably committed and the native transaction is permitted, later recording of `COMMITTED | ABORTED` is not itself a precondition for Git correctness.

```text
PREPARED durable
+ committed/aborted callback lost, duplicated, reordered, or persistence fails
→ do not veto/rollback Git
→ retain PREPARED/UNRESOLVED
→ reconcile from exact state + trustworthy coverage + adapter evidence
```

This is required because a veto-capable hook phase precedes linearization, while post-commit/post-abort callbacks cannot in general undo a transaction and Git may omit an `aborted` callback when the hook itself caused the veto.

The architecture therefore never depends on a guaranteed final callback for cleanup or exactly-once settlement.

### 3. Wakeups, logs, telemetry and diagnostics are advisory

Failure to persist or deliver:

```text
wakeups
metrics
traces
logs
non-authoritative diagnostics
```

MUST NOT reject a native Git transaction. They may be lost/coalesced/replayed according to their own delivery contract. A later explicit `ruu`, global demand, or exact-state sweep restores progress without manufacturing missing causal history.

### 4. A repository-common `ManagedRefProtectionFilter` narrows authority lookups without becoming managed truth

A conforming observer MAY/SHOULD maintain a repository-common, local, conservative acceleration structure conceptually named:

```text
ManagedRefProtectionFilter
```

Its only normative question is:

```text
trustworthy ABSENT
→ this ref is proven outside the protected candidate set for this filter generation

PRESENT
→ this ref MAY require managed protection; consult authoritative managed state
```

The filter MUST NOT be the authority for:

```text
ContributionUnit identity
work_occurrence identity
binding_generation
CURRENT/non-CURRENT status
semantic disposition
```

Those remain authoritative in the CoordinationStore.

False positives are safe and permitted. False negatives for safety-relevant refs are forbidden while the filter is trusted for negative answers.

### 5. Missing/corrupt/untrusted filter means degraded fast-path, not an observation coverage gap

A filter can be used for negative answers only when its repository identity, observer-binding/profile identity, format/generation and integrity are trustworthy. `missing`, `unreadable`, `corrupt`, `wrong repository`, `wrong generation`, or unknown format MUST NOT be interpreted as an empty filter.

If the observer is still reached but the filter is untrusted:

```text
ProtectionFilterHealth = DEGRADED
```

The observer disables negative fast-path decisions and consults authoritative managed state for every cessation/replacement candidate. This is **not** by itself a `coverage_epoch` gap because the pre-linearization observer path remains intact.

If both the filter is untrusted and the authoritative managed state required to classify a cessation candidate is unavailable, that candidate transaction is vetoed. Transactions with no cessation/replacement candidate remain allowed.

### 6. Filter growth is conservative; normal correctness never depends on eager removal

Before a ref can become a current managed binding, the filter is conservatively enlarged/published or the negative fast-path is durably disabled for the relevant domain. Before a native rename/rebind may carry a protected managed line to a successor ref name, that successor is likewise protected before permission to linearize.

Normal correctness MUST NOT require prompt removal of filter entries. A stale entry creates only a false positive/extra authority lookup.

Implementations MAY rebuild/compact the filter by first making negative answers unavailable/degraded, rebuilding from authoritative safety-relevant state, and atomically publishing a new trustworthy generation. Rebuild never bridges a native-observation coverage gap and never treats an incomplete reconstruction as trustworthy absence.

### 7. Initial managed binding admission requires a native `RefAdmissionBarrier`

Creating a branch/worktree during pre-edit provisioning does not yet make it managed. It is a **candidate authoring surface** and remains unavailable to the coding producer.

Before the candidate ref becomes a current managed binding, the selected backend/adapter MUST provide a `RefAdmissionBarrier` capability with the following property:

```text
exact candidate ref preimage is verified
under exclusion with every conforming native mutation of that ref
and that exclusion remains held
until authoritative binding publication is committed
```

The authoritative binding MUST become current **while the barrier is still held**. Releasing the barrier before binding publication is forbidden because a native transaction could otherwise pass the observer under the old unmanaged state and commit after admission.

The ordering is conceptually:

```text
candidate ref/worktree exists; no producer authoring authority yet
→ establish conservative filter protection (or degraded-safe mode)
→ acquire RefAdmissionBarrier at exact ref preimage
→ revalidate exact candidate worktree/ref topology
→ commit authoritative CURRENT binding while barrier is held
→ release barrier
→ perform initial authoring-authority handoff
→ first managed write may occur
```

Failure at any step before authoritative binding commit leaves no current managed binding. Failure after binding commit leaves a protected current binding even if producer handoff never completed; provisioning/recovery may later resume or retire that unused surface.

### 8. Git-core V1 may realize the admission barrier with a prepared exact no-op ref transaction

The architecture specifies the barrier capability, not a permanent command/backend implementation.

For the currently demonstrated Git-core/files profile, an existing candidate ref at exact OID `X` can be guarded by a ref transaction equivalent to:

```text
start
update refs/heads/<candidate> X X
prepare
... publish binding while ref transaction remains prepared ...
abort
```

The exact no-op `old == new` obtains/refuses the native ref lock under exact-preimage checking while planning no ref value change. The adapter MUST classify `old == new` as `NO_OP`, never as a cessation, rename, abandonment, or managed semantic event.

For an absent future ref, current Git-core behavior also supports exact absence verification under a prepared transaction (zero/absence preimage), but v1 ordinary ContributionUnit admission SHOULD prefer creating the candidate branch/worktree first and then admitting the existing exact ref. This avoids adding a durable "managed but ref not yet created" state.

A future backend/native API may implement the same barrier property differently without changing core semantics.

### 9. `RefAdmissionBarrier` is not implemented by taking ownership of backend internals

`ruu` MUST NOT satisfy the barrier contract by independently emulating undocumented `.lock` files, reftable internals, or other backend-private storage protocols merely to avoid normal Git transaction callbacks.

A native/public adapter primitive is preferred even if a no-op transaction is visible to other conforming `reference-transaction` observers. Other hooks may observe the no-op; Ruu's own observer must treat it as semantically empty.

### 10. Initial worktree handoff is an authority boundary, not a Git worktree-lock guarantee

`git worktree lock` may be used as defense-in-depth during provisioning, but it is not a correctness primitive for authoring topology: it does not freeze `HEAD` against ordinary checkout/switch operations.

Before initial handoff, the provisioning path retains exclusive mutation authority over the candidate surface. While the `RefAdmissionBarrier` is held, it revalidates at least:

```text
repository identity
worktree identity / registered path
expected symbolic HEAD/ref relationship
exact HEAD/ref OID
expected candidate ref
observer coverage/profile
```

After authoritative binding publication and barrier release, authoring authority is transferred to the supported harness/producer. No conforming coding producer may write the candidate worktree before that transfer.

Thus:

```text
binding CURRENT
!= producer already authorized to write
```

The interval between CURRENT publication and completed handoff is valid and recoverable. The first managed write is permitted only after exact initial topology has been established and the authority handoff completes.

### 11. Live lock ordering is Git/native exclusion before CoordinationStore, never the reverse

The normal critical observer path already holds native ref exclusion while persisting a managed preparation. Initial admission uses the same order:

```text
Git/native ref exclusion
→ short authoritative CoordinationStore transaction
```

No conforming path may hold a live CoordinationStore transaction/mutex/write lock while waiting to acquire a Git/native ref lock needed by the same protocol. Durable claims/rows that do not keep a live lock are not prohibited. This rule prevents lock inversion/deadlock between admission and native observation.

### 12. Coverage failure, filter degradation and persistence failure are distinct states

The system distinguishes:

```text
COVERAGE GAP
→ required native mutation did not traverse a trustworthy observer path
→ coverage epoch closes/breaks

PROTECTION_FILTER_DEGRADED
→ observer still intercepts mutations but negative acceleration cannot be trusted
→ fallback to authoritative classification

CRITICAL_PERSISTENCE_FAILURE
→ observer identified a current managed critical transition but cannot durably prepare it
→ veto the native transaction
```

A successfully vetoed persistence failure is evidence that coverage worked; it is not a coverage gap.

A repaired observer/filter never retroactively proves an earlier actual coverage gap. Final topology alone remains insufficient to invent a missing managed-binding causal history.

## Failure matrix

| Observation/persistence condition | Native Git consequence |
| --- | --- |
| No cessation/replacement candidate | allow; exact-state rediscovery later |
| Trustworthy filter proves candidate ref outside protected set | allow; no authoritative lookup required |
| Filter degraded but authoritative state proves no current managed binding | allow |
| Candidate affects current managed binding and complete preparation batch becomes durable | allow |
| Candidate may affect managed binding but authoritative classification unavailable | veto |
| Current managed binding identified but preparation classification/persistence unavailable | veto |
| Durable preparation exists; final outcome callback/persistence unavailable | allow; reconcile later |
| Wakeup/log/telemetry/diagnostic write unavailable | allow; advisory loss tolerated |
| Observer coverage itself absent/bypassed | integrity/coverage gap; do not reconstruct causal history from final topology |

## Consequences

### Positive

- Ordinary Git tip movement and unrelated ref operations remain largely independent of managed persistence health.
- Correctness-critical rejection is restricted to transitions that can actually terminate/replace a managed binding when protection cannot be proven.
- The protection filter improves availability without duplicating managed semantic authority.
- Initial managed admission is race-safe against already-in-flight/concurrent native ref transactions.
- Crash states bias toward harmless false positives or already-protected current bindings, never an admitted unprotected binding.
- The zero-preflight supported-harness Product Intent remains intact: all barriers/filter/handoff mechanics are internal pre-edit plumbing.

### Costs

- A historically protected ref name may incur an unnecessary CoordinationStore lookup while its filter generation remains conservative.
- When both negative filter evidence and authoritative managed state are unavailable, some ref deletion/rename transactions must fail closed even if they would ultimately prove unrelated.
- The Git-core no-op barrier is visible to composed `reference-transaction` participants; third-party hooks must tolerate semantically empty transactions according to their own contract.
- Provisioning requires exact lock ordering and initial authority handoff discipline.

## Rejected alternatives

### Reject every ref transaction whenever Ruu persistence is unhealthy

Rejected. This would make ordinary Git availability depend on unrelated managed telemetry/state and violate the minimal-rejection requirement.

### Fail open when the authoritative store is unavailable

Rejected. A candidate may be the current managed binding; allowing termination without a durable preparation would lose the exact causal distinction ADR-075 exists to preserve.

### Make a local safety store a second authoritative binding database

Rejected. Duplicating `binding_generation`/CURRENT authority creates split-brain and requires a distributed commit protocol between stores. The conservative filter intentionally contains less semantic information.

### Encode all managed refs in a reserved namespace

Rejected. Existing architecture intentionally keeps editing branch names natively meaningful/descriptive and does not use branch naming as managed identity/correctness.

### Remove protection entries eagerly

Rejected as a correctness dependency. Concurrent ref-name reuse can race cleanup. Stale conservative entries are cheaper and safer; compaction is an explicit degraded-safe rebuild operation.

### Publish the binding after releasing the ref barrier

Rejected. A native transaction could pass observation under the old unmanaged state and linearize after admission.

### Give the candidate worktree to the agent before admission completes

Rejected. First managed writes would occur before isolation/coverage/binding invariants are established and cannot be made safe retroactively.

### Treat `git worktree lock` as the authoring handoff fence

Rejected. It does not freeze the worktree's checked-out `HEAD`/branch against ordinary switch/checkout.

### Implement ref locking directly through backend-private `.lock`/reftable manipulation

Rejected. It would make Ruu a partial ref-backend implementation and undermine ADR-075/077 capability-based coexistence.

## Verification notes

Current Git documentation establishes that `reference-transaction` may veto in pre-linearization phases and that post-commit/post-abort exit status is not a rollback mechanism; the hook may also omit a later `aborted` callback when its own veto caused the abort. Current `git update-ref --stdin` documentation establishes that `prepare` locks all queued refs and `abort` releases prepared locks.

Concrete Git 2.47.3 smokes in this package retain ADR-075/077 behavior and additionally demonstrate:

- prepared exact no-op `X → X` admission locking on an existing ref;
- concurrent mutation rejection while that prepared barrier is held;
- exact absence verification/locking for a not-yet-existing ref;
- no-op hook visibility rather than a false managed deletion;
- a locked worktree can still switch/detach HEAD, proving worktree lock is defense-in-depth rather than the authoring authority fence.

These concrete behaviors support the current Git-core/files adapter profile; the normative architecture remains capability-based.
