"""채용 홈페이지 배경 이미지 3종(영상 A안과 같은 찰흙 그림체, 흰 글자가 얹히므로 깊은 보라 바탕).
- history_bg.png  3840x1440  홈 '우리가 걸어온 길' 뒷배경
- bottom_banner.png 3840x840 홈 최하단 배너
- about_hero.jpg  3200x954   회사 소개 최상단 배너
사용법: python3 video/brand-film-hf/banners/build.py  (HTML을 만든 뒤 Chromium으로 2배 해상도 캡처)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from reskin import CLAY  # noqa: E402

A = HERE / "assets"
PREVIEW = "--preview" in sys.argv


def crop(src, dst):
    im = Image.open(src).convert("RGBA")
    ys, xs = np.where(np.asarray(im)[..., 3] > 24)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst)


def page(w, h, svg, dom, text=""):
    clay = CLAY.format(id="clay", box=f'filterUnits="userSpaceOnUse" x="-100" y="-100" width="{w + 200}" height="{h + 200}"')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: P; font-weight: 800; src: url(../../brand-film/assets/fonts/Pretendard-ExtraBold.otf); }}
@font-face {{ font-family: P; font-weight: 500; src: url(../../brand-film/assets/fonts/Pretendard-Medium.otf); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {w}px; height: {h}px; overflow: hidden; }}
#r {{ position: relative; width: {w}px; height: {h}px; overflow: hidden; font-family: P;
  background: radial-gradient(ellipse 75% 120% at 50% 42%, #4A2DD0 0%, #3A20B4 45%, #2A1590 100%); }}
#floor {{ position: absolute; inset: 0; background: linear-gradient(rgba(20,8,90,0) 62%, rgba(20,8,90,.35) 100%); }}
svg {{ position: absolute; left: 0; top: 0; }}
img {{ position: absolute; }}
.sh {{ position: absolute; border-radius: 50%; background: rgba(14,4,70,.55); filter: blur(14px); }}
.t {{ position: absolute; color: #fff; text-align: center; }}
</style></head><body><div id="r"><div id="floor"></div>
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{clay}
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .09 -.02"/></filter></defs>
{svg}
<rect width="{w}" height="{h}" filter="url(#grain)" opacity=".9"/></svg>
{dom}
{text if PREVIEW else ""}
</div></body></html>"""


TUBE = 'fill="none" stroke="#9C84FF" stroke-width="16" stroke-linecap="round"'


def node(x, y, r=22, on=False):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#6A3DE8" if on else "#E4DAFF"}"/>' +
            (f'<circle cx="{x}" cy="{y}" r="{r * 0.36:.0f}" fill="#FF7A62"/>' if on else ""))


def bot(x, y, r=46):
    k = r / 66
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#F4EFFF"/>'
            f'<g transform="translate({x} {y}) scale({k})" fill="none" stroke="#5630D6" stroke-linecap="round"><path d="M-40 4 a40 40 0 0 1 80 0" stroke-width="8"/>'
            f'<rect x="-50" y="-6" width="16" height="30" rx="7" fill="#5630D6" stroke="none"/><rect x="34" y="-6" width="16" height="30" rx="7" fill="#5630D6" stroke="none"/><path d="M42 24 q0 22 -28 24" stroke-width="6"/></g>')


def rack(x, y, w=92, h=190):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#F4EFFF"/>'
    for i in range(6):
        s += f'<rect x="{x + 14}" y="{y + 18 + i * 27}" width="{w - 28}" height="14" rx="5" fill="{"#6A3DE8" if i % 3 == 1 else "#CDBDF8"}"/>'
    return s


def bubble(x, y, w=150, h=70):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="#fff"/><path d="M{x + 34} {y + h - 6} l-4 26 l30 -24 z" fill="#fff"/>' +
            "".join(f'<circle cx="{x + w / 2 + d}" cy="{y + h / 2}" r="8" fill="#6A3DE8"/>' for d in (-30, 0, 30)))


def who(name, x, bottom, hgt, flip=False):
    im = Image.open(A / f"{name}.png"); w = hgt * im.width / im.height
    return (f'<div class="sh" style="left:{x + w * 0.06:.0f}px;top:{bottom - 22}px;width:{w * 0.88:.0f}px;height:40px"></div>'
            f'<img src="assets/{name}.png" style="left:{x:.0f}px;top:{bottom - hgt}px;height:{hgt}px;{"transform:scaleX(-1);" if flip else ""}"/>'), w


