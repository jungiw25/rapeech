"""채용 홈페이지 배경 이미지 4종(영상 A안과 같은 찰흙 그림체). 크기는 실제 사이트의 PC(1920) 섹션 크기의 2배.
- history_bg.jpg     3840x2373  홈 '우리가 걸어온 길' 뒷배경
- bottom_banner.jpg  3840x716   홈 최하단 배너
- about_hero.jpg     3840x657   회사 소개 최상단 배너
- recruit_banner.jpg 3840x1120  채용 공고 최상단 배너(문구 포함)
사용법: python3 video/brand-film-hf/banners/build.py  → out/  (그다음 python3 video/brand-film-hf/banners/check.py 로 화면 너비별 잘림 확인)
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
PREVIEW = False


def crop(src, dst):
    im = Image.open(src).convert("RGBA")
    ys, xs = np.where(np.asarray(im)[..., 3] > 24)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst)


def page(w, h, svg, dom, pad=320):
    """w x h = 1920 화면에서의 섹션 크기. 양옆으로 pad 만큼 바탕을 더 그려, 2560 화면까지는 위아래가 잘리지 않게 한다."""
    clay = CLAY.format(id="clay", box=f'filterUnits="userSpaceOnUse" x="-{pad + 50}" y="-100" width="{w + 2 * pad + 100}" height="{h + 200}"')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: P; font-weight: 800; src: url(../../brand-film/assets/fonts/Pretendard-ExtraBold.otf); }}
@font-face {{ font-family: P; font-weight: 500; src: url(../../brand-film/assets/fonts/Pretendard-Medium.otf); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {w + 2 * pad}px; height: {h}px; overflow: hidden; }}
#r {{ position: relative; width: {w + 2 * pad}px; height: {h}px; overflow: hidden; font-family: P;
  background: radial-gradient(ellipse 75% 120% at 50% 42%, #4A2DD0 0%, #3A20B4 45%, #2A1590 100%); }}
#floor {{ position: absolute; inset: 0; background: linear-gradient(rgba(20,8,90,0) 62%, rgba(20,8,90,.35) 100%); }}
#c {{ position: absolute; left: {pad}px; top: 0; width: {w}px; height: {h}px; }}
svg {{ position: absolute; left: 0; top: 0; overflow: visible; }}
img {{ position: absolute; }}
.sh {{ position: absolute; border-radius: 50%; background: rgba(14,4,70,.55); filter: blur(14px); }}
</style></head><body><div id="r"><div id="floor"></div>
<div id="c"><svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{clay}</defs>{svg}</svg>
{dom}</div>
<svg width="{w + 2 * pad}" height="{h}"><defs><filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .09 -.02"/></filter></defs>
<rect width="{w + 2 * pad}" height="{h}" filter="url(#grain)" opacity=".9"/></svg>
</div></body></html>"""


def dots(items):
    """떠 있는 작은 찰흙 구슬(깊이감용). items = [(x, y, r, 색)]"""
    return '<g filter="url(#clay)">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in items) + "</g>"


def obj(name, x, bottom, hgt, flip=False, sh=True, rot=0, dark=True):
    im = Image.open(A / f"{name}.png"); w = hgt * im.width / im.height
    t = ("scaleX(-1) " if flip else "") + (f"rotate({rot}deg)" if rot else "")
    shadow = (f'<div class="sh" style="left:{x + w * 0.08:.0f}px;top:{bottom - 26}px;width:{w * 0.84:.0f}px;height:44px;{"" if dark else "background:rgba(70,45,130,.30);"}"></div>' if sh else "")
    return shadow + f'<img src="assets/{name}.png" style="left:{x:.0f}px;top:{bottom - hgt:.0f}px;height:{hgt}px;{"transform:" + t + ";" if t else ""}"/>'


L, W_, C_ = "#CDBDF8", "#F4EFFF", "#FF7A62"


# ── 실제 사이트 측정값(2026-11, 나인하이어): 네 곳 모두 object-fit: cover + 가운데 기준 자르기 ──
# 그래서 ① 이미지 비율은 1920 화면에서의 섹션 비율과 같게 하고 ② 소품은 글자 옆, 가운데에서 가까운 곳에 둔다.
# 화면이 좁아지면 같은 배율로 양옆만 잘리므로, 가운데에서 ±640px(1280 화면) 안에 둔 소품은 PC·노트북에서 모두 보인다.
def history():
    """연혁: 1920x1582(PC 실제 섹션 크기). 제목 아래 비어 있는 왼쪽 칸(가운데에서 -590~-60px)에 세로 계단."""
    W, H = 1920, 1582
    svg = dots([(1010, 96, 10, L), (1640, 150, 14, W_), (1700, 900, 18, L), (1620, 1480, 11, C_), (300, 620, 12, L), (250, 1380, 16, L), (880, 1440, 9, C_), (-180, 300, 16, L), (2080, 500, 14, W_), (-120, 1200, 12, C_)])
    dom = obj("stairs_tall", 490, 1300, 760)
    return W, H, page(W, H, svg, dom)


