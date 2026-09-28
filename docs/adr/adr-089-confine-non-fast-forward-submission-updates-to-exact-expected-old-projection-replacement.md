---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Confine non-fast-forward submission updates to exact expected-old projection replacement"
id: "ADR-089"
status: "accepted"
date: "2026-09-28"
decision_body_sha256: "d77d610dd92a18a717f1a93f4d45527b655990644e7d42282a03110e3f11ab43"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-026"
    - "ADR-028"
    - "ADR-043"
    - "ADR-044"
    - "ADR-049"
    - "ADR-050"
    - "ADR-051"
    - "ADR-055"
    - "ADR-062"
    - "ADR-066"
  supersedes: []
  confirms:
    - "ADR-042"
    - "ADR-060"
    - "ADR-087"
    - "ADR-088"
governs:
  - "Submission-head semantic revision and exact Git ref-effect layering"
  - "Submission-ref fast-forward versus non-fast-forward effect classification"
  - "Exact expected-old non-fast-forward provider-projection replacement"
  - "Non-fast-forward ref-role and policy-authority confinement"
  - "Previous submission-head reachability and recovery-resource lifecycle"
  - "Logical submission-revision monotonicity versus provider-head Git ancestry"
---


# ADR-089 — Confine non-fast-forward submission updates to exact expected-old projection replacement

- **Status:** Accepted
- **Date:** 2026-09-28
- **Amends:** ADR-026, ADR-028, ADR-043, ADR-044, ADR-049, ADR-050, ADR-051, ADR-055, ADR-062, and ADR-066
- **Confirms:** ADR-042, ADR-060, ADR-087, and ADR-088

## Context

Ruu already separates immutable internal/owned Git state from provider-facing submission projections. ADR-049 gives a logical Submission stable identity and monotonic exact revisions, ADR-050 derives stacked projection heads from immutable owned state, ADR-055 scopes provider submission identity and refs to PublicationEpisodes, and ADR-066 proves provider-route realization through exact `C → H → R → O` chains.

The current representation nevertheless gives durable submission state standing mutation authority:

```text
submission_class:
  IMMUTABLE
  REWRITEABLE

BOUND_IMMUTABLE(rev,H)
BOUND_REWRITEABLE(rev,H)
```

That representation conflates four layers:

```text
durable logical Submission/PublicationEpisode state
semantic submission-head revision
exact Git ref effect
backend transport mechanism
```

A new exact provider projection may be a descendant of the current head or may be unrelated by ancestry. The latter is ordinary for repeated ADR-050 reprojection from immutable `(old_base_oid, owned_candidate_oid)` onto a changed predecessor. It does not grant the submission ref standing rewrite authority and does not make generic force push a core semantic primitive.

The required correction preserves the semantic vocabulary while deriving and authorizing one exact physical effect for one current transition.

## Discovery classification

```text
decision-required, resolved; submission-projection ref-effect, authorization, and recovery boundary
```

This decision fixes the submission-projection effect contract. It does not choose a public `.ruu/policy.toml` field, serialized enum, provider API, Git CLI spelling, UserBehavior dimension, RuntimeConfig field, implementation language, or storage architecture. Provider governance-observation representation remains separate work.

## Decision

### 1. Separate semantic, exact-effect, and backend layers

The core semantic transition remains:

```text
REVISE_SUBMISSION_HEAD
```

ADR-050 may separately require:

```text
EXECUTE_RESTACK_CONTRACT
```

to derive the next exact projected head. The semantic layer does not add `FORCE_PUSH`, `FORCE_UPDATE`, or an effect-contract name as a new top-level ADR-051 operation.

After the semantic next head is known, Ruu derives one exact Git ref effect. A backend then selects a conforming Git/provider mechanism for that effect:

```text
SEMANTIC LAYER
REVISE_SUBMISSION_HEAD
+ EXECUTE_RESTACK_CONTRACT when required

EXACT GIT EFFECT LAYER
NOOP
| FF_SUBMISSION_REF_ADVANCE
| NON_FF_SUBMISSION_PROJECTION_REPLACEMENT

BACKEND LAYER
exact Git/provider mechanism satisfying the selected effect contract
```

No Submission, PublicationEpisode, SubmissionRef, or bound revision possesses standing non-fast-forward authority.

### 2. Classify the required ref effect only from exact Git state

For authoritative current bound head `H1` and required next exact head `H2`, classification is ordered:

```text
H1 == H2
→ NOOP

git-is-ancestor(H1,H2)
→ FF_SUBMISSION_REF_ADVANCE

otherwise
→ NON_FF_SUBMISSION_PROJECTION_REPLACEMENT
```

Equality is handled before ancestry. `NOOP` retains the existing bound revision and does not create a new physical submission-head revision merely because the same exact head was requested again.

