#!/usr/bin/env python3

import copy
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRIPTS = FRAMEWORK / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = load_module("performance_cohorts")
SCHEMAS = load_module("schema_validation")
PUBLISHED = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
METRIC_NAMES = sorted(MODULE.INTEGER_METRICS | MODULE.FLOAT_METRICS)


def timestamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


class EvidenceFixture:
    """Build real, hash-bound publication and measurement evidence."""

    def __init__(self, root, base_media, media_metadata):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.base_media = Path(base_media)
        self.media_metadata = copy.deepcopy(media_metadata)
        self.records = []
        self.attribution_refs = {}
        self.attribution_paths = {}
        self.evidence_counter = 0
        self.production_counter = 0
        self.profile, self.platform_catalog_path = self._install_platform_catalog()
        self.creative_catalog_path = self._install_creative_catalog()

    def _install_platform_catalog(self):
        catalog = read_json(FRAMEWORK / "platforms/catalog.json")
        profile = next(
            item
            for item in catalog["profiles"]
            if item["id"] == "PLATFORM-INSTAGRAM-REELS-ORGANIC-001"
        )
        profile["internal_defaults"]["canvas"].update(
            {"width": 64, "height": 96, "fps": 10, "aspect_ratio": "2:3"}
        )
        profile["internal_defaults"]["video"]["target_bitrate_mbps"] = 0.005
        MODULE.plan_platform_derivatives.validate_catalog_document(catalog)
        path = self.root / "platforms/catalog.json"
        write_json(path, catalog)
        return copy.deepcopy(profile), path

    def _install_creative_catalog(self):
        catalog = read_json(FRAMEWORK / "creative-recipes/catalog.json")
        MODULE.compose_recipe.validate_catalog(catalog)
        path = self.root / "creative/catalog.json"
        write_json(path, catalog)
        return path

    def _creative_attribution(self, video_id, publication_id, published_at, option_index):
        plan = read_json(FRAMEWORK / "templates/creative-recipe-plan.json")
        plan = json.loads(json.dumps(plan).replace("VIDEO-00", video_id))
        catalog_relative = self.creative_catalog_path.relative_to(self.root).as_posix()
        plan["inputs"]["catalog"] = {
            "path": catalog_relative,
            "sha256": MODULE.sha256_file(self.creative_catalog_path),
        }
        catalog = read_json(self.creative_catalog_path)
        MODULE.compose_recipe.validate_plan(plan, catalog=catalog)
        plan_path = self.root / "creative" / f"{video_id}-recipe-plan.json"
        write_json(plan_path, plan)

        proposal = plan["proposals"][option_index]
        attribution = {
            "schema_version": "1.0.0",
            "attribution_id": "ATTR-0000000000000000",
            "project_id": "SERIE-TEST",
            "video_id": video_id,
            "selected_at": timestamp(published_at - timedelta(hours=1)),
            "selection_basis": "explicit_human_selection",
            "selected_by_reference": "human:test-fixture",
            "plan": {
                "path": plan_path.relative_to(self.root).as_posix(),
                "sha256": MODULE.sha256_file(plan_path),
                "plan_id": plan["plan_id"],
            },
            "selection": {
                "option_id": proposal["option_id"],
                "recipe_id": proposal["recipe_id"],
                "primary_family_id": proposal["primary_family_id"],
                "hybrid": proposal["hybrid"],
                "contributing_family_ids": proposal["contributing_family_ids"],
                "module_ids": proposal["module_ids"],
            },
            "governance": {
                "performance_causality_claimed": False,
                "automatic_family_credit": False,
                "human_selection_required": True,
            },
        }
        attribution["attribution_id"] = MODULE.creative_attribution_id(attribution)
        attribution_path = self.root / "creative" / f"{video_id}-attribution.json"
        write_json(attribution_path, attribution)
        reference = {
            "path": attribution_path.relative_to(self.root).as_posix(),
            "sha256": MODULE.sha256_file(attribution_path),
            "attribution_id": attribution["attribution_id"],
        }
        self.attribution_refs[publication_id] = reference
        self.attribution_paths[publication_id] = attribution_path

    def add_publication(
        self,
        index,
        *,
        option_index=0,
        published_at=PUBLISHED,
        package_mutator=None,
        check_mutator=None,
    ):
        video_id = f"VIDEO-{index:02d}"
        publication_id = f"PUB-{index:02d}"
        package_dir = self.root / "evidence" / video_id / "publish-package"
        delivery = package_dir / "instagram" / f"{video_id}-reels-organic.mp4"
        delivery.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.base_media, delivery)

        catalog_relative = self.platform_catalog_path.relative_to(self.root).as_posix()
        catalog_hash = MODULE.sha256_file(self.platform_catalog_path)
        package = read_json(FRAMEWORK / "templates/publish-package.json")
        package.update(
            {
                "package_id": f"PUBLISH-{video_id}-TEST",
                "project_id": "SERIE-TEST",
                "video_id": video_id,
                "generated_at": timestamp(published_at - timedelta(hours=3)),
                "status": "ready_for_derivative_build",
                "blocking_reasons": [],
            }
        )
        package["adaptation"].update(
            {
                "status": "ready_for_platform_preview",
                "catalog_path": catalog_relative,
                "catalog_sha256": catalog_hash,
            }
        )
        target = package["targets"][0]
        target.update(
            {
                "status": "awaiting_derivative_render",
                "delivery_output": f"instagram/{video_id}-reels-organic.mp4",
            }
        )
        target["provenance"].update(
            {
                "catalog_path": catalog_relative,
                "catalog_sha256": catalog_hash,
                "profile_version": self.profile["profile_version"],
                "evidence_reviewed_at": self.profile["evidence_reviewed_at"],
            }
        )
        if package_mutator:
            package_mutator(package)
        package_path = package_dir / "publish-package.json"
        write_json(package_path, package)

        check = {
            "schema_version": "1.0.0",
            "profile_id": self.profile["id"],
            "platform": "instagram",
            "surface": "reels_organic",
            "media_path": str(delivery),
            "media_sha256": MODULE.sha256_file(delivery),
            "inspected_at": timestamp(published_at - timedelta(minutes=30)),
            "safe_zone_provenance": self.profile["internal_defaults"]["safe_zones"][
                "provenance"
            ],
            "technical_status": "passed",
            "manual_review_status": "passed",
            "delivery_status": "ready",
            "metadata": copy.deepcopy(self.media_metadata),
            "findings": [],
        }
        if check_mutator:
            check_mutator(check)
        check_path = delivery.parent / "delivery-check.json"
        write_json(check_path, check)

        publication_evidence_path = (
            self.root / "evidence" / video_id / "publication-evidence.json"
        )
        write_json(
            publication_evidence_path,
            {
                "schema_version": "1.0.0",
                "publication_id": publication_id,
                "platform": "instagram",
                "captured_at": timestamp(published_at + timedelta(minutes=4)),
                "notice": "Local fixture only; it does not prove remote authenticity.",
            },
        )
        record = {
            "record_id": "PUBREC-0000000000000000",
            "publication_id": publication_id,
            "project_id": "SERIE-TEST",
            "video_id": video_id,
            "platform": "instagram",
            "surface": "reels_organic",
            "published_at": timestamp(published_at),
            "registered_at": timestamp(published_at + timedelta(minutes=5)),
            "package": {
                "path": package_path.relative_to(self.root).as_posix(),
                "sha256": MODULE.sha256_file(package_path),
                "package_id": package["package_id"],
            },
            "delivery": {
                "path": delivery.relative_to(self.root).as_posix(),
                "sha256": MODULE.sha256_file(delivery),
                "size_bytes": delivery.stat().st_size,
            },
            "delivery_check": {
                "path": check_path.relative_to(self.root).as_posix(),
                "sha256": MODULE.sha256_file(check_path),
                "profile_id": self.profile["id"],
                "required_delivery_status": "ready",
            },
            "publication_evidence": {
                "path": publication_evidence_path.relative_to(self.root).as_posix(),
                "sha256": MODULE.sha256_file(publication_evidence_path),
                "type": "local_record",
                "integrity_scope": "local_artifact_integrity_only",
            },
            "source_reference": f"platform:instagram/{publication_id}",
        }
        record["record_id"] = MODULE.publication_record_id(record)
        self.records.append(record)
        self._creative_attribution(video_id, publication_id, published_at, option_index)
        return record, package_path, delivery, check_path

    def mutate_attribution(self, publication_id, mutator):
        path = self.attribution_paths[publication_id]
        document = read_json(path)
        mutator(document)
        document["attribution_id"] = MODULE.creative_attribution_id(document)
        write_json(path, document)
        reference = {
            "path": path.relative_to(self.root).as_posix(),
            "sha256": MODULE.sha256_file(path),
            "attribution_id": document["attribution_id"],
        }
        self.attribution_refs[publication_id] = reference
        return reference

    def bind_metrics_evidence(self, raw):
        self.evidence_counter += 1
        metrics = {name: raw.get(name) for name in METRIC_NAMES}
        path = self.root / "metrics" / (
            f"{raw['publication_id']}-{raw['window_hours']}h-{self.evidence_counter:03d}.json"
        )
        write_json(
            path,
            {
                "schema_version": "1.0.0",
                "publication_id": raw["publication_id"],
                "captured_at": raw["captured_at"],
                "window_hours": raw["window_hours"],
                "metrics": metrics,
            },
        )
        raw["evidence"] = {
            "path": path.relative_to(self.root).as_posix(),
            "sha256": MODULE.sha256_file(path),
            "type": "local_record",
            "integrity_scope": "local_artifact_integrity_only",
        }
        return raw

    def observation(self, record, *, window=24, views=100, metric_overrides=None):
        published = MODULE.parse_time(record["published_at"], "fixture published_at")
        metrics = {
            "impressions": views + 20,
            "reach": views,
            "views": views,
            "total_watch_time_s": views * 12,
            "average_watch_time_s": 12,
            "completion_rate": 0.4,
            "likes": 10,
            "comments": 2,
            "shares": 4,
            "saves": 6,
            "clicks": 3,
            "conversions": 1,
        }
        metrics.update(metric_overrides or {})
        raw = {
            "project_id": record["project_id"],
            "video_id": record["video_id"],
            "publication_id": record["publication_id"],
            "platform": record["platform"],
            "surface": record["surface"],
            "published_at": record["published_at"],
            "captured_at": timestamp(published + timedelta(hours=window)),
            "window_hours": window,
            "duration_s": 30,
            "creative_attribution": copy.deepcopy(
                self.attribution_refs[record["publication_id"]]
            ),
            "traffic_source": "organic",
            "paid_spend": 0,
            "currency": "USD",
            "campaign_objective": "education",
            "audience_segment": "FOUNDERS",
            "followers_at_publish": 1000,
            "publish_slot": "weekday-evening",
            "account_id": "ACCOUNT-TEST",
            "language": "es",
            "topic_id": "TOPIC-TEST",
            "campaign_id": "CAMPAIGN-TEST",
            "publication_period": published.strftime("%Y-%m"),
            **metrics,
            "confounders": [],
            "source_reference": f"export:{record['publication_id']}-{window}h.json",
        }
        return self.bind_metrics_evidence(raw)

    def production_record(
        self, video_id="VIDEO-01", *, assembly=30, verified=True, time_offset=False
    ):
        self.production_counter += 1
        item = read_json(FRAMEWORK / "templates/production-metrics.json")
        item.update(
            {
                "production_record_id": "PROD-0000000000000000",
                "project_id": "SERIE-TEST",
                "video_id": video_id,
                "captured_at": "2026-09-03T12:00:00Z",
                "started_at": "2026-09-01T08:00:00Z",
                "first_reviewable_at": "2026-09-01T10:00:00Z",
                "final_delivered_at": "2026-09-01T11:00:00Z",
            }
        )
        if time_offset:
            item.update(
                {
                    "captured_at": "2026-09-03T07:00:00-05:00",
                    "started_at": "2026-09-01T03:00:00-05:00",
                    "first_reviewable_at": "2026-09-01T05:00:00-05:00",
                    "final_delivered_at": "2026-09-01T06:00:00-05:00",
                }
            )
        item["stage_minutes"].update({"assembly": assembly, "quality_control": 5})
        item["assets"].update(
            {
                "reused": 2,
                "derived": 1,
                "generated": 1,
                "generated_but_unused": 0,
                "reuse_rate": 0.5,
            }
        )
        item["reviews"].update(
            {
                "rounds": 1,
                "atomic_decisions": 4,
                "approved_first_pass": 3,
                "first_pass_approval_rate": 0.75,
            }
        )
        item["rework"]["change_count"] = 1
        if verified:
            evidence_path = self.root / "production" / (
                f"{video_id}-{self.production_counter:03d}.json"
            )
            write_json(
                evidence_path,
                {
                    "schema_version": "1.0.0",
                    "video_id": video_id,
                    "measurement_method": "manual_timer",
                    "captured_at": item["captured_at"],
                },
            )
            item.update(
                {
                    "measurement_method": "manual_timer",
                    "verification_status": "verified",
                    "evidence": {
                        "path": evidence_path.relative_to(self.root).as_posix(),
                        "sha256": MODULE.sha256_file(evidence_path),
                        "type": "timer_export",
                        "integrity_scope": "local_artifact_integrity_only",
                    },
                }
            )
        else:
            item.update(
                {
                    "measurement_method": "self_reported",
                    "verification_status": "self_reported",
                    "evidence": None,
                }
            )
        item["production_record_id"] = MODULE.production_record_id(item)
        return item

    def write_registry(self, name="publication-registry.json"):
        registry = {
            "schema_version": "1.0.0",
            "registry_id": "PUBLICATION-REGISTRY-TEST",
            "updated_at": "2026-09-25T00:00:00Z",
            "records": self.records,
        }
        path = self.root / name
        write_json(path, registry)
        return path

    def load_registry(self):
        return MODULE.load_publication_registry(self.write_registry(), self.root)


class PerformanceCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_temp = tempfile.TemporaryDirectory()
        cls.base_media = Path(cls.media_temp.name) / "verified-h264-aac.mp4"
        command = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=64x96:r=10:d=1.2",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo",
            "-t",
            "1.2",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-x264-params",
            "colorprim=bt709:transfer=bt709:colormatrix=bt709",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(cls.base_media),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError as error:
            raise unittest.SkipTest("ffmpeg is required for real-media lineage tests") from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"ffmpeg fixture failed: {error.stderr}") from error
        cls.media_metadata = MODULE.check_platform_delivery.parse_ffprobe(
            MODULE.check_platform_delivery.run_ffprobe(cls.base_media)
        )

    @classmethod
    def tearDownClass(cls):
        cls.media_temp.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.evidence = EvidenceFixture(
            self.root, self.base_media, self.media_metadata
        )

    def tearDown(self):
        self.temporary.cleanup()

    def fixture_at(self, name):
        return EvidenceFixture(
            self.root / name, self.base_media, self.media_metadata
        )

    def add_publications(self, count, *, options=None):
        options = options or [0] * count
        records = [
            self.evidence.add_publication(index, option_index=options[index - 1])[0]
            for index in range(1, count + 1)
        ]
        return records, self.evidence.load_registry()

    def store_with(self, records, registry, *, transform=None):
        raw = [self.evidence.observation(record) for record in records]
        if transform:
            for index, item in enumerate(raw):
                transform(index, item)
                self.evidence.bind_metrics_evidence(item)
        store, _ = MODULE.merge_observations(
            MODULE.empty_store(updated_at="2026-09-25T00:00:00Z"),
            raw,
            publication_registry=registry,
            updated_at="2026-09-25T00:00:00Z",
        )
        return store

    def test_real_lineage_is_verified_and_safe_ratios_are_computed(self):
        records, registry = self.add_publications(1)
        value = MODULE.normalize_observation(
            self.evidence.observation(records[0]), registry
        )
        self.assertEqual(value["lineage"]["verification_status"], "verified_ready_delivery")
        self.assertEqual(value["lineage"]["publication_registry_sha256"], registry["registry_sha256"])
        self.assertEqual(value["derived"]["average_watch_ratio"], 0.4)
        self.assertEqual(value["derived"]["shares_per_reach"], 0.04)
        self.assertEqual(value["content"]["primary_family_id"], "FAMILY-CLEAN-AUTHORITY")
        self.assertFalse(value["governance"]["causal_claim_allowed"])

    def test_registry_rejects_fake_mp4_even_when_hashes_are_self_consistent(self):
        record, _, delivery, check_path = self.evidence.add_publication(1)
        delivery.write_bytes(b"not-an-mp4")
        check = read_json(check_path)
        check["media_sha256"] = MODULE.sha256_file(delivery)
        write_json(check_path, check)
        record["delivery"].update(
            {"sha256": MODULE.sha256_file(delivery), "size_bytes": delivery.stat().st_size}
        )
        record["delivery_check"]["sha256"] = MODULE.sha256_file(check_path)
        record["record_id"] = MODULE.publication_record_id(record)
        with self.assertRaisesRegex(MODULE.PerformanceError, "ffprobe verification failed"):
            self.evidence.load_registry()

    def test_registry_rejects_stale_probe_metadata_and_missing_publication_evidence(self):
        stale = self.fixture_at("stale")
        record, _, _, check_path = stale.add_publication(1)
        check = read_json(check_path)
        check["metadata"]["width"] += 1
        write_json(check_path, check)
        record["delivery_check"]["sha256"] = MODULE.sha256_file(check_path)
        record["record_id"] = MODULE.publication_record_id(record)
        with self.assertRaisesRegex(MODULE.PerformanceError, "fresh ffprobe facts"):
            stale.load_registry()

        missing = self.fixture_at("missing-publication-evidence")
        record = missing.add_publication(1)[0]
        record.pop("publication_evidence")
        with self.assertRaisesRegex(MODULE.PerformanceError, "invalid publication registry"):
            missing.load_registry()

    def test_missing_metrics_evidence_is_rejected(self):
        records, registry = self.add_publications(1)
        raw = self.evidence.observation(records[0])
        raw.pop("evidence")
        with self.assertRaisesRegex(MODULE.PerformanceError, "metrics evidence must be an object"):
            MODULE.normalize_observation(raw, registry)

    def test_registry_rejects_package_mismatch_and_symlink(self):
        self.evidence.add_publication(
            1,
            package_mutator=lambda value: value["targets"][0].update(
                surface="other_surface"
            ),
        )
        with self.assertRaisesRegex(MODULE.PerformanceError, "matching target"):
            self.evidence.load_registry()

        clean = self.fixture_at("clean")
        clean.add_publication(2)
        real = clean.write_registry("registry-real.json")
        alias = clean.root / "registry-alias.json"
        os.symlink(real, alias)
        with self.assertRaisesRegex(MODULE.PerformanceError, "symlink"):
            MODULE.load_publication_registry(alias, clean.root)

    def test_publication_id_binds_source_registration_and_evidence(self):
        record = self.evidence.add_publication(1)[0]
        baseline = MODULE.publication_record_id(record)
        variants = []
        source = copy.deepcopy(record)
        source["source_reference"] += ":changed"
        variants.append(source)
        registered = copy.deepcopy(record)
        registered["registered_at"] = "2026-09-01T12:06:00Z"
        variants.append(registered)
        evidence = copy.deepcopy(record)
        evidence["publication_evidence"]["sha256"] = "a" * 64
        variants.append(evidence)
        for variant in variants:
            self.assertNotEqual(MODULE.publication_record_id(variant), baseline)

    def test_bilateral_windows_enforce_both_bounds_and_allow_edges(self):
        records, registry = self.add_publications(1)
        base = self.evidence.observation(records[0])
        for elapsed in (21.999, 26.001):
            invalid = copy.deepcopy(base)
            invalid["captured_at"] = timestamp(PUBLISHED + timedelta(hours=elapsed))
            self.evidence.bind_metrics_evidence(invalid)
            with self.assertRaisesRegex(MODULE.PerformanceError, "outside the bilateral"):
                MODULE.normalize_observation(invalid, registry)
        for elapsed in (22, 26):
            valid = copy.deepcopy(base)
            valid["captured_at"] = timestamp(PUBLISHED + timedelta(hours=elapsed))
            self.evidence.bind_metrics_evidence(valid)
            self.assertEqual(MODULE.normalize_observation(valid, registry)["window_hours"], 24)

    def test_unknown_free_creative_and_unreproducible_ids_are_rejected(self):
        records, registry = self.add_publications(1)
        raw = self.evidence.observation(records[0])
        raw["mystery"] = True
        with self.assertRaisesRegex(MODULE.PerformanceError, "unknown observation fields"):
            MODULE.normalize_observation(raw, registry)

        raw = self.evidence.observation(records[0])
        raw["content"] = {"duration_s": 30, "primary_family_id": "FAMILY-INVENTED"}
        with self.assertRaisesRegex(MODULE.PerformanceError, "free text"):
            MODULE.normalize_observation(raw, registry)

        raw = self.evidence.observation(records[0])
        raw["observation_id"] = "OBS-0000000000000000"
        with self.assertRaisesRegex(MODULE.PerformanceError, "not reproducible"):
            MODULE.normalize_observation(raw, registry)

    def test_creative_attribution_drift_from_real_plan_is_rejected(self):
        records, registry = self.add_publications(1)

        def drift(document):
            document["selection"]["primary_family_id"] = (
                document["selection"]["contributing_family_ids"][-1]
            )

        self.evidence.mutate_attribution(records[0]["publication_id"], drift)
        raw = self.evidence.observation(records[0])
        with self.assertRaisesRegex(MODULE.PerformanceError, "selection drifts"):
            MODULE.normalize_observation(raw, registry)

    def test_observation_ids_are_deterministic_and_merge_is_idempotent(self):
        records, registry = self.add_publications(1)
        raw = self.evidence.observation(records[0])
        first = MODULE.normalize_observation(raw, registry)
        second = MODULE.normalize_observation(copy.deepcopy(raw), registry)
        self.assertEqual(first["observation_id"], second["observation_id"])
        initial = MODULE.empty_store(updated_at="2026-09-25T00:00:00Z")
        merged, added = MODULE.merge_observations(
            initial, [raw], publication_registry=registry
        )
        repeated, added_again = MODULE.merge_observations(
            merged, [raw], publication_registry=registry
        )
        self.assertEqual((added, added_again), (1, 0))
        self.assertEqual(repeated, merged)
        conflict = self.evidence.observation(records[0], views=999)
        with self.assertRaisesRegex(MODULE.PerformanceError, "one observation per window"):
            MODULE.merge_observations(merged, [conflict], publication_registry=registry)

    def test_cumulative_metrics_cannot_decrease_across_null_intermediate_windows(self):
        records, registry = self.add_publications(1)
        first = self.evidence.observation(records[0], window=24, views=100)
        middle = self.evidence.observation(
            records[0],
            window=72,
            views=120,
            metric_overrides={
                "impressions": None,
                "reach": None,
                "views": None,
                "total_watch_time_s": None,
            },
        )
        later = self.evidence.observation(records[0], window=168, views=90)
        with self.assertRaisesRegex(MODULE.PerformanceError, "decreases"):
            MODULE.merge_observations(
                MODULE.empty_store(),
                [first, middle, later],
                publication_registry=registry,
            )

    def test_effective_n_is_true_intersection_of_core_metrics(self):
        records, registry = self.add_publications(3)
        raws = [
            self.evidence.observation(
                records[0], metric_overrides={"views": None}
            ),
            self.evidence.observation(
                records[1],
                metric_overrides={
                    "completion_rate": None,
                    "average_watch_time_s": None,
                },
            ),
            self.evidence.observation(records[2]),
        ]
        store, _ = MODULE.merge_observations(
            MODULE.empty_store(), raws, publication_registry=registry
        )
        cohort = MODULE.build_cohort_report(
            store, publication_registry=registry
        )["cohorts"][0]
        effective = cohort["creative_performance"]["effective_publications"]
        self.assertEqual(effective["views"], 2)
        self.assertEqual(effective["completion_rate"], 2)
        self.assertEqual(effective["average_watch_ratio"], 2)
        self.assertEqual(effective["joint_core"], 1)
        self.assertEqual(cohort["effective_sample_size"], 1)
        self.assertEqual(cohort["evidence_strength"], "insufficient")

    def test_creative_dimensions_come_from_selected_real_proposals(self):
        records, registry = self.add_publications(3, options=[0, 1, 2])
        report = MODULE.build_cohort_report(
            self.store_with(records, registry), publication_registry=registry
        )
        self.assertEqual(len(report["cohorts"]), 1)
        variation = {
            item["dimension"]: item
            for item in report["cohorts"][0]["creative_variation"]
        }
        self.assertEqual(variation["primary_family_id"]["variant_count"], 1)
        self.assertEqual(variation["recipe_id"]["variant_count"], 3)
        self.assertEqual(variation["structure_id"]["variant_count"], 3)
        self.assertEqual(variation["sound_id"]["variant_count"], 3)

    def test_comparability_splits_account_language_topic_campaign_and_currency(self):
        records, registry = self.add_publications(2)
        cases = {
            "account_id": "ACCOUNT-OTHER",
            "language": "en",
            "topic_id": "TOPIC-OTHER",
            "campaign_id": "CAMPAIGN-OTHER",
            "currency": "EUR",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                store = self.store_with(
                    records,
                    registry,
                    transform=lambda index, item, field=field, value=value: (
                        item.update({field: value}) if index == 1 else None
                    ),
                )
                report = MODULE.build_cohort_report(
                    store, publication_registry=registry
                )
                self.assertEqual(len(report["cohorts"]), 2)

    def test_material_confounders_cap_directional_strength(self):
        records, registry = self.add_publications(5)
        store = self.store_with(
            records,
            registry,
            transform=lambda _index, item: item.update(
                {"confounders": ["selection_not_randomized"]}
            ),
        )
        cohort = MODULE.build_cohort_report(
            store, publication_registry=registry
        )["cohorts"][0]
        self.assertEqual(cohort["effective_sample_size"], 5)
        self.assertEqual(cohort["evidence_strength"], "exploratory")
        self.assertIn(
            "evidence_strength_capped_by_material_confounders",
            cohort["interpretation"]["confounders"],
        )

    def test_production_contract_requires_evidence_dedupes_and_rejects_conflicts(self):
        value = self.evidence.production_record()
        lookup, normalized = MODULE._production_lookup(
            [value, copy.deepcopy(value)], project_root=self.root
        )
        self.assertEqual(len(lookup), 1)
        self.assertEqual(len(normalized), 1)
        changed = self.evidence.production_record(assembly=40)
        with self.assertRaisesRegex(MODULE.PerformanceError, "conflicting production metrics"):
            MODULE._production_lookup(
                [value, changed], project_root=self.root
            )
        invalid = copy.deepcopy(value)
        invalid["reviews"]["first_pass_approval_rate"] = 0.5
        invalid["production_record_id"] = MODULE.production_record_id(invalid)
        with self.assertRaisesRegex(MODULE.PerformanceError, "first_pass_approval_rate"):
            MODULE.normalize_production_record(invalid, project_root=self.root)

        missing = copy.deepcopy(value)
        missing["evidence"] = None
        missing["production_record_id"] = MODULE.production_record_id(missing)
        with self.assertRaisesRegex(MODULE.PerformanceError, "evidence must be an object"):
            MODULE.normalize_production_record(missing, project_root=self.root)

    def test_self_reported_and_foreign_production_do_not_enter_comparison(self):
        records, registry = self.add_publications(1)
        store = self.store_with(records, registry)
        self_reported = self.evidence.production_record(verified=False)
        foreign = self.evidence.production_record(video_id="VIDEO-99")
        report = MODULE.build_cohort_report(
            store,
            publication_registry=registry,
            production_records=[self_reported, foreign],
        )
        efficiency = report["cohorts"][0]["production_efficiency"]
        self.assertEqual(efficiency["status"], "not_measured")
        self.assertEqual(efficiency["sample_size"], 0)
        self.assertNotIn(self_reported["production_record_id"], report["production_record_ids"])
        self.assertNotIn(foreign["production_record_id"], report["production_record_ids"])

    def test_report_and_cohort_ids_include_members_parameters_and_verified_production(self):
        records, registry = self.add_publications(1)
        store = self.store_with(records, registry)
        production = self.evidence.production_record()
        first = MODULE.build_cohort_report(
            store,
            publication_registry=registry,
            production_records=[production],
            generated_at="2026-09-25T00:00:00Z",
        )
        later_clock = MODULE.build_cohort_report(
            store,
            publication_registry=registry,
            production_records=[production],
            generated_at="2027-01-01T00:00:00Z",
        )
        self.assertEqual(first["report_id"], later_clock["report_id"])
        self.assertEqual(
            first["cohorts"][0]["cohort_id"], later_clock["cohorts"][0]["cohort_id"]
        )
        changed = MODULE.build_cohort_report(
            store,
            publication_registry=registry,
            production_records=[self.evidence.production_record(assembly=31)],
        )
        self.assertNotEqual(first["report_id"], changed["report_id"])
        self.assertNotEqual(
            first["cohorts"][0]["cohort_id"], changed["cohorts"][0]["cohort_id"]
        )

    def test_equivalent_timestamp_instants_have_identical_ids(self):
        record = self.evidence.add_publication(1)[0]
        equivalent = copy.deepcopy(record)
        equivalent["published_at"] = "2026-09-01T07:00:00-05:00"
        equivalent["registered_at"] = "2026-09-01T07:05:00-05:00"
        self.assertEqual(
            MODULE.publication_record_id(record), MODULE.publication_record_id(equivalent)
        )

        production = self.evidence.production_record()
        production_equivalent = copy.deepcopy(production)
        production_equivalent.update(
            {
                "captured_at": "2026-09-03T07:00:00-05:00",
                "started_at": "2026-09-01T03:00:00-05:00",
                "first_reviewable_at": "2026-09-01T05:00:00-05:00",
                "final_delivered_at": "2026-09-01T06:00:00-05:00",
            }
        )
        self.assertEqual(
            MODULE.production_record_id(production),
            MODULE.production_record_id(production_equivalent),
        )

        attribution = read_json(
            self.evidence.attribution_paths[record["publication_id"]]
        )
        attribution_equivalent = copy.deepcopy(attribution)
        selected = MODULE.parse_time(attribution["selected_at"], "selected_at")
        attribution_equivalent["selected_at"] = selected.astimezone(
            timezone(timedelta(hours=-5))
        ).isoformat()
        self.assertEqual(
            MODULE.creative_attribution_id(attribution),
            MODULE.creative_attribution_id(attribution_equivalent),
        )

    def test_report_semantic_verifier_detects_tampering(self):
        records, registry = self.add_publications(3)
        store = self.store_with(records, registry)
        report = MODULE.build_cohort_report(store, publication_registry=registry)
        self.assertEqual(
            MODULE.verify_cohort_report(
                report, store=store, publication_registry=registry
            ),
            report,
        )
        tampered = copy.deepcopy(report)
        tampered["cohorts"][0]["creative_performance"]["median_views"] = 999
        with self.assertRaisesRegex(MODULE.PerformanceError, "semantic verification failed"):
            MODULE.verify_cohort_report(
                tampered, store=store, publication_registry=registry
            )

    def test_report_output_is_no_clobber_by_report_id(self):
        records, registry = self.add_publications(1)
        report = MODULE.build_cohort_report(
            self.store_with(records, registry), publication_registry=registry
        )
        path = self.root / "reports/cohort-report.json"
        self.assertTrue(
            MODULE.atomic_write_json(
                path,
                report,
                project_root=self.root,
                no_clobber_id_field="report_id",
            )
        )
        self.assertFalse(
            MODULE.atomic_write_json(
                path,
                copy.deepcopy(report),
                project_root=self.root,
                no_clobber_id_field="report_id",
            )
        )
        tampered = copy.deepcopy(report)
        tampered["separation_notice"] += " changed"
        with self.assertRaisesRegex(MODULE.PerformanceError, "refusing to overwrite"):
            MODULE.atomic_write_json(
                path,
                tampered,
                project_root=self.root,
                no_clobber_id_field="report_id",
            )

    def test_atomic_cas_rejects_stale_revision_and_store_symlink(self):
        path = self.root / "data/performance-store.json"
        store = MODULE.empty_store(updated_at="2026-09-25T00:00:00Z")
        MODULE.atomic_write_json(
            path,
            store,
            project_root=self.root,
            expected_revision=MODULE.MISSING_REVISION,
        )
        stale = MODULE.file_revision(path)
        changed = copy.deepcopy(store)
        changed["updated_at"] = "2026-09-25T01:00:00Z"
        MODULE.atomic_write_json(
            path, changed, project_root=self.root, expected_revision=stale
        )
        with self.assertRaisesRegex(MODULE.PerformanceError, "concurrent store update"):
            MODULE.atomic_write_json(
                path, store, project_root=self.root, expected_revision=stale
            )
        alias = self.root / "store-alias.json"
        os.symlink(path, alias)
        with self.assertRaisesRegex(MODULE.PerformanceError, "symlink"):
            MODULE.load_store_state(alias, self.root, require_existing=True)

    def test_report_rejects_missing_and_arbitrary_empty_store(self):
        with self.assertRaisesRegex(MODULE.PerformanceError, "does not exist"):
            MODULE.load_store_state(
                self.root / "missing-store.json", self.root, require_existing=True
            )
        registry = self.evidence.load_registry()
        with self.assertRaisesRegex(MODULE.PerformanceError, "empty performance store"):
            MODULE.build_cohort_report(
                MODULE.empty_store(), publication_registry=registry
            )

    def test_csv_input_expands_hash_bound_references_then_verifies(self):
        records, registry = self.add_publications(1)
        path = self.root / "observations.csv"
        row = self.evidence.observation(records[0])
        attribution = row.pop("creative_attribution")
        evidence = row.pop("evidence")
        row.update(
            {
                "creative_attribution_path": attribution["path"],
                "creative_attribution_sha256": attribution["sha256"],
                "creative_attribution_id": attribution["attribution_id"],
                "metrics_evidence_path": evidence["path"],
                "metrics_evidence_sha256": evidence["sha256"],
                "metrics_evidence_type": evidence["type"],
                "metrics_evidence_integrity_scope": evidence["integrity_scope"],
                "confounders": "slot|audience",
            }
        )
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        loaded = MODULE.load_records(path, self.root)
        normalized = MODULE.normalize_observation(loaded[0], registry)
        self.assertEqual(normalized["confounders"], ["audience", "slot"])

    def test_templates_and_generated_report_match_schemas(self):
        mapping = {
            "templates/publication-registry.json": "schemas/publication-registry.schema.json",
            "templates/creative-attribution.json": "schemas/creative-attribution.schema.json",
            "templates/production-metrics.json": "schemas/production-metrics.schema.json",
            "templates/performance-observation.json": "schemas/performance-observation.schema.json",
            "templates/performance-store.json": "schemas/performance-store.schema.json",
            "templates/performance-cohort-report.json": "schemas/performance-cohort-report.schema.json",
        }
        for template_path, schema_path in mapping.items():
            template = read_json(FRAMEWORK / template_path)
            schema = SCHEMAS.load_json(FRAMEWORK / schema_path)
            self.assertEqual(
                SCHEMAS.validate_document(template, schema), [], template_path
            )
        records, registry = self.add_publications(1)
        report = MODULE.build_cohort_report(
            self.store_with(records, registry), publication_registry=registry
        )
        schema = SCHEMAS.load_json(
            FRAMEWORK / "schemas/performance-cohort-report.schema.json"
        )
        self.assertEqual(SCHEMAS.validate_document(report, schema), [])


if __name__ == "__main__":
    unittest.main()
