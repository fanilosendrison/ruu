# Ruu — Global State-Space Consistency Audit v2

- **Date:** 2026-09-04
- **Scope:** main requirements + ADR-001..ADR-032 after integration of the verification/review decisions
- **Result:** **PASS with open design backlog; no contradictory authorized transition found in the modeled finite families**

## 1. Why the audit was rerun

The previous global audit covered 12,246 factorized combinations after the convergence-unit/promotion-unit/submission-ref redesign.

The current revision adds new independent dimensions:

```text
managed full-verification eligibility
exact evidence reuse/invalidation
verification-induced mutation/fixed point
verification-capacity admission
review-request publication intent
review-request invalidation after head revision
internal integration result verification
```

These dimensions affect commit authority, internal synchronization, promotion, submission publication, and fixed-point terminal states, so a local paragraph-level review was insufficient.

## 2. Reproducible enumeration

`state-space-audit-v2.py` exhaustively enumerates the new finite factorized families and asserts their authorization predicates.

Observed result:

```text
Ruu state-space audit v2: PASS
baseline existing factorized combinations: 12,246
writer_commit_verification_crosscheck: 810
state_producing_transition_verification: 432
verification_evidence_reuse: 72
verification_fixed_point: 108
verification_capacity_scheduler: 180
review_request_intent: 108
review_revision_invalidation: 24
internal_integration_evidence: 240
new combinations evaluated: 1,974
combined factorized combinations represented: 14,220
```

The audit remains factorized rather than pretending that an unbounded Git DAG/provider world can be finitely exhaustively enumerated.

## 3. Commit/ownership crosscheck

Verified simultaneously:

- ACTIVE writer + no exact delegation never becomes commit-authorized;
- another invocation's delegation never authorizes this invocation;
- an INACTIVE writer still requires this invocation's worktree claim;
- dirty state alone is insufficient;
- claim/authority alone is insufficient;
- `PASS` evidence that is stale/missing/failed/unknown cannot authorize commit;
- a mutated/unknown candidate cannot authorize commit;
- `REMOVED` never becomes committable;
- verification-capacity state cannot substitute for writer authority.

Result: **PASS**.

## 4. Verification-induced mutation / fixed point

Verified:

```text
PASS + exact stable candidate
→ potentially eligible

intentional candidate mutation
→ new candidate
→ old PASS cannot authorize it

unknown/cyclic/non-convergent mutation
→ blocked

FAIL / infrastructure failure
→ cannot authorize result
```

Parasite outputs remain outside candidate state by policy rather than becoming implicit changes.

Result: **PASS**.

## 5. Evidence reuse

The only reusable family is semantically:

```text
exact result SAME
verification policy SAME
relevant declared verification context SAME
evidence VALID
```

Any changed result, changed/unknown policy, changed/unknown context, stale/missing/failed evidence blocks reuse.

This confirms that the architecture now expresses:

> **the exact result must be fully verified**

rather than:

> **the same process must be redundantly re-executed at every boundary**.

Result: **PASS**.

## 6. Internal integration crosscheck

Checked `target/base→convergence-unit`, `convergence-unit→writer`, and `writer→convergence-unit` implications.

- divergent/state-producing merges need evidence for the new exact result;
- a conflict never advances the authoritative ref;
- unknown ancestry never advances the authoritative ref;
- missing/stale/failed evidence never authorizes a new integration result;
- FF/state-preserving adoption may consume valid exact evidence;
- `writer→convergence-unit` remains FF-only;
- no verification rule accidentally introduces rebase/non-FF authority for internal refs.

Result: **PASS**.

## 7. Verification capacity versus mutation authority

Checked:

- `AVAILABLE` compute does not authorize Git mutation;
- Git claim does not imply compute availability;
- `SATURATED`, `DISABLED`, or `UNKNOWN` capacity never starts a queued verification;
- stale/unknown candidate freshness never starts using an old queue reservation;
- `verification_capacity=1` remains compatible with fine-grained parallel Git claims.

