# NetOps Copilot — 고급 랩 (ADVANCED lab)

> **이게 뭔가요?** 단순 데모와 같은 아이디어를 현실적인 백본에서 검증한 버전입니다. 노드 13개, 지역 2개, route reflector 1대입니다.
> **어떤 문제를 푸나요?** 단순 데모로는 링크 단절, 출구 변경, hijack, reflector 장애를 보여줄 수 없습니다.
> **판정은?** 8개 시나리오입니다. 허용 1개, 검토 3개, 차단 4개입니다. 라이브 7개는 라이브와 기록 재생 판정이 같고, RPKI는 기록 재생 전용입니다(아래 참조).

기본 아이디어(먼저 시뮬레이션하고, 증거로 판정하고, 사람이 결정한다)는 [단순 README](../README.ko.md)에 있습니다.
이 파일은 더 커진 부분만 다룹니다.

![고급 토폴로지](../docs/topology-advanced.png)

## 연결 (한 줄에 하나씩)

지역 A, 내부:

- coreA1 — coreA2
- coreA1 — edgeA1, coreA1 — edgeA2
- coreA2 — edgeA1, coreA2 — edgeA2

지역 B, 내부:

- coreB1 — coreB2
- coreB1 — edgeB1, coreB2 — edgeB1

지역 간:

- coreA1 — coreB1, coreA2 — coreB2

Route reflector (그림의 금색 선):

- rr1 — coreA1, rr1 — coreB1
- iBGP: 모든 core/edge는 rr1하고만 피어링합니다 (논리 세션, 별도 선이 아닙니다)

외부 (AS64496 경계에서 외부로):

- edgeA1 — peer1 (AS64497), edgeA1 — transit1 (AS64501)
- edgeA2 — cust1 (AS64498)
- edgeB1 — peer2 (AS64499), edgeB1 — cust2 (AS64500), edgeB1 — cust1 (AS64498, 두 번째 링크)

OSPF area: core와 지역 간 링크는 area 0, 지역 A edge는 area 10, 지역 B edge는 area 20입니다.

## 감시 prefix와 flow

| Prefix | Origin AS | 경유 |
|---|---|---|
| 192.0.2.0/24 (자체 aggregate) | 64496 | edgeA1 |
| 198.51.100.128/25 (peer1) | 64497 | edgeA1 |
| 198.51.100.192/26 (peer2) | 64499 | edgeB1 |
| 203.0.113.0/24 (cust1) | 64498 | edgeA2와 edgeB1 (이중 연결) |
| 203.0.113.128/25 (cust2) | 64500 | edgeB1 |

감시 flow (6개): coreA1→cust1, coreA1→peer1, coreB1→cust2, coreB1→peer2, coreA2→peer2, coreB2→cust1.

## 시나리오

라이브 7개는 라이브와 기록 재생 판정이 같습니다. RPKI는 라이브 실행이 없습니다(E5 참조).

| 시나리오 | 변경 | 판정 | 결과 |
|---|---|---|---|
| `link-failure-coreA1-edgeA1` | coreA1–edgeA1 링크 중단 | 🟢 ALLOW | BGP 경로 변화 없음, flow 6개 전부 전달 (IGP가 coreA2로 우회) |
| `bgp-session-down-peer1` | edgeA1–peer1 세션 중단 | 🔴 BLOCK | peer1 prefix 7개 노드에서 소실, peer1 flow가 NO_ROUTE로 중단, 고객은 유지 |
| `localpref-exit-shift` | edgeB1에서 cust1에 LOCAL_PREF 200 | 🟡 REVIEW | cust1 출구가 6개 노드에서 edgeA2→edgeB1으로 이동, flow는 전부 유지 |
| `hijack-customer-prefix` | peer2가 203.0.113.0/25를 Null0로 광고 | 🔴 BLOCK | 203.0.113.10으로 가는 flow가 DELIVERED→NULL_ROUTED로 전환 |
| `rr-failure` | rr1 인터페이스 중단 | 🔴 BLOCK | iBGP 경로 29개 소실, flow 6개 전부 NO_ROUTE로 중단 |
| `blackhole-rtbh-cust2` | edgeB1에서 피해자 호스트 203.0.113.130/32만 Null0로 | 🟡 REVIEW | 그 호스트의 flow만 DELIVERED→NULL_ROUTED로 바뀌고, cust2 /25 경로는 그대로, 나머지 flow 전부 유지 |
| `rpki-invalid-origin` | peer2가 cust1 203.0.113.0/24를 발표 (ROA는 AS64498만 허용) — 기록 재생 전용 | 🔴 BLOCK | 유효하지 않은 origin은, 포워딩 표에 경로가 보여도 거부해야 합니다 |
| `aspath-prepend-deprefer` | edgeA2에서 cust1에 AS64496 ×2 prepend | 🟡 REVIEW | LOCAL_PREF와 같은 출구 이동을 다른 방식으로, flow는 유지 |

## 실행 방법

```bash
python3 advanced/advanced.py --mock --all   # Batfish 불필요, ~1초

bash ~/workspace/batfish-lab-advanced/start-batfish-advanced.sh   # 라이브, 포트 9996
python3 advanced/advanced.py --all

python3 -m unittest discover -s tests   # 단순 + 고급, 테스트 26개
```

