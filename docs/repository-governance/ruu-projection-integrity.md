---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "projection-registry"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Projection Registry"

projection_registry:
  model_version: 1
  authority:
    responsibility: projection_registry_declaration
    source: projection_registry
  projections:
    adr_index:
      responsibility: adr_metadata
      canonical_source: canonical_adr_records
      secondary_source: adr_index
      mode: generated
      validation: adr_metadata_check
      generator_source: adr_metadata_generator
    adr_annotated_history:
      responsibility: adr_metadata
      canonical_source: canonical_adr_records
      secondary_source: adr_history
      mode: mechanically_validated_maintained
      validation: projection_integrity_tests
    active_repository_manifest:
      responsibility: repository_artifact_state
      canonical_source: repository_git_tree
      secondary_source: active_repository_manifest
      mode: generated
      validation: active_manifest_currentness
      generator_source: active_manifest_generator
    retained_lineage:
      responsibility: retained_lineage_currentness
      canonical_source: immutable_adr080_snapshot
      secondary_source: retained_lineage
      mode: generated
      validation: retained_lineage_currentness
      generator_source: retained_lineage_generator
    retained_state_space_custody:
      responsibility: retained_historical_snapshot
      canonical_source: immutable_adr080_snapshot
      secondary_source: retained_state_space
      mode: bounded_historical_snapshot
      validation: qualification_layout
      boundary_source: immutable_adr080_snapshot
    retained_git_smoke_custody:
      responsibility: retained_historical_snapshot
      canonical_source: immutable_adr080_snapshot
      secondary_source: retained_git_smoke
      mode: bounded_historical_snapshot
      validation: qualification_layout
      boundary_source: immutable_adr080_snapshot
    retained_qualification_custody:
      responsibility: retained_historical_snapshot
      canonical_source: immutable_adr080_snapshot
      secondary_source: retained_qualification_evidence
      mode: bounded_historical_snapshot
      validation: qualification_layout
      boundary_source: immutable_adr080_snapshot
    governed_adr_catalog:
      responsibility: governed_adr_catalog_currentness
      canonical_source: canonical_adr_records
      secondary_source: governed_objects_profile
      mode: mechanically_validated_maintained
      validation: governed_objects_check
    executable_binding_registry_representation:
      responsibility: executable_provider_binding
      canonical_source: executable_dependency_manifest
      secondary_source: governance_binding_registry
      mode: mechanically_validated_maintained
      validation: proto_ring_binding_registry_currentness
      binding: proto_ring_executable
    effective_proto_ring_realization:
      responsibility: executable_provider_binding
      canonical_source: executable_dependency_manifest
      secondary_source: effective_proto_ring_provider
      mode: mechanically_validated_maintained
      validation: proto_ring_provider_currentness
      binding: proto_ring_executable
---

# Ruu Projection Registry

This registry declares only Ruu authority-to-secondary-representation
relations. Generated active metadata remains Ruu-owned. Bounded historical
entries preserve custody without claiming current qualification truth, and
post-baseline registrations remain authority rather than projections.
