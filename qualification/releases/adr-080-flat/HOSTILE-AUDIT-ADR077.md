# Hostile Audit — ADR-077 observer ownership / installation / coexistence

- **Date:** 2026-09-08
- **Target:** ADR-077
- **Verdict:** **PASS WITH 30.54/30.55 EXPLICITLY REMAINING OPEN**

## Attack 1 — Linked worktree bypasses a worktree-local observer

**Attack:** install the observer only on the managed worktree while another linked worktree mutates the same `refs/heads/*` binding.

**Resolution:** rejected structurally. ADR-077 requires repository-common coverage for shared refs. `git-native-observation-smoke-v4.sh` demonstrates on Git 2.47.3/files that a traditional common hook is visible when the deletion is initiated from a linked worktree.

## Attack 2 — Existing project/user hook is silently replaced

**Attack:** obtain ADR-075 coverage by overwriting a foreign `reference-transaction` or changing `core.hooksPath`.

**Resolution:** forbidden. Observer ownership is exact and expected-state guarded. Foreign configuration causes composition/admission failure unless a separately supported composition adapter exists.

## Attack 3 — Turn Ruu into a universal hook dispatcher

**Attack:** wrap arbitrary pre-existing hooks automatically so `ruu` can always occupy the only legacy slot.

**Resolution:** rejected. Generic custody of foreign hook order, input, exit behavior, upgrades and removal is outside product scope. Git-native configured multi-hook composition is preferred when available; explicit dispatcher adapters remain possible if independently demonstrated.

## Attack 4 — Presence of a hook file is treated as proof of coverage

**Attack:** hook exists at an expected pathname but effective `core.hooksPath`, config scope, engine behavior or execution path bypasses it.

**Resolution:** rejected. Coverage requires functional attestation. Smoke v4 demonstrates both observer/veto reachability and a foreign `core.hooksPath` making the default hook ineffective.

## Attack 5 — Old/alternate Git engine ignores the admitted observer surface

**Attack:** a repository is attested with one Git/profile and then another engine writes refs without triggering the observer.

**Resolution:** ADR-077 makes coverage a property of an admitted mutation-engine/adapter path. V1 guarantees Git core; alternative engines need separately demonstrated adapters. A writer bypassing that path cannot acquire managed semantics.

## Attack 6 — libgit2/JGit/direct writer changes a managed ref

**Attack:** mutate the ref store without any ADR-075 causal preparation, then rely on the next sweep to infer what happened.

**Resolution:** fail closed as `UNWITNESSED_MANAGED_BINDING_MUTATION`. ADR-076 forbids synthesizing causal history from final state. The ECP's generation-bound recovery declaration remains the explicit exceptional path.

## Attack 7 — Repair observer and pretend the gap never happened

**Attack:** coverage disappears, a managed transition may occur, observer is repaired, then current health is used to bless the whole interval.

**Resolution:** forbidden by coverage epochs. Repair opens a new trusted epoch and cannot retroactively cover the prior gap. Exact consequences of a persistence/coverage failure are intentionally delegated to open item 30.54.

## Attack 8 — Clone inherits managed identity so observer is assumed present

**Attack:** logical `repository_id` survives relocation/recreation, but hooks/configuration do not.

**Resolution:** ADR-077 separates repository identity from local observer realization. Clone/recreation/reactivation/new effective profile requires re-establishment and functional re-attestation before managed authoring.

## Attack 9 — Concurrent sessions race installing observers

**Attack:** each session assumes it owns hook installation and clobbers another session/tool.

**Resolution:** observer binding is repository-scoped shared infrastructure. Install/upgrade/remove are expected-state/CAS operations and already-correct state is adopted idempotently.

## Attack 10 — Git 2.54 feature accidentally becomes a hidden universal minimum

**Attack:** configured multi-hook behavior is described as the solution and older but otherwise conforming Git paths become architecturally invalid.

**Resolution:** ADR-077 explicitly rejects that coupling. Git 2.54+ configured hooks are a preferred composition profile, not the semantic definition. The retained Git 2.47.3/files traditional-hook profile remains demonstrably usable when its effective slot is uncontested.

## Remaining attack surface intentionally deferred

ADR-077 does **not** decide:

- exact reject/retry behavior when required witness persistence fails inside a transaction or when a coverage gap is discovered (**30.54**);
- how local native observations compose with provider-side merges, remote writers, or remote-ref movement (**30.55**).

Those are not hidden holes in 30.53; they remain explicit next decisions under umbrella 30.49.
