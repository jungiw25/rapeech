"""브랜드 필름 리뉴얼 시안 영상 2종(A 에디토리얼 / B 3D 재질)을 만든다.

두 시안은 같은 이야기·같은 타이밍(22초)이라 나란히 비교할 수 있다.
  0.0– 4.2  목소리에서 시작
  4.2–12.3  AI 콜봇 4단계(음성 인식 → 의도 파악 → 목소리 인증 → 업무 처리)
 12.3–17.0  대화 아래의 인프라(데이터센터)
 17.0–22.0  AI + 인프라, 한 팀(클라이맥스)
사용법: python3 video/samples/build_samples.py  → video/samples/{a,b}/index.html (HyperFrames 프로젝트)
렌더:   cd video/samples/a && npx hyperframes render --fps 60 --quality delivery --output out/sample_a.mp4
"""
import json
import math
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FILM = REPO / "video" / "brand-film"
DUR = 22.0
ARR = [5.4, 7.2, 9.0, 10.8]          # 단계 도착
DEP = [4.2, 5.9, 7.7, 9.5]           # 단계 출발
STEPS = [("01", "음성 인식", "“카드를 잃어버렸어요”"), ("02", "의도 파악", "카드 분실 신고"),
         ("03", "목소리 인증", "본인 확인 완료"), ("04", "업무 처리", "카드 사용 정지")]
C30 = math.cos(math.pi / 6)

