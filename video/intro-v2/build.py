"""인트로 v2: 앞부분(0–6.95초)을 '회사가 하는 일'이 보이게 새로 만들고, 6.95초부터는 기존 인트로(로고)를 그대로 붙인다.

이야기(한 줄의 선이 모양만 바꿔 가며 이어짐):
  0.0–0.9  선이 그어짐
  0.9–2.3  고객 목소리 파형 → 막대가 글자 "카드를 잃어버렸어요"로 모임   01 음성 인식 / AI가 목소리를 알아듣고
  2.3–3.3  핵심 단어에 밑줄 → 문장이 "카드 분실 신고" 태그로 정리      02 의도 파악 / 무엇을 원하는지 이해한 뒤
  3.3–4.6  태그가 AI 콜봇의 대답 파형으로, 아래에 대답이 글자로        03 AI 콜봇 / 목소리로 바로 답합니다
  4.6–6.95 대답이 빛 하나로 모여 케이블 → 스위치 포트 → 서버 랙         04 네트워크 인프라 / 그 대화가 흐르는 인프라까지
  6.95–12  기존 인트로 그대로(원형 와이프 → 로고, 마지막 프레임 = 아웃트로 마지막 프레임)
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
SENT = "카드를 잃어버렸어요"
ANS = "분실 신고, 바로 도와드릴게요"
CAPS = [("01  음성 인식", "AI가 [목소리를 알아듣고]", 0.95, 2.25),
        ("02  의도 파악", "[무엇을 원하는지] 이해한 뒤", 2.35, 3.25),
        ("03  AI 콜봇", "[목소리로] 바로 답합니다", 3.35, 4.55),
        ("04  네트워크 인프라", "그 대화가 흐르는 [네트워크 인프라]까지", 4.7, None)]


def cap_html(i, tag, text):
    t = text
    while "[" in t:
        a, b = t.index("["), t.index("]")
        t = t[:a] + f'<span class="g">{t[a + 1:b]}</span>' + t[b + 1:]
    return (f'<div class="cap" id="cap{i}"><div class="tag"><span class="cl{i}">{tag}</span></div>'
            f'<div class="ct"><span class="cl{i}">{t}</span></div></div>')


def build_html():
    bars = "".join(f'<div class="bar" id="b{k}" style="left:{960 + (k - 5.5) * 34 - 7:.0f}px;background:{G[k]};color:{G[k]}"></div>' for k in range(12))
    abars = "".join(f'<div class="bar abar" id="a{k}" style="left:{960 + (k - 5.5) * 34 - 7:.0f}px;background:{G[k]};color:{G[k]}"></div>' for k in range(12))
    sent = "".join(f'<span class="ch" id="s{i}">{"&nbsp;" if c == " " else c}</span>' for i, c in enumerate(SENT))
    ans = "".join(f'<span class="ach">{"&nbsp;" if c == " " else c}</span>' for c in ANS)
    # 스위치(정면) + 서버 랙 3대
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
    ni = f'''<svg id="ni" class="layer" viewBox="0 0 1920 1080">
  <defs><filter id="gl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="dotg"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#ff8be6" stop-opacity=".8"/><stop offset="1" stop-color="#ff4fd8" stop-opacity="0"/></radialGradient></defs>
  <path id="drop" d="M960 420 C 960 470, 790 380, 801 452" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2"/>
  <g id="sw"><rect id="swb" x="390" y="425" width="500" height="80" rx="12" fill="#120d24" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/>{ports}</g>
  {cables}<g id="racks">{racks}</g>{rleds}{pulses}
  <text class="dlab" id="dl0" x="640" y="550" text-anchor="middle">스위치</text>
  <text class="dlab" id="dl1" x="1430" y="640" text-anchor="middle">서버 랙 · AI 데이터센터</text>
  <g id="dot"><circle r="34" fill="url(#dotg)"/><circle r="8" fill="#fff"/></g>
</svg>'''
    caps = "".join(cap_html(i, tag, text) for i, (tag, text, _, _) in enumerate(CAPS))
    html = f"""<!doctype html>
