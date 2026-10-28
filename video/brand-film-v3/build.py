"""회사 소개 영상 v3, 뒷부분(29.6초). 앞부분은 이전 소개 영상의 AI 콜봇 원테이크(고객 전화 → AI가 알아듣고 → 답 → 상담사)를 그대로 쓴다.

빛 번짐(글로우)과 그라데이션 고리를 덜어낸 평면 스타일: 가는 흰 선, 무광 노드, 선 아이콘, 강조색은 소제목 한 단어와 작은 표시에만.
  0.0– 6.9 대화형 AI 플랫폼 ConvAI: NLU 콜봇 · LLM AI 에이전트 · AICC 구축 (조달청 우수조달물품 2026)
  6.9–15.0 네트워크 인프라: 케이블 → 스위치 → 서버 랙 → AI 데이터센터 · 전산센터 · ESS 공장
 15.0–21.5 설계 → 구축 → 보안·관제 → 운영 (점이 표식의 정확히 한가운데를 지남, 도착하면 선 아이콘이 그려짐)
 21.5–28.4 AI와 NI 두 원이 겹치고, 겹친 자리가 라피치
 28.4–29.6 어둡게 정리 → 아웃트로
사용법: python3 video/brand-film-v3/build.py && cd video/brand-film-v3 && npx hyperframes render --fps 60 --quality delivery --output out/rest.mp4
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import FILM, G, REPO, cap_html, page, setup_project  # noqa: E402

import os
MODE = os.environ.get("MODE", "")   # "b": ConvAI 장면을 시안 B(별도 영상)로 대체 → 이 영상은 5.6초부터 사용
DUR = 29.6
FLOW_CUT = 32.6            # 이전 소개 영상 원테이크에서 쓰는 길이(본편 기준)
CAPS = [("c3", "대화형 AI 플랫폼", "콜봇부터 [AI 에이전트], AICC 구축까지"),
        ("c4", "네트워크 인프라", "그리고 그 대화가 흐르는 [네트워크]도 설계하고 구축합니다"),
        ("c5", "네트워크 인프라", "[AI 데이터센터]부터 전산센터, ESS 공장까지"),
        ("c6", "설계부터 운영까지", "설계, 구축, 보안과 관제, [운영까지]"),
        ("c7", "한 팀", "인프라 구축부터 AI 도입까지, [한 팀이] 함께합니다")]
MX, MY = [560, 880, 1200, 1520], 470      # 설계~운영 표식(점은 y=MY 위로만 이동 → 표식 한가운데를 지남)
STEPS = [("01", "설계"), ("02", "구축"), ("03", "보안 · 관제"), ("04", "운영")]
LINE = 'fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'


def icons():
    out = []
    for i, x in enumerate(MX):
        y = 340
        if i == 0:   # 설계: 도면(격자) + 삼각자
            g = (f'<rect x="{x - 44}" y="{y - 32}" width="88" height="64" rx="4" {LINE}/>'
                 + "".join(f'<line x1="{x - 44}" y1="{y - 32 + k * 16}" x2="{x + 44}" y2="{y - 32 + k * 16}" stroke="#fff" stroke-opacity=".3" stroke-width="1"/>' for k in (1, 2, 3))
                 + f'<path d="M{x - 30} {y + 22} L{x - 30} {y - 18} L{x + 10} {y + 22} Z" {LINE}/>')
        elif i == 1:  # 구축: 랙
            g = (f'<rect x="{x - 30}" y="{y - 44}" width="60" height="88" rx="6" {LINE}/>'
                 + "".join(f'<rect x="{x - 20}" y="{y - 34 + k * 20}" width="40" height="12" rx="2" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.4"/>' for k in range(4))
                 + "".join(f'<circle class="icled" cx="{x + 14}" cy="{y - 28 + k * 20}" r="2.5" fill="{G[2 + k * 3]}"/>' for k in range(4)))
        elif i == 2:  # 보안·관제: 방패 + 체크
            g = (f'<path d="M{x} {y - 44} L{x + 36} {y - 30} L{x + 36} {y + 2} C {x + 36} {y + 24}, {x + 18} {y + 38}, {x} {y + 46} C {x - 18} {y + 38}, {x - 36} {y + 24}, {x - 36} {y + 2} L{x - 36} {y - 30} Z" {LINE}/>'
                 f'<path d="M{x - 14} {y} l10 10 l20 -22" fill="none" stroke="#ff4fd8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        else:         # 운영: 모니터 + 맥박선
            g = (f'<rect x="{x - 46}" y="{y - 36}" width="92" height="60" rx="5" {LINE}/>'
                 f'<path d="M{x - 12} {y + 40} L{x + 12} {y + 40} M{x} {y + 24} L{x} {y + 40}" {LINE}/>'
                 f'<polyline points="{x - 34},{y - 4} {x - 14},{y - 4} {x - 6},{y - 20} {x + 4},{y + 10} {x + 12},{y - 6} {x + 34},{y - 6}" fill="none" stroke="#ff4fd8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<g class="ic" id="ic{i}">{g}</g>')
    return "".join(out)


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
    pulses = "".join(f'<circle class="pulse" id="pu{r}" r="5" fill="#fff"/>' for r in range(3))
    return (f'<g id="niG"><path id="drop" d="M960 430 C 960 480, 790 380, 801 452" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>'
            f'<rect id="swb" x="390" y="425" width="500" height="80" rx="12" fill="#120d24" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/>{ports}'
            f'{cables}{racks}{rleds}{pulses}'
            f'<text class="dlab" id="dl0" x="640" y="550" text-anchor="middle">스위치</text>'
            f'<text class="dlab" id="dl1" x="1430" y="640" text-anchor="middle">서버 랙</text></g>')


def sites_svg():
    st = 'fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.6"'
    a = f'<rect class="bld" x="250" y="220" width="640" height="440" rx="14" {st}/><line class="bld" x1="250" y1="262" x2="890" y2="262" stroke="#fff" stroke-opacity=".3" stroke-width="1.2"/>'
    win = "".join(f'<rect class="bdet" x="{1030 + c * 72}" y="{350 + r * 64}" width="48" height="36" rx="5" fill="none" stroke="#fff" stroke-opacity=".3"/>' for r in range(4) for c in range(4))
    b = f'<rect class="bld" x="1000" y="300" width="330" height="360" rx="12" {st}/>{win}'
    roof = "M1420 660 L1420 470 L1495 420 L1495 470 L1570 420 L1570 470 L1645 420 L1645 470 L1720 470 L1720 660 Z"
    cells = "".join(f'<rect class="bdet" x="{1442 + c * 68}" y="530" width="48" height="96" rx="6" fill="none" stroke="#fff" stroke-opacity=".35"/>'
                    f'<rect class="bdet" x="{1448 + c * 68}" y="{540 + (3 - c) * 12}" width="36" height="{78 - (3 - c) * 12}" rx="3" fill="{G[3 + c * 2]}" opacity=".7"/>' for c in range(4))
    c = f'<path class="bld" d="{roof}" {st}/>{cells}'
    links = (f'<path class="lnk" id="lk0" d="M890 600 L1000 600" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
             f'<path class="lnk" id="lk1" d="M1330 600 L1420 600" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>'
             f'<circle class="lpu" id="lp0" r="5" fill="#fff"/><circle class="lpu" id="lp1" r="5" fill="#fff"/>')
    labs = "".join(f'<text class="dlab slab" x="{x}" y="700" text-anchor="middle">{t}</text>' for x, t in ((570, "AI 데이터센터"), (1165, "전산센터"), (1570, "ESS 공장")))
    return f'<g id="sites">{a}{b}{c}{links}{labs}</g>'


def build():
    cx, cy = 960, 430
    svg = f'''<svg class="layer" id="main" viewBox="0 0 1920 1080">
  <defs><clipPath id="vennA"><circle cx="820" cy="440" r="240"/></clipPath>
  <linearGradient id="lensg" x1="860" y1="0" x2="1060" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff3fcf"/><stop offset="1" stop-color="#6a4dff"/></linearGradient>
  <radialGradient id="fillA" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff4fd8" stop-opacity=".05"/><stop offset="1" stop-color="#ff4fd8" stop-opacity=".2"/></radialGradient>
  <radialGradient id="fillB" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#5a5cff" stop-opacity=".05"/><stop offset="1" stop-color="#5a5cff" stop-opacity=".22"/></radialGradient></defs>
  <g id="cvG"><circle cx="{cx}" cy="{cy}" r="76" fill="#15102a" stroke="#fff" stroke-opacity=".35" stroke-width="1.5"/>
    <circle id="cvRing" cx="{cx}" cy="{cy}" r="88" fill="none" stroke="#fff" stroke-width="2" transform="rotate(-90 {cx} {cy})"/>
    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="30" fill="#fff">ConvAI</text></g>
  <path class="con" d="M872 {cy} L606 {cy}" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>
  <path class="con" d="M1048 {cy} L1296 {cy}" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>
  <path class="con" d="M{cx} {cy + 88} L{cx} {cy + 168}" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"/>
  {ni_svg()}
  {sites_svg()}
  <line id="gd" x1="400" y1="{MY}" x2="1680" y2="{MY}" stroke="#fff" stroke-opacity=".16" stroke-width="1.5" stroke-dasharray="2 9"/>
  <line id="trk" x1="400" y1="{MY}" x2="400" y2="{MY}" stroke="#fff" stroke-opacity=".75" stroke-width="2"/>
  {icons()}
  {"".join(f'<g class="mk" id="mk{i}"><circle cx="{x}" cy="{MY}" r="16" fill="#0c0916" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/><circle class="mkf" id="mkf{i}" cx="{x}" cy="{MY}" r="0" fill="#fff"/></g>' for i, x in enumerate(MX))}
  <g id="venn">
    <g id="gA"><circle cx="820" cy="440" r="240" fill="url(#fillA)"/>
      <circle class="vring" cx="820" cy="440" r="240" fill="none" stroke="#ff6fdc" stroke-opacity=".85" stroke-width="2"/>
      <circle id="dA" cx="820" cy="440" r="222" fill="none" stroke="#ff6fdc" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="2 10"/>
      <g id="cA"><g class="vic">{"".join(f'<rect x="{676 + k * 13}" y="{384 - h / 2}" width="7" height="{h}" rx="3.5" fill="#ff8be6"/>' for k, h in enumerate((16, 30, 46, 34, 50, 26, 14)))}</g>
      <text class="vt" x="718" y="458" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">대화형</text>
      <text class="vt" x="718" y="500" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">AI</text></g></g>
    <g id="gB"><circle cx="1100" cy="440" r="240" fill="url(#fillB)"/>
      <circle class="vring" cx="1100" cy="440" r="240" fill="none" stroke="#8a8cff" stroke-opacity=".85" stroke-width="2"/>
      <circle id="dB" cx="1100" cy="440" r="222" fill="none" stroke="#8a8cff" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="2 10"/>
      <g id="cB"><g class="vic"><path d="M1160 362 L1206 384 L1248 360 M1206 384 L1199 410" fill="none" stroke="#a9abff" stroke-width="2.2"/>
        <circle cx="1160" cy="362" r="7" fill="#a9abff"/><circle cx="1206" cy="384" r="8" fill="#a9abff"/><circle cx="1248" cy="360" r="7" fill="#a9abff"/><circle cx="1199" cy="410" r="6" fill="#a9abff"/></g>
      <text class="vt" x="1202" y="458" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">네트워크</text>
      <text class="vt" x="1202" y="500" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">인프라</text></g></g>
    <circle id="lens" cx="1100" cy="440" r="240" fill="url(#lensg)" clip-path="url(#vennA)"/>
    <text id="tL" x="960" y="453" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="38" fill="#fff">라피치</text></g>
  <g id="dot"><circle r="14" fill="#fff" opacity=".22"/><circle r="6.5" fill="#fff"/></g>
</svg>'''
    pills = "".join(f'<div style="position:absolute;left:{x}px;top:{y - 32}px;width:0;display:flex;justify-content:center"><div class="pill" id="p{i}">{t}</div></div>'
                    for i, (x, y, t) in enumerate(((470, cy, "NLU 콜봇"), (1450, cy, "LLM AI 에이전트"), (cx, cy + 200, "AICC 구축"))))
    labs = "".join(f'<div class="cwrap mkl" id="mkl{i}" style="left:{x}px;top:{MY + 34}px"><div class="mono">{n}</div><div class="val">{t}</div></div>' for i, (x, (n, t)) in enumerate(zip(MX, STEPS)))
    dom = (f'<div class="cwrap" id="cvl" style="left:{cx}px;top:{cy - 172}px"><div class="mono">자체 대화형 AI 플랫폼</div>'
           f'<div class="mono" style="margin-top:10px;font-size:16px;letter-spacing:.12em;color:#8e86a8">조달청 우수조달물품 지정 · 2026</div></div>' + pills + labs)
    caps = "".join(cap_html(c, t, x) for c, t, x in CAPS)
    body = f'''<div class="layer vig"></div>
{svg}
<div class="layer">{dom}</div>
{caps}
<img id="prev" class="layer" src="assets/flow_last.png" />
<img id="symEnd" src="assets/symbol_purple.svg" style="position:absolute;left:{960 - 75}px;top:{540 - 80.36:.2f}px;width:150px;height:160.71px;opacity:0" />
<div id="blackout" class="layer" style="background:#0c0916"></div>'''
    css = ".pill { background: #15102a; border: 1.5px solid rgba(255,255,255,.35); }"
    js = f"""
