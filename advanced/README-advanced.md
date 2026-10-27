# NetOps Copilot — ADVANCED lab

> **What is this?** The same idea as the simple demo, on a realistic backbone: 13 nodes, 2 regions, a route reflector.
> **What problem does it solve?** Simple demos cannot show link failures, exit shifts, hijacks, or a reflector outage.
> **What is the verdict?** 8 scenarios: 1 ALLOW, 3 REVIEW, 4 BLOCK. All 8 are live; live and recorded-replay verdicts agree on all 8 (see E5 for the RPKI honest split).

The basic idea (simulate first, judge from evidence, human decides) is in the [simple README](../README.md).
This file only covers what is bigger here.

![Advanced topology](../docs/topology-advanced.png)

## Connections (one per line)

Region A, inside:

- coreA1 — coreA2
- coreA1 — edgeA1, coreA1 — edgeA2
- coreA2 — edgeA1, coreA2 — edgeA2

Region B, inside:

- coreB1 — coreB2
- coreB1 — edgeB1, coreB2 — edgeB1

Between regions:

- coreA1 — coreB1, coreA2 — coreB2

Route reflector (gold lines in the picture):

- rr1 — coreA1, rr1 — coreB1
- iBGP: every core/edge peers ONLY with rr1 (logical sessions, not extra lines)

Outside (AS64496 border to externals):

- edgeA1 — peer1 (AS64497), edgeA1 — transit1 (AS64501)
- edgeA2 — cust1 (AS64498)
- edgeB1 — peer2 (AS64499), edgeB1 — cust2 (AS64500), edgeB1 — cust1 (AS64498, second link)

OSPF areas: area 0 for core and inter-region links, area 10 for Region A edges, area 20 for Region B edges.

## Watched prefixes and flows

| Prefix | Origin AS | Via |
|---|---|---|
| 192.0.2.0/24 (own aggregate) | 64496 | edgeA1 |
| 198.51.100.128/25 (peer1) | 64497 | edgeA1 |
| 198.51.100.192/26 (peer2) | 64499 | edgeB1 |
| 203.0.113.0/24 (cust1) | 64498 | edgeA2 and edgeB1 (dual-homed) |
| 203.0.113.128/25 (cust2) | 64500 | edgeB1 |

Watched flows (6): coreA1→cust1, coreA1→peer1, coreB1→cust2, coreB1→peer2, coreA2→peer2, coreB2→cust1.

## Scenarios

Live and recorded-replay verdicts are identical for all 8 scenarios. RPKI is live via route-map enforcement (see E5).

| Scenario | Change | Verdict | What happened |
|---|---|---|---|
| `link-failure-coreA1-edgeA1` | coreA1–edgeA1 link shutdown | 🟢 ALLOW | BGP routes unchanged, all 6 flows delivered (IGP reroutes via coreA2) |
| `bgp-session-down-peer1` | edgeA1–peer1 session shutdown | 🔴 BLOCK | peer1 prefix lost at 7 nodes, peer1 flow to NO_ROUTE, customers intact |
| `localpref-exit-shift` | LOCAL_PREF 200 for cust1 at edgeB1 | 🟡 REVIEW | cust1 exit shifts edgeA2→edgeB1 at 6 nodes, all flows survive |
| `hijack-customer-prefix` | peer2 announces 203.0.113.0/25 via Null0 | 🔴 BLOCK | Flows to 203.0.113.10 go DELIVERED→NULL_ROUTED |
| `rr-failure` | rr1 interfaces shutdown | 🔴 BLOCK | 29 iBGP routes lost, all 6 flows to NO_ROUTE |
| `blackhole-rtbh-cust2` | edgeB1 /32 Null0 for victim host 203.0.113.130 only | 🟡 REVIEW | Only that host's flow goes DELIVERED→NULL_ROUTED; the cust2 /25 route stays intact, all other flows survive |
| `rpki-invalid-origin` | peer2 announces cust1 203.0.113.0/25 (ROA: 203.0.113.0/24, AS64498, maxLength 24) — live, two runs: control (no route-map) diverts cust1 flows to Null0, protected (edgeB1 route-map) rejects it | 🔴 BLOCK | Invalid origin must be rejected; BLOCK here means rejected, not an outage |
| `aspath-prepend-deprefer` | Prepend AS64496 ×2 to cust1 at edgeA2 | 🟡 REVIEW | Same exit shift as LOCAL_PREF, by a different mechanism, flows survive |

## How to run

```bash
python3 advanced/advanced.py --mock --all   # no Batfish needed, ~1 second

bash ~/workspace/batfish-lab-advanced/start-batfish-advanced.sh   # live, port 9996
python3 advanced/advanced.py --all

python3 -m unittest discover -s tests   # simple + advanced, 33 tests
```

Files here: `advanced.py` (runner), `roas.json` (fictional ROA table for the RPKI check), `demo-data-advanced/*.txt` (verbatim live impact reports; the RPKI file holds both live runs, control + protected),
`demo-output-advanced/*.md` + `*.json` (one per scenario, labelled live or mock honestly).
The Batfish lab itself lives outside the demo repo at `~/workspace/batfish-lab-advanced/` and is not pushed to GitHub;
the demo repo carries the canned reports, so a judge can reproduce every verdict with `--mock` alone.

## Real operations: how an operator uses this

