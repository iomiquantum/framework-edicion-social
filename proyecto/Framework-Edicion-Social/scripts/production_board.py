#!/usr/bin/env python3
"""Atomically claim and release VIDEO-NN work on a shared production board."""

from __future__ import annotations

import argparse
import portable_fcntl as fcntl
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


VIDEO_ID = re.compile(r"^VIDEO-[0-9]{2,}$")
WORKLOADS = {"light", "heavy"}


class BoardError(RuntimeError):
    """The board is malformed or cannot be operated safely."""


class BoardConflict(BoardError):
    """The requested claim/release conflicts with current ownership or capacity."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_nonempty(value, field):
    if not isinstance(value, str) or not value.strip():
        raise BoardError(f"{field} must be a non-empty string")


def validate_board(board):
    if not isinstance(board, dict):
        raise BoardError("board must be a JSON object")
    required = {"schema_version", "project_id", "max_heavy_jobs", "generation", "claims", "updated_at"}
    missing = sorted(required - set(board))
    unknown = sorted(set(board) - required)
    if missing:
        raise BoardError(f"board is missing fields: {', '.join(missing)}")
    if unknown:
        raise BoardError(f"board has unknown fields: {', '.join(unknown)}")
    if board["schema_version"] != "1.0.0":
        raise BoardError("unsupported production board schema_version")
    if not isinstance(board["project_id"], str):
        raise BoardError("project_id must be a string")
    limit = board["max_heavy_jobs"]
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 64:
        raise BoardError("max_heavy_jobs must be an integer from 1 to 64")
    generation = board["generation"]
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
        raise BoardError("generation must be a non-negative integer")
    if not isinstance(board["updated_at"], str):
        raise BoardError("updated_at must be a string")
    claims = board["claims"]
    if not isinstance(claims, list):
        raise BoardError("claims must be an array")
    seen = set()
    for index, claim in enumerate(claims):
        path = f"claims[{index}]"
        if not isinstance(claim, dict):
            raise BoardError(f"{path} must be an object")
        fields = {"video_id", "owner", "workload", "claimed_at", "note"}
        if set(claim) != fields:
            raise BoardError(f"{path} must contain exactly {sorted(fields)}")
        video_id = claim["video_id"]
        if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
            raise BoardError(f"{path}.video_id must match VIDEO-NN")
        if video_id in seen:
            raise BoardError(f"duplicate active claim for {video_id}")
        seen.add(video_id)
        _require_nonempty(claim["owner"], f"{path}.owner")
        if claim["workload"] not in WORKLOADS:
            raise BoardError(f"{path}.workload must be light or heavy")
        _require_nonempty(claim["claimed_at"], f"{path}.claimed_at")
        if not isinstance(claim["note"], str):
            raise BoardError(f"{path}.note must be a string")
    heavy = sum(claim["workload"] == "heavy" for claim in claims)
    if heavy > limit:
        raise BoardError(f"board already exceeds heavy-job limit ({heavy}/{limit})")
    return board


def load_board(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            return validate_board(json.load(handle))
    except FileNotFoundError as error:
        raise BoardError(f"production board does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise BoardError(f"invalid production board JSON: {error}") from error


@contextmanager
def board_lock(path: Path, exclusive=True):
    lock_path = path.with_name(f".{path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        directory_fd = os.open(path.parent, directory_flags)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def initialize(path: Path, project_id: str, max_heavy_jobs: int):
    _require_nonempty(project_id, "project_id")
    if not isinstance(max_heavy_jobs, int) or isinstance(max_heavy_jobs, bool) or not 1 <= max_heavy_jobs <= 64:
        raise BoardError("max_heavy_jobs must be an integer from 1 to 64")
    with board_lock(path):
        if path.exists():
            raise BoardConflict(f"refusing to overwrite existing production board: {path}")
        board = {
            "schema_version": "1.0.0",
            "project_id": project_id,
            "max_heavy_jobs": max_heavy_jobs,
            "generation": 0,
            "claims": [],
            "updated_at": utc_now(),
        }
        atomic_write_json(path, board)
    return board


def claim_video(path: Path, video_id: str, owner: str, workload: str, note=""):
    if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
        raise BoardError("video_id must match VIDEO-NN")
    _require_nonempty(owner, "owner")
    if workload not in WORKLOADS:
        raise BoardError("workload must be light or heavy")
    if not isinstance(note, str):
        raise BoardError("note must be a string")
    owner = owner.strip()
    with board_lock(path):
        board = load_board(path)
        existing = next((item for item in board["claims"] if item["video_id"] == video_id), None)
        if existing:
            if existing["owner"] == owner and existing["workload"] == workload:
                return board, False
            raise BoardConflict(
                f"{video_id} is already owned by {existing['owner']} ({existing['workload']})"
            )
        if workload == "heavy":
            active_heavy = sum(item["workload"] == "heavy" for item in board["claims"])
            if active_heavy >= board["max_heavy_jobs"]:
                raise BoardConflict(
                    f"heavy-job capacity reached ({active_heavy}/{board['max_heavy_jobs']})"
                )
        board["claims"].append(
            {
                "video_id": video_id,
                "owner": owner,
                "workload": workload,
                "claimed_at": utc_now(),
                "note": note,
            }
        )
        board["claims"].sort(key=lambda item: item["video_id"])
        board["generation"] += 1
        board["updated_at"] = utc_now()
        validate_board(board)
        atomic_write_json(path, board)
        return board, True


def release_video(path: Path, video_id: str, owner: str):
    if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
        raise BoardError("video_id must match VIDEO-NN")
    _require_nonempty(owner, "owner")
    owner = owner.strip()
    with board_lock(path):
        board = load_board(path)
        existing = next((item for item in board["claims"] if item["video_id"] == video_id), None)
        if existing is None:
            raise BoardConflict(f"{video_id} is not claimed")
        if existing["owner"] != owner:
            raise BoardConflict(f"{video_id} is owned by {existing['owner']}, not {owner}")
        board["claims"] = [item for item in board["claims"] if item["video_id"] != video_id]
        board["generation"] += 1
        board["updated_at"] = utc_now()
        validate_board(board)
        atomic_write_json(path, board)
        return board


def board_status(path: Path, video_id=None):
    if not path.exists():
        raise BoardError(f"production board does not exist: {path}")
    with board_lock(path, exclusive=False):
        board = load_board(path)
    if video_id is not None:
        if not VIDEO_ID.fullmatch(video_id):
            raise BoardError("video_id must match VIDEO-NN")
        claims = [item for item in board["claims"] if item["video_id"] == video_id]
    else:
        claims = list(board["claims"])
    active_heavy = sum(item["workload"] == "heavy" for item in board["claims"])
    return {
        "project_id": board["project_id"],
        "generation": board["generation"],
        "max_heavy_jobs": board["max_heavy_jobs"],
        "active_heavy_jobs": active_heavy,
        "heavy_slots_available": board["max_heavy_jobs"] - active_heavy,
        "claims": claims,
        "updated_at": board["updated_at"],
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create a new production board")
    init.add_argument("--project-id", required=True)
    init.add_argument("--max-heavy-jobs", type=int, default=1)

    claim = subparsers.add_parser("claim", help="claim one VIDEO-NN")
    claim.add_argument("--video", required=True)
    claim.add_argument("--owner", required=True)
    claim.add_argument("--workload", choices=sorted(WORKLOADS), default="light")
    claim.add_argument("--note", default="")

    release = subparsers.add_parser("release", help="release an owned VIDEO-NN")
    release.add_argument("--video", required=True)
    release.add_argument("--owner", required=True)

    status = subparsers.add_parser("status", help="show current ownership and capacity")
    status.add_argument("--video")
    status.add_argument("--json", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = args.board.expanduser().resolve()
    try:
        if args.command == "init":
            board = initialize(path, args.project_id, args.max_heavy_jobs)
            print(f"initialized {path} (heavy capacity {board['max_heavy_jobs']})")
        elif args.command == "claim":
            board, created = claim_video(path, args.video, args.owner, args.workload, args.note)
            verb = "claimed" if created else "already claimed idempotently"
            print(f"{verb}: {args.video} -> {args.owner} ({args.workload}); generation {board['generation']}")
        elif args.command == "release":
            board = release_video(path, args.video, args.owner)
            print(f"released: {args.video} by {args.owner}; generation {board['generation']}")
        else:
            status = board_status(path, args.video)
            if args.json:
                print(json.dumps(status, ensure_ascii=False, indent=2))
            else:
                print(
                    f"{status['project_id']}: {len(status['claims'])} active, "
                    f"heavy {status['active_heavy_jobs']}/{status['max_heavy_jobs']}"
                )
                for item in status["claims"]:
                    print(f"{item['video_id']}\t{item['owner']}\t{item['workload']}\t{item['claimed_at']}")
        return 0
    except BoardConflict as error:
        print(f"CONFLICT: {error}", file=sys.stderr)
        return 3
    except (BoardError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
