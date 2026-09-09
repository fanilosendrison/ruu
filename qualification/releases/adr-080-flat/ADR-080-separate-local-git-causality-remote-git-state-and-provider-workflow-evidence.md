# ADR-080 — Separate local Git causality, remote Git state, and provider workflow evidence

- **Status:** Accepted
- **Date:** 2026-09-08
- **Closes:** backlog 30.55 and the 30.49 native-Git observation-plane umbrella
- **Amends:** ADR-042, ADR-051, ADR-052, ADR-065, ADR-066, ADR-074, ADR-075, ADR-077, ADR-079, the consolidated specification, the External Control Plane contract, and the observation backlog
- **Leaves open in this cluster:** none

## Context

ADR-074–079 deliberately make the local native-Git observation plane narrow: only disposition of a currently bound managed authoring ref requires irreducibly causal pre-linearization evidence. All other correctness-relevant Git/provider facts are re-observed from current authoritative state when a transition needs them.

30.55 asks where that local authority stops. A local `reference-transaction` observer cannot witness a provider-side merge, a ref mutation performed in another clone, or a remote ref movement that the local clone has not yet observed. Treating local hooks, remote-tracking refs, provider webhooks, and provider APIs as one distributed event stream would reintroduce exactly the ambiguity the local observation work removed.

The product also must remain meaningful without GitHub/GitLab or any provider API. A bare Git remote over ordinary Git transport must be able to support remote publication and exact remote-ref reconciliation whenever repository policy permits a provider-free route.

## Decision

### 1. Observation authority is source-domain scoped

The reconciler composes facts from three distinct source domains:

```text
LOCAL_GIT
→ exact local repository/worktree/ref/object state
→ the only current pre-linearization causal observer domain for managed authoring-binding disposition

REMOTE_GIT
→ exact current refs/OIDs exposed by a remote Git endpoint
→ exact-preconditioned remote ref mutation/result observation

PROVIDER
→ provider-owned workflow/governance/finalization facts
→ submissions, reviews, checks, merge queues, provider transformations and equivalent provider objects
```

No source implicitly acquires authority over another source's facts.

A local native hook is authoritative only for the local mutation surface on which its adapter coverage was established. It never proves that a remote/provider mutation happened merely because a local cache later changed.

### 2. Remote-tracking refs are local caches, never authoritative remote state

`refs/remotes/<remote>/*` and equivalent local tracking state record what this clone last learned. They may be stale even while the remote has already moved or deleted the corresponding ref.

A transition that requires **current authoritative remote Git state** MUST obtain it from an admitted direct remote-Git observation primitive, for example an exact transport/ref advertisement such as `git ls-remote`, a fetch/transport result whose adapter contract proves the required freshness/state, or an equivalent backend/provider ref primitive explicitly demonstrated to be authoritative for that remote Git ref.

A local hook observing a remote-tracking ref update proves only that the local cache was updated. It does not manufacture a causal remote-ref event.

### 3. Remote Git publication/recovery does not require a provider

`REMOTE_GIT` is independently useful and a bare Git remote is a first-class endpoint.

When Ruu owns a remote-ref mutation, the mutation must retain the existing exact-precondition semantics: expected old identity, route/policy/currentness guards, and exact post-operation re-observation. A Git-core implementation may use an explicit expected-old lease/ref update such as `--force-with-lease=<ref>:<expected>` where its semantics match the required operation; the architecture remains capability-based.

If a network/result acknowledgement is lost:

```text
Operation/Attempt outcome = UNKNOWN
→ re-observe authoritative remote ref
→ expected new exact state present: adopt if all other guards still hold
→ expected old exact state present: effect not realized; retry only under current authority
→ different state present: concurrent drift; reconcile/fail closed as required
```

No exactly-once remote event delivery is required.

### 4. PROVIDER is an optional capability domain

A repository/route that needs only native Git remote publication MUST NOT require a provider API, provider webhook, PR/MR object, merge queue, or provider event history.

If current policy requires a semantic operation that belongs to `PROVIDER` and no conforming provider adapter/capability exists, that transition is `UNSUPPORTED`/blocked for missing capability. It is not `UNKNOWN_INCONSISTENT`, and Ruu does not emulate provider semantics with ordinary Git refs.

Conversely, when a provider-mediated route is required, provider-owned facts come from the provider domain and remain independently composed with authoritative remote/target Git facts as already required by ADR-065/066.

### 5. Webhook delivery is an unreliable transport, not a completeness authority

A webhook delivery MAY serve as:

```text
WAKEUP
→ schedule/reprioritize reconciliation

POSITIVE_PROVIDER_EVIDENCE
→ authenticated provider-scoped historical fact
→ only when the adapter demonstrates exact subject/revision/result semantics
```

A webhook delivery MUST NOT, merely by existing, be treated as:

```text
complete provider event log
current remote Git state
cross-system ordering authority
exactly-once semantic operation identity
```

Absence of a webhook never proves absence of the provider event. Delivery loss, duplication, redelivery and reordering are tolerated by idempotent observation/adoption semantics.

