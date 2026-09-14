---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu engineering discovery classification profile"
---

# Ruu engineering discovery classification profile

Apply the shared `engineering-discovery-classification` skill before using this
profile. This file binds the shared classification mechanics to Ruu authority,
architecture, qualification, and work routing. It creates no Ruu product
semantics, accepted decision, or qualification evidence.

## Authority binding

Use the authority order in [`AGENTS.md`](../../AGENTS.md#authority-order). Read
the current sources governing the affected concept and preserve every conflict;
do not copy their meaning into this profile or a discovery record.

Bind the shared layers as follows:

- `normative-contract` maps to
  [`docs/specification/ruu-spec.md`](../specification/ruu-spec.md) and
  [`docs/specification/external-control-plane-contract.md`](../specification/external-control-plane-contract.md)
  according to their declared responsibilities and precedence.
- `decision-history` maps to accepted ADRs under [`docs/adr/`](../adr/),
  including explicit later amendments.
- `formal-model-or-analysis` maps to non-normative architecture and design
  analysis and to analytical or state-space representations used by
  qualification. Those artifacts do not replace the normative specifications.
- `verification-or-qualification-evidence` maps to exact-scope artifacts under
  `qualification/`, subject to their immutable snapshot, retained-evidence,
  post-baseline, lineage, manifest, and replay boundaries.
- `architecture-or-implementation` maps to accepted architecture decisions,
  non-normative architecture projections, and future implementation artifacts.
  The repository currently has no production implementation.
- `integration-or-conformance` maps to provider, Git, external-control-plane,
  and environment capability or conformance findings without transferring
  semantic authority away from the specifications and accepted ADRs.
- `repository-governance-or-documentation` maps to procedures under
  `docs/repository-governance/`, generated projections, explanatory documents,
  and work-management records without promoting them into product authority.

## Normative promotion

Classify a discovery as `derived-from-existing-authority` only with a complete
derivation from the current specifications and accepted decisions. Prefer
correcting the mapping, qualification coverage, or clarification of an existing
normative obligation when cited authority already entails the discovery.

Classify behavior not uniquely determined by current authority as
`decision-required`. Keep it locked until Ruu's accepted ADR process resolves
the choice and every affected normative document is synchronized. A user task,
agent recommendation, Issue, architecture preference, qualification result,
provider capability, or implementation convenience does not accept that
decision.

Use `authority-conflict-or-uncertain` when controlling sources disagree, source
provenance is insufficient, or a derivation requires an unstated assumption.
Apply the authority order and required ADR amendment process instead of silently
selecting a convenient source.

## Qualification interpretation

Treat qualification as exact-scope evidence, not product authority:

- never infer new behavior from a passing or failing qualification artifact
  without classification against current authority;
- never report a historical replay as passing without its exact admitted source
  package;
- never modify the immutable release snapshot or retained evidence to make a
  current check pass;
- record post-baseline evidence only through the current qualification metadata,
  continuity, manifest, and replay contracts;
- distinguish an invalid expectation, model, fixture, environment, or evidence
  record from a normative defect.

Load the shared verification-evidence context for state-space results, replay,
Git-smoke evidence, manifests, lineage, audits, or other qualification claims.

## Durable routing and synchronization

Keep transient discoveries with no durable impact in working notes. Preserve a
discovery in the resulting ADR, Issue, review record, commit, architecture or
specification artifact, or qualification record when its reasoning must survive
the session.

For independently tracked work, apply the shared GitHub Engineering Projects
skill and the [Ruu Engineering profile](ruu-engineering.md). Never append new
findings to the retired design backlog. An Issue records work and provenance; it
does not accept Ruu semantics or establish qualification evidence.

Follow the generation, manifest, qualification, replay, and validation contract
in [`AGENTS.md`](../../AGENTS.md#mandatory-validation) after every repository
change. Classification never substitutes for ADR lifecycle, immutable evidence
boundaries, permission, review, or validation.
