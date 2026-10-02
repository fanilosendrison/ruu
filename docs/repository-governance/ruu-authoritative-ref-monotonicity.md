---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Authoritative Ref Monotonicity binding"
authoritative_ref_monotonicity:
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

The routed Governance Binding Registry owns the exact proto-ring Authoritative
Ref Monotonicity contract identity.

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
