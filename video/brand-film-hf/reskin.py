"""회사 소개 영상(v16)의 장면 페이지를 복사해 A안(밝은 클레이) 모습으로 바꾼다.
장면·문구·타이밍은 원본 그대로 두고 색·질감·캐릭터 그림만 바꾼다.
사용법: python3 video/brand-film-hf/reskin.py flow|convai|rest
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FULL = HERE / "full"
BG, INK, PUR, PUR_D, PUR_L, LILAC, COR, GREY = "#F6F4F0", "#1B1B1F", "#6A3DE8", "#5630D6", "#8E72F2", "#DCCFFC", "#FF6B55", "#7B6FA6"

CMAP = {
    "#0c0916": BG, "rgba(0,0,0,0.45)": "rgba(120,100,160,.07)", "rgba(0,0,0,.45)": "rgba(120,100,160,.07)",
    "rgba(60,36,243,0.11)": "rgba(255,255,255,.7)", "rgba(60,36,243,.10)": "rgba(255,255,255,.7)",
    "rgba(28,23,48,.92)": "#ffffff", "rgba(20,15,42,.9)": "#ffffff", "#15102a": "#ffffff",
    "#1c1730": LILAC, "#1a1233": LILAC, "#120d24": "#EDE7FB",
    "#3a3158": "#C9BCF2", "#4a4166": "#C9BCF2",
    "#a69cc8": GREY, "#b5abd8": GREY, "#cfc6ec": GREY, "#8e86a8": GREY,
    "#ff03c8": PUR_L, "#ff4fd8": PUR_L, "#e807c3": PUR_L, "#d10bbd": PUR_L, "#ba0fb8": PUR_L, "#bd12ad": PUR_L, "#ad16a7": PUR_L, "#ff6fdc": PUR_L,
    "#ff8be6": "#B79CFF",
    "#a518a4": PUR, "#9b19ab": PUR, "#8f1ab8": PUR, "#881bb9": PUR, "#7a1dcc": PUR, "#751dc7": PUR, "#6a4dff": PUR, "#b25cff": PUR, "#7a6bff": PUR, "#9d79ff": PUR,
    "#661fdc": PUR_D, "#621fd6": PUR_D, "#5422e6": PUR_D, "#4823ee": PUR_D, "#4024f1": PUR_D, "#3c24f3": PUR_D,
    "#a9abff": PUR_L, "#8a8cff": PUR_L, "#5a5cff": PUR,
    "rgba(255,79,216,.75)": "rgba(106,61,232,.35)", "rgba(157,121,255,.6)": "rgba(106,61,232,.0)",
    "rgba(255,255,255,.4)": "rgba(106,61,232,.0)", "rgba(255,255,255,.3)": "rgba(106,61,232,.0)", "rgba(255,255,255,.35)": "rgba(106,61,232,.3)",
}
SHADOW = '<feDropShadow dx="0" dy="{dy}" stdDeviation="{sd}" flood-color="#46308a" flood-opacity="{op}"/>'
DEFS = f"""<radialGradient id="clay-off" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#f4eeff"/><stop offset=".45" stop-color="#cfbffb"/><stop offset="1" stop-color="#a48aee"/></radialGradient>
<radialGradient id="clay-on" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#b9a0ff"/><stop offset=".5" stop-color="#6f45ea"/><stop offset="1" stop-color="#4a25bd"/></radialGradient>
<radialGradient id="clay-cor" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#ffd0c4"/><stop offset=".55" stop-color="#ff7a62"/><stop offset="1" stop-color="#e2543f"/></radialGradient>
<filter id="clay-blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="clay-sh" x="-60%" y="-60%" width="220%" height="260%">{SHADOW.format(dy=12, sd=8, op=.32)}</filter>"""
CSS = f"""
/* ── A안(밝은 클레이) 덮어쓰기 ── */
.say, .ct {{ font-weight: 900 !important; }}
.grad, .g {{ background: none !important; -webkit-background-clip: border-box !important; background-clip: border-box !important; color: {PUR} !important; }}
.f-card {{ border: none !important; border-radius: 30px !important; box-shadow: 0 26px 34px -14px rgba(70,45,130,.30); }}
.f-cl {{ color: {PUR_D} !important; font-weight: 700 !important; }}
.f-bub, .bub, .pill, .plate {{ box-shadow: 0 18px 26px -10px rgba(70,45,130,.28); border: none !important; }}
"""


