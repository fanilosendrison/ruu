---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Isolate concurrent work production with Git worktrees"
id: "ADR-001"
status: "accepted"
date: "2026-09-04"
decision_body_sha256: "d486d1c2d98021df27a80ddce8dfa906e4d86a7c7a680b9cd56cd662e9e35734"
relation_completeness: "legacy-partial"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-001: Isolate concurrent work production with Git worktrees

- **Status:** Accepted — terminology clarified by ADR-034; bounded contribution-unit lifecycle clarified by ADR-035
- **Date:** 2026-09-04
- **Decision order:** 001

## Context

The system must allow several external producers, including agents from different Pi sessions, to work in the same repository and even on the same logical file concurrently. If they share one physical checkout, filesystem writes race before Git can detect or reconcile anything. Git refs alone do not isolate the files being mutated.

## Decision

Every concurrently mutable repository-local **contribution unit** gets a physically isolated Git worktree.

Concurrent changes to the same logical path are allowed only because they occur in distinct worktrees. Reconciliation happens later through Git history/merge semantics rather than through concurrent writes to one checkout.

## Rationale

This moves concurrency from an unsafe shared-filesystem problem into Git's explicit history/reconciliation model. It also makes dirty state, conflicts, exact Git state, recovery, and mutation authority observable per repository-local contribution unit.

## Consequences

- Two concurrently mutable contribution units never write the same physical worktree.
- Same-file concurrent work is supported.
- Each worktree has its own checkout/index/dirty state.
- Reconciliation happens after isolated work rather than during file writes.
- Worktree lifecycle becomes orchestration state that must be registered and cleaned safely.

## Alternatives considered

- **One shared checkout for all agents/processes:** rejected because Git cannot prevent filesystem-level overwrite races.
- **Separate refs without separate worktrees:** rejected because refs do not physically isolate simultaneous edits.
- **Serialize all work:** rejected because it defeats the required concurrency.
