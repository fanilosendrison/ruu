---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Bind each ConvergenceUnit to an immutable pre-authoring PromotionTarget"
id: "ADR-061"
status: "accepted"
date: "2026-09-07"
decision_body_sha256: "d06fe81a0e41b330e4a789b4413721066fe2acddb4d516a72c7c45dbbc32316d"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-061 — Bind each ConvergenceUnit to an immutable pre-authoring PromotionTarget

- **Status:** Accepted
- **Date:** 2026-09-07
- **Decision order:** 061

## Context

The architecture already requires repository-local ConvergenceUnit/ContributionUnit topology to exist before the first managed write. ADR-006/015 describe a `target/base → ConvergenceUnit → ContributionUnit` hierarchy, and ADR-056 requires a real configured bootstrap target for brand-new repositories.

However, the current wording leaves two distinct concepts insufficiently separated:

1. the repository-local Git base/ref from which a ConvergenceUnit is provisioned and synchronized during authoring; and
2. the logical repository/ref that the completed work is ultimately intended to reach.

The second concept was also partially assigned to `EffectivePromotionPolicy`, which previously said it resolved `target_repository` / `target_ref`. That creates an architectural ambiguity: a later policy/configuration refresh could appear to choose or retarget the destination of work that was already authored.

In the intended development-system model, the higher-level system should not finish authoring and then issue a late command such as `merge main`. It should establish before authoring that a ConvergenceUnit belongs to a particular destination lineage. Later `ruu` invocations mechanically advance that already-bound work as far as current state and policy permit.

## Decision

### 1. Separate `ConvergenceBase` from `PromotionTarget`

A ConvergenceUnit has two distinct destination-related bindings:

```text
ConvergenceBase
= repository-local Git ref/state used as the managed authoring/convergence base

PromotionTarget
= immutable logical final destination
  (target_repository_id, target_ref)
```

The legacy phrase `target/base` in internal synchronization rules refers to the **ConvergenceBase**, not to a mutable late promotion-destination choice.

For a simple same-repository workflow they will commonly refer to the same logical branch, for example:

```text
source repository     = RepoA
ConvergenceBase       = RepoA/refs/heads/main
PromotionTarget       = RepoA/refs/heads/main
```

For a cross-repository contribution they may differ, for example:

```text
source repository     = contributor-fork
ConvergenceBase       = repository-local authorized base/tracking state
PromotionTarget       = upstream/refs/heads/main
```

### 2. PromotionTarget is established before the first managed write

The External Control Plane / pre-edit provisioner MUST resolve and durably bind the ConvergenceUnit's canonical PromotionTarget before any ContributionUnit attached to that ConvergenceUnit receives managed write authorization.

Conceptually:

```text
resolve/admit source repository
→ resolve ConvergenceBase
→ resolve PromotionTarget(target_repository_id, target_ref)
→ create/reuse ConvergenceUnit with immutable target binding
→ provision ContributionUnit/worktree/mutation authority
→ authorize first managed write
```

Reusing an existing ConvergenceUnit requires an exact match of the already-authoritative PromotionTarget. A requested different target is not a mutation of the old ConvergenceUnit; it requires a distinct convergence scope / new ConvergenceUnit identity.

### 3. PromotionTarget is immutable for the ConvergenceUnit lifetime

Once a ConvergenceUnit has admitted managed authoring:

```text
PromotionTarget(CU) = T
```

must remain `T` through `OPEN`, `SEALED`, `READY_INTERNAL`, promotion, correction/continuation while the lineage remains nonterminal, `PROMOTED`, and retirement.

No policy refresh, caller invocation, local config change, provider discovery, review state, or runtime request may silently change:

```text
target_repository_id
target_ref
```

for that ConvergenceUnit.

If the Development System genuinely wants the same authored idea to target another destination, that is new explicit convergence topology, not a policy mutation. The existing ConvergenceUnit is not retargeted.

### 4. `EffectivePromotionPolicy` answers HOW, not WHERE

`EffectivePromotionPolicy` consumes the already-bound PromotionTarget as part of its exact promotion context. It MUST NOT select or rewrite that target.

The boundary is:

```text
WHERE should this work ultimately land?
→ External Control Plane
→ immutable PromotionTarget

HOW may the current exact state reach that target now?
→ Ruu + current EffectivePromotionPolicy + provider capabilities/state
```

Policy may resolve/authorize, as applicable:

```text
promotion_mode = DIRECT | PR
provider/governance operation constraints
submission/rewrite permissions
review/queue requirements
publication repository/remote mechanics when needed
```