def cmap(s):
    def r(m):
        k = m.group(0).lower().replace(" ", "")
        return CMAP.get(k, m.group(0))
    return re.sub(r"#[0-9a-fA-F]{6}\b|rgba\([^)]*\)", r, s)


def common(s):
    s = cmap(s)
    s = re.sub(r"color:\s*#fff\b", f"color: {INK}", s)
    s = re.sub(r'(<text\b[^>]*fill=")#fff(")', rf"\g<1>{INK}\2", s)
    # 번지는 빛(glow) 필터 → 아래로 떨어지는 부드러운 그림자
    s = re.sub(r"(<filter\b[^>]*>)\s*<feGaussianBlur[^>]*/>\s*<feMerge>.*?</feMerge>\s*(</filter>)",
               lambda m: m.group(1) + SHADOW.format(dy=10, sd=7, op=.3) + m.group(2), s, flags=re.S)
    s = s.replace("<defs>", "<defs>" + DEFS, 1)
    s = s.replace("</style>", CSS + "</style>", 1)
    return s


def crop(src, dst):
    im = Image.open(src).convert("RGBA")
    ys, xs = np.where(np.asarray(im)[..., 3] > 24)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)); im.save(dst)
    return im.size


def flow():
    d = FULL / "flow"
    if d.exists(): shutil.rmtree(d)
    src = REPO / "video/brand-film"
    (d / "compositions").mkdir(parents=True)
    shutil.copytree(src / "assets", d / "assets", ignore=shutil.ignore_patterns("*.mp4", "*.wav"))
    for f in ("hyperframes.json", "meta.json", "package.json"):
        if (src / f).exists(): shutil.copy(src / f, d / f)
    cw, ch = crop(HERE / "assets_src/a_customer.png", d / "assets/customer.png")
    aw, ah = crop(HERE / "assets_src/a_counselor.png", d / "assets/counselor.png")
    # 콜봇 흐름 장면만 0초부터 렌더
    idx = (src / "index.html").read_text()
    idx = re.sub(r'\s*<(video|audio)\b[^>]*></\1>', "", idx)
    idx = re.sub(r'\s*<div id="s\d\d"[^>]*>\s*</div>', "", idx, flags=re.S)
    idx = idx.replace('data-start="12.00"', 'data-start="0"').replace('data-duration="74.50"', 'data-duration="35"')
    (d / "index.html").write_text(cmap(idx))
    s = common((src / "compositions/flow.html").read_text())
    # 단추(노드): 연보라 찰흙 공 → 켜지면 진보라 + 주황 심
    s = re.sub(rf'(<circle cx="\d+" cy="\d+" r="(?:30|66)") fill="{LILAC}" stroke="#C9BCF2" stroke-width="3"/>', r'\1 fill="url(#clay-off)" filter="url(#clay-sh)"/>', s)
    s = re.sub(r'(class="f-nfill o" id="f-nf\d" cx="\d+" cy="\d+" r="30") fill="url\(#flow-g\)" filter="url\(#flow-glow\)"', r'\1 fill="url(#clay-on)"', s)
    s = re.sub(r'(class="o" id="f-nf4" cx="\d+" cy="\d+" r="66") fill="url\(#flow-g\)" filter="url\(#flow-glow\)"', r'\1 fill="url(#clay-on)"', s)
    s = re.sub(r'(class="f-ncore o" id="f-nc\d"[^>]*) fill="#fff"', r'\1 fill="url(#clay-cor)"', s)
    s = s.replace(f'font-size="34" fill="{INK}">AI<', 'font-size="34" fill="#fff">AI<')
    # 목소리 알갱이: 주황
    s = s.replace('id="f-pkr" x="-56" y="-24" width="112" height="48" rx="24" fill="url(#flow-g)"', 'id="f-pkr" x="-56" y="-24" width="112" height="48" rx="24" fill="url(#clay-cor)"')
    s = s.replace('<g id="f-rpk"><circle r="16" fill="#fff"', '<g id="f-rpk"><circle r="18" fill="url(#clay-cor)"')
    # 고객: 찰흙 캐릭터(전화기를 들고 있으므로 따로 그린 전화기는 숨김)
    H = 330; W = H * cw / ch; X = 452 - W * 0.985; Y = 500 - H * 0.42
    s = re.sub(r'<image href="assets/emoji/speaking_head_lit.png"[^>]*/>', f'<image href="assets/customer.png" x="{X:.0f}" y="{Y:.0f}" width="{W:.0f}" height="{H}"/>', s)
    s = s.replace('<g id="f-phone">', '<g id="f-phone" style="display:none">')
    # 상담사
    s = re.sub(r'<image href="assets/emoji/agent_headset_lit.png" x="(\d+)" y="(\d+)" width="180" height="180"/>',
               lambda m: f'<image href="assets/counselor.png" x="{int(m.group(1)) - 20}" y="{int(m.group(2)) - 30}" width="{220 * aw / ah:.0f}" height="220"/>', s)
    # 봇 답변 말풍선: 진보라 바탕 흰 글씨
    s = re.sub(r'(id="f-bbub" style="background:)[^;]*;color:[^"]*"', rf'\1{PUR};color:#fff"', s)
    s = s.replace('class="f-hr" cx="234" cy="504" r="118" fill="none" stroke="#fff"', f'class="f-hr" cx="234" cy="504" r="118" fill="none" stroke="{COR}"')
    # 선은 굵은 찰흙 관으로, 단추는 조금 크게
    s = re.sub(r'(<path id="f-rail[LR]"[^>]*stroke-width=")6"', r'\g<1>16"', s)
    s = s.replace('stroke="url(#flow-g)" stroke-width="5" stroke-linecap="round" filter="url(#flow-glows)"/>', 'stroke="url(#flow-g)" stroke-width="10" stroke-linecap="round" filter="url(#flow-glows)"/>')
    s = re.sub(r'(<circle (?:class="f-nfill o" id="f-nf\d" )?cx="\d+" cy="\d+" r=")30"', r'\g<1>40"', s)
    s = re.sub(r'(class="f-ncore o"[^>]*r=")11"', r'\g<1>14"', s)
    s = re.sub(r'(class="f-npulse o" id="f-np[0-3]"[^>]*r=")36"', r'\g<1>48"', s)
    s = re.sub(r'(class="f-ring"[^>]*stroke-width=")4"', r'\g<1>9"', s)
    s = s.replace("font-size:60px", "font-size:74px")
    # 고객 뒤의 빛 대신 바닥 그림자
    s = s.replace('<g id="f-av">\n      <circle cx="234" cy="504" r="150" fill="url(#f-avglow)"/>', f'<g id="f-av">\n      <ellipse cx="{X + W * 0.45:.0f}" cy="{Y + H - 8:.0f}" rx="{W * 0.46:.0f}" ry="20" fill="#3c286e" opacity=".3" filter="url(#clay-blur)"/>')
    assert "clay-blur)\"/>" in s
    (d / "compositions/flow.html").write_text(s)
    return d