const MX = {json_dump(MX)}, MY = {MY};
gsap.set(["#cvG", ".con", ".pill", "#cvl", "#niG", "#sites", "#gd", "#trk", ".ic", ".mk", ".mkl", "#venn", "#dot", ".cap", "#blackout"], {{ opacity: 0 }});
gsap.set("#dot", {{ x: {cx}, y: {cy}, transformOrigin: "50% 50%" }});
prep(document.getElementById("cvRing"));

// ── 1. 이전 장면이 가운데로 모이며 ConvAI 노드가 됨
__CONVAI__

// ── 2. 네트워크 인프라
const N = 7.4;
CAP("c4", N, 10.9);
tl.fromTo("#dot", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power2.out", immediateRender: false }}, 7.1);
FIN("#niG", N - 0.05, 0.2);
DR("#swb", N, 0.8); DR(".port", N + 0.2, 0.5, "power2.out", 0.03);
DR(".rk", N + 0.1, 0.9, "power2.inOut", 0.12); DR(".rslot", N + 0.4, 0.5, "power2.out", 0.008);
ALONG("#drop", "#dot", N + 0.35, 0.75);
tl.to("#dot", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, N + 1.05);
FOUT("#drop", N + 1.2, 0.6);
tl.to("#pl7", {{ attr: {{ fill: "#ff4fd8" }}, duration: 0.2 }}, N + 1.1);
gsap.utils.toArray(".pled").forEach((el, i) => {{ if (i !== 7) tl.to(el, {{ attr: {{ fill: i % 2 ? "#9d79ff" : "#5a5cff" }}, duration: 0.15 }}, N + 1.15 + (7 - i) * 0.035); }});
DECOR(".cab", {{ size: 10 }}); DR(".cab", N + 1.05, 0.6, "power2.out", 0.06);
FIN(".dk-cab0, .dk-cab1, .dk-cab2", N + 1.6, 0.3);
gsap.utils.toArray(".cab").forEach((c, r) => {{
  const L = c.getTotalLength(), q = {{ p: 0 }}, pu = document.getElementById("pu" + r);
  gsap.set(pu, {{ opacity: 0 }});
  tl.fromTo(q, {{ p: 0 }}, {{ p: 1, duration: 0.6, ease: "power1.inOut", immediateRender: false, onUpdate: () => {{ const pt = c.getPointAtLength(q.p * L); gsap.set(pu, {{ x: pt.x, y: pt.y, opacity: q.p < 0.97 ? 1 : 0 }}); }} }}, N + 1.2 + r * 0.08);
}});
gsap.set(".rled", {{ opacity: 0.12 }});
gsap.utils.toArray(".rled").forEach((el) => {{ const r = +el.classList[1].slice(1), j = +el.dataset.j; tl.to(el, {{ opacity: 1, duration: 0.15, ease: "none" }}, N + 1.65 + r * 0.06 + j * 0.03); }});
gsap.set(".dlab", {{ opacity: 0 }});
FIN(["#dl0", "#dl1"], N + 0.9, 0.5);
FOUT(["#dl0", "#dl1"], 10.8, 0.3);
tl.to("#niG", {{ scale: 0.42, x: 135.3, y: 255.5, svgOrigin: "0 0", duration: 1.3, ease: "power3.inOut" }}, 10.9);
CAP("c5", 11.4, 14.8);
FIN("#sites", 11.35, 0.05);
gsap.set([".bdet", ".lpu"], {{ opacity: 0 }});
DR(".bld", 11.4, 1.0, "power2.inOut", 0.25);
FIN(".bdet", 12.2, 0.6);
DECOR(".lnk", {{ size: 9 }}); FIN(".lnk", 12.5, 0.05); DR(".lnk", 12.5, 0.5, "power2.out", 0.1);
FIN(".dk-lk0, .dk-lk1", 12.95, 0.3);
[["#lk0", "#lp0"], ["#lk1", "#lp1"]].forEach(([p, d], i) => {{
  for (let r = 0; r < 2; r++) {{ FIN(d, 12.9 + i * 0.15 + r * 0.8, 0.05); ALONG(p, d, 12.9 + i * 0.15 + r * 0.8, 0.6, "power1.inOut", false); FOUT(d, 13.45 + i * 0.15 + r * 0.8, 0.1); }}
}});
FIN(".slab", 12.5, 0.6);
FOUT(["#niG", "#sites"], 14.8, 0.45);

// ── 3. 설계 → 구축 → 보안·관제 → 운영 (점은 y=MY 위로만 움직여 표식의 정확히 한가운데를 지남)
CAP("c6", 15.4, 21.2);
FIN(["#gd", ".mk"], 15.3, 0.6);
tl.set("#dot", {{ x: 400, y: MY, scale: 1 }}, 15.2);
FIN("#dot", 15.4, 0.4); FIN("#trk", 15.75, 0.05);
const LEG = [[15.8, 16.6], [17.2, 18.0], [18.6, 19.4], [20.0, 20.8]];
LEG.forEach(([a, b], i) => {{
  tl.to("#dot", {{ x: MX[i], duration: b - a, ease: "power2.inOut" }}, a);
  tl.to("#trk", {{ attr: {{ x2: MX[i] }}, duration: b - a, ease: "power2.inOut" }}, a);
  tl.fromTo("#mkf" + i, {{ attr: {{ r: 0 }} }}, {{ attr: {{ r: 9 }}, duration: 0.45, ease: "back.out(2)", immediateRender: false }}, b - 0.05);
  FIN("#ic" + i, b - 0.1, 0.05);
  DR("#ic" + i + " > *", b - 0.05, 0.8, "power2.out", 0.04);
  tl.fromTo("#mkl" + i, {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }}, b + 0.1);
}});
FOUT(["#gd", "#trk", ".mk", ".mkl", ".ic", "#dot"], 21.3, 0.5);

