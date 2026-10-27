"""Tests for web/app.py — recorded path and live-unreachable error path.

No Batfish server is needed: recorded scenarios use canned reports, and
the live-unreachable path is exercised by patching the harness call to
raise (as it does on connection refused). The server is started on an
ephemeral localhost port in a thread and stopped after each test class.
"""
import importlib.util
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("web_app", DEMO / "web" / "app.py")
web_app = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(web_app)


def _post(port, payload):
    req = urllib.request.Request(
        "http://127.0.0.1:%d/api/validate" % port,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _get(port, path):
    with urllib.request.urlopen(
            "http://127.0.0.1:%d%s" % (port, path), timeout=30) as resp:
        body = resp.read()
        if path.startswith("/api/"):
            body = json.loads(body)
        return resp.status, body


class WebAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_scenarios_list_has_11(self):
        status, body = _get(self.port, "/api/scenarios")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["scenarios"]), 11)
        names = [s["name"] for s in body["scenarios"]]
        self.assertIn("ospf-cost-shift", names)
        self.assertIn("rpki-invalid-origin", names)
        # No verdict expectation is revealed before a run.
        self.assertNotIn("verdict", json.dumps(body))

    def test_recorded_simple_allow(self):
        status, data = _post(self.port, {"scenario": "ospf-cost-shift",
                                         "mode": "recorded"})
        self.assertEqual(status, 200)
        self.assertEqual(data["verdict"], "ALLOW")
        self.assertIn("recorded", data["evidence_source"])
        self.assertIn("NOT actual device output", data["cli_view"])

    def test_recorded_advanced_block(self):
        status, data = _post(self.port, {"scenario": "bgp-session-down-peer1",
                                         "mode": "recorded"})
        self.assertEqual(status, 200)
        self.assertEqual(data["verdict"], "BLOCK")
        self.assertIn("recorded", data["evidence_source"])

    def test_recorded_advanced_review(self):
        status, data = _post(self.port, {"scenario": "localpref-exit-shift",
                                         "mode": "recorded"})
        self.assertEqual(status, 200)
        self.assertEqual(data["verdict"], "REVIEW")

    def test_live_unreachable_returns_503_with_start_command(self):
        orig = web_app.copilot.run_batfish
        web_app.copilot.run_batfish = lambda _d: (_ for _ in ()).throw(
            RuntimeError("connection refused"))
        try:
            status, data = _post(self.port, {"scenario": "ospf-cost-shift",
                                             "mode": "live"})
        finally:
            web_app.copilot.run_batfish = orig
        self.assertEqual(status, 503)
        self.assertIn("start-batfish.sh", data["start_command"])
        self.assertNotIn("verdict", data)

    def test_live_mock_only_scenario_is_rejected(self):
        status, data = _post(self.port, {"scenario": "add-customer-prefix",
                                         "mode": "live"})
        self.assertEqual(status, 400)
        self.assertIn("recorded", data["error"])

    def test_unknown_scenario_is_rejected(self):
        status, _data = _post(self.port, {"scenario": "no-such-scenario",
                                          "mode": "recorded"})
        self.assertEqual(status, 400)

    def test_index_and_topology_png_serve(self):
        status, body = _get(self.port, "/")
        self.assertEqual(status, 200)
        self.assertIn(b"NetOps Copilot", body)
        status, body = _get(self.port, "/docs/topology-simple.png")
        self.assertEqual(status, 200)
        self.assertTrue(body.startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
