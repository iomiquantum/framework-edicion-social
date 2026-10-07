#!/usr/bin/env python3
"""Verify publication lineage, ingest metric snapshots, and build non-causal cohorts."""

from __future__ import annotations

import argparse
import csv
import portable_fcntl as fcntl
import hashlib
import io
import json
import math
import os
import re
import stat
import statistics
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import load_json as load_schema_json  # noqa: E402
from schema_validation import validate_document  # noqa: E402
import check_platform_delivery  # noqa: E402
import compose_recipe  # noqa: E402
import plan_platform_derivatives  # noqa: E402


OBS_SCHEMA = FRAMEWORK / "schemas/performance-observation.schema.json"
STORE_SCHEMA = FRAMEWORK / "schemas/performance-store.schema.json"
REPORT_SCHEMA = FRAMEWORK / "schemas/performance-cohort-report.schema.json"
REGISTRY_SCHEMA = FRAMEWORK / "schemas/publication-registry.schema.json"
PRODUCTION_SCHEMA = FRAMEWORK / "schemas/production-metrics.schema.json"
PACKAGE_SCHEMA = FRAMEWORK / "schemas/publish-package.schema.json"
ATTRIBUTION_SCHEMA = FRAMEWORK / "schemas/creative-attribution.schema.json"

WINDOW_TOLERANCE_HOURS = {24: 2.0, 72: 4.0, 168: 8.0}
WINDOWS = set(WINDOW_TOLERANCE_HOURS)
INTEGER_METRICS = {
    "impressions", "reach", "views", "likes", "comments", "shares", "saves",
    "clicks", "conversions",
}
FLOAT_METRICS = {"total_watch_time_s", "average_watch_time_s", "completion_rate"}
CUMULATIVE_METRICS = INTEGER_METRICS | {"total_watch_time_s"}
CONTENT_FIELDS = (
    "primary_family_id", "recipe_id", "hook_id", "structure_id", "visual_system_id",
    "motion_id", "sound_id", "cta_id",
)
MODULE_FIELDS = ("hook", "structure", "visual_system", "motion", "sound", "cta")
METRIC_OUTPUTS = (
    "views", "completion_rate", "average_watch_ratio", "shares_per_reach",
    "saves_per_reach",
)
PRODUCTION_STAGE_FIELDS = (
    "ingest_and_selects", "transcription_and_semantic_lock", "resource_preparation",
    "assembly", "review_changes", "quality_control", "rendering",
)
RFC3339 = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
SHA256 = re.compile(r"^[a-f0-9]{64}$")
MISSING_REVISION = "<missing>"
ANALYSIS_PARAMETERS = {
    "aggregation_version": "2.0.0",
    "window_tolerance_hours": {
        str(key): value for key, value in sorted(WINDOW_TOLERANCE_HOURS.items())
    },
    "minimum_comparable_publications": 3,
    "creative_dimensions": list(CONTENT_FIELDS),
    "cohort_unit": "unique_publication",
    "effective_sample_rule": "intersection_of_all_core_metrics",
    "material_confounder_strength_cap": "exploratory",
    "production_comparison_status": "verified_only",
}

RAW_IDENTITY_FIELDS = {
    "schema_version", "observation_id", "project_id", "video_id", "publication_id",
    "platform", "surface", "published_at", "captured_at", "window_hours",
    "captured_elapsed_hours", "window_tolerance_hours", "source_reference",
    "confounders", "lineage", "content", "distribution", "metrics", "derived",
    "governance", "evidence", "creative_attribution",
}
LINEAGE_FIELDS = {
    "publication_record_id", "publication_registry_id", "package_id", "package_sha256",
    "target_profile_id", "delivery_sha256", "delivery_check_sha256",
    "publication_evidence_sha256", "publication_registry_sha256", "verification_status",
}
DISTRIBUTION_FIELDS = {
    "traffic_source", "paid_spend", "currency", "campaign_objective",
    "audience_segment", "followers_at_publish", "publish_slot", "account_id",
    "language", "topic_id", "campaign_id", "publication_period",
}
DERIVED_FIELDS = {
    "average_watch_ratio", "shares_per_reach", "saves_per_reach",
    "engagements_per_reach", "clicks_per_reach",
}
GOVERNANCE_FIELDS = {
    "causal_claim_allowed", "automatic_rule_promotion", "human_review_required",
}
FLAT_INPUT_FIELDS = (
    LINEAGE_FIELDS | DISTRIBUTION_FIELDS | INTEGER_METRICS
    | FLOAT_METRICS | {"duration_s"}
)
RAW_ALLOWED_FIELDS = RAW_IDENTITY_FIELDS | FLAT_INPUT_FIELDS
DELIVERY_CHECK_FIELDS = {
    "schema_version", "profile_id", "platform", "surface", "media_path",
    "media_sha256", "inspected_at", "safe_zone_provenance", "technical_status",
    "manual_review_status", "delivery_status", "metadata", "findings",
}
LOCAL_EVIDENCE_TYPES = {
    "platform_export", "screenshot", "local_record", "timer_export", "work_log"
}


