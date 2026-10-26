---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "ruu"
severity: "strict"
name: "Adopt native proto-ring compatibility execution boundary"
id: "ADR-094"
status: "accepted"
date: "2026-10-20"
decision_body_sha256: "f15472618b1bd6bba0764eb974e0194e136c34b690a69804b51620379af1fd76"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-091"
  supersedes: []
  confirms:
    - "ADR-083"
    - "ADR-085"
governs:
  - "Native proto-ring executable-provider execution boundary"
  - "Authority for the exact executable proto-ring provider identity"
  - "Managed realization of the immutable proto-ring compatibility executable"
  - "Removal of Python proto-ring from active Ruu validation execution"
  - "Preservation of Ruu qualification, replay, evidence, and historical authority"
---

# ADR-094 — Adopt native proto-ring compatibility execution boundary

## Context

ADR-083 permits reusable governance implementation to be external without
transferring Ruu authority. ADR-085 makes the applicable immutably bound
proto-ring mechanism mandatory for generic repository governance. ADR-091
adopts the structured Repository Governance Model v2 substrate and currently
makes `requirements.txt` the authority for Ruu's executable proto-ring
provider identity.

Proto-Ring Issue #72 independently confronted Ruu's complete current governance
and qualification surface against the Rust reference engine. The final Phase-1
requalification at Ruu
`5d04c58170b2ce3f0e47aa0554a97906d2256492` and Proto-Ring
`4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f` established exact parity for the
complete seven-component RepositoryGovernanceState projection, all eight RGM
routes, all 93 governed ADR objects, all 25 Repository Integrity validations,
the two post-baseline Evidence Requirements, live Exact Evidence Binding calls,
generic ADR operations, Repository Integrity evaluation, historical replay,
post-baseline replay, and all retained Git-smoke suites.

That confrontation is qualification evidence for this repository-governance
decision. It does not create Ruu product semantics.

The Python distribution is therefore no longer required as Ruu's active
execution mechanism for generic Proto-Ring governance. Retaining
`requirements.txt`, pip installation provenance, and PEP-610 metadata as the
authority for the executable provider would preserve an implementation-specific
authority surface after the executable boundary has moved to the native
compatibility process.

This decision changes repository-governance execution only. It does not change
Ruu product semantics, external-control-plane semantics, qualification claims,
retained history, replay semantics, or evidence interpretation.

## Decision

### Native compatibility executable

Ruu SHALL execute applicable generic Proto-Ring governance through the exact
native `proto-ring-compat` executable built from:

`fanilosendrison/proto-ring`
`4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f`

using compatibility transport version `1`.

Ruu SHALL NOT consume Proto-Ring through a Rust crate dependency.

Ruu SHALL NOT commit Proto-Ring source or executable bytes into this repository.

The compatibility transport remains a migration/local execution boundary. It
does not become Ruu semantic authority.

### Executable-provider authority

ADR-091 section 3 is amended.

`requirements.txt` no longer owns the exact executable Proto-Ring identity.

The routed Ruu Governance Binding Registry becomes the sole repository
authority for the active `proto_ring_executable` identity.

The effective native realization remains a secondary representation that must
be proven current against that binding.

`requirements.txt` remains an ordinary Python dependency manifest for Ruu-owned
Python tooling. It no longer contains or represents the Proto-Ring executable
provider.

Pip installation metadata and PEP-610 provenance no longer participate in the
active executable-provider authority chain.

### Managed immutable realization

The exact provider source SHALL be realized outside the Ruu repository from the
immutable Git identity declared in the Governance Binding Registry.

Provider preparation SHALL:

- obtain the exact bound repository and commit;
- use a detached exact source checkout;
- reject dirty, untracked, ignored, wrong-origin, or wrong-HEAD source state;
- build `proto-ring-compat` with `cargo build --release --locked -p proto-ring-compat`;
- use the provider's own pinned Rust toolchain declaration;
- record a canonical realization manifest including exact provider identity and
  executable SHA-256;
- verify `engine.identity` against the authoritative binding.

Provider source, build output, and realization metadata remain non-authoritative
external cache state.

Repository validation SHALL fail closed when the exact provider realization is
missing or invalid.

