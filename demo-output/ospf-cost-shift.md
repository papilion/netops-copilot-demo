# NetOps Copilot — OSPF cost shift: core1 -> edge1 link cost 10 -> 100

**Verdict: ALLOW**

의도: Shift traffic so core1 reaches edge1 via core2 instead of directly, without breaking any watched prefix or flow.
판정: 적용 가능 (감시 범위 내). 감시 대상 prefix의 경로가 사라지지 않았고, 감시 대상 flow도 모두 유지됐습니다. 판정은 감시 대상 항목 기준이며, 감시 범위 밖의 전달 경로 변화까지 보장하지 않습니다.
영향 받은 prefix: 없음

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

core1 -> edge1 구간 OSPF 비용을 10에서 100으로 올리는 변경을 시뮬레이션했습니다.
의도는 감시 중인 prefix나 flow를 깨지 않으면서 core1에서 edge1로 가는 트래픽을 직접 경로 대신 core2 경유로 돌리는 것입니다.
Batfish 판정은 ALLOW이며 violations와 notes가 없습니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

Batfish 검증 결과는 ALLOW로 감시 범위 내에서는 core1→edge1 비용 10→100 상향으로 core2 경유 유도가 가능합니다. 적용 전 반드시 시뮬레이션으로 검증하세요.

판정은 Batfish 증거 기준이며, 이 설명과 제안은 판정이 아닙니다. 제안은 적용하기 전에 다시 시뮬레이션해야 합니다.

## Evidence (Batfish)

- core1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core1 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core1 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core2 198.51.100.128/25: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core2 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edge1 192.0.2.0/24: UNCHANGED (base: static via discard -> change: static via discard)
- edge1 198.51.100.128/25: UNCHANGED (base: bgp via ip 198.51.100.2 -> change: bgp via ip 198.51.100.2)
- edge1 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.6 -> change: bgp via ip 198.51.100.6)
- flow core1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

---

### Batfish raw output

```
== Base snapshot ==
All 5 config files parsed OK.
  core1   192.0.2.0/24       ibgp via ip 192.0.2.3
  core1   198.51.100.128/25  ibgp via ip 192.0.2.3
  core1   203.0.113.0/24     ibgp via ip 192.0.2.3
  core2   192.0.2.0/24       ibgp via ip 192.0.2.3
  core2   198.51.100.128/25  ibgp via ip 192.0.2.3
  core2   203.0.113.0/24     ibgp via ip 192.0.2.3
  edge1   192.0.2.0/24       static via discard
  edge1   198.51.100.128/25  bgp via ip 198.51.100.2
  edge1   203.0.113.0/24     bgp via ip 198.51.100.6
  flow core1 -> 198.51.100.130: DELIVERED_TO_SUBNET
  flow core1 -> 203.0.113.10: DELIVERED_TO_SUBNET

== Proposed change: ospf-cost-shift ==

== Impact report ==
  core1   192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core1   198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core1   203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core2   192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core2   198.51.100.128/25  UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core2   203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edge1   192.0.2.0/24       UNCHANGED        base[static via discard] -> change[static via discard]
  edge1   198.51.100.128/25  UNCHANGED        base[bgp via ip 198.51.100.2] -> change[bgp via ip 198.51.100.2]
  edge1   203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.6] -> change[bgp via ip 198.51.100.6]
  flow core1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

Summary: 0 watched item(s) affected by the proposed change.
```
