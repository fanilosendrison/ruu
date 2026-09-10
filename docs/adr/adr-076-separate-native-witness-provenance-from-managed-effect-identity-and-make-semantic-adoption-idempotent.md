# ADR-076 — Separate native witness provenance from managed effect identity and make semantic adoption exactly-once

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.52
- **Amends:** ADR-042, ADR-071, ADR-074, ADR-075, the consolidated specification, the External Control Plane contract, and the observation backlog
- **Leaves open:** backlog 30.49 umbrella and 30.53–30.55

## Context

ADR-075 establishes one correctness-critical local native-Git event family: a native mutation capable of ending/replacing the currently bound managed authoring ref must produce a durable normalized pre-linearization witness before causal commit. All other currently retained observations are exact-state rediscovery or best-effort wakeups.

30.52 must decide how that native witness plane composes with ADR-042's recoverable-effect journal:

```text
Operation → Attempt → Observation → Adoption
```

without treating one physical Git transition as two managed effects when `ruu` itself caused the transition, and without making crash recovery depend on exactly-once hook delivery.

The tempting model is to identify every native Git transition as an `Operation`, or to derive a universal event identity from `(old_oid, new_oid, ref)` or another transition fingerprint. Both are wrong for this architecture:

- a native Git command executed outside `ruu` is not a managed intent;
- the same transition content may occur again later as a genuinely different physical occurrence;
- the same physical occurrence may be delivered/replayed more than once;
- current-state scans may rediscover an already-realized managed effect without possessing event provenance;
- actor identity is neither Git truth nor required for the managed correctness decision.

The architecture therefore needs **semantic exactly-once adoption**, not exactly-once observation delivery and not a universal Git transaction identity.

## Decision

### 1. Managed effect intent, native causal witness, and managed semantic transition are distinct objects

The system distinguishes three planes:

```text
Managed effect plane
Operation → Attempt → Observation → Adoption

Native causal evidence plane
NativeRefWitness / NativeBindingPreparation

Managed domain transition plane
binding-generation disposition / current-state CAS transition
```

An ADR-075 native witness is evidence that Git is attempting or has realized a physical ref transition. It is **not** a managed `Operation` merely because the transition may affect managed state.

The ADR-042 journal therefore remains a journal of recoverable effects **owned/caused by `ruu`**, not a universal audit log of every Git command.

### 2. A native witness never manufactures a second managed Operation

When a managed `Attempt` causes a Git ref transition that is also observed through the native-ref adapter:

```text
Operation O
→ Attempt A
→ native Git transition
→ NativeRefWitness W
→ exact Observation for O
→ Adoption for O
```

`W` may be referenced as causal/physical evidence by the Observation or managed transition, but it MUST NOT create a second logical Operation for the same physical transition.

Conversely, a native Git transition with no managed originating Attempt remains a native witness and may drive the appropriate managed binding-disposition transition without inventing an `Operation` whose intent never existed.

### 3. Attempt provenance is optional, narrow, and non-authoritative

A native witness MAY carry:

```text
originating_attempt_id = <Attempt>
```

only when the adapter can obtain that correlation from a trusted attempt-scoped execution context established by `ruu` for the child Git operation.

Otherwise:

```text
originating_attempt_id = NULL
```

is normal and does not weaken the witness.

Attempt provenance answers only:

> this native physical occurrence was correlated with this managed physical Attempt.

It does **not** authorize the mutation, prove current policy/disposition, bypass expected-old/CAS checks, or establish managed success. All ordinary exact-state, current-disposition, claim/fence, policy, preimage, and result checks remain independently required.

No correctness rule may require inference of a human, agent, IDE, terminal session, or command-line actor identity from native Git evidence.

### 4. The authoritative exactly-once identities remain logical managed identities

The correctness property is not "one native delivery". It is:

```text
one logical managed transition
→ at most one authoritative adoption
```

Specifically:

```text
Operation(operation_id)
→ at most one successful Adoption
→ at most one mutually-exclusive terminal non-adopting Closure

AuthoringBindingGeneration(repository_id, work_occurrence_id, binding_generation)
→ at most one committed cessation/rebind disposition
→ at most one authoritative transition out of that generation
```

A committed `CONTINUATION` creates the next binding generation. A committed `ABANDON` terminalizes the current managed authoring occurrence as already defined by ADR-071/074/075.

