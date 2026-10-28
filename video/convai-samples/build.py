"""ConvAI 장면(콜봇부터 AI 에이전트, AICC 구축까지)을 쉽게 푼 두 시안.

A: 범위가 넓어지는 원. 안쪽 콜봇 원은 끝까지 밝게 일함(대체가 아니라 역할이 넓어짐). 오른쪽에 짧은 예시
B: 같은 고객, 세 가지 상황. 간단한 문의 → 콜봇 / 복잡한 질문 → AI 에이전트 / 물러나면 수많은 대화가 도는 고객센터(AICC)
둘 다 이전 장면(AI 콜봇 원테이크)의 마지막 화면에서 시작하고, ConvAI 받침 판으로 끝난다.
사용법: python3 video/convai-samples/build.py → video/convai-samples/{a,b}/index.html
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import FILM, cap_html, page, setup_project  # noqa: E402

FLOW_CUT = 32.6
CSS = """
.bub { position: relative; flex: none; padding: 16px 28px; border-radius: 30px; font-size: 28px; font-weight: 700; white-space: nowrap; }
.q { background: #fff; color: #1b1530; }
.a { background: #15102a; color: #fff; border: 1.5px solid rgba(255,79,216,.75); }
.think { background: #15102a; border: 1.5px solid rgba(255,255,255,.3); color: #fff; letter-spacing: .3em; }
.who2 { flex: none; white-space: nowrap; font-size: 18px; font-weight: 600; letter-spacing: .2em; color: #b5abd8; margin-bottom: 10px; }
.plate { position: absolute; height: 74px; border-radius: 18px; background: #15102a; border: 1.5px solid rgba(255,255,255,.4);
  display: flex; align-items: center; justify-content: center; gap: 18px; font-size: 34px; font-weight: 800; color: #fff; }
.plate small { font-size: 18px; font-weight: 600; letter-spacing: .14em; color: #b5abd8; }
"""
CHECK = ('<svg class="ck" width="30" height="30" viewBox="0 0 30 30" style="margin-left:12px;vertical-align:-6px"><circle cx="15" cy="15" r="14" fill="#ff4fd8"/>'
         '<path d="M9 15.5 l4.5 4.5 l8 -9" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def at(x, y, inner, cid="", col=False):
    d = "column" if col else "row"
    return (f'<div {f"id={chr(34)}{cid}{chr(34)}" if cid else ""} style="position:absolute;left:{x}px;top:{y}px;width:0;height:0;display:flex;flex-direction:{d};'
            f'align-items:center;justify-content:center">{inner}</div>')


INTRO_JS = """
tl.to("#prev", { scale: 0.06, opacity: 0, transformOrigin: "960px 540px", duration: 1.1, ease: "power3.in" }, 0.0);
"""


# ─────────────────────────────────────────────── A: 범위가 넓어지는 원
def build_a():
    CX, CY, R = 560, 440, [90, 160, 235]
    dur = 17.5
    caps = [("k1", "NLU 콜봇", "자주 하는 문의는 [바로 처리]하고"),
            ("k2", "LLM AI 에이전트", "복잡한 질문은 [맥락을 이해해] 답하고"),
            ("k3", "AICC 구축", "고객센터 [전체를] AI로"),
            ("k4", "ConvAI  ·  조달청 우수조달물품 지정 2026", "이 모든 것을 하나의 플랫폼, [ConvAI]로")]
    calls = "".join(f'<circle class="call" id="call{i}" r="5" fill="#fff"/>' for i in range(9))
    center = "".join(f'<circle class="cc" id="cc{i}" r="6" fill="#fff"/>' for i in range(6))
    svg = f'''<svg class="layer" viewBox="0 0 1920 1080">
  <g id="rings">
    <circle id="r3" cx="{CX}" cy="{CY}" r="{R[2]}" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>
    <circle id="r2" cx="{CX}" cy="{CY}" r="{R[1]}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>
    <g id="core"><circle cx="{CX}" cy="{CY}" r="{R[0]}" fill="#1a1233"/><circle id="coreRing" cx="{CX}" cy="{CY}" r="{R[0]}" fill="none" stroke="#ff4fd8" stroke-width="2.5" transform="rotate(-90 {CX} {CY})"/>
      <text x="{CX}" y="{CY + 10}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="30" fill="#fff">콜봇</text></g>
    <text id="t2" x="{CX}" y="{CY - R[0] - 26}" text-anchor="middle" font-family="Pretendard" font-weight="700" font-size="24" fill="#e6e0f7">AI 에이전트</text>
    <text id="t3" x="{CX}" y="{CY - R[1] - 28}" text-anchor="middle" font-family="Pretendard" font-weight="700" font-size="24" fill="#e6e0f7">AICC</text>
    {calls}
  </g>
  <g id="center3"><rect x="1040" y="250" width="600" height="380" rx="20" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>
    <text x="1070" y="290" font-family="Pretendard" font-weight="600" font-size="20" letter-spacing="4" fill="#b5abd8">고객센터</text>
    <circle cx="1460" cy="380" r="54" fill="#1a1233" stroke="#ff4fd8" stroke-width="2"/><text x="1460" y="389" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="26" fill="#fff">AI</text>
    <image href="assets/agent.png" x="1410" y="470" width="100" height="100"/><text x="1460" y="600" text-anchor="middle" font-family="Pretendard" font-weight="600" font-size="18" fill="#cfc6ec">상담사</text>
    {center}</g>
</svg>'''
    dom = (at(1320, 300, '<div class="who2">고객</div><div class="bub q" id="q1">카드 분실 신고할게요</div>', col=True)
           + at(1320, 440, f'<div class="bub a" id="a1">분실 신고가 완료됐어요{CHECK}</div>')
           + at(1320, 290, '<div class="who2">고객</div><div class="bub q" id="q2">해외에서 잃어버렸는데, 재발급은 어떻게 받나요?</div>', col=True)
           + at(1320, 420, '<div class="bub think" id="th">• • •</div>')
           + at(1320, 420, f'<div class="bub a" id="a2">재발급 방법과 기간을 안내해 드릴게요{CHECK}</div>')
           + f'<div class="plate" id="plate" style="left:660px;top:650px;width:600px">ConvAI<small>대화형 AI 플랫폼</small></div>')
    caps_html = "".join(cap_html(c, t, x) for c, t, x in caps)
    body = f'''<div class="layer vig"></div>{svg}<div class="layer">{dom}</div>{caps_html}<img id="prev" class="layer" src="assets/flow_last.png" />'''
    js = INTRO_JS + f"""
const CX = {CX}, CY = {CY};
gsap.set(["#rings", "#r2", "#r3", "#t2", "#t3", "#center3", ".call", ".cc", "#q1", "#a1", "#q2", "#th", "#a2", "#plate", ".cap"], {{ opacity: 0 }});
prep(document.getElementById("coreRing"));
// ── 1. 콜봇: 가장 안쪽 원
FIN("#rings", 0.8, 0.05);
tl.fromTo("#core", {{ scale: 0.3, opacity: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, opacity: 1, duration: 0.8, ease: "power3.out", immediateRender: false }}, 0.8);
DR("#coreRing", 1.2, 0.9, "power2.inOut");
CAP("k1", 1.4, 5.0);
// 콜봇은 끝까지 일함: 왼쪽에서 문의(점)가 계속 들어옴
for (let i = 0; i < 9; i++) {{
  const t = 1.6 + i * 1.4, y = CY + [-40, 30, -10, 50, -55, 15, -30, 40, 0][i];
  tl.fromTo("#call" + i, {{ x: CX - 330, y, opacity: 0 }}, {{ x: CX - 70, y: CY + (y - CY) * 0.3, opacity: 1, duration: 1.0, ease: "power1.in", immediateRender: false }}, t);
  tl.to("#call" + i, {{ opacity: 0, duration: 0.15 }}, t + 1.0);
}}
tl.fromTo("#q1", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, 1.8);
gsap.set(document.querySelector("#q1").previousSibling, {{ opacity: 0 }});
FIN(document.querySelector("#q1").previousSibling, 1.8, 0.6);
tl.fromTo("#a1", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, 2.9);
FOUT(["#q1", "#a1", document.querySelector("#q1").previousSibling], 4.9, 0.4);
// ── 2. AI 에이전트: 바깥 원이 넓어짐(콜봇 원은 그대로 밝게)
DR("#r2", 5.2, 1.0, "power2.inOut"); FIN("#r2", 5.2, 0.05); FIN("#t2", 5.8, 0.5);
CAP("k2", 5.4, 9.5);
gsap.set(document.querySelector("#q2").previousSibling, {{ opacity: 0 }});
FIN(document.querySelector("#q2").previousSibling, 5.7, 0.6);
tl.fromTo("#q2", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, 5.7);
tl.fromTo("#th", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, immediateRender: false }}, 6.6);
for (let k = 0; k < 2; k++) tl.to("#th", {{ opacity: 0.45, duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut" }}, 6.9 + k * 0.5);
tl.to("#th", {{ opacity: 0, duration: 0.2 }}, 8.0);
tl.fromTo("#a2", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, 8.1);
FOUT(["#q2", "#a2", document.querySelector("#q2").previousSibling], 9.4, 0.4);
// ── 3. AICC: 가장 바깥 원 = 고객센터 전체
DR("#r3", 9.7, 1.1, "power2.inOut"); FIN("#r3", 9.7, 0.05); FIN("#t3", 10.3, 0.5);
CAP("k3", 9.9, 13.5);
FIN("#center3", 10.0, 0.6);
for (let i = 0; i < 6; i++) {{
  const t = 10.5 + i * 0.4, y0 = 330 + i * 45, toA = i !== 4;
  tl.fromTo("#cc" + i, {{ x: 1080, y: y0, opacity: 0 }}, {{ x: toA ? 1400 : 1405, y: toA ? 380 + (i - 2.5) * 6 : 520, opacity: 1, duration: 1.1, ease: "power1.inOut", immediateRender: false }}, t);
  tl.to("#cc" + i, {{ opacity: 0, duration: 0.2 }}, t + 1.1);
}}
FOUT("#center3", 13.4, 0.4);
// ── 4. 모두 하나의 플랫폼 위에
tl.to("#rings", {{ x: 960 - CX, y: -40, scale: 0.85, transformOrigin: "{CX}px {CY}px", duration: 1.0, ease: "power3.inOut" }}, 13.6);
tl.fromTo("#plate", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: false }}, 14.3);
CAP("k4", 14.0, null);
"""
    return page("ConvAI 시안 A", body, js, dur, CSS,
                audio=f'<audio id="sfx" class="clip" src="assets/sfx_a.wav" data-start="0" data-duration="{dur}" data-track-index="2" data-volume="1"></audio>'), dur


# ─────────────────────────────────────────────── B: 같은 고객, 세 가지 상황
def build_b():
    dur = 28.0
    caps = [("k1", "NLU 콜봇", "자주 하는 문의는 [바로 처리]하고"),
            ("k2", "LLM AI 에이전트", "복잡한 질문은 [맥락을 이해해] 답하고"),
            ("k3", "상담사 연결  ·  대화 요약 전달", "사람이 필요한 상담은 [상담사]에게 바로"),
            ("k4", "AICC 구축", "상담사와 AI가 [함께 일하는] 고객센터"),
            ("k5", "ConvAI  ·  조달청 우수조달물품 지정 2026", "고객은 더 빠르게, 상담사는 [더 중요한 상담]에 집중")]
    P = dict(cu=(300, 470), n1=(1180, 330), n2=(1180, 610), n3=(1600, 470))
    cx, cy = P["cu"]

    def nd(nid, xy, text):
        x, y = xy
        return (f'<g id="{nid}"><circle cx="{x}" cy="{y}" r="70" fill="#1a1233" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>'
                f'<circle id="{nid}R" cx="{x}" cy="{y}" r="70" fill="none" stroke="#ff4fd8" stroke-width="2.5" transform="rotate(-90 {x} {y})"/>'
                f'<text class="ntxt" x="{x}" y="{y + 9}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="26" fill="#fff">{text}</text></g>')

    def paths(pre, w=2, op=".7"):
        l1 = f'M{cx + 120} {cy - 40} C {cx + 400} {cy - 40}, 800 {P["n1"][1]}, {P["n1"][0] - 72} {P["n1"][1]}'
        l2 = f'M{cx + 120} {cy + 10} C {cx + 400} {cy + 10}, 800 {P["n2"][1]}, {P["n2"][0] - 72} {P["n2"][1]}'
        l3 = f'M{P["n2"][0] + 72} {P["n2"][1]} C {P["n2"][0] + 220} {P["n2"][1]}, {P["n3"][0] - 200} {P["n3"][1]}, {P["n3"][0] - 74} {P["n3"][1]}'
        return "".join(f'<path id="{pre}{k}" d="{d}" fill="none" stroke="#fff" stroke-opacity="{op}" stroke-width="{w}"/>' for k, d in (("1", l1), ("2", l2), ("3", l3)))

    x3, y3 = P["n3"]
    counselor = (f'<g id="n3"><circle cx="{x3}" cy="{y3}" r="74" fill="#1a1233" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>'
                 f'<circle id="n3R" cx="{x3}" cy="{y3}" r="74" fill="none" stroke="#ff4fd8" stroke-width="2.5" transform="rotate(-90 {x3} {y3})"/>'
                 f'<image href="assets/agent.png" x="{x3 - 56}" y="{y3 - 60}" width="112" height="112"/>'
                 f'<text class="ntxt" x="{x3}" y="{y3 + 112}" text-anchor="middle" font-family="Pretendard" font-weight="700" font-size="26" fill="#fff">상담사</text></g>')
    card = ('<g id="card"><rect x="-86" y="-24" width="172" height="48" rx="12" fill="#fff"/>'
            '<rect x="-70" y="-10" width="20" height="20" rx="4" fill="#ff4fd8"/>'
            '<text x="-40" y="8" font-family="Pretendard" font-weight="800" font-size="20" fill="#1b1530">대화 요약</text></g>')
    convo = ('<g id="convo">'
             f'<circle id="cglow" cx="{cx}" cy="{cy - 30}" r="130" fill="url(#avg)"/>'
             f'<image id="cust" href="assets/customer.png" x="{cx - 110}" y="{cy - 140}" width="220" height="220"/>'
             + paths("l") + nd("n1", P["n1"], "콜봇") + nd("n2", P["n2"], "AI 에이전트") + counselor
             + '<circle id="d1" r="7" fill="#fff"/><circle id="d2" r="7" fill="#fff"/><circle id="d3" r="7" fill="#fff"/>' + card + '</g>')
    cells = ""
    W, H, S = 540, 190, 0.3
    k = 0
    for r in range(3):
        for c in range(3):
            if (r, c) == (1, 1):
                continue
            tx, ty = 960 + (c - 1) * W - 1000 * S, 420 + (r - 1) * H - 480 * S
            cells += (f'<g class="cell" transform="translate({tx:.1f} {ty:.1f}) scale({S})">'
                      f'<image href="assets/customer.png" x="{cx - 110}" y="{cy - 140}" width="220" height="220"/>'
                      + paths(f"c{k}p", 3, ".55")
                      + "".join(f'<circle cx="{P[n][0]}" cy="{P[n][1]}" r="70" fill="#1a1233" stroke="#ff4fd8" stroke-width="4"/>' for n in ("n1", "n2"))
                      + f'<circle cx="{x3}" cy="{y3}" r="74" fill="#1a1233" stroke="#ff4fd8" stroke-width="4"/>'
                      f'<image href="assets/agent.png" x="{x3 - 56}" y="{y3 - 60}" width="112" height="112"/>'
                      f'<circle class="cd" id="cd{k}" r="16" fill="#fff"/><rect class="cc" id="cc{k}" x="-50" y="-16" width="100" height="32" rx="8" fill="#fff"/></g>')
            k += 1
    svg = ('<svg class="layer" viewBox="0 0 1920 1080">'
           '<defs><radialGradient id="avg"><stop offset="0" stop-color="#6a4dff" stop-opacity=".3"/><stop offset="1" stop-color="#6a4dff" stop-opacity="0"/></radialGradient></defs>'
           f'<g id="grid">{cells}</g>{convo}'
           '<rect id="frame" x="140" y="140" width="1640" height="570" rx="24" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="1.5"/>'
           '</svg>')
    dom = (at(620, 255, '<div class="bub q" id="q1">카드 분실 신고할게요</div>')
           + at(1540, 250, f'<div class="bub a" id="a1">신고 완료됐어요{CHECK}</div>')
           + at(700, 700, '<div class="bub q" id="q2">해외에서 잃어버렸는데, 재발급은 어떻게 받나요?</div>')
           + at(1500, 610, '<div class="bub think" id="th">• • •</div>')
           + at(1560, 610, f'<div class="bub a" id="a2" style="font-size:24px">재발급 방법을 안내해 드릴게요{CHECK}</div>')
           + at(800, 470, '<div class="bub q" id="q3">부정 사용이 의심돼요. 상담사와 통화하고 싶어요</div>')
           + at(1600, 260, '<div class="bub a" id="a3" style="font-size:24px">앞선 내용 확인했어요, 바로 도와드릴게요</div>')
           + '<div class="plate" id="plate" style="left:560px;top:668px;width:800px">ConvAI<small>대화형 AI 플랫폼</small></div>')
    caps_html = "".join(cap_html(c, t, x) for c, t, x in caps)
    body = f'<div class="layer vig"></div>{svg}<div class="layer">{dom}</div>{caps_html}<img id="prev" class="layer" src="assets/flow_last.png" />'
    js = INTRO_JS + B_JS
    return page("ConvAI 시안 B", body, js, dur, CSS,
                audio=f'<audio id="sfx" class="clip" src="assets/sfx_b.wav" data-start="0" data-duration="{dur}" data-track-index="2" data-volume="1"></audio>'), dur


B_JS = """
gsap.set(["#convo", "#grid", ".cell", "#frame", "#n1", "#n2", "#n3", "#l1", "#l2", "#l3", "#d1", "#d2", "#d3", "#card", "#cust",
  "#q1", "#a1", "#q2", "#th", "#a2", "#q3", "#a3", "#plate", ".cap", ".cd", ".cc"], { opacity: 0 });
["n1R", "n2R", "n3R"].forEach((id) => prep(document.getElementById(id)));
// 선 꾸밈(그라데이션 + 시작 점 + 방향 화살표)
DECOR("#l1, #l2, #l3");
DECOR(".cell path", { hidden: false, w: 4, size: 24, aw: 6, dot: 9 });
FIN(".dk-l1", 3.45, 0.3); FIN(".dk-l2", 8.65, 0.3); FIN(".dk-l3", 15.75, 0.3);
// 체크 표시는 말풍선 글자가 나온 다음에
gsap.set(".ck", { opacity: 0 });
tl.fromTo("#a1 .ck", { opacity: 0, scale: 0.3, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)", immediateRender: false }, 4.6);
tl.fromTo("#a2 .ck", { opacity: 0, scale: 0.3, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)", immediateRender: false }, 10.3);
// ── 1. 간단한 문의 → 콜봇이 바로 처리
FIN("#convo", 0.9, 0.05);
tl.fromTo("#cust", { opacity: 0, scale: 0.85, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.9, ease: "power3.out", immediateRender: false }, 0.9);
tl.fromTo("#n1", { opacity: 0, scale: 0.7, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.7, ease: "power3.out", immediateRender: false }, 1.3);
CAP("k1", 1.4, 6.1);
tl.fromTo("#q1", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 1.9);
FIN(["#l1", "#d1"], 2.5, 0.05); ALONG("#l1", "#d1", 2.5, 1.0); FOUT("#d1", 3.5, 0.2);
DR("#n1R", 3.4, 0.7);
tl.fromTo("#a1", { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 4.1);
FOUT("#q1", 5.9, 0.4);
// ── 2. 복잡한 질문 → AI 에이전트(콜봇과 나란히)
tl.fromTo("#n2", { opacity: 0, scale: 0.7, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.7, ease: "power3.out", immediateRender: false }, 6.4);
CAP("k2", 6.6, 11.9);
tl.fromTo("#q2", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 7.0);
FIN(["#l2", "#d2"], 7.7, 0.05); ALONG("#l2", "#d2", 7.7, 1.0); FOUT("#d2", 8.7, 0.2);
DR("#n2R", 8.6, 1.3);
tl.fromTo("#th", { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, 8.8);
tl.to("#th", { opacity: 0.4, duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut" }, 9.1);
tl.to("#th", { opacity: 0, duration: 0.2 }, 9.7);
tl.fromTo("#a2", { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 9.8);
FOUT(["#q2", "#a1", "#a2"], 11.8, 0.4);
// ── 3. 사람이 필요한 상담 → AI가 대화를 정리해 상담사에게(고객은 같은 말을 반복하지 않음)
tl.fromTo("#n3", { opacity: 0, scale: 0.7, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.8, ease: "power3.out", immediateRender: false }, 12.2);
CAP("k3", 12.4, 17.6);
tl.fromTo("#q3", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 12.7);
FIN("#d3", 13.4, 0.05); ALONG("#l2", "#d3", 13.4, 0.9, "power2.inOut", false); FOUT("#d3", 14.3, 0.2);
FIN("#l3", 14.5, 0.05); FIN("#card", 14.75, 0.2);
ALONG("#l3", "#card", 14.5, 1.3, "power2.inOut");
DR("#n3R", 15.6, 0.8);
tl.to("#card", { opacity: 0, duration: 0.4, ease: "power2.in" }, 15.75);
tl.fromTo("#a3", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 16.2);
FOUT(["#q3", "#a3"], 17.5, 0.4);
// ── 4. 물러나면: 상담사와 AI가 함께 일하는 고객센터
tl.to("#convo", { scale: 0.3, x: 960 - 1000 * 0.3, y: 420 - 480 * 0.3, svgOrigin: "0 0", duration: 1.4, ease: "power3.inOut" }, 17.8);
FIN("#grid", 18.7, 0.05);
gsap.utils.toArray(".cell").forEach((el, i) => tl.fromTo(el, { opacity: 0 }, { opacity: 0.8, duration: 0.6, ease: "sine.out", immediateRender: false }, 18.7 + i * 0.07));
FIN("#frame", 19.0, 0.05); DR("#frame", 19.0, 1.0);
// 넓게 물러나면 가운데 대화의 이름표·빛이 서서히 사라져 나머지 8개와 같아짐
tl.to(".ntxt, #cglow", { opacity: 0, duration: 0.9, ease: "sine.inOut" }, 18.4);
CAP("k4", 18.4, 22.9);
for (let k = 0; k < 8; k++) for (let r = 0; r < 2; r++) {
  const t = 19.4 + k * 0.17 + r * 1.5, m = (k + r) % 3;
  if (m === 2) {
    tl.fromTo("#cc" + k, { opacity: 0 }, { opacity: 1, duration: 0.1, immediateRender: false }, t);
    ALONG("#c" + k + "p3", "#cc" + k, t, 1.0, "power2.inOut", false); FOUT("#cc" + k, t + 1.0, 0.15);
  } else {
    tl.fromTo("#cd" + k, { opacity: 0 }, { opacity: 1, duration: 0.1, immediateRender: false }, t);
    ALONG("#c" + k + "p" + (m + 1), "#cd" + k, t, 1.0, "power2.inOut", false); FOUT("#cd" + k, t + 1.0, 0.15);
  }
}
// ── 5. 하나의 플랫폼 위에, 모두에게 좋은 고객센터
tl.to("#grid, #convo, #frame", { y: "-=60", duration: 1.0, ease: "power3.inOut" }, 23.0);
tl.fromTo("#plate", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: false }, 23.6);
CAP("k5", 23.2, null);
"""


def sound(out, dur, events, bed_on=True):
    from engine.bgm import SR, add, synth, lowpass, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int((dur + 1) * SR), 2))
    for kind, t in events:
        if kind == "chime":
            add(buf, bell(88, 0.9, 0.35), t, 0.11); add(buf, bell(95, 1.2, 0.5), t + 0.08, 0.1)
        elif kind == "pop":
            add(buf, pop(820, 380), t, 0.07)
        elif kind == "whoosh":
            add(buf, sweep(240, 900, 0.8, partials=((1, 1), (2, 0.3)), a=0.1, r=0.2, rise=True), t, 0.03)
        elif kind == "down":
            add(buf, sweep(900, 240, 1.0, partials=((1, 1), (2, 0.3)), a=0.1, r=0.2, rise=False), t, 0.045)
    if bed_on:
        bed = synth(dur + 0.5, seed=21, bpm=92)[: len(buf)]
        buf[: len(bed)] += bed * 0.42
    buf = lowpass(buf, 10000)[: int(dur * SR)]
    buf *= 10 ** (-3 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    for name, fn, ev in (("a", build_a, [("down", 0.0), ("chime", 2.1), ("pop", 1.8), ("pop", 2.9), ("whoosh", 5.2), ("pop", 5.7), ("pop", 8.1), ("chime", 8.2),
                                         ("whoosh", 9.7), ("chime", 11.6), ("whoosh", 13.6), ("chime", 14.4)]),
                         ("b", build_b, [("down", 0.0), ("pop", 1.9), ("whoosh", 2.5), ("chime", 4.1), ("pop", 7.0), ("whoosh", 7.7), ("chime", 9.8),
                                         ("pop", 12.7), ("whoosh", 13.4), ("whoosh", 14.5), ("chime", 16.0), ("down", 17.8), ("whoosh", 19.0), ("chime", 23.7)])):
        d = HERE / name
        a = setup_project(d, f"convai-{name}", [(FILM / "assets" / "emoji" / "speaking_head_lit.png", "customer.png"),
                                                 (FILM / "assets" / "emoji" / "agent_headset_lit.png", "agent.png")])
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{12 + FLOW_CUT:.3f}", "-i", str(FILM / "out" / "raw.mp4"), "-frames:v", "1", str(a / "flow_last.png")], check=True)
        html, dur = fn()
        (d / "index.html").write_text(html, encoding="utf-8")
        sound(a / f"sfx_{name}.wav", dur, ev)
        sound(a / f"sfx_{name}_nobed.wav", dur, ev, bed_on=False)   # 회사 소개 영상에 넣을 때(배경음악은 영상 전체에 따로)
    print("ok")
