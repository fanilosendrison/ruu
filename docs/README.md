---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu-architecture"
severity: "guideline"
name: "Ruu architecture documentation"
---

# Ruu architecture documentation

This directory contains Ruu product documentation, design history, and a
separate repository-governance area. Repository process must not be confused
with product semantics.

## Ruu product and architecture documentation

### Normative specifications

- [Ruu specification](specification/ruu-spec.md)
- [External Control Plane contract](specification/external-control-plane-contract.md)

These documents define current requirements, invariants, state semantics, and
authority boundaries.

### Non-normative architecture

- [Problem statement](architecture/problem-statement.md)
- [Architecture overview](architecture/overview.md)

These documents explain the product problem, rationale, and mental model. They
do not override a normative specification or an accepted ADR.

### Architectural decisions

- [ADR index](adr/README.md)

ADRs remain chronological. Their directory is not subdivided by topic because
decision order and amendment history are part of their meaning.

### Design material

- [Decision integration log](design/decision-integration-log.md)

Design material records reasoning and integration history. It is not a work
queue and does not create product semantics.

## Qualification and history

- [Qualification policy and replay limitations](../qualification/README.md)
- [Design backlog through ADR-081](history/design-backlog-through-adr-081.md)
- [Ruu rename migration](history/rename-migration-ruu.md)

The former design backlog is retired historical material. No new findings or
work items belong there. The immutable pre-reorganization package is retained
under `qualification/releases/adr-080-flat/` and is not an active editing
surface.

## Repository governance

- [Ruu Engineering Project profile](repository-governance/ruu-engineering.md)
- [Ruu Engineering GitHub Project](https://github.com/users/fanilosendrison/projects/3)

This area tells agents and maintainers how to discover, create, classify, and
complete repository work. Ruu Engineering is the primary durable tracker for
new specification, formal-verification, qualification, implementation, and
review follow-ups.

GitHub Issues, Project fields, comments, and Pull Requests are work-management
records. They never substitute for normative specifications or accepted ADRs.

## Recommended product reading order

1. Problem statement.
2. Architecture overview.
3. Product intent in the Ruu specification.
4. External Control Plane contract.
5. ADR-070 and ADR-078 for the governing product experience.
6. ADR-074 through ADR-080 for the current observation model.
7. ADR-081 for exact authoring dependencies before source promotion.
8. Earlier ADRs when implementation details require their decision history.

For repository work, apply the shared GitHub Engineering Projects protocol and
read the Ruu Engineering profile before handling an Issue or creating a durable
finding.
