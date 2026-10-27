#!/usr/bin/env python3
"""Unit tests for NetOps Copilot — stdlib unittest only, no network.

Run from the demo folder:  python3 -m unittest discover -s tests -v
Covers: impact parsing, ALLOW/BLOCK/REVIEW policy, mock evidence
verdicts, and the Meta API prompt / usage / cost helpers (offline).
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import copilot  # noqa: E402


class TestParseAndPolicy(unittest.TestCase):
    def test_allow_when_nothing_changes(self):
        text = (HERE / "demo-data" / "ospf-cost-shift.txt").read_text()
        routes, flows = copilot.parse_impact(text)
        self.assertEqual(len(routes), 9)
        self.assertEqual(len(flows), 2)
        verdict, violations, notes = copilot.apply_policy(routes, flows)
        self.assertEqual(verdict, "ALLOW")
        self.assertEqual(violations, [])
        self.assertEqual(notes, [])

    def test_block_on_route_lost_and_flow_break(self):
        text = (HERE / "demo-data" / "block-peer-prefix.txt").read_text()
        routes, flows = copilot.parse_impact(text)
        verdict, violations, notes = copilot.apply_policy(routes, flows)
        self.assertEqual(verdict, "BLOCK")
        self.assertEqual(len(violations), 4)
        self.assertTrue(any("198.51.100.128/25" in v for v in violations))
        self.assertTrue(any("NO_ROUTE" in v for v in violations))

    def test_review_on_route_added(self):
        text = (HERE / "demo-data" / "add-customer-prefix.txt").read_text()
        routes, flows = copilot.parse_impact(text)
        verdict, violations, notes = copilot.apply_policy(routes, flows)
        self.assertEqual(verdict, "REVIEW")
        self.assertEqual(violations, [])
        self.assertTrue(any("203.0.113.128/25" in n for n in notes))

    def test_customer_prefix_intact_in_block_scenario(self):
        text = (HERE / "demo-data" / "block-peer-prefix.txt").read_text()
        routes, _ = copilot.parse_impact(text)
        cust = [r for r in routes if r["prefix"] == "203.0.113.0/24"]
        self.assertTrue(cust)
        self.assertTrue(all(r["verdict"] == "UNCHANGED" for r in cust))

    def test_next_hop_shift_is_not_block(self):
        routes = [{"node": "core1", "prefix": "203.0.113.0/24",
                   "verdict": "NEXT-HOP CHANGED",
                   "base": "ibgp via ip 192.0.2.3",
                   "change": "ibgp via ip 192.0.2.4"}]
        verdict, violations, _ = copilot.apply_policy(routes, [])
        # Policy: next-hop shift alone (no new route, no flow change) = ALLOW.
        self.assertEqual(verdict, "ALLOW")
        self.assertEqual(violations, [])


class TestMetaHelpers(unittest.TestCase):
    def test_prompt_keeps_verdict_and_evidence_only(self):
        scenario = copilot.SCENARIOS["block-peer-prefix"]
        prompt = copilot.build_meta_prompt(scenario, "BLOCK", ["v1"], [])
        self.assertIn("BLOCK", prompt)
        self.assertIn("198.51.100.128/25", prompt)
        self.assertIn("Do NOT invent", prompt)
        data = json.loads(prompt.rsplit("Evidence (JSON):\n", 1)[1])
        self.assertEqual(data["verdict_from_batfish"], "BLOCK")

    def test_parse_meta_response_and_cost(self):
        data = {"choices": [{"message": {"content": "  Briefing text. "}}],
                "usage": {"prompt_tokens": 1000, "completion_tokens": 100,
                          "total_tokens": 1100,
                          "prompt_tokens_details": {"cached_tokens": 200}}}
        text, usage = copilot.parse_meta_response(data)
        self.assertEqual(text, "Briefing text.")
        # (800 * 1.25 + 200 * 0.15 + 100 * 4.25) / 1e6 = 0.001455
        self.assertAlmostEqual(copilot.estimate_cost(usage, "muse-spark-1.3"),
                               0.001455)

    def test_estimate_cost_none_without_usage(self):
        self.assertIsNone(copilot.estimate_cost(None))
        self.assertIsNone(copilot.estimate_cost({}, "muse-spark-1.3"))
        self.assertIsNone(copilot.estimate_cost(
            {"prompt_tokens": 10, "completion_tokens": 5}, "unknown-model"))


if __name__ == "__main__":
    unittest.main()
