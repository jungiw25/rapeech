"""인트로 v2: 앞부분(0–6.95초)을 '회사가 하는 일'이 보이게 새로 만들고, 6.95초부터는 기존 인트로(로고)를 그대로 붙인다.

구체적인 상담 문장 없이, 장면 두 개를 여유 있게(장면 사이 쉼 포함) 보여 준다.
  0.0–1.1  선이 그어짐
  1.0–4.4  고객 목소리(왼쪽 파형) → 가운데 AI 콜봇이 듣고 인식(고리가 차오름) → AI 콜봇이 목소리로 답함(오른쪽 파형)
           소제목: 대화형 AI · 고객의 목소리를 [AI 콜봇이 알아듣고] 답합니다
  4.4–6.95 대화가 빛 하나로 모여 케이블 → 스위치 포트 → 서버 랙
           소제목: 네트워크 인프라 · 그 대화가 흐르는 [네트워크 인프라]까지
  6.95–12  기존 인트로 그대로(원형 와이프 → 로고). 7.5초부터는 기존 인트로 프레임을 그대로 이어 붙여 마지막 프레임이 같다
사용법: python3 video/intro-v2/build.py && cd video/intro-v2 && npx hyperframes render --fps 60 --quality delivery --output out/raw.mp4
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FILM = REPO / "video" / "brand-film"
CUT = 6.95
sys.path.insert(0, str(REPO))

FONT_CSS = "".join(f'@font-face {{ font-family: "Pretendard"; font-weight: {w}; src: url("assets/fonts/Pretendard-{n}.otf"); }}\n'
                   for w, n in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")))

G = ["#ff03c8", "#e807c3", "#d10bbd", "#ba0fb8", "#a518a4", "#8f1ab8", "#7a1dcc", "#661fdc", "#5422e6", "#4823ee", "#4024f1", "#3c24f3"]
CAPS = [("대화형 AI", "고객의 목소리를 [AI 콜봇이 알아듣고] 답합니다", 1.25, 4.25),
        ("네트워크 인프라", "그 대화가 흐르는 [네트워크 인프라]까지", 4.65, None)]
LY = 420                       # 대화 장면의 가로선 높이
CX, BR = 960, 74               # AI 콜봇 노드


def cap_html(i, tag, text):
    t = text
    while "[" in t:
        a, b = t.index("["), t.index("]")
        t = t[:a] + f'<span class="g">{t[a + 1:b]}</span>' + t[b + 1:]
    return (f'<div class="cap" id="cap{i}"><div class="tag"><span class="cl{i}">{tag}</span></div>'
            f'<div class="ct"><span class="cl{i}">{t}</span></div></div>')


def wave(cls, x0, n=10, gap=30, colors=G[:10]):
    return "".join(f'<div class="bar {cls}" style="left:{x0 + k * gap - 6:.0f}px;background:{colors[k]};color:{colors[k]}"></div>' for k in range(n))


def build_html():
    left = wave("cb", 360, colors=G[:6] + G[:4])            # 고객(분홍 쪽)
    right = wave("ab", 1290, colors=G[6:] + G[6:12])         # AI 콜봇(파랑 쪽)
    ports = "".join(f'<rect class="port" x="{420 + i * 52}" y="452" width="34" height="26" rx="4" fill="#0c0916" stroke="#fff" stroke-opacity=".55" stroke-width="1.4"/>'
                    f'<circle class="pled" id="pl{i}" cx="{437 + i * 52}" cy="440" r="4" fill="#3a3158"/>' for i in range(8))
    racks, rleds = "", ""
    for r, rx in enumerate((1180, 1360, 1540)):
        racks += f'<rect class="rk" x="{rx}" y="300" width="140" height="300" rx="10" fill="#120d24" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>'
        for j in range(9):
            y = 570 - j * 30
            racks += f'<rect class="rslot" x="{rx + 16}" y="{y - 9}" width="108" height="18" rx="4" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1"/>'
            rleds += f'<rect class="rled r{r}" data-j="{j}" x="{rx + 24}" y="{y - 2}" width="{36 + (j * 17 + r * 7) % 44}" height="4" rx="2" fill="{G[min(11, 2 + r * 4 + j % 3)]}"/>'
    cables = "".join(f'<path class="cab" id="cab{r}" d="M890 465 C 1010 465, 1060 {350 + r * 110}, {1180 + r * 180} {350 + r * 110}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>'
                     for r in range(3))
    pulses = "".join(f'<circle class="pulse" id="pu{r}" r="7" fill="#fff" filter="url(#gl)"/>' for r in range(3))
    talk = f'''<svg id="talk" class="layer" viewBox="0 0 1920 1080">
  <defs><linearGradient id="ring" x1="{CX - BR}" y1="0" x2="{CX + BR}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <radialGradient id="nodeg" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#2a1f55"/><stop offset="1" stop-color="#140f2a"/></radialGradient>
  <filter id="gl2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="stream" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff4fd8" stop-opacity="0"/><stop offset="1" stop-color="#ffd2f5"/></linearGradient></defs>
  <line id="axL" x1="{CX - BR - 18}" y1="{LY}" x2="{CX - BR - 18}" y2="{LY}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>
  <line id="axR" x1="{CX + BR + 18}" y1="{LY}" x2="{CX + BR + 18}" y2="{LY}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>
  <rect id="streamIn" x="-90" y="{LY - 2}" width="90" height="4" rx="2" fill="url(#stream)"/>
  <g id="node"><circle cx="{CX}" cy="{LY}" r="{BR}" fill="url(#nodeg)" stroke="#fff" stroke-opacity=".25" stroke-width="1.5"/>
    <circle id="ringFill" cx="{CX}" cy="{LY}" r="{BR + 12}" fill="none" stroke="url(#ring)" stroke-width="5" stroke-linecap="round" transform="rotate(-90 {CX} {LY})" filter="url(#gl2)"/>
    <circle id="flashIn" cx="{CX}" cy="{LY}" r="{BR}" fill="#fff"/>
    <circle id="flashRing" cx="{CX}" cy="{LY}" r="{BR + 12}" fill="none" stroke="#fff" stroke-width="2"/>
    <text x="{CX}" y="{LY + 13}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="38" fill="#fff">AI</text></g>
</svg>'''
    ni = f'''<svg id="ni" class="layer" viewBox="0 0 1920 1080">
  <defs><filter id="gl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <path id="drop" d="M960 420 C 960 470, 790 380, 801 452" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>
  <g id="sw"><rect id="swb" x="390" y="425" width="500" height="80" rx="12" fill="#120d24" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/>{ports}</g>
  {cables}<g id="racks">{racks}</g>{rleds}{pulses}
  <text class="dlab" id="dl0" x="640" y="550" text-anchor="middle">스위치</text>
  <text class="dlab" id="dl1" x="1430" y="640" text-anchor="middle">서버 랙 · AI 데이터센터</text>
</svg>
<svg class="layer" viewBox="0 0 1920 1080"><defs><radialGradient id="dotg"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#ff8be6" stop-opacity=".8"/><stop offset="1" stop-color="#ff4fd8" stop-opacity="0"/></radialGradient></defs>
  <g id="dot"><circle r="34" fill="url(#dotg)"/><circle r="8" fill="#fff"/></g></svg>'''
    caps = "".join(cap_html(i, tag, text) for i, (tag, text, _, _) in enumerate(CAPS))
    who = lambda i, x, label, bg: (f'<div style="position:absolute;left:{x}px;top:{LY - 150}px;width:0;display:flex;justify-content:center">'
                                   f'<div class="who" id="who{i}" style="{bg}">{label}</div></div>')
    js = f"""
