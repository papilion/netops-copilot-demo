# NetOps Copilot — Meta Global AI Developer Hackathon demo

ISP 백본 운영자가 BGP/OSPF 변경을 운영망에 적용하기 **전에**,
Batfish 디지털 트윈으로 시뮬레이션하고 영향 범위·정책 위반·판정을
평문으로 알려주는 데모입니다.

## 데모 시나리오 (3개, 대조 구조)

| 시나리오 | 변경 | 기대 판정 |
|---|---|---|
| `ospf-cost-shift` | core1→edge1 OSPF cost 10→100 | 감시 대상 0건 변화 (BGP 경로·flow 유지) → **ALLOW** |
| `block-peer-prefix` | edge1에서 peer1발 198.51.100.128/25 inbound 차단 | 감시 prefix 소실 + flow 중단 → **BLOCK** |
| `add-customer-prefix` | edge1에 신규 고객 prefix 203.0.113.128/25 등장 (mock-only) | 신규 경로 → 사람이 확인해야 함 → **REVIEW** |

세 시나리오를 나란히 보여주는 것이 데모의 핵심입니다.
"안전한 변경은 통과시키고, 망을 끊는 변경은 막고, 새로운
공지는 사람이 확인한다"는 것을 같은 엔진·같은 정책으로 증명합니다.

## 고급 버전 (대형 토폴로지, 별도 섹션)

단순 데모 위에, 13개 노드·2개 지역·route reflector·OSPF area 분리·
고객/peer/transit 다중 외부연결을 갖춘 고급 랩이 `advanced/`에 있습니다.
링크 단절, BGP 세션 단절, LOCAL_PREF 출구 변경, more-specific hijack,
RR 장애, AS_PATH prepend까지 6개 시나리오를 라이브 Batfish와 mock으로
둘 다 검증했습니다. 상세는 `advanced/README-advanced.md`를 보세요.

## 구조

```
제안된 BGP/OSPF 변경
        │
        ▼
Batfish 디지털 트윈 (live) ──또는── demo-data/ canned impact report (mock)
        │  routes + traceroute flows, base vs change
        ▼
copilot.py: parse → apply_policy → ALLOW / REVIEW / BLOCK
        │  판정은 항상 Batfish 증거에서만 나옵니다
        ▼
설명 레이어: Meta Model API (Muse Spark 1.3, 키가 있을 때) ──또는── 로컬 템플릿
        │
        ▼
demo-output/*.json + *.md  (판정, 위반, 증거, 설명 출처, 비용 추정치)
```

## 실행 — Quickstart (재현, Batfish 불필요)

```bash
cd ~/workspace/hackathon/netops-copilot-demo
python3 copilot.py --mock --all   # ~1초, 3개 판정: ALLOW / BLOCK / REVIEW
python3 -m unittest discover -s tests -v   # 정책·파싱·Meta 비용 계산 테스트
```

`--mock`은 `demo-data/`의 canned Batfish impact report를 씁니다.
ospf/block 파일은 기록된 live 실행의 raw output을 그대로 가져온
것이라 mock 판정은 live 판정과 동일합니다 (ALLOW / BLOCK).
`add-customer-prefix`는 mock-only 시나리오입니다.

## 실행 — 전체 live Batfish (선택)

```bash
# 1. Batfish 서비스 시작 (별도 터미널, 포트 9996)
bash ~/workspace/batfish-lab/start-batfish.sh

# 2. 데모 실행 (live 모드에서는 mock-only 시나리오가 건너뛰어집니다)
cd ~/workspace/hackathon/netops-copilot-demo
python3 copilot.py --all
```

## Meta Model API 설명 (기본 경로)

`META_API_KEY`가 설정되면 설명은 Meta Model API가 기본으로
만듭니다 (모델 `muse-spark-1.3`, OpenAI-compatible 엔드포인트).
API 응답의 usage가 있으면 리포트에 `usage`와 `cost_usd_estimate`도
기록됩니다. 키가 없으면 명확히 건너뛴다고 출력하고 로컬 템플릿을
씁니다. 키가 없어도 기록된 API 스타일 샘플은
`demo-output/playground-samples.md`에서 볼 수 있습니다.
키 값은 절대 파일에 넣지 마세요 (환경변수만).

