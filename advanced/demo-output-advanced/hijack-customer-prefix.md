# NetOps Copilot (advanced) — More-specific hijack: peer2 announces 203.0.113.0/25 via Null0

**Verdict: BLOCK**

의도: Peer2 announces a more-specific of cust1's /24; traffic to 203.0.113.10 must divert to peer2's Null0 and break. See README-advanced.md for why the exact /24 announcement was replaced: Batfish kept the legitimate best path for /24, so the classic more-specific hijack is the scenario that actually diverts traffic in this lab.
판정: 적용 중단. 아래 영향이 확인됐기 때문에, 의도가 정확히 이 영향과 일치하지 않는 한 운영망에 적용하면 안 됩니다.
- 위반: Watched flow coreA1 -> 203.0.113.10 stops working: DELIVERED_TO_SUBNET -> NULL_ROUTED (diverted to a Null0, e.g. by a more-specific hijack)
- 위반: Watched flow coreB2 -> 203.0.113.10 stops working: DELIVERED_TO_SUBNET -> NULL_ROUTED (diverted to a Null0, e.g. by a more-specific hijack)
영향 받은 prefix: 없음

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

Batfish 판정은 BLOCK입니다. 이번 변경은 peer2가 cust1의 /24에 대해 203.0.113.0/25를 Null0으로 발표하는 more-specific hijack입니다. coreA1 -> 203.0.113.10 트래픽이 DELIVERED_TO_SUBNET에서 NULL_ROUTED로 바뀌어 중단됩니다. coreB2 -> 203.0.113.10 트래픽도 DELIVERED_TO_SUBNET에서 NULL_ROUTED로 바뀌어 중단됩니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

BLOCK 판정입니다. peer2의 203.0.113.0/25 more-specific 발표를 거부하고 peer 경유로 고객 prefix를 받지 않아 cust1의 정당한 경로를 복원하세요. coreA1·coreB2에서 203.0.113.10으로 가는 흐름이 복구되는지 반드시 시뮬레이션으로 확인하기 전에는 이 제안을 신뢰하지 마세요.

판정은 Batfish 증거 기준이며, 이 설명과 제안은 판정이 아닙니다. 제안은 적용하기 전에 다시 시뮬레이션해야 합니다.

## Evidence (Batfish, batfish-live-advanced)

- corea1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea1 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.4)
- corea1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea2 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.4)
- corea2 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb1 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.4)
- coreb1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb2 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.4)
- coreb2 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea1 192.0.2.0/24: UNCHANGED (base: static via discard -> change: static via discard)
- edgea1 198.51.100.128/25: UNCHANGED (base: bgp via ip 198.51.100.2 -> change: bgp via ip 198.51.100.2)
- edgea1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea1 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.4)
- edgea1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgea2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgea2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea2 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.6 -> change: bgp via ip 198.51.100.6)
- edgea2 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgeb1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgeb1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgeb1 198.51.100.192/26: UNCHANGED (base: bgp via ip 198.51.100.10 -> change: bgp via ip 198.51.100.10)
- edgeb1 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.18 -> change: bgp via ip 198.51.100.18)
- edgeb1 203.0.113.128/25: UNCHANGED (base: bgp via ip 198.51.100.14 -> change: bgp via ip 198.51.100.14)
- flow coreA1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreA1 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)
- flow coreA2 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 203.0.113.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB2 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)

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

== Proposed change: hijack-customer-prefix ==

== Impact report ==
  corea1  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea1  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea1  203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.4]
  corea1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea2  203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.4]
  corea2  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb1  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb1  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb1  203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.4]
  coreb1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb2  203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.4]
  coreb2  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea1  192.0.2.0/24       UNCHANGED        base[static via discard] -> change[static via discard]
  edgea1  198.51.100.128/25  UNCHANGED        base[bgp via ip 198.51.100.2] -> change[bgp via ip 198.51.100.2]
  edgea1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea1  203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.4]
  edgea1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgea2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgea2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea2  203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.6] -> change[bgp via ip 198.51.100.6]
  edgea2  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgeb1  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgeb1  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgeb1  198.51.100.192/26  UNCHANGED        base[bgp via ip 198.51.100.10] -> change[bgp via ip 198.51.100.10]
  edgeb1  203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.18] -> change[bgp via ip 198.51.100.18]
  edgeb1  203.0.113.128/25   UNCHANGED        base[bgp via ip 198.51.100.14] -> change[bgp via ip 198.51.100.14]
  flow coreA1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreA1 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)
  flow coreA2 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB1 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB1 -> 203.0.113.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB2 -> 203.0.113.10: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)

Summary: 2 watched item(s) affected by the proposed change.
```