class PerformanceError(ValueError):
    """Performance input is malformed, contradictory, unverifiable, or unsafe."""


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(value):
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time(value, label):
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise PerformanceError(f"{label} must be an RFC3339 timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise PerformanceError(f"{label} must be a valid RFC3339 timestamp") from error
    return parsed.astimezone(timezone.utc)


def canonical_time(value, label):
    return parse_time(value, label).isoformat().replace("+00:00", "Z")


def _stable_file_bytes(path, label):
    """Read one regular file from a no-follow fd and reject path replacement."""

    path = Path(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise PerformanceError(f"cannot open stable {label} {path}: {error}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise PerformanceError(f"{label} is not a regular file: {path}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    current = os.stat(path, follow_symlinks=False)
    if not stat.S_ISREG(current.st_mode):
        raise PerformanceError(f"{label} is not a regular file: {path}")
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    identity_current = (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
    if identity_before != identity_after or identity_after != identity_current:
        raise PerformanceError(f"{label} changed while it was being read: {path}")
    return b"".join(chunks)


def _stable_json(path, label, expected_sha256=None):
    payload = _stable_file_bytes(path, label)
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise PerformanceError(f"{label} hash mismatch")
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PerformanceError(f"cannot parse {label} {path}: {error}") from error
    return document, digest


@contextmanager
def _stable_media_snapshot(path, label):
    """Copy exact delivery bytes to an immutable private snapshot for probing."""

    path = Path(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise PerformanceError(f"cannot open stable {label} {path}: {error}") from error
    temporary = None
    digest = hashlib.sha256()
    size = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise PerformanceError(f"{label} is not a regular file: {path}")
        with tempfile.NamedTemporaryFile(
            prefix="performance-delivery-", suffix=path.suffix, delete=False
        ) as output:
            temporary = Path(output.name)
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        after = os.fstat(descriptor)
        current = os.stat(path, follow_symlinks=False)
        before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        current_id = (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
        if before_id != after_id or after_id != current_id or size != before.st_size:
            raise PerformanceError(f"{label} changed while it was snapshotted: {path}")
        yield temporary, digest.hexdigest(), size
    finally:
        os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _lexical_absolute(path):
    return Path(os.path.abspath(os.fspath(Path(path).expanduser())))


def _within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def safe_project_root(path):
    root = _lexical_absolute(path)
    if not root.exists() or not root.is_dir():
        raise PerformanceError(f"project root is not a directory: {root}")
    if root.is_symlink():
        raise PerformanceError(f"project root may not be a symlink: {root}")
    return root


def safe_project_path(root, value, *, must_exist=True, regular_file=True):
    root = safe_project_root(root)
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = _lexical_absolute(candidate)
    if not _within(candidate, root):
        raise PerformanceError(f"path escapes project root: {candidate}")
    current = root
    for part in candidate.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise PerformanceError(f"symlink paths are not allowed: {current}")
        if not current.exists():
            if must_exist:
                raise PerformanceError(f"path does not exist: {current}")
            break
    if must_exist:
        if regular_file and not candidate.is_file():
            raise PerformanceError(f"expected regular file: {candidate}")
        if not regular_file and not candidate.exists():
            raise PerformanceError(f"path does not exist: {candidate}")
    return candidate


def safe_output_path(root, value):
    root = safe_project_root(root)
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = _lexical_absolute(candidate)
    if not _within(candidate, root):
        raise PerformanceError(f"output escapes project root: {candidate}")
    parent = candidate.parent
    existing = parent
    while not existing.exists() and existing != root:
        existing = existing.parent
    safe_project_path(root, existing, must_exist=True, regular_file=False)
    parent.mkdir(parents=True, exist_ok=True)
    safe_project_path(root, parent, must_exist=True, regular_file=False)
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_file()):
        raise PerformanceError(f"output is not a safe regular file: {candidate}")
    return candidate


def _read_json(path, label):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise PerformanceError(f"cannot read {label} {path}: {error}") from error


def _nullable_text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _number(value, label, *, integer=False, nullable=True):
    if value in (None, ""):
        if nullable:
            return None
        raise PerformanceError(f"{label} is required")
    if isinstance(value, bool):
        raise PerformanceError(f"{label} cannot be boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise PerformanceError(f"{label} must be numeric") from error
    if not math.isfinite(result) or result < 0:
        raise PerformanceError(f"{label} must be finite and non-negative")
    if integer:
        if not result.is_integer():
            raise PerformanceError(f"{label} must be an integer")
        return int(result)
    return result


def _ratio(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator)


def _same_value(left, right):
    if left in (None, "") and right in (None, ""):
        return True
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        try:
            return float(left) == float(right)
        except (TypeError, ValueError):
            pass
    return left == right


def _field(raw, container, key):
    nested = raw.get(container)
    nested_has = isinstance(nested, dict) and key in nested
    flat_has = key in raw
    if nested_has and flat_has and not _same_value(nested[key], raw[key]):
        raise PerformanceError(f"conflicting values for {container}.{key} and flat {key}")
    return nested.get(key) if nested_has else raw.get(key)


def _reject_unknown_observation_fields(raw):
    unknown = sorted(set(raw) - RAW_ALLOWED_FIELDS)
    if unknown:
        raise PerformanceError(f"unknown observation fields: {unknown}")
    containers = {
        "lineage": LINEAGE_FIELDS,
        "content": {"duration_s", "hybrid", "contributing_family_ids", *CONTENT_FIELDS},
        "distribution": DISTRIBUTION_FIELDS,
        "metrics": INTEGER_METRICS | FLOAT_METRICS,
        "derived": DERIVED_FIELDS,
        "governance": GOVERNANCE_FIELDS,
    }
    for name, allowed in containers.items():
        value = raw.get(name)
        if value is None:
            continue
        if not isinstance(value, dict):
            raise PerformanceError(f"{name} must be an object")
        extra = sorted(set(value) - set(allowed))
        if extra:
            raise PerformanceError(f"unknown {name} fields: {extra}")


def _platform_surface(raw):
    platform = str(raw.get("platform") or "").strip().lower()
    surface = str(raw.get("surface") or "").strip().lower()
    if platform == "youtube_shorts":
        platform = "youtube"
        surface = surface or "shorts"
    defaults = {
        "instagram": "reels_organic",
        "tiktok": "tiktok_organic",
        "youtube": "shorts",
    }
    surface = surface or defaults.get(platform, "")
    if not surface:
        raise PerformanceError("surface is required for this platform")
    return platform, surface


def publication_record_id(record):
    payload = {
        "publication_id": record["publication_id"],
        "project_id": record["project_id"],
        "video_id": record["video_id"],
        "platform": record["platform"],
        "surface": record["surface"],
        "published_at": canonical_time(record["published_at"], "publication published_at"),
        "registered_at": canonical_time(record["registered_at"], "publication registered_at"),
        "package": record["package"],
        "delivery": record["delivery"],
        "delivery_check": record["delivery_check"],
        "publication_evidence": record["publication_evidence"],
        "source_reference": record["source_reference"],
    }
    return f"PUBREC-{canonical_sha256(payload)[:16].upper()}"


def _verify_delivery_check(check, record, delivery_path):
    if not isinstance(check, dict) or set(check) != DELIVERY_CHECK_FIELDS:
        raise PerformanceError(
            "delivery check fields must be exactly " + str(sorted(DELIVERY_CHECK_FIELDS))
        )
    expected = {
        "schema_version": "1.0.0",
        "profile_id": record["delivery_check"]["profile_id"],
        "platform": record["platform"],
        "surface": record["surface"],
        "media_sha256": record["delivery"]["sha256"],
        "technical_status": "passed",
        "manual_review_status": "passed",
        "delivery_status": "ready",
    }
    for key, value in expected.items():
        if check.get(key) != value:
            raise PerformanceError(f"delivery check {key} must equal {value!r}")
    parse_time(check.get("inspected_at"), "delivery check inspected_at")
    if not isinstance(check.get("metadata"), dict) or not isinstance(check.get("findings"), list):
        raise PerformanceError("delivery check metadata/findings have invalid types")
    if Path(str(check.get("media_path") or "")).name != delivery_path.name:
        raise PerformanceError("delivery check media_path does not identify the registered MP4")


def _verify_local_evidence(root, evidence, label):
    if not isinstance(evidence, dict):
        raise PerformanceError(f"{label} must be an object")
    expected_fields = {"path", "sha256", "type", "integrity_scope"}
    if set(evidence) != expected_fields:
        raise PerformanceError(f"{label} fields must be exactly {sorted(expected_fields)}")
    if evidence.get("type") not in LOCAL_EVIDENCE_TYPES:
        raise PerformanceError(f"{label} has unsupported evidence type")
    if evidence.get("integrity_scope") != "local_artifact_integrity_only":
        raise PerformanceError(
            f"{label} must state local_artifact_integrity_only; local evidence does not prove remote authenticity"
        )
    path = safe_project_path(root, evidence.get("path"))
    payload = _stable_file_bytes(path, label)
    if not payload:
        raise PerformanceError(f"{label} may not be empty")
    actual = hashlib.sha256(payload).hexdigest()
    if actual != evidence.get("sha256"):
        raise PerformanceError(f"{label} hash mismatch")
    return {"path": path, "sha256": actual, "bytes": len(payload), "type": evidence["type"]}


def _verified_target_profile(root, package, target):
    adaptation = package["adaptation"]
    provenance = target["provenance"]
    if (
        provenance["catalog_path"] != adaptation["catalog_path"]
        or provenance["catalog_sha256"] != adaptation["catalog_sha256"]
    ):
        raise PerformanceError("publish-package target catalog provenance conflicts with adaptation")
    catalog_path = safe_project_path(root, provenance["catalog_path"])
    catalog, catalog_hash = _stable_json(
        catalog_path, "platform catalog", provenance["catalog_sha256"]
    )
    try:
        plan_platform_derivatives.validate_catalog_document(catalog)
    except plan_platform_derivatives.PlatformPlanError as error:
        raise PerformanceError(f"invalid platform catalog: {error}") from error
    profiles = [item for item in catalog["profiles"] if item["id"] == target["profile_id"]]
    if len(profiles) != 1:
        raise PerformanceError("platform catalog must contain exactly one target profile")
    profile = profiles[0]
    expected = {
        "platform": target["platform"],
        "surface": target["surface"],
        "profile_version": provenance["profile_version"],
        "evidence_reviewed_at": provenance["evidence_reviewed_at"],
        "kind": "derivative",
        "status": "active",
    }
    for field, value in expected.items():
        if profile.get(field) != value:
            raise PerformanceError(f"target profile {field} conflicts with publish-package")
    return profile, catalog_path, catalog_hash


def _probe_verified_delivery(snapshot_path, delivery_hash, profile, check):
    try:
        probe = check_platform_delivery.run_ffprobe(snapshot_path)
        metadata = check_platform_delivery.parse_ffprobe(probe)
        replay = check_platform_delivery.evaluate_delivery(
            profile, metadata, review=None, media_sha256=delivery_hash,
            media_path=snapshot_path,
        )
    except check_platform_delivery.DeliveryCheckError as error:
        raise PerformanceError(f"delivery ffprobe verification failed: {error}") from error
    if replay["technical_status"] != "passed":
        codes = [item.get("code") for item in replay.get("findings", [])]
        raise PerformanceError(
            "delivery does not satisfy its target profile on fresh ffprobe: "
            + ", ".join(str(code) for code in codes if code)
        )
    if check.get("metadata") != metadata:
        raise PerformanceError("delivery-check metadata differs from fresh ffprobe facts")
    return metadata


def load_publication_registry(path, project_root):
    root = safe_project_root(project_root)
    registry_path = safe_project_path(root, path)
    registry, registry_hash = _stable_json(registry_path, "publication registry")
    errors = validate_document(registry, load_schema_json(REGISTRY_SCHEMA))
    if errors:
        raise PerformanceError("invalid publication registry: " + "; ".join(errors))
    records = {}
    seen_record_ids = set()
    for original_record in registry["records"]:
        record = json.loads(json.dumps(original_record))
        expected_id = publication_record_id(record)
        if record["record_id"] != expected_id:
            raise PerformanceError(
                f"publication record id is not reproducible: expected {expected_id}"
            )
        if record["record_id"] in seen_record_ids:
            raise PerformanceError(f"duplicate publication record_id: {record['record_id']}")
        seen_record_ids.add(record["record_id"])
        if record["publication_id"] in records:
            raise PerformanceError(f"duplicate publication_id: {record['publication_id']}")
        published = parse_time(record["published_at"], "publication published_at")
        registered = parse_time(record["registered_at"], "publication registered_at")
        if registered < published:
            raise PerformanceError("publication registered_at cannot precede published_at")
        record["published_at"] = published.isoformat().replace("+00:00", "Z")
        record["registered_at"] = registered.isoformat().replace("+00:00", "Z")
        publication_evidence = _verify_local_evidence(
            root, record["publication_evidence"], "publication evidence"
        )

        package_path = safe_project_path(root, record["package"]["path"])
        package, _ = _stable_json(
            package_path, "publish-package", record["package"]["sha256"]
        )
        package_errors = validate_document(package, load_schema_json(PACKAGE_SCHEMA))
        if package_errors:
            raise PerformanceError("invalid linked publish-package: " + "; ".join(package_errors))
        if package["status"] != "ready_for_derivative_build":
            raise PerformanceError("linked publish-package is not ready_for_derivative_build")
        if package["package_id"] != record["package"]["package_id"]:
            raise PerformanceError("publish-package package_id conflicts with publication record")
        for field in ("project_id", "video_id"):
            if package[field] != record[field]:
                raise PerformanceError(f"publish-package {field} conflicts with publication record")
        targets = [
            item for item in package["targets"]
            if item["profile_id"] == record["delivery_check"]["profile_id"]
            and item["platform"] == record["platform"]
            and item["surface"] == record["surface"]
        ]
        if len(targets) != 1:
            raise PerformanceError("publish-package must contain exactly one matching target")
        target = targets[0]
        if target["status"] != "awaiting_derivative_render":
            raise PerformanceError("matching publish-package target is not awaiting_derivative_render")
        profile, catalog_path, catalog_hash = _verified_target_profile(root, package, target)

        delivery_path = safe_project_path(root, record["delivery"]["path"])
        if delivery_path.suffix.casefold() != ".mp4":
            raise PerformanceError("registered delivery must be an MP4")
        declared_output = Path(target["delivery_output"])
        if not declared_output.is_absolute():
            declared_output = package_path.parent / declared_output
        declared_output = safe_project_path(root, declared_output)
        if declared_output != delivery_path:
            raise PerformanceError("delivery path differs from publish-package target output")

        check_path = safe_project_path(root, record["delivery_check"]["path"])
        check, _ = _stable_json(
            check_path, "delivery-check", record["delivery_check"]["sha256"]
        )
        _verify_delivery_check(check, record, delivery_path)
        if parse_time(check["inspected_at"], "delivery check inspected_at") > published:
            raise PerformanceError("publication cannot precede its ready delivery check")
        with _stable_media_snapshot(delivery_path, "delivery MP4") as (
            snapshot_path, delivery_hash, delivery_size,
        ):
            if delivery_hash != record["delivery"]["sha256"]:
                raise PerformanceError(f"delivery hash mismatch for {record['publication_id']}")
            if delivery_size != record["delivery"]["size_bytes"]:
                raise PerformanceError(f"delivery size mismatch for {record['publication_id']}")
            fresh_metadata = _probe_verified_delivery(
                snapshot_path, delivery_hash, profile, check
            )
        records[record["publication_id"]] = {
            "record": record,
            "package": package,
            "delivery_check": check,
            "fresh_delivery_metadata": fresh_metadata,
            "publication_evidence": publication_evidence,
            "verified_paths": {
                "package": package_path,
                "delivery": delivery_path,
                "delivery_check": check_path,
                "platform_catalog": catalog_path,
                "publication_evidence": publication_evidence["path"],
            },
        }
    return {
        "registry_id": registry["registry_id"],
        "registry_sha256": registry_hash,
        "registry_path": registry_path,
        "project_root": root,
        "records": records,
    }


def _verified_publication(raw, registry):
    if not registry or not isinstance(registry.get("records"), dict):
        raise PerformanceError("a verified publication registry is required")
    publication_id = str(raw.get("publication_id") or "").strip()
    evidence = registry["records"].get(publication_id)
    if evidence is None:
        raise PerformanceError(f"publication_id is not registered: {publication_id!r}")
    return evidence


def creative_attribution_id(document):
    payload = {
        key: value for key, value in document.items() if key != "attribution_id"
    }
    payload["selected_at"] = canonical_time(
        document["selected_at"], "creative attribution selected_at"
    )
    return f"ATTR-{canonical_sha256(payload)[:16].upper()}"


def _verify_creative_attribution(raw, publication_registry, record):
    reference = raw.get("creative_attribution")
    expected_reference_fields = {"path", "sha256", "attribution_id"}
    if not isinstance(reference, dict) or set(reference) != expected_reference_fields:
        raise PerformanceError(
            "creative_attribution must contain exactly path, sha256, and attribution_id"
        )
    root = publication_registry["project_root"]
    attribution_path = safe_project_path(root, reference["path"])
    attribution, attribution_hash = _stable_json(
        attribution_path, "creative attribution", reference["sha256"]
    )
    errors = validate_document(attribution, load_schema_json(ATTRIBUTION_SCHEMA))
    if errors:
        raise PerformanceError("invalid creative attribution: " + "; ".join(errors))
    expected_id = creative_attribution_id(attribution)
    if attribution["attribution_id"] != expected_id or reference["attribution_id"] != expected_id:
        raise PerformanceError(f"creative attribution id is not reproducible: expected {expected_id}")
    for field in ("project_id", "video_id"):
        if attribution[field] != record[field]:
            raise PerformanceError(f"creative attribution {field} conflicts with publication")
    if parse_time(attribution["selected_at"], "creative attribution selected_at") > parse_time(
        record["published_at"], "publication published_at"
    ):
        raise PerformanceError("creative attribution selection cannot follow publication")

    plan_reference = attribution["plan"]
    plan_path = safe_project_path(root, plan_reference["path"])
    plan, plan_hash = _stable_json(
        plan_path, "creative recipe plan", plan_reference["sha256"]
    )
    if plan.get("plan_id") != plan_reference["plan_id"]:
        raise PerformanceError("creative attribution plan_id conflicts with recipe plan")
    if plan.get("blueprint", {}).get("video_id") != record["video_id"]:
        raise PerformanceError("creative recipe plan video_id conflicts with publication")
    catalog_reference = plan.get("inputs", {}).get("catalog")
    if not isinstance(catalog_reference, dict):
        raise PerformanceError("creative recipe plan has no catalog binding")
    catalog_path = safe_project_path(root, catalog_reference.get("path"))
    catalog, catalog_hash = _stable_json(
        catalog_path, "creative recipe catalog", catalog_reference.get("sha256")
    )
    try:
        compose_recipe.validate_catalog(catalog)
        compose_recipe.validate_plan(plan, catalog=catalog)
    except compose_recipe.CreativeRecipeError as error:
        raise PerformanceError(f"invalid creative recipe plan: {error}") from error

    selection = attribution["selection"]
    matches = [
        proposal for proposal in plan["proposals"]
        if proposal["recipe_id"] == selection["recipe_id"]
        and proposal["option_id"] == selection["option_id"]
    ]
    if len(matches) != 1:
        raise PerformanceError("creative attribution does not select exactly one real proposal")
    proposal = matches[0]
    expected_selection = {
        "option_id": proposal["option_id"],
        "recipe_id": proposal["recipe_id"],
        "primary_family_id": proposal["primary_family_id"],
        "hybrid": proposal["hybrid"],
        "contributing_family_ids": proposal["contributing_family_ids"],
        "module_ids": proposal["module_ids"],
    }
    if selection != expected_selection:
        raise PerformanceError("creative attribution selection drifts from selected proposal")
    return {
        "path": str(reference["path"]),
        "sha256": attribution_hash,
        "attribution_id": expected_id,
        "selected_at": canonical_time(
            attribution["selected_at"], "creative attribution selected_at"
        ),
        "selection_basis": attribution["selection_basis"],
        "selected_by_reference": attribution["selected_by_reference"],
        "plan": {
            "path": str(plan_reference["path"]),
            "sha256": plan_hash,
            "plan_id": plan["plan_id"],
            "catalog_path": str(catalog_reference["path"]),
            "catalog_sha256": catalog_hash,
        },
        "selection": expected_selection,
    }


def _verify_metrics_evidence(raw, publication_registry, record, metrics, captured_at, window):
    reference = raw.get("evidence")
    if isinstance(reference, dict) and "authenticity_notice" in reference:
        if reference.get("authenticity_notice") != (
            "SHA-256 proves integrity of the local evidence artifact, not authenticity or completeness "
            "of the remote platform data."
        ):
            raise PerformanceError("metrics evidence authenticity_notice conflicts with policy")
        reference = {
            key: reference[key]
            for key in ("path", "sha256", "type", "integrity_scope")
            if key in reference
        }
    evidence = _verify_local_evidence(
        publication_registry["project_root"], reference, "metrics evidence"
    )
    if evidence["type"] == "local_record":
        document, _ = _stable_json(evidence["path"], "metrics evidence", evidence["sha256"])
        expected_fields = {
            "schema_version", "publication_id", "captured_at", "window_hours", "metrics"
        }
        if not isinstance(document, dict) or set(document) != expected_fields:
            raise PerformanceError(
                "local_record metrics evidence must contain exactly " + str(sorted(expected_fields))
            )
        if document["schema_version"] != "1.0.0":
            raise PerformanceError("unsupported metrics evidence schema_version")
        if document["publication_id"] != record["publication_id"]:
            raise PerformanceError("metrics evidence publication_id conflicts with observation")
        if canonical_time(document["captured_at"], "metrics evidence captured_at") != captured_at:
            raise PerformanceError("metrics evidence captured_at conflicts with observation")
        if document["window_hours"] != window or document["metrics"] != metrics:
            raise PerformanceError("metrics evidence values conflict with normalized observation")
    return {
        "path": str(reference["path"]),
        "sha256": evidence["sha256"],
        "type": evidence["type"],
        "integrity_scope": "local_artifact_integrity_only",
        "authenticity_notice": (
            "SHA-256 proves integrity of the local evidence artifact, not authenticity or completeness "
            "of the remote platform data."
        ),
    }


def observation_id(result):
    payload = {
        key: result[key]
        for key in (
            "project_id", "video_id", "publication_id", "platform", "surface", "lineage",
            "published_at", "captured_at", "window_hours", "content", "distribution",
            "metrics", "evidence", "creative_attribution", "confounders", "source_reference",
        )
    }
    return f"OBS-{canonical_sha256(payload)[:16].upper()}"


def normalize_observation(raw, publication_registry=None):
    if not isinstance(raw, dict):
        raise PerformanceError("each observation must be an object")
    _reject_unknown_observation_fields(raw)
    nested_content = raw.get("content") if isinstance(raw.get("content"), dict) else {}
    if not raw.get("observation_id") and set(nested_content) - {"duration_s"}:
        raise PerformanceError(
            "creative content dimensions may not be supplied as free text; bind creative_attribution"
        )
    if raw.get("schema_version") not in (None, "", "1.0.0"):
        raise PerformanceError("unsupported observation schema_version")
    evidence = _verified_publication(raw, publication_registry)
    record = evidence["record"]
    published = parse_time(raw.get("published_at"), "published_at")
    captured = parse_time(raw.get("captured_at"), "captured_at")
    elapsed = (captured - published).total_seconds() / 3600
    if elapsed < 0:
        raise PerformanceError("captured_at cannot precede published_at")
    window = _number(raw.get("window_hours"), "window_hours", integer=True, nullable=False)
    if window not in WINDOWS:
        raise PerformanceError("window_hours must be 24, 72, or 168")
    tolerance = WINDOW_TOLERANCE_HOURS[window]
    lower, upper = window - tolerance, window + tolerance
    if not lower <= elapsed <= upper:
        raise PerformanceError(
            f"capture at {elapsed:.2f}h is outside the bilateral {window}h window "
            f"[{lower:.2f}, {upper:.2f}]"
        )
    duration = _number(_field(raw, "content", "duration_s"), "content.duration_s", nullable=False)
    if duration <= 0:
        raise PerformanceError("content.duration_s must be greater than zero")
    attribution = _verify_creative_attribution(raw, publication_registry, record)
    selection = attribution["selection"]
    derived_content = {
        "primary_family_id": selection["primary_family_id"],
        "recipe_id": selection["recipe_id"],
        "hook_id": selection["module_ids"]["hook"],
        "structure_id": selection["module_ids"]["structure"],
        "visual_system_id": selection["module_ids"]["visual_system"],
        "motion_id": selection["module_ids"]["motion"],
        "sound_id": selection["module_ids"]["sound"],
        "cta_id": selection["module_ids"]["cta"],
        "hybrid": selection["hybrid"],
        "contributing_family_ids": selection["contributing_family_ids"],
    }
    for key, expected in derived_content.items():
        supplied = nested_content.get(key)
        if supplied is not None and supplied != expected:
            raise PerformanceError(f"content.{key} conflicts with creative attribution")
    metrics = {
        key: _number(_field(raw, "metrics", key), f"metrics.{key}", integer=True)
        for key in sorted(INTEGER_METRICS)
    }
    metrics.update({
        key: _number(_field(raw, "metrics", key), f"metrics.{key}")
        for key in sorted(FLOAT_METRICS)
    })
    if metrics["completion_rate"] is not None and metrics["completion_rate"] > 1:
        raise PerformanceError("metrics.completion_rate must be between 0 and 1")
    engagement_values = [metrics[key] for key in ("likes", "comments", "shares", "saves")]
    engagements = None if any(value is None for value in engagement_values) else sum(engagement_values)
    confounders_raw = raw.get("confounders", [])
    if isinstance(confounders_raw, str):
        confounders_raw = confounders_raw.split("|")
    if not isinstance(confounders_raw, list):
        raise PerformanceError("confounders must be an array or pipe-separated text")
    confounders = sorted({str(item).strip() for item in confounders_raw if str(item).strip()})
    platform, surface = _platform_surface(raw)
    declared = {
        "project_id": str(raw.get("project_id") or "").strip(),
        "video_id": str(raw.get("video_id") or "").strip(),
        "publication_id": str(raw.get("publication_id") or "").strip(),
        "platform": platform,
        "surface": surface,
        "published_at": published.isoformat().replace("+00:00", "Z"),
    }
    for field, value in declared.items():
        if value != record[field]:
            raise PerformanceError(f"observation {field} conflicts with verified publication record")
    lineage = {
        "publication_record_id": record["record_id"],
        "publication_registry_id": publication_registry["registry_id"],
        "publication_registry_sha256": publication_registry["registry_sha256"],
        "package_id": record["package"]["package_id"],
        "package_sha256": record["package"]["sha256"],
        "target_profile_id": record["delivery_check"]["profile_id"],
        "delivery_sha256": record["delivery"]["sha256"],
        "delivery_check_sha256": record["delivery_check"]["sha256"],
        "publication_evidence_sha256": record["publication_evidence"]["sha256"],
        "verification_status": "verified_ready_delivery",
    }
    for key, expected in lineage.items():
        supplied = _field(raw, "lineage", key)
        if supplied not in (None, "") and supplied != expected:
            raise PerformanceError(f"declared lineage {key} conflicts with verified evidence")
    traffic = str(_field(raw, "distribution", "traffic_source") or "unknown").strip().lower()
    paid_spend = _number(_field(raw, "distribution", "paid_spend"), "distribution.paid_spend")
    currency = _nullable_text(_field(raw, "distribution", "currency"))
    if paid_spend and not currency:
        raise PerformanceError("distribution.currency is required when paid_spend is positive")
    if traffic == "organic" and paid_spend not in (None, 0):
        raise PerformanceError("organic traffic cannot declare positive paid_spend")
    account_id = _nullable_text(_field(raw, "distribution", "account_id"))
    language = _nullable_text(_field(raw, "distribution", "language"))
    topic_id = _nullable_text(_field(raw, "distribution", "topic_id"))
    if not account_id or not language or not topic_id:
        raise PerformanceError("distribution account_id, language, and topic_id are required")
    publication_period = published.strftime("%Y-%m")
    supplied_period = _nullable_text(_field(raw, "distribution", "publication_period"))
    if supplied_period is not None and supplied_period != publication_period:
        raise PerformanceError("distribution.publication_period conflicts with published_at")
    captured_text = captured.isoformat().replace("+00:00", "Z")
    metrics_evidence = _verify_metrics_evidence(
        raw, publication_registry, record, metrics, captured_text, window
    )
    derived = {
        "average_watch_ratio": _ratio(metrics["average_watch_time_s"], duration),
        "shares_per_reach": _ratio(metrics["shares"], metrics["reach"]),
        "saves_per_reach": _ratio(metrics["saves"], metrics["reach"]),
        "engagements_per_reach": _ratio(engagements, metrics["reach"]),
        "clicks_per_reach": _ratio(metrics["clicks"], metrics["reach"]),
    }
    governance = {
        "causal_claim_allowed": False,
        "automatic_rule_promotion": False,
        "human_review_required": True,
    }
    result = {
        "schema_version": "1.0.0",
        "observation_id": "",
        **declared,
        "lineage": lineage,
        "captured_at": captured_text,
        "window_hours": window,
        "window_tolerance_hours": tolerance,
        "captured_elapsed_hours": round(elapsed, 6),
        "content": {
            "duration_s": duration,
            **derived_content,
        },
        "creative_attribution": {
            "path": attribution["path"],
            "sha256": attribution["sha256"],
            "attribution_id": attribution["attribution_id"],
        },
        "distribution": {
            "traffic_source": traffic,
            "paid_spend": paid_spend,
            "currency": currency,
            "campaign_objective": _nullable_text(_field(raw, "distribution", "campaign_objective")),
            "audience_segment": _nullable_text(_field(raw, "distribution", "audience_segment")),
            "followers_at_publish": _number(
                _field(raw, "distribution", "followers_at_publish"),
                "distribution.followers_at_publish", integer=True,
            ),
            "publish_slot": _nullable_text(_field(raw, "distribution", "publish_slot")),
            "account_id": account_id,
            "language": language,
            "topic_id": topic_id,
            "campaign_id": _nullable_text(_field(raw, "distribution", "campaign_id")),
            "publication_period": publication_period,
        },
        "metrics": metrics,
        "evidence": metrics_evidence,
        "derived": derived,
        "confounders": confounders,
        "source_reference": str(raw.get("source_reference") or "").strip(),
        "governance": governance,
    }
    result["observation_id"] = observation_id(result)
    supplied_id = str(raw.get("observation_id") or "").strip()
    if supplied_id and supplied_id != result["observation_id"]:
        raise PerformanceError(
            f"observation_id is not reproducible: expected {result['observation_id']}"
        )
    for name, computed in (("derived", derived), ("governance", governance)):
        supplied = raw.get(name)
        if supplied is not None and supplied != computed:
            raise PerformanceError(f"supplied {name} conflicts with computed values")
    if raw.get("captured_elapsed_hours") not in (None, "") and not _same_value(
        raw["captured_elapsed_hours"], result["captured_elapsed_hours"]
    ):
        raise PerformanceError("captured_elapsed_hours conflicts with timestamps")
    if raw.get("window_tolerance_hours") not in (None, "") and not _same_value(
        raw["window_tolerance_hours"], tolerance
    ):
        raise PerformanceError("window_tolerance_hours conflicts with policy")
    errors = validate_document(result, load_schema_json(OBS_SCHEMA))
    if errors:
        raise PerformanceError("invalid normalized observation: " + "; ".join(errors))
    return result


def empty_store(store_id="PERFORMANCE-STORE-MAIN", updated_at=None):
    return {
        "schema_version": "1.0.0",
        "store_id": store_id,
        "updated_at": updated_at or utc_now(),
        "observations": [],
    }


def _validate_monotonic(observations):
    groups = defaultdict(list)
    for item in observations:
        groups[item["publication_id"]].append(item)
    for publication_id, items in groups.items():
        ordered = sorted(items, key=lambda item: item["window_hours"])
        static_keys = (
            "project_id", "video_id", "platform", "surface", "lineage", "published_at",
            "content", "creative_attribution", "distribution",
        )
        for earlier, later in zip(ordered, ordered[1:]):
            for key in static_keys:
                if earlier[key] != later[key]:
                    raise PerformanceError(
                        f"publication {publication_id} changes immutable {key} across windows"
                    )
        for metric in sorted(CUMULATIVE_METRICS):
            measured = [
                (item["window_hours"], item["metrics"].get(metric))
                for item in ordered if item["metrics"].get(metric) is not None
            ]
            for (before_window, before), (after_window, after) in zip(measured, measured[1:]):
                if after < before:
                    raise PerformanceError(
                        f"cumulative metric {metric} decreases for {publication_id} "
                        f"between {before_window}h and {after_window}h"
                    )


def validate_store(store, publication_registry=None):
    errors = validate_document(store, load_schema_json(STORE_SCHEMA))
    if errors:
        raise PerformanceError("invalid performance store: " + "; ".join(errors))
    seen_ids = set()
    seen_windows = set()
    normalized = []
    for item in store["observations"]:
        observation = normalize_observation(item, publication_registry)
        obs_id = observation["observation_id"]
        if obs_id in seen_ids:
            raise PerformanceError(f"duplicate observation_id: {obs_id}")
        seen_ids.add(obs_id)
        key = (observation["publication_id"], observation["window_hours"])
        if key in seen_windows:
            raise PerformanceError(
                f"duplicate publication/window: {observation['publication_id']}/{observation['window_hours']}"
            )
        seen_windows.add(key)
        normalized.append(observation)
    _validate_monotonic(normalized)
    return normalized


def merge_observations(store, incoming, *, publication_registry, updated_at=None):
    existing = validate_store(store, publication_registry)
    by_id = {item["observation_id"]: item for item in existing}
    additions = 0
    for raw in incoming:
        item = normalize_observation(raw, publication_registry)
        previous = by_id.get(item["observation_id"])
        if previous is not None:
            if previous != item:
                raise PerformanceError(
                    f"observation_id conflict: {item['observation_id']} already has different data"
                )
            continue
        by_id[item["observation_id"]] = item
        additions += 1
    observations = sorted(
        by_id.values(),
        key=lambda item: (item["publication_id"], item["window_hours"], item["observation_id"]),
    )
    window_keys = [(item["publication_id"], item["window_hours"]) for item in observations]
    if len(window_keys) != len(set(window_keys)):
        raise PerformanceError("a publication may contain only one observation per window")
    _validate_monotonic(observations)
    if additions == 0:
        return store, 0
    result = {
        "schema_version": "1.0.0",
        "store_id": store["store_id"],
        "updated_at": updated_at or utc_now(),
        "observations": observations,
    }
    validate_store(result, publication_registry)
    return result, additions


def _duration_band(seconds):
    if seconds <= 20:
        return "01-20s"
    if seconds <= 40:
        return "21-40s"
    if seconds <= 60:
        return "41-60s"
    return "61s-plus"


def _median(values):
    clean = [float(value) for value in values if value is not None]
    return statistics.median(clean) if clean else None


def _metric_value(item, metric):
    return item["metrics"][metric] if metric in item["metrics"] else item["derived"][metric]


def _publication_metric_summary(items):
    by_publication = {item["publication_id"]: item for item in items}
    effective = {
        metric: sum(_metric_value(item, metric) is not None for item in by_publication.values())
        for metric in METRIC_OUTPUTS
    }
    effective["joint_core"] = sum(
        all(_metric_value(item, metric) is not None for metric in METRIC_OUTPUTS)
        for item in by_publication.values()
    )
    return {
        "median_views": _median(_metric_value(item, "views") for item in by_publication.values()),
        "median_completion_rate": _median(
            _metric_value(item, "completion_rate") for item in by_publication.values()
        ),
        "median_average_watch_ratio": _median(
            _metric_value(item, "average_watch_ratio") for item in by_publication.values()
        ),
        "median_shares_per_reach": _median(
            _metric_value(item, "shares_per_reach") for item in by_publication.values()
        ),
        "median_saves_per_reach": _median(
            _metric_value(item, "saves_per_reach") for item in by_publication.values()
        ),
        "effective_publications": effective,
    }


def _cohort_key(item):
    return (
        item["project_id"], item["platform"], item["surface"],
        item["lineage"]["target_profile_id"], item["window_hours"],
        item["distribution"]["traffic_source"], item["distribution"]["campaign_objective"],
        _duration_band(item["content"]["duration_s"]),
        item["distribution"]["audience_segment"],
        item["distribution"]["account_id"], item["distribution"]["language"],
        item["distribution"]["topic_id"], item["distribution"]["campaign_id"],
        item["distribution"]["publication_period"], item["distribution"]["currency"],
    )


def _strength(size):
    if size < 3:
        return "insufficient"
    if size < 5:
        return "exploratory"
    if size < 10:
        return "directional"
    return "stronger_non_causal"


def production_record_id(record):
    payload = {
        key: json.loads(json.dumps(value))
        for key, value in record.items()
        if key != "production_record_id"
    }
    # JSON Schema treats 3 and 3.0 as the same numeric value. Canonicalize the
    # duration-like fields so their identifier does too, regardless of whether
    # the input came from JSON (number) or CSV (text converted to float).
    stages = payload.get("stage_minutes")
    if isinstance(stages, dict):
        for field in PRODUCTION_STAGE_FIELDS:
            value = stages.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                stages[field] = float(value)
    for field in ("captured_at", "started_at", "first_reviewable_at", "final_delivered_at"):
        value = payload.get(field)
        if value is not None:
            payload[field] = canonical_time(value, f"production {field}")
    return f"PROD-{canonical_sha256(payload)[:16].upper()}"


def normalize_production_record(item, project_root=None):
    if not isinstance(item, dict):
        raise PerformanceError("production metrics entries must be objects")
    errors = validate_document(item, load_schema_json(PRODUCTION_SCHEMA))
    if errors:
        raise PerformanceError("invalid production metrics: " + "; ".join(errors))
    normalized = json.loads(json.dumps(item))
    for field in PRODUCTION_STAGE_FIELDS:
        normalized["stage_minutes"][field] = _number(
            normalized["stage_minutes"][field], f"stage_minutes.{field}", nullable=False
        )
    if normalized["assets"]["generated_but_unused"] > normalized["assets"]["generated"]:
        raise PerformanceError("assets.generated_but_unused cannot exceed assets.generated")
    denominator = sum(normalized["assets"][key] for key in ("reused", "derived", "generated"))
    expected_reuse = normalized["assets"]["reused"] / denominator if denominator else None
    declared_reuse = normalized["assets"]["reuse_rate"]
    if (expected_reuse is None) != (declared_reuse is None) or (
        expected_reuse is not None and abs(expected_reuse - declared_reuse) > 1e-9
    ):
        raise PerformanceError("assets.reuse_rate conflicts with asset counts")
    atomic_decisions = normalized["reviews"]["atomic_decisions"]
    approved_first_pass = normalized["reviews"]["approved_first_pass"]
    if approved_first_pass > atomic_decisions:
        raise PerformanceError(
            "reviews.approved_first_pass cannot exceed reviews.atomic_decisions"
        )
    expected_first_pass = (
        approved_first_pass / atomic_decisions if atomic_decisions else None
    )
    declared_first_pass = normalized["reviews"]["first_pass_approval_rate"]
    if (expected_first_pass is None) != (declared_first_pass is None) or (
        expected_first_pass is not None
        and abs(expected_first_pass - declared_first_pass) > 1e-9
    ):
        raise PerformanceError(
            "reviews.first_pass_approval_rate conflicts with review counts"
        )
    for name in ("started_at", "first_reviewable_at", "final_delivered_at"):
        if normalized[name] is not None:
            normalized[name] = canonical_time(normalized[name], name)
    times = [
        parse_time(normalized[name], name)
        for name in ("started_at", "first_reviewable_at", "final_delivered_at")
        if normalized[name] is not None
    ]
    if times != sorted(times):
        raise PerformanceError("production timestamps must be chronological")
    normalized["captured_at"] = canonical_time(normalized["captured_at"], "captured_at")
    captured_at = parse_time(normalized["captured_at"], "captured_at")
    if times and captured_at < times[-1]:
        raise PerformanceError("captured_at cannot precede recorded production timestamps")
    verification_status = normalized["verification_status"]
    measurement_method = normalized["measurement_method"]
    evidence = normalized["evidence"]
    if verification_status == "verified":
        if measurement_method == "self_reported":
            raise PerformanceError("verified production metrics need a measured method")
        if project_root is None:
            raise PerformanceError("verified production metrics require a project root")
        _verify_local_evidence(project_root, evidence, "production metrics evidence")
    else:
        if measurement_method != "self_reported" or evidence is not None:
            raise PerformanceError(
                "self_reported production metrics must use self_reported method and no evidence"
            )
    expected_id = production_record_id(normalized)
    if normalized["production_record_id"] != expected_id:
        raise PerformanceError(
            f"production_record_id is not reproducible: expected {expected_id}"
        )
    return normalized


def _production_lookup(records, *, project_root=None, allowed_keys=None):
    lookup = {}
    by_id = {}
    relevant_ids = set()
    for raw in records or []:
        if (
            allowed_keys is not None
            and isinstance(raw, dict)
            and (raw.get("project_id"), raw.get("video_id")) not in allowed_keys
        ):
            # A report must neither validate nor seal unrelated production data.
            continue
        item = normalize_production_record(raw, project_root=project_root)
        existing_id = by_id.get(item["production_record_id"])
        if existing_id is not None:
            if existing_id != item:
                raise PerformanceError(f"production_record_id conflict: {item['production_record_id']}")
            continue
        by_id[item["production_record_id"]] = item
        key = (item["project_id"], item["video_id"])
        if allowed_keys is not None and key not in allowed_keys:
            continue
        if item["verification_status"] != "verified":
            continue
        relevant_ids.add(item["production_record_id"])
        previous = lookup.get(key)
        if previous is not None:
            if previous == item:
                continue
            raise PerformanceError(f"conflicting production metrics for {key[0]}/{key[1]}")
        lookup[key] = item
    return lookup, [by_id[key] for key in sorted(relevant_ids)]


def _production_summary(item):
    return {
        "production_record_id": item["production_record_id"],
        "total_minutes": sum(item["stage_minutes"].values()),
        "review_rounds": item["reviews"]["rounds"],
        "change_count": item["rework"]["change_count"],
    }


def _creative_variation(items):
    dimensions = []
    publication_count = len({item["publication_id"] for item in items})
    for field in CONTENT_FIELDS:
        groups = defaultdict(list)
        missing = set()
        for item in items:
            value = item["content"][field]
            if value is None:
                missing.add(item["publication_id"])
            else:
                groups[value].append(item)
        variants = []
        for value in sorted(groups):
            summary = _publication_metric_summary(groups[value])
            variants.append({
                "value": value,
                "publication_count": len({item["publication_id"] for item in groups[value]}),
                **summary,
            })
        variant_count = len(variants)
        status = (
            "missing" if variant_count == 0
            else "single_variant" if variant_count == 1
            else "multiple_variants"
        )
        dimensions.append({
            "dimension": field,
            "status": status,
            "variant_count": variant_count,
            "missing_publications": len(missing),
            "cohort_publications": publication_count,
            "variants": variants,
        })
    return dimensions


def build_cohort_report(store, *, publication_registry, production_records=None, generated_at=None):
    observations = validate_store(store, publication_registry)
    if not observations:
        raise PerformanceError("cannot build a cohort report from an empty performance store")
    groups = defaultdict(list)
    for item in observations:
        groups[_cohort_key(item)].append(item)
    allowed_production_keys = {
        (item["project_id"], item["video_id"]) for item in observations
    }
    production, production_normalized = _production_lookup(
        production_records,
        project_root=publication_registry["project_root"],
        allowed_keys=allowed_production_keys,
    )
    cohorts = []
    for key in sorted(
        groups,
        key=lambda value: tuple("" if part is None else str(part) for part in value),
    ):
        items = groups[key]
        publications = {item["publication_id"]: item for item in items}
        size = len(publications)
        creative_summary = _publication_metric_summary(items)
        effective = creative_summary["effective_publications"]
        effective_size = effective["joint_core"]
        production_keys = {
            (item["project_id"], item["video_id"])
            for item in publications.values()
            if (item["project_id"], item["video_id"]) in production
        }
        production_items = [
            _production_summary(production[production_key])
            for production_key in sorted(production_keys)
        ]
        definition = {
            "project_id": key[0], "platform": key[1], "surface": key[2],
            "target_profile_id": key[3], "window_hours": key[4],
            "traffic_source": key[5], "campaign_objective": key[6],
            "duration_band": key[7], "audience_segment": key[8],
            "account_id": key[9], "language": key[10], "topic_id": key[11],
            "campaign_id": key[12], "publication_period": key[13],
            "currency": key[14],
        }
        members = [
            {
                "observation_id": item["observation_id"],
                "publication_id": item["publication_id"],
                "video_id": item["video_id"],
            }
            for item in sorted(publications.values(), key=lambda value: value["publication_id"])
        ]
        cohort_payload = {
            "definition": definition,
            "members": members,
            "production_record_ids": [item["production_record_id"] for item in production_items],
            "analysis_parameters": ANALYSIS_PARAMETERS,
        }
        confounders = {value for item in items for value in item["confounders"]}
        slots = {item["distribution"]["publish_slot"] for item in items}
        if len(slots) > 1:
            confounders.add("publish_slot_varies_within_cohort")
        follower_counts = [
            item["distribution"]["followers_at_publish"] for item in items
            if item["distribution"]["followers_at_publish"] is not None
        ]
        if follower_counts and min(follower_counts) > 0 and max(follower_counts) / min(follower_counts) > 1.2:
            confounders.add("audience_size_varies_over_20_percent")
        spends = [
            item["distribution"]["paid_spend"] for item in items
            if item["distribution"]["paid_spend"] is not None
        ]
        if len(set(spends)) > 1:
            confounders.add("paid_spend_varies_within_cohort")
        if any(count < size for count in effective.values()):
            confounders.add("metric_specific_effective_n_varies")
        missing = max(0, 3 - effective_size)
        strength = _strength(effective_size)
        if confounders and strength in {"directional", "stronger_non_causal"}:
            strength = "exploratory"
            confounders.add("evidence_strength_capped_by_material_confounders")
        cohorts.append({
            "cohort_id": f"COHORT-{canonical_sha256(cohort_payload)[:16].upper()}",
            "definition": definition,
            "members": members,
            "sample_size": size,
            "effective_sample_size": effective_size,
            "evidence_strength": strength,
            "creative_performance": creative_summary,
            "creative_variation": _creative_variation(items),
            "production_efficiency": {
                "status": "measured_separately" if production_items else "not_measured",
                "sample_size": len(production_items),
                "production_record_ids": [item["production_record_id"] for item in production_items],
                "median_total_minutes": _median(item["total_minutes"] for item in production_items),
                "median_review_rounds": _median(item["review_rounds"] for item in production_items),
                "median_change_count": _median(item["change_count"] for item in production_items),
                "not_combined_with_creative_score": True,
            },
            "interpretation": {
                "status": "collect_more" if effective_size < 3 else "human_hypothesis_review",
                "minimum_additional_publications": missing,
                "confounders": sorted(confounders),
                "next_step": (
                    f"Reunir {missing} publicacion(es) comparable(s) con las metricas nucleares."
                    if missing
                    else "Revisar variaciones como hipotesis contextual; no atribuir causalidad ni promover reglas automaticamente."
                ),
            },
        })
    store_sha = canonical_sha256({"store_id": store["store_id"], "observations": observations})
    report_payload = {
        "source_store_sha256": store_sha,
        "cohort_ids": [item["cohort_id"] for item in cohorts],
        "production_record_ids": [item["production_record_id"] for item in production_normalized],
        "analysis_parameters": ANALYSIS_PARAMETERS,
    }
    generated = canonical_time(generated_at or utc_now(), "generated_at")
    report = {
        "schema_version": "1.0.0",
        "report_id": f"COHORT-REPORT-{canonical_sha256(report_payload)[:16].upper()}",
        "generated_at": generated,
        "source_store_id": store["store_id"],
        "source_store_sha256": store_sha,
        "observation_count": len(observations),
        "production_record_ids": [item["production_record_id"] for item in production_normalized],
        "analysis_parameters": ANALYSIS_PARAMETERS,
        "cohorts": cohorts,
        "separation_notice": (
            "El rendimiento creativo y la eficiencia de produccion se informan por separado; "
            "no se combinan en una puntuacion causal."
        ),
        "governance": {
            "causal_claim_allowed": False,
            "automatic_rule_promotion": False,
            "minimum_comparable_publications": 3,
            "human_interpretation_required": True,
        },
    }
    errors = validate_document(report, load_schema_json(REPORT_SCHEMA))
    if errors:
        raise PerformanceError("generated cohort report is invalid: " + "; ".join(errors))
    return report


def verify_cohort_report(
    report, *, store, publication_registry, production_records=None
):
    """Recompute every governed aggregate and identity before consumption."""

    errors = validate_document(report, load_schema_json(REPORT_SCHEMA))
    if errors:
        raise PerformanceError("invalid cohort report: " + "; ".join(errors))
    expected = build_cohort_report(
        store,
        publication_registry=publication_registry,
        production_records=production_records,
        generated_at=report["generated_at"],
    )
    if report != expected:
        raise PerformanceError(
            "cohort report semantic verification failed; IDs, members, effective N, strength, "
            "medians, or bindings differ from recomputed evidence"
        )
    return expected


def load_records(path, project_root=None):
    path = safe_project_path(project_root, path) if project_root else Path(path)
    if path.is_symlink() or not path.is_file():
        raise PerformanceError(f"input is not a safe regular file: {path}")
    if path.suffix.lower() == ".csv":
        payload = _stable_file_bytes(path, "CSV input")
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise PerformanceError(f"cannot decode CSV input {path}: {error}") from error
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise PerformanceError("CSV headers must be present and unique")
        rows = []
        for row in reader:
            expanded = dict(row)
            expanded["creative_attribution"] = {
                "path": expanded.pop("creative_attribution_path", ""),
                "sha256": expanded.pop("creative_attribution_sha256", ""),
                "attribution_id": expanded.pop("creative_attribution_id", ""),
            }
            expanded["evidence"] = {
                "path": expanded.pop("metrics_evidence_path", ""),
                "sha256": expanded.pop("metrics_evidence_sha256", ""),
                "type": expanded.pop("metrics_evidence_type", ""),
                "integrity_scope": expanded.pop("metrics_evidence_integrity_scope", ""),
            }
            rows.append(expanded)
        return rows
    value, _ = _stable_json(path, "input")
    if isinstance(value, dict) and "observations" in value:
        value = value["observations"]
    elif isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise PerformanceError("input JSON must be an observation, array, or store")
    return value


def file_revision(path):
    path = Path(path)
    if not path.exists():
        return MISSING_REVISION
    return hashlib.sha256(_stable_file_bytes(path, "revision input")).hexdigest()


def load_store_state(path, project_root, *, require_existing=False):
    root = safe_project_root(project_root)
    candidate = safe_project_path(root, path, must_exist=False)
    if not candidate.exists():
        if require_existing:
            raise PerformanceError(f"performance store does not exist: {candidate}")
        return empty_store(), MISSING_REVISION, candidate
    safe_project_path(root, candidate)
    store, revision = _stable_json(candidate, "performance store")
    return store, revision, candidate


def atomic_write_json(
    path, value, *, project_root, expected_revision=None, no_clobber_id_field=None
):
    path = safe_output_path(project_root, path)
    lock_path = path.with_name(path.name + ".lock")
    if lock_path.exists() and lock_path.is_symlink():
        raise PerformanceError(f"lock path may not be a symlink: {lock_path}")
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        lock_fd = os.open(lock_path, flags, 0o600)
    except OSError as error:
        raise PerformanceError(f"cannot open safe store lock {lock_path}: {error}") from error
    temporary = None
    try:
        with os.fdopen(lock_fd, "a+") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            actual_revision = file_revision(path)
            if no_clobber_id_field is not None and actual_revision != MISSING_REVISION:
                existing, _ = _stable_json(path, "existing output")
                existing_id = existing.get(no_clobber_id_field) if isinstance(existing, dict) else None
                incoming_id = value.get(no_clobber_id_field) if isinstance(value, dict) else None
                if existing_id == incoming_id and existing == value:
                    return False
                raise PerformanceError(
                    f"refusing to overwrite existing {no_clobber_id_field} "
                    f"{existing_id!r} with {incoming_id!r}"
                )
            if expected_revision is not None and actual_revision != expected_revision:
                raise PerformanceError("concurrent store update detected; reload and merge before writing")
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(value, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            temporary = None
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("ingest", "verify lineage, normalize, and merge observations"),
        ("report", "build a comparable non-causal cohort report"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--project-root", type=Path, required=True)
        command.add_argument("--publication-registry", type=Path, required=True)
        command.add_argument("--store", type=Path, required=True)
        command.add_argument("--write", action="store_true")
        if name == "ingest":
            command.add_argument("--input", type=Path, required=True)
        else:
            command.add_argument("--production-metrics", type=Path)
            command.add_argument("--out", type=Path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        root = safe_project_root(args.project_root)
        registry = load_publication_registry(args.publication_registry, root)
        if args.command == "ingest":
            store, revision, store_path = load_store_state(args.store, root)
            result, additions = merge_observations(
                store, load_records(args.input, root), publication_registry=registry
            )
            if args.write and additions:
                atomic_write_json(
                    store_path, result, project_root=root, expected_revision=revision
                )
            print(json.dumps({"added": additions, "store": result}, ensure_ascii=False, indent=2))
            return 0
        store, _, _ = load_store_state(args.store, root, require_existing=True)
        production = load_records(args.production_metrics, root) if args.production_metrics else None
        report = build_cohort_report(
            store, publication_registry=registry, production_records=production
        )
        verify_cohort_report(
            report,
            store=store,
            publication_registry=registry,
            production_records=production,
        )
        if args.write:
            if args.out is None:
                raise PerformanceError("--out is required with --write")
            atomic_write_json(
                args.out,
                report,
                project_root=root,
                no_clobber_id_field="report_id",
            )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (PerformanceError, OSError, TypeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
