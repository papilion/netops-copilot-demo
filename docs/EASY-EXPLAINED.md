# NetOps Copilot, Explained Simply — for Judges

> Read this first. It takes under 10 minutes. It explains the pictures,
> why this project exists, and what every test is trying to prove —
> in plain language. The code and the full reports are in the repo;
> this page is the guide to them.

**Plain words used here.** A *router* is an intersection that forwards
traffic. A *prefix* is a block of addresses, like one neighbourhood.
*BGP* is the system that tells other networks which way to reach a
prefix — think road signs between cities. *OSPF* is the map inside
one network — think the street map inside one city. A *flow* is one
test journey: "can traffic get from here to that address?" A *digital
twin* is a virtual copy of the network, built from config files, so
you can try a change without touching the real network. *Batfish* is
the tool that builds that virtual copy and answers route and flow
questions. *AS* (Autonomous System) is just a network's ID number;
64496 is our backbone, the others are neighbours and customers.
All addresses and AS numbers here are fictional samples
(RFC 5737 documentation space). No real production config is used.

## 1. The idea in 30 seconds: roads and traffic lights

Think of the internet as roads.

- A router is an intersection. A prefix is a neighbourhood.
- BGP is the road sign that says "this neighbourhood is that way."
- OSPF is the map inside our own city.

One wrong road sign can stop traffic in seconds. Until now, operators
checked a change by hand, slowly, before applying it.

This tool does a rehearsal first. It builds the same roads in a
virtual copy (the Batfish digital twin), tries the proposed change
there, and compares "before" and "after" for the roads we watch.
Then it answers with a traffic light:

- 🟢 **GREEN — ALLOW.** Every watched customer and partner road
  still works. Safe to change, within the watched roads only.
- 🔴 **RED — BLOCK.** A watched road is broken. Do not change.
- 🟡 **YELLOW — REVIEW.** A new road appeared, or traffic moved to
  another exit. It may be fine, but a human must confirm it was
  intended. Yellow does not mean "go slowly" — it means "stop and
  ask a human."

The tool never applies a change. A human decides. The verdict always
comes from the simulation evidence, never from a model's guess.
The model (Muse Spark 1.3) only rewrites the evidence into plain
language.

## 2. Why it was made: the operator's real problem

**Before — the manual way.** An engineer wants to change a BGP
filter or an OSPF cost. She reads configs, checks neighbours in her
head, asks a colleague, and hopes she did not miss a customer route.
A mistake is found only after real traffic breaks — or after a
long, careful review that still cannot try every path.

**After — the simulation way.** The same engineer proposes the
change, and the tool answers in under a minute: which watched
prefixes are lost, which test journeys break, which customers are
untouched, and a green, yellow, or red verdict. The review becomes
"check this short list and decide," instead of "imagine every path."

That is the whole creation intent: turn a slow, risky, manual
pre-check into a fast, repeatable, evidence-based pre-check, for
the backbone changes that operators actually fear — filters,
session changes, cost changes, exit changes, and bad announcements.

## 3. Simple diagram explained, node by node

![Simple demo topology](topology-simple.png)

Picture: 5 boxes. On the left, two blue core boxes. In the middle,
one blue border box. On the right, one orange peer box and one
green customer box.

- **core1 and core2 (AS64496, core).** The backbone's middle
  intersections. They do not talk to the outside world directly;
  they pass traffic to the border router.
- **edge1 (AS64496, border).** The gate to the outside. It is the
  only box that talks to a peer and to a customer.
- **peer1 (AS64497, peer).** A neighbouring network that exchanges
  traffic with us. It owns the prefix 198.51.100.128/25.
- **cust1 (AS64498, customer).** A customer network. It owns the
  prefix 203.0.113.0/24.
- **Own aggregate 192.0.2.0/24 (AS64496).** Our own address block,
  announced by edge1. It is there so the test also watches
  something we own, not only other people's prefixes.

**Links, one by one.**

- core1 — core2: internal link, OSPF map.
- core1 — edge1: internal link, OSPF map.
- core2 — edge1: internal link, OSPF map.
- edge1 — peer1: outside link, BGP road sign to the peer.
- edge1 — cust1: outside link, BGP road sign to the customer.
- Inside the backbone, core1, core2, and edge1 also share BGP
  routes with each other (a full mesh: every box talks to every
  other box). That is the simple version; the advanced lab replaces
  it with a route reflector (see Section 4).

**What we watch, and why these three were chosen.**

- 192.0.2.0/24 — our own block. If we break our own announcement,
  we must know.
