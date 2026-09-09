# State-Space Audit v18 — ADR-048 Repository-Local Multi-Source Candidate Materialization

## 1. Scope

This audit extends v17 after ADR-048 closes backlog 30.39. It revalidates every prior finite architecture family and adds explicit coverage for deterministic materialization of one exact repository-local multi-source PromotionUnit into one exact publication candidate/head.

This is a finite regression/state-machine audit. It does not claim to prove arbitrary Git DAGs, every Git implementation/version, provider behavior, or semantic correctness of an externally authored conflict resolution. ADR-048 instead fixes the exact materialization contract and fail-closed boundaries that implementations must enforce.

## 2. ADR-048 properties exercised

The executable audit checks that:

1. candidate materialization is bound to one exact PromotionUnit source set, one exact effective base, and one MaterializationContract;
2. ancestry reduction changes only the execution fold and never mutates logical PromotionUnit provenance;
3. sources already contained by the base or another retained source may disappear from the execution fold without disappearing from final ancestry requirements;
4. canonical source ordering is invariant to runtime/arrival/agent completion order;
5. pairwise conflict results do not become adopted candidates and route to the existing reconciliation boundary;
6. a valid final candidate requires exact base ancestry, all-source ancestry, exact canonical-fold tree identity, and deterministic metadata/OID inputs;
7. transient fold commits are not final candidates and cannot be authoritatively adopted as promotion candidates;
8. a new final candidate requires exact valid full-verification evidence plus current exact inputs/claim before adoption;
9. crash/retry reuse is valid only when source snapshot, effective base, MaterializationContract, and observed candidate all still match exactly.

## 3. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-048**;
- main §30 marks **30.39 resolved by ADR-048**;
- the open backlog no longer lists item 39;
- main invariants 47J–47P encode exact materialization inputs, canonical ordering, pairwise semantics, ancestry closure, deterministic final identity, reconciliation routing, and final-candidate verification;
- main §33.21A contains the explicit candidate-materialization state model;
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` keeps candidate materialization inside Ruu and does not add external merge-order/conflict-resolution intent;
- ADR-047/046/045 and earlier ADRs that formerly described 30.39 as open now identify ADR-048 as its subsequent closure;
- DIRECT and PR lifecycle sections consume the shared ADR-048 candidate instead of defining incompatible local composition semantics;
- recovery wording recognizes transient/final materialization objects under the existing ADR-042 effect journal;
- no native octopus strategy is accidentally promoted to the normative materialization algorithm.

## 4. New finite families

ADR-048 adds:

```text
materialization_ancestry_reduction: 12
materialization_canonical_order_independence: 18
materialization_conflict_boundary: 18
materialization_final_candidate_guards: 16
materialization_verification_adoption: 72
materialization_recovery_contract: 36
```

All prior v17 families are re-run unchanged unless their static assertions are intentionally advanced to ADR-048.

## 5. Git semantic smoke test

A separate executable smoke test (`git-materialization-smoke-v1.sh`) exercises the concrete Git mechanism on the audit host using a rename+modify case that the pairwise full two-head path resolves while native multi-head octopus rejects. It also verifies multi-parent commit creation, base/source ancestry closure, and deterministic recreation of the candidate OID for identical exact inputs/metadata.

Recorded result (`git-materialization-smoke-v1.txt`):

```text
Ruu ADR-048 materialization smoke: PASS
pairwise_merge_tree=PASS
rename_plus_modify=PASS
multi_parent_commit=PASS
base_and_all_source_ancestry=PASS
deterministic_oid_recreation=PASS
native_octopus_rejected_complex_case=PASS
```

This smoke test validates the selected Git plumbing/mechanics on the current audit Git implementation; it is not a proof that every Git version is semantically identical. ADR-048 therefore keeps Git/backend version and relevant merge configuration inside the MaterializationContract/reuse boundary.

## 6. Result

Executable result:

```text
Ruu state-space audit v18: PASS
changed/revalidated finite combinations evaluated: 13,468
markdown artifacts statically cross-checked: 69
```

## 7. Resulting promotion pipeline

```text
Development session
  ↓
ConvergenceUnits
  ↓ exact READY_INTERNAL states
PromotionGroup
  ↓ ADR-047 deterministic repository projection
repository-local PromotionUnit P = {x,y,z,...}
  ↓ ADR-048
exact effective base B
  ↓
execution-only ancestry reduction
  ↓
canonical retained-source order
  ↓
pairwise full two-head merge fold (ort-class / proven-equivalent)
  ↓
final tree T
  ↓
one canonical synthetic multi-parent candidate C
  ↓
exact full verification of C
  ↓
DIRECT or PR publication mechanics
```

Required final relation:

```text
B ancestor-or-equal C

∀ source s in original PromotionUnit P:
  s ancestor-or-equal C
```

A materialization conflict requiring semantic authoring does not produce a candidate. It produces/refreshes exact ADR-040 `RECONCILIATION_REQUIRED` evidence and waits for new externally authored development state to re-enter the ordinary convergence pipeline.
