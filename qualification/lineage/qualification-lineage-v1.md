# Qualification Lineage — Ruu through ADR-080

- **Date:** 2026-09-09
- **Status:** RESTORED / RENAME-MIGRATED / VERIFIED
- **Nature:** package qualification/provenance maintenance; **not** a new architectural decision and therefore not ADR-081

## Purpose

This package retains the complete qualification lineage through ADR-080 while applying the project-wide rename to **Ruu**.

Before the rename, a packaging continuity regression had already been repaired: historical executable/result pairs for state-space audits v2–v37 and older Git smoke suites were restored from previously verified source packages, and v38/intermediate smokes were restored from the ADR-073 line.

The rename requirement is stricter than ordinary provenance preservation: the former product-name token must not remain anywhere in packaged filenames or textual artifacts. Therefore historical qualification files that contained that token were mechanically rewritten as part of the rename migration and are no longer byte-identical to the pre-rename source packages.

## Rename migration rule

The migration changes naming only:

```text
product display name → Ruu
CLI spelling         → ruu
primary spec         → RUU-SPEC.md
requirements alias   → ruu-requirements-v1-merge-policy.md
matching ADR slugs   → ...-ruu...
```

All internal links and static audit assertions that referenced renamed paths/names are migrated consistently. No architectural state, invariant, identity, policy rule, or transition semantics are intentionally changed by this rename.

The pre-rename package remains externally identifiable by its SHA-256 provenance anchor:

```text
9bb847bd1dc7c5e005f3d8da183c1484d11278539e4d70add5f1bf1b3c36772b
```

That source hash is retained so an auditor can distinguish **rename transformation** from architectural mutation without embedding the former product-name token in the Ruu package.

## State-space lineage

The package contains a contiguous qualification chain:

```text
v2 .. v45
  report      STATE-SPACE-AUDIT-vN.md
  executable  state-space-audit-vN.py
  output      state-space-audit-vN.txt
              (v38 retains its historical uppercase output filename)
```

`QUALIFICATION-LINEAGE.json` contains the current SHA-256 of every retained report, executable and recorded output after the rename migration.

Historical scripts retain their historical architectural assertions. Some old scripts are package-snapshot checks and therefore are replayed in their historical package context rather than being rewritten to pretend they were designed for ADR-080.

## Git-smoke lineage

Retained suites include the historical checkpoint/materialization/restack/provider/bootstrap smokes, the intermediate reference-transaction/run-lock smokes, and current native/remote observation smokes.

## Anti-disappearance rule

> Once a qualification artefact is admitted to `QUALIFICATION-LINEAGE.json`, it may not silently disappear or silently change bytes in a later package.

A future physical removal requires an explicit archival transition containing at least:

```text
status = ARCHIVED
content SHA-256
durable archive location
reason / supersession record
```

Supersession alone does not authorize deletion of historical evidence.

`verify-qualification-lineage.py` enforces:

- contiguous state-space versions v2..v45;
- existence and exact SHA-256 of every report/executable/recorded output;
- existence and exact SHA-256 of every retained smoke script/result;
- no unregistered state-space/smoke qualification artefact in the package.

## Replay versus recorded output

Historical `.txt` files remain recorded qualification outputs, now rename-migrated where necessary. Replays must not overwrite them. Current-environment replay results remain separate in `QUALIFICATION-REPLAY-ADR080.txt`.
