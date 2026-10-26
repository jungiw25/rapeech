"""채용 홈페이지 섹션 배경 2종(상단 배너와 같은 톤, 글자는 나인하이어에서 입력).

- history_bg: '우리가 걸어온 길' 연혁 섹션(1920×720). 왼쪽 위 제목, 가운데 연혁 카드 자리는 비움
- recruit_bg: '지금, 우리의 여정에 함께하세요.' 섹션(1920×420). 가운데 제목·버튼 자리는 비움
각각 SVG와 1배·2배 PNG, 글자를 얹은 미리보기(preview_*.png)를 만든다.
사용법: python3 brand/careers_banner/build_sections.py
"""
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C30 = math.cos(math.pi / 6)
G = ["#ff03c8", "#a518a4", "#3c24f3"]


def grad_hex(t):
    cs = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in G]
    seg = 0 if t < 0.5 else 1
    u = min(1, max(0, t * 2 - seg))
    a, b = cs[seg], cs[seg + 1]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))


def common_defs(W, H):
    return f'''
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
  <filter id="glow" filterUnits="userSpaceOnUse" x="-200" y="-200" width="{W + 400}" height="{H + 400}"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="glow-s" filterUnits="userSpaceOnUse" x="-200" y="-200" width="{W + 400}" height="{H + 400}"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" filterUnits="userSpaceOnUse" x="-200" y="-200" width="{W + 400}" height="{H + 400}"><feGaussianBlur stdDeviation="22"/></filter>'''


def iso_grid(ox, oy, k, n, color="#4a3f78", op=0.5):
    """등각 바닥 격자(원점 ox, oy 기준 -n..n 칸)."""
    out = []
    for i in range(-n, n + 1, 2):
        for a, b in (((i, -n), (i, n)), ((-n, i), (n, i))):
            x1, y1 = ox + (a[0] - a[1]) * C30 * k, oy + (a[0] + a[1]) * 0.5 * k
            x2, y2 = ox + (b[0] - b[1]) * C30 * k, oy + (b[0] + b[1]) * 0.5 * k
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.2" opacity="{op}"/>')
    return "".join(out)


def wave_bars(x0, base, n, gap, wbar, hmax, seed=0.4, center=True, op=1.0):
    """영상의 목소리 파형 막대(브랜드 그라데이션). center=True면 가운데 기준 위아래로."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        h = hmax * (0.18 + 0.82 * abs(math.sin(i * 1.37 + seed)) * (0.35 + 0.65 * math.sin(math.pi * t)))
        x = x0 + i * gap
        y = base - h / 2 if center else base - h
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{wbar}" height="{h:.1f}" rx="{wbar / 2}" fill="{grad_hex(t)}" opacity="{op}"/>')
    return "".join(out)


def node(x, y, r=10, ring=False):
    s = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 1.9:.1f}" fill="url(#edge)" opacity=".35" filter="url(#glow)"/>'
    s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#edge)" filter="url(#glow-s)"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.42:.1f}" fill="#fff"/>'
    if ring:
        s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 3.2:.1f}" fill="none" stroke="#9d79ff" stroke-width="2" opacity=".75"/>'
              f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 4.6:.1f}" fill="none" stroke="#9d79ff" stroke-width="1.2" opacity=".4"/>')
        for a in range(0, 360, 30):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            s += (f'<line x1="{x + ca * r * 3.5:.1f}" y1="{y + sa * r * 3.5:.1f}" x2="{x + ca * r * 3.95:.1f}" y2="{y + sa * r * 3.95:.1f}" '
                  f'stroke="#9d79ff" stroke-width="2" opacity=".55" stroke-linecap="round"/>')
    return s


def smooth_path(pts):
    """점들을 지나는 부드러운 곡선(Catmull-Rom → 베지어)."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {p2[0]:.1f} {p2[1]:.1f}"
    return d


def wrap(W, H, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{common_defs(W, H)}{defs}</defs>'
            f'<rect width="{W}" height="{H}" fill="#0c0916"/>{body}<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')


