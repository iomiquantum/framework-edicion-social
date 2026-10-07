#!/usr/bin/env python3
"""Production preflight for projects that consume Framework-Edicion-Social."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from check_qa_scorecard import analyze_scorecard


FRAMEWORK = Path(__file__).resolve().parents[1]
CATALOG_PATH = FRAMEWORK / "library/catalog.json"
STYLE_CATALOG_PATH = FRAMEWORK / "styles/catalog.json"


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finding(severity, code, message, path=None, video_id=None):
    item = {"severity": severity, "code": code, "message": message}
    if path is not None:
        item["path"] = str(path)
    if video_id is not None:
        item["video_id"] = video_id
    return item


def is_forbidden(asset):
    approval = asset.get("approval", {})
    reuse = asset.get("reuse", {})
    return (
        asset.get("status") == "deprecated"
        or approval.get("user_approval_status") == "explicit_rejected"
        or approval.get("reuse_status") == "ineligible"
        or reuse.get("policy") == "do_not_reuse"
    )


def resolve_style_path(raw):
    candidate = (FRAMEWORK / raw).resolve()
    if candidate.exists():
        return candidate
    alternate = (STYLE_CATALOG_PATH.parent / raw).resolve()
    return alternate if alternate.exists() else candidate


def style_package_sha256(root):
    digest = hashlib.sha256()
    for name in ("README.md", "motion.json", "style.json"):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / name).read_bytes())
    return digest.hexdigest()


def collect_manifests(project, requested_videos):
    manifests = sorted(project.glob("VIDEO-*/manifest.json"))
    if (project / "manifest.json").is_file():
        manifests.append(project / "manifest.json")
    if not requested_videos:
        return manifests
    wanted = set(requested_videos)
    selected = []
    for path in manifests:
        try:
            video_id = read_json(path).get("video_id")
        except (OSError, json.JSONDecodeError):
            video_id = path.parent.name
        if video_id in wanted:
            selected.append(path)
    return selected


def inspect_styles(findings):
    catalog = read_json(STYLE_CATALOG_PATH)
    seen = set()
    for style in catalog.get("styles", []):
        style_id = style.get("id", "unknown")
        if style_id in seen:
            findings.append(finding("error", "STYLE_DUPLICATE", f"Duplicate style {style_id}", STYLE_CATALOG_PATH))
            continue
        seen.add(style_id)
        root = resolve_style_path(style.get("canonical_path", ""))
        if not root.is_dir():
            findings.append(finding("error", "STYLE_PATH_MISSING", f"{style_id} path does not exist", root))
            continue
        for name in ("README.md", "style.json", "motion.json"):
            target = root / name
            if not target.is_file():
                findings.append(finding("error", "STYLE_FILE_MISSING", f"{style_id} is missing {name}", target))
        style_file = root / "style.json"
        motion_file = root / "motion.json"
        if style_file.is_file() and motion_file.is_file():
            style_data = read_json(style_file)
            motion_data = read_json(motion_file)
            if style_data.get("id") != style_id or motion_data.get("style_id") != style_id:
                findings.append(finding("error", "STYLE_ID_DRIFT", f"{style_id} identifiers disagree across files", root))
            if style_data.get("version") != motion_data.get("version"):
                findings.append(finding("error", "STYLE_VERSION_DRIFT", f"{style_id} style and motion versions differ", root))
            declared_version = style.get("version")
            if declared_version and declared_version != style_data.get("version"):
                findings.append(finding("error", "STYLE_CATALOG_VERSION_DRIFT", f"{style_id} catalog version differs from style.json", root))
            if not declared_version:
                findings.append(finding("warning", "STYLE_VERSION_UNLOCKED", f"{style_id} has no version in styles/catalog.json", STYLE_CATALOG_PATH))
            declared_hash = style.get("package_sha256")
            if not declared_hash:
                findings.append(finding("warning", "STYLE_HASH_UNLOCKED", f"{style_id} has no package hash", STYLE_CATALOG_PATH))
            elif style_package_sha256(root) != declared_hash:
                findings.append(finding("error", "STYLE_PACKAGE_HASH_DRIFT", f"{style_id} files changed without a catalog version/hash update", root))


def inspect_sources(project, stage, deep, requested_videos, findings):
    manifest_path = project / "00-INGESTA/source-manifest.json"
    if not manifest_path.is_file():
        findings.append(finding("warning", "SOURCE_MANIFEST_MISSING", "No 00-INGESTA/source-manifest.json was found", manifest_path))
        return
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as error:
        findings.append(finding("error", "SOURCE_MANIFEST_INVALID", str(error), manifest_path))
        return
    wanted = set(requested_videos)
    for source in manifest.get("sources", []):
        if wanted and not wanted.intersection(source.get("expected_video_ids", [])):
            continue
        path = manifest_path.parent / source.get("file", "")
        source_id = source.get("id", path.name)
        if not path.is_file():
            findings.append(finding("error", "SOURCE_FILE_MISSING", f"Missing source {source_id}", path))
            continue
        expected_size = source.get("size_bytes")
        if expected_size is not None and path.stat().st_size != expected_size:
            findings.append(finding("error", "SOURCE_SIZE_DRIFT", f"{source_id} size changed", path))
        if deep and source.get("sha256") and sha256(path) != source["sha256"]:
            findings.append(finding("error", "SOURCE_HASH_DRIFT", f"{source_id} hash changed", path))
        selection = source.get("audio_stream_selection")
        if selection in (None, "", "pending_listen"):
            severity = "warning" if stage == "ingest" else "error"
            findings.append(finding(severity, "AUDIO_STREAM_UNLOCKED", f"{source_id} audio stream has not been selected by listening", manifest_path))


def selected_audio_index(selection):
    if isinstance(selection, int):
        return selection
    if isinstance(selection, dict) and isinstance(selection.get("index"), int):
        return selection["index"]
    if isinstance(selection, str) and selection.isdigit():
        return int(selection)
    return None


def inspect_ingest_artifacts(project, stage, deep, requested_videos, findings):
    """Ensure edit/render tasks consume the shared ingest instead of rescanning masters."""
    if stage == "ingest":
        return
    source_manifest_path = project / "00-INGESTA/source-manifest.json"
    if not source_manifest_path.is_file():
        return
    source_manifest = read_json(source_manifest_path)
    source_by_id = {source.get("id"): source for source in source_manifest.get("sources", [])}
    expected_videos = {
        video_id
        for source in source_manifest.get("sources", [])
        for video_id in source.get("expected_video_ids", [])
    }
    wanted = set(requested_videos) if requested_videos else expected_videos
    mapped_videos = {}

    map_paths = sorted(
        path
        for path in (project / "00-INGESTA").glob("take-map-*.json")
        if not path.name.endswith("-proxy-manifest.json")
    )
    if not map_paths:
        findings.append(finding(
            "error",
            "TAKE_MAP_MISSING",
            "Shared one-pass ingest is incomplete: no reviewed take-map-*.json exists",
            project / "00-INGESTA"
        ))
        return

    for map_path in map_paths:
        try:
            take_map = read_json(map_path)
        except (OSError, json.JSONDecodeError) as error:
            findings.append(finding("error", "TAKE_MAP_INVALID", str(error), map_path))
            continue
        map_video_ids = {video.get("video_id") for video in take_map.get("videos", [])}
        if requested_videos and not wanted.intersection(map_video_ids):
            continue
        qa = take_map.get("qa", {})
        if not qa.get("human_review_completed"):
            findings.append(finding("error", "TAKE_MAP_UNREVIEWED", "Marker map has not completed human review", map_path))
        unresolved = []
        if qa.get("unknown_markers"):
            unresolved.append("unknown markers")
        if qa.get("orphan_decision_markers"):
            unresolved.append("orphan decisions")
        if qa.get("orphan_correction_markers"):
            unresolved.append("orphan corrections")
        affected_multiple = set(qa.get("multiple_approved_videos", [])).intersection(wanted)
        if affected_multiple:
            unresolved.append("multiple approved takes")
        affected_duplicates = [
            take_id for take_id in qa.get("duplicate_take_ids", [])
            if any(take_id.startswith(f"{video_id}-TAKE-") for video_id in wanted)
        ]
        if affected_duplicates:
            unresolved.append("duplicate take identifiers")
        affected_ambiguous = {
            video.get("video_id")
            for video in take_map.get("videos", [])
            if video.get("video_id") in wanted
            and any(
                str(take.get("decision", {}).get("status", "")).startswith("ambiguous")
                for take in video.get("takes", [])
            )
        }
        if affected_ambiguous:
            unresolved.append("ambiguous takes")
        affected_corrections = [
            correction
            for video in take_map.get("videos", [])
            if video.get("video_id") in wanted
            for take in video.get("takes", [])
            for correction in take.get("corrections", [])
            if correction.get("status") != "resolved"
        ]
        if affected_corrections:
            unresolved.append("phrase corrections pending audio review")
        if unresolved:
            findings.append(finding(
                "error", "TAKE_MAP_UNRESOLVED",
                f"Marker map still contains unresolved items: {', '.join(unresolved)}",
                map_path
            ))

        source_record = take_map.get("source", {})
        source_id = source_record.get("id")
        manifest_source = source_by_id.get(source_id)
        if not manifest_source:
            findings.append(finding("error", "TAKE_MAP_SOURCE_UNKNOWN", f"Unknown source id {source_id}", map_path))
        else:
            if source_record.get("sha256") != manifest_source.get("sha256"):
                findings.append(finding("error", "TAKE_MAP_SOURCE_HASH_DRIFT", f"{source_id} hash differs from source manifest", map_path))
            map_audio = source_record.get("audio_stream_index")
            manifest_audio = selected_audio_index(manifest_source.get("audio_stream_selection"))
            if map_audio is None:
                findings.append(finding("error", "TAKE_MAP_AUDIO_UNLOCKED", f"{source_id} has no audio_stream_index", map_path))
            elif manifest_audio is not None and map_audio != manifest_audio:
                findings.append(finding("error", "TAKE_MAP_AUDIO_DRIFT", f"{source_id} audio selection differs from source manifest", map_path))

        for video in take_map.get("videos", []):
            video_id = video.get("video_id")
            if video_id in mapped_videos:
                findings.append(finding("error", "VIDEO_MAPPED_TWICE", f"{video_id} appears in more than one take map", map_path, video_id))
            mapped_videos[video_id] = (video, take_map, map_path)

    for video_id in sorted(wanted):
        entry = mapped_videos.get(video_id)
        if not entry:
            findings.append(finding("error", "VIDEO_TAKE_MISSING", f"{video_id} has no reviewed take entry", project / "00-INGESTA", video_id))
            continue
        video, take_map, map_path = entry
        selected = video.get("selected_take_id")
        if not selected:
            findings.append(finding("error", "VIDEO_TAKE_UNSELECTED", f"{video_id} has no selected approved take", map_path, video_id))
            continue
        take = next((item for item in video.get("takes", []) if item.get("take_id") == selected), None)
        if not take or take.get("decision", {}).get("status") != "approved":
            findings.append(finding("error", "VIDEO_TAKE_NOT_APPROVED", f"{selected} is not an approved take", map_path, video_id))
            continue
        proxy_root = project / video_id / "source"
        stem = selected.lower()
        proxy_path = proxy_root / f"{stem}-proxy.mp4"
        range_path = proxy_root / f"{stem}-source-range.json"
        if not proxy_path.is_file():
            findings.append(finding("error", "EDITING_PROXY_MISSING", f"Missing proxy for {selected}", proxy_path, video_id))
        if not range_path.is_file():
            findings.append(finding("error", "SOURCE_RANGE_MISSING", f"Missing source range for {selected}", range_path, video_id))
            continue
        try:
            source_range = read_json(range_path)
        except (OSError, json.JSONDecodeError) as error:
            findings.append(finding("error", "SOURCE_RANGE_INVALID", str(error), range_path, video_id))
            continue
        if source_range.get("take_id") != selected or source_range.get("video_id") != video_id:
            findings.append(finding("error", "SOURCE_RANGE_ID_DRIFT", f"Range metadata does not identify {selected}", range_path, video_id))
        if source_range.get("original_source_sha256") != take_map.get("source", {}).get("sha256"):
            findings.append(finding("error", "SOURCE_RANGE_HASH_DRIFT", f"{selected} range points to a different original", range_path, video_id))
        if source_range.get("final_render_must_use_original") is not True:
            findings.append(finding("error", "PROXY_FINAL_RENDER_FORBIDDEN", f"{selected} does not enforce final render from original", range_path, video_id))
        if proxy_path.is_file() and deep and source_range.get("proxy_sha256") and sha256(proxy_path) != source_range["proxy_sha256"]:
            findings.append(finding("error", "PROXY_HASH_DRIFT", f"{selected} proxy hash changed", proxy_path, video_id))


def inspect_manifest(path, catalog_by_id, forbidden_ids, deep, findings, lock_videos):
    try:
        manifest = read_json(path)
    except (OSError, json.JSONDecodeError) as error:
        findings.append(finding("error", "PROJECT_MANIFEST_INVALID", str(error), path))
        return
    video_id = manifest.get("video_id") or path.parent.name
    locked_resources = []
    seen_ids = set()
    for resource in manifest.get("resources", []):
        resource_id = resource.get("id", "")
        if resource_id in seen_ids:
            findings.append(finding("error", "PROJECT_RESOURCE_DUPLICATE", f"Duplicate resource {resource_id}", path, video_id))
        seen_ids.add(resource_id)
        source_id = resource.get("source_asset_id") or (resource_id if resource_id in catalog_by_id else None)
        project_file = path.parent / resource.get("file", "")
        project_hash = None
        if not project_file.is_file():
            findings.append(finding("error", "PROJECT_ASSET_MISSING", f"Missing file for {resource_id}", project_file, video_id))
        else:
            project_hash = sha256(project_file)
            if resource.get("sha256") and project_hash != resource["sha256"]:
                findings.append(finding("error", "PROJECT_ASSET_HASH_DRIFT", f"Hash changed for {resource_id}", project_file, video_id))

        catalog_asset = catalog_by_id.get(source_id) if source_id else None
        if source_id and not catalog_asset:
            findings.append(finding("error", "SOURCE_ASSET_UNKNOWN", f"{resource_id} references unknown catalog asset {source_id}", path, video_id))
        if source_id in forbidden_ids:
            findings.append(finding("error", "ASSET_FORBIDDEN", f"{resource_id} references rejected or ineligible asset {source_id}", path, video_id))
        if catalog_asset:
            if resource.get("source_status") and resource["source_status"] != catalog_asset.get("status"):
                findings.append(finding("error", "SOURCE_STATUS_STALE", f"{resource_id} source status is stale", path, video_id))
            if project_hash and project_hash != catalog_asset.get("sha256"):
                findings.append(finding("error", "SOURCE_COPY_HASH_DRIFT", f"{resource_id} differs from locked catalog file; derive a new ID instead", project_file, video_id))

        locked_resources.append({
            "resource_id": resource_id,
            "source_asset_id": source_id,
            "project_file": str(project_file.relative_to(path.parent.parent if path.parent.name.startswith("VIDEO-") else path.parent)),
            "project_sha256": project_hash or resource.get("sha256", ""),
            "catalog_sha256": catalog_asset.get("sha256") if catalog_asset else None,
            "catalog_status": catalog_asset.get("status") if catalog_asset else "project_only",
            "user_approval_status": (catalog_asset or {}).get("approval", {}).get("user_approval_status", "not_reviewed")
        })
    lock_videos.append({"video_id": video_id, "manifest": str(path), "resources": locked_resources})


def scan_forbidden_references(project, manifests, forbidden_ids, requested_videos, findings):
    if not forbidden_ids:
        return
    patterns = {asset_id: re.compile(rf"(?<![A-Z0-9-]){re.escape(asset_id)}(?![A-Z0-9-])") for asset_id in forbidden_ids}
    docs = []
    for manifest in manifests:
        docs.extend(sorted(manifest.parent.glob("PLAN*.md")))
    if not requested_videos:
        for name in ("RESUMEN_RECURSOS.md",):
            candidate = project / name
            if candidate.is_file():
                docs.append(candidate)
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for asset_id, pattern in patterns.items():
            if pattern.search(text):
                findings.append(finding("error", "FORBIDDEN_REFERENCE_IN_PLAN", f"Plan still mentions {asset_id}", path))
    if not requested_videos:
        summary = project / "resumen_manifest.json"
        if summary.is_file():
            raw = summary.read_text(encoding="utf-8")
            for asset_id, pattern in patterns.items():
                if pattern.search(raw):
                    findings.append(finding("error", "FORBIDDEN_REFERENCE_IN_SUMMARY", f"Summary still mentions {asset_id}", summary))


def scan_forbidden_file_copies(project, catalog_by_id, forbidden_ids, requested_videos, findings):
    """Keep rejected source files out of active VIDEO-NN trees even when unreferenced."""
    forbidden_hashes = {
        asset.get("sha256"): asset_id
        for asset_id, asset in catalog_by_id.items()
        if asset_id in forbidden_ids and asset.get("sha256")
    }
    wanted = set(requested_videos)
    audio_suffixes = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
    for video_root in sorted(project.glob("VIDEO-*")):
        if not video_root.is_dir() or wanted and video_root.name not in wanted:
            continue
        active_audio_roots = [video_root / "audio", *video_root.glob("editable*/.media/audio")]
        for audio_root in active_audio_roots:
            if not audio_root.is_dir():
                continue
            for path in audio_root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in audio_suffixes:
                    continue
                asset_id = forbidden_hashes.get(sha256(path))
                if asset_id:
                    findings.append(finding(
                        "error",
                        "FORBIDDEN_FILE_IN_ACTIVE_TREE",
                        f"Active video tree still contains an exact copy of rejected asset {asset_id}; move it to project quarantine",
                        path,
                        video_root.name,
                    ))


def inspect_rejected_asset_quarantine(project, catalog_by_id, forbidden_ids, findings):
    manifest_path = project / "_quarantine/rejected-sfx/manifest.json"
    if not manifest_path.is_file():
        return
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as error:
        findings.append(finding("error", "QUARANTINE_MANIFEST_INVALID", str(error), manifest_path))
        return
    if manifest.get("recoverable") is not True or manifest.get("policy") != "do_not_reuse":
        findings.append(finding("error", "QUARANTINE_POLICY_INVALID", "Rejected asset quarantine must remain recoverable and do_not_reuse", manifest_path))
    for item in manifest.get("assets", []):
        asset_id = item.get("asset_id")
        catalog_asset = catalog_by_id.get(asset_id)
        if asset_id not in forbidden_ids or not catalog_asset:
            findings.append(finding("error", "QUARANTINE_ASSET_NOT_FORBIDDEN", f"{asset_id} is not a current forbidden catalog asset", manifest_path))
            continue
        declared_hash = item.get("sha256")
        if declared_hash != catalog_asset.get("sha256"):
            findings.append(finding("error", "QUARANTINE_HASH_DRIFT", f"{asset_id} hash differs from catalog", manifest_path))
        filename = item.get("original_filename", "")
        for video_id in item.get("videos", []):
            path = manifest_path.parent / video_id / filename
            if not path.is_file():
                findings.append(finding("error", "QUARANTINE_FILE_MISSING", f"Missing recoverable copy of {asset_id}", path, video_id))
            elif sha256(path) != declared_hash:
                findings.append(finding("error", "QUARANTINE_FILE_HASH_DRIFT", f"Quarantined copy of {asset_id} changed", path, video_id))


def inspect_render_artifacts(manifests, findings):
    for manifest in manifests:
        video_id = manifest.parent.name
        root = manifest.parent
        requirements = {
            "HYPERFRAMES_PROJECT_MISSING": list(root.rglob("hyperframes.json")),
            "CUT_PLAN_MISSING": list(root.rglob("cut-plan.json")),
            "TRANSCRIPT_MISSING": [path for path in root.rglob("*.json") if "transcript" in path.name.lower()],
            "RENDER_MANIFEST_MISSING": list(root.rglob("render-manifest.json")),
            "REVIEW_MP4_MISSING": list(root.rglob("*.mp4")),
            "QA_SCORECARD_MISSING": list(root.rglob("qa-scorecard.json"))
        }
        for code, matches in requirements.items():
            if not matches:
                findings.append(finding("error", code, f"{video_id} is missing a required render deliverable", root, video_id))
        for scorecard_path in requirements["QA_SCORECARD_MISSING"]:
            try:
                scorecard = read_json(scorecard_path)
                qa_report = analyze_scorecard(scorecard)
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
                findings.append(finding("error", "QA_SCORECARD_INVALID", str(error), scorecard_path, video_id))
                continue
            if not qa_report.get("valid"):
                details = "; ".join(
                    f"{item.get('code')}: {item.get('message')}" for item in qa_report.get("errors", [])[:5]
                )
                findings.append(finding("error", "QA_SCORECARD_INVALID", details or "QA scorecard is invalid", scorecard_path, video_id))
            elif not qa_report.get("delivery_ready"):
                blockers = ", ".join(qa_report.get("blockers", [])[:8]) or "pending QA checks"
                findings.append(finding("error", "QA_DELIVERY_BLOCKED", f"QA has not authorized delivery: {blockers}", scorecard_path, video_id))


def write_asset_lock(project, project_id, framework_version, lock_videos):
    lock = {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "framework_version": framework_version,
        "catalog_path": str(CATALOG_PATH.relative_to(project.parent) if CATALOG_PATH.is_relative_to(project.parent) else CATALOG_PATH),
        "catalog_sha256": sha256(CATALOG_PATH),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "videos": lock_videos
    }
    path = project / "asset-lock.json"
    path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Series or single-video project directory")
    parser.add_argument("--video", action="append", default=[], help="Limit to a VIDEO-NN id; repeatable")
    parser.add_argument("--stage", choices=("ingest", "edit", "render"), default="edit")
    parser.add_argument("--deep", action="store_true", help="Also hash large source masters")
    parser.add_argument("--json", action="store_true", help="Print the complete report as JSON")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-lock", action="store_true", help="Write asset-lock.json only when no errors exist")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    findings = []
    if not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 2

    catalog = read_json(CATALOG_PATH)
    catalog_by_id = {asset["id"]: asset for asset in catalog.get("assets", [])}
    forbidden_ids = {asset_id for asset_id, asset in catalog_by_id.items() if is_forbidden(asset)}
    manifests = collect_manifests(project, args.video)
    if not manifests:
        findings.append(finding("error", "VIDEO_MANIFESTS_MISSING", "No matching video manifests were found", project))

    inspect_styles(findings)
    inspect_sources(project, args.stage, args.deep, args.video, findings)
    inspect_ingest_artifacts(project, args.stage, args.deep, args.video, findings)
    lock_videos = []
    for path in manifests:
        inspect_manifest(path, catalog_by_id, forbidden_ids, args.deep, findings, lock_videos)
    scan_forbidden_references(project, manifests, forbidden_ids, args.video, findings)
    scan_forbidden_file_copies(project, catalog_by_id, forbidden_ids, args.video, findings)
    inspect_rejected_asset_quarantine(project, catalog_by_id, forbidden_ids, findings)
    if args.stage == "render":
        inspect_render_artifacts(manifests, findings)

    rules = read_json(FRAMEWORK / "rules/registry.json")
    project_id = project.name
    summary_path = project / "resumen_manifest.json"
    if summary_path.is_file():
        project_id = read_json(summary_path).get("project_id", project_id)

    counts = {level: sum(item["severity"] == level for item in findings) for level in ("error", "warning")}
    report = {
        "schema_version": "1.0.0",
        "project": str(project),
        "project_id": project_id,
        "framework_version": rules.get("framework_version"),
        "stage": args.stage,
        "videos_checked": [item.get("video_id") for item in lock_videos],
        "status": "fail" if counts["error"] else "pass_with_warnings" if counts["warning"] else "pass",
        "counts": counts,
        "findings": findings,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

    if args.write_report:
        report_path = project / "preflight-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.write_lock:
        if counts["error"]:
            findings.append(finding("error", "ASSET_LOCK_BLOCKED", "asset-lock.json was not written because preflight failed", project))
            counts["error"] += 1
            report["status"] = "fail"
            report["counts"] = counts
        else:
            report["asset_lock"] = str(write_asset_lock(project, project_id, rules.get("framework_version", ""), lock_videos))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"PREFLIGHT {report['status'].upper()}: {counts['error']} errors, {counts['warning']} warnings")
        for item in findings:
            location = f" [{item['path']}]" if item.get("path") else ""
            print(f"- {item['severity'].upper()} {item['code']}: {item['message']}{location}")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
