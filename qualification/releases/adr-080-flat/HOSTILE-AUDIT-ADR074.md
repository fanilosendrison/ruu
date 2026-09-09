# Hostile Audit — ADR-074

- **Date:** 2026-09-08
- **Target:** minimal native-Git observation set and managed authoring-binding disposition
- **Verdict:** **PASS — ONE LOCAL EVENT-SEMANTIC FAMILY; NO OID-BASED CONTINUITY GUESSING**

## Attacks exercised

### H1 — ordinary branch rename is misclassified as abandonment

Attack:

```text
managed foo
→ git branch -m foo bar
→ reference-transaction exposes foo old → zero
```

Expected: the old-ref removal records `AUTHORING_BINDING_TRANSITION_PREPARED`; commit leaves disposition unresolved until native rename/rebind continuity is proven. Then `CONTINUATION`, not `CANCEL`.

Concrete linked-worktree/reflog smoke: **PASS**.

### H2 — another branch points at the same OID

Attack: infer that identical OID means the same authoring line.

Expected: rejected. OID/tree/ancestry is consistency state, never continuity identity. **PASS**.

### H3 — copy then delete masquerades as rename

Attack:

```text
git branch -c foo bar
git branch -D foo
```

Expected: `foo` is genuinely abandoned; `bar` is an ordinary separate branch. Native reflog evidence identifies copy rather than rename. **PASS**.

### H4 — worktree HEAD is manually switched to another branch

Attack: infer rebind from `git switch bar` while managed `foo` still exists.

Expected: topology mismatch only. Worktree HEAD alone does not authorize rebind. **PASS**.

### H5 — managed reflog is missing when Ruu is invoked

Case A:

```text
expected managed binding intact
+ no unresolved transition
+ exact current state coherent
```

Expected: Ruu may create/repair reflog and establish a new future baseline. The concrete smoke shows that a branch-specific empty reflog baseline can support a later native rename record even with repository-wide automatic reflogs disabled. **PASS**.

Case B:

```text
unresolved binding transition
+ missing causal reflog history
```

Expected: recreating reflog cannot invent the past. Use other sufficient native evidence or exceptional recovery; otherwise block. **PASS**.

### H6 — stale ECP metadata silently resurrects abandoned work

Attack: old control-plane binding says C continues on `bar` after a real abandonment.

Expected: rejected. `AuthoringBindingRecovery` is expected-old and binding-generation guarded; Ruu independently revalidates actual Git/ref/worktree/OID state and mutation authority. **PASS**.

### H7 — ECP claims a Git rename happened

Expected: rejected boundary. ECP may declare logical `REBIND(new_ref) | ABANDON` only for exceptional recovery; Git history/facts remain owned by Git observation. **PASS**.

### H8 — replace refs silently change ancestry decisions

Attack: keep commit OIDs stable while `refs/replace/*` changes the effective object/parent view.

Expected: ancestry interpretation environment is correctness-relevant state. Ancestry-dependent progression waits for the normalized/proven authoritative view. **PASS**.

### H9 — `info/grafts` bypasses `GIT_NO_REPLACE_OBJECTS`

Concrete smoke confirms that the tested Git still applies graft parent rewriting even with `GIT_NO_REPLACE_OBJECTS=1`.

Expected: do not assume disabling replace refs disables grafts. Detect/account for graft state explicitly. **PASS**.

### H10 — shallow repository yields incomplete ancestry

Expected: a shallow boundary is state, not a semantic event. If required ancestry cannot be proven, fetch/deepen/recover under the final 30.51 mechanism or block; never classify divergence from incomplete history as authoritative merely because Git returned a local answer. **PASS**.

### H11 — hook coverage is disabled, managed ref is delete/recreated at the old OID, coverage later returns

Attack:

```text
coverage lost
→ managed foo deleted (real abandonment)
→ foo recreated at same OID
→ coverage restored
```

Current state alone looks familiar.

Expected: ADR-074 does **not** declare this safe. Continuous observation integrity is explicitly delegated to 30.53/30.54; a coverage gap cannot be treated as proof that no event occurred. **PASS / OPEN MECHANISM PRESERVED**.

### H12 — broaden event logging to every Git command

Expected: rejected. Internal refs, submission refs, target refs, worktrees, HEAD/index structural state, tags/stash/notes, and ordinary tip movement remain state-observed unless a future concrete correctness proof establishes another irreducibly causal event family. **PASS**.

## Adversarial conclusion

The corrected architecture is deliberately narrow:

```text
one local business-event family
= managed authoring-binding disposition

most Git behavior
= exact current state

proof-infrastructure health
= separate observation-integrity concern
```

This fixes the rename false-abandonment bug without turning Ruu into a command proxy or general Git audit daemon.

**Verdict: PASS.**
