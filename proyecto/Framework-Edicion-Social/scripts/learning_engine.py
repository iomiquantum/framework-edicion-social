#!/usr/bin/env python3
"""Conservative, append-only learning engine for social-video editing.

The engine normalizes approval, feedback, performance and QA evidence into one
contract.  It can recommend that a contextual pattern enter human review, but
it deliberately cannot promote a rule, expand its scope, or write a registry.
Template families are evaluated as a portfolio: candidates from different
families or applicability contexts never compete for one global winning slot.
"""

from __future__ import annotations

import argparse
import portable_fcntl as fcntl
import hashlib
import json
import math
import os
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from schema_validation import validate_document


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "learning/promotion-policy.v1.json"
EVENT_SCHEMA_PATH = ROOT / "schemas/learning-evidence-event.schema.json"
POLICY_SCHEMA_PATH = ROOT / "schemas/learning-promotion-policy.schema.json"
REPORT_SCHEMA_PATH = ROOT / "schemas/learning-recommendation-report.schema.json"
FAMILY_CONTROLLED_AXES = {"structure", "format", "style", "rhythm", "transitions", "audio"}
TECHNICAL_PATTERN_AXES = {"technical", "workflow"}
HIGHER_SCOPE_PARENTS = {
    "series": {"video"},
    "style": {"video", "series"},
    "creator": {"series", "style"},
    "account": {"creator", "series", "style"},
    "global": {"creator", "account"},
}
SCOPE_CHAINS = (
    ("video", "series", "creator", "global"),
    ("video", "series", "account", "global"),
    ("video", "style", "creator", "global"),
    ("video", "style", "account", "global"),
)
MONOTONIC_THRESHOLD_FIELDS = (
    "min_support_contexts",
    "min_unique_videos",
    "min_unique_projects",
    "min_unique_series",
    "min_positive_ratio",
    "min_alternative_margin",
)
MINIMUM_POLICY_FLOORS = {
    "asset": {
        "min_support_contexts": 2,
        "min_unique_videos": 1,
        "min_unique_projects": 1,
        "min_unique_series": 0,
        "min_evidence_types": 1,
        "min_explicit_human_supports": 1,
        "min_positive_ratio": 0.75,
        "min_alternative_margin": 0.10,
    },
    "video": {
        "min_support_contexts": 1,
        "min_unique_videos": 1,
        "min_unique_projects": 1,
        "min_unique_series": 0,
        "min_evidence_types": 1,
        "min_explicit_human_supports": 0,
        "min_positive_ratio": 0.60,
        "min_alternative_margin": 0.00,
    },
    "series": {
        "min_support_contexts": 3,
        "min_unique_videos": 3,
        "min_unique_projects": 1,
        "min_unique_series": 1,
        "min_evidence_types": 2,
        "min_explicit_human_supports": 1,
        "min_positive_ratio": 0.75,
        "min_alternative_margin": 0.15,
    },
    "style": {
        "min_support_contexts": 5,
        "min_unique_videos": 4,
        "min_unique_projects": 2,
        "min_unique_series": 2,
        "min_evidence_types": 2,
        "min_explicit_human_supports": 1,
        "min_positive_ratio": 0.75,
        "min_alternative_margin": 0.15,
    },
    "creator": {
        "min_support_contexts": 6,
        "min_unique_videos": 4,
        "min_unique_projects": 2,
        "min_unique_series": 2,
        "min_evidence_types": 2,
        "min_explicit_human_supports": 2,
        "min_positive_ratio": 0.78,
        "min_alternative_margin": 0.15,
    },
    "account": {
        "min_support_contexts": 6,
        "min_unique_videos": 4,
        "min_unique_projects": 2,
        "min_unique_series": 2,
        "min_evidence_types": 2,
        "min_explicit_human_supports": 2,
        "min_positive_ratio": 0.78,
        "min_alternative_margin": 0.15,
    },
    # Global learning is restricted to technical contracts and requires a
    # separate governance authorization. Human taste is therefore not used as
    # a synthetic evidence type merely to satisfy diversity thresholds.
    "global": {
        "min_support_contexts": 8,
        "min_unique_videos": 5,
        "min_unique_projects": 2,
        "min_unique_series": 2,
        "min_evidence_types": 1,
        "min_explicit_human_supports": 0,
        "min_positive_ratio": 0.80,
        "min_alternative_margin": 0.20,
    },
}


class LearningContractError(ValueError):
    """Raised when evidence would violate an auditable learning contract."""


def _reject_nonfinite(token):
    raise ValueError(f"non-finite JSON number is forbidden: {token}")


def json_loads_strict(text):
    return json.loads(text, parse_constant=_reject_nonfinite)


