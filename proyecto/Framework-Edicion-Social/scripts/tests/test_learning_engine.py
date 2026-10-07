#!/usr/bin/env python3

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("learning_engine", SCRIPTS / "learning_engine.py")
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def make_event(
    suffix,
    *,
    evidence_type="preference",
    scope_level="video",
    scope_id="VIDEO-01",
    project_id="PROJECT-01",
    video_id="VIDEO-01",
    series_id="SERIES-01",
    creator_id="CREATOR-01",
    account_id="ACCOUNT-01",
    family_id="FAMILY-TALKING-HEAD",
    variant_id="VARIANT-TIGHT-RHYTHM",
    variant_axis=None,
    variation_mode="controlled_variant",
    independent_context_id=None,
    pattern_value=None,
    signal="supports",
    supersedes=None,
    explicit_human=None,
    comparison_basis="cohort",
    decision_domain=None,
    hard_gate_status=None,
    confidence="high",
):
    source_kind = {
        "technical": "qa_measurement",
        "creative": "approval",
        "preference": "feedback",
        "performance": "performance",
    }[evidence_type]
    if explicit_human is None:
        explicit_human = evidence_type in {"creative", "preference"}
    if decision_domain is None:
        decision_domain = "technical_contract" if evidence_type == "technical" and hard_gate_status is None else "editorial_choice"
    if variant_axis is None:
        variant_axis = "technical" if decision_domain == "technical_contract" else "rhythm"
    performance_context = None
    if evidence_type == "performance":
        metric_value = 0.78 if signal == "supports" else 0.62 if signal == "opposes" else 0.70
        performance_context = {
            "comparison_basis": comparison_basis,
            "metric_name": "completion_rate",
            "metric_value": metric_value,
            "metric_direction": "higher_is_better",
            "benchmark_id": None if comparison_basis == "none" else "COHORT-01",
            "benchmark_value": None if comparison_basis == "none" else 0.70,
            "experiment_id": "EXP-01" if comparison_basis == "ab_test" else None,
            "observation_window_hours": 72,
            "causal_claim_allowed": False,
        }
    context_ids = {
        "asset": (scope_id, video_id, series_id, None, creator_id, account_id),
        "video": (None, scope_id, series_id, None, creator_id, account_id),
        "series": (None, video_id, scope_id, None, creator_id, account_id),
        "style": (None, video_id, series_id, scope_id, creator_id, account_id),
        "creator": (None, video_id, series_id, None, scope_id, account_id),
        "account": (None, video_id, series_id, None, creator_id, scope_id),
        "global": (None, video_id, series_id, None, creator_id, account_id),
    }
    asset_id, actual_video_id, actual_series_id, style_id, actual_creator_id, actual_account_id = context_ids[scope_level]
    source_hash = hashlib.sha256(f"evidence:{suffix}".encode()).hexdigest()
    subject_hash = hashlib.sha256(f"subject:{suffix}".encode()).hexdigest()
    if independent_context_id is None:
        if performance_context and performance_context["experiment_id"]:
            independent_context_id = f"CTX-EXP-{performance_context['experiment_id']}"
        elif actual_video_id:
            independent_context_id = f"CTX-{project_id}-{actual_video_id}"
        elif asset_id:
            independent_context_id = f"CTX-{project_id}-{asset_id}"
        else:
            independent_context_id = f"CTX-{project_id}-{subject_hash[:12]}"
    scope = {"level": scope_level, "id": "global" if scope_level == "global" else scope_id}
    source_scope_level = {
        "series": "video",
        "style": "video",
        "creator": "series",
        "account": "creator",
        "global": "account",
    }.get(scope_level)
    context_scope_ids = {
        "video": actual_video_id,
        "series": actual_series_id,
        "style": style_id,
        "creator": actual_creator_id,
        "account": actual_account_id,
    }
    scope_authorization = None
    if source_scope_level:
        authorization_hash = hashlib.sha256(f"authorization:{scope_level}:{scope_id}".encode()).hexdigest()
        scope_authorization = {
            "approval_id": f"SCOPE-AUTH-{scope_level.upper()}-{scope_id}",
            "approval_mode": "human_explicit",
            "decision": "allow_evaluation_exact_scope",
            "approved_by": "human-reviewer",
            "approved_at": "2026-09-25T11:00:00Z",
            "artifact_path": f"evidence/scope-{scope_level}-{scope_id}.json",
            "artifact_sha256": authorization_hash,
            "source_scope": {"level": source_scope_level, "id": context_scope_ids[source_scope_level]},
            "target_scope": scope,
        }
    if hard_gate_status is not None:
        signal = "neutral"
    return {
        "schema_version": "1.0.0",
        "event_id": f"LE-{suffix}",
        "occurred_at": "2026-09-25T12:00:00Z",
        "source": {
            "kind": source_kind,
            "artifact_path": f"evidence/{suffix}.json",
            "artifact_sha256": source_hash,
            "subject_sha256": subject_hash,
            "recorded_by": "human" if explicit_human else "system",
        },
        "evidence_type": evidence_type,
        "scope": scope,
        "context": {
            "project_id": project_id,
            "video_id": actual_video_id,
            "series_id": actual_series_id,
            "style_id": style_id,
            "creator_id": actual_creator_id,
            "account_id": actual_account_id,
            "asset_id": asset_id,
            "platform": "instagram_reels",
            "independent_context_id": independent_context_id,
        },
        "pattern": {
            "key": "delivery.codec.contract" if decision_domain == "technical_contract" else "editing.rhythm.pause_policy",
            "value": pattern_value if pattern_value is not None else {"mode": "tight_natural"},
            "decision_domain": decision_domain,
            "variant_axis": variant_axis,
            "template_family_id": family_id,
            "variant_id": variant_id,
            "variation_mode": variation_mode,
            "applicability": {
                "content_type": "ai_education",
                "platform": "vertical_social",
                "audience_goal": "retention",
                "source_format": "talking_head",
                "duration_band": "15_60s",
                "language": "es",
            },
        },
        "evidence": {
            "signal": signal,
            "weight": 0 if signal in {"neutral", "revokes"} else 1,
            "confidence": confidence,
            "explicit_human": explicit_human,
            "measured": evidence_type in {"technical", "performance"},
            "sample_size": 100 if evidence_type == "performance" else 1,
            "reason": "Controlled unit-test evidence.",
            "performance_context": performance_context,
            "hard_gate": None
            if hard_gate_status is None
            else {
                "gate_id": "GATE-DELIVERY-INTEGRITY",
                "status": hard_gate_status,
                "override_permitted": False,
            },
        },
        "scope_authorization": scope_authorization,
        "supersedes_event_id": supersedes,
        "supersession_reason": "Correct or revoke prior evidence." if supersedes else None,
    }


class LearningEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = ENGINE.load_policy()

    def test_policy_and_all_four_evidence_types_are_valid(self):
        events = [
            make_event("TYPE-TECH", evidence_type="technical"),
            make_event("TYPE-CREATIVE", evidence_type="creative"),
            make_event("TYPE-PREFERENCE", evidence_type="preference"),
            make_event("TYPE-PERFORMANCE", evidence_type="performance"),
        ]
        self.assertEqual(ENGINE.validate_event_set(events, self.policy), [])

    def test_semantics_reject_inferred_preference_and_unbenchmarked_comparison(self):
        inferred = make_event("BAD-INFERRED", evidence_type="preference", explicit_human=False)
        errors = ENGINE.validate_event(inferred, self.policy)
        self.assertTrue(any("must be explicit" in error for error in errors))

        performance = make_event("BAD-PERF", evidence_type="performance")
        performance["evidence"]["performance_context"]["benchmark_id"] = None
        errors = ENGINE.validate_event(performance, self.policy)
        self.assertTrue(any("needs benchmark_id" in error for error in errors))

    def test_controlled_creative_axes_require_family_and_variant(self):
        event = make_event("BAD-FAMILY", family_id=None, variant_id=None, variant_axis="transitions")
        errors = ENGINE.validate_event(event, self.policy)
        self.assertTrue(any("requires template_family_id and variant_id" in error for error in errors))

    def test_global_editorial_learning_is_rejected_and_account_stays_observed(self):
        global_editorial = make_event("GLOBAL-EDITORIAL", scope_level="global")
        errors = ENGINE.validate_event(global_editorial, self.policy)
        self.assertTrue(any("reserved for technical contracts" in error for error in errors))

        report = ENGINE.build_recommendation_report(
            [make_event("ACCOUNT-ONE", scope_level="account")],
            self.policy,
            generated_at="2026-09-25T13:00:00Z",
        )
        candidate = report["candidates"][0]
        self.assertEqual(candidate["evidence_level"], "observed")
        self.assertEqual(candidate["recommendation"], "test_more")
        self.assertIn("insufficient_independent_support_contexts", candidate["blockers"])
        self.assertFalse(report["governance"]["automatic_promotion"])
        self.assertFalse(report["governance"]["scope_escalation_allowed"])

    def test_performance_alone_never_becomes_promotion_candidate(self):
        events = []
        for index in range(10):
            events.append(
                make_event(
                    f"PERF-{index:02d}",
                    evidence_type="performance",
                    scope_level="account",
                    project_id=f"PROJECT-{index % 2}",
                    video_id=f"VIDEO-{index:02d}",
                    series_id=f"SERIES-{index % 2}",
                )
            )
        report = ENGINE.build_recommendation_report(events, self.policy, generated_at="2026-09-25T13:00:00Z")
        candidate = report["candidates"][0]
        self.assertIn("performance_only_cannot_promote", candidate["blockers"])
        self.assertNotEqual(candidate["recommendation"], "eligible_for_portfolio_review")

    def test_triangulated_diverse_evidence_can_only_enter_human_review(self):
        evidence_types = [
            "preference",
            "preference",
            "creative",
            "creative",
            "performance",
            "performance",
            "preference",
            "creative",
        ]
        events = [
            make_event(
                f"MIXED-{index:02d}",
                evidence_type=evidence_type,
                scope_level="account",
                project_id=f"PROJECT-{index % 2}",
                video_id=f"VIDEO-{index:02d}",
                series_id=f"SERIES-{index % 2}",
            )
            for index, evidence_type in enumerate(evidence_types)
        ]
        report = ENGINE.build_recommendation_report(events, self.policy, generated_at="2026-09-25T13:00:00Z")
        candidate = report["candidates"][0]
        self.assertEqual(candidate["evidence_level"], "promotion_candidate")
        self.assertEqual(candidate["recommendation"], "eligible_for_portfolio_review")
        self.assertEqual(candidate["human_review"]["status"], "pending")
        self.assertFalse(report["governance"]["registry_write_permitted"])

    def test_template_families_coexist_as_contextual_portfolio(self):
        first = make_event("FAMILY-A", family_id="FAMILY-A", variant_id="A-01")
        second = make_event("FAMILY-B", family_id="FAMILY-B", variant_id="B-01")
        report = ENGINE.build_recommendation_report(
            [first, second], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        self.assertEqual(len(report["portfolio"]), 2)
        self.assertEqual(
            {candidate["recommendation"] for candidate in report["candidates"]},
            {"eligible_for_portfolio_review"},
        )
        self.assertFalse(report["governance"]["single_template_winner"])
        self.assertNotIn("winner", report)

    def test_raw_event_volume_in_one_context_counts_once(self):
        shared_context = "CTX-SAME-VIDEO"
        first = make_event("DUP-CONTEXT-1", evidence_type="preference", independent_context_id=shared_context)
        second = make_event("DUP-CONTEXT-2", evidence_type="creative", independent_context_id=shared_context)
        report = ENGINE.build_recommendation_report(
            [first, second], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = report["candidates"][0]
        self.assertEqual(candidate["evidence"]["active_event_count"], 2)
        self.assertEqual(candidate["evidence"]["support_contexts"], 1)
        self.assertEqual(candidate["evidence"]["support_weight"], 1.0)

    def test_revocation_removes_previous_support_without_erasing_history(self):
        original = make_event("REVOKE-ORIGINAL")
        revoked = make_event(
            "REVOKE-NEW",
            signal="revokes",
            supersedes=original["event_id"],
        )
        report = ENGINE.build_recommendation_report(
            [original, revoked], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = report["candidates"][0]
        self.assertEqual(candidate["evidence"]["support_contexts"], 0)
        self.assertEqual(candidate["evidence"]["revocation_count"], 1)
        self.assertEqual(candidate["evidence"]["superseded_event_ids"], [original["event_id"]])
        self.assertEqual(candidate["lifecycle_status"], "actively_revoked")
        self.assertEqual(candidate["recommendation"], "retire")
        self.assertEqual(candidate["evidence_level"], "deprecated")
        self.assertIn("confirm_retirement", candidate["human_review"]["decision_options"])
        self.assertEqual(report["input"]["superseded_event_count"], 1)

    def test_exploratory_variant_cannot_be_recommended_for_promotion(self):
        event = make_event("EXPLORE", variation_mode="exploratory")
        report = ENGINE.build_recommendation_report(
            [event], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = report["candidates"][0]
        self.assertIn("exploratory_variant_requires_controlled_test", candidate["blockers"])
        self.assertEqual(candidate["recommendation"], "blocked")

    def test_lower_authority_measurement_cannot_revoke_human_evidence(self):
        original = make_event("AUTH-HUMAN", evidence_type="preference")
        revoked = make_event(
            "AUTH-PERFORMANCE",
            evidence_type="performance",
            signal="revokes",
            comparison_basis="none",
            supersedes=original["event_id"],
        )
        errors = ENGINE.validate_event_set([original, revoked], self.policy)
        self.assertTrue(any("only explicit human evidence may revoke human evidence" in error for error in errors))

    def test_performance_volume_cannot_outvote_active_human_opposition(self):
        events = []
        kinds = ["preference", "preference", "performance", "performance", "performance", "performance"]
        for index, evidence_type in enumerate(kinds):
            events.append(
                make_event(
                    f"PRECEDENCE-SUPPORT-{index}",
                    evidence_type=evidence_type,
                    scope_level="account",
                    project_id=f"PROJECT-{index % 2}",
                    video_id=f"VIDEO-SUPPORT-{index}",
                    series_id=f"SERIES-{index % 2}",
                )
            )
        events.append(
            make_event(
                "PRECEDENCE-OPPOSE",
                evidence_type="preference",
                scope_level="account",
                project_id="PROJECT-1",
                video_id="VIDEO-OPPOSE",
                series_id="SERIES-1",
                signal="opposes",
            )
        )
        report = ENGINE.build_recommendation_report(
            events, self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = report["candidates"][0]
        self.assertIn("active_explicit_human_opposition", candidate["blockers"])
        self.assertEqual(candidate["recommendation"], "blocked")

    def test_hard_gate_failure_blocks_score_and_measured_pass_clears_it(self):
        support = make_event("GATE-SUPPORT", evidence_type="preference")
        failure = make_event(
            "GATE-FAIL",
            evidence_type="technical",
            decision_domain="editorial_choice",
            variant_axis="rhythm",
            hard_gate_status="fail",
        )
        failed_report = ENGINE.build_recommendation_report(
            [support, failure], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        failed = failed_report["candidates"][0]
        self.assertEqual(failed["recommendation"], "blocked")
        self.assertIn("active_hard_gate_failure", failed["blockers"])
        self.assertEqual(failed["evidence"]["hard_gate_failures"], 1)

        passed = make_event(
            "GATE-PASS",
            evidence_type="technical",
            decision_domain="editorial_choice",
            variant_axis="rhythm",
            hard_gate_status="pass",
            supersedes=failure["event_id"],
        )
        passed_report = ENGINE.build_recommendation_report(
            [support, failure, passed], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = passed_report["candidates"][0]
        self.assertEqual(candidate["evidence"]["hard_gate_failures"], 0)
        self.assertEqual(candidate["evidence"]["hard_gate_passes"], 1)
        self.assertEqual(candidate["recommendation"], "eligible_for_portfolio_review")

    def test_non_gate_technical_evidence_cannot_vote_for_editorial_pattern(self):
        event = make_event(
            "TECH-AS-TASTE",
            evidence_type="technical",
            decision_domain="editorial_choice",
            variant_axis="rhythm",
        )
        errors = ENGINE.validate_event(event, self.policy)
        self.assertTrue(any("non-gate technical evidence" in error for error in errors))

    def test_higher_scopes_require_matching_governance_authorization(self):
        series = make_event("NO-SCOPE-AUTH", scope_level="series")
        series["scope_authorization"] = None
        errors = ENGINE.validate_event(series, self.policy)
        self.assertTrue(any("requires explicit governance authorization" in error for error in errors))

        global_technical = make_event(
            "GLOBAL-TECHNICAL",
            evidence_type="technical",
            scope_level="global",
            variant_axis="technical",
            decision_domain="technical_contract",
        )
        self.assertEqual(ENGINE.validate_event(global_technical, self.policy), [])

    def test_repeated_global_technical_contract_only_enters_human_review(self):
        events = [
            make_event(
                f"GLOBAL-TECH-{index}",
                evidence_type="technical",
                scope_level="global",
                project_id=f"PROJECT-{index % 2}",
                video_id=f"VIDEO-{index}",
                series_id=f"SERIES-{index % 2}",
                variant_axis="technical",
                decision_domain="technical_contract",
            )
            for index in range(8)
        ]
        report = ENGINE.build_recommendation_report(
            events, self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        candidate = report["candidates"][0]
        self.assertEqual(candidate["recommendation"], "eligible_for_portfolio_review")
        self.assertTrue(candidate["human_review"]["required"])
        self.assertFalse(report["governance"]["automatic_promotion"])

    def test_directional_performance_requires_real_comparison_and_confidence(self):
        no_comparison = make_event(
            "PERF-NO-COMPARISON", evidence_type="performance", comparison_basis="none"
        )
        errors = ENGINE.validate_event(no_comparison, self.policy)
        self.assertTrue(any("requires a comparison" in error for error in errors))

        insufficient = make_event("PERF-INSUFFICIENT", evidence_type="performance", confidence="insufficient")
        errors = ENGINE.validate_event(insufficient, self.policy)
        self.assertTrue(any("insufficient-confidence" in error for error in errors))

    def test_binding_provenance_is_required(self):
        event = make_event("NO-PROVENANCE")
        event["source"]["artifact_path"] = ""
        event["source"]["artifact_sha256"] = None
        event["source"]["subject_sha256"] = None
        errors = ENGINE.validate_event(event, self.policy)
        self.assertTrue(any("artifact_path" in error for error in errors))
        self.assertTrue(any("artifact_sha256" in error for error in errors))
        self.assertTrue(any("subject_sha256" in error for error in errors))

    def test_independent_context_ids_are_bijective_with_natural_context(self):
        alias_a = make_event("CTX-ALIAS-A", independent_context_id="CTX-ALIAS-A")
        alias_b = make_event("CTX-ALIAS-B", independent_context_id="CTX-ALIAS-B")
        errors = ENGINE.validate_event_set([alias_a, alias_b], self.policy)
        self.assertTrue(any("aliased" in error for error in errors))

        reused_a = make_event("CTX-REUSED-A", scope_id="VIDEO-A", independent_context_id="CTX-REUSED")
        reused_b = make_event("CTX-REUSED-B", scope_id="VIDEO-B", independent_context_id="CTX-REUSED")
        errors = ENGINE.validate_event_set([reused_a, reused_b], self.policy)
        self.assertTrue(any("maps to more than one" in error for error in errors))

    def test_tied_conflicting_values_are_both_blocked_even_when_margin_floor_is_zero(self):
        first = make_event("TIE-A", pattern_value={"mode": "a"}, variant_id="SAME-VARIANT")
        second = make_event("TIE-B", pattern_value={"mode": "b"}, variant_id="SAME-VARIANT")
        report = ENGINE.build_recommendation_report(
            [first, second], self.policy, generated_at="2026-09-25T13:00:00Z"
        )
        self.assertEqual({candidate["recommendation"] for candidate in report["candidates"]}, {"blocked"})
        self.assertTrue(
            all(
                "ambiguous_alternative_within_same_variant_context" in candidate["blockers"]
                for candidate in report["candidates"]
            )
        )

    def test_policy_cannot_weaken_floors_or_higher_scope_monotonicity(self):
        weakened = copy.deepcopy(self.policy)
        weakened["scope_thresholds"]["global"]["min_support_contexts"] = 1
        errors = ENGINE.validate_policy(weakened)
        self.assertTrue(any("conservative floor" in error for error in errors))

        non_monotonic = copy.deepcopy(self.policy)
        non_monotonic["scope_thresholds"]["creator"]["min_unique_projects"] = 1
        errors = ENGINE.validate_policy(non_monotonic)
        self.assertTrue(any("cannot be lower than style" in error for error in errors))

    def test_concurrent_cli_ingests_preserve_every_event(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store_path = root / "events.jsonl"
            commands = []
            for index in range(6):
                input_path = root / f"input-{index}.json"
                input_path.write_text(json.dumps(make_event(f"CONCURRENT-{index}")), encoding="utf-8")
                commands.append(
                    [
                        sys.executable,
                        str(SCRIPTS / "learning_engine.py"),
                        "ingest",
                        "--store",
                        str(store_path),
                        "--event",
                        str(input_path),
                    ]
                )
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for command in commands]
            results = [process.communicate(timeout=15) + (process.returncode,) for process in processes]
            self.assertTrue(all(returncode == 0 for _, _, returncode in results), results)
            records = ENGINE.read_store_records(store_path)
            self.assertEqual(len(records), len(commands))
            self.assertEqual(len({record["event_id"] for record in records}), len(commands))

    def test_cli_ingest_is_atomic_and_duplicate_safe_then_writes_report(self):
        event = make_event("CLI-001")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "input.json"
            store_path = root / "events.jsonl"
            report_path = root / "report.json"
            input_path.write_text(json.dumps(event), encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = ENGINE.main(["ingest", "--store", str(store_path), "--event", str(input_path)])
            self.assertEqual(result, 0)
            self.assertEqual(len(ENGINE.read_records(store_path)), 1)

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                duplicate_result = ENGINE.main(
                    ["ingest", "--store", str(store_path), "--event", str(input_path)]
                )
            self.assertEqual(duplicate_result, 2)
            self.assertIn("already exists", stderr.getvalue())
            self.assertEqual(len(ENGINE.read_records(store_path)), 1)

            with contextlib.redirect_stdout(io.StringIO()):
                report_result = ENGINE.main(
                    [
                        "recommend",
                        "--store",
                        str(store_path),
                        "--output",
                        str(report_path),
                        "--generated-at",
                        "2026-09-25T13:00:00Z",
                    ]
                )
            self.assertEqual(report_result, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["governance"]["human_review_required"])

    def test_ingest_rejects_non_jsonl_store_without_changing_it(self):
        event = make_event("CLI-BAD-STORE")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "input.json"
            store_path = root / "events.jsonl"
            input_path.write_text(json.dumps(event), encoding="utf-8")
            original = "[]\n"
            store_path.write_text(original, encoding="utf-8")
            with self.assertRaises(ENGINE.LearningContractError):
                ENGINE.ingest_events(store_path, input_path)
            self.assertEqual(store_path.read_text(encoding="utf-8"), original)

    def test_supersession_cannot_cross_scope_or_template_family(self):
        original = make_event("LINEAGE-OLD")
        changed = make_event(
            "LINEAGE-NEW",
            family_id="OTHER-FAMILY",
            supersedes=original["event_id"],
        )
        errors = ENGINE.validate_event_set([original, changed], self.policy)
        self.assertTrue(any("cannot cross" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
