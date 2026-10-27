# NetOps Copilot — Add new customer prefix: 203.0.113.128/25 appears at edge1

**Verdict: REVIEW**

의도: Announce a new fictional customer prefix 203.0.113.128/25 without touching any existing watched prefix or flow. A new route should be REVIEW, not ALLOW, because a human must confirm the new announcement is intended.
판정: 재검토 필요. 아래 변경 사항을 확인한 뒤 적용 여부를 결정하세요.
- 참고: New route for 203.0.113.128/25 at edge1 (bgp via ip 198.51.100.6)
영향 받은 prefix: 203.0.113.128/25

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

edge1에서 BGP(198.51.100.6 경유)로 203.0.113.128/25에 대한 신규 경로가 확인되었습니다. violations는 비어 있습니다. 신규 발표는 사람의 확인이 필요하므로 판정은 REVIEW입니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

판정은 REVIEW입니다. edge1에 나타난 203.0.113.128/25 신규 경로(bgp via 198.51.100.6)가 의도한 고객 prefix 발표인지 사람이 먼저 확인하세요. 확인 후에만 적용하고, 이 제안을 믿기 전에 반드시 시뮬레이션하세요.

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
- edge1 203.0.113.128/25: ROUTE ADDED (base: None -> change: bgp via ip 198.51.100.6)
- flow core1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
- flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

## CLI-style view (Batfish evidence rendered like router output — NOT actual device output)

```
CLI-style view — Batfish evidence rendered like router output. NOT actual device output: no router was connected and no command was run on a device. Admin distance and metric are not reported by Batfish, so they are omitted here (shown as nothing, never invented). Interface names, uptime and BGP session state are likewise not reported and are never shown.

Routes (changed watched routes only; UNCHANGED routes omitted):
  edge1: B 203.0.113.128/25 via 198.51.100.6 — route ADDED

Flows (traceroute-style result; no hop list reported):
  core1 -> 198.51.100.130: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
  core1 -> 203.0.113.10: DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET (unchanged)
```

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

== Proposed change: add-customer-prefix ==

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
  edge1   203.0.113.128/25   ROUTE ADDED      base[None] -> change[bgp via ip 198.51.100.6]
  flow core1 -> 198.51.100.130: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)
  flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

Summary: 1 watched item(s) affected by the proposed change.
```
