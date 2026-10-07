#!/usr/bin/env python3
"""QA post-render reproducible para uno o mas MP4 finales locales.

El programa solo lee los MP4. Para cada archivo recopila metadatos, verifica una
decodificacion completa, mide loudness EBU R128, calcula SHA-256, extrae seis
fotogramas uniformes y crea una hoja de contacto. El resultado tecnico nunca se
interpreta como aprobacion editorial o visual.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0.0"
FRAME_COUNT = 6
MAX_JOBS = 2


class QaError(RuntimeError):
    """Error de uso o de preflight que impide iniciar el QA."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def run_command(argv: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "argv": argv,
        "exit_code": completed.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def command_evidence(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "argv": result["argv"],
        "exit_code": result["exit_code"],
        "elapsed_seconds": result["elapsed_seconds"],
    }


def first_line(command: str) -> str:
    result = run_command([command, "-version"])
    if result["exit_code"] != 0:
        raise QaError(f"No se pudo ejecutar {command}: {result['stderr'].strip()}")
    return result["stdout"].splitlines()[0].strip()


def file_stat(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "inode": stat.st_ino,
    }


def sha256_file(path: Path) -> tuple[str, float]:
    started = time.perf_counter()
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest(), round(time.perf_counter() - started, 3)


def safe_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("-._").lower()
    return slug or "video"


def parse_fraction(value: Any) -> float | None:
    if not isinstance(value, str) or value in {"", "0/0", "N/A"}:
        return None
    try:
        return round(float(Fraction(value)), 6)
    except (ValueError, ZeroDivisionError):
        return None


def parse_duration(probe: dict[str, Any]) -> float | None:
    candidates: list[Any] = [probe.get("format", {}).get("duration")]
    candidates.extend(stream.get("duration") for stream in probe.get("streams", []))
    parsed: list[float] = []
    for candidate in candidates:
        try:
            number = float(candidate)
        except (TypeError, ValueError):
            continue
        if number > 0:
            parsed.append(number)
    return max(parsed) if parsed else None


def summarize_probe(probe: dict[str, Any]) -> dict[str, Any]:
    streams = probe.get("streams", [])
    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]

    videos: list[dict[str, Any]] = []
    for stream in video_streams:
        videos.append(
            {
                "index": stream.get("index"),
                "codec_name": stream.get("codec_name"),
                "profile": stream.get("profile"),
                "width": stream.get("width"),
                "height": stream.get("height"),
                "pixel_format": stream.get("pix_fmt"),
                "fps": parse_fraction(stream.get("avg_frame_rate"))
                or parse_fraction(stream.get("r_frame_rate")),
                "frame_rate_raw": stream.get("avg_frame_rate") or stream.get("r_frame_rate"),
                "frames_reported": stream.get("nb_frames"),
                "color_range": stream.get("color_range"),
                "color_space": stream.get("color_space"),
                "color_transfer": stream.get("color_transfer"),
                "color_primaries": stream.get("color_primaries"),
            }
        )

    audios: list[dict[str, Any]] = []
    for stream in audio_streams:
        audios.append(
            {
                "index": stream.get("index"),
                "codec_name": stream.get("codec_name"),
                "profile": stream.get("profile"),
                "sample_rate_hz": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "channel_layout": stream.get("channel_layout"),
                "bit_rate": stream.get("bit_rate"),
            }
        )

    format_info = probe.get("format", {})
    return {
        "duration_seconds": parse_duration(probe),
        "format_name": format_info.get("format_name"),
        "format_long_name": format_info.get("format_long_name"),
        "size_bytes_reported": int(format_info["size"]) if str(format_info.get("size", "")).isdigit() else None,
        "bit_rate": int(format_info["bit_rate"])
        if str(format_info.get("bit_rate", "")).isdigit()
        else None,
        "video_streams": videos,
        "audio_streams": audios,
    }


NUMBER = r"([+-]?(?:\d+(?:\.\d+)?|inf))"


def parse_loudness(stderr: str) -> dict[str, str | None]:
    summary_index = stderr.rfind("Summary:")
    summary = stderr[summary_index:] if summary_index >= 0 else stderr

    def match(pattern: str) -> str | None:
        found = re.search(pattern, summary, flags=re.MULTILINE | re.DOTALL)
        return found.group(1) if found else None

    return {
        "integrated_lufs": match(r"Integrated loudness:\s*\n\s*I:\s*" + NUMBER + r"\s*LUFS"),
        "integrated_threshold_lufs": match(
            r"Integrated loudness:.*?Threshold:\s*" + NUMBER + r"\s*LUFS"
        ),
        "lra_lu": match(r"Loudness range:\s*\n\s*LRA:\s*" + NUMBER + r"\s*LU"),
        "lra_threshold_lufs": match(r"Loudness range:.*?Threshold:\s*" + NUMBER + r"\s*LUFS"),
        "lra_low_lufs": match(r"LRA low:\s*" + NUMBER + r"\s*LUFS"),
        "lra_high_lufs": match(r"LRA high:\s*" + NUMBER + r"\s*LUFS"),
        "true_peak_dbfs": match(r"True peak:\s*\n\s*Peak:\s*" + NUMBER + r"\s*dBFS"),
    }


