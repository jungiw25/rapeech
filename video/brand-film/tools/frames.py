"""스타일 프레임 12장 생성기.

각 장면의 '결정적인 한 순간'을 정지 화면 composition으로 만든다(compositions/sNN.html).
제작 단계에서는 같은 파일에 타임라인을 붙여 애니메이션으로 바꾼다.
사용법: python3 tools/frames.py  →  npx hyperframes snapshot --at 0.5,1.5,...
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "compositions"
COMP.mkdir(exist_ok=True)

DARK, LIGHT, INK, SUB, LIL = "#0c0916", "#faf9fd", "#1b1530", "#a69cc8", "#9d79ff"
G = ["#FF03C8", "#EE06C1", "#DE0ABA", "#CD0EB4", "#BD12AD", "#AD16A7", "#9B19AB", "#881BB9", "#751DC7", "#621FD6", "#4F21E4", "#3C24F3"]

FONTS = "".join(
    f'@font-face {{ font-family: "Pretendard"; font-weight: {w}; src: url("assets/fonts/Pretendard-{n}.otf"); }}\n'
    for w, n in [(900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")]
)
BASE = FONTS + f"""
#root {{ position: absolute; inset: 0; overflow: hidden; font-family: "Pretendard", sans-serif; background: {DARK}; }}
.grad {{ background: linear-gradient(100deg, #ff03c8, #a518a4 55%, #6a4dff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.say {{ position: absolute; font-weight: 800; color: #fff; letter-spacing: -0.03em; line-height: 1.12; }}
.lab {{ position: absolute; font-weight: 600; color: {SUB}; font-size: 30px; letter-spacing: 0.01em; }}
.vig {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(60,36,243,0.10), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45)); }}
"""


def scene(sid, body, css="", light=False):
    bg = LIGHT if light else DARK
    html = f"""<template>
  <style>
{BASE}
    #root {{ background: {bg}; }}
{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div id="{sid}-all" class="clip" data-start="0" data-duration="1" data-track-index="1" data-layout-allow-overflow data-layout-allow-overlap>
{body}
    </div>
  </div>
  <script>
    window.__timelines["{sid}"] = gsap.timeline({{ paused: true }});
  </script>
</template>
"""
    (COMP / f"{sid}.html").write_text(html, encoding="utf-8")


def grad_defs(gid, x1, x2, vertical=False):
    if vertical:
        return f'<linearGradient id="{gid}" x1="0" y1="{x1}" x2="0" y2="{x2}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'
    return f'<linearGradient id="{gid}" x1="{x1}" y1="0" x2="{x2}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'


GLOW = '<filter id="glow" filterUnits="userSpaceOnUse" x="-300" y="-300" width="2520" height="1680"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
FG = 'filter="url(#glow)"'
GLOW_S = '<filter id="glows" filterUnits="userSpaceOnUse" x="-300" y="-300" width="2520" height="1680"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'


def svg(inner, defs=""):
    return f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;overflow:visible"><defs>{GLOW}{GLOW_S}{defs}</defs>{inner}</svg>'


def wave_heights(n, seed, amp=1.0):
    s = seed
    out = []
    for k in range(n):
        s = (s * 1664525 + 1013904223) % 4294967296
        r = s / 4294967296
        env = math.sin(math.pi * (k + 0.5) / n) ** 0.7
        out.append((0.15 + 0.85 * r) * env * amp)
    return out


# ----------------------------------------------------------------- 1 로고에서 신호로
logo = (ROOT / "assets/brand/symbol_purple.svg").read_text() if (ROOT / "assets/brand/symbol_purple.svg").exists() else ""
s1 = f"""
      <div style="position:absolute;left:0;top:0;width:820px;height:1080px;background:{LIGHT};clip-path:polygon(0 0,100% 0,72% 100%,0 100%)"></div>
      <img src="assets/brand/symbol_purple.svg" style="position:absolute;left:250px;top:390px;width:260px;filter:none" />
      {svg(f'''
        <path d="M470 430 L1960 300" stroke="url(#g1)" stroke-width="10" stroke-linecap="round" filter="url(#glow)" />
        <path d="M720 412 L1960 300" stroke="#fff" stroke-opacity=".55" stroke-width="2" />
        {''.join(f'<path d="M{900+i*130} {404-i*11+(i%3-1)*40} l{180+i*20} {-16-i*2}" stroke="#fff" stroke-opacity="{0.10+0.03*(i%3)}" stroke-width="2"/>' for i in range(8))}
      ''', grad_defs("g1", 470, 1960))}
      <div class="lab" style="left:1220px;top:700px">하나의 신호가 출발합니다</div>
"""
scene("s01", s1)

# ----------------------------------------------------------------- 2 목소리의 시작
layers = []
for li, (dy, op, blur, sc, seed) in enumerate([(-10, 0.25, 6, 0.75, 3), (0, 0.5, 2, 0.9, 7), (8, 1, 0, 1.0, 11)]):
    hs = wave_heights(36, seed, sc)
    bars = "".join(
        f'<rect x="{980 + k * 22 - 4 + li * 6}" y="{540 + dy - h * 300}" width="9" height="{max(10, h * 600)}" rx="4.5" fill="{G[min(11, k // 3)]}" opacity="{op}"/>'
        for k, h in enumerate(hs)
    )
    layers.append(f'<g style="filter:blur({blur}px)">{bars}</g>')
s2 = f"""
      <div class="vig"></div>
      {svg(''.join(layers))}
      <div class="say" style="left:150px;top:390px;font-size:96px">모든 대화는,<br/><span class="grad">목소리</span>에서<br/>시작합니다</div>
"""
scene("s02", s2)

# ----------------------------------------------------------------- 3 전화망 → AI 게이트웨이
gate = "".join(
    f'<rect x="{900 + i * 28}" y="{300 + i * 14}" width="{120 - i * 4}" height="{480 - i * 28}" rx="18" fill="none" stroke="url(#g3)" stroke-opacity="{1 - i * 0.18}" stroke-width="{4 - i * 0.5}"/>'
    for i in range(5)
)
s3 = f"""
      <div class="vig"></div>
      {svg(f'''
        <path d="M-40 560 L940 540" stroke="#6b6380" stroke-width="8" stroke-linecap="round" stroke-dasharray="2 22" />
        <path d="M-40 560 L940 540" stroke="#8a8399" stroke-opacity=".5" stroke-width="3" />
        {gate}
        <path d="M960 540 L1980 520" stroke="url(#g3)" stroke-width="10" stroke-linecap="round" filter="url(#glow)" />
        {''.join(f'<path d="M{1060+i*95} {528-i*2+((i*37)%5-2)*26} l{90+i*8} -2" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>' for i in range(9))}
      ''', grad_defs("g3", 900, 1980))}
      <div class="lab" style="left:120px;top:610px">전화망</div>
      <div class="lab" style="left:870px;top:830px;color:#fff">AI 봇 게이트웨이</div>
      <div class="say" style="left:120px;top:150px;font-size:72px">전화가 걸려 오는 순간,<br/>AI가 <span class="grad">함께 듣습니다</span></div>
"""
scene("s03", s3)

# ----------------------------------------------------------------- 4 말을 글로, 뜻으로
import random
rnd = random.Random(4)
parts = []
for i in range(420):
    t = rnd.random()
    x = 260 + t * 900 + rnd.gauss(0, 18)
    y = 560 + rnd.gauss(0, 90 * (1 - t) + 14)
    r = rnd.uniform(1.5, 4.5) * (1 - 0.6 * t)
    c = G[min(11, int(t * 12))]
    parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{c}" opacity="{0.35 + 0.6 * (1 - t):.2f}"/>')
hs = wave_heights(14, 5)
wbars = "".join(f'<rect x="{120 + k * 18}" y="{560 - h * 200}" width="8" height="{max(8, h * 400)}" rx="4" fill="{G[k * 11 // 13]}"/>' for k, h in enumerate(hs))
s4 = f"""
      <div class="vig"></div>
      {svg(wbars + ''.join(parts))}
      <div style="position:absolute;left:1120px;top:500px;font-size:66px;font-weight:700;color:#fff;letter-spacing:-0.02em">
        <span style="position:relative;display:inline-block">보험금 청구<i style="position:absolute;left:0;right:0;bottom:-14px;height:10px;border-radius:5px;background:linear-gradient(90deg,#ff03c8,#3c24f3)"></i></span>하고 싶어요
      </div>
      <div style="position:absolute;left:1120px;top:620px;font-size:34px;font-weight:600;color:{SUB}">의도 <span style="color:#fff;margin-left:14px">보험금 청구</span></div>
      <div class="say" style="left:120px;top:150px;font-size:72px">말을 글로, 글을 <span class="grad">뜻</span>으로</div>
"""
scene("s04", s4)

# ----------------------------------------------------------------- 5 알맞은 AI로
nodes = [(1320, 330), (1420, 560), (1320, 790)]
br = "".join(
    f'<path d="M760 560 C 1000 560, 1060 {y}, {x - 60} {y}" fill="none" stroke="{"url(#g5)" if i == 1 else "#3a3350"}" stroke-width="{9 if i == 1 else 4}" stroke-linecap="round" {FG if i == 1 else ""}/>'
    for i, (x, y) in enumerate(nodes)
)
nd = "".join(
    (f'<circle cx="{x}" cy="{y}" r="74" fill="none" stroke="url(#g5)" stroke-width="3" opacity=".5"/><circle cx="{x}" cy="{y}" r="52" fill="#faf9fd"/><circle cx="{x}" cy="{y}" r="24" fill="url(#g5)"/>'
     if i == 1 else f'<circle cx="{x}" cy="{y}" r="46" fill="#1c1730" stroke="#3a3350" stroke-width="3"/>')
    for i, (x, y) in enumerate(nodes)
)
s5 = f"""
      <div class="vig"></div>
      {svg(f'<path d="M-40 560 L760 560" stroke="url(#g5)" stroke-width="9" stroke-linecap="round" filter="url(#glow)"/>' + br + nd, grad_defs("g5", 0, 1500))}
      <div class="lab" style="left:1520px;top:540px;color:#fff;font-size:34px">가장 알맞은 AI</div>
      <div class="say" style="left:120px;top:150px;font-size:72px">질문에 <span class="grad">가장 알맞은 AI</span>로</div>
"""
scene("s05", s5)

# ----------------------------------------------------------------- 6 목소리가 열쇠
rings = []
for i in range(9):
    R = 90 + i * 34
    pts = []
    for a in range(0, 361, 4):
        th = math.radians(a)
        wob = 1 + 0.05 * math.sin(th * (3 + i % 4) + i) * (i / 8)
        pts.append(f"{960 + R * wob * math.cos(th):.1f},{560 + R * wob * math.sin(th):.1f}")
    rings.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{G[11 - i]}" stroke-width="{3 if i % 2 else 5}" opacity="{1 - i * 0.07:.2f}"/>')
lock = f'''<g transform="translate(960 560)">
  <path d="M-34 -10 V-44 a34 34 0 0 1 68 0 V-30" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" transform="rotate(-18 34 -10)"/>
  <rect x="-50" y="-12" width="100" height="78" rx="14" fill="#fff"/><circle cx="0" cy="22" r="10" fill="{DARK}"/><rect x="-4" y="22" width="8" height="22" rx="4" fill="{DARK}"/></g>'''
s6 = f"""
      <div class="vig"></div>
      {svg(''.join(rings) + f'<circle cx="960" cy="560" r="400" fill="none" stroke="url(#g6)" stroke-width="2" opacity=".35" filter="url(#glows)"/>' + lock, grad_defs("g6", 560, 1360))}
      <div class="say" style="left:120px;top:150px;font-size:72px">목소리 하나로,<br/><span class="grad">본인 확인</span>까지</div>
      <div class="lab" style="left:1420px;top:880px;color:#fff">화자인증</div>
"""
scene("s06", s6)

# ----------------------------------------------------------------- 7 답, 그리고 역할 분담
s7 = f"""
      <div style="position:absolute;left:0;top:0;width:1920px;height:540px;background:{DARK}"></div>
      <div style="position:absolute;left:0;top:540px;width:1920px;height:540px;background:{LIGHT}"></div>
      <div style="position:absolute;left:0;top:536px;width:1920px;height:8px;background:linear-gradient(90deg,#ff03c8,#a518a4 50%,#3c24f3)"></div>
      <div class="lab" style="left:120px;top:110px">고객에게</div>
      <div style="position:absolute;left:120px;top:190px;padding:0 64px;height:140px;border-radius:70px;background:linear-gradient(100deg,#ff03c8,#a518a4 50%,#3c24f3);color:#fff;font-size:52px;font-weight:700;display:flex;align-items:center">네, 청구 접수를 도와드릴게요.</div>
      <div class="say" style="left:1180px;top:200px;font-size:60px">단순 문의는<br/><span class="grad">AI</span>가 바로</div>
      <div class="lab" style="left:120px;top:620px;color:#6b6380">상담사에게</div>
      <div style="position:absolute;left:120px;top:690px;width:760px;height:280px;border-radius:24px;background:#fff;box-shadow:0 18px 40px rgba(27,21,48,.12);padding:40px 48px">
        <div style="font-size:30px;font-weight:700;color:{INK}">상담 요약</div>
        <div style="margin-top:22px;font-size:30px;font-weight:500;color:#5d5672;line-height:1.6">· 보험금 청구 문의<br/>· 목소리로 본인 확인 완료<br/>· 청구 접수 안내</div>
      </div>
      <div class="say" style="left:1180px;top:730px;font-size:60px;color:{INK}">깊은 상담은<br/><span class="grad">사람</span>이 더 깊게</div>
"""
scene("s07", s7)


# ----------------------------------------------------------------- 등각 도우미
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))


def iso(x, y, z, ox, oy, k):
    return (ox + (x - y) * C30 * k, oy + (x + y) * S30 * k - z * k)


def box(x, y, z, w, d, h, ox, oy, k, top, left, right, stroke="none", sw=0, op=1):
    P = lambda a, b, c: "%.1f,%.1f" % iso(a, b, c, ox, oy, k)
    t = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    l = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    r = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    st = f'stroke="{stroke}" stroke-width="{sw}"' if sw else ""
    return (f'<polygon points="{" ".join(l)}" fill="{left}" opacity="{op}" {st}/>'
            f'<polygon points="{" ".join(r)}" fill="{right}" opacity="{op}" {st}/>'
            f'<polygon points="{" ".join(t)}" fill="{top}" opacity="{op}" {st}/>')


# ----------------------------------------------------------------- 8 카메라 후퇴: 서버 랙
k, ox, oy = 62, 900, 330
racks = []
floor = "".join(
    f'<path d="M{iso(i, -1, 0, ox, oy, k)[0]:.0f} {iso(i, -1, 0, ox, oy, k)[1]:.0f} L{iso(i, 8, 0, ox, oy, k)[0]:.0f} {iso(i, 8, 0, ox, oy, k)[1]:.0f}" stroke="#2a2440" stroke-width="1.5"/>'
    for i in range(-1, 9)
) + "".join(
    f'<path d="M{iso(-1, j, 0, ox, oy, k)[0]:.0f} {iso(-1, j, 0, ox, oy, k)[1]:.0f} L{iso(8, j, 0, ox, oy, k)[0]:.0f} {iso(8, j, 0, ox, oy, k)[1]:.0f}" stroke="#2a2440" stroke-width="1.5"/>'
    for j in range(-1, 9)
)
for row in (0, 3.2):
    for i in range(7):
        x = i * 1.05
        racks.append(box(x, row, 0, 0.9, 1.1, 3.0, ox, oy, k, "#2b2445", "#1a1530", "#231c3a"))
        # 앞면 LED 줄
        for j in range(8):
            a = iso(x + 0.12, row + 1.1, 0.3 + j * 0.33, ox, oy, k)
            b = iso(x + 0.78, row + 1.1, 0.3 + j * 0.33, ox, oy, k)
            lit = (i * 3 + j) % 5 == 0
            hl = (row == 3.2 and i == 3 and j == 4)
            racks.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{"url(#g8)" if hl else ("#9d79ff" if lit else "#3a3350")}" stroke-width="{7 if hl else 3}" stroke-linecap="round" {FG if hl else ""}/>')
hl = iso(3 * 1.05 + 0.45, 3.2 + 1.1, 0.3 + 4 * 0.33, ox, oy, k)
s8 = f"""
      <div class="vig"></div>
      {svg(floor + ''.join(racks) + f'<circle cx="{hl[0]:.0f}" cy="{hl[1]:.0f}" r="60" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>', grad_defs("g8", 900, 1200))}
      <div class="say" style="left:120px;top:150px;font-size:72px">이 모든 대화가<br/><span class="grad">달리는 곳</span></div>
      <div class="lab" style="left:{hl[0] + 80:.0f}px;top:{hl[1] + 40:.0f}px;color:#fff">방금 그 통화</div>
"""
scene("s08", s8)

# ----------------------------------------------------------------- 9 길을 짓다: 데이터센터 단면
k, ox, oy = 60, 800, 420
steps = ["전산 설계", "통합배선", "네트워크", "출입보안", "통합관제", "유지보수"]
el = []
for f in range(6):
    z = f * 1.15
    lit = f <= 4
    el.append(box(0, 0, z, 7, 4, 0.12, ox, oy, k, "#2b2445" if lit else "#1c1730", "#16122a", "#1f1936"))
    if f == 0:  # 설계 도면 선
        for g in range(1, 7):
            a, b = iso(g, 0.2, z + 0.13, ox, oy, k), iso(g, 3.8, z + 0.13, ox, oy, k)
            el.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="#6a4dff" stroke-width="1.5" stroke-dasharray="6 6"/>')
    if f == 1:  # 배선
        for c in range(4):
            pts = [iso(0.3, 0.6 + c * 0.8, z + 0.14, ox, oy, k), iso(4.5 + c * 0.5, 0.6 + c * 0.8, z + 0.14, ox, oy, k), iso(4.5 + c * 0.5, 3.6, z + 0.14, ox, oy, k)]
            el.append(f'<polyline points="{" ".join("%.0f,%.0f" % p for p in pts)}" fill="none" stroke="url(#g9)" stroke-width="4" filter="url(#glows)"/>')
    if f == 2:  # 장비
        for c in range(5):
            el.append(box(0.6 + c * 1.25, 1.4, z + 0.12, 0.9, 1.2, 0.45, ox, oy, k, "#3a3060", "#241d40", "#2d2550"))
            a = iso(0.75 + c * 1.25, 2.6, z + 0.35, ox, oy, k)
            el.append(f'<circle cx="{a[0]:.0f}" cy="{a[1]:.0f}" r="4" fill="#9d79ff"/>')
    if f == 3:  # 출입문
        el.append(box(3.0, 3.85, z + 0.12, 1.0, 0.1, 0.9, ox, oy, k, "#3a3060", "#9d79ff", "#6a4dff", op=0.9))
    if f == 4:  # 관제 화면
        el.append(box(1.0, 0.3, z + 0.12, 5.0, 0.12, 0.8, ox, oy, k, "#2d2550", "url(#g9)", "#3a3060"))
    a = iso(7.05, 2.0, z + 0.06, ox, oy, k)
    el.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{1460:.0f} {a[1]:.0f}" stroke="{"#9d79ff" if lit else "#3a3350"}" stroke-width="1.5"/>')
    el.append(f'<text x="1480" y="{a[1] + 11:.0f}" font-family="Pretendard" font-weight="700" font-size="34" fill="{"#fff" if lit else "#5d5672"}">{steps[f]}</text>')
s9 = f"""
      <div class="vig"></div>
      {svg(''.join(el), grad_defs("g9", 700, 1300))}
      <div class="say" style="left:120px;top:120px;font-size:72px"><span class="grad">AI 인프라</span>를<br/>짓습니다</div>
      <div class="lab" style="left:120px;top:900px">데이터센터 · 전산센터 · ESS · 스마트공장</div>
"""
scene("s09", s9)

# ----------------------------------------------------------------- 10 바다를 건너
dots = json.loads((ROOT / "assets/data/pacific_dots.json").read_text())["dots"]
L0, L1, A0, A1 = 95, 300, 10, 60
X = lambda lon: 60 + (lon - L0) / (L1 - L0) * 1800
Y = lambda lat: 160 + (A1 - lat) / (A1 - A0) * 800
dd = "".join(f'<circle cx="{X(lo):.0f}" cy="{Y(la):.0f}" r="3.2" fill="#3a3158"/>' for lo, la in dots)
kr = (127.0, 37.0)
us = [(-85.0, 43.0), (-82.8, 40.3), (-111.9, 34.2), (-98.0, 31.0), (-86.5, 35.8)]
kx, ky = X(kr[0]), Y(kr[1])
arcs = ""
pins = ""
for lo, la in us:
    ux, uy = X(lo + 360), Y(la)
    mx, my = (kx + ux) / 2, min(ky, uy) - 260
    arcs += f'<path d="M{kx:.0f} {ky:.0f} Q {mx:.0f} {my:.0f} {ux:.0f} {uy:.0f}" fill="none" stroke="url(#g10)" stroke-width="3" opacity=".85" filter="url(#glows)"/>'
    pins += f'<circle cx="{ux:.0f}" cy="{uy:.0f}" r="18" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2"/><circle cx="{ux:.0f}" cy="{uy:.0f}" r="8" fill="#fff"/>'
pins += f'<circle cx="{kx:.0f}" cy="{ky:.0f}" r="22" fill="none" stroke="#ff03c8" stroke-width="3"/><circle cx="{kx:.0f}" cy="{ky:.0f}" r="9" fill="#ff03c8"/>'
s10 = f"""
      <div class="vig"></div>
      {svg(dd + arcs + pins, grad_defs("g10", kx, X(-82 + 360)))}
      <div class="lab" style="left:{kx - 40:.0f}px;top:{ky + 30:.0f}px;color:#fff">한국</div>
      <div class="lab" style="left:{X(-100 + 360):.0f}px;top:{Y(28):.0f}px;color:#fff">미국 5개 주</div>
      <div class="say" style="left:120px;top:110px;font-size:64px">미국 배터리 · 태양광 공장의<br/><span class="grad">현장까지</span></div>
"""
scene("s10", s10)

# ----------------------------------------------------------------- 11 한 팀
k, ox, oy = 66, 980, 560
up = box(0, 0, 2.2, 6, 6, 0.35, ox, oy - 240, k, "#faf9fd", "#d9d0f5", "#c2b3f2")
dn = box(0, 0, 0, 6, 6, 0.6, ox, oy, k, "#2b2445", "#16122a", "#1f1936")
grid = "".join(
    f'<path d="M{iso(i, 0, 0.61, ox, oy, k)[0]:.0f} {iso(i, 0, 0.61, ox, oy, k)[1]:.0f} L{iso(i, 6, 0.61, ox, oy, k)[0]:.0f} {iso(i, 6, 0.61, ox, oy, k)[1]:.0f}" stroke="#6a4dff" stroke-width="1.5" opacity=".7"/>'
    for i in range(1, 6))
hs = wave_heights(16, 9)
wv = "".join(
    (lambda a, b: f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{G[i * 11 // 15]}" stroke-width="8" stroke-linecap="round"/>')(
        iso(0.6 + i * 0.32, 3, 2.56 + 240 / k, ox, oy, k), iso(0.6 + i * 0.32, 3, 2.56 + 240 / k + h * 1.4, ox, oy, k))
    for i, h in enumerate(hs))
c0, c1 = iso(3, 3, 0.6, ox, oy, k), iso(3, 3, 2.2 + 240 / k, ox, oy, k)
beam = f'<rect x="{c0[0] - 14:.0f}" y="{c1[1]:.0f}" width="28" height="{c0[1] - c1[1]:.0f}" rx="14" fill="url(#g11v)" filter="url(#glow)"/>'
s11 = f"""
      <div class="vig"></div>
      {svg(dn + grid + beam + up + wv, grad_defs("g11v", c1[1], c0[1], vertical=True))}
      <div class="lab" style="left:1450px;top:330px;color:#fff;font-size:36px">AI</div>
      <div class="lab" style="left:1450px;top:700px;color:#fff;font-size:36px">인프라</div>
      <div class="say" style="left:120px;top:150px;font-size:68px">인프라 구축부터<br/>AI 도입까지,<br/><span class="grad">한 팀이</span></div>
      <div style="position:absolute;left:120px;top:830px;font-size:30px;font-weight:600;color:{SUB};line-height:1.7">조달청 우수조달물품 · 중기부 혁신제품<br/>등록 특허 7건</div>
"""
scene("s11", s11)

# ----------------------------------------------------------------- 12 아웃트로로
s12 = f"""
      {svg('<path d="M260 540 L1660 540" stroke="url(#g12)" stroke-width="6" stroke-linecap="round" filter="url(#glows)"/>' + ''.join(f'<path d="M{960 + (1 if i % 2 else -1) * (900 - i * 60)} {540 + (i % 3 - 1) * (300 - i * 20)} L{960 + (1 if i % 2 else -1) * (700 - i * 50)} {540 + (i % 3 - 1) * (230 - i * 16)}" stroke="#9d79ff" stroke-opacity="{0.15 + i * 0.02:.2f}" stroke-width="2"/>' for i in range(10)), grad_defs("g12", 260, 1660))}
"""
scene("s12", s12)

# ----------------------------------------------------------------- 미리보기 index
hosts = "\n".join(
    f'      <div id="s{i:02d}" data-composition-id="s{i:02d}" data-composition-src="compositions/s{i:02d}.html" data-start="{i - 1}" data-duration="1" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>'
    for i in range(1, 13)
)
(ROOT / "frames.html").write_text(f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="assets/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:{DARK}}} #root{{position:relative;width:100%;height:100%}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="12" data-width="1920" data-height="1080">
{hosts}
</div><script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script></body></html>
""", encoding="utf-8")
print("ok")