Duplicate native evidence, duplicate outcome delivery, repeated exact-state scans, process replay, or repeated wakeups cannot multiply these transitions because adoption/disposition is guarded by the current logical identity and expected-state/CAS.

### 5. Native physical occurrence identity is local evidence identity, not domain identity

The adapter/core boundary MAY represent an active physical occurrence with an opaque synthetic identity, conceptually:

```text
NativeRefOccurrence {
  native_occurrence_id
  repository_id
  adapter_capability_id
  adapter_version
  normalized_ref_updates[]
  originating_attempt_id?   // optional correlation only
}
```

and one affected managed binding with a durable preparation such as:

```text
NativeBindingPreparation {
  preparation_id
  native_occurrence_id?
  repository_id
  work_occurrence_id
  binding_generation
  affected_ref
  exact_preimage_oid
  classification = TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED
  normalized_witness_ref
  outcome = PREPARED | COMMITTED | ABORTED | UNRESOLVED
}
```

The exact schema is implementation-defined. The normative properties are:

- `preparation_id` is immutable and non-recycled;
- one physical ref transaction may contain several affected managed bindings;
- each binding consequence is independently generation-bound;
- physical occurrence identity never replaces `operation_id`, ContributionUnit/work-occurrence identity, or binding generation as managed authority identity.

The core MUST NOT require a backend to expose a globally unique permanent Git transaction identifier. Adapter-local correlation sufficient for the active serialized occurrence is enough.

### 6. Duplicate delivery of one active native occurrence is idempotent

A conforming ADR-075 adapter must additionally provide **active-occurrence correlation** sufficient to ensure that repeated delivery/re-entry for the same in-flight pre-linearization occurrence does not create a second semantic preparation or cause a false veto.

Conceptually:

```text
same active physical occurrence
→ same effective NativeBindingPreparation
→ same permit/veto decision
```

This correlation may be implemented with backend/adapter-specific mechanisms and remains outside core business semantics.

A transition fingerprint such as `(old_oid, new_oid, ref)` may be retained as evidence/debug data but MUST NOT be treated as a globally unique occurrence identity: two distinct later transactions may have identical transition content.

### 7. One binding generation cannot have competing unresolved cessation/rebind preparations

For one current managed binding generation:

```text
ACTIVE generation G
→ at most one unresolved correctness-critical cessation/rebind preparation
```

A duplicate delivery of that same active occurrence is idempotent. A genuinely distinct conflicting native transition cannot establish a second concurrent preparation against the same still-current generation; it must wait, fail/veto, or be reconciled after the first preparation is resolved under the adapter's causal-serialization rules.

After `ABORTED`, generation `G` remains current and a later distinct transaction may create a new preparation. After committed `CONTINUATION` or `ABANDON`, generation `G` is no longer current and stale deliveries cannot re-dispose it.

This is a correctness serialization rule, not a requirement to serialize unrelated refs or repositories.

### 8. Outcome delivery is at-least-once/best-effort compatible; semantic settlement remains exact

Delivered native outcome notifications SHOULD update the durable preparation:

```text
PREPARED → COMMITTED
PREPARED → ABORTED
```

Duplicate outcome delivery is idempotent. Contradictory outcome delivery is an observation-integrity failure and fails closed.

If a committed/aborted callback is lost after the durable preparation exists, ADR-075 recovery remains controlling:

```text
PREPARED durable
+ exact current ref/backend state
+ trustworthy continuous-coverage interval
→ prove COMMITTED / ABORTED when possible
→ otherwise remain UNRESOLVED
```

No outcome is guessed merely to clear a pending preparation.

### 9. Exact-state rediscovery never manufactures a missing causal event

A later scan may:

```text
- observe the current result of an existing Operation;
- resolve the outcome of an already-durable native preparation when proof is sufficient;
- detect a coverage/evidence contradiction and fail closed;
```

but it MUST NOT synthesize a historical `TERMINAL_REMOVAL_PREPARED`, `RENAME_CARRY_PREPARED`, or equivalent causal witness merely because the current ref topology looks compatible with one.

Therefore:

```text
ref absent now
≠ proof that terminal removal was causally witnessed

same/similar successor now
≠ proof that native rename continuity was causally witnessed
```

This preserves ADR-074/075's positive-proof model.