Repository Integrity SHALL NOT clone, fetch, prepare, or build the provider
implicitly.

Provider preparation is an explicit bootstrap step before governed validation.

### Ruu authority remains local

This cutover does not transfer authority for:

- Ruu product or specification semantics;
- the external-control-plane contract;
- accepted ADR meaning;
- qualification policy or qualification PASS/FAIL;
- qualification artifact schemas, roles, registration, or membership;
- SHA-256 construction;
- the ADR-080 immutable snapshot;
- retained lineage or retained qualification evidence;
- post-baseline qualification evidence;
- historical replay semantics or outcomes;
- post-baseline replay semantics or outcomes;
- Git-smoke semantics or Git-version requirements;
- exact replay stdout comparison;
- generated Ruu artifacts or the active repository manifest;
- repository-specific validation policy.

Repository Governance State composition remains read-only and non-executing.

Repository Integrity remains current-state validation only.

The mandatory qualification sequence remains:

Repository Integrity
→ retained historical replay
→ post-baseline replay
→ Git-smoke replay.

### Post-baseline Exact Evidence Binding

Ruu continues to construct SHA-256 values locally.

For post-baseline evidence identity comparison, Ruu continues to treat the
64-character lowercase SHA-256 text as the subject identity bytes exactly as
before this cutover.

The native compatibility request therefore transports those existing identity
bytes as hexadecimal transport for:

`sha_text.encode("ascii")`

and does not reinterpret the textual SHA as the 32 raw digest bytes.

Proto-Ring owns the generic requirement/binding comparison mechanism only.

Ruu continues to own evidence class selection, artifact roles, metadata schema,
registration, replay execution, expected exit code, exact stdout comparison,
and qualification verdict.

### Repository Integrity membership and order

The existing 25 Repository Integrity validation IDs and their exact order remain
unchanged.

The `accepted_adr_body_immutability` validation keeps its existing identity and
position but executes through a Ruu-local wrapper over the native compatibility
operation instead of `python -m proto_ring.accepted_adr_body`.

No historical replay, post-baseline replay, or Git-smoke replay is moved into
Repository Integrity.

### Qualification and CI

Ruu CI SHALL prepare and verify the exact native provider before Repository
Integrity.

After provider preparation, the existing sequence of Git-version checking,
Repository Integrity, retained historical replay, post-baseline replay,
Git-smoke replay, and whitespace checking remains mandatory.

No mutable provider branch is consulted as execution authority.

## Consequences

- Active Ruu validation no longer requires the Python `proto-ring`
  distribution.
- The Governance Binding Registry becomes the single active authority for the
  executable provider identity.
- The native provider remains explicitly reproducible from an immutable source
  identity.
- Ruu's product, qualification, replay, evidence, history, and repository-local
  policy remain local.
- Existing generic contract pins remain unchanged unless separately migrated.
- The 25-entry Repository Integrity membership/order remains unchanged.
- Immutable qualification artifacts are not rewritten by this migration.

## Verification obligation

This decision is satisfied only when:

1. the Governance Binding Registry identifies exactly
   `fanilosendrison/proto-ring@4ae1a2a549d7dae8e4cce7f727b9bc5330f3823f`
   as the executable provider authority;
2. no active maintained Python file imports the `proto_ring` package;
3. `requirements.txt` contains no Proto-Ring package declaration;
4. no Proto-Ring Rust crate dependency, provider source, or provider binary is
   committed in Ruu;
5. provider realization fails closed when absent, malformed, dirty, mismatched,
   or otherwise not exact;
6. `engine.identity` matches the authoritative binding;
7. the exact 25 Repository Integrity validation IDs and order remain unchanged;
8. post-baseline SHA construction and interpretation remain Ruu-owned;
9. retained historical artifacts and post-baseline evidence remain byte
   identical;
10. Repository Integrity passes through the native provider;
11. latest retained historical replay passes;
12. all post-baseline replay passes;
13. all retained Git-smoke replay passes;
14. a fresh environment with no importable Python `proto_ring` distribution can
    prepare the provider and pass the full qualification sequence; and
15. exact published-SHA CI and independent postpublication review pass.
