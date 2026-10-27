#!/usr/bin/env python3
"""NetOps Copilot demo — Meta Global AI Developer Hackathon (Indie).

What it does, in one sentence:
  A proposed BGP/OSPF change is simulated in a Batfish digital twin
  BEFORE it reaches production, and the Copilot reports blast radius,
  policy violations, and a plain-language verdict.

Pipeline:
  1. Run the existing Batfish harness (batfish-lab/harness/validate.py)
     for the base snapshot and for one proposed-change overlay.
  2. Parse its impact report (routes + traceroute flows).
  3. Apply a small, explicit policy (see POLICY below).
  4. Explain the result in plain language.
     - Default: a deterministic local template (no API call, no credit used).
     - Optional: if META_API_KEY is set, ask the Meta Model API
       (OpenAI-compatible endpoint) to rewrite the explanation from the
       SAME impact JSON. The model must not invent routes; the verdict
       always comes from the Batfish evidence, never from the model alone.

Safety / scope:
  - All topologies, prefixes and AS numbers here are FICTIONAL samples
    (RFC 5737 documentation space, AS 64496-64498). No production
    config, no real customer prefix, no company-internal data.
  - This demo never applies a change. It only reports. Applying is a
    separate human decision.

Usage (reproducible, no Batfish needed — start here):
  python3 copilot.py --mock --all
  python3 copilot.py --mock --change add-customer-prefix
Usage (full live Batfish run, needs batfish-lab + a running Batfish service):
  python3 copilot.py --change ospf-cost-shift
  python3 copilot.py --change block-peer-prefix
  python3 copilot.py --all
  META_API_KEY=... META_MODEL=muse-spark-1.3 python3 copilot.py --all
    (default model muse-spark-1.3, confirmed against the dev.meta.ai
     model list on 2026-10-27: $1.25/1M input, $0.15 cached, $4.25/1M output.)

Requires a running Batfish service (batfish-lab/start-batfish.sh)
and the batfish-lab venv (pybatfish).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = Path.home() / "workspace" / "batfish-lab"
VALIDATE = LAB / "harness" / "validate.py"
LAB_VENV_PYTHON = LAB / "venv" / "bin" / "python"
OUT_DIR = HERE / "demo-output"
DATA_DIR = HERE / "demo-data"

# Meta Model API pricing (dev.meta.ai model list, checked 2026-10-27).
# Used only for the cost estimate shown next to an API explanation.
MODEL_PRICING = {
    "muse-spark-1.3": {"input": 1.25, "cached_input": 0.15, "output": 4.25},
}
DEFAULT_MODEL = "muse-spark-1.3"

# ---------------------------------------------------------------- policy
# Verdicts are derived from Batfish evidence only.
#   BLOCK  : a watched route is lost, or a watched flow stops working.
#   REVIEW : a route is added, or a flow changes in a non-fatal way.
#   ALLOW  : only next-hop shifts, with every watched flow unchanged.
# ----------------------------------------------------------------------

ROUTE_RE = re.compile(
    r"^\s+(\S+)\s+(\S+)\s+(UNCHANGED|ROUTE LOST|ROUTE ADDED|NEXT-HOP CHANGED)\s+base\[(.*?)\] -> change\[(.*?)\]\s*$"
)
FLOW_RE = re.compile(
    r"^\s+flow (\S+) -> (\S+): (UNCHANGED|FLOW IMPACT) \((.*?) -> (.*?)\)\s*$"
)

SCENARIOS = {
    "ospf-cost-shift": {
        "title": "OSPF cost shift: core1 -> edge1 link cost 10 -> 100",
        "intent": "Shift traffic so core1 reaches edge1 via core2 instead of directly, "
                  "without breaking any watched prefix or flow.",
        "change_dir": LAB / "changes" / "ospf-cost-shift",
        "mock_file": DATA_DIR / "ospf-cost-shift.txt",
        "mock_only": False,
    },
    "block-peer-prefix": {
        "title": "BGP inbound filter: deny peer prefix 198.51.100.128/25 from peer1 at edge1",
        "intent": "Block the peer prefix 198.51.100.128/25 inbound from peer1 (AS64497).",
        "change_dir": LAB / "changes" / "block-peer-prefix",
        "mock_file": DATA_DIR / "block-peer-prefix.txt",
        "mock_only": False,
    },
    "add-customer-prefix": {
        "title": "Add new customer prefix: 203.0.113.128/25 appears at edge1",
        "intent": "Announce a new fictional customer prefix 203.0.113.128/25 "
                  "without touching any existing watched prefix or flow. "
                  "A new route should be REVIEW, not ALLOW, because a "
                  "human must confirm the new announcement is intended.",
        "change_dir": None,
        "mock_file": DATA_DIR / "add-customer-prefix.txt",
        # Mock-verified only: no live Batfish overlay for this scenario
        # is shipped in the repo, so the live run skips it (see main()).
        "mock_only": True,
    },
}


def run_batfish(change_dir):
    """Run validate.py and return its stdout."""
    cmd = [str(LAB_VENV_PYTHON), str(VALIDATE), "--change", str(change_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            "Batfish harness failed.\nSTDOUT:\n%s\nSTDERR:\n%s"
            % (proc.stdout, proc.stderr)
        )
    return proc.stdout


def run_mock(name):
    """Return the canned Batfish impact report for a scenario.

    The ospf/block files are the verbatim impact reports from the
    recorded live runs (demo-output/*.md, Batfish raw output section);
    parsing them must give the same verdicts as the live runs. The
    add-customer-prefix file is mock-verified only (see SCENARIOS).
    """
    mock_file = SCENARIOS[name]["mock_file"]
    return mock_file.read_text(encoding="utf-8")


def build_meta_prompt(scenario, verdict, violations, notes):
    """Build the Meta Model API prompt from Batfish evidence only."""
    evidence = {
        "change": scenario["title"],
        "intent": scenario["intent"],
        "verdict_from_batfish": verdict,
        "violations": violations,
        "notes": notes,
    }
    return (
        "You are a network operations assistant. Rewrite the following "
        "Batfish simulation result as a short plain-language briefing "
        "for a network engineer (max 5 sentences, Korean). Do NOT invent "
        "routes, prefixes, or flows beyond the evidence. Keep the verdict "
        "exactly as given.\n\nEvidence (JSON):\n%s"
        % json.dumps(evidence, ensure_ascii=False)
    )


def parse_meta_response(data):
    """Extract (text, usage) from an OpenAI-compatible chat response.

    Returns (text, usage_dict_or_None). Raises KeyError/ValueError on
    malformed responses so the caller can fall back to the local template.
    """
    text = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage") or None
    return text, usage


def estimate_cost(usage, model=DEFAULT_MODEL):
    """Estimate USD cost from a usage dict, or None if unusable.

    Pricing is per 1M tokens. prompt_tokens_details.cached_tokens, when
    present, is billed at the cached-input rate; the rest at input rate.
    """
    if not usage:
        return None
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    try:
        prompt = int(usage.get("prompt_tokens", 0))
        completion = int(usage.get("completion_tokens", 0))
        details = usage.get("prompt_tokens_details") or {}
        cached = int(details.get("cached_tokens", 0))
    except (TypeError, ValueError):
        return None
    cached = min(cached, prompt)
    cost = ((prompt - cached) * pricing["input"]
            + cached * pricing["cached_input"]
            + completion * pricing["output"]) / 1_000_000
    return round(cost, 6)


def parse_impact(text):
    routes, flows = [], []
    for line in text.splitlines():
        m = ROUTE_RE.match(line)
        if m:
            node, prefix, verdict, base, change = m.groups()
            routes.append(
                {"node": node, "prefix": prefix, "verdict": verdict,
                 "base": base, "change": change}
            )
            continue
        m = FLOW_RE.match(line)
        if m:
            start, dst, verdict, base, change = m.groups()
            flows.append(
                {"start": start, "dst_ip": dst, "verdict": verdict,
                 "base": base, "change": change}
            )
    return routes, flows


def apply_policy(routes, flows):
    violations, notes = [], []
    for r in routes:
        if r["verdict"] == "ROUTE LOST":
            violations.append(
                "Watched prefix %s: route LOST at %s (was: %s)"
                % (r["prefix"], r["node"], r["base"] or "none")
            )
        elif r["verdict"] == "ROUTE ADDED":
            notes.append(
                "New route for %s at %s (%s)"
                % (r["prefix"], r["node"], r["change"])
            )
        elif r["verdict"] == "NEXT-HOP CHANGED":
            notes.append(
                "Path shift for %s at %s: %s -> %s"
                % (r["prefix"], r["node"], r["base"], r["change"])
            )
    for f in flows:
        if f["verdict"] == "FLOW IMPACT":
            # A flow that stops being accepted is a hard violation;
            # any other disposition change is still flagged.
            if "DENIED" in f["change"] or "NO_ROUTE" in f["change"] or "DROP" in f["change"]:
                violations.append(
                    "Watched flow %s -> %s stops working: %s -> %s"
                    % (f["start"], f["dst_ip"], f["base"], f["change"])
                )
            else:
                notes.append(
                    "Flow %s -> %s changed: %s -> %s"
                    % (f["start"], f["dst_ip"], f["base"], f["change"])
                )
    if violations:
        verdict = "BLOCK"
    elif notes and any("New route" in n or "Flow" in n for n in notes):
        verdict = "REVIEW"
    else:
        verdict = "ALLOW"
    return verdict, violations, notes


def local_explanation(scenario, verdict, violations, notes, routes, flows):
    """Deterministic explanation from evidence only (no model call)."""
    affected = sorted({r["prefix"] for r in routes if r["verdict"] != "UNCHANGED"})
    lines = []
    lines.append("의도: %s" % scenario["intent"])
    if verdict == "ALLOW":
        lines.append(
            "판정: 적용 가능 (감시 범위 내). 감시 대상 prefix의 경로가 "
            "사라지지 않았고, 감시 대상 flow도 모두 유지됐습니다. "
            "판정은 감시 대상 항목 기준이며, 감시 범위 밖의 전달 경로 "
            "변화까지 보장하지 않습니다."
        )
    elif verdict == "BLOCK":
        lines.append(
            "판정: 적용 중단. 아래 영향이 확인됐기 때문에, 의도가 "
            "정확히 이 영향과 일치하지 않는 한 운영망에 적용하면 안 됩니다."
        )
    else:
        lines.append("판정: 재검토 필요. 아래 변경 사항을 확인한 뒤 적용 여부를 결정하세요.")
    for v in violations:
        lines.append("- 위반: %s" % v)
    for n in notes:
        lines.append("- 참고: %s" % n)
    if affected:
        lines.append("영향 받은 prefix: %s" % ", ".join(affected))
    else:
        lines.append("영향 받은 prefix: 없음")
    return "\n".join(lines)


def meta_explanation(api_key, model, scenario, verdict, violations, notes):
    """Ask Meta Model API to rewrite the explanation from the same evidence.

    Returns (text_or_None, usage_or_None, cost_or_None). On any failure
    the caller falls back to the local explanation — the verdict itself
    never depends on this call.
    """
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user",
                      "content": build_meta_prompt(scenario, verdict, violations, notes)}],
        "temperature": 0.2,
        "max_tokens": 400,
    }).encode()
    req = urllib.request.Request(
        "https://api.meta.ai/v1/chat/completions",
        data=body,
        headers={"Authorization": "Bearer %s" % api_key,
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        text, usage = parse_meta_response(data)
        return text, usage, estimate_cost(usage, model)
    except Exception as exc:  # noqa: BLE001 - demo fallback path
        print("Meta API call failed (%s); using local explanation." % exc,
              file=sys.stderr)
        return None, None, None


def run_one(name, mock=False):
    scenario = SCENARIOS[name]
    print("== %s ==" % scenario["title"])
    if mock:
        raw = run_mock(name)
        evidence_source = "mock (canned Batfish impact report in demo-data/)"
    else:
        if scenario.get("mock_only"):
            print("Skipping %s: mock-only scenario, no live Batfish overlay." % name)
            return None
        raw = run_batfish(scenario["change_dir"])
        evidence_source = "batfish-live"
    routes, flows = parse_impact(raw)
    verdict, violations, notes = apply_policy(routes, flows)
    explanation = local_explanation(scenario, verdict, violations, notes, routes, flows)
    source = "local-template (no API call, no credit used)"

    # Meta API is the primary explanation path whenever a key is set;
    # without a key this is skipped explicitly (never silently) and the
    # local template is used. The verdict never depends on the model.
    api_key = os.environ.get("META_API_KEY", "").strip()
    model = os.environ.get("META_MODEL", DEFAULT_MODEL)
    usage, cost, api_note = None, None, None
    if api_key:
        model_text, usage, cost = meta_explanation(
            api_key, model, scenario, verdict, violations, notes)
        if model_text:
            explanation = model_text + "\n[설명 출처: Meta Model API, 판정은 Batfish 증거 기준]"
            source = "Meta Model API (%s)" % model
        else:
            api_note = "Meta Model API call failed; fell back to local template."
    else:
        model = None
        api_note = ("Meta Model API explanation skipped: META_API_KEY is not "
                    "set, so the local template is used. Set META_API_KEY "
                    "(env var only, never in files) to get a Muse Spark 1.3 "
                    "explanation. A recorded API-style sample is in "
                    "demo-output/playground-samples.md.")
        print(api_note, file=sys.stderr)

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
        "explanation_source": source,
        "model": model,
        "usage": usage,
        "cost_usd_estimate": cost,
        "api_note": api_note,
        "evidence_source": evidence_source,
        "evidence_note": "All data fictional (RFC 5737, AS 64496-64498). "
                         "Batfish raw output is in the .txt report.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ("%s.json" % name)).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = []
    report.append("# NetOps Copilot — %s" % scenario["title"])
    report.append("")
    report.append("**Verdict: %s**" % verdict)
    report.append("")
    report.append(explanation)
    report.append("")
    report.append("## Evidence (Batfish)")
    report.append("")
    for r in routes:
        report.append("- %s %s: %s (base: %s -> change: %s)"
                      % (r["node"], r["prefix"], r["verdict"], r["base"], r["change"]))
    for f in flows:
        report.append("- flow %s -> %s: %s (%s -> %s)"
                      % (f["start"], f["dst_ip"], f["verdict"], f["base"], f["change"]))
    report.append("")
    report.append("---")
    report.append("")
    report.append("### Batfish raw output")
    report.append("")
    report.append("```")
    report.append(raw.rstrip())
    report.append("```")
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
                    help="use canned Batfish impact reports in demo-data/ "
                         "(no Batfish server, Java or venv needed)")
    args = ap.parse_args()
    names = list(SCENARIOS) if args.all else [args.change]
    if not names:
        ap.error("give --change <name> or --all")
    if not args.mock:
        skipped = [n for n in names if SCENARIOS[n].get("mock_only")]
        names = [n for n in names if not SCENARIOS[n].get("mock_only")]
        for n in skipped:
            print("Skipping %s in live mode (mock-only scenario)." % n)
    for name in names:
        run_one(name, mock=args.mock)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
