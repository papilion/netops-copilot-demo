#!/usr/bin/env python3
"""Unit tests for the ADVANCED lab policy — stdlib unittest only, no network.

Run from the demo folder:  python3 -m unittest discover -s tests -v
Covers: hijack rule (E3), exit-shift REVIEW (E2), NULL_ROUTED fatal (E1),
link-failure reroute is not BLOCK, RR-failure BLOCK, and mock verdicts
matching the live verdicts recorded in README-advanced.md.
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

EXPECTED = {
    "link-failure-coreA1-edgeA1": "ALLOW",
    "bgp-session-down-peer1": "BLOCK",
    "localpref-exit-shift": "REVIEW",
    "hijack-customer-prefix": "BLOCK",
    "rr-failure": "BLOCK",
    "aspath-prepend-deprefer": "REVIEW",
}


def verdict_for(scenario):
    text = (ADV / "demo-data-advanced" / ("%s.txt" % scenario)).read_text()
    routes, flows = copilot.parse_impact(text)
    verdict, _, _ = advanced.apply_advanced_policy(routes, flows)
    return verdict, routes, flows


class TestAdvancedPolicy(unittest.TestCase):
    def test_hijack_rule_blocks_direct_peer_next_hop(self):
        # Synthetic: edgeB1's cust route via peer2 IP, not the customer IP.
        # Batfish's routes query has no AS_PATH, so this next-hop is the
        # documented proxy for a hijack announcement.
        routes = [{"node": "edgeb1", "prefix": "203.0.113.0/24",
                   "verdict": "NEXT-HOP CHANGED",
                   "base": "bgp via ip 198.51.100.18",
                   "change": "bgp via ip 198.51.100.10"}]
        verdict, violations, _ = advanced.apply_advanced_policy(routes, [])
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any("Hijack" in v for v in violations))

    def test_hijack_rule_does_not_fire_on_legitimate_ibgp(self):
        routes = [{"node": "corea1", "prefix": "203.0.113.0/24",
                   "verdict": "NEXT-HOP CHANGED",
                   "base": "ibgp via ip 192.0.2.4",
                   "change": "ibgp via ip 192.0.2.7"}]
        verdict, violations, _ = advanced.apply_advanced_policy(routes, [])
        self.assertNotEqual(verdict, "BLOCK")
        self.assertFalse(any("Hijack" in v for v in violations))

    def test_link_failure_reroute_is_not_block(self):
        verdict, routes, flows = verdict_for("link-failure-coreA1-edgeA1")
        self.assertEqual(verdict, "ALLOW")
        self.assertTrue(all(f["verdict"] == "UNCHANGED" for f in flows))
        self.assertTrue(all(r["verdict"] == "UNCHANGED" for r in routes))

    def test_rr_failure_blocks(self):
        verdict, routes, flows = verdict_for("rr-failure")
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any(f["verdict"] == "FLOW IMPACT" for f in flows))
        self.assertTrue(any(r["verdict"] == "ROUTE LOST" for r in routes))

    def test_exit_shift_is_review_not_allow(self):
        for scenario in ("localpref-exit-shift", "aspath-prepend-deprefer"):
            verdict, _, flows = verdict_for(scenario)
            self.assertEqual(verdict, "REVIEW")
            self.assertTrue(all(f["verdict"] == "UNCHANGED" for f in flows))

    def test_null_routed_is_fatal(self):
        verdict, _, flows = verdict_for("hijack-customer-prefix")
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any("NULL_ROUTED" in f["change"] for f in flows))

    def test_mock_verdicts_match_live_verdicts(self):
        # Mock data are verbatim live Batfish reports, so the verdicts
        # computed from them must equal the live verdicts in the README.
        for scenario, expected in EXPECTED.items():
            verdict, _, _ = verdict_for(scenario)
            self.assertEqual(verdict, expected, scenario)

    def test_simple_demo_scenarios_unchanged(self):
        # The advanced work must not change the simple demo's scenario set.
        self.assertEqual(set(copilot.SCENARIOS),
                         {"ospf-cost-shift", "block-peer-prefix",
                          "add-customer-prefix"})


if __name__ == "__main__":
    unittest.main()
