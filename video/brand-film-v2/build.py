"""회사 소개 영상 v2 본편(49초). 인트로 v2와 같은 언어: 가는 선, 게이지 노드(차면 띠링과 반짝), 아래 가운데 한글 소제목.
목표: 회사가 무슨 사업을 하는지 분명하게(대화형 AI + 네트워크 인프라).

  0.0– 3.6 인트로 마지막 화면(밝은 로고) → 심볼이 점으로 → 점에서 어둠이 퍼지고 선이 뻗음
  3.6–13.6 AI 콜봇: 고객 목소리 → 음성 인식 · 의도 파악 · 목소리 인증 · 업무 처리 → 답이 고객에게
 13.6–19.5 역할 분담: 단순 문의는 AI 콜봇이, 깊은 상담은 상담사가
 19.5–25.4 대화형 AI 플랫폼 ConvAI: NLU 콜봇 · LLM AI 에이전트 · AICC 구축 (조달청 우수조달물품 2026.01)
 25.4–33.4 네트워크 인프라: 케이블 → 스위치 → 서버 랙 → AI 데이터센터 · 전산센터 · ESS 공장
 33.4–39.5 설계 · 구축 · 보안과 관제 · 운영
 39.5–46.4 AI + NI, 한 팀
 46.4–49.0 아웃트로 첫 화면(막대 12개)으로 이어짐
사실 근거: CLAUDE.md '라피치 사실 자료'(사업: NLU 콜봇, LLM AI Agent, AICC 구축, NI: AI 데이터센터·ESS 공장·전산센터 네트워크, ConvAI 2026.01 우수조달물품)
사용법: python3 video/brand-film-v2/build.py && cd video/brand-film-v2 && npx hyperframes render --fps 60 --quality delivery --output out/body.mp4
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import FILM, G, REPO, SVG_DEFS, cap_html, node, page, setup_project  # noqa: E402

DUR = 49.0
LY = 420
NX = [600, 920, 1240, 1560]
SYM_S = 1920 * 0.5 / 314
SYM_X, SYM_Y = 960 - 122 * SYM_S, 540 - 45 * SYM_S - 40
SYM_CX, SYM_CY = SYM_X + 42 * SYM_S, SYM_Y + 47 * SYM_S
S1_LAB = [("음성 인식", "말을 글로"), ("의도 파악", "원하는 것을 이해"), ("목소리 인증", "목소리로 본인 확인"), ("업무 처리", "업무를 바로 처리")]
S5_LAB = [("01", "설계"), ("02", "구축"), ("03", "보안 · 관제"), ("04", "운영")]
CAPS = [("c1", "AI 콜봇", "AI 콜봇이 [듣고, 이해하고, 처리합니다]"),
        ("c2", "역할 분담", "단순한 문의는 [AI 콜봇]이, 깊은 상담은 [상담사]가"),
        ("c3", "대화형 AI 플랫폼", "콜봇부터 [AI 에이전트], AICC 구축까지"),
        ("c4", "네트워크 인프라", "그 대화가 흐르는 [네트워크]를 설계하고 구축합니다"),
        ("c5", "네트워크 인프라", "[AI 데이터센터]부터 전산센터, ESS 공장까지"),
        ("c6", "설계부터 운영까지", "설계, 구축, 보안과 관제, [운영까지]"),
        ("c7", "한 팀", "인프라 구축부터 AI 도입까지, [한 팀이] 함께합니다")]


def cw(x, y, tag, val, cls, i):
    return (f'<div class="cwrap {cls}" id="{cls}{i}" style="left:{x}px;top:{y}px"><div class="mono">{tag}</div>'
            f'<div class="val">{val}</div></div>')


def ni_svg():
    ports = "".join(f'<rect class="port" x="{420 + i * 52}" y="452" width="34" height="26" rx="4" fill="#0c0916" stroke="#fff" stroke-opacity=".55" stroke-width="1.4"/>'
                    f'<circle class="pled" id="pl{i}" cx="{437 + i * 52}" cy="440" r="4" fill="#3a3158"/>' for i in range(8))
    racks, rleds = "", ""
    for r, rx in enumerate((1180, 1360, 1540)):
        racks += f'<rect class="rk" x="{rx}" y="300" width="140" height="300" rx="10" fill="#120d24" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>'
        for j in range(9):
            y = 570 - j * 30
            racks += f'<rect class="rslot" x="{rx + 16}" y="{y - 9}" width="108" height="18" rx="4" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1"/>'
            rleds += f'<rect class="rled r{r}" data-j="{j}" x="{rx + 24}" y="{y - 2}" width="{36 + (j * 17 + r * 7) % 44}" height="4" rx="2" fill="{G[min(11, 2 + r * 4 + j % 3)]}"/>'
    cables = "".join(f'<path class="cab" id="cab{r}" d="M890 465 C 1010 465, 1060 {350 + r * 110}, {1180 + r * 180} {350 + r * 110}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>' for r in range(3))
    pulses = "".join(f'<circle class="pulse" id="pu{r}" r="7" fill="#fff" filter="url(#gl)"/>' for r in range(3))
    return (f'<g id="niG"><path id="drop" d="M960 420 C 960 470, 790 380, 801 452" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>'
            f'<rect id="swb" x="390" y="425" width="500" height="80" rx="12" fill="#120d24" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/>{ports}'
            f'{cables}{racks}{rleds}{pulses}'
            f'<text class="dlab" id="dl0" x="640" y="550" text-anchor="middle">스위치</text>'
            f'<text class="dlab" id="dl1" x="1430" y="640" text-anchor="middle">서버 랙</text></g>')


def sites_svg():
    st = 'fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.6"'
    a = (f'<rect class="bld" x="250" y="220" width="640" height="440" rx="14" {st}/><line class="bld" x1="250" y1="262" x2="890" y2="262" stroke="#fff" stroke-opacity=".3" stroke-width="1.2"/>')
    win = "".join(f'<rect class="bdet" x="{1030 + c * 72}" y="{350 + r * 64}" width="48" height="36" rx="5" fill="none" stroke="#fff" stroke-opacity=".3"/>' for r in range(4) for c in range(4))
    b = f'<rect class="bld" x="1000" y="300" width="330" height="360" rx="12" {st}/>{win}'
    roof = "M1420 660 L1420 470 L1495 420 L1495 470 L1570 420 L1570 470 L1645 420 L1645 470 L1720 470 L1720 660 Z"
    cells = "".join(f'<rect class="bdet" x="{1442 + c * 68}" y="530" width="48" height="96" rx="6" fill="none" stroke="#fff" stroke-opacity=".35"/>'
                    f'<rect class="bdet cell" x="{1448 + c * 68}" y="{540 + (3 - c) * 12}" width="36" height="{78 - (3 - c) * 12}" rx="3" fill="{G[3 + c * 2]}" opacity=".85"/>' for c in range(4))
    c = f'<path class="bld" d="{roof}" {st}/>{cells}'
    links = (f'<path class="lnk" id="lk0" d="M890 600 L1000 600" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
             f'<path class="lnk" id="lk1" d="M1330 600 L1420 600" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
             f'<circle class="lpu" id="lp0" r="6" fill="#fff" filter="url(#gl)"/><circle class="lpu" id="lp1" r="6" fill="#fff" filter="url(#gl)"/>')
    labs = "".join(f'<text class="dlab slab" x="{x}" y="700" text-anchor="middle">{t}</text>' for x, t in ((570, "AI 데이터센터"), (1165, "전산센터"), (1570, "ESS 공장")))
    return f'<g id="sites">{a}{b}{c}{links}{labs}</g>'


def agent_glyph(x, y):
    return (f'<circle cx="{x}" cy="{y - 9}" r="9" fill="none" stroke="#fff" stroke-width="2.4"/>'
            f'<path d="M{x - 16} {y + 17} C {x - 16} {y + 4}, {x + 16} {y + 4}, {x + 16} {y + 17}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M{x - 13} {y - 9} a13 13 0 0 1 26 0" fill="none" stroke="#ff4fd8" stroke-width="2.4" stroke-linecap="round"/>')


def build():
    cb = "".join(f'<div class="bar cb" style="left:{230 + k * 30 - 6}px;top:{LY}px;background:{G[k]};color:{G[k]}"></div>' for k in range(7))
    s1nodes = "".join(f'<g class="s1n">{node(f"s1n{i}", x, LY, 40)}</g>' for i, x in enumerate(NX))
    s5nodes = "".join(f'<g class="s5n">{node(f"s5n{i}", x, LY, 40)}</g>' for i, x in enumerate(NX))
    svg = f'''<svg class="layer" id="main" viewBox="0 0 1920 1080">{SVG_DEFS}
  <line id="axL" x1="960" y1="{LY}" x2="960" y2="{LY}" stroke="#fff" stroke-opacity=".22" stroke-width="2"/>
  <line id="axR" x1="960" y1="{LY}" x2="960" y2="{LY}" stroke="#fff" stroke-opacity=".22" stroke-width="2"/>
  <line id="trk" x1="430" y1="{LY}" x2="430" y2="{LY}" stroke="#fff" stroke-opacity=".8" stroke-width="2"/>
  <path id="ret" d="M1560 {LY} C 1320 90, 600 90, 360 {LY - 92}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>
  {s1nodes}
  <path id="br" d="M1560 {LY + 50} L1560 {LY + 156}" fill="none" stroke="#9d79ff" stroke-width="2" stroke-dasharray="2 10" stroke-linecap="round"/>
  <g id="agG">{node("ag", 1560, LY + 200, 36, sub=agent_glyph(1560, LY + 200))}<text class="dlab" x="1616" y="{LY + 207}">상담사</text></g>
  {"".join(f'<circle class="sd" id="sd{i}" r="6" fill="#fff" filter="url(#gl)"/>' for i in range(5))}
  <g id="cvG">{node("cv", 960, LY, 72, "ConvAI", 28)}</g>
  <path class="con" d="M886 {LY} L606 {LY}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="1.6"/>
  <path class="con" d="M1034 {LY} L1300 {LY}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="1.6"/>
  <path class="con" d="M960 {LY + 84} L960 {LY + 166}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="1.6"/>
  {ni_svg()}
  {sites_svg()}
  <line id="gd5" x1="430" y1="{LY}" x2="1560" y2="{LY}" stroke="#fff" stroke-opacity=".14" stroke-width="1.5" stroke-dasharray="2 9"/>
  <line id="trk5" x1="430" y1="{LY}" x2="430" y2="{LY}" stroke="#fff" stroke-opacity=".8" stroke-width="2"/>
  {s5nodes}
  <g id="aiG">{node("ai", 720, 540, 60, "AI", 40)}</g><g id="niN">{node("ni", 1200, 540, 60, "NI", 40)}</g>
  <g id="oneG">{node("one", 960, 540, 80, "AI + NI", 32)}</g>
  <g id="dot"><circle r="30" fill="url(#dotg)"/><circle r="7" fill="#fff"/></g>
</svg>'''
    pills = "".join(f'<div style="position:absolute;left:{x}px;top:{y - 32}px;width:0;display:flex;justify-content:center"><div class="pill" id="p{i}">{t}</div></div>'
                    for i, (x, y, t) in enumerate(((470, LY, "NLU 콜봇"), (1450, LY, "LLM AI 에이전트"), (960, LY + 200, "AICC 구축"))))
    dom = (f'<div style="position:absolute;left:330px;top:{LY - 150}px;width:0;display:flex;justify-content:center"><div class="who" id="who0" style="background:#fff;color:#1b1530">고객</div></div>'
           f'<svg id="chk" style="position:absolute;left:{330 + 50}px;top:{LY - 154}px" width="48" height="48" viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="url(#ckg)"/><path d="M14 24.5 l7 7 l14 -15" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="ckg" x1="0" y1="0" x2="48" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset="1" stop-color="#3c24f3"/></linearGradient></defs></svg>'
           + cb
           + "".join(cw(x, LY + 66, t, v, "l1", i) for i, (x, (t, v)) in enumerate(zip(NX, S1_LAB)))
           + "".join(cw(x, LY + 66, t, v, "l5", i) for i, (x, (t, v)) in enumerate(zip(NX, S5_LAB)))
           + f'<div class="cwrap" id="cvl" style="left:960px;top:{LY - 168}px"><div class="mono">자체 대화형 AI 플랫폼</div><div class="mono" style="margin-top:10px;font-size:16px;letter-spacing:.12em;color:#8e86a8">조달청 우수조달물품 지정 · 2026</div></div>'
           + pills
           + cw(720, 640, "", "대화형 AI", "l6", 0) + cw(1200, 640, "", "네트워크 인프라", "l6", 1))
    caps = "".join(cap_html(c, t, x) for c, t, x in CAPS)
    dashes = "".join(f'<div class="dash" style="left:{960 + (k - 5.5) * 46 - 9:.1f}px;background:{G[k]}"></div>' for k in range(12))
    body = f'''<div id="dark" class="layer" style="background:#0c0916"></div>
<div id="light" class="layer" style="background:#faf9fd"></div>
<div id="iris" class="layer" style="background:#0c0916"></div>
<div id="vig" class="layer vig"></div>
{svg}
<div class="layer" id="domL">{dom}</div>
{caps}
<div id="endline" style="position:absolute;left:{960 - 262}px;top:539px;width:524px;height:2px;background:linear-gradient(90deg,#ff03c8,#a518a4 50%,#3c24f3)"></div>
{dashes}
<img id="last" class="layer" src="assets/intro_last.png" />
<img id="sym" src="assets/symbol_purple.svg" style="position:absolute;left:{SYM_X:.1f}px;top:{SYM_Y:.1f}px;width:{84 * SYM_S:.1f}px;height:{90 * SYM_S:.1f}px" />
<img id="ofirst" class="layer" src="assets/outro_first.png" />'''
    css = ".dash { position: absolute; top: 535.8px; width: 18px; height: 8.4px; border-radius: 4.2px; }"
    js = f"""
