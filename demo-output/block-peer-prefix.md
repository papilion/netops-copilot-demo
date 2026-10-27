# NetOps Copilot — BGP inbound filter: deny peer prefix 198.51.100.128/25 from peer1 at edge1

**Verdict: BLOCK**

의도: Block the peer prefix 198.51.100.128/25 inbound from peer1 (AS64497).
판정: 적용 중단. 아래 영향이 확인됐기 때문에, 의도가 정확히 이 영향과 일치하지 않는 한 운영망에 적용하면 안 됩니다.
- 위반: Watched prefix 198.51.100.128/25: route LOST at core1 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at core2 (was: ibgp via ip 192.0.2.3)
- 위반: Watched prefix 198.51.100.128/25: route LOST at edge1 (was: bgp via ip 198.51.100.2)
- 위반: Watched flow core1 -> 198.51.100.130 stops working: DELIVERED_TO_SUBNET -> NO_ROUTE
영향 받은 prefix: 198.51.100.128/25

## AI explanation / proposed next step (to be re-simulated — NOT the verdict)

설명 (Meta Model API, muse-spark-1.3):

edge1에서 peer1(AS64497)로부터 198.51.100.128/25를 인바운드 차단하도록 BGP 필터를 변경했습니다. 판정: BLOCK. core1과 core2에서 198.51.100.128/25 경로가 소실되었고(기존 ibgp via ip 192.0.2.3), edge1에서도 해당 경로가 소실되었습니다(기존 bgp via ip 198.51.100.2). core1에서 198.51.100.130으로 가는 플로우는 DELIVERED_TO_SUBNET에서 NO_ROUTE로 바뀌어 더 이상 전달되지 않습니다.

제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다. Meta Model API muse-spark-1.3이 규칙 기반 제안을 다듬은 것입니다):

Batfish 검증 결과 BLOCK이므로 이 inbound 차단 변경을 적용하지 마세요. edge1의 peer1용 deny 필터를 제거하거나 수정해 198.51.100.128/25 경로 유지를 검토하세요. 이 제안을 믿기 전에 반드시 다시 시뮬레이션하세요.

판정은 Batfish 증거 기준이며, 이 설명과 제안은 판정이 아닙니다. 제안은 적용하기 전에 다시 시뮬레이션해야 합니다.

## Evidence (Batfish)

- core1 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core1 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- core1 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core2 192.0.2.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- core2 198.51.100.128/25: ROUTE LOST (base: ibgp via ip 192.0.2.3 -> change: None)
- core2 203.0.113.0/24: UNCHANGED (base: ibgp via ip 192.0.2.3 -> change: ibgp via ip 192.0.2.3)
- edge1 192.0.2.0/24: UNCHANGED (base: static via discard -> change: static via discard)
- edge1 198.51.100.128/25: ROUTE LOST (base: bgp via ip 198.51.100.2 -> change: None)
- edge1 203.0.113.0/24: UNCHANGED (base: bgp via ip 198.51.100.6 -> change: bgp via ip 198.51.100.6)
- flow core1 -> 198.51.100.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
- flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

## CLI-style view (Batfish evidence rendered like router output — NOT actual device output)

```
CLI-style view — Batfish evidence rendered like router output. NOT actual device output: no router was connected and no command was run on a device. Admin distance and metric are not reported by Batfish, so they are omitted here (shown as nothing, never invented). Interface names, uptime and BGP session state are likewise not reported and are never shown.

Routes (changed watched routes only; UNCHANGED routes omitted):
  core1: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  core2: i 198.51.100.128/25 — route LOST (was: ibgp via ip 192.0.2.3)
  edge1: B 198.51.100.128/25 — route LOST (was: bgp via ip 198.51.100.2)

Flows (traceroute-style result; no hop list reported):
  core1 -> 198.51.100.130: DELIVERED_TO_SUBNET -> NO_ROUTE (CHANGED)
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

== Proposed change: block-peer-prefix ==

== Impact report ==
  core1   192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core1   198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  core1   203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core2   192.0.2.0/24       UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  core2   198.51.100.128/25  ROUTE LOST       base[ibgp via ip 192.0.2.3] -> change[None]
  core2   203.0.113.0/24     UNCHANGED        base[ibgp via ip 192.0.2.3] -> change[ibgp via ip 192.0.2.3]
  edge1   192.0.2.0/24       UNCHANGED        base[static via discard] -> change[static via discard]
  edge1   198.51.100.128/25  ROUTE LOST       base[bgp via ip 198.51.100.2] -> change[None]
  edge1   203.0.113.0/24     UNCHANGED        base[bgp via ip 198.51.100.6] -> change[bgp via ip 198.51.100.6]
  flow core1 -> 198.51.100.130: FLOW IMPACT (DELIVERED_TO_SUBNET -> NO_ROUTE)
  flow core1 -> 203.0.113.10: UNCHANGED (DELIVERED_TO_SUBNET -> DELIVERED_TO_SUBNET)

Summary: 4 watched item(s) affected by the proposed change.
```
