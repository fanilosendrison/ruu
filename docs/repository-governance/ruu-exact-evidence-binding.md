---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Exact Evidence Binding"
exact_evidence_binding:
  contract:
    repository: "fanilosendrison/proto-ring"
    commit: "3bddcd4b49147f022466fdeb4acbf590e68890ce"
    path: "docs/contracts/exact-evidence-binding.md"
---

# Ruu Exact Evidence Binding

## Shared contract

Apply the proto-ring Exact Evidence Binding contract at this immutable identity:

```text
fanilosendrison/proto-ring
3bddcd4b49147f022466fdeb4acbf590e68890ce
docs/contracts/exact-evidence-binding.md
```

Mutable proto-ring state is not authority for this binding.

## Ruu authority remains local

Retain Ruu authority for:

```text
exact state identity construction
SHA-256 construction
qualification artifact roles
qualification metadata
snapshot layout
lineage
manifests
post-baseline registration
replay rules
expected result semantics
recorded outputs
provider/Git semantics
product semantics
qualification truth
```

Exact Evidence Binding consumes Ruu-owned identity tokens. It does not construct
those identities or become their owner.

Exact Evidence Binding does not resurrect
`DevelopmentValidationEvidence`
or
`DevelopmentValidationDemand`.

## Post-baseline artifact mapping

Limit the current repository-level executable adoption to exact binding in
post-baseline qualification registration.

Map each registered artifact as follows:

```text
evidence class
=
Ruu-owned artifact role

required subject token
=
ASCII bytes of the Ruu-owned expected SHA-256

observed evidence subject token
=
ASCII bytes of the Ruu-owned actual SHA-256

context_required
=
false
```

Ruu continues to construct the actual SHA-256 from the artifact bytes and owns
all metadata, path-safety, role, file-presence, symlink, and registration rules.

## Replay metadata mapping

Map replay output registration as follows:

```text
evidence class
=
"recorded_output"

required subject token
=
ASCII bytes of replay.stdout_sha256

observed subject token
=
ASCII bytes of the registered recorded-output SHA-256
```

Replay execution remains a separate Ruu-owned operation.

## Binding boundary

`MATCH` means only exact binding.

It does not mean the qualification passes.

In particular:

```text
MATCH != evidence success
MATCH != proof validity
MATCH != claim truth
MATCH != obligation satisfaction
```

Ruu retains its existing diagnostics for any non-`MATCH` binding result. Runtime
exit-code comparison, byte-for-byte stdout comparison, and replay `PASS` or
`FAIL` remain Ruu-owned replay semantics.