- 198.51.100.128/25 — the peer's block. If we lose the peer, we
  must know.
- 203.0.113.0/24 — the customer's block. If we break a customer,
  we must know.
- Flow 1: core1 → 203.0.113.10 (can we still reach the customer?).
- Flow 2: core1 → 198.51.100.130 (can we still reach the peer?).

One of each kind — own, peer, customer — is the smallest set that
can tell "did we break ourselves, a partner, or a customer?"
That is why these three were chosen, and no more.

## 4. Advanced diagram explained, region by region

![Advanced topology](topology-advanced.png)

Picture: two big boxes, Region A on the left (blue) and Region B
on the right (green). A gold box, rr1, sits at the top centre.
Orange, green, and purple boxes sit outside the regions.

**Region A (left).** coreA1, coreA2, edgeA1, edgeA2 — all AS64496.
Links inside Region A: coreA1 — coreA2, coreA1 — edgeA1,
coreA1 — edgeA2, coreA2 — edgeA1, coreA2 — edgeA2. Think of it as
one city with two main intersections and two gates.

**Region B (right).** coreB1, coreB2, edgeB1 — all AS64496.
Links inside Region B: coreB1 — coreB2, coreB1 — edgeB1,
coreB2 — edgeB1. A second city, smaller, with one gate.

**Between regions.** coreA1 — coreB1 and coreA2 — coreB2.
Two roads between the cities, so one road can fail and the other
still connects them.

**rr1 (AS64496, route reflector, gold).** In the simple demo,
every backbone box talked BGP to every other box. In a real
backbone that becomes too many conversations. A route reflector
is a central post office: every core and edge box tells BGP routes
to rr1 only, and rr1 passes them on. The gold lines in the picture
are that logical job. If rr1 stops, the boxes stop learning each
other's routes — which is exactly one of the tests below.
*Plain-language note:* rr1 is deliberately a single post office
here, so its failure is a real test. A production network would
normally have a second one; this lab does not, on purpose.

**Outside boxes (externals).**

- peer1 (AS64497) — via edgeA1, owns 198.51.100.128/25.
- transit1 (AS64501) — via edgeA1, a second upstream road.
  It has no watched prefix of its own; it is there so the
  topology has two upstreams, like a real border.
- cust1 (AS64498) — owns 203.0.113.0/24, connected to BOTH
  edgeA2 and edgeB1 (dual-homed: two gates, like a shop with two
  entrances). That second gate is what makes exit-change tests
  possible: traffic can move from one gate to the other.
- peer2 (AS64499) — via edgeB1, owns 198.51.100.192/26.
- cust2 (AS64500) — via edgeB1, owns 203.0.113.128/25.

**What we watch here.** Five prefixes (own 192.0.2.0/24, peer1,
peer2, cust1, cust2) and six flows, including cross-region
journeys (coreA → peer2, coreB → cust1). Cross-region flows matter
because a change in one city must not break a journey that ends
in the other city.

**OSPF areas, in one sentence.** Area 0 is the backbone map
(core and inter-region roads). Area 10 is Region A's edge map.
Area 20 is Region B's edge map. Areas are just chapters of the
internal map, so a change in one chapter does not rewrite the
whole book.

## 5. Test intent: what each test proves

A test here is not "does the code run?" It is "if an operator
proposes this change, does the tool catch the right outcome?"
For every scenario: the change proposed, what we watch, what
PASS looks like, what FAIL looks like, and why an operator cares.
PASS means the tool's verdict matches the real simulated impact.
FAIL would mean it says green when traffic breaks, or red when
nothing breaks — both are bad, in opposite ways.

### Simple demo — 3 tests

**Test 1 — OSPF cost change → ALLOW (green).**
Change: raise the core1 → edge1 internal cost from 10 to 100,
so traffic should go via core2 instead.
Watch: all 3 prefixes, both flows.
Pass (what happened): 0 watched items changed. Routes and flows
all stayed the same. Verdict ALLOW.
Fail would be: the tool blocks a harmless change, and engineers
stop trusting it.
Why an operator cares: many safe changes look scary on paper.
A tool that blocks everything is useless; it must also say
"this one is fine" when it really is fine.