### 10. Wakeups are deliberately non-semantic

Hook/watcher/provider notifications used only to request another global sweep are coalescible signals:

```text
duplicate wakeup → harmless
lost wakeup      → later demand/sweep rediscovers state
reordered wakeup → harmless
```

A wakeup has no semantic occurrence identity and never satisfies an Operation, a native binding preparation, or a managed disposition by itself.

### 11. One physical fact may support several distinct semantic consequences without double-counting

A single native transaction may legitimately support more than one consequence, for example a forced rename that carries one managed source binding while terminally replacing another managed destination binding.

Likewise, a native witness correlated with managed Attempt `A` may simultaneously:

```text
- serve as physical evidence while Operation O is observed/adopted; and
- serve as causal evidence for an affected binding-generation disposition.
```

This is not double-counting because the authoritative identities and state transitions are different. Double-counting means multiplying one logical Operation adoption or one binding-generation disposition, which the rules above prohibit.

### 12. Exactly-once delivery is explicitly not required

The v1 contract is:

```text
native witness / outcome / scan / wakeup delivery
→ may be duplicated or replayed
→ some noncritical signals may be lost

managed authoritative adoption/disposition
→ exactly-once per logical identity under CAS/current-generation guards
```

For correctness-critical pre-linearization preparation itself, ADR-075/30.54 still require that the necessary durable preparation exist before causal commit. ADR-076 does not weaken that persistence rule; 30.54 remains responsible for the concrete failure/retry behavior when persistence is unavailable.

## Consequences

- Backlog **30.52 is closed**.
- Native observation is not folded into the ADR-042 Operation journal as fake managed intent.
- The journal remains `Operation → Attempt → Observation → Adoption` for effects `ruu` owns/causes.
- Native-ref causal evidence has its own durable evidence/preparation records and may optionally correlate to an Attempt.
- Actor identity is irrelevant to correctness unless a future separately-ratified boundary explicitly requires it.
- Exactly-once applies to authoritative logical transition, not delivery.
- Repeated scans cannot invent causal history.
- The native-ref adapter capability contract gains active-occurrence correlation/idempotent duplicate handling for the in-flight pre-linearization interval.
- 30.53 remains responsible for establishing/composing continuous observer coverage; 30.54 for persistence-failure semantics; 30.55 for local/remote/provider composition.

## Rejected alternatives

### Make every native Git transition an `Operation`

Rejected. It turns ADR-042's recoverable-effect journal into an audit log and invents managed intent for ordinary native Git actions.

### Use `(old_oid, new_oid, ref)` or a hash of it as universal event identity

Rejected. Identical transition content can occur in distinct transactions at different times, while one transaction may itself be delivered repeatedly.

### Require exact actor attribution

Rejected. Human/agent/IDE/process identity is not required to classify the Git fact and is weaker than exact managed identities/current state for correctness.

### Treat attempt provenance as authorization

Rejected. Provenance explains physical origin; current policy/disposition/claims/CAS still govern authority.

### Reconstruct a missing causal preparation from final state

Rejected. That would reintroduce the delete/recreate and rename/copy ambiguities ADR-074/075 explicitly closed.

### Demand globally exactly-once hook delivery

Rejected. Crash/replay-safe systems should tolerate duplicate delivery and recover lost outcome notifications; the exact-once boundary is authoritative managed adoption.

## Subsequent observer-coverage amendment — ADR-077

ADR-077 subsequently closes backlog 30.53. ADR-076's `trustworthy continuous-coverage interval` is concretized as an attested repository-common coverage epoch for an admitted mutation-engine/adapter profile. Repair opens a new epoch and never retroactively proves a prior gap; direct/uninstrumented managed-ref mutation without the required preparation is an observation-integrity failure rather than reconstructible causal history.

## Clarification by ADR-081 — ContributionUnit identity and dependency adoption

The `work_occurrence_id` examples in this historical ADR are read in current v1 as `contribution_unit_id`; no second WorkOccurrence identity exists. Binding generation remains separate.

AuthoringDependency adoption is a managed ADR-042 Operation because Ruu creates a correctness-critical exact-OID anchor and adopts a semantic source/version relation. The native commit that supplied the OID remains ordinary Git state and does not create another Operation. Duplicate selection/observation/recovery converges on one immutable dependency identity and at most one CAS-adopted source promotion projection.
