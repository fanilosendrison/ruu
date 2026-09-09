# Hostile Audit — ADR-075

- **Date:** 2026-09-08
- **Target:** 30.51 observation strength, native-ref adapter/core boundary, positive disposition proofs, backend capability contract
- **Verdict:** **PASS — PRE-LINEARIZATION CAPTURE IS MINIMAL, BACKEND-CAPABILITY-BASED, AND POSITIVE-PROOF-DRIVEN**

## Attacks exercised

### H1 — Treat every observable Git mutation as a durable semantic event

Attack: generalize the observation plane into a Git audit daemon.

Expected: rejected. Only native mutations capable of terminating/replacing the current managed authoring binding require correctness-critical pre-linearization capture. Ordinary ref tips, worktrees, HEAD/index, internal/submission/target refs and ancestry environment remain exact-state rediscovery. **PASS**.

### H2 — Observe managed abandonment only after Git commits

Attack:

```text
read current disposition NORMAL
→ native binding deletion linearizes
→ old nominal effect linearizes before observer persists ABANDON
```

Expected: rejected. The binding-ending mutation must cross a vetoable/equivalently serialized adapter point before linearization. Post-commit observation cannot repair the causal race. **PASS**.

### H3 — Let the native adapter decide `ABANDON` / `CONTINUATION`

Attack: backend-specific code acquires business semantics.

Expected: rejected. Adapter emits normalized native facts/witnesses only; core combines them with current binding generation and derives `TERMINAL_REMOVAL_PREPARED | RENAME_CARRY_PREPARED | UNKNOWN`. **PASS**.

### H4 — `!ContinuationProof => ABANDON`

Attack: interrupted rename removes source but never establishes successor.

Expected: rejected. `ABANDON` requires positive terminal-removal preparation plus committed outcome. Incomplete rename remains unresolved/recovery. **PASS**.

### H5 — `git branch -M foo bar` silently destroys another managed destination

Concrete `files` smoke:

```text
foo source
→ RENAME_CARRY_PREPARED

existing bar destination
→ TERMINAL_REMOVAL_PREPARED
```

The two affected managed bindings are classified independently. **PASS**.

### H6 — force-delete reports zero old OID and loses exact preimage

Concrete `files` smoke shows `git branch -D` / forced destination deletion may expose zero-valued old fields while the ref is still resolvable during `prepared`.

Expected: adapter establishes the actual exact preimage rather than trusting the zero sentinel as historical truth. **PASS**.

### H7 — Assume `reference-transaction` support means every backend is conforming

Concrete stock Git 2.47.3 reftable smoke:

```text
branch -D foo
→ reference-transaction callback observed

branch -m foo bar
→ rename succeeds
→ zero reference-transaction callbacks

branch -M foo bar (bar already exists)
→ replacement succeeds
→ zero reference-transaction callbacks
```

Expected: backend/hook name is not the contract. This tested reftable path is nonconforming for live managed authoring until an equivalent pre-linearization capability exists. **PASS**.

### H8 — Permanently ban reftable

Attack: turn current Git implementation detail into architecture.

Expected: rejected. Backend admissibility is property-based. Any future reftable/Git adapter satisfying the capability contract becomes conforming without a core ADR change. **PASS**.

### H9 — Leak `.tmp-renamed-log` or reftable storage details into core semantics

Expected: rejected. Backend-specific carrier representation remains inside the native-ref adapter. Durable correctness state is the normalized witness plus core preparation classification. **PASS**.

### H10 — Persist only an opaque backend witness digest

Attack: trust a hash after transient native evidence disappears.

Expected: rejected. Opaque digest alone has no interpretable semantics. Normalized witness fields are durable correctness evidence; optional raw evidence/digest is audit/debug only. **PASS**.

### H11 — Fingerprint the physical reflog file or complete history

Attack: make correctness depend on `files` path/layout or on old reflog entries that normal expiry/GC may remove.

Expected: rejected. `ReflogBaselineV1` is `ENTRY(anchor_entry_fingerprint) | EMPTY_PRESENT`; the entry fingerprint covers logical reflog entry fields and excludes physical storage/ref-name/ordinal metadata. **PASS**.

### H12 — Require same worktree `HEAD` rebind for continuation

Attack: Git ref rename succeeds but process crashes before linked-worktree `HEAD` repair.

Expected: rejected. Worktree state is corroborating/editing topology. A complete native rename proof may establish continuation while worktree topology separately requires repair. **PASS**.

### H13 — Lose ordinary ref/worktree notifications

Expected: safe. Their current exact consequences are rediscovered on the next sweep; notification loss affects latency, not correctness. **PASS**.

### H14 — Let replace refs/grafts silently alter managed ancestry

Expected: rejected. Managed ancestry uses a canonical raw-object proof or blocks; shallow history is deepened/fetched when authorized/possible or remains unknown. Overlay creation history itself is not an event. **PASS**.

### H15 — Treat automatic reftable→files migration as the architecture

Expected: rejected. Migration may be an implementation/bootstrap technique only when separately safe; it does not replace the backend capability contract and cannot be assumed universally available with active worktrees/concurrent writers. **PASS**.

## Concrete regression evidence

`git-native-observation-smoke-v3.sh` on Git 2.47.3:

```text
retained_v2_regressions: PASS
files_rename_carry_prepared: PASS
files_terminal_removal_prepared: PASS
files_force_rename_two_bindings: PASS
prelinearization_veto_effective: PASS
reftable_delete_callback_visible: PASS
reftable_rename_bypass_detected: PASS
reftable_force_rename_bypass_detected: PASS
git-native observation smoke v3: PASS
```

## Adversarial conclusion

ADR-075 preserves the intentionally narrow architecture:

```text
one local event-semantic family
→ managed authoring-binding disposition

only binding-ending/replacing native mutations
→ pre-linearization durable witness

all other facts
→ exact-state rediscovery

backend specifics
→ adapter only

managed semantic conclusion
→ core only
```

**Verdict: PASS.**
