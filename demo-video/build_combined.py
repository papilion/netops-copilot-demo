#!/usr/bin/env python3
"""Build the ONE combined submission video (<180s).

Structure: intent -> traffic light -> AI role -> simple diagram +
3 verdicts -> advanced diagram + 8 verdicts -> RPKI LIVE highlight
-> blackhole highlight -> conclusion. Rendered frames (no display
capture on this VM). Terminal slides are labelled honestly: RPKI
is LIVE, the blackhole slide is a MOCK RUN with a live-matching
verdict. Subtitles (EN + KO) are generated from the same slide list
with the same timings.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_en import slide, terminal, image_frame, sections, highlight, assemble, YELLOW

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def fmt(ms):
    total_s, millis = divmod(ms, 1000)
    h, rem = divmod(total_s, 3600)
    minutes, secs = divmod(rem, 60)
    return "%02d:%02d:%02d,%03d" % (h, minutes, secs, millis)

def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(cues, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (i, fmt(start), fmt(end), text))

def main():
    adv = sections(Path("/tmp/combined-adv-en.txt").read_text(encoding="utf-8"))
    by_title = {}
    for sec in adv:
        by_title[sec[0]] = sec
    rpki = next(s for s in adv if s[0].startswith("== RPKI"))
    blackhole = next(s for s in adv if "blackhole" in s[0].lower())
    rpki_hl, rpki_footer = highlight(rpki)
    bh_hl, bh_footer = highlight(blackhole)

    frames = [
        (slide("NetOps Copilot — check before you change", [
            "Validate a BGP / OSPF change in a virtual copy first.",
            "One video: the simple demo and the advanced lab.",
            "All data is fictional (RFC 5737, AS 64496–64501).",
        ]), 8),
        (slide("Why was this made?", [
            "A wrong BGP or OSPF change can stop traffic in seconds.",
            "Today operators check it by hand — slow, and easy to miss.",
            "So: try the change in a virtual copy first, then decide.",
        ]), 10),
        (slide("Think of roads and traffic lights", [
            "Router = intersection. Prefix = neighbourhood.",
            "BGP = road sign. OSPF = map inside our network.",
            "GREEN = all watched roads work. RED = a road is broken.",
            "YELLOW = new road or new exit — a human must confirm.",
        ]), 10),
        (slide("What does the AI do?", [
            "It NEVER decides the verdict. Batfish evidence does.",
            "It explains the verdict in plain words.",
            "It suggests a better change — then we simulate that too.",
            "Example: blackhole at /32, not the whole /25.",
        ]), 10),
        (image_frame(ROOT / "docs" / "topology-simple.png",
                      "Simple diagram — 5 nodes: cores left, edge centre, peer and customer right"), 10),
        (slide("Simple demo — 3 verdicts", [
            "OSPF cost change → GREEN ALLOW: watched roads unchanged.",
            "Peer prefix blocked → RED BLOCK: prefix lost, flow broken.",
            "New customer prefix → YELLOW REVIEW: human confirms it.",
        ]), 12),
        (image_frame(ROOT / "docs" / "topology-advanced.png",
                      "Advanced diagram — Region A left, Region B right, rr1 gold on top"), 10),
        (slide("Advanced lab — 8 verdicts (1 of 2)", [
            "Link failure → GREEN ALLOW: traffic reroutes via coreA2.",
            "BGP session down → RED BLOCK: peer prefix lost at 7 nodes.",
            "LOCAL_PREF exit shift → YELLOW REVIEW: exit moves, flows live.",
            "More-specific hijack → RED BLOCK: cust1 flows to a dead end.",
        ]), 12),
        (slide("Advanced lab — 8 verdicts (2 of 2)", [
            "Route reflector failure → RED BLOCK: all 6 flows break.",
            "Blackhole /32 → YELLOW REVIEW: one host drops, prefix lives.",
            "RPKI invalid origin → RED BLOCK: LIVE, route-map rejects it.",
            "AS_PATH prepend → YELLOW REVIEW: exit moves, flows live.",
        ]), 12),
        (terminal("$ python3 advanced/advanced.py --all | LIVE — control diverts, route-map rejects (rendered)",
                  rpki_hl, footer=rpki_footer), 14),
        (terminal("$ python3 advanced/advanced.py --mock --all | MOCK RUN — verdicts match live (rendered)",
                  bh_hl, footer=bh_footer), 12),
        (slide("How operators use it in real work", [
            "1. Write the change as a diff / ticket.",
            "2. Twin it from current configs. 3. Watch list FIRST.",
            "4. Read the light. 5. A human approves — never auto-applied.",
            "6. Post-check after applying. 7. In CI/CD: BLOCK fails, REVIEW needs sign-off.",
            "Not automated: pushing configs, replacing approval, unwatched prefixes.",
        ]), 14),
        (slide("Where AI acts — and where it does not", [
            "AFTER verdict: explains evidence in plain words.",
            "AFTER verdict: proposes a next change — re-simulate it first.",
            "BEFORE verdict: turns plain intent into a checkable proposal.",
            "NEVER: decides the verdict, edits router configs, sees real configs here.",
            "11 reports' real explanations cost about $0.17 total. Cheap, not a replacement for judgement.",
        ]), 14),
        (slide("Conclusion", [
            "Safe change passes. Breaking change is stopped.",
            "New announcement waits for a human — even at 13 nodes.",
            "The model explains and suggests. It never decides.",
            "GitHub: github.com/papilion/netops-copilot-demo",
        ], badge="GREEN  •  YELLOW  •  RED", badge_col=YELLOW), 10),
    ]
    total = assemble(frames, HERE / "combined_frames", "netops-copilot-demo-combined-en.mp4")
    assert total < 180, total

    en = [
        "NetOps Copilot: check before you change. Validate a BGP or OSPF change in a virtual copy first. One video: the simple demo and the advanced lab.",
        "Why was this made? A wrong BGP or OSPF change can stop traffic in seconds. Today operators check it by hand, slow and easy to miss. So try the change in a virtual copy first, then decide.",
        "Think of roads and traffic lights. Router means intersection, prefix means neighbourhood. BGP is the road sign, OSPF is the map inside our network. Green means all watched roads work, red means a road is broken, yellow means a new road or new exit, and a human must confirm.",
        "What does the AI do? It never decides the verdict. Batfish evidence does. It explains the verdict in plain words. It suggests a better change, then we simulate that too. Example: blackhole at /32, not the whole /25.",
        "Simple diagram: five nodes, cores on the left, edge in the centre, peer and customer on the right.",
        "Simple demo, three verdicts. OSPF cost change: green, ALLOW, watched roads unchanged. Peer prefix blocked: red, BLOCK, prefix lost, flow broken. New customer prefix: yellow, REVIEW, a human confirms it.",
        "Advanced diagram: Region A on the left, Region B on the right, route reflector rr1 in gold on top.",
        "Advanced lab, eight verdicts, part one. Link failure: green, ALLOW, traffic reroutes via coreA2. BGP session down: red, BLOCK, peer prefix lost at seven nodes. LOCAL_PREF exit shift: yellow, REVIEW, exit moves, flows live. More-specific hijack: red, BLOCK, cust1 flows to a dead end.",
        "Advanced lab, part two. Route reflector failure: red, BLOCK, all six flows break. Blackhole /32: yellow, REVIEW, one host drops, prefix lives. RPKI invalid origin: red, BLOCK, live, the route-map rejects it. AS_PATH prepend: yellow, REVIEW, exit moves, flows live.",
        "Terminal, live: RPKI invalid origin. Verdict: BLOCK. Without the route-map, cust1 flows divert to a dead end. With the route-map, the invalid announcement is rejected.",
        "Terminal, mock run: blackhole /32. Verdict: REVIEW. Only the victim host drops. The customer prefix stays intact.",
        "How operators use it in real work. One: write the change as a diff or ticket. Two: twin it from current configs. Three: watch list first. Four: read the light. Five: a human approves, never auto-applied. Six: post-check after applying. Seven: in CI/CD, BLOCK fails, REVIEW needs sign-off. Not automated: pushing configs, replacing approval, unwatched prefixes.",
        "Where AI acts, and where it does not. After the verdict: it explains evidence in plain words. After the verdict: it proposes a next change, which must be re-simulated first. Before the verdict: it turns plain intent into a checkable proposal. Never: decides the verdict, edits router configs, sees real configs here. Eleven reports' real explanations cost about seventeen cents total. Cheap, not a replacement for judgement.",
        "Conclusion. Safe change passes. Breaking change is stopped. New announcement waits for a human, even at 13 nodes. The model explains and suggests. It never decides.",
    ]
    ko = [
        "NetOps Copilot, 바꾸기 전에 확인합니다. BGP·OSPF 변경을 가상 복사본에서 먼저 검증합니다. 단순 데모와 고급 랩을 한 영상에 담았습니다.",
        "왜 만들었나? 잘못된 BGP·OSPF 변경 하나가 몇 초 만에 트래픽을 멈춥니다. 지금까지는 사람이 손으로, 느리게 확인했습니다. 그래서 가상 복사본에서 먼저 바꿔보고 결정합니다.",
        "도로와 신호등으로 생각해 보세요. 라우터는 교차로, prefix는 동네입니다. BGP는 도로 표지판, OSPF는 우리 네트워크 안의 지도입니다. 초록불은 감시 대상 도로가 전부 살아있다는 뜻, 빨간불은 도로가 끊겼다는 뜻, 노란불은 새 도로·새 출구라 사람이 확인해야 한다는 뜻입니다.",
        "AI는 무엇을 하나요? 판정을 내리지 않습니다. Batfish 증거가 판정합니다. AI는 판정을 쉬운 말로 설명하고, 더 나은 변경을 제안합니다. 그리고 그 제안도 다시 시뮬레이션합니다. 예: 블랙홀은 /25 전체가 아니라 /32 호스트 하나만.",
        "단순 구성도: 노드 5개, 왼쪽이 코어, 가운데가 edge, 오른쪽이 peer와 고객입니다.",
        "단순 데모, 판정 3개. OSPF 비용 변경: 초록불 ALLOW, 감시 대상 도로는 그대로입니다. peer prefix 차단: 빨간불 BLOCK, prefix가 사라지고 트래픽이 끊깁니다. 신규 고객 prefix: 노란불 REVIEW, 사람이 확인합니다.",
        "고급 구성도: 왼쪽이 A지역, 오른쪽이 B지역, 위에 금색 route reflector rr1이 있습니다.",
        "고급 랩, 판정 8개 중 전반부. 링크 단절: 초록불 ALLOW, coreA2로 우회합니다. BGP 세션 단절: 빨간불 BLOCK, peer prefix가 7개 노드에서 사라집니다. LOCAL_PREF 출구 변경: 노란불 REVIEW, 출구가 바뀌지만 트래픽은 살아있습니다. more-specific hijack: 빨간불 BLOCK, cust1 트래픽이 막다른 길로 빠집니다.",
        "고급 랩, 후반부. route reflector 장애: 빨간불 BLOCK, 트래픽 6개가 전부 끊깁니다. 블랙홀 /32: 노란불 REVIEW, 호스트 하나만 떨어지고 prefix는 살아남습니다. RPKI 유효하지 않은 origin: 빨간불 BLOCK, 라이브로 route-map이 거부합니다. AS_PATH prepend: 노란불 REVIEW, 출구가 바뀌지만 트래픽은 살아있습니다.",
        "터미널, 라이브: RPKI 유효하지 않은 origin. 판정 BLOCK입니다. route-map이 없으면 cust1 트래픽이 막다른 길로 빠지고, route-map이 있으면 유효하지 않은 발표가 거부됩니다.",
        "터미널, 기록 재생: 블랙홀 /32. 판정 REVIEW입니다. 피해자 호스트만 떨어지고, 고객 prefix는 그대로입니다.",
        "실무 사용법. 첫째, 변경을 diff나 티켓으로 씁니다. 둘째, 현재 설정으로 트윈을 만듭니다. 셋째, 감시 목록을 먼저 정합니다. 넷째, 신호등을 읽습니다. 다섯째, 사람이 승인합니다. 절대 자동 적용하지 않습니다. 여섯째, 적용 뒤에 사후 확인합니다. 일곱째, CI/CD에서는 BLOCK이면 실패, REVIEW면 서명 필요입니다. 자동화되지 않는 것: 라우터에 설정 밀어넣기, 승인 대체, 감시하지 않은 prefix입니다.",
        "AI가 작용하는 곳과 아닌 곳. 판정 뒤에 증거를 평문으로 설명합니다. 판정 뒤에 다음 변경을 제안하고, 그 제안은 먼저 다시 시뮬레이션해야 합니다. 판정 앞에는 평문 의도를 검사 가능한 제안으로 바꿉니다. 절대 하지 않는 것: 판정 내리기, 라우터 설정 고치기, 여기서 실제 설정 보기입니다. 리포트 11건의 실제 설명 비용은 합계 약 0.17달러입니다. 저렴하다는 뜻이지, 판단을 대체한다는 뜻이 아닙니다.",
        "결론. 안전한 변경은 통과하고, 망을 끊는 변경은 막습니다. 새 발표는 13개 노드에서도 사람이 확인합니다. 모델은 설명하고 제안할 뿐, 판정하지 않습니다.",
    ]
    assert len(en) == len(frames) == len(ko), (len(en), len(frames), len(ko))
    cues_en, cues_ko, t = [], [], 0
    for (img, dur), e, k in zip(frames, en, ko):
        cues_en.append((t * 1000, (t + dur) * 1000, e))
        cues_ko.append((t * 1000, (t + dur) * 1000, k))
        t += dur
    assert t == total, (t, total)
    write_srt(HERE / "netops-copilot-demo-combined-en.en.srt", cues_en)
    write_srt(HERE / "netops-copilot-demo-combined-en.ko.srt", cues_ko)
    print("srt cues:", len(cues_en), "total seconds:", total)

if __name__ == "__main__":
    main()
