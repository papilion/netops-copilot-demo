#!/usr/bin/env python3
"""NetOps Copilot — ADVANCED lab (Meta Global AI Developer Hackathon).

Same idea as the simple demo, on a larger fictional topology:
  AS64496 backbone, two regions, one route reflector, OSPF areas 0/10/20,
  two peers, two customers (one dual-homed), one transit upstream.
  See README-advanced.md for the topology, scenario table and policy rules.

This file does NOT replace the simple demo. Run the simple demo with
  python3 copilot.py --mock --all
and the advanced demo with
  python3 advanced/advanced.py --mock --all          (no Batfish needed)
  python3 advanced/advanced.py --all                (live Batfish, see README)

Policy: the simple policy (copilot.apply_policy) runs first, then the
advanced extensions in apply_advanced_policy() — see that function's
docstring for E1 (NULL_ROUTED is fatal), E2 (exit-shift -> REVIEW) and
E3 (hijack announcement via direct peer next-hop, the documented proxy
because Batfish's routes query exposes no AS_PATH).

All data fictional (RFC 5737, AS 64496-64501). No production configs.
This demo never applies a change; a human decides.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent
sys.path.insert(0, str(DEMO))
import copilot  # noqa: E402  (reuse parse_impact, local_explanation, Meta helpers)

ADV_LAB = Path.home() / "workspace" / "batfish-lab-advanced"
SIMPLE_LAB = Path.home() / "workspace" / "batfish-lab"
ADV_VENV_PYTHON = SIMPLE_LAB / "venv" / "bin" / "python"  # pybatfish lives here
ADV_VALIDATE = ADV_LAB / "harness" / "validate.py"
ADV_WATCH = ADV_LAB / "watch-advanced.json"
ADV_SNAPSHOT = ADV_LAB / "snapshot"
OUT_DIR = HERE / "demo-output-advanced"
DATA_DIR = HERE / "demo-data-advanced"

SCENARIOS = {
    "link-failure-coreA1-edgeA1": {
        "title": "Link failure: coreA1-edgeA1 shutdown",
        "intent": "Shutdown the coreA1-edgeA1 link; traffic must reroute via coreA2 and all watched flows must survive.",
        "change_dir": ADV_LAB / "changes" / "link-failure-coreA1-edgeA1",
    },
    "bgp-session-down-peer1": {
        "title": "eBGP session down: edgeA1-peer1 neighbor shutdown",
        "intent": "Shutdown the edgeA1-peer1 eBGP session; the peer1 prefix must be lost and its flow must break, while customer prefixes stay intact.",
        "change_dir": ADV_LAB / "changes" / "bgp-session-down-peer1",
    },
    "localpref-exit-shift": {
        "title": "LOCAL_PREF exit shift: cust1 via edgeB1 preferred",
        "intent": "Raise LOCAL_PREF to 200 for cust1 at edgeB1; every core must shift the cust1 exit from edgeA2 to edgeB1, with all flows surviving.",
        "change_dir": ADV_LAB / "changes" / "localpref-exit-shift",
    },
    "hijack-customer-prefix": {
        "title": "More-specific hijack: peer2 announces 203.0.113.0/25 via Null0",
        "intent": "Peer2 announces a more-specific of cust1's /24; traffic to 203.0.113.10 must divert to peer2's Null0 and break. See README-advanced.md for why the exact /24 announcement was replaced: Batfish kept the legitimate best path for /24, so the classic more-specific hijack is the scenario that actually diverts traffic in this lab.",
        "change_dir": ADV_LAB / "changes" / "hijack-customer-prefix",
    },
    "rr-failure": {
        "title": "Route reflector failure: rr1 interfaces shutdown",
        "intent": "Shutdown rr1; iBGP clients must lose reflected routes and all watched flows must break.",
        "change_dir": ADV_LAB / "changes" / "rr-failure",
    },
    "aspath-prepend-deprefer": {
        "title": "AS_PATH prepend deprefer: cust1 via edgeA2 prepended",
        "intent": "Prepend AS64496 twice to cust1 at edgeA2; every core must shift the cust1 exit to edgeB1, with all flows surviving.",
        "change_dir": ADV_LAB / "changes" / "aspath-prepend-deprefer",
    },
}

# --- advanced policy extensions -------------------------------------------
# Batfish's routes query returns Node/VRF/Network/Next_Hop/Protocol only —
# no AS_PATH. The hijack rule therefore uses the next-hop as a proxy and
# says so wherever it is used. A direct eBGP next-hop that is a peer IP
# for a watched *customer* prefix is an announcement from the wrong source.
PEER_IPS = {"198.51.100.2", "198.51.100.10", "198.51.100.22"}  # peer1, peer2, transit1
CUSTOMER_PREFIXES = {"203.0.113.0/24", "203.0.113.128/25"}
FATAL_DISPOSITIONS = ("DENIED", "NO_ROUTE", "DROP", "NULL_ROUTED")
# next-hop IP -> the edge that owns that exit (loopbacks and direct eBGP IPs)
EDGE_OF_IP = {
    "192.0.2.3": "edgeA1", "192.0.2.4": "edgeA2", "192.0.2.7": "edgeB1",
    "192.0.2.1": "coreA1", "192.0.2.2": "coreA2",
    "192.0.2.5": "coreB1", "192.0.2.6": "coreB2", "192.0.2.8": "rr1",
    "198.51.100.2": "edgeA1", "198.51.100.22": "edgeA1",
    "198.51.100.6": "edgeA2", "198.51.100.18": "edgeB1",
    "198.51.100.10": "edgeB1", "198.51.100.14": "edgeB1",
}


def _next_hop_ip(route_text):
    """Extract the IP from 'ibgp via ip X' / 'bgp via ip X'; None otherwise."""
    m = re.search(r"via ip (\S+)", route_text or "")
    return m.group(1) if m else None


def apply_advanced_policy(routes, flows):
    """Simple policy first, then advanced extensions.

    E1: NULL_ROUTED is a fatal flow disposition (in addition to the simple
        policy's DENIED/NO_ROUTE/DROP). A flow diverted to a Null0 is broken.
    E2: Exit shift -> REVIEW. If the simple policy says ALLOW but a watched
        prefix's exit edge changed (base edge != change edge) while all
        flows survive, the change is not a plain ALLOW: it moves traffic
        between regions/edges and a human must confirm the new exit.
        A single next-hop change that stays on the same edge is still ALLOW.
    E3: Hijack announcement -> BLOCK. A watched customer prefix whose
        change route is a direct eBGP route via a peer IP (not a customer
        IP) is an announcement from the wrong source. Proxy disclaimer:
        Batfish's routes query exposes no AS_PATH, so this rule uses the
        direct next-hop IP, which is unambiguous at the edge that receives
        the announcement (its own direct next-hop is either the customer
        or the peer, never both).
    Returns (verdict, violations, notes).
    """
    verdict, violations, notes = copilot.apply_policy(routes, flows)
    violations = list(violations)
    notes = list(notes)

    # E3: hijack announcement (check first so it is reported even if other
    # violations already make the verdict BLOCK).
    for r in routes:
        if r["prefix"] not in CUSTOMER_PREFIXES:
            continue
        ch_ip = _next_hop_ip(r["change"])
        if r["verdict"] in ("UNCHANGED", "NEXT-HOP CHANGED", "ROUTE ADDED") and ch_ip in PEER_IPS:
            # Only a direct eBGP route counts: iBGP next-hops are loopbacks,
            # never peer IPs, so this cannot fire on a legitimate iBGP route.
            if r["change"].strip().startswith("bgp "):
                violations.append(
                    "Hijack: watched customer prefix %s at %s is now via peer IP %s "
                    "(direct eBGP next-hop, not a customer IP). AS_PATH is not "
                    "exposed by Batfish's routes query, so the direct peer "
                    "next-hop is used as the documented proxy."
                    % (r["prefix"], r["node"], ch_ip)
                )
    # E1: NULL_ROUTED flows are fatal (simple policy puts them in notes).
    for f in flows:
        if f["verdict"] == "FLOW IMPACT" and "NULL_ROUTED" in f["change"]:
            violations.append(
                "Watched flow %s -> %s stops working: %s -> NULL_ROUTED "
                "(diverted to a Null0, e.g. by a more-specific hijack)"
                % (f["start"], f["dst_ip"], f["base"])
            )
            notes = [n for n in notes if not (f["start"] in n and f["dst_ip"] in n)]
    if violations:
        return "BLOCK", violations, notes

    # E2: exit shift -> REVIEW (only when the simple policy said ALLOW).
    if verdict == "ALLOW":
        for r in routes:
            if r["verdict"] != "NEXT-HOP CHANGED":
                continue
            base_edge = EDGE_OF_IP.get(_next_hop_ip(r["base"]))
            change_edge = EDGE_OF_IP.get(_next_hop_ip(r["change"]))
            if base_edge and change_edge and base_edge != change_edge:
                notes.append(
                    "Exit shift for %s: %s -> %s (%s -> %s); flows survive, "
                    "but the new exit must be confirmed by a human."
                    % (r["prefix"], base_edge, change_edge,
                       _next_hop_ip(r["base"]), _next_hop_ip(r["change"]))
                )
                return "REVIEW", violations, notes
    return verdict, violations, notes


def run_batfish_advanced(change_dir):
    cmd = [str(ADV_VENV_PYTHON), str(ADV_VALIDATE),
           "--snapshot", str(ADV_SNAPSHOT), "--watch", str(ADV_WATCH),
           "--change", str(change_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            "Advanced Batfish harness failed.\nSTDOUT:\n%s\nSTDERR:\n%s"
            % (proc.stdout, proc.stderr)
        )
    return proc.stdout


def run_one(name, mock=False):
    scenario = SCENARIOS[name]
    print("== %s ==" % scenario["title"])
    if mock:
        raw = (DATA_DIR / ("%s.txt" % name)).read_text(encoding="utf-8")
        source = "mock-advanced (canned live Batfish impact report)"
    else:
        raw = run_batfish_advanced(scenario["change_dir"])
        source = "batfish-live-advanced"
    routes, flows = copilot.parse_impact(raw)
    verdict, violations, notes = apply_advanced_policy(routes, flows)
    explanation = copilot.local_explanation(
        scenario, verdict, violations, notes, routes, flows)
    result = {
        "scenario": name,
        "title": scenario["title"],
        "intent": scenario["intent"],
        "verdict": verdict,
        "violations": violations,
        "notes": notes,
        "routes": routes,
        "flows": flows,
        "explanation": explanation,
        "evidence_source": source,
        "policy": "advanced (simple policy + E1 NULL_ROUTED fatal, "
                  "E2 exit-shift REVIEW, E3 hijack peer-next-hop BLOCK)",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % name)).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# NetOps Copilot (advanced) — %s" % scenario["title"], "",
              "**Verdict: %s**" % verdict, "", explanation, "",
              "## Evidence (Batfish, %s)" % source, ""]
    for r in routes:
        report.append("- %s %s: %s (base: %s -> change: %s)"
                      % (r["node"], r["prefix"], r["verdict"], r["base"], r["change"]))
    for f in flows:
        report.append("- flow %s -> %s: %s (%s -> %s)"
                      % (f["start"], f["dst_ip"], f["verdict"], f["base"], f["change"]))
    report += ["", "---", "", "### Batfish raw output", "", "```", raw.rstrip(), "```"]
    (OUT_DIR / ("%s.md" % name)).write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Verdict: %s" % verdict)
    print(explanation)
    print("-> %s" % (OUT_DIR / ("%s.md" % name)))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--change", choices=list(SCENARIOS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--mock", action="store_true",
                    help="use canned live impact reports, no Batfish needed")
    args = ap.parse_args()
    names = list(SCENARIOS) if args.all else [args.change]
    if not names:
        ap.error("give --change <name> or --all")
    for name in names:
        run_one(name, mock=args.mock)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
