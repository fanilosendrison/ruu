# Ruu — Project Rename Migration

- **Date:** 2026-09-09
- **Scope:** complete packaged corpus through ADR-080
- **Architectural effect:** none intended

The project is named **Ruu** and its CLI spelling is **`ruu`**.

This package applies the rename across:

- prose and headings;
- code blocks, comments, assertions, and recorded textual outputs;
- Markdown links and cross-references;
- filenames whose names contained the former project token;
- the primary specification and requirements alias;
- qualification lineage metadata and hashes;
- final ZIP/package naming.

The migration deliberately removes the former project-name token from the Ruu corpus rather than preserving it inside historical files. As a result, historical files that mentioned the former name are rename-migrated snapshots, not byte-identical copies of their pre-rename versions. Their current SHA-256 values are recorded in `QUALIFICATION-LINEAGE.json`.

No Git terminology is removed: **Git remains the native object/history substrate and interoperability boundary**. Only the project/product/CLI name changes.

The normative architecture remains through **ADR-080**. This rename does not create ADR-081 because it does not intentionally change architectural semantics.