The classification is solely an exact Git fact. Policy, UserBehavior, BuiltInBehavior, provider terminology, caller intent, local configuration, and branch naming cannot relabel the relation.

### 3. Use exact expected-old effect contracts

The fast-forward effect contract is:

```text
AdvanceSubmissionRefExpectedOldFF(
    submission_ref,
    expected_old = H1,
    new = H2
)
```

Success requires all of:

```text
current authoritative ref == H1
H1 ancestor-or-equal H2
exact expected-old comparison succeeds
effect updates only the intended submission_ref
authoritative post-effect observation == H2
```

The non-fast-forward effect contract is:

```text
ReplaceSubmissionRefExpectedOld(
    submission_ref,
    expected_old = H1,
    new = H2
)
```

Success requires all of:

```text
current authoritative ref == H1
exact ref-role eligibility
current semantic revision requires H2
fresh current governance authorization
contextual technical support for REVISE_SUBMISSION_HEAD
  in a context requiring NON_FF_SUBMISSION_PROJECTION_REPLACEMENT
claim/fence/recovery prerequisites
exact expected-old comparison succeeds
effect updates only the intended submission_ref
authoritative post-effect observation == H2
```

These names identify effect contracts below `REVISE_SUBMISSION_HEAD`; they are not new semantic domain operations.

### 4. Confine non-fast-forward eligibility to one exact ref role

`NON_FF_SUBMISSION_PROJECTION_REPLACEMENT` is structurally eligible only for:

```text
the submission_ref
of the current nonterminal PublicationEpisode
whose exact REVISE_SUBMISSION_HEAD transition is being realized
```

Being that ref is necessary but not sufficient authorization. The effect MUST be impossible for:

```text
ContributionUnit managed authoring ref
ConvergenceUnit ref
ConvergenceBase ref
PromotionTarget ref
authoritative target ref
operation recovery ref
attempt recovery ref
SUBMISSION_REVISION_OID_ANCHOR
AUTHORING_DEPENDENCY_OID_ANCHOR
other recovery/retention refs
another PublicationEpisode's ref
terminal PublicationEpisode ref
unmanaged/unbound ref
```

Ruu's Authoritative Ref Monotonicity governance remains unchanged. It protects the repository authoritative ref and does not require physical ancestry monotonicity for a non-authoritative provider projection ref.

### 5. Authorize each required non-fast-forward effect through current policy

ADR-087/088 remain the only promotion-policy model. The current `EffectivePromotionPolicy` must determine whether the exact required `NON_FF_SUBMISSION_PROJECTION_REPLACEMENT` is authorized for the current PublicationEpisode, submission ref, revision, destination, and governance context.

The dimension is operation/effect authorization. It is not:

```text
submission_class
REWRITEABLE
FF_ONLY
UserBehavior
BuiltInBehavior
RuntimeConfig
caller intent
```

No public policy key or serialized enum is selected here.

For a dedicated Ruu current PublicationEpisode submission ref, authoritative composition may authorize the exact expected-old non-fast-forward effect when:

```text
the relevant authoritative governance is positively known
AND no applicable repository/provider/organization constraint forbids the effect
```

This is zero-onboarding closure only from positively known authority:

```text
no observed prohibition
!= proof that no prohibition exists

required governance observability MISSING / UNKNOWN
→ no replacement
```

Authorization is freshly revalidated at the effect boundary under ADR-044. A previous successful replacement or stale policy snapshot is never standing future mutation authority.

### 6. Keep capability contextual and separate from authorization

Capability remains queried for semantic operation:

```text
REVISE_SUBMISSION_HEAD
```

with exact context sufficient to distinguish the required effect, including conceptually:

```text
current exact head H1
required next exact head H2
required ref effect:
  EXPECTED_OLD_FF
  or
  EXPECTED_OLD_NON_FF_REPLACEMENT
current PublicationEpisode
current provider submission identity/state
repository/remote/provider context
```

Support for ordinary fast-forward revision does not imply support for non-fast-forward replacement. A generic provider fact such as `supports_force_push = true` is never sufficient capability evidence.

The execution boundary remains:

```text
REVISE_SUBMISSION_HEAD REQUIRED
∩ exact effect context SUPPORTED
∩ exact effect AUTHORIZED by current EffectivePromotionPolicy
∩ exact state / claim / fence / recovery prerequisites
→ executable effect
```

`SUPPORTED != AUTHORIZED`. Provider authorization-observation representation remains outside this decision.

### 7. Keep force-like mechanisms below the backend boundary

A backend MAY use a mechanism semantically equivalent to exact:

```text
force-with-lease(expected_old=H1,new=H2)
```

to realize `ReplaceSubmissionRefExpectedOld`. The architecture does not bless one Git CLI or provider API spelling.

A conforming backend guarantees:

```text
exact intended submission_ref
exact old OID H1
no mutation on expected-old mismatch
no overwrite of concurrent HX
authoritative post-effect observation == H2
```

