# ADR-056: Bootstrap new repositories before managed authoring and keep provider creation external

- **Status:** Accepted; amended by ADR-061 and clarified by ADR-078
- **Date:** 2026-09-06
- **Decision order:** 056

## Context

ADR-015 and ADR-023 require repository-local ConvergenceUnit/ContributionUnit topology to exist before the first managed write, while `ruu` is invoked later to advance already-existing managed Git state. Those decisions assumed that the repository itself already existed and therefore had a configured target/base OID from which the ConvergenceUnit could be provisioned.

A development session may discover during implementation that a completely new repository is required. Treating that case as an ad hoc `git init` by the coding agent would bypass pre-edit isolation, identity, policy, and recovery boundaries. Allowing a repository with an unborn target into the managed model would also introduce nullable/nonexistent target OIDs into ancestry, policy-baseline, verification, CAS, DIRECT-promotion, and readiness invariants that otherwise operate on exact Git objects.

The architecture therefore needs a bootstrap contract that turns a nonexistent repository into an ordinary managed repository before any ContributionUnit receives write authority, without making `ruu` itself a repository/infrastructure provisioner.

## Decision

### 1. Repository creation is outside `ruu`

`ruu` MUST NOT create a local repository or provider repository as a side effect of convergence.

A coding agent/session/orchestrator may emit a request such as:

```text
RepositoryNeed {
  semantic purpose
  suggested human name, if any
}
```

but the request carries no creation authority.

The **External Control Plane** owns repository-creation authorization and policy resolution. A **Repository Provisioner** acting on its behalf executes authorized creation. The control plane may be a user-facing tool, orchestrator, agent runtime, policy engine, provisioner, or composition of those roles; no particular implementation is required.

### 2. RepositoryCreationPolicy is external and pre-repository

Because the repository does not yet exist, creation authority cannot originate from repository-committed policy in that repository.

The External Control Plane resolves a `RepositoryCreationPolicy` (or equivalent standing/explicit authorization) sufficient for the requested creation. It may determine, as applicable:

```text
creation allowed / denied
canonical repository identity
local managed locator
provider, if any
provider account / organization / namespace
canonical provider repository name
visibility
configured default target ref
bootstrap profile
governance/bootstrap requirements
whether provider attachment is eager or may be deferred
```

An agent may suggest values but MUST NOT self-authorize provider/account/organization/visibility or bypass the resolved creation policy.

If provider-repository creation is authorized but visibility is otherwise genuinely underdetermined, the built-in safe default is:

```text
PRIVATE
```

No built-in rule infers `PUBLIC`. Provider/account/organization/namespace are not guessed when authority is insufficient; the affected provisioning operation blocks/fails closed.

### 3. Every newly admitted repository has a real non-null bootstrap target OID

V1 does not admit an unborn/null target into the managed Git model.

Before any ConvergenceUnit/ContributionUnit managed authoring begins, the Repository Provisioner MUST establish an exact configured target ref at an exact commit OID `B0`:

```text
new repository
  ↓ authorized bootstrap
configured target (normally main) → B0
  ↓ RepositoryBootstrapContract satisfied
normal managed repository
```

`B0` may be a minimal root commit (including an empty-tree root commit) or a bootstrap/template commit containing authorized initial files such as policy, CI/bootstrap configuration, `.gitignore`, license material, or repository scaffolding. The exact content is a creation-policy/bootstrap-profile concern; the architectural requirement is that the authoritative configured target exists at a real exact OID before managed authoring.

Once `B0` exists, ordinary ADR-015/ADR-023 provisioning applies unchanged:

```text
configured target @ B0
→ ConvergenceUnit ref @ B0
→ new ContributionUnit ref @ current ConvergenceUnit state
→ isolated worktree
→ external mutation authority
→ first managed write
```

This prevents nullable target/base semantics from leaking into `ruu` ancestry, policy, verification, readiness, candidate materialization, or DIRECT CAS+FF rules.

### 4. Repository admission is an explicit handoff boundary

The repository is not considered admitted for ordinary managed authoring merely because some filesystem directory or provider object exists.

The External Control Plane/Repository Provisioner MUST durably establish and observe the `RepositoryBootstrapContract`, including at least the applicable facts below:

```text
stable repository_id allocated/bound
+ authorized local locator established
+ locator contains the intended valid Git repository
+ configured target ref exists at exact non-null B0
+ required bootstrap/governance profile is established
+ provider binding exists and is validated if required for the current phase
+ observed facts match the durable provisioning intent
→ REPOSITORY_ADMITTED
```

Only after `REPOSITORY_ADMITTED` may ADR-015/023 create the first managed ConvergenceUnit/ContributionUnit authoring surface.

Once admitted, `ruu` treats the repository exactly like any other existing managed repository; it does not need a special `NEW_REPOSITORY`, `UNBORN_TARGET`, or null-OID path.

### 5. Local repository creation and provider repository creation are distinct

