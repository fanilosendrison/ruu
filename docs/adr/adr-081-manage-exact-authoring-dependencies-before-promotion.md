---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "normative"
name: "Manage exact authoring dependencies before promotion"
status: "accepted"
---

# ADR-081 — Manage exact authoring dependencies before promotion

- **Status:** Accepted — 2026-11-03
- **Decision order:** 081
- **Closes:** backlog 30.56
- **Engineering follow-ups:** [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1) and [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2)
- **Supersedes:** none
- **Amends/clarifies:** ADR-003, ADR-009, ADR-023, ADR-033, ADR-035, ADR-038, ADR-039, ADR-040, ADR-042, ADR-047, ADR-048, ADR-050, ADR-054, ADR-068, ADR-069, ADR-071, ADR-073, ADR-074, ADR-075, ADR-076, and ADR-078

## Context

Ruu permits ordinary native Git commits inside active managed ContributionUnit worktrees. Such commits are exact Git versions, but commit creation alone is not a Ruu checkpoint, handoff, completion, PromotionGroup, or publication event.

The existing dependency model in ADR-050 begins only after another promotion obligation is already known. It cannot represent this ordering:

```text
source ContributionUnit α
→ native exact commit A
→ no Ruu handoff or PromotionGroup yet

consumer ContributionUnit β
→ explicitly consumes α@A
→ authors exact state B
→ invokes Ruu before α
```

Requiring α to invoke first would export avoidable sequencing to the user. Consuming α's dirty worktree would make mutable staged, unstaged, untracked, ignored, generated, secret, or half-authored state into hidden durable history. Inferring the dependency from ancestry would confuse Git graph evidence with semantic authority.

The architecture therefore needs one durable authoring-level relation that can exist before promotion identity, preserve the exact consumed OID, retain that object through ref movement and Git garbage collection, and later enter ADR-050 without guessing which promotion occurrence owns the source obligation.

## Decision

### 1. ContributionUnit is the authoring-occurrence identity

`ContributionUnit` already is the stable repository-local bounded authoring occurrence. ADR-081 introduces no distinct `WorkOccurrence` identity.

The canonical source or consumer identity is:

```text
CanonicalContributionUnitRef = (
  repository_id,
  contribution_unit_id
)
```

Historical wording such as `ContributionUnit/work occurrence` refers to this same object. A separate `work_occurrence_id` is not part of the current v1 domain model. Binding generation remains a separate generation of the current editing-surface binding for the same ContributionUnit.

An exact authored version needs no redundant `ExactAuthoringVersion` object. Where exact source attribution is required, it is represented by:

```text
CanonicalContributionUnitRef
+ git_object_format
+ exact commit OID
```

Therefore:

```text
OID alone
!= semantic source identity

session / process / task / branch / worktree identity
!= semantic source identity
```

Two ContributionUnits that expose the same OID remain distinct possible semantic sources.

### 2. The Development System explicitly selects the source and exact version

The Development System may select a repository-local authoring dependency before the consumer's first managed write:

```text
AuthoringDependencySelection {
  consumer: CanonicalContributionUnitRef
  source: CanonicalContributionUnitRef
  git_object_format
  consumed_exact_oid
}
```

The source and consumer MUST be distinct ContributionUnits in the same authoritative repository. Cross-repository semantic coordination remains PromotionGroup-level coordination; a commit in one repository is not a Git base in another repository.

Selection is semantic authority owned by the Development System. Ruu MUST NOT manufacture it from:

```text
commit ancestry alone
file overlap
prompt or task similarity
session/process order
branch/ref/worktree names
recency
latest pending work
provider topology
```

The selection does not choose a PromotionGroup, PromotionUnit, submission parent, stack, or provider layout. Once the exact relation is adopted, Ruu owns its mechanical reconciliation.

### 3. Adoption requires exact Git truth and source attribution

The selected OID MUST resolve to an ordinary commit in the selected repository. At adoption, Ruu MUST prove all of:

```text
source ContributionUnit identity and binding are current and unambiguous
source disposition is not abandoned or unresolved
selected commit exists under the declared Git object format
selected commit is equal to or canonically reachable from the current
  source managed ref or latest authoritative source checkpoint
selected commit is a strict canonical descendant of the source
  ContributionUnit's exact authoring base at admission
canonical ancestry ignores replace/graft overlays and treats incomplete
  shallow history as unknown
```

The explicit selection supplies semantic dependency authority. The exact Git proof supplies object and lineage truth. Neither alone is sufficient.

The source worktree need not be clean. If its managed ref identifies exact commit `A` while the worktree also contains dirty state, the consumer may receive only `A`. Dirty filesystem/index state is neither inspected as the dependency version nor captured on the source's behalf.

Ruu MUST NOT silently snapshot, commit, stash, stage, copy, or otherwise make another active producer's dirty surface durable merely to satisfy a dependency.

### 4. Native commits remain facts; dependency adoption is the managed event

Ordinary native Git operations inside a managed authoring surface remain exact-state-rediscovered facts under ADR-074/075:

```text
commit
reset
merge
ordinary managed authoring ref-tip movement
```

Ruu does not journal each native commit as a managed business event. The managed fact is the explicit adoption of a selected source identity plus exact OID.

A native commit made during active authoring means only that an exact native Git version exists. It does not imply:

```text
semantic completion
ContributionUnit closure
managed checkpoint
frozen handoff
PromotionGroup creation
PromotionUnit creation
promotion readiness
publication readiness
end of turn or session
```

Thus:

```text
commit != completion

exact native authoring version
!= managed checkpoint / handed-off promotion state
```

### 5. Dependency adoption is atomic with durable object retention

An AuthoringDependency is not authoritative until the exact consumed commit has a Ruu-owned reachability root.

Adoption uses the ADR-042 recoverable-effect envelope. An immutable Operation/Attempt records the source/consumer identities, source binding generation, source exact lineage proof, object format, consumed OID, intended dependency identity, and a non-reused recovery-resource namespace.

The crash-safe sequence is:

```text
TX-A (durable semantic-selection linearization):
  create/reuse immutable dependency-adoption Operation
  persist the exact External Control Plane selection and expected source row/binding generation
  append fenced Attempt
  record expected AUTHORING_DEPENDENCY_OID_ANCHOR as REQUIRED
COMMIT

outside SQLite, under exact native-ref exclusion:
  revalidate source binding/ref and exact lineage
  create the Ruu recovery anchor at consumed_exact_oid
  observe exact anchor/ref/object state

TX-B:
  verify current run fence and immutable intent
  revalidate exact source ContributionUnit row version, binding generation,
    binding continuity, lineage proof, and non-abandoned disposition
  append exact Observation
  adopt AuthoringDependency by expected-state/CAS
  keep its recovery resource REQUIRED
COMMIT
```

The exact Git ref transaction MAY combine an exact no-op lock of the current source ref with expected-absent creation of the anchor so the recorded source preimage and anchor creation share one native serialization boundary. No SQLite transaction spans the Git effect.

Crash consequences are exact:

```text
before anchor creation
→ unresolved Operation/Attempt; no adopted dependency

after anchor creation but before adoption
→ required recoverable/orphan anchor; no adopted unanchored dependency

after adoption
→ dependency and REQUIRED anchor are durable and idempotent
```

TX-A is the durable semantic-selection boundary used to order a concurrently accepted source handoff. If a uniquely attributable qualifying source handoff is accepted after TX-A but before TX-B, TX-B or recovery MAY adopt the dependency directly in its resolved/same-group state after all anchor, source-checkpoint, target, disposition, and CAS predicates are revalidated. It MUST NOT strand the relation as raw merely because physical anchor/adoption work overlapped the source handoff.

If source binding/disposition changes after anchor creation but before TX-B, the stale CAS does not adopt the dependency; recovery reclassifies the exact selection as target-satisfied, source-resolved, reconciliation-required, stale, or closed without treating the anchor as authority.