const LY = {LY}, NX = {json.dumps(NX)};
// ── 초기 상태
gsap.set(["#vig", "#dot", "#who0", "#chk", ".cb", ".l1", ".l5", ".l6", "#ret", "#br", "#agG", ".sd", "#cvG", "#cvl", ".con", ".pill",
  "#niG", "#sites", "#gd5", "#trk5", ".s5n", "#aiG", "#niN", "#oneG", "#endline", ".dash", "#ofirst", ".cap", ".s1n", "#trk"], {{ opacity: 0 }});
gsap.set("#iris", {{ clipPath: "circle(0px at 960px {LY}px)" }});
gsap.set("#dot", {{ x: 960, y: LY }});
gsap.set(".cb", {{ scaleY: 0.05 }});
// ── 0. 인트로 마지막 화면 → 심볼이 점으로 → 점에서 어둠이 퍼지고 선이 양쪽으로
tl.to("#last", {{ opacity: 0, duration: 0.9, ease: "sine.inOut" }}, 0.4);
tl.to("#sym", {{ x: {960 - SYM_CX:.1f}, y: {LY - SYM_CY:.1f}, scale: 0.07, transformOrigin: "50% 52.2%", duration: 1.3, ease: "power3.inOut" }}, 1.1);
tl.to("#sym", {{ opacity: 0, duration: 0.35, ease: "sine.in" }}, 2.05);
tl.fromTo("#dot", {{ opacity: 0, scale: 0.2 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power2.out", immediateRender: false }}, 1.95);
tl.fromTo("#iris", {{ clipPath: "circle(0px at 960px {LY}px)" }}, {{ clipPath: "circle(1700px at 960px {LY}px)", duration: 1.4, ease: "power2.inOut", immediateRender: false }}, 2.2);
FIN("#vig", 3.0, 0.6, "sine.inOut");
tl.fromTo("#axL", {{ attr: {{ x2: 960 }} }}, {{ attr: {{ x2: 200 }}, duration: 1.1, ease: "power2.inOut" }}, 2.9);
tl.fromTo("#axR", {{ attr: {{ x2: 960 }} }}, {{ attr: {{ x2: 1720 }}, duration: 1.1, ease: "power2.inOut" }}, 2.9);
tl.to("#dot", {{ x: 430, scale: 0.7, duration: 1.0, ease: "power2.inOut" }}, 3.3);

// ── 1. AI 콜봇: 고객의 목소리 → 네 단계 → 답이 고객에게
CAP("c1", 3.8, 13.4);
FIN("#who0", 4.0);
tl.fromTo(".cb", {{ opacity: 0, scaleY: 0.05 }}, {{ opacity: 1, scaleY: 0.3, duration: 0.5, ease: "power2.out", stagger: 0.04, immediateRender: false }}, 4.1);
speak(".cb", 4.6, 5.5, 3);
tl.to(".cb", {{ scaleY: 0.08, duration: 0.5, ease: "sine.inOut" }}, 5.5);
tl.fromTo(".s1n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "sine.out", stagger: 0.12, immediateRender: false }}, 4.2);
FIN("#trk", 5.5, 0.1);
const LEG = [[5.6, 6.4], [7.2, 7.9], [8.7, 9.4], [10.2, 10.9]];
LEG.forEach(([a, b], i) => {{
  tl.to("#dot", {{ x: NX[i], duration: b - a, ease: "power2.inOut" }}, a);
  tl.to("#trk", {{ attr: {{ x2: NX[i] }}, duration: b - a, ease: "power2.inOut" }}, a);
  GAUGE("s1n" + i, b - 0.05, 0.7);
  tl.fromTo("#l1" + i, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, b + 0.2);
}});
FIN("#ret", 11.7, 0.05);
ALONG("#ret", "#dot", 11.75, 1.2, "power2.inOut");
tl.to("#dot", {{ opacity: 0, scale: 0.4, duration: 0.3 }}, 12.9);
tl.fromTo("#chk", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.8)", immediateRender: false }}, 12.9);
FOUT([".l1", "#ret", "#chk"], 13.5, 0.5);

// ── 2. 역할 분담: 단순 문의는 AI 콜봇이, 깊은 상담은 상담사가
CAP("c2", 14.2, 19.2);
for (let i = 0; i < 4; i++) {{
  const t = 14.4 + i * 0.42;
  tl.fromTo("#sd" + i, {{ x: 430, y: LY, opacity: 0 }}, {{ x: 1560, duration: 1.6, ease: "power1.inOut", immediateRender: false }}, t);
  tl.fromTo("#sd" + i, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, t);
  tl.to("#sd" + i, {{ opacity: 0, duration: 0.25 }}, t + 1.4);
}}
FIN("#br", 15.6, 0.1); DR("#br", 15.6, 0.6, "power2.out");
tl.fromTo("#agG", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: false }}, 15.9);
tl.fromTo("#sd4", {{ x: 430, y: LY, opacity: 0 }}, {{ x: 1560, opacity: 1, duration: 1.6, ease: "power1.inOut", immediateRender: false }}, 16.4);
tl.to("#sd4", {{ y: LY + 164, duration: 0.6, ease: "power2.inOut" }}, 18.0);
tl.to("#sd4", {{ opacity: 0, duration: 0.2 }}, 18.55);
GAUGE("ag", 18.5, 0.8);

// ── 3. 대화형 AI 플랫폼 ConvAI
FOUT(["#axL", "#axR", "#trk", ".cb", "#who0", "#br", "#agG"], 19.3, 0.5);
tl.to(".s1n", {{ x: (i) => 960 - NX[i], opacity: 0, duration: 0.8, ease: "power3.inOut" }}, 19.3);
CAP("c3", 20.0, 25.0);
tl.fromTo("#cvG", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "power3.out", immediateRender: false }}, 19.9);
GAUGE("cv", 20.3, 1.0);
tl.fromTo("#cvl", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: false }}, 20.5);
FIN(".con", 21.3, 0.05); DR(".con", 21.3, 0.55, "power2.out", 0.15);
gsap.utils.toArray(".pill").forEach((el, i) => tl.fromTo(el, {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.5)", immediateRender: false }}, 21.6 + i * 0.18));
FOUT([".pill", ".con", "#cvl"], 25.0, 0.4);
tl.to("#cvG", {{ scale: 0.12, opacity: 0, duration: 0.5, ease: "power3.in" }}, 25.25);

// ── 4. 네트워크 인프라: 케이블 → 스위치 → 서버 랙 → 사이트들
const N = 25.8;
CAP("c4", N, 29.3);
tl.set("#dot", {{ x: 960, y: LY }}, 25.5);
tl.fromTo("#dot", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power2.out", immediateRender: false }}, 25.6);
FIN("#niG", N - 0.05, 0.2);
DR("#swb", N, 0.8); DR(".port", N + 0.2, 0.5, "power2.out", 0.03);
DR(".rk", N + 0.1, 0.9, "power2.inOut", 0.12); DR(".rslot", N + 0.4, 0.5, "power2.out", 0.008);
ALONG("#drop", "#dot", N + 0.35, 0.75);
tl.to("#dot", {{ scale: 0.4, opacity: 0, duration: 0.3, ease: "power2.in" }}, N + 1.05);
FOUT("#drop", N + 1.2, 0.6);
tl.to("#pl7", {{ attr: {{ fill: "#ff4fd8" }}, duration: 0.2 }}, N + 1.1);
gsap.utils.toArray(".pled").forEach((el, i) => {{ if (i !== 7) tl.to(el, {{ attr: {{ fill: i % 2 ? "#9d79ff" : "#5a5cff" }}, duration: 0.15 }}, N + 1.15 + (7 - i) * 0.035); }});
DR(".cab", N + 1.05, 0.6, "power2.out", 0.06);
gsap.utils.toArray(".cab").forEach((c, r) => {{
  const L = c.getTotalLength(), q = {{ p: 0 }}, pu = document.getElementById("pu" + r);
  gsap.set(pu, {{ opacity: 0 }});
  tl.fromTo(q, {{ p: 0 }}, {{ p: 1, duration: 0.6, ease: "power1.inOut", immediateRender: false, onUpdate: () => {{ const pt = c.getPointAtLength(q.p * L); gsap.set(pu, {{ x: pt.x, y: pt.y, opacity: q.p < 0.97 ? 1 : 0 }}); }} }}, N + 1.2 + r * 0.08);
}});
gsap.set(".rled", {{ opacity: 0.12 }});
gsap.utils.toArray(".rled").forEach((el) => {{ const r = +el.classList[1].slice(1), j = +el.dataset.j; tl.to(el, {{ opacity: 1, duration: 0.15, ease: "none" }}, N + 1.65 + r * 0.06 + j * 0.03); }});
gsap.set(".dlab", {{ opacity: 0 }});
FIN(["#dl0", "#dl1"], N + 0.9, 0.5);
// 한 걸음 물러나면: 장비들은 AI 데이터센터 안에, 옆에는 전산센터와 ESS 공장
FOUT(["#dl0", "#dl1"], 29.2, 0.3);
tl.to("#niG", {{ scale: 0.42, x: 135.3, y: 255.5, svgOrigin: "0 0", duration: 1.3, ease: "power3.inOut" }}, 29.3);
CAP("c5", 29.8, 33.2);
FIN("#sites", 29.75, 0.05);
gsap.set([".bdet", ".lpu"], {{ opacity: 0 }});
DR(".bld", 29.8, 1.0, "power2.inOut", 0.25);
FIN(".bdet", 30.6, 0.6);
FIN(".lnk", 30.9, 0.05); DR(".lnk", 30.9, 0.5, "power2.out", 0.1);
[["#lk0", "#lp0"], ["#lk1", "#lp1"]].forEach(([p, d], i) => {{
  for (let r = 0; r < 2; r++) {{ FIN(d, 31.3 + i * 0.15 + r * 0.8, 0.05); ALONG(p, d, 31.3 + i * 0.15 + r * 0.8, 0.6, "power1.inOut", false); FOUT(d, 31.85 + i * 0.15 + r * 0.8, 0.1); }}
}});
FIN(".slab", 30.9, 0.6);
FOUT(["#niG", "#sites"], 33.2, 0.45);

// ── 5. 설계 · 구축 · 보안과 관제 · 운영
CAP("c6", 33.9, 39.2);
FIN("#gd5", 33.7, 0.6);
tl.fromTo(".s5n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "sine.out", stagger: 0.12, immediateRender: false }}, 33.7);
tl.set("#dot", {{ x: 430, y: LY, scale: 0.7 }}, 33.6);
FIN("#dot", 33.8, 0.4); FIN("#trk5", 34.2, 0.1);
const LEG5 = [[34.3, 35.0], [35.6, 36.3], [36.9, 37.6], [38.2, 38.9]];
LEG5.forEach(([a, b], i) => {{
  tl.to("#dot", {{ x: NX[i], duration: b - a, ease: "power2.inOut" }}, a);
  tl.to("#trk5", {{ attr: {{ x2: NX[i] }}, duration: b - a, ease: "power2.inOut" }}, a);
  GAUGE("s5n" + i, b - 0.05, 0.55);
  tl.fromTo("#l5" + i, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, b + 0.15);
}});
FOUT(["#gd5", "#trk5", ".s5n", ".l5", "#dot"], 39.5, 0.5);

// ── 6. AI + NI, 한 팀
tl.fromTo("#aiG", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "power3.out", immediateRender: false }}, 39.9);
tl.fromTo("#niN", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "power3.out", immediateRender: false }}, 40.05);
FIN(".l6", 40.3, 0.6);
GAUGE("ai", 40.4, 1.0); GAUGE("ni", 40.55, 1.0);
FOUT(".l6", 41.7, 0.4);
tl.to("#aiG", {{ x: 240, duration: 0.9, ease: "power3.inOut" }}, 41.8);
tl.to("#niN", {{ x: -240, duration: 0.9, ease: "power3.inOut" }}, 41.8);
FOUT(["#aiG", "#niN"], 42.4, 0.3);
tl.fromTo("#oneG", {{ opacity: 0, scale: 0.75, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.7, ease: "power3.out", immediateRender: false }}, 42.3);
GAUGE("one", 42.6, 0.9);
CAP("c7", 42.6, 46.2);

