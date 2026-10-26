"""Resolve Ruu post-baseline policy through native Proto-Ring operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

_SOURCE = "post_baseline_qualification_evidence"
_RESPONSIBILITY = "qualification_evidence_binding"
_IDS = (
    "post_baseline_artifact_binding",
    "post_baseline_recorded_output_binding",
)


class PostBaselineEvidenceRequirementsError(ValueError):
    """Report controlled failure to resolve Ruu's persistent requirements."""


@dataclass(frozen=True)
class DeclarationSourcePolicy:
    kind: str
    source: str | None


@dataclass(frozen=True)
class EvidenceClassesPolicy:
    kind: str
    classes: frozenset[str] | None
    source: str | None


@dataclass(frozen=True)
class ContextPolicy:
    required: bool
    source: str | None


@dataclass(frozen=True)
class TargetPolicy:
    interface: str
    object: str


@dataclass(frozen=True)
class PersistentEvidenceRequirementPolicy:
    id: str
    responsibility: str
    instances: DeclarationSourcePolicy
    evidence_classes: EvidenceClassesPolicy
    subject_source: str
    context: ContextPolicy
    candidate_source: str
    target: TargetPolicy | None


@dataclass(frozen=True)
class PostBaselineEvidencePolicies:
    artifact: PersistentEvidenceRequirementPolicy
    recorded_output: PersistentEvidenceRequirementPolicy


def _policy(value: dict[str, object]) -> PersistentEvidenceRequirementPolicy:
    instances = value["instances"]
    classes = value["evidence_classes"]
    context = value["context"]
    target = value["target"]
    if not isinstance(instances, dict) or not isinstance(classes, dict) or not isinstance(context, dict):
        raise ValueError("native evidence requirement has invalid nested policy")
    return PersistentEvidenceRequirementPolicy(
        id=str(value["id"]),
        responsibility=str(value["responsibility"]),
        instances=DeclarationSourcePolicy(str(instances["kind"]), instances["source"]),
        evidence_classes=EvidenceClassesPolicy(
            str(classes["kind"]),
            frozenset(classes["classes"]) if classes["classes"] is not None else None,
            classes["source"],
        ),
        subject_source=str(value["subject_source"]),
        context=ContextPolicy(bool(context["required"]), context["source"]),
        candidate_source=str(value["candidate_source"]),
        target=(TargetPolicy(str(target["interface"]), str(target["object"])) if isinstance(target, dict) else None),
    )


def _require_source_shape(requirement: PersistentEvidenceRequirementPolicy) -> None:
    if requirement.responsibility != _RESPONSIBILITY:
        raise ValueError("post-baseline requirement has the wrong responsibility")
    if requirement.target is not None:
        raise ValueError("post-baseline requirement must not target a governed object")
    if requirement.instances != DeclarationSourcePolicy("source", _SOURCE):
        raise ValueError("post-baseline requirement instances must be source-driven")
    if requirement.subject_source != _SOURCE:
        raise ValueError("post-baseline requirement has the wrong subject source")
    if requirement.context.required:
        raise ValueError("post-baseline requirement must not require context")
    if requirement.candidate_source != _SOURCE:
        raise ValueError("post-baseline requirement has the wrong candidate source")


def load(root: Path) -> PostBaselineEvidencePolicies:
    """Load and constrain exactly the two routed Ruu evidence requirements."""

    try:
        value = invoke_compat_result(
            root,
            "evidence-requirements.registry",
            {"repository": str(root), "requirement_ids": list(_IDS)},
        )
    except ProtoRingExecutableError as error:
        raise PostBaselineEvidenceRequirementsError(str(error)) from error
    requirements = value["requirements"]
    if set(requirements) != set(_IDS):
        raise ValueError("Evidence Requirements Registry has unexpected requirements")
    artifact = _policy(requirements[_IDS[0]])
    recorded = _policy(requirements[_IDS[1]])
    _require_source_shape(artifact)
    _require_source_shape(recorded)
    if artifact.evidence_classes != EvidenceClassesPolicy("source", None, _SOURCE):
        raise ValueError("artifact evidence classes must be source-backed")
    if recorded.evidence_classes != EvidenceClassesPolicy(
        "explicit", frozenset({"recorded_output"}), None
    ):
        raise ValueError("recorded-output requirement must admit only recorded_output")
    return PostBaselineEvidencePolicies(artifact, recorded)


def binding_status(
    requirement: PersistentEvidenceRequirementPolicy,
    evidence_class: str,
    required_sha256: str,
    candidate_sha256: str,
) -> str:
    """Return the provider's typed exact-binding status for Ruu-owned SHA text."""

    classes = requirement.evidence_classes
    if classes.kind == "explicit":
        if classes.classes is None:
            raise ValueError("explicit evidence classes are missing")
        admitted = sorted(classes.classes)
    else:
        if classes.kind != "source" or classes.source != _SOURCE:
            raise ValueError("source-backed evidence classes have the wrong source")
        admitted = [evidence_class]
    try:
        value = invoke_compat_result(
            TOOLS.parent,
            "exact-evidence-binding.evaluate",
            {
                "mode": "evaluate_binding",
                "requirement": {
                    "admitted_classes": admitted,
                    "subject_hex": required_sha256.encode("ascii").hex(),
                    "context_hex": None,
                    "context_required": False,
                },
                "binding": {
                    "evidence_class": evidence_class,
                    "subject_hex": candidate_sha256.encode("ascii").hex(),
                    "context_hex": None,
                },
            },
        )
    except (UnicodeEncodeError, ProtoRingExecutableError) as error:
        raise ValueError(str(error)) from error
    return value["status"]
