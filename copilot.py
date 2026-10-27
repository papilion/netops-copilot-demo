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


# Vendor lab folders (same topology, IPs, ASNs and policies; only the
# config syntax differs). Cisco is the original; Arista EOS and Juniper
# Junos variants were translated and verified to give identical Batfish
# verdicts for all 11 scenarios (see labs/ README note in web/README.md).
VENDORS = {
    "cisco": "batfish-lab",
    "arista": "batfish-lab-arista",
    "juniper": "batfish-lab-juniper",
}


def _resolve_lab(vendor="cisco"):
    """Lab folder: env override, else labs/ in this repo, else legacy path.

    A clone (e.g. a GitHub Codespace) contains labs/batfish-lab, so live
    runs work without the old ~/workspace layout. The legacy path stays
    as a fallback for the original development machine. The env override
    applies to Cisco only; vendor labs always come from labs/ in the repo.
    """
    if vendor not in VENDORS:
        raise ValueError("Unknown vendor: %s (cisco, arista, juniper)" % vendor)
    if vendor == "cisco":
        env = os.environ.get("NETOPS_SIMPLE_LAB")
        if env:
            return Path(env)
    repo_lab = HERE / "labs" / VENDORS[vendor]
    if (repo_lab / "snapshot").exists():
        return repo_lab
    if vendor == "cisco":
        return Path.home() / "workspace" / "batfish-lab"
    raise RuntimeError("Vendor lab not found: %s" % repo_lab)