Supported-harness pre-edit provisioning submits this dependency-adoption work as an authorized internal provisioning demand to the existing single-host OS-owned and SQLite-fenced ConvergenceEngine, then waits for the exact result before permitting the consumer's first write. It is not a work-bearing checkpoint invocation, creates no PromotionGroup, and requires no user-facing preflight command. Using the existing fenced executor avoids a second adoption-authority domain.

An adopted dependency without its exact reachable object is `UNKNOWN_INCONSISTENT` / `BLOCKED_MISSING_MANAGED_STATE`; it is never treated as satisfied.

### 6. The exact dependency identity and consumed OID are immutable

The dependency identity is a versioned domain-separated content address over one RFC 8785 JSON Canonicalization Scheme (JCS) object with exactly these semantic fields:

```json
{
  "schema": "Ruu/authoring-dependency/v1",
  "repository_id": "<opaque canonical repository ID>",
  "consumer_contribution_unit_id": "<opaque canonical ContributionUnit ID>",
  "source_contribution_unit_id": "<opaque canonical ContributionUnit ID>",
  "git_object_format": "sha1 | sha256",
  "consumed_exact_oid": "<lowercase full-width hexadecimal OID>"
}
```

IDs use their existing canonical UTF-8 string encodings. `git_object_format` uses Git's canonical algorithm name, and the OID width MUST match that format. Unknown fields/algorithms, Unicode-normalization changes to opaque IDs, abbreviated OIDs, uppercase hexadecimal, or non-JCS encodings are non-canonical.

```text
authoring_dependency_id = SHA-256(
  UTF-8(JCS(the exact object above))
)
```

The `schema` field provides domain separation; JCS member ordering and JSON string encoding provide an injective boundary without ambiguous concatenation.

Same identity plus same immutable definition is idempotent replay. Same identity plus different definition is an integrity failure. A changed source identity or consumed OID is a different dependency.

A consumer may carry a finite set of distinct dependency records. Duplicate adoption of the same exact relation is idempotent. A dependency cycle or unknown/multiply-bound source identity is invalid and fails closed.

The `consumed_exact_oid` never changes when the dependency later resolves. Logical source ownership and current source realization state are separate facts.

### 7. The ordinary path adopts dependencies before consumer authoring

The supported path selects and adopts authoring dependencies during pre-edit provisioning, before the consumer's first managed write and before mutation authority over the consumer's own managed surface is handed to the consumer.

The consumer's exact authoring base MUST canonically contain every selected dependency OID. For the ordinary single-source case:

```text
consumer initial exact base = consumed_exact_oid A
```

If a finite selected set has one existing exact commit that canonically contains every selected OID, that commit may be the single Git authoring base. ADR-081 does not synthesize an authoring-base merge. Incomparable selected commits with no already-existing exact containing base block consumer provisioning pending an explicit architecture/semantic resolution; dirty state is never used to bridge them.

This decision does not authorize rewriting or refounding a consumer that has already authored from another base. Possible future refoundation semantics are tracked non-normatively in [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2).

### 8. A clean native tip can become a managed checkpoint only at handoff

The current specification's dirty-surface checkpoint path remains unchanged. In addition, a frozen work-bearing handoff may adopt the current clean managed-ref tip as the latest authoritative managed checkpoint without creating another commit when:

```text
current managed binding and authoring authority are exact
handoff is frozen and bound to the logical invocation
current ref tip is an ordinary commit under the canonical ancestry contract
current ref tip descends the prior authoritative checkpoint or admitted base
no structural Git/observation inconsistency exists
exact claim, run fence, and managed-state CAS succeed
```

The handoff adoption is the managed checkpoint event. The earlier native commit creation remains an ordinary Git fact. A clean tip that is not handed off remains only native authoring state.

This rule allows both source and consumer to author with ordinary native commits while preserving:

```text
native commit creation != Ruu checkpoint adoption
```

### 9. Raw dependencies are durable localized obligations

After adoption and before promotion resolution, the relation is:

```text
RAW_AUTHORING_SOURCE
```

It is a globally visible nonterminal managed obligation and survives process/session death, Ruu restart, concurrent invocations, repeated sweeps, source advancement, provider waits, ref movement, and retry.