The source/target repository relation is derived from authoritative repository identity + PromotionTarget. Policy/provider constraints determine whether the required SAME_REPOSITORY or CROSS_REPOSITORY operation is authorized/supported; they do not invent a different target to obtain a satisfiable policy.

Every `EffectivePromotionPolicy` observation/fingerprint used for authorization MUST be context-bound to the immutable PromotionTarget identity and the exact mutable target-policy baseline/current provider-governance observations from which it was composed. A policy result computed for one target ref is never reusable as authorization for another target.

### 5. Repository-local PromotionGroup projection must be target-coherent

ADR-047 projects one PromotionUnit per represented authoritative source repository. Therefore all ConvergenceUnits from the same source repository that a PromotionGroup projects into one PromotionUnit MUST have the same immutable PromotionTarget.

If one PromotionGroup contains, for the same source repository, members bound to different PromotionTargets:

```text
→ TARGET_INCOHERENT_PROMOTION_GROUP
→ group resolution/promotion for that projection fails closed
→ Ruu MUST NOT split the group by target or choose one target
```

A higher-level workflow that truly intends different targets must declare appropriate distinct convergence/promotion scopes rather than relying on policy-time splitting.

### 6. Target currentness remains dynamic; target identity does not

Immutability applies to the target **identity** `(target_repository_id, target_ref)`, not to its current OID.

The target ref may legitimately advance while work is in progress. Existing synchronization, exact effective-base derivation, policy-baseline reading, stack dependency derivation, and ADR-052 expected-old CAS+FF rules continue to re-observe the current exact target state.

Thus:

```text
immutable: target repository/ref identity
mutable and revalidated: current target OID / provider/governance facts
```

### 7. Invocation remains a convergence demand, not `merge-main` intent

A Development System does not need to transmit a terminal command such as:

```text
ruu --merge-main
```

The destination was already bound before authoring. The system only establishes the lifecycle/grouping/intent facts it owns and signals convergence demand. `ruu` then derives the legal current transitions and may progress from checkpoint through internal convergence and publication toward the immutable PromotionTarget until it reaches a fixed point or localized wait/block.

## Supersession / amendments

This ADR amends:

- ADR-006/015/023 by making the pre-edit ConvergenceUnit topology include an immutable PromotionTarget in addition to its repository-local ConvergenceBase;
- ADR-026 by removing `target_repository` / `target_ref` from policy-selected outputs and treating the source/target relation as derived promotion context that policy authorizes rather than chooses;
- ADR-039 / `EXTERNAL-CONTROL-PLANE-CONTRACT.md` by assigning PromotionTarget resolution/binding/currentness ownership explicitly to the External Control Plane before first managed write;
- ADR-043/044 by making policy composition/currentness operate against a fixed target identity while the target baseline OID and governance observations remain freshly revalidated;
- ADR-045/046/047 by requiring target coherence for repository-local PromotionGroup projection while keeping target outside PromotionUnit content identity because it is already immutable in each member ConvergenceUnit identity/binding;
- ADR-049/050/052 by deriving stable submission destination, dependency target facts, and DIRECT target mutation from the immutable PromotionTarget rather than from a late policy-selected target.

ADR-056's configured bootstrap target remains the required non-null repository bootstrap/base state for a brand-new repository. ADR-061 adds the separate ConvergenceUnit PromotionTarget binding before managed authoring; in the common same-repository case both may designate the same branch.

## Consequences

- The Development System decides `this work is for main` before authoring, not `merge main now` after authoring.
- `ruu` never guesses or retargets semantic destination from invocation reason.
- Policy changes may change DIRECT↔PR eligibility, required review/provider mechanics, or block promotion, but cannot turn `main` work into `develop` work.
- Cross-repository publication remains supported without conflating source repository, repository-local convergence base, and final target repository.
- Same-source PromotionGroup projection is deterministic only when immutable target bindings agree; inconsistent grouping fails closed instead of being silently split.
- Target OID drift remains an ordinary exact-state/currentness concern and does not violate target-identity immutability.

## Amendment — ADR-062 (2026-09-07)

The HOW/WHERE separation is strengthened: policy HOW now resolves `target_realization_route = DIRECT_TARGET_ADVANCE | PROVIDER_SUBMISSION` plus exact provider mechanics. Pull Request is not a destination and not a semantic promotion mode; it is a provider-specific projection used on the provider-submission route. The immutable PromotionTarget remains unchanged by route or provider surface.

