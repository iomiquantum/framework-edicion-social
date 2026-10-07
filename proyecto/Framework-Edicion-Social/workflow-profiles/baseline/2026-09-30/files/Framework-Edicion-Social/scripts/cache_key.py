#!/usr/bin/env python3
"""Build a deterministic cache key for the six production input families."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


CACHE_KEY_VERSION = "1"
ASSET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class CacheKeyError(ValueError):
    pass


def _hash_file(path: Path):
    if path.is_symlink():
        raise CacheKeyError(f"symbolic links are not accepted as cache inputs: {path}")
    try:
        before = path.stat()
    except FileNotFoundError as error:
        raise CacheKeyError(f"cache input does not exist: {path}") from error
    if not path.is_file():
        raise CacheKeyError(f"cache input is not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    after = path.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise CacheKeyError(f"cache input changed while hashing: {path}")
    return digest.hexdigest()


def hash_path(path: Path | str):
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise CacheKeyError(f"symbolic links are not accepted as cache inputs: {candidate}")
    path = candidate.resolve()
    if path.is_file():
        return _hash_file(path)
    if not path.is_dir():
        raise CacheKeyError(f"cache input does not exist: {path}")

    before_entries = sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix())
    linked = next((item for item in before_entries if item.is_symlink()), None)
    if linked is not None:
        raise CacheKeyError(f"symbolic links are not accepted in cache directories: {linked}")
    before_files = [item.relative_to(path).as_posix() for item in before_entries if item.is_file()]
    digest = hashlib.sha256()
    digest.update(b"directory-v1\0")
    for relative in before_files:
        child = path / relative
        if child.is_symlink():
            raise CacheKeyError(f"symbolic links are not accepted in cache directories: {child}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_hash_file(child).encode("ascii"))
        digest.update(b"\0")
    after_entries = sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix())
    if any(item.is_symlink() for item in after_entries):
        raise CacheKeyError(f"cache directory gained a symbolic link while hashing: {path}")
    after_files = [item.relative_to(path).as_posix() for item in after_entries if item.is_file()]
    if before_files != after_files:
        raise CacheKeyError(f"cache directory changed while hashing: {path}")
    return digest.hexdigest()


def parse_assets(specifications):
    assets = {}
    for specification in specifications:
        if "=" not in specification:
            raise CacheKeyError("each --asset must use ID=PATH")
        asset_id, raw_path = specification.split("=", 1)
        if not ASSET_ID.fullmatch(asset_id):
            raise CacheKeyError(f"invalid asset id: {asset_id!r}")
        if asset_id in assets:
            raise CacheKeyError(f"duplicate asset id: {asset_id}")
        if not raw_path:
            raise CacheKeyError(f"asset {asset_id} has an empty path")
        assets[asset_id] = Path(raw_path)
    return assets


def compute_cache_manifest(*, source, transcription, cut_plan, style, assets, mix):
    scalar_paths = {
        "source": Path(source),
        "transcription": Path(transcription),
        "cut_plan": Path(cut_plan),
        "style": Path(style),
        "mix": Path(mix),
    }
    if not isinstance(assets, dict):
        raise CacheKeyError("assets must be a mapping of logical id to path")
    if len(assets) != len(set(assets)):
        raise CacheKeyError("asset ids must be unique")

    component_hashes = {name: hash_path(path) for name, path in scalar_paths.items()}
    asset_hashes = {asset_id: hash_path(assets[asset_id]) for asset_id in sorted(assets)}
    key_material = {
        "cache_key_version": CACHE_KEY_VERSION,
        "source": component_hashes["source"],
        "transcription": component_hashes["transcription"],
        "cut_plan": component_hashes["cut_plan"],
        "style": component_hashes["style"],
        "assets": asset_hashes,
        "mix": component_hashes["mix"],
    }
    canonical = json.dumps(key_material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    key = hashlib.sha256(b"framework-edicion-social-cache\0" + canonical).hexdigest()
    return {
        "schema_version": "1.0.0",
        "algorithm": "sha256",
        "cache_key_version": CACHE_KEY_VERSION,
        "cache_key": key,
        "components": {
            **{name: {"path": str(path.expanduser().resolve()), "sha256": component_hashes[name]} for name, path in scalar_paths.items()},
            "assets": [
                {
                    "id": asset_id,
                    "path": str(Path(assets[asset_id]).expanduser().resolve()),
                    "sha256": asset_hashes[asset_id],
                }
                for asset_id in sorted(assets)
            ],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--transcription", type=Path, required=True)
    parser.add_argument("--cut-plan", type=Path, required=True)
    parser.add_argument("--style", type=Path, required=True, help="style file or directory")
    parser.add_argument("--asset", action="append", default=[], help="logical ID=PATH; repeatable")
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true", help="print full manifest instead of only the key")
    args = parser.parse_args(argv)
    try:
        result = compute_cache_manifest(
            source=args.source,
            transcription=args.transcription,
            cut_plan=args.cut_plan,
            style=args.style,
            assets=parse_assets(args.asset),
            mix=args.mix,
        )
        if args.out:
            atomic_write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result["cache_key"])
        return 0
    except (CacheKeyError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
