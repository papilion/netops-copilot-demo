"""Tests for copilot.render_cli (CLI-style view of Batfish evidence).

The CLI view must use only reported fields, must carry the
NOT-device-output disclaimer, and must never invent an admin
distance, metric, interface name, uptime, or session state.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import copilot  # noqa: E402

ROUTES = [
    {"node": "core1", "prefix": "192.0.2.0/24", "verdict": "UNCHANGED",
     "base": "ibgp via ip 192.0.2.3", "change": "ibgp via ip 192.0.2.3"},
    {"node": "core1", "prefix": "198.51.100.128/25", "verdict": "ROUTE LOST",
     "base": "ibgp via ip 192.0.2.3", "change": "None"},
    {"node": "edge1", "prefix": "198.51.100.128/25", "verdict": "ROUTE LOST",
     "base": "bgp via ip 198.51.100.2", "change": "None"},
    {"node": "edge1", "prefix": "203.0.113.128/25", "verdict": "ROUTE ADDED",
     "base": "None", "change": "bgp via ip 198.51.100.6"},
    {"node": "edgeB1", "prefix": "203.0.113.130/32", "verdict": "NEXT-HOP CHANGED",
     "base": "bgp via ip 198.51.100.14", "change": "static via discard"},
]
FLOWS = [
    {"start": "core1", "dst_ip": "198.51.100.130", "verdict": "FLOW IMPACT",
     "base": "DELIVERED_TO_SUBNET", "change": "NO_ROUTE"},
]


class TestCliView(unittest.TestCase):
    def test_contains_watched_prefix_and_next_hop(self):
        out = copilot.render_cli(ROUTES, FLOWS)
        self.assertIn("198.51.100.128/25", out)
        self.assertIn("198.51.100.2", out)
        self.assertIn("198.51.100.130", out)
        # Node names distinguish the same prefix on two devices.
        self.assertIn("core1:", out)
        self.assertIn("edge1:", out)

    def test_disclaimer_present(self):
        out = copilot.render_cli(ROUTES, FLOWS)
        self.assertIn("NOT actual device output", out)
        self.assertIn("no router was connected", out)

    def test_no_invented_fields(self):
        out = copilot.render_cli(ROUTES, FLOWS)
        # Admin distance / metric are never reported by Batfish.
        self.assertNotIn("[20/0]", out)
        self.assertNotIn("[200/0]", out)
        # "uptime" may only appear in the disclaimer ("not reported");
        # no data line may carry an uptime value.
        for line in out.splitlines()[1:]:
            self.assertNotIn("uptime", line.lower())
        # Protocol codes come from the evidence strings only.
        self.assertIn("B 198.51.100.128/25", out)  # edge1 bgp route
        self.assertIn("S 203.0.113.130/32", out)  # static discard route

    def test_unchanged_routes_omitted_and_said_so(self):
        out = copilot.render_cli(ROUTES, FLOWS)
        self.assertIn("UNCHANGED routes omitted", out)
        # The unchanged 192.0.2.0/24 row must not appear as a route line.
        self.assertNotIn("192.0.2.0/24", out)

    def test_does_not_mutate_inputs(self):
        routes = [dict(r) for r in ROUTES]
        flows = [dict(f) for f in FLOWS]
        copilot.render_cli(routes, flows)
        self.assertEqual(routes, ROUTES)
        self.assertEqual(flows, FLOWS)

    def test_all_reports_carry_cli_view_and_verdict(self):
        root = Path(__file__).resolve().parent.parent
        files = sorted(root.glob("demo-output/*.json")) + sorted(
            root.glob("advanced/demo-output-advanced/*.json"))
        self.assertEqual(len(files), 11)
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            self.assertIn(data["verdict"], ("ALLOW", "BLOCK", "REVIEW"))
            self.assertIn("NOT actual device output", data["cli_view"])
            self.assertNotIn("[20/0]", data["cli_view"])


if __name__ == "__main__":
    unittest.main()
