---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Cancel unrealized PromotionGroups explicitly and keep Git artifact deletion semantically neutral"
id: "ADR-068"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "948b4a47849766fb16cf6942efdbd0f6e9947dd47dce3ce7138c7bbffb2545fe"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends:
    - "ADR-038"
    - "ADR-046"
    - "ADR-054"
    - "ADR-055"
    - "ADR-067"
  supersedes: []
  confirms: []
governs: []
---

# ADR-068 — Cancel unrealized PromotionGroups explicitly and keep Git artifact deletion semantically neutral

- **Status:** Accepted
- **Date:** 2026-09-07
- **Closes:** backlog 30.41
- **Amends:** ADR-038, ADR-046, ADR-054, ADR-055, ADR-067 and the main lifecycle/External Control Plane contract
- **Subsequently amended by:** ADR-071 (managed authoring-ref deletion is the native abandonment signal; current-disposition causal fencing)

## Context

`ruu` deliberately coexists with ordinary Git. A user or agent may create or delete ordinary authoring branches, refs and worktrees without routing those actions through `ruu`. ADR-038 already establishes that a ContributionUnit is a durable logical identity independent of those editing artifacts and that deleting an editing branch/ref/worktree does not itself mean `CLOSED`, semantic abandonment, remote-deletion intent or local-recreation intent.

A different lifecycle question appears after the External Control Plane has already declared an immutable closed PromotionGroup:

```text
G = {X_A, X_B, ...}
```

The group declaration means that these logical ConvergenceUnits belong to one ship. Because `G` is immutable, silently retiring one group-bound ConvergenceUnit would not remove it from `G`; it would instead strand the group's terminal-settlement obligation. ADR-055 already rejects silent abandonment after one or more repository-local promotion effects have been realized, but no exact pre-promotion cancellation settlement existed for a group with zero realized effects.

The architecture therefore needs to distinguish three independent events:

```text
ordinary Git artifact deletion
!= ContributionUnit / ConvergenceUnit lifecycle disposition
!= PromotionGroup cancellation
```

The key requirement is to close the logical ship without giving branch deletion hidden protocol meaning and without making PromotionGroup membership mutable.

## Decision

### 1. Ordinary authoring-artifact deletion remains semantically neutral

A user or agent may normally delete an ordinary contribution/authoring branch, ref or worktree in its development session:

```text
git branch -D topic
```

That operation is ordinary Git artifact management. By itself it means none of:

```text
ContributionUnit CLOSED
ConvergenceUnit ABANDONING
PromotionGroup CANCELLED
remote deletion intent
local recreation intent
semantic abandonment
```

`ruu` observes/reconciles the durable exact managed state that actually exists. It MUST NOT reinterpret ordinary branch/ref/worktree deletion as a command in the `ruu` protocol, and it MUST NOT require users or agents to replace normal Git deletion with a `ruu` cancellation operation.

If an already-created exact managed checkpoint remains recoverable, ordinary convergence may continue from that OID even after the editing artifact disappears. If required exact state is unrecoverable, the existing localized recovery/data-loss semantics apply. Neither case changes the semantic meaning of the deletion itself.

### 2. Group-bound cancellation is a PromotionGroup disposition, not a member mutation

Once a ConvergenceUnit `X` is referenced by immutable PromotionGroup `G`, the External Control Plane cannot cancel only `X` *inside that group* by mutating membership or by asking `ruu` to retire `X` locally.

If the previously declared ship is no longer desired, the semantic authority acts on the group:

```text
PromotionGroup G
→ explicit current cancellation intent
→ exact cancellation guards satisfied
→ CANCELLED
```

`CANCELLED` is a terminal **PromotionGroup settlement**. It means:

> the External Control Plane explicitly withdrew the still-unrealized ship represented by this immutable PromotionGroup, and `ruu` established that no managed promotion effect for that group has been realized or remains able to realize through an unresolved committed/uncertain effect.

`CANCELLED` does not mean the group's historical identity or membership disappears. `G` remains immutable audit history.

### 3. `CANCELLED` requires explicit current semantic authority

`ruu` MUST NOT infer cancellation from:

