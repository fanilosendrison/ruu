---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "evidence-requirement-registry"
domain: "ruu-repository-governance"
severity: "strict"
name: "Ruu Evidence Requirements Registry"

evidence_requirements:
  model_version: 1
  authority:
    responsibility: evidence_requirements_declaration
    source: evidence_requirements_registry
  requirements:
    post_baseline_artifact_binding:
      responsibility: qualification_evidence_binding
      instances:
        kind: source
        source: post_baseline_qualification_evidence
      evidence_classes:
        kind: source
        source: post_baseline_qualification_evidence
      subject:
        source: post_baseline_qualification_evidence
      context:
        required: false
      candidates:
        source: post_baseline_qualification_evidence
    post_baseline_recorded_output_binding:
      responsibility: qualification_evidence_binding
      instances:
        kind: source
        source: post_baseline_qualification_evidence
      evidence_classes:
        kind: explicit
        classes:
          - recorded_output
      subject:
        source: post_baseline_qualification_evidence
      context:
        required: false
      candidates:
        source: post_baseline_qualification_evidence
---

# Ruu Evidence Requirements Registry

The registry declares source-driven post-baseline artifact requirements and the
distinct `recorded_output` registration requirement. Ruu continues to own the
metadata schema, registration membership, path and file rules, SHA-256
construction, artifact roles, replay runner, expected exit code, exact stdout
comparison, and qualification PASS/FAIL semantics.
