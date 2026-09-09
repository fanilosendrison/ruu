# State-Space Audit v25 — ADR-056 new-repository bootstrap/admission

## 1. Scope

This audit extends v24 after ADR-056 closes backlog 30.26. It revalidates every prior finite architecture family and adds explicit coverage for brand-new repository creation authority, exact bootstrap/admission, local-versus-provider creation separation, provider-visibility authority, collision-safe provisioning adoption, and non-destructive recovery after partial provisioning.

ADR-056 remains outside `ruu` execution ownership: the External Control Plane resolves creation authority and a Repository Provisioner performs/reconciles creation. The new Git smoke therefore validates only the exact Git bootstrap boundary (`unborn` repository → real `B0` target → ordinary ConvergenceUnit/ContributionUnit descendants), while the state-space/static audit validates the external authority and recovery contract.

The pass also rechecks the External Control Plane summary after ADR-050 and removes one stale phrase that still described promotion topology as externally declared; only PromotionGroup membership remains externally declared, while promotion dependency/topology is derived by `ruu`.

## 2. ADR-056 properties exercised

The executable audit checks that:

1. an agent/user/orchestrator request never gives `ruu` repository-creation authority;
2. repository creation is permitted only under current External Control Plane creation authority and is executed by the Repository Provisioner role;
3. a brand-new repository cannot become `REPOSITORY_ADMITTED` with an absent/unborn configured target;
4. exact non-null `B0`, valid repository facts, required bootstrap/governance, observation match, and any phase-required provider binding are all admission guards;
5. local managed authoring may proceed after local admission without eager provider creation, while provider-sensitive operations remain blocked until a valid provider binding exists;
6. an underdetermined provider visibility becomes `PRIVATE`, never `PUBLIC`;
7. an explicit/public outcome without public authority does not become authorized merely because an agent suggested it;
8. matching repository names/paths do not authorize adoption: durable identity/binding and exact observed facts must match;
9. a later provisioning failure does not authorize deleting an already-created local/provider repository without separate destructive authority;
10. the main specification, ADR-015/023/039/056, backlog, and External Control Plane contract consistently keep repository creation outside `ruu`;
11. no current normative document leaves backlog 30.26 open;
12. V1 has no managed `UNBORN_TARGET`/null-OID authoring path.

## 3. New finite families

ADR-056 adds:

```text
new_repository_creation_authority: 18
repository_bootstrap_admission: 64
local_provider_creation_decoupling: 8
repository_visibility_authority: 24
repository_provisioning_identity_collision: 12
repository_provisioning_non_destructive_recovery: 16
```

Every v24 family is re-run as well.

## 4. Static integration checks

Static checks verify that:

- ADR numbering is contiguous through **ADR-056**;
- main §30 marks **30.26 resolved by ADR-056** and the open backlog no longer lists 30.26;
- main pre-edit provisioning routes brand-new repositories through `RepositoryCreationPolicy → RepositoryBootstrapContract → REPOSITORY_ADMITTED → ADR-015/023` before first managed write;
- main invariants 125–130 encode request/authority separation, no unborn/null target, bootstrap admission, local/provider decoupling, collision-safe identity, and non-destructive provisioning recovery;
- `EXTERNAL-CONTROL-PLANE-CONTRACT.md` defines creation authorization, exact `B0` admission, `PRIVATE` fallback, lazy provider attachment, identity-safe retry/adoption, and separate destructive authority;
- ADR-015/023 are amended so ordinary ConvergenceUnit/ContributionUnit provisioning starts only after new-repository bootstrap admission;
- ADR-039's formerly open 30.26 boundary is now explicitly closed by ADR-056;
- old current-summary wording that treated promotion topology as externally declared is removed; ADR-050 derived-topology semantics remain intact;
- existing ADR-048 materialization, ADR-050 restack, ADR-052 DIRECT CAS+FF, ADR-053 correction, ADR-054 retirement, and ADR-055 settlement families remain intact.

## 5. Result

Executable result:

```text
Ruu state-space audit v25: PASS
changed/revalidated finite combinations evaluated: 15,966
markdown artifacts statically cross-checked: 84
```

Concrete Git smoke results:

```text
Ruu ADR-048 materialization smoke: PASS
Ruu ADR-050 restack smoke: PASS
Ruu DIRECT target advance smoke v1: PASS
Ruu repository bootstrap smoke v1: PASS
```

Expected brand-new repository boundary:

```text
session/agent discovers need for new repo
        ↓ request only
External Control Plane RepositoryCreationPolicy
        ↓ authorize/resolve
Repository Provisioner
        ↓ durable create/observe/adopt
local Git repository
        ↓
configured target → exact B0
        ↓
RepositoryBootstrapContract satisfied
        ↓
REPOSITORY_ADMITTED
        ↓
ordinary ADR-015/023 ConvergenceUnit + ContributionUnit provisioning
        ↓
first managed authoring

provider repository may be attached eagerly or later;
provider-sensitive progression waits for that binding.
```

No unborn/null managed target, no name-based silent adoption, no automatic public repository inference, and no destructive rollback from provisioning failure.
