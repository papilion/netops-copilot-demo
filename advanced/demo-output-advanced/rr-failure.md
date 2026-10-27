# NetOps Copilot (advanced) — Route reflector failure: rr1 interfaces shutdown

**Verdict: BLOCK**

의도: Shutdown rr1; iBGP clients must lose reflected routes and all watched flows must break.
판정: 적용 중단. 아래 영향이 확인됐기 때문에, 의도가 정확히 이 영향과 일치하지 않는 한 운영망에 적용하면 안 됩니다.
- 위반: Watched prefix 192.0.2.0/24: route LOST at corea1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at corea1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.192/26: route LOST at corea1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.0/24: route LOST at corea1 (was: ibgp via ip 192.0.2.4)
- 위반: Watched prefix 203.0.113.128/25: route LOST at corea1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 192.0.2.0/24: route LOST at corea2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at corea2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.192/26: route LOST at corea2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.0/24: route LOST at corea2 (was: ibgp via ip 192.0.2.4)
- 위반: Watched prefix 203.0.113.128/25: route LOST at corea2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 192.0.2.0/24: route LOST at coreb1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at coreb1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.192/26: route LOST at coreb1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.0/24: route LOST at coreb1 (was: ibgp via ip 192.0.2.4)
- 위반: Watched prefix 203.0.113.128/25: route LOST at coreb1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 192.0.2.0/24: route LOST at coreb2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at coreb2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.192/26: route LOST at coreb2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.0/24: route LOST at coreb2 (was: ibgp via ip 192.0.2.4)
- 위반: Watched prefix 203.0.113.128/25: route LOST at coreb2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 198.51.100.192/26: route LOST at edgea1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.0/24: route LOST at edgea1 (was: ibgp via ip 192.0.2.4)
- 위반: Watched prefix 203.0.113.128/25: route LOST at edgea1 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 192.0.2.0/24: route LOST at edgea2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at edgea2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.192/26: route LOST at edgea2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 203.0.113.128/25: route LOST at edgea2 (was: ibgp via ip 192.0.2.7)
- 위반: Watched prefix 192.0.2.0/24: route LOST at edgeb1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at edgeb1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched flow coreA1 -> 198.51.100.130 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
- 위반: Watched flow coreA1 -> 203.0.113.10 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
- 위반: Watched flow coreA2 -> 198.51.100.200 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
- 위반: Watched flow coreB1 -> 198.51.100.200 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
- 위반: Watched flow coreB1 -> 203.0.113.130 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
- 위반: Watched flow coreB2 -> 203.0.113.10 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
영향 받은 prefix: 192.0.2.0/24, 198.51.100.128/25, 198.51.100.192/26, 203.0.113.0/24, 203.0.113.128/25

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

rr1 인터페이스 shutdown 상황을 시뮬레이션했습니다. corea1, corea2, coreb1, coreb2, edgea1, edgea2, edgeb1에서 감시 대상 prefix들의 iBGP 경로가 상실되었습니다. coreA1, coreA2, coreB1, coreB2 출발 감시 플로우가 DELIVERED_TO_SUBNET에서 NO_ROUTE 상태로 중단되었습니다. 판정은 BLOCK입니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

rr1 인터페이스 shutdown을 되돌려 iBGP 세션을 복원하세요. (판정: BLOCK) 이 제안을 신뢰하기 전에 반드시 시뮬레이션으로 검증하세요.

판정은 Batfish 증거 기준이며, 이 설명과 제안은 판정이 아닙니다. 제안은 적용하기 전에 다시 시뮬레이션해야 합니다.

## Evidence (Batfish, batfish-live-advanced)

