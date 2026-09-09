# ADR-048: Materialize repository-local multi-source PromotionUnits by canonical pairwise merging

## Status

Accepted — 2026-09-06

## Context

ADR-047 closes the structural multi-source projection problem: one completely exact-resolved PromotionGroup is partitioned deterministically by authoritative source repository, yielding exactly one repository-local PromotionUnit per represented repository.

A repository-local PromotionUnit can still contain several exact ConvergenceUnit states:

```text
PromotionUnit P = {
  RepoA/CX@x,
  RepoA/CY@y,
  RepoA/CZ@z
}
```

The member set is exact, immutable, unordered, and content-addressed under ADR-045. It says exactly which internal states belong to the repository-local promotion, but Git/provider publication still needs one exact candidate/head. A PR has one exact head; DIRECT promotion advances one exact target ref. Git cannot publish a set of sibling commit OIDs as one head.

The materialization problem is therefore:

```text
exact effective base B
+
exact unordered PromotionUnit source set {x,y,z,...}
→ one exact repository-local candidate C
```

while preserving all exact source provenance, avoiding any rewrite of internal ConvergenceUnit refs, refusing semantic conflict authoring, supporting crash/retry/recovery, and obtaining development-validation evidence for the exact final result.

Git offers an `octopus` merge strategy for more than two heads, but Git documents `octopus` as refusing complex merges that require more involved resolution, while the normal `ort` strategy provides the full two-head three-way merge semantics including rename handling. Therefore native multi-head `octopus` is not sufficiently general to define v1 materialization semantics. Git also permits commits with any number of parents, so the computation algorithm and the final graph representation do not need to be the same mechanism.

Backlog item 30.39 exists to close this downstream materialization problem.

## Decision

Backlog item **30.39 is closed** by defining repository-local multi-source candidate materialization as a deterministic canonical pairwise fold using full Git two-head merge semantics, followed by one canonical synthetic multi-parent materialization commit.

### 1. Materialization inputs are exact and repository-local

The materialization operation consumes at least:

```text
MaterializationInput {
  promotion_unit_id
  exact_effective_base_oid
  exact_source_oids: Set<CommitOID>
  materialization_contract
}
```

The source OIDs are exactly the OIDs bound by the immutable PromotionUnit. They all belong to the same authoritative source repository by ADR-047.

The operation MUST NOT rewrite, rebase, amend, reset, or otherwise mutate any source ConvergenceUnit ref/OID merely to construct the candidate.

### 2. Effective base is snapshotted exactly

The effective materialization base is the exact state over which the current promotion must be represented:

```text
INDEPENDENT promotion
→ exact current policy-selected target head

DEPENDENT promotion with predecessor not yet target-realized
→ exact current predecessor candidate/submission head derived by ADR-050 promotion-dependency reconciliation
```

The chosen base is recorded as `exact_effective_base_oid = B` in the materialization Operation/Attempt input.

If the authoritative target/predecessor state changes before candidate adoption or a later policy-sensitive publication mutation, the prior candidate is stale for that progression and the reconciler re-evaluates/rematerializes from current exact state as required. A previously materialized candidate never authorizes publication against a different base merely because its tree still appears applicable.

### 3. Ancestry reduction is mechanical and provenance-preserving

Before pairwise composition, `ruu` computes an execution-only reduced source-head set.

A source may be omitted from the fold when its exact state is already contained by the effective base or by another retained source head:

```text
s ancestor B
→ no merge step required for s

s1 ancestor s2
→ s1 may be removed from the fold when s2 is retained
```

This reduction MUST NOT mutate the PromotionUnit definition or erase provenance. Every original PromotionUnit source remains part of the exact promotion source set and must remain provably reachable from the final candidate.

The fold therefore operates on the ancestry-maximal source heads not already contained by the effective base.

### 4. Fold order is canonical; arrival/runtime order is irrelevant

The PromotionUnit member set is unordered. Runtime arrival order, agent completion order, branch enumeration order, filesystem order, process scheduling, or provider order MUST NOT affect materialization.

