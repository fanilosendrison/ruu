---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Bind full-verification evidence to exact state and reuse it when still valid"
id: "ADR-030"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "88a468263eb45e9e5bcf4709e3f20641f66ee7a404ae95976ba11b4bccbc9e9b"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-030: Bind full-verification evidence to exact state and reuse it when still valid

- **Status:** Accepted historically — generic development-validation evidence semantics superseded by ADR-060; broader exact-state binding retained
- **Date:** 2026-09-04
- **Decision order:** 030

## Current normative reading after ADR-057

The exact-state binding/reuse rule remains normative; the historical internal verifier/fixed-point algorithm does not. **Any text below saying verification “must run again”, classifying verifier outputs, or describing an internal fixed-point loop means that a new exact candidate needs its own valid external development-validation evidence under current policy. The Development System decides how to obtain it.**

`ruu` never mutates an immutable synthesized candidate in response to semantic validation feedback and never runs formatter/codegen/test retry loops.

## Context

Re-running a full suite at every boundary is safe but can be redundant when the exact resulting state and the complete verification contract are unchanged. Conversely, reusing a `PASS` merely because a branch, contribution unit, or PR has previously passed is unsafe when the candidate, policy, or relevant verification context has changed.

Verification itself may also mutate tracked candidate state through snapshots, generated source, golden files, lockfiles, or other generators. A suite that started on state `X` must not silently authorize a different state `X'` without validating the resulting state.

## Decision

Full-verification evidence is exact-state-bound.

A reusable full-verification record MUST identify at least:

```text
exact candidate identity
verification-policy fingerprint
relevant declared verification-context fingerprint
result
```

Before a commit exists, exact candidate identity may be represented by a deterministic candidate-state fingerprint covering the exact tracked/index state and policy-relevant untracked/generated inputs. After commit/materialization, evidence SHOULD bind to the exact resulting Git object identity where possible.

The validity rule is:

```text
exact resulting state has valid full-verification evidence
```

Then:

```text
if exact state + verification policy + relevant declared context are unchanged
→ existing valid evidence may be reused

if exact state changes
or verification policy changes
or relevant declared verification context changes
or evidence is unknown/stale/incomplete
→ verification must run again
```

This is state/evidence-oriented, not invocation-count-oriented. A second boundary does not require a second execution merely because it is a second boundary when it consumes the exact same still-valid verified result.

### Verification-induced mutation and fixed point

While verifying candidate `X`:

```text
verification leaves candidate unchanged
→ PASS may bind to X

verification changes candidate to X'
→ PASS for X does not authorize X'
→ X' becomes the new candidate
→ full verification must run against X'
```

The candidate is eligible only when verification reaches a stable fixed point:

```text
full_verification(C) = PASS
AND
verification no longer changes policy-relevant candidate state C
```

Incidental outputs such as logs, coverage artifacts, caches, temporary browser files, or other explicitly non-candidate outputs must be redirected/ignored/cleaned or treated as verification-environment violations rather than silently incorporated.

Intentional generated artifacts that are repository state become part of the new candidate and must participate in the fixed-point loop.

Cycles, non-convergence, or unclassifiable candidate mutation fail closed for that transition.

### Evidence classes remain distinct

Full-verification evidence is not the same as:

```text
convergence-unit readiness evidence
promotion readiness evidence
provider review/check evidence
```

ADR-037 removes the former separate ContributionUnit integration-readiness evidence class. A valid authoritative managed checkpoint is an eager integration candidate; exact state/topology/claim/conflict/verification preconditions still must be revalidated. The remaining evidence classes may have additional context bindings (for example sealed membership, target observation, policy, submission revision, or provider semantics).

## Rationale

The real requirement is that the **exact result** has a valid proof, not that the same expensive process be repeated a fixed number of times.

This preserves strong verification while enabling exact safe reuse later and prevents verifier-induced mutations from escaping unverified.

## Consequences

- A fast-forward to an exact already-verified OID can reuse valid full-verification evidence.
- A new merge/projection/restack result requires new evidence.
- Policy changes invalidate evidence governed by the changed policy.
- Verification-context changes invalidate only evidence whose declared context includes those changed inputs.
- Evidence cache/persistence format becomes a design concern, but correctness does not require all historical evidence to be retained forever.
- Local critical-section execution may use transient evidence for immediate commit correctness and persist it afterward for audit/cache.
- Remote verification requires an immutable transported candidate identity so the returned evidence can bind to exactly what is later promoted.

## Alternatives considered

- **Always rerun at every boundary even for the exact same state:** safe but rejected as the semantic invariant because it conflates proof validity with process repetition.
- **Cache by branch name or PR number:** rejected because names do not identify exact content/context.
- **Accept test-generated tracked changes after a passing run without re-verification:** rejected because the committed state would not be the fully verified state.

## Related decisions

Extends ADR-010 and ADR-029; interacts with ADR-007, ADR-012, ADR-021, ADR-027, and ADR-028.


## Amendment by ADR-057 — retain exact binding, remove internal verification loop

ADR-057 retains this ADR's exact-state evidence rule but supersedes the `ruu`-owned verification-induced mutation/fixed-point loop. External `DevelopmentValidationEvidence` may be reused only for the same exact candidate + applicable development-gate profile + relevant declared context. A different candidate is never authorized by evidence for the old one.

If Development System validation tools mutate source state, formatting, generated artifacts, snapshots, lockfiles, or other candidate content, that mutation is handled entirely in the Development System. The changed state must later re-enter `ruu` as ordinary authored/current managed work and acquire its own exact-bound evidence. `ruu` does not classify parasite outputs, detect formatter/generator cycles, choose a maximum validation iteration count, or clean verifier artifacts.

When `ruu` itself materializes an immutable exact candidate and validation discovers semantic changes are needed, the candidate is not mutated in place; the external system authors a new state through normal ContributionUnit/reconciliation/review/settlement flows.

## Amendment by ADR-060 — generic development-validation gate removed

Any wording in this ADR that requires, consumes, reuses, waits on, persists, or emits a generic `DevelopmentValidationEvidence` / `DevelopmentValidationDemand` as a `ruu` prerequisite is superseded by ADR-060. Development-quality validation remains outside `ruu`; each Git/managed/provider transition now uses only its transition-local exact prerequisites plus the narrow authoritative external facts specific to that boundary. Broader exact-state/TOCTOU binding remains normative for evidence/facts that still genuinely exist.
