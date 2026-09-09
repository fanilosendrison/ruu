# ADR-054 — Separate PromotionUnit completion, ConvergenceUnit closure, and retirement

- **Status:** Accepted
- **Date:** 2026-09-06
- **Closes:** backlog 30.24
- **Amends:** ADR-014, ADR-021, ADR-039, ADR-042, ADR-046, ADR-049, ADR-053 and the ConvergenceUnit lifecycle/retention model

## Context

A repository-local PromotionUnit is an immutable exact-state snapshot. A ConvergenceUnit is a longer-lived logical development lineage that may produce multiple exact snapshots over the lifetime of one logical ship. These two objects therefore cannot share one completion boundary.

The distinction becomes correctness-critical after ADR-053. A PR may receive `CHANGES_REQUESTED` long after the coding session that produced its current head has ended. The External Control Plane can start a new correction continuation, reactivate the existing ConvergenceUnit(s), create new ContributionUnits, and later let the same immutable PromotionGroup resolve to new exact PromotionUnits. Thus a locally promoted exact snapshot does not necessarily mean its ConvergenceUnit can never be written again.

The cross-repository case makes the failure mode explicit. For one PromotionGroup `G = {XA, XB}` projected to repositories A and B, repository A may already be promoted while repository B is still in review. A later review correction on B can semantically require a companion correction in A. If `XA` were irreversibly retired merely because A's exact PromotionUnit reached `PROMOTED`, the architecture would have closed the development lineage before the logical ship was terminally settled.

Backlog 30.24 therefore needs to separate:

1. completion of one exact repository-local PromotionUnit;
2. semantic closure of a ConvergenceUnit lineage for the logical ship(s) that still reference it;
3. operational retirement of that lineage after correctness-critical recovery/resource dependencies are gone;
4. physical ref/audit retention after retirement.

This ADR deliberately does **not** define the detailed roll-forward/compensation semantics of backlog 30.25. It defines only the retirement barrier that those future terminal settlement outcomes must satisfy.

## Decision

Backlog item **30.24 is closed**.

### 1. PromotionUnit `PROMOTED` means only that exact snapshot reached its terminal publication outcome

A PromotionUnit is immutable exact state. Its terminal success means:

```text
PromotionUnit P = exact repository-local member snapshot
P PROMOTED
→ this exact snapshot reached/adopted its authoritative promotion outcome
```

It does **not** by itself mean:

```text
all logical work for the ConvergenceUnit is permanently closed
all repositories in the logical ship are settled
no review-correction continuation can still require new authoring
all recovery/audit refs may be deleted
```

Therefore the following implication is forbidden:

```text
PromotionUnit PROMOTED
⇒ referenced ConvergenceUnit RETIRED
```

### 2. A ConvergenceUnit stays reactivable while any relevant logical ship remains nonterminal

For ConvergenceUnit `X`, define the set of durable PromotionGroups that reference `X` and are still relevant to the logical publication lineage.

`X` MUST NOT become semantically closed merely because one repository-local projection has promoted. In particular:

```text
PromotionGroup G spans A + B
A projection PROMOTED
B projection REVIEWING / BLOCKED / otherwise nonterminal
→ G is not terminally settled
→ XA and XB remain eligible for explicit ADR-053 semantic reactivation
```

A cross-repository local success therefore does not collapse the higher-level ship boundary.

### 3. ConvergenceUnit `PROMOTED` is the semantic no-more-authoring boundary

A ConvergenceUnit may enter `PROMOTED` only when all of the following hold:

```text
1. every relevant PromotionGroup/promotion obligation referencing X is terminally settled;
2. no current durable ReviewCorrectionDemand or other authoring/reconciliation obligation can still reactivate X within those ships;
3. no current PromotionGroup resolution/revision obligation requires X to remain semantically mutable;
4. the transition is adopted under current expected-state/CAS guards.
```

For the ordinary successful path:

```text
all repository-local PromotionUnits for G promoted
→ G = ALL_PROMOTED
→ G is terminally settled successfully
```

Governing ADRs now define the other terminal dispositions used by this closure barrier: ADR-055 defines `COMPENSATED` forward settlement after realized partial effects, ADR-068 defines `CANCELLED` explicit non-delivery settlement before any promotion effect realizes, and ADR-067 defines repository-local PromotionUnit `SUPERSEDED` without treating it as group settlement. `CANCELLED` gates the distinct `ABANDONING` lineage-disposition path rather than silently converting an unrealized lineage into successful `PROMOTED` closure.

Once `X = PROMOTED`:

```text
new ContributionUnit attachment to X is forbidden
ADR-053 semantic reopen of X is forbidden
later newly discovered semantic work requires a new ConvergenceUnit/new ship lineage
```

Thus `PROMOTED` on a ConvergenceUnit means: **this development lineage is semantically closed for the settled ship(s)**.

### 4. `PROMOTED` is still not `RETIRED`

