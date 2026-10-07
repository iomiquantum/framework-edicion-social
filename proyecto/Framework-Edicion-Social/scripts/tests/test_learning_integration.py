#!/usr/bin/env python3

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("validate_framework", SCRIPTS / "validate_framework.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LearningIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.approval = MODULE.load("templates/approval-receipt.json")
        cls.policy = MODULE.load("learning/promotion-policy.v1.json")
        cls.contract = MODULE.load("templates/series-contract.json")
        cls.masters = [
            MODULE.load("master-profiles/editorial-mezzanine-hdr-001.json"),
            MODULE.load("master-profiles/social-delivery-sdr-001.json"),
        ]

    def validate(self, approval=None, policy=None, contract=None, masters=None):
        return MODULE.validate_learning_contracts(
            approval or copy.deepcopy(self.approval),
            policy or copy.deepcopy(self.policy),
            contract or copy.deepcopy(self.contract),
            masters or copy.deepcopy(self.masters),
        )

    def test_current_learning_contracts_preserve_human_review_and_portfolio(self):
        counts = self.validate()
        self.assertEqual(counts["master_profiles"], 2)
        self.assertGreaterEqual(counts["template_families"], 2)

    def test_approval_template_cannot_start_approved(self):
        approval = copy.deepcopy(self.approval)
        approval["decision"]["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "begin pending"):
            self.validate(approval=approval)

    def test_single_template_winner_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["governance"]["single_template_winner"] = True
        with self.assertRaisesRegex(ValueError, "contextual patterns"):
            self.validate(policy=policy)

    def test_similarity_cannot_become_quality_gate(self):
        contract = copy.deepcopy(self.contract)
        contract["quality_policy"]["similarity_can_fail_quality"] = True
        with self.assertRaisesRegex(ValueError, "Similarity"):
            self.validate(contract=contract)

    def test_delivery_profile_requires_approved_editorial_lineage(self):
        masters = copy.deepcopy(self.masters)
        delivery = next(item for item in masters if item["artifact_role"] == "social_delivery_master")
        delivery["governance"]["requires_approved_source_receipt"] = False
        with self.assertRaisesRegex(ValueError, "approved source receipt"):
            self.validate(masters=masters)


if __name__ == "__main__":
    unittest.main()