def snap(proj, t, dst):
    """앞 장면의 마지막 화면을 다음 장면의 첫 화면으로 쓴다(이음매가 튀지 않게)."""
    o = FULL / proj / "snap_last"
    if o.exists(): shutil.rmtree(o)
    subprocess.run(["npx", "hyperframes", "snapshot", "--at", str(t), "--no-end", "-o", str(o)], cwd=FULL / proj, check=True, capture_output=True)
    shutil.copy(sorted(o.glob("frame-*.png"))[0], dst)


def copy_proj(src, name):
    d = FULL / name
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copytree(src / "assets", d / "assets", ignore=shutil.ignore_patterns("*.wav"))
    for f in ("hyperframes.json", "meta.json"):
        shutil.copy(src / f, d / f)
    return d


def lines(s, w=1.8, col=PUR_D):
    """흰 가는 선 → 보라 선(조금 굵게, 또렷하게)."""
    def r(m):
        t = m.group(0).replace('stroke="#fff"', f'stroke="{col}"')
        t = re.sub(r'stroke-width="([\d.]+)"', lambda k: f'stroke-width="{float(k.group(1)) * w:.1f}"', t)
        t = re.sub(r'stroke-opacity="\.(\d+)"', lambda k: f'stroke-opacity="{min(1, float("0." + k.group(1)) * 1.6):.2f}"', t)
        return t
    return re.sub(r'<(?:path|rect|line|circle|polyline)\b[^>]*stroke="#fff"[^>]*>', r, s)


