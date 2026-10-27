# NetOps Copilot — Meta Global AI Developer Hackathon demo

ISP 백본 운영자가 BGP/OSPF 변경을 운영망에 적용하기 **전에**,
Batfish 디지털 트윈으로 시뮬레이션하고 영향 범위·정책 위반·판정을
평문으로 알려주는 데모입니다.

## 데모 시나리오 (2개, 대조 구조)

| 시나리오 | 변경 | 기대 판정 |
|---|---|---|
| `ospf-cost-shift` | core1→edge1 OSPF cost 10→100 | 감시 대상 0건 변화 (BGP 경로·flow 유지) → **ALLOW** |
| `block-peer-prefix` | edge1에서 peer1발 198.51.100.128/25 inbound 차단 | 감시 prefix 소실 + flow 중단 → **BLOCK** |

두 시나리오를 나란히 보여주는 것이 데모의 핵심입니다.
"안전한 변경은 통과시키고, 망을 끊는 변경은 막는다"는 것을
같은 엔진·같은 정책으로 증명합니다.

## 실행

```bash
# 1. Batfish 서비스 시작 (별도 터미널, 포트 9996)
bash ~/workspace/batfish-lab/start-batfish.sh

# 2. 데모 실행 (기본: 로컬 설명 템플릿, API 호출 없음, 크레딧 소모 없음)
cd ~/workspace/hackathon/netops-copilot-demo
python3 copilot.py --all

# 3. Meta Model API 설명을 붙이고 싶을 때만 (선택, 소량 과금)
META_API_KEY='...' META_MODEL='muse-spark-1.3' python3 copilot.py --all
# 모델 ID는 dev.meta.ai에서 실제 목록을 확인한 뒤 지정하세요.
```

결과는 `demo-output/`에 JSON + Markdown 리포트로 남습니다.
판정은 항상 Batfish 증거에서 나오고, 모델 설명은 그 증거를
다시 쓰는 역할만 합니다. 모델이 판정을 뒤집지 않습니다.

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
- Meta 도구 활용 25%: Meta Model API로 증거 기반 설명 생성
  (기본 실행은 크레딧을 쓰지 않는 로컬 템플릿, 선택 시 API 연결)
- Demo 25%: 위 2개 시나리오의 ALLOW/BLOCK 대조 실행 + 리포트
- 기술 깊이 20%: Batfish 라우팅·traceroute 증거를 파싱해
  정책으로 판정하는 파이프라인
