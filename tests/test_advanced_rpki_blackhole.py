#!/usr/bin/env python3
"""Unit tests for the new advanced scenarios: DDoS blackhole (E4) and
RPKI origin validation (E5). Stdlib unittest only, no network.

Run from the demo folder:  python3 -m unittest discover -s tests -v

Terminology: "recorded replay (mock)" = a canned report played back
without a live server. The --mock flag name is unchanged; new
user-facing text explains it once as recorded replay, then uses
recorded replay.
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


def routes_flows_for(scenario):
    text = (ADV / "demo-data-advanced" / ("%s.txt" % scenario)).read_text()
    return copilot.parse_impact(text)


class TestBlackholeE4(unittest.TestCase):
    def test_intended_victim_only_is_review_not_block(self):
        routes, flows = routes_flows_for("blackhole-rtbh-cust2")
        verdict, violations, notes = advanced.apply_advanced_policy(
            routes, flows, intended_victim="203.0.113.130/32")
        self.assertEqual(verdict, "REVIEW")
        self.assertEqual(violations, [])
        self.assertTrue(any("Intended blackhole" in n for n in notes))
        # Only the victim flow breaks; everything else is intact.
        broken = [f for f in flows if f["verdict"] == "FLOW IMPACT"]
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0]["dst_ip"], "203.0.113.130")

    def test_victim_25_prefix_route_stays_intact(self):
        # Granularity proof for the /32 blackhole: the cust2 /25 route
        # must survive at every node (only the one host drops, not the
        # whole customer prefix). The /32 itself is not a watched prefix,
        # so it does not appear as a route row; the victim flow proves it.
        routes, flows = routes_flows_for("blackhole-rtbh-cust2")
        cust2 = [r for r in routes if r["prefix"] == "203.0.113.128/25"]
        self.assertTrue(cust2, "no cust2 /25 route rows in the report")
        self.assertTrue(all(r["verdict"] == "UNCHANGED" for r in cust2),
                        [r for r in cust2 if r["verdict"] != "UNCHANGED"])
        self.assertEqual(
            [r for r in routes if r["node"] == "edgeb1"
             and r["prefix"] == "203.0.113.128/25"][0]["change"],
            "bgp via ip 198.51.100.14")

    def test_victim_plus_other_break_stays_block(self):
        routes, flows = routes_flows_for("blackhole-rtbh-cust2")
        flows = list(flows) + [{
            "start": "coreA1", "dst_ip": "198.51.100.130",
            "verdict": "FLOW IMPACT",
            "base": "DELIVERED_TO_SUBNET", "change": "NO_ROUTE"}]
        verdict, _, _ = advanced.apply_advanced_policy(
            routes, flows, intended_victim="203.0.113.130/32")
        self.assertEqual(verdict, "BLOCK")

    def test_blackhole_without_declaration_stays_block(self):
        # E4 must be driven by the scenario's declaration, not hard-coded:
        # the same evidence with no intended victim is an outage.
        routes, flows = routes_flows_for("blackhole-rtbh-cust2")
        verdict, _, _ = advanced.apply_advanced_policy(routes, flows)
        self.assertEqual(verdict, "BLOCK")


RPKI_INVALID = {
    "prefix": "203.0.113.0/24", "more_specific": "203.0.113.0/25",
    "peer_ip": "198.51.100.10", "peer_as": 64499,
    "roa_as": 64498, "roa_maxlen": 24, "edge": "edgeB1",
}


class TestRPKIE5(unittest.TestCase):
    def test_invalid_origin_is_block(self):
        routes, flows = routes_flows_for("rpki-invalid-origin")
        verdict, violations, _ = advanced.apply_advanced_policy(
            routes, flows, invalid_announcement=RPKI_INVALID)
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue(any("RPKI invalid" in v for v in violations))

    def test_valid_origin_is_not_block(self):
        # Legitimate cust1 announcement by AS64498 (customer IP).
        routes = [{"node": "edgeb1", "prefix": "203.0.113.0/24",
                   "verdict": "UNCHANGED",
                   "base": "bgp via ip 198.51.100.18",
                   "change": "bgp via ip 198.51.100.18"}]
        verdict, violations, _ = advanced.apply_advanced_policy(routes, [])
        self.assertNotEqual(verdict, "BLOCK")
        self.assertFalse(any("RPKI" in v for v in violations))

    def test_rpki_scenario_is_live_not_recorded_only(self):
        # RPKI is live since the route-map-enforcement redesign: the
        # scenario has a real change overlay (announcement + route-map)
        # plus an unprotected control overlay, and no live_supported=False.
        sc = advanced.SCENARIOS["rpki-invalid-origin"]
        self.assertTrue(sc.get("live_supported", True))
        self.assertTrue(sc["change_dir"].name == "rpki-invalid-origin")
        self.assertTrue(sc["control_dir"].name == "rpki-invalid-origin-unprotected")
        self.assertEqual(sc["invalid_announcement"]["more_specific"],
                         "203.0.113.0/25")

    def test_rpki_protected_run_keeps_legit_route(self):
        # Merged evidence: the protected run's edgeB1 cust1 /24 route
        # must stay via cust1 (198.51.100.18), never via peer2, while
        # the control run diverts cust1 flows to NULL_ROUTED.
        routes, flows = routes_flows_for("rpki-invalid-origin")
        legit = [r for r in routes if r["node"] == "edgeb1"
                 and r["prefix"] == "203.0.113.0/24"]
        self.assertTrue(legit)
        self.assertTrue(all(r["change"] == "bgp via ip 198.51.100.18"
                            for r in legit), legit)
        diverted = [f for f in flows if f["verdict"] == "FLOW IMPACT"
                    and "NULL_ROUTED" in f["change"]
                    and f["dst_ip"] == "203.0.113.10"]
        intact = [f for f in flows if f["verdict"] == "UNCHANGED"
                  and f["dst_ip"] == "203.0.113.10"]
        self.assertTrue(diverted, "control diversion missing")
        self.assertTrue(intact, "protected intact rows missing")

    def test_roa_table_matches_watch_list(self):
        self.assertEqual(advanced.ROAS["203.0.113.0/24"], 64498)
        self.assertEqual(advanced.ROAS["203.0.113.128/25"], 64500)
        self.assertEqual(advanced.ROAS["198.51.100.128/25"], 64497)


class TestNewScenariosDoNotBreakOldOnes(unittest.TestCase):
    def test_all_eight_scenarios_present(self):
        self.assertEqual(set(advanced.SCENARIOS), {
            "link-failure-coreA1-edgeA1", "bgp-session-down-peer1",
            "localpref-exit-shift", "hijack-customer-prefix", "rr-failure",
            "aspath-prepend-deprefer", "blackhole-rtbh-cust2",
            "rpki-invalid-origin"})

    def test_old_mock_verdicts_unchanged(self):
        expected = {
            "link-failure-coreA1-edgeA1": "ALLOW",
            "bgp-session-down-peer1": "BLOCK",
            "localpref-exit-shift": "REVIEW",
            "hijack-customer-prefix": "BLOCK",
            "rr-failure": "BLOCK",
            "aspath-prepend-deprefer": "REVIEW",
        }
        for name, want in expected.items():
            routes, flows = routes_flows_for(name)
            verdict, _, _ = advanced.apply_advanced_policy(routes, flows)
            self.assertEqual(verdict, want, name)


if __name__ == "__main__":
    unittest.main()