<html lang="ko" data-resolution="landscape">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>Rapeech intro v2</title>
<script src="assets/gsap.min.js"></script>
<style>{FONT_CSS}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0c0916; }}
#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: "Pretendard", sans-serif; background: #0c0916; }}
.layer {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
.vig {{ background: radial-gradient(ellipse at 50% 45%, rgba(60,36,243,.10), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.45)); }}
#line {{ position: absolute; left: 360px; top: 419px; width: 1200px; height: 2px; background: linear-gradient(90deg, rgba(255,3,200,0), #ff03c8 20%, #a518a4 50%, #3c24f3 80%, rgba(60,36,243,0)); transform-origin: 50% 50%; }}
.bar {{ position: absolute; top: 420px; width: 14px; height: 200px; margin-top: -100px; border-radius: 7px; box-shadow: 0 0 16px currentColor; }}
.who {{ position: absolute; top: 272px; height: 40px; padding: 0 18px; border-radius: 20px; font-size: 20px; font-weight: 700; line-height: 40px; white-space: nowrap; }}
#sent {{ position: absolute; left: 0; top: 386px; width: 1920px; text-align: center; font-size: 64px; font-weight: 800; color: #fff; letter-spacing: -0.02em; white-space: nowrap; }}
.ch {{ display: inline-block; position: relative; }}
.ul {{ position: absolute; left: 0; bottom: -8px; height: 6px; width: 100%; border-radius: 3px; background: linear-gradient(90deg, #ff03c8, #6a4dff); transform-origin: 0 50%; }}
#chip {{ position: absolute; left: 960px; top: 420px; }}
#chipi {{ position: absolute; left: 0; top: 0; transform: translate(-50%, -50%); display: flex; align-items: center; gap: 16px; height: 92px; padding: 0 40px 0 30px; border-radius: 46px; white-space: nowrap;
  background: rgba(28,23,48,.9); border: 2px solid transparent; background-clip: padding-box; box-shadow: 0 0 0 2px rgba(157,121,255,.55); font-size: 44px; font-weight: 800; color: #fff; }}
#ans {{ position: absolute; left: 0; top: 560px; width: 1920px; text-align: center; font-size: 40px; font-weight: 700; color: #fff; white-space: nowrap; }}
.ach {{ display: inline-block; }}
.cap {{ position: absolute; left: 0; top: 780px; width: 1920px; text-align: center; }}
.tag {{ overflow: hidden; font-size: 19px; font-weight: 600; letter-spacing: 0.24em; color: #a69cc8; padding-bottom: 4px; }}
.ct {{ overflow: hidden; margin-top: 14px; font-size: 50px; font-weight: 800; color: #fff; letter-spacing: -0.03em; padding-bottom: 8px; }}
.tag span, .ct span[class^="cl"] {{ display: inline-block; }}
.g {{ background: linear-gradient(100deg, #ff4fd8, #b25cff 55%, #7a6bff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.dlab {{ font-family: "Pretendard"; font-weight: 600; font-size: 20px; letter-spacing: 3px; fill: #cfc6ec; }}
#wipe {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="12" data-fps="60" data-width="1920" data-height="1080">
  <div id="front" class="layer">
    <div class="layer vig"></div>
    <div id="line"></div>
    <div style="position:absolute;left:960px;top:272px;width:0;display:flex;justify-content:center"><div class="who" id="who1" style="position:relative;top:0;flex:none;background:#fff;color:#1b1530">고객</div></div>
    {bars}
    <div id="sent">{sent}</div>
    <div id="chip"><div id="chipi"><svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="url(#ckg)"/><path d="M11 20.5 l6 6 l12 -13" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="ckg" x1="0" y1="0" x2="40" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset="1" stop-color="#3c24f3"/></linearGradient></defs></svg>카드 분실 신고</div></div>
    <div style="position:absolute;left:960px;top:272px;width:0;display:flex;justify-content:center"><div class="who" id="who2" style="position:relative;top:0;flex:none;background:linear-gradient(100deg,#ff03c8,#a518a4 50%,#3c24f3);color:#fff">AI 콜봇</div></div>
    {abars}
    <div id="ans">{ans}</div>
    {ni}
    {caps}
  </div>
  <video id="logo" class="clip layer" src="assets/intro.mp4" data-start="{CUT}" data-duration="{12 - CUT:.2f}" data-media-start="{CUT}" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index: 5"></video>
  <audio id="sfx" class="clip" src="assets/front_sfx.wav" data-start="0" data-duration="12" data-track-index="2" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const SENT = {json.dumps(SENT, ensure_ascii=False)}, CAPS = {json.dumps([[c[2], c[3]] for c in CAPS])};
const hsh = (a, b) => {{ let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }};
// ── 0. 선
tl.fromTo("#line", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, duration: 0.9, ease: "power3.inOut" }}, 0.05);
// ── 1. 고객 목소리 파형(선에서 막대가 솟음)
gsap.set(".bar", {{ scaleY: 0.04, opacity: 0 }});
gsap.set(["#who1", "#who2", "#sent .ch", "#chip", ".abar", ".ach", "#ni", ".cap"], {{ opacity: 0 }});
tl.to("#line", {{ opacity: 0, duration: 0.4, ease: "sine.inOut" }}, 0.75);
gsap.utils.toArray("#front > .bar:not(.abar)").forEach((el, k) => {{
  tl.fromTo(el, {{ opacity: 0, scaleY: 0.04 }}, {{ opacity: 1, scaleY: 0.25, duration: 0.3, ease: "power2.out", immediateRender: false }}, 0.8 + k * 0.012);
  let t = 1.05; for (let s = 0; s < 4; s++) {{ tl.to(el, {{ scaleY: 0.18 + 0.82 * hsh(k, s + 1) * Math.sin(Math.PI * (k + 0.5) / 12), duration: 0.16, ease: "sine.inOut" }}, t); t += 0.16; }}
}});
tl.fromTo("#who1", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out", immediateRender: false }}, 0.95);
// 막대가 글자 자리로 날아가 글자가 됨(글자 위치는 글꼴이 준비된 뒤 측정)
function build() {{
  const chars = gsap.utils.toArray("#sent .ch"), rootR = document.getElementById("root").getBoundingClientRect();
  const cx = chars.map((c) => {{ const r = c.getBoundingClientRect(); return r.left - rootR.left + r.width / 2; }});
  gsap.utils.toArray("#front > .bar:not(.abar)").forEach((el, k) => {{
    const ci = Math.round(k * (chars.length - 1) / 11), x0 = 960 + (k - 5.5) * 34;
    tl.to(el, {{ x: cx[ci] - x0, scaleY: 0.3, scaleX: 0.45, duration: 0.45, ease: "power3.inOut" }}, 1.7 + k * 0.012);
    tl.to(el, {{ opacity: 0, duration: 0.2, ease: "sine.in" }}, 2.05 + k * 0.012);
  }});
  chars.forEach((c, i) => tl.fromTo(c, {{ opacity: 0, y: 14, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "power3.out", immediateRender: false }}, 1.95 + i * 0.025));
  // ── 2. 핵심 단어 밑줄 → 문장이 태그로 정리
  ["s0", "s4"].forEach((id, j) => {{
    const a = document.getElementById(id), last = j ? chars[chars.length - 1] : chars[2];
    const ra = a.getBoundingClientRect(), rb = last.getBoundingClientRect();
    const ul = document.createElement("div"); ul.className = "ul"; ul.style.width = (rb.right - ra.left) + "px"; a.appendChild(ul);
    tl.fromTo(ul, {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.inOut" }}, 2.35 + j * 0.15);
  }});
  tl.to("#who1", {{ opacity: 0, duration: 0.3 }}, 2.35);
  tl.to("#sent", {{ scaleX: 0.3, opacity: 0, filter: "blur(8px)", duration: 0.32, ease: "power3.in" }}, 2.78);
  tl.fromTo("#chip", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.7)", immediateRender: false }}, 3.08);
  // ── 3. 태그가 AI 콜봇의 대답 파형으로, 대답이 글자로
  tl.to("#chip", {{ scale: 0.2, opacity: 0, duration: 0.35, ease: "power2.in" }}, 3.4);
  tl.fromTo("#who2", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out", immediateRender: false }}, 3.5);
  gsap.utils.toArray(".abar").forEach((el, k) => {{
    tl.fromTo(el, {{ opacity: 0, scaleY: 0.04 }}, {{ opacity: 1, scaleY: 0.3, duration: 0.3, ease: "power2.out", immediateRender: false }}, 3.55 + Math.abs(k - 5.5) * 0.015);
    let t = 3.85; for (let s = 0; s < 4; s++) {{ tl.to(el, {{ scaleY: 0.18 + 0.82 * hsh(k + 40, s + 1) * Math.sin(Math.PI * (k + 0.5) / 12), duration: 0.17, ease: "sine.inOut" }}, t); t += 0.17; }}
  }});
  tl.fromTo(".ach", {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out", stagger: 0.035, immediateRender: false }}, 3.75);
  // ── 4. 대답이 빛 하나로 모여 케이블 → 스위치 포트 → 서버 랙
  tl.to(".abar", {{ x: (k, el) => 960 - parseFloat(el.style.left) - 7, scaleY: 0.06, duration: 0.4, ease: "power3.in" }}, 4.55);
  tl.to(".abar", {{ opacity: 0, duration: 0.15 }}, 4.9);
  tl.to(["#who2", "#ans"], {{ opacity: 0, y: -10, duration: 0.35, ease: "power2.in" }}, 4.55);
  tl.fromTo("#ni", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, immediateRender: false }}, 4.8);
  const DR = (sel, t, d, e = "power2.inOut", s = 0) => gsap.utils.toArray(sel).forEach((el, i) => {{
    const L = el.getTotalLength(); el.setAttribute("stroke-dasharray", `${{L}} ${{L}}`);
    tl.fromTo(el, {{ attr: {{ "stroke-dashoffset": L }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: d, ease: e }}, t + i * s);
  }});
  DR("#swb", 4.85, 0.6); DR(".port", 5.0, 0.4, "power2.out", 0.03);
  DR(".rk", 4.95, 0.7, "power2.inOut", 0.1); DR(".rslot", 5.2, 0.4, "power2.out", 0.008);
  // 빛 하나가 포트로(선은 점이 지나간 자리까지만)
  const drop = document.getElementById("drop"), DL = drop.getTotalLength();
  drop.setAttribute("stroke-dasharray", `${{DL}} ${{DL}}`);
  const pd = {{ p: 0 }}, putDot = () => {{ const pt = drop.getPointAtLength(pd.p * DL); gsap.set("#dot", {{ x: pt.x, y: pt.y }}); drop.setAttribute("stroke-dashoffset", DL * (1 - pd.p)); }};
  gsap.set("#dot", {{ x: 960, y: 420, scale: 0, opacity: 0 }}); drop.setAttribute("stroke-dashoffset", DL);
  tl.fromTo("#dot", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, 4.8);
  tl.fromTo(pd, {{ p: 0 }}, {{ p: 1, duration: 0.6, ease: "power2.inOut", onUpdate: putDot, immediateRender: false }}, 5.0);
  tl.to("#dot", {{ scale: 0.4, opacity: 0, duration: 0.25, ease: "power2.in" }}, 5.55);
  tl.to("#drop", {{ opacity: 0, duration: 0.5, ease: "sine.inOut" }}, 5.7);
  tl.to("#pl7", {{ attr: {{ fill: "#ff4fd8" }}, duration: 0.15 }}, 5.6);
  gsap.utils.toArray(".pled").forEach((el, i) => {{ if (i !== 7) tl.to(el, {{ attr: {{ fill: i % 2 ? "#9d79ff" : "#5a5cff" }}, duration: 0.12 }}, 5.65 + (7 - i) * 0.03); }});
  // 케이블을 따라 빛이 랙으로
  DR(".cab", 5.55, 0.5, "power2.out", 0.06);
  gsap.utils.toArray(".cab").forEach((c, r) => {{
    const L = c.getTotalLength(), q = {{ p: 0 }}, pu = document.getElementById("pu" + r);
    gsap.set(pu, {{ opacity: 0 }});
    tl.fromTo(q, {{ p: 0 }}, {{ p: 1, duration: 0.55, ease: "power1.inOut", immediateRender: false, onUpdate: () => {{ const pt = c.getPointAtLength(q.p * L); gsap.set(pu, {{ x: pt.x, y: pt.y, opacity: q.p < 0.97 ? 1 : 0 }}); }} }}, 5.7 + r * 0.08);
  }});
  gsap.set(".rled", {{ opacity: 0.12 }});
  gsap.utils.toArray(".rled").forEach((el) => {{ const r = +el.classList[1].slice(1), j = +el.dataset.j; tl.to(el, {{ opacity: 1, duration: 0.12, ease: "none" }}, 6.2 + r * 0.08 + j * 0.035); }});
  tl.fromTo([".dlab"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.12, immediateRender: false }}, 5.6);
  gsap.set(".dlab", {{ opacity: 0 }});
  // ── 한글 소제목(줄 마스크로 올라오고 내려감)
  CAPS.forEach(([a, b], i) => {{
    tl.fromTo("#cap" + i, {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01, immediateRender: false }}, a);
    tl.fromTo(".cl" + i, {{ yPercent: 120 }}, {{ yPercent: 0, duration: 0.7, ease: "expo.out", stagger: 0.06 }}, a);
    if (b) tl.to(".cl" + i, {{ yPercent: -120, duration: 0.35, ease: "power3.in", stagger: 0.03 }}, b);
  }});
  // ── 6.95 원형 와이프: 기존 인트로(로고)가 가운데서 열림(기존 인트로와 같은 곡선)
  tl.fromTo("#logo", {{ clipPath: "circle(0px at 960px 540px)" }}, {{ clipPath: "circle(1200px at 960px 540px)", duration: 0.55, ease: "power2.out", immediateRender: false }}, {CUT});
  gsap.set("#logo", {{ clipPath: "circle(0px at 960px 540px)" }});
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
}}
document.fonts.ready.then(build);
</script>
</body></html>"""
    return html


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int(12 * SR), 2))
    add(buf, sweep(260, 900, 0.9, partials=((1, 1), (2, 0.3)), a=0.1, r=0.25, rise=True), 0.05, 0.045)
    for i, m in enumerate([76, 79, 81, 79, 84, 81]):                      # 고객 목소리(짧은 음)
        add(buf, tone(hz(m), 0.16, ((1, 1), (2, 0.2)), a=0.01, r=0.06, decay=0.12), 0.95 + i * 0.16, 0.05, -0.2)
    for i in range(10):                                                    # 막대가 글자로 내려앉음
        add(buf, pop(1300 + i * 30, 700, 0.05), 1.98 + i * 0.025, 0.035)
    add(buf, bell(88, 0.9, 0.35), 3.02, 0.13); add(buf, bell(95, 1.2, 0.5), 3.1, 0.12)   # 이해 완료(띠링)
    for i, m in enumerate([84, 81, 86, 84, 88, 86]):                      # AI 대답
        add(buf, tone(hz(m), 0.16, ((1, 1), (2, 0.15)), a=0.01, r=0.06, decay=0.12), 3.85 + i * 0.17, 0.05, 0.2)
    add(buf, sweep(900, 220, 0.6, partials=((1, 1), (2, 0.3)), a=0.05, r=0.15, rise=False), 4.6, 0.05)
    add(buf, pop(620, 260, 0.12), 5.58, 0.16)                              # 포트에 꽂힘
    for r in range(3):
        add(buf, sweep(500, 1500, 0.5, partials=((1, 1),), a=0.05, r=0.1, rise=True), 5.7 + r * 0.08, 0.018)
    for i in range(12):                                                    # 랙 LED
        add(buf, tone(hz(91 + (i % 4) * 2), 0.06, ((1, 1),), a=0.003, r=0.03, decay=0.04), 6.2 + i * 0.035, 0.03, (i % 3 - 1) * 0.4)
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