FONT_CSS = "".join(f'@font-face {{ font-family: "Pretendard"; font-weight: {w}; src: url("assets/fonts/Pretendard-{n}.otf"); }}\n'
                   for w, n in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")))
BASE_CSS = FONT_CSS + """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #0c0916; }
#root { position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: "Pretendard", sans-serif; background: #0c0916; }
.layer { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
.hl { position: absolute; color: #fff; font-weight: 800; letter-spacing: -0.035em; line-height: 1.16; white-space: nowrap; }
.hl .ln { display: block; overflow: hidden; padding: 0 0.06em 0.12em 0; margin-bottom: -0.12em; }
.hl .ln > span { display: inline-block; }
.g { background: linear-gradient(100deg, #ff4fd8, #b25cff 55%, #7a6bff); -webkit-background-clip: text; background-clip: text; color: transparent; }
.v { display: inline-block; }
.mono { position: absolute; font-weight: 600; font-size: 19px; letter-spacing: 0.24em; color: #8e86a8; white-space: nowrap; }
.val { position: absolute; font-weight: 700; color: #fff; letter-spacing: -0.02em; white-space: nowrap; }
.cwrap { position: absolute; width: 0; display: flex; flex-direction: column; align-items: center; }
"""

# 헤드라인·스크램블 등 두 시안 공용 JS(타임라인 tl 위에서 동작)
KIT_JS = r"""
const tl = gsap.timeline({ paused: true });
const REVEAL = (sel, t, o = {}) => tl.fromTo(sel, { yPercent: 118 }, { yPercent: 0, duration: o.d || 1.15, ease: "expo.out", stagger: o.s ?? 0.09 }, t);
const HIDE = (sel, t, o = {}) => tl.to(sel, { yPercent: -118, duration: o.d || 0.55, ease: "power3.in", stagger: o.s ?? 0.05 }, t);
const FADE = (sel, t, a, b, d = 0.6, e = "sine.inOut") => tl.fromTo(sel, { opacity: a }, { opacity: b, duration: d, ease: e, immediateRender: false }, t);
const SYL = "가각간갈감강개거건검겨경고공과관구국군그근글기나남내너노누는다단달대더도동두라락란람랑래러로루르리마만말매머모목무문미바반발방배버번보복본부분비사산살상새서선설성세소속손수순스시신실심아안알애야약양어언업에여역연열영오온와완요용우운울원위유으은을음의이인일자작잔장재저전절점정제조종주중지진차찬창채처천철청초총추축출치친카타탑태터토통트파판패포표프피하학한할함합해행허현형호화확환활회효후휘흐희";
const hsh = (a, b) => { let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
const KEEP = " “”,.·";
function scrambleText(text, p, d) {
  if (p <= 0) return "";
  const n = text.length, f = Math.floor(p * d * 24);
  let out = "";
  for (let i = 0; i < n; i++) {
    const c = text[i], r = 0.3 + 0.7 * i / n;
    if (p >= r || KEEP.includes(c)) out += (p >= r - 0.5 ? c : (KEEP.includes(c) ? c : ""));
    else if (p >= r - 0.5) out += SYL[Math.floor(hsh(i + 1, f + 7) * SYL.length)];
  }
  return out;
}
const SCRAMBLE = (el, text, t, d = 1.0) => { const o = { p: 0 }; el.textContent = ""; tl.fromTo(o, { p: 0 }, { p: 1, duration: d, ease: "none", onUpdate() { el.textContent = scrambleText(text, o.p, d); } }, t); };
const DRAWS = (sel, t, d = 1.0, e = "power2.inOut", s = 0) => gsap.utils.toArray(sel).forEach((el, i) => {
  const L = el.getTotalLength(); el.setAttribute("stroke-dasharray", `${L} ${L}`);
  tl.fromTo(el, { attr: { "stroke-dashoffset": L } }, { attr: { "stroke-dashoffset": 0 }, duration: d, ease: e }, t + i * s);
});
"""


def hl(hid, lines, x, y, size, extra=""):
    """[단어]는 그라데이션, {단어}는 단계별로 켜지는 동사."""
    out = []
    vi = 0
    for ln in lines:
        s = ln
        while "[" in s:
            a, b = s.index("["), s.index("]")
            s = s[:a] + f'<span class="g">{s[a + 1:b]}</span>' + s[b + 1:]
        while "{" in s:
            a, b = s.index("{"), s.index("}")
            s = s[:a] + f'<span class="v {hid}-v" id="{hid}-v{vi}">{s[a + 1:b]}</span>' + s[b + 1:]
            vi += 1
        out.append(f'<span class="ln"><span class="{hid}-l">{s}</span></span>')
    return f'<div class="hl" id="{hid}" style="left:{x}px;top:{y}px;font-size:{size}px;{extra}">{"".join(out)}</div>'


def page(title, css, body, script, head_js=()):
    heads = "".join(f'<script src="{s}"></script>' for s in ("assets/gsap.min.js",) + tuple(head_js))
    return f"""<!doctype html>
<html lang="ko" data-resolution="landscape">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>{title}</title>{heads}
<style>{BASE_CSS}{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="60" data-width="1920" data-height="1080">
{body}
<audio id="bed" class="clip" src="assets/bed.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="0.42" data-fade-in="1.2" data-fade-out="2.2"></audio>
<audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="3" data-volume="1"></audio>
</div>
<script>
{KIT_JS}
{script}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body></html>"""


# ─────────────────────────────────────────────── 공용 텍스트(두 시안 같은 문구·같은 시각)
def texts(s2_y=160, lab_mode="under"):
    h = [
        '<div class="mono" id="k1" style="left:160px;top:236px">RAPEECH  ·  CONVERSATIONAL AI</div>',
        hl("h1", ["모든 대화는,", "[목소리]에서 시작합니다."], 156, 280, 92),
        hl("h2", ["AI 콜봇이 {듣고}, {이해하고},", "{확인하고}, {처리합니다}."], 156, s2_y, 76),
        hl("h3", ["끊김 없는 대화 뒤에는,", "[단단한 인프라]가 있습니다."], 156, 160, 76),
        hl("h4", ["인프라 구축부터 AI 도입까지,", "[한 팀이] 함께합니다."], 156, 160, 76),
    ]
    return "\n".join(h)


TEXT_JS = """
gsap.set("#k1", { opacity: 0 });
REVEAL(".h1-l", 0.9); FADE("#k1", 0.7, 0, 1, 0.8); HIDE(".h1-l", 3.75); FADE("#k1", 3.75, 1, 0, 0.4);
REVEAL(".h2-l", 4.35); gsap.set(".h2-v", { opacity: 0.22 });
ARR.forEach((t, i) => tl.to("#h2-v" + i, { opacity: 1, duration: 0.5, ease: "sine.out" }, t + 0.05));
HIDE(".h2-l", 12.0);
REVEAL(".h3-l", 13.2); HIDE(".h3-l", 16.55);
REVEAL(".h4-l", 17.7);
"""


# ─────────────────────────────────────────────── A안: 에디토리얼(가는 선, 필름 질감, 타이포)
def build_a():
    k, ox, oy = 56, 1180, 600
    iso = lambda x, y, z: (ox + (x - y) * C30 * k, oy + (x + y) * 0.5 * k - z * k)
    P = lambda x, y, z=0: "%.1f,%.1f" % iso(x, y, z)
    SX = [400, 800, 1200, 1600]
    LY = 640
    labs = ["전산 설계", "통합배선", "네트워크", "출입보안", "통합관제", "유지보수"]
    plates, glow = [], []
    for f in range(6):
        top = " ".join([P(0, 0), P(7, 0), P(7, 4), P(0, 4)])
        side = " ".join([P(0, 4), P(7, 4), P(7, 4, -0.12), P(0, 4, -0.12)]) + " " + " ".join([P(7, 0), P(7, 0, -0.12)])
        det = ""
        if f == 0:
            det = "".join(f'<line x1="{iso(gx, 0.3, 0)[0]:.1f}" y1="{iso(gx, 0.3, 0)[1]:.1f}" x2="{iso(gx, 3.7, 0)[0]:.1f}" y2="{iso(gx, 3.7, 0)[1]:.1f}" stroke="#fff" stroke-opacity=".28" stroke-width="1" stroke-dasharray="3 7"/>' for gx in range(1, 7))
        if f == 1:
            det = "".join(f'<polyline class="a-cable" points="{P(0.3, 0.6 + c * 0.8)} {P(4.5 + c * 0.5, 0.6 + c * 0.8)} {P(4.5 + c * 0.5, 3.6)}" fill="none" stroke="url(#a-g)" stroke-width="1.6"/>' for c in range(4))
        if f == 2:
            det = "".join(f'<polygon points="{P(0.6 + c * 1.25, 1.4)} {P(1.5 + c * 1.25, 1.4)} {P(1.5 + c * 1.25, 2.6)} {P(0.6 + c * 1.25, 2.6)}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1"/>' for c in range(5))
        if f == 3:
            det = f'<polyline points="{P(3.0, 3.9)} {P(3.0, 3.9, 0.9)} {P(4.0, 3.9, 0.9)} {P(4.0, 3.9)}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="1.2"/>'
        if f == 4:
            det = f'<polyline points="{P(1.0, 0.35)} {P(1.0, 0.35, 0.7)} {P(6.0, 0.35, 0.7)} {P(6.0, 0.35)}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1.2"/>'
        if f == 5:
            cx, cy = iso(3.5, 2.0, 0)
            det = f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="34" ry="20" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.3"/><path d="M{cx - 12:.1f} {cy:.1f} l9 5 l16 -11" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        rx, ry = iso(7, 0, 0)
        lab = (f'<line class="a-lead" x1="{rx + 8:.1f}" y1="{ry:.1f}" x2="{rx + 90:.1f}" y2="{ry:.1f}" stroke="#fff" stroke-opacity=".35" stroke-width="1"/>'
               f'<text class="a-lab" x="{rx + 102:.1f}" y="{ry + 6:.1f}" font-family="Pretendard" font-weight="600" font-size="19" letter-spacing="3" fill="#a69cc8">{labs[f]}</text>')
        plates.append(f'<g class="a-plz" id="a-plz{f}"><g class="a-pl" id="a-pl{f}">'
                      f'<polygon points="{top}" fill="#150f2c" fill-opacity=".86"/>'
                      f'<polygon class="a-edge" points="{top}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.3"/>'
                      f'<polyline points="{side}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1"/>'
                      f'<polygon class="a-hot" points="{top}" fill="none" stroke="url(#a-g)" stroke-width="2.2" opacity="0"/>'
                      f'<g class="a-det">{det}</g>{lab}</g></g>')
    mid = iso(3.5, 2.0, 0)
    ai_lab, ni_lab = iso(7, 0, 3.24), iso(7, 0, 0.24)
    svg = f'''<svg class="layer" viewBox="0 0 1920 1080">
  <defs>
    <linearGradient id="a-g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff4fd8"/><stop offset=".55" stop-color="#b25cff"/><stop offset="1" stop-color="#6a5cff"/></linearGradient>
    <radialGradient id="a-halo"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".25" stop-color="#ff7be2" stop-opacity=".45"/><stop offset="1" stop-color="#ff4fd8" stop-opacity="0"/></radialGradient>
    <linearGradient id="a-tail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#ffd6f6" stop-opacity=".9"/></linearGradient>
  </defs>
  <g id="a-s2">
    <line id="a-guide" x1="160" y1="{LY}" x2="1760" y2="{LY}" stroke="#fff" stroke-opacity=".14" stroke-width="1" stroke-dasharray="2 9"/>
    <line id="a-trk" x1="160" y1="{LY}" x2="160" y2="{LY}" stroke="#fff" stroke-opacity=".75" stroke-width="2"/>
    {"".join(f'<g id="a-n{i}"><circle class="a-ring" id="a-r{i}" cx="{x}" cy="{LY}" r="15" fill="#0c0916" stroke="#fff" stroke-width="1.5"/><circle id="a-d{i}" cx="{x}" cy="{LY}" r="4.5" fill="#fff"/><circle id="a-p{i}" cx="{x}" cy="{LY}" r="15" fill="none" stroke="#fff" stroke-width="1"/></g>' for i, x in enumerate(SX))}
  </g>
  {"".join(f'<circle class="a-wave" cx="160" cy="{LY}" r="10" fill="none" stroke="#fff" stroke-width="1.2"/>' for _ in range(3))}
  <g id="a-stack">{"".join(plates)}
    <g id="a-ailab" opacity="0"><line x1="{ai_lab[0] + 8:.1f}" y1="{ai_lab[1]:.1f}" x2="{ai_lab[0] + 90:.1f}" y2="{ai_lab[1]:.1f}" stroke="#fff" stroke-opacity=".5"/><text x="{ai_lab[0] + 102:.1f}" y="{ai_lab[1] + 7:.1f}" font-family="Pretendard" font-weight="700" font-size="24" fill="#fff">AI · 대화</text></g>
    <g id="a-nilab" opacity="0"><line x1="{ni_lab[0] + 8:.1f}" y1="{ni_lab[1]:.1f}" x2="{ni_lab[0] + 90:.1f}" y2="{ni_lab[1]:.1f}" stroke="#fff" stroke-opacity=".5"/><text x="{ni_lab[0] + 102:.1f}" y="{ni_lab[1] + 7:.1f}" font-family="Pretendard" font-weight="700" font-size="24" fill="#fff">NI · 인프라</text></g>
  </g>
  <g id="a-cm"><g id="a-cms"><rect id="a-tl" x="-150" y="-1.5" width="150" height="3" fill="url(#a-tail)" opacity="0"/><circle r="30" fill="url(#a-halo)"/><circle r="5.5" fill="#fff"/></g></g>
</svg>'''
    labels = "".join(f'<div class="cwrap" style="left:{x}px;top:{LY + 46}px"><div class="mono a-sl" id="a-sl{i}" style="position:relative">{n}  {lab}</div>'
                     f'<div class="val a-sv" id="a-sv{i}" style="position:relative;margin-top:14px;font-size:34px"></div></div>'
                     for i, (x, (n, lab, _)) in enumerate(zip(SX, STEPS)))
    body = f'''<canvas id="bg" class="layer" width="1920" height="1080"></canvas>
{svg}
<div class="layer">{labels}</div>
{texts()}'''
    script = f"""
const ARR = {json.dumps(ARR)}, DEP = {json.dumps(DEP)}, SX = {json.dumps(SX)}, STEPS = {json.dumps([s[2] for s in STEPS], ensure_ascii=False)};
const LY = {LY}, K = {k};
{TEXT_JS}
// ── 1. 목소리: 점 하나와 퍼지는 가는 고리
gsap.set("#a-cm", {{ x: 160, y: LY }});
gsap.set("#a-cms", {{ svgOrigin: "0 0", scale: 0, opacity: 0 }});
tl.fromTo("#a-cms", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.9, ease: "power3.out", immediateRender: false }}, 0.5);
gsap.set(".a-wave", {{ opacity: 0 }});
gsap.utils.toArray(".a-wave").forEach((el, j) => {{
  for (let r = 0; r < 2; r++) tl.fromTo(el, {{ attr: {{ r: 8 }}, opacity: 0.7 }}, {{ attr: {{ r: 90 }}, opacity: 0, duration: 1.6, ease: "power2.out", immediateRender: false }}, 1.0 + r * 1.4 + j * 0.28);
}});
// ── 2. 선은 점이 지나간 자리까지만 정확히(점과 선이 같은 트윈 시간·이징)
FADE("#a-guide", 4.0, 0, 1, 0.8);
gsap.set(["#a-r0", "#a-r1", "#a-r2", "#a-r3", "#a-d0", "#a-d1", "#a-d2", "#a-d3", "#a-p0", "#a-p1", "#a-p2", "#a-p3", ".a-sl"], {{ opacity: 0 }});
for (let i = 0; i < 4; i++) {{
  const d = ARR[i] - DEP[i];
  tl.to("#a-cm", {{ x: SX[i], duration: d, ease: "power2.inOut" }}, DEP[i]);
  tl.to("#a-trk", {{ attr: {{ x2: SX[i] }}, duration: d, ease: "power2.inOut" }}, DEP[i]);
  tl.fromTo("#a-tl", {{ opacity: 0 }}, {{ opacity: 1, duration: d * 0.5, ease: "sine.in", yoyo: true, repeat: 1, immediateRender: false }}, DEP[i]);
  const t = ARR[i];
  tl.fromTo("#a-r" + i, {{ opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.7, ease: "expo.out" }}, t - 0.05);
  tl.fromTo("#a-d" + i, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, t + 0.1);
  tl.fromTo("#a-p" + i, {{ opacity: 0.8, scale: 1, transformOrigin: "50% 50%" }}, {{ opacity: 0, scale: 3.2, duration: 1.1, ease: "power2.out", immediateRender: false }}, t);
  tl.fromTo("#a-sl" + i, {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, t + 0.1);
  SCRAMBLE(document.getElementById("a-sv" + i), STEPS[i], t + 0.2, 0.95);
  if (i < 3) tl.to(["#a-sl" + i, "#a-sv" + i], {{ opacity: 0.38, duration: 0.6, ease: "sine.inOut" }}, ARR[i + 1] - 0.3);
}}
// ── 3. 전환: 모든 것이 물러나고 점만 데이터센터의 맨 아래 판으로
tl.to(["#a-s2", ".a-sl", ".a-sv"], {{ opacity: 0, duration: 0.7, ease: "sine.inOut" }}, 12.0);
tl.to("#a-cm", {{ x: {mid[0]:.1f}, y: {mid[1]:.1f}, duration: 1.0, ease: "power3.inOut" }}, 12.15);
tl.to("#a-cms", {{ scale: 0, opacity: 0, duration: 0.45, ease: "power2.in" }}, 13.1);
gsap.set(".a-pl", {{ opacity: 0 }});
for (let f = 0; f < 6; f++) gsap.set("#a-plz" + f, {{ y: -f * K }});
for (let f = 0; f < 6; f++) {{
  const t = 13.1 + f * 0.36;
  tl.fromTo("#a-pl" + f, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "none" }}, t);
  tl.fromTo("#a-pl" + f, {{ y: 26 }}, {{ y: 0, duration: 1.0, ease: "expo.out" }}, t);
  DRAWS("#a-pl" + f + " .a-edge", t, 0.9, "power2.inOut");
  tl.fromTo("#a-pl" + f + " .a-det", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "sine.out" }}, t + 0.45);
  tl.fromTo("#a-pl" + f + " .a-lab", {{ opacity: 0, x: -10 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, t + 0.35);
  DRAWS("#a-pl" + f + " .a-lead", t + 0.3, 0.5, "power2.out");
}}
DRAWS(".a-cable", 13.75, 0.9, "power2.inOut", 0.08);
// ── 4. 여섯 층이 두 층으로 모임: 아래 3층은 인프라, 위 3층은 AI
tl.to([".a-lab", ".a-lead"], {{ opacity: 0, duration: 0.4, ease: "sine.in" }}, 16.6);
const Z = [0, 0.12, 0.24, 3.0, 3.12, 3.24];
for (let f = 0; f < 6; f++) tl.to("#a-plz" + f, {{ y: -Z[f] * K, duration: 1.3, ease: "power3.inOut" }}, 16.85 + (f < 3 ? 0 : 0.08));
tl.to(".a-det", {{ opacity: 0.35, duration: 0.6 }}, 16.85);
FADE("#a-ailab", 18.2, 0, 1, 0.6); FADE("#a-nilab", 18.35, 0, 1, 0.6);
// 빛 하나가 위에서 AI 층을 지나 인프라 층에 닿음 → 두 층 테두리에 브랜드 빛
tl.fromTo("#a-cm", {{ x: {mid[0]:.1f}, y: {mid[1] - 520:.1f} }}, {{ x: {mid[0]:.1f}, y: {mid[1] - 3.24 * k:.1f}, duration: 0.7, ease: "power2.in", immediateRender: false }}, 18.3);
tl.fromTo("#a-cms", {{ scale: 1, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, immediateRender: false }}, 18.3);
tl.to("#a-cm", {{ y: {mid[1] - 0.24 * k:.1f}, duration: 0.55, ease: "power2.inOut" }}, 19.0);
tl.to(["#a-pl3 .a-hot", "#a-pl4 .a-hot", "#a-pl5 .a-hot"], {{ opacity: 1, duration: 0.5, ease: "sine.out", stagger: 0.05 }}, 18.95);
tl.to(["#a-pl0 .a-hot", "#a-pl1 .a-hot", "#a-pl2 .a-hot"], {{ opacity: 1, duration: 0.5, ease: "sine.out", stagger: 0.05 }}, 19.5);
tl.to("#a-cms", {{ scale: 2.2, opacity: 0, duration: 0.9, ease: "power2.out" }}, 19.55);

// ── 배경: 아주 느린 그라데이션 + 고운 필름 질감(시드 고정, 시간으로만 결정)
const cv = document.getElementById("bg"), cx = cv.getContext("2d");
const NZ = [];
for (let n = 0; n < 6; n++) {{
  const c = document.createElement("canvas"); c.width = 960; c.height = 540;
  const x = c.getContext("2d"), im = x.createImageData(960, 540);
  for (let i = 0; i < im.data.length; i += 4) {{ const v = Math.floor(hsh(i >> 2, n * 7919) * 255); im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }}
  x.putImageData(im, 0, 0); NZ.push(c);
}}
const BL = [
  [0.72, 0.42, 0.62, [92, 40, 200], 0.55, 0.11, 0.07, 0.0],
  [0.18, 0.88, 0.55, [150, 20, 130], 0.42, 0.08, 0.09, 1.7],
  [0.95, 0.95, 0.5, [40, 30, 170], 0.40, 0.07, 0.06, 3.1],
];
function drawBg(t) {{
  cx.globalCompositeOperation = "source-over"; cx.globalAlpha = 1;
  cx.fillStyle = "#0c0916"; cx.fillRect(0, 0, 1920, 1080);
  for (const [x, y, r, c, a, ax, ay, ph] of BL) {{
    const px = (x + ax * Math.sin(t * 0.21 + ph)) * 1920, py = (y + ay * Math.cos(t * 0.17 + ph)) * 1080, R = r * 1920;
    const g = cx.createRadialGradient(px, py, 0, px, py, R);
    g.addColorStop(0, `rgba(${{c[0]}},${{c[1]}},${{c[2]}},${{a}})`); g.addColorStop(1, `rgba(${{c[0]}},${{c[1]}},${{c[2]}},0)`);
    cx.fillStyle = g; cx.fillRect(0, 0, 1920, 1080);
  }}
  const v = cx.createRadialGradient(960, 540, 300, 960, 540, 1150);
  v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, "rgba(0,0,0,0.55)");
  cx.fillStyle = v; cx.fillRect(0, 0, 1920, 1080);
  cx.globalAlpha = 0.055; cx.drawImage(NZ[Math.floor(t * 24) % NZ.length], 0, 0, 1920, 1080);
  cx.globalAlpha = 1;
}}
window.addEventListener("hf-seek", (e) => drawBg(e.detail.time));
drawBg(0);
"""
    return page("Rapeech 시안 A", "", body, script)


# ─────────────────────────────────────────────── B안: 3D 재질(액체 목소리 + 실제 3D 데이터센터)
def build_b():
    labels = ('<div id="b-shade" class="layer" style="background:linear-gradient(90deg,rgba(12,9,22,.78),rgba(12,9,22,.35) 38%,rgba(12,9,22,0) 60%)"></div>'
              + "".join(f'<div class="mono b-sl" id="b-sl{i}" style="left:1240px;top:842px">{n} / 04   {lab}</div>'
                        f'<div class="val b-sv" id="b-sv{i}" style="left:1236px;top:880px;font-size:56px;letter-spacing:-0.03em"></div>'
                        for i, (n, lab, _) in enumerate(STEPS))
              + '<div class="mono" id="b-ai" style="left:0;top:0;opacity:0">AI · 대화</div><div class="mono" id="b-ni" style="left:0;top:0;opacity:0">NI · 인프라</div>')
    body = f'''<canvas id="gl" class="layer" width="1920" height="1080"></canvas>
<div class="layer">{labels}</div>
{texts()}'''
    script = f"""
const ARR = {json.dumps(ARR)}, DEP = {json.dumps(DEP)}, STEPS = {json.dumps([s[2] for s in STEPS], ensure_ascii=False)};
{TEXT_JS}
gsap.set([".b-sl"], {{ opacity: 0 }});
for (let i = 0; i < 4; i++) {{
  const t = ARR[i];
  tl.fromTo("#b-sl" + i, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, t + 0.05);
  SCRAMBLE(document.getElementById("b-sv" + i), STEPS[i], t + 0.15, 0.95);
  const off = i < 3 ? DEP[i + 1] + 0.1 : 12.0;
  tl.to(["#b-sl" + i, "#b-sv" + i], {{ opacity: 0, y: -10, duration: 0.45, ease: "power2.in" }}, off);
}}
tl.fromTo("#b-shade", {{ opacity: 1 }}, {{ opacity: 0.55, duration: 2, immediateRender: false }}, 13.0);
FADE("#b-ai", 18.9, 0, 1, 0.6); FADE("#b-ni", 19.2, 0, 1, 0.6);

// ───────── three.js 장면(시간 t만으로 그리는 순수 함수)
const W = 1920, H = 1080;
const renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById("gl"), antialias: true, preserveDrawingBuffer: true }});
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0c0916);
scene.fog = new THREE.Fog(0x0c0916, 10, 26);
const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 120);
const C = (h) => new THREE.Color(h);

scene.add(new THREE.HemisphereLight(C("#6d5bd0"), C("#0c0916"), 0.32));
const key = new THREE.DirectionalLight(C("#fff1fb"), 0.75); key.position.set(-5, 9, 7); scene.add(key);
const rim = new THREE.DirectionalLight(C("#5a6bff"), 0.9); rim.position.set(7, 3, -8); scene.add(rim);
const orbLight = new THREE.PointLight(C("#ff5ad9"), 1.2, 3.2, 2); scene.add(orbLight);

// 서버 랙(바닥 아래): 몸체 + 앞면 LED 줄(인스턴스)
const ROWS = [-7.0, -4.6, -2.2, 0.2, 2.6, 5.0], RX = [];
for (let x = -10.5; x <= 10.51; x += 0.78) RX.push(x);
const NR = ROWS.length * RX.length, NL = NR * 6;
const rackGeo = new THREE.BoxGeometry(0.7, 2.1, 1.1);
const rackMat = new THREE.MeshStandardMaterial({{ color: C("#16122a"), roughness: 0.42, metalness: 0.6 }});
const racks = new THREE.InstancedMesh(rackGeo, rackMat, NR);
const ledGeo = new THREE.BoxGeometry(0.46, 0.028, 0.01);
const ledMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, toneMapped: false }});
const leds = new THREE.InstancedMesh(ledGeo, ledMat, NL);
const M = new THREE.Matrix4(), LEDINFO = [];
let ri = 0, li = 0;
for (const z of ROWS) for (const x of RX) {{
  M.makeTranslation(x, -1.4, z); racks.setMatrixAt(ri++, M);
  for (let j = 0; j < 6; j++) {{
    M.makeTranslation(x - 0.05, -0.62 - j * 0.24, z + 0.556); leds.setMatrixAt(li, M);
    const h = hsh(li, 31);
    LEDINFO.push({{ x, z, base: h < 0.18 ? 1 : (h < 0.5 ? 0.35 : 0.12), hue: (x + 10.5) / 21 }});
    leds.setColorAt(li++, C("#000"));
  }}
}}
scene.add(racks, leds);
const PINK = C("#ff4fd8"), PURP = C("#9d6bff"), BLUE = C("#5a5cff"), DIM = C("#2c2548"), tmp = new THREE.Color();

// 바닥(대화가 흐르는 면) + 가는 격자
const floorMat = new THREE.MeshLambertMaterial({{ color: C("#0b0818"), transparent: true }});
const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), floorMat); floor.rotation.x = -Math.PI / 2; scene.add(floor);
const gp = [];
for (let i = -20; i <= 20; i++) {{ gp.push(i, 0.002, -20, i, 0.002, 20, -20, 0.002, i, 20, 0.002, i); }}
const gridGeo = new THREE.BufferGeometry(); gridGeo.setAttribute("position", new THREE.Float32BufferAttribute(gp, 3));
const gridMat = new THREE.LineBasicMaterial({{ color: C("#3a3160"), transparent: true, opacity: 0.35 }});
scene.add(new THREE.LineSegments(gridGeo, gridMat));

// 지나온 길(점 뒤로만 자람)과 관문 4개
const START = -7.5, GX = [-4.5, -1.5, 1.5, 4.5];
const trk = new THREE.Mesh(new THREE.BoxGeometry(1, 0.012, 0.035), new THREE.MeshBasicMaterial({{ color: C("#e9ddff"), toneMapped: false }}));
trk.position.y = 0.007; scene.add(trk);
const gates = GX.map((x) => {{
  const m = new THREE.Mesh(new THREE.TorusGeometry(0.86, 0.016, 16, 160), new THREE.MeshBasicMaterial({{ color: C("#3d355c"), toneMapped: false, transparent: true }}));
  m.position.set(x, 0.86, 0); m.rotation.y = Math.PI / 2; scene.add(m); return m;
}});

// 목소리: 액체 금속 구(정점 변형 + 브랜드 톤 반사)
const orbMat = new THREE.ShaderMaterial({{
  uniforms: {{ uT: {{ value: 0 }}, uRip: {{ value: 0 }}, uFin: {{ value: 0 }}, uBreath: {{ value: 1 }} }},
  vertexShader: `
    uniform float uT, uRip, uFin, uBreath;
    varying vec3 vN; varying vec3 vP;
    float disp(vec3 d){{
      float s = 0.022 * uBreath * sin(d.x*3.1 + uT*1.3) * sin(d.y*3.7 - uT*1.1) * sin(d.z*2.9 + uT*0.9);
      s += uRip * 0.016 * sin(d.x*19.0 - uT*8.0) * smoothstep(-0.9, 0.2, d.x);
      s += uFin * 0.011 * sin(length(d.xy - vec2(0.05, 0.12))*46.0) * smoothstep(0.1, 0.7, d.z);
      return s;
    }}
    vec3 P(vec3 d){{ d = normalize(d); return d * 0.55 * (1.0 + disp(d)); }}
    void main(){{
      vec3 d = normalize(position);
      vec3 t1 = normalize(abs(d.y) > 0.99 ? cross(d, vec3(1.,0.,0.)) : cross(d, vec3(0.,1.,0.)));
      vec3 t2 = cross(d, t1);
      vec3 p0 = P(d), pa = P(d + t1*0.012), pb = P(d + t2*0.012);
      vec3 n = normalize(cross(pa - p0, pb - p0)); if (dot(n, d) < 0.) n = -n;
      vN = normalize(normalMatrix * n);
      vec4 mv = modelViewMatrix * vec4(p0, 1.0);
      vP = mv.xyz;
      gl_Position = projectionMatrix * mv;
    }}`,
  fragmentShader: `
    varying vec3 vN; varying vec3 vP;
    vec3 env(vec3 r){{
      vec3 c = mix(vec3(.025,.018,.06), vec3(.14,.09,.30), smoothstep(-1., 1., r.y));
      c += vec3(1.,.97,1.) * smoothstep(.72, .95, r.y) * 1.25;
      c += vec3(1.,.30,.85) * smoothstep(.80, .98, -r.x) * 1.15;
      c += vec3(.40,.36,1.) * smoothstep(.80, .98, r.x*.9 + r.z*.25) * 1.1;
      c += vec3(.85,.8,1.) * exp(-abs(r.y + .08) * 16.) * .22;
      return c;
    }}
    void main(){{
      vec3 N = normalize(vN), V = normalize(-vP);
      vec3 Rv = reflect(-V, N);
      vec3 R = (vec4(Rv, 0.) * viewMatrix).xyz;
      float ndv = clamp(dot(N, V), 0., 1.);
      vec3 Nw = (vec4(N, 0.) * viewMatrix).xyz;
      vec3 b = mix(vec3(1., .18, .78), vec3(.32, .26, 1.), smoothstep(-.7, .7, Nw.x + Nw.y*.3));
      vec3 c = env(R) * mix(vec3(.9), b * 1.35, .5);
      c += b * pow(1. - ndv, 3.) * .7;
      c = c / (1. + c * .55);
      gl_FragColor = vec4(pow(c, vec3(.95)), 1.);
    }}`,
}});
const orb = new THREE.Mesh(new THREE.SphereGeometry(0.55, 200, 140), orbMat); scene.add(orb);
// 접지 그림자
const sc = document.createElement("canvas"); sc.width = sc.height = 128;
const sg = sc.getContext("2d"), grd = sg.createRadialGradient(64, 64, 0, 64, 64, 64);
grd.addColorStop(0, "rgba(0,0,0,.75)"); grd.addColorStop(1, "rgba(0,0,0,0)"); sg.fillStyle = grd; sg.fillRect(0, 0, 128, 128);
const shadow = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.6), new THREE.MeshBasicMaterial({{ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }}));
shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.004; scene.add(shadow);
// 클라이맥스의 빛기둥
const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1, 12), new THREE.MeshBasicMaterial({{ color: C("#ff7be2"), toneMapped: false, transparent: true }}));
scene.add(beam);

// ───────── 시간 함수
const cl = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const io = (x) => x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;      // power2.inOut
const io3 = (x) => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; // power3.inOut
const seg = (t, a, b) => cl((t - a) / (b - a));
const lerp = (a, b, u) => a + (b - a) * u;
const V3 = (a, b, u) => new THREE.Vector3(lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u));
function orbX(t) {{
  let x = START;
  for (let i = 0; i < 4; i++) {{ if (t >= DEP[i]) x = lerp(i ? GX[i - 1] : START, GX[i], io(seg(t, DEP[i], ARR[i]))); }}
  if (t >= 12.4) x = lerp(GX[3], 0, io3(seg(t, 12.4, 14.0)));
  return x;
}}
const follow = (t) => {{ let s = 0; for (let k = 0; k < 8; k++) s += orbX(t - k * 0.06); return s / 8; }};
function camAt(t) {{
  const f = follow(Math.min(t, 12.3));
  const s2 = (ff) => [new THREE.Vector3(ff - 3.6, 2.35, 6.8), new THREE.Vector3(ff + 1.5, 0.95, 0)];
  const s1 = (u) => [V3([START - 0.2, 1.3, 5.6], [START - 0.5, 1.5, 6.4], u), V3([START - 1.7, 0.75, 0], [START - 1.9, 0.75, 0], u)];
  if (t < 4.9) {{
    const a = s1(io(seg(t, 0, 3.4))), w = io3(seg(t, 3.4, 4.9));
    if (w <= 0) return a;
    const b = s2(f);
    return [a[0].lerp(b[0], w), a[1].lerp(b[1], w)];
  }}
  if (t < 12.3) return s2(f);
  const [e2, e2t] = s2(GX[3]);
  const hp = new THREE.Vector3(2.2, 8.8, 12.8), ht = new THREE.Vector3(-3.4, -1.4, 0);
  if (t < 17.0) {{ const u = io3(seg(t, 12.3, 15.6)); const p = e2.clone().lerp(hp, u); p.y += Math.sin(u * Math.PI) * 0.8; return [p, e2t.clone().lerp(ht, u)]; }}
  const u = Math.sin(seg(t, 17.0, 22.0) * Math.PI / 2);
  return [hp.clone().lerp(new THREE.Vector3(6.4, 7.4, 11.6), u), ht.clone().lerp(new THREE.Vector3(-3.6, -0.1, 0), u)];
}}
const pinkC = C("#ff4fd8"), gateOff = C("#3d355c"), gateOn = C("#b58cff");
function renderAt(t) {{
  const x = orbX(t);
  // 단계별 표면: 1 음성 인식(물결) 2 의도 파악(매끈) 3 인증(지문 고리) 4 처리(매끈)
  const hit = (i) => Math.exp(-Math.pow((t - ARR[i] - 0.5) / 0.9, 2));
  orbMat.uniforms.uT.value = t;
  orbMat.uniforms.uRip.value = cl(seg(t, 0.8, 2.0)) * (1 - seg(t, 3.6, 4.4)) + hit(0) * 1.2;
  orbMat.uniforms.uFin.value = hit(2) * 1.4;
  orbMat.uniforms.uBreath.value = 1 + hit(1) * 0.8;
  // 클라이맥스: 위로 떠올라 납작한 판(AI 층)으로 모양이 바뀜
  const fl = io3(seg(t, 17.3, 18.8));
  const yb = 0.62 + Math.sin(t * 1.4) * 0.03;
  orb.position.set(x, lerp(yb, 1.9, fl), 0);
  orb.scale.set(lerp(1, 3.0, fl), lerp(1, 0.16, fl), lerp(1, 3.0, fl));
  orb.rotation.y = t * 0.15;
  const pulse = 1 + 0.06 * Math.exp(-Math.pow((t - 0.6) / 0.3, 2));
  if (t < 1.5) orb.scale.multiplyScalar(io(seg(t, 0.2, 1.3)) * pulse);
  orbLight.position.set(x, orb.position.y + 0.25, 0.4);
  orbLight.intensity = 1.2 * (1 - seg(t, 13.5, 15)) + 1.0 * fl;
  shadow.position.x = x; shadow.material.opacity = (t < 1.5 ? seg(t, 0.2, 1.3) : 1) * (1 - fl);
  // 길: 출발점부터 점이 있는 곳까지만
  const tx = t < 12.3 ? x : GX[3];
  trk.scale.x = Math.max(0.0001, tx - START); trk.position.x = (START + tx) / 2;
  trk.material.opacity = 1; trk.visible = t > DEP[0] - 0.05;
  trk.material.transparent = true; trk.material.opacity = 1 - seg(t, 12.6, 13.8);
  gates.forEach((g, i) => {{
    const on = seg(t, ARR[i] - 0.1, ARR[i] + 0.25), glow = Math.exp(-Math.pow((t - ARR[i] - 0.15) / 0.35, 2));
    g.material.color.copy(gateOff).lerp(gateOn, on).lerp(pinkC, glow * 0.8);
    g.material.opacity = cl(seg(t, 3.8, 4.8)) * (1 - seg(t, 12.5, 13.6));
    g.scale.setScalar(1 + glow * 0.06);
  }});
  // 바닥이 사라지며 아래의 데이터센터가 드러남
  const fo = 1 - io(seg(t, 13.0, 15.0));
  floorMat.opacity = 0.97 * fo; floorMat.depthWrite = fo > 0.9; floor.visible = fo > 0.01;
  gridMat.opacity = 0.35 * fo;
  // LED: 평소엔 은은하게, 클라이맥스엔 가운데서 퍼지는 빛의 물결
  const reveal = seg(t, 12.8, 15.2), wave = t - 19.0;
  for (let i = 0; i < NL; i++) {{
    const L = LEDINFO[i], d = Math.hypot(L.x, L.z);
    let a = L.base * (0.25 + 0.75 * reveal) * (0.8 + 0.2 * Math.sin(t * 2.0 + i * 1.7));
    if (wave > 0) a += Math.exp(-Math.pow((d - wave * 6.5) / 1.1, 2)) * 1.6 + 0.35 * seg(wave, 0.5, 2.2);
    tmp.copy(L.hue < 0.5 ? PINK : PURP).lerp(L.hue < 0.5 ? PURP : BLUE, (L.hue % 0.5) * 2);
    leds.setColorAt(i, DIM.clone().lerp(tmp, cl(a)).multiplyScalar(0.5 + 1.4 * cl(a, 0, 2)));
  }}
  leds.instanceColor.needsUpdate = true;
  // 빛기둥: AI 판에서 인프라로
  const bu = io(seg(t, 18.55, 19.05));
  beam.visible = bu > 0.001;
  const top = orb.position.y - 0.1, bot = -0.3, hgt = (top - bot) * bu;
  beam.scale.y = Math.max(0.0001, hgt); beam.position.set(0, top - hgt / 2, 0);
  beam.material.opacity = 1 - 0.4 * seg(t, 20, 22);
  const [p, tg] = camAt(t);
  cam.position.copy(p); cam.lookAt(tg); cam.updateMatrixWorld();
  renderer.render(scene, cam);
  // AI/NI 라벨을 3D 위치에 붙임
  const put = (id, v, dx) => {{ const s = v.clone().project(cam); const el = document.getElementById(id); el.style.left = ((s.x + 1) / 2 * W + dx) + "px"; el.style.top = ((1 - s.y) / 2 * H - 12) + "px"; }};
  put("b-ai", new THREE.Vector3(1.9, orb.position.y, 0), 24);
  put("b-ni", new THREE.Vector3(2.4, -0.3, 0.75), 30);
}}
window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
renderAt(0);
"""
    return page("Rapeech 시안 B", "", body, script, head_js=("assets/three.min.js",))


def sound(out_dir):
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(FILM / "tools"))
    from engine.bgm import SR, add, lowpass, synth, tone, hz, write_wav
    from intro.sfx import pop, sweep
    import sound as S  # brand-film/tools/sound.py 의 띠링·이동 소리
    import numpy as np
    bed = synth(DUR + 0.5, seed=21, bpm=92)
    write_wav(out_dir / "bed.wav", bed)
    buf = np.zeros((int((DUR + 1) * SR), 2))
    add(buf, pop(900, 420, 0.16), 0.55, 0.10)
    for t in DEP:
        S.whoosh(buf, t, up=True, gain=0.03, dur=1.1)
    for t in ARR:
        S.chime(buf, t + 0.02)
    S.whoosh(buf, 12.15, up=False, gain=0.05, dur=1.6)
    for f in range(6):
        add(buf, tone(hz(43 + f), 0.45, ((1, 1), (2, 0.4), (3, 0.12)), a=0.005, r=0.1, decay=0.2), 13.1 + f * 0.36, 0.11)
    add(buf, sweep(160, 1300, 1.1, partials=((1, 1), (2, 0.3), (3, 0.1))), 17.6, 0.06)
    add(buf, tone(hz(36), 1.4, ((1, 1), (2, 0.3)), a=0.005, r=0.5, decay=0.5), 18.95, 0.3)
    for m in (60, 64, 67, 71, 74):
        add(buf, tone(hz(m + 12), 2.4, ((1, 1), (2, 0.15)), a=0.01, r=0.9, decay=1.2), 18.95, 0.045)
    buf = lowpass(buf, 10000)[: int(DUR * SR)]
    buf *= 10 ** (-3 / 20) / np.abs(buf).max()
    write_wav(out_dir / "sfx.wav", buf)


def project(name, html):
    d = HERE / name
    (d / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (FILM / "assets" / "fonts").glob("Pretendard-*"):
        shutil.copy(f, d / "assets" / "fonts" / f.name)
    shutil.copy(FILM / "assets" / "gsap.min.js", d / "assets" / "gsap.min.js")
    if name == "b":
        shutil.copy(REPO / "fx" / "vendor" / "three.min.js", d / "assets" / "three.min.js")
    for f in ("hyperframes.json",):
        shutil.copy(FILM / f, d / f)
    (d / "meta.json").write_text(json.dumps({"id": f"sample-{name}", "name": f"sample-{name}"}))
    (d / "index.html").write_text(html, encoding="utf-8")
    return d


if __name__ == "__main__":
    da = project("a", build_a())
    db = project("b", build_b())
    sound(da / "assets")
    for f in ("bed.wav", "sfx.wav"):
        shutil.copy(da / "assets" / f, db / "assets" / f)
    print("ok", da, db)