A semantically closed ConvergenceUnit may still be needed operationally for:

```text
Operation/Attempt/Observation/Adoption recovery
exact-state provenance
pending reconciliation/adoption records
correctness-critical reachability anchors
final target/provider observation
```

Therefore:

```text
ConvergenceUnit PROMOTED
→ not automatically RETIRED
```

A ConvergenceUnit may enter `RETIRED` only when no correctness-critical live obligation requires it as a mutable/recovery resource and all required terminal effects have been durably observed/adopted.

Conceptually:

```text
PROMOTED
+ no nonterminal operation/recovery dependency requiring this lineage/ref
+ no outstanding authoring/reconciliation demand
+ terminal settlement already durable
→ RETIRED
```

`RETIRED` means **Ruu no longer needs the ConvergenceUnit as a live operational resource**. It does not mean historical identity/audit data is deleted.

### 5. ABANDONING follows an explicit higher-level disposition and the same retirement barrier

ADR-068 sharpens the previously generic abandonment path. Ordinary authoring branch/ref/worktree deletion has no ConvergenceUnit lifecycle meaning. For an ungrouped ConvergenceUnit, the External Control Plane may explicitly dispose the lineage before promotion binding. For a group-bound ConvergenceUnit, member-local abandonment cannot strand or mutate an immutable PromotionGroup: every relevant ship that would otherwise require delivery must first have an applicable terminal disposition, principally ADR-068 `CANCELLED` for a still-unrealized withdrawn group.

```text
explicit applicable lineage/group disposition
+ no replacement/nonterminal group still requires X
+ no current authoring/reconciliation demand
→ ABANDONING
→ recovery/resource guards clear
→ RETIRED
```

If another relevant group remains nonterminal or a replacement group still uses the lineage, cancellation of one group does not move `X` to `ABANDONING`. If existing relevant terminal settlements drive the ordinary ADR-054 `PROMOTED` closure, history is not rewritten as abandonment.

Abandonment cannot be used as a shortcut around unresolved publication/recovery effects.

### 6. Retirement and physical ref deletion are separate

After `RETIRED`, a Ruu-controlled historical ConvergenceUnit ref is no longer correctness-required merely to keep the lifecycle live. It becomes **GC-eligible by lifecycle**, subject to any other reachability/recovery references and retention policy:

```text
ConvergenceUnit RETIRED
→ historical internal ref may become GC_ELIGIBLE
```

This is not an instruction to delete it immediately.

The same separation used by ADR-042 applies:

```text
logical terminality
≠ recovery sufficiency
≠ GC eligibility
≠ physical deletion
```

Physical cleanup remains best-effort/idempotent after explicit eligibility proof.

### 7. V1 built-in historical internal-ref retention is `KEEP`

For v1 zero-config behavior, Ruu does **not** automatically delete retired historical internal ConvergenceUnit refs:

```text
built_in_retention_policy = KEEP
```

A future explicit policy may allow bounded deletion/archival after GC eligibility, but it MUST NOT remove a ref/object still required by an unresolved operation, recovery path, active ship lineage, or declared audit-retention requirement.

The purpose of `KEEP` is conservative reachability and audit/reproduction simplicity, not lifecycle authority. Retained refs do not make a retired ConvergenceUnit active again.

Provider-owned/provider-facing submission-ref deletion remains governed by ADR-049/provider semantics and is never the durable identity/audit record. This ADR does not require a provider to preserve a merged PR branch indefinitely.

### 8. Durable logical/audit history is independent from physical ref retention

The CoordinationStore retains durable logical history sufficient to reconstruct:

```text
ConvergenceUnit identity/lifecycle
PromotionGroup memberships and terminal settlements
immutable PromotionUnit identities/exact OIDs
submission revisions/provider identities
Operation/Attempt/Observation/Adoption history
relevant provenance references
```

according to the architecture's audit/retention contract.

V1 may retain terminal coordination metadata indefinitely, consistent with ADR-042. Physical Git-object/ref cleanup never authorizes deletion of durable logical identity/history by itself.

This ADR closes **historical managed ref lifecycle semantics**, not the separate backlog 30.28 verification-evidence persistence/reuse schema and retention questions.

### 9. Multiple/superseding PromotionGroups are handled by the universal quantifier

If ConvergenceUnit `X` is referenced by more than one still-relevant group (for example because a later explicitly declared superseding ship also references the same not-yet-closed lineage), completion of one group is insufficient:

```text
RetirableSemantically(X)
iff
for every relevant group G referencing X:
    G is terminally settled
and no current authoring/reconciliation demand can reopen X
```

Once `X` has itself entered `PROMOTED`, later semantic work cannot attach another group to reopen that lineage; it requires a new ConvergenceUnit identity.

### 10. The resulting lifecycle has three distinct completion meanings

```text
PromotionUnit P PROMOTED
→ one exact repository-local snapshot is done

ConvergenceUnit X PROMOTED
→ X's development lineage is semantically closed for all relevant settled ships

ConvergenceUnit X RETIRED
→ X is no longer required as a live operational/recovery resource
```

