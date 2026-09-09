# Ruu — Hostile-audit follow-up resolution through ADR-068

- **Date:** 2026-09-07
- **Baseline:** ADR-067 verified package
- **New decision:** ADR-068
- **Current finite audit:** `STATE-SPACE-AUDIT-v35.md`

## Issue closed

The ADR-067 package intentionally left backlog 30.41 open because the older ConvergenceUnit lifecycle still exposed a vague group-bound `ABANDONING` path:

```text
immutable PromotionGroup G references X
+ ship not terminal
+ higher-level system wants to stop pursuing it
→ what legal terminal disposition exists?
```

Silently retiring `X` would strand immutable `G`, while treating ordinary branch deletion as cancellation would violate the core requirement that users/agents continue to use Git normally.

## ADR-068 resolution

The architecture now separates:

```text
ordinary Git artifact deletion
!= logical lifecycle disposition
!= PromotionGroup cancellation
```

A user/agent may delete an ordinary authoring branch/ref/worktree directly. That deletion has no hidden `ruu` semantic effect.

If an already-declared ship is withdrawn before realization, the External Control Plane explicitly cancels the **PromotionGroup**. Terminal `CANCELLED` requires:

```text
zero realized group promotion effects
zero unresolved committed/unknown effects capable of realizing
managed provider/publication surfaces terminally non-realizing
required recovery observations/adoptions complete
```

If any promotion effect already realized, `CANCELLED` is forbidden. Cross-repository partial state remains under ADR-055 settlement. Membership changes use cancel-old + declare-new immutable group, never mutation.

ConvergenceUnit `ABANDONING` is consequently gated by higher-level terminal non-delivery disposition plus absence of replacement/nonterminal groups and current authoring/reconciliation demand. It is never inferred from `git branch -D`.

## Verification

`STATE-SPACE-AUDIT-v35.py` adds:

```text
48  PromotionGroup cancellation combinations
64  ConvergenceUnit disposition combinations
8   immutable membership-change combinations
```

for a current total of **14,806 finite combinations**.

Seven Git primitive smokes pass, including a new branch-deletion-neutrality smoke in which an exact checkpoint remains reachable through its managed anchor after the ordinary authoring branch is deleted.

## Result

Backlog 30.41 is closed. No current core design backlog item remains open after ADR-068. This is a statement about the presently modeled architecture, not a claim that future hostile review cannot uncover another issue.
