# Ruu — State-Space / Global Consistency Audit v10

- **Date:** 2026-09-05
- **Model baseline:** ADR-001..ADR-040
- **Trigger:** ADR-040 closes conflict-resolution and mutation-attribution backlog items by introducing exact `RECONCILIATION_REQUIRED` obligations and boundary-scoped candidate attribution.
- **Result:** **PASS**

## 1. Purpose

This audit revalidates the complete current architecture after fixing two ContributionUnit-layer semantics:

```text
authoring-required conflict
→ authoritative refs unchanged
→ exact-state-bound RECONCILIATION_REQUIRED
→ external Development System authors
→ current-state revalidation + claims/CAS + full verification before adoption

valid ContributionUnit mutation-authority boundary
→ process identity irrelevant to candidate attribution
```

The audit specifically checks that ADR-040 does not:

- make a reconciliation descriptor an adoption token;
- allow a resolver report to bypass current-state revalidation or full verification;
- lose authoring-required conflicts when an isolated merge workspace is discarded;
- turn semantic conflict resolution into a `ruu` coding responsibility;
- make per-process provenance necessary for hooks/generators/tooling;
- automatically include parasite/untracked/generated outputs merely because they were produced inside the boundary;
- weaken exclusive mutation authority, eager integration, `READY_INTERNAL`, or the ADR-036 global sweep.

This remains a factorized finite-state audit rather than enumeration of the unbounded Git DAG/provider state space.

## 2. New finite family: exact reconciliation obligation contract

`reconciliation_required_contract` enumerates:

```text
reconciliation outcome:
  DETERMINISTIC_CLEAN
  SEMANTIC_CONFLICT

reconciliation descriptor:
  NONE
  EXACT
  STALE

authoritative ref:
  UNCHANGED
  ADVANCED

authored result:
  ABSENT
  PRESENT

current-state revalidation:
  YES
  NO

verification evidence:
  VALID
  INVALID

current claim:
  HELD
  NOT_HELD
```

Result: **192 combinations**.

Validated:

```text
SEMANTIC_CONFLICT
→ safe recording requires authoritative ref UNCHANGED
→ exact conflict descriptor required

later authored state
→ adoption depends only on current revalidation + current claim + exact valid evidence
→ historical descriptor may be EXACT, STALE, or absent as an adoption basis
→ therefore reconciliation evidence is diagnostic, not authority
```

## 3. New finite family: candidate-attribution boundary

`candidate_attribution_boundary` varies:

```text
authority:
  VALID
  VIOLATED
  UNKNOWN

producer:
  CODING_AGENT
  HOOK
  GENERATOR
  FORMATTER
  EXTERNAL_TOOL

exact state:
  STABLE
  STALE

verification evidence:
  VALID
  INVALID
```

Result: **60 combinations**.

Validated:

- producer identity never changes candidate ownership under a valid ContributionUnit mutation-authority boundary;
- known/unknown authority violations never authorize attribution/adoption;
- stale or unverified candidate state never authorizes adoption;
- candidate membership rules remain independent of process provenance.

## 4. External Control Plane / Development System boundary

The v10 responsibility-boundary family now includes three distinct roles:

```text
External Control Plane
→ topology/lifecycle/transferability declarations
→ delivery of reconciliation obligations

Development System
→ semantic conflict authoring

Ruu
→ exact Git/provider observation
→ conflict detection + reconciliation record
→ deterministic clean reconciliation
→ current-state validation / claims / verification / adoption
```

Nineteen representative responsibilities are checked against five claimed owners, for **95 combinations**.

## 5. Global-obligation and wait coverage

`RECONCILIATION_REQUIRED` is added explicitly to both:

- global managed-obligation coverage;
- externally waiting/nonterminal obligations rechecked on every invocation.

Counts become:

```text
global_managed_obligation_coverage: 486
external_wait_recheck: 96
```

Thus an authoring wait is localized but can never disappear from the global sweep.

## 6. Revalidated prior families

The executable v10 audit reruns all prior current families, including:

- ContributionUnit identity/cardinality/lifecycle and artifact independence;
- checkpoint-record CAS;
- external ConvergenceUnit grouping;
- eager ContributionUnit integration;
- sealed ConvergenceUnit readiness;
- experimental isolation;
- worktree mutation authority;
- commit/full-verification cross-check;
- state-producing transition verification;
- verification evidence reuse/fixed point/capacity;
- review-request and revision invalidation;
- internal integration evidence.

Total finite combinations evaluated: **12,120**.

## 7. Static architecture consistency checks

The static audit verifies:

1. ADR numbering is contiguous from **001 through 040**.
2. Markdown fences are balanced across all current architecture artifacts.
3. Main §30 marks **30.10** and **30.12** resolved by ADR-040.
4. `OPEN-DESIGN-BACKLOG.md` no longer lists 30.10 or 30.12 as open.
5. Main invariants include:
   - exact reconciliation obligation semantics;
   - boundary-scoped candidate attribution.
6. `EXTERNAL-CONTROL-PLANE-CONTRACT.md` defines reconciliation delivery to the Development System.
7. ADR-009/012/013/033/036/037/038/039 are compatible with ADR-040 amendments.
8. `RECONCILIATION_REQUIRED` remains nonterminal and globally visible.
9. No per-process actor identity is reintroduced into ContributionUnit ownership.
10. Candidate-membership/generated-output policy remains explicitly open separately.

## 8. Result

The executable audit reports **PASS** with **12,120 finite combinations**. After inclusion of this report, the package contains **53 Markdown artifacts** subject to static cross-checking.

## 9. Interpretation

The architecture now has a clean authoring boundary:

```text
mechanically constructible Git result
→ Ruu verifies/adopts

semantic conflict
→ Ruu records exact RECONCILIATION_REQUIRED
→ Development System authors
→ Ruu independently revalidates/verifies/adopts current result
```

And ContributionUnit provenance remains actor-independent:

```text
valid mutation boundary
→ one candidate boundary

process identity
→ non-normative
```

This closes the last two open questions in the ContributionUnit conflict/provenance packet without broadening `ruu` into a development/authoring system.