A correctness-critical provider fact obtained from a webhook must either be recoverable/revalidable from a durable authoritative provider surface or be strictly additive evidence whose loss does not make recovery depend on that delivery. A provider adapter may assign stronger historical authority only to a separately demonstrated durable, replayable, sufficiently complete provider event/audit capability; that authority is not implied by generic webhooks.

### 6. Delivery identity is not semantic operation identity

Provider delivery/event occurrence identifiers are useful for authentication, replay detection and deduplication. They do not automatically become the logical managed `Operation`, provider finalization identity, PromotionUnit identity, or semantic adoption identity.

The ADR-076 rule generalizes across boundaries:

```text
observation occurrence/delivery
≠ managed semantic transition identity
```

A delayed duplicate provider event may add duplicate evidence for an already-adopted fact but cannot re-run the logical transition.

### 7. Cross-source composition uses exact identities, not wall-clock ordering

Observations are source-scoped and retain enough identity/provenance to compose exact facts, conceptually including:

```text
source_domain
source_identity
subject identity
exact ref/revision/result state
provider/transport occurrence identity when available
freshness/revision information when the source defines it
observed_at for diagnostics, never generic global causality
```

A transition may require a chain such as:

```text
immutable candidate C
→ exact submission projection H
→ provider finalization H → R on immutable target T
→ authoritative remote/target Git observation O containing/equal to R
```

Those links are established by exact source-owned identities and documented adapter semantics. Relative arrival time or wall-clock timestamps from local Git, provider webhooks, remote reads and policy reads are never sufficient to invent a global causal order.

If cross-system chronology is actually correctness-relevant and the available authoritative source revisions/operation identities cannot establish it, the affected transition fails closed/`UNKNOWN_INCONSISTENT`. Missing chronology does not block transitions that depend only on current exact state.

### 8. Remote publication artifacts do not inherit local managed-binding disposition semantics

The `CONTINUATION | ABANDON` causal classifier applies only to the **currently bound local managed authoring ref** under the admitted local native observation domain.

Remote deletion/creation/rename-like topology, remote-tracking ref movement, provider branch deletion, or submission-ref drift does not by itself abandon, continue or rebind a ContributionUnit. Those artifacts are reconciled according to their own publication/submission/target obligations from exact current remote/provider state.

Therefore:

```text
remote branch deleted
≠ local managed authoring ABANDON

remote delete + create elsewhere
≠ local managed authoring CONTINUATION
```

### 9. Historical provider facts and current Git state remain distinct

A positively established provider historical fact may remain true even after current target topology changes. For example, exact provider finalization `H → R` remains historical evidence after later target drift, while the separate current remote/target observation may no longer contain `R`.

This preserves ADR-065/066 and the terminal historical meaning of `PROMOTED`: historical realization and current topology are different facts.

## Consequences

- The local observer stays small and never becomes a network/provider proxy.
- Bare Git remotes remain fully supported for provider-free routes.
- Remote-tracking refs can be used as caches/wakeups but never as authoritative remote currentness.
- Provider APIs/webhooks do not contaminate core Git identity or local causal semantics.
- Webhooks can improve latency and preserve useful positive evidence without becoming a correctness single point of failure.
- Remote/provider outages localize only transitions requiring those domains; local managed authoring and unrelated Git operations remain independent.
- Cross-system ambiguity is failed closed only where the transition genuinely requires the missing chronology or identity proof.
- The 30.49 observation-plane umbrella is now coherent: causal transactional observation is minimal/local, exact-state rediscovery is source-owned, and advisory delivery remains non-authoritative.

## Rejected alternatives

### Treat local hooks as the start of a distributed transaction
Rejected. A local hook has no causal control over another clone, remote server or provider and cannot make such effects atomic with local SQLite/Git state.

### Treat remote-tracking refs as current remote truth
Rejected. They are local caches whose freshness depends on fetch/transport observation.

### Require GitHub/GitLab/provider APIs for every remote
Rejected. Native Git remotes are a complete and useful remote-ref domain without provider workflow objects.

### Make webhooks wakeup-only and discard all payload evidence
Rejected as unnecessarily weak. Authenticated payloads may carry useful positive provider-scoped historical evidence when exact semantics are demonstrated.

### Make webhooks a complete authoritative event log
Rejected. Generic delivery channels may lose, duplicate, redeliver or reorder occurrences and absence is not negative proof.

### Infer cross-system chronology from timestamps
Rejected. Wall-clock observations across independent systems do not create a reliable causal order.

## Verification obligations

Implementations/adapters must demonstrate, where applicable:

1. authoritative remote-ref observation is distinguishable from local remote-tracking cache state;
2. exact expected-old remote mutation rejects stale concurrent state and re-observation recovers ambiguous outcomes;
3. provider-free remote Git progression works without provider objects/webhooks;
4. missing provider capability blocks only provider-required transitions;
5. webhook delivery duplicates/reordering/loss cannot duplicate semantic adoption or establish negative evidence;
6. local remote/submission artifact deletion never invokes local managed-binding `ABANDON/CONTINUATION` semantics;
7. source-domain provenance and exact identities are retained wherever cross-source composition is correctness-relevant.