```text
branch/ref/worktree deletion
ContributionUnit closure
absence of current session
lack of recent activity
provider submission inactivity
review latency
policy drift
one member becoming obsolete
caller identity
```

Cancellation requires an explicit current External Control Plane / Development System declaration bound to `promotion_group_id` and adopted under the ordinary managed-state currentness/CAS discipline.

An old cancellation declaration cannot authorize new provider/Git cancellation effects after it becomes stale. Historical authorization may explain already-committed cancellation effects under ADR-066, but never provides future mutation authority.

### 4. `CANCELLED` is available only before any promotion effect has been realized

Before adopting `G = CANCELLED`, `ruu` must establish over **all current and historical repository-local PromotionUnits/publication episodes belonging to G**:

```text
zero route-conformant realized target-promotion effects
+ zero unresolved committed effects that can still realize promotion
+ zero UNKNOWN/uncertain promotion effects that can still realize promotion
+ every managed provider/publication surface is terminally non-realizing,
  revoked/closed/cancelled where necessary, or otherwise proven unable
  to complete the cancelled ship
+ correctness-critical recovery observations/adoptions complete
```

Therefore:

```text
no realized effect + no in-flight/uncertain realizing effect
→ group cancellation may terminalize as CANCELLED

realized effect exists
→ CANCELLED forbidden

committed/uncertain effect may still realize
→ cancellation not yet terminal; recover/observe first
```

A provider submission merely being open is not automatically a committed finalization effect, but `G` cannot become terminal `CANCELLED` while a managed provider surface can still realize the ship under outstanding managed authority. `ruu` must first establish a terminal non-realizing provider state using currently authorized provider mechanics where such a state transition is required.

### 5. Already-realized effects are never rewritten as cancellation

If any repository-local promotion effect belonging to `G` has already been route-conformantly realized/adopted, cancellation is no longer a legal history for that group.

For a multi-repository group:

```text
at least one repository promoted
+ another repository not yet promoted
→ ADR-055 PARTIALLY_PROMOTED / forward settlement semantics
→ never CANCELLED
```

The group continues toward `ALL_PROMOTED` or, when explicitly selected under ADR-055, terminal `COMPENSATED` settlement after the required forward effects.

For a singleton/single-repository group whose required promotion effect is already realized, ordinary successful terminal settlement is `ALL_PROMOTED`; later product intent may create new forward development/promotion work but cannot relabel the historical success as `CANCELLED`.

### 6. Changing ship membership means cancel old G and declare a new immutable G'

Suppose the originally declared ship was:

```text
G1 = {X_A, X_B}
```

and the External Control Plane later wants to ship only `X_A` before any effect of `G1` has been realized.

It does not mutate `G1` into `{X_A}`. Instead:

```text
G1 = {X_A, X_B}
→ CANCELLED

G2 = {X_A}
→ newly declared immutable PromotionGroup
```

`G1` remains historical evidence of the withdrawn intent. `G2` is the new ship intent. If any `G1` effect was already realized, `G1` cannot use this cancellation path and the existing settlement rules apply.

### 7. PromotionGroup cancellation does not automatically abandon every member ConvergenceUnit

After `G = CANCELLED`, each member ConvergenceUnit is reconciled against **all** of its relevant groups and current authoring/reconciliation demands.

A member `X` does **not** enter `ABANDONING` merely because one group was cancelled if, for example:

```text
X is referenced by another nonterminal PromotionGroup
or
X is participating in a newly declared replacement group G'
or
current authorized authoring/reconciliation work still exists
or
another relevant terminal settlement means ordinary ADR-054 PROMOTED closure applies
```

The group cancellation only removes the cancelled group's obligation to realize that ship.

### 8. `ABANDONING` becomes a mechanically gated lineage-disposition state

For a ConvergenceUnit with no still-relevant successful/compensated promotion closure and no remaining nonterminal ship/authoring/reconciliation obligation, explicit semantic disposal may lead to:

```text
ACTIVE / READY_INTERNAL / PROMOTION_BOUND
→ ABANDONING
```

For a group-bound lineage, this is legal only after every relevant ship that would otherwise require it has a terminal disposition that permits non-delivery—principally `CANCELLED` under this ADR—and no replacement/nonterminal group still requires the lineage.

