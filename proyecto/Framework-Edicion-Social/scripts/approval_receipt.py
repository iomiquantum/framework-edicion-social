#!/usr/bin/env python3
"""Prepare, seal, and verify SHA-256-bound editorial approval receipts.

The default behavior is read-only: ``prepare`` and ``seal`` emit JSON to
stdout, while ``verify`` only inspects. A filesystem write requires both
``--out`` and the explicit ``--write`` flag. Preparing a receipt always creates
a pending decision; it never infers or records approval.

The SHA-256 seal provides integrity, not identity or non-repudiation. An
approval is usable only when it carries a structured reference to independently
inspectable human evidence. Deployments that need cryptographic authenticity
must additionally sign the sealed receipt with a key controlled outside this
file and its producer. ``created_at`` records receipt preparation,
``decision.decided_at`` records when the human decided (which may be earlier),
and ``decision.recorded_at`` records when that decision was entered here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = SCRIPT_DIR.parent
DEFAULT_SCHEMA = FRAMEWORK_ROOT / "schemas/approval-receipt.schema.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import UnsupportedSchemaKeyword, validate_document  # noqa: E402


SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
RFC3339_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
USER_MESSAGE_REFERENCE = re.compile(r"^thread:[^\s/]+/turn:[^\s/]+$")
REVIEW_SYSTEM_REFERENCE = re.compile(r"^review:[^\s/]+/decision:[^\s/]+$")
SIGNED_FORM_REFERENCE = re.compile(r"^signed-form:sha256:[a-f0-9]{64}$")
AUTOMATION_IDENTITIES = {"ai", "agent", "assistant", "automation", "codex", "system"}
MEDIA_ROLES = {
    "editorial_mezzanine",
    "social_delivery_master",
    "platform_derivative",
    "other",
}

PENDING_DECISION = {
    "status": "pending",
    "explicit_user_approval": False,
    "approver": None,
    "decided_at": None,
    "recorded_at": None,
    "recorded_by": None,
    "evidence": {"kind": "none", "reference": "", "excerpt": ""},
    "scope": {"whole_artifact": False, "approved_layers": []},
}


class ApprovalReceiptError(ValueError):
    """Receipt input, evidence, or artifact binding is unsafe or malformed."""


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path, label="JSON document"):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as error:
        raise ApprovalReceiptError(f"{label} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ApprovalReceiptError(f"{label} must be a JSON object")
    return value


def parse_rfc3339(value):
    if not isinstance(value, str) or RFC3339_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def is_verifiable_human_reference(kind, reference):
    if not isinstance(reference, str):
        return False
    patterns = {
        "user_message": USER_MESSAGE_REFERENCE,
        "review_system": REVIEW_SYSTEM_REFERENCE,
        "signed_form": SIGNED_FORM_REFERENCE,
    }
    pattern = patterns.get(kind)
    return pattern is not None and pattern.fullmatch(reference) is not None


def is_human_identity(value):
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value.strip().casefold() not in AUTOMATION_IDENTITIES
    )


def file_fingerprint(path):
    """Hash and size one stable regular-file handle, rejecting in-place mutation."""
    path = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ApprovalReceiptError(f"artifact is not a regular file: {path}")
        digest = hashlib.sha256()
        total = 0
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                total += len(chunk)
        after = os.fstat(descriptor)
        stable_identity = (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
        stable_metadata = (
            before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns
            and before.st_ctime_ns == after.st_ctime_ns
            and total == after.st_size
        )
        if not stable_identity or not stable_metadata:
            raise ApprovalReceiptError(f"artifact changed while it was being fingerprinted: {path}")
        return {"sha256": digest.hexdigest(), "size_bytes": total}
    finally:
        os.close(descriptor)


def sha256_file(path):
    """Compatibility wrapper for callers that only need the digest."""
    return file_fingerprint(path)["sha256"]


def _absolute_without_resolving(path):
    return Path(os.path.abspath(os.fspath(Path(path).expanduser())))


def atomic_write_text(path, text):
    """Atomically replace a regular destination without following temp symlinks."""
    destination = _absolute_without_resolving(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ApprovalReceiptError(f"refusing to replace symlink destination: {destination}")

    descriptor = None
    temporary = None
    try:
        descriptor, raw_temporary = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary = Path(raw_temporary)
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=True) as handle:
            descriptor = None
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if destination.is_symlink():
            raise ApprovalReceiptError(f"refusing to replace symlink destination: {destination}")
        os.replace(temporary, destination)
        temporary = None
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
        directory_descriptor = os.open(destination.parent, directory_flags)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def canonical_payload(receipt):
    """Return the stable payload covered by ``binding.payload_sha256``."""
    payload = {key: copy.deepcopy(value) for key, value in receipt.items() if key != "binding"}
    binding = receipt.get("binding") if isinstance(receipt.get("binding"), dict) else {}
    payload["binding_contract"] = {
        "algorithm": binding.get("algorithm"),
        "canonicalization": binding.get("canonicalization"),
    }
    return payload


def payload_sha256(receipt):
    encoded = json.dumps(
        canonical_payload(receipt),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def schema_errors(receipt, schema_path=DEFAULT_SCHEMA):
    schema = load_json(schema_path, "approval receipt schema")
    try:
        return validate_document(receipt, schema)
    except UnsupportedSchemaKeyword as error:
        raise ApprovalReceiptError(f"unsupported approval receipt schema: {error}") from error


def semantic_errors(receipt):
    """Enforce cross-field safety rules that the simple JSON schema cannot express."""
    errors = []
    artifact = receipt.get("artifact") if isinstance(receipt.get("artifact"), dict) else {}
    decision = receipt.get("decision") if isinstance(receipt.get("decision"), dict) else {}
    evidence = decision.get("evidence") if isinstance(decision.get("evidence"), dict) else {}
    scope = decision.get("scope") if isinstance(decision.get("scope"), dict) else {}
    binding = receipt.get("binding") if isinstance(receipt.get("binding"), dict) else {}

    binding_status = artifact.get("binding_status")
    artifact_hash = artifact.get("sha256")
    artifact_size = artifact.get("size_bytes")
    artifact_path = artifact.get("path")
    payload_hash = binding.get("payload_sha256")
    if binding_status == "unbound":
        if artifact_hash is not None or artifact_size is not None or payload_hash is not None:
            errors.append("an unbound receipt may not contain artifact or payload hashes")
        if decision.get("status") != "pending":
            errors.append("an unbound receipt must remain pending")
    elif binding_status == "bound":
        if not isinstance(artifact_path, str) or not artifact_path.strip():
            errors.append("a bound receipt requires a non-empty artifact path")
        if not isinstance(artifact_hash, str) or not SHA256_PATTERN.fullmatch(artifact_hash):
            errors.append("a bound receipt requires a lowercase artifact SHA-256")
        if not isinstance(artifact_size, int) or isinstance(artifact_size, bool) or artifact_size < 0:
            errors.append("a bound receipt requires a non-negative artifact size")
        if not isinstance(payload_hash, str) or not SHA256_PATTERN.fullmatch(payload_hash):
            errors.append("a bound receipt requires a lowercase payload SHA-256")
        if receipt.get("created_at") is None:
            errors.append("a bound receipt requires created_at")

    status = decision.get("status")
    explicit = decision.get("explicit_user_approval")
    approver = decision.get("approver")
    decided_at = decision.get("decided_at")
    recorded_at = decision.get("recorded_at")
    recorded_by = decision.get("recorded_by")
    evidence_kind = evidence.get("kind")
    evidence_reference = evidence.get("reference")
    evidence_excerpt = evidence.get("excerpt")
    whole_artifact = scope.get("whole_artifact")
    approved_layers = scope.get("approved_layers")
    created_at = parse_rfc3339(receipt.get("created_at"))
    decision_time = parse_rfc3339(decided_at)
    recorded_time = parse_rfc3339(recorded_at)
    now = datetime.now(timezone.utc)

    if binding_status == "bound" and created_at is not None and created_at > now:
        errors.append("created_at cannot be in the future")

    if status == "pending":
        if explicit is not False:
            errors.append("a pending receipt cannot claim explicit user approval")
        if any(value is not None for value in (approver, decided_at, recorded_at, recorded_by)):
            errors.append("a pending receipt cannot name an approver, decision time, recording time, or recorder")
        if evidence_kind != "none" or evidence_reference or evidence_excerpt:
            errors.append("a pending receipt cannot contain decision evidence")
        if whole_artifact is not False or approved_layers:
            errors.append("a pending receipt cannot approve scope")
    elif status == "approved":
        if binding_status != "bound":
            errors.append("approval requires an artifact bound to an exact SHA-256")
        if explicit is not True:
            errors.append("approved status requires explicit_user_approval=true")
        for label, value in (
            ("approver", approver),
            ("decided_at", decided_at),
            ("recorded_at", recorded_at),
            ("recorded_by", recorded_by),
            ("evidence.reference", evidence_reference),
            ("evidence.excerpt", evidence_excerpt),
        ):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"approved status requires non-empty {label}")
        if evidence_kind in (None, "none"):
            errors.append("approved status requires a concrete evidence kind")
        elif not is_verifiable_human_reference(evidence_kind, evidence_reference):
            errors.append(
                "approved status requires a verifiable human reference: "
                "thread:<id>/turn:<id>, review:<id>/decision:<id>, or "
                f"signed-form:sha256:<digest>; got {evidence_reference!r}"
            )
        if not is_human_identity(approver):
            errors.append("approved status requires an explicitly identified human approver")
        if whole_artifact is not True and not approved_layers:
            errors.append("approved status requires whole-artifact or layer-specific scope")
    elif status in {"changes_requested", "rejected"}:
        if explicit is not False:
            errors.append(f"{status} cannot set explicit_user_approval=true")
        for label, value in (
            ("approver", approver),
            ("decided_at", decided_at),
            ("recorded_at", recorded_at),
            ("recorded_by", recorded_by),
            ("evidence.reference", evidence_reference),
            ("evidence.excerpt", evidence_excerpt),
        ):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{status} requires non-empty {label}")
        if evidence_kind in (None, "none"):
            errors.append(f"{status} requires a concrete evidence kind")
        elif not is_verifiable_human_reference(evidence_kind, evidence_reference):
            errors.append(f"{status} requires a verifiable human evidence reference")
        if not is_human_identity(approver):
            errors.append(f"{status} requires an explicitly identified human approver")
        if whole_artifact is not False or approved_layers:
            errors.append(f"{status} cannot contain approved scope")

    if status != "pending":
        if decision_time is not None and decision_time > now:
            errors.append("decided_at cannot be in the future")
        if recorded_time is not None:
            if recorded_time > now:
                errors.append("recorded_at cannot be in the future")
            if decision_time is not None and decision_time > recorded_time:
                errors.append("decided_at cannot follow recorded_at")
            if created_at is not None and created_at > recorded_time:
                errors.append("created_at cannot follow recorded_at")

    return errors


def validate_receipt(receipt, schema_path=DEFAULT_SCHEMA):
    return schema_errors(receipt, schema_path) + semantic_errors(receipt)


def prepare_receipt(
    artifact_path,
    *,
    receipt_id,
    project_id,
    video_id,
    media_role="editorial_mezzanine",
    profile_id=None,
    created_at=None,
    notes="",
):
    """Create a hash-bound *pending* receipt without recording a decision."""
    artifact_path = Path(artifact_path).expanduser().resolve()
    if media_role not in MEDIA_ROLES:
        raise ApprovalReceiptError(f"unsupported media role: {media_role}")
    fingerprint = file_fingerprint(artifact_path)
    receipt = {
        "schema_version": "1.0.0",
        "receipt_id": receipt_id,
        "project_id": project_id,
        "video_id": video_id,
        "artifact": {
            "binding_status": "bound",
            "path": str(artifact_path),
            "sha256": fingerprint["sha256"],
            "size_bytes": fingerprint["size_bytes"],
            "media_role": media_role,
            "profile_id": profile_id,
        },
        "decision": copy.deepcopy(PENDING_DECISION),
        "binding": {
            "algorithm": "sha256",
            "canonicalization": "json-sort-keys-utf8-v1",
            "payload_sha256": None,
        },
        "created_at": created_at or utc_now(),
        "notes": notes,
    }
    receipt["binding"]["payload_sha256"] = payload_sha256(receipt)
    errors = validate_receipt(receipt)
    if errors:
        raise ApprovalReceiptError("prepared receipt is invalid: " + "; ".join(errors))
    return receipt


def _resolve_artifact(receipt, receipt_path=None, artifact_override=None):
    if artifact_override is not None:
        return Path(artifact_override).expanduser().resolve()
    artifact = receipt.get("artifact") if isinstance(receipt.get("artifact"), dict) else {}
    raw = artifact.get("path")
    if not raw:
        return None
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    base = Path(receipt_path).expanduser().resolve().parent if receipt_path else Path.cwd()
    return (base / candidate).resolve()


def resolve_artifact_path(receipt, receipt_path=None, artifact_override=None):
    """Resolve the artifact referenced by a receipt without modifying it."""
    return _resolve_artifact(receipt, receipt_path, artifact_override)


def seal_receipt(receipt, *, receipt_path=None, artifact_override=None, schema_path=DEFAULT_SCHEMA):
    """Recompute payload integrity only after validating explicit decision evidence.

    This does not create evidence or alter decision fields. It refuses to rebind
    a changed artifact; use ``prepare`` for a different file.
    """
    sealed = copy.deepcopy(receipt)
    artifact = sealed.get("artifact") if isinstance(sealed.get("artifact"), dict) else {}
    binding = sealed.get("binding") if isinstance(sealed.get("binding"), dict) else {}
    if artifact.get("binding_status") != "bound":
        raise ApprovalReceiptError("only a bound receipt can be sealed")
    path = _resolve_artifact(sealed, receipt_path, artifact_override)
    if path is None:
        raise ApprovalReceiptError(f"bound artifact does not exist: {path}")
    fingerprint = file_fingerprint(path)
    if fingerprint["sha256"] != artifact.get("sha256"):
        raise ApprovalReceiptError("artifact SHA-256 changed; prepare a new receipt instead of rebinding")
    if fingerprint["size_bytes"] != artifact.get("size_bytes"):
        raise ApprovalReceiptError("artifact size changed; prepare a new receipt instead of rebinding")

    stored_hash = binding.get("payload_sha256") if isinstance(binding, dict) else None
    if not isinstance(stored_hash, str) or not SHA256_PATTERN.fullmatch(stored_hash):
        raise ApprovalReceiptError("receipt must carry the intact payload hash created by prepare")

    current_hash = payload_sha256(sealed)
    if stored_hash != current_hash:
        prepared = copy.deepcopy(sealed)
        prepared["decision"] = copy.deepcopy(PENDING_DECISION)
        if payload_sha256(prepared) != stored_hash:
            raise ApprovalReceiptError(
                "prepared receipt integrity failed; only decision fields may change before first seal"
            )
        if sealed.get("decision", {}).get("status") == "pending":
            raise ApprovalReceiptError("a pending receipt with altered fields cannot be resealed")

    sealed["binding"]["payload_sha256"] = payload_sha256(sealed)
    errors = validate_receipt(sealed, schema_path)
    if errors:
        raise ApprovalReceiptError("receipt cannot be sealed: " + "; ".join(errors))
    return sealed


def verify_receipt(receipt, *, receipt_path=None, artifact_override=None, schema_path=DEFAULT_SCHEMA):
    errors = validate_receipt(receipt, schema_path)
    artifact = receipt.get("artifact") if isinstance(receipt.get("artifact"), dict) else {}
    decision = receipt.get("decision") if isinstance(receipt.get("decision"), dict) else {}
    binding = receipt.get("binding") if isinstance(receipt.get("binding"), dict) else {}

    if artifact.get("binding_status") != "bound":
        artifact_status = "unbound"
        actual_artifact_hash = None
        actual_size = None
    else:
        path = _resolve_artifact(receipt, receipt_path, artifact_override)
        if path is None or not path.is_file():
            artifact_status = "missing"
            actual_artifact_hash = None
            actual_size = None
            errors.append(f"bound artifact is missing: {path}")
        else:
            try:
                fingerprint = file_fingerprint(path)
            except (ApprovalReceiptError, OSError) as error:
                artifact_status = "unreadable"
                actual_artifact_hash = None
                actual_size = None
                errors.append(f"bound artifact cannot be fingerprinted: {error}")
                fingerprint = None
            if fingerprint is None:
                hash_matches = False
                size_matches = False
            else:
                actual_artifact_hash = fingerprint["sha256"]
                actual_size = fingerprint["size_bytes"]
                hash_matches = actual_artifact_hash == artifact.get("sha256")
                size_matches = actual_size == artifact.get("size_bytes")
            if fingerprint is not None:
                if hash_matches and size_matches:
                    artifact_status = "match"
                elif not hash_matches and not size_matches:
                    artifact_status = "hash_and_size_mismatch"
                elif not hash_matches:
                    artifact_status = "hash_mismatch"
                else:
                    artifact_status = "size_mismatch"
                if artifact_status != "match":
                    errors.append(f"artifact binding failed: {artifact_status}")

    stored_payload_hash = binding.get("payload_sha256")
    if stored_payload_hash is None:
        binding_status = "unsealed"
    else:
        binding_status = "match" if stored_payload_hash == payload_sha256(receipt) else "mismatch"
        if binding_status == "mismatch":
            errors.append("receipt payload SHA-256 does not match its current contents")

    approval_status = decision.get("status", "unknown")
    usable = (
        not errors
        and artifact_status == "match"
        and binding_status == "match"
        and approval_status == "approved"
        and decision.get("explicit_user_approval") is True
    )
    if errors:
        overall = "invalid"
    elif usable:
        overall = "approved_match"
    elif approval_status == "pending":
        overall = "valid_pending"
    else:
        overall = "valid_decision"
    return {
        "schema_version": "1.0.0",
        "receipt_id": receipt.get("receipt_id"),
        "project_id": receipt.get("project_id"),
        "video_id": receipt.get("video_id"),
        "overall_status": overall,
        "document_status": "valid" if not errors else "invalid",
        "artifact_status": artifact_status,
        "binding_status": binding_status,
        "approval_status": approval_status,
        "explicit_user_approval": decision.get("explicit_user_approval") is True,
        "usable_as_approval": usable,
        "integrity_status": binding_status,
        "authenticity_status": (
            "human_reference_present_not_cryptographically_authenticated"
            if usable
            else "not_established"
        ),
        "security_notice": (
            "SHA-256 proves integrity only. Verify the referenced human evidence independently; "
            "use an external digital signature when cryptographic identity is required."
        ),
        "expected_artifact_sha256": artifact.get("sha256"),
        "actual_artifact_sha256": actual_artifact_hash,
        "expected_size_bytes": artifact.get("size_bytes"),
        "actual_size_bytes": actual_size,
        "errors": errors,
    }


def emit_json(value, *, out=None, write=False):
    if out is not None and not write:
        raise ApprovalReceiptError("--out requires explicit --write; default operation is read-only")
    if write and out is None:
        raise ApprovalReceiptError("--write requires --out")
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if out is not None:
        atomic_write_text(out, encoded)
    print(encoded, end="")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="hash an artifact and emit a pending receipt")
    prepare.add_argument("--artifact", type=Path, required=True)
    prepare.add_argument("--receipt-id", required=True)
    prepare.add_argument("--project-id", required=True)
    prepare.add_argument("--video-id", required=True)
    prepare.add_argument("--media-role", choices=sorted(MEDIA_ROLES), default="editorial_mezzanine")
    prepare.add_argument("--profile-id")
    prepare.add_argument("--created-at")
    prepare.add_argument("--notes", default="")
    prepare.add_argument("--out", type=Path)
    prepare.add_argument("--write", action="store_true")

    seal = subparsers.add_parser("seal", help="validate supplied evidence and reseal receipt payload")
    seal.add_argument("--receipt", type=Path, required=True)
    seal.add_argument("--artifact", type=Path)
    seal.add_argument("--out", type=Path)
    seal.add_argument("--write", action="store_true")

    verify = subparsers.add_parser("verify", help="read-only verification of document and artifact hashes")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--artifact", type=Path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            value = prepare_receipt(
                args.artifact,
                receipt_id=args.receipt_id,
                project_id=args.project_id,
                video_id=args.video_id,
                media_role=args.media_role,
                profile_id=args.profile_id,
                created_at=args.created_at,
                notes=args.notes,
            )
            emit_json(value, out=args.out, write=args.write)
            return 0
        receipt = load_json(args.receipt, "approval receipt")
        if args.command == "seal":
            value = seal_receipt(
                receipt,
                receipt_path=args.receipt,
                artifact_override=args.artifact,
            )
            emit_json(value, out=args.out, write=args.write)
            return 0
        result = verify_receipt(
            receipt,
            receipt_path=args.receipt,
            artifact_override=args.artifact,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["overall_status"] == "approved_match":
            return 0
        if result["overall_status"] == "valid_pending":
            return 4
        if result["overall_status"] == "valid_decision":
            return 5
        return 3
    except (ApprovalReceiptError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