A raw dependency does not block otherwise legal consumer authoring, handoff, checkpointing, internal convergence, PromotionGroup creation, group-local exact-state adoption, PromotionUnit declaration, or exact candidate materialization.

It does block every direct/provider realization that would implicitly publish the source effect without an authorized resolution. Blocking is local to affected consumer projections. Unrelated repositories, groups, and obligations continue through the global fixed-point sweep.

For a consumer exact state `B` authored from consumed base `A`, Ruu retains the immutable owned-state provenance:

```text
owned_base_oid = A
owned_candidate_oid = B
```

Candidate materialization may use the raw exact base to preserve owned-state exactness, but the raw dependency itself grants no publication authority.

### 10. Current target state may satisfy a dependency directly

Before requiring a parent promotion, Ruu observes the consumer's current authoritative PromotionTarget.

A dependency may become:

```text
SATISFIED_BY_TARGET(proof_ref)
```

only when the canonical raw-object ancestry contract proves:

```text
target_oid == consumed_exact_oid
or
consumed_exact_oid ancestor-of target_oid
```

The exact current target observation and ancestry proof are durably adopted. No fake PromotionGroup or PromotionUnit is created.

`SATISFIED_BY_TARGET` is a terminal historical dependency fact. Valid historical realization permanently establishes that the source effect crossed an authorized target boundary; later target drift or source abandonment does not revoke that established dependency authority or rewrite the adopted fact, just as later drift does not rewrite an existing route-conformant `PROMOTED` fact. A later consumer realization may therefore include `A`, but it still evaluates its own current target, route, policy, disposition, expected-old, ancestry, and causal guards. Historical satisfaction is not permission to bypass the current realization route.

### 11. A later source handoff resolves to the source promotion projection

A raw dependency may resolve to:

```text
RESOLVED_PROMOTION_PROJECTION(
  source_promotion_group_id,
  source_repository_id
)
```

only when all of the following hold:

```text
a later accepted handoff explicitly carries the same source ContributionUnit
that handoff is causally after durable semantic selection at TX-A
before any downward synchronization for that handoff, its exact frozen/adopted
  source ContributionUnit checkpoint S contains consumed A under canonical ancestry
its PromotionGroup exact source state K is durably attributable to that handoff
  and incorporates S
source and consumer immutable PromotionTargets are exactly equal
current source/group disposition still authorizes the realization path
expected-state/CAS selects exactly one owning source handoff/projection
```

The first causally accepted qualifying source handoff after TX-A claims the pending/raw obligation by CAS. A handoff accepted between TX-A and TX-B may be adopted directly during TX-B/recovery. Concurrent or duplicate reconciliation is idempotent. If several candidate groups appear without one unique source-handoff attribution and expected raw-dependency generation, resolution is `UNKNOWN_INCONSISTENT`; Ruu does not choose by aggregate ConvergenceUnit ancestry, time, recency, or provider order.

The source-checkpoint predicate prevents laundering `A` back through the consumer. Aggregate group-local `K` containing `A` is insufficient when the source's own exact frozen checkpoint `S` did not contain `A` before consumer-bearing downward synchronization.

If a qualifying source handoff exists but source and consumer immutable PromotionTargets are not exactly equal, the relation becomes `RECONCILIATION_REQUIRED(TARGET_INCOHERENT_AUTHORING_DEPENDENCY)` unless the consumer target independently satisfies `A`. Ruu does not create a cross-target stack or retarget either ConvergenceUnit.

The stable logical predecessor is the existing repository projection identity:

```text
(source_promotion_group_id, source_repository_id)
```

The dependency still retains:

```text
consumed_exact_oid = A
```

The parent's current exact candidate/submission state remains separately `K`. Ruu MUST NOT replace `A` with `K` in the dependency record.

### 12. ADR-050 governs exact reprojection after resolution

For separate PromotionGroups, the resolved relation enters ADR-050's ordinary promotion dependency model.

If the consumer owns `B` over consumed base `A` and the source projection now owns current exact state `K`, the exact descendant reprojection is:

