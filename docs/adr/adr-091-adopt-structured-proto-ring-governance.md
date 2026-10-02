---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Adopt structured proto-ring governance"
id: "ADR-091"
status: "accepted"
date: "2026-10-02"
decision_body_sha256: "a20e4605cc5a901885f070251b3e7bbb2cc77abced3e00fd95edd8e790062959"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-083"
    - "ADR-085"
governs:
  - "Repository Governance Model v2 adoption"
  - "Structured governance registry and profile ownership"
  - "Executable proto-ring provider authority and currentness"
  - "Ruu governance and qualification authority preservation"
  - "Obsolete active governance carrier retirement"
---

# ADR-091 — Adopt structured proto-ring governance

## Context

Ruu adopted proto-ring as a shared governance provider in ADR-083 and bound its
active governance contracts in ADR-085. Those decisions remain immutable
historical records, but the original active realization distributed current
contract pins, validation membership, projection mappings, and evidence mappings
across prose-heavy local carriers and Python construction.

Proto-ring Issues #47 through #51 now provide consumer-owned Governance Binding,
Repository Integrity, Evidence Requirements, and Projection registries plus
Repository Governance Model v2 routing. Independent confrontation against Ruu's
current authority found that those generic structures can represent Ruu without
assuming Turnlock-specific product, formal, qualification, or repository
semantics.

Ruu must adopt the structured substrate without transferring authority for its
product, specification, external control plane, qualification evidence,
retained history, replay, or repository-specific rules. In particular,
`requirements.txt` already owns the executable proto-ring identity, while the
installed distribution and Governance Binding Registry are distinct secondary
representations requiring distinct currentness checks.

## Decision

### 1. Adopt Repository Governance Model v2

Ruu adopts model version 2 with exactly these applicable capabilities:

```text
architecture_decisions
governance_authority
governed_objects
shared_governance_provider
projection_integrity
repository_integrity
evidence_requirements
authoritative_ref_monotonicity
```

The repository-owned `AGENTS.md` frontmatter routes each capability to its
canonical consumer-owned profile, registry, or binding. The provider binding
uses `shared_governance_provider / registry`.

### 2. Adopt canonical structured declarations

Ruu adopts:

- a Governance Binding Registry as authority for active generic governance
  contract pins;
- a Projection Registry for real authority-to-secondary-representation
  relations;
- a persistent Repository Integrity profile as authority for current-state
  validation membership and order; and
- an Evidence Requirements Registry for post-baseline artifact and
  recorded-output identity requirements.

The governed-object catalog remains intentionally limited to canonical ADR
identities. Qualification obligations, artifacts, replay entries, repository
checks, and specification sections do not become governed objects merely to
populate these registries.

### 3. Preserve executable-provider authority separation

`requirements.txt` remains the sole authority for Ruu's exact executable
proto-ring provider identity. The Governance Binding Registry contains a
structured secondary representation of that identity, and the effective
installed/executed proto-ring distribution is a separate secondary
representation.

Ruu owns one validation for registry-copy currentness and another for installed
provider currentness. Pip, Python, PEP 610, and requirements-file semantics
remain Ruu realization concerns; proto-ring does not acquire those semantics.

### 4. Preserve Ruu authority and qualification boundaries

Ruu retains authority for:

- product and specification semantics;
- the external-control-plane contract;
- accepted decisions and canonical ADR content;
- qualification policy, evidence schemas, registrations, artifact roles,
  SHA-256 construction, and exact replay comparison;
- immutable ADR-080 custody, retained lineage, and historical evidence;
- post-baseline evidence and replay;
- Git-smoke replay and its Git version requirement; and
- repository-specific validation, CI, engineering-work, and discovery rules.

Repository Integrity remains current-state validation. The qualification
sequence remains Repository Integrity followed by retained historical replay,
post-baseline replay, and Git-smoke replay. Registry declarations do not turn
bounded historical custody into current qualification truth.

### 5. Retire duplicate active carriers after migration

After each active fact has a structured owner, Ruu removes the obsolete Shared
Governance Provider and Exact Evidence Binding carriers, duplicate contract pins
from local profiles and bindings, and Python-owned Repository Integrity
membership/order. Historical ADR-083 and ADR-085 text remains unchanged because
it records accepted historical decisions rather than mutable current binding
state.

## Consequences

- Active generic governance dependencies are mechanically discoverable through
  one routed model and exact registries.
- Dynamic validation membership is persistent selector policy rather than
  Python-owned canonical membership.
- Post-baseline hash comparisons instantiate routed persistent evidence
  requirements while Ruu retains all domain interpretation.
- Generated and bounded-historical projections are distinguished explicitly.
- Ruu and Turnlock-Rust exercise the same generic substrate without sharing or
  transferring consumer semantics.
- Updating an executable provider requires independently updating and proving
  the authoritative requirement, registry representation, and installed
  realization as applicable.