Repository identity is not provider-location identity.

V1 permits:

```text
create/admit local repository first
→ managed local authoring may proceed
→ attach/create provider repository later when required
```

or eager provider creation when policy requires it.

A missing provider binding blocks only provider-sensitive operations that require that binding, for example provider governance discovery, provider PR creation/publication, provider checks/review/merge-queue interaction, or remote publication whose destination is that provider. It does not retroactively invalidate otherwise-authorized local managed authoring.

When a provider repository is later attached, the provisioner establishes/observes the binding to the same stable `repository_id` and establishes the configured provider target/bootstrap facts required by policy before provider-sensitive `ruu` progression may use it.

### 6. Provisioning is durable, idempotent, and reconciler-oriented

Repository creation/provisioning can contain non-atomic external effects. The External Control Plane/Repository Provisioner therefore owns durable provisioning intent and recovery equivalent in spirit to:

```text
RepositoryProvisioningOperation
→ one or more attempts
→ observe local/provider reality
→ adopt already-realized steps
→ continue until RepositoryBootstrapContract is satisfied or blocked
```

This operation is outside the `ruu` CoordinationStore unless an implementation deliberately shares infrastructure; ADR-042's concrete `ruu` store is not made responsible for repository creation.

Crash recovery MUST prefer exact observation/adoption over blind recreation.

### 7. Names/paths are not identity and collisions fail closed

Neither a filesystem path nor a repository/provider name is sufficient evidence that an observed repository is the one created by a durable provisioning operation.

A retry may adopt a previously created local/provider repository only when durable provisioning identity/bindings and exact observed facts establish that it is the same intended repository.

Otherwise:

```text
occupied local locator
or provider name collision
or mismatched provider repository identity
→ IDENTITY_CONFLICT / BLOCKED
```

The system MUST NOT silently adopt an unrelated preexisting repository because the requested name happens to match.

### 8. No destructive rollback of partially created repositories

If provisioning has already created a local/provider repository or bootstrap object and a later configuration step fails, the built-in recovery path is reconcile/continue/block, not destructive deletion.

Deleting a local or provider repository requires separate explicit destructive authority. A provisioning failure does not itself authorize that deletion.

### 9. Promotion grouping remains unchanged

A repository created during an ordinary development session can participate in that session's PromotionGroup exactly like any other repository once admitted and its ConvergenceUnit is part of the group declared by the External Control Plane.

If a genuinely new repository/new ConvergenceUnit is first discovered during later correction work after an immutable PromotionGroup has already been declared, ADR-053 still applies: the new logical scope cannot be appended to the old closed group and requires a different/superseding PromotionGroup workflow.

## Rationale

A real bootstrap commit is a small cost that preserves the existing exact-state model everywhere else. Supporting unborn/null targets would force special cases into ancestry, trusted-target policy baselines, candidate materialization, verification bindings, readiness, and exact-old DIRECT target advancement.

Separating local creation from provider creation also preserves agent autonomy without creating unnecessary external provider resources during exploratory work. External side effects remain policy-authorized, identity-safe, and recoverable.

## Consequences

- Backlog item **30.26 is closed**.
- `ruu` receives no new repository-creation command or provider-resource creation authority.
- ADR-015/023 provisioning now explicitly begins only after `RepositoryBootstrapContract` admission for brand-new repositories.
- The External Control Plane contract gains repository-creation authorization, bootstrap, provider-attachment, idempotence, and collision responsibilities.
- V1 has no managed null/unborn target state.
- Provider creation may be eager or lazy; provider-sensitive progression waits for the required provider binding.
- Built-in underdetermined provider visibility defaults to `PRIVATE`, never `PUBLIC`.
- Repository creation failures do not authorize destructive rollback/deletion.

## Related decisions

Amends ADR-015, ADR-022, ADR-023, ADR-039, and the normative External Control Plane contract. It preserves ADR-042's repository identity/locator separation and recovery philosophy without moving external repository-provisioning operations into `ruu`. ADR-043's trusted repository policy still begins from the authoritative target baseline; for a new repository that baseline is `B0` after bootstrap. ADR-053's immutable PromotionGroup scope-expansion rule remains unchanged.

## Amendment by ADR-061

The configured bootstrap target at `B0` is the non-null repository bootstrap/base admission state. ADR-061 separately requires each subsequently created/reused ConvergenceUnit to carry an immutable PromotionTarget before first managed write. In the common same-repository case both may designate the same branch, but they are distinct architectural responsibilities.



## Clarification by ADR-078

This ADR's "outside `ruu`" wording denotes **outside the later convergence engine/invocation and outside its semantic authority**, not a mandatory product-packaging boundary. A Ruu distribution MAY bundle a Repository Provisioner/harness integration that executes an externally authorized `RepositoryCreationPolicy` before managed authoring. The convergence engine still MUST NOT create repositories as a side effect of convergence, and an agent still cannot self-authorize repository/provider creation.
