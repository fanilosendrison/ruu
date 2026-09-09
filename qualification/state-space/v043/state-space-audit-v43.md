# State-Space Audit v43 — ADR-078 zero-preflight supported-harness product contract

- **Date:** 2026-09-08
- **Retained baseline:** v42 / 15,740 combinations
- **New ADR-078 combinations:** 128
- **Total:** **15,868 combinations — PASS**

## New dimensions

v43 adds finite coverage for:

1. supported-harness ordinary UX requiring no explicit start/create-CU/provision preflight and no second control-plane product;
2. pre-edit worktree/observer/provisioning safety remaining mandatory before the first managed write;
3. bundled Ruu harness integration without collapsing External-Control-Plane semantic authority;
4. prohibition on retroactive provisioning as a later checkpoint/convergence side effect;
5. simple later `ruu` invocation with internal IDs/repository cohort carried behind the interface;
6. lazy per-repository first-authoring-touch provisioning across multi-repository sessions;
7. administrative/testing provisioning primitives remaining allowed while never becoming ordinary supported-harness requirements.

## Executable result

```text
ADR-078 zero-preflight-supported-harness family: 16 PASS
ADR-078 pre-edit-safety-timing family: 16 PASS
ADR-078 authority-vs-packaging family: 16 PASS
ADR-078 checkpoint-simplicity family: 16 PASS
ADR-078 lazy-multi-repo-first-touch family: 32 PASS
ADR-078 admin-vs-ordinary-interface family: 32 PASS
new combinations: 128 PASS
retained v42 baseline: 15740
v43 total: 15868 PASS
```

## Key safety/product assertions

```text
supported harness + ordinary use
→ no explicit start/create-cu/provision command
→ no separately operated control-plane product

first managed write
→ required pre-edit topology/observer already established
→ never retroactively created by later checkpoint

bundled harness integration
→ allowed
→ does not move semantic authority into convergence engine

later checkpoint
→ ordinary `ruu`
→ harness/integration carries opaque internal handoff metadata
→ caller does not reconstruct CU/repo/group topology

multi-repo session
→ each newly authored repository provisioned lazily before its first write
→ no up-front caller-authored repository list required

admin/testing primitives
→ may exist
→ not ordinary product prerequisites
```

## Verdict

**PASS.** ADR-078 strengthens the governing product contract without weakening the retained pre-edit safety or semantic-authority boundaries.
