---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "governance-authority-profile"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Governance Authority profile"

governance_authority_contract:
  repository: "fanilosendrison/proto-ring"
  commit: "22965fb97be23d7b43b8517b6786d65f5b8a41db"
  path: "docs/contracts/governance-authority.md"

governance_authority:
  model_version: 1
  sources:
    ruu_spec:
      repository_target: "docs/specification/ruu-spec.md"
    external_control_plane_contract:
      repository_target: "docs/specification/external-control-plane-contract.md"
    accepted_adrs:
      repository_target: "docs/adr"
    canonical_adr_records:
      repository_target: "docs/adr"
    adr_profile:
      repository_target: "docs/adr/adr-profile.yaml"
    adr_index:
      repository_target: "docs/adr/index.md"
    adr_history:
      repository_target: "docs/adr/README.md"
    architecture_overview:
      repository_target: "docs/architecture/overview.md"
    problem_statement:
      repository_target: "docs/architecture/problem-statement.md"
    historical_design_material: {}
    qualification_policy_document:
      repository_target: "qualification/README.md"
    immutable_adr080_snapshot:
      repository_target: "qualification/releases/adr-080-flat"
    retained_lineage:
      repository_target: "qualification/lineage/lineage-v2.json"
    retained_qualification_evidence: {}
    post_baseline_qualification_evidence:
      repository_target: "qualification/state-space/post-baseline"
    active_repository_manifest:
      repository_target: "qualification/manifests/current.sha256"
    shared_governance_provider_binding:
      repository_target: "docs/repository-governance/ruu-shared-governance-provider.md"
    discovery_classification_profile:
      repository_target: "docs/repository-governance/ruu-discovery-classification.md"
    agents_governance_frontmatter:
      repository_target: "AGENTS.md"
    agents_directives:
      repository_target: "AGENTS.md"
    repository_validation_entrypoint:
      repository_target: "tools/check-repository-integrity.py"
    qualification_ci:
      repository_target: ".github/workflows/qualification.yml"
    repository_git_tree: {}
    github_engineering_work_state: {}
  responsibilities:
    product_semantics:
      roles:
        ruu_spec: authority
        external_control_plane_contract: authority
        accepted_adrs: authority
        architecture_overview: non_authoritative
        problem_statement: non_authoritative
        historical_design_material: non_authoritative
      precedence:
        - higher_source: ruu_spec
          lower_source: external_control_plane_contract
        - higher_source: external_control_plane_contract
          lower_source: accepted_adrs
    external_control_plane_authority_boundary:
      roles:
        external_control_plane_contract: authority
      precedence: []
    accepted_decisions:
      roles:
        accepted_adrs: authority
      precedence: []
    adr_metadata:
      roles:
        canonical_adr_records: authority
        adr_index: secondary_representation
        adr_history: secondary_representation
      precedence: []
    adr_history_narrative:
      roles:
        adr_history: authority
      precedence: []
    adr_representation_rules:
      roles:
        adr_profile: authority
      precedence: []
    repository_artifact_state:
      roles:
        repository_git_tree: authority
        active_repository_manifest: secondary_representation
      precedence: []
    retained_historical_snapshot:
      roles:
        immutable_adr080_snapshot: authority
        retained_lineage: secondary_representation
        retained_qualification_evidence: secondary_representation
      precedence: []
    qualification_execution_evidence:
      roles:
        retained_qualification_evidence: authority
        post_baseline_qualification_evidence: authority
      precedence: []
    post_baseline_qualification_registration:
      roles:
        post_baseline_qualification_evidence: authority
      precedence: []
    qualification_policy:
      roles:
        agents_directives: authority
        qualification_policy_document: authority
      precedence: []
    shared_governance_provider_adoption:
      roles:
        accepted_adrs: authority
        shared_governance_provider_binding: secondary_representation
      precedence: []
    adr_profile_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    shared_governance_provider_binding_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    governed_objects_profile_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    repository_agent_guardrails:
      roles:
        agents_directives: authority
      precedence: []
    repository_validation_membership_order:
      roles:
        repository_validation_entrypoint: authority
      precedence: []
    repository_ci_bootstrap:
      roles:
        qualification_ci: authority
      precedence: []
    engineering_work_state:
      roles:
        github_engineering_work_state: authority
      precedence: []
    discovery_classification_binding:
      roles:
        discovery_classification_profile: authority
      precedence: []
    historical_design_record:
      roles:
        historical_design_material: authority
      precedence: []
---

# Ruu Governance Authority profile

This profile is the canonical machine-readable mapping of Ruu governance
authority roles. Underlying Ruu semantic authority remains in the sources
identified here. The immutable proto-ring contract pin governs only the generic
representation. Body prose does not replace the structured mapping.
