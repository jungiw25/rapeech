"""채용 홈페이지 상단 배너(1920×560, 2배 3840×1120 PNG). 회사 소개 영상과 같은 톤.

왼쪽은 홈페이지 글자가 올라가므로 비워 두고, 오른쪽에 '인프라 위에 AI' 등각 장면을 둔다.
사용법: python3 brand/careers_banner/build_banner.py
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H = 1920, 560
C30, S30 = math.cos(math.pi / 6), 0.5
K = 23
OX, OY = 1330, 262          # 등각 원점(인프라 판 뒤쪽 모서리)
G = ["#ff03c8", "#a518a4", "#3c24f3"]


def iso(x, y, z):
    return OX + (x - y) * C30 * K, OY + (x + y) * S30 * K - z * K


def P(x, y, z):
    return "%.1f,%.1f" % iso(x, y, z)


def box(x, y, z, w, d, h, top, left, right, extra=""):
    t = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    l = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    r = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    return (f'<polygon points="{" ".join(l)}" fill="{left}" {extra}/><polygon points="{" ".join(r)}" fill="{right}" {extra}/>'
            f'<polygon points="{" ".join(t)}" fill="{top}" {extra}/>')


def line(a, b, stroke, w=1.5, op=1.0, extra=""):
    (x1, y1), (x2, y2) = iso(*a), iso(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}" opacity="{op}" stroke-linecap="round" {extra}/>'


def lerp_hex(t):
    """브랜드 그라데이션 #ff03c8 → #a518a4 → #3c24f3 에서 t(0..1) 색."""
    cs = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in G]
    seg = 0 if t < 0.5 else 1
    u = t * 2 - seg
    a, b = cs[seg], cs[seg + 1]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))


svg = []
# 바닥 격자(가장자리로 갈수록 흐려짐)
grid = []
for i in range(-14, 25, 2):
    grid.append(line((i, -14, 0), (i, 24, 0), "#4a3f78", 1.2, 0.55))
    grid.append(line((-14, i, 0), (24, i, 0), "#4a3f78", 1.2, 0.55))
cx, cy = iso(5, 5, 0)
svg.append(f'<g mask="url(#gridmask)">{"".join(grid)}</g>')

# 바닥을 따라 들어오는 신호선(영상의 원테이크 선) + 노드
sig_a, sig_b = iso(5, 26, 0), iso(5, 10.2, 0)
svg.append(f'<line x1="{sig_a[0]:.1f}" y1="{sig_a[1]:.1f}" x2="{sig_b[0]:.1f}" y2="{sig_b[1]:.1f}" stroke="url(#sig)" stroke-width="5" stroke-linecap="round" filter="url(#glow-s)"/>')
for yy in (21, 16.5, 12.5):
    nx, ny = iso(5, yy, 0)
    svg.append(f'<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="17" ry="10" fill="url(#gh)" filter="url(#glow)"/>'
               f'<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="6.5" ry="3.8" fill="#fff"/>')

# 인프라 판
svg.append(f'<g filter="url(#shadow)">{box(0, 0, -0.7, 10, 10, 0.7, "#2a2342", "#1f1934", "#171329")}</g>')
for i in range(1, 10):
    svg.append(line((i, 0, 0), (i, 10, 0), "#5b4c8f", 1, 0.45))
    svg.append(line((0, i, 0), (10, i, 0), "#5b4c8f", 1, 0.45))
# 판 가장자리 빛 테
svg.append(line((0, 10, 0), (10, 10, 0), "url(#edge)", 2.5, 0.9))
svg.append(line((10, 0, 0), (10, 10, 0), "#6f5cc8", 2, 0.6))

# 서버 랙(가운데는 비워 빛기둥이 지나가게)
racks = [(x, y) for x in (0.7, 2.6, 6.2, 8.1) for y in (0.7, 2.6, 6.2, 8.1)]
racks += [(4.4, 0.7), (0.7, 4.4)]
racks.remove((6.2, 6.2))   # 빛기둥 밑동이 보이게 앞 랙 하나 비움
racks.sort(key=lambda p: p[0] + p[1])
RH = 3.1


def rack(x, y):
    svg = []
    svg.append(box(x, y, 0, 1.25, 1.25, RH, "#3a3158", "#251e3c", "#1c1731"))
    for j in range(7):
        z = 0.35 + j * 0.38
        hot = (round(x * 7 + y * 3 + j * 5) % 9 == 0)
        col = "#ff4fd8" if hot else "#7b68c9"
        op = 1.0 if hot else 0.55
        ex = 'filter="url(#glow-s)"' if hot else ""
        # 앞면 두 개에 LED 줄
        svg.append(line((x + 0.18, y + 1.25, z), (x + 1.0, y + 1.25, z), col, 2, op, ex))
        svg.append(line((x + 1.25, y + 0.18, z), (x + 1.25, y + 0.7, z), "#5b4c8f", 1.6, 0.6))
    return "".join(svg)


# 빛기둥보다 뒤의 랙 먼저, 앞의 랙은 기둥 다음에 그린다(가림 순서)
for (x, y) in racks:
    if x + y < 9:
        svg.append(rack(x, y))

# 인프라 → AI 빛기둥
bx0, by0 = iso(5, 5, 0)
bx1, by1 = iso(5, 5, 7.4)
svg.append(f'<rect x="{bx0 - 12:.1f}" y="{by1:.1f}" width="24" height="{by0 - by1:.1f}" rx="12" fill="url(#beam)" filter="url(#glow)"/>')
svg.append(f'<rect x="{bx0 - 3:.1f}" y="{by1:.1f}" width="6" height="{by0 - by1:.1f}" rx="3" fill="#fff" opacity=".85"/>')
svg.append(f'<ellipse cx="{bx0:.1f}" cy="{by0:.1f}" rx="46" ry="26" fill="url(#gh)" opacity=".7" filter="url(#glow)"/>')

