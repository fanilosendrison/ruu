# State-Space Audit v19 — ADR-049/ADR-050 Submission Identity and Derived Dependency Restacking

## 1. Scope

This audit extends v18 after ADR-049 closes backlog 30.19 and ADR-050 closes backlog 30.20. It revalidates every prior finite architecture family and adds explicit coverage for provider-facing submission-ref separation, stable logical submission identity across exact revisions, exact expected-old publication guards, derived promotion-dependency/stack representation, exact state-transplant restacking, no-drift restack anchoring, executor-neutral result adoption, verification, and recovery.

This is a finite regression/state-machine audit. It does not claim to enumerate every arbitrary Git DAG/provider implementation or prove all provider behavior. Exact Git semantics selected by ADR-050 are additionally exercised by `git-restack-smoke-v1.sh`.

## 2. ADR-049 properties exercised

The executable audit checks that:

1. provider-facing submission refs are always distinct from internal refs, even when both point to the same OID;
2. stable logical submission identity depends on repository-local logical projection + canonical publication destination, not one exact PromotionUnit/head;
3. changed exact PromotionUnit/head may remain a revision of the same submission when logical projection/destination are unchanged;
4. changed projection/destination does not silently reuse the same logical submission;
5. revision publication requires distinct refs, current policy authorization, current claim, valid exact verification, and exact expected-old match;
6. unexpected/unknown expected-old state cannot authorize submission rewrite.

## 3. ADR-050 properties exercised

The executable audit checks that:

1. stack shape is never selected as caller intent;
2. an ordinary promotion is used when there is no unresolved dependency or the predecessor is already realized in the authoritative target;
3. an unsatisfied exact dependency becomes stacked only when provider/policy supports and authorizes that representation;
4. unsupported/forbidden stack representation waits rather than silently flattening/duplicating the dependency;
5. unknown dependency/target facts never authorize stacked publication;
6. restack adoption requires a current immutable owned anchor, current new base, clean exact transplant, valid exact full-verification evidence, and expected-old match;
7. a semantic transplant conflict cannot be adopted and routes to reconciliation;
8. repeated restacks use the immutable owned anchor rather than a prior restacked provider head;
9. local/provider-native/external-tool executor choice cannot alter semantic adoption predicates.

## 4. New finite families

ADR-049/050 add:

```text
submission_ref_separation: 8
submission_logical_identity_revision: 16
submission_expected_old_update: 162
derived_dependency_representation: 27
restack_state_transplant_guards: 162
restack_no_projection_drift: 6
restack_executor_neutral_adoption: 81
```

Every v18 family is re-run as well.

## 5. Git semantic smoke test

`git-restack-smoke-v1.sh` constructs:

```text
old predecessor/base A
child-owned candidate B over A
new predecessor/base A'
```

and computes the exact restack tree with Git's full two-head merge engine using explicit merge base:

```text
base   = A
ours   = A'
theirs = B
```

The recorded result (`git-restack-smoke-v1.txt`) is:

```text
Ruu ADR-050 restack smoke: PASS
exact_three_way_transplant=PASS
predecessor_evolution_preserved=PASS
child_owned_effect_preserved=PASS
deterministic_tree=PASS
deterministic_submission_head=PASS
new_head_parent_is_new_base=PASS
semantic_conflict_blocks=PASS
```

The smoke test verifies that independent predecessor evolution and child-owned effect are preserved together, identical exact inputs reproduce the same tree/head under fixed metadata, the provider-facing head is based on the new predecessor, and conflicting concurrent edits fail instead of producing a silently selected semantic result.

## 6. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-050**;
- main §30 marks **30.19 resolved by ADR-049** and **30.20 resolved by ADR-050**;
- the open backlog no longer lists items 19/20;
- ADR-049 supersedes internal/submission ref aliasing and fixes stable logical submission identity/ref lifecycle;
- ADR-050 supersedes caller-authored stack-layout intent and fixes exact dependency-derived stacked representation;
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` no longer requires the External Control Plane to choose stack layout;
- ADR-027/039/047/048 are explicitly amended to the derived-dependency model;
- main invariants 53–65 enforce distinct refs, logical-vs-exact submission identity, exact expected-old rewrite guards, exact dependency derivation, submission-only restack, and no projection drift;
- §33.26 uses derived dependency state and §33.27 uses exact state-transplant revision semantics;
- 30.21 remains open as provider capability normalization rather than stack semantic authority.

## 7. Result

Executable result:

```text
Ruu state-space audit v19: PASS
changed/revalidated finite combinations evaluated: 13,930
markdown artifacts statically cross-checked: 72
```

## 8. Resulting publication/restack pipeline

```text
Development session(s)
  ↓
PromotionGroup(s)
  ↓ ADR-047
repository-local PromotionUnit(s)
  ↓ ADR-048
immutable exact owned candidate C0 over exact base B0
  ↓
current target/predecessor reconciliation
  ↓
no unsatisfied predecessor
  → ordinary publication

unsatisfied predecessor B1 + stack supported/authorized
  → stacked provider representation
  ↓ predecessor revision
RESTACK_REQUIRED
  ↓ ADR-050
three-way state transplant(base=B0, ours=new predecessor/base, theirs=C0)
  ↓
exact new submission head H1
  ↓ full verification
ADR-049 expected-old guarded submission-ref revision
  ↓
provider observation/adoption
```

Internal exact refs/candidates are never rewritten by this path.
