---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu-qualification"
severity: "strict"
name: "Ruu qualification evidence"
---

# Ruu qualification evidence

This directory keeps the immutable ADR-080 qualification baseline separate from qualifications created after that baseline.

## Provenance boundary

The repository contains two evidence classes.

### Retained historical evidence

- `releases/adr-080-flat/` is the immutable, self-contained ADR-080 package.
- Direct `state-space/v002/` through `state-space/v045/` directories are byte-identical retained projections.
- The existing `git-smoke/` family directories are byte-identical retained projections.
- `lineage/lineage-v2.json` maps every retained artifact from its flat snapshot path to its organized path and admitted SHA-256.
- Retained reports, executables, smoke scripts, and recorded outputs must not be edited or regenerated.

The retained paths remain unchanged to preserve existing links and lineage. They are not moved under a new `retained/` directory.

### Post-baseline evidence

State-space qualifications after ADR-080 use this separate path:

```text
state-space/post-baseline/vNNN/
├── qualification-metadata.json
├── state-space-audit-vN.md
├── state-space-audit-vN.py
└── state-space-audit-vN.txt
```

A post-baseline artifact never appears in `lineage/lineage-v2.json` and never claims an `original_path` in the ADR-080 snapshot. Its metadata must declare:

```text
provenance = POST_BASELINE
baseline = ADR-080
```

`state-space/post-baseline/qualification-metadata-v1.schema.json` defines the registration format. The Python verifier enforces the same closed contract without requiring a third-party JSON Schema runtime.

`manifests/current.sha256` authenticates every maintained repository file outside `releases/`, including retained projections, post-baseline registrations, tools, documentation, tests, and CI. The manifest excludes itself so one generation pass reaches a fixed point.

## Permanent verification invariants

`tools/verify-qualification-layout.py` verifies all of the following:

- the immutable snapshot's legacy lineage verifier;
- every snapshot manifest entry and the retained snapshot-manifest copy;
- non-writable snapshot files and directories;
- byte identity between each retained artifact, its snapshot source, and its lineage hash;
- retained paths that are derived exactly from flat snapshot paths;
- complete retained versions derived from the immutable snapshot lineage;
- strict exclusion of post-baseline paths from retained lineage;
- unique post-baseline identity and version;
- exact version agreement among directory, metadata, filenames, and report heading;
- one report, executable, and recorded output for every post-baseline qualification;
- executable permissions and SHA-256 for every registered artifact;
- exhaustive post-baseline discovery, including supporting artifacts;
- strict continuity across retained and post-baseline state-space versions;
- absence of collisions with retained history;
- complete active-manifest registration and content hashes.

The verifier does not infer validity from a recorded `PASS` string. Replay is a separate required operation.

## Historical replay

The ADR-070 and ADR-073 source packages are not present locally. Historical audits with package-context assertions cannot be honestly replayed without their exact admitted archive.

The historical replay tool therefore uses explicit non-success states:

```text
NON_REPLAYABLE_MISSING_BASELINE
BASELINE_HASH_MISMATCH
BASELINE_EXTRACTION_FAILED
```

None of these states is `PASS`. Before execution, the replay tool verifies the executable and recorded-output hashes against immutable lineage. It then requires exit code zero and byte-for-byte stdout equality with the recorded output.

Replay the latest retained checkpoint, derived from the immutable snapshot lineage:

```bash
python3 tools/replay-historical-qualification.py latest
```

Replay another snapshot-compatible retained version:

```bash
python3 tools/replay-historical-qualification.py 38
```

Replay a package-scoped historical audit only with its exact admitted archive:

```bash
python3 tools/replay-historical-qualification.py 37 \
  --baseline-archive <verified-source-package>
```

## Adding a post-baseline state-space qualification

The first post-baseline version is v46, covering ADR-081 exact authoring dependencies and an exact Git object-retention smoke. Every later version is the next integer after the highest registered version; gaps and retained collisions fail verification.

1. Create `state-space/post-baseline/vNNN/`.
2. Add `state-space-audit-vN.md`, `state-space-audit-vN.py`, and `state-space-audit-vN.txt`.
3. Make the Python source executable.
4. Add `qualification-metadata.json` using the local version 1 schema.
5. Register every additional fixture or source file under `supporting_artifacts`; unregistered files fail verification.
6. Record SHA-256 values after file contents are final.
7. Replay the new version before regenerating repository metadata.

During creation of a new, not-yet-registered version, its deterministic output may be captured with:

```bash
python3 qualification/state-space/post-baseline/v046/state-space-audit-v46.py \
  > qualification/state-space/post-baseline/v046/state-space-audit-v46.txt
chmod +x qualification/state-space/post-baseline/v046/state-space-audit-v46.py
shasum -a 256 qualification/state-space/post-baseline/v046/*
```

Do not use this command to overwrite retained or previously recorded evidence. A correction to an accepted qualification should normally be represented by the next version.

Replay the current post-baseline version:

```bash
python3 tools/replay-post-baseline-qualification.py 46
```

The v46 registration includes one supporting native Git smoke in the same version directory. The primary Python executable runs it, so recorded-output replay covers both the finite state families and the Git reachability assertion.

Replay all registered post-baseline versions:

```bash
python3 tools/replay-post-baseline-qualification.py
```

Replay succeeds only when the executable exits with the registered success code and its stdout bytes exactly equal the recorded output bytes. A repository with no post-baseline qualification reports a count of zero; it does not claim that a future qualification passed.

## Git smoke replay

Git smoke replay requires Git 2.28.0 or newer. An older or unidentifiable Git is an unsupported environment and exits nonzero before any suite runs.

```bash
python3 tools/replay-git-smokes.py --check-version
python3 tools/replay-git-smokes.py
```

The runner canonicalizes temporary-path output so retained path comparisons remain valid on systems where temporary directories have equivalent aliased paths.

## Local validation and CI

Run the same sequence used by GitHub Actions:

```bash
python3 tools/replay-git-smokes.py --check-version
python3 tools/generate-qualification-lineage.py
python3 tools/generate-current-manifest.py
git diff --exit-code
python3 tools/verify-qualification-layout.py
python3 tools/verify-markdown-links.py
python3 tools/tests/test-qualification-infrastructure.py
python3 tools/replay-historical-qualification.py latest
python3 tools/replay-post-baseline-qualification.py
python3 tools/replay-git-smokes.py
git diff --check
```

The GitHub Actions workflow runs on every push and pull request. It pins action revisions and the Python patch version, regenerates retained lineage before the active manifest, then rejects any tracked or untracked difference before running verification and replay. Generation therefore cannot hide stale committed metadata.