for (x, y) in racks:
    if x + y >= 9:
        svg.append(rack(x, y))

# AI 판(밝은 판) + 위에 선 목소리 파형
ZA = 7.4
svg.append(f'<g filter="url(#shadow)">{box(0.6, 0.6, ZA, 8.8, 8.8, 0.55, "#f7f5ff", "#cfc7f2", "#aa9fdc")}</g>')
bars = []
n = 15
for i in range(n):
    t = i / (n - 1)
    x = 1.6 + t * 6.8
    y = 5.0 - 0.15
    h = 0.6 + 3.3 * abs(math.sin(i * 1.13 + 0.4)) * (0.45 + 0.55 * math.sin(math.pi * t))
    bars.append((x, y, h, lerp_hex(t)))
for (x, y, h, c) in sorted(bars, key=lambda b: b[0] + b[1]):
    svg.append(box(x, y, ZA + 0.55, 0.26, 0.26, h, c, c, c, 'opacity=".95"'))
svg.append(f'<g filter="url(#glow-s)" opacity=".55">' + "".join(
    box(x, y, ZA + 0.55, 0.26, 0.26, h, c, c, c) for (x, y, h, c) in sorted(bars, key=lambda b: b[0] + b[1])) + '</g>')
# 판 둘레 그라데이션 테
svg.append(line((0.6, 9.4, ZA + 0.55), (9.4, 9.4, ZA + 0.55), "url(#edge)", 3, 1))
svg.append(line((9.4, 0.6, ZA + 0.55), (9.4, 9.4, ZA + 0.55), "#6f5cc8", 2.5, 0.8))

gx0, gy0 = iso(5, 26, 0)
gx1, gy1 = iso(5, 10.2, 0)
defs = f'''
<defs>
  <radialGradient id="bgGlow" cx="{cx / W:.3f}" cy="0.5" r="0.55" gradientTransform="translate({cx / W:.3f} .5) scale(.62 1) translate(-{cx / W:.3f} -.5)">
    <stop offset="0" stop-color="#2b1d73" stop-opacity=".85"/><stop offset=".55" stop-color="#1a1240" stop-opacity=".45"/><stop offset="1" stop-color="#0c0916" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="pinkGlow" cx=".86" cy="1.05" r=".38"><stop offset="0" stop-color="#c0179f" stop-opacity=".55"/><stop offset="1" stop-color="#c0179f" stop-opacity="0"/></radialGradient>
  <linearGradient id="leftShade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0c0916" stop-opacity=".95"/><stop offset=".42" stop-color="#0c0916" stop-opacity=".55"/><stop offset=".6" stop-color="#0c0916" stop-opacity="0"/></linearGradient>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
  <radialGradient id="gridfade" cx="{cx / W:.3f}" cy="{(cy + 20) / H:.3f}" r=".3" gradientTransform="translate({cx / W:.3f} {(cy + 20) / H:.3f}) scale(1 3.43) translate(-{cx / W:.3f} -{(cy + 20) / H:.3f})">
    <stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".7" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="gridmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#gridfade)"/></mask>
  <linearGradient id="sig" x1="{gx0:.1f}" y1="{gy0:.1f}" x2="{gx1:.1f}" y2="{gy1:.1f}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#ff03c8" stop-opacity="0"/><stop offset=".25" stop-color="#ff03c8"/><stop offset=".65" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#3c24f3"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#ff03c8"/></linearGradient>
  <linearGradient id="gh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff03c8"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="glow-s" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="shadow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000" flood-opacity=".55"/></filter>
</defs>'''

doc = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs}
<rect width="{W}" height="{H}" fill="#0c0916"/>
<rect width="{W}" height="{H}" fill="url(#bgGlow)"/>
<rect width="{W}" height="{H}" fill="url(#pinkGlow)"/>
{"".join(svg)}
<rect width="{W}" height="{H}" fill="url(#leftShade)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>'''
(ROOT / "careers_banner.svg").write_text(doc, encoding="utf-8")


PREVIEW_TEXT = '''<div style="position:absolute;left:360px;top:190px;font-family:Pretendard,sans-serif;color:#fff">
<div style="letter-spacing:.2em;font-size:17px;font-weight:600;opacity:.85">RAPEECH CAREERS</div>
<div style="margin-top:28px;font-size:48px;font-weight:800;line-height:1.35">라피치의 내일을<br>함께 이끌어갈 인재를 찾습니다</div></div>'''


def render():
    """크로미움으로 PNG를 찍는다(1배·2배, 글자 얹은 미리보기)."""
    import subprocess
    import tempfile
    html = f'<html><body style="margin:0;background:#0c0916">{doc}</body></html>'
    tmp = Path(tempfile.mkdtemp())
    (tmp / "a.html").write_text(html, encoding="utf-8")
    (tmp / "b.html").write_text(html.replace("</body>", PREVIEW_TEXT + "</body>"), encoding="utf-8")
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const shots = [['a.html', 2, 'careers_banner@2x.png'], ['a.html', 1, 'careers_banner.png'], ['b.html', 1, 'preview_with_text.png']];
  for (const [f, s, out] of shots) {{
    const pg = await b.newPage({{ viewport: {{ width: {W}, height: {H} }}, deviceScaleFactor: s }});
    await pg.goto('file://{tmp}/' + f);
    await pg.screenshot({{ path: '{ROOT}/' + out }});
  }}
  await b.close();
}})();"""
    (tmp / "shot.js").write_text(js)
    subprocess.run(["node", str(tmp / "shot.js")], check=True)


if __name__ == "__main__":
    render()
    print("ok")
