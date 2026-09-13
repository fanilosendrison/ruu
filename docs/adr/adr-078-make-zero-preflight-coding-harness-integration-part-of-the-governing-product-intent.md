---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Make zero-preflight coding-harness integration part of the governing product intent"
id: "ADR-078"
status: "accepted"
date: "2026-09-08"
decision_body_sha256: "e9baab86e60137fdb9dfd1bb5cb138f89d917fdd21549251daf915e1a3372f80"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-078 — Make zero-preflight coding-harness integration part of the governing product intent

- **Status:** Accepted
- **Date:** 2026-09-08
- **Decision order:** 078
- **Amends/clarifies:** ADR-023, ADR-039, ADR-056, ADR-070, ADR-073, ADR-077, the consolidated specification, and the External Control Plane contract
- **Leaves open:** backlog 30.49 umbrella and 30.54–30.55

## Context

The architecture correctly requires several facts to exist **before the first managed write**: ContributionUnit/ConvergenceUnit identity and binding, isolated worktree/ref topology, mutation authority, and (after ADR-075/077) repository-common native-ref observer coverage. ADR-023 intentionally placed this pre-edit provisioning outside the later `ruu` convergence invocation so isolation could not be created retroactively after editing.

That phase separation can, however, be misread as a product requirement for a second user-operated Development System or an explicit preflight workflow such as:

```text
ruu start
ruu create-cu
ruu provision
launch agent
...
ruu
```

Such an implementation could satisfy many lower-level invariants while violating the intended product. The intended experience is that the user installs Ruu once, launches a supported coding harness (Pi, Claude Code, Codex, or another integrated harness), tells the agent what to implement, and later the user or agent invokes `ruu` whenever the current block should cross the Git boundary. CU/worktree/ref/observer/binding machinery is internal plumbing.

The missing distinction is between **architectural authority** and **product packaging**. The External Control Plane / Development System must remain authoritative for semantic work decisions that Ruu cannot infer safely. That does not imply it must be a separately installed product. A Ruu distribution can supply an adapter/integration that implements the role for a supported coding harness while keeping the convergence engine semantically neutral.

## Decision

### 1. Zero-preflight is part of the normative ordinary user experience

For a supported coding harness, the ordinary conforming sequence is:

```text
one-time: install Ruu
          (installation may register supported-harness adapters)

per coding session/work request:
launch supported harness
→ tell agent what to implement
→ agent authors normally

when a checkpoint/convergence boundary is desired:
user or agent runs `ruu`
```

The ordinary workflow MUST NOT require the user to run a separate Ruu `start`, `create-cu`, `provision`, `init/register`, observer-install, or topology command before implementation. It MUST NOT require the user to operate a second control-plane/provisioner product merely to begin managed coding.

Administrative, diagnostic, recovery and testing interfaces may expose internal provisioning primitives; they are not the normative ordinary authoring interface.

### 2. Required pre-edit guarantees remain mandatory and move behind the harness integration

Zero-preflight does not weaken ADR-023/073/075/077 timing. Before the first managed write in each repository touched for authoring, the supported harness integration MUST cause the required safe surface to exist, including as applicable:

```text
repository admission/reactivation
ConvergenceUnit / ContributionUnit durable identity and bindings
immutable PromotionTarget binding
managed authoring ref
dedicated V1 worktree
mutation authority/write authorization
attested repository-common native-ref observer coverage
opaque coordination metadata needed for later handoff/checkpoint
```

The integration may establish this lazily on first **authoring intent/touch** of a repository. It MUST happen before the first managed write, not after detecting that edits already occurred. For an existing repository not yet known to the coordination domain, the integration may also perform the explicit ADR-022 admission/registration transition automatically when current authority/policy makes that repository admissible. This is distinct from silently registering a repository merely because a later `ruu` command happens to be invoked from its CWD.

### 3. The External Control Plane is a role, not a mandatory second product

The External Control Plane / Development System remains the normative authority boundary defined by ADR-039. A conforming Ruu distribution MAY ship a supported-harness integration that implements part or all of that role's runtime/provisioning mechanics.

Therefore:

```text
architecturally external semantic authority
!=
separately installed/user-operated product
```

The same installed product may contain:

