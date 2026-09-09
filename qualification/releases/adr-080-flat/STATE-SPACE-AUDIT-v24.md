# State-Space Audit v24 — ADR-055 cross-repository settlement and PublicationEpisode continuation

## 1. Scope

This audit extends v23 after ADR-055 closes backlog 30.25. It revalidates every prior finite architecture family and adds explicit coverage for non-atomic cross-repository partial progress, durable settlement demand identity, external semantic roll-forward/compensation authority, forward-only settlement effects, logical-submission PublicationEpisode continuation, and terminal `ALL_PROMOTED | COMPENSATED` settlement semantics.

The pass also performs a retrospective static audit of `EXTERNAL-CONTROL-PLANE-CONTRACT.md` against accepted pre-ADR-039 decisions. It makes ADR-022/024/026/032/036 boundaries explicit without changing their underlying semantics.

ADR-055 introduces no new low-level Git DAG mutation primitive: compensation/roll-forward work re-enters ordinary development/convergence/promotion, and PublicationEpisode creation reuses existing provider publication/ref safety. The ADR-048 materialization, ADR-050 restack, and ADR-052 DIRECT CAS+FF smokes therefore remain the concrete Git behavior checks.

## 2. ADR-055 properties exercised

The executable audit checks that:

1. `PARTIALLY_PROMOTED` plus a still-sufficient nominal remaining path does **not** create an automatic settlement/rollback action;
2. exact-generation settlement demand identity is independent of hook/sweep discovery and same-generation rediscovery is idempotent;
3. `ruu` never chooses semantic `ROLL_FORWARD` or `COMPENSATE` on behalf of the External Control Plane/Development System;
4. authoritative target effects remain forward-only and a backward/force reset is never a conforming compensation effect;
5. an open PublicationEpisode receives exact revisions on the same provider PR, while a terminal episode cannot be revised;
6. a terminal provider episode plus a later exact publication need in the same nonterminal logical submission creates a distinct new PublicationEpisode/provider PR;
7. new episode identity does not mint a new logical `submission_id` when the logical key is unchanged, and provider PR identity is distinct across episodes;
8. `COMPENSATED` is terminal only with explicit compensation intent, semantic completion, exact required forward effects adopted, and recovery clear;
9. a partial ship with already-realized effects has no silent built-in `ABANDONED` terminal path;
10. repository admission/active-index, trigger/authority, review-intent/readiness, and runtime-policy-bypass pre-ADR-039 boundaries are explicit in the normative External Control Plane contract;
11. the ADR-052 DIRECT state machine contains no residual local-target pre-advancement step.

## 3. New finite families

ADR-055 adds:

```text
partial_progress_settlement_trigger: 18
cross_repository_settlement_demand_idempotence: 18
cross_repository_settlement_authority_forward_only: 18
publication_episode_lifecycle: 24
publication_episode_identity_separation: 8
compensated_terminal_settlement: 16
control_plane_retrospective_boundaries: 64
```

Every v23 family is re-run as well.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-055**;
- main §30 marks **30.25 resolved by ADR-055** and the open backlog no longer lists 30.25;
- ADR-049 is amended so stable logical `submission_id` is distinct from per-episode provider PR/ref identity;
- terminal provider PRs are never reopened and later same-logical-submission publication uses a new episode under first-publication guards;
- main invariants 63H–63L encode partial-progress non-failure, external settlement authority, forward-only compensation, episode continuity, and no silent partial abandonment;
- `ALL_PROMOTED` and explicit `COMPENSATED` plug into ADR-054's terminal-settlement closure predicate without weakening retirement/recovery guards;
- `CrossRepositorySettlementDemand` is a durable global nonterminal managed obligation and discovery caller/session does not inherit the work;
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` explicitly carries ADR-022 registry/admission, ADR-024/036 trigger, ADR-026 promotion-authority, and ADR-032 review-intent boundaries;
- the existing 30.32/30.36 review policy questions remain open;
- ADR-052 DIRECT progression no longer contains the stale `local target FF -> remote push` wording;
- ADR-014/021/022/024/026/032/036/039/042/049/053/054 and the External Control Plane contract carry the ADR-055 amendments consistently;
- all ADR-054 retirement, ADR-053 review-correction, ADR-052 DIRECT, ADR-051 capability, ADR-050 restack, ADR-049 logical-submission, ADR-048 materialization, and earlier architecture families remain intact.

## 5. Result

Executable result:

```text
Ruu state-space audit v24: PASS
changed/revalidated finite combinations evaluated: 15,824
markdown artifacts statically cross-checked: 82
```

Retained concrete Git smoke results:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
```

Expected settlement boundary:

```text
PARTIALLY_PROMOTED
      |
      +-- ordinary remaining paths sufficient
      |       -> continue normally
      |
      +-- semantic cross-repo disposition required
              -> exact-generation CrossRepositorySettlementDemand
              -> External Control Plane / Development System
                    chooses forward completion or compensation
              -> new ordinary development/convergence/promotion state
              -> provider episode revision if current PR open
                 OR new PublicationEpisode if prior PR terminal
              -> terminal ALL_PROMOTED
                 OR explicit COMPENSATED after required forward effects

No backward target reset and no silent partial abandonment.
```
