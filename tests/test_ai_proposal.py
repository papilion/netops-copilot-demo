#!/usr/bin/env python3
"""Unit tests for the AI proposal field: the model NEVER decides the
verdict. Batfish evidence decides (apply_policy); propose_next_step()
only suggests a next step, labelled as NOT the verdict, and every
proposal must be re-simulated before anyone trusts it.

These tests cover the helpers only — they do not call run_one, so
they never overwrite demo-output reports.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ADV = HERE / "advanced"
sys.path.insert(0, str(ADV))
sys.path.insert(0, str(HERE))

import advanced  # noqa: E402
import copilot  # noqa: E402


class TestProposalLabelAndVerdictSeparation(unittest.TestCase):
    def test_every_proposal_says_not_the_verdict_and_re_simulate(self):
        for verdict in ("ALLOW", "BLOCK", "REVIEW"):
            for lang in ("en", "ko"):
                text = copilot.propose_next_step(verdict, [], [], lang)
                self.assertIn("NOT the verdict" if lang == "en"
                              else "판정이 아닙니다", text)
                self.assertIn("re-simulated" if lang == "en"
                              else "시뮬레이션", text)

    def test_block_proposals_are_concrete_not_generic(self):
        rpki = copilot.propose_next_step("BLOCK", ["RPKI invalid: x"], [], "en")
        self.assertIn("ROA", rpki)
        hijack = copilot.propose_next_step("BLOCK", ["Hijack: x"], [], "en")
        self.assertIn("Reject the announcement from the peer", hijack)
        review = copilot.propose_next_step("REVIEW", [], ["new route"], "en")
        self.assertIn("confirm the intent", review)

    def test_proposal_does_not_change_verdicts(self):
        # Same evidence, with or without asking for a proposal, must
        # give the same verdict — the helper takes the verdict as input
        # and never feeds anything back into apply_policy.
        routes, flows = [], []
        verdict, _, _ = copilot.apply_policy(routes, flows)
        self.assertEqual(verdict, "ALLOW")
        copilot.propose_next_step(verdict, [], [], "en")
        verdict2, _, _ = copilot.apply_policy(routes, flows)
        self.assertEqual(verdict, verdict2)


class TestAdvancedProposals(unittest.TestCase):
    def test_blackhole_proposal_is_32_not_25(self):
        text = advanced.propose_next_step_advanced(
            "blackhole-rtbh-cust2", "REVIEW", [], [], "en")
        self.assertIn("203.0.113.130", text)
        self.assertIn("do NOT widen it to the whole cust2 /25", text)
        self.assertIn("NOT the verdict", text)

    def test_hijack_proposal_rejects_announcement(self):
        # Live hijack evidence has no "Hijack" violation row (the /25 is
        # not a watched prefix), so the proposal is name-based.
        text = advanced.propose_next_step_advanced(
            "hijack-customer-prefix", "BLOCK", [], [], "en")
        self.assertIn("Reject the more-specific announcement", text)
        self.assertIn("cust1", text)

    def test_rpki_proposal_rejects_and_fixes_roa(self):
        text = advanced.propose_next_step_advanced(
            "rpki-invalid-origin", "BLOCK", ["RPKI invalid: x"], [], "en")
        self.assertIn("Reject the invalid announcement", text)
        self.assertIn("ROA", text)
        self.assertIn("re-simulate the legitimate AS64498", text)


if __name__ == "__main__":
    unittest.main()