```text
Ruu convergence engine/CLI
+ native observer helper
+ coding-harness adapters
+ pre-edit provisioning primitives
```

without collapsing the authority boundary.

### 4. Semantic authority does not move into the convergence engine

A Ruu-supplied harness integration is plumbing for realizing externally authoritative work intent safely. It does not authorize the convergence engine to infer or decide:

```text
what task/feature means
whether two semantic work scopes are the same
whether work is semantically complete
whether validation is sufficient
whether ambiguous authored meaning should be chosen
```

Those remain Development System / External Control Plane concerns. Opaque identities and topology may be generated automatically, but semantic declarations that the architecture marks external remain external declarations.

### 5. ADR-023 means phase separation, not product separation

ADR-023 is henceforth interpreted as:

```text
pre-edit provisioning phase
!=
later convergence/checkpoint invocation phase
```

not:

```text
pre-edit provisioning product
!=
Ruu distribution
```

The later `ruu` invocation MUST NOT create a missing worktree/observer/binding retroactively and pretend prior edits were protected. A Ruu-supplied harness integration MAY perform those operations beforehand.

### 6. Supported harnesses may differ; the product contract is capability-based

The core architecture does not require Pi, Claude Code, Codex, `/go`, or any named harness. A harness is product-supported when its integration can reliably establish the required pre-edit boundary before managed writes and supply/recover the durable external declarations required by the contract.

An unsupported harness does not become supported merely because it can execute the `ruu` CLI after editing. Implementations may add harness adapters incrementally without changing the core semantics.

### 7. Invocation UX remains the checkpoint boundary

Once authoring has been provisioned invisibly, the explicit `ruu` invocation keeps the meaning already established by ADR-057/069/070:

```text
"this current block is ready to cross the Git boundary"
```

The user/agent does not manually provide CU IDs, repository lists, PromotionGroup membership, stack topology, or other derivable internal coordination data. The harness integration carries/generates the durable invocation/handoff metadata behind that ordinary command.

## Rationale

This preserves all pre-edit safety invariants while aligning the implementation boundary with the intended product. The user experiences one version-control product, not a visible orchestration stack. Internally, authority remains separated so Ruu does not become a semantic task orchestrator.

It also prevents a future implementation from using the words "External Control Plane" or "provisioner" as justification for requiring manual lifecycle commands that the product can perform mechanically.

## Consequences

- A supported coding-harness integration is part of the normative product experience, even though the core remains harness-agnostic.
- One-time installation may install/register observer helpers and harness adapters; per-repository/per-CU plumbing is automatic/idempotent.
- The first managed authoring touch becomes an integration boundary that must occur before write.
- The ordinary later `ruu` command remains simple and explicit.
- ADR-023's safety phase separation is preserved but its packaging interpretation is narrowed.
- Observer coverage from ADR-077 remains invisible product plumbing rather than a user prerequisite.
- Supporting a new harness requires proving its pre-edit interception/provisioning contract; simply being able to run a shell command after edits is insufficient.

## Rejected alternatives

### Require explicit `ruu start` before every work block

Rejected because it exports internal lifecycle topology to the user and violates the governing hands-off experience.

### Require a separate Development System product

Rejected as a product requirement. The Development System/ECP is an architectural role and may be implemented by bundled integration. Separate products remain possible deployments, not the normative UX.

### Defer provisioning until the first `ruu` checkpoint

Rejected because worktree isolation, binding identity and observer coverage cannot be established retroactively.

### Let the convergence engine infer all semantic work topology automatically

Rejected because zero-preflight is not permission to guess semantic intent. Authority separation remains normative.

## Amendment by ADR-081 — exact dependency selection remains hidden plumbing

A supported harness may expose/discover exact pending managed authoring commits and explicitly select one stable source ContributionUnit/version for a new consumer before first write. The user does not construct AuthoringDependency records, invoke the source first, or select a later provider stack. The harness submits an authorized internal provisioning demand to the existing fenced ConvergenceEngine; Ruu performs exact source proof, durable OID anchoring, adoption, and mechanical reconciliation before permitting the consumer's first write. This internal demand is not a work-bearing checkpoint invocation and creates no PromotionGroup. Failure never falls back to dirty producer-state capture or ancestry guessing.
