#!/usr/bin/env python3
"""Bloquea la edición individual hasta terminar una sola ingesta compartida."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(code: str, message: str, findings: list[dict[str, str]]) -> None:
    findings.append({"code": code, "message": message})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desde", type=int, required=True, help="Primer número del lote")
    parser.add_argument("--hasta", type=int, required=True, help="Último número del lote")
    parser.add_argument(
        "--project",
        default=str(Path(__file__).resolve().parents[1]),
        help="Raíz de Serie-IA-Negocios-10-Videos",
    )
    parser.add_argument("--write-lock", action="store_true", help="Escribir recibo solo si todo pasa")
    args = parser.parse_args()

    if args.desde < 1 or args.hasta < args.desde:
        parser.error("El rango del lote no es válido")

    project = Path(args.project).expanduser().resolve()
    videos = [f"VIDEO-{number:02d}" for number in range(args.desde, args.hasta + 1)]
    ingest = project / "00-INGESTA"
    take_map_path = ingest / f"take-map-{args.desde:02d}-{args.hasta:02d}.json"
    proxy_manifest_path = ingest / f"take-map-{args.desde:02d}-{args.hasta:02d}-proxy-manifest.json"
    lock_path = ingest / f"ingest-ready-{args.desde:02d}-{args.hasta:02d}.json"
    framework_preflight = project.parent / "Framework-Edicion-Social/scripts/preflight_project.py"
    findings: list[dict[str, str]] = []

    if not take_map_path.is_file():
        fail("TAKE_MAP_MISSING", f"Falta {take_map_path}", findings)
        take_map = {}
    else:
        try:
            take_map = json.loads(take_map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            fail("TAKE_MAP_INVALID", str(error), findings)
            take_map = {}

    qa = take_map.get("qa", {})
    if not qa.get("human_review_completed"):
        fail("TAKE_MAP_UNREVIEWED", "qa.human_review_completed no es true", findings)
    for key in (
        "unknown_markers",
        "orphan_decision_markers",
        "orphan_correction_markers",
        "multiple_approved_videos",
        "duplicate_take_ids",
        "unresolved_corrections",
    ):
        if qa.get(key):
            fail("TAKE_MAP_UNRESOLVED", f"{key} contiene elementos pendientes", findings)

    mapped = {item.get("video_id"): item for item in take_map.get("videos", [])}
    for video_id in videos:
        video = mapped.get(video_id)
        if not video:
            fail("VIDEO_TAKE_MISSING", f"{video_id} no aparece en el take-map", findings)
            continue
        selected = video.get("selected_take_id")
        if not selected:
            fail("VIDEO_TAKE_UNSELECTED", f"{video_id} no tiene toma seleccionada", findings)
            continue
        take = next((item for item in video.get("takes", []) if item.get("take_id") == selected), None)
        if not take or take.get("decision", {}).get("status") != "approved":
            fail("VIDEO_TAKE_NOT_APPROVED", f"{selected} no es una toma aprobada", findings)
        pending = [item for item in (take or {}).get("corrections", []) if item.get("status") != "resolved"]
        if pending:
            fail("VIDEO_CORRECTIONS_PENDING", f"{selected} conserva correcciones sin resolver", findings)

    if not proxy_manifest_path.is_file():
        fail("PROXY_MANIFEST_MISSING", f"Falta {proxy_manifest_path}", findings)

    preflight_report = None
    if framework_preflight.is_file():
        command = [
            sys.executable,
            str(framework_preflight),
            "--project",
            str(project),
            "--stage",
            "edit",
            "--deep",
            "--json",
        ]
        for video_id in videos:
            command.extend(["--video", video_id])
        completed = subprocess.run(command, capture_output=True, text=True)
        try:
            preflight_report = json.loads(completed.stdout)
        except json.JSONDecodeError:
            fail("PREFLIGHT_INVALID", completed.stderr or completed.stdout or "Sin salida JSON", findings)
        else:
            if completed.returncode != 0 or preflight_report.get("status") != "pass":
                for item in preflight_report.get("findings", []):
                    if item.get("severity") == "error":
                        fail(item.get("code", "PREFLIGHT_ERROR"), item.get("message", "Error de preflight"), findings)
    else:
        fail("PREFLIGHT_SCRIPT_MISSING", f"Falta {framework_preflight}", findings)

    if findings:
        report = {
            "status": "fail",
            "batch": f"{args.desde:02d}-{args.hasta:02d}",
            "videos": videos,
            "lock_written": False,
            "findings": findings,
            "instruction": "Resolver el lote una sola vez en 00-INGESTA; no editar ni retranscribir desde VIDEO-NN.",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    receipt = {
        "schema_version": "1.0.0",
        "status": "ready_for_individual_editing",
        "batch": f"{args.desde:02d}-{args.hasta:02d}",
        "videos": videos,
        "take_map": str(take_map_path),
        "take_map_sha256": sha256(take_map_path),
        "proxy_manifest": str(proxy_manifest_path),
        "proxy_manifest_sha256": sha256(proxy_manifest_path),
        "source_sha256": take_map.get("source", {}).get("sha256"),
        "preflight_status": preflight_report.get("status") if preflight_report else None,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }
    if args.write_lock:
        lock_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["lock_written"] = bool(args.write_lock)
    receipt["lock_path"] = str(lock_path)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