// ── 7. 아웃트로 첫 화면(막대 12개)으로
tl.to("#oneG", {{ scale: 0.1, opacity: 0, duration: 0.5, ease: "power3.in" }}, 46.4);
tl.fromTo("#endline", {{ opacity: 1, scaleX: 0 }}, {{ opacity: 1, scaleX: 1, duration: 0.6, ease: "expo.out", immediateRender: false }}, 46.75);
FOUT("#endline", 47.45, 0.35);
gsap.utils.toArray(".dash").forEach((el, k) => tl.fromTo(el, {{ opacity: 0, scaleX: 0.2 }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, 47.4 + Math.abs(k - 5.5) * 0.03));
FIN("#ofirst", 48.55, 0.25, "none");
"""
    return page("Rapeech brand film v2", body, js, DUR, css,
                audio=f'<audio id="sfx" class="clip" src="assets/body_sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int((DUR + 1) * SR), 2))

    def chime(t, g=0.12, hi=False):
        a, b = (91, 98) if hi else (88, 95)
        add(buf, bell(a, 0.9, 0.35), t, g); add(buf, bell(b, 1.2, 0.5), t + 0.08, g * 0.92)

    def whoosh(t, up=True, g=0.035, d=0.8):
        add(buf, sweep(220 if up else 900, 900 if up else 220, d, partials=((1, 1), (2, 0.3)), a=0.1, r=0.2, rise=up), t, g)

    whoosh(1.1, False, 0.04, 1.1); add(buf, pop(900, 420, 0.16), 2.0, 0.1); whoosh(2.9, True, 0.045, 1.1)
    for i, m in enumerate([76, 79, 81, 79]):
        add(buf, tone(hz(m), 0.2, ((1, 1), (2, 0.2)), a=0.015, r=0.08, decay=0.15), 4.65 + i * 0.24, 0.04, -0.4)
    for a, b in [[5.6, 6.4], [7.2, 7.9], [8.7, 9.4], [10.2, 10.9]]:
        whoosh(a, True, 0.025, b - a + 0.2); chime(b + 0.6, 0.1)
    whoosh(11.75, True, 0.03, 1.2); add(buf, pop(980, 420), 12.9, 0.1)
    for i in range(4):
        add(buf, pop(1100, 600, 0.06), 15.9 + i * 0.42, 0.04)
    chime(19.3, 0.11)
    chime(21.3, 0.12, hi=True)
    for i in range(3):
        add(buf, pop(820, 380), 21.6 + i * 0.18, 0.07)
    whoosh(25.3, False, 0.04, 0.6); add(buf, pop(620, 260, 0.12), 26.9, 0.15)
    for r in range(3):
        add(buf, sweep(500, 1500, 0.55, partials=((1, 1),), a=0.06, r=0.12, rise=True), 27.0 + r * 0.08, 0.016)
    for i in range(10):
        add(buf, tone(hz(91 + (i % 4) * 2), 0.07, ((1, 1),), a=0.003, r=0.04, decay=0.05), 27.45 + i * 0.045, 0.024, (i % 3 - 1) * 0.4)
    whoosh(29.3, False, 0.05, 1.3)
    for i in range(3):
        add(buf, tone(hz(43 + i), 0.45, ((1, 1), (2, 0.4), (3, 0.12)), a=0.005, r=0.1, decay=0.2), 29.9 + i * 0.25, 0.1)
    for a, b in [[34.3, 35.0], [35.6, 36.3], [36.9, 37.6], [38.2, 38.9]]:
        whoosh(a, True, 0.022, b - a + 0.2); chime(b + 0.45, 0.09)
    chime(41.4, 0.1); chime(41.55, 0.08, hi=True)
    whoosh(41.8, True, 0.04, 0.9)
    add(buf, tone(hz(36), 1.4, ((1, 1), (2, 0.3)), a=0.005, r=0.5, decay=0.5), 43.5, 0.28)
    for m in (60, 64, 67, 71, 74):
        add(buf, tone(hz(m + 12), 2.4, ((1, 1), (2, 0.15)), a=0.01, r=0.9, decay=1.2), 43.5, 0.045)
    chime(43.5, 0.12, hi=True)
    whoosh(46.4, False, 0.04, 0.9)
    buf = lowpass(buf, 10000)[: int(DUR * SR)]
    buf *= 10 ** (-3 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "brand-film-v2", [(FILM / "assets" / "intro_last.png", "intro_last.png"),
                                               (FILM / "assets" / "brand" / "symbol_purple.svg", "symbol_purple.svg")])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(REPO / "intro" / "out" / "rapeech_outro_16x9.mp4"), "-frames:v", "1", str(a / "outro_first.png")], check=True)
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "body_sfx.wav")
    print("ok")
