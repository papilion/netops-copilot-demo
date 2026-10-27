# NetOps Copilot — ADVANCED lab

The simple demo (5 nodes, 3 prefixes) proves the ALLOW/BLOCK/REVIEW
idea. This advanced lab proves it survives a realistic backbone:
two regions, a route reflector, OSPF areas, dual-homed customers,
two peers and a transit upstream — all fictional sample data.

The simple demo is NOT replaced. Run it with
`python3 copilot.py --mock --all` from the demo root.

## Topology (ASCII)

```
Region A (area 10 edges)                 Region B (area 20 edges)
  coreA1 ---- coreA2                       coreB1 ---- coreB2
   | \        / |                           | \        / |
   |  edgeA1  edgeA2  (cust1 dual-homed)     |  edgeB1 (peer2, cust1, cust2)
   |   | peer1, transit1                     |
   +--- coreA1-coreB1, coreA2-coreB2 ------+
   rr1 (route reflector, AS64496) -- coreA1, coreB1
```

iBGP: every core/edge peers ONLY with rr1 (no full mesh).
OSPF: area 0 = core links, inter-region links, rr1 links;
area 10 = Region A core-edge links; area 20 = Region B core-edge links.
eBGP: peer1 (AS64497) via edgeA1, transit1 (AS64501) via edgeA1,
cust1 (AS64498) via edgeA2 AND edgeB1, peer2 (AS64499) via edgeB1,
cust2 (AS64500) via edgeB1.

## Nodes and watched prefixes

| Node | AS | Role |
|---|---|---|
| coreA1, coreA2, coreB1, coreB2 | 64496 | core |
| edgeA1, edgeA2, edgeB1 | 64496 | border |
| rr1 | 64496 | route reflector (iBGP only) |
| peer1, peer2, transit1 | 64497, 64499, 64501 | upstreams |
| cust1, cust2 | 64498, 64500 | customers |

| Watched prefix | Origin AS | Via |
|---|---|---|
| 192.0.2.0/24 (own aggregate) | 64496 | edgeA1 (static Null0) |
| 198.51.100.128/25 (peer1) | 64497 | edgeA1 |
| 198.51.100.192/26 (peer2) | 64499 | edgeB1 |
| 203.0.113.0/24 (cust1) | 64498 | edgeA2 and edgeB1 (dual-homed) |
| 203.0.113.128/25 (cust2) | 64500 | edgeB1 |

Watched flows (6): coreA1->203.0.113.10, coreA1->198.51.100.130,
coreB1->203.0.113.130, coreB1->198.51.100.200,
coreA2->198.51.100.200, coreB2->203.0.113.10.
Batfish lowercases node names (corea1, edgeb1, …) in its output;
the policy code matches on next-hop IPs, not on node-name case.

## Scenarios — intended vs live vs mock

All six were run live in Batfish first, then canned verbatim into
`demo-data-advanced/`. Mock verdicts equal live verdicts for all six.

| Scenario | Change | Live | Mock | What happened |
|---|---|---|---|---|
| link-failure-coreA1-edgeA1 | shutdown coreA1-edgeA1 link (both sides) | ALLOW | ALLOW | BGP routes unchanged, all 6 flows delivered (IGP reroutes via coreA2; the BGP table is the watched scope, so this is ALLOW, not a claim that forwarding never changed) |
| bgp-session-down-peer1 | neighbor shutdown edgeA1-peer1 | BLOCK | BLOCK | peer1 prefix lost at 7 nodes, flow coreA1->198.51.100.130 to NO_ROUTE; customers intact |
| localpref-exit-shift | LOCAL_PREF 200 for cust1 at edgeB1 | REVIEW | REVIEW | cust1 exit shifts edgeA2->edgeB1 at 6 nodes, all flows survive (see E2) |
| hijack-customer-prefix | peer2 announces 203.0.113.0/25 via Null0 | BLOCK | BLOCK | /24 routes unchanged, but flows to 203.0.113.10 go DELIVERED->NULL_ROUTED (see deviation note) |
| rr-failure | shutdown rr1 interfaces | BLOCK | BLOCK | 29 iBGP routes lost, all 6 flows to NO_ROUTE |
| aspath-prepend-deprefer | prepend AS64496 x2 to cust1 at edgeA2 | REVIEW | REVIEW | same exit shift as localpref, via a different mechanism; flows survive |

