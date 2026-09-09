# HOSTILE AUDIT — ADR-070 product-intent conformance

**Date:** 2026-09-07  
**Target:** ADR-070 + consolidated specification through ADR-070  
**Purpose:** try to falsify the written product promise against the existing technical architecture.

## Verdict

**PASS WITH EXPLICIT GOVERNANCE.**

ADR-070 does not require a new Git state-machine transition. It makes a previously distributed product assumption normative and provides a precedence rule. Existing accepted mechanisms support the promise when read together: CWD-independent/global discovery (ADR-004/022/036), isolated writer authority (ADR-009/033/064), coalesced top-level execution (ADR-041/042), ordinary Git equivalence (ADR-058), and durable work-bearing invocation cohorts (ADR-069).

## Hostile scenarios

### H1 — Three sessions invoke from different repositories

```text
A works from frontend
B works from backend
C works from schema
A invokes
C invokes while B still authors
B invokes later
```

Required result: no human mutex, no invocation ordering contract, no CWD-scoped correctness. Distinct work-bearing LogicalInvocations remain durable; convergence demands may coalesce; the authoritative executor sweeps globally.

**PASS.** ADR-041/042 and ADR-069 already separate logical occurrence from wake-up/run identity.

### H2 — One invocation touched multiple repositories but caller invokes from only one

Required result: the caller does not pass `--repos`; the ADR-069 sealed ContributionUnit cohort supplied by the Development System carries the work occurrence; CWD is only discovery context.

**PASS.** ADR-004/022 plus ADR-069 support this reading. ADR-070 now makes any future CWD-scoped reinterpretation a product regression.

### H3 — Two sessions eventually contribute to the same ConvergenceUnit

Required result: stale relative state is expected, not automatically fatal. Exact mechanical integration/reconciliation proceeds when possible; semantic conflict produces an exact obligation.

**PASS.** ADR-016/037/040/048/050 plus ADR-069 provide the mechanisms. ADR-070 forbids exporting avoidable coordination to the user.

### H4 — Simultaneous invocations

Required result: the user does not acquire a mutex or wait for another caller. Top-level work safely coalesces behind the authoritative executor while the logical invocation facts remain distinct.

**PASS.** ADR-005 as superseded by ADR-041/042 already establishes this.

### H5 — Another session advances state while producer still owns a worktree

Naive product interpretation: silently rebase/update the producer's active worktree in the background.

Required result: reject that implementation. External mutation authority remains exclusive; reconciliation occurs at safe handoff boundaries.

**PASS.** ADR-009/033/064 are consistent with ADR-070 §6.

### H6 — User deletes a normal branch while work is managed

Required result: ordinary deletion remains ordinary Git, not hidden cancellation/group control.

**PASS.** ADR-058 and ADR-068 preserve native meaning.

### H7 — Implementation proposes mandatory `--group`, `--repos`, `--depends-on`, or global user serialization

Required result: reject unless a later ADR explicitly amends ADR-070 and updates Product intent.

**PASS BY NEW GOVERNANCE RULE.** This was not previously explicit enough; ADR-070 closes that interpretive gap.

### H8 — Irreducible semantic conflict

Required result: the product does not guess merely to preserve the appearance of hands-off operation. It emits/localizes exact reconciliation work to the Development System.

**PASS.** ADR-012/040/050 and the External Control Plane boundary already require fail-closed semantic escalation.

## Static drift scan targets

Current-doc scans must flag new normative wording equivalent to:

```text
CWD == semantic scope
caller must enumerate all repositories
caller chooses PromotionGroup membership
caller declares stack topology
user must serialize Ruu invocations
stale base alone is terminal failure
reconciler may mutate externally owned worktree to keep it fresh
provider PR/merge-queue/review objects define core version identity or convergence truth
```

Historical rejected/superseded ADR text may contain such concepts only when clearly non-current.

## Conclusion

ADR-070 is compatible with the current architecture and adds a missing **architectural priority rule**. Its main effect is preventative: technical decisions that are internally coherent but would re-export orchestration burden to the user can no longer enter the architecture silently.

## Product-definition refinement check — 2026-09-07

The product-intent wording was additionally challenged against a narrower interpretation in which `ruu` is merely a sophisticated GitHub/PR convergence orchestrator. That interpretation is now normatively rejected. The core remains meaningful without provider APIs: concurrent agentic work is isolated, checkpointed, versioned, integrated, reconciled, and converged as exact native Git state. Provider publication remains a supported realization/projection layer and may impose route-specific constraints, but it must not become the source of core version identity or convergence truth where those facts are provider-independent. This refinement is consistent with ADR-058 native-Git equivalence, ADR-061 target identity, ADR-062 route-independent PromotionUnits, ADR-065/066 realization proof, and ADR-069 group-local exact state.