- corea1 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- corea1 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- corea1 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- corea1 203.0.113.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.4 -> change: None)
- corea1 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- corea2 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- corea2 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- corea2 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- corea2 203.0.113.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.4 -> change: None)
- corea2 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- coreb1 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- coreb1 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- coreb1 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- coreb1 203.0.113.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.4 -> change: None)
- coreb1 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- coreb2 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- coreb2 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- coreb2 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- coreb2 203.0.113.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.4 -> change: None)
- coreb2 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- edgea1 192.0.2.0/24: UNCHANGED (base: static via discard -> change: static via discard)
- edgea1 198.51.100.128/25: UNCHANGED (base: bgp via ip 198.51.100.2 -> change: bgp via ip 198.51.100.2)
- edgea1 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- edgea1 203.0.113.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.4 -> change: None)
- edgea1 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- edgea2 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- edgea2 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- edgea2 198.51.100.192/26: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- edgea2 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.6 -> change: bgp via ip 198.51.100.6)
- edgea2 203.0.113.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.7 -> change: None)
- edgeb1 192.0.2.0/24: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- edgeb1 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- edgeb1 198.51.100.192/26: UNCHANGED (base: bgp via ip 198.51.100.10 -> change: bgp via ip 198.51.100.10)
- edgeb1 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.18 -> change: bgp via ip 198.51.100.18)
- edgeb1 203.0.113.128/25: UNCHANGED (base: bgp via ip 198.51.100.14 -> change: bgp via ip 198.51.100.14)
- flow coreA1 -> 198.51.100.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow coreA1 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow coreA2 -> 198.51.100.200: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow coreB1 -> 198.51.100.200: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow coreB1 -> 203.0.113.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow coreB2 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)

## CLI-style view (Batfish evidence rendered like router output — NOT actual device output)

```
CLI-style view — Batfish evidence rendered like router output. NOT actual device output: no router was connected and no command was run on a device. Admin distance and metric are not reported by Batfish, so they are omitted here (shown as nothing, never invented). Interface names, uptime and BGP session state are likewise not reported and are never shown.

Routes (changed watched routes only; UNCHANGED routes omitted):
  corea1: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  corea1: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  corea1: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  corea1: i 203.0.113.0/24 — route LOST (was: ibgp via ip 192.0.2.4)
  corea1: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  corea2: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  corea2: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  corea2: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  corea2: i 203.0.113.0/24 — route LOST (was: ibgp via ip 192.0.2.4)
  corea2: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  coreb1: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  coreb1: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  coreb1: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  coreb1: i 203.0.113.0/24 — route LOST (was: ibgp via ip 192.0.2.4)
  coreb1: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  coreb2: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  coreb2: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  coreb2: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  coreb2: i 203.0.113.0/24 — route LOST (was: ibgp via ip 192.0.2.4)
  coreb2: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  edgea1: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  edgea1: i 203.0.113.0/24 — route LOST (was: ibgp via ip 192.0.2.4)
  edgea1: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  edgea2: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  edgea2: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  edgea2: i 198.51.100.192/26 — route LOST (was: ibgp via ip 192.0.2.7)
  edgea2: i 203.0.113.128/25 — route LOST (was: ibgp via ip 192.0.2.7)
  edgeb1: i 192.0.2.0/24 — route LOST (was: ibgp via ip 192.0.2.3)
  edgeb1: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)

Flows (traceroute-style result; no hop list reported):
  coreA1 -> 198.51.100.130: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
  coreA1 -> 203.0.113.10: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
  coreA2 -> 198.51.100.200: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
  coreB1 -> 198.51.100.200: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
  coreB1 -> 203.0.113.130: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
  coreB2 -> 203.0.113.10: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
```

---

### Batfish raw output