Blind `git push --force` or any equivalent unconditional replacement is never conforming. "Force push" is not semantic/core vocabulary.

### 8. Preserve the current open PublicationEpisode and forbid topology fallback

Within one current nonterminal PublicationEpisode:

```text
submission_id stable
publication_episode_id stable
provider_submission_identity stable
submission_revision monotonic
```

A newly required exact head revises the same episode/provider submission regardless of whether the exact ref effect is fast-forward or authorized non-fast-forward replacement.

ADR-055 remains the only episode-continuation rule:

```text
current episode terminal
+ logical submission still has later exact publication obligation
+ PromotionGroup nonterminal
→ new PublicationEpisode
```

Ruu MUST NOT create a new episode merely to avoid non-fast-forward replacement.

When the required replacement is forbidden, missing/unknown, unsupported, or support is unknown, the affected publication obligation blocks locally. Ruu MUST NOT automatically:

```text
create another provider submission
create another PublicationEpisode
flatten a stack
switch realization route
retarget
invent a synthetic merge only to obtain FF ancestry
rewrite internal state
blind-force the ref
```

Unrelated global obligations continue.

### 9. Retain the old exact head through recovery

This decision uses ADR-042's existing generic recovery-resource model with one domain-specific kind:

```text
resource_kind = SUBMISSION_REVISION_OID_ANCHOR
```

It creates no new storage or recovery architecture.

Before a non-fast-forward replacement may remove the current submission ref as a reachability root for `H1`, require either:

```text
a current REQUIRED SUBMISSION_REVISION_OID_ANCHOR for exact H1
```

or:

```text
another already-existing REQUIRED durable reachability root
proven sufficient for every correctness-critical H1 obligation
```

An OID stored only in SQLite/metadata is not a Git reachability root. If required reachability cannot be established or verified, Ruu MUST NOT perform the replacement.

The ordinary recoverable transition is:

```text
durable revision Operation/Attempt exists
→ establish REQUIRED H1 reachability
→ revalidate exact current role/policy/capability/ref state
→ attempt H1 → H2 exact replacement
→ observe exact authoritative result
→ adopt revision exactly once when proven
→ retain H1 reachability while any H1-bound correctness obligation remains
→ prove all such obligations terminal/sufficiently retained
→ recovery resource GC_ELIGIBLE
→ physical cleanup best-effort
```

`H1` remains correctness-required while any relevant obligation may still need object availability, including:

```text
ambiguous ref-effect recovery
provider finalization already accepted/committed for H1
C→H1→R→O route-conformance recovery
head-bound review/check/queue state whose contract requires H1 availability
unresolved Operation/Attempt/Observation/Adoption path
other explicit audit/recovery contracts requiring the Git object
```

The anchor is not future mutation authority and cannot reopen terminal provider state.

### 10. Keep provider facts bound to their exact head

For:

```text
revision r @ H1
→ revision r+1 @ H2
```

facts bound to `H1` remain `H1`-bound. Ruu does not automatically transfer:

```text
checks(H1)
reviews(H1)
queue-state(H1)
provider-head observation(H1)
review/publication facts whose exact contract is head-bound
```

`H2` receives whatever fresh, rebound, re-observed, invalidated, or re-established transition-local facts existing contracts require. ADR-060 remains controlling; no generic `DevelopmentValidationEvidence`, validation certificate, or post-restack quality gate is introduced.

### 11. Preserve ADR-050 restack provenance and ADR-066 route proof

Repeated restack semantics remain:

```text
Restack(B0,C0,B1) → H1
Restack(B0,C0,B2) → H2
```

where `(B0,C0)` is the applicable immutable owned child anchor. `H2` is never computed semantically from `H1`, internal candidate/source refs are never mutated, and `H1 !ancestor H2` is not semantic drift when `H2` is the exact newly derived authorized projection.

Each exact submitted head has its own immutable projection proof:

```text
revision r:
C → H1

revision r+1:
C → H2
```

or the applicable newer exact candidate when authored state changed. Provider terminal proof for `H2` remains:

```text
C
→ SubmissionProjectionProof(C,H2)
→ ProviderFinalizationObservation(H2,R)
→ authoritative target observation R→O
```

No semantic `H1 → H2` ancestry proof is created or required.

Logical submission monotonicity is:

```text
stable submission identity
+ stable current PublicationEpisode
+ monotonic submission_revision
+ immutable exact revision/projection history
```

It is not Git ancestry monotonicity of successive provider heads.

### 12. Adopt each actual new revision exactly once

For an actual new exact bound head `H2` successfully realized:

```text
submission_revision := revision + 1
```

exactly once. Duplicate/replayed Attempts, Observations, provider events, and recovery passes do not increment it again.