```bash
META_API_KEY='...' META_MODEL='muse-spark-1.3' python3 copilot.py --mock --all
# 모델 ID는 dev.meta.ai에서 실제 목록을 확인한 뒤 지정하세요.
```

결과는 `demo-output/`에 JSON + Markdown 리포트로 남습니다.
판정은 항상 Batfish 증거에서 나오고, 모델 설명은 그 증거를
다시 쓰는 역할만 합니다. 모델이 판정을 뒤집지 않습니다.

## MCP 서버 (에이전트가 부르는 도구)

```bash
python3 mcp_server.py   # stdlib만, JSON-RPC over stdio
```

도구: `list_scenarios`, `validate_change` (기본 mock, live는
`use_mock: false`), `get_policy`. 예시 클라이언트 설정:

```json
{
  "mcpServers": {
    "netops-copilot": {
      "command": "python3",
      "args": ["/path/to/netops-copilot-demo/mcp_server.py"]
    }
  }
}
```

이 데모는 변경을 **적용하지 않습니다**. `validate_change`는 판정만
반환합니다. 적용 여부는 사람이 결정합니다.

## 모델 선택 (dev.meta.ai 목록, 2026-10-27 확인)

- **사용: Muse Spark 1.3 (Standard)** — $1.25/1M 입력, $0.15 캐시,
  $4.25/1M 출력. 장시간 코딩·다단계 에이전트 작업용, 네이티브
  툴 호출·MCP 지원이라 이 데모 구조와 맞습니다.
- **안 씀: Muse Wonder** — $4/$20으로 4~5배 비싸고, 이 설명
  작업에는 과합니다. Wonder Full은 API가 아니라 Muse Code
  구독(Power/Maximum) 전용이라 API 데모에 쓸 수 없습니다.
- **안 씀: Spark 1.3 Contributor** — $0.10/$0.20으로 95% 싸지만
  입출력이 모델 학습에 쓰이고, 일부 국가에서만 제공됩니다.
- **안 씀: SAM/Image/Voice, Spark Open/Glimmer, 1.2/1.1** —
  채팅 설명용이 아니거나, 구버전·다운로드형이라 해당 없습니다.

## 정책 (copilot.py의 apply_policy)

- **BLOCK**: 감시 prefix 경로 소실, 또는 감시 flow 중단(DENIED/NO_ROUTE/DROP)
- **REVIEW**: 신규 경로 추가, 또는 비치명적 flow 변경
- **ALLOW**: next-hop 변경만 있고 감시 flow 전부 유지

## 데이터 주의

모든 토폴로지·prefix·AS 번호는 가상 샘플입니다
(RFC 5737 문서용 대역, AS 64496–64498).
실제 운영망 설정, 실제 고객 prefix, 회사 내부 정보는 일절 없습니다.
이 데모는 변경을 **적용하지 않습니다**. 적용 여부는 사람이 결정합니다.

## 제출 스토리 (해커톤 심사 기준 대응)

- Impact 30%: 잘못된 BGP/OSPF 변경이 초 단위로 번지는 백본에서,
  적용 전 시뮬레이션으로 장애를 막는다는 문제 정의
- Meta 도구 활용 25%: Meta Model API가 키가 있을 때 기본 설명 경로
  (usage·비용 추정치 기록, 키가 없으면 명시적으로 건너뜀) + MCP 서버
- Demo 25%: 3개 시나리오의 ALLOW/BLOCK/REVIEW 대조 실행 + 리포트,
  mock 모드로 심사자가 즉시 재현 가능
- 기술 깊이 20%: Batfish 라우팅·traceroute 증거를 파싱해
  정책으로 판정하는 파이프라인
