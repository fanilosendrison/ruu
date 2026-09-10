# ADR-075 — Require pre-linearization native-ref witnesses only for managed authoring disposition; rediscover all other Git facts from exact state

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.51
- **Amends:** ADR-023, ADR-039, ADR-071, ADR-073, ADR-074, the consolidated specification, the External Control Plane contract, and the observation backlog
- **Leaves open:** backlog 30.49 umbrella and 30.52–30.55

## Context

ADR-074 closes the **what must be observed** question. It identifies one local Git business-event family whose occurrence cannot safely be reconstructed from final state alone: disposition of the currently bound managed authoring ref. All other currently identified local Git mutations remain state-observed.

30.51 must now decide **how strong each observation must be**.

The distinction is correctness-critical. A final ref state can reconstruct ordinary tip movement, target drift, internal-ref state, worktree topology, submission heads, and similar facts. It cannot prove that a managed authoring ref was never deleted and recreated, nor can a post-commit observation retroactively prevent a stale realization effect from crossing ADR-071's current-disposition fence.

Hostile Git testing also exposed two implementation traps:

1. on the historical `files` ref backend, a native branch rename may expose the source ref removal through `reference-transaction` while Git has already moved the source reflog into its backend-specific rename transport;
2. on the tested stock Git 2.47.3 `reftable` backend, native `git branch -m/-M` succeeds without any `reference-transaction` callback, including forced rename over an existing destination ref. Therefore `reference-transaction` support alone is not a sufficient backend capability contract.

The architecture must norm the required properties, not a particular ref backend or on-disk representation.

## Decision

### 1. Observation strength has exactly three semantic classes

Every retained 30.50 observation belongs to one of:

```text
TRANSACTIONAL / PRE-LINEARIZATION
→ loss could permit an otherwise-forbidden irreversible managed effect
→ a durable native witness is required before the Git mutation may linearize

EXACT-STATE REDISCOVERY
→ current authoritative Git/remote/provider state fully determines safe reconciliation
→ no durable event history is required

BEST-EFFORT SIGNAL
→ useful only to wake the reconciler or improve diagnostics/latency
→ loss may delay work but cannot change correctness
```

Hook availability never promotes a state fact into a business event.

### 2. Only managed authoring-binding cessation/replacement requires pre-linearization capture

For live managed authoring, any native mutation capable of making a currently bound managed authoring ref cease to be that binding — including terminal deletion, replacement, forced rename destination overwrite, or an equivalent backend operation — MUST satisfy the following property:

> **Before that mutation linearizes, a conforming native-ref adapter must expose a vetoable or equivalently causally serialized observation point from which Ruu can durably record a normalized witness for every affected currently bound managed authoring ref.**

A purely post-commit notification is not equivalent, because it cannot prevent a stale managed realization from racing through the current-disposition fence.

This requirement is semantic and capability-based. It does not mandate `reference-transaction`, the `files` backend, or any backend-specific filesystem layout.

### 3. The native-ref adapter reports Git/backend facts; the core derives managed semantics

Backend-specific state is translated into a normalized witness before being persisted. Conceptually:

```text
NormalizedNativeRefWitnessV1 {
  observation_contract_version
  adapter_capability_id
  adapter_version

  affected_ref
  exact_preimage_oid

  baseline_state =
      ENTRY_MATCH(anchor_entry_fingerprint)
    | EMPTY_PRESENT
    | NOT_PROVABLE

  native_relation =
      REMOVAL_SOURCE
    | RENAME_SOURCE
    | RENAME_DESTINATION_REPLACEMENT
    | OTHER_REPLACEMENT
    | UNKNOWN

  successor_ref?        // only when the adapter can prove it
}
```

The exact implementation schema may evolve compatibly, but the semantic separation is normative:

```text
backend-specific ephemeral evidence
→ native-ref adapter
→ normalized native witness
→ durable write
→ core classification
```

The adapter MUST NOT emit ContributionUnit lifecycle decisions, `ABANDON`, `CONTINUATION`, PromotionGroup state, or other managed business semantics.

The core combines the witness with current durable managed bindings and binding generation to derive:

```text
TERMINAL_REMOVAL_PREPARED
RENAME_CARRY_PREPARED
UNKNOWN
```

### 4. `UNKNOWN` before linearization is vetoed

For a mutation affecting a currently bound managed authoring ref:

