#!/usr/bin/env python3
"""NetOps Copilot — local web app (standard library only).

Serves the same validation the CLI runners do, over HTTP, so an operator
can run a scenario from a browser instead of a terminal. It reuses the
existing policy, parsing, CLI rendering and proposal helpers from
copilot.py and advanced/advanced.py; it does NOT duplicate the policy
and it does NOT write demo-output report files (unlike run_one, which
writes .md/.json on every run — this server only returns the result).

Modes, labelled honestly everywhere:
  recorded — canned Batfish impact reports in demo-data/; works with no
             Batfish server. Labelled "recorded replay" in the UI.
  live     — the Batfish service on port 9996. If Batfish is unreachable
             the endpoint returns HTTP 503 with the exact start command
             and does NOT silently fall back to recorded.

Port conflict, stated plainly: the simple lab and the advanced lab share
Batfish port 9996, so only one Batfish service runs at a time. Stop one
before starting the other. This server never auto-starts Batfish.

Security: this demo server binds 127.0.0.1 only and has NO
authentication. Do NOT expose it to the internet or a shared network
without adding auth. It never applies a change to a router (validation
only; a human decides). The Meta API key, when set on the server via
META_API_KEY, is used server-side only: it is never sent to the browser,
never shown in the UI, and never logged. Without a key the UI shows
rule-based text with a "Meta API not configured on this server" note —
never a fake model answer.

Run:
  python3 web/app.py            # http://127.0.0.1:8000
  WEB_PORT=8080 python3 web/app.py

Live Batfish (one at a time):
  bash scripts/start-live.sh        (Codespaces / clone: starts the
                                     Batfish container, then this app)
  or, on the original dev machine:
  ~/workspace/batfish-lab/start-batfish.sh
  ~/workspace/batfish-lab-advanced/start-batfish-advanced.sh
"""

import importlib.util
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent
sys.path.insert(0, str(DEMO))

import copilot  # noqa: E402  (scenario defs, policy, parsing, CLI, proposals)

_spec = importlib.util.spec_from_file_location(
    "advanced_mod", DEMO / "advanced" / "advanced.py")
advanced_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(advanced_mod)

SIMPLE_START = "bash scripts/start-live.sh  (starts the Batfish container, then this app)"
ADVANCED_START = "bash scripts/start-live.sh  (starts the Batfish container, then this app)"

VERDICT_MEANING = {
    "ALLOW": "GREEN — every watched customer and partner road still works. "
             "Safe to change, within the watched roads only.",
    "BLOCK": "RED — a watched road is broken, or an invalid announcement must "
             "be rejected. Do not change as proposed.",
    "REVIEW": "YELLOW — a new road appeared, traffic moved to another exit, or "
              "an intended drop (blackhole) needs a human to confirm it "
              "was intended.",
}


def scenario_list():
    """All 11 scenarios, with NO verdict expectation revealed."""
    out = []
    for name, s in copilot.SCENARIOS.items():
        out.append({
            "name": name, "group": "simple", "title": s["title"],
            "intent": s["intent"],
            "live_supported": not s.get("mock_only", False),
        })
    for name, s in advanced_mod.SCENARIOS.items():
        out.append({
            "name": name, "group": "advanced", "title": s["title"],
            "intent": s["intent"], "live_supported": True,
        })
    return out


def _meta_refine(scenario, verdict, violations, notes, proposal, lang="ko"):
    """Refine a rule-based proposal with the Meta API, if configured.

    Returns (proposal, source). The key is read server-side only and is
    never part of the returned payload. On any failure the rule-based
    text stands.
    """
    api_key = os.environ.get("META_API_KEY", "").strip()
    if not api_key:
        return proposal, "rule-based (no API call)"
    model = os.environ.get("META_MODEL", copilot.DEFAULT_MODEL)
    try:
        refined, _usage, _cost = copilot.meta_explanation(
            api_key, model, scenario, verdict, violations, notes, lang,
            prompt_fn=copilot.build_meta_proposal_prompt, proposal=proposal)
    except Exception:
        refined = None
    if refined:
        return refined, "Meta Model API (refined from rule-based proposal)"
    return proposal, "rule-based (Meta API call failed, fell back)"