## Policy extensions (advanced only)

The simple policy runs first; then:

- **E1 — NULL_ROUTED is fatal.** The simple policy treats
  DENIED/NO_ROUTE/DROP as fatal. The advanced policy adds NULL_ROUTED:
  a flow diverted to a Null0 (more-specific hijack) is broken, even
  though the /24 route table looks unchanged.
- **E2 — Exit shift -> REVIEW.** If the simple policy says ALLOW but
  a watched prefix's exit edge changed (base edge != change edge,
  mapped from next-hop IPs) while all flows survive, the verdict is
  REVIEW, not ALLOW. Moving traffic between regions/edges changes
  latency and capacity and must be confirmed by a human. A next-hop
  change that stays on the same edge is still ALLOW.
- **E3 — Hijack announcement -> BLOCK (proxy, documented).**
  A watched customer prefix whose change route is a direct eBGP route
  via a peer IP (peer1 198.51.100.2, peer2 198.51.100.10, transit
  198.51.100.22) instead of a customer IP is a BLOCK violation.
  Batfish's routes query returns Node/VRF/Network/Next_Hop/Protocol
  only — it exposes NO AS_PATH — so the direct peer next-hop is used
  as the proxy. At the edge that receives the announcement this is
  unambiguous: its direct next-hop for that prefix is either the
  customer or the peer, never both. E3 is unit-tested synthetically;
  it did not fire in the live /25 hijack (see deviation note), which
  is BLOCKed by E1 instead.

## Deviations from the original design (honest, not hidden)

1. **Hijack /24 -> /25.** The exact /24 announcement (peer2 announces
   203.0.113.0/24, first via a Loopback1 in that subnet, then via a
   Null0 static route) was tested twice in Batfish: the legitimate
   cust1 best path was kept at every watched node, so the /24
   scenario changed nothing. The scenario was therefore redesigned
   to the classic more-specific hijack: peer2 announces
   203.0.113.0/25 via Null0, which diverts the 203.0.113.10 flows
   to NULL_ROUTED. The /24 test result is recorded here, not hidden.
2. **Link failure shows no BGP change.** Shutting the coreA1-edgeA1
   link reroutes IGP forwarding via coreA2, but BGP next-hop IPs do
   not change, so the watched BGP table is UNCHANGED and the verdict
   is ALLOW. That is the correct verdict for the watched scope; it
   is not a claim that the IGP path did not change.
3. **Advanced service reuses the simple lab's Batfish runtime.**
   `batfish-lab-advanced/start-batfish-advanced.sh` uses the simple
   lab's JRE + jar (2.3 GB, not copied) with its own containers
   directory, on the same port 9996 — so stop the simple service
   before starting the advanced one.
4. **Cust1 is dual-homed** (edgeA2 + edgeB1) so that LOCAL_PREF and
   prepend exit shifts have a second exit to shift to. Without a
   second exit, neither mechanism can move the exit at all.

## How to run

```bash
# Mock (no Batfish needed, ~1 second, verdicts = live verdicts)
cd ~/workspace/hackathon/netops-copilot-demo
python3 advanced/advanced.py --mock --all

# Live (Batfish service on port 9996, advanced lab)
bash ~/workspace/batfish-lab-advanced/start-batfish-advanced.sh
python3 advanced/advanced.py --all

# Tests (simple + advanced, stdlib only, no network)
python3 -m unittest discover -s tests -v
```

Files in this folder: `advanced.py` (policy + runner),
`demo-data-advanced/*.txt` (verbatim live impact reports),
`demo-output-advanced/*.md` + `*.json` (one per scenario, labelled
`batfish-live-advanced` or `mock-advanced` honestly),
`README-advanced.md` (this file), `V3-VIDEO-OUTLINE.md` (video plan,
not yet built). The advanced lab itself lives outside the demo repo
at `~/workspace/batfish-lab-advanced/` (snapshot, watch, changes,
harness, start script) and is not pushed to GitHub with the demo;
the demo repo carries the canned reports and the runner, so a judge
can reproduce every verdict with `--mock` alone.
