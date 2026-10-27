# NetOps Copilot (advanced) — LOCAL_PREF exit shift: cust1 via edgeB1 preferred

**Verdict: REVIEW**

의도: Raise LOCAL_PREF to 200 for cust1 at edgeB1; every core must shift the cust1 exit from edgeA2 to edgeB1, with all flows surviving.
판정: 재검토 필요. 아래 변경 사항을 확인한 뒤 적용 여부를 결정하세요.
- 참고: Path shift for 203.0.113.0/24 at corea1: ibgp via ip 192.0.2.4 -> ibgp via ip 192.0.2.7
- 참고: Path shift for 203.0.113.0/24 at corea2: ibgp via ip 192.0.2.4 -> ibgp via ip 192.0.2.7
- 참고: Path shift for 203.0.113.0/24 at coreb1: ibgp via ip 192.0.2.4 -> ibgp via ip 192.0.2.7
- 참고: Path shift for 203.0.113.0/24 at coreb2: ibgp via ip 192.0.2.4 -> ibgp via ip 192.0.2.7
- 참고: Path shift for 203.0.113.0/24 at edgea1: ibgp via ip 192.0.2.4 -> ibgp via ip 192.0.2.7
- 참고: Path shift for 203.0.113.0/24 at edgea2: bgp via ip 198.51.100.6 -> ibgp via ip 192.0.2.7
- 참고: Exit shift for 203.0.113.0/24: edgeA2 -> edgeB1 (192.0.2.4 -> 192.0.2.7); flows survive, but the new exit must be confirmed by a human.
영향 받은 prefix: 203.0.113.0/24

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

Batfish 판정: REVIEW입니다. cust1(203.0.113.0/24)에 대해 edgeB1에서 LOCAL_PREF 200 적용 의도대로 corea1, corea2, coreb1, coreb2와 edgea1, edgea2에서 경로가 edgeA2(192.0.2.4)에서 edgeB1(192.0.2.7)로 이동했습니다. 위반 사항은 없으며 모든 플로우는 유지됩니다. 단, 새 출구 edgeB1은 사람의 최종 확인이 필요합니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

판정은 REVIEW를 유지합니다. 203.0.113.0/24의 출구가 edgeA2(192.0.2.4)에서 edgeB1(192.0.2.7)로 이동한 것이 의도와 맞는지, 새 출구의 용량과 지연을 사람이 확인한 뒤에만 적용하세요. 이 제안을 믿기 전에 반드시 시뮬레이션으로 검증하세요.

판정은 Batfish 증거 기준이며, 이 설명과 제안은 판정이 아닙니다. 제안은 적용하기 전에 다시 시뮬레이션해야 합니다.

## Evidence (Batfish, batfish-live-advanced)

- corea1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea1 203.0.113.0/24: NEXT-HOP CHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.7)
- corea1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- corea2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- corea2 203.0.113.0/24: NEXT-HOP CHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.7)
- corea2 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb1 203.0.113.0/24: NEXT-HOP CHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.7)
- coreb1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- coreb2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- coreb2 203.0.113.0/24: NEXT-HOP CHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.7)
- coreb2 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea1 192.0.2.0/24: UNCHANGED (base: static via discard -> change: static via discard)
- edgea1 198.51.100.128/25: UNCHANGED (base: bgp via ip 198.51.100.2 -> change: bgp via ip 198.51.100.2)
- edgea1 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea1 203.0.113.0/24: NEXT-HOP CHANGED (base: ibgp via ip 192.0.2.4 -> change: ibgp via ip 192.0.2.7)
- edgea1 203.0.113.128/25: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgea2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edgea2 198.51.100.192/26: UNCHANGED (base: ibgp via ip 192.0.2.7 -> change: ibgp via ip 192.0.2.7)
- edgea2 203.0.113.0/24: NEXT-HOP CHANGED (base: bgp via ip 198.51.100.6 -> change: ibgp via ip 192.0.2.7)
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
- flow coreB1 -> 203.0.113.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
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

== Proposed change: localpref-exit-shift ==

== Impact report ==
  corea1  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea1  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea1  203.0.113.0/24     NEXT-HOP CHANGED base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.7]
  corea1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  corea2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  corea2  203.0.113.0/24     NEXT-HOP CHANGED base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.7]
  corea2  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb1  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb1  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb1  203.0.113.0/24     NEXT-HOP CHANGED base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.7]
  coreb1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  coreb2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  coreb2  203.0.113.0/24     NEXT-HOP CHANGED base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.7]
  coreb2  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea1  192.0.2.0/24       UNCHANGED        base[static via discard] -> change[static via discard]
  edgea1  198.51.100.128/25  UNCHANGED        base[bgp via ip 198.51.100.2] -> change[bgp via ip 198.51.100.2]
  edgea1  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea1  203.0.113.0/24     NEXT-HOP CHANGED base[ibgp via ip 192.0.2.4] -> change[ibgp via ip 192.0.2.7]
  edgea1  203.0.113.128/25   UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea2  192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgea2  198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edgea2  198.51.100.192/26  UNCHANGED        base[ibgp via ip 192.0.2.7] -> change[ibgp via ip 192.0.2.7]
  edgea2  203.0.113.0/24     NEXT-HOP CHANGED base[bgp via ip 198.51.100.6] -> change[ibgp via ip 192.0.2.7]
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
  flow coreB1 -> 203.0.113.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow coreB2 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

Summary: 0 watched item(s) affected by the proposed change.
```
