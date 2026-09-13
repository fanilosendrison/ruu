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
- Read the problem statement, architecture overview, and normative specifications before making an architectural or implementation decision.
- Preserve native Git semantics and the authority boundaries defined by the Ruu specification.
- Do not infer new product behavior from summaries, historical reports, or qualification scripts.
- Keep the repository root limited to system entry points and responsibility-based directories.
- Use lowercase kebab-case for new files and directories, except recognized system entry points such as `AGENTS.md` and `README.md`.
- When the user mentions an Issue, Project work, backlog work, or a review finding, apply the shared GitHub Engineering Projects operational protocol, then read `docs/repository-governance/ruu-engineering.md` before acting.

## Authority order

Use the following precedence when sources appear inconsistent:

1. `docs/specification/ruu-spec.md`
2. `docs/specification/external-control-plane-contract.md`
3. Accepted ADRs under `docs/adr/`, including later amendments
4. `docs/architecture/overview.md`
5. `docs/architecture/problem-statement.md`
6. Design history, audits, reports, and recorded outputs

The architecture overview and problem statement are non-normative. They explain the system and its rationale but do not create product semantics. Qualification evidence demonstrates properties of a defined baseline but does not create product semantics. Generated ADR indexes and README files project or explain authoritative records; they do not create product semantics.

For records not present on the exact `legacy.unstructured` allowlist, ADR frontmatter is canonical for identity, lifecycle, explicitly recorded outgoing relations, governed scope, and body integrity. `docs/adr/adr-profile.yaml` and its schemas govern that representation and the temporary compatibility boundary; they do not outrank accepted decision bodies or the specification authority order.

Repository-governance documents, GitHub Issues, Project fields, comments, and Pull Requests are also non-normative work-management sources. They may identify required work but never override the authority order above.

Report every inconsistency between authoritative sources. Do not silently choose a convenient interpretation.

## Required reading

Before changing architecture or preparing implementation work, read:

1. `docs/architecture/problem-statement.md`
2. `docs/architecture/overview.md`
3. `docs/specification/ruu-spec.md`
4. `docs/specification/external-control-plane-contract.md`
5. The ADRs governing the affected concepts

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
│   ├── history/
│   └── repository-governance/
├── qualification/
│   ├── README.md
│   ├── state-space/
│   ├── git-smoke/
│   ├── audits/
│   ├── package-verification/
│   ├── lineage/
│   ├── manifests/
│   └── releases/
├── requirements.txt
└── tools/
    └── tests/
```

## Documentation rules

### Active specifications

- Treat `docs/specification/` as the active normative source.
- Maintain exactly one active Ruu specification: `docs/specification/ruu-spec.md`.
- Do not recreate the historical `ruu-requirements-v1-merge-policy.md` alias as a second editable specification.
- Introduce a semantic architecture change through an explicit ADR and synchronize every affected normative document.
- Keep descriptive filenames and relative links aligned with the organized layout.

### Architectural decisions

- Keep ADRs chronological under `docs/adr/` and follow the pinned contract in `docs/adr/adr-profile.yaml`.
- Do not reorganize accepted ADRs by topic; use indexes for topic-based navigation.
- Treat accepted ADR identity, name, date, outgoing relations, governed scope, and decision body as immutable.
- Use a later ADR to amend or supersede an accepted decision; derive incoming relations instead of editing old records.
- Permit a representation/schema migration only through a later governance ADR and machine-readable body-preservation evidence.
- Keep `docs/adr/README.md` as the maintained annotated history. Never hand-edit the required generated projection at `docs/adr/index.md`.
- Permit non-semantic path or link maintenance only when the immutable source-package version remains preserved.

### Design and history

- Keep Ruu design material under `docs/design/` and project-wide migration or retired design records under `docs/history/`.
- Treat `docs/history/design-backlog-through-adr-081.md` as a closed archive. Never append a finding, question, or work item to it.
- Do not treat design history or the decision-integration log as normative when a specification or accepted ADR controls.

### Repository governance and work tracking

- Apply the shared GitHub Engineering Projects operational protocol for generic Issue and Project operations; use `docs/repository-governance/ruu-engineering.md` only for the Ruu-specific profile.
- Keep repository process documentation under `docs/repository-governance/`, separate from Ruu product documentation.
- Use the private GitHub Project **Ruu Engineering** as the primary durable work tracker.
- Resolve an unqualified `Issue #N` as `fanilosendrison/ruu#N`, then retrieve the Issue and its live Project fields according to `docs/repository-governance/ruu-engineering.md`.
- Treat `Ready` items in the Project's `Agent Queue` as the normal autonomous pickup surface. A direct user request may select other work but cannot ratify proposed semantics or bypass unresolved dependencies.
- Create a `fanilosendrison/ruu` Issue for every validated review finding or other work item that must be deferred, handed off, scheduled, or tracked independently, then add and classify it in Ruu Engineering.
- Revalidate findings against current content, search for duplicates, and preserve exact provenance, authority boundaries, acceptance criteria, validation requirements, and controlling repository references.
- Never use an Issue, Project field, comment, or Pull Request as the only record of an accepted semantic decision. Synchronize the governing ADR and every affected normative document.

