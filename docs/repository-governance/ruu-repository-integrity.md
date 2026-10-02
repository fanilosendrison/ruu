---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "repository-integrity-profile"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Repository Integrity profile"

repository_integrity:
  model_version: 1
  authority:
    responsibility: repository_validation_membership_order
    source: repository_integrity_profile
  environments:
    - ruu_python
  continue_after_non_satisfied: true
  validations:
    maintained_python_syntax:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances:
        kind: repository_paths
        mode: append_all
        selectors:
          - {kind: glob, glob: "tools/*.py"}
          - {kind: glob, glob: "tools/qualification/*.py"}
          - {kind: glob, glob: "tools/tests/*.py"}
      command: {kind: command, environment: ruu_python, arguments: [-m, py_compile], undetermined_exit_codes: []}
    json_syntax:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances:
        kind: repository_paths
        mode: for_each
        selectors:
          - {kind: glob, glob: "docs/adr/schemas/*.json"}
          - {kind: path, path: "qualification/lineage/lineage-v2.schema.json"}
          - {kind: path, path: "qualification/state-space/post-baseline/qualification-metadata-v1.schema.json"}
      command: {kind: command, environment: ruu_python, arguments: [-m, json.tool], undetermined_exit_codes: []}
    adr_metadata_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-adr-metadata.py], undetermined_exit_codes: []}
    projection_integrity_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-projection-integrity.py], undetermined_exit_codes: []}
    exact_evidence_binding_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-exact-evidence-binding.py], undetermined_exit_codes: []}
    governed_objects_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-governed-objects.py], undetermined_exit_codes: []}
    historical_qualification_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-historical-qualification.py], undetermined_exit_codes: []}
    repository_integrity_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-repository-integrity.py], undetermined_exit_codes: []}
    qualification_infrastructure_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-qualification-infrastructure.py], undetermined_exit_codes: []}
    structured_governance_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-structured-governance.py], undetermined_exit_codes: []}
    proto_ring_binding_registry_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-proto-ring-binding-registry.py], undetermined_exit_codes: []}
    proto_ring_provider_tests:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/tests/test-proto-ring-provider.py], undetermined_exit_codes: []}
    adr_metadata_check:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/adr-metadata.py, check], undetermined_exit_codes: []}
    accepted_adr_body_immutability:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [-m, proto_ring.accepted_adr_body], undetermined_exit_codes: []}
    proto_ring_binding_registry_currentness:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-proto-ring-binding-registry.py], undetermined_exit_codes: []}
    proto_ring_provider_currentness:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-proto-ring-provider.py], undetermined_exit_codes: []}
    structured_governance_check:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-structured-governance.py], undetermined_exit_codes: []}
    governance_authority_check:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-governance-authority.py], undetermined_exit_codes: []}
    governed_objects_check:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-governed-objects.py], undetermined_exit_codes: []}
    authoritative_ref_monotonicity_effective_rules:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-authoritative-ref-monotonicity.py], undetermined_exit_codes: [2]}
    retained_lineage_currentness:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/generate-qualification-lineage.py], undetermined_exit_codes: []}
    active_manifest_currentness:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/generate-current-manifest.py], undetermined_exit_codes: []}
    qualification_layout:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/verify-qualification-layout.py], undetermined_exit_codes: []}
    markdown_links:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/verify-markdown-links.py], undetermined_exit_codes: []}
    git_whitespace:
      responsibility: repository_validation_membership_order
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: ruu_python, arguments: [tools/check-git-whitespace.py], undetermined_exit_codes: []}
  order:
    - maintained_python_syntax
    - json_syntax
    - adr_metadata_tests
    - projection_integrity_tests
    - exact_evidence_binding_tests
    - governed_objects_tests
    - historical_qualification_tests
    - repository_integrity_tests
    - qualification_infrastructure_tests
    - structured_governance_tests
    - proto_ring_binding_registry_tests
    - proto_ring_provider_tests
    - adr_metadata_check
    - accepted_adr_body_immutability
    - proto_ring_binding_registry_currentness
    - proto_ring_provider_currentness
    - structured_governance_check
    - governance_authority_check
    - governed_objects_check
    - authoritative_ref_monotonicity_effective_rules
    - retained_lineage_currentness
    - active_manifest_currentness
    - qualification_layout
    - markdown_links
    - git_whitespace
---

# Ruu Repository Integrity profile

This profile is the sole authority for mandatory current-state validation
membership and order. Runtime Python executable paths and process environments
are supplied through the `ruu_python` evaluation context. Historical replay,
post-baseline replay, and Git-smoke replay remain separate Ruu qualification
phases.