def convai():
    d = copy_proj(REPO / "video/convai-samples/b", "convai")
    crop(HERE / "assets_src/a_customer.png", d / "assets/customer.png")
    crop(HERE / "assets_src/a_counselor.png", d / "assets/agent.png")
    snap("flow", 32.6, d / "assets/flow_last.png")
    s = (REPO / "video/convai-samples/b/index.html").read_text()
    s = re.sub(r'\s*<audio\b[^>]*></audio>', "", s)
    # 단추: 찰흙 공. 연결선: 굵은 보라 관. 움직이는 점: 주황 구슬
    s = re.sub(r'fill="#1a1233" stroke="#fff" stroke-opacity=".4" stroke-width="1.5"', 'fill="url(#clay-off)" filter="url(#clay-sh)"', s)
    s = s.replace('stroke="#fff" stroke-opacity=".7" stroke-width="2"', f'stroke="{PUR}" stroke-width="7" stroke-linecap="round"')
    s = s.replace('stroke="#ff4fd8" stroke-width="2.5"', f'stroke="{PUR}" stroke-width="6" stroke-linecap="round"')
    s = re.sub(r'(<circle (?:id="d\d"|class="[^"]*")? ?r=")7" fill="#fff"', r'\g<1>11" fill="url(#clay-cor)"', s)
    s = s.replace('stroke="#fff" stroke-opacity=".45" stroke-width="1.5"', 'stroke="#C9BCF2" stroke-width="3"')
    s = s.replace('<rect x="-86" y="-24" width="172" height="48" rx="12" fill="#fff"/>', '<rect x="-86" y="-24" width="172" height="48" rx="14" fill="#fff" filter="url(#clay-sh)"/>')
    s = common(s)
    s = s.replace("</style>", f"""
.ct {{ font-size: 64px !important; }}
.a {{ background: {PUR} !important; color: #fff !important; }}
.think {{ background: {LILAC} !important; color: {PUR_D} !important; }}
.q {{ color: {INK} !important; }}
.plate small {{ color: {GREY} !important; }}
</style>""", 1)
    (d / "index.html").write_text(s)
    return d


def rest():
    d = copy_proj(REPO / "video/brand-film-v3b", "rest")
    shutil.copy(REPO / "video/brand-film-v3b/assets/rest_sfx.wav", d / "assets/rest_sfx.wav")
    snap("flow", 32.6, d / "assets/flow_last.png")
    snap("convai", 27.98, d / "assets/convai_last.png")
    s = (REPO / "video/brand-film-v3b/index.html").read_text()
    # 장비·건물은 흰 몸체 + 그림자, 단계 표시는 찰흙 공, 진행선은 굵은 관
    s = re.sub(r'((?:id="swb"|class="rk")[^>]*) fill="#120d24"', r'\1 fill="#ffffff" filter="url(#clay-sh)"', s)
    s = re.sub(r'(<(?:rect|path) class="bld"(?! x="250")[^>]*) fill="none"', r'\1 fill="#ffffff" filter="url(#clay-sh)"', s)
    s = s.replace('stroke="#fff" stroke-opacity=".75" stroke-width="2"/>', f'stroke="{PUR}" stroke-width="10" stroke-linecap="round"/>')
    s = s.replace('r="16" fill="#0c0916" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"', 'r="24" fill="url(#clay-off)" filter="url(#clay-sh)"')
    s = s.replace("{ attr: { r: 9 } }", "{ attr: { r: 24 } }")
    s = re.sub(r'(class="(?:pulse|lpu)"[^>]*r=")5" fill="#fff"', r'\g<1>9" fill="url(#clay-cor)"', s)
    s = re.sub(r'(class="mkf"[^>]*) fill="#fff"', r'\1 fill="url(#clay-on)"', s)
    s = s.replace('<g id="dot"><circle r="14" fill="#fff" opacity=".22"/><circle r="6.5" fill="#fff"/></g>', f'<g id="dot"><circle r="16" fill="{PUR}" opacity=".22"/><circle r="8" fill="{PUR}"/></g>')
    s = lines(s)
    s = s.replace("#f7c6ec", "#EDE3FF").replace("#d3c9fe", "#CDBBFA")
    s = s.replace("mix-blend-mode:lighten", "mix-blend-mode:darken")
    s = common(s)
    s = s.replace("</style>", f"""
.ct {{ font-size: 64px !important; }}
.val {{ color: {INK} !important; font-weight: 800 !important; }}
</style>""", 1)
    (d / "index.html").write_text(s)
    return d


def outro():
    d = copy_proj(REPO / "video/outro-v4", "outro")
    shutil.copy(REPO / "video/outro-v4/assets/outro_sfx.wav", d / "assets/outro_sfx.wav")
    (d / "index.html").write_text(common((REPO / "video/outro-v4/index.html").read_text()))
    return d


if __name__ == "__main__":
    print({"flow": flow, "convai": convai, "rest": rest, "outro": outro}[sys.argv[1]]())
