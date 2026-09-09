# Ruu — STATE-SPACE-AUDIT v37

- **Date:** 2026-09-07
- **Technical finite-state families:** through ADR-069
- **Package governance:** ADR-070 product-intent layer statically checked; no new transition family
- **Baseline retained:** v36 = 14,818 finite combinations
- **Current total:** **14,866 finite combinations — PASS**

## New ADR-069 families

### A. Work-bearing invocation / PromotionGroup occurrence identity — 16 combinations

Dimensions:

```text
invocation relation: SAME | DISTINCT
cohort relation: SAME | DIFFERENT
promotion binding: NEW_GROUP | REVISE_EXISTING_GROUP
group-bound authority: absent | present
```

Verified properties:

```text
same invocation id + changed immutable cohort
→ INTEGRITY_FAILURE

same invocation id + same definition
→ idempotent replay

distinct invocation + NEW_GROUP
→ distinct PromotionGroup occurrence

distinct invocation + identical ConvergenceUnit members
→ still distinct PromotionGroup occurrence

REVISE_EXISTING_GROUP without current group-bound authority
→ blocked / fail closed
```

### B. Group-local exact resolution and terminal freeze — 24 combinations

Dimensions:

```text
group terminality: nonterminal | terminal
unrelated live ConvergenceUnit movement: absent | present
revision authority: NONE | VALID | INVALID
member touched by revision: no | yes
```

Verified properties:

```text
unrelated live movement + no group-bound revision
→ retain prior group-local exact state

valid nonterminal same-group revision + touched member
→ adopt new group-local exact state

valid same-group revision + untouched member
→ retain untouched prior binding

terminal group + attempted revision
→ resolution frozen

invalid revision authority
→ blocked / fail closed
```

### C. Descendant restack versus authored child revision — 8 combinations

Dimensions:

```text
parent exact state changed: no | yes
ADR-050 transplant result: CLEAN | CONFLICT
explicit child semantic reconciliation authority: absent | present
```

Verified properties:

```text
parent changed + clean transplant
→ provider/submission restack only
→ child internal owned exact state unchanged

parent changed + conflict + no semantic authority
→ RECONCILIATION_REQUIRED
→ child owned state unchanged

parent changed + conflict + explicit authority
→ child may enter REVISE_EXISTING_GROUP continuation
```

## Concrete Git regression added

`git-group-local-correction-smoke-v1.sh` proves the minimal case:

```text
M -> A          # G1 exact state
     \
      B         # later G2 owns A -> B

G1 correction authored from A:
A -> A'
```

The smoke verifies:

1. `A'` does not contain G2-owned work from `B`;
2. the original child owned anchor `B` remains unchanged/auditable;
3. ADR-050-style exact state transplant `Restack(A, B, A')` yields a clean tree containing both the G1 correction and G2-owned effect.

Result:

```text
group-local correction + descendant restack smoke: PASS
```

## Retained executable regressions

```text
ADR-048 materialization: PASS
ADR-050 restack: PASS
DIRECT target advancement: PASS
repository bootstrap: PASS
canonical checkpoint: PASS
provider-route C→H→R→O realization: PASS
ordinary branch deletion / managed checkpoint neutrality: PASS
ADR-069 group-local correction / descendant restack: PASS
```

## Static/current-document checks

```text
ADR numbering 001..070: PASS
ADR-070 agentic-version-control Product intent / ECP conformance vocabulary: PASS
Markdown fence balance: PASS
current normative ADR-069 vocabulary: PASS
ADR-070 adds no finite state dimension; existing 14,866-combination model is unchanged
legacy spec filename compatibility: checked by packaging pass
```

Key required current semantics are statically asserted:

```text
LogicalInvocation
REVISE_EXISTING_GROUP
group-local exact resolution
membership_fingerprint
Invariant 161
Invariant 168
ADR-069 closure of backlog 30.42/30.43
agentic version control built on Git
provider publication as extended realization layer, not core identity
```

## Total

```text
retained v36: 14,818
ADR-069 new families: 48
------------------------
v37 total: 14,866
```

**Verdict: PASS.**
