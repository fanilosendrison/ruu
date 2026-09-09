# ADR-073 — Require Git worktrees as the v1 authoring isolation substrate

- **Status:** Accepted — authoring-surface evidence requirement amended by ADR-074; initial handoff/admission clarified by ADR-079
- **Date:** 2026-09-08
- **Closes:** backlog 30.47
- **Clarifies/Amends:** ADR-001, ADR-002, ADR-023, ADR-038, ADR-058, ADR-059, ADR-064, ADR-070 product-conformance reading, the consolidated specification, and the External Control Plane contract

## Context

The current architecture authors concurrent ContributionUnits through dedicated Git worktree/ref surfaces:

```text
agent/session
→ isolated ContributionUnit worktree
→ frozen mutation handoff
→ exact whole-surface Git tree construction
→ canonical managed checkpoint
→ convergence
```

Backlog 30.47 asked whether v1 should generalize this authoring boundary to accept arbitrary immutable inputs such as a prebuilt commit OID, `tree + parent`, or a sandbox snapshot supplied directly by a materially different Development System.

That generalization has no concrete v1 product requirement today. It would add a second authoring contract, new exactness/admissibility proofs, provenance/authority questions, and adapter abstractions before any real producer needs them.

The likely future alternative is not an arbitrary commit/tree feed but a stronger isolated sandbox substrate. That is a plausible v2 direction, but it should not be prematurely encoded as a v1 API.

## Decision

### 1. V1 authoring uses Git worktrees normatively

Every actively authored managed ContributionUnit in v1 MUST be provisioned with its own dedicated Git worktree/ref editing surface before its first managed write.

Concurrent ContributionUnits MUST NOT share one mutable checkout.

Therefore the v1 authoring path is normatively:

```text
ContributionUnit
→ dedicated Git worktree/ref surface
→ external authoring
→ frozen mutation-authority handoff
→ exact whole-surface capture
→ canonical managed checkpoint
```

### 2. V1 has no alternative direct immutable authoring input contract

V1 does not define a normative Development-System input that bypasses the managed worktree by directly supplying:

```text
arbitrary prebuilt commit OID
arbitrary tree + parent tuple
filesystem/sandbox snapshot as direct checkpoint input
other external immutable authoring artifact
```

This does not forbid ordinary native Git commits made by a human/agent **inside the managed worktree**. Native Git remains ordinary under ADR-058/070/071; such state is reconciled from the managed worktree/ref topology. The prohibition is on defining a second v1 authoring substrate that bypasses that topology.

### 3. Worktrees are the v1 substrate, not the eternal semantic identity

The guarantees that matter are the properties the v1 worktree model provides:

```text
isolated mutable authoring state
exact repository/base identity
dedicated ContributionUnit authority boundary
freezeable mutation handoff
complete/deterministic Git-relevant capture
no shared mutable checkout between concurrent ContributionUnits
```

The durable identity of a ContributionUnit and its already-created exact managed checkpoints does not depend on the worktree continuing to exist after capture. ADR-038 and ADR-071 remain controlling for post-capture artifact disappearance/abandonment.

Thus:

```text
worktree required while v1 managed authoring is active
≠
worktree required forever after exact state is captured
```

### 4. Future sandbox support requires a new architecture decision

A future version MAY replace or supplement worktrees with a sandbox substrate only if that substrate proves at least the same relevant isolation, base-identity, mutation-authority, and exact-capture properties.

Such support is intentionally deferred and MUST be introduced by a future ADR with explicit conformance rules. ADR-073 does not predefine an `AuthoringIngress`, `SnapshotAdapter`, generic external-tree API, or trust model for that future design.

### 5. Do not abstract for abstraction purity

Core semantic wording SHOULD name the invariant properties where that improves future substitutability, but v1 implementation/contracts may and should state plainly that the concrete supported authoring substrate is Git worktrees.

No implementation is required to build unused adapter layers merely to preserve hypothetical pluggability.

## Consequences

- V1 has one concrete, testable authoring topology.
- Existing worktree isolation/freeze/canonical-capture ADRs remain the normative path rather than one adapter among speculative peers.
- Ordinary Git inside the managed worktree remains supported.
- Post-checkpoint worktree deletion does not erase durable managed identity/state.
- A sandbox-based v2 remains architecturally possible without claiming compatibility before its invariants are specified and proven.


## Amendment by ADR-074

The concrete v1 managed authoring surface is now explicitly `dedicated worktree/ref + native reflog evidence infrastructure`. ADR-075 adds that the selected native-ref backend/adapter must also satisfy the pre-linearization binding-cessation/replacement observation capability contract before live managed authoring is admitted. The reflog remains evidence infrastructure only: durable ContributionUnit identity is still independent of branch name, worktree lifetime, reflog lifetime, and ref-backend name.


## Amendment by ADR-079

The dedicated worktree/ref surface is a **candidate provisioning surface** until exact managed admission completes. The pre-edit provisioner retains exclusive mutation authority, establishes a conforming native `RefAdmissionBarrier` over the exact candidate ref, revalidates repository/worktree/HEAD/ref/OID topology, commits the authoritative current binding while the barrier is still held, releases the barrier, and only then transfers authoring authority to the producer. `git worktree lock` may be defense-in-depth but is not the correctness primitive because it does not freeze HEAD/switch behavior.
