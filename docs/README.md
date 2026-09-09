---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu-architecture"
severity: "guideline"
name: "Ruu architecture documentation"
---

# Ruu architecture documentation

This directory is the active source for Ruu architecture documentation.

## Authority classes

### Normative specifications

- [Ruu specification](specification/ruu-spec.md)
- [External Control Plane contract](specification/external-control-plane-contract.md)

These documents define current requirements, invariants, state semantics, and authority boundaries.

### Non-normative architecture map

- [Architecture overview](architecture/overview.md)

The overview provides the recommended mental model but does not override a normative specification or an accepted ADR.

### Architectural decisions

- [ADR index](adr/README.md)

ADRs remain chronological. Their directory is not subdivided by topic because decision order and amendment history are part of their meaning.

### Design and history

- [Open design backlog](design/open-design-backlog.md)
- [Decision integration log](design/decision-integration-log.md)
- [Ruu rename migration](history/rename-migration-ruu.md)

The design backlog records current and closed questions. It is not a substitute for the normative specification.

## Recommended reading order

1. Architecture overview.
2. Product intent in the Ruu specification.
3. External Control Plane contract.
4. ADR-070 and ADR-078 for the governing product experience.
5. ADR-074 through ADR-080 for the current observation model.
6. Earlier ADRs when implementation details require their decision history.

The immutable pre-reorganization package is retained under `qualification/releases/adr-080-flat/` and is not an active editing surface.