1. Write the change as a config diff / change ticket. 2. Build
the Batfish twin from current production configs (in this demo,
the fictional lab; production configs are never pasted into a
public demo). 3. Define the watched list FIRST — the verdict
only covers the watched scope. 4. Read ALLOW / BLOCK / REVIEW
with the evidence. 5. A human approves or rejects; the tool
never applies a change. 6. After applying, re-run as a
post-check against the new live state. 7. In CI/CD it is a
gate: BLOCK fails the pipeline, REVIEW needs a human sign-off,
ALLOW proceeds. Not automated: pushing configs to routers,
replacing change approval, or covering unwatched prefixes.

## Where AI acts (short version)

Exactly three places, nowhere else. (1) AFTER the verdict, it
explains the evidence in plain language, so review is faster
and less error-prone — the verdict is unchanged. (2) AFTER
the verdict, it proposes a concrete next change (remove the
blocking filter, LOCAL_PREF/prepend instead of dropping, /32
not /25 blackhole, reject an invalid RPKI origin and fix the
ROA), which must be re-simulated before anyone trusts it.
(3) BEFORE the verdict, as an interface (MCP server, Meta
prompt path), it turns a plain-language intent into a
checkable proposal — the verdict still comes only from
Batfish. It never decides the verdict, never edits a router
config, never sees real production configs here, and its
wording can be wrong even when the verdict is right — hence
the evidence section shown alongside it. Cost note, no
time-saving claim: the 11 reports' real model explanations
cost about $0.17 in total (plus about $0.02 for the RPKI
re-run); that shows the step is cheap, not that it replaces
engineering judgement.

## Appendix — Details / honest notes

- **AI role — the model never decides the verdict.** Batfish evidence decides ALLOW / BLOCK / REVIEW by fixed rules. The Meta model only (1) explains the verdict in plain language from the evidence JSON, and (2) proposes a next step or optimisation, which must be re-simulated before anyone trusts it. Each report carries it as "AI explanation / proposed next step (to be re-simulated — NOT the verdict)". The blackhole /32 (keep the drop on one host, never widen to the /25) is the optimisation example. Honest status: the 11 reports now carry real Meta Model API explanations (about $0.17 total, plus about $0.02 for the RPKI re-run); rule-based text is the fallback. The playground samples in the simple demo's `demo-output/playground-samples.md` are additional examples.
- **E1 — NULL_ROUTED is fatal.** A flow diverted to a Null0 counts as broken, like NO_ROUTE or DROP.
- **E2 — Exit shift → REVIEW.** If flows survive but a prefix's exit edge changes, a human must confirm the new exit.
  A next-hop change staying on the same edge is still ALLOW.
- **E4 — Intended blackhole (/32) → REVIEW.** If the scenario declares an intended victim host and every fatal violation is a flow to that /32 host, the drop is the intended mitigation, not an outage: REVIEW. Any non-victim break keeps BLOCK. Why /32, in plain words: a DDoS usually targets one host, so operators blackhole the /32 host route. Blackholing the whole /25 would also kill the customer's innocent hosts on the same prefix, so the /32 minimises collateral. The live proof is the granularity: the victim host flow goes DELIVERED→NULL_ROUTED while the cust2 /25 route at edgeB1 stays `bgp via ip 198.51.100.14`, unchanged, and all other 5 flows survive.
- **E5 — RPKI invalid origin → BLOCK (LIVE via route-map enforcement, honest split).** Batfish does NOT compute an ROV (route origin validation) state: a Cisco-style RPKI server stanza parsed OK but produced no validation state and no impact, so Batfish itself is never claimed to have validated anything. The validation DECISION comes from the fictional ROA table (203.0.113.0/24 → AS64498, maxLength 24); the ENFORCEMENT is a real inbound route-map on edgeB1. peer2 (AS64499) announces the more-specific 203.0.113.0/25: invalid on two counts — origin AS64499 ≠ ROA AS64498, and /25 exceeds maxLength 24. Two live runs prove it: control (announcement only) diverts cust1 flows to peer2's Null0 → BLOCK (the announcement must be rejected); protected (announcement + route-map) has 0 items affected, the legitimate /24 via cust1 stays, all flows delivered → enforcement works. An exact /24 announcement from peer2 was tested first and never becomes best at edgeB1 (the legitimate direct cust1 route wins), so it is unobservable in the RIB; the more-specific is the live-observable invalid case. BLOCK here means the announcement must be rejected, not that an outage occurred. A legitimate announcement via the ROA AS does not fire.
- **E3 — Hijack announcement → BLOCK (proxy).** A customer prefix arriving as a direct eBGP route via a peer IP is a BLOCK violation.
  Batfish's routes query returns no AS_PATH, so the direct peer next-hop is the documented proxy (peer1 .2, peer2 .10, transit .22).
  E3 is unit-tested synthetically; it did not fire in the live /25 hijack, which E1 blocks instead.
- **Hijack /24 → /25.** The exact /24 announcement was tested twice in Batfish (Loopback, then Null0 static route).
  The legitimate cust1 path was kept every time, so nothing changed. The scenario was redesigned to the classic
  more-specific /25 hijack, which actually diverts traffic. The /24 result is recorded here, not hidden.
- **Link failure shows no BGP change.** IGP reroutes via coreA2, but BGP next-hop IPs do not change.
  ALLOW is the correct verdict for the watched BGP scope, not a claim that the IGP path never changed.
- **Batfish lowercases node names** (corea1, edgeb1) in its output. The policy matches on next-hop IPs, not on name case.
- **Advanced service reuses the simple lab's Batfish runtime** (JRE + jar, not copied, own containers dir, same port 9996).
  Stop the simple service before starting the advanced one.
- **Cust1 is dual-homed** (edgeA2 + edgeB1) so LOCAL_PREF and prepend exit shifts have a second exit to move to.
  Without a second exit, neither mechanism can move the exit at all.
