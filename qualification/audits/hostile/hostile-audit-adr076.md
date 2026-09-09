# Hostile Audit — ADR-076

- **Date:** 2026-09-08
- **Target:** 30.52 native witness provenance, replay, duplicate delivery, journal composition, exactly-once semantic adoption
- **Verdict:** **PASS — DELIVERY MAY REPEAT; LOGICAL ADOPTION CANNOT**

## Attacks exercised

### H1 — Turn an external native Git delete into a synthetic managed `Operation`

Expected: rejected. A native witness is causal evidence, not managed intent. No Operation is invented merely because managed state is affected. **PASS**.

### H2 — Managed Attempt produces a ref transition and the hook sees it too

Attack: count the same physical Git effect once through the Operation journal and once again as a native operation.

Expected: the native witness may correlate to the Attempt and support its Observation, but it never creates a second Operation. Binding disposition, if independently affected, is a different generation-bound semantic transition. **PASS**.

### H3 — Duplicate `prepared` delivery for one active native occurrence

Expected: adapter active-occurrence correlation maps repeated delivery to the same effective preparation/decision. No second semantic preparation and no false veto. **PASS**.

### H4 — Two genuinely distinct later transactions have identical `(old,new,ref)` content

Expected: a content fingerprint is not universal occurrence identity. After an earlier preparation aborts/resolves, a later physical occurrence may receive a distinct preparation identity. **PASS**.

### H5 — Two competing unresolved preparations attempt to terminate the same binding generation

Expected: forbidden. One generation admits at most one unresolved correctness-critical cessation/rebind preparation. A distinct competitor waits/vetoes/fails until the first resolves. Unrelated refs remain concurrent. **PASS**.

### H6 — Crash after PREPARED; committed callback is lost

Expected: the durable preparation survives. Recovery uses exact state plus trustworthy coverage to prove committed/aborted when possible; otherwise it remains unresolved. No second Operation or guessed outcome is created. **PASS**.

### H7 — Crash after managed Git effect succeeds but before Operation Observation/Adoption

Expected: recovery observes exact state for the existing immutable Operation and appends the ordinary Observation/Adoption. A native witness, whether correlated or unattributed, does not change Operation identity. **PASS**.

### H8 — Repeated scan sees managed ref absent with no causal preparation

Expected: scan cannot invent `TERMINAL_REMOVAL_PREPARED`. The state is an observation-integrity/causality problem and fails closed or uses the explicit ADR-074 generation-bound recovery path. **PASS**.

### H9 — Scan sees a plausible successor branch with same OID

Expected: scan cannot invent `RENAME_CARRY_PREPARED`; same OID/tree/ancestry is not continuity proof. **PASS**.

### H10 — Duplicate committed/aborted callback

Expected: identical repeats are idempotent. A contradictory terminal outcome is an observation-integrity failure rather than a second disposition. **PASS**.

### H11 — Attribute native mutation to the wrong human/agent/session

Expected: actor attribution is not required for correctness and is not inferred. Optional `originating_attempt_id` is limited to trusted attempt-scoped correlation and remains non-authoritative. **PASS**.

### H12 — Old Attempt correlation token is replayed after binding generation advances

Expected: current binding generation / expected-state guards reject stale semantic adoption. Provenance cannot resurrect authority. **PASS**.

### H13 — Wakeup delivered 0, 1, or many times and out of order

Expected: wakeups are coalescible non-semantic demand signals. They neither satisfy Operations nor create native causal history. **PASS**.

### H14 — One forced rename affects two managed bindings

Expected: one physical occurrence may support independent generation-bound consequences for source continuation and destination terminal replacement. Exactly-once is enforced per affected logical identity, not by pretending the transaction has only one semantic consequence. **PASS**.

## Adversarial conclusion

ADR-076 keeps the identities correctly layered:

```text
Operation identity
→ managed effect intent

native preparation identity
→ physical/causal evidence occurrence

binding generation
→ managed authoring-disposition authority identity
```

Delivery/replay is allowed to be at-least-once. Exactness is enforced where it matters: one Operation adoption and one binding-generation disposition.

**Verdict: PASS.**
