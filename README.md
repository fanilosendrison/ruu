---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "readme"
domain: "ruu"
severity: "guideline"
name: "Ruu"
---

# Ruu

Ruu is Git-based version control designed for concurrent agentic software development.

This repository currently contains the active architecture corpus and its qualification evidence; it does not yet contain a production implementation.

The accepted architecture defines capability-based cognitive execution
without mandating Turnlock or any workflow engine. Ruu Core retains
exact-state convergence and recovery authority; Turnlock and native
harness facilities are potential execution realizations
([ADR-092](docs/adr/adr-092-allow-capability-based-cognitive-execution-without-mandatory-workflow-runtime.md)).
For authored checkpoint messages the associated continuing main agent
is the default when reachable; users may choose an independent agent,
raw LLM, or any compatible external service
([ADR-093](docs/adr/adr-093-make-commit-message-providers-user-selectable-with-main-agent-default.md)).
These are specification commitments, not shipped implementation claims.

The non-normative [Ruu Product Rationale](docs/product/ruu-product-rationale.md)
explains the user problem, intended value, pain removed, continuous-convergence
value, and capabilities that motivate the existing Product Intent. It creates
no Ruu product semantics and is not an independent input to normative
derivation.

Repository structure, architectural authority, contribution rules, and mandatory validation are defined in [AGENTS.md](AGENTS.md). The [annotated ADR history](docs/adr/README.md) explains accepted decisions, the [generated ADR index](docs/adr/index.md) projects canonical metadata, and the [ADR metadata profile](docs/adr/adr-profile.yaml) pins their machine-readable representation and validation contract. The [Governance Binding Registry](docs/repository-governance/ruu-governance-bindings.md) binds Ruu to exact generic proto-ring contracts, while the [Evidence Requirements Registry](docs/repository-governance/ruu-evidence-requirements.md) declares persistent post-baseline evidence mappings. Ruu-specific authority remains local.
