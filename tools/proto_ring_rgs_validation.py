"""Strictly validate complete and summary RepositoryGovernanceState DTOs."""

from __future__ import annotations

import re
from typing import Any

_INTEGER = re.compile(r"(?:0|-?[1-9][0-9]*)\Z")


class RepositoryGovernanceStateShapeError(ValueError):
    """A composed governance-state value differs from the compat DTO."""


def _object(value: object, label: str, keys: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RepositoryGovernanceStateShapeError(f"{label} must be an object")
    if keys is not None and set(value) != keys:
        raise RepositoryGovernanceStateShapeError(f"{label} has missing or unknown fields")
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RepositoryGovernanceStateShapeError(f"{label} must be a list")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise RepositoryGovernanceStateShapeError(f"{label} must be a string")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int:
        raise RepositoryGovernanceStateShapeError(f"{label} must be an integer")
    return value


def _boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise RepositoryGovernanceStateShapeError(f"{label} must be boolean")
    return value


def _strings(value: object, label: str) -> list[str]:
    values = _list(value, label)
    for item in values:
        _string(item, label)
    return values


def _optional_string(value: object, label: str) -> None:
    if value is not None:
        _string(value, label)


def _map(value: object, label: str, validator) -> dict[str, Any]:
    items = _object(value, label)
    for key, item in items.items():
        _string(key, f"{label} key")
        validator(item, f"{label}.{key}")
    return items


def _structured(value: object, label: str) -> None:
    item = _object(value, label, {"type", "value"})
    tag = _string(item["type"], f"{label}.type")
    payload = item["value"]
    if tag == "null" and payload is None:
        return
    if tag == "boolean" and type(payload) is bool:
        return
    if tag == "integer" and isinstance(payload, str) and _INTEGER.fullmatch(payload):
        return
    if tag == "string" and isinstance(payload, str):
        return
    if tag == "sequence" and isinstance(payload, list):
        for index, child in enumerate(payload):
            _structured(child, f"{label}.value[{index}]")
        return
    if tag == "record" and isinstance(payload, list):
        names: set[str] = set()
        for index, raw_entry in enumerate(payload):
            entry = _object(raw_entry, f"{label}.value[{index}]", {"name", "value"})
            name = _string(entry["name"], f"{label}.value[{index}].name")
            if name in names:
                raise RepositoryGovernanceStateShapeError(f"{label} has duplicate record names")
            names.add(name)
            _structured(entry["value"], f"{label}.value[{index}].value")
        return
    raise RepositoryGovernanceStateShapeError(f"{label} has an invalid structured value")


def _target(value: object, label: str) -> None:
    item = _object(value, label, {"interface", "object"})
    _string(item["interface"], f"{label}.interface")
    _string(item["object"], f"{label}.object")


def _route(value: object, label: str) -> None:
    item = _object(value, label, {"route", "declared_path", "resolved_target"})
    _strings(item["route"], f"{label}.route")
    _string(item["declared_path"], f"{label}.declared_path")
    _string(item["resolved_target"], f"{label}.resolved_target")


def _authority(value: object, label: str) -> None:
    item = _object(value, label, {"responsibility", "source"})
    _string(item["responsibility"], f"{label}.responsibility")
    _string(item["source"], f"{label}.source")


def _binding(value: object, label: str) -> None:
    item = _object(value, label)
    present = _boolean(item.get("present"), f"{label}.present")
    if not present:
        _object(item, label, {"present"})
        return
    _object(item, label, {"present", "kind", "scope", "identity", "authority"})
    _string(item["kind"], f"{label}.kind")
    scope = _object(item["scope"], f"{label}.scope", {"kind", "capability", "interface", "object"})
    _string(scope["kind"], f"{label}.scope.kind")
    for key in ("capability", "interface", "object"):
        _optional_string(scope[key], f"{label}.scope.{key}")
    identity = _object(item["identity"], f"{label}.identity")
    kind = _string(identity.get("kind"), f"{label}.identity.kind")
    expected = {"kind", "repository", "commit"} | ({"path"} if kind == "governance_contract" else set())
    if kind not in {"executable_provider", "governance_contract"}:
        raise RepositoryGovernanceStateShapeError(f"{label}.identity.kind is unknown")
    _object(identity, f"{label}.identity", expected)
    for key in expected - {"kind"}:
        _string(identity[key], f"{label}.identity.{key}")
    _authority(item["authority"], f"{label}.authority")


def _repository_governance_model(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "provider", "capabilities"})
    _integer(item["model_version"], f"{label}.model_version")
    provider = _object(item["provider"], f"{label}.provider", {"id", "binding"})
    _string(provider["id"], f"{label}.provider.id")
    binding = _object(provider["binding"], f"{label}.provider.binding", {"capability", "route"})
    _string(binding["capability"], f"{label}.provider.binding.capability")
    _string(binding["route"], f"{label}.provider.binding.route")
    def capability(raw: object, child: str) -> None:
        cap = _object(raw, child, {"configuration", "routes"})
        _map(cap["configuration"], f"{child}.configuration", _structured)
        _map(cap["routes"], f"{child}.routes", _route)
    _map(item["capabilities"], f"{label}.capabilities", capability)


