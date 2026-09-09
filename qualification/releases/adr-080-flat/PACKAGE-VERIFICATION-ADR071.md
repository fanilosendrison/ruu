# Ruu — Package Verification through ADR-071

- **Date:** 2026-09-08
- **Current architecture:** ADR-001..ADR-071
- **Current finite technical audit:** `STATE-SPACE-AUDIT-v38.md` / **14,992 combinations**
- **Current open design items:** 30.46, 30.47; 30.49 deferred until both close

## Integrated decision

ADR-071 closes backlog 30.44/30.45 and amends ADR-068/ADR-070 §0.8.

```text
reconciliation may recover knowledge without recovering authority
```

Every new managed realization effect is gated by current semantic disposition under a causal authorization fence. Successful native deletion of a currently bound managed authoring ref is the ordinary abandonment gesture; it is captured crash-safely with Git `reference-transaction` rather than inferred from later branch absence. No routine `Ruu cancel` command is required.

## Native Git regression

Executed with Git 2.47.3:

```text
reference-transaction managed deletion commit: PASS
reference-transaction prepared failure aborts deletion: PASS
```

The architecture minimum remains Git >= 2.28 because that release documents `reference-transaction` prepared/committed/aborted and prepared-phase abort semantics.

## State-space verification

Fresh v38 executable model:

```text
ADR-071 causal authorization family: PASS (48)
ADR-071 transactional managed-ref deletion family: PASS (24)
ADR-071 external/provider cancellation race family: PASS (54)
ADR-071 new finite combinations: PASS (126)
retained v37 baseline: 14,866
v38 total: 14,992
```

Backlog 30.48 is closed by this verification.

## Post-ADR-071 backlog extension

A later design review records **30.49 Native Git observation plane for out-of-band mutations**. This is backlog capture only, not a ratified semantic change to ADR-071. The investigation asks whether selected Git-native hooks/transaction points should durably report correctness-relevant native Git mutations while all managed interpretation remains in the reconciler. By explicit scheduling decision, 30.49 is deferred until 30.46 and 30.47 close.

## Static/package checks

The final packaging pass verifies:

```text
ADR numbering 001..071
spec / legacy alias byte equality
Markdown fence balance
Python audit compilation
shell syntax
ADR-071 current-disposition anchors
reference-transaction / Git >= 2.28 anchors
backlog 30.44/30.45/30.48 closed
backlog 30.46/30.47 immediate; 30.49 explicitly deferred/open
```

## Verdict

**VERIFIED / PASS.**