def history():
    W, H = 1920, 720
    # 왼쪽 아래에서 들어와 바닥을 따라가다 오른쪽 끝에서 위로 올라가는 길(걸어온 길). 글자가 놓이는 가운데는 비움
    d = "M-40 650 L1560 650 C 1700 650, 1760 560, 1760 440 L1760 250"
    svg = (f'<g filter="url(#clay)"><path d="{d}" {TUBE}/>' + node(240, 650, on=True) + node(620, 650, on=True) + node(1000, 650, on=True) + node(1380, 650, on=True) + node(1760, 440)
           + bot(1760, 200, 54) + "</g>")
    c, w = who("customer", 28, 640, 190)
    text = ('<div class="t" style="left:360px;top:250px;text-align:left;font-weight:800;font-size:15px">우리가 걸어온 길<div style="font-size:48px;line-height:1.3;margin-top:12px">우리는 새로운 역사를<br>쓰고 있습니다.</div></div>'
            '<div class="t" style="left:920px;top:120px;width:640px;text-align:left;font-weight:500;font-size:17px;line-height:2">2026 · 코넥스 펀드 추가 투자 유치<br>라피치 NI사업부 인수 합병<br>2025 · …<br>2024 · …<br>2022 · …<br>2009 · …<br>2005 · …</div>')
    return W, H, page(W, H, svg, c, text)


def bottom():
    W, H = 1920, 420
    d = "M330 372 L1590 372"
    svg = f'<g filter="url(#clay)"><path d="{d}" {TUBE}/>' + node(520, 372, 18) + node(1400, 372, 18) + bubble(318, 70, 132, 62) + "</g>"
    c, w = who("customer", 110, 384, 250)
    a, w2 = who("counselor", 1590, 384, 250)
    text = ('<div class="t" style="left:0;top:118px;width:1920px;font-weight:800;font-size:40px">지금, 우리의 여정에 함께하세요.<div style="font-weight:500;font-size:18px;margin-top:18px">저희와 함께 더 나은 채용 문화를 만들어 나갈 멤버를 기다리고 있습니다.</div>'
            '<div style="display:inline-block;margin-top:30px;padding:14px 28px;border-radius:8px;background:#fff;color:#3A20B4;font-size:16px">진행 중인 공고 보러가기 ↗︎</div></div>')
    return W, H, page(W, H, svg, c + a, text)


def hero():
    W, H = 1600, 477
    # 왼쪽 = 대화형 AI(고객의 말), 오른쪽 = 네트워크 인프라(장비), 둘을 잇는 한 줄
    d = "M250 420 L1290 420"
    svg = (f'<g filter="url(#clay)"><path d="{d}" {TUBE}/>' + node(430, 420, 18, True) + node(800, 420, 18) + node(1170, 420, 18, True)
           + bubble(236, 44, 124, 58) + rack(1300, 236) + rack(1408, 236) + "</g>")
    c, w = who("customer", 70, 432, 240)
    text = ('<div style="position:absolute;inset:0;background:rgba(27,33,44,.4)"></div>'
            '<div class="t" style="left:0;top:130px;width:1600px;font-weight:800;font-size:16px;color:#B9CCF2">ABOUT RAPEECH<div style="font-size:44px;color:#fff;margin-top:14px">대화형 AI Agent부터 AI 인프라까지, 하나의 파트너로</div>'
            '<div style="font-weight:500;font-size:18px;color:#fff;margin-top:18px">라피치는 고객센터를 돕는 대화형 AI를 만들고, 그 AI가 일할 수 있는 네트워크까지 직접 구축합니다.</div></div>')
    return W, H, page(W, H, svg, c, text)


if __name__ == "__main__":
    A.mkdir(exist_ok=True)
    crop(HERE.parent / "assets_src/a_customer.png", A / "customer.png")
    crop(HERE.parent / "assets_src/a_counselor.png", A / "counselor.png")
    out = HERE / ("preview" if PREVIEW else "out"); out.mkdir(exist_ok=True)
    jobs = []
    for name, fn in (("history_bg", history), ("bottom_banner", bottom), ("about_hero", hero)):
        w, h, html = fn()
        (HERE / f"{name}.html").write_text(html)
        jobs.append((name, w, h))
    js = "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();" + "".join(
        f"{{const p=await b.newPage({{viewport:{{width:{w},height:{h}}},deviceScaleFactor:2}});await p.goto('file://{HERE}/{n}.html');await p.waitForTimeout(600);await p.screenshot({{path:'{out}/{n}.png'}});await p.close();}}"
        for n, w, h in jobs) + "await b.close();})();"
    subprocess.run(["node", "-e", js], check=True, cwd="/")
    if not PREVIEW:
        Image.open(out / "about_hero.png").convert("RGB").save(out / "about_hero.jpg", quality=93); (out / "about_hero.png").unlink()
    for p in sorted(out.iterdir()):
        print(p, Image.open(p).size)
