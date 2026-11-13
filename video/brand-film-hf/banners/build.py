"""채용 홈페이지 배경 이미지 3종(영상 A안과 같은 찰흙 그림체, 흰 글자가 얹히므로 깊은 보라 바탕).
- history_bg.png  3840x1440  홈 '우리가 걸어온 길' 뒷배경
- bottom_banner.png 3840x840 홈 최하단 배너
- about_hero.jpg  3200x954   회사 소개 최상단 배너
- recruit_banner.png 3840x1120 채용 공고 최상단 배너(문구 포함, 원본 1920x560의 2배)
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


def dots(items):
    """떠 있는 작은 찰흙 구슬(깊이감용). items = [(x, y, r, 색)]"""
    return '<g filter="url(#clay)">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in items) + "</g>"


def obj(name, x, bottom, hgt, flip=False, sh=True, rot=0, dark=True):
    im = Image.open(A / f"{name}.png"); w = hgt * im.width / im.height
    t = ("scaleX(-1) " if flip else "") + (f"rotate({rot}deg)" if rot else "")
    shadow = (f'<div class="sh" style="left:{x + w * 0.08:.0f}px;top:{bottom - 26}px;width:{w * 0.84:.0f}px;height:44px;{"" if dark else "background:rgba(70,45,130,.30);"}"></div>' if sh else "")
    return shadow + f'<img src="assets/{name}.png" style="left:{x:.0f}px;top:{bottom - hgt:.0f}px;height:{hgt}px;{"transform:" + t + ";" if t else ""}"/>'


L, W_, C_ = "#CDBDF8", "#F4EFFF", "#FF7A62"


def history():
    """걸어온 길 = 한 계단씩 올라온 계단과 꼭대기의 깃발. 글자가 놓이는 왼쪽·가운데는 비움."""
    W, H = 1920, 720
    svg = dots([(150, 610, 26, L), (236, 668, 14, C_), (1490, 96, 16, W_), (1836, 150, 10, L), (92, 120, 12, L)])
    dom = obj("stairs", 1470, 700, 430)
    text = ('<div class="t" style="left:360px;top:250px;text-align:left;font-weight:800;font-size:15px">우리가 걸어온 길<div style="font-size:48px;line-height:1.3;margin-top:12px">우리는 새로운 역사를<br>쓰고 있습니다.</div></div>'
            '<div class="t" style="left:920px;top:120px;width:560px;text-align:left;font-weight:500;font-size:17px;line-height:2">2026 · 코넥스 펀드 추가 투자 유치<br>라피치 NI사업부 인수 합병<br>2025 · …<br>2024 · …<br>2022 · …<br>2009 · …<br>2005 · …</div>')
    return W, H, page(W, H, svg, dom, text)


def bottom():
    """함께하세요 = 손 흔드는 동료들 + 날아오는 종이비행기(지원)."""
    W, H = 1920, 420
    svg = ('<path d="M70 360 C 170 330, 210 250, 300 215" fill="none" stroke="#B9A5FF" stroke-width="7" stroke-linecap="round" stroke-dasharray="2 22" filter="url(#clay)"/>'
           + dots([(1290, 84, 12, W_), (1884, 120, 14, L), (520, 370, 10, C_)]))
    dom = obj("plane", 280, 250, 150, sh=False, rot=-6) + obj("team", 1330, 436, 300, sh=False)
    text = ('<div class="t" style="left:0;top:118px;width:1920px;font-weight:800;font-size:40px">지금, 우리의 여정에 함께하세요.<div style="font-weight:500;font-size:18px;margin-top:18px">저희와 함께 더 나은 채용 문화를 만들어 나갈 멤버를 기다리고 있습니다.</div>'
            '<div style="display:inline-block;margin-top:30px;padding:14px 28px;border-radius:8px;background:#fff;color:#3A20B4;font-size:16px">진행 중인 공고 보러가기 ↗︎</div></div>')
    return W, H, page(W, H, svg, dom, text)


def hero():
    """대화형 AI(헤드셋·말풍선)부터 AI 인프라(서버·케이블)까지. 사이트에서 40% 어두운 덮개가 씌워지므로 소품은 밝게."""
    W, H = 1600, 477
    svg = dots([(330, 70, 11, L), (1250, 80, 14, W_), (56, 250, 9, C_), (1560, 150, 9, C_)])
    dom = obj("headset", 30, 452, 280) + obj("racks", 1270, 458, 212)
    text = ('<div style="position:absolute;inset:0;background:rgba(27,33,44,.4)"></div>'
            '<div class="t" style="left:0;top:130px;width:1600px;font-weight:800;font-size:16px;color:#B9CCF2">ABOUT RAPEECH<div style="font-size:44px;color:#fff;margin-top:14px">대화형 AI Agent부터 AI 인프라까지, 하나의 파트너로</div>'
            '<div style="font-weight:500;font-size:18px;color:#fff;margin-top:18px">라피치는 고객센터를 돕는 대화형 AI를 만들고, 그 AI가 일할 수 있는 네트워크까지 직접 구축합니다.</div></div>')
    return W, H, page(W, H, svg, dom, text)


def recruit():
    """채용 공고 상단(글자가 이미지에 들어감): 영상과 같은 밝은 미색 바탕 + 지원서가 떠 있는 노트북."""
    W, H = 1920, 560
    svg = dots([(1090, 96, 14, L), (1846, 210, 12, C_), (1180, 470, 10, "#6A3DE8")])
    dom = (obj("desk", 1270, 520, 400, dark=False) + obj("plane", 1120, 250, 120, sh=False, rot=-8)
           + '<div style="position:absolute;left:300px;top:168px;color:#1B1B1F"><div style="font-weight:800;font-size:17px;letter-spacing:.32em;color:#6A3DE8">RAPEECH CAREERS</div>'
             '<div style="font-family:PB;font-weight:900;font-size:62px;line-height:1.32;letter-spacing:-.035em;margin-top:26px">라피치의 내일을<br>함께 이끌어갈 <span style="color:#6A3DE8">인재</span>를 찾습니다</div></div>')
    html = page(W, H, svg, dom)
    html = html.replace("background: radial-gradient(ellipse 75% 120% at 50% 42%, #4A2DD0 0%, #3A20B4 45%, #2A1590 100%);",
                        "background: radial-gradient(ellipse 60% 90% at 72% 62%, #fffdf9 0%, rgba(255,253,249,0) 70%), linear-gradient(#F6F4F0 55%, #ECE8E1);")
    html = html.replace("background: linear-gradient(rgba(20,8,90,0) 62%, rgba(20,8,90,.35) 100%);", "background: none;")
    html = html.replace("0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .09 -.02", "0 0 0 0 .3  0 0 0 0 .2  0 0 0 0 .4  0 0 0 .07 -.02")
    html = html.replace("@font-face {{", "@font-face {{").replace("</style>", "@font-face { font-family: PB; font-weight: 900; src: url(../../brand-film/assets/fonts/Pretendard-Black.otf); }\n</style>", 1)
    return W, H, html


if __name__ == "__main__":
    A.mkdir(exist_ok=True)
    for n in ("stairs", "team", "headset", "racks", "desk", "plane"):
        crop(HERE.parent / f"assets_src/p_{n}.png", A / f"{n}.png")
    out = HERE / ("preview" if PREVIEW else "out"); out.mkdir(exist_ok=True)
    jobs = []
    for name, fn in (("history_bg", history), ("bottom_banner", bottom), ("about_hero", hero), ("recruit_banner", recruit)):
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