def bottom():
    """최하단: 1920x477. 글자는 가운데 ±300px. 동료들은 오른쪽(+310~+670), 종이비행기는 왼쪽(-540~-400)."""
    W, H = 1920, 477
    svg = ('<path d="M250 420 C 330 400, 380 330, 440 290" fill="none" stroke="#B9A5FF" stroke-width="6" stroke-linecap="round" stroke-dasharray="2 20" filter="url(#clay)"/>'
           + dots([(620, 70, 9, L), (1250, 60, 10, W_), (1700, 150, 13, L), (150, 180, 12, L), (1780, 400, 9, C_), (-160, 330, 12, L), (2100, 220, 14, W_)]))
    dom = obj("plane", 420, 290, 125, sh=False, rot=-6) + obj("team", 1242, 487, 205, sh=False)
    return W, H, page(W, H, svg, dom)


def hero():
    """회사 소개 상단: 1920x438. 글자는 가운데 ±508px(제목 줄)이라, 소품은 제목 아래 양쪽 아래 모서리에."""
    W, H = 1920, 438
    svg = dots([(330, 110, 10, L), (1600, 96, 12, W_), (190, 300, 9, C_), (1730, 300, 9, C_), (960, 400, 8, L), (-150, 150, 12, L), (2090, 250, 13, W_)])
    dom = obj("headset", 372, 424, 186) + obj("racks", 1352, 424, 150)
    return W, H, page(W, H, svg, dom)


def recruit():
    """채용 공고 상단(글자 포함): 1920x560. 휴대폰에서는 가운데 ±340px만 보이므로 글자를 가운데에 두고 소품은 양옆."""
    W, H = 1920, 560
    svg = dots([(700, 90, 12, L), (1230, 470, 9, "#6A3DE8"), (1640, 120, 11, C_), (260, 420, 14, L), (1780, 420, 12, L)])
    dom = (obj("desk", 1310, 420, 222, dark=False) + obj("plane", 420, 300, 120, sh=False, rot=-8)
           + '<div style="position:absolute;left:0;top:170px;width:1920px;text-align:center;color:#1B1B1F"><div style="font-weight:800;font-size:16px;letter-spacing:.32em;color:#6A3DE8">RAPEECH CAREERS</div>'
             '<div style="font-family:PB;font-weight:900;font-size:50px;line-height:1.34;letter-spacing:-.035em;margin-top:22px">라피치의 내일을<br>함께 이끌어갈 <span style="color:#6A3DE8">인재</span>를 찾습니다</div></div>')
    html = page(W, H, svg, dom, pad=0)
    html = html.replace("background: radial-gradient(ellipse 75% 120% at 50% 42%, #4A2DD0 0%, #3A20B4 45%, #2A1590 100%);",
                        "background: radial-gradient(ellipse 60% 90% at 50% 55%, #fffdf9 0%, rgba(255,253,249,0) 70%), linear-gradient(#F6F4F0 55%, #ECE8E1);")
    html = html.replace("background: linear-gradient(rgba(20,8,90,0) 62%, rgba(20,8,90,.35) 100%);", "background: none;")
    html = html.replace("0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .09 -.02", "0 0 0 0 .3  0 0 0 0 .2  0 0 0 0 .4  0 0 0 .07 -.02")
    html = html.replace("</style>", "@font-face { font-family: PB; font-weight: 900; src: url(../../brand-film/assets/fonts/Pretendard-Black.otf); }\n</style>", 1)
    return W, H, html


if __name__ == "__main__":
    A.mkdir(exist_ok=True)
    for n in ("stairs", "stairs_tall", "team", "headset", "racks", "desk", "plane"):
        crop(HERE.parent / f"assets_src/p_{n}.png", A / f"{n}.png")
    out = HERE / ("preview" if PREVIEW else "out"); out.mkdir(exist_ok=True)
    jobs = []
    for name, fn in (("history_bg", history), ("bottom_banner", bottom), ("about_hero", hero), ("recruit_banner", recruit)):
        w, h, html = fn()
        (HERE / f"{name}.html").write_text(html)
        jobs.append((name, w + (0 if name == "recruit_banner" else 640), h))
    js = "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();" + "".join(
        f"{{const p=await b.newPage({{viewport:{{width:{w},height:{h}}},deviceScaleFactor:{3840 / w}}});await p.goto('file://{HERE}/{n}.html');await p.waitForTimeout(600);await p.screenshot({{path:'{out}/{n}.png'}});await p.close();}}"
        for n, w, h in jobs) + "await b.close();})();"
    subprocess.run(["node", "-e", js], check=True, cwd="/")
    if not PREVIEW:
        for n, _, _ in jobs:
            Image.open(out / f"{n}.png").convert("RGB").save(out / f"{n}.jpg", quality=93); (out / f"{n}.png").unlink()
    for p in sorted(out.iterdir()):
        print(p, Image.open(p).size)
