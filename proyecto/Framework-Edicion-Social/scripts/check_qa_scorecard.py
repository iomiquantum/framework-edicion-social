#!/usr/bin/env python3
"""Validate QA scorecard semantics and gate delivery.

Exit codes:
  0  scorecard is delivery-ready, or valid under --validate-only
  1  scorecard is valid but delivery remains blocked/pending
  2  scorecard is internally invalid or unreadable

The QA schema uses Draft 2020-12 references and conditionals. This checker does
not route it through the framework's intentionally small schema validator;
instead it enforces the delivery semantics explicitly.

``--validate-only`` is deliberately restricted to the untouched initial
template. It is never a delivery-gate bypass for a populated scorecard.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


STATUSES = {"pass", "warn", "fail", "not_run"}
HARD_MODES = {"automatic", "hybrid"}
EXPECTED_SCHEMA_REFERENCE = "../schemas/qa-scorecard.schema.json"
EXPECTED_SCHEMA_VERSION = "1.0.0"
DEVICES = {
    "headphones",
    "studio_monitors",
    "phone_speaker",
    "phone_screen",
    "desktop_speaker",
    "platform_preview",
}
EVIDENCE_KINDS = {
    "command_output",
    "metric",
    "artifact",
    "timestamp_range",
    "frame",
    "transcript_alignment",
    "waveform",
    "listening_observation",
    "visual_observation",
    "platform_preview",
}
REQUIRED_SECTIONS = (
    "source_and_take",
    "phonemes_and_cadence",
    "captions",
    "face_gestures_and_safe_zones",
    "semantic_visuals",
    "color",
    "audio_and_sfx",
    "structure_hook_and_cta",
    "technical_validation",
    "device_playback",
)
EXPECTED_POLICY = {
    "status_values": ["pass", "warn", "fail", "not_run"],
    "any_hard_fail_blocks_delivery": True,
    "required_hard_not_run_blocks_delivery": True,
    "hard_fail_exception_override_allowed": False,
    "evaluated_check_requires_evidence": True,
    "warn_or_fail_requires_note": True,
    "time_evidence_uses_final_render_timeline": True,
}
HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
HARD_ID_PATTERN = re.compile(r"^HG-[A-Z]+-[0-9]{3}$")
EDITORIAL_ID_PATTERN = re.compile(r"^ED-[A-Z]+-[0-9]{3}$")
EVIDENCE_ID_PATTERN = re.compile(r"^EVID-[A-Z0-9-]+$")
EXCEPTION_ID_PATTERN = re.compile(r"^EXC-[A-Z0-9-]+$")
TOP_LEVEL_FIELDS = {
    "$schema",
    "schema_version",
    "scorecard_id",
    "project_id",
    "video_id",
    "render_id",
    "evaluated_at",
    "policy",
    "artifacts",
    "sections",
    "exceptions",
    "editorial_signoff",
    "summary",
}
ARTIFACT_FIELDS = {
    "source_manifest_path",
    "source_sha256",
    "approved_take_id",
    "transcript_path",
    "transcript_sha256",
    "cut_plan_path",
    "cut_plan_sha256",
    "render_path",
    "render_sha256",
    "render_manifest_path",
    "framework_version",
    "hyperframes_version",
}
SUMMARY_FIELDS = {
    "hard_gate_counts",
    "editorial_counts",
    "hard_gate_status",
    "editorial_status",
    "delivery_decision",
    "delivery_allowed",
    "blocking_check_ids",
    "warning_check_ids",
    "unresolved_exception_ids",
    "notes",
}
COUNT_FIELDS = {"total", "pass", "warn", "fail", "not_run"}
SIGNOFF_FIELDS = {"status", "reviewer", "reviewed_at", "accepted_exception_ids", "notes"}
HARD_CHECK_FIELDS = {
    "id",
    "title",
    "requirement",
    "required",
    "verification_mode",
    "status",
    "evidence",
    "notes",
    "exception_ids",
}
EDITORIAL_CHECK_FIELDS = {
    "id",
    "title",
    "review_question",
    "required",
    "verification_mode",
    "status",
    "evidence",
    "notes",
    "exception_ids",
}
EVIDENCE_FIELDS = {
    "evidence_id",
    "kind",
    "artifact_path",
    "artifact_sha256",
    "start_s",
    "end_s",
    "frame",
    "device",
    "command",
    "metric",
    "value",
    "unit",
    "observed_by",
    "recorded_at",
    "note",
}
EXCEPTION_FIELDS = {
    "id",
    "check_ids",
    "start_s",
    "end_s",
    "reason",
    "risk",
    "compensating_controls",
    "requested_by",
    "approved_by",
    "approved_at",
    "disposition",
    "hard_gate_override",
}


def _finding(code, path, message):
    return {"code": code, "path": path, "message": message}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        or isinstance(value, float)
        and math.isfinite(value)
    )


def _validate_shape(item, path, required, allowed, errors):
    for key in sorted(required - set(item)):
        errors.append(_finding("FIELD_MISSING", f"{path}.{key}", "required field is missing"))
    for key in sorted(set(item) - allowed):
        errors.append(_finding("FIELD_UNKNOWN", f"{path}.{key}", "unknown field"))


def _string_list(value, path, errors, *, pattern=None):
    if not isinstance(value, list):
        errors.append(_finding("LIST_TYPE", path, "must be an array of strings"))
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append(_finding("LIST_ITEM", f"{path}[{index}]", "must be a string"))
            continue
        if pattern is not None and not pattern.fullmatch(item):
            errors.append(_finding("LIST_ITEM", f"{path}[{index}]", "has an invalid identifier"))
            continue
        result.append(item)
    if len(result) != len(set(result)):
        errors.append(_finding("LIST_DUPLICATE", path, "array values must be unique"))
    return result


def _validate_declared_counts(value, path, errors):
    if not isinstance(value, dict):
        errors.append(_finding("COUNTS_TYPE", path, "must be an object of non-negative integers"))
        return
    _validate_shape(value, path, COUNT_FIELDS, COUNT_FIELDS, errors)
    for field in COUNT_FIELDS:
        count = value.get(field)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            errors.append(_finding("COUNT_VALUE", f"{path}.{field}", "must be a non-negative integer"))
    values = [value.get(field) for field in ("pass", "warn", "fail", "not_run")]
    if all(isinstance(item, int) and not isinstance(item, bool) and item >= 0 for item in values):
        total = value.get("total")
        if isinstance(total, int) and not isinstance(total, bool) and total != sum(values):
            errors.append(_finding("COUNT_TOTAL", f"{path}.total", "must equal pass + warn + fail + not_run"))


def _is_machine_evidence_linked_to_render(item, render_sha256):
    if not isinstance(item, dict) or item.get("artifact_sha256") != render_sha256:
        return False
    if item.get("kind") == "command_output":
        return _nonempty(item.get("command"))
    if item.get("kind") == "metric":
        return (
            _nonempty(item.get("metric"))
            and item.get("value") is not None
            and _nonempty(item.get("unit"))
        )
    return False


def _validate_evidence(item, path, evidence_ids, errors):
    if not isinstance(item, dict):
        errors.append(_finding("EVIDENCE_TYPE", path, "evidence must be an object"))
        return
    _validate_shape(item, path, {"evidence_id", "kind", "note"}, EVIDENCE_FIELDS, errors)
    evidence_id = item.get("evidence_id")
    if not isinstance(evidence_id, str) or not EVIDENCE_ID_PATTERN.fullmatch(evidence_id):
        errors.append(_finding("EVIDENCE_ID", f"{path}.evidence_id", "invalid evidence id"))
    elif evidence_id in evidence_ids:
        errors.append(_finding("EVIDENCE_ID_DUPLICATE", f"{path}.evidence_id", f"duplicate evidence id {evidence_id}"))
    else:
        evidence_ids.add(evidence_id)

    kind = item.get("kind")
    if not isinstance(kind, str) or kind not in EVIDENCE_KINDS:
        errors.append(_finding("EVIDENCE_KIND", f"{path}.kind", f"unsupported evidence kind {kind!r}"))
    if not _nonempty(item.get("note")):
        errors.append(_finding("EVIDENCE_NOTE", f"{path}.note", "evidence note is required"))

    for field in ("artifact_path", "command", "metric", "unit", "observed_by", "recorded_at"):
        value = item.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(_finding("EVIDENCE_FIELD_TYPE", f"{path}.{field}", "must be a string or null"))
    device = item.get("device")
    if device is not None and (not isinstance(device, str) or device not in DEVICES):
        errors.append(_finding("EVIDENCE_DEVICE", f"{path}.device", "must be a supported device or null"))
    value = item.get("value")
    if value is not None and (
        not isinstance(value, (str, int, float, bool))
        or isinstance(value, float) and not math.isfinite(value)
    ):
        errors.append(_finding("EVIDENCE_VALUE_TYPE", f"{path}.value", "must be a finite scalar or null"))

    start = item.get("start_s")
    end = item.get("end_s")
    if (start is None) != (end is None):
        errors.append(_finding("EVIDENCE_TIME_PAIR", path, "start_s and end_s must be supplied together"))
    if start is not None and (not _number(start) or start < 0):
        errors.append(_finding("EVIDENCE_START", f"{path}.start_s", "start_s must be a non-negative number"))
    if end is not None and (not _number(end) or end < 0):
        errors.append(_finding("EVIDENCE_END", f"{path}.end_s", "end_s must be a non-negative number"))
    if _number(start) and _number(end) and end < start:
        errors.append(_finding("EVIDENCE_TIME_ORDER", path, "end_s precedes start_s"))

    if kind == "timestamp_range" and (not _number(start) or not _number(end)):
        errors.append(_finding("EVIDENCE_TIME_REQUIRED", path, "timestamp_range requires numeric start_s and end_s"))
    if kind == "frame":
        frame = item.get("frame")
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
            errors.append(_finding("EVIDENCE_FRAME", f"{path}.frame", "frame evidence requires a non-negative integer"))
    elif item.get("frame") is not None and (
        not isinstance(item.get("frame"), int)
        or isinstance(item.get("frame"), bool)
        or item.get("frame") < 0
    ):
        errors.append(_finding("EVIDENCE_FRAME", f"{path}.frame", "frame must be a non-negative integer or null"))
    if kind == "metric" and (
        not _nonempty(item.get("metric"))
        or item.get("value") is None
        or not _nonempty(item.get("unit"))
    ):
        errors.append(_finding("EVIDENCE_METRIC", path, "metric evidence requires metric, non-null value, and unit"))
    if kind == "command_output" and not _nonempty(item.get("command")):
        errors.append(_finding("EVIDENCE_COMMAND", path, "command_output evidence requires command"))
    if kind == "artifact" and not _nonempty(item.get("artifact_path")):
        errors.append(_finding("EVIDENCE_ARTIFACT", path, "artifact evidence requires artifact_path"))
    if kind == "listening_observation":
        if not isinstance(item.get("device"), str) or item.get("device") not in DEVICES:
            errors.append(_finding("EVIDENCE_DEVICE", f"{path}.device", "listening evidence requires a supported device"))
        if not _nonempty(item.get("observed_by")):
            errors.append(_finding("EVIDENCE_OBSERVER", f"{path}.observed_by", "listening evidence requires observed_by"))

    artifact_hash = item.get("artifact_sha256")
    if artifact_hash is not None and (not isinstance(artifact_hash, str) or not HASH_PATTERN.fullmatch(artifact_hash)):
        errors.append(_finding("EVIDENCE_HASH", f"{path}.artifact_sha256", "artifact hash must be 64 lowercase hex characters"))


def _validate_check(
    item,
    path,
    kind,
    check_ids,
    evidence_ids,
    errors,
    *,
    template_mode,
    render_sha256,
):
    if not isinstance(item, dict):
        errors.append(_finding("CHECK_TYPE", path, "check must be an object"))
        return None
    fields = HARD_CHECK_FIELDS if kind == "hard" else EDITORIAL_CHECK_FIELDS
    _validate_shape(item, path, fields, fields, errors)
    check_id = item.get("id")
    pattern = HARD_ID_PATTERN if kind == "hard" else EDITORIAL_ID_PATTERN
    if not isinstance(check_id, str) or not pattern.fullmatch(check_id):
        errors.append(_finding("CHECK_ID", f"{path}.id", f"invalid {kind} check id"))
    elif check_id in check_ids:
        errors.append(_finding("CHECK_ID_DUPLICATE", f"{path}.id", f"duplicate check id {check_id}"))
    else:
        check_ids.add(check_id)

    status = item.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        errors.append(_finding("CHECK_STATUS", f"{path}.status", f"invalid status {status!r}"))
    if not isinstance(item.get("required"), bool):
        errors.append(_finding("CHECK_REQUIRED", f"{path}.required", "required must be boolean"))
    mode = item.get("verification_mode")
    if kind == "hard" and (not isinstance(mode, str) or mode not in HARD_MODES):
        errors.append(_finding("CHECK_MODE", f"{path}.verification_mode", "hard gate mode must be automatic or hybrid"))
    if kind == "editorial" and mode != "human":
        errors.append(_finding("CHECK_MODE", f"{path}.verification_mode", "editorial criteria must use human verification"))
    if not isinstance(item.get("title"), str) or len(item.get("title", "").strip()) < 3:
        errors.append(_finding("CHECK_TITLE", f"{path}.title", "title must contain at least 3 characters"))
    statement_field = "requirement" if kind == "hard" else "review_question"
    statement = item.get(statement_field)
    if not isinstance(statement, str) or len(statement.strip()) < 8:
        errors.append(
            _finding(
                "CHECK_STATEMENT",
                f"{path}.{statement_field}",
                f"{statement_field} must contain at least 8 characters",
            )
        )
    if not isinstance(item.get("notes"), str):
        errors.append(_finding("CHECK_NOTES", f"{path}.notes", "notes must be a string"))

    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        errors.append(_finding("CHECK_EVIDENCE_TYPE", f"{path}.evidence", "evidence must be an array"))
        evidence = []
    if isinstance(status, str) and status in {"pass", "warn", "fail"} and not evidence:
        errors.append(_finding("CHECK_EVIDENCE_MISSING", f"{path}.evidence", "an evaluated check requires evidence"))
    if isinstance(status, str) and status in {"warn", "fail"} and not _nonempty(item.get("notes")):
        errors.append(_finding("CHECK_NOTE_MISSING", f"{path}.notes", "warn or fail requires a note"))
    if (
        not template_mode
        and item.get("required") is False
        and status == "not_run"
        and not _nonempty(item.get("notes"))
    ):
        errors.append(
            _finding(
                "CHECK_NOT_APPLICABLE_NOTE",
                f"{path}.notes",
                "optional not_run requires a note explaining why the check does not apply",
            )
        )
    for index, evidence_item in enumerate(evidence):
        _validate_evidence(evidence_item, f"{path}.evidence[{index}]", evidence_ids, errors)
    if (
        kind == "hard"
        and mode == "automatic"
        and isinstance(status, str)
        and status in {"pass", "warn", "fail"}
    ):
        linked = any(
            _is_machine_evidence_linked_to_render(evidence_item, render_sha256)
            for evidence_item in evidence
        )
        if not linked:
            errors.append(
                _finding(
                    "AUTOMATIC_EVIDENCE",
                    f"{path}.evidence",
                    "evaluated automatic gate requires command_output or metric evidence linked to render_sha256",
                )
            )

    exception_ids = _string_list(
        item.get("exception_ids"),
        f"{path}.exception_ids",
        errors,
        pattern=EXCEPTION_ID_PATTERN,
    )

    return {
        "id": check_id if isinstance(check_id, str) else f"invalid:{path}",
        "kind": kind,
        "required": item.get("required") is True,
        "status": status if isinstance(status, str) else None,
        "exception_ids": exception_ids,
    }


def _counts(checks):
    counter = Counter(
        item["status"]
        for item in checks
        if isinstance(item.get("status"), str) and item.get("status") in STATUSES
    )
    return {
        "total": len(checks),
        "pass": counter["pass"],
        "warn": counter["warn"],
        "fail": counter["fail"],
        "not_run": counter["not_run"],
    }


def _aggregate(checks):
    relevant = [item for item in checks if item.get("required")]
    statuses = {item.get("status") for item in relevant}
    if "fail" in statuses:
        return "fail"
    if "not_run" in statuses or not relevant:
        return "not_run"
    if "warn" in statuses:
        return "warn"
    return "pass"


def analyze_scorecard(data, *, template_mode=False):
    """Return structural errors plus the independently computed delivery gate.

    ``template_mode`` only permits the intentionally blank optional checks in
    the repository's initial template. Delivery callers must keep it false.
    """
    errors = []
    if not isinstance(data, dict):
        return {
            "valid": False,
            "delivery_ready": False,
            "status": "invalid",
            "counts": {"hard": _counts([]), "editorial": _counts([])},
            "blockers": ["scorecard"],
            "warnings": [],
            "errors": [_finding("ROOT_TYPE", "$", "scorecard must be an object")],
        }

    _validate_shape(data, "$", TOP_LEVEL_FIELDS, TOP_LEVEL_FIELDS, errors)
    if data.get("$schema") != EXPECTED_SCHEMA_REFERENCE:
        errors.append(
            _finding(
                "SCHEMA_URI",
                "$.$schema",
                f"expected {EXPECTED_SCHEMA_REFERENCE!r}",
            )
        )
    schema_version = data.get("schema_version")
    if schema_version != EXPECTED_SCHEMA_VERSION:
        errors.append(
            _finding(
                "SCHEMA_VERSION",
                "$.schema_version",
                f"expected {EXPECTED_SCHEMA_VERSION!r}",
            )
        )
    for field in ("scorecard_id", "project_id", "video_id", "render_id", "evaluated_at"):
        if not isinstance(data.get(field), str):
            errors.append(_finding("IDENTITY_TYPE", f"$.{field}", "must be a string"))

    policy = data.get("policy")
    if not isinstance(policy, dict):
        errors.append(_finding("POLICY_MISSING", "$.policy", "policy object is required"))
    else:
        _validate_shape(policy, "$.policy", set(EXPECTED_POLICY), set(EXPECTED_POLICY), errors)
        for key, expected in EXPECTED_POLICY.items():
            actual = policy.get(key)
            matches = actual is expected if isinstance(expected, bool) else type(actual) is type(expected) and actual == expected
            if not matches:
                errors.append(_finding("POLICY_DRIFT", f"$.policy.{key}", f"expected {expected!r}"))

    sections = data.get("sections")
    if not isinstance(sections, dict):
        errors.append(_finding("SECTIONS_MISSING", "$.sections", "sections object is required"))
        sections = {}
    missing_sections = [name for name in REQUIRED_SECTIONS if name not in sections]
    extra_sections = [name for name in sections if name not in REQUIRED_SECTIONS]
    for name in missing_sections:
        errors.append(_finding("SECTION_MISSING", f"$.sections.{name}", "required QA section is missing"))
    for name in extra_sections:
        errors.append(_finding("SECTION_UNKNOWN", f"$.sections.{name}", "unknown QA section"))

    check_ids = set()
    evidence_ids = set()
    hard_checks = []
    editorial_checks = []
    raw_artifacts = data.get("artifacts")
    render_sha256 = raw_artifacts.get("render_sha256") if isinstance(raw_artifacts, dict) else None
    for section_name in REQUIRED_SECTIONS:
        section = sections.get(section_name)
        section_path = f"$.sections.{section_name}"
        if not isinstance(section, dict):
            if section_name in sections:
                errors.append(_finding("SECTION_TYPE", section_path, "section must be an object"))
            continue
        _validate_shape(
            section,
            section_path,
            {"hard_gates", "editorial_criteria"},
            {"hard_gates", "editorial_criteria"},
            errors,
        )
        hard = section.get("hard_gates")
        editorial = section.get("editorial_criteria")
        if not isinstance(hard, list) or not hard:
            errors.append(_finding("HARD_GATES_MISSING", f"{section_path}.hard_gates", "section requires at least one hard gate"))
            hard = []
        if not isinstance(editorial, list):
            errors.append(_finding("EDITORIAL_TYPE", f"{section_path}.editorial_criteria", "editorial_criteria must be an array"))
            editorial = []
        for index, item in enumerate(hard):
            record = _validate_check(
                item,
                f"{section_path}.hard_gates[{index}]",
                "hard",
                check_ids,
                evidence_ids,
                errors,
                template_mode=template_mode,
                render_sha256=render_sha256,
            )
            if record:
                hard_checks.append(record)
        for index, item in enumerate(editorial):
            record = _validate_check(
                item,
                f"{section_path}.editorial_criteria[{index}]",
                "editorial",
                check_ids,
                evidence_ids,
                errors,
                template_mode=template_mode,
                render_sha256=render_sha256,
            )
            if record:
                editorial_checks.append(record)

    exceptions = data.get("exceptions")
    if not isinstance(exceptions, list):
        errors.append(_finding("EXCEPTIONS_TYPE", "$.exceptions", "exceptions must be an array"))
        exceptions = []
    exception_by_id = {}
    unresolved_exception_ids = []
    for index, item in enumerate(exceptions):
        path = f"$.exceptions[{index}]"
        if not isinstance(item, dict):
            errors.append(_finding("EXCEPTION_TYPE", path, "exception must be an object"))
            continue
        _validate_shape(item, path, EXCEPTION_FIELDS, EXCEPTION_FIELDS, errors)
        exception_id = item.get("id")
        if not isinstance(exception_id, str) or not EXCEPTION_ID_PATTERN.fullmatch(exception_id):
            errors.append(_finding("EXCEPTION_ID", f"{path}.id", "invalid exception id"))
            continue
        if exception_id in exception_by_id:
            errors.append(_finding("EXCEPTION_DUPLICATE", f"{path}.id", f"duplicate exception id {exception_id}"))
            continue
        exception_by_id[exception_id] = item
        if item.get("hard_gate_override") is not False:
            errors.append(_finding("HARD_OVERRIDE_FORBIDDEN", f"{path}.hard_gate_override", "hard gate override must be false"))
        referenced = _string_list(item.get("check_ids"), f"{path}.check_ids", errors)
        if not referenced:
            errors.append(_finding("EXCEPTION_CHECKS", f"{path}.check_ids", "exception must reference at least one check"))
        for check_id in referenced:
            if check_id not in check_ids:
                errors.append(_finding("EXCEPTION_UNKNOWN_CHECK", f"{path}.check_ids", f"unknown check {check_id}"))
        if not isinstance(item.get("reason"), str) or len(item.get("reason", "").strip()) < 8:
            errors.append(_finding("EXCEPTION_REASON", f"{path}.reason", "reason must contain at least 8 characters"))
        if not isinstance(item.get("risk"), str) or len(item.get("risk", "").strip()) < 8:
            errors.append(_finding("EXCEPTION_RISK", f"{path}.risk", "risk must contain at least 8 characters"))
        start = item.get("start_s")
        end = item.get("end_s")
        if (start is None) != (end is None):
            errors.append(_finding("EXCEPTION_TIME_PAIR", path, "start_s and end_s must be supplied together"))
        if start is not None and (not _number(start) or start < 0):
            errors.append(_finding("EXCEPTION_START", f"{path}.start_s", "must be a non-negative number or null"))
        if end is not None and (not _number(end) or end < 0):
            errors.append(_finding("EXCEPTION_END", f"{path}.end_s", "must be a non-negative number or null"))
        if _number(start) and _number(end) and end < start:
            errors.append(_finding("EXCEPTION_TIME_ORDER", path, "end_s precedes start_s"))
        controls = _string_list(item.get("compensating_controls"), f"{path}.compensating_controls", errors)
        for field in ("requested_by", "approved_by", "approved_at"):
            if not isinstance(item.get(field), str):
                errors.append(_finding("EXCEPTION_FIELD_TYPE", f"{path}.{field}", "must be a string"))
        disposition = item.get("disposition")
        if not isinstance(disposition, str) or disposition not in {"pending", "accepted", "rejected", "superseded"}:
            errors.append(_finding("EXCEPTION_DISPOSITION", f"{path}.disposition", "invalid exception disposition"))
        if disposition == "pending":
            unresolved_exception_ids.append(exception_id)
        if disposition == "accepted":
            if not _nonempty(item.get("approved_by")) or not _nonempty(item.get("approved_at")):
                errors.append(_finding("EXCEPTION_APPROVAL", path, "accepted exception requires approver and date"))
            if not controls or not all(_nonempty(value) for value in controls):
                errors.append(_finding("EXCEPTION_CONTROLS", path, "accepted exception requires compensating controls"))

        # Store normalized identifiers for link checks; malformed raw values must
        # never crash the checker while it is trying to explain the error.
        item = dict(item)
        item["check_ids"] = referenced
        exception_by_id[exception_id] = item

    checks_by_id = {item["id"]: item for item in hard_checks + editorial_checks if isinstance(item.get("id"), str)}
    for check in hard_checks + editorial_checks:
        for exception_id in check["exception_ids"]:
            exception = exception_by_id.get(exception_id)
            if not exception:
                errors.append(_finding("CHECK_UNKNOWN_EXCEPTION", f"check:{check['id']}", f"unknown exception {exception_id}"))
            elif check["id"] not in exception.get("check_ids", []):
                errors.append(_finding("EXCEPTION_LINK_ASYMMETRIC", f"check:{check['id']}", f"exception {exception_id} does not link back"))
    for exception_id, exception in exception_by_id.items():
        for check_id in exception.get("check_ids", []):
            check = checks_by_id.get(check_id)
            if check and exception_id not in check["exception_ids"]:
                errors.append(_finding("EXCEPTION_LINK_ASYMMETRIC", f"exception:{exception_id}", f"check {check_id} does not link back"))

    hard_counts = _counts(hard_checks)
    editorial_counts = _counts(editorial_checks)
    hard_status = _aggregate(hard_checks)
    editorial_status = _aggregate(editorial_checks)
    hard_fail_ids = [item["id"] for item in hard_checks if item.get("status") == "fail"]
    hard_not_run_ids = [item["id"] for item in hard_checks if item.get("required") and item.get("status") == "not_run"]
    editorial_fail_ids = [item["id"] for item in editorial_checks if item.get("status") == "fail"]
    editorial_not_run_ids = [item["id"] for item in editorial_checks if item.get("required") and item.get("status") == "not_run"]
    warning_ids = [item["id"] for item in hard_checks + editorial_checks if item.get("status") == "warn"]

    signoff = data.get("editorial_signoff")
    if not isinstance(signoff, dict):
        errors.append(_finding("SIGNOFF_MISSING", "$.editorial_signoff", "editorial signoff is required"))
        signoff = {}
    else:
        _validate_shape(signoff, "$.editorial_signoff", SIGNOFF_FIELDS, SIGNOFF_FIELDS, errors)
    signoff_status = signoff.get("status")
    if not isinstance(signoff_status, str) or signoff_status not in STATUSES:
        errors.append(_finding("SIGNOFF_STATUS", "$.editorial_signoff.status", "invalid signoff status"))
    accepted_ids = _string_list(
        signoff.get("accepted_exception_ids"),
        "$.editorial_signoff.accepted_exception_ids",
        errors,
        pattern=EXCEPTION_ID_PATTERN,
    )
    for exception_id in accepted_ids:
        exception = exception_by_id.get(exception_id)
        if not exception or exception.get("disposition") != "accepted":
            errors.append(_finding("SIGNOFF_EXCEPTION_INVALID", "$.editorial_signoff.accepted_exception_ids", f"{exception_id} is not an accepted exception"))
    expected_accepted_ids = {
        exception_id
        for exception_id, exception in exception_by_id.items()
        if exception.get("disposition") == "accepted"
    }
    if set(accepted_ids) != expected_accepted_ids:
        errors.append(
            _finding(
                "SIGNOFF_EXCEPTIONS_MISMATCH",
                "$.editorial_signoff.accepted_exception_ids",
                f"expected {sorted(expected_accepted_ids)}",
            )
        )
    for field in ("reviewer", "reviewed_at", "notes"):
        if not isinstance(signoff.get(field), str):
            errors.append(_finding("SIGNOFF_FIELD_TYPE", f"$.editorial_signoff.{field}", "must be a string"))

    summary = data.get("summary")
    if not isinstance(summary, dict):
        errors.append(_finding("SUMMARY_MISSING", "$.summary", "summary object is required"))
        summary = {}
    else:
        _validate_shape(summary, "$.summary", SUMMARY_FIELDS, SUMMARY_FIELDS, errors)
    _validate_declared_counts(summary.get("hard_gate_counts"), "$.summary.hard_gate_counts", errors)
    _validate_declared_counts(summary.get("editorial_counts"), "$.summary.editorial_counts", errors)
    if summary.get("hard_gate_counts") != hard_counts:
        errors.append(_finding("SUMMARY_HARD_COUNTS", "$.summary.hard_gate_counts", f"expected {hard_counts}"))
    if summary.get("editorial_counts") != editorial_counts:
        errors.append(_finding("SUMMARY_EDITORIAL_COUNTS", "$.summary.editorial_counts", f"expected {editorial_counts}"))
    if summary.get("hard_gate_status") != hard_status:
        errors.append(_finding("SUMMARY_HARD_STATUS", "$.summary.hard_gate_status", f"expected {hard_status}"))
    if summary.get("editorial_status") != editorial_status:
        errors.append(_finding("SUMMARY_EDITORIAL_STATUS", "$.summary.editorial_status", f"expected {editorial_status}"))
    blocking_check_ids = _string_list(summary.get("blocking_check_ids"), "$.summary.blocking_check_ids", errors)
    declared_warning_ids = _string_list(summary.get("warning_check_ids"), "$.summary.warning_check_ids", errors)
    declared_unresolved_ids = _string_list(
        summary.get("unresolved_exception_ids"),
        "$.summary.unresolved_exception_ids",
        errors,
        pattern=EXCEPTION_ID_PATTERN,
    )
    actual_blocking_check_ids = set(
        hard_fail_ids + hard_not_run_ids + editorial_fail_ids + editorial_not_run_ids
    )
    unexpected_blocking_ids = sorted(set(blocking_check_ids) - actual_blocking_check_ids)
    if unexpected_blocking_ids:
        errors.append(
            _finding(
                "SUMMARY_BLOCKERS_UNKNOWN",
                "$.summary.blocking_check_ids",
                f"not currently blocking: {unexpected_blocking_ids}",
            )
        )
    if set(declared_warning_ids) != set(warning_ids):
        errors.append(_finding("SUMMARY_WARNINGS", "$.summary.warning_check_ids", f"expected {sorted(warning_ids)}"))
    if set(declared_unresolved_ids) != set(unresolved_exception_ids):
        errors.append(_finding("SUMMARY_EXCEPTIONS", "$.summary.unresolved_exception_ids", f"expected {sorted(unresolved_exception_ids)}"))
    if not isinstance(summary.get("delivery_decision"), str) or summary.get("delivery_decision") not in {"pending", "blocked", "needs_human_review", "ready"}:
        errors.append(_finding("SUMMARY_DECISION", "$.summary.delivery_decision", "invalid delivery decision"))
    if not isinstance(summary.get("delivery_allowed"), bool):
        errors.append(_finding("SUMMARY_ALLOWED", "$.summary.delivery_allowed", "delivery_allowed must be boolean"))
    if not isinstance(summary.get("notes"), str):
        errors.append(_finding("SUMMARY_NOTES", "$.summary.notes", "notes must be a string"))

    metadata_blockers = []
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(_finding("ARTIFACTS_MISSING", "$.artifacts", "artifacts object is required"))
        artifacts = {}
    else:
        _validate_shape(artifacts, "$.artifacts", ARTIFACT_FIELDS, ARTIFACT_FIELDS, errors)
    ready_identity_fields = ("scorecard_id", "project_id", "video_id", "render_id", "evaluated_at")
    for field in ready_identity_fields:
        if not _nonempty(data.get(field)):
            metadata_blockers.append(f"metadata:{field}")
    ready_artifact_fields = (
        "source_manifest_path",
        "source_sha256",
        "approved_take_id",
        "transcript_path",
        "transcript_sha256",
        "cut_plan_path",
        "cut_plan_sha256",
        "render_path",
        "render_sha256",
        "render_manifest_path",
        "framework_version",
        "hyperframes_version",
    )
    for field in ready_artifact_fields:
        value = artifacts.get(field)
        if not isinstance(value, str):
            errors.append(_finding("ARTIFACT_TYPE", f"$.artifacts.{field}", "must be a string"))
        if not _nonempty(value):
            metadata_blockers.append(f"artifact:{field}")
        if field.endswith("sha256") and _nonempty(value) and not HASH_PATTERN.fullmatch(value):
            errors.append(_finding("ARTIFACT_HASH", f"$.artifacts.{field}", "hash must be 64 lowercase hex characters"))
    if isinstance(signoff_status, str) and signoff_status in {"pass", "warn"}:
        if not _nonempty(signoff.get("reviewer")) or not _nonempty(signoff.get("reviewed_at")):
            errors.append(_finding("SIGNOFF_IDENTITY", "$.editorial_signoff", "completed signoff requires reviewer and reviewed_at"))

    hard_blockers = hard_fail_ids + hard_not_run_ids
    editorial_blockers = editorial_fail_ids + editorial_not_run_ids
    blockers = hard_blockers + editorial_blockers + unresolved_exception_ids
    if not isinstance(signoff_status, str) or signoff_status not in {"pass", "warn"}:
        blockers.append("editorial_signoff")
    blockers.extend(metadata_blockers)
    blockers = list(dict.fromkeys(blockers))

    delivery_ready = not errors and not blockers
    declared_allowed = summary.get("delivery_allowed")
    if declared_allowed is not delivery_ready:
        errors.append(_finding("DELIVERY_FLAG", "$.summary.delivery_allowed", f"expected {delivery_ready}"))
        delivery_ready = False
    raw_decision = summary.get("delivery_decision")
    decision = raw_decision if isinstance(raw_decision, str) else None
    if hard_fail_ids:
        if decision != "blocked":
            errors.append(_finding("HARD_FAIL_DECISION", "$.summary.delivery_decision", "any hard fail requires blocked"))
        if declared_allowed is not False:
            errors.append(_finding("HARD_FAIL_ALLOWED", "$.summary.delivery_allowed", "hard fail can never allow delivery"))
        declared_blockers = set(blocking_check_ids)
        missing = sorted(set(hard_fail_ids) - declared_blockers)
        if missing:
            errors.append(_finding("HARD_FAIL_NOT_LISTED", "$.summary.blocking_check_ids", f"missing hard fails {missing}"))
    if hard_not_run_ids and decision not in {"pending", "blocked"}:
        errors.append(_finding("HARD_NOT_RUN_DECISION", "$.summary.delivery_decision", "required hard checks not_run require pending or blocked"))
    if delivery_ready and decision != "ready":
        errors.append(_finding("READY_DECISION", "$.summary.delivery_decision", "delivery-ready scorecard must declare ready"))
        delivery_ready = False
    if decision == "ready" and not delivery_ready:
        errors.append(_finding("PREMATURE_READY", "$.summary.delivery_decision", "scorecard declares ready while blockers remain"))

    status = "invalid" if errors else "ready" if delivery_ready else "blocked"
    return {
        "valid": not errors,
        "delivery_ready": delivery_ready,
        "status": status,
        "counts": {"hard": hard_counts, "editorial": editorial_counts},
        "aggregate": {"hard": hard_status, "editorial": editorial_status},
        "blockers": blockers,
        "warnings": warning_ids,
        "errors": errors,
    }


def load_scorecard(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def is_initial_template(data):
    """Return true only for the untouched, non-deliverable starter template."""
    if not isinstance(data, dict):
        return False
    identity_fields = ("scorecard_id", "project_id", "video_id", "render_id", "evaluated_at")
    if any(data.get(field) != "" for field in identity_fields):
        return False
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or any(artifacts.get(field) != "" for field in ARTIFACT_FIELDS):
        return False
    if data.get("exceptions") != []:
        return False
    signoff = data.get("editorial_signoff")
    if not isinstance(signoff, dict) or signoff != {
        "status": "not_run",
        "reviewer": "",
        "reviewed_at": "",
        "accepted_exception_ids": [],
        "notes": "",
    }:
        return False
    summary = data.get("summary")
    if not isinstance(summary, dict):
        return False
    if (
        summary.get("delivery_decision") != "pending"
        or summary.get("delivery_allowed") is not False
        or summary.get("blocking_check_ids") != []
        or summary.get("warning_check_ids") != []
        or summary.get("unresolved_exception_ids") != []
    ):
        return False
    sections = data.get("sections")
    if not isinstance(sections, dict):
        return False
    for section in sections.values():
        if not isinstance(section, dict):
            return False
        for group in ("hard_gates", "editorial_criteria"):
            checks = section.get(group)
            if not isinstance(checks, list):
                return False
            for check in checks:
                if not isinstance(check, dict):
                    return False
                if (
                    check.get("status") != "not_run"
                    or check.get("evidence") != []
                    or check.get("exception_ids") != []
                    or check.get("notes") != ""
                ):
                    return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--json", action="store_true", help="Print the complete result as JSON")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate only the untouched initial template; never bypasses delivery gates",
    )
    args = parser.parse_args()
    try:
        scorecard = load_scorecard(args.scorecard)
        initial_template = is_initial_template(scorecard)
        report = analyze_scorecard(
            scorecard,
            template_mode=args.validate_only and initial_template,
        )
        if args.validate_only and not initial_template:
            report["errors"].append(
                _finding(
                    "VALIDATE_ONLY_SCOPE",
                    "$",
                    "--validate-only is restricted to the untouched initial template and cannot bypass delivery gates",
                )
            )
            report["valid"] = False
            report["delivery_ready"] = False
            report["status"] = "invalid"
    except (OSError, json.JSONDecodeError) as error:
        report = {
            "valid": False,
            "delivery_ready": False,
            "status": "invalid",
            "counts": {"hard": _counts([]), "editorial": _counts([])},
            "blockers": ["scorecard"],
            "warnings": [],
            "errors": [_finding("READ_ERROR", str(args.scorecard), str(error))],
        }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"QA {report['status'].upper()}: "
            f"{len(report['errors'])} errors, {len(report['blockers'])} blockers, "
            f"{len(report['warnings'])} warnings"
        )
        for item in report["errors"]:
            print(f"- ERROR {item['code']} {item['path']}: {item['message']}")
        if report["blockers"]:
            print(f"- BLOCKERS: {', '.join(report['blockers'])}")

    if not report["valid"]:
        return 2
    if args.validate_only or report["delivery_ready"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