def validate_simple(name, mode, lang="ko"):
    scenario = copilot.SCENARIOS[name]
    if mode == "recorded":
        raw = copilot.run_mock(name)
        evidence_source = "recorded-replay (canned Batfish impact report)"
    else:
        if scenario.get("mock_only"):
            raise ValueError(
                "Scenario %s has no live Batfish overlay; use recorded "
                "replay for it." % name)
        raw = copilot.run_batfish(scenario["change_dir"])
        evidence_source = "batfish-live"
    routes, flows = copilot.parse_impact(raw)
    verdict, violations, notes = copilot.apply_policy(routes, flows)
    explanation = copilot.local_explanation(
        scenario, verdict, violations, notes, routes, flows, lang)
    explanation_source = "local-template (no API call)"
    api_key = os.environ.get("META_API_KEY", "").strip()
    if api_key:
        model = os.environ.get("META_MODEL", copilot.DEFAULT_MODEL)
        try:
            model_text, _usage, _cost = copilot.meta_explanation(
                api_key, model, scenario, verdict, violations, notes, lang)
        except Exception:
            model_text = None
        if model_text:
            explanation = model_text
            explanation_source = "Meta Model API (%s)" % model
    proposal = copilot.propose_next_step(verdict, violations, notes, lang)
    proposal, proposal_source = _meta_refine(
        scenario, verdict, violations, notes, proposal, lang)
    return {
        "scenario": name, "group": "simple", "title": scenario["title"],
        "intent": scenario["intent"], "verdict": verdict,
        "verdict_meaning": VERDICT_MEANING[verdict],
        "violations": violations, "notes": notes,
        "routes": routes, "flows": flows,
        "changed_routes": [r for r in routes if r["verdict"] != "UNCHANGED"],
        "changed_flows": [f for f in flows if f["verdict"] != "UNCHANGED"],
        "unchanged_count": sum(1 for r in routes if r["verdict"] == "UNCHANGED")
        + sum(1 for f in flows if f["verdict"] == "UNCHANGED"),
        "explanation": explanation, "explanation_source": explanation_source,
        "proposed_next_step": proposal,
        "proposed_next_step_source": proposal_source,
        "evidence_source": evidence_source,
        "cli_view": copilot.render_cli(routes, flows),
        "meta_configured": bool(api_key),
    }