def _governance_authority(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "sources", "responsibilities"})
    _integer(item["model_version"], f"{label}.model_version")
    def source(raw: object, child: str) -> None:
        source_value = _object(raw, child, {"repository_target"})
        if source_value["repository_target"] is not None:
            _route(source_value["repository_target"], f"{child}.repository_target")
    def responsibility(raw: object, child: str) -> None:
        responsibility_value = _object(raw, child, {"roles", "precedence"})
        _map(responsibility_value["roles"], f"{child}.roles", lambda role, role_label: _string(role, role_label))
        for index, raw_edge in enumerate(_list(responsibility_value["precedence"], f"{child}.precedence")):
            edge = _object(raw_edge, f"{child}.precedence[{index}]", {"higher_source", "lower_source"})
            _string(edge["higher_source"], f"{child}.precedence[{index}].higher_source")
            _string(edge["lower_source"], f"{child}.precedence[{index}].lower_source")
    _map(item["sources"], f"{label}.sources", source)
    _map(item["responsibilities"], f"{label}.responsibilities", responsibility)


def _governed_objects(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "interfaces"})
    _integer(item["model_version"], f"{label}.model_version")
    def interface(raw: object, child: str) -> None:
        interface_value = _object(raw, child, {"objects"})
        def governed_object(raw_object: object, object_label: str) -> None:
            governed = _object(raw_object, object_label, {"responsibilities", "relations"})
            _strings(governed["responsibilities"], f"{object_label}.responsibilities")
            for index, raw_relation in enumerate(_list(governed["relations"], f"{object_label}.relations")):
                relation = _object(raw_relation, f"{object_label}.relations[{index}]", {"relation", "responsibility", "target"})
                _string(relation["relation"], f"{object_label}.relations[{index}].relation")
                _string(relation["responsibility"], f"{object_label}.relations[{index}].responsibility")
                _target(relation["target"], f"{object_label}.relations[{index}].target")
        _map(interface_value["objects"], f"{child}.objects", governed_object)
    _map(item["interfaces"], f"{label}.interfaces", interface)


def _governance_bindings(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "source", "bindings"})
    _integer(item["model_version"], f"{label}.model_version")
    _string(item["source"], f"{label}.source")
    _map(item["bindings"], f"{label}.bindings", _binding)


def _repository_integrity(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "authority", "environments", "continue_after_non_satisfied", "identity_present", "validations", "order"})
    _integer(item["model_version"], f"{label}.model_version")
    _authority(item["authority"], f"{label}.authority")
    _strings(item["environments"], f"{label}.environments")
    _boolean(item["continue_after_non_satisfied"], f"{label}.continue_after_non_satisfied")
    _boolean(item["identity_present"], f"{label}.identity_present")
    def validation(raw: object, child: str) -> None:
        val = _object(raw, child, {"id", "responsibility", "prerequisites", "instances", "command", "target"})
        _string(val["id"], f"{child}.id")
        _string(val["responsibility"], f"{child}.responsibility")
        _strings(val["prerequisites"], f"{child}.prerequisites")
        instances = _object(val["instances"], f"{child}.instances", {"kind", "mode", "selectors"})
        _string(instances["kind"], f"{child}.instances.kind")
        _optional_string(instances["mode"], f"{child}.instances.mode")
        for index, raw_selector in enumerate(_list(instances["selectors"], f"{child}.instances.selectors")):
            selector = _object(raw_selector, f"{child}.instances.selectors[{index}]", {"kind", "value"})
            _string(selector["kind"], f"{child}.instances.selectors[{index}].kind")
            _string(selector["value"], f"{child}.instances.selectors[{index}].value")
        command = _object(val["command"], f"{child}.command", {"environment", "arguments", "undetermined_exit_codes"})
        _string(command["environment"], f"{child}.command.environment")
        _strings(command["arguments"], f"{child}.command.arguments")
        _strings(command["undetermined_exit_codes"], f"{child}.command.undetermined_exit_codes")
        if val["target"] is not None:
            _target(val["target"], f"{child}.target")
    _map(item["validations"], f"{label}.validations", validation)
    _strings(item["order"], f"{label}.order")