```text
normalized witness sufficient for terminal removal
→ persist TERMINAL_REMOVAL_PREPARED
→ mutation may continue

normalized witness sufficient for native rename transport
→ persist RENAME_CARRY_PREPARED
→ mutation may continue

witness absent / contradictory / NOT_PROVABLE / UNKNOWN
→ do not let the ambiguous managed binding mutation silently linearize
```

The exact persistence-failure/retry UX remains under 30.54, but the correctness rule is fixed: an ambiguous correctness-critical managed binding mutation cannot be allowed to commit merely because later recovery may be difficult.

### 5. Terminal abandonment is a positive proof, not the complement of continuation

`ABANDON` requires a positive terminal-removal preparation plus committed outcome.

Conceptually:

```text
TerminalAbandonmentProofV1(T) =
  T is for the current binding generation N / ref R / exact preimage X
  AND durable preparation classification == TERMINAL_REMOVAL_PREPARED
  AND the corresponding native ref cessation/replacement committed
  AND no observation-integrity contradiction invalidates the preparation interval
```

Then:

```text
→ ABANDON
```

Therefore:

```text
!ContinuationProof
≠ ABANDON
```

A crash after source removal but during an incomplete rename remains `UNRESOLVED` unless terminal-removal preparation had already been positively established.

### 6. Automatic continuation is also a positive causal proof

A native rename preserves the same managed authoring occurrence only when the current binding generation is causally transported to a successor ref.

Conceptually:

```text
AutomaticContinuationProofV1(T, successor) =
  T belongs to current binding generation N / old_ref / preimage X
  AND durable preparation classification == RENAME_CARRY_PREPARED
  AND the old binding cessation committed
  AND the native adapter/recovery view proves the corresponding rename successor
  AND the rename point is exact-preimage compatible with X
  AND no COPY/CREATE boundary substitutes for rename
  AND no conflicting managed binding is silently overwritten
  AND current exact Git topology/state is revalidated
  AND required observation-integrity coverage remained trustworthy
```

Then:

```text
→ CONTINUATION
→ increment binding generation
→ bind successor ref
```

The successor ref may have advanced after the rename. Current successor OID equality with the old preimage is not required; exact current state is handled normally by the state plane.

A surviving worktree whose `HEAD` follows the successor is useful corroboration/topology evidence but is not required lineage identity. A stale/broken worktree after a causally proven rename is a topology-repair condition, not proof that the rename did not occur.

### 7. Managed reflog baseline is logical evidence, never an on-disk fingerprint

A managed authoring surface retains the ADR-074 native reflog requirement. The baseline is represented as:

```text
ReflogBaselineV1 =
    ENTRY(anchor_entry_fingerprint)
  | EMPTY_PRESENT
```

`anchor_entry_fingerprint` fingerprints one **logical reflog entry**, not a physical reflog file and not the entire reflog history. Physical `.git/logs/...` files, reftable files, ordinals such as `@{17}`, inode/path details, and backend update indexes are non-normative.

A conforming entry fingerprint is versioned and based on the backend-independent logical entry fields exposed by Git/ref APIs, at minimum:

```text
object format
old OID
new OID
committer identity
entry timestamp
entry timezone
normalized reflog message bytes
```

The current ref name is excluded from the entry fingerprint so the same historical entry remains identifiable after a native rename.

`EMPTY_PRESENT` means a reflog surface was positively present but contained no anchor entry. It is not equivalent to "reflog absent". A missing expected baseline during a correctness-critical transition is not retroactively repaired.

The baseline is evidence infrastructure for the current binding generation; it is not ContributionUnit identity and does not alone prove `RENAME` versus `COPY`.

### 8. Backend-specific rename carriers remain inside adapters

For the tested stock Git `files` backend, hostile testing demonstrated a conforming evidence path:

```text
terminal branch delete during prepared
→ managed baseline remains attached to old ref

native branch rename during prepared
→ managed baseline has entered Git's native rename transport
```

The current implementation detail may involve backend-specific temporary reflog state. Such paths/names MUST NOT appear in core semantics.

The normalized witness is the durable correctness record. An opaque hash of transient backend internals is not sufficient proof by itself.

Optional raw backend evidence/digests may be retained for audit/debugging, but core correctness MUST NOT depend on being able to reconstruct an expired temporary file/table representation later.

### 9. Backend admissibility is capability-based, not backend-name-based

A native ref backend/adapter is admissible for live managed authoring only if it proves all of:

