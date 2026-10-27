# NetOps Copilot (advanced) — DDoS blackhole (RTBH): drop only victim host 203.0.113.130/32 at edgeB1

**Verdict: REVIEW**

의도: DDoS mitigation for cust2: drop ONLY the victim host 203.0.113.130/32 at edgeB1 (border /32 Null0 route, the forwarding effect an RTBH trigger installs). A DDoS usually targets one host, so operators blackhole the /32, not the whole cust2 /25 — blackholing the whole /25 would also kill the customer's innocent hosts on the same prefix, so the /32 minimises collateral. The /25 route must stay intact and every other watched prefix and flow must stay intact, and the victim drop must be recognised as intended, not as an accidental outage.
판정: 재검토 필요. 아래 변경 사항을 확인한 뒤 적용 여부를 결정하세요.
- 참고: Intended blackhole: only the declared victim host 203.0.113.130/32 is dropped (DDoS mitigation, /32 host route); the victim's /25 prefix route and all other watched prefixes and flows are intact. Confirm the victim is the intended one before applying.
영향 받은 prefix: 없음

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

AI 설명 / 제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다): 차단은 /32 호스트 203.0.113.130에만 유지하세요. cust2 /25 전체로 넓히면 안 됩니다. 넓히면 같은 prefix의 무고한 고객 호스트까지 죽습니다. /32가 부수 피해를 줄이는 최적화입니다. 피해자 호스트를 확인하고, 만료와 해제 계획을 정한 뒤, 해제 후 트래픽이 돌아오는지 다시 시뮬레이션하세요. 이 제안도 믿기 전에 시뮬레이션하세요.

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
- flow coreA1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreA2 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 203.0.113.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)
- flow coreB2 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

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

== Proposed change: blackhole-rtbh-cust2 ==

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
  flow coreA1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreA2 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB1 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB1 -> 203.0.113.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)
  flow coreB2 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

Summary: 1 watched item(s) affected by the proposed change.
```