이 폴더의 파일: `advanced.py` (실행기), `roas.json` (RPKI 검사용 가상 ROA 표), `demo-data-advanced/*.txt` (라이브 impact report 원문과 기록 재생 RPKI 보고서),
`demo-output-advanced/*.md` + `*.json` (시나리오별 1개씩, live 또는 mock이라고 정직하게 표기).
Batfish 랩 자체는 데모 저장소 밖에 있는 `~/workspace/batfish-lab-advanced/`에 있고 GitHub에는 올리지 않습니다.
데모 저장소에는 기록된 리포트가 들어 있어, 판정만으로 `--mock`만으로 모든 판정을 재현할 수 있습니다.

설명 언어 (기본값은 원래 한국어입니다):

```bash
python3 advanced/advanced.py --mock --all --lang en   # 영어 설명, 판정은 동일
python3 advanced/advanced.py --mock --all --lang ko   # 한국어 설명 (기본값)
```

## 부록 — 세부 사항 / 정직한 메모

- **E1 — NULL_ROUTED도 치명적입니다.** Null0으로 전환된 flow는 NO_ROUTE나 DROP과 마찬가지로 중단된 것으로 봅니다.
- **E2 — 출구 변경 → REVIEW.** Flow가 살아남아도 prefix의 출구 edge가 바뀌면 사람이 새 출구를 확인해야 합니다.
  같은 edge 안에서 next-hop만 바뀌는 경우는 그대로 ALLOW입니다.
- **E4 — 의도된 블랙홀(/32) → REVIEW.** 시나리오가 의도된 피해자 호스트를 선언하고, 치명적인 위반이 그 /32 호스트로 가는 flow뿐이면, 그 차단은 사고가 아니라 의도된 완화 조치입니다. 그래서 REVIEW입니다. 피해자 외 다른 것이 깨지면 그대로 BLOCK입니다. 왜 /32인지 쉽게 말하면, DDoS는 보통 호스트 하나를 노리기 때문에 운영자는 /32 호스트 경로를 블랙홀 처리합니다. /25 전체를 블랙홀 처리하면 같은 prefix의 무고한 고객 호스트까지 죽기 때문에, /32가 부수 피해를 줄입니다. 라이브 증거가 바로 그 정밀함입니다. 피해자 호스트 flow만 DELIVERED→NULL_ROUTED로 바뀌고, edgeB1의 cust2 /25 경로는 `bgp via ip 198.51.100.14` 그대로이며, 나머지 flow 5개도 살아남습니다.
- **E5 — RPKI 유효하지 않은 origin → BLOCK (기록 재생 전용).** ROA가 있는 감시 prefix에 대해, ROA AS와 다른 peer IP를 통한 직접 eBGP 경로로 변경되면 그 발표는 유효하지 않으므로 거부해야 합니다. 포워딩 표에 경로가 보여도 마찬가지입니다. 그 경로 자체를 받아들이면 안 되기 때문입니다. Batfish는 검증 가능한 ROV(경로 origin 검증) 상태를 주지 않습니다. Cisco식 RPKI 서버 설정은 파싱은 됐지만 검증 상태도 영향도 없었기 때문에, 라이브 RPKI라고 주장하지 않습니다. 이 시나리오는 기록 재생(recorded replay, mock)입니다. 라이브 서버 없이 저장된 보고서를 재생하는 것으로, 여기서 한 번 풀어 쓰고 새 사용자용 문장에서는 "기록 재생"이라고 씁니다. E3와 같은 next-hop IP → AS 대리 지표를 씁니다. ROA AS를 통한 정당한 발표는 발동하지 않습니다.
- **E3 — Hijack 광고 → BLOCK (대리 지표).** 고객 prefix가 peer IP를 통한 직접 eBGP 경로로 들어오면 BLOCK 위반입니다.
  Batfish의 routes 조회는 AS_PATH를 주지 않으므로, 직접 peer next-hop을 문서화된 대리 지표로 씁니다 (peer1 .2, peer2 .10, transit .22).
  E3는 합성 테스트로만 검증했고, 라이브 /25 hijack에서는 발동하지 않았습니다. 그 경우는 E1이 차단합니다.
- **Hijack /24 → /25.** 정확한 /24 광고는 Batfish에서 두 번 테스트했습니다 (Loopback, 그다음 Null0 static route).
  정당한 cust1 경로는 매번 유지돼 아무 변화가 없었습니다. 그래서 실제로 트래픽을 빼앗는 고전적인
  more-specific /25 hijack으로 시나리오를 바꿨습니다. /24 결과는 숨기지 않고 여기에 기록합니다.
- **링크 단절은 BGP 변화를 보이지 않습니다.** IGP가 coreA2로 우회하지만 BGP next-hop IP는 바뀌지 않습니다.
  ALLOW는 감시 대상 BGP 범위에서의 올바른 판정이지, IGP 경로가 바뀌지 않았다는 주장이 아닙니다.
- **Batfish는 노드 이름을 소문자로 출력합니다** (corea1, edgeb1). 정책은 이름 대소문자가 아니라 next-hop IP로 매칭합니다.
- **고급 서비스는 단순 랩의 Batfish 런타임을 재사용합니다** (JRE + jar, 복사하지 않음, 자체 containers 디렉터리, 같은 포트 9996).
  고급 서비스를 시작하기 전에 단순 서비스를 멈추세요.
- **Cust1은 이중 연결입니다** (edgeA2 + edgeB1). 그래야 LOCAL_PREF와 prepend 출구 변경이 이동할 두 번째 출구가 생깁니다.
  두 번째 출구가 없으면 두 메커니즘 모두 출구를 이동시킬 수 없습니다.