The retained source heads are sorted by a versioned canonical ordering over their exact canonical source refs/OIDs. The exact ordering rule is part of the `materialization_contract`.

Thus:

```text
same exact base
+ same exact PromotionUnit source set
+ same materialization contract
→ same canonical fold sequence
```

### 5. Canonical merge semantics are ancestry-aware pairwise full two-head merges

Let the ordered retained heads be:

```text
[s1, s2, ..., sn]
```

The semantic fold starts at `C0 = B` and treats ancestry-preserving steps as state reuse rather than manufacturing no-op merge commits:

```text
for i in 1..n:
  if si ancestor-or-equal C(i-1):
    Ci = C(i-1)

  else if C(i-1) ancestor-or-equal si:
    Ci = si

  else:
    Ti = FullTwoHeadMergeTree(C(i-1), si)
    Ci = CanonicalTransientMergeCommit(
           tree = Ti,
           parents = [C(i-1), si]
         )
```

`FullTwoHeadMergeTree` uses the versioned v1 Git merge profile based on full `ort`-class two-head three-way merge semantics or an implementation proven equivalent for the exact contract.

Consequently, if `B` already contains every PromotionUnit source, materialization reuses `B` as the exact candidate. If one existing source head is a descendant of `B` and contains every other source, that exact source head is reused as the candidate. No synthetic commit is created merely to restate already-existing ancestry.

The reference implementation may use modern plumbing such as `git merge-tree --write-tree` plus `git commit-tree`, or an isolated equivalent implementation. The command choice is not itself the semantic contract.

Native multi-head `octopus` MUST NOT define materialization semantics. An optimization/backend may be substituted only when the implementation verifies that it produces the exact same final tree required by the canonical pairwise contract for the same exact inputs.

### 6. Pairwise transient commits are computational artifacts, not promotion states

Intermediate `Ci` commits exist only to give each subsequent two-head merge an exact Git commit parent/state.

They are not:

```text
PromotionUnits
submission revisions
provider-visible heads
authoritative managed promotion checkpoints
separate PRs
```

They need not receive independent development-validation evidence merely because they exist during the fold. They remain attempt-scoped/recoverable computational artifacts until the final candidate is constructed.

### 7. The final representation reuses an exact existing state when possible; otherwise it is one canonical synthetic multi-parent commit

If the ancestry-aware fold completes without requiring any synthetic merge and its result is already an existing exact commit (`B` or one retained source head), that exact commit is the final candidate and is reused directly.

Otherwise, after the fold yields final tree `Tfinal`, `ruu` creates exactly one final synthetic materialization candidate commit `C`:

```text
C.tree = Tfinal

C.parents = [
  B,                       # first parent
  ...canonical retained source heads
]
```

Parents are unique. Sources already reachable through another retained source or through `B` need not appear redundantly as direct parents; their provenance remains in the PromotionUnit and their ancestry remains required.

The effective base `B` MUST be the first parent. This makes the publication line mechanically explicit:

```text
B → C
```

while the additional parents preserve exact source ancestry.

When synthesis is required, the synthetic commit metadata is canonical and wall-clock-independent under a versioned metadata profile. Author/committer identity, message format, timestamps/timezone, parent ordering, tree encoding, and any other OID-affecting fields MUST be deterministically derived/fixed by the `materialization_contract`; current runtime time MUST NOT be an input.

Therefore the final candidate OID is reproducible for the same exact materialization inputs and contract, whether the result is exact-state reuse or a newly synthesized commit.

### 8. Final ancestry invariants are mandatory

For the final candidate `C`:

```text
B ancestor-or-equal C

∀ s ∈ PromotionUnit.members:
  exact_source_oid(s) ancestor-or-equal C
```

The final candidate tree MUST equal the exact final tree produced by the canonical pairwise fold under the recorded materialization contract.

A candidate that fails any of these checks is `UNKNOWN_INCONSISTENT` and cannot be adopted/published.

### 9. Conflict handling reuses RECONCILIATION_REQUIRED