A durable revision Operation carries exact semantic intent, current episode/ref role, `H1`, `H2`, required effect, policy/capability provenance, and recovery binding. Recovery re-observes current authoritative state before effect causation or adoption.

A state scan with no durable matching revision Operation/Attempt MUST NOT invent an authorized revision transition from final topology alone. Unexpected external head movement remains `DRIFTED / UNKNOWN_INCONSISTENT` unless an existing authorized exact operation/recovery contract proves the corresponding managed revision.

## Rationale

The correction makes each authority answer one question:

```text
core semantic state
→ which exact head is required

Git object relation
→ which exact ref effect is required

EffectivePromotionPolicy
→ whether that effect is authorized now

CapabilityObservation
→ whether that effect contract is technically supported now

backend
→ how to execute the contract without weakening it
```

This preserves safe hands-off stacked progression without turning a ref, prior replacement, provider feature label, or caller request into standing authority. Exact expected-old comparison prevents lost updates; typed old-head reachability preserves recovery and route proof after a non-fast-forward projection change.

## Consequences

- Persistent `submission_class = IMMUTABLE | REWRITEABLE` state is removed.
- `BOUND_IMMUTABLE` and `BOUND_REWRITEABLE` collapse to exact `BOUND(rev,H)` plus a derived per-transition effect.
- `REVISE_SUBMISSION_HEAD` remains the semantic operation.
- Equality/ancestry mechanically derives NOOP, fast-forward advance, or non-fast-forward replacement.
- Every non-fast-forward replacement needs fresh policy authorization, contextual support, exact role, expected-old, fence, and recovery guards.
- Only the current nonterminal episode submission ref is structurally eligible.
- Blind force and topology fallback remain forbidden.
- Old exact heads remain durably reachable while correctness obligations require them.
- Head-bound provider facts remain revision-specific.
- ADR-050 immutable-source reprojection and ADR-066 per-revision `C → H → R → O` proof remain unchanged.
- Logical revision monotonicity no longer implies provider-head ancestry monotonicity.

## Rejected alternatives

### Keep a persistent REWRITEABLE submission class

Rejected. Durable identity state cannot authorize an unknown future non-fast-forward effect.

### Add FORCE_PUSH or FORCE_UPDATE as a semantic operation

Rejected. Force-like transport is only a possible backend realization of the exact expected-old replacement contract.

### Infer permission from absence of an observed prohibition

Rejected. Missing required governance visibility is `MISSING / UNKNOWN`, never authorization.

### Create another episode or flatten topology when replacement blocks

Rejected. That would change ADR-055 lifecycle or ADR-050 derived topology to avoid a localized effect constraint.

### Invent merge ancestry to make the update fast-forward

Rejected. Physical ancestry cannot be manufactured solely to evade the required effect classification.

### Derive the next restack from the prior provider head

Rejected. ADR-050 requires immutable owned-state source provenance.

### Transfer H1-bound facts to H2

Rejected. Transition-local provider facts retain their exact-head binding.

### Store only the H1 OID as recovery metadata

Rejected. Metadata does not keep the Git object reachable.

## Verification obligation

No new qualification package is created by this decision. GitHub Issue #52 owns the dedicated provider-neutral state-space and native-Git qualification. The accepted specification and ADR-089 are the semantic oracle; existing qualification evidence does not prove this decision.

Future qualification MUST cover at least:

```text
exact NOOP / FF_SUBMISSION_REF_ADVANCE /
  NON_FF_SUBMISSION_PROJECTION_REPLACEMENT classification
policy cannot alter exact Git relation classification
FF exact expected-old success and mismatch rejection
non-FF exact expected-old success on the current nonterminal episode ref
rejection for every forbidden ref role
fresh authorization and capability for every replacement
prior successful replacement never becomes standing authority
policy drift and capability drift before effect causation
missing/unknown governance and unsupported/unknown capability
stale expected-old and concurrent replacement races
unexpected external movement → DRIFTED / UNKNOWN_INCONSISTENT
exactly-once submission_revision adoption
NOOP creates no revision
ADR-050 repeated restack from immutable owned anchor
immutable per-revision C→H projection history
H1-bound checks/reviews/queue/provider facts not transferred to H2
REQUIRED SUBMISSION_REVISION_OID_ANCHOR or sufficient existing root
old-head retention through ambiguous recovery and H1-bound obligations
GC_ELIGIBLE only after every H1 requirement permits release
crash before effect, after Attempt, after effect, after Observation,
  and after Adoption
no topology/route/episode/internal-history fallback
native Git exact compare-and-replace smoke distinct from blind force
```

Every invariant requires a deliberate falsifying case. Provider-specific governance/currentness/execution-identity verification and profile/UserBehavior integration remain with their existing independent owners; Issue #52 must not duplicate those oracles and must replace stale `FF_ONLY` terminology with ADR-089's per-transition model.