const tl = gsap.timeline({{ paused: true }});
const CAPS = {json.dumps([[c[2], c[3]] for c in CAPS])}, LY = {LY}, CX = {CX}, BR = {BR};
const hsh = (a, b) => {{ let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }};
const DR = (sel, t, d, e = "power2.inOut", s = 0) => gsap.utils.toArray(sel).forEach((el, i) => {{
  const L = el.getTotalLength(); el.setAttribute("stroke-dasharray", `${{L}} ${{L}}`);
  tl.fromTo(el, {{ attr: {{ "stroke-dashoffset": L }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: d, ease: e }}, t + i * s);
}});
// 말하는 파형: 정해진 높이 사이를 부드럽게 오감(시드 고정)
const speak = (sel, t0, t1, seed, step = 0.24) => gsap.utils.toArray(sel).forEach((el, k) => {{
  let t = t0, s = 0;
  while (t < t1) {{ tl.to(el, {{ scaleY: 0.2 + 0.8 * hsh(k + seed, ++s) * Math.sin(Math.PI * (k + 0.5) / 10), duration: step, ease: "sine.inOut" }}, t); t += step; }}
}});
gsap.set(".bar", {{ scaleY: 0.05, opacity: 0 }});
gsap.set(["#who0", "#who1", "#ni", ".cap", ".dlab", "#streamIn"], {{ opacity: 0 }});
gsap.set("#node", {{ scale: 0, transformOrigin: "{CX}px {LY}px" }});
// ── 0. 선 하나가 천천히 그어짐
tl.fromTo("#line", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.1, ease: "power2.inOut" }}, 0.0);
// ── 1. 선이 가운데에서 열리며 AI 콜봇 노드가 생기고, 양쪽은 대화의 축이 됨
tl.to("#line", {{ opacity: 0, duration: 0.6, ease: "sine.inOut" }}, 1.05);
tl.to("#node", {{ scale: 1, duration: 0.9, ease: "power3.out" }}, 1.0);
tl.fromTo("#axL", {{ attr: {{ x1: {CX - BR - 18} }} }}, {{ attr: {{ x1: 330 }}, duration: 0.9, ease: "power2.out" }}, 1.05);
tl.fromTo("#axR", {{ attr: {{ x2: {CX + BR + 18} }} }}, {{ attr: {{ x2: 1590 }}, duration: 0.9, ease: "power2.out" }}, 1.05);
// 고객의 목소리(왼쪽)
tl.fromTo("#who0", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out", immediateRender: false }}, 1.35);
tl.fromTo(".cb", {{ opacity: 0, scaleY: 0.05 }}, {{ opacity: 1, scaleY: 0.3, duration: 0.5, ease: "power2.out", stagger: 0.03, immediateRender: false }}, 1.4);
speak(".cb", 1.9, 3.2, 0);
tl.to(".cb", {{ scaleY: 0.08, duration: 0.5, ease: "sine.inOut" }}, 3.25);
// 목소리가 선을 타고 AI 콜봇으로 들어가며 고리가 차오름(=인식)
tl.fromTo("#streamIn", {{ x: 330, opacity: 0 }}, {{ x: {CX - BR - 18}, opacity: 1, duration: 1.0, ease: "power1.in", immediateRender: false }}, 1.95);
tl.to("#streamIn", {{ opacity: 0, duration: 0.2 }}, 2.95);
DR("#ringFill", 2.0, 1.4, "power2.inOut");
// 게이지가 다 차면 띠링과 함께 반짝(크기는 그대로)
gsap.set(["#flashIn", "#flashRing"], {{ opacity: 0 }});
tl.fromTo("#flashIn", {{ opacity: 0 }}, {{ opacity: 0.55, duration: 0.08, ease: "none", immediateRender: false }}, 3.38);
tl.to("#flashIn", {{ opacity: 0, duration: 0.6, ease: "power2.out" }}, 3.46);
tl.fromTo("#flashRing", {{ opacity: 0.9, attr: {{ r: {BR + 12} }} }}, {{ opacity: 0, attr: {{ r: {BR + 46} }}, duration: 0.8, ease: "power2.out", immediateRender: false }}, 3.38);
tl.fromTo("#ringFill", {{ attr: {{ "stroke-width": 5 }} }}, {{ attr: {{ "stroke-width": 8 }}, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, 3.38);
// AI 콜봇이 목소리로 답함(오른쪽)
tl.fromTo("#who1", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out", immediateRender: false }}, 3.35);
tl.fromTo(".ab", {{ opacity: 0, scaleY: 0.05 }}, {{ opacity: 1, scaleY: 0.3, duration: 0.5, ease: "power2.out", stagger: 0.03, immediateRender: false }}, 3.4);
speak(".ab", 3.9, 4.4, 50);
// ── 2. 대화가 빛 하나로 모여 케이블 → 스위치 포트 → 서버 랙
tl.to([".cb", ".ab"], {{ x: (k, el) => CX - parseFloat(el.style.left) - 6, scaleY: 0.05, opacity: 0, duration: 0.6, ease: "power3.inOut" }}, 4.35);
tl.to(["#who0", "#who1", "#axL", "#axR"], {{ opacity: 0, duration: 0.45, ease: "sine.inOut" }}, 4.35);
tl.to("#node", {{ scale: 0.12, opacity: 0, duration: 0.55, ease: "power3.in" }}, 4.45);
gsap.set("#dot", {{ x: CX, y: LY, scale: 0, opacity: 0 }});
tl.fromTo("#dot", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "power2.out", immediateRender: false }}, 4.85);
tl.fromTo("#ni", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, immediateRender: false }}, 4.75);
DR("#swb", 4.8, 0.8); DR(".port", 5.0, 0.5, "power2.out", 0.03);
DR(".rk", 4.9, 0.9, "power2.inOut", 0.12); DR(".rslot", 5.2, 0.5, "power2.out", 0.008);
const drop = document.getElementById("drop"), DL = drop.getTotalLength();
drop.setAttribute("stroke-dasharray", `${{DL}} ${{DL}}`); drop.setAttribute("stroke-dashoffset", DL);
const pd = {{ p: 0 }}, putDot = () => {{ const pt = drop.getPointAtLength(pd.p * DL); gsap.set("#dot", {{ x: pt.x, y: pt.y }}); drop.setAttribute("stroke-dashoffset", DL * (1 - pd.p)); }};
tl.fromTo(pd, {{ p: 0 }}, {{ p: 1, duration: 0.75, ease: "power2.inOut", onUpdate: putDot, immediateRender: false }}, 5.15);
tl.to("#dot", {{ scale: 0.4, opacity: 0, duration: 0.3, ease: "power2.in" }}, 5.85);
tl.to("#drop", {{ opacity: 0, duration: 0.6, ease: "sine.inOut" }}, 6.0);
tl.to("#pl7", {{ attr: {{ fill: "#ff4fd8" }}, duration: 0.2 }}, 5.9);
gsap.utils.toArray(".pled").forEach((el, i) => {{ if (i !== 7) tl.to(el, {{ attr: {{ fill: i % 2 ? "#9d79ff" : "#5a5cff" }}, duration: 0.15 }}, 5.95 + (7 - i) * 0.035); }});
DR(".cab", 5.85, 0.6, "power2.out", 0.06);
gsap.utils.toArray(".cab").forEach((c, r) => {{
  const L = c.getTotalLength(), q = {{ p: 0 }}, pu = document.getElementById("pu" + r);
  gsap.set(pu, {{ opacity: 0 }});
  tl.fromTo(q, {{ p: 0 }}, {{ p: 1, duration: 0.6, ease: "power1.inOut", immediateRender: false, onUpdate: () => {{ const pt = c.getPointAtLength(q.p * L); gsap.set(pu, {{ x: pt.x, y: pt.y, opacity: q.p < 0.97 ? 1 : 0 }}); }} }}, 6.0 + r * 0.08);
}});
gsap.set(".rled", {{ opacity: 0.12 }});
gsap.utils.toArray(".rled").forEach((el) => {{ const r = +el.classList[1].slice(1), j = +el.dataset.j; tl.to(el, {{ opacity: 1, duration: 0.15, ease: "none" }}, 6.45 + r * 0.06 + j * 0.03); }});
tl.fromTo(".dlab", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, stagger: 0.15, immediateRender: false }}, 5.7);
// ── 한글 소제목: 두 번만 바뀜(줄 마스크로 천천히)
CAPS.forEach(([a, b], i) => {{
  tl.fromTo("#cap" + i, {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, a);
  tl.fromTo(".cl" + i, {{ yPercent: 120 }}, {{ yPercent: 0, duration: 1.0, ease: "expo.out", stagger: 0.08 }}, a);
  if (b) tl.to(".cl" + i, {{ yPercent: -120, duration: 0.45, ease: "power2.in", stagger: 0.04 }}, b);
}});
// ── 6.95 원형 와이프: 기존 인트로(로고)가 가운데서 열림(기존 인트로와 같은 곡선)
gsap.set("#logo", {{ clipPath: "circle(0px at 960px 540px)" }});
tl.fromTo("#logo", {{ clipPath: "circle(0px at 960px 540px)" }}, {{ clipPath: "circle(1200px at 960px 540px)", duration: 0.55, ease: "power2.out", immediateRender: false }}, {CUT});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
"""
    return f"""<!doctype html>
<html lang="ko" data-resolution="landscape">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>Rapeech intro v2</title>
<script src="assets/gsap.min.js"></script>
<style>{FONT_CSS}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0c0916; }}
#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: "Pretendard", sans-serif; background: #0c0916; }}
.layer {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
.vig {{ background: radial-gradient(ellipse at 50% 45%, rgba(60,36,243,.10), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.45)); }}
#line {{ position: absolute; left: 330px; top: {LY - 1}px; width: 1260px; height: 2px; background: linear-gradient(90deg, rgba(255,3,200,0), #ff03c8 20%, #a518a4 50%, #3c24f3 80%, rgba(60,36,243,0)); transform-origin: 50% 50%; }}
.bar {{ position: absolute; top: {LY}px; width: 12px; height: 220px; margin-top: -110px; border-radius: 6px; box-shadow: 0 0 14px currentColor; }}
.who {{ position: relative; flex: none; height: 40px; padding: 0 18px; border-radius: 20px; font-size: 20px; font-weight: 700; line-height: 40px; white-space: nowrap; }}
.cap {{ position: absolute; left: 0; top: 760px; width: 1920px; text-align: center; }}
.tag {{ overflow: hidden; font-size: 20px; font-weight: 600; letter-spacing: 0.24em; color: #b5abd8; padding-bottom: 4px; }}
.ct {{ overflow: hidden; margin-top: 16px; font-size: 52px; font-weight: 800; color: #fff; letter-spacing: -0.03em; padding-bottom: 8px; }}
.tag span, .ct span[class^="cl"] {{ display: inline-block; }}
.g {{ background: linear-gradient(100deg, #ff4fd8, #b25cff 55%, #7a6bff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.dlab {{ font-family: "Pretendard"; font-weight: 600; font-size: 20px; letter-spacing: 3px; fill: #cfc6ec; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="12" data-fps="60" data-width="1920" data-height="1080">
  <div id="front" class="layer">
    <div class="layer vig"></div>
    <div id="line"></div>
    {talk}
    {who(0, 495, "고객", "background:#fff;color:#1b1530")}
    {who(1, 1425, "AI 콜봇", "background:linear-gradient(100deg,#ff03c8,#a518a4 50%,#3c24f3);color:#fff")}
    {left}{right}
    {ni}
    {caps}
  </div>
  <video id="logo" class="clip layer" src="assets/intro.mp4" data-start="{CUT}" data-duration="{12 - CUT:.2f}" data-media-start="{CUT}" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index: 5"></video>
  <audio id="sfx" class="clip" src="assets/front_sfx.wav" data-start="0" data-duration="12" data-track-index="2" data-volume="1"></audio>
</div>
<script>{js}</script>
</body></html>"""


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int(12 * SR), 2))
    add(buf, sweep(240, 760, 1.1, partials=((1, 1), (2, 0.3)), a=0.15, r=0.3, rise=True), 0.0, 0.04)
    add(buf, pop(760, 380, 0.14), 1.05, 0.08)                              # AI 콜봇 노드
    for i, m in enumerate([76, 79, 81, 79, 84, 81]):                      # 고객 목소리(짧은 음)
        add(buf, tone(hz(m), 0.2, ((1, 1), (2, 0.2)), a=0.015, r=0.08, decay=0.15), 1.9 + i * 0.24, 0.045, -0.35)
    add(buf, sweep(400, 1100, 1.4, partials=((1, 1), (2, 0.2)), a=0.3, r=0.3, rise=True), 2.0, 0.025)   # 고리가 차오름
    add(buf, bell(88, 0.9, 0.35), 3.38, 0.12); add(buf, bell(95, 1.2, 0.5), 3.46, 0.11)                # 인식 완료(띠링)
    for i, m in enumerate([84, 81, 86]):                                   # AI 대답
        add(buf, tone(hz(m), 0.2, ((1, 1), (2, 0.15)), a=0.015, r=0.08, decay=0.15), 3.9 + i * 0.24, 0.045, 0.35)
    add(buf, sweep(900, 240, 0.7, partials=((1, 1), (2, 0.3)), a=0.06, r=0.2, rise=False), 4.4, 0.045)
    add(buf, pop(620, 260, 0.12), 5.88, 0.15)                              # 포트에 꽂힘
    for r in range(3):
        add(buf, sweep(500, 1500, 0.55, partials=((1, 1),), a=0.06, r=0.12, rise=True), 6.0 + r * 0.08, 0.016)
    for i in range(10):                                                    # 랙 LED
        add(buf, tone(hz(91 + (i % 4) * 2), 0.07, ((1, 1),), a=0.003, r=0.04, decay=0.05), 6.45 + i * 0.045, 0.026, (i % 3 - 1) * 0.4)
    buf = lowpass(buf, 10000)
    buf *= 10 ** (-4 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = HERE / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (FILM / "assets" / "fonts").glob("Pretendard-*"):
        shutil.copy(f, a / "fonts" / f.name)
    shutil.copy(FILM / "assets" / "gsap.min.js", a / "gsap.min.js")
    shutil.copy(REPO / "intro" / "out" / "rapeech_intro_16x9.mp4", a / "intro.mp4")
    shutil.copy(FILM / "hyperframes.json", HERE / "hyperframes.json")
    (HERE / "meta.json").write_text(json.dumps({"id": "intro-v2", "name": "intro-v2"}))
    (HERE / "index.html").write_text(build_html(), encoding="utf-8")
    sound(a / "front_sfx.wav")
    print("ok")