# ───────────────────────────── 연혁 섹션
def history():
    W, H = 1920, 720
    oy = (H - 665) / 2          # 화면에 보이는 높이(약 665)를 가운데 기준으로
    pts = [(-40, 690), (180, 640), (560, 556), (940, 470), (1290, 392), (1540, 330), (1760, 284), (1980, 246)]
    path = smooth_path(pts)
    defs = f'''
  <radialGradient id="g1" cx=".61" cy=".5" r=".5" gradientTransform="translate(.61 .5) scale(.42 1) translate(-.61 -.5)"><stop offset="0" stop-color="#3b2a90" stop-opacity=".95"/><stop offset=".6" stop-color="#22175a" stop-opacity=".55"/><stop offset="1" stop-color="#0c0916" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx=".02" cy="1" r=".4"><stop offset="0" stop-color="#c0179f" stop-opacity=".5"/><stop offset="1" stop-color="#c0179f" stop-opacity="0"/></radialGradient>
  <radialGradient id="g3" cx=".95" cy=".3" r=".3"><stop offset="0" stop-color="#3c24f3" stop-opacity=".45"/><stop offset="1" stop-color="#3c24f3" stop-opacity="0"/></radialGradient>
  <linearGradient id="road" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <radialGradient id="gfade" cx=".5" cy=".95" r=".6" gradientTransform="translate(.5 .95) scale(1 2.2) translate(-.5 -.95)"><stop offset="0" stop-color="#fff" stop-opacity=".8"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#gfade)"/></mask>
  <filter id="bigsoft" filterUnits="userSpaceOnUse" x="-200" y="-200" width="{W + 400}" height="{H + 400}"><feGaussianBlur stdDeviation="45"/></filter>'''
    body = [f'<rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/><rect width="{W}" height="{H}" fill="url(#g3)"/>']
    body.append(f'<g mask="url(#gm)">{iso_grid(960, 820, 46, 30, op=.45)}</g>')
    # 연혁 카드(나인하이어의 반투명 흰 카드) 뒤를 보랏빛으로 밝혀 회색이 아니라 연보라 유리처럼 보이게
    body.append(f'<rect x="905" y="{oy + 20:.0f}" width="535" height="625" rx="60" fill="#4b37b5" opacity=".95" filter="url(#bigsoft)"/>')
    # 로고 사선(영상 인트로의 12개 줄)을 왼쪽 위 모서리에 옅게
    for j in range(12):
        x = -60 + j * 34
        body.append(f'<line x1="{x:.1f}" y1="{oy + 150:.1f}" x2="{x + 62:.1f}" y2="{oy - 30:.1f}" stroke="{grad_hex(j / 11)}" stroke-width="12" stroke-linecap="round" opacity=".22"/>')
    # 걸어온 길: 아래 넓은 빛 + 선 + 노드
    body.append(f'<path d="{path}" fill="none" stroke="url(#road)" stroke-width="40" opacity=".22" filter="url(#soft)"/>')
    body.append(f'<path d="{path}" fill="none" stroke="url(#road)" stroke-width="6" stroke-linecap="round" filter="url(#glow-s)"/>')
    body.append(f'<path d="{path}" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="26 22" opacity=".55"/>')
    for (x, y) in [(180, 640), (560, 556)]:
        body.append(node(x, y, 11))
    body.append(node(1540, 330, 11))
    body.append(node(1760, 284, 16, ring=True))
    # 목소리 파형(왼쪽, 제목 아래)
    body.append(f'<g filter="url(#glow-s)" opacity=".9">{wave_bars(120, oy + 430, 23, 16, 7, 150)}</g>')
    svg = wrap(W, H, defs, "".join(body))
    preview = f'''<div style="position:absolute;left:510px;top:{oy + 80:.0f}px;font-family:Pretendard,sans-serif;color:#fff">
<div style="font-size:13px;font-weight:700">우리가 걸어온 길</div>
<div style="margin-top:22px;font-size:38px;font-weight:800;line-height:1.55">우리는 새로운 역사를<br>쓰고 있습니다.</div></div>
<div style="position:absolute;left:935px;top:{oy + 42:.0f}px;width:475px;height:580px;border-radius:18px;background:rgba(255,255,255,.6);font-family:Pretendard,sans-serif;color:#333;padding:28px 30px;box-sizing:border-box;font-size:13px;line-height:1.6">
<b style="font-size:19px">2026</b><br>서경엔씨에스(네트워크 인프라 사업) 인수 · 합병<br><br><b style="font-size:19px">2025</b><br>Scale up Tips 'LLM기반 AI 휴먼' R&amp;D 연구과제 선정<br>하이서울 인증기업 선정<br>혁신 프리미어 1000 인공지능 분야 유망기업 선정<br><br><b style="font-size:19px">2024</b><br>ConvAI 플랫폼 혁신제품 지정<br>기업부설연구소 확장 및 본사 리뉴얼<br><br><b style="font-size:19px">2020 ~ 2023</b><br>라피치로 사명 변경 · 코넥스(KONEX) 상장<br>금융권 AICC 및 콜봇 시스템 구축</div>'''
    return "history_bg", W, H, svg, preview


