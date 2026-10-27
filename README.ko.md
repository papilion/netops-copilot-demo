# NetOps Copilot — Meta Global AI Developer Hackathon demo

> **이게 뭔가요?** BGP/OSPF 변경을 운영망에 적용하기 전에, 디지털 트윈에서 먼저 시뮬레이션하는 도구입니다.
> **어떤 문제를 푸나요?** 잘못된 백본 변경은 초 단위로 번지는데, 지금까지는 사람이 수동으로, 느리게 확인했습니다.
> **판정은?** Batfish 증거만으로 🟢 ALLOW / 🟡 REVIEW / 🔴 BLOCK 중 하나를 냅니다. 사람이 최종 결정합니다.

![Simple demo topology](docs/topology-simple.png)

## 문제 (2문장)

ISP 백본에서 BGP/OSPF 변경 하나가 잘못되면, 장애가 순식간에 퍼집니다.
그런데 적용 전에 그 영향을 전부 확인하는 일은 아직 수작업이라 느리고, 실수하기 쉽습니다.

## 동작 방식 (3단계)

![How it works](docs/how-it-works.png)

1. **제안된 변경을 받습니다.** 아직 운영망에 적용하지 않습니다.
2. **Batfish 디지털 트윈에서 시뮬레이션합니다.** 변경 전과 변경 후의 경로·flow를 비교합니다.
3. **정책으로 판정하고, 평문으로 설명합니다.** 판정은 증거에서만 나오고, 모델이 판정을 뒤집지 않습니다.

## 시나리오

| 시나리오 | 변경 | 결과 |
|---|---|---|
| `ospf-cost-shift` | core1→edge1 OSPF cost 10→100 | 🟢 ALLOW — 감시 대상 0건 변화, 경로·flow 유지 |
| `block-peer-prefix` | edge1에서 peer1발 198.51.100.128/25 inbound 차단 | 🔴 BLOCK — 해당 prefix 3개 노드에서 소실, peer flow 중단 |
| `add-customer-prefix` | edge1에 신규 고객 prefix 203.0.113.128/25 등장 (mock-only) | 🟡 REVIEW — 신규 경로라 사람이 의도를 확인해야 함 |

## 정책 (한 문단)

감시 prefix 경로가 사라지거나 감시 flow가 중단(DENIED/NO_ROUTE/DROP)되면 BLOCK입니다.
신규 경로가 생기거나 flow가 비치명적으로 바뀌면 REVIEW, next-hop만 바뀌고 flow가 전부 유지되면 ALLOW입니다.

## 실행

```bash
python3 copilot.py --mock --all   # Batfish 불필요, ~1초, 3개 판정
python3 -m unittest discover -s tests   # 테스트 26개 (단순 8 + 고급 18)
```

`--mock`은 `demo-data/`의 기록된 Batfish impact report를 씁니다.
그래서 mock 판정과 live 판정이 같습니다.

전체 live 실행 (선택):

```bash
bash ~/workspace/batfish-lab/start-batfish.sh   # 별도 터미널, 포트 9996
python3 copilot.py --all   # mock-only 시나리오는 건너뜁니다
```

## 모델과 MCP

`META_API_KEY`가 있으면 설명은 Meta Model API(`muse-spark-1.3`)가 기본으로 만듭니다.
사용량이 있으면 리포트에 `usage`와 `cost_usd_estimate`도 기록됩니다.

키가 없으면 건너뛴다고 명확히 출력하고 로컬 템플릿을 씁니다.

구조 규칙: 판정(ALLOW / BLOCK / REVIEW)은 Batfish 증거가 고정된 규칙으로 내리고, Meta 모델은 판정을 내리지 않습니다. 모델은 판정을 평문으로 설명하고 다음 단계를 제안할 뿐입니다 (예: 블랙홀을 /25가 아니라 /32로 유지). 그 제안은 믿기 전에 다시 시뮬레이션해야 합니다. 각 리포트에는 "AI 설명 / 제안하는 다음 단계 (재시뮬레이션 필요 — 판정이 아닙니다)"로 들어 있습니다. 라이브 API 설명은 아직 키를 기다리고 있어 현재 리포트는 규칙 기반이고, Meta 모델이 쓴 유일한 예시는 `demo-output/playground-samples.md`의 playground 샘플입니다.
키 값은 절대 파일에 넣지 마세요 (환경변수만).

MCP 서버도 있습니다 (stdlib만, JSON-RPC over stdio):

```bash
python3 mcp_server.py   # 도구: list_scenarios, validate_change, get_policy
```

이 데모는 변경을 **적용하지 않습니다**. 판정만 반환합니다.

## 고급 버전

13개 노드·2개 지역·route reflector를 갖춘 대형 랩은 `advanced/`에 있습니다.
링크 단절, BGP 세션 단절, LOCAL_PREF 출구 변경, hijack, RR 장애, DDoS 블랙홀(/32 피해자 호스트), RPKI 유효하지 않은 origin(기록 재생 전용), AS_PATH prepend까지 8개 시나리오입니다.
자세한 구성도와 판정표는 [advanced/README-advanced.md](advanced/README-advanced.md)를 보세요.

## 데이터 주의

모든 토폴로지·prefix·AS 번호는 가상 샘플입니다 (RFC 5737 문서용 대역, AS 64496–64498).
실제 운영망 설정, 실제 고객 prefix, 회사 내부 정보는 일절 없습니다.