```text
PRE_LINEARIZATION_COVERAGE
→ every native deletion/replacement/rename-overwrite capable of ending a current managed binding is observed before causal commit

VETO_OR_CAUSAL_SERIALIZATION
→ ambiguous or unpersistable managed-binding transitions cannot silently linearize

EXACT_PREIMAGE
→ the actual current ref/OID preimage can be established even when a hook/API exposes force semantics such as zero-valued old fields

RENAME_VS_TERMINAL_EVIDENCE
→ native rename transport can be distinguished from terminal removal without OID/ancestry guessing

DURABLE_NORMALIZED_WITNESS
→ enough backend-independent evidence is persisted before commit for crash recovery/audit

RECOVERY_CONSISTENCY
→ committed/aborted/lost-callback outcomes can be reconciled without inventing causal history
```

The contract names properties, not `files`, `reftable`, or any future backend.

### 10. Current backend conformance evidence

The package smoke suite demonstrates:

```text
stock Git 2.47.3 / files
→ native rename source removal is pre-commit observable
→ terminal delete is pre-commit observable
→ forced rename over existing destination exposes both affected ref removals
→ backend-specific carrier state distinguishes rename source from terminal destination replacement
→ currently demonstrated candidate for a conforming adapter

stock Git 2.47.3 / reftable
→ terminal `branch -D` / `update-ref -d` is reference-transaction observable
→ native `branch -m` and forced `branch -M` complete with zero reference-transaction callbacks in the tested path
→ a managed destination can therefore be overwritten without the required current vetoable observation surface
→ stock tested path is NOT conforming for live managed authoring
```

This is a conformance result, not a permanent prohibition on reftable. A future Git/reftable implementation or external adapter that exposes the required pre-linearization capability becomes admissible automatically without changing core semantics.

Automatic ref-storage migration is not a normative substitute for this contract. It may be a bootstrap implementation technique only when separately proven safe for the repository's current worktree/concurrency state.

### 11. `reference-transaction` is one implementation primitive, not the architecture

ADR-071's former wording that v1 "MUST install/use `reference-transaction`" is narrowed by this ADR.

A conforming implementation MUST satisfy the capability contract in §9. The currently demonstrated `files` adapter uses `reference-transaction` plus backend-specific native rename evidence. Other adapters may use a future Git primitive that is equally vetoable and causally strong.

Current Git-version requirements therefore follow from the selected conforming adapter implementation; Git >=2.28 remains sufficient for the tested `reference-transaction` primitive but is not by itself proof that a repository/ref backend is admissible.

### 12. `committed` / `aborted` delivery is valuable but not the sole correctness primitive

For a prepared correctness-critical transition, delivered committed/aborted callbacks SHOULD be durably recorded when available.

However correctness MUST survive a crash/lost outcome notification:

```text
PREPARED durable
+ outcome callback missing
→ re-observe exact ref/backend state under continuous-coverage assumptions
→ prove committed / aborted / still unresolved
```

If exact recovery cannot distinguish the outcome, the transition remains unresolved and uses the existing recovery path; no result is guessed.

### 13. All other 30.50 observations are exact-state rediscovery

No durable local command/event log is required for:

```text
ordinary authoring ref tip movement
commit / reset / merge / rebase
worktree add/remove/move and HEAD switch/detach
index and structural in-progress state
submodule/sparse observability
internal contribution/convergence refs
submission refs and remote/provider heads
promotion targets
remote-tracking refs
stash / tags / notes
ancestry interpretation environment
```

When a current transition requires them, `ruu` re-observes exact current authoritative state and applies its existing expected-old, ancestry, policy, provider, claim, and recovery rules.

A lost intermediate event may cause rediscovery, drift handling, or fail-closed recovery; it does not create a new semantic transition.

### 14. Ancestry is reconstructed under a canonical proof contract

`refs/replace/*`, grafts, and shallow boundaries remain state-plane inputs, not events.

Managed ancestry proofs MUST be independent of unnoticed mutable local history overlays:

```text
replace refs
→ must be disabled/ignored by the ancestry proof implementation or cause the proof to block

grafts
→ must be excluded by a canonical raw-object ancestry implementation or cause the proof to block

shallow boundary
→ a negative/unknown relation that may depend on unavailable history is not authoritative
→ deepen/fetch/recover when authorized and possible, otherwise block as ancestry unknown
```

