# NetOps Copilot — Playground samples (Muse Spark 1.3)

Source: dev.meta.ai playground, model Muse Spark 1.3, 2026-10-27.
Prompts pasted the Batfish evidence from `copilot.py` by hand;
the model did not run Batfish itself. All data fictional
(RFC 5737, AS 64496–64498).

## 1. BGP inbound filter — expected BLOCK

Prompt evidence: edge1 denies peer prefix 198.51.100.128/25 inbound
from peer1; routes lost at core1/core2/edge1; flow core1 ->
198.51.100.130 DELIVERED_TO_SUBNET -> NO_ROUTE; customer prefix
203.0.113.0/24 and flow to 203.0.113.10 unchanged.

Model answer (user-pasted, verbatim in substance):

> 이 변경은 운영망에 적용할 수 없으며 판정은 BLOCK입니다.
> edge1에서 peer1발 198.51.100.128/25 inbound 차단 후 감시 prefix
> 198.51.100.128/25가 core1, core2, edge1에서 경로를 소실했고
> 감시 flow core1 -> 198.51.100.130이 DELIVERED_TO_SUBNET에서
> NO_ROUTE로 중단되었습니다. 따라서 의도한 peer1로부터의 차단에도
> 불구하고 감시 대상에 대한 위반이 발생했습니다. 다만 고객 prefix
> 203.0.113.0/24와 flow core1 -> 203.0.113.10은 변경이 없었습니다.

Assessment: facts match Batfish evidence, verdict matches policy,
unaffected customer prefix correctly distinguished. Nuance for
submission: BLOCK means "do not apply as a routine change; confirm
that the peer outage is intended and notify the peer first", not
"this change is always wrong".

## 2. OSPF cost shift — expected ALLOW (watched scope)

Prompt evidence: core1 -> edge1 OSPF cost 10 -> 100; 0 watched
items changed; all watched BGP routes and both watched flows
UNCHANGED / DELIVERED_TO_SUBNET.

Model answer (user-pasted, verbatim in substance):

> 이번 변경은 core1 -> edge1 OSPF cost를 10에서 100으로 올리는
> 것으로, 감시 범위 내에서는 적용 가능하며 판정은 ALLOW
> (감시 범위 내)입니다. core1의 192.0.2.0/24, 198.51.100.128/25,
> 203.0.113.0/24는 ibgp via 192.0.2.3으로 유지되어 모두
> UNCHANGED였습니다. core2의 세 감시 prefix와 edge1의
> 198.51.100.128/25(bgp via 198.51.100.2 유지),
> 203.0.113.0/24(bgp via 198.51.100.6 유지)도 모두 UNCHANGED였고
> 두 감시 flow도 DELIVERED_TO_SUBNET으로 유지되어 감시 대상
> 변화는 0건이었습니다. 따라서 감시 대상 prefix나 flow를 끊지
> 않는다는 의도는 만족되었습니다. 단, 이 판정은 감시 대상 항목
> 기준이며, 감시 범위 밖의 전달 경로 변화까지 보장하지는 않습니다.

Assessment: correct on every checked item, including the
watched-scope limitation. The ALLOW/BLOCK contrast is complete.