# ───────────────────────────── 채용(함께하세요) 섹션
def recruit():
    W, H = 1920, 420
    pts = [(1300, 470), (1470, 372), (1620, 278), (1760, 196), (1990, 70)]
    path = smooth_path(pts)
    defs = f'''
  <radialGradient id="g1" cx=".5" cy=".5" r=".5" gradientTransform="translate(.5 .5) scale(.45 1.3) translate(-.5 -.5)"><stop offset="0" stop-color="#3b2a90" stop-opacity=".9"/><stop offset=".65" stop-color="#22175a" stop-opacity=".45"/><stop offset="1" stop-color="#0c0916" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx=".08" cy="1.1" r=".35" gradientTransform="translate(.08 1.1) scale(1 3) translate(-.08 -1.1)"><stop offset="0" stop-color="#c0179f" stop-opacity=".55"/><stop offset="1" stop-color="#c0179f" stop-opacity="0"/></radialGradient>
  <radialGradient id="g3" cx=".92" cy=".2" r=".3" gradientTransform="translate(.92 .2) scale(1 3) translate(-.92 -.2)"><stop offset="0" stop-color="#3c24f3" stop-opacity=".5"/><stop offset="1" stop-color="#3c24f3" stop-opacity="0"/></radialGradient>
  <linearGradient id="road" x1="1300" y1="0" x2="1990" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>
  <linearGradient id="sidefade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".3" stop-color="#fff" stop-opacity=".15"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset=".7" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>
  <mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#sidefade)"/></mask>'''
    body = [f'<rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/><rect width="{W}" height="{H}" fill="url(#g3)"/>']
    body.append(f'<g mask="url(#gm)">{iso_grid(960, 360, 44, 34, op=.4)}</g>')
    # 왼쪽: 바닥에서 솟은 목소리 파형
    body.append(f'<g filter="url(#glow-s)">{wave_bars(110, H - 30, 26, 17, 8, 190, seed=1.1, center=False)}</g>')
    # 오른쪽: 이어지는 길 끝에 '다음 멤버' 자리 노드
    body.append(f'<path d="{path}" fill="none" stroke="url(#road)" stroke-width="40" opacity=".22" filter="url(#soft)"/>')
    body.append(f'<path d="{path}" fill="none" stroke="url(#road)" stroke-width="6" stroke-linecap="round" filter="url(#glow-s)"/>')
    body.append(f'<path d="{path}" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="26 22" opacity=".55"/>')
    body.append(node(1470, 372, 11))
    body.append(node(1620, 278, 11))
    body.append(node(1760, 196, 16, ring=True))
    svg = wrap(W, H, defs, "".join(body))
    preview = '''<div style="position:absolute;left:0;top:113px;width:1920px;text-align:center;font-family:Pretendard,sans-serif;color:#fff">
<div style="font-size:36px;font-weight:800">지금, 우리의 여정에 함께하세요.</div>
<div style="margin-top:26px;font-size:12px;font-weight:600">저희와 함께 더 나은 채용 문화를 만들어 나갈 멤버를 기다리고 있습니다.</div>
<div style="margin:40px auto 0;width:158px;height:36px;border-radius:18px;background:#fff;color:#111;font-size:12px;font-weight:700;line-height:36px">진행 중인 공고 보러가기 ↗</div></div>'''
    return "recruit_bg", W, H, svg, preview


def render(items):
    tmp = Path(tempfile.mkdtemp())
    shots = []
    for name, W, H, svg, preview in items:
        (ROOT / f"{name}.svg").write_text(svg, encoding="utf-8")
        html = f'<html><body style="margin:0;background:#0c0916;position:relative">{svg}</body></html>'
        (tmp / f"{name}.html").write_text(html, encoding="utf-8")
        (tmp / f"{name}_p.html").write_text(html.replace("</body>", preview + "</body>"), encoding="utf-8")
        shots += [(f"{name}.html", W, H, 2, f"{name}@2x.png"), (f"{name}.html", W, H, 1, f"{name}.png"), (f"{name}_p.html", W, H, 1, f"preview_{name}.png")]
    js = "const { chromium } = require('playwright');\n(async () => {\n  const b = await chromium.launch();\n"
    for f, W, H, s, out in shots:
        js += (f"  {{ const pg = await b.newPage({{ viewport: {{ width: {W}, height: {H} }}, deviceScaleFactor: {s} }});"
               f" await pg.goto('file://{tmp}/{f}'); await pg.screenshot({{ path: '{ROOT}/{out}' }}); }}\n")
    js += "  await b.close();\n})();"
    (tmp / "shot.js").write_text(js)
    subprocess.run(["node", str(tmp / "shot.js")], check=True)


if __name__ == "__main__":
    render([history(), recruit()])
    print("ok")
