# Ruu — Package Verification through ADR-069

- **Date:** 2026-09-07
- **Baseline:** ADR-068 verified/H4-ratified package
- **Current architecture:** ADR-001..ADR-069
- **Current finite audit:** `STATE-SPACE-AUDIT-v37.md`
- **Targeted hostile audit:** `HOSTILE-AUDIT-ADR069.md`

## Integrated decision

ADR-069 ratifies the architecture developed from hostile finding 30.42 and the subsequent correction/restack analysis:

```text
work-bearing logical Ruu invocation
→ durable idempotent invocation identity
→ sealed ContributionUnit handoff cohort
→ ordinary NEW_GROUP mechanically creates one PromotionGroup occurrence
→ PromotionGroup identity is occurrence-bound, not member-set-only
→ exact resolution is group-local, not current(X)
→ ordinary later work never revises older groups
→ explicit group-bound correction/reconciliation may revise one nonterminal group
→ correction starts from that group's exact reviewed/prior state
→ untouched members keep prior exact bindings
→ terminal group resolution freezes
→ ADR-050 restacks descendants without automatic internal-state rewrite
```

This closes hostile backlog **30.42** and **30.43**. Items 30.44–30.48 remain open; v37 narrows 30.48 but does not close it.

## Executable verification

`state-space-audit-v37.py`:

```text
14,866 finite combinations: PASS
ADR numbering 001..069: PASS
current-doc static checks: PASS
Markdown fence balance: PASS
```

New ADR-069 finite families:

```text
logical invocation / group occurrence identity: 16 PASS
group-local resolution / terminal freeze: 24 PASS
descendant restack / authored revision: 8 PASS
```

Concrete mechanics:

```text
ADR-048 materialization: PASS
ADR-050 restack: PASS
DIRECT target advancement: PASS
repository bootstrap: PASS
canonical checkpoint: PASS
provider-route C→H→R→O: PASS
ordinary branch deletion / managed checkpoint neutrality: PASS
ADR-069 group-local correction / descendant restack: PASS
```

The ADR-069 Git smoke proves that a correction for `G1` is authored from `G1`'s exact state and does not absorb later `G2` work, while the descendant owned effect can be transplanted cleanly onto the corrected predecessor under ADR-050.

## Hostile/static consistency pass

The current consolidated spec and ECP contract were scanned for obsolete current rules including:

```text
same-session PromotionGroup identity
DeclarePromotionGroup(...) as ordinary grouping authority
member-set-only promotion_group_id
unqualified current READY_INTERNAL as PromotionGroup resolution
```

No obsolete current normative instance remains in the consolidated spec/contract. Historical ADR-046 wording is preserved as architectural history and explicitly superseded/amended by ADR-069.

Targeted crash/retry cases checked in `HOSTILE-AUDIT-ADR069.md` include:

```text
lost response after invocation acceptance
invocation-id reuse with changed cohort
identical member sets across distinct invocations
shared live ConvergenceUnit after older group settlement
review correction of G1 while G2 already owns later work
clean/conflicting descendant restack
partial multi-repository handoff before invocation seal
same-group PromotionUnit supersession vs unrelated later group
```

## Package integrity

All packaged shell scripts pass syntax validation. All packaged Python audit files pass bytecode compilation. `RUU-SPEC.md` and the legacy compatibility filename `ruu-requirements-v1-merge-policy.md` are byte-for-byte identical in the final package. `MANIFEST.sha256` is regenerated after all final checks.

## Interpretation

ADR-069 does **not** turn logical invocations into FIFO reconciler jobs. Durable logical invocation state records the work checkpoint/promotion occurrence; convergence demand remains coalescible and every authoritative executor run remains a global fixed-point sweep.

A PromotionGroup's group-local exact binding is historical/current state for that group, not a perpetual pointer to the live ConvergenceUnit tip. This is what allows one live ConvergenceUnit lineage to support several independent PromotionGroups safely.

**Verdict: VERIFIED / PASS.**
