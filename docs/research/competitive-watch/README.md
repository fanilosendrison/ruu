---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "research-index"
domain: "ruu-competitive-watch"
severity: "guideline"
name: "Ruu / Ruu Cloud Competitive Autonomous-Versioning Watch"
---

# Ruu / Ruu Cloud Competitive Autonomous-Versioning Watch

The Ruu / Ruu Cloud Competitive Autonomous-Versioning Watch is a dated,
evidence-based research archive for comparing available alternatives with the
responsibilities of Ruu Core and Ruu Cloud. Core and Cloud share one cumulative
research history in this repository. The independently pinned Ruu Cloud
repository is a comparison baseline, not a second archive location.

No competitor assessment or rating is established merely by installing this
framework. The initial watchlist contains discovery seeds only. Grouped labels
do not establish legal ownership, affiliation, identity, capability, or
technical equivalence; a real report must verify those facts.

## Authority boundary

This directory governs only how competitive research is conducted and reported.
It does not create or modify Ruu Product Intent, the Ruu specification, the
External Control Plane contract, accepted ADRs, the Ruu Product Rationale, Ruu
Cloud Product Intent, Ruu Cloud Product Rationale, architecture, or
implementation obligations.

Research findings may motivate questions. They cannot automatically mutate
product authority. Named observations and ratings belong only in immutable,
dated reports with explicit scope and evidence.

The governing comparison outcome is:

> **You manage intent; Ruu manages versions.**

The methodology defines the exact semantic boundary behind that benchmark.

## Contents

- [Methodology](methodology.md) defines the comparison benchmark, Core and
  Cloud axes, permanent radar, open discovery, technical inspection, ratings,
  evidence discipline, scenarios, and historical interpretation.
- [Execution](execution.md) defines cadence, coverage operations, publication,
  additive chat delivery, and failure handling without creating a scheduler.
- [Watchlist](watchlist.json) initializes discovery seeds and topics. It is not
  the complete historical roster and contains no rating.
- [Report schema](report.schema.json) defines the source JSON contract for new
  reports.
- [Report template](report-template.md) defines the French-readable Markdown
  projection of the same report data.

## Archive structure

Every future report occupies a new directory:

```text
docs/research/competitive-watch/reports/YYYY/
  RUW-YYYYMMDDTHHMMSSZ/
    report.json
    report.md
```

No report is created by framework installation. The first real watch run creates
the first report.

Published report directories are immutable and append-only. A correction is a
new report that references the report and findings it corrects. A daily,
weekly, monthly, alert, or correction report never overwrites another report.

`report.json` is the source representation. `report.md` is its human-readable
projection and must not add ratings, judgments, evidence, or conclusions absent
from the JSON.

## Four comparison dimensions

Every actor/component is assessed independently on exactly four dimensions:

1. `autonomous_versioning_outcome` — how completely ordinary use removes
   routine version-topology reasoning from users and coding agents.
2. `ruu_core_guarantees` — how completely the examined scope supplies the
   applicable single-host Ruu Core guarantees.
3. `ruu_cloud_guarantees` — how completely the examined scope supplies the
   applicable team-wide, multi-host Ruu Cloud guarantees.
4. `downstream_version_intelligence` — how completely available version-state
   signals support valid longitudinal analysis, evaluation, routing, assurance,
   audit, forensics, and related downstream uses.

There is no aggregate score and no averaging. A component may be strong in one
dimension, depend on another provider in another, and remain indeterminate in
the others.

## Permanent radar and discovery

The effective radar is cumulative. Once an identifiable actor, product, or
component has been evaluated, it remains monitored indefinitely unless an
explicit user instruction stops active monitoring. Stopping monitoring does not
erase identity, findings, evidence, or history.

Every execution performs both accumulated-radar monitoring and open discovery.
The watchlist is discovery seed material only; it never overrides prior report
admissions, explicit user additions, or recoverable pending registrations.

An incomplete scan is reported as incomplete. Public research is not a
conclusion. “No new entrant found” is not proof that no entrant exists.

## Technical depth

Claims and documentation are starting evidence, not automatic guarantee
conclusions. When source is public and a result depends on implementation,
research follows the production path through harness integration, authoring
state, identity, isolation, checkpointing, convergence, stale reconciliation,
dependency adoption, persistence, authority and fencing, retry and recovery,
remote synchronization, provider publication, and downstream capture.

Code, configuration, defaults, feature flags, bypass paths, unknown/error paths,
tests, and production reachability are inspected when needed. `claim`,
`documentation`, `source_inspection`, `tests_inspected`, `reproduced`, and
`proof_artifact` remain distinct evidence classes.

Closed, inaccessible, or incomplete source creates an evidence limitation, not
a negative capability finding. Absence of a public source is not evidence that
a capability is absent. The actor remains on the radar and unfinished technical
questions remain persistent investigations.

## Human-readable delivery

Each execution is intended to deliver its complete readable report as a new,
distinct ordinary chat response. A correction is also a new response. A rolling
edited message, link-only notification, or weekly synthesis does not replace a
daily report.

Repository archive history and chat history are complementary. Neither replaces
the other. The external scheduler and chat interface control execution,
routing, display, and retention; repository configuration cannot create or
verify the scheduler, force delivery into a particular conversation, recover a
deleted chat, or impose platform retention policy.

A future run may claim `ARCHIVED` only after reading its newly published files
back from the real published reference. Until that has occurred, recurring
publication remains an operational dependency rather than an established fact.
