# ADR-042: Use a reconciler-driven CoordinationStore with OS-owned runs and an append-only effect journal

- **Status:** Accepted
- **Date:** 2026-09-05
- **Decision order:** 042
- **Subsequently amended by:** ADR-071 current-disposition causal authorization fence and ref-transaction abandonment ingress

## Context

ADR-041 fixed the semantic concurrency model:

```text
single-host coordination domain
+ coalescible convergence demand
+ at most one authoritative top-level convergence run
+ durable fencing
+ exact-state/CAS adoption
+ exact recovery of non-atomic Git/provider effects
```

It intentionally left backlog item 30.13 open for the concrete CoordinationStore/runtime design.

Subsequent review established that `ruu` is not a durable step workflow and does not need an external workflow orchestrator. Its top-level control flow is a **current-state reconciliation loop**:

```text
convergence demand
→ observe current authoritative state
→ derive all nonterminal obligations
→ progress mechanically safe obligations
→ exactly observe/adopt results
→ repeat until the current global fixed point
```

A crash is therefore not recovered by resuming an in-memory step. Recovery reconstructs current managed state, unresolved effect records, Git/remotes/provider facts, and then reconciles again.

The remaining design questions were:

1. concrete v1 CoordinationStore shape and schema/version discipline;
2. physical ownership and fencing of the one single-host convergence run;
3. durable representation of effects that cross SQLite/Git/provider/filesystem transaction boundaries;
4. transaction boundaries and crash windows;
5. repository identity/relocation binding;
6. temporary recovery-resource lifecycle and GC;
7. hung-process/liveness behavior.

## Decision

### 1. `ruu` is orchestrated by its own reconciler, not by a workflow engine

The top-level runtime is a `ConvergenceEngine` / reconciler. It has no durable `STEP_1 → STEP_2 → STEP_3` execution ontology.

Each sweep operates from **current authoritative state**. Specialized reconcilers may classify obligations as, for example:

```text
NO_ACTION
PROGRESSABLE
WAITING
RECONCILIATION_REQUIRED
BLOCKED
```

An internal resource-aware scheduler may execute independent progressable work in parallel, but scheduling does not change the one top-level convergence-run authority or the global sweep scope.

Waiting provider/CI/review states are represented as nonterminal managed obligations. The engine does not keep the convergence run alive merely to wait for them:

```text
freshly observed WAITING state
+ no other progressable obligation
→ current fixed point
→ release top-level run ownership
```

Recovery after crash is:

```text
load CoordinationStore
→ recover unresolved operations by exact observation
→ re-enumerate current obligations
→ reconcile current state
```

not `resume workflow at previous step`.

### 2. SQLite is the concrete v1 backend, while the contract remains semantic

The v1 implementation uses one host-local SQLite CoordinationStore for the coordination domain.

SQLite is not a portable architecture requirement for future versions, but the v1 implementation is allowed to use SQLite directly rather than building a multi-backend abstraction.

The store is the authority for `ruu` managed coordination state. It is **not** a mirror that supersedes Git/provider truth.

The v1 schema has the following mandatory table families or semantically equivalent normalized representations.

#### 2.1 Schema metadata

```text
schema_meta
  singleton = 1
  schema_version
  migration_id / migration lineage
```

An established non-empty store with a missing/unknown/incompatible schema descriptor, required table, required singleton row, enum value, or invariant MUST fail closed. It MUST NOT silently recreate missing authority or coerce unknown values to defaults.

A brand-new empty store may be initialized. Known older schemas are upgraded only by explicit ordered migrations. Each store-only migration is executed under SQLite serialization in a short transaction and revalidates the resulting invariants before normal coordination writes resume. Unknown newer schemas fail closed.

No schema migration performs Git/provider/filesystem business effects inside the migration transaction.

#### 2.2 Coordination-domain singleton

```text
coordination_domain
  singleton = 1
  requested_generation
  processed_generation
  run_generation
  run_state = IDLE | ACTIVE
  run_token = nullable unique incarnation token
  diagnostic owner/process/timestamp fields as optional non-authority metadata
  row_version
```