**Test 2 — Peer filter → BLOCK (red).**
Change: at edge1, refuse the peer prefix 198.51.100.128/25
coming from peer1.
Watch: all 3 prefixes, both flows.
Pass (what happened): that prefix is lost at core1, core2, and
edge1; the flow core1 → 198.51.100.130 goes from delivered to
NO_ROUTE (no road at all). The customer prefix is untouched.
Verdict BLOCK.
Fail would be: the tool says green while peer traffic is dead.
Why an operator cares: a filter typo is a classic backbone
accident. This test proves the tool names the blast radius —
which boxes, which prefix, which journey, and which customer
is safe — before anyone applies the filter.

**Test 3 — New customer prefix → REVIEW (yellow).**
Change: a new prefix, 203.0.113.128/25, appears at edge1.
Watch: all 3 prefixes, both flows.
Pass (what happened): nothing old breaks, but one new route
appears. Verdict REVIEW, not ALLOW.
Fail would be: the tool auto-approves a new announcement.
Why an operator cares: a new announcement can be a real new
customer, a typo, or a hijack (someone claiming an address that
is not theirs). Only a human can tell which. The tool's job is
to stop and ask, not to guess.

### Advanced lab — 8 tests

**Test 4 — Link failure → ALLOW (green).**
Change: shut the coreA1 — edgeA1 road, on both sides.
Watch: 5 prefixes, 6 flows.
Pass (what happened): BGP routes unchanged, all 6 flows still
delivered. The internal map reroutes via coreA2.
Fail would be: the tool panics about a reroute that harms
nothing, or misses a flow that actually breaks.
Why an operator cares: links fail in real life. The question is
never "did the map change?" but "did any watched journey break?"
This test proves the tool answers the second question.
*Scope note:* ALLOW here means the watched BGP roads and flows
are fine. It does not claim the internal path never changed —
it did, via coreA2. That is the point of watched scope.

**Test 5 — BGP session down → BLOCK (red).**
Change: shut the edgeA1 — peer1 BGP session (the road sign
conversation stops).
Watch: 5 prefixes, 6 flows.
Pass (what happened): the peer1 prefix is lost at 7 boxes,
the flow coreA1 → 198.51.100.130 breaks, customers stay intact.
Verdict BLOCK.
Fail would be: the tool misses a dead peer, or blames a
customer that is actually fine.
Why an operator cares: a session drop is a common outage.
The operator needs, in one answer: which peer died, where it
is missing, and proof the customers are safe.

**Test 6 — LOCAL_PREF exit shift → REVIEW (yellow).**
Change: raise LOCAL_PREF (a BGP preference number — higher
means "prefer this exit") to 200 for cust1 at edgeB1.
Watch: cust1 prefix, all flows.
Pass (what happened): cust1's exit moves from edgeA2 to edgeB1
at 6 boxes, all flows survive. Verdict REVIEW.
Fail would be: the tool calls it green (a silent exit move
changes latency and capacity) or red (nothing broke).
Why an operator cares: exit moves are deliberate, everyday
traffic engineering — but a silent exit move can overload the
new gate. A human must confirm the new exit on purpose.

**Test 7 — More-specific hijack → BLOCK (red).**
Change: peer2 announces 203.0.113.0/25 — a smaller, more
specific slice of cust1's 203.0.113.0/24 — pointing at a
dead end (Null0, a "throw it away" route).
Watch: cust1 journeys, especially to 203.0.113.10.
Pass (what happened): the /24 table looks unchanged, but the
journeys to 203.0.113.10 go from delivered to NULL_ROUTED
(thrown away). Verdict BLOCK.
Fail would be: the tool looks only at the /24 table, sees
"unchanged," and says green while customer traffic is
diverted. That is why the policy also treats NULL_ROUTED as
fatal — a lesson built into the advanced policy.
Why an operator cares: hijack is the nightmare case. The
attacker does not need to break a route; a more specific
announcement wins by being more precise. This test proves the
tool watches journeys, not just tables.
*Honest lab note:* the exact /24 hijack was tried first, twice,
and Batfish kept the legitimate cust1 path, so it changed
nothing. The classic more-specific /25 version is the one that
actually diverts traffic in this lab, and it is the version
tested here. In the lab, the diversion points at Null0 (a
dead end) as a stand-in; in the real world it could point at
the attacker instead. The verdict — BLOCK — is the same either
way, because the customer journey breaks.

**Test 8 — Route reflector failure → BLOCK (red).**
Change: shut rr1's interfaces (the central post office stops).
Watch: 5 prefixes, 6 flows.
Pass (what happened): 29 internal routes lost, all 6 flows
break. Verdict BLOCK.
Fail would be: the tool under-reports a backbone-wide outage
as a small problem.
Why an operator cares: a reflector is a single point of
failure if it has no backup. This test proves the tool can
tell a local problem from a backbone-wide problem by counting
how much is lost, not just by naming one prefix.