def _projection_registry(value: object, label: str) -> None:
    item = _object(value, label, {"model_version", "authority", "projections"})
    _integer(item["model_version"], f"{label}.model_version")
    _authority(item["authority"], f"{label}.authority")
    def projection(raw: object, child: str) -> None:
        projection_value = _object(raw, child, {"id", "responsibility", "canonical_source", "secondary_source", "mode", "validation", "generator_source", "boundary_source", "target", "binding"})
        for key in ("id", "responsibility", "canonical_source", "secondary_source", "mode", "validation"):
            _string(projection_value[key], f"{child}.{key}")
        for key in ("generator_source", "boundary_source", "binding"):
            _optional_string(projection_value[key], f"{child}.{key}")
        if projection_value["target"] is not None:
            _target(projection_value["target"], f"{child}.target")
    _map(item["projections"], f"{label}.projections", projection)


def _evidence_requirements(value: object, label: str) -> None:
    item = _object(value, label, {"authority_source", "model_version", "registry_authority", "requirement_ids", "requirements"})
    _string(item["authority_source"], f"{label}.authority_source")
    _integer(item["model_version"], f"{label}.model_version")
    _authority(item["registry_authority"], f"{label}.registry_authority")
    _strings(item["requirement_ids"], f"{label}.requirement_ids")
    def requirement(raw: object, child: str) -> None:
        req = _object(raw, child, {"id", "responsibility", "instances", "evidence_classes", "subject_source", "context", "candidate_source", "target"})
        for key in ("id", "responsibility", "subject_source", "candidate_source"):
            _string(req[key], f"{child}.{key}")
        instances = _object(req["instances"], f"{child}.instances", {"kind", "source"})
        _string(instances["kind"], f"{child}.instances.kind")
        _optional_string(instances["source"], f"{child}.instances.source")
        classes = _object(req["evidence_classes"], f"{child}.evidence_classes", {"kind", "classes", "source"})
        _string(classes["kind"], f"{child}.evidence_classes.kind")
        if classes["classes"] is not None:
            _strings(classes["classes"], f"{child}.evidence_classes.classes")
        _optional_string(classes["source"], f"{child}.evidence_classes.source")
        context = _object(req["context"], f"{child}.context", {"required", "source"})
        _boolean(context["required"], f"{child}.context.required")
        _optional_string(context["source"], f"{child}.context.source")
        if req["target"] is not None:
            _target(req["target"], f"{child}.target")
    _map(item["requirements"], f"{label}.requirements", requirement)


_COMPONENTS = {"repository_governance_model", "governance_authority", "governed_objects", "governance_bindings", "repository_integrity", "projection_registry", "evidence_requirements"}
_STATE_VALIDATORS = {
    "repository_governance_model": _repository_governance_model,
    "governance_authority": _governance_authority,
    "governed_objects": _governed_objects,
    "governance_bindings": _governance_bindings,
    "repository_integrity": _repository_integrity,
    "projection_registry": _projection_registry,
    "evidence_requirements": _evidence_requirements,
}


def validate_compose(request: dict[str, Any], raw_value: object) -> None:
    """Reject every missing, unknown, or mistyped complete/summary DTO field."""

    projection = request.get("projection", "summary")
    keys = {"stage", "identity_present", "scope_paths", "components", "bindings"}
    if projection == "complete":
        keys.add("state")
    elif projection != "summary":
        raise RepositoryGovernanceStateShapeError("composition projection is unknown")
    value = _object(raw_value, "composition", keys)
    _string(value["stage"], "composition.stage")
    _boolean(value["identity_present"], "composition.identity_present")
    _strings(value["scope_paths"], "composition.scope_paths")
    components = _object(value["components"], "composition.components", _COMPONENTS)
    for name in _COMPONENTS:
        _boolean(components[name], f"composition.components.{name}")
    _map(value["bindings"], "composition.bindings", _binding)
    if projection == "complete":
        state = _object(value["state"], "composition.state", _COMPONENTS)
        for name, validator in _STATE_VALIDATORS.items():
            component = state[name]
            if component is None and name in {"governed_objects", "repository_integrity", "projection_registry", "evidence_requirements"}:
                continue
            validator(component, f"composition.state.{name}")