These meanings MUST NOT be conflated.

## Consequences

- Cross-repository partial promotion remains correct: one locally promoted repository does not prematurely close its ConvergenceUnit while the logical ship remains open elsewhere.
- ADR-053 review corrections can reactivate existing group members until the ship terminally settles.
- Once the ship is terminally settled and the ConvergenceUnit is `PROMOTED`, later bugs/features become new work rather than mutation of historical ship lineage.
- `RETIRED` becomes an operational resource-lifecycle state rather than a synonym for “merged”.
- Git ref cleanup is safe and conservative: correctness first, GC eligibility second, physical deletion last.
- V1 avoids arbitrary time windows and defaults to keeping retired historical internal refs.
- ADR-055 subsequently defines cross-repository compensation/roll-forward terminal outcomes without reopening the retirement semantics.

## Rejected alternatives

### `PromotionUnit PROMOTED → ConvergenceUnit RETIRED`

Rejected. A repository-local exact snapshot can finish while another repository in the same logical ship remains in review or later causes a cross-repository correction.

### Retire each ConvergenceUnit as soon as its repository-local projection merges

Rejected. This makes ADR-053 same-ship correction impossible during partial cross-repository progress.

### Keep a ConvergenceUnit re-openable forever after successful ship settlement

Rejected. Historical ship identity would never acquire a stable closure boundary; later unrelated fixes could mutate the meaning of old publication lineage.

### Delete refs immediately on retirement

Rejected. Lifecycle terminality is not proof that no recovery/audit/reproduction dependency remains.

### Choose an arbitrary default time window such as 7/30/90 days

Rejected for v1. There is no evidence-based duration yet, and retained internal refs are cheap compared with the correctness/audit ambiguity introduced by premature deletion. Built-in v1 behavior is `KEEP`.

## Relationship to prior ADRs

Builds on ADR-014 cross-repository non-atomic progress, ADR-021 provider-wait/reopen semantics, ADR-042 recovery-resource lifecycle, ADR-046 immutable PromotionGroups, ADR-049 submission identity/ref separation, and ADR-053 durable review correction. Amends the main ConvergenceUnit lifecycle so PromotionUnit terminality, ConvergenceUnit semantic closure, operational retirement, and physical retention are four distinct concerns.

Closes backlog **30.24**. ADR-055 subsequently closes 30.25, ADR-056 closes 30.26, ADR-057 reclassifies development-validation execution, and ADR-058/ADR-059 close 30.27; the remaining genuine open core items are 30.28, 30.34, and 30.36; 30.39 is already closed by ADR-048.

## Amendment by ADR-055

ADR-055 defines `ALL_PROMOTED` and `COMPENSATED` terminal settlement forms. ADR-068 additionally defines `CANCELLED` for explicit withdrawal before any promotion effect has realized and after every still-realizing/uncertain managed effect is eliminated or resolved. `ALL_PROMOTED` is normal successful settlement over the current exact repository projection mapping. `COMPENSATED` is an explicit terminal semantic settlement requiring current External Control Plane compensation intent/completion plus independent observation/adoption of every exact forward Git/provider effect declared required by the plan. `CANCELLED` is a non-delivery terminal disposition and gates `ABANDONING` rather than silently converting an unrealized lineage into `PROMOTED`. `PARTIALLY_PROMOTED` and active settlement/cancellation recovery demands remain nonterminal.

## Amendment — ADR-065 (2026-09-07)

`PromotionUnit PROMOTED` now explicitly requires durable adoption of an ADR-065 exact target realization proof. Provider-submission terminality or provider `MERGED` state cannot by itself complete a PromotionUnit. Downstream ConvergenceUnit closure/retirement semantics remain unchanged and therefore inherit this stronger local completion boundary.

## Amendment by ADR-067 — obsolete exact PromotionUnits terminalize as SUPERSEDED

When the same immutable PromotionGroup/repository projection adopts a different current exact PromotionUnit, an older unpromoted PromotionUnit may terminalize as `SUPERSEDED` once no unresolved committed/uncertain promotion effect can still realize and no correctness-critical recovery operation requires it to remain nonterminal. A previously `PROMOTED` exact snapshot remains `PROMOTED` historical fact.

If an old non-current PromotionUnit still has an in-flight/uncertain external effect, it initiates no new promotion mutation but remains recovery-visible until exact observation establishes route-conformant realization (`PROMOTED`) or safe non-realization/closure (`SUPERSEDED`).

## Amendment by ADR-069

A live ConvergenceUnit may be referenced by several independent PromotionGroups with different exact group-local snapshots. Later ordinary authoring for one/new group does not mutate older groups. Terminal PromotionGroups freeze their exact resolution; ConvergenceUnit closure/retirement continues to quantify over all relevant group and authoring/reconciliation obligations.