```
== Base snapshot ==
All 13 config files parsed OK.
  corea1  192.0.2.0/24       ibgp via ip 192.0.2.3
  corea1  198.51.100.128/25  ibgp via ip 192.0.2.3
  corea1  198.51.100.192/26  ibgp via ip 192.0.2.7
  corea1  203.0.113.0/24     ibgp via ip 192.0.2.4
  corea1  203.0.113.128/25   ibgp via ip 192.0.2.7
  corea2  192.0.2.0/24       ibgp via ip 192.0.2.3
  corea2  198.51.100.128/25  ibgp via ip 192.0.2.3
  corea2  198.51.100.192/26  ibgp via ip 192.0.2.7
  corea2  203.0.113.0/24     ibgp via ip 192.0.2.4
  corea2  203.0.113.128/25   ibgp via ip 192.0.2.7
  coreb1  192.0.2.0/24       ibgp via ip 192.0.2.3
  coreb1  198.51.100.128/25  ibgp via ip 192.0.2.3
  coreb1  198.51.100.192/26  ibgp via ip 192.0.2.7
  coreb1  203.0.113.0/24     ibgp via ip 192.0.2.4
  coreb1  203.0.113.128/25   ibgp via ip 192.0.2.7
  coreb2  192.0.2.0/24       ibgp via ip 192.0.2.3
  coreb2  198.51.100.128/25  ibgp via ip 192.0.2.3
  coreb2  198.51.100.192/26  ibgp via ip 192.0.2.7
  coreb2  203.0.113.0/24     ibgp via ip 192.0.2.4
  coreb2  203.0.113.128/25   ibgp via ip 192.0.2.7
  edgea1  192.0.2.0/24       static via discard
  edgea1  198.51.100.128/25  bgp via ip 198.51.100.2
  edgea1  198.51.100.192/26  ibgp via ip 192.0.2.7
  edgea1  203.0.113.0/24     ibgp via ip 192.0.2.4
  edgea1  203.0.113.128/25   ibgp via ip 192.0.2.7
  edgea2  192.0.2.0/24       ibgp via ip 192.0.2.3
  edgea2  198.51.100.128/25  ibgp via ip 192.0.2.3
  edgea2  198.51.100.192/26  ibgp via ip 192.0.2.7
  edgea2  203.0.113.0/24     bgp via ip 198.51.100.6
  edgea2  203.0.113.128/25   ibgp via ip 192.0.2.7
  edgeb1  192.0.2.0/24       ibgp via ip 192.0.2.3
  edgeb1  198.51.100.128/25  ibgp via ip 192.0.2.3
  edgeb1  198.51.100.192/26  bgp via ip 198.51.100.10
  edgeb1  203.0.113.0/24     bgp via ip 198.51.100.18
  edgeb1  203.0.113.128/25   bgp via ip 198.51.100.14
  flow coreA1 -> 198.51.100.130: DELIVERED_TO_SUBNET
  flow coreA1 -> 203.0.113.10: DELIVERED_TO_SUBNET
  flow coreA2 -> 198.51.100.200: DELIVERED_TO_SUBNET
  flow coreB1 -> 198.51.100.200: DELIVERED_TO_SUBNET
  flow coreB1 -> 203.0.113.130: DELIVERED_TO_SUBNET
  flow coreB2 -> 203.0.113.10: DELIVERED_TO_SUBNET

== Proposed change: rr-failure ==

== Impact report ==
  corea1  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  corea1  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  corea1  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  corea1  203.0.113.0/24     ROUTE LOST       base[ibgp via ip 192.0.2.4] -> change[None]
  corea1  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  corea2  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  corea2  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  corea2  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  corea2  203.0.113.0/24     ROUTE LOST       base[ibgp via ip 192.0.2.4] -> change[None]
  corea2  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  coreb1  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  coreb1  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  coreb1  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  coreb1  203.0.113.0/24     ROUTE LOST       base[ibgp via ip 192.0.2.4] -> change[None]
  coreb1  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  coreb2  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  coreb2  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  coreb2  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  coreb2  203.0.113.0/24     ROUTE LOST       base[ibgp via ip 192.0.2.4] -> change[None]
  coreb2  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  edgea1  192.0.2.0/24       UNCHANGED        base[static via discard] -> change[static via discard]
  edgea1  198.51.100.128/25  UNCHANGED        base[bgp via ip 198.51.100.2] -> change[bgp via ip 198.51.100.2]
  edgea1  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  edgea1  203.0.113.0/24     ROUTE LOST       base[ibgp via ip 192.0.2.4] -> change[None]
  edgea1  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  edgea2  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  edgea2  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  edgea2  198.51.100.192/26  ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  edgea2  203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.6] -> change[bgp via ip 198.51.100.6]
  edgea2  203.0.113.128/25   ROUTE LOST       base[ibgp via ip 192.0.2.7] -> change[None]
  edgeb1  192.0.2.0/24       ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  edgeb1  198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  edgeb1  198.51.100.192/26  UNCHANGED        base[bgp via ip 198.51.100.10] -> change[bgp via ip 198.51.100.10]
  edgeb1  203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.18] -> change[bgp via ip 198.51.100.18]
  edgeb1  203.0.113.128/25   UNCHANGED        base[bgp via ip 198.51.100.14] -> change[bgp via ip 198.51.100.14]
  flow coreA1 -> 198.51.100.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow coreA1 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow coreA2 -> 198.51.100.200: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow coreB1 -> 198.51.100.200: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow coreB1 -> 203.0.113.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow coreB2 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)

Summary: 35 watched item(s) affected by the proposed change.
```
