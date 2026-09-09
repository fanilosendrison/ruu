# ADR-022: Keep managed repository discovery/registry and a derived active-convergence index

- **Status:** Accepted — ownership/provisioning amended by ADR-023, terminology/policy amended by ADR-025–ADR-027, verification responsibility amended by ADR-031, invocation-scope authority superseded by ADR-036, and brand-new repository admission clarified by ADR-056
- **Date:** 2026-09-04
- **Decision order:** 022

## Context

`ruu` is intentionally invocable from any working directory and may need to converge work in repositories other than the caller's CWD. It also has to recover work left by other sessions, observe pending PRs, finish pushes, and repair interrupted Git operations.

Therefore it needs durable knowledge of which repositories belong to its orchestration domain and which of those repositories still have unresolved convergence responsibilities.

This state cannot belong exclusively to `/go`, because `ruu` must remain usable from ordinary coding-agent sessions outside any `/go` run.

At the same time, “global convergence” must not mean recursively scanning every `.git` directory on the machine.

## Decision

`ruu` uses two durable repository-discovery/index concepts:

```text
KNOWN_REPOSITORIES
=
catalog of repositories admitted into shared managed Git coordination

ACTIVE_CONVERGENCE_SET
=
derived/reconstructible index of known repositories with at least one recorded nonterminal managed obligation
```

A repository remains active while any of these exist:

```text
unresolved contribution unit
nonterminal convergence-unit lifecycle
pending/inconsistent contribution-unit or convergence-unit publication
nonterminal PR/review/check/provider/merge-queue workflow
Git merge/conflict/in-progress recovery
incomplete cleanup/claim
crash-recovery obligation
relevant UNKNOWN_INCONSISTENT state
```

A repository may index as `KNOWN_INACTIVE` only when authoritative managed obligation records show that all such responsibilities are terminal/absent. This index is an optimization, not processing authority.

Each executed global sweep derives its authoritative processing universe from **all known nonterminal managed obligations**, regardless of caller, repository, age, ContributionUnit, ConvergenceUnit, PromotionUnit, or trigger reason. `ACTIVE_CONVERGENCE_SET` may accelerate repository lookup but may not exclude an obligation. If stale or contradictory, it is rebuilt from authoritative managed records.

No normal whole-disk Git scan is performed.

Repositories are admitted into the shared managed registry through contribution-unit provisioning or explicit management/recovery paths. Registration and repository identity resolution happen before the first managed write in a contribution unit. An arbitrary `ruu` invocation from an unknown CWD does not itself provision/register that repository.

Concurrent first registration of the same repository converges on one repository identity.

The registry is authoritative only for managed coordination relationships such as repository membership, contribution-unit/worktree mapping, convergence-unit mapping, claims, external mutation-access observations, promotion/provider identities, and lifecycle metadata. Actual Git/remotes/provider state remains authoritative for refs/OIDs/worktrees/dirty state/remote refs/PR state.

`ruu` must remain functionally safe without `/go`. Higher-level systems may enrich records with workflow metadata, but they are not required for Git safety.

## Rationale

The registry is required by the shared managed Git system so `ruu` can enumerate authoritative nonterminal obligations across isolation, convergence, publication, provider governance, final integration proof, and recovery.

Separating `KNOWN_REPOSITORIES` from the derived `ACTIVE_CONVERGENCE_SET` avoids deep-scanning truly quiescent repositories while authoritative nonterminal managed obligations prevent pending PR/recovery/convergence/provider work from being forgotten.

Automatic registration preserves the no-onboarding workflow.

Keeping Git facts authoritative prevents a stale orchestration database from manufacturing repository reality.

## Consequences

- CWD is discovery context, never the complete scope.
- A pending/frozen PR keeps its repository active even when no local mutation is currently authorized.
- A fully quiescent repository with zero authoritative nonterminal managed obligations remains known but need not be deeply scanned every executed global sweep.
- New managed work automatically reactivates a known-inactive repository.
- First managed contribution unit edit is forbidden until repository identity, convergence-unit/contribution-unit mapping, and isolated worktree are durably established.
- Repository identity/path recovery becomes part of crash recovery.
- Ambiguous duplicate repository identities enter fail-closed recovery.
- `/go` can provide logical feature/run/work-package metadata but cannot be required to tell `ruu` what Git state is safe.
- ADR-041 fixes the v1 coordination domain as single-host and requires a durable transactional coordination store; exact schema, repository-ID derivation, retention policy, migration details, and transaction layout remain open implementation questions.

