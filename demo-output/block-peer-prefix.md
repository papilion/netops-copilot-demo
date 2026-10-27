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

AI 설명 / 제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다): 경로를 사라지게 한 변경을 제거하거나 수정하세요 (예: 차단 필터 제거, 세션 복원). 다른 것을 적용하기 전에 다시 시뮬레이션하세요. 이 제안도 믿기 전에 시뮬레이션하세요.

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