```text
Restack(
  old_base = A,
  owned_candidate = B,
  new_base = K
)
```

A clean transplant changes only the consumer's candidate/provider submission projection. It never rewrites the consumer's immutable internal owned state or an active producer/consumer worktree. A semantic conflict creates the existing exact `RECONCILIATION_REQUIRED` continuation authority.

Source advancement after dependency adoption does not surprise-update the consumer's authored base. It affects only later reconciliation after a valid promotion-projection mapping exists.

### 13. Same-group dependencies stay internal

If source and consumer handoffs already belong to the same immutable PromotionGroup occurrence under ADR-069, the source's own exact frozen checkpoint `S` contains `A` before downward synchronization, and the exact group-local state authoritatively incorporates both `S` and the consumer handoff, the dependency becomes:

```text
INTERNAL_TO_SAME_GROUP(
  promotion_group_id,
  source_repository_id
)
```

ADR-047/048 then govern the single canonical repository projection. No artificial parent/child provider topology is created between pieces of that projection.

Ruu MUST NOT add the source to an already closed PromotionGroup, split one same-group repository projection, or revise terminal group membership merely to internalize a raw dependency.

### 14. Source abandonment never transfers authority

Dependency reconciliation checks target satisfaction before abandonment failure.

```text
consumed A already has a durably adopted valid target-satisfaction proof
→ terminal SATISFIED_BY_TARGET remains controlling even after later drift

no adopted target-satisfaction proof and consumed A is not validly realized
  in the fresh current authoritative target
→ no satisfaction

A not validly realized
+ source ContributionUnit/group loses its realization path
→ RECONCILIATION_REQUIRED(SOURCE_REALIZATION_PATH_LOST)
```

A consumer never gains authority to publish `A` merely because `A` appears in its ancestry or tree. Parent cancellation, source abandonment, or source ref deletion cannot become residual child authority.

A dependency already resolved to a source PromotionGroup remains governed by ADR-071's current-disposition causal fence. Causally committed or already realized history is recovered/adopted under existing rules; proven-absent incompatible effects are not retried.

### 15. Lifecycle and retention are explicit

The dependency lifecycle is:

```text
RAW_AUTHORING_SOURCE
RESOLVED_PROMOTION_PROJECTION(group_id, repository_id)
INTERNAL_TO_SAME_GROUP(group_id, repository_id)
SATISFIED_BY_TARGET(proof_ref)
RECONCILIATION_REQUIRED(reason)
UNKNOWN_INCONSISTENT
```

Allowed progression is monotonic in semantic knowledge:

```text
RAW_AUTHORING_SOURCE
→ RESOLVED_PROMOTION_PROJECTION
→ SATISFIED_BY_TARGET

RAW_AUTHORING_SOURCE
→ INTERNAL_TO_SAME_GROUP

RAW_AUTHORING_SOURCE or RESOLVED_PROMOTION_PROJECTION
→ SATISFIED_BY_TARGET

RAW_AUTHORING_SOURCE or RESOLVED_PROMOTION_PROJECTION
→ RECONCILIATION_REQUIRED

contradictory/missing identity, object, attribution, or proof
→ UNKNOWN_INCONSISTENT
```

`INTERNAL_TO_SAME_GROUP` and `SATISFIED_BY_TARGET` are terminal for dependency resolution. `RECONCILIATION_REQUIRED` remains nonterminal and may later become target-satisfied only from a fresh authoritative proof or receive separately ratified semantic resolution.

The `AUTHORING_DEPENDENCY_OID_ANCHOR` remains `REQUIRED` while any raw, resolved, restack, realization, reconciliation, audit, or recovery obligation may need `consumed_exact_oid`. A dependency state transition alone does not release it. It may become `GC_ELIGIBLE` only after every dependent consumer/source/promotion/recovery obligation is terminal and another durable retained reachability root is proven sufficient for every remaining exact use. Built-in v1 retention is `KEEP`, so Ruu performs no automatic physical deletion even after eligibility.

Unexpected external mutation/deletion of the anchor is an integrity/data-loss condition, never evidence that the dependency disappeared or was satisfied.

