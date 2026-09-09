---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu"
severity: "strict"
name: "Ruu repository agent directives"
---

# Ruu repository directives

This file is the operational map for agents working in the Ruu repository. Follow these project-specific directives together with all applicable parent workspace instructions. Never duplicate, weaken, or override a parent safety or permission rule here.

## General guidelines

- Treat this repository as an architecture and qualification corpus. It does not yet contain a production implementation.
- Read the architecture overview and normative specifications before making an architectural or implementation decision.
- Preserve native Git semantics and the authority boundaries defined by the Ruu specification.
- Do not infer new product behavior from summaries, historical reports, or qualification scripts.
- Keep the repository root limited to system entry points and responsibility-based directories.
- Use lowercase kebab-case for new files and directories, except recognized system entry points such as `AGENTS.md` and `README.md`.

## Authority order

Use the following precedence when sources appear inconsistent:

1. `docs/specification/ruu-spec.md`
2. `docs/specification/external-control-plane-contract.md`
3. Accepted ADRs under `docs/adr/`, including later amendments
4. `docs/architecture/overview.md`
5. Design history, audits, reports, and recorded outputs

The architecture overview is non-normative. Qualification evidence demonstrates properties of a defined baseline but does not create product semantics.

Report every inconsistency between authoritative sources. Do not silently choose a convenient interpretation.

## Required reading

Before changing architecture or preparing implementation work, read:

1. `docs/architecture/overview.md`
2. `docs/specification/ruu-spec.md`
3. `docs/specification/external-control-plane-contract.md`
4. The ADRs governing the affected concepts

For the shortest current decision path, begin with ADR-070 and ADR-078, then read ADR-074 through ADR-080.

## Folder structure

```text
ruu/
├── AGENTS.md
├── README.md
├── docs/
│   ├── README.md
│   ├── architecture/
│   ├── specification/
│   ├── adr/
│   ├── design/
│   └── history/
├── qualification/
│   ├── README.md
│   ├── state-space/
│   ├── git-smoke/
│   ├── audits/
│   ├── package-verification/
│   ├── lineage/
│   ├── manifests/
│   └── releases/
└── tools/
```

## Documentation rules

### Active specifications

- Treat `docs/specification/` as the active normative source.
- Maintain exactly one active Ruu specification: `docs/specification/ruu-spec.md`.
- Do not recreate the historical `ruu-requirements-v1-merge-policy.md` alias as a second editable specification.
- Introduce a semantic architecture change through an explicit ADR and synchronize every affected normative document.
- Keep descriptive filenames and relative links aligned with the organized layout.

### Architectural decisions

- Keep ADRs chronological under `docs/adr/`.
- Do not reorganize accepted ADRs by topic; use indexes for topic-based navigation.
- Do not silently rewrite the semantics of an accepted ADR.
- Use a later ADR to amend or supersede an accepted decision.
- Permit non-semantic path or link maintenance only when the immutable source-package version remains preserved.

### Design and history

- Keep unresolved and closed design questions under `docs/design/`.
- Do not treat the design backlog or decision-integration log as normative when a specification or accepted ADR controls.
- Keep project-wide migration records under `docs/history/`.

## Qualification rules

### Immutable release snapshot

`qualification/releases/adr-080-flat/` is the immutable, self-contained baseline copied from the original flat package.

- Never edit, rename, reformat, delete, or make files writable inside this directory.
- Never regenerate a recorded output inside the snapshot.
- Verify the snapshot through its own legacy lineage and manifest.
- Preserve its historical filenames and flat layout even when they violate current naming conventions.

### Organized active evidence

- Treat `qualification/state-space/` and `qualification/git-smoke/` as organized, byte-identical projections of retained snapshot evidence.
- Do not edit retained audit executables, reports, smoke scripts, or recorded outputs directly.
- Keep each state-space version in its `vNNN/` directory.
- Keep Git smoke suites grouped by behavioral family.
- Use `qualification/lineage/lineage-v2.json` to map every `original_path` to its `current_path` and admitted SHA-256.
- Exclude `qualification/releases/` from active recursive discovery and the active manifest.

### Replay integrity

- Never report a historical replay as passing without the exact admitted source package.
- Treat missing ADR-070 or ADR-073 source packages as `NON_REPLAYABLE_MISSING_BASELINE`.
- Treat an unexpected package digest as `BASELINE_HASH_MISMATCH`.
- Never overwrite recorded `.txt` outputs with current replay output.
- Use `tools/replay-historical-qualification.py` rather than running an organized historical state-space executable from its new directory.

Git smoke replay requires Git 2.28.0 or newer. An older Git installation is an unsupported environment, not a passing or failing conformance result.

## Tool responsibilities

- `tools/generate-qualification-lineage.py` generates the path-aware active lineage from the immutable snapshot.
- `tools/generate-current-manifest.py` generates the SHA-256 manifest for the active layout.
- `tools/verify-qualification-layout.py` verifies the snapshot, active evidence, lineage, permissions, and manifests.
- `tools/verify-markdown-links.py` verifies maintained relative Markdown links.
- `tools/replay-historical-qualification.py` enforces exact-baseline state-space replay.
- `tools/replay-git-smokes.py` enforces the minimum Git version before smoke replay.

Do not duplicate these responsibilities in ad hoc scripts.

## Mandatory validation

After any intentional change, regenerate active metadata in this order:

```bash
python3 tools/generate-qualification-lineage.py
python3 tools/generate-current-manifest.py
```

Then run:

```bash
python3 tools/verify-qualification-layout.py
python3 tools/verify-markdown-links.py
```

When the installed Git version is supported, also run:

```bash
python3 tools/replay-git-smokes.py
```

Replay the current state-space checkpoint when qualification behavior or tooling changes:

```bash
python3 tools/replay-historical-qualification.py 45
```

Do not declare work complete when a change-caused validation failure remains unresolved.

## Quick navigation

- Product mental model: `docs/architecture/overview.md`
- Normative requirements and invariants: `docs/specification/ruu-spec.md`
- External authority boundary: `docs/specification/external-control-plane-contract.md`
- Architectural decision history: `docs/adr/README.md`
- Open and closed design questions: `docs/design/open-design-backlog.md`
- Qualification policy and replay limitations: `qualification/README.md`
- Immutable ADR-080 package: `qualification/releases/adr-080-flat/`

## Future implementation boundary

Do not create a speculative `src/`, `tests/`, package manifest, or language-specific module layout before the implementation language and module boundaries are explicitly decided. When implementation begins, use the standard layout and official tooling of the selected ecosystem rather than inventing a repository-specific build structure.
