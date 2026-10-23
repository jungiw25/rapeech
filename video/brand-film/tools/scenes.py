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
SCENES = [("flow", 35), ("s08", 5), ("s09", 9), ("s10", 4), ("s11", 4), ("s12", 2)]
DUR = {k: v for k, v in SCENES}
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

exec((ROOT / "tools" / "flow_block.py").read_text(encoding="utf-8"))

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
      <div id="s08-barwrap" style="position:absolute;inset:0">{BAR.replace("__ID__", "s08-bar")}</div>
      {say("끊김 없는 대화 뒤에는,|[단단한 인프라]가 있습니다", 68, 120, 150, "s08")}
      <div class="lab" id="s08-lab" style="left:{HX + 80:.0f}px;top:{HY + 40:.0f}px;color:#fff">방금 그 통화</div>
"""
s08_js = f"""
      // 연속 줌 아웃: 화면을 채우던 빛이 서버 랙 LED 한 칸이었음
      tl.fromTo("#s08-cam", {{ scale: 9, x: {960 - HX:.0f} * 9 / 9, y: {540 - HY:.0f}, transformOrigin: "{HX:.0f}px {HY:.0f}px" }},
        {{ scale: 1, x: 0, y: 0, duration: 2.8, ease: "power3.inOut" }}, 0);
      tl.fromTo("#s08-cam", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "sine.inOut" }}, 0.05);
      tl.to("#s08-barwrap", {{ opacity: 0, duration: 0.6, ease: "sine.inOut" }}, 0.25);
      tl.fromTo(".s08-led", {{ opacity: 0.2 }}, {{ opacity: 1, duration: 1.0, ease: "sine.inOut", stagger: 0.02 }}, 1.4);
      tl.fromTo("#s08-ring", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 1.0, ease: "expo.out" }}, 2.6);
      IN(".s08-w", 2.0);
      IN("#s08-lab", 2.9, {{ y: 10 }});
      OUT([".s08-w", "#s08-lab", "#s08-ring"], 4.3);
      tl.to("#s08-cam", {{ opacity: 0, scale: 0.92, duration: 0.7, ease: "power2.inOut" }}, 4.3);
"""
scene("s08", DUR["s08"], s08, s08_js)

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
      {say("데이터센터,|[설계부터 운영까지]", 72, 120, 120, "s09")}
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
scene("s09", DUR["s09"], s09, s09_js)

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
scene("s10", DUR["s10"], s10, s10_js)

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
scene("s11", DUR["s11"], s11, s11_js)

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
scene("s12", DUR["s12"], s12, s12_js)

# ================================================================ index.html
t = INTRO
hosts = []
for i, (sid, d) in enumerate(SCENES):
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
      <audio id="bed" class="clip" src="assets/bed.wav" data-start="{INTRO}" data-duration="{TOTAL - INTRO:.2f}" data-track-index="2" data-volume="0.45" data-fade-in="1.5" data-fade-out="2.5"></audio>
      <audio id="sfx" class="clip" src="assets/sfx.wav" data-start="{INTRO}" data-duration="{TOTAL - INTRO:.2f}" data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")
print("total", TOTAL, "outro at", OUT_START)