## Alternatives considered

- **Let `/go` own the repository registry:** rejected because `ruu` must work safely without `/go`.
- **Use only the caller's CWD:** rejected because eligible work/PR/recovery state may exist in other repositories.
- **Scan every Git repository on the machine every invocation:** rejected as the wrong scope boundary and unnecessarily expensive/intrusive.
- **Deep-refresh every known repository forever:** rejected because historical/quiescent repositories with zero authoritative nonterminal obligations do not require deep refresh.
- **Trust registry state over Git when they disagree:** rejected because Git/remotes/provider are authoritative for the facts they own.

## Related decisions

Clarifies ADR-002 and ADR-004, extends ADR-013 and ADR-015, and defines repository discovery/index substrate used by ADR-007 and ADR-021. ADR-036 defines the authoritative invocation universe.

## Amendment by ADR-023

The concepts `KNOWN_REPOSITORIES`, a derived/reconstructible `ACTIVE_CONVERGENCE_SET`, quiescence optimization, no whole-disk scan, and Git-over-metadata authority remain accepted. ADR-036 supersedes any interpretation in which the active set itself defines authoritative invocation scope.

Superseded parts:
- repository/context registry ownership is no longer exclusive to `ruu`;
- pre-edit repository/convergence-unit/contribution-unit/worktree/mutation-authority provisioning is not a `ruu` responsibility;
- invocation from an unknown repository does not itself auto-register/provision that repository.

Durable repository/context state now belongs to a shared Git coordination substrate used by both the contribution-unit provisioner and `ruu`.

## Amendment by ADR-025, ADR-026, and ADR-027

The shared coordination substrate now additionally records convergence-unit identities, repository promotion policy state, promotion-unit bindings, submission refs/PR identities, and promotion topology.

Repository activity is kept alive by unresolved DIRECT or PR promotion responsibilities, including stacked/submission revision state.

## Terminology note by ADR-025

Where this historical ADR uses `feature` for the repository-local shared Git parent of contribution units, the current normative term is **convergence unit**. Product-feature semantics are not implied. The original wording is retained to preserve decision history.

## Amendment by ADR-031

Queued/running/recoverable required verification is a nonterminal managed obligation that keeps/reactivates the repository in the derived active index.

Verification-capacity waiting never removes that obligation from the global invocation universe, and it does not block unrelated obligations from progressing.

## Amendment by ADR-036

The authoritative invocation universe is no longer the repository active set. Every explicit invocation re-evaluates all known **nonterminal managed obligations** across ContributionUnit, ConvergenceUnit, PromotionUnit, publication, PR/review/check/provider, merge-queue/update/restack, final integration proof, verification, recovery, and cleanup layers.

`ACTIVE_CONVERGENCE_SET` is only a derived/reconstructible acceleration index. A stale/missing index cannot suppress an obligation. A waiting external/provider state remains a nonterminal obligation and is refreshed on every later invocation.


## Amendment by ADR-039

Repository admission/reactivation before new managed writes is an External Control Plane responsibility under [`EXTERNAL-CONTROL-PLANE-CONTRACT.md`](../specification/external-control-plane-contract.md). The durable registry remains a shared Git coordination substrate consumed by `ruu`; `ACTIVE_CONVERGENCE_SET` remains only a derived acceleration index under ADR-036.


## Amendment by ADR-041

The shared coordination substrate also carries durable monotonic convergence demand and fenced top-level executor ownership. Explicit invocations are coalescible demand signals rather than FIFO work items. V1 is single-host; a distributed multi-host coordination domain is not an implicit extension of this ADR.

## Amendment by ADR-055

A nonterminal `CrossRepositorySettlementDemand` is authoritative managed obligation state and therefore keeps/reactivates the affected managed repositories regardless of `ACTIVE_CONVERGENCE_SET` cache state. ADR-055's retrospective External Control Plane audit also makes ADR-022's repository admission/reactivation contract explicit in the normative companion file.


## Amendment by ADR-056

Brand-new repository identity may be reserved during an external `RepositoryProvisioningOperation`, but ordinary managed authoring admission occurs only after ADR-056 establishes the intended Git repository and exact non-null configured-target bootstrap OID `B0`. The External Control Plane/Repository Provisioner owns that creation/bootstrap boundary; `ruu` consumes the admitted stable `repository_id` and its exact Git/provider facts. Path/name collisions never define identity, and lazy provider attachment does not mint a second repository identity.
