# ADR-067 — Terminalize obsolete unpromoted PromotionUnits by current-resolution supersession

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 067
- **Amends:** ADR-036, ADR-042, ADR-045, ADR-046, ADR-047, ADR-049, ADR-054, ADR-055 and the PromotionUnit lifecycle

## Context

ADR-045 makes every PromotionUnit an immutable content-addressed exact-state snapshot. ADR-046/047 already allow one immutable PromotionGroup to resolve repeatedly as its member ConvergenceUnits reopen and later reach new exact `READY_INTERNAL` states.

Therefore the same stable repository-local projection boundary may move from:

```text
(G, RepoR) → P0(C0)
```

to:

```text
(G, RepoR) → P1(C1)
```

without mutating either the PromotionGroup or `P0`.

The current requirements correctly say `P0` becomes stale/ineligible when its source state is no longer current, but its generic lifecycle still contains vague `ABANDONED` wording and the global sweep treats every nonterminal PromotionUnit as a live managed obligation. Without a precise disposition, an obsolete `P0` can remain globally nonterminal forever.

The architecture also must not erase an already-promoted historical snapshot, nor ignore an in-flight external effect for `P0` that may still realize after `P1` becomes current.

## Decision

### 1. No new PromotionGroupResolution semantic object is introduced

ADR-046/047's current-resolution mapping is already sufficient:

```text
PromotionGroup G
→ current RESOLVED(repository_id → PromotionUnitRef) mapping
```

The group remains immutable. A changed exact member state causes a different content-addressed PromotionUnit and a new current mapping under the existing snapshot/CAS rules.

### 2. Supersession is derived from replacement in the current repository projection

When a current resolution for the same stable projection boundary changes:

```text
old: (G,R) → P0
new: (G,R) → P1
P0 != P1
```

`ruu` durably records the exact replacement relation:

```text
P0.superseded_by = P1
```

This relation is mechanical consequence of the adopted current group resolution. It does not require the Development System to make a separate semantic declaration that `P0` and `P1` represent the same code meaning.

The semantic decision already happened upstream when the existing ConvergenceUnit lineage was legitimately reopened/reauthored and reached a new exact state.

### 3. `SUPERSEDED` is the terminal disposition for an obsolete unrealized PromotionUnit

If all of the following hold:

```text
P0 is no longer the current (G,R) projection
P0 has not already become PROMOTED
no unresolved committed/uncertain promotion effect for P0 can still realize
no correctness-critical recovery operation requires P0 to remain promotion-nonterminal
```

then:

```text
P0 → SUPERSEDED
```

`SUPERSEDED` means:

```text
this exact immutable snapshot is no longer the current promotion obligation
and will not itself initiate further promotion work
```

It remains durable audit history and is never physically rewritten into `P1`.

### 4. A PROMOTED old snapshot is never superseded retroactively

If:

```text
P0 == PROMOTED
new current mapping becomes P1
```

then:

```text
P0 remains PROMOTED
P1 becomes the new current exact promotion obligation
```

`P0 PROMOTED` is a historical fact under ADR-054/066. Later authoring does not rewrite that history.

### 5. An unresolved committed effect delays terminal supersession

Replacement in the current mapping does not authorize forgetting an external effect already in flight.

If `P0` is no longer current but has an ADR-042/066 effect that is committed, possibly committed, or otherwise requires exact recovery observation:

```text
P0 is non-current
P0.superseded_by = P1
but P0 does not initiate new promotion mutations
and its exact recovery obligation remains globally visible
```

Recovery then resolves the historical effect:

```text
route-conformant realization of P0 is proven
→ P0 becomes/remains PROMOTED historical fact

exact observation proves the effect did not realize / was cancelled / is no longer possible
+ recovery resources/operations can be terminally closed
→ P0 becomes SUPERSEDED

outcome cannot be established
→ remain recovery-nonterminal / UNKNOWN_INCONSISTENT as applicable
```

This prevents a new current snapshot from hiding an older side effect that may already have escaped into the provider/target.

### 6. `SUPERSEDED` replaces vague PromotionUnit `ABANDONED` semantics

V1 removes generic `ABANDONED` from the PromotionUnit lifecycle.

For current architecture, an obsolete exact PromotionUnit has one precise no-success terminal disposition:

```text
SUPERSEDED
```

A future genuinely user-directed pre-promotion cancellation/disposition model, if needed, requires a separate explicit ADR. `ABANDONED` is not retained as a catch-all state.

This does not alter ADR-055's rule that a partially promoted cross-repository ship cannot silently disappear. Group-level settlement remains `ALL_PROMOTED`, `COMPENSATED`, or another explicitly governed future terminal settlement.

### 7. Global sweep semantics become finite

ADR-036 continues to process all nonterminal managed obligations.

Once `P0 = SUPERSEDED` and no separate Operation/Attempt/recovery obligation remains:

```text
P0 itself leaves the nonterminal managed-obligation universe
```

Historical metadata remains retained according to audit/retention rules.

### 8. Submission identity remains stable when the logical projection remains the same

Superseding `P0` with `P1` under the same `(PromotionGroup, source repository, publication destination)` does not by itself create a new logical submission identity.

ADR-049/055 continue to govern provider surfaces:

```text
current PublicationEpisode nonterminal
→ update/revise the same episode to the new exact current revision when allowed

current PublicationEpisode terminal
+ same nonterminal logical ship still needs publication
→ create next PublicationEpisode
```

The obsolete PromotionUnit lifecycle and provider publication-episode lifecycle remain separate.

## Consequences

- Immutable PromotionUnits never change candidate identity.
- The already-existing current PromotionGroup resolution mechanism is reused; no duplicate generation object is invented.
- Obsolete exact PromotionUnits stop leaking forever into the global nonterminal sweep.
- Historical promoted snapshots remain true historical facts.
- In-flight side effects cannot be hidden by supersession.
- Vague PromotionUnit `ABANDONED` semantics are removed from v1.

## Related decisions

ADR-036, ADR-042, ADR-045, ADR-046, ADR-047, ADR-049, ADR-053, ADR-054, ADR-055, ADR-066.

## Amendment by ADR-068 — supersession and group cancellation are distinct

`SUPERSEDED` remains a repository-local disposition for an obsolete exact PromotionUnit when the same immutable group/repository current mapping moves to a newer exact PromotionUnit. ADR-068 `PromotionGroup CANCELLED` instead withdraws the entire still-unrealized logical ship under explicit external authority. Ordinary branch deletion triggers neither state. A group cannot terminalize `CANCELLED` while any old/current PromotionUnit has a realized or unresolved still-realizing effect; such effects remain subject to ADR-066/067 recovery and ADR-055 settlement where applicable.

## Amendment by ADR-069

A repository-local PromotionUnit becomes non-current under the same PromotionGroup only when that **same nonterminal group** legitimately adopts a newer group-local exact resolution through explicit group-bound correction/reconciliation authority. Unrelated live ConvergenceUnit movement or a later ordinary PromotionGroup does not supersede it. Terminal PromotionGroups are resolution-frozen.

