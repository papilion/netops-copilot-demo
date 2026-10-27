#!/usr/bin/env python3
"""Batfish change-validation harness (ADVANCED lab, sample data).

Usage:
    python3 validate.py --change ../changes/block-peer-prefix
    python3 validate.py            # base snapshot only (sanity check)

Loads the base snapshot, optionally overlays a proposed change (a folder
whose configs/ replace same-named base configs), and prints an impact
report: for every watched prefix and node, whether the route survives,
changes next-hop, or disappears; for every watched flow, whether the
traceroute disposition changes.

Requires a running Batfish service (see runbook) and pybatfish.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from pybatfish.client.session import Session
from pybatfish.datamodel.flow import HeaderConstraints

LAB = Path(__file__).resolve().parent.parent


def routes_by_node_prefix(bf, nodes, prefixes):
    out = {}
    for prefix in prefixes:
        df = bf.q.routes(nodes=",".join(nodes), network=prefix).answer().frame()
        for _, row in df.iterrows():
            out[(row["Node"], prefix)] = f'{row["Protocol"]} via {row["Next_Hop"]}'
    return out


def flow_dispositions(bf, flows):
    out = {}
    for flow in flows:
        df = (
            bf.q.traceroute(
                startLocation=flow["start_node"],
                headers=HeaderConstraints(dstIps=flow["dst_ip"]),
            )
            .answer()
            .frame()
        )
        disps = sorted({getattr(t.disposition, "name", str(t.disposition)) for t in df["Traces"][0]}) if len(df) else ["NO_TRACES"]
        out[(flow["start_node"], flow["dst_ip"])] = ",".join(disps)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=str(LAB / "snapshot"))
    ap.add_argument("--change", default=None, help="overlay folder with configs/ to replace")
    ap.add_argument("--watch", default=str(LAB / "watch.json"))
    ap.add_argument("--host", default="localhost")
    args = ap.parse_args()

    watch = json.loads(Path(args.watch).read_text())
    nodes, prefixes = watch["nodes"], [p["network"] for p in watch["prefixes"]]
    flows = watch["flows"]

    bf = Session(host=args.host)
    bf.set_network("batfish-lab-advanced-juniper")

    print("== Base snapshot ==")
    bf.init_snapshot(args.snapshot, name="base", overwrite=True)
    parse = bf.q.fileParseStatus().answer().frame()
    bad = parse[parse["Status"] != "PASSED"]
    if len(bad):
        print("PARSE ISSUES:\n", bad.to_string())
    else:
        print(f"All {len(parse)} config files parsed OK.")
    base_routes = routes_by_node_prefix(bf, nodes, prefixes)
    base_flows = flow_dispositions(bf, flows)
    for (node, prefix), route in sorted(base_routes.items()):
        print(f"  {node:7s} {prefix:18s} {route}")
    for key, disp in sorted(base_flows.items()):
        print(f"  flow {key[0]} -> {key[1]}: {disp}")

    if not args.change:
        print("\nNo change overlay given; base sanity check only.")
        return 0

    print(f"\n== Proposed change: {Path(args.change).name} ==")
    merged = Path(tempfile.mkdtemp(prefix="batfish-change-"))
    shutil.copytree(args.snapshot, merged, dirs_exist_ok=True)
    shutil.copytree(Path(args.change) / "configs", merged / "configs", dirs_exist_ok=True)
    bf.init_snapshot(str(merged), name="change", overwrite=True)
    ch_routes = routes_by_node_prefix(bf, nodes, prefixes)
    ch_flows = flow_dispositions(bf, flows)

    print("\n== Impact report ==")
    problems = 0
    for key in sorted(set(base_routes) | set(ch_routes)):
        b, c = base_routes.get(key), ch_routes.get(key)
        if b == c:
            verdict = "UNCHANGED"
        elif b and not c:
            verdict = "ROUTE LOST"
            problems += 1
        elif c and not b:
            verdict = "ROUTE ADDED"
        else:
            verdict = "NEXT-HOP CHANGED"
        print(f"  {key[0]:7s} {key[1]:18s} {verdict:16s} base[{b}] -> change[{c}]")
    for key in sorted(set(base_flows) | set(ch_flows)):
        b, c = base_flows.get(key), ch_flows.get(key)
        verdict = "UNCHANGED" if b == c else "FLOW IMPACT"
        if b != c:
            problems += 1
        print(f"  flow {key[0]} -> {key[1]}: {verdict} ({b} -> {c})")
    print(f"\nSummary: {problems} watched item(s) affected by the proposed change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