The implementation may use native Git or another exact object-graph reader, but it MUST prove the same raw repository object ancestry contract rather than silently inheriting ambient replacement/graft interpretation.

### 15. Additional notifications are best-effort only

Hooks/watchers may notify the reconciler about ordinary ref/worktree/index changes to reduce latency or improve diagnostics.

Loss, duplication, reordering, or coalescing of such notifications MUST NOT affect correctness. The next executed sweep reconstructs current state.

The identity/idempotency scheme for durable normalized witnesses and duplicate hook delivery remains explicitly under 30.52.

## Consequences

- Backlog **30.51 is closed**.
- 30.49 remains open until 30.52–30.55 are coherently resolved.
- Correctness-critical capture is limited to native mutations that can terminate/replace the currently bound managed authoring ref.
- `ABANDON` and `CONTINUATION` are independently positive proofs; failure to prove one never implies the other.
- Ambiguous managed-binding mutation is vetoed before linearization when the selected adapter can still prevent it.
- Native-ref adapters normalize backend-specific facts; only the core derives managed disposition semantics.
- The architecture norms backend capabilities, not `files` or `reftable` names.
- The tested stock `files` path is a demonstrated candidate implementation; the tested stock `reftable` rename path is not currently conforming because rename/forced-rename can bypass the required vetoable observation point.
- A future upstream Git primitive around native rename can make reftable conform without changing the core contract.
- Opaque backend witness hashes are non-normative; durable normalized witness facts are the correctness record.
- All other currently identified local Git observations remain exact-state rediscovery; extra wakeups are best effort.
- 30.52 now owns durable witness identity, provenance, replay, duplicate delivery, and idempotency.
- 30.53/30.54 still own hook/observer installation, continuous coverage, and concrete persistence-failure handling.

## Rejected alternatives

### Require the `files` ref backend in v1

Rejected. The architecture depends on causal observation properties, not an on-disk ref implementation. A backend satisfying the capability contract is admissible regardless of name.

### Treat `reference-transaction` support as sufficient backend conformance

Rejected. Tested stock reftable branch rename/forced rename can bypass that callback path.

### Infer terminal abandonment from failure to prove continuation

Rejected. An interrupted rename can leave the source absent without proving a terminal deletion.

### Let a post-commit observer repair the causal race later

Rejected. Post-state proof cannot retroactively prevent an already unauthorized realization effect from crossing the disposition fence.

### Put backend-specific temporary paths in the core model

Rejected. Backend adapters own physical representation; the core consumes normalized facts only.

### Persist only an opaque backend witness digest

Rejected. A digest without durable normalized semantics cannot be independently interpreted after transient backend state disappears.

### Turn every Git event into a durable journal entry

Rejected. Exact-state rediscovery remains the simpler and stronger default wherever event history is not semantically required.


## Amendment by ADR-076 — active-occurrence correlation and semantic exactly-once

The capability contract gains one replay/idempotency requirement:

```text
ACTIVE_OCCURRENCE_CORRELATION
→ repeated delivery/re-entry for the same active pre-linearization native occurrence is correlated sufficiently to reuse the same effective durable preparation and permit/veto decision
→ a genuinely distinct competing occurrence cannot establish a second unresolved cessation/rebind preparation against the same current binding generation
```

This is adapter-local causal correlation, not a requirement for a backend-provided globally unique permanent transaction ID. Transition-content fingerprints may be evidence/debug material but are not universal occurrence identity. Native witnesses are causal evidence, not managed Operations; optional trusted `originating_attempt_id` is correlation only. Outcome callbacks may duplicate or be lost after durable PREPARED state; recovery remains exact-state-based and unresolved when proof is insufficient. A state scan never manufactures a missing causal preparation.

## Subsequent observer-coverage amendment — ADR-077

ADR-077 subsequently closes backlog 30.53. The ADR-075 capability contract remains controlling for capture strength; ADR-077 defines how that capability is established non-destructively as an attested repository-common observer binding for an admitted mutation-engine/adapter profile, with Git core as the required V1 engine family and coverage epochs for continuous-trust accounting.

## Clarification by ADR-081 — exact authoring dependencies preserve the observation split

Native commit/reset/merge and ordinary tip movement remain exact-state rediscovery even when an exact commit may later be selected as a dependency. Only the semantic dependency adoption is managed state. The adoption operation may use exact native-ref exclusion to prove the source preimage and create its recovery anchor; this does not promote ordinary commit creation into a pre-linearization business-event family.
