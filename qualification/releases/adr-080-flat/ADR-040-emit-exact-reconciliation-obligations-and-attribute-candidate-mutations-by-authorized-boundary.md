# ADR-040: Emit exact reconciliation obligations and attribute candidate mutations by authorized ContributionUnit boundary

- **Status:** Accepted
- **Date:** 2026-09-05
- **Decision order:** 040

## Context

Two remaining ContributionUnit-layer questions were still open:

```text
30.10 conflict resolution policy
30.12 attribution of hook/generator/tool-produced modifications
```

The architecture already makes `ruu` responsible for deterministic Git progression, exact-state revalidation, exact external development-validation binding when policy requires it, fine-grained claims/CAS, and localized blocked states. It also deliberately keeps semantic development/authoring outside `ruu`.

A conflict therefore needs more than a transient `merge conflict` error, but must not turn `ruu` into a coding agent. Likewise, tracking which individual process wrote each byte is neither necessary nor compatible with the actor-independent ContributionUnit model.

## Decision

### 1. Deterministic reconciliation remains inside `ruu`

If Git plus deterministic repository-configured mechanics can construct a clean synchronization/integration candidate without semantic authoring, `ruu` may continue normally:

```text
exact inputs
→ deterministic clean candidate
→ exact-state revalidation
→ exact external development-validation evidence when required by current policy
→ expected-old/CAS adoption
```

A deterministic merge/merge-driver result is still only a candidate; it gains no authority until the ordinary validation/adoption rules pass.

### 2. Semantic conflicts emit `RECONCILIATION_REQUIRED`

If safe progress requires choosing or authoring code rather than mechanically constructing an unambiguous candidate, `ruu` MUST NOT resolve the conflict semantically.

Instead it MUST:

```text
leave authoritative managed refs/state unchanged
record a durable nonterminal RECONCILIATION_REQUIRED obligation
bind that obligation to the exact conflicting state observed
expose enough mechanical conflict evidence for external authoring
continue unrelated global progress
```

The exact reconciliation descriptor is logically bound to the conflict-producing facts, including as applicable:

```text
repository_id
operation/edge kind
relevant ContributionUnit / ConvergenceUnit / PromotionUnit / submission identities
exact input OIDs / exact current destination OID
merge-base OID(s) where applicable
conflicting paths and mechanical conflict kinds where observable
```

This is a logical contract, not a required persistence schema. Storage/API representation remains implementation work.

A low-level owned Git operation may transiently be `BLOCKED_CONFLICT`, but an authoring-required conflict MUST surface as the managed `RECONCILIATION_REQUIRED` obligation rather than disappearing with a temporary merge workspace.

### 3. The External Control Plane routes reconciliation to the Development System

`RECONCILIATION_REQUIRED` is an output from `ruu` to the external development side.

The **Development System** is the external authoring capability that can modify code: for example an agent runtime, coding agent, human, or tooling coordinated through the External Control Plane. It is a role, not a mandated product.

The External Control Plane MUST make active reconciliation obligations available/actionable to the Development System. It does not need to choose a particular resolver policy.

If the original ContributionUnit remains `OPEN`, authoring may continue there when the external mutation-authority contract permits. If it is `CLOSED`, later authoring uses a new ContributionUnit bound to the relevant ConvergenceUnit under the existing lifecycle rules.

### 4. Reconciliation evidence is diagnostic, never adoption authority

A reconciliation obligation is exact-state-bound evidence of **why automatic progress stopped**. It is not a token authorizing a future result.

Any state produced by the Development System re-enters the ordinary pipeline:

```text
observe current authoritative Git/topology/policy state
→ revalidate against the current state, not the historical conflict snapshot
→ establish the required claims/CAS guards
→ require exact external development-validation evidence for the exact candidate/result when policy requires it
→ adopt only if every current precondition passes
```

If the destination/inputs advance while authoring is in progress, the old reconciliation descriptor remains historically true but stale as an adoption basis. A later sweep re-evaluates the current relation. No external `mark resolved` assertion can bypass Git-state proof, exact revalidation, or any policy-required exact external development-validation prerequisite.

`RECONCILIATION_REQUIRED` is considered resolved/superseded when current authoritative state demonstrates that the blocked exact obligation no longer remains and the ordinary convergence path has progressed accordingly.

### 5. Contribution mutation attribution is boundary-scoped, not process-scoped

For convergence purposes, `ruu` does not track actor/process provenance for individual file mutations.

```text
valid ContributionUnit mutation-authority boundary
+ exact candidate state produced inside that boundary
→ mutations belong to that ContributionUnit candidate
```

This includes subordinate tools invoked within the authorized boundary, such as:

```text
formatters
hooks
generators
package managers
migration/code-generation tools
other repository tooling
```

This attribution rule does **not** mean process attribution itself defines candidate bytes. ADR-058/ADR-059 now close 30.27: whole-surface intent is canonicalized through native Git tree construction, with staging non-authoritative and explicit untracked/ignored/structural/submodule/sparse/no-op rules. Verifier parasite/generated-output handling belongs to the Development System under ADR-057.

If a mutation occurs in violation of the required external/exclusive mutation-authority contract, the problem is an integrity/staleness condition, not an attribution ambiguity:

```text
known/observed authority violation or concurrent unexpected mutation
→ candidate/preconditions stale or inconsistent
→ no authoritative adoption
→ re-establish valid authority + exact state and reverify, or enter localized recovery
```

`ruu` MUST NOT guess which actor “owns” such bytes.

## Rationale

This preserves the core boundary:

```text
Ruu
→ mechanical Git reconciliation, conflict detection, exact diagnostics,
  validation and adoption

Development System
→ semantic code authoring when reconciliation requires judgment
```

It also keeps ContributionUnit identity actor-independent and treats the worktree/candidate boundary, not process identity, as the relevant provenance boundary.

## Consequences

- Backlog items **30.10** and **30.12** are closed.
- Authoring-required conflicts become durable globally visible managed obligations rather than transient errors.
- `RECONCILIATION_REQUIRED` is re-evaluated by every later global sweep under ADR-036.
- Authoritative refs never advance merely because a resolver reports success.
- Reconciliation output always returns through current-state revalidation and any policy-required exact external development-validation prerequisite.
- Per-process/per-file actor attribution is not required.
- Unauthorized concurrent mutation remains a fail-closed integrity condition.
- Existing candidate-membership/generated-output policy questions remain open; this ADR only closes ownership/provenance attribution.

## Amendments

This ADR amends ADR-009, ADR-012, ADR-013, ADR-033, ADR-036, ADR-037, and ADR-039 where they describe conflict handling, external authoring routing, candidate mutation boundaries, global obligation coverage, or readiness blocking.


## Amendment by ADR-057

Development verification execution is external. Any exact validation precondition mentioned above is satisfied by current externally produced `DevelopmentValidationEvidence`; `ruu` does not run/schedule tests to produce it.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