Conceptually:

```text
all relevant PromotionGroups terminal
+ no relevant group still requires delivery
+ no current authoring/reconciliation demand
+ explicit higher-level disposal authority where required
→ ABANDONING
→ recovery/resource guards clear
→ RETIRED
```

If any relevant group is `ALL_PROMOTED`, `COMPENSATED`, or otherwise satisfies the existing ADR-054 normal terminal-settlement path for that lineage, ADR-054's semantic `PROMOTED` closure remains the governing closure rather than rewriting history into abandonment.

For an ungrouped ConvergenceUnit, the External Control Plane may explicitly dispose the lineage before promotion binding; ordinary branch deletion still does not create that disposition automatically.

### 9. Cancellation is historical settlement, not perpetual exclusion from Git

After `G = CANCELLED`, users and agents remain free to use Git normally. A later unrelated/manual Git operation may happen to make some old candidate content reachable from a target. That does not reopen `G`, does not retroactively make `G` successful, and does not violate the cancellation record merely because Git history later contains overlapping content.

`CANCELLED` records the terminal disposition of the managed ship obligation, not a permanent prohibition on future Git states.

Likewise, if a user later wants that work shipped intentionally, the Development System creates the appropriate current authoring/convergence/promotion intent; it does not mutate or reopen the historical cancelled group.

## PromotionGroup settlement model after this ADR

The logical settlement dimension is now:

```text
OPEN / NONTERMINAL
ALL_PROMOTED   # terminal successful settlement of current exact mapping
COMPENSATED    # terminal explicit forward settlement after realized partial effects
CANCELLED      # terminal explicit withdrawal before any promotion effect realized
```

`PARTIALLY_PROMOTED` remains nonterminal progress, never cancellation.

## Recovery implications

Cancellation follows ADR-042/066 recovery discipline:

```text
semantic cancellation intent
→ exact cancellation Operation/Attempt persisted
→ provider/Git observations of any required non-realizing effects
→ Adoption under current managed-state CAS
→ PromotionGroup CANCELLED
```

Attempt metadata never proves that an external provider surface was actually closed/revoked. Exact observation is required before terminal adoption whenever external cancellation/non-realization effects are part of the proof.

If recovery cannot determine whether an already-authorized provider operation can still realize the ship:

```text
UNKNOWN / effect-acceptance uncertainty
→ fail closed
→ G remains nonterminal
```

## Consequences

- Ordinary Git remains ordinary Git; deleting an authoring branch carries no hidden `ruu` protocol semantics.
- PromotionGroup membership remains immutable.
- A withdrawn pre-promotion ship has a precise terminal settlement instead of stranding group-bound ConvergenceUnits.
- Cancellation cannot erase or relabel already-realized repository effects.
- In-flight/uncertain effects remain recovery-visible until they are proven realizing or terminally non-realizing.
- A membership change is represented by historical cancellation plus a new immutable group, not by editing the old group.
- `ABANDONING` is no longer a vague shortcut around group settlement; it is gated by higher-level terminal dispositions and recovery sufficiency.
- `ruu` receives no authority to decide that development work is unwanted. The semantic cancellation/disposal decision remains external.

## Rejected alternatives

### Interpret branch deletion as semantic abandonment

Rejected. It gives ordinary Git artifact operations hidden protocol meaning and makes two identical Git states ambiguous depending on user intent that Git cannot encode.

### Remove a cancelled member from an existing PromotionGroup

Rejected. PromotionGroup immutability is a core identity/provenance invariant.

### Allow `CANCELLED` after one repository already promoted

Rejected. It would erase a real historical effect and recreate the silent partial-abandonment problem rejected by ADR-055.

### Mark the group cancelled while a provider finalization may still complete

Rejected. Terminal cancellation must not coexist with an unresolved managed effect capable of realizing the ship.

### Require all branch deletion to go through Ruu

Rejected. `ruu` must coexist with normal Git usage rather than monopolize Git mutation.

## Backlog impact

Backlog **30.41 is closed**.

No core design backlog item remains open after this ADR. This statement is limited to the currently modeled architecture and does not imply that future hostile review cannot expose a new design question.