### 16. Cardinality and late discovery remain bounded constraints

The dependency record model safely represents a finite set. ADR-081 does not ratify provider/publication semantics for more than one independently unsatisfied predecessor when an ordinary Git/provider submission has one exact base and ADR-050 has one parent submission relation.

Until a later accepted ADR resolves [GitHub issue #1](https://github.com/fanilosendrison/ruu/issues/1):

```text
more than one independently unsatisfied external promotion predecessor
→ authoring/checkpointing may continue when one exact authored base exists
→ realization remains locally blocked
→ provider topology is not invented
```

ADR-048 canonical multi-source composition does not by itself solve this authority/topology problem; it composes exact sources within one repository-local PromotionUnit, not several independently governed predecessor groups.

ADR-081 also does not authorize a late rewrite/refoundation after a consumer has authored from an ordinary baseline and only then discovers a dependency. ADR-050 restacks provider projection after managed handoff; it does not grant mutation authority over an active consumer worktree. [GitHub issue #2](https://github.com/fanilosendrison/ruu/issues/2) tracks the non-normative engineering question of whether a new ContributionUnit, exact transplant, merge, or another explicit semantic mechanism should own that transition.

### 17. Zero-preflight remains governing

For supported harnesses, dependency selection and adoption are internal capability flows behind the ordinary experience. The integration submits an authorized internal provisioning demand to the existing fenced ConvergenceEngine and waits before first consumer write; it does not ask the user to invoke Ruu or create a work-bearing checkpoint:

```text
install Ruu once
launch supported harness
ask the agent to implement
harness explicitly selects an exact pending managed version when needed
author normally
invoke Ruu when desired
```

The user does not manually construct AuthoringDependency records, create ContributionUnits/worktrees, name PromotionGroups, select provider parents, enumerate repositories, or choose stacks.

Failure to establish exact source identity, object truth, retention, or a valid base blocks only the affected authoring/progression path. It never permits dirty-state capture, guessed ancestry, or manual topology fallback.

## Required invariants

```text
INV-203
A dirty managed authoring surface is mutable state, never an exact dependency version.
```

```text
INV-204
ContributionUnit is the sole v1 stable authoring-occurrence identity; work_occurrence_id is not a second domain identity.
```

```text
INV-205
An AuthoringDependency is created only by explicit Development System source/version selection plus exact Git proof; neither ancestry nor selection alone is sufficient.
```

```text
INV-206
Native commit creation is exact Git state but not managed checkpoint, handoff, completion, or promotion state.
```

```text
INV-207
A durable AuthoringDependency always retains its exact consumed commit through a REQUIRED Ruu recovery anchor.
```

```text
INV-208
The consumed exact OID is immutable across raw, promotion-resolved, same-group, target-satisfied, and reconciliation states.
```

```text
INV-209
A raw authoring dependency blocks unauthorized realization, not otherwise legal authoring, checkpointing, convergence, or unrelated global progress.
```

```text
INV-210
Authoritative target containment may satisfy an authoring dependency without creating a synthetic promotion parent.
```

```text
INV-211
Promotion compression requires a source handoff after durable selection, an exact frozen source checkpoint containing the consumed OID before downward synchronization, exact group-local incorporation, equal immutable PromotionTargets, and canonical ancestry. Aggregate candidate ancestry alone never selects the parent projection.
```

```text
INV-212
Source advancement never mutates the selected consumed version or an active consumer worktree.
```

```text
INV-213
Same-group dependencies create no provider topology and never mutate immutable group membership.
```

```text
INV-214
Source abandonment or cancellation never transfers source publication authority to a consumer.
```

```text
INV-215
A clean native managed-ref tip becomes a managed checkpoint only through exact frozen handoff adoption.
```

```text
INV-216
Crash/retry and concurrent reconciliation preserve one dependency identity, one consumed OID, one owning source projection when resolvable, and no adopted unanchored state.
```

## Consequences

### Positive

- An exact intermediate native commit can be consumed without invoking its producer first.
- Dirty producer state cannot silently become dependency or reachable history.
- Source advancement does not surprise-update consumers.
- Dependency OIDs remain reachable through reset, amend, ref deletion, restart, and Git garbage collection.
- Raw authoring provenance enters ADR-050 through durable source-handoff identity rather than ancestry guessing.
- Target realization can discharge a dependency without a fake PromotionGroup.
- Source abandonment does not transfer publication authority.
- Waits remain local while the global reconciler progresses unrelated work.
- Supported-harness zero-preflight authoring remains intact.

### Costs and limits

- Dependency adoption adds a recoverable operation and long-lived Git recovery anchor.
- Source handoff compression needs exact causal attribution and CAS, not only ancestry.
- Implementations must preserve consumed-base/owned-candidate provenance across promotion.
- Multi-unsatisfied-predecessor publication and late dependency refoundation remain explicit HIGH engineering follow-ups in the Ruu Engineering project; project state cannot alter the current fail-closed semantics.

## Rejected alternatives

### Consume the producer's current dirty worktree

Rejected. Mutable staged, unstaged, untracked, ignored, generated, or secret state is not an exact version.

### Create a hidden producer snapshot commit

Rejected. It transfers producer-owned dirty state into durable history without handoff or authority.

### Infer dependency from ancestry or recency

Rejected. Git relation does not supply semantic source identity.

### Require the source to invoke Ruu first

Rejected. It violates localized waiting, independent authoring, and zero-preflight concurrency.

### Create a fake parent PromotionGroup

Rejected. A raw dependency or target-satisfied effect does not create promotion authority.

### Follow the source's live tip

Rejected. The selected exact consumed OID is immutable.

### Transfer source authority after abandonment

Rejected. Dependency consumption is not lifecycle or publication authority.

### Journal every native authoring commit

Rejected. Ordinary commit creation remains native exact-state observation.

## Relationship to prior decisions

ADR-003/033/064 remain authoritative for checkpoint handoff and mutation claims. ADR-081 only adds exact adoption of a clean native tip at that handoff.

ADR-038/054/042 remain authoritative for exact-state continuity, recovery resources, and retention. ADR-081 applies their existing `REQUIRED → GC_ELIGIBLE` and built-in `KEEP` model to consumed dependency OIDs.

ADR-047/048 remain authoritative for same-group repository projection and candidate composition. They do not create cross-group predecessor authority.

ADR-050 remains authoritative after a parent promotion projection is known. ADR-081 supplies the earlier raw provenance and the exact source-checkpoint/handoff mapping into ADR-050; it does not weaken ADR-050's rejection of incidental ancestry. DIRECT realization requires zero unsatisfied external predecessors; only a single predecessor on the provider route may use ADR-050 stacked representation.

ADR-068/071 remain authoritative for cancellation, abandonment, causally committed effects, and current-disposition fencing. ADR-081 adds the rule that none of those transitions transfers source realization authority to a consumer.

ADR-073/074/075/076 remain authoritative for managed worktrees and native observation. ADR-081 keeps ordinary commit movement in exact-state rediscovery and makes only semantic dependency/checkpoint adoption durable managed facts.

ADR-078 remains the governing user experience. All new plumbing stays behind supported-harness integration.

## References

- [Ruu specification](../specification/ruu-spec.md)
- [External Control Plane contract](../specification/external-control-plane-contract.md)
- [ADR-042 recovery coordination](adr-042-use-a-reconciler-driven-coordination-store-with-os-owned-runs-and-append-only-effect-journal.md)
- [ADR-048 canonical materialization](adr-048-materialize-repository-local-multi-source-promotion-units-by-canonical-pairwise-merging.md)
- [ADR-050 promotion dependency and restack](adr-050-derive-stacked-publication-from-unsatisfied-promotion-dependencies-and-restack-by-exact-state-transplant.md)
- [ADR-069 group-local exact state](adr-069-bind-promotion-groups-to-work-bearing-invocations-and-group-local-exact-state.md)
- [ADR-073 managed worktrees](adr-073-require-git-worktrees-as-the-v1-authoring-isolation-substrate.md)
- [Git object model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