If any pairwise merge step cannot produce a clean deterministic tree without semantic code authoring, materialization stops before authoritative candidate adoption.

`ruu` MUST NOT choose conflict content, invoke an LLM to author a semantic resolution, or silently switch algorithms/orders to obtain a different answer.

It emits/refreshes the existing ADR-040 exact-state-bound `RECONCILIATION_REQUIRED` obligation with materialization-specific mechanical evidence sufficient to reproduce the conflict, including at least:

```text
promotion_unit_id
exact_effective_base_oid
materialization_contract fingerprint
canonical retained source order
successfully incorporated prefix
current source head
merge/conflict records and affected paths where available
exact relevant OIDs
```

Authoritative source/target refs remain unchanged. Any externally authored reconciliation returns through normal current-state observation, exact PromotionUnit resolution, materialization, and any policy-required external development-validation gate for the resulting exact candidate.

### 10. Materialization is isolated from producer worktrees

Candidate computation MUST NOT mutate a ContributionUnit producer worktree.

Implementations SHOULD prefer side-effect-minimal Git plumbing that computes/writes trees/commit objects without checking out producer state. Where a worktree/index is required by the implementation/backend, it MUST be a dedicated Ruu attempt-scoped isolated workspace under existing mutation/recovery authority rules.

Any correctness-critical temporary refs/workspaces/object anchors use non-recycled Operation/Attempt/incarnation namespaces under ADR-042 and remain `REQUIRED` until durable reachability/recovery sufficiency is established.

ADR-052 subsequently closes the DIRECT-specific final target-advancement mechanics under 30.22 as a pure exact-old CAS+FF ref effect; this ADR remains the candidate materialization semantics shared by DIRECT and PR flows.

### 11. The exact final candidate may require exact external development validation before adoption

A newly materialized final candidate `C` is a new exact state-producing result.

Before it becomes an authoritative managed promotion/submission candidate, it MUST have valid repository-required development-validation evidence bound to exact `C` under ADR-029/030.

```text
PromotionUnit sources READY_INTERNAL
≠ final candidate development-validation prerequisite satisfied
```

Source evidence may be reused only when ADR-030 says the exact final state already has valid reusable evidence. Otherwise `ruu` keeps `C` immutable/recoverable and emits/refreshes an exact external `DevelopmentValidationDemand`; it does not schedule or execute tests.

Transient fold commits do not independently satisfy or replace any development-validation prerequisite attached to final `C`.

### 12. Materialization is an Operation→Attempt→Observation→Adoption effect

Materialization participates in ADR-042 recovery semantics.

The logical Operation records/fingerprints the exact materialization input/contract. Physical Attempts are separately fenced. Candidate objects/recovery anchors do not prove adoption merely by existing.

After crash/retry, the reconciler re-observes:

```text
current PromotionUnit exact source set
current effective base
materialization contract/environment fingerprint
candidate/recovery objects
verification evidence
managed metadata/CAS state
```

If the exact inputs still match, deterministic recomputation or exact candidate observation may adopt/reuse the same candidate. If any correctness-relevant input changed, the old attempt result is stale/superseded and current state is recomputed.

No SQLite transaction spans Git merge computation or verification.

### 13. MaterializationContract captures determinism-relevant merge semantics

The v1 contract fingerprint includes all correctness-relevant factors capable of changing the fold result/OID, including conceptually:

```text
contract/domain version
canonical source ordering version
merge semantic/backend profile (ort-class)
Git/backend version or pinned semantic profile
relevant merge/rename/config fingerprint
canonical transient-commit metadata profile
canonical final-commit metadata profile
```

Environment/config drift that changes one of these correctness-relevant inputs invalidates reuse under the old contract unless equivalence is independently proven.

V1 is single-host under ADR-041, so this contract primarily provides deterministic retry/audit/recovery and future-proofs later multi-host execution without pretending different Git merge implementations are automatically identical.

## Consequences

### Positive

