---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Engineering GitHub Project profile"
---

# Ruu Engineering GitHub Project profile

Apply the shared GitHub Engineering Projects operational protocol before using
this profile. This file contains only Ruu-specific routing, authority,
classification, and workflow policy.

## Fixed routing

- GitHub owner: `fanilosendrison`
- Default repository: `fanilosendrison/ruu`
- Project title: `Ruu Engineering`
- Project number: `3`
- Project URL: <https://github.com/users/fanilosendrison/projects/3>
- Project type: private user-owned GitHub Project V2

Resolve an unqualified `Issue #N` as `fanilosendrison/ruu#N`. Follow an explicit
repository-qualified reference or Issue URL instead when the user provides one.

## Ruu authority boundary

Treat Ruu Engineering as the authority for durable work existence,
classification, priority, and workflow state. Never treat it as authority for
Ruu product semantics.

Apply this repository authority order:

1. `docs/specification/ruu-spec.md`
2. `docs/specification/external-control-plane-contract.md`
3. accepted ADRs under `docs/adr/`, including later amendments
4. `docs/architecture/overview.md`
5. `docs/architecture/problem-statement.md`
6. design history, audits, reports, and recorded outputs

An Issue may identify a semantic defect or propose a resolution, but only the
required accepted ADR and synchronized normative documents can ratify a semantic
change. Report every conflict between an Issue and the controlling repository
sources.

Keep repository process under `docs/repository-governance/`. Keep Ruu product
semantics, architecture, decisions, design history, and qualification evidence
outside that directory.

## Workflow-status mapping

Map the shared protocol's workflow roles to these exact `Status` values:

- unready backlog: `Backlog`
- ready for independent pickup: `Ready`
- active execution: `In Progress`
- reviewable result: `Review`
- completed work: `Done`

`Ready` means that the item can be picked up without reopening its underlying
design discussion. Use the Project's `Agent Queue` as the normal autonomous
pickup surface. A direct user request may select another item, but it does not
ratify proposed semantics or remove unresolved dependencies.

## Classification fields

### Phase

Use `Phase` for the domain that owns the immediate deliverable:

- `Specification`
- `Formal Verification`
- `Implementation`

Classify state-space work, model checking, and associated qualification evidence
as `Formal Verification` under the current field vocabulary. Create linked
follow-up Issues when downstream phases require independent acceptance or
scheduling.

### Kind

Use `Kind` for the item's relationship to the engineering plan:

- `Agent Task`: independently scoped work intended for direct execution.
- `Follow-up`: downstream work created by another task, finding, or accepted
  decision.
- `Finding`: a validated concern that still requires adjudication, design, or
  correction.

Do not retain unvalidated observations as `Finding` items.

### Priority

Use `Priority` according to the Project contract:

- `P0`: blocks current progress.
- `P1`: should be completed in the current phase.
- `P2`: important but non-blocking.
- `P3`: useful or worth retaining, but can wait.

Priority controls scheduling only. It never overrides Ruu authority,
prerequisites, qualification, or fail-closed behavior.

## Project views

The intended views are:

- `Now`: board filtered to `Phase: Specification`.
- `Agent Queue`: table filtered to Issues in `Ready` or `In Progress`.
- `Specification`: table filtered to `Phase: Specification`.
- `Formal Verification`: table filtered to `Phase: Formal Verification`.
- `Implementation`: table filtered to `Phase: Implementation`.

Treat any difference between these declarations and live GitHub configuration as
an inconsistency to report before relying on the affected routing.

## Issue requirements

A Ruu Issue that may change semantics must:

- distinguish the observed problem from a proposed resolution;
- state the current authoritative and fail-closed boundary;
- link the controlling specification sections and ADRs;
- identify every affected normative and qualification artifact;
- define acceptance criteria and replay or validation obligations;
- end with the reminder that the Issue is a work-management record and that
  repository specifications and accepted ADRs remain authoritative.

Use native GitHub parent, sub-issue, dependency, and Pull Request relationships
when available. Do not encode the only dependency record in Project ordering.

## Findings and retired backlog

Never add new work or review findings to
`docs/history/design-backlog-through-adr-081.md`. It is a closed historical
archive.

Create a `fanilosendrison/ruu` Issue for every validated finding or other work
unit that must be deferred, handed off, scheduled, or tracked independently.
Add it to Ruu Engineering and populate `Status`, `Phase`, `Kind`, and `Priority`.
Default a retained finding to `Backlog`; use `Ready` only when its dependencies,
scope, authority boundary, acceptance criteria, and validation contract make it
independently executable.

## Repository validation

Use the complete mandatory generation, qualification, replay, Git-smoke, and
whitespace sequence in `AGENTS.md`. Project completion cannot replace any
required repository evidence.
