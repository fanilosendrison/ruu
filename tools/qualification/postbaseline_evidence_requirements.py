"""Resolve Ruu post-baseline registrations through routed evidence requirements."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from proto_ring import evidence_requirements, repository_governance_state
from proto_ring.exact_evidence_binding import (
    BindingStatus,
    EvidenceBinding,
    EvidenceRequirement,
    evaluate,
)

_SOURCE = "post_baseline_qualification_evidence"
_RESPONSIBILITY = "qualification_evidence_binding"


class PostBaselineEvidenceRequirementsError(ValueError):
    """Report controlled failure to resolve Ruu's persistent requirements."""


@dataclass(frozen=True)
class PostBaselineEvidencePolicies:
    """The two persistent requirement declarations used by registration checks."""

    artifact: evidence_requirements.PersistentEvidenceRequirement
    recorded_output: evidence_requirements.PersistentEvidenceRequirement


def _require_source_shape(
    requirement: evidence_requirements.PersistentEvidenceRequirement,
) -> None:
    if requirement.responsibility_id != _RESPONSIBILITY:
        raise ValueError("post-baseline requirement has the wrong responsibility")
    if requirement.target is not None:
        raise ValueError("post-baseline requirement must not target a governed object")
    if requirement.instances.kind is not evidence_requirements.InstantiationKind.SOURCE:
        raise ValueError("post-baseline requirement instances must be source-driven")
    if requirement.instances.source_id != _SOURCE:
        raise ValueError("post-baseline requirement has the wrong instance source")
    if requirement.subject_source_id != _SOURCE:
        raise ValueError("post-baseline requirement has the wrong subject source")
    if requirement.context.required:
        raise ValueError("post-baseline requirement must not require context")
    if requirement.candidate_source_id != _SOURCE:
        raise ValueError("post-baseline requirement has the wrong candidate source")


def load(root: Path) -> PostBaselineEvidencePolicies:
    """Load and constrain the routed requirements used by Ruu metadata discovery."""

    try:
        state = repository_governance_state.load(root)
        registry = state.evidence_requirements
        if registry is None:
            raise PostBaselineEvidenceRequirementsError(
                "evidence_requirements capability is required"
            )
    except repository_governance_state.RepositoryGovernanceStateError as error:
        raise PostBaselineEvidenceRequirementsError(str(error)) from error
    try:
        artifact = registry.requirements["post_baseline_artifact_binding"]
        recorded = registry.requirements["post_baseline_recorded_output_binding"]
    except KeyError as error:
        raise PostBaselineEvidenceRequirementsError(
            f"missing post-baseline evidence requirement: {error.args[0]}"
        ) from error
    if set(registry.requirements) != {
        "post_baseline_artifact_binding",
        "post_baseline_recorded_output_binding",
    }:
        raise ValueError("Evidence Requirements Registry has unexpected requirements")
    _require_source_shape(artifact)
    _require_source_shape(recorded)
    if artifact.evidence_classes.kind is not evidence_requirements.EvidenceClassKind.SOURCE:
        raise ValueError("artifact evidence classes must be source-backed")
    if artifact.evidence_classes.source_id != _SOURCE:
        raise ValueError("artifact evidence classes have the wrong source")
    if recorded.evidence_classes.kind is not evidence_requirements.EvidenceClassKind.EXPLICIT:
        raise ValueError("recorded-output evidence classes must be explicit")
    if recorded.evidence_classes.explicit_classes != frozenset({"recorded_output"}):
        raise ValueError("recorded-output requirement must admit only recorded_output")
    return PostBaselineEvidencePolicies(artifact, recorded)


def binding_status(
    requirement: evidence_requirements.PersistentEvidenceRequirement,
    evidence_class: str,
    required_sha256: str,
    candidate_sha256: str,
) -> BindingStatus:
    """Instantiate one Ruu-owned SHA identity comparison from persistent policy."""

    classes = requirement.evidence_classes
    if classes.kind is evidence_requirements.EvidenceClassKind.EXPLICIT:
        admitted = classes.explicit_classes
        if admitted is None:
            raise ValueError("explicit evidence classes are missing")
    else:
        if classes.source_id != _SOURCE:
            raise ValueError("source-backed evidence classes have the wrong source")
        admitted = frozenset({evidence_class})
    persistent_requirement = EvidenceRequirement(
        admitted_classes=admitted,
        subject_identity=required_sha256.encode("ascii"),
    )
    evidence = EvidenceBinding(
        evidence_class=evidence_class,
        subject_identity=candidate_sha256.encode("ascii"),
    )
    return evaluate(persistent_requirement, evidence)
