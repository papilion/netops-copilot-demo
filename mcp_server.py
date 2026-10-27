#!/usr/bin/env python3
"""NetOps Copilot MCP server — stdlib only, JSON-RPC over stdio.

Exposes the Batfish-backed change check as tools an agent can call,
instead of a script a human must run. The verdict always comes from
Batfish evidence (live) or from canned Batfish impact reports (mock);
the model is never asked to invent a verdict.

Tools:
  list_scenarios  — the 3 scenarios, with title/intent/mock_only.
  validate_change — scenario + use_mock (default true). With
                    use_mock=false it runs the live Batfish harness
                    (needs batfish-lab + a running Batfish service);
                    mock-only scenarios are rejected in live mode.
  get_policy      — the ALLOW/BLOCK/REVIEW policy rules.

Protocol: newline-delimited JSON-RPC 2.0 on stdin/stdout.
  {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
  {"jsonrpc":"2.0","method":"notifications/initialized"}
  {"jsonrpc":"2.0","id":2,"method":"tools/list"}
  {"jsonrpc":"2.0","id":3,"method":"tools/call",
   "params":{"name":"validate_change",
             "arguments":{"scenario":"block-peer-prefix","use_mock":true}}}

Run:  python3 mcp_server.py
Smoke test:  printf '%s\n' '<initialize>' '<tools/list>' '<tools/call>' \
               | python3 mcp_server.py
All data is fictional (RFC 5737, AS 64496-64498). This server never
applies a change; it only reports a verdict.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import copilot  # noqa: E402

POLICY_TEXT = (
    "BLOCK: a watched route is LOST, or a watched flow stops working "
    "(DENIED / NO_ROUTE / DROP). "
    "REVIEW: a route is ADDED, or a flow changes in a non-fatal way. "
    "ALLOW: only next-hop shifts, with every watched flow unchanged. "
    "Verdicts are derived from Batfish evidence only; a model may only "
    "rewrite the explanation, never change the verdict."
)


def _validate_change(arguments):
    scenario_name = (arguments or {}).get("scenario")
    if scenario_name not in copilot.SCENARIOS:
        raise ValueError("unknown scenario: %r (see list_scenarios)"
                         % scenario_name)
    use_mock = (arguments or {}).get("use_mock", True)
    scenario = copilot.SCENARIOS[scenario_name]
    if use_mock:
        raw = copilot.run_mock(scenario_name)
        evidence_source = "mock (canned Batfish impact report in demo-data/)"
    else:
        if scenario.get("mock_only"):
            raise ValueError("scenario %r is mock-only; no live Batfish "
                             "overlay is shipped for it" % scenario_name)
        raw = copilot.run_batfish(scenario["change_dir"])
        evidence_source = "batfish-live"
    routes, flows = copilot.parse_impact(raw)
    verdict, violations, notes = copilot.apply_policy(routes, flows)
    return {
        "scenario": scenario_name,
        "title": scenario["title"],
        "intent": scenario["intent"],
        "verdict": verdict,
        "violations": violations,
        "notes": notes,
        "routes": routes,
        "flows": flows,
        "evidence_source": evidence_source,
        "policy": POLICY_TEXT,
    }


def _list_scenarios(_arguments):
    return [{"name": name,
             "title": s["title"],
             "intent": s["intent"],
             "mock_only": bool(s.get("mock_only"))}
            for name, s in copilot.SCENARIOS.items()]


TOOLS = {
    "list_scenarios": {
        "description": "List the change scenarios NetOps Copilot can validate.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": _list_scenarios,
    },
    "validate_change": {
        "description": "Validate a proposed BGP/OSPF change against the "
                       "Batfish digital twin (mock evidence by default) "
                       "and return ALLOW, REVIEW or BLOCK with evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario": {"type": "string",
                             "enum": list(copilot.SCENARIOS)},
                "use_mock": {"type": "boolean", "default": True},
            },
            "required": ["scenario"],
        },
        "handler": _validate_change,
    },
    "get_policy": {
        "description": "Return the ALLOW/BLOCK/REVIEW policy rules.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": lambda _a: {"policy": POLICY_TEXT},
    },
}


def handle(request):
    """Handle one JSON-RPC request; returns a response dict or None."""
    method = request.get("method")
    req_id = request.get("id")
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"protocolVersion": "2024-11-05",
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "netops-copilot",
                                          "version": "0.2.0"}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"tools": [
                    {"name": name,
                     "description": t["description"],
                     "inputSchema": t["inputSchema"]}
                    for name, t in TOOLS.items()]}}
    if method == "tools/call":
        params = request.get("params") or {}
        tool = TOOLS.get(params.get("name"))
        if tool is None:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602,
                              "message": "unknown tool: %r" % params.get("name")}}
        try:
            result = tool["handler"](params.get("arguments") or {})
        except Exception as exc:  # noqa: BLE001 - surfaced as tool error
            return {"jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text",
                                            "text": "Error: %s" % exc}],
                               "isError": True}}
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text",
                                        "text": json.dumps(result, ensure_ascii=False)}],
                           "isError": False}}
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": "method not found: %r" % method}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(json.dumps(
                {"jsonrpc": "2.0", "id": None,
                 "error": {"code": -32700, "message": "parse error: %s" % exc}})
                + "\n")
            sys.stdout.flush()
            continue
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
