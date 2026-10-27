# NetOps Copilot (advanced) — DDoS blackhole (RTBH): drop only victim host 203.0.113.130/32 at edgeB1

**Verdict: REVIEW**

의도: DDoS mitigation for cust2: drop ONLY the victim host 203.0.113.130/32 at edgeB1 (border /32 Null0 route, the forwarding effect an RTBH trigger installs). A DDoS usually targets one host, so operators blackhole the /32, not the whole cust2 /25 — blackholing the whole /25 would also kill the customer's innocent hosts on the same prefix, so the /32 minimises collateral. The /25 route must stay intact and every other watched prefix and flow must stay intact, and the victim drop must be recognised as intended, not as an accidental outage.
판정: 재검토 필요. 아래 변경 사항을 확인한 뒤 적용 여부를 결정하세요.
- 참고: Intended blackhole: only the declared victim host 203.0.113.130/32 is dropped (DDoS mitigation, /32 host route); the victim's /25 prefix route and all other watched prefixes and flows are intact. Confirm the victim is the intended one before applying.
영향 받은 prefix: 없음

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

Batfish 판정은 REVIEW입니다.
이번 변경은 edgeB1에서 203.0.113.130/32 단일 호스트만 드롭하는 DDoS 대응 RTBH 블랙홀(/32 Null0)입니다.
해당 /32를 제외하고 cust2의 /25 경로와 나머지 감시 대상 prefix·flow는 모두 유지되며 위반 사항은 없습니다.
적용 전 피해 호스트가 의도한 대상인지 확인하십시오.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

edgeB1에서 203.0.113.130/32 피해 호스트에 대한 차단만 유지하고 cust2 /25 전체로 넓히지 마세요, /25를 넓히면 같은 prefix의 정상 호스트까지 차단됩니다. 적용 전에 피해자가 맞는지와 만료·해제 계획을 확인하세요, 현재 판정은 REVIEW입니다. 이 제안을 믿기 전에 반드시 시뮬레이션으로 검증하세요.

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
- flow coreA1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreA2 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 198.51.100.200: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow coreB1 -> 203.0.113.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NULL_ROUTED)
- flow coreB2 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

## CLI-style view (Batfish evidence rendered like router output — NOT actual device output)

```
CLI-style view — Batfish evidence rendered like router output. NOT actual device output: no router was connected and no command was run on a device. Admin distance and metric are not reported by Batfish, so they are omitted here (shown as nothing, never invented). Interface names, uptime and BGP session state are likewise not reported and are never shown.

Routes (changed watched routes only; UNCHANGED routes omitted):
  (no watched route changed)

Flows (traceroute-style result; no hop list reported):
  coreA1 -> 198.51.100.130: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
  coreA1 -> 203.0.113.10: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
  coreA2 -> 198.51.100.200: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
  coreB1 -> 198.51.100.200: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
  coreB1 -> 203.0.113.130: DELIVERED_TO_SUBNET -> NULL_ROUTED (CHANGED)
  coreB2 -> 203.0.113.10: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
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