// ── 4. 두 원(AI, NI)이 겹치고, 겹친 자리가 라피치
FIN("#venn", 21.8, 0.05);
gsap.set(["#lens", "#tL", ".vt", ".vic"], {{ opacity: 0 }});
tl.fromTo("#gA", {{ x: -200, opacity: 0 }}, {{ x: -200, opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }}, 21.8);
tl.fromTo("#gB", {{ x: 200, opacity: 0 }}, {{ x: 200, opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }}, 21.95);
gsap.set("#gA", {{ x: -200 }}); gsap.set("#gB", {{ x: 200 }});
DR(".vring", 21.85, 1.0, "power2.inOut", 0.12);
tl.fromTo(".vic", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out", stagger: 0.12, immediateRender: false }}, 22.3);
tl.fromTo(".vt", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, stagger: 0.06, immediateRender: false }}, 22.45);
tl.fromTo("#dA", {{ rotation: 0, svgOrigin: "820 440" }}, {{ rotation: 60, svgOrigin: "820 440", duration: 6.6, ease: "none" }}, 21.8);
tl.fromTo("#dB", {{ rotation: 0, svgOrigin: "1100 440" }}, {{ rotation: -60, svgOrigin: "1100 440", duration: 6.6, ease: "none" }}, 21.8);
gsap.set("#cA", {{ x: 102 }}); gsap.set("#cB", {{ x: -102 }});
tl.to("#cA", {{ x: 0, duration: 1.2, ease: "power3.inOut" }}, 23.0);
tl.to("#cB", {{ x: 0, duration: 1.2, ease: "power3.inOut" }}, 23.0);
tl.to("#gA", {{ x: 0, duration: 1.2, ease: "power3.inOut" }}, 23.0);
tl.to("#gB", {{ x: 0, duration: 1.2, ease: "power3.inOut" }}, 23.0);
FIN("#lens", 24.15, 0.6, "sine.out");
FIN("#tL", 24.35, 0.5);
CAP("c7", 24.4, 27.0);
tl.to(["#cA", "#cB", "#tL"], {{ opacity: 0, duration: 0.45, ease: "sine.in" }}, 26.9);
tl.to(["#gA", "#gB"], {{ opacity: 0, duration: 0.7, ease: "sine.inOut" }}, 27.1);
tl.to("#lens", {{ scaleX: 0.35, scaleY: 0.42, opacity: 0, svgOrigin: "960 440", duration: 0.8, ease: "power3.inOut" }}, 27.3);
tl.fromTo("#symEnd", {{ opacity: 0, scale: 0.55, y: -100, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, y: 0, duration: 1.0, ease: "power3.inOut", immediateRender: false }}, 27.4);
// ── 5. 어둡게 정리 → 아웃트로
"""
    convai = """tl.to("#prev", { scale: 0.06, opacity: 0, transformOrigin: "960px 540px", duration: 1.1, ease: "power3.in" }, 0.0);
