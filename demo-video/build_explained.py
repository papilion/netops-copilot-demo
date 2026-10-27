#!/usr/bin/env python3
"""Build explained videos: intent -> diagram -> test intent -> verdicts.
Rendered frames (no display capture on this VM). Terminal slides are
MOCK RUN with live-matching verdicts, verbatim highlights only."""
import sys
sys.path.insert(0, str(__file__.rsplit('/', 1)[0]))
from pathlib import Path
from build_en import slide, terminal, image_frame, sections, highlight, assemble, GREEN, RED, YELLOW

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MOCK = "MOCK RUN — same verdicts as live Batfish run (rendered terminal, not a screen recording)"

def main():
    only_advanced = "advanced" in sys.argv
    simple = sections((HERE / "simple-mock-en-stdout.txt").read_text(encoding="utf-8"))
    adv = sections((HERE / "advanced-mock-en-stdout.txt").read_text(encoding="utf-8"))
    assert len(simple) == 3 and len(adv) == 8, [s[0] for s in adv]

    # ---- Simple explained (skipped with `advanced` arg; that video is unchanged) ----
    if only_advanced:
        s = None
    else:
        s = [
        (slide("Why was this made?", [
            "A wrong BGP or OSPF change can stop traffic in seconds.",
            "Today operators check it by hand — slow, and easy to miss.",
            "So: try the change in a virtual copy first, then decide.",
        ]), 18),
        (slide("Think of roads and traffic lights", [
            "Router = intersection. Prefix = neighbourhood.",
            "BGP = road sign. OSPF = map inside our network.",
            "GREEN = all watched roads work. RED = a road is broken.",
            "YELLOW = new road or new exit — a human must confirm.",
        ]), 18),
        (image_frame(ROOT / "docs" / "topology-simple.png",
                      "Simple diagram — 5 nodes: cores left, edge centre, peer and customer right"), 22),
        (slide("Diagram, in plain words", [
            "core1, core2: backbone intersections (AS64496).",
            "edge1: the gate to the outside world.",
            "peer1 (AS64497): a neighbour. cust1 (AS64498): a customer.",
            "We watch 3 prefixes and 2 journeys: our own, the peer's, the customer's.",
        ]), 20),
        (slide("What is a test here?", [
            "Propose a change. Simulate it. Compare before and after.",
            "PASS = the verdict matches the real simulated impact.",
            "FAIL = green when traffic breaks, or red when nothing breaks.",
            "The tool never applies a change. A human decides.",
        ]), 18),
        (terminal(f"$ python3 copilot.py --mock --all  |  {MOCK}", simple[0]), 14),
        (terminal(f"$ python3 copilot.py --mock --all  |  {MOCK}", simple[1]), 16),
        (terminal(f"$ python3 copilot.py --mock --all  |  {MOCK}", simple[2]), 14),
        (slide("Conclusion", [
            "Safe change passes. Breaking change is stopped.",
            "New announcement waits for a human.",
            "All data is fictional (RFC 5737, AS 64496-64498).",
        ], badge="GREEN  •  YELLOW  •  RED", badge_col=YELLOW), 16),
        ]
    if not only_advanced:
        assemble(s, HERE / "explained_simple_frames", "netops-copilot-demo-simple-explained-en.mp4")

    # ---- Advanced explained ----
    topo = image_frame(ROOT / "docs" / "topology-advanced.png",
                       "Advanced diagram — Region A left, Region B right, rr1 gold on top")
    a = [
        (slide("Why was this made? — bigger roads", [
            "The simple demo proves the idea on 5 nodes.",
            "Real backbones have regions, reflectors, and many neighbours.",
            "So: the same traffic light, on a 13-node backbone.",
        ]), 10),
        (topo, 16),
        (slide("Diagram, in plain words", [
            "Region A: coreA1, coreA2, edgeA1, edgeA2.",
            "Region B: coreB1, coreB2, edgeB1. Two roads join the regions.",
            "rr1: central post office for BGP routes. No full mesh.",
            "cust1 has two gates (edgeA2 + edgeB1) — so its exit can move.",
        ]), 14),
        (slide("What is a test here?", [
            "Same rule as the simple demo: propose, simulate, compare.",
            "We watch 5 prefixes and 6 journeys, including cross-region ones.",
            "8 tests now: the 6 above, plus a /32 blackhole and an RPKI check.",
        ]), 10),
    ]
    # All 8 advanced scenarios, highlights, in scenario order:
    # link, session, localpref, hijack, rr, blackhole, rpki, prepend.
    adv_durs = [9, 12, 10, 12, 12, 13, 13, 10]
    for idx, dur in zip(range(8), adv_durs):
        hl, footer = highlight(adv[idx])
        if idx == 6:  # RPKI: recorded replay only, never labelled as live.
            header = ("$ python3 advanced/advanced.py --mock --all | "
                      "RECORDED REPLAY — RPKI has no live run (rendered)")
        else:
            header = ("$ python3 advanced/advanced.py --mock --all | "
                      "MOCK RUN — verdicts match live (rendered)")
        a.append((terminal(header, hl, footer=footer), dur))
    a.append((slide("Conclusion", [
        "Same policy, bigger topology: safe passes, broken stops,",
        "new exit waits for a human — even at 13 nodes.",
        "A /32 blackhole drops one host, not a whole prefix.",
        "All data is fictional (RFC 5737, AS 64496-64501).",
    ], badge="GREEN  •  YELLOW  •  RED", badge_col=YELLOW), 10))
    assemble(a, HERE / "explained_adv_frames", "netops-copilot-demo-advanced-explained-en.mp4")

if __name__ == "__main__":
    main()