Required invariants:

```text
0 <= processed_generation <= requested_generation
run_generation is monotonic and never decrements
run_state = IDLE  ↔ run_token is NULL
run_state = ACTIVE → run_token is non-NULL
```

The OS lock determines physical top-level ownership; this row determines durable fencing/adoption authority.

#### 2.3 Stable repository identity and current locator binding

```text
repositories
  repository_id  -- opaque stable primary identity
  row_version
  admitted metadata

repository_bindings
  repository_id
  current host-local locator
  binding_revision / row_version
  External Control Plane declaration/version reference as applicable
```

`repository_id` is allocated as an opaque stable identity at admission. It is never derived from path, remote URL, inode, branch name, CWD, or provider identity.

Relocation changes the current locator binding through an exact expected-state/CAS update; it does not change `repository_id`. The External Control Plane remains responsible for the correctness of the logical repository binding. A current locator MUST NOT be simultaneously authoritative for multiple repository identities in one coordination domain.

Git/provider facts observed at the locator remain externally authoritative and must still be revalidated.

#### 2.4 Managed domain state

Current authoritative domain tables represent the existing architecture entities, including as applicable:

```text
repositories / repository bindings
ContributionUnits
ConvergenceUnits
PromotionGroups
PromotionUnits
managed obligations
resource claims
submission/provider logical state
policy observations/fingerprints
verification-evidence references
recovery-resource references
```

Every mutable authoritative row that participates in adoption has an exact expected-state guard such as `row_version`, exact state fingerprint, exact OID, or stronger equivalent. A zero-row expected-state update is a stale/lost CAS and MUST NOT be interpreted as success.

Unknown states fail closed.

#### 2.5 Canonical v1 logical table set and key constraints

The v1 implementation MUST expose the following logical tables (exact physical column encoding may use normalized columns and/or canonical JSON payloads where the domain schema already defines the content):

```text
schema_meta(
  singleton PK,
  schema_version,
  migration_id
)

coordination_domain(
  singleton PK,
  requested_generation,
  processed_generation,
  run_generation,
  run_state,
  run_token UNIQUE NULLABLE,
  row_version
)

repositories(
  repository_id PK,
  row_version,
  admitted metadata
)

repository_bindings(
  repository_id PK FK repositories,
  locator UNIQUE,
  binding_revision,
  external_declaration_fingerprint/version,
  row_version
)

contribution_units(
  contribution_unit_id PK,
  repository_id FK,
  convergence_unit_id FK,
  lifecycle,
  latest_authoritative_managed_checkpoint_oid NULLABLE,
  row_version,
  ...existing exact managed fields
)

convergence_units(
  convergence_unit_id PK,
  repository_id FK,
  membership_state,
  convergence_ref,
  row_version,
  ...existing exact managed fields
)

promotion_groups(
  promotion_group_id PK,
  immutable canonical member-set payload/fingerprint,
  current_resolution_promotion_unit_id NULLABLE,
  row_version
)

promotion_group_members(
  promotion_group_id FK,
  repository_id FK,
  convergence_unit_id FK,
  PRIMARY KEY(promotion_group_id, repository_id, convergence_unit_id)
)

promotion_units(
  promotion_unit_id PK,
  row_version,
  ...existing explicit source/topology/lifecycle fields
)

managed_obligations(
  obligation_id PK,
  obligation_kind,
  logical_scope_key,
  terminality/current classification,
  exact_state_fingerprint,
  row_version,
  ...kind-specific payload
)

resource_claims(
  resource_key PK,
  claim_kind,
  owning run_generation/run_token,
  owning operation_id/attempt_id as applicable,
  expected_resource_fingerprint,
  row_version
)

operations(
  operation_id PK,
  operation_kind/version,
  logical_scope_key,
  intent_fingerprint UNIQUE WITHIN logical identity,
  immutable intent payload,
  stable idempotency identity,
  creation metadata
)

operation_attempts(
  attempt_id PK,
  operation_id FK,
  run_generation,
  run_token,
  exact effect/request fingerprint,
  provider idempotency token NULLABLE,
  immutable start metadata
)

operation_observations(
  observation_id PK,
  operation_id FK,
  attempt_id FK NULLABLE,
  authority/source,
  exact observed-state fingerprint/payload,
  observing run_generation/run_token,
  immutable observation metadata
)

operation_adoptions(
  adoption_id PK,
  operation_id UNIQUE FK,
  observation_id FK,
  adopting run_generation/run_token,
  exact managed precondition fingerprint/version,
  exact adopted-result fingerprint,
  immutable commit metadata
)

operation_closures(
  closure_id PK,
  operation_id UNIQUE FK,
  observation_id FK,
  terminal non-adopting disposition,
  closing run_generation/run_token,
  immutable commit metadata
)

recovery_resources(
  recovery_resource_id PK,
  operation_id FK,
  attempt_id FK,
  resource_kind,
  non-reused locator/ref namespace UNIQUE,
  exact OID/hash/identity,
  lifecycle = REQUIRED | GC_ELIGIBLE,
  row_version
)
```

