# Hostile Audit — ADR-078 zero-preflight coding-harness product intent

- **Date:** 2026-09-08
- **Target:** ADR-078
- **Verdict:** **PASS**

## Attack 1 — Technically compliant but user must run `ruu start`

**Attack:** keep ADR-023 pre-edit safety but expose it as a mandatory user command before every work block.

**Resolution:** rejected as product-nonconformant. ADR-078 makes zero-preflight ordinary supported-harness authoring normative. Internal/admin provisioning commands may exist but cannot be required in the normal path.

## Attack 2 — Require a second Development-System product

**Attack:** interpret “External Control Plane” as “the user must install and operate another daemon/orchestrator before Ruu works.”

**Resolution:** rejected. Architectural externality is authority separation, not mandatory product separation. A Ruu distribution may ship the harness integration/provisioner implementation.

## Attack 3 — Bundle the integration and silently move semantic authority into Ruu

**Attack:** because the adapter ships with Ruu, let the convergence engine infer task grouping, completion, target intent, or validation semantics.

**Resolution:** rejected. Packaging does not change authority. The bundled integration realizes externally authoritative declarations; the convergence engine remains semantically neutral.

## Attack 4 — Provision only when `ruu` is invoked after coding

**Attack:** preserve the simple UX by waiting until checkpoint time, then create the ContributionUnit/worktree/observer around already-edited files.

**Resolution:** rejected. ADR-023/073/075/077 timing remains controlling: required topology and observer coverage must exist before first managed write. ADR-078 moves this work behind harness integration; it does not relax timing.

## Attack 5 — Make the user understand CU/ConvergenceUnit IDs anyway

**Attack:** automatically create topology but require the user to pass internal identities or repository lists at checkpoint.

**Resolution:** rejected under ADR-070/078. The harness/integration carries opaque work-bearing invocation/handoff metadata behind the ordinary `ruu` command.

## Attack 6 — Require all repositories up front

**Attack:** before authoring, ask the user/agent to enumerate every repo the implementation might touch so provisioning can happen.

**Resolution:** rejected. Provisioning remains lazy per repository. A supported harness detects/declares authoring intent as new repos are touched and establishes the surface before that repo's first managed write.

## Attack 7 — “Supported harness” means any shell that can run `ruu`

**Attack:** claim support for a harness even though no pre-edit integration exists; rely on the later CLI invocation.

**Resolution:** rejected. Support is capability-based: the harness integration must reliably establish the pre-edit boundary and durable declarations before managed writes. Post-edit CLI access alone is insufficient.

## Attack 8 — Hidden manual observer setup leaks through ADR-077

**Attack:** advertise zero-preflight but require the user to install `reference-transaction` hooks in every repository.

**Resolution:** rejected. Observer installation/attestation is internal pre-edit product plumbing. Conflicting foreign hook surfaces may block managed authoring under ADR-077, but the normal supported path does not export installation choreography to the user.

## Attack 9 — One-time installation becomes per-session setup

**Attack:** require `Ruu integrate pi` or equivalent before every new coding session.

**Resolution:** nonconformant as an ordinary recurring step. One-time installation/integration may register harness adapters; per-session/per-repository provisioning is automatic and idempotent behind the integration.

## Attack 10 — Hidden `Ruu init` per repository

**Attack:** avoid explicit CU provisioning but still require the user to initialize/register every existing repo manually before launching the harness.

**Resolution:** rejected for the ordinary supported-harness path. The integration may perform the explicit repository-admission transition automatically before first managed write when the repo is admissible. A late CLI invocation still cannot infer registration merely from CWD.

## Attack 11 — Product simplicity weakens fail-closed behavior

**Attack:** if automatic provisioning cannot establish a safe surface, let the agent write anyway to avoid UX friction.

**Resolution:** rejected. Zero-preflight means no manual choreography, not “never block.” If pre-edit safety cannot be established, the managed write must not be admitted. The error is surfaced as a capability/integration problem rather than silently creating unsafe managed history.

## Verdict

ADR-078 preserves the existing safety/authority boundaries while making the intended product path unambiguous: one installed product, supported harness integration, automatic pre-edit plumbing, and a later simple `ruu` checkpoint command.