Result: **PASS**.

## 8. PR publication/review intent

Checked the new orthogonal axis:

```text
NONE
REVIEW_NOT_REQUESTED
REVIEW_REQUESTED
```

A valid `REVIEW_REQUESTED` state requires:

```text
provider submission exists
internal/promotion readiness required by policy
exact current head/revision
valid PR-author/ship-ready gate
```

A changed exact head cannot retain stale review-request evidence.

`REVIEW_NOT_REQUESTED` may coexist with either internal readiness state and therefore does not become a disguised `DRAFT` business state.

Result: **PASS**.

## 9. Ref-class/history crosscheck after verification changes

Rechecked that verification requirements do not accidentally alter the already-decided history model:

```text
WRITER_REF / CONVERGENCE_UNIT_REF
→ append-only
→ never rebase/amend/backward-reset/non-FF rewrite

DIRECT target
→ descendant-only FF

PR target
→ read-only to Ruu

rewriteable SUBMISSION_REF
→ narrow policy/provider-authorized restack/rebase
→ expected-old protection
→ internal source OIDs unchanged
```

Result: **PASS**.

## 10. Readiness/verification independence

Rechecked that:

```text
COMMITTED / full-verification PASS
```

does not imply:

```text
writer CLOSED
writer READY
convergence unit READY_INTERNAL
promotion unit READY_FOR_PROMOTION
REVIEW_REQUESTED
```

Likewise, provider review intent does not manufacture internal readiness.

Result: **PASS**.

## 11. Fixed-point/global parallelism

New waiting/blocking terminal classes are localized:

```text
WAITING_VERIFICATION_CAPACITY
BLOCKED_VERIFICATION
REVIEW_NOT_REQUESTED provider wait/check state
```

They do not become a global mutex and do not suppress unrelated:

```text
writer work
other repo convergence
push recovery
DIRECT promotion
PR update/restack
provider observation
cleanup
```

Result: **PASS**.

## 12. Static consistency/lint checks

The revised artifact set also passed:

- balanced Markdown code fences;
- ADR reference resolution (ADR-001..ADR-032 all present);
- sequential ADR decision order 001..032;
- no remaining normative `commit if eligible` shortcut in the main document;
- no internal writer/convergence `DRAFT` state introduced;
- required main-spec markers for verification, evidence reuse, capacity, and review intent present;
- main audit total updated to 14,220 factorized combinations.

## 13. Open questions are not contradictions

The audit deliberately does **not** pretend the following are decided:

- flaky-test retry/quarantine policy;
- external-service test policy;
- evidence storage/retention schema;
- executor/context equivalence for reuse;
- exact PR-author gate contents;
- exact agentic review policy;
- exact GitHub canonical CI/security policy;
- exact provider merge-result/final integration proof policy;
- scheduling/fairness/multi-host verification details.

They are collected in `OPEN-DESIGN-BACKLOG.md` and fail closed where missing policy is required for a critical transition.

## 14. Audit conclusion

The newly added verification and review-request dimensions are compatible with the existing ownership, append-only internal history, promotion-unit/submission architecture, provider governance, and fixed-point concurrency model.

The most important cross-model conclusion is:

```text
new exact managed result
→ exact valid full-verification evidence required
→ only then authoritative adoption

same exact result + same policy/context + valid evidence
→ evidence may be reused
```

No modeled path was found where:

- a writer without authority can commit because verification passed;
- a newly produced internal merge can become authoritative without evidence;
- stale evidence can authorize a changed result;
- verification capacity grants mutation authority;
- a provider draft creates internal readiness;
- `REVIEW_REQUESTED` survives a stale exact-head quality assertion;
- verification requirements grant forbidden rebase/non-FF authority to internal refs.

**Verdict: PASS for the finite factorized state model represented by this specification.**