def _python_with_pybatfish(lab):
    # Lab venv first, then the original dev machine's venv, then the
    # current interpreter (a Codespace installs pybatfish system-wide).
    candidates = [
        lab / "venv" / "bin" / "python",
        Path.home() / "workspace" / "batfish-lab" / "venv" / "bin" / "python",
        Path(sys.executable),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


LAB = _resolve_lab()
VALIDATE = LAB / "harness" / "validate.py"
LAB_VENV_PYTHON = _python_with_pybatfish(LAB)
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


def run_batfish(change_dir, vendor="cisco"):
    """Run validate.py and return its stdout.

    For a non-Cisco vendor the change overlay is re-based onto that
    vendor's lab (same change name, same node filenames), so the Cisco
    SCENARIOS table needs no per-vendor copy.
    """
    if vendor == "cisco":
        validate, venv_python = VALIDATE, LAB_VENV_PYTHON
        change = Path(change_dir)
    else:
        lab = _resolve_lab(vendor)
        validate = lab / "harness" / "validate.py"
        venv_python = _python_with_pybatfish(lab)
        change = lab / "changes" / Path(change_dir).name
    cmd = [str(venv_python), str(validate), "--change", str(change)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            "Batfish harness failed.\nSTDOUT:\n%s\nSTDERR:\n%s"
            % (proc.stdout, proc.stderr)
        )
    return proc.stdout


MOCK_DIRS = {
    "cisco": DATA_DIR,
    "arista": HERE / "demo-data-arista",
    "juniper": HERE / "demo-data-juniper",
}


def run_mock(name, vendor="cisco"):
    """Return the canned Batfish impact report for a scenario.

    The ospf/block files are the verbatim impact reports from the
    recorded live runs (demo-output/*.md, Batfish raw output section);
    parsing them must give the same verdicts as the live runs. The
    add-customer-prefix file is mock-verified only (see SCENARIOS) and
    is a verbatim Cisco copy in every vendor directory. Vendor
    directories hold live-captured reports from that vendor's lab,
    except add-customer-prefix (no live overlay exists for any vendor).
    """
    if vendor not in MOCK_DIRS:
        raise ValueError("Unknown vendor: %s (cisco, arista, juniper)" % vendor)
    if vendor == "cisco":
        mock_file = SCENARIOS[name]["mock_file"]
    else:
        mock_file = MOCK_DIRS[vendor] / ("%s.txt" % name)
    return mock_file.read_text(encoding="utf-8")


def build_meta_prompt(scenario, verdict, violations, notes, lang="ko"):
    """Build the Meta Model API prompt from Batfish evidence only.

    lang="ko" (default, backward compatible) asks for a Korean briefing;
    lang="en" asks for an English briefing. The verdict and evidence are
    identical in both languages; only the explanation language changes.
    """
    evidence = {
        "change": scenario["title"],
        "intent": scenario["intent"],
        "verdict_from_batfish": verdict,
        "violations": violations,
        "notes": notes,
    }
    lang_word = "Korean" if lang == "ko" else "English"
    return (
        "You are a network operations assistant. Rewrite the following "
        "Batfish simulation result as a short plain-language briefing "
        "for a network engineer (max 5 sentences, %s). Do NOT invent "
        "routes, prefixes, or flows beyond the evidence. Keep the verdict "
        "exactly as given.\n\nEvidence (JSON):\n%s"
        % (lang_word, json.dumps(evidence, ensure_ascii=False))
    )


def build_meta_proposal_prompt(scenario, verdict, violations, notes, proposal,
                               lang="ko"):
    """Prompt asking the model to REFINE a rule-based proposal, never to
    decide the verdict. The verdict and evidence are fixed inputs; the
    model only rewords the proposal in plain language (max 3 sentences).
    Used only when META_API_KEY is set; without a key the rule-based
    proposal from propose_next_step() is used as-is."""
    lang_word = "Korean" if lang == "ko" else "English"
    evidence = {
        "change": scenario["title"],
        "intent": scenario["intent"],
        "verdict_from_batfish": verdict,
        "violations": violations,
        "notes": notes,
        "rule_based_proposal": proposal,
    }
    return (
        "You are a network operations assistant. Rewrite the rule-based "
        "proposal below as a short plain-language suggestion for a network "
        "engineer (max 3 sentences, %s). Do NOT change the verdict, do NOT "
        "invent routes, prefixes, or flows beyond the evidence, and keep "
        "the warning that the proposal must be simulated before trusting "
        "it.\n\nEvidence (JSON):\n%s"
        % (lang_word, json.dumps(evidence, ensure_ascii=False))
    )


def propose_next_step(verdict, violations, notes, lang="ko"):
    """Rule-based proposal for the NEXT step — deterministic, no model call.

    Architecture rule: this proposal NEVER decides the verdict. The
    verdict comes from Batfish evidence only (apply_policy). This helper
    only suggests what to try next, and every proposal must be
    re-simulated before anyone trusts it. It exists even without a
    META_API_KEY; when a key is set, copilot.run_one may ask the Meta
    model to reword it (build_meta_proposal_prompt), falling back to
    this text on any failure.
    """
    joined = " ".join(violations) + " " + " ".join(notes)
    if lang == "en":
        head = ("AI explanation / proposed next step (to be re-simulated "
                "— NOT the verdict): ")
        tail = (" Simulate this proposal too, before trusting it.")
        if verdict == "ALLOW":
            body = ("No watched route was lost and no watched flow broke, "
                    "so this change is safe within the watched scope. "
                    "Apply it as proposed, then re-check after applying.")
        elif verdict == "BLOCK":
            if "RPKI" in joined:
                body = ("Reject the invalid announcement and check or fix "
                        "the ROA so only the legitimate AS may announce "
                        "the prefix. Then re-simulate the legitimate "
                        "announcement and confirm it is ALLOW.")
            elif "Hijack" in joined:
                body = ("Reject the announcement from the peer — do not "
                        "accept a customer prefix via a peer next-hop — "
                        "and confirm the legitimate customer path. Then "
                        "re-simulate.")
            elif "route LOST" in joined:
                body = ("Remove or fix the change that lost the route "
                        "(for example, remove the blocking filter or "
                        "restore the session) and re-simulate before "
                        "applying anything else.")
            else:
                body = ("Instead of dropping traffic, move it with "
                        "LOCAL_PREF or AS_PATH prepend — traffic "
                        "engineering that keeps flows alive — and "
                        "re-simulate that alternative.")
        else:  # REVIEW
            body = ("Ask a human to confirm the intent first: is the new "
                    "route or exit exactly what was intended, and can "
                    "the new exit handle the traffic (capacity and "
                    "latency)? Only apply after confirmation, then "
                    "re-simulate.")
        return head + body + tail
    head = ("AI 설명 / 제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 "
            "아닙니다): ")
    tail = " 이 제안도 믿기 전에 시뮬레이션하세요."
    if verdict == "ALLOW":
        body = ("감시 대상 경로가 사라지지 않았고 감시 대상 flow도 "
                "깨지지 않았으므로, 감시 범위 내에서는 안전한 변경입니다. "
                "제안대로 적용한 뒤, 적용 후 다시 확인하세요.")
    elif verdict == "BLOCK":
        if "RPKI" in joined:
            body = ("유효하지 않은 발표를 거부하고, 정당한 AS만 해당 "
                    "prefix를 발표할 수 있도록 ROA를 확인하거나 "
                    "수정하세요. 그다음 정당한 발표를 다시 시뮬레이션해서 "
                    "ALLOW인지 확인하세요.")
        elif "Hijack" in joined:
            body = ("peer를 통한 발표는 거부하세요. 고객 prefix를 peer "
                    "next-hop으로 받아들이면 안 됩니다. 정당한 고객 "
                    "경로를 확인한 뒤 다시 시뮬레이션하세요.")
        elif "route LOST" in joined:
            body = ("경로를 사라지게 한 변경을 제거하거나 수정하세요 "
                    "(예: 차단 필터 제거, 세션 복원). 다른 것을 적용하기 "
                    "전에 다시 시뮬레이션하세요.")
        else:
            body = ("트래픽을 끊는 대신 LOCAL_PREF나 AS_PATH prepend로 "
                    "옮기세요. flow를 살리는 트래픽 엔지니어링입니다. "
                    "그 대안을 다시 시뮬레이션하세요.")
    else:  # REVIEW
        body = ("먼저 사람이 의도를 확인하세요. 새 경로 또는 출구가 "
                "정말 의도한 것이 맞는지, 새 출구가 트래픽을 감당할 수 "
                "있는지(용량과 지연) 확인하세요. 확인한 뒤에만 적용하고, "
                "다시 시뮬레이션하세요.")
    return head + body + tail


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


CLI_DISCLAIMER = (
    "CLI-style view — Batfish evidence rendered like router output. "
    "NOT actual device output: no router was connected and no command "
    "was run on a device. Admin distance and metric are not reported "
    "by Batfish, so they are omitted here (shown as nothing, never "
    "invented). Interface names, uptime and BGP session state are "
    "likewise not reported and are never shown."
)


def _cli_protocol(route_text):
    """Protocol code from a Batfish route string, or '?' if unknown."""
    text = (route_text or "").strip()
    if text.startswith("ibgp "):
        return "i"
    if text.startswith("bgp "):
        return "B"
    if text.startswith("static "):
        return "S"
    return "?"


def _cli_via(route_text):
    """Next-hop from a Batfish route string, using only reported fields."""
    text = route_text or ""
    m = re.search(r"via ip (\S+)", text)
    if m:
        return m.group(1)
    if "via discard" in text:
        return "discard"
    return "—"


def render_cli(routes, flows, label=None):
    """Render Batfish evidence in Cisco-style CLI form.

    Uses ONLY fields Batfish actually reports (node, prefix, route
    verdict, base/change route strings, flow start/destination and
    base/change dispositions). Changed watched routes only are shown;
    UNCHANGED routes are omitted and said so, because a full RIB dump
    would bury the change. Flows have no hop list in the evidence, so
    they are rendered as a traceroute-style result line, not as hops.
    The disclaimer is part of the output: this is Batfish evidence in
    CLI form, never output captured from a real router.
    """
    lines = []
    if label:
        lines.append(label)
    lines.append(CLI_DISCLAIMER)
    lines.append("")
    lines.append("Routes (changed watched routes only; "
                 "UNCHANGED routes omitted):")
    changed = [r for r in routes if r["verdict"] != "UNCHANGED"]
    if not changed:
        lines.append("  (no watched route changed)")
    for r in changed:
        # For a lost route the change string is "None"; use the base
        # string so the code still reflects the route that was lost.
        # The node is part of every line: a "show ip route" output
        # belongs to one device, and without the node the same prefix
        # would appear twice with no way to tell core1 from core2.
        src = r["change"] if r["change"] not in (None, "None") else r["base"]
        code = _cli_protocol(src)
        if r["verdict"] == "ROUTE LOST":
            lines.append("  %s: %s %s — route LOST (was: %s)"
                         % (r["node"], code, r["prefix"], r["base"]))
        elif r["verdict"] == "ROUTE ADDED":
            lines.append("  %s: %s %s via %s — route ADDED"
                         % (r["node"], code, r["prefix"], _cli_via(src)))
        else:
            lines.append("  %s: %s %s via %s — %s (was: %s)"
                         % (r["node"], code, r["prefix"], _cli_via(src),
                            r["verdict"], r["base"]))
    lines.append("")
    lines.append("Flows (traceroute-style result; no hop list reported):")
    if not flows:
        lines.append("  (no watched flows)")
    for f in flows:
        status = "unchanged" if f["verdict"] == "UNCHANGED" else "CHANGED"
        lines.append("  %s -> %s: %s -> %s (%s)"
                     % (f["start"], f["dst_ip"], f["base"], f["change"],
                        status))
    return "\n".join(lines)


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


def local_explanation(scenario, verdict, violations, notes, routes, flows,
                      lang="ko"):
    """Deterministic explanation from evidence only (no model call).

    lang="ko" (default, backward compatible) produces the original Korean
    text; lang="en" produces the same content in English. Verdicts,
    violations, notes and affected prefixes are identical in both.
    """
    affected = sorted({r["prefix"] for r in routes if r["verdict"] != "UNCHANGED"})
    lines = []
    if lang == "en":
        lines.append("Intent: %s" % scenario["intent"])
        if verdict == "ALLOW":
            lines.append(
                "Verdict: Safe to apply (within watched scope). No watched "
                "prefix route was lost and all watched flows were preserved. "
                "The verdict covers watched items only; it does not guarantee "
                "forwarding changes outside the watched set."
            )
        elif verdict == "BLOCK":
            lines.append(
                "Verdict: Do not apply. Because of the impact below, do not "
                "apply this to production unless the impact exactly matches "
                "the intent."
            )
        else:
            lines.append("Verdict: Review required. Check the changes below "
                         "before deciding whether to apply.")
        for v in violations:
            lines.append("- Violation: %s" % v)
        for n in notes:
            lines.append("- Note: %s" % n)
        if affected:
            lines.append("Affected prefixes: %s" % ", ".join(affected))
        else:
            lines.append("Affected prefixes: none")
        return "\n".join(lines)
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


def meta_explanation(api_key, model, scenario, verdict, violations, notes,
                     lang="ko", prompt_fn=None, proposal=None):
    """Ask Meta Model API to rewrite the explanation from the same evidence.

    Returns (text_or_None, usage_or_None, cost_or_None). On any failure
    the caller falls back to the local explanation — the verdict itself
    never depends on this call. With prompt_fn=build_meta_proposal_prompt
    and proposal set, it instead refines a rule-based proposal (the
    verdict still comes from Batfish, never from the model).
    """
    if prompt_fn is None:
        prompt = build_meta_prompt(scenario, verdict, violations, notes, lang)
    else:
        prompt = prompt_fn(scenario, verdict, violations, notes, proposal, lang)
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        # 2026-10-27 live test: Muse Spark 1.3 spends ~965 tokens on
        # reasoning before answering, so 400 produced an empty reply
        # (finish_reason "length"). 2000 worked for most scenarios, but
        # bgp-session-down and aspath-prepend truncated mid-sentence
        # (reasoning ~1,850-2,190 tokens), so 3000 is the safe budget.
        "max_tokens": 3000,
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


def run_one(name, mock=False, lang="ko", vendor="cisco"):
    scenario = SCENARIOS[name]
    print("== %s ==" % scenario["title"])
    if mock:
        raw = run_mock(name, vendor=vendor)
        evidence_source = ("mock (canned Batfish impact report in %s/)"
                           % MOCK_DIRS[vendor].name)
    else:
        if scenario.get("mock_only"):
            print("Skipping %s: mock-only scenario, no live Batfish overlay." % name)
            return None
        raw = run_batfish(scenario["change_dir"], vendor=vendor)
        evidence_source = "batfish-live"
    routes, flows = parse_impact(raw)
    verdict, violations, notes = apply_policy(routes, flows)
    explanation = local_explanation(scenario, verdict, violations, notes,
                                    routes, flows, lang)
    source = "local-template (no API call, no credit used)"

    # Meta API is the primary explanation path whenever a key is set;
    # without a key this is skipped explicitly (never silently) and the
    # local template is used. The verdict never depends on the model.
    api_key = os.environ.get("META_API_KEY", "").strip()
    model = os.environ.get("META_MODEL", DEFAULT_MODEL)
    usage, cost, api_note = None, None, None
    if api_key:
        model_text, usage, cost = meta_explanation(
            api_key, model, scenario, verdict, violations, notes, lang)
        if model_text:
            if lang == "en":
                explanation = (model_text + "\n[Explanation source: Meta Model "
                               "API, verdict is based on Batfish evidence]")
            else:
                explanation = model_text + "\n[설명 출처: Meta Model API, 판정은 Batfish 증거 기준]"
            source = "Meta Model API (%s)" % model
        else:
            api_note = "Meta Model API call failed; fell back to local template."
    else:
        model = None
        if lang == "en":
            api_note = ("Meta Model API explanation skipped: META_API_KEY is not "
                        "set, so the local template is used. Set META_API_KEY "
                        "(env var only, never in files) to get a Muse Spark 1.3 "
                        "explanation. A recorded API-style sample is in "
                        "demo-output/playground-samples.md.")
        else:
            api_note = ("Meta Model API explanation skipped: META_API_KEY is not "
                        "set, so the local template is used. Set META_API_KEY "
                        "(env var only, never in files) to get a Muse Spark 1.3 "
                        "explanation. A recorded API-style sample is in "
                        "demo-output/playground-samples.md.")
        print(api_note, file=sys.stderr)

    # Proposed next step: rule-based by default; when a key is set, the
    # model may reword it, but the verdict never comes from the model.
    # The proposal is a suggestion only — it must be re-simulated.
    proposal = propose_next_step(verdict, violations, notes, lang)
    proposal_source = "rule-based (no API call)"
    if api_key:
        refined, _, _ = meta_explanation(
            api_key, model, scenario, verdict, violations, notes, lang,
            prompt_fn=build_meta_proposal_prompt, proposal=proposal)
        if refined:
            proposal = refined
            proposal_source = "Meta Model API (refined from rule-based proposal)"

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
        "proposed_next_step": proposal,
        "proposed_next_step_source": proposal_source,
        "explanation_source": source,
        "model": model,
        "usage": usage,
        "cost_usd_estimate": cost,
        "api_note": api_note,
        "evidence_source": evidence_source,
        "evidence_note": "All data fictional (RFC 5737, AS 64496-64498). "
                         "Batfish raw output is in the .txt report.",
        "cli_view": render_cli(routes, flows),
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
    report.append("## AI explanation / proposed next step "
                  "(to be re-simulated — NOT the verdict)")
    report.append("")
    report.append(proposal)
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
    report.append("## CLI-style view (Batfish evidence rendered like "
                  "router output — NOT actual device output)")
    report.append("")
    report.append("```")
    report.append(render_cli(routes, flows))
    report.append("```")
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
    ap.add_argument("--lang", choices=["ko", "en"], default="ko",
                    help="explanation language: ko (default, original) or en")
    ap.add_argument("--vendor", choices=["cisco", "arista", "juniper"],
                    default="cisco",
                    help="lab vendor for live and recorded runs (default cisco)")
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
        run_one(name, mock=args.mock, lang=args.lang, vendor=args.vendor)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
