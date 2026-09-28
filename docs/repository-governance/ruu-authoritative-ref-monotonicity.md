---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Authoritative Ref Monotonicity binding"
authoritative_ref_monotonicity:
  contract:
    repository: "fanilosendrison/proto-ring"
    commit: "650a481b7dfa7c4d3671bd053c63642a5dab1087"
    path: "docs/contracts/authoritative-ref-monotonicity.md"
  repository:
    provider: "github"
    owner: "fanilosendrison"
    name: "ruu"
  authoritative_ref: "refs/heads/main"
  protection:
    mechanism: "github-repository-ruleset"
    ruleset_id: 24106347
---

# Ruu Authoritative Ref Monotonicity binding

## Shared contract

Apply the proto-ring Authoritative Ref Monotonicity contract at this immutable
identity:

```text
fanilosendrison/proto-ring
650a481b7dfa7c4d3671bd053c63642a5dab1087
docs/contracts/authoritative-ref-monotonicity.md
```

## Local realization

Ruu uses these local coordinates:

```text
provider: GitHub
repository: fanilosendrison/ruu
authoritative ref: refs/heads/main
protection mechanism: repository ruleset
ruleset ID: 24106347
```

These are consumer-local external-system binding coordinates; they do not
redefine the shared contract.

## Required provider behavior

For an ordinary writer, the provider rejects:

- a non-fast-forward update of the authoritative ref; and
- deletion of the authoritative ref.

## Authority boundary

Ruu product semantics remain local. Qualification policy and evidence remain
local. Retained snapshots remain local. Administrator honesty remains outside
this contract. Authoritative State Admission remains separate.
