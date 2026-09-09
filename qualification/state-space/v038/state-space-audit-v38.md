# Ruu — STATE-SPACE-AUDIT v38

- **Date:** 2026-09-08
- **Technical finite-state families:** through ADR-071
- **Baseline retained:** v37 = 14,866 finite combinations
- **New ADR-071 combinations:** 126
- **Current total:** **14,992 finite combinations — PASS**

## A. Current-disposition causal authorization fence — 48 combinations

Dimensions:

```text
disposition: NORMAL | CANCEL | COMPENSATE
operation stage: NONE | ATTEMPT_ABSENT | COMMITTED_UNRESOLVED | REALIZED
effect class: NOMINAL | COMPENSATION
current exact plan authorization: absent | present
```

Required properties:

```text
CANCEL + old nominal ATTEMPT whose effect is absent
→ BLOCK new nominal effect

COMPENSATE + old nominal ATTEMPT whose effect is absent
→ BLOCK old nominal retry

COMMITTED_UNRESOLVED / REALIZED
→ OBSERVE_RECOVER
→ historical operation knowledge is not converted into fresh mutation authority

COMPENSATE + compensation effect
→ CAUSE only when the current exact compensation plan authorizes it
```

Result: **PASS (48)**.

## B. Transactional managed-authoring-ref deletion — 24 combinations

Dimensions:

```text
ref binding: UNMANAGED | MANAGED
prepared write-ahead persistence: failed | durable
Git transaction outcome: ABORT | COMMIT
associated group state: UNREALIZED | PROMOTED | PARTIAL
```

Required properties:

```text
UNMANAGED deletion
→ semantically neutral

MANAGED + prepared persistence failure
→ deletion must not be permitted to commit

MANAGED + durable prepare + ABORT
→ no committed abandonment

MANAGED + durable prepare + COMMIT + UNREALIZED
→ CANCEL disposition

MANAGED + durable prepare + COMMIT + PROMOTED
→ branch cleanup only; historical success unchanged

MANAGED + durable prepare + COMMIT + PARTIAL
→ ADR-055 partial settlement; no history erasure
```

Result: **PASS (24)**.

## C. External/provider cancellation-race classification — 54 combinations

Dimensions:

```text
committed abandonment event: no | yes
promotion evidence: ABSENT | COMMITTED_UNRESOLVED | REALIZED
external movement: NONE | OBSERVED | LATER_DRIFT
causal order evidence: PRE_ABANDON | POST_ABANDON | UNKNOWN
```

Required properties:

```text
pre-abandon committed/realized promotion
→ recover/adopt historical realization

post-abandon attempt/effect
→ CANCEL dominates new managed realization authority

post-terminal later unrelated movement
→ external history drift; no group resurrection

unmanaged external movement + causal order UNKNOWN
→ fail closed for terminal semantic classification
→ do not manufacture order from independent clocks
```

Result: **PASS (54)**.

## Native Git `reference-transaction` regression

`git-reference-transaction-abandonment-smoke-v1.sh` was executed with Git 2.47.3 and verifies:

```text
native branch deletion reaches reference-transaction prepared
native branch deletion reaches reference-transaction committed
the update names refs/heads/<branch> with all-zero new OID
non-zero prepared hook aborts the deletion
aborted deletion leaves the branch present
```

Result:

```text
reference-transaction managed deletion commit: PASS
reference-transaction prepared failure aborts deletion: PASS
```

The smoke intentionally does not assume that every Git ref update supplies a non-zero exact old OID to the hook. Git documents all-zero old values for force-style updates; ADR-071 therefore permits exact read-only preimage resolution during the prepared phase when needed.

## Retained architecture properties

The v37 families remain retained, including ADR-069 invocation/group occurrence identity, group-local exact-state freeze, descendant restack, ADR-068 historical cancellation/settlement constraints as amended by ADR-071, ADR-066 route-conformant realization, and the older exact Git/provider recovery families.

## Backlog impact

The verification gap tracked as **30.48 is closed**.

The audit does **not** claim that `reference-transaction` creates a distributed transaction with GitHub/GitLab or arbitrary external Git writers. ADR-071 explicitly keeps genuinely unprovable cross-system causal ordering fail-closed.

## Total

```text
retained v37:       14,866
ADR-071 new:           126
--------------------------
v38 total:          14,992
```

**Verdict: PASS.**