**Test 9 — AS_PATH prepend → REVIEW (yellow).**
Change: add our own AS number twice to cust1's announcement
at edgeA2 (AS_PATH prepend — making the path look longer, so
others prefer the other gate).
Watch: cust1 prefix, all flows.
Pass (what happened): the same exit shift as Test 6, by a
different mechanism; flows survive. Verdict REVIEW.
Fail would be: the tool treats two different mechanisms as
different outcomes when the impact is the same.
Why an operator cares: operators use prepend and LOCAL_PREF
interchangeably to move traffic. A good pre-check judges the
impact (exit moved, flows fine → human confirms), not the
knob that was turned.

**Test 10 — DDoS blackhole, /32 host only → REVIEW (yellow).**
Change: at edgeB1, throw away traffic to one host only,
203.0.113.130/32, with a Null0 ("throw it away") route.
Watch: 5 prefixes, 6 flows — including the cust2 /25 route
that contains that host.
Pass (what happened): only that one journey breaks
(coreB1 → 203.0.113.130, DELIVERED → NULL_ROUTED). The
cust2 /25 route stays exactly as it was at edgeB1, and the
other 5 flows survive. Verdict REVIEW, not BLOCK.
Fail would be: the tool calls an intended mitigation an
outage (BLOCK), or lets a whole-prefix blackhole pass
without noticing the collateral damage.
Why an operator cares, and why /32: a DDoS usually targets
one host, not a whole customer prefix. Blackholing the
whole /25 would also kill the customer's innocent hosts on
the same prefix. Real operators blackhole the /32 to
minimise collateral, and this test proves the tool checks
exactly that granularity — one host drops, the prefix lives.
The REVIEW is the human check: "is 203.0.113.130 really
the intended victim?" before anyone applies it.

**Test 11 — RPKI invalid origin → BLOCK (red).**
Change: peer2 announces cust1's prefix 203.0.113.0/24.
Watch: the ROA (a certificate-like record that says who
may announce a prefix) for that prefix, which allows
AS64498 only. Peer2 is AS64499.
Pass (what happened): the announcement is invalid and must
be rejected. Verdict BLOCK — even though a forwarding
table would show the route, because the route itself must
not be accepted.
Fail would be: the tool accepts any announcement as long
as a route exists, or blocks a legitimate announcement by
the ROA's own AS.
Why an operator cares: RPKI is how the internet checks
"are you really allowed to announce this address?" Without
it, a wrong announcement can hijack traffic.
*Honest limit, read this:* this test is recorded replay
(mock) only — a canned report played back without a live
server, explained once here and called "recorded replay"
in new user-facing text. Batfish does not expose a
verifiable ROV (route origin validation) state: a
Cisco-style RPKI server setting parsed fine but produced
no validation state and no impact, so no live RPKI claim
is made. Like the hijack rule, it uses the direct peer
next-hop IP as a proxy, because Batfish's routes query
exposes no AS_PATH.

## 6. Reproduce it in 30 seconds, and what the verdict does NOT guarantee

```bash
# Simple demo, no Batfish server needed (mock replays canned live reports)
python3 copilot.py --mock --all
# Advanced lab, same idea
python3 advanced/advanced.py --mock --all
# Full test suite (code checks only, no network)
python3 -m unittest discover -s tests
```

Mock means: the live Batfish run was already done, its impact
report was saved word for word, and the mock run replays it.
Verdicts are identical to live verdicts. A report labelled
`mock` is a replay; a report labelled `batfish-live` (or
`batfish-live-advanced`) is the original live run. Both are
honest labels — check the `evidence_source` field in the JSON.

**What the verdict does NOT guarantee (read this before trusting it).**

- It guarantees only the watched prefixes and flows. A change
  can move an unwatched road and still be ALLOW. That is a
  feature (watch what matters), not a bug — but it must be
  understood.
- It does not apply the change, and it does not know your
  business intent. BLOCK means "this impact was found; do not
  apply unless the impact exactly matches what you intended."
  An intentional peer shutdown, for example, would still be
  BLOCK — correctly — because the operator must confirm the
  outage is intended and warn the peer first.
- It is a pre-check, not a proof of the whole internet. It
  proves what happens in this virtual copy, for these watched
  items, under this proposed change.

**If you remember one sentence:** try the change in a virtual
copy first, watch the roads that matter, and let a traffic
light — green, yellow, or red — tell a human whether to go,
ask, or stop.