## Qualification rules

### Immutable release snapshot

`qualification/releases/adr-080-flat/` is the immutable, self-contained baseline copied from the original flat package.

- Never edit, rename, reformat, delete, or make files writable inside this directory.
- Never regenerate a recorded output inside the snapshot.
- Verify the snapshot through its own legacy lineage and manifest.
- Preserve its historical filenames and flat layout even when they violate current naming conventions.

### Retained and post-baseline evidence

- Treat direct `qualification/state-space/vNNN/` directories through the retained checkpoint and the existing `qualification/git-smoke/` families as byte-identical ADR-080 snapshot projections.
- Do not edit retained audit executables, reports, smoke scripts, or recorded outputs directly.
- Use `qualification/lineage/lineage-v2.json` only for snapshot-backed retained artifacts; never add post-baseline evidence to that lineage.
- Put every new state-space qualification under `qualification/state-space/post-baseline/vNNN/` with valid `qualification-metadata.json`.
- Keep state-space versions contiguous across the retained and post-baseline boundaries.
- Exclude `qualification/releases/` from active recursive discovery and the active manifest.

### Replay integrity

- Never report a historical replay as passing without the exact admitted source package.
- Treat missing ADR-070 or ADR-073 source packages as `NON_REPLAYABLE_MISSING_BASELINE`.
- Treat an unexpected package digest as `BASELINE_HASH_MISMATCH`.
- Never overwrite recorded `.txt` outputs with current replay output.
- Use `tools/replay-historical-qualification.py` rather than running an organized historical state-space executable from its new directory.

Git smoke replay requires Git 2.28.0 or newer. An older Git installation is an unsupported environment, not a passing or failing conformance result.

## Tool responsibilities

- `tools/adr-metadata.py` validates active ADR metadata and renders only the generated ADR index; it never rewrites source ADRs or qualification snapshots.
- `tools/generate-qualification-lineage.py` generates only the retained path-aware lineage from the immutable snapshot.
- `tools/generate-current-manifest.py` generates the SHA-256 manifest for the active layout.
- `tools/verify-qualification-layout.py` verifies the snapshot, retained evidence, post-baseline registrations, continuity, permissions, and manifests.
- `tools/verify-markdown-links.py` verifies maintained relative Markdown links.
- `tools/replay-historical-qualification.py` enforces exact-baseline retained state-space replay.
- `tools/replay-post-baseline-qualification.py` replays registered post-baseline state-space evidence and compares exact recorded output.
- `tools/replay-git-smokes.py` enforces the minimum Git version before smoke replay.

Do not duplicate these responsibilities in ad hoc scripts.

## Mandatory validation

Create an isolated Python 3 environment and install the pinned dependencies before validation:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

When ADR metadata changes and the profile requires the generated index, regenerate it first:

```bash
.venv/bin/python tools/adr-metadata.py render
```

After any intentional change, regenerate active metadata in this order:

```bash
python3 tools/generate-qualification-lineage.py
python3 tools/generate-current-manifest.py
```

Confirm that generation produced no uncommitted difference, then run:

```bash
git diff --exit-code
.venv/bin/python tools/tests/test-adr-metadata.py
.venv/bin/python tools/adr-metadata.py check
python3 tools/verify-qualification-layout.py
python3 tools/verify-markdown-links.py
python3 tools/tests/test-qualification-infrastructure.py
python3 tools/replay-historical-qualification.py latest
python3 tools/replay-post-baseline-qualification.py
python3 tools/replay-git-smokes.py
git diff --check
```

The Git smoke command must fail as unsupported when Git is older than 2.28.0. The GitHub Actions qualification workflow runs the same sequence. Do not declare work complete when a change-caused validation failure remains unresolved.

## Quick navigation

- Product problem and rationale: `docs/architecture/problem-statement.md`
- Product mental model: `docs/architecture/overview.md`
- Normative requirements and invariants: `docs/specification/ruu-spec.md`
- External authority boundary: `docs/specification/external-control-plane-contract.md`
- Annotated architectural decision history: `docs/adr/README.md`
- ADR metadata profile: `docs/adr/adr-profile.yaml`
- Generated ADR index: `docs/adr/index.md`
- ADR metadata migration evidence: `docs/adr/metadata-migration-evidence.yaml`
- ADR metadata validator and renderer: `tools/adr-metadata.py`
- Ruu Engineering Project profile: `docs/repository-governance/ruu-engineering.md`
- Retired design-backlog history: `docs/history/design-backlog-through-adr-081.md`
- Qualification policy and replay limitations: `qualification/README.md`
- Immutable ADR-080 package: `qualification/releases/adr-080-flat/`

## Future implementation boundary

Do not create a speculative `src/`, `tests/`, package manifest, or language-specific module layout before the implementation language and module boundaries are explicitly decided. When implementation begins, use the standard layout and official tooling of the selected ecosystem rather than inventing a repository-specific build structure.