def validate_advanced(name, mode, lang="ko"):
    scenario = advanced_mod.SCENARIOS[name]
    control_routes = control_flows = None
    protected_routes = protected_flows = None
    if mode == "recorded":
        raw = (advanced_mod.DATA_DIR / ("%s.txt" % name)).read_text(
            encoding="utf-8")
        evidence_source = "recorded-replay (canned live Batfish report)"
    elif scenario.get("control_dir"):
        raw_control = advanced_mod.run_batfish_advanced(
            scenario["control_dir"])
        raw = advanced_mod.run_batfish_advanced(scenario["change_dir"])
        control_routes, control_flows = copilot.parse_impact(raw_control)
        raw = (raw_control + "\n\n===== Protected run (with route-map) "
               "=====\n\n" + raw)
        evidence_source = "batfish-live-advanced"
    else:
        raw = advanced_mod.run_batfish_advanced(scenario["change_dir"])
        evidence_source = "batfish-live-advanced"
    routes, flows = copilot.parse_impact(raw)
    if "===== Protected run (with route-map) =====" in raw:
        _ctrl_raw, _prot_raw = raw.split(
            "===== Protected run (with route-map) =====", 1)
        control_routes, control_flows = copilot.parse_impact(_ctrl_raw)
        protected_routes, protected_flows = copilot.parse_impact(_prot_raw)
    verdict, violations, notes = advanced_mod.apply_advanced_policy(
        routes, flows, intended_victim=scenario.get("intended_victim"),
        invalid_announcement=scenario.get("invalid_announcement"))
    explanation = copilot.local_explanation(
        scenario, verdict, violations, notes, routes, flows, lang)
    proposal = advanced_mod.propose_next_step_advanced(
        name, verdict, violations, notes, lang)
    proposal, proposal_source = _meta_refine(
        scenario, verdict, violations, notes, proposal, lang)
    if control_routes is not None and protected_routes is not None:
        cli_view = (copilot.render_cli(
            control_routes, control_flows,
            label="Control run (announcement only, no route-map)")
            + "\n\n" + copilot.render_cli(
                protected_routes, protected_flows,
                label="Protected run (announcement + edgeB1 route-map)"))
    else:
        cli_view = copilot.render_cli(routes, flows)
    result = {
        "scenario": name, "group": "advanced", "title": scenario["title"],
        "intent": scenario["intent"], "verdict": verdict,
        "verdict_meaning": VERDICT_MEANING[verdict],
        "violations": violations, "notes": notes,
        "routes": routes, "flows": flows,
        "changed_routes": [r for r in routes if r["verdict"] != "UNCHANGED"],
        "changed_flows": [f for f in flows if f["verdict"] != "UNCHANGED"],
        "unchanged_count": sum(1 for r in routes if r["verdict"] == "UNCHANGED")
        + sum(1 for f in flows if f["verdict"] == "UNCHANGED"),
        "explanation": explanation,
        "explanation_source": "local-template (no API call)",
        "proposed_next_step": proposal,
        "proposed_next_step_source": proposal_source,
        "evidence_source": evidence_source,
        "cli_view": cli_view,
        "meta_configured": bool(os.environ.get("META_API_KEY", "").strip()),
        "control_routes": control_routes, "control_flows": control_flows,
        "protected_routes": protected_routes,
        "protected_flows": protected_flows,
    }
    return result


def validate(name, mode, lang="ko"):
    """Dispatch to the simple or advanced validator. Raises on error."""
    if name in copilot.SCENARIOS:
        return validate_simple(name, mode, lang)
    if name in advanced_mod.SCENARIOS:
        return validate_advanced(name, mode, lang)
    raise ValueError("Unknown scenario: %s" % name)


def live_start_command(group):
    return SIMPLE_START if group == "simple" else ADVANCED_START


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep stdout clean
        pass

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, content_type):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._file(HERE / "static" / "index.html", "text/html; charset=utf-8")
        elif parsed.path == "/api/scenarios":
            self._json(200, {"scenarios": scenario_list()})
        elif parsed.path.startswith("/docs/"):
            name = Path(parsed.path).name
            target = DEMO / "docs" / name
            if name.endswith(".png") and target.exists():
                self._file(target, "image/png")
            else:
                self._json(404, {"error": "not found"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/validate":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception as exc:
            self._json(400, {"error": "invalid JSON: %s" % exc})
            return
        name = body.get("scenario", "")
        mode = body.get("mode", "recorded")
        lang = body.get("lang", "ko")
        if mode not in ("live", "recorded"):
            self._json(400, {"error": "mode must be 'live' or 'recorded'"})
            return
        group = "simple" if name in copilot.SCENARIOS else (
            "advanced" if name in advanced_mod.SCENARIOS else None)
        if group is None:
            self._json(400, {"error": "Unknown scenario: %s" % name})
            return
        try:
            result = validate(name, mode, lang)
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            # Live Batfish unreachable (or harness failure): say so
            # plainly, give the exact start command, never fake a verdict.
            if mode == "live":
                self._json(503, {
                    "error": "Batfish is not reachable. Start exactly one "
                             "Batfish service, then try again. Do not start "
                             "both labs: they share port 9996.",
                    "start_command": live_start_command(group),
                    "detail": str(exc)[-500:],
                })
            else:
                self._json(500, {"error": str(exc)[-500:]})
            return
        self._json(200, result)


def main():
    port = int(os.environ.get("WEB_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("NetOps Copilot web app: http://127.0.0.1:%d/ (local only)"
          % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