Additional domain tables such as submission/provider records, policy observations, and verification-evidence references MAY remain separate typed tables, but they obey the same exact-state/CAS and fail-closed rules. Domain-specific payload fields whose semantics remain open under the promotion backlog are not accidentally fixed by this storage ADR; ADR-042 fixes their storage/identity/CAS/journaling envelope, not those separate policies. Backlog 30.14 was subsequently closed by ADR-043, 30.15 by ADR-044, PromotionUnit exact-state definition/identity 30.16 by ADR-045, PromotionGroup/default-mapping semantics 30.17 by ADR-046, and repository-local PromotionGroup projection 30.18 by ADR-047. Repository-local multi-source candidate/head materialization was subsequently closed under 30.39 by ADR-048.

Required relational constraints include:

```text
ContributionUnit.repository_id and .convergence_unit_id are singular and immutable for that identity
ConvergenceUnit.repository_id is singular
PromotionGroup member set is immutable, non-empty, unique, and canonical
PromotionGroup current resolution is updated only by expected-state/CAS against current member READY_INTERNAL states
current repository locator is unique within the coordination domain
operation intent is immutable for one operation_id
attempt_id belongs to exactly one operation_id
Observation is append-only and bound to exactly one Operation
an Operation has at most one successful Adoption
an Operation has at most one terminal non-adopting Closure
Adoption and Closure are mutually exclusive terminal outcomes
recovery-resource physical locator/ref namespace is never reassigned to another attempt
```

Historical journal rows are INSERT-only after creation. Current managed/domain/recovery-resource rows may change only through guarded transactions specified by this architecture.

### 3. One physical top-level run is owned by an OS process-lifetime lock

V1 does **not** use a heartbeat/TTL lease to decide whether the single-host top-level run is alive.

The coordination domain has a dedicated OS-backed exclusive advisory lock held through an open process-owned handle for the lifetime of the active top-level convergence run (`flock`/`fcntl`-class semantics or a platform-equivalent primitive).

The existence or contents of a lock file are not authority. Only successful acquisition of the OS lock is physical ownership.

```text
process owns OS lock
→ it may attempt to establish/continue current run authority

process exits/crashes/closes ownership handle
→ OS releases physical ownership automatically
```

A process that is alive but hung retains the OS lock. V1 performs no automatic lease takeover of such a process.

### 4. Durable run fencing uses monotonic `run_generation` + unique `run_token`

After acquiring the OS lock, the process transactionally establishes the next active run incarnation:

```text
BEGIN
  verify CoordinationStore invariants
  run_generation := run_generation + 1
  run_state := ACTIVE
  run_token := fresh unique token
COMMIT
```

Every authoritative managed-state adoption, resource-claim adoption, operation observation accepted into authority, and operation finalization that is performed on behalf of the run MUST prove the current exact `run_generation + run_token` (or a stronger equivalent fence).

A stale generation may leave physical residue and late worker results may physically arrive, but they cannot create authoritative progression after the durable fence has changed.

Worker results are data. A stale worker does not write authoritative adoption directly; the current fenced run revalidates any usable result against current state before adoption.

