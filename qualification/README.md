---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu-qualification"
severity: "strict"
name: "Ruu qualification evidence"
---

# Ruu qualification evidence

This directory separates organized active evidence from the immutable source package that established the ADR-080 qualification baseline.

## Authority boundary

- `releases/adr-080-flat/` is an immutable, self-contained copy of the original flat package.
- `state-space/` and `git-smoke/` organize byte-identical retained evidence for active discovery.
- `lineage/lineage-v2.json` maps every retained artifact from its original path to its current path.
- `manifests/current.sha256` authenticates the active layout and excludes immutable releases.
- `manifests/adr-080-flat.sha256` preserves the original manifest bytes for reference. It is evaluated from the release snapshot root, not from the manifests directory.

The active evidence duplicates retained files from the snapshot intentionally. The verifier requires both copies to match the admitted SHA-256 value. Organized historical executables are retained for discovery, not as standalone working-directory layouts; replay commands use the immutable package or an exact external baseline.

## Historical replay boundary

The ADR-070 and ADR-073 source packages are not present locally. State-space audits v3 through v37 contain package-context assertions and cannot be honestly replayed without the exact corresponding source package.

The replay tool therefore uses explicit non-success states:

```text
NON_REPLAYABLE_MISSING_BASELINE
BASELINE_HASH_MISMATCH
BASELINE_EXTRACTION_FAILED
```

None of these states is reported as `PASS`.

Current-snapshot-compatible audits can be replayed directly:

```bash
python3 tools/replay-historical-qualification.py 45
```

Git smoke replay requires Git 2.28.0 or newer. The runner reports an unsupported environment before executing any suite when that prerequisite is not met:

```bash
python3 tools/replay-git-smokes.py
```

A snapshot-scoped historical audit requires its exact admitted archive:

```bash
python3 tools/replay-historical-qualification.py 37 \
  --baseline-archive <verified-source-package>
```

## Verification workflow

Regenerate the path-aware lineage and active manifest:

```bash
python3 tools/generate-qualification-lineage.py
python3 tools/generate-current-manifest.py
```

Then run:

```bash
python3 tools/verify-qualification-layout.py
```

The verifier checks:

- the legacy lineage inside the immutable snapshot;
- all 282 entries in the original flat manifest;
- contiguous state-space evidence from v2 through v45;
- every active artifact against its snapshot SHA-256;
- exhaustive recursive discovery outside `qualification/releases/`;
- the active-layout manifest.

Recorded outputs are evidence and must never be overwritten by a replay.