def load_json(path):
    return json_loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def document_sha256(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _contract_errors(value, schema_path, label):
    schema = load_json(schema_path)
    return [f"{label}: {error}" for error in validate_document(value, schema)]


def _raise_errors(errors):
    if errors:
        raise LearningContractError("\n".join(f"- {error}" for error in errors))


def validate_policy(policy):
    """Validate both the JSON contract and conservative, cross-scope floors."""
    errors = _contract_errors(policy, POLICY_SCHEMA_PATH, "policy")
    if errors:
        return errors
    axes = set(policy.get("safeguards", {}).get("controlled_variation_axes", []))
    if axes and axes != FAMILY_CONTROLLED_AXES:
        errors.append(
            "policy: controlled_variation_axes must contain exactly structure, format, style, rhythm, transitions and audio"
        )
    required_family_axes = set(policy.get("safeguards", {}).get("require_template_family_for_axes", []))
    if not axes.issubset(required_family_axes):
        errors.append("policy: every controlled variation axis must require a template family")
    governance = policy.get("governance", {})
    if any(
        (
            governance.get("automatic_promotion") is not False,
            governance.get("registry_write_permitted") is not False,
            governance.get("human_review_required") is not True,
            governance.get("scope_escalation_allowed") is not False,
            governance.get("single_template_winner") is not False,
        )
    ):
        errors.append("policy: immutable safety governance was weakened")
    thresholds = policy.get("scope_thresholds", {})
    for scope, floors in MINIMUM_POLICY_FLOORS.items():
        configured = thresholds.get(scope, {})
        for field, floor in floors.items():
            if configured.get(field, -math.inf) < floor:
                errors.append(f"policy: {scope}.{field} cannot be lower than conservative floor {floor}")
    for chain in SCOPE_CHAINS:
        for lower_scope, higher_scope in zip(chain, chain[1:]):
            lower = thresholds.get(lower_scope, {})
            higher = thresholds.get(higher_scope, {})
            for field in MONOTONIC_THRESHOLD_FIELDS:
                if field in lower and field in higher and higher[field] < lower[field]:
                    errors.append(
                        f"policy: {higher_scope}.{field} cannot be lower than {lower_scope}.{field}"
                    )
    return sorted(set(errors))


def load_policy(path=DEFAULT_POLICY):
    policy = load_json(path)
    errors = validate_policy(policy)
    _raise_errors(errors)
    return policy


def _context_scope_id(context, level):
    return {
        "asset": context["asset_id"],
        "video": context["video_id"],
        "series": context["series_id"],
        "style": context["style_id"],
        "creator": context["creator_id"],
        "account": context["account_id"],
        "global": "global",
    }[level]


def _scope_authorization_errors(event):
    scope = event["scope"]
    context = event["context"]
    authorization = event["scope_authorization"]
    errors = []
    if scope["level"] in {"asset", "video"}:
        if authorization is not None:
            errors.append(f"event {event['event_id']}: exact asset/video evidence cannot carry scope authorization")
        return errors
    if authorization is None:
        return [f"event {event['event_id']}: {scope['level']} scope requires explicit governance authorization"]

    source_scope = authorization["source_scope"]
    target_scope = authorization["target_scope"]
    allowed_parents = HIGHER_SCOPE_PARENTS[scope["level"]]
    if source_scope["level"] not in allowed_parents:
        errors.append(
            f"event {event['event_id']}: {source_scope['level']} cannot authorize direct evaluation at {scope['level']} scope"
        )
    if target_scope != scope:
        errors.append(f"event {event['event_id']}: authorization target must equal the event scope")
    expected_source_id = _context_scope_id(context, source_scope["level"])
    if expected_source_id is None or source_scope["id"] != expected_source_id:
        errors.append(
            f"event {event['event_id']}: authorization source must match the declared context"
        )
    approved_at = datetime.fromisoformat(authorization["approved_at"].replace("Z", "+00:00"))
    occurred_at = datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
    if approved_at > occurred_at:
        errors.append(f"event {event['event_id']}: scope authorization cannot postdate the evidence event")
    return errors


def validate_event(event, policy=None):
    """Return all schema and semantic errors for one normalized event."""
    if policy is None:
        policy = load_policy()
    errors = _contract_errors(event, EVENT_SCHEMA_PATH, "event")
    if errors:
        return errors

    source = event["source"]
    evidence_type = event["evidence_type"]
    evidence = event["evidence"]
    scope = event["scope"]
    context = event["context"]
    pattern = event["pattern"]
    source_kind = source["kind"]
    signal = evidence["signal"]
    hard_gate = evidence["hard_gate"]
    decision_domain = pattern["decision_domain"]

    if source_kind in {"approval", "feedback"} and not evidence["explicit_human"]:
        errors.append(f"event {event['event_id']}: {source_kind} must be explicit human evidence")
    if source_kind in {"approval", "feedback"} and source["recorded_by"] == "system":
        errors.append(f"event {event['event_id']}: explicit human evidence cannot be recorded_by system")
    if source_kind == "approval" and evidence_type not in {"creative", "preference"}:
        errors.append(f"event {event['event_id']}: approval must be creative or preference evidence")
    if source_kind == "feedback" and evidence_type not in {"creative", "preference"}:
        errors.append(f"event {event['event_id']}: feedback must be creative or preference evidence")
    if evidence_type == "preference" and not evidence["explicit_human"]:
        errors.append(f"event {event['event_id']}: preference evidence must be explicit")
    if source_kind == "performance" and evidence_type != "performance":
        errors.append(f"event {event['event_id']}: performance source must use performance evidence_type")
    if evidence_type == "performance" and source_kind != "performance":
        errors.append(f"event {event['event_id']}: performance evidence_type requires performance source")
    if source_kind == "qa_measurement" and evidence_type != "technical":
        errors.append(f"event {event['event_id']}: qa_measurement must be technical evidence")
    if source_kind in {"performance", "qa_measurement"} and not evidence["measured"]:
        errors.append(f"event {event['event_id']}: measured source is marked unmeasured")
    if source_kind in {"performance", "qa_measurement"} and evidence["explicit_human"]:
        errors.append(f"event {event['event_id']}: measured system evidence cannot claim explicit_human")

    performance_context = evidence["performance_context"]
    if evidence_type == "performance":
        if not isinstance(performance_context, dict):
            errors.append(f"event {event['event_id']}: performance_context is required")
        else:
            comparison = performance_context["comparison_basis"]
            if signal in {"supports", "opposes"} and performance_context["metric_value"] is None:
                errors.append(f"event {event['event_id']}: directional performance evidence needs metric_value")
            if signal in {"supports", "opposes"} and comparison == "none":
                errors.append(f"event {event['event_id']}: directional performance evidence requires a comparison")
            if comparison in {"cohort", "control", "ab_test"} and not performance_context["benchmark_id"]:
                errors.append(f"event {event['event_id']}: {comparison} comparison needs benchmark_id")
            if comparison == "none" and any(
                performance_context[field] is not None
                for field in ("benchmark_id", "benchmark_value", "experiment_id")
            ):
                errors.append(f"event {event['event_id']}: comparison_basis none cannot carry comparison identifiers")
            if signal in {"supports", "opposes"} and performance_context["benchmark_value"] is None:
                errors.append(f"event {event['event_id']}: directional performance evidence needs benchmark_value")
            if comparison == "ab_test" and not performance_context["experiment_id"]:
                errors.append(f"event {event['event_id']}: ab_test comparison needs experiment_id")
            if comparison != "ab_test" and performance_context["experiment_id"] is not None:
                errors.append(f"event {event['event_id']}: experiment_id is reserved for ab_test evidence")
            if signal in {"supports", "opposes"} and performance_context["observation_window_hours"] <= 0:
                errors.append(f"event {event['event_id']}: directional performance evidence needs a positive observation window")
            if (
                signal in {"supports", "opposes"}
                and evidence["sample_size"] < policy["safeguards"]["min_directional_performance_sample_size"]
            ):
                errors.append(
                    f"event {event['event_id']}: directional performance sample_size is below policy minimum"
                )
            metric_value = performance_context["metric_value"]
            benchmark_value = performance_context["benchmark_value"]
            if signal in {"supports", "opposes"} and metric_value is not None and benchmark_value is not None:
                higher_is_better = performance_context["metric_direction"] == "higher_is_better"
                supports = metric_value > benchmark_value if higher_is_better else metric_value < benchmark_value
                opposes = metric_value < benchmark_value if higher_is_better else metric_value > benchmark_value
                if (signal == "supports" and not supports) or (signal == "opposes" and not opposes):
                    errors.append(f"event {event['event_id']}: performance signal contradicts metric direction")
    elif performance_context is not None:
        errors.append(f"event {event['event_id']}: non-performance evidence cannot carry performance_context")

    if signal in {"supports", "opposes"} and evidence["weight"] <= 0:
        errors.append(f"event {event['event_id']}: directional signal needs positive weight")
    if signal in {"supports", "opposes"} and evidence["confidence"] == "insufficient":
        errors.append(f"event {event['event_id']}: insufficient-confidence evidence cannot be directional")
    if signal in {"neutral", "revokes"} and evidence["weight"] != 0:
        errors.append(f"event {event['event_id']}: neutral or revocation signal must have zero weight")
    if signal == "revokes" and not event["supersedes_event_id"]:
        errors.append(f"event {event['event_id']}: revocation must identify the superseded event")
    if event["supersedes_event_id"] and not event["supersession_reason"]:
        errors.append(f"event {event['event_id']}: supersession requires a reason")
    if not event["supersedes_event_id"] and event["supersession_reason"] is not None:
        errors.append(f"event {event['event_id']}: supersession_reason requires supersedes_event_id")

    if hard_gate is not None:
        if source_kind != "qa_measurement" or evidence_type != "technical":
            errors.append(f"event {event['event_id']}: hard gates require technical qa_measurement evidence")
        if signal != "neutral" or evidence["weight"] != 0:
            errors.append(f"event {event['event_id']}: hard gates are separate from score and must be neutral with zero weight")
    elif evidence_type == "technical":
        if decision_domain != "technical_contract" or pattern["variant_axis"] not in TECHNICAL_PATTERN_AXES:
            errors.append(
                f"event {event['event_id']}: non-gate technical evidence may only evaluate technical/workflow contracts"
            )
    elif decision_domain == "technical_contract":
        errors.append(f"event {event['event_id']}: technical contracts require technical evidence")

    if decision_domain == "editorial_choice" and evidence_type not in {"creative", "preference", "performance", "technical"}:
        errors.append(f"event {event['event_id']}: unsupported evidence for editorial choice")
    if scope["level"] == "global" and decision_domain != "technical_contract":
        errors.append(f"event {event['event_id']}: global learned scope is reserved for technical contracts")

    if scope["level"] == "global":
        if scope["id"] != "global":
            errors.append(f"event {event['event_id']}: global scope id must be 'global'")
    elif _context_scope_id(context, scope["level"]) != scope["id"]:
        errors.append(
            f"event {event['event_id']}: {scope['level']} scope id must equal its context id"
        )
    errors.extend(_scope_authorization_errors(event))

    required_family_axes = set(policy["safeguards"]["require_template_family_for_axes"])
    if pattern["variant_axis"] in required_family_axes:
        if not pattern["template_family_id"] or not pattern["variant_id"]:
            errors.append(
                f"event {event['event_id']}: {pattern['variant_axis']} learning requires template_family_id and variant_id"
            )
    if pattern["variation_mode"] in {"controlled_variant", "exploratory"} and not pattern["variant_id"]:
        errors.append(f"event {event['event_id']}: variation mode requires variant_id")
    return errors


def _lineage_identity(event):
    pattern = event["pattern"]
    return canonical_json(
        {
            "pattern_key": pattern["key"],
            "pattern_value": pattern["value"],
            "scope": event["scope"],
            "decision_domain": pattern["decision_domain"],
            "variant_axis": pattern["variant_axis"],
            "template_family_id": pattern["template_family_id"],
            "variant_id": pattern["variant_id"],
            "variation_mode": pattern["variation_mode"],
            "applicability": pattern["applicability"],
        }
    )


def _independence_anchor(event):
    context = event["context"]
    performance_context = event["evidence"]["performance_context"]
    if performance_context and performance_context["experiment_id"]:
        return canonical_json(
            {
                "kind": "experiment",
                "project_id": context["project_id"],
                "experiment_id": performance_context["experiment_id"],
            }
        )
    if context["video_id"]:
        return canonical_json(
            {"kind": "video", "project_id": context["project_id"], "video_id": context["video_id"]}
        )
    if context["asset_id"]:
        return canonical_json(
            {"kind": "asset", "project_id": context["project_id"], "asset_id": context["asset_id"]}
        )
    return canonical_json(
        {"kind": "subject", "project_id": context["project_id"], "subject_sha256": event["source"]["subject_sha256"]}
    )


def _event_authority(event):
    if event["evidence"]["hard_gate"] is not None:
        return 4
    if event["evidence"]["explicit_human"]:
        return 3
    if event["evidence_type"] == "technical":
        return 2
    if event["evidence_type"] == "performance":
        return 1
    return 0


def validate_event_set(events, policy=None):
    """Validate identities and immutable supersession semantics across a store."""
    if policy is None:
        policy = load_policy()
    else:
        policy_errors = validate_policy(policy)
        if policy_errors:
            return policy_errors
    errors = []
    by_id = {}
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"event[{index}]: expected object")
            continue
        errors.extend(validate_event(event, policy))
        event_id = event.get("event_id")
        if event_id in by_id:
            errors.append(f"duplicate event_id: {event_id}")
        else:
            by_id[event_id] = event
    if errors:
        return errors

    context_to_anchor = {}
    anchor_to_context = {}
    authorization_by_id = {}
    for event in events:
        context_id = event["context"]["independent_context_id"]
        anchor = _independence_anchor(event)
        prior_anchor = context_to_anchor.get(context_id)
        if prior_anchor is not None and prior_anchor != anchor:
            errors.append(f"independent_context_id {context_id} maps to more than one natural context")
        else:
            context_to_anchor[context_id] = anchor
        prior_context = anchor_to_context.get(anchor)
        if prior_context is not None and prior_context != context_id:
            errors.append(
                f"natural context is aliased by both {prior_context} and {context_id}; context ids must be one-to-one"
            )
        else:
            anchor_to_context[anchor] = context_id
        authorization = event["scope_authorization"]
        if authorization is not None:
            approval_id = authorization["approval_id"]
            fingerprint = canonical_json(authorization)
            prior_fingerprint = authorization_by_id.get(approval_id)
            if prior_fingerprint is not None and prior_fingerprint != fingerprint:
                errors.append(f"scope authorization {approval_id} has conflicting immutable content")
            else:
                authorization_by_id[approval_id] = fingerprint
    if errors:
        return sorted(set(errors))

    successors = {}
    for event in events:
        target_id = event["supersedes_event_id"]
        if target_id is None:
            continue
        if target_id == event["event_id"]:
            errors.append(f"event {event['event_id']}: cannot supersede itself")
            continue
        target = by_id.get(target_id)
        if target is None:
            errors.append(f"event {event['event_id']}: superseded event does not exist: {target_id}")
            continue
        if target_id in successors:
            errors.append(
                f"event {target_id}: ambiguous history; superseded by both {successors[target_id]} and {event['event_id']}"
            )
        else:
            successors[target_id] = event["event_id"]
        if _lineage_identity(event) != _lineage_identity(target):
            errors.append(
                f"event {event['event_id']}: supersession cannot cross pattern value, scope, domain, family, variant or context"
            )
        event_gate = event["evidence"]["hard_gate"]
        target_gate = target["evidence"]["hard_gate"]
        if (event_gate is None) != (target_gate is None):
            errors.append(f"event {event['event_id']}: hard-gate history cannot supersede scored evidence or vice versa")
        elif event_gate is not None:
            if event_gate["gate_id"] != target_gate["gate_id"]:
                errors.append(f"event {event['event_id']}: a hard-gate update must keep the same gate_id")
            if event["evidence"]["signal"] == "revokes":
                errors.append(f"event {event['event_id']}: hard gates are cleared by a measured pass, never by revocation")
        elif event["evidence"]["signal"] == "revokes":
            if _event_authority(event) < _event_authority(target):
                errors.append(f"event {event['event_id']}: revocation authority is lower than the target evidence")
            if target["evidence"]["explicit_human"] and not event["evidence"]["explicit_human"]:
                errors.append(f"event {event['event_id']}: only explicit human evidence may revoke human evidence")
        elif (
            event["source"]["kind"] != target["source"]["kind"]
            or event["evidence_type"] != target["evidence_type"]
        ):
            errors.append(
                f"event {event['event_id']}: a correction must preserve source kind and evidence type; use an authorized revocation otherwise"
            )
        current_time = datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
        target_time = datetime.fromisoformat(target["occurred_at"].replace("Z", "+00:00"))
        if current_time < target_time:
            errors.append(f"event {event['event_id']}: supersession predates {target_id}")

    for origin in by_id:
        seen = set()
        cursor = origin
        while cursor in successors:
            if cursor in seen:
                errors.append(f"supersession cycle detected at {cursor}")
                break
            seen.add(cursor)
            cursor = successors[cursor]
    return sorted(set(errors))