### 5. Demand admission and run release use an `ACTIVE → IDLE` handshake to prevent lost wakeups

An authorized trigger first transactionally advances `requested_generation`, independently of run ownership.

It then attempts the OS lock.

```text
OS lock acquired
→ establish a new ACTIVE run generation and service demand

OS lock BUSY + coordination_domain.run_state = ACTIVE
→ an authoritative run is still responsible for re-reading demand
→ caller may return

OS lock BUSY + coordination_domain.run_state = IDLE
→ physical owner is in the short release window or another caller is establishing ownership
→ caller MUST retry/complete ownership acquisition; it MUST NOT return merely because the OS lock was momentarily busy
```

At a current fixed point, the active run completes demand accounting and release in one short SQLite transaction:

```text
BEGIN
  verify current run_generation + run_token + ACTIVE
  advance processed_generation through the exact target_generation covered

  if requested_generation > processed_generation:
      remain ACTIVE
  else:
      run_state := IDLE
      run_token := NULL
COMMIT
```

If the transaction leaves the run `ACTIVE`, the same run performs another global sweep.

If it commits `IDLE`, that commit **immediately fences the old run from all further authoritative actions**, even though it may still hold the OS handle for a few instructions. It then performs only non-authoritative handle release/process exit.

A trigger arriving after the `IDLE` commit but before physical OS-lock release sees `BUSY + IDLE` and must retry until it either acquires the lock or observes a newly `ACTIVE` successor. Therefore accepted demand cannot be stranded in the release window.

### 6. External-effect recovery uses an append-only `Operation → Attempt → Observation → Adoption` journal

The journal records effects whose crash outcome can affect authoritative adoption/recovery. It is not a trace of every reconcile decision.

#### 6.1 `Operation`

An `Operation` is the immutable logical intent of one recoverable effect.

At minimum it records:

```text
operation_id
operation kind/version
stable logical resource/scope identity
exact intent payload/fingerprint
exact managed/Git/provider preconditions used to derive the intent
stable idempotency identity when applicable
creation metadata
```

`operation_id` survives retries/recovery. The same `operation_id` MUST NOT be reused for a changed intent fingerprint.

When an external/provider API supports a client idempotency key/token, the operation's stable identity SHOULD be mapped to that facility under provider policy.

#### 6.2 `Attempt`

Each physical execution is a separate immutable attempt:

```text
attempt_id
operation_id
run_generation
run_token
exact request/effect fingerprint
provider/client idempotency token when used
started metadata
```

A new fenced run may create a new Attempt for an unresolved Operation. It does not invent a new logical Operation merely because the previous process died.

#### 6.3 `Observation`

After an external effect attempt or during recovery, the current fenced run performs exact observation of the relevant Git/remote/provider/current physical state and appends an immutable Observation:

```text
observation_id
operation_id
attempt_id when causally applicable
observed authority/source
exact observed OIDs/state/fingerprint
observed metadata/time
current run fence
```

Durable metadata saying that an effect was attempted never substitutes for this observation.

A current-run observation may be committed even if later managed-state adoption loses its CAS; the observation remains historical evidence of what was actually seen at that time and the engine re-reconciles current state.

A stale fenced generation cannot append new authoritative observations.

#### 6.4 `Adoption`

An Adoption is appended only in the **same SQLite transaction** that successfully performs the corresponding authoritative managed-state CAS.

```text
adoption_id
operation_id
observation_id
run_generation + run_token
exact managed precondition/version/fingerprint
exact adopted transition/result fingerprint
committed metadata
```

A failed CAS creates no Adoption and never counts as progression.

An Operation that becomes terminal without managed adoption (for example because current exact state proves the intent superseded or no longer required) receives an immutable terminal closure/disposition bound to the decisive Observation. This is the non-adopting terminal branch; it does not turn the journal into a mutable workflow FSM.

The success path remains:

```text
Operation
→ one or more Attempts
→ exact Observation
→ fenced CAS Adoption
```

### 7. Journal scope is correctness effects, not filesystem implementation detail

