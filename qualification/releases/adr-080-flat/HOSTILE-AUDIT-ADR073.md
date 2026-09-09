# Hostile Audit — ADR-073

- **Date:** 2026-09-08
- **Target:** v1 authoring substrate boundary
- **Verdict:** **PASS — WORKTREE-ONLY V1 WITHOUT PERMANENT WORKTREE IDENTITY**

## Attacks exercised

### H1 — two active ContributionUnits share one checkout

Expected: forbidden by ADR-001/073. Every actively authored v1 ContributionUnit has a dedicated Git worktree/ref surface. **PASS.**

### H2 — external Development System supplies a prebuilt commit and bypasses managed authoring topology

Expected: no normative v1 direct immutable-input contract exists. A future alternative substrate requires a new ADR. **PASS.**

### H3 — human/agent makes an ordinary Git commit inside the managed worktree

Expected: still valid native Git use. ADR-073 does not forbid ordinary commits inside the supported worktree substrate; Ruu reconciles exact state from the managed topology. **PASS.**

### H4 — worktree disappears after exact checkpoint capture

Attack: infer that ADR-073 made the worktree the permanent ContributionUnit identity.

Expected: rejected. ADR-038/071 remain controlling: durable identity/checkpoints survive post-capture artifact disappearance. **PASS.**

### H5 — worktree deleted during still-live authoring

Expected after ADR-074 correction: managed-authoring old-ref removal opens the ADR-071/074 disposition transition; proven terminal deletion means abandonment, while proven rename/rebind means continuation. ADR-073 adds no competing lifecycle meaning. **PASS.**

### H6 — future sandbox support is blocked forever

Expected: false. ADR-073 deliberately phrases the durable requirements as isolation/base/authority/freeze/exact-capture properties and permits a future sandbox ADR to prove equivalence. It merely refuses speculative v1 adapter APIs today. **PASS.**

### H7 — implementation adds unused generic `AuthoringIngress` layer for hypothetical producers

Expected: unnecessary and not required for conformance. V1 may directly implement the one supported Git-worktree path. **PASS.**

## Adversarial conclusion

The decision is intentionally asymmetric:

```text
V1 concrete authoring substrate = Git worktree
core durable identity after capture != worktree lifetime
future sandbox support = possible, but not predesigned
```

This closes 30.47 without weakening native Git compatibility or over-generalizing the v1 proof surface.

**Verdict: PASS.**