def md_escape(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def build_markdown(evidence: dict[str, Any]) -> str:
    metadata = evidence.get("metadata", {})
    video = (metadata.get("video_streams") or [{}])[0]
    audio = (metadata.get("audio_streams") or [{}])[0]
    loudness = evidence.get("loudness", {})
    decode = evidence.get("full_decode", {})
    frames = evidence.get("frames", {})
    integrity = evidence.get("input_integrity", {})

    lines = [
        f"# Evidencia de QA post-render — {evidence['input']['name']}",
        "",
        f"- **Estado técnico:** `{evidence['technical_status'].upper()}`",
        "- **Aprobación editorial/visual:** `no evaluada`",
        f"- **Inicio UTC:** `{evidence['started_at']}`",
        f"- **Fin UTC:** `{evidence['finished_at']}`",
        f"- **Tiempo total:** `{evidence['elapsed_seconds']:.3f} s`",
        f"- **Entrada:** `{evidence['input']['path']}`",
        f"- **SHA-256:** `{integrity.get('sha256_before')}`",
        f"- **Entrada sin cambios:** `{str(integrity.get('unchanged')).lower()}`",
        "",
        "> Un pase técnico confirma que las comprobaciones automatizadas terminaron. No equivale a aprobación humana ni a publicación.",
        "",
        "## Metadatos principales",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Duración | {md_escape(metadata.get('duration_seconds'))} s |",
        f"| Contenedor | {md_escape(metadata.get('format_name'))} |",
        f"| Video | {md_escape(video.get('codec_name'))} / {md_escape(video.get('profile'))} |",
        f"| Resolución | {md_escape(video.get('width'))}×{md_escape(video.get('height'))} |",
        f"| FPS | {md_escape(video.get('fps'))} |",
        f"| Pixel format | {md_escape(video.get('pixel_format'))} |",
        f"| Color | {md_escape(video.get('color_primaries'))} / {md_escape(video.get('color_transfer'))} / {md_escape(video.get('color_space'))} |",
        f"| Audio | {md_escape(audio.get('codec_name'))} / {md_escape(audio.get('sample_rate_hz'))} Hz / {md_escape(audio.get('channels'))} canales |",
        "",
        "## Pruebas automatizadas",
        "",
        "| Prueba | Estado | Tiempo | Resultado |",
        "|---|---:|---:|---|",
        f"| ffprobe | {md_escape(evidence.get('ffprobe', {}).get('status'))} | {md_escape(evidence.get('ffprobe', {}).get('elapsed_seconds'))} s | metadatos completos en `ffprobe.json` |",
        f"| Decodificación completa | {md_escape(decode.get('status'))} | {md_escape(decode.get('elapsed_seconds'))} s | exit {md_escape(decode.get('exit_code'))} |",
        f"| EBU R128 | {md_escape(loudness.get('status'))} | {md_escape(loudness.get('elapsed_seconds'))} s | I {md_escape(loudness.get('measurements', {}).get('integrated_lufs'))} LUFS; LRA {md_escape(loudness.get('measurements', {}).get('lra_lu'))} LU; pico {md_escape(loudness.get('measurements', {}).get('true_peak_dbfs'))} dBFS |",
        f"| 6 fotogramas | {md_escape(frames.get('status'))} | {md_escape(frames.get('elapsed_seconds'))} s | {md_escape(len(frames.get('items', [])))} archivos |",
        f"| Hoja de contacto | {md_escape(evidence.get('contact_sheet', {}).get('status'))} | {md_escape(evidence.get('contact_sheet', {}).get('elapsed_seconds'))} s | `contact-sheet.png` |",
        "",
        "## Fotogramas uniformes",
        "",
    ]
    for frame in frames.get("items", []):
        lines.append(
            f"- `{frame['file']}` — `{frame['timestamp_seconds']:.3f} s` "
            f"({frame['position_fraction']:.6f} de la duración)."
        )
    lines.extend(
        [
            "",
            "![Hoja de contacto](contact-sheet.png)",
            "",
            "La hoja conserva la señal decodificada y no aplica una conversión creativa de color. En material HLG/PQ debe interpretarse como evidencia de muestreo, no como simulación certificada de una pantalla HDR.",
            "",
            "## Pendiente humano",
            "",
            "Revisar reproducción completa, sincronía, color en una pantalla adecuada, encuadre, textos y contenido. Esta automatización no asigna el estado `aprobado`.",
            "",
        ]
    )
    return "\n".join(lines)


def qa_one(input_path: Path, run_dir: Path, ffmpeg: str, ffprobe: str, frame_width: int) -> dict[str, Any]:
    started_clock = time.perf_counter()
    started_at = utc_now()
    stat_before = file_stat(input_path)
    sha_before, sha_before_seconds = sha256_file(input_path)
    item_dir = run_dir / f"{safe_slug(input_path.stem)}--{sha_before[:12]}"
    item_dir.mkdir(parents=False, exist_ok=False)

    evidence: dict[str, Any] = {
        "schema_version": 1,
        "script_version": SCRIPT_VERSION,
        "technical_status": "fail",
        "approval_status": "not_evaluated",
        "started_at": started_at,
        "input": {
            "path": str(input_path),
            "name": input_path.name,
            "suffix": input_path.suffix,
        },
    }

    probe_result = run_command(
        [
            ffprobe,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-show_programs",
            "-show_chapters",
            "-of",
            "json",
            str(input_path),
        ]
    )
    atomic_write_text(item_dir / "ffprobe.stderr.log", probe_result["stderr"])
    try:
        probe_payload = json.loads(probe_result["stdout"]) if probe_result["stdout"] else {}
    except json.JSONDecodeError:
        probe_payload = {}
    atomic_write_json(item_dir / "ffprobe.json", probe_payload)
    metadata = summarize_probe(probe_payload)
    has_video = bool(metadata["video_streams"])
    has_audio = bool(metadata["audio_streams"])
    duration = metadata.get("duration_seconds")
    probe_ok = probe_result["exit_code"] == 0 and has_video and duration is not None
    evidence["ffprobe"] = {
        **command_evidence(probe_result),
        "status": "pass" if probe_ok else "fail",
        "has_video": has_video,
        "has_audio": has_audio,
    }
    evidence["metadata"] = metadata

    decode_result = run_command(
        [
            ffmpeg,
            "-nostdin",
            "-hide_banner",
            "-v",
            "error",
            "-xerror",
            "-err_detect",
            "explode",
            "-i",
            str(input_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-sn",
            "-dn",
            "-f",
            "null",
            "-",
        ]
    )
    atomic_write_text(item_dir / "decode.stderr.log", decode_result["stderr"])
    evidence["full_decode"] = {
        **command_evidence(decode_result),
        "status": "pass" if decode_result["exit_code"] == 0 else "fail",
    }

    if has_audio:
        loudness_result = run_command(
            [
                ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-nostats",
                "-i",
                str(input_path),
                "-map",
                "0:a:0",
                "-vn",
                "-af",
                "ebur128=peak=true",
                "-f",
                "null",
                "-",
            ]
        )
        atomic_write_text(item_dir / "loudness-ebur128.stderr.log", loudness_result["stderr"])
        measurements = parse_loudness(loudness_result["stderr"])
        loudness_ok = loudness_result["exit_code"] == 0 and measurements["integrated_lufs"] is not None
        evidence["loudness"] = {
            **command_evidence(loudness_result),
            "status": "pass" if loudness_ok else "fail",
            "measurements": measurements,
        }
    else:
        atomic_write_text(item_dir / "loudness-ebur128.stderr.log", "No audio stream detected.\n")
        evidence["loudness"] = {
            "status": "not_applicable",
            "reason": "no_audio_stream",
            "exit_code": None,
            "elapsed_seconds": 0.0,
            "measurements": {},
        }

    frame_items: list[dict[str, Any]] = []
    frame_logs: list[str] = []
    frames_started = time.perf_counter()
    frames_ok = bool(has_video and duration)
    if has_video and duration:
        for index in range(1, FRAME_COUNT + 1):
            fraction = index / (FRAME_COUNT + 1)
            timestamp = duration * fraction
            frame_name = f"frame-{index:02d}.png"
            frame_result = run_command(
                [
                    ffmpeg,
                    "-nostdin",
                    "-hide_banner",
                    "-v",
                    "error",
                    "-ss",
                    f"{timestamp:.6f}",
                    "-i",
                    str(input_path),
                    "-map",
                    "0:v:0",
                    "-frames:v",
                    "1",
                    "-an",
                    "-sn",
                    "-dn",
                    "-vf",
                    f"scale={frame_width}:-2:flags=lanczos",
                    "-y",
                    str(item_dir / frame_name),
                ]
            )
            frame_exists = (item_dir / frame_name).is_file() and (item_dir / frame_name).stat().st_size > 0
            frame_ok = frame_result["exit_code"] == 0 and frame_exists
            frames_ok = frames_ok and frame_ok
            frame_items.append(
                {
                    "index": index,
                    "file": frame_name,
                    "timestamp_seconds": round(timestamp, 6),
                    "position_fraction": round(fraction, 6),
                    "status": "pass" if frame_ok else "fail",
                    "elapsed_seconds": frame_result["elapsed_seconds"],
                    "exit_code": frame_result["exit_code"],
                }
            )
            if frame_result["stderr"]:
                frame_logs.append(f"--- {frame_name} ---\n{frame_result['stderr']}")
    else:
        frame_logs.append("No se pudieron extraer fotogramas: falta video o duración válida.\n")
    atomic_write_text(item_dir / "frames.stderr.log", "\n".join(frame_logs))
    evidence["frames"] = {
        "status": "pass" if frames_ok and len(frame_items) == FRAME_COUNT else "fail",
        "count_expected": FRAME_COUNT,
        "count_created": sum(1 for item in frame_items if item["status"] == "pass"),
        "elapsed_seconds": round(time.perf_counter() - frames_started, 3),
        "sampling": "duration * i / 7, i=1..6",
        "items": frame_items,
    }

    if evidence["frames"]["status"] == "pass":
        contact_result = run_command(
            [
                ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-v",
                "error",
                "-framerate",
                "1",
                "-start_number",
                "1",
                "-i",
                str(item_dir / "frame-%02d.png"),
                "-frames:v",
                "1",
                "-vf",
                "tile=3x2:padding=12:margin=12:color=black",
                "-y",
                str(item_dir / "contact-sheet.png"),
            ]
        )
        atomic_write_text(item_dir / "contact-sheet.stderr.log", contact_result["stderr"])
        contact_exists = (item_dir / "contact-sheet.png").is_file() and (
            item_dir / "contact-sheet.png"
        ).stat().st_size > 0
        contact_ok = contact_result["exit_code"] == 0 and contact_exists
        evidence["contact_sheet"] = {
            **command_evidence(contact_result),
            "status": "pass" if contact_ok else "fail",
            "file": "contact-sheet.png",
            "layout": "3x2",
        }
    else:
        atomic_write_text(
            item_dir / "contact-sheet.stderr.log",
            "No se creó la hoja: la extracción de seis fotogramas no terminó correctamente.\n",
        )
        evidence["contact_sheet"] = {
            "status": "fail",
            "reason": "frame_extraction_failed",
            "exit_code": None,
            "elapsed_seconds": 0.0,
            "file": None,
            "layout": "3x2",
        }

    sha_after, sha_after_seconds = sha256_file(input_path)
    stat_after = file_stat(input_path)
    unchanged = sha_before == sha_after and stat_before == stat_after
    evidence["input_integrity"] = {
        "sha256_before": sha_before,
        "sha256_after": sha_after,
        "sha256_before_elapsed_seconds": sha_before_seconds,
        "sha256_after_elapsed_seconds": sha_after_seconds,
        "stat_before": stat_before,
        "stat_after": stat_after,
        "unchanged": unchanged,
    }

    required_statuses = [
        evidence["ffprobe"]["status"],
        evidence["full_decode"]["status"],
        evidence["frames"]["status"],
        evidence["contact_sheet"]["status"],
    ]
    loudness_status = evidence["loudness"]["status"]
    if has_audio:
        required_statuses.append(loudness_status)
    technical_pass = all(status == "pass" for status in required_statuses) and unchanged
    evidence["technical_status"] = "pass" if technical_pass else "fail"
    evidence["finished_at"] = utc_now()
    evidence["elapsed_seconds"] = round(time.perf_counter() - started_clock, 3)
    evidence["evidence_directory"] = str(item_dir)

    atomic_write_json(item_dir / "evidence.json", evidence)
    atomic_write_text(item_dir / "EVIDENCE.md", build_markdown(evidence))
    return evidence


def build_summary(run: dict[str, Any]) -> str:
    lines = [
        "# Resumen de QA post-render",
        "",
        f"- **Estado técnico del lote:** `{run['technical_status'].upper()}`",
        "- **Aprobación editorial/visual:** `no evaluada`",
        f"- **Inicio UTC:** `{run['started_at']}`",
        f"- **Fin UTC:** `{run['finished_at']}`",
        f"- **Tiempo total:** `{run['elapsed_seconds']:.3f} s`",
        f"- **Archivos:** `{len(run['results'])}`",
        f"- **Paralelismo:** `{run['jobs']}`",
        "",
        "| Archivo | Estado técnico | Duración | Decode | Loudness | Evidencia |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for result in run["results"]:
        evidence_dir = Path(result["evidence_directory"])
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(result["input"]["name"]),
                    md_escape(result["technical_status"]),
                    f"{md_escape(result.get('metadata', {}).get('duration_seconds'))} s",
                    f"{md_escape(result.get('full_decode', {}).get('elapsed_seconds'))} s",
                    f"{md_escape(result.get('loudness', {}).get('elapsed_seconds'))} s",
                    f"[{evidence_dir.name}/{Path('EVIDENCE.md').name}]({evidence_dir.name}/EVIDENCE.md)",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "> Este resumen no aprueba los videos. La revisión visual y editorial completa sigue pendiente de una persona.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Genera evidencia técnica post-render para uno o más MP4 sin modificarlos ni marcarlos aprobados."
        )
    )
    parser.add_argument("inputs", nargs="+", metavar="MP4", help="Uno o más MP4 finales locales.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directorio nuevo para la evidencia. Si se omite, crea qa-post-render-<UTC> en el cwd.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        choices=range(1, MAX_JOBS + 1),
        metavar="{1,2}",
        help="MP4 procesados en paralelo (predeterminado: 1; máximo seguro: 2).",
    )
    parser.add_argument(
        "--frame-width",
        type=int,
        default=360,
        help="Ancho de cada fotograma de la hoja de contacto (predeterminado: 360).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.frame_width < 160 or args.frame_width > 1080:
        raise QaError("--frame-width debe estar entre 160 y 1080.")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise QaError("Se necesitan ffmpeg y ffprobe disponibles en PATH.")

    inputs: list[Path] = []
    seen: set[Path] = set()
    for raw in args.inputs:
        path = Path(raw).expanduser().resolve(strict=True)
        if not path.is_file():
            raise QaError(f"No es un archivo regular: {path}")
        if path.suffix.lower() != ".mp4":
            raise QaError(f"Solo se aceptan MP4: {path}")
        if path in seen:
            continue
        seen.add(path)
        inputs.append(path)

    run_started_clock = time.perf_counter()
    run_started_at = utc_now()
    if args.output_dir:
        run_dir = args.output_dir.expanduser().resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        run_dir = (Path.cwd() / f"qa-post-render-{stamp}").resolve()
    if run_dir.exists():
        raise QaError(f"El directorio de salida ya existe; no se sobrescribe evidencia: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    jobs = min(args.jobs, len(inputs))
    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(qa_one, path, run_dir, ffmpeg, ffprobe, args.frame_width): path
            for path in inputs
        }
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(
                    f"[{result['technical_status'].upper()}] {path.name} "
                    f"({result['elapsed_seconds']:.3f} s) -> {result['evidence_directory']}",
                    flush=True,
                )
            except Exception as exc:  # evidencia de fallos inesperados del worker
                failures.append({"input": str(path), "error": f"{type(exc).__name__}: {exc}"})
                print(f"[ERROR] {path.name}: {exc}", file=sys.stderr, flush=True)

    results.sort(key=lambda item: item["input"]["path"])
    technical_pass = not failures and len(results) == len(inputs) and all(
        result["technical_status"] == "pass" for result in results
    )
    run = {
        "schema_version": 1,
        "script_version": SCRIPT_VERSION,
        "technical_status": "pass" if technical_pass else "fail",
        "approval_status": "not_evaluated",
        "started_at": run_started_at,
        "finished_at": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - run_started_clock, 3),
        "jobs": jobs,
        "frame_count_per_video": FRAME_COUNT,
        "tool_versions": {
            "python": sys.version.split()[0],
            "ffmpeg": first_line(ffmpeg),
            "ffprobe": first_line(ffprobe),
        },
        "results": results,
        "failures": failures,
        "output_directory": str(run_dir),
    }
    atomic_write_json(run_dir / "summary.json", run)
    atomic_write_text(run_dir / "SUMMARY.md", build_summary(run))
    print(
        f"Resumen: {run['technical_status'].upper()} | {len(results)}/{len(inputs)} MP4 | "
        f"{run['elapsed_seconds']:.3f} s | {run_dir}",
        flush=True,
    )
    return 0 if technical_pass else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (QaError, FileNotFoundError) as exc:
        print(f"qa_post_render: {exc}", file=sys.stderr)
        raise SystemExit(2)