An effect enters the recoverable Operation journal when at least one is true:

```text
it mutates authoritative Git/remote/provider state;
its crash outcome can change what Ruu is allowed to adopt;
it creates/destroys the only durable copy needed for recovery;
it is not mechanically repeatable/reconstructible from current authoritative state.
```

Typical journaled effects include exact Git ref/checkpoint transitions, remote publication, provider mutation, and correctness-critical recovery-ref creation/update.

The following are not Operations merely because they touch disk:

```text
reconstructible isolated workspace creation
checkout/build/test scratch
cache writes
ordinary logs
best-effort cleanup of already-disposable state
```

Immutable evidence/manifests may be written as content-addressed durable artifacts and referenced by hash from the CoordinationStore without becoming separate Operations. An unreferenced blob is GC-able orphan data; a referenced missing/corrupt blob fails closed for the evidence that depends on it.

### 8. No SQLite transaction spans an external effect

Transactions are short and contain only CoordinationStore work.

Forbidden:

```text
BEGIN
→ Git command / network provider call / long filesystem operation / external-effect wait
→ COMMIT
```

Required external-effect shape:

```text
TX-A:
  create/resolve immutable Operation
  append fenced Attempt
COMMIT

(no SQLite transaction held)
perform bounded external effect
exactly observe current external state

TX-B:
  verify current run fence
  append Observation
  attempt exact managed-state CAS
  if CAS succeeds: append Adoption atomically with that managed transition
  if CAS misses: commit Observation only and re-reconcile
COMMIT
```

An external effect that completed before a crash but lacks Observation/Adoption is recovered by exact re-observation, not blind replay.

### 9. Long operations are bounded; waits do not hold the convergence run indefinitely

The OS lock deliberately favors simple correctness over automatic hung-process takeover. Therefore all normal potentially blocking work MUST have explicit bounded behavior:

```text
test/build/verification subprocesses → timeout/cancellation policy
Git subprocesses                    → bounded execution/cancellation
provider/network calls             → deadline/timeout
provider CI/review/queue waits     → record WAITING and reach fixed point; do not sleep holding the run
SQLite transactions                → short; no external awaits/effects
```

A watchdog MAY emit diagnostics such as `CONVERGENCE_RUN_STALLED`, but it does not itself grant takeover authority.

A genuinely hung process may block liveness until it is externally terminated or supervised. This is an accepted v1 availability tradeoff. Once the process actually dies, the OS releases physical ownership and the next run fences the old generation before recovery.

A long pause never makes old observations fresh: before mutation/adoption, exact expected-old OIDs, row-version CAS, current policy/fingerprint, and evidence validity are revalidated as required by existing invariants.

### 10. Recovery refs/workspaces use non-reused attempt/incarnation namespaces

Correctness-critical temporary Git refs/workspaces are operation-owned and physically non-aliasing across stale attempts/generations.

A preferred form is semantically equivalent to:

```text
refs/Ruu/operations/<operation_id>/attempts/<attempt_id>/...
workspaces/<run_generation>/<operation_id>/<attempt_id>/...
```

Exact naming syntax is implementation detail, but a pathname/ref that can still be targeted by cleanup from an old attempt MUST NOT be recycled for a newer attempt.

A temporary recovery ref may act as the durable reachability root for a newly produced OID before managed adoption. Its lifecycle is:

```text
REQUIRED
→ prove another durable reachability root exists
  AND no unresolved recovery path still depends on this resource
→ GC_ELIGIBLE
→ best-effort physical cleanup
```

The correctness transition is `REQUIRED → GC_ELIGIBLE`, stored/guarded in managed coordination state. Physical deletion after `GC_ELIGIBLE` is idempotent best-effort cleanup and is not itself an Operation.

Cleanup failure leaves harmless garbage and MUST NOT invalidate convergence correctness.

### 11. Retention/GC cannot be a correctness prerequisite

The following MUST NOT be garbage-collected while still required:

```text
nonterminal managed obligations
unresolved Operations/Attempts needed for recovery
current managed-state bindings/checkpoints
REQUIRED recovery resources
evidence/artifacts still required by their independent validity contract
schema/migration authority
```