def read_records(path, *, missing_ok=False):
    path = Path(path)
    if not path.exists():
        if missing_ok:
            return []
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    try:
        parsed = json_loads_strict(text)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json_loads_strict(line))
            except (json.JSONDecodeError, ValueError) as error:
                raise LearningContractError(f"{path}:{line_number}: invalid JSONL: {error}") from error
        return records
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return parsed
    raise LearningContractError(f"{path}: expected a JSON object, array, or JSONL records")


def read_store_records(path, *, missing_ok=False):
    """Read the append-only store and reject formats that cannot be safely appended."""
    path = Path(path)
    if not path.exists():
        if missing_ok:
            return []
        raise FileNotFoundError(path)
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json_loads_strict(line)
        except (json.JSONDecodeError, ValueError) as error:
            raise LearningContractError(f"{path}:{line_number}: invalid JSONL store: {error}") from error
        if not isinstance(record, dict):
            raise LearningContractError(f"{path}:{line_number}: learning store records must be JSON objects")
        records.append(record)
    return records


def _atomic_text_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise LearningContractError(f"refusing to replace symlink: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


@contextmanager
def _exclusive_store_lock(store_path):
    """Serialize the complete read/validate/replace transaction across processes."""
    store_path = Path(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = store_path.with_name(f".{store_path.name}.lock")
    if lock_path.is_symlink():
        raise LearningContractError(f"refusing symlink lock file: {lock_path}")
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(lock_path, flags, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def ingest_events(store_path, event_path, policy_path=DEFAULT_POLICY):
    """Validate a complete batch, then append it atomically without mutating records."""
    policy = load_policy(policy_path)
    store_path = Path(store_path)
    incoming = read_records(event_path)
    if not incoming:
        raise LearningContractError("event input contains no records")
    with _exclusive_store_lock(store_path):
        existing = read_store_records(store_path, missing_ok=True)
        existing_ids = {item.get("event_id") for item in existing if isinstance(item, dict)}
        repeated = sorted(
            event.get("event_id")
            for event in incoming
            if isinstance(event, dict) and event.get("event_id") in existing_ids
        )
        if repeated:
            raise LearningContractError(f"event_id already exists: {', '.join(repeated)}")
        combined = existing + incoming
        _raise_errors(validate_event_set(combined, policy))

        original = store_path.read_text(encoding="utf-8") if store_path.exists() else ""
        if original and not original.endswith("\n"):
            original += "\n"
        appended = "".join(canonical_json(event) + "\n" for event in incoming)
        _atomic_text_write(store_path, original + appended)
    return {
        "status": "ingested",
        "store": str(store_path),
        "added": len(incoming),
        "total": len(combined),
        "automatic_promotion": False,
        "human_review_required": True,
    }


def _candidate_identity(event):
    pattern = event["pattern"]
    return {
        "pattern_key": pattern["key"],
        "pattern_value": pattern["value"],
        "decision_domain": pattern["decision_domain"],
        "variant_axis": pattern["variant_axis"],
        "template_family_id": pattern["template_family_id"],
        "variant_id": pattern["variant_id"],
        "variation_mode": pattern["variation_mode"],
        "applicability": pattern["applicability"],
        "scope": event["scope"],
    }


def _comparison_identity(identity):
    return canonical_json(
        {
            "pattern_key": identity["pattern_key"],
            "decision_domain": identity["decision_domain"],
            "variant_axis": identity["variant_axis"],
            "template_family_id": identity["template_family_id"],
            "variant_id": identity["variant_id"],
            "variation_mode": identity["variation_mode"],
            "applicability": identity["applicability"],
            "scope": identity["scope"],
        }
    )


def _portfolio_identity(identity):
    return canonical_json(
        {
            "template_family_id": identity["template_family_id"],
            "applicability": identity["applicability"],
        }
    )


def _active_events(events):
    superseded_ids = {event["supersedes_event_id"] for event in events if event["supersedes_event_id"]}
    return [event for event in events if event["event_id"] not in superseded_ids], superseded_ids


def _summarize_candidate(group_events, historical_superseded, type_weights):
    by_context = defaultdict(list)
    for event in group_events:
        by_context[event["context"]["independent_context_id"]].append(event)

    support_weight = 0.0
    opposition_weight = 0.0
    support_contexts = 0
    oppose_contexts = 0
    conflicted_contexts = 0
    neutral_contexts = 0
    evidence_types = set()
    explicit_human_supports = 0
    explicit_human_oppositions = 0
    measured_supports = 0
    performance_sample_size = 0
    videos = set()
    projects = set()
    series = set()
    hard_gate_counts = {"pass": 0, "fail": 0, "not_run": 0}
    hard_gate_ids = set()
    for event in group_events:
        hard_gate = event["evidence"]["hard_gate"]
        if hard_gate is not None:
            hard_gate_counts[hard_gate["status"]] += 1
            hard_gate_ids.add(hard_gate["gate_id"])

    for context_events in by_context.values():
        supports = [event for event in context_events if event["evidence"]["signal"] == "supports"]
        opposes = [event for event in context_events if event["evidence"]["signal"] == "opposes"]
        context_support = max(
            (event["evidence"]["weight"] * type_weights[event["evidence_type"]] for event in supports),
            default=0.0,
        )
        context_oppose = max(
            (event["evidence"]["weight"] * type_weights[event["evidence_type"]] for event in opposes),
            default=0.0,
        )
        support_weight += context_support
        opposition_weight += context_oppose
        if context_support and context_oppose:
            conflicted_contexts += 1
        if any(event["evidence"]["explicit_human"] for event in opposes):
            explicit_human_oppositions += 1
        if context_support > context_oppose:
            support_contexts += 1
            evidence_types.update(event["evidence_type"] for event in supports)
            if any(event["evidence"]["explicit_human"] for event in supports):
                explicit_human_supports += 1
            if any(event["evidence"]["measured"] for event in supports):
                measured_supports += 1
            performance_sample_size += max(
                (
                    event["evidence"]["sample_size"]
                    for event in supports
                    if event["evidence_type"] == "performance"
                ),
                default=0,
            )
            for event in supports:
                context = event["context"]
                projects.add(context["project_id"])
                if context["video_id"]:
                    videos.add(context["video_id"])
                if context["series_id"]:
                    series.add(context["series_id"])
        elif context_oppose > context_support:
            oppose_contexts += 1
        else:
            neutral_contexts += 1

    total_weight = support_weight + opposition_weight
    positive_ratio = support_weight / total_weight if total_weight else 0.0
    return {
        "active_event_count": len(group_events),
        "support_contexts": support_contexts,
        "oppose_contexts": oppose_contexts,
        "conflicted_contexts": conflicted_contexts,
        "neutral_contexts": neutral_contexts,
        "revocation_count": sum(event["evidence"]["signal"] == "revokes" for event in group_events),
        "actively_revoked": any(event["evidence"]["signal"] == "revokes" for event in group_events),
        "hard_gate_passes": hard_gate_counts["pass"],
        "hard_gate_failures": hard_gate_counts["fail"],
        "hard_gate_not_run": hard_gate_counts["not_run"],
        "hard_gate_ids": sorted(hard_gate_ids),
        "support_weight": round(support_weight, 6),
        "opposition_weight": round(opposition_weight, 6),
        "positive_ratio": round(positive_ratio, 6),
        "unique_videos": len(videos),
        "unique_projects": len(projects),
        "unique_series": len(series),
        "evidence_types": sorted(evidence_types),
        "explicit_human_supports": explicit_human_supports,
        "explicit_human_oppositions": explicit_human_oppositions,
        "measured_supports": measured_supports,
        "performance_sample_size": performance_sample_size,
        "source_event_ids": sorted(event["event_id"] for event in group_events),
        "superseded_event_ids": sorted(historical_superseded),
    }


def _threshold_blockers(identity, evidence, threshold, policy, alternative_margin, relative_rank, competitor_count):
    blockers = []
    if evidence["actively_revoked"]:
        blockers.append("actively_revoked")
    if evidence["hard_gate_failures"]:
        blockers.append("active_hard_gate_failure")
    if evidence["hard_gate_not_run"]:
        blockers.append("hard_gate_not_run")
    if evidence["explicit_human_oppositions"]:
        blockers.append("active_explicit_human_opposition")
    if evidence["support_contexts"] == 0:
        blockers.append("no_active_support")
    checks = (
        ("support_contexts", "min_support_contexts", "insufficient_independent_support_contexts"),
        ("unique_videos", "min_unique_videos", "insufficient_video_diversity"),
        ("unique_projects", "min_unique_projects", "insufficient_project_diversity"),
        ("unique_series", "min_unique_series", "insufficient_series_diversity"),
    )
    for observed, required, label in checks:
        if evidence[observed] < threshold[required]:
            blockers.append(label)
    required_evidence_types = 1 if identity["decision_domain"] == "technical_contract" else threshold["min_evidence_types"]
    if len(evidence["evidence_types"]) < required_evidence_types:
        blockers.append("insufficient_evidence_type_diversity")

    required_human_supports = (
        0 if identity["decision_domain"] == "technical_contract" else threshold["min_explicit_human_supports"]
    )
    if evidence["explicit_human_supports"] < required_human_supports:
        blockers.append("insufficient_explicit_human_support")
    if evidence["positive_ratio"] < threshold["min_positive_ratio"]:
        blockers.append("opposition_or_ambiguity_above_scope_limit")
    if evidence["evidence_types"] == ["performance"] and not policy["safeguards"]["performance_alone_may_promote"]:
        blockers.append("performance_only_cannot_promote")
    if identity["variation_mode"] == "exploratory" and not policy["safeguards"]["exploratory_variants_may_promote"]:
        blockers.append("exploratory_variant_requires_controlled_test")
    if relative_rank > 1:
        blockers.append("better_supported_alternative_within_same_variant_context")
    if competitor_count > 1 and (
        alternative_margin <= 0 or alternative_margin < threshold["min_alternative_margin"]
    ):
        blockers.append("ambiguous_alternative_within_same_variant_context")
    return sorted(set(blockers))


def _recommendation(blockers, evidence):
    if evidence["actively_revoked"]:
        return "retire"
    if not blockers:
        return "eligible_for_portfolio_review"
    hard = {
        "performance_only_cannot_promote",
        "exploratory_variant_requires_controlled_test",
        "better_supported_alternative_within_same_variant_context",
        "ambiguous_alternative_within_same_variant_context",
        "active_hard_gate_failure",
        "hard_gate_not_run",
        "active_explicit_human_opposition",
    }
    if hard.intersection(blockers):
        return "blocked"
    if evidence["support_contexts"] == 0 and evidence["opposition_weight"] == 0:
        return "observe"
    if evidence["opposition_weight"] > evidence["support_weight"]:
        return "do_not_promote"
    return "test_more"


def _evidence_level(evidence, recommendation):
    if recommendation == "retire":
        return "deprecated"
    if recommendation == "eligible_for_portfolio_review":
        return "promotion_candidate"
    if evidence["support_contexts"] == 0:
        return "insufficient"
    if evidence["support_contexts"] == 1:
        return "observed"
    if evidence["support_contexts"] >= 3 and len(evidence["evidence_types"]) >= 2:
        return "triangulated"
    return "repeated"


def build_recommendation_report(events, policy=None, *, generated_at=None):
    """Build non-binding recommendations without mutating any registry."""
    if policy is None:
        policy = load_policy()
    _raise_errors(validate_event_set(events, policy))
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # Reuse the schema validator for date-time correctness instead of accepting
    # a non-deterministic or malformed report timestamp.
    timestamp_errors = validate_document(
        generated_at,
        {"type": "string", "format": "date-time"},
        "$.generated_at",
    )
    _raise_errors(timestamp_errors)

    active, superseded_ids = _active_events(events)
    active_groups = defaultdict(list)
    historical_by_candidate = defaultdict(list)
    identities = {}
    for event in active:
        identity = _candidate_identity(event)
        key = canonical_json(identity)
        identities[key] = identity
        active_groups[key].append(event)
    for event in events:
        if event["event_id"] in superseded_ids:
            identity = _candidate_identity(event)
            key = canonical_json(identity)
            identities.setdefault(key, identity)
            historical_by_candidate[key].append(event["event_id"])

    type_weights = policy["safeguards"]["evidence_type_weights"]
    drafts = []
    for key in sorted(identities):
        identity = identities[key]
        group_events = active_groups.get(key, [])
        # A fully revoked candidate remains visible through the active revoke
        # event because revocations carry the same candidate identity.
        evidence = _summarize_candidate(group_events, historical_by_candidate[key], type_weights)
        candidate_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16].upper()
        drafts.append(
            {
                "key": key,
                "candidate_id": f"LC-{candidate_hash}",
                "identity": identity,
                "evidence": evidence,
                "net_score": evidence["support_weight"] - evidence["opposition_weight"],
                "comparison_key": _comparison_identity(identity),
            }
        )

    comparisons = defaultdict(list)
    for draft in drafts:
        comparisons[draft["comparison_key"]].append(draft)
    for competing in comparisons.values():
        competing.sort(key=lambda item: (-item["net_score"], item["candidate_id"]))
        top_score = competing[0]["net_score"]
        for index, draft in enumerate(competing):
            rank = 1 + sum(item["net_score"] > draft["net_score"] for item in competing)
            if len(competing) == 1:
                margin = 1.0
            elif math.isclose(draft["net_score"], top_score, abs_tol=1e-12):
                other_scores = [item["net_score"] for item in competing if item is not draft]
                runner_up = max(other_scores)
                denominator = max(abs(draft["net_score"]), abs(runner_up), 1.0)
                margin = max(0.0, min(1.0, (draft["net_score"] - runner_up) / denominator))
            else:
                margin = 0.0
            draft["relative_rank"] = rank
            draft["alternative_margin"] = round(margin, 6)
            draft["competitor_count"] = len(competing)

    candidates = []
    for draft in sorted(drafts, key=lambda item: item["candidate_id"]):
        identity = draft["identity"]
        evidence = draft["evidence"]
        evidence.update(
            {
                "alternative_margin": draft["alternative_margin"],
                "relative_rank_within_variant_context": draft["relative_rank"],
                "competing_value_count": draft["competitor_count"],
            }
        )
        threshold = policy["scope_thresholds"][identity["scope"]["level"]]
        blockers = _threshold_blockers(
            identity,
            evidence,
            threshold,
            policy,
            draft["alternative_margin"],
            draft["relative_rank"],
            draft["competitor_count"],
        )
        recommendation = _recommendation(blockers, evidence)
        safeguards = [
            "exact_scope_only_no_automatic_scope_expansion",
            "exact_applicability_context_only",
            "human_review_required_before_any_registry_change",
            "independent_contexts_count_once_regardless_of_raw_event_volume",
            "performance_sample_size_does_not_multiply_editorial_votes",
            "template_families_form_a_portfolio_no_global_template_winner",
        ]
        questions = [
            "¿La evidencia representa el contexto declarado sin extrapolar a otros formatos o audiencias?",
            "¿El patrón conserva claridad, estructura, lógica, accesibilidad y calidad técnica?",
            "¿Conviene aprobarlo solo para este alcance, continuar probándolo o rechazarlo?",
        ]
        decision_options = [
            "confirm_retirement",
            "reinstate_with_new_evidence",
            "reject_recommendation",
        ] if recommendation == "retire" else [
            "approve_for_exact_scope",
            "continue_testing",
            "reject_candidate",
        ]
        candidates.append(
            {
                "candidate_id": draft["candidate_id"],
                "pattern_key": identity["pattern_key"],
                "pattern_value": identity["pattern_value"],
                "decision_domain": identity["decision_domain"],
                "variant_axis": identity["variant_axis"],
                "template_family_id": identity["template_family_id"],
                "variant_id": identity["variant_id"],
                "variation_mode": identity["variation_mode"],
                "applicability": identity["applicability"],
                "scope": identity["scope"],
                "lifecycle_status": "actively_revoked" if evidence["actively_revoked"] else "active",
                "evidence_level": _evidence_level(evidence, recommendation),
                "recommendation": recommendation,
                "evidence": evidence,
                "blockers": blockers,
                "safeguards": safeguards,
                "human_review": {
                    "required": True,
                    "status": "pending",
                    "decision_options": decision_options,
                    "questions": questions,
                },
            }
        )

    portfolios = defaultdict(list)
    candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
    for candidate in candidates:
        portfolios[
            canonical_json(
                {
                    "template_family_id": candidate["template_family_id"],
                    "applicability": candidate["applicability"],
                }
            )
        ].append(candidate["candidate_id"])
    portfolio_output = []
    for portfolio_identity, candidate_ids in sorted(portfolios.items()):
        identity = json_loads_strict(portfolio_identity)
        digest = hashlib.sha256(portfolio_identity.encode("utf-8")).hexdigest()[:16].upper()
        sorted_ids = sorted(candidate_ids)
        portfolio_output.append(
            {
                "portfolio_key": f"LP-{digest}",
                "template_family_id": identity["template_family_id"],
                "applicability": identity["applicability"],
                "variation_axes": sorted({candidate_by_id[item]["variant_axis"] for item in sorted_ids}),
                "candidate_ids": sorted_ids,
                "eligible_for_human_review_ids": [
                    item
                    for item in sorted_ids
                    if candidate_by_id[item]["recommendation"] == "eligible_for_portfolio_review"
                ],
            }
        )

    warnings = []
    if not events:
        warnings.append("no_evidence_events")
    if candidates and not any(item["recommendation"] == "eligible_for_portfolio_review" for item in candidates):
        warnings.append("no_candidate_currently_meets_human_review_thresholds")
    if any(event["evidence_type"] == "performance" for event in active):
        warnings.append("performance_is_contextual_evidence_not_causal_proof")
    if any(candidate["variation_mode"] == "exploratory" for candidate in candidates):
        warnings.append("exploratory_variants_require_controlled_testing")
    if any(candidate["lifecycle_status"] == "actively_revoked" for candidate in candidates):
        warnings.append("actively_revoked_candidates_must_be_retired_or_explicitly_reinstated")
    if any(candidate["evidence"]["hard_gate_failures"] for candidate in candidates):
        warnings.append("active_hard_gate_failure_blocks_candidate")

    events_hash = document_sha256(events)
    policy_hash = document_sha256(policy)
    report_seed = canonical_json({"events": events_hash, "policy": policy_hash})
    report_id = "LR-" + hashlib.sha256(report_seed.encode("utf-8")).hexdigest()[:16].upper()
    report = {
        "schema_version": "1.0.0",
        "report_id": report_id,
        "generated_at": generated_at,
        "input": {
            "events_sha256": events_hash,
            "policy_id": policy["policy_id"],
            "policy_sha256": policy_hash,
            "event_count": len(events),
            "active_event_count": len(active),
            "superseded_event_count": len(superseded_ids),
        },
        "governance": dict(policy["governance"]),
        "candidates": candidates,
        "portfolio": portfolio_output,
        "warnings": sorted(set(warnings)),
    }
    _raise_errors(_contract_errors(report, REPORT_SCHEMA_PATH, "generated report"))
    return report


def write_report(path, report, *, pretty=True):
    if pretty:
        text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    else:
        text = canonical_json(report) + "\n"
    _atomic_text_write(path, text)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Ingesta evidencia y recomienda patrones contextuales sin promocionarlos automáticamente."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validar eventos sin escribirlos")
    validate_parser.add_argument("--event", required=True, type=Path)
    validate_parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)

    ingest_parser = subparsers.add_parser("ingest", help="Añadir eventos válidos a un JSONL inmutable")
    ingest_parser.add_argument("--store", required=True, type=Path)
    ingest_parser.add_argument("--event", required=True, type=Path)
    ingest_parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)

    recommend_parser = subparsers.add_parser("recommend", help="Crear recomendaciones no vinculantes")
    recommend_parser.add_argument("--store", required=True, type=Path)
    recommend_parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    recommend_parser.add_argument("--output", type=Path)
    recommend_parser.add_argument("--generated-at")
    recommend_parser.add_argument("--compact", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            policy = load_policy(args.policy)
            events = read_records(args.event)
            _raise_errors(validate_event_set(events, policy))
            result = {"status": "valid", "events": len(events)}
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "ingest":
            result = ingest_events(args.store, args.event, args.policy)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "recommend":
            policy = load_policy(args.policy)
            events = read_store_records(args.store, missing_ok=True)
            report = build_recommendation_report(events, policy, generated_at=args.generated_at)
            if args.output:
                write_report(args.output, report, pretty=not args.compact)
                result = {
                    "status": "report_written",
                    "output": str(args.output),
                    "candidates": len(report["candidates"]),
                    "eligible_for_human_review": sum(
                        candidate["recommendation"] == "eligible_for_portfolio_review"
                        for candidate in report["candidates"]
                    ),
                    "automatic_promotion": False,
                }
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            elif args.compact:
                print(canonical_json(report))
            else:
                print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))
            return 0
    except (FileNotFoundError, LearningContractError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