- One repository-local PromotionUnit always produces one exact candidate/head, preserving the one-proposal boundary established upstream.
- Full two-head Git merge semantics are used rather than the more limited multi-head octopus strategy.
- Runtime/agent arrival order cannot affect the result.
- Internal ConvergenceUnit OIDs are never rewritten to manufacture a candidate.
- Exact base and every exact source remain mechanically provable ancestors of the final candidate.
- State-preserving/ancestry-subsumed cases reuse an existing exact commit; when composition is required, the final provider-facing graph contains one synthetic materialization commit instead of a chain of technical fold commits.
- Conflict handling reuses the existing exact `RECONCILIATION_REQUIRED` boundary instead of creating a second semantic-conflict protocol.
- Full verification is attached to the exact combined result that will actually be promoted.
- Deterministic commit metadata makes crash/retry/idempotent recreation capable of reproducing the same final OID under the same exact contract.

### Costs / constraints

- Candidate construction is more explicit than simply invoking `git merge <many-heads>`.
- The implementation needs a sufficiently capable two-head merge backend; modern `git merge-tree --write-tree` is a strong reference implementation but is not assumed to exist on every legacy Git installation.
- Relevant Git/backend version/config becomes part of the materialization contract/reuse boundary.
- The synthetic final multi-parent commit tree is produced by the canonical pairwise algorithm rather than by Git's native octopus strategy; tooling must treat Ruu's materialization contract as authoritative for that commit.
- Intermediate transient commits/objects may require temporary reachability anchors until final candidate/recovery state is durable.

## Rejected alternatives

### Native octopus merge as the normative algorithm

Rejected. Git's octopus strategy handles more than two heads but intentionally refuses more complex cases that the normal two-head merge engine can handle. It would create false `BLOCKED` outcomes for mechanically resolvable states and therefore is not sufficiently general for Ruu's normative semantics.

### Rebase/cherry-pick sources into a stack and publish the last rewritten head

Rejected. It rewrites/duplicates the exact source histories, weakens direct ancestry/provenance binding to the immutable PromotionUnit source OIDs, and turns publication materialization into source-history transformation.

### Publish one stacked PR per PromotionUnit source

Rejected. ADR-047 already establishes that same PromotionGroup + same repository yields one PromotionUnit/proposal boundary. Splitting its members into provider-visible stacked PRs would invent promotion granularity downstream.

### Pairwise merge chain as the final provider-visible graph

Rejected as the canonical representation. Pairwise commits are useful to compute with full two-head semantics, but exposing every fold step as durable publication history adds technical commits that do not correspond to independent promotion obligations. V1 condenses the result into one final multi-parent materialization commit.

### Semantic conflict authoring inside Ruu

Rejected. Conflict authoring remains outside Ruu under ADR-040; Ruu emits exact reconciliation evidence and later consumes current authored Git state through ordinary revalidation.

## References

Git behavior used by this ADR is consistent with the official Git documentation:

- `git merge`: `ort` resolves two heads with three-way merge and rename handling; `octopus` handles more than two heads but refuses complex merges needing manual resolution.
- `git commit-tree`: a commit may have any number of parents.
- `git merge-tree --write-tree`: modern plumbing can compute a two-head merge tree without mutating a normal producer worktree.

## Relationship to prior ADRs

Builds on ADR-010, ADR-012, ADR-016, ADR-017, ADR-028, ADR-029, ADR-030, ADR-040, ADR-042, ADR-045, ADR-047.

Closes backlog **30.39**. ADR-049 subsequently closes 30.19 and ADR-050 closes 30.20. ADR-051 subsequently closes 30.21 provider capability discovery, and ADR-052 subsequently closes 30.22 DIRECT target advancement without changing this ADR's candidate-tree/materialization semantics.


## Amendment by ADR-050

ADR-050 removes caller-authored stack layout from effective-base selection. A predecessor base is used only when exact managed promotion facts establish an unsatisfied dependency on another promotion that is not yet realized in the authoritative target. ADR-048 continues to materialize the child's immutable owned candidate over that exact base; if the predecessor later changes, ADR-050 restacks the provider representation by exact state transplant without rewriting the ADR-048 owned candidate/source state.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
