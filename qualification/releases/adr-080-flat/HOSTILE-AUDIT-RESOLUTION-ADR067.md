# Ruu — Hostile Audit Resolution through ADR-067

- **Date:** 2026-09-07
- **Source audit:** `HOSTILE-AUDIT-ADR065.md`
- **Current state-space audit:** `STATE-SPACE-AUDIT-v34.md`

## Resolution summary

### H1 — Native ancestry bypassed required provider governance — CLOSED by ADR-066

Old invalid shortcut:

```text
C == O or C ancestor-of O
→ PROMOTED regardless of route
```

Current rule:

```text
DIRECT
→ native C realization is sufficient when DIRECT is route-compatible

PROVIDER_SUBMISSION
→ exact C→H projection
→ exact H→R provider finalization
→ exact R→O target proof
→ only then PROMOTED
```

Candidate inclusion can no longer bypass a provider-required route.

### H2 — ADR-065 bound the wrong object across restack — CLOSED by ADR-066

ADR-050 already distinguishes immutable internal candidate `C` from provider-facing restacked head `H`. ADR-066 makes that distinction normative in final proof:

```text
C → H  Ruu deterministic projection
H → R  provider finalization
R → O  authoritative Git inclusion
```

The provider is never required to attest an internal `C` it did not receive.

### H3 — Crash + policy drift conflated adoption with new authorization — CLOSED by ADR-066

Route-specific effect commitment separates history from future authority:

```text
old policy
→ may justify adoption of an effect proven already committed while it applied
→ never authorizes a new effect/retry capable of causing the mutation
```

Provider commitment is durable provider acceptance of the exact finalization operation. DIRECT commitment is the direct target mutation itself. Unknown commitment timing across policy drift fails closed.

### H4 — Post-PROMOTED drift observability contradiction — CLOSED as historical semantics by ADR-066

`PromotionUnit PROMOTED` is explicitly historical completion, consistent with ADR-054. V1 does not continuously resweep terminal PromotionUnits merely to prove permanent target inclusion. A later force rewrite does not retroactively erase the historical promotion; if independently discovered, it is a new integrity/reconciliation fact.

### H5 — 30.36 simultaneously closed and open — CLOSED as documentary inconsistency

The stale main-spec `## 30.36 REVIEW_NOT_REQUESTED eligibility policy` text was replaced with the already-accepted ADR-062 no-projection default. Backlog/main now agree that 30.36 is closed.

### H6a — PromotionUnit ABANDONED / obsolete exact unit lifecycle — CLOSED by ADR-067

PromotionUnit generic `ABANDONED` is removed. When current `(PromotionGroup, repository)` resolution replaces `P0` by `P1`, the exact supersession relation is recorded. An unrealized old unit becomes `SUPERSEDED` only after no unresolved committed/uncertain external effect can still realize it. A historically promoted old unit remains `PROMOTED`.

### H6b — ConvergenceUnit ABANDONING after PromotionGroup binding — OPEN as 30.41

The hostile review also exposed older ConvergenceUnit lifecycle wording:

```text
READY_INTERNAL / PROMOTION_BOUND
→ abandon/disposition
→ ABANDONING
```

No current ADR fully specifies what terminal group/ConvergenceUnit disposition is legal when an immutable PromotionGroup already references that lineage, especially before any effect has shipped. ADR-055 forbids silent partial abandonment but does not define a general pre-promotion cancellation model.

This ambiguity is now explicit backlog **30.41**. Until resolved, generic abandonment cannot silently retire a group-bound ConvergenceUnit.

## Additional guard recovered during discussion

`ruu` must not require all ordinary Git mutations to pass through itself.

```text
DIRECT route
+ legitimate user/agent direct Git advancement
+ exact route-compatible target realization
→ reconcilable/adoptable
```

Route conformance is not process attribution. This guard prevents the proof model from turning `ruu` into a Git monopoly.

## Audit result

The architectural closure claim from ADR-065 is withdrawn. ADR-066/067 close H1, H2, H3, H4, H5 and PromotionUnit portion H6; one narrow ConvergenceUnit disposition question remains open as 30.41.


## 2026-09-07 ratification note — H4

H4's ADR-066 closure is explicitly user-ratified: `PROMOTED` is historical terminal completion, later target drift is a separate new fact, and terminal PromotionUnits are not reopened merely because later target history no longer contains the realized result. State-space audit v36 adds a dedicated 12-case family for this semantics.
