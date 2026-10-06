---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "research-operations"
domain: "ruu-competitive-watch"
severity: "strict"
name: "Ruu / Ruu Cloud Competitive Watch Execution"
---

# Ruu / Ruu Cloud Competitive Watch Execution

This document defines watch operations and their limits. It does not create,
activate, modify, or verify a scheduler. The controlling operational statement
is: `repository configuration does not create or verify the scheduler`.

## Agreed cadence

The intended external cadence is:

- a daily morning run around 08:00 Europe/Paris;
- a weekly synthesis on Monday, using the same report format; and
- monthly trajectories in the first-Monday weekly report.

The external scheduling task is named **“Veille Ruu et Ruu Cloud”**. Its actual
calendar, execution, retries, and availability belong to the external
scheduler. This framework neither creates nor changes that task, and the
presence of this file does not prove that the schedule has run.

## No-forgetting and coverage operations

Every run must:

1. reconstruct the effective roster from watchlist seeds, all prior report
   admissions, explicit user additions, and recoverable pending registrations;
2. read source cursors preserved by successful archives;
3. perform both **A — accumulated-radar monitoring** and **B — open discovery**;
4. deepen relevant changes and persistent investigations; and
5. produce a new report even when no significant change is found.

Neither mandatory activity may be omitted because the other consumed available
resources. If either is incomplete, the report declares the corresponding
coverage incomplete.

Coverage targets are:

- refresh sources for every active or not-yet-classified actor at least every
  7 days; and
- check lifecycle, successors, forks, and transferred technology for every
  confirmed dormant or discontinued actor at least every 30 days.

These targets are not expiry periods. Overdue work remains visible and may not
be hidden by repeatedly preferring high-profile actors.

A scan that did not occur remains `not_checked` or `overdue`. Its observation
date, last successful cursor, and due date do not advance. Source cursors may be
commit SHAs, dates, or opaque provider references; their `reason` explains the
meaning when needed. Deferred coverage and capacity limits are reported.

## Basis and publication

Every report pins:

- `fanilosendrison/ruu` and an exact commit;
- `fanilosendrison/ruu-cloud` and an exact commit;
- the report schema version and immutable schema source;
- methodology version `1.0.0` and immutable methodology source; and
- the independently observed Ruu Cloud baseline status.

Before publication:

1. validate `report.json` against `report.schema.json`;
2. verify identifiers, references, dates, axis completeness, semantic
   constraints, source cursors, and radar continuity;
3. render `report.md` from the same data;
4. verify JSON/Markdown equivalence;
5. apply Ruu's current worktree, review, validation, and publication workflow;
   and
6. prove that no previous report changed.

Publication occurs exclusively under:

```text
docs/research/competitive-watch/reports/YYYY/
  RUW-YYYYMMDDTHHMMSSZ/
    report.json
    report.md
```

An ordinary watch run never modifies:

```text
Ruu Product Intent
Ruu specification
External Control Plane contract
accepted ADRs
Ruu Product Rationale
Ruu Cloud Product Intent
Ruu Cloud Product Rationale
competitive-watch methodology
```

The `fanilosendrison/ruu-cloud` repository is a pinned comparison baseline. It
is never the archive location and is not modified by an ordinary run.

Announce `ARCHIVED` only after the report files have been read back from their
real published reference. If archival fails, preserve the produced material,
announce `ARCHIVE_PENDING`, identify the intended destination and exact blocker,
and do not advance source cursors as if archival succeeded.

A report cannot know the commit that will publish itself. The publication
receipt stays outside the immutable report. Never amend a report after
publication merely to insert its publishing commit.

## Additive chat delivery

Every execution delivers a new ordinary response containing the readable French
report. Its title is:

```text
Veille Ruu / Ruu Cloud — Rapport du <date et heure Europe/Paris>
```

The response includes the report ID, observation window, report kind, readable
content, sources, and coverage.

Never:

- replace or edit a previous response as the sole result;
- maintain one rolling canvas or block;
- deliver only a link, notification, or “report updated” statement; or
- replace daily reports with the weekly synthesis.

A correction is a new response that identifies the corrected report. Archived
JSON and Markdown complement chat delivery; they do not replace it. An archival
failure does not cancel readable delivery.

If a platform limit prevents complete display, the new response preserves the
essential conclusions and evidence, identifies exactly what was omitted, and
attaches the complete report only when that artifact was actually produced. It
must not claim that omitted content was displayed.

Use links to prior chat responses only when real links are available. Otherwise
refer to their dates and report IDs without inventing URLs. The scheduler and
chat platform own routing and retention.

## First report and unavailable history

The first real run independently verifies its baseline from primary sources.
Coverage may be partial but must be described precisely. It must not republish
old chat analysis as verified evidence.

If expected roster history cannot be recovered, the report declares
`ROSTER_HISTORY_INCOMPLETE`, preserves every recoverable actor, exposes the
limits, and avoids claiming verified continuity.

No empty report, invented assessment, pre-populated score, or fake historical
report is created to make the framework appear operational. Corrections are
always new reports.
