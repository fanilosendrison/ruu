# Hostile Audit — ADR-071

- **Date:** 2026-09-08
- **Target:** ADR-071 + amended ADR-068 cancellation/deletion semantics
- **Verdict:** **PASS WITH EXPLICIT CROSS-SYSTEM FAIL-CLOSED BOUNDARY**

## Attacks exercised

### H1 — crash after old nominal Attempt, before effect; abandonment occurs

Expected: recovery may inspect the old Attempt but cannot reuse it as current authority. `CANCEL` blocks a new nominal effect. **PASS.**

### H2 — COMPENSATE selected while old nominal Attempt is still absent

Expected: nominal retry blocked unless the current compensation plan explicitly authorizes that exact effect. **PASS.**

### H3 — human uses only native Git to abandon

```text
git branch -D managed-topic
```

Expected: no second PromotionGroup command; managed-ref deletion is captured through `reference-transaction`. **PASS.**

### H4 — unmanaged branch or worktree deletion

Expected: no hidden cancellation semantics. **PASS.**

### H5 — Ruu is down while managed branch is deleted

Expected: deletion event cannot be reconstructed merely from later absence; write-ahead hook persists the prepared transaction inside the Git command itself. **PASS.**

### H6 — durable ingress write fails

Expected: correctness-critical managed branch deletion aborts rather than silently losing abandonment. Concrete smoke confirms non-zero `prepared` leaves branch present. **PASS.**

### H7 — crash after ref commit before committed-hook persistence

Expected: unresolved prepared record + exact ref state drives recovery; prepared is not itself semantic abandonment until transaction commit is established. **PASS.**

### H8 — PR has CHANGES_REQUESTED

Expected: ADR-053 correction continuation, no cancellation. **PASS.**

### H9 — PR closed/rejected without merge

Expected: terminal non-realizing publication episode, not automatic ship abandonment. Native deletion of the managed authoring branch remains the abandonment gesture. **PASS.**

### H10 — branch deleted after historical promotion

Expected: historical promotion remains; deletion is ordinary branch cleanup and adds no lifecycle state. **PASS.**

### H11 — provider surface exists before abandonment

Expected: old open PR/auto-merge/queue state is not residual future authority. Current cancellation causes Ruu to revoke/close what remains revocable. **PASS.**

### H12 — provider effect was causally committed before abandonment

Expected: recover/adopt the historical effect; cancellation cannot travel backward. **PASS.**

### H13 — external provider/Git movement races with local abandonment and order is not provable

Attack: pretend `reference-transaction` created a distributed transaction with GitHub and choose an order from timestamps.

Expected: reject the premise. The hook makes the local deletion event durable but does not create a common provider clock/fence. Terminal classification remains fail-closed when authoritative causal order is genuinely unavailable. **PASS.**

### H14 — later manual equivalent Git state after terminal CANCELLED

Expected: historical cancelled group remains terminal; later activity is new external history, not resurrection. **PASS.**

## Key adversarial conclusion

ADR-071 closes the lost-deletion-event defect without claiming an impossible distributed atomic transaction. Its strongest safe guarantee is:

```text
native managed-ref deletion is durably observable and recoverable
+
current disposition fences all new managed causal effects
+
unprovable unmanaged cross-system ordering is never invented
```

**Verdict: PASS.**