V1 may retain append-only terminal journal metadata indefinitely. Automatic deletion of terminal journal history is not required for correctness. Any future history-retention/compaction policy must prove that no current state, audit reference required by policy, recovery path, or unresolved operation depends on the removed records.

Scratch/recovery-resource cleanup is independent and may proceed after explicit `GC_ELIGIBLE` proof.

Verification-evidence retention details remain governed by the separate verification-evidence backlog; this ADR does not silently close those policy questions.

## Rationale

This design combines four properties appropriate to the actual problem:

1. **current-state reconciliation** rather than persisted workflow-step replay;
2. **process-lifetime single-host ownership** rather than heartbeat-based distributed leader election that v1 does not need;
3. **monotonic fencing** so late workers/processes cannot adopt after takeover/release;
4. **append-only effect history + exact observation** across transaction boundaries that SQLite cannot share with Git/provider state.

The OS lock solves local physical ownership with the kernel's process lifetime semantics. The SQLite fence solves authority. Neither is asked to do the other's job.

The journal separates:

```text
logical intent
≠ physical attempt
≠ observed fact
≠ authoritative adoption
```

which allows exact recovery without turning the current managed state into full event sourcing.

Attempt/incarnation-specific physical namespaces remove an entire class of stale-cleanup races instead of trying to coordinate destructive cleanup through a more complex journal.

## Consequences

- Backlog **30.13 is closed** at the architecture level.
- SQLite is the concrete v1 CoordinationStore backend, but future backend replacement requires preserving these semantics rather than the exact API.
- No external workflow engine is required to orchestrate `ruu`.
- No automatic lease takeover exists for a live-but-hung top-level process in v1.
- Normal long operations require timeout/cancellation or wait-state localization.
- `Operation → Attempt → Observation → Adoption` is the normative recoverable-effect success path.
- Current managed state remains transactionally mutable; the system is not full event sourced.
- Physical cleanup is kept off the correctness path wherever possible.
- Repository identity is stable across host-local relocation because identity is opaque and locator binding is separately mutable.

## Amendments

This ADR closes the implementation questions deliberately left under ADR-041 §7–8 and backlog 30.13. It amends ADR-005, ADR-013, ADR-022, ADR-028, ADR-031, ADR-036, ADR-038, ADR-041, the main requirements, and the External Control Plane contract wherever they leave exact run ownership/takeover, recoverable-effect journaling, repository relocation binding, physical recovery-resource reuse, or CoordinationStore transaction layout open.


## Amendment by ADR-046

The CoordinationStore now includes durable immutable `PromotionGroup` definitions and their canonical member rows. The group declaration is trigger-independent authority state. `current_resolution_promotion_unit_id`, when stored, is derived/cacheable current state and may move only through expected-state/CAS after all declared members are revalidated as current exact `READY_INTERNAL`; historical PromotionUnit identities remain immutable. This amendment closes the 30.17 domain semantics that ADR-042 intentionally left open without changing the reconciler/run/journal envelope.

## Amendment by ADR-052

DIRECT target advancement uses the existing `Operation → Attempt → Observation → Adoption` model with durable logical `(target_ref, expected_old_oid, candidate_oid)` intent and an attempt-scoped non-business recovery anchor that keeps the exact candidate reachable. Recovery observes authoritative target history: `target == candidate` or `candidate` ancestor-of target proves the effect is realized; target still at expected-old proves it is not yet realized; other history is stale/drift. The anchor becomes cleanup-eligible only after durable adoption/recovery sufficiency.

## Amendment by ADR-054

ConvergenceUnit lifecycle terminality is now separated from recovery-resource lifecycle. `ConvergenceUnit PROMOTED` requires terminal semantic settlement; `RETIRED` additionally requires all correctness-critical terminal effects/recovery dependencies to be durably adopted/clear. Only then may historical internal refs become `GC_ELIGIBLE`, and built-in v1 retention remains `KEEP`; physical deletion is never implied by retirement itself.

## Amendment by ADR-055

