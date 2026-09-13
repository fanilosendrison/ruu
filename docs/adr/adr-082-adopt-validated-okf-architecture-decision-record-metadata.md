---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Adopt validated OKF Architecture Decision Record metadata"
id: "ADR-082"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "e403c6a5e83e60e22e80485466e7204705277e21e3da9c968e6c9c6765bbf8bb"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Architecture Decision Record metadata, lifecycle, integrity, and generated projections"
  - "Semantics-preserving migration of active Ruu Architecture Decision Records"
  - "Repository-local validation of the adopted OKF ADR profile"
---

# ADR-082 — Adopt validated OKF Architecture Decision Record metadata

## Context

Ruu's active Architecture Decision Records span several historical Markdown
header styles. They contain stable identities and rich decision history, but
most predate a machine-readable repository contract for lifecycle state,
decision dates, outgoing relationships, governed scope, and decision-body
integrity. ADR-081 introduced partial OKF frontmatter, but it does not yet
conform to a complete shared ADR schema.

Accepted Ruu ADRs are immutable decision records. A repository-wide metadata
migration must therefore be explicitly authorized, mechanically prove that the
existing H1-to-EOF payload of every active ADR remains unchanged, and remain
strictly outside immutable qualification snapshots and byte-identical retained
projections.

The generalized OKF Architecture Decision Record profile provides a shared
metadata vocabulary and schema. Ruu needs a pinned, independently validatable
adoption that preserves repository-specific H1 history, qualification rules,
active-manifest generation, and the distinction between annotated history and
generated projections.

## Decision

Ruu adopts version `0.1.0` of the generalized OKF Architecture Decision Record
profile through:

1. a byte-identical vendored canonical JSON Schema;
2. provenance metadata containing its source repository, path, commit, `$id`,
   and SHA-256 digest;
3. a hash-pinned Ruu overlay for domain and three-digit identity constraints;
   and
4. repository-owned validation, rendering, regression tests, and CI checks.

Canonical ADR metadata lives in YAML frontmatter. The stable `id` determines
numeric order and validates the filename and H1 identity. Existing colon and em
dash H1 separators remain valid for migrated records; new records use the em
dash form. Every allocated identity MUST remain retained and MUST NOT be reused.

The validator rejects calendar-invalid dates and decision dates later than the
validation day. It permits `date: null` only for the exact legacy records whose
accepted dates are not present in the authored decision: ADR-049, ADR-050, and
ADR-055. Git creation dates MUST NOT be substituted silently for missing
decision dates.

Only outgoing `clarifies`, `amends`, `supersedes`, and `confirms` relationships
are stored. Incoming relationships are generated from those assertions. A
migrated record uses `relation_completeness: legacy-partial` unless a complete
semantic audit has established that every explicitly asserted outgoing
relationship is represented. Unambiguous legacy header relations MAY be copied
without reinterpreting combined labels such as `Amends/clarifies` or
`Clarifies/Amends`.

For accepted ADRs, the following are immutable:

- identity, name, and decision date;
- outgoing relationships and governed scope; and
- exact decision-body bytes beginning at the first `## Context` heading.

Lifecycle status may change only through a transition declared in the repository
profile. A later metadata/schema migration or relation normalization requires a
later governance decision and equivalent preservation evidence.

This decision authorizes one semantics-neutral migration of active
`docs/adr/adr-001-*.md` through `adr-081-*.md`. The migration MAY prepend or
replace frontmatter but MUST preserve each committed baseline payload from its
H1 through EOF byte-for-byte. In particular, ADR-081's existing partial
frontmatter MAY be replaced, while its corrected H1, historical metadata, and
decision content remain unchanged.

The migration MUST:

- record baseline-file, baseline-payload, migrated-payload, and before/after
  decision-body SHA-256 digests against the committed pre-migration baseline;
- keep ambiguous historical relationship wording in the retained Markdown
  payload rather than resolving it implicitly;
- clear the temporary unstructured-record allowlist;
- enable a generated `docs/adr/index.md` projection; and
- regenerate the active qualification manifest.

The generated index projects canonical frontmatter and derives incoming
relationships. `docs/adr/README.md` remains the manually maintained annotated
decision history and repository guide. Neither projection creates product
semantics.

The migration applies only to active ADRs under `docs/adr/`. It MUST NOT edit,
rename, reformat, make writable, or regenerate any file in
`qualification/releases/adr-080-flat/`, any snapshot-backed retained artifact,
or any historical byte-identical projection. Those artifacts remain governed
by their existing qualification and lineage contracts.

This decision changes ADR representation and repository governance only. It
does not change Ruu product semantics, the specification authority order,
qualification claims, or implementation architecture.

## Rationale

A pinned shared schema avoids incompatible repository-specific ADR formats.
Ruu's overlay and validator preserve local authority and fail closed without
making a modified schema appear canonical. Exact Git-bound payload evidence
protects accepted history during migration, including legacy metadata before
`## Context`.

Using `legacy-partial` avoids falsely claiming that heterogeneous historical
relationship prose has already been normalized completely. Separating the
generated graph from the annotated history preserves nuance while removing
incoming-relation dual writes from future ADRs.

## Consequences

- New active Ruu ADRs must validate as OKF `KnowledgeAsset` records under both
  the pinned base schema and Ruu overlay.
- ADR-001 through ADR-081 may receive canonical frontmatter only under the exact
  preservation boundary in this decision.
- ADR-049, ADR-050, and ADR-055 retain explicitly unknown dates rather than
  inferred Git timestamps.
- Historical relation projections remain intentionally incomplete while any
  record is `legacy-partial`.
- The active qualification manifest includes every metadata, tooling, ADR, and
  generated-index change.
- A later profile upgrade or historical relation normalization requires a later
  ADR and new migration evidence.

## Alternatives considered

### Keep heterogeneous Markdown headers as the only metadata

Rejected. They cannot enforce provenance, lifecycle vocabulary, body integrity,
relation direction, or generated-projection freshness mechanically.

### Treat MADR or Log4brains as Ruu's format authority

Rejected. Their conventions are useful inputs, but Ruu requires an OKF-governed,
repository-enforced profile with explicit local authority and qualification
boundaries.

### Infer all historical relations during the mechanical migration

Rejected. Combined labels, partial supersession, retained cores, and nuanced
status prose require semantic review. A representation migration must not make
those decisions implicitly.

### Infer missing dates from Git history

Rejected. File-creation timestamps are evidence about repository history, not
automatically authored decision dates.

### Regenerate snapshot or retained projections with canonical frontmatter

Rejected. Their byte identity is part of the qualification contract. Active ADR
formatting cannot override immutable evidence boundaries.

## Verification obligation

The repository must demonstrate that:

1. canonical and local schemas match their pinned identities and digests;
2. both schemas validate every structured active ADR with calendar-aware and
   non-future date checks;
3. IDs are unique and contiguous, filenames and H1 identities agree, and all
   structured relation targets exist without self-reference;
4. unstructured and null-date exceptions are exact, fixed, and reject stale
   entries;
5. migration evidence reads the committed baseline through Git and proves exact
   H1-to-EOF and `## Context`-to-EOF preservation for ADR-001 through ADR-081;
6. ADR-082 appears in the generated index but not in migration evidence;
7. immutable snapshot and retained projection digests remain unchanged;
8. the active qualification manifest is current; and
9. the complete repository qualification suite passes.
