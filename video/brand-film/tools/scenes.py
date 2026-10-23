"""브랜드 필름 본편 12장면 생성기 (애니메이션 포함).

원칙: 툭툭 끊기지 않게. 모든 등장·이동은 0.8~1.4 s의 긴 감속, 글자는 단어마다 흐림+투명도로 풀리고,
퇴장은 등장보다 짧고 부드럽게. 장면 끝 상태가 다음 장면 첫 상태와 이어진다.
사용법: python3 tools/scenes.py  → compositions/sNN.html, index.html
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "compositions"
COMP.mkdir(exist_ok=True)

DARK, LIGHT, INK, SUB = "#0c0916", "#faf9fd", "#1b1530", "#a69cc8"
G = ["#FF03C8", "#EE06C1", "#DE0ABA", "#CD0EB4", "#BD12AD", "#AD16A7", "#9B19AB", "#881BB9", "#751DC7", "#621FD6", "#4F21E4", "#3C24F3"]

# 본편 장면 길이(초). 합계 72
DUR = [5, 7, 8, 8, 6, 7, 7, 5, 9, 4, 4, 2]
INTRO, OUTRO = 12.0, 7.5

FONTS = "".join(
    f'@font-face {{ font-family: "Pretendard"; font-weight: {w}; src: url("assets/fonts/Pretendard-{n}.otf"); }}\n'
    for w, n in [(900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")]
)
BASE = FONTS + f"""
#root {{ position: absolute; inset: 0; overflow: hidden; font-family: "Pretendard", sans-serif; background: {DARK}; }}
.grad {{ background: linear-gradient(100deg, #ff03c8, #a518a4 55%, #6a4dff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.say {{ position: absolute; font-weight: 800; color: #fff; letter-spacing: -0.03em; line-height: 1.16; }}
.say .w {{ display: inline-block; margin-right: 0.24em; will-change: transform, filter, opacity; }}
.lab {{ position: absolute; font-weight: 600; color: {SUB}; font-size: 30px; letter-spacing: 0.01em; }}
.vig {{ position: absolute; inset: -40px; background: radial-gradient(ellipse at 50% 45%, rgba(60,36,243,0.11), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45)); }}

"""

# 공통 JS: 부드러운 등장/퇴장, 선 그리기
JS = """
      const IN = (sel, t, o = {}) => tl.fromTo(sel,
        { opacity: 0, y: o.y ?? 26, filter: `blur(${o.b ?? 14}px)` },
        { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d ?? 1.1, ease: o.e ?? "power3.out", stagger: o.s ?? 0.085 }, t);
      const OUT = (sel, t, o = {}) => tl.to(sel,
        { opacity: 0, y: o.y ?? -14, filter: `blur(${o.b ?? 12}px)`, duration: o.d ?? 0.7, ease: "power2.inOut", stagger: o.s ?? 0.03 }, t);
      const FADE = (sel, t, d = 0.9, from = 0) => tl.fromTo(sel, { opacity: from }, { opacity: 1, duration: d, ease: "sine.inOut" }, t);
      if (document.querySelector(".o")) gsap.set(".o", { transformOrigin: "50% 50%" });
      const DRAW = (sel, t, d = 1.2, e = "power2.inOut", s = 0) => {
        gsap.utils.toArray(sel).forEach((el, i) => {
          const L = el.getTotalLength();
          el.setAttribute("stroke-dasharray", `${L} ${L}`);
          tl.fromTo(el, { attr: { "stroke-dashoffset": L } }, { attr: { "stroke-dashoffset": 0 }, duration: d, ease: e }, t + i * s);
        });
      };
"""


def say(text, size, left, top, sid, color="#fff", extra=""):
    """'모든 대화는,|[목소리]에서|시작합니다' → 단어 span. | 는 줄바꿈, [] 는 그라데이션(여러 단어 가능)."""
    lines, on = [], False
    for line in text.split("|"):
        ws = []
        for w in line.split(" "):
            segs, cur = [], ""
            for ch in w:
                if ch in "[]":
                    if cur:
                        segs.append((cur, on))
                    cur, on = "", ch == "["
                else:
                    cur += ch
            if cur:
                segs.append((cur, on))
            inner = "".join(f'<span class="grad">{t}</span>' if g else t for t, g in segs)
            ws.append(f'<span class="w {sid}-w">{inner}</span>')
        lines.append("".join(ws))
    return f'<div class="say" id="{sid}-say" style="left:{left}px;top:{top}px;font-size:{size}px;color:{color};{extra}">{"<br/>".join(lines)}</div>'


def scene(sid, dur, body, script, css="", bg=DARK):
    html = f"""<template>
  <style>
{BASE}
    #root {{ background: {bg}; }}
{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div id="{sid}-all" class="clip" data-start="0" data-duration="{dur}" data-track-index="1" data-layout-allow-overflow data-layout-allow-overlap>
{body}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{JS}
{script}
      if (document.querySelector("#{sid}-all .vig")) tl.fromTo("#{sid}-all .vig", {{ x: -40, y: -16, scale: 1.0 }}, {{ x: 40, y: 16, scale: 1.06, duration: {dur}, ease: "sine.inOut" }}, 0);
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
    (COMP / f"{sid}.html").write_text(html, encoding="utf-8")


def gdef(gid, x1, x2, vertical=False):
    a = f'x1="0" y1="{x1}" x2="0" y2="{x2}"' if vertical else f'x1="{x1}" y1="0" x2="{x2}" y2="0"'
    return f'<linearGradient id="{gid}" {a} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'


def svg(inner, defs="", sid="x", style=""):
    f = (f'<filter id="{sid}-glow" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2720" height="1880"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
         f'<filter id="{sid}-glows" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2720" height="1880"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;overflow:visible;{style}"><defs>{f}{defs}</defs>{inner}</svg>'


def wave_heights(n, seed, amp=1.0):
    s, out = seed, []
    for k in range(n):
        s = (s * 1664525 + 1013904223) % 4294967296
        env = math.sin(math.pi * (k + 0.5) / n) ** 0.7
        out.append((0.15 + 0.85 * s / 4294967296) * env * amp)
    return out


C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))


def iso(x, y, z, ox, oy, k):
    return (ox + (x - y) * C30 * k, oy + (x + y) * S30 * k - z * k)


def box(x, y, z, w, d, h, ox, oy, k, top, left, right, extra=""):
    P = lambda a, b, c: "%.1f,%.1f" % iso(a, b, c, ox, oy, k)
    t = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    l = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    r = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    return (f'<polygon points="{" ".join(l)}" fill="{left}" {extra}/><polygon points="{" ".join(r)}" fill="{right}" {extra}/>'
            f'<polygon points="{" ".join(t)}" fill="{top}" {extra}/>')


# 인트로 마지막 화면의 심볼 위치(build_intro.py와 같은 계산)
SYM_S = 1920 * 0.5 / 314
SYM_X, SYM_Y = 960 - 122 * SYM_S, 540 - 45 * SYM_S - 40
STRIPE_ANG = math.degrees(math.atan2(4.045 - 73.183, 83.967 - 55.374))  # 로고 사선 각도(약 -67.5°)

# ================================================================ s01 로고에서 신호로 (5 s)
lx, ly = SYM_X + 56 * SYM_S, SYM_Y + 40 * SYM_S
s01 = f"""
      <div id="s01-dark" style="position:absolute;inset:0;background:{DARK}"></div>
      <div class="vig" id="s01-vig"></div>
      <div id="s01-light" style="position:absolute;inset:0;background:{LIGHT}"></div>
      <img id="s01-last" src="assets/intro_last.png" style="position:absolute;left:0;top:0;width:1920px;height:1080px" />
      <img id="s01-sym" src="assets/brand/symbol_purple.svg" style="position:absolute;left:{SYM_X:.1f}px;top:{SYM_Y:.1f}px;width:{84 * SYM_S:.1f}px;height:{90 * SYM_S:.1f}px" />
      {svg(f'''<g id="s01-beam"><path id="s01-line" d="M{lx:.0f} {ly:.0f} L3200 {ly:.0f}" stroke="url(#s01-g)" stroke-width="10" stroke-linecap="round" filter="url(#s01-glow)"/></g>
        {''.join(f'<path class="s01-st" d="M{700 + i * 160} {ly + ((i * 53) % 7 - 3) * 60:.0f} l{220 + i * 15} 0" stroke="#fff" stroke-opacity="{0.10 + 0.03 * (i % 3)}" stroke-width="2"/>' for i in range(9))}''',
        gdef("s01-g", lx, 2200), "s01")}
"""
s01_js = f"""
      // 인트로 마지막 화면 → 워드마크만 서서히 사라지고 심볼만 남음
      tl.to("#s01-last", {{ opacity: 0, duration: 0.9, ease: "sine.inOut" }}, 0.15);
      // 심볼에서 신호선이 오른쪽으로 뻗어 나감
      tl.fromTo("#s01-line", {{ attr: {{ d: "M{lx:.0f} {ly:.0f} L{lx + 1:.0f} {ly:.0f}" }} }}, {{ attr: {{ d: "M{lx:.0f} {ly:.0f} L3200 {ly:.0f}" }}, duration: 1.5, ease: "power3.inOut" }}, 0.7);
      // 밝은 면이 오른쪽에서부터 걷히며 어두운 공간이 드러남
      tl.fromTo("#s01-light", {{ clipPath: "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)" }},
        {{ clipPath: "polygon(0% 0%, 0% 0%, -10% 100%, 0% 100%)", duration: 1.8, ease: "power2.inOut" }}, 1.1);
      // 심볼은 왼쪽으로 물러나며 흐려지고, 카메라가 선을 따라 가운데로
      tl.to("#s01-sym", {{ x: -420, opacity: 0, filter: "blur(10px)", duration: 1.6, ease: "power2.inOut" }}, 1.9);
      tl.to("#s01-beam", {{ y: {540 - ly:.0f}, duration: 2.0, ease: "power2.inOut" }}, 2.0);
      tl.to("#s01-line", {{ attr: {{ d: "M-200 {ly:.0f} L3200 {ly:.0f}" }}, duration: 1.8, ease: "power2.inOut" }}, 2.2);
      tl.fromTo(".s01-st", {{ opacity: 0, x: 200 }}, {{ opacity: 1, x: -600, duration: 2.2, ease: "sine.inOut", stagger: 0.05 }}, 1.8);
      tl.to(".s01-st", {{ opacity: 0, duration: 0.5, ease: "sine.inOut" }}, 4.42);
"""
scene("s01", DUR[0], s01, s01_js)

# ================================================================ s02 목소리의 시작 (7 s)
N2 = 36
layers, idx = [], 0
for li, (op, blur, sc, seed) in enumerate([(0.25, 6, 0.75, 3), (0.5, 2, 0.9, 7), (1, 0, 1.0, 11)]):
    bars = "".join(
        f'<rect class="s02-b s02-l{li} o" x="{1000 + k * 22 + li * 6}" y="240" width="9" height="600" rx="4.5" fill="{G[min(11, k // 3)]}" opacity="{op}"/>'
        for k in range(N2))
    layers.append(f'<g style="filter:blur({blur}px)">{bars}</g>')
H2 = [wave_heights(N2, s, a) for s, a in [(3, 0.75), (7, 0.9), (11, 1.0)]]
s02 = f"""
      <div class="vig"></div>
      {svg(f'<path id="s02-line" d="M-200 540 L2120 540" stroke="url(#s02-g)" stroke-width="10" stroke-linecap="round" filter="url(#s02-glow)"/>' + ''.join(layers), gdef("s02-g", 0, 1920), "s02")}
      {say("모든 대화는,|[목소리]에서|시작합니다", 96, 150, 380, "s02")}
"""
s02_js = f"""
      const H = {json.dumps([[round(h, 3) for h in hs] for hs in H2])};
      // 선이 파형 자리로 모이며 막대가 솟음(가운데부터)
      tl.to("#s02-line", {{ attr: {{ d: "M1000 540 L1790 540" }}, duration: 1.2, ease: "power3.inOut" }}, 0);
      tl.to("#s02-line", {{ opacity: 0, duration: 0.6, ease: "sine.inOut" }}, 1.0);
      for (let li = 0; li < 3; li++) {{
        gsap.utils.toArray(".s02-l" + li).forEach((el, k) => {{
          const d = Math.abs(k - {N2 / 2}) * 0.018;
          tl.fromTo(el, {{ scaleY: 0.012 }}, {{ scaleY: Math.max(0.02, H[li][k]), duration: 1.2, ease: "power3.out" }}, 0.55 + d + li * 0.06);
          // 말하는 듯 부드럽게 오르내림(사인 이징, 끊김 없이 이어짐)
          let t = 1.9 + d + li * 0.06, s = (k + 1) * 9301 + li * 49297;
          while (t < 5.6) {{
            s = (s * 1664525 + 1013904223) % 4294967296;
            const amp = (0.25 + 0.75 * s / 4294967296) * H[li][k] * 1.15 + 0.02;
            tl.to(el, {{ scaleY: amp, duration: 0.42, ease: "sine.inOut" }}, t);
            t += 0.42;
          }}
          tl.to(el, {{ scaleY: 0.012, duration: 0.9, ease: "power2.inOut" }}, 5.7 + d * 0.5);
        }});
      }}
      IN(".s02-w", 1.2);
      OUT(".s02-w", 6.0);
      // 끝: 다시 한 줄의 신호선(다음 장면의 전화망 선과 같은 높이)
      tl.to("#s02-line", {{ attr: {{ d: "M-200 548 L2120 548" }}, opacity: 1, duration: 1.0, ease: "power3.inOut" }}, 5.95);
"""
scene("s02", DUR[1], s02, s02_js)

# ================================================================ s03 전화망 → AI 게이트웨이 (8 s)
gate = "".join(
    f'<rect class="s03-gate o" x="{900 + i * 28}" y="{300 + i * 14}" width="{120 - i * 4}" height="{480 - i * 28}" rx="18" fill="none" stroke="url(#s03-g)" stroke-opacity="{1 - i * 0.18:.2f}" stroke-width="{4 - i * 0.5}"/>'
    for i in range(5))
s03 = f"""
      <div class="vig"></div>
      {svg(f'''
        <path id="s03-grey" d="M-200 548 L960 540" stroke="#8a8399" stroke-opacity=".55" stroke-width="3"/>
        <path id="s03-dots" d="M-200 548 L960 540" stroke="#6b6380" stroke-width="8" stroke-linecap="round" stroke-dasharray="2 22"/>
        <path id="s03-in" d="M-200 548 L2120 540" stroke="url(#s03-g)" stroke-width="10" stroke-linecap="round" filter="url(#s03-glow)"/>
        {gate}
        <path id="s03-out" d="M960 540 L2120 520" stroke="url(#s03-g)" stroke-width="10" stroke-linecap="round" filter="url(#s03-glow)"/>
        <circle id="s03-pulse" cx="-40" cy="546" r="9" fill="#fff" filter="url(#s03-glows)"/>
        {''.join(f'<path class="s03-st" d="M{1060 + i * 95} {528 - i * 2 + ((i * 37) % 5 - 2) * 26} l{90 + i * 8} -2" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>' for i in range(9))}
      ''', gdef("s03-g", 900, 1980), "s03")}
      <div class="lab" id="s03-l1" style="left:120px;top:610px">전화망</div>
      <div class="lab" id="s03-l2" style="left:870px;top:830px;color:#fff">AI 봇 게이트웨이</div>
      {say("전화가 걸려 오는 순간,|AI가 [함께 듣습니다]", 72, 120, 150, "s03")}
"""
s03_js = """
      // 앞 장면의 그라데이션 선이 관문 앞에서 회색 전화망으로 식어 감
      tl.to("#s03-in", { opacity: 0, duration: 1.0, ease: "sine.inOut" }, 0.1);
      FADE(["#s03-grey", "#s03-dots"], 0.1, 1.0);
      // 관문이 겹겹이 떠오름
      tl.fromTo(".s03-gate", { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 1.3, ease: "expo.out", stagger: 0.09 }, 0.5);
      DRAW("#s03-out", 1.4, 1.4, "power2.inOut");
      // 신호 하나가 관문을 통과(통과 순간 색이 바뀜)
      tl.fromTo("#s03-pulse", { attr: { cx: -40, cy: 547 }, fill: "#9a94aa" }, { attr: { cx: 940, cy: 541 }, duration: 1.6, ease: "power2.in" }, 2.2);
      tl.to("#s03-pulse", { fill: "#ff3fd6", duration: 0.2, ease: "none" }, 3.75);
      tl.to("#s03-pulse", { attr: { cx: 2050, cy: 522 }, duration: 1.4, ease: "power2.out" }, 3.8);
      tl.to(".s03-gate", { scale: 1.06, duration: 0.25, ease: "power2.out", stagger: 0.03 }, 3.75);
      tl.to(".s03-gate", { scale: 1, duration: 0.6, ease: "power2.inOut", stagger: 0.03 }, 4.0);
      tl.fromTo(".s03-st", { opacity: 0, x: 150 }, { opacity: 1, x: -450, duration: 3.6, ease: "sine.inOut", stagger: 0.06 }, 3.6);
      IN(".s03-w", 0.5);
      IN(["#s03-l1", "#s03-l2"], 1.6, { s: 0.3, y: 10 });
      OUT([".s03-w", "#s03-l1", "#s03-l2", ".s03-gate", "#s03-grey", "#s03-dots", ".s03-st"], 7.15, { s: 0.015 });
      tl.to("#s03-out", { opacity: 0, duration: 0.6, ease: "sine.inOut" }, 7.3);
"""
scene("s03", DUR[2], s03, s03_js)

# ================================================================ s04 말을 글로, 뜻으로 (8 s)
rnd = random.Random(4)
NP = 260
sx, sy, tx, ty, op = [], [], [], [], []
for i in range(NP):
    sx.append(round(200 + rnd.gauss(0, 50)))
    sy.append(round(560 + rnd.gauss(0, 90)))
    tx.append(round(1130 + rnd.random() * 560))
    ty.append(round(520 + rnd.gauss(0, 22)))
    op.append(round(0.4 + 0.5 * rnd.random(), 2))
parts = "".join(f'<circle class="s04-p" cx="{sx[i]}" cy="{sy[i]}" r="{rnd.uniform(1.6, 4.2):.1f}" fill="{G[min(11, int(i / NP * 12))]}" opacity="0"/>' for i in range(NP))
hs = wave_heights(14, 5)
wbars = "".join(f'<rect class="s04-b o" x="{120 + k * 18}" y="360" width="8" height="400" rx="4" fill="{G[k * 11 // 13]}"/>' for k in range(14))
chars = "".join(f'<b class="s04-c" style="display:inline-block;font-weight:700">{"&nbsp;" if c == " " else c}</b>' for c in "보험금 청구")
chars2 = "".join(f'<b class="s04-c" style="display:inline-block;font-weight:700">{"&nbsp;" if c == " " else c}</b>' for c in "하고 싶어요")
s04 = f"""
      <div class="vig"></div>
      {svg(wbars + parts, "", "s04")}
      <div id="s04-text" style="position:absolute;left:1120px;top:500px;font-size:66px;font-weight:700;color:#fff;letter-spacing:-0.02em;white-space:nowrap">
        <span style="position:relative;display:inline-block">{chars}<i id="s04-ul" style="position:absolute;left:0;right:0;bottom:-14px;height:10px;border-radius:5px;background:linear-gradient(90deg,#ff03c8,#3c24f3)"></i></span>{chars2}
      </div>
      <div id="s04-intent" style="position:absolute;left:1120px;top:620px;font-size:34px;font-weight:600;color:{SUB}">의도 <span style="color:#fff;margin-left:14px">보험금 청구</span></div>
      {say("말을 글로, 글을 [뜻]으로", 72, 120, 150, "s04")}
"""
s04_js = f"""
      const H = {json.dumps([round(h, 3) for h in hs])};
      const SX = {sx}, SY = {sy}, TX = {tx}, TY = {ty}, OP = {op};
      // 왼쪽에서 파형이 말하듯 움직임
      gsap.utils.toArray(".s04-b").forEach((el, k) => {{
        tl.fromTo(el, {{ scaleY: 0.02 }}, {{ scaleY: H[k], duration: 1.0, ease: "power3.out" }}, 0.2 + Math.abs(k - 7) * 0.03);
        let t = 1.2, s = k * 7919 + 13;
        while (t < 3.0) {{ s = (s * 1664525 + 1013904223) % 4294967296; tl.to(el, {{ scaleY: (0.3 + 0.7 * s / 4294967296) * H[k] + 0.03, duration: 0.4, ease: "sine.inOut" }}, t); t += 0.4; }}
        tl.to(el, {{ scaleY: 0.02, opacity: 0.25, duration: 1.0, ease: "power2.inOut" }}, 3.0 + k * 0.02);
      }});
      // 목소리가 입자로 풀려 오른쪽으로 흘러가 글자가 됨
      tl.fromTo(".s04-p", {{ attr: {{ cx: i => SX[i], cy: i => SY[i] }}, opacity: 0 }},
        {{ attr: {{ cx: i => TX[i], cy: i => TY[i] }}, opacity: i => OP[i], duration: 2.0, ease: "power2.inOut", stagger: {{ each: 0.006 }} }}, 1.3);
      tl.to(".s04-p", {{ opacity: 0, duration: 0.6, ease: "sine.inOut", stagger: {{ each: 0.006 }} }}, 3.3);
      tl.fromTo(".s04-c", {{ opacity: 0, filter: "blur(12px)", y: 8 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.9, ease: "power2.out", stagger: 0.07 }}, 2.6);
      tl.fromTo("#s04-ul", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 1.0, ease: "power3.inOut" }}, 3.9);
      IN("#s04-intent", 4.4, {{ y: 12 }});
      IN(".s04-w", 0.4);
      OUT([".s04-w", "#s04-text", "#s04-intent", ".s04-b"], 7.1);
"""
scene("s04", DUR[3], s04, s04_js)

# ================================================================ s05 알맞은 AI로 (6 s)
nodes = [(1320, 330), (1420, 560), (1320, 790)]
branches = "".join(f'<path class="s05-br" d="M760 560 C 1000 560, 1060 {y}, {x - 60} {y}" fill="none" stroke="#3a3350" stroke-width="4" stroke-linecap="round"/>' for x, y in nodes)
hot = f'<path id="s05-hot" d="M760 560 C 1000 560, 1060 560, 1360 560" fill="none" stroke="url(#s05-g)" stroke-width="9" stroke-linecap="round" filter="url(#s05-glow)"/>'
nd = "".join(f'<circle class="s05-n o" cx="{x}" cy="{y}" r="46" fill="#1c1730" stroke="#3a3350" stroke-width="3"/>' for x, y in nodes)
lit = '<circle id="s05-r" class="o" cx="1420" cy="560" r="74" fill="none" stroke="url(#s05-g)" stroke-width="3"/><circle id="s05-w" class="o" cx="1420" cy="560" r="52" fill="#faf9fd"/><circle id="s05-c" class="o" cx="1420" cy="560" r="24" fill="url(#s05-g)"/>'
s05 = f"""
      <div class="vig"></div>
      {svg(f'<path id="s05-main" d="M-200 560 L760 560" stroke="url(#s05-g)" stroke-width="9" stroke-linecap="round" filter="url(#s05-glow)"/>' + branches + hot + nd + lit, gdef("s05-g", 0, 1500), "s05")}
      <div class="lab" id="s05-lab" style="left:1520px;top:540px;color:#fff;font-size:34px">가장 알맞은 AI</div>
      {say("질문에 [가장 알맞은 AI]로", 72, 120, 150, "s05")}
"""
s05_js = """
      DRAW("#s05-main", 0.0, 1.0, "power2.out");
      DRAW(".s05-br", 0.7, 1.1, "power2.inOut", 0.08);
      tl.fromTo(".s05-n", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.9, ease: "back.out(1.3)", stagger: 0.1 }, 1.4);
      // 질문이 셋 중 하나를 골라 흘러감
      DRAW("#s05-hot", 2.3, 1.0, "power2.inOut");
      tl.fromTo("#s05-w", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.8, ease: "back.out(1.4)" }, 3.1);
      tl.fromTo("#s05-c", { scale: 0 }, { scale: 1, duration: 0.7, ease: "back.out(1.6)" }, 3.25);
      tl.fromTo("#s05-r", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 0.6, duration: 1.1, ease: "expo.out" }, 3.3);
      tl.to(".s05-n", { opacity: 0.45, duration: 0.8, ease: "sine.inOut" }, 3.2);
      IN("#s05-lab", 3.6, { y: 10 });
      IN(".s05-w", 0.4);
      OUT([".s05-w", "#s05-lab", ".s05-br", ".s05-n", "#s05-hot", "#s05-main", "#s05-r", "#s05-c"], 5.2, { s: 0.015 });
      tl.to("#s05-w", { scale: 0.5, opacity: 0, duration: 0.7, ease: "power2.inOut" }, 5.25);
"""
scene("s05", DUR[4], s05, s05_js)

# ================================================================ s06 목소리가 열쇠 (7 s)
rings = []
for i in range(9):
    R = 90 + i * 34
    pts = []
    for a in range(0, 361, 4):
        th = math.radians(a - 90)
        wob = 1 + 0.05 * math.sin(th * (3 + i % 4) + i) * (i / 8)
        pts.append(f"{960 + R * wob * math.cos(th):.1f},{560 + R * wob * math.sin(th):.1f}")
    rings.append(f'<polyline class="s06-r" points="{" ".join(pts)}" fill="none" stroke="{G[11 - i]}" stroke-width="{3 if i % 2 else 5}" stroke-linecap="round" opacity="{1 - i * 0.07:.2f}"/>')
lock = f'''<g id="s06-lock" class="o"><g transform="translate(960 560)">
  <path id="s06-sh" d="M-34 -10 V-44 a34 34 0 0 1 68 0 V-10" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>
  <rect x="-50" y="-12" width="100" height="78" rx="14" fill="#fff"/><circle cx="0" cy="22" r="10" fill="{DARK}"/><rect x="-4" y="22" width="8" height="22" rx="4" fill="{DARK}"/></g></g>'''
s06 = f"""
      <div class="vig"></div>
      {svg(f'<g id="s06-rings">{"".join(rings)}</g><circle id="s06-pulse" class="o" cx="960" cy="560" r="400" fill="none" stroke="url(#s06-g)" stroke-width="2" filter="url(#s06-glows)"/>' + lock, gdef("s06-g", 560, 1360), "s06")}
      {say("목소리 하나로,|[본인 확인]까지", 72, 120, 150, "s06")}
      <div class="lab" id="s06-lab" style="left:1420px;top:880px;color:#fff">화자인증</div>
"""
s06_js = """
      // 목소리 지문이 안쪽부터 그려짐
      DRAW(".s06-r", 0.2, 1.5, "power2.inOut", 0.11);
      tl.fromTo("#s06-rings", { rotation: -14, transformOrigin: "960px 560px" }, { rotation: 6, duration: 7, ease: "sine.inOut" }, 0);
      tl.fromTo("#s06-lock", { scale: 0.8, opacity: 0, filter: "blur(10px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 1.0, ease: "power3.out" }, 1.5);
      // 열림: 고리가 부드럽게 들리며 회전, 빛의 파동이 퍼짐
      tl.to("#s06-sh", { rotation: -24, y: -10, svgOrigin: "34 -10", duration: 0.9, ease: "back.out(1.4)" }, 3.2);
      tl.fromTo("#s06-pulse", { scale: 0.3, opacity: 0.9 }, { scale: 1.15, opacity: 0, duration: 1.6, ease: "power2.out" }, 3.25);
      tl.to(".s06-r", { opacity: 1, duration: 0.5, ease: "sine.out" }, 3.25);
      IN(".s06-w", 0.5);
      IN("#s06-lab", 3.6, { y: 10 });
      OUT([".s06-w", "#s06-lab", "#s06-lock"], 6.2);
      tl.to("#s06-rings", { scale: 0.2, opacity: 0, duration: 0.9, ease: "power2.inOut" }, 6.0);
"""
scene("s06", DUR[5], s06, s06_js)

# ================================================================ s07 답, 그리고 역할 분담 (7 s)
s07 = f"""
      <div id="s07-low" style="position:absolute;left:0;top:540px;width:1920px;height:540px;background:{LIGHT}"></div>
      <div id="s07-seam" style="position:absolute;left:0;top:536px;width:1920px;height:8px;background:linear-gradient(90deg,#ff03c8,#a518a4 50%,#3c24f3)"></div>
      <div class="lab" id="s07-l1" style="left:120px;top:110px">고객에게</div>
      <div id="s07-bub" style="position:absolute;left:120px;top:190px;padding:0 64px;height:140px;border-radius:70px;background:linear-gradient(100deg,#ff03c8,#a518a4 50%,#3c24f3);color:#fff;font-size:52px;font-weight:700;display:flex;align-items:center;white-space:nowrap"><span id="s07-bt">네, 청구 접수를 도와드릴게요.</span></div>
      {say("단순 문의는|[AI]가 바로", 60, 1180, 200, "s07a")}
      <div class="lab" id="s07-l2" style="left:120px;top:620px;color:#6b6380">상담사에게</div>
      <div id="s07-card" style="position:absolute;left:120px;top:690px;width:760px;height:280px;border-radius:24px;background:#fff;box-shadow:0 18px 40px rgba(27,21,48,.12);padding:40px 48px">
        <div style="font-size:30px;font-weight:700;color:{INK}">상담 요약</div>
        <div style="margin-top:22px;font-size:30px;font-weight:500;color:#5d5672;line-height:1.6">
          <div class="s07-row">· 보험금 청구 문의</div><div class="s07-row">· 목소리로 본인 확인 완료</div><div class="s07-row">· 청구 접수 안내</div></div>
      </div>
      {say("깊은 상담은|[사람]이 더 깊게", 60, 1180, 730, "s07b", color=INK)}
"""
s07_js = """
      // 아래 절반이 밝게 차오르고 경계선이 그어짐
      tl.fromTo("#s07-low", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 1.2, ease: "power3.inOut" }, 0.1);
      tl.fromTo("#s07-seam", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 1.3, ease: "power3.inOut" }, 0.6);
      // 답변 말풍선이 왼쪽에서 펼쳐짐
      tl.fromTo("#s07-bub", { clipPath: "inset(0% 100% 0% 0% round 70px)", opacity: 0 }, { clipPath: "inset(0% 0% 0% 0% round 70px)", opacity: 1, duration: 1.1, ease: "power3.inOut" }, 1.0);
      IN("#s07-bt", 1.55, { y: 0, b: 10 });
      IN("#s07-l1", 0.8, { y: 10 });
      IN(".s07a-w", 1.4);
      // 상담 요약 카드가 떠오르고 줄마다 채워짐
      tl.fromTo("#s07-card", { y: 60, opacity: 0, filter: "blur(10px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 1.2, ease: "power3.out" }, 2.6);
      IN(".s07-row", 3.2, { y: 10, s: 0.22, d: 0.9 });
      IN("#s07-l2", 2.5, { y: 10 });
      IN(".s07b-w", 3.0);
      OUT([".s07a-w", ".s07b-w", "#s07-l1", "#s07-l2", "#s07-bub", "#s07-card"], 5.9, { s: 0.02 });
      tl.to("#s07-seam", { scaleX: 0, transformOrigin: "100% 50%", duration: 0.8, ease: "power2.inOut" }, 6.1);
      tl.to("#s07-low", { scaleY: 0, duration: 0.9, ease: "power3.inOut" }, 6.05);
"""
scene("s07", DUR[6], s07, s07_js)

# ================================================================ s08 카메라 후퇴: 서버 랙 (5 s)
k, ox, oy = 62, 900, 330
els = []
for i in range(-1, 9):
    a, b = iso(i, -1, 0, ox, oy, k), iso(i, 8, 0, ox, oy, k)
    els.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="#2a2440" stroke-width="1.5"/>')
    a, b = iso(-1, i, 0, ox, oy, k), iso(8, i, 0, ox, oy, k)
    els.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="#2a2440" stroke-width="1.5"/>')
for row in (0, 3.2):
    for i in range(7):
        x = i * 1.05
        els.append(f'<g class="s08-rack">{box(x, row, 0, 0.9, 1.1, 3.0, ox, oy, k, "#2b2445", "#1a1530", "#231c3a")}')
        for j in range(8):
            a = iso(x + 0.12, row + 1.1, 0.3 + j * 0.33, ox, oy, k)
            b = iso(x + 0.78, row + 1.1, 0.3 + j * 0.33, ox, oy, k)
            hl = row == 3.2 and i == 3 and j == 4
            litc = (i * 3 + j) % 5 == 0
            cls = ' id="s08-hl"' if hl else (' class="s08-led"' if litc else "")
            els.append(f'<path{cls} d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{"url(#s08-g)" if hl else ("#9d79ff" if litc else "#3a3350")}" stroke-width="{7 if hl else 3}" stroke-linecap="round" {"filter=" + chr(34) + "url(#s08-glow)" + chr(34) if hl else ""}/>')
        els.append("</g>")
HX, HY = iso(3 * 1.05 + 0.45, 3.2 + 1.1, 0.3 + 4 * 0.33, ox, oy, k)
s08 = f"""
      <div class="vig"></div>
      <div id="s08-cam" style="position:absolute;inset:0">
        {svg(''.join(els) + f'<circle id="s08-ring" class="o" cx="{HX:.0f}" cy="{HY:.0f}" r="60" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>', gdef("s08-g", HX - 40, HX + 40), "s08")}
      </div>
      {say("이 모든 대화가|[달리는 곳]", 72, 120, 150, "s08")}
      <div class="lab" id="s08-lab" style="left:{HX + 80:.0f}px;top:{HY + 40:.0f}px;color:#fff">방금 그 통화</div>
"""
s08_js = f"""
      // 연속 줌 아웃: 화면을 채우던 빛이 서버 랙 LED 한 칸이었음
      tl.fromTo("#s08-cam", {{ scale: 9, x: {960 - HX:.0f} * 9 / 9, y: {540 - HY:.0f}, transformOrigin: "{HX:.0f}px {HY:.0f}px" }},
        {{ scale: 1, x: 0, y: 0, duration: 2.8, ease: "power3.inOut" }}, 0);
      tl.fromTo("#s08-cam", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "sine.out" }}, 0);
      tl.fromTo(".s08-led", {{ opacity: 0.2 }}, {{ opacity: 1, duration: 1.0, ease: "sine.inOut", stagger: 0.02 }}, 1.4);
      tl.fromTo("#s08-ring", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 1.0, ease: "expo.out" }}, 2.6);
      IN(".s08-w", 2.0);
      IN("#s08-lab", 2.9, {{ y: 10 }});
      OUT([".s08-w", "#s08-lab", "#s08-ring"], 4.3);
      tl.to("#s08-cam", {{ opacity: 0, scale: 0.92, duration: 0.7, ease: "power2.inOut" }}, 4.3);
"""
scene("s08", DUR[7], s08, s08_js)

# ================================================================ s09 AI 인프라를 짓다 (9 s)
k, ox, oy = 60, 800, 420
steps = ["전산 설계", "통합배선", "네트워크", "출입보안", "통합관제", "유지보수"]
fl, labs = [], []
for f in range(6):
    z = f * 1.15
    g = [box(0, 0, z, 7, 4, 0.12, ox, oy, k, "#2b2445", "#16122a", "#1f1936")]
    det = []
    if f == 0:
        for gx in range(1, 7):
            a, b = iso(gx, 0.2, z + 0.13, ox, oy, k), iso(gx, 3.8, z + 0.13, ox, oy, k)
            det.append(f'<path class="s09-d0" d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="#6a4dff" stroke-width="1.5" stroke-dasharray="6 6" fill="none"/>')
    if f == 1:
        for c in range(4):
            pts = [iso(0.3, 0.6 + c * 0.8, z + 0.14, ox, oy, k), iso(4.5 + c * 0.5, 0.6 + c * 0.8, z + 0.14, ox, oy, k), iso(4.5 + c * 0.5, 3.6, z + 0.14, ox, oy, k)]
            det.append(f'<polyline class="s09-d1" points="{" ".join("%.0f,%.0f" % p for p in pts)}" fill="none" stroke="url(#s09-g)" stroke-width="4" filter="url(#s09-glows)"/>')
    if f == 2:
        for c in range(5):
            det.append(f'<g class="s09-d2">{box(0.6 + c * 1.25, 1.4, z + 0.12, 0.9, 1.2, 0.45, ox, oy, k, "#3a3060", "#241d40", "#2d2550")}')
            a = iso(0.75 + c * 1.25, 2.6, z + 0.35, ox, oy, k)
            det.append(f'<circle class="s09-led" cx="{a[0]:.0f}" cy="{a[1]:.0f}" r="4" fill="#9d79ff"/></g>')
    if f == 3:
        det.append(f'<g class="s09-d3">{box(3.0, 3.85, z + 0.12, 1.0, 0.1, 0.9, ox, oy, k, "#3a3060", "#9d79ff", "#6a4dff")}</g>')
    if f == 4:
        det.append(f'<g class="s09-d4">{box(1.0, 0.3, z + 0.12, 5.0, 0.12, 0.8, ox, oy, k, "#2d2550", "url(#s09-g)", "#3a3060")}</g>')
    if f == 5:
        a = iso(3.5, 2.0, z + 0.4, ox, oy, k)
        det.append(f'<g class="s09-d5"><circle cx="{a[0]:.0f}" cy="{a[1]:.0f}" r="34" fill="none" stroke="url(#s09-g)" stroke-width="5"/><path d="M{a[0] - 14:.0f} {a[1]:.0f} l10 10 l20 -22" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')
    a = iso(7.05, 2.0, z + 0.06, ox, oy, k)
    fl.append(f'<g id="s09-f{f}">{"".join(g)}{"".join(det)}<path class="s09-lead" id="s09-ld{f}" d="M{a[0]:.0f} {a[1]:.0f} L1460 {a[1]:.0f}" stroke="#9d79ff" stroke-width="1.5" fill="none"/></g>')
    labs.append(f'<div class="lab s09-lab" id="s09-lb{f}" style="left:1480px;top:{a[1] - 22:.0f}px;color:#fff;font-size:34px;font-weight:700">{steps[f]}</div>')
s09 = f"""
      <div class="vig"></div>
      <div id="s09-cam" style="position:absolute;inset:0">{svg(''.join(fl), gdef("s09-g", 700, 1300), "s09")}{''.join(labs)}</div>
      {say("[AI 인프라]를|짓습니다", 72, 120, 120, "s09")}
      <div class="lab" id="s09-sub" style="left:120px;top:900px">데이터센터 · 전산센터 · ESS · 스마트공장</div>
"""
s09_js = """
      // 아래층부터 차례로 내려앉으며 지어짐, 층마다 그 층의 일이 켜짐
      const T = [0.5, 1.75, 3.0, 4.25, 5.5, 6.6];
      for (let f = 0; f < 6; f++) {
        tl.fromTo("#s09-f" + f, { y: -70, opacity: 0 }, { y: 0, opacity: 1, duration: 1.2, ease: "power3.out" }, T[f]);
        IN("#s09-lb" + f, T[f] + 0.45, { y: 0, b: 10, d: 0.9 });
      }
      DRAW(".s09-lead", 0.9, 0.9, "power2.inOut", 1.25);
      tl.fromTo(".s09-d0", { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "sine.inOut", stagger: 0.08 }, 0.9);
      DRAW(".s09-d1", 2.1, 1.3, "power2.inOut", 0.12);
      tl.fromTo(".s09-d2", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out", stagger: 0.09 }, 3.35);
      tl.fromTo(".s09-led", { opacity: 0.2 }, { opacity: 1, duration: 0.6, ease: "sine.inOut", stagger: 0.12 }, 3.9);
      tl.fromTo(".s09-d3", { opacity: 0, scaleY: 0.2, transformOrigin: "50% 100%" }, { opacity: 1, scaleY: 1, duration: 0.9, ease: "power3.out" }, 4.6);
      tl.fromTo(".s09-d4", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "sine.inOut" }, 5.85);
      tl.fromTo(".s09-d5", { opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.9, ease: "back.out(1.4)" }, 6.95);
      // 장면 내내 아주 느린 카메라 이동(흐르는 느낌)
      tl.fromTo("#s09-cam", { scale: 0.97, x: 20 }, { scale: 1.02, x: -20, duration: 9, ease: "sine.inOut" }, 0);
      IN(".s09-w", 0.3);
      IN("#s09-sub", 1.2, { y: 10 });
      OUT([".s09-w", "#s09-sub", ".s09-lab"], 8.2, { s: 0.02 });
      tl.to("#s09-cam", { y: 260, opacity: 0, duration: 0.8, ease: "power2.in" }, 8.2);
"""
scene("s09", DUR[8], s09, s09_js)

# ================================================================ s10 미국 현장까지 (4 s)
dots = json.loads((ROOT / "assets/data/pacific_dots.json").read_text())["dots"]
L0, L1, A0, A1 = 95, 300, 10, 60
X = lambda lon: 60 + (lon - L0) / (L1 - L0) * 1800
Y = lambda lat: 160 + (A1 - lat) / (A1 - A0) * 800
dd = "".join(f'<circle cx="{X(lo):.0f}" cy="{Y(la):.0f}" r="3.2" fill="#3a3158"/>' for lo, la in dots)
kx, ky = X(127.0), Y(37.0)
us = [(-85.0, 43.0), (-82.8, 40.3), (-111.9, 34.2), (-98.0, 31.0), (-86.5, 35.8)]
arcs, pins = "", ""
for i, (lo, la) in enumerate(us):
    ux, uy = X(lo + 360), Y(la)
    mx, my = (kx + ux) / 2, min(ky, uy) - 260
    arcs += f'<path class="s10-arc" d="M{kx:.0f} {ky:.0f} Q {mx:.0f} {my:.0f} {ux:.0f} {uy:.0f}" fill="none" stroke="url(#s10-g)" stroke-width="3" filter="url(#s10-glows)"/>'
    pins += f'<g class="s10-pin o"><circle cx="{ux:.0f}" cy="{uy:.0f}" r="18" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2"/><circle cx="{ux:.0f}" cy="{uy:.0f}" r="8" fill="#fff"/></g>'
kr = f'<g id="s10-kr" class="o"><circle cx="{kx:.0f}" cy="{ky:.0f}" r="22" fill="none" stroke="#ff03c8" stroke-width="3"/><circle cx="{kx:.0f}" cy="{ky:.0f}" r="9" fill="#ff03c8"/></g>'
s10 = f"""
      <div class="vig"></div>
      <div id="s10-cam" style="position:absolute;inset:0">
        {svg(f'<g id="s10-dots">{dd}</g>' + arcs + pins + kr, gdef("s10-g", kx, X(-82 + 360)), "s10")}
        <div class="lab" id="s10-l1" style="left:{kx - 40:.0f}px;top:{ky + 30:.0f}px;color:#fff">한국</div>
        <div class="lab" id="s10-l2" style="left:{X(-100 + 360):.0f}px;top:{Y(28):.0f}px;color:#fff">미국 5개 주</div>
      </div>
      {say("미국 배터리 · 태양광 공장의|[현장까지]", 64, 120, 110, "s10")}
"""
s10_js = """
      // 아래에서 위로 떠오르며 지도가 드러남(앞 장면의 하강과 이어짐)
      tl.fromTo("#s10-cam", { y: -200, scale: 1.08, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 1.2, ease: "power3.out" }, 0);
      tl.fromTo("#s10-kr", { scale: 0 }, { scale: 1, duration: 0.7, ease: "back.out(1.6)" }, 0.6);
      DRAW(".s10-arc", 0.9, 1.2, "power2.inOut", 0.08);
      tl.fromTo(".s10-pin", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.6)", stagger: 0.08 }, 1.9);
      IN(["#s10-l1", "#s10-l2"], 1.2, { y: 8, s: 0.6 });
      IN(".s10-w", 0.3);
      OUT([".s10-w", "#s10-cam"], 3.4, { s: 0.05, d: 0.6 });
"""
scene("s10", DUR[9], s10, s10_js)

# ================================================================ s11 한 팀 (4 s)
k, ox, oy = 66, 980, 560
up = box(0, 0, 2.2, 6, 6, 0.35, ox, oy - 240, k, "#faf9fd", "#d9d0f5", "#c2b3f2")
dn = box(0, 0, 0, 6, 6, 0.6, ox, oy, k, "#2b2445", "#16122a", "#1f1936")
grid = "".join(
    f'<path class="s11-gr" d="M{iso(i, 0, 0.61, ox, oy, k)[0]:.0f} {iso(i, 0, 0.61, ox, oy, k)[1]:.0f} L{iso(i, 6, 0.61, ox, oy, k)[0]:.0f} {iso(i, 6, 0.61, ox, oy, k)[1]:.0f}" stroke="#6a4dff" stroke-width="1.5" opacity=".7"/>'
    for i in range(1, 6))
hs = wave_heights(16, 9)
wv = "".join(
    (lambda a, b: f'<path class="s11-wv o" d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{G[i * 11 // 15]}" stroke-width="8" stroke-linecap="round" style="transform-origin:50% 100%"/>')(
        iso(0.6 + i * 0.32, 3, 2.56, ox, oy - 240, k), iso(0.6 + i * 0.32, 3, 2.56 + h * 1.4, ox, oy - 240, k))
    for i, h in enumerate(hs))
c0, c1 = iso(3, 3, 0.6, ox, oy, k), iso(3, 3, 2.2, ox, oy - 240, k)
beam = f'<rect id="s11-beam" x="{c0[0] - 14:.0f}" y="{c1[1]:.0f}" width="28" height="{c0[1] - c1[1]:.0f}" rx="14" fill="url(#s11-gv)" filter="url(#s11-glow)"/>'
s11 = f"""
      <div class="vig"></div>
      {svg(f'<g id="s11-dn">{dn}{grid}</g>' + beam + f'<g id="s11-up">{up}{wv}</g>', gdef("s11-gv", c1[1], c0[1], vertical=True), "s11")}
      <div class="lab" id="s11-la" style="left:1450px;top:330px;color:#fff;font-size:36px">AI</div>
      <div class="lab" id="s11-li" style="left:1450px;top:700px;color:#fff;font-size:36px">인프라</div>
      {say("인프라 구축부터|AI 도입까지,|[한 팀이]", 68, 120, 150, "s11")}
      <div id="s11-proof" style="position:absolute;left:120px;top:830px;font-size:30px;font-weight:600;color:{SUB};line-height:1.7">조달청 우수조달물품 · 중기부 혁신제품<br/>등록 특허 7건</div>
"""
s11_js = f"""
      tl.fromTo("#s11-dn", {{ y: 90, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 1.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s11-up", {{ y: -160, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 1.3, ease: "power3.inOut" }}, 0.3);
      tl.fromTo("#s11-beam", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.9, ease: "power3.inOut" }}, 1.3);
      gsap.set(".s11-wv", {{ transformOrigin: "50% 100%" }});
      tl.fromTo(".s11-wv", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.8, ease: "power3.out", stagger: 0.03 }}, 1.8);
      IN(["#s11-la", "#s11-li"], 1.2, {{ y: 8, s: 0.15 }});
      IN(".s11-w", 0.2);
      IN("#s11-proof", 1.0, {{ y: 10 }});
      OUT([".s11-w", "#s11-proof", "#s11-la", "#s11-li"], 3.3, {{ s: 0.02, d: 0.55 }});
      tl.to(["#s11-up", "#s11-dn", "#s11-beam"], {{ scale: 0.6, y: {540 - oy:.0f}, opacity: 0, transformOrigin: "{ox:.0f}px {oy:.0f}px", duration: 0.7, ease: "power2.in" }}, 3.3);
"""
scene("s11", DUR[10], s11, s11_js)

# ================================================================ s12 아웃트로로 (2 s)
OB = [960 + (k - 5.5) * 46 for k in range(12)]  # 아웃트로 첫 프레임의 막대 중심
dashes = "".join(f'<rect class="s12-d" x="{x - 9:.0f}" y="535.8" width="18" height="8.4" rx="4.2" fill="{G[k]}"/>' for k, x in enumerate(OB))
streaks = "".join(
    f'<path class="s12-s" d="M{960 + (1 if i % 2 else -1) * (900 - i * 50)} {540 + (i % 3 - 1) * (300 - i * 18)} L{960 + (1 if i % 2 else -1) * (760 - i * 46)} {540 + (i % 3 - 1) * (250 - i * 15)}" stroke="#9d79ff" stroke-opacity="{0.15 + i * 0.02:.2f}" stroke-width="2"/>'
    for i in range(10))
s12 = f"""
      {svg(f'<path id="s12-line" d="M260 540 L1660 540" stroke="url(#s12-g)" stroke-width="6" stroke-linecap="round" filter="url(#s12-glows)"/>' + streaks + dashes, gdef("s12-g", 260, 1660), "s12")}
"""
s12_js = """
      // 흩어진 빛이 가운데로 모이며 한 줄 → 아웃트로 첫 화면(작은 막대 12개)
      tl.fromTo(".s12-s", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "sine.out" }, 0);
      tl.to(".s12-s", { x: (i) => (i % 2 ? -1 : 1) * 380, y: (i) => -((i % 3) - 1) * 180, opacity: 0, duration: 0.95, ease: "power3.in", stagger: 0.02 }, 0.3);
      tl.fromTo("#s12-line", { scaleX: 0, transformOrigin: "50% 50%" }, { scaleX: 1, duration: 0.8, ease: "power3.out" }, 0.15);
      tl.to("#s12-line", { scaleX: 0.36, opacity: 0, duration: 0.8, ease: "power2.inOut" }, 1.05);
      tl.fromTo(".s12-d", { opacity: 0, scaleX: 2.4, transformOrigin: "50% 50%" }, { opacity: 1, scaleX: 1, duration: 0.75, ease: "power2.out", stagger: 0.01 }, 1.15);
"""
scene("s12", DUR[11], s12, s12_js)

# ================================================================ index.html
t = INTRO
hosts = []
for i, d in enumerate(DUR):
    sid = f"s{i + 1:02d}"
    hosts.append(f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{t:.2f}" data-duration="{d}"
        data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index: {i + 2}"></div>''')
    t += d
OUT_START = t
TOTAL = t + OUTRO
(ROOT / "index.html").write_text(f"""<!doctype html>
<html lang="ko" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {DARK}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      .full {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: contain; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-fps="60" data-width="1920" data-height="1080">
      <video id="intro-video" class="clip full" src="assets/intro.mp4" data-start="0" data-duration="{INTRO}" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index: 1"></video>
{chr(10).join(hosts)}
      <video id="outro-video" class="clip full" src="assets/outro.mp4" data-start="{OUT_START:.2f}" data-duration="{OUTRO}" data-track-index="0" muted playsinline style="z-index: 20"></video>
      <audio id="bed" class="clip" src="assets/bed.wav" data-start="{INTRO}" data-duration="{TOTAL - INTRO:.2f}" data-track-index="2" data-volume="0.6" data-fade-in="1.5" data-fade-out="2.5"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")
print("total", TOTAL, "outro at", OUT_START)