The CoordinationStore current-state model now includes durable exact-generation `CrossRepositorySettlementDemand` state and logical-submission PublicationEpisode bindings/history. Provider PR/ref creation/revision effects still use ordinary `Operation → Attempt → Observation → Adoption`; no external effect is enclosed in a SQLite transaction, and semantic settlement declarations never manufacture provider/Git success.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.

## Amendment by ADR-065 — realization proof is a separate recoverable Observation→Adoption boundary

Provider target integration completion, canonical provider `C → R` observation, fresh authoritative target observation, `PromotionRealizationProof`, and terminal PromotionUnit adoption are separate durable/recoverable facts. A crash after external finalization must rediscover/observe exact result state rather than blind-retry or infer promotion from an API success. Once the exact proof is durably adopted, retries are idempotent.

## Amendment by ADR-066 — historical effect commitment versus fresh mutation authority

For policy-sensitive effects, Operation/Attempt history must retain the exact authorization/policy fingerprint and request/effect identity needed to establish the route-specific commitment boundary.

A previous policy snapshot may be used during recovery only to explain/adopt an effect already committed while that authorization applied. It never authorizes an action that may newly cause or re-cause the effect. Any such causal retry requires freshly current policy plus ordinary exact guards.

Provider commitment is durable provider acceptance/ownership of the exact finalization operation for exact submitted revision `H` and target `T`. DIRECT commitment is the target ref mutation itself; there is no separate accepted-but-not-realized phase. If policy drift occurred and commitment timing/provenance cannot be established, recovery fails closed rather than treating old Attempt metadata as a perpetual capability.

Observation/adoption remains distinct from effect causation. Polling an already accepted provider operation or adopting an already realized route-conformant result is recovery, not a new policy authorization.


## Amendment by ADR-076 — native causal witnesses are evidence, not synthetic Operations

ADR-042's `Operation → Attempt → Observation → Adoption` journal remains the recoverable-effect journal for effects owned/caused by `ruu`; it is not a universal Git event log. ADR-075 native-ref witnesses/preparations live on a separate causal-evidence plane and MUST NOT manufacture a managed Operation when native Git acts outside the managed executor. A witness MAY carry trusted optional `originating_attempt_id` correlation when a managed Attempt launched the physical Git operation, but that provenance is never authorization and absence of it is normal.

Exactly-once remains an authoritative logical-state property: one Operation has at most one Adoption (or mutually exclusive terminal Closure), while one current managed authoring binding generation has at most one committed disposition out of that generation. Duplicate/replayed witness delivery, repeated exact-state observations, and reordered/coalesced wakeups do not create additional logical effects. Exact-state scans may observe an existing Operation or resolve an already-durable native preparation, but they never invent missing causal preparation from final topology alone.

## Amendment by ADR-081 — exact authoring-dependency adoption and retention

An AuthoringDependency adoption is an ADR-042 recoverable Operation because it creates the durable reachability root required for an exact consumed commit. Supported-harness pre-edit provisioning submits an authorized internal provisioning demand to this same single-host fenced executor and waits for adoption before consumer write; no second adoption-authority domain or work-bearing checkpoint is created. TX-A durably linearizes immutable source/consumer/OID selection, expected source row/binding generation, an Attempt, and a `REQUIRED` `AUTHORING_DEPENDENCY_OID_ANCHOR`; Git then creates/observes the non-reused anchor outside SQLite; TX-B revalidates source generation/continuity/disposition and atomically adopts the dependency with its exact Observation and managed-state CAS. A qualifying source handoff between TX-A and TX-B may be incorporated directly into resolved adoption rather than stranding a raw relation. A crash may leave a recoverable attempt or orphan anchor, but never an authoritative unanchored dependency.

The anchor remains `REQUIRED` while any raw, resolved, restack, realization, reconciliation, audit, or recovery obligation may need the consumed OID. Source ref movement, dependency compression, or target satisfaction alone never makes it disposable. It may become `GC_ELIGIBLE` only after every dependent obligation is terminal and another durable retained root is sufficient; built-in v1 retention remains `KEEP`.
