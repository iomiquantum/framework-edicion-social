#!/usr/bin/env python3

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "cache_key.py"
SPEC = importlib.util.spec_from_file_location("cache_key", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CacheKeyTests(unittest.TestCase):
    def make_inputs(self, root):
        paths = {}
        for name in ("source", "transcription", "cut_plan", "mix"):
            path = root / f"{name}.dat"
            path.write_text(name, encoding="utf-8")
            paths[name] = path
        style = root / "style"
        style.mkdir()
        (style / "style.json").write_text('{"accent":"sage"}', encoding="utf-8")
        paths["style"] = style
        asset_a = root / "a.svg"
        asset_b = root / "b.wav"
        asset_a.write_text("asset-a", encoding="utf-8")
        asset_b.write_text("asset-b", encoding="utf-8")
        paths["assets"] = {"ICON-A": asset_a, "SFX-B": asset_b}
        return paths

    def manifest(self, paths, assets=None):
        return MODULE.compute_cache_manifest(
            source=paths["source"],
            transcription=paths["transcription"],
            cut_plan=paths["cut_plan"],
            style=paths["style"],
            assets=paths["assets"] if assets is None else assets,
            mix=paths["mix"],
        )

    def test_key_is_deterministic_and_asset_order_independent(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.make_inputs(Path(temporary))
            forward = self.manifest(paths)["cache_key"]
            reverse_assets = dict(reversed(list(paths["assets"].items())))
            reverse = self.manifest(paths, reverse_assets)["cache_key"]
            self.assertEqual(forward, reverse)

    def test_each_input_family_invalidates_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.make_inputs(Path(temporary))
            original = self.manifest(paths)["cache_key"]
            for name in ("source", "transcription", "cut_plan", "mix"):
                with self.subTest(component=name):
                    prior = paths[name].read_text(encoding="utf-8")
                    paths[name].write_text(prior + "-changed", encoding="utf-8")
                    self.assertNotEqual(self.manifest(paths)["cache_key"], original)
                    paths[name].write_text(prior, encoding="utf-8")
            (paths["style"] / "style.json").write_text("changed-style", encoding="utf-8")
            self.assertNotEqual(self.manifest(paths)["cache_key"], original)
            (paths["style"] / "style.json").write_text('{"accent":"sage"}', encoding="utf-8")
            next(iter(paths["assets"].values())).write_text("changed-asset", encoding="utf-8")
            self.assertNotEqual(self.manifest(paths)["cache_key"], original)

    def test_missing_input_and_bad_asset_specs_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.make_inputs(Path(temporary))
            paths["source"].unlink()
            with self.assertRaisesRegex(MODULE.CacheKeyError, "does not exist"):
                self.manifest(paths)
            with self.assertRaisesRegex(MODULE.CacheKeyError, "ID=PATH"):
                MODULE.parse_assets(["not-a-pair"])
            with self.assertRaisesRegex(MODULE.CacheKeyError, "duplicate"):
                MODULE.parse_assets(["A=/tmp/a", "A=/tmp/b"])

    def test_empty_asset_set_still_produces_a_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.make_inputs(Path(temporary))
            result = self.manifest(paths, {})
            self.assertRegex(result["cache_key"], r"^[a-f0-9]{64}$")
            self.assertEqual(result["components"]["assets"], [])

    def test_symlink_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.dat"
            target.write_text("target", encoding="utf-8")
            link = root / "link.dat"
            link.symlink_to(target)
            with self.assertRaisesRegex(MODULE.CacheKeyError, "symbolic links"):
                MODULE.hash_path(link)


if __name__ == "__main__":
    unittest.main()