tl.fromTo("#cvG", { opacity: 0, scale: 0.6, y: 110, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, y: 110, duration: 0.8, ease: "power3.out", immediateRender: false }, 0.75);
tl.to("#cvG", { y: 0, duration: 0.8, ease: "power2.inOut" }, 1.55);
DR("#cvRing", 1.6, 1.1, "power2.inOut");
tl.to("#cvRing", { attr: { stroke: "#ff4fd8" }, duration: 0.4, ease: "sine.out" }, 2.7);
CAP("c3", 1.4, 6.5);
tl.fromTo("#cvl", { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", immediateRender: false }, 2.4);
FIN(".con", 2.6, 0.05); DR(".con", 2.6, 0.55, "power2.out", 0.15);
gsap.utils.toArray(".pill").forEach((el, i) => tl.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 2.9 + i * 0.2));
FOUT([".pill", ".con", "#cvl"], 6.5, 0.4);
tl.to("#cvG", { scale: 0.12, opacity: 0, transformOrigin: "50% 50%", duration: 0.5, ease: "power3.in" }, 6.7);"""
    if MODE == "b":
        # 앞 장면(9개 상담 그래픽)을 칸별로 잘라, 가운데 한 점으로 모은 뒤 그 점이 네트워크(스위치)로 들어감
        cells = [(cx, cy) for cy in (167, 357, 547) for cx in (400, 940, 1480)]
        convai = """
FOUT("#pvLow", 5.6, 0.45);
tl.to("#pvLow", { y: 24, duration: 0.45, ease: "power2.in" }, 5.6);
FOUT("#pvFrame", 5.7, 0.45);
tl.to("#pvFrame", { scale: 0.94, transformOrigin: "960px 365px", duration: 0.5, ease: "power2.in" }, 5.7);
"""
        order = sorted(range(9), key=lambda i: -abs(cells[i][0] - 960) - abs(cells[i][1] - 430))
        for k, i in enumerate(order):
            cx, cy = cells[i]
            t0 = 5.85 + k * 0.05
            convai += (f'tl.to("#pc{i}", {{ x: {960 - cx}, y: {430 - cy}, scale: 0.04, transformOrigin: "{cx}px {cy}px", '
                       f'duration: 0.95, ease: "power3.in" }}, {t0:.2f});\n'
                       f'tl.to("#pc{i}", {{ opacity: 0, duration: 0.2, ease: "sine.in" }}, {t0 + 0.75:.2f});\n')
        convai += """
tl.fromTo("#mglow", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.5, ease: "sine.out", immediateRender: false }, 6.5);
tl.to("#mglow", { opacity: 0, scale: 1.4, duration: 0.8, ease: "sine.inOut" }, 7.05);
tl.set("#dot", { x: 960, y: 430 }, 6.8);
tl.fromTo("#dot", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)", immediateRender: false }, 6.85);
"""
        pv = []
        pv.append('<img id="pvLow" class="layer" src="assets/convai_last.png" style="clip-path:inset(655px 0px 0px 0px)" />')
        pv.append('<img id="pvFrame" class="layer" src="assets/convai_last.png" style="clip-path:path(evenodd,\'M128 68 H1792 V662 H128 Z M152 92 V638 H1768 V92 Z\')" />')
        for i, (cx, cy) in enumerate(cells):
            l, r, t, b = cx - 262, cx + 262, cy - 88, cy + 88   # 칸 경계를 부드럽게 흐려 사각 테두리가 안 보이게
            m = (f"linear-gradient(90deg,transparent {l}px,#000 {l + 26}px,#000 {r - 26}px,transparent {r}px),"
                 f"linear-gradient(transparent {t}px,#000 {t + 22}px,#000 {b - 22}px,transparent {b}px)")
            pv.append(f'<div id="pc{i}" class="layer" style="mix-blend-mode:lighten"><img class="layer" src="assets/convai_last.png" '
                      f'style="-webkit-mask-image:{m};mask-image:{m};-webkit-mask-composite:source-in;mask-composite:intersect" /></div>')
        pv.append('<div id="mglow" style="position:absolute;left:760px;top:230px;width:400px;height:400px;border-radius:50%;'
                  'background:radial-gradient(closest-side,rgba(214,120,255,.55),rgba(140,80,255,.18) 45%,rgba(120,60,255,0));opacity:0"></div>')
        body = body.replace('<img id="prev" class="layer" src="assets/flow_last.png" />', "\n".join(pv))
    js = js.replace("__CONVAI__", convai)
    if MODE == "b":
        js = js.replace('tl.fromTo("#dot", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.35, ease: "power2.out", immediateRender: false }, 7.1);', "")
    return page("Rapeech brand film v3 (rest)", body, js, DUR, css,
                audio=f'<audio id="sfx" class="clip" src="assets/rest_sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def json_dump(v):
    import json
    return json.dumps(v)


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int((DUR + 1) * SR), 2))

    def chime(t, g=0.11, hi=False):
        a, b = (91, 98) if hi else (88, 95)
        add(buf, bell(a, 0.9, 0.35), t, g); add(buf, bell(b, 1.2, 0.5), t + 0.08, g * 0.92)

    def whoosh(t, up=True, g=0.035, d=0.8):
        add(buf, sweep(220 if up else 900, 900 if up else 220, d, partials=((1, 1), (2, 0.3)), a=0.1, r=0.2, rise=up), t, g)

    if MODE == "b":
        whoosh(5.8, False, 0.04, 1.0); add(buf, pop(700, 340, 0.12), 6.85, 0.09); add(buf, bell(93, 0.8, 0.3), 6.88, 0.05)
    else:
        whoosh(0.0, False, 0.045, 1.1); add(buf, pop(760, 380, 0.14), 0.85, 0.08)
    if MODE != "b":
        chime(2.7, 0.11, hi=True)
        for i in range(3):
            add(buf, pop(820, 380), 2.9 + i * 0.2, 0.06)
    whoosh(6.7, False, 0.04, 0.6); add(buf, pop(620, 260, 0.12), 8.5, 0.14)
    for r in range(3):
        add(buf, sweep(500, 1500, 0.55, partials=((1, 1),), a=0.06, r=0.12, rise=True), 8.6 + r * 0.08, 0.015)
    for i in range(10):
        add(buf, tone(hz(91 + (i % 4) * 2), 0.07, ((1, 1),), a=0.003, r=0.04, decay=0.05), 9.05 + i * 0.045, 0.022, (i % 3 - 1) * 0.4)
    whoosh(10.9, False, 0.05, 1.3)
    for i in range(3):
        add(buf, tone(hz(43 + i), 0.45, ((1, 1), (2, 0.4), (3, 0.12)), a=0.005, r=0.1, decay=0.2), 11.5 + i * 0.25, 0.09)
    for a, b in [[15.8, 16.6], [17.2, 18.0], [18.6, 19.4], [20.0, 20.8]]:
        whoosh(a, True, 0.02, b - a + 0.2); add(buf, pop(900, 500, 0.08), b, 0.07)
    chime(20.85, 0.09)
    whoosh(23.0, True, 0.035, 1.2)
    add(buf, tone(hz(36), 1.4, ((1, 1), (2, 0.3)), a=0.005, r=0.5, decay=0.5), 24.15, 0.26)
    for m in (60, 64, 67, 71, 74):
        add(buf, tone(hz(m + 12), 2.4, ((1, 1), (2, 0.15)), a=0.01, r=0.9, decay=1.2), 24.15, 0.04)
    chime(24.15, 0.11, hi=True)
    buf = lowpass(buf, 10000)[: int(DUR * SR)]
    buf *= 10 ** (-3 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    if MODE == "b":
        HERE = HERE.parent / "brand-film-v3b"
        HERE.mkdir(exist_ok=True)
    a = setup_project(HERE, "brand-film-v3" + MODE, [(FILM / "assets" / "brand" / "symbol_purple.svg", "symbol_purple.svg")])
    if MODE == "b":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.02", "-i", str(REPO / "video" / "convai-samples" / "b" / "out" / "raw.mp4"), "-frames:v", "1", "-update", "1", str(a / "convai_last.png")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{12 + FLOW_CUT:.3f}", "-i", str(FILM / "out" / "raw.mp4"), "-frames:v", "1", str(a / "flow_last.png")], check=True)
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "rest_sfx.wav")
    print("ok")
