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
# 찰흙 질감: 가장자리를 둥글게 부풀려 빛을 받게 하고(위 왼쪽 조명), 고운 알갱이와 바닥 그림자를 더함
CLAY = """<filter id="{id}" {box} color-interpolation-filters="sRGB">
<feGaussianBlur in="SourceAlpha" stdDeviation="5" result="b"/>
<feDiffuseLighting in="b" surfaceScale="7" diffuseConstant="1.06" lighting-color="#ffffff" result="l"><feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting>
<feComposite in="l" in2="SourceGraphic" operator="arithmetic" k1="0.9" k2="0" k3="0.25" k4="0" result="s"/>
<feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="2" seed="7" result="n"/>
<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .4 -.16" result="na"/>
<feMerge result="m"><feMergeNode in="s"/><feMergeNode in="na"/></feMerge>
<feComposite in="m" in2="SourceAlpha" operator="in" result="body"/>
<feGaussianBlur in="SourceAlpha" stdDeviation="7" result="sb"/><feOffset in="sb" dy="12" result="so"/>
<feFlood flood-color="#46308a" flood-opacity=".3"/><feComposite in2="so" operator="in" result="sh"/>
<feMerge><feMergeNode in="sh"/><feMergeNode in="body"/></feMerge></filter>"""
DEFS = f"""<radialGradient id="clay-off" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#f4eeff"/><stop offset=".45" stop-color="#cfbffb"/><stop offset="1" stop-color="#a48aee"/></radialGradient>
<radialGradient id="clay-on" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="#b9a0ff"/><stop offset=".5" stop-color="#6f45ea"/><stop offset="1" stop-color="#4a25bd"/></radialGradient>
<radialGradient id="clay-cor" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#ffd0c4"/><stop offset=".55" stop-color="#ff7a62"/><stop offset="1" stop-color="#e2543f"/></radialGradient>
<filter id="clay-blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="12"/></filter>
{CLAY.format(id="clayS", box='x="-30%" y="-30%" width="160%" height="185%"')}
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
    # 연결선은 흐릿하게 시작하지 않고 처음부터 또렷한 보라 끈
    s = s.replace('p.setAttribute("stroke", "url(#" + id + ")"); p.removeAttribute("stroke-opacity");', 'p.removeAttribute("stroke-opacity");')
    s = s.replace('o.end || "#ff8be6"', f'o.end || "{PUR}"').replace('st.setAttribute("fill", "#fff"); st.setAttribute("fill-opacity", ".6")', f'st.setAttribute("fill", "{PUR}"); st.setAttribute("fill-opacity", "1")')
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
    bx = Image.open(HERE / "assets_src/a_customer.png").convert("RGBA")
    ys, xs = np.where(np.asarray(bx)[..., 3] > 24)
    Image.open(HERE / "assets_src/a_customer_talk.png").crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(d / "assets/customer_talk.png")
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
    s = clay_flow(s, X, Y, W, H)
    (d / "compositions/flow.html").write_text(s)
    return d


POP = '''const POP = (sel, t, st = 0, d = 0.8) => { gsap.set(sel, { opacity: 0 }); tl.fromTo(sel, { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: d, ease: "elastic.out(1,0.6)", stagger: st, immediateRender: false }, t); };
'''


def must(s, a, b, n=1):
    assert s.count(a) >= n, a[:70]
    return s.replace(a, b)


def clay_flow(s, X, Y, W, H):
    CX, BY = X + W * 0.45, Y + H
    s = s.replace("<defs>", "<defs>" + CLAY.format(id="clayRail", box='filterUnits="userSpaceOnUse" x="380" y="470" width="4300" height="170"'), 1)
    # 선·단추·알갱이를 캐릭터와 같은 찰흙 질감으로
    s = must(s, 'fill="url(#clay-off)" filter="url(#clay-sh)"', 'fill="#CDBDF8" filter="url(#clayS)"', 5)
    s = must(s, 'fill="url(#clay-on)"', f'fill="{PUR}" filter="url(#clayS)"', 5)
    s = must(s, 'fill="url(#clay-cor)"', 'fill="#FF7A62" filter="url(#clayS)"', 5)
    s = re.sub(r'(<path id="f-rail[LR]"[^>]*) filter="url\(#flow-glows\)"', r'\1 filter="url(#clayRail)"', s)
    s = must(s, 'stroke-width="10" stroke-linecap="round" filter="url(#flow-glows)"/>', 'stroke-width="10" stroke-linecap="round" filter="url(#clayS)"/>')
    # 띠링(빛 고리) → 찰흙 세계에 맞게: 연보라 고리가 폭신하게 퍼졌다 사라짐
    s = re.sub(rf'(class="f-npulse o"[^>]*) stroke="{PUR_L}" stroke-width="3"', r'\1 stroke="#D9CCFF" stroke-width="12"', s)
    s = re.sub(r'(class="f-hr"[^>]*stroke=")[^"]*(" stroke-width=")[\d.]+', r'\g<1>#D9CCFF\g<2>16', s)
    # 고객: 입 다문 그림 + 입 벌린 그림(말할 때 번갈아)
    s = re.sub(r'(<image href="assets/customer.png"[^>]*/>)', lambda m: f'<g id="f-cimg">{m.group(1).replace("<image", "<image id=\"f-m0\"")}{m.group(1).replace("customer.png", "customer_talk.png").replace("<image", "<image id=\"f-m1\" opacity=\"0\"")}</g>', s)
    s, n = re.subn(r'(<circle cx="3660" cy="870" r="120"[^>]*/>.*?상담사</text>)', r'<g id="f-agimg">\1</g>', s, flags=re.S)
    assert n == 1
    O = f'svgOrigin: "{CX:.0f} {BY:.0f}"'
    # ── 움직임 ──
    s = must(s, 'tl.fromTo("#f-av", { opacity: 0, scale: 0.85, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 1.1, ease: "power3.out" }, 3.7);',
             f"""tl.fromTo("#f-av", {{ opacity: 1, y: -620, scaleX: 0.92, scaleY: 1.1, {O} }}, {{ opacity: 1, y: 0, duration: 0.42, ease: "power2.in" }}, 3.75);
      gsap.set("#f-av", {{ opacity: 0 }}); tl.set("#f-av", {{ opacity: 1 }}, 3.75);
      tl.to("#f-av", {{ scaleX: 1.12, scaleY: 0.84, {O}, duration: 0.1, ease: "power2.out" }}, 4.17);
      tl.to("#f-av", {{ scaleX: 1, scaleY: 1, {O}, duration: 0.9, ease: "elastic.out(1,0.42)" }}, 4.27);""")
    s = must(s, 'tl.fromTo(["#f-n1", "#f-n2", "#f-n3", "#f-bot"], { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "sine.inOut" }, 3.4);',
             """gsap.set(["#f-n1", "#f-n2", "#f-n3", "#f-bot"], { opacity: 0 });
      tl.fromTo("#f-n1", { opacity: 0, scale: 0, svgOrigin: "1860 540" }, { opacity: 1, scale: 1, duration: 0.9, ease: "elastic.out(1,0.5)" }, 3.8);
      tl.set(["#f-n2", "#f-n3", "#f-bot"], { opacity: 1 }, 5.4);""")
    s = must(s, 'ease: "back.out(1.4)" }, 3.45);', 'ease: "elastic.out(1,0.5)" }, 3.45);')
    # 전화가 울릴 때: 캐릭터가 살짝 흔들림(따로 그린 전화기는 숨겼으므로)
    s = must(s, '"#f-phone", { rotation: k % 2 ? 7 : -7, svgOrigin: "425 500"', f'"#f-cimg", {{ rotation: k % 2 ? 2 : -2, {O}', 2)
    s = must(s, '"#f-phone", { rotation: 0, svgOrigin: "425 500"', f'"#f-cimg", {{ rotation: 0, {O}', 2)
    # 말풍선: 통 튀어나옴 / 말하는 동안 입이 움직임
    s = must(s, '{ opacity: 0, y: 20, scale: 0.9, filter: "blur(10px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }',
             '{ opacity: 0, y: 30, scale: 0.35 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "elastic.out(1,0.6)" }', 2)
    s = must(s, '// 목소리 묶음:', f"""for (let k = 0; k < 9; k++) {{ tl.set("#f-m1", {{ opacity: k % 2 ? 0 : 1 }}, 7.8 + k * 0.15); tl.set("#f-m0", {{ opacity: k % 2 ? 1 : 0 }}, 7.8 + k * 0.15); }}
      tl.set("#f-m1", {{ opacity: 0 }}, 9.2); tl.set("#f-m0", {{ opacity: 1 }}, 9.2);
      for (let k = 0; k < 4; k++) tl.to("#f-cimg", {{ y: -9, duration: 0.14, ease: "sine.out", yoyo: true, repeat: 1 }}, 7.82 + k * 0.3);
      // 목소리 묶음:""")
    # 단추에 닿는 순간: 눌렸다가 탱 하고 돌아옴(빛 번쩍임 대신) / 카드는 톡 튀어나옴
    s = must(s, 'const R = i < 4 ? 30 : 66;', """const R = i < 4 ? 40 : 66;
        tl.fromTo(i < 4 ? "#f-n" + i : "#f-bot", { scaleX: 1.25, scaleY: 0.78, svgOrigin: ST[i] + " " + LY }, { scaleX: 1, scaleY: 1, svgOrigin: ST[i] + " " + LY, duration: 1.0, ease: "elastic.out(1,0.38)", immediateRender: false }, t + 0.03);""")
    s = must(s, 'tl.fromTo("#f-nf" + i, { scale: 1 }, { scale: 1.14, duration: 0.22, ease: "power2.out", yoyo: true, repeat: 1 }, t + 0.02);', "")
    s = must(s, 'tl.set("#f-pkr", { attr: CIRC(30) }, t);', 'tl.set("#f-pkr", { attr: CIRC(40) }, t);')
    s = must(s, '{ opacity: 0, y: 26, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }',
             '{ opacity: 0, y: -34, scale: 0.6, transformOrigin: "50% 0%" }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "elastic.out(1,0.62)" }')
    # 답이 고객에게 닿는 순간: 캐릭터가 기뻐서 폴짝
    s = must(s, 'tl.fromTo("#f-hglow", { opacity: 0 }', f"""tl.to("#f-av", {{ y: -80, duration: 0.24, ease: "power2.out", yoyo: true, repeat: 1 }}, 30.0);
      tl.to("#f-av", {{ scaleX: 1.1, scaleY: 0.86, {O}, duration: 0.1, ease: "power2.out" }}, 30.48);
      tl.to("#f-av", {{ scaleX: 1, scaleY: 1, {O}, duration: 0.8, ease: "elastic.out(1,0.42)" }}, 30.58);
      tl.fromTo("#f-hglow", {{ opacity: 0 }}""")
    # 상담사는 점선이 다 이어진 뒤에 톡 나타남(먼저 보이지 않게)
    s = must(s, 'tl.fromTo("#f-agent", { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "sine.inOut" }, 29.4);',
             """gsap.set("#f-branch", { opacity: 0 }); tl.set("#f-branch", { opacity: 1 }, 29.5);
      tl.fromTo("#f-agimg", { opacity: 0, scale: 0.3, svgOrigin: "3660 900" }, { opacity: 1, scale: 1, duration: 0.8, ease: "elastic.out(1,0.55)", immediateRender: false }, 30.3);
      tl.set("#f-agent", { opacity: 1 }, 29.45);""")
    return s


def clay_convai(s):
    s = must(s, 'fill="url(#clay-off)" filter="url(#clay-sh)"', 'fill="#CDBDF8" filter="url(#clayS)"', 3)
    s = must(s, f'stroke="{PUR}" stroke-width="7" stroke-linecap="round"', f'stroke="{PUR}" stroke-width="8" stroke-linecap="round" filter="url(#clayS)"', 3)
    s = must(s, f'stroke="{PUR}" stroke-width="6" stroke-linecap="round"', f'stroke="{PUR}" stroke-width="9" stroke-linecap="round" filter="url(#clayS)"', 3)
    s = must(s, 'fill="url(#clay-cor)"', 'fill="#FF7A62" filter="url(#clayS)"', 3)
    s = must(s, "// ── 1.", POP + "// ── 1.")
    # 선은 구슬이 지나가는 만큼만 그려짐(먼저 보이지 않게)
    s = must(s, 'FIN(["#l1", "#d1"], 2.5, 0.05);', 'FIN(["#l1", "#d1"], 2.5, 0.05); DR("#l1", 2.5, 1.0);')
    s = must(s, 'FIN(["#l2", "#d2"], 7.7, 0.05);', 'FIN(["#l2", "#d2"], 7.7, 0.05); DR("#l2", 7.7, 1.0);')
    s = must(s, 'FIN("#l3", 14.5, 0.05);', 'FIN("#l3", 14.5, 0.05); DR("#l3", 14.5, 0.9);')
    # 등장은 톡 튀어나오게
    s = re.sub(r'(tl\.fromTo\("#(?:cust|n\d)", \{ opacity: 0, scale: )0\.\d+(, transformOrigin: "50% 50%" \}, \{ opacity: 1, scale: 1, duration: )[\d.]+, ease: "power3.out"',
               r'\g<1>0.3\g<2>1.0, ease: "elastic.out(1,0.55)"', s)
    s = re.sub(r'(tl\.fromTo\("#[qa]\d", \{ opacity: 0, [xy]: -?\d+) \}, \{ opacity: 1, ([xy]): 0, duration: 0.6, ease: "power3.out"',
               r'\1, scale: 0.4 }, { opacity: 1, \2: 0, scale: 1, duration: 0.8, ease: "elastic.out(1,0.62)"', s)
    # 단추에 고리가 다 감기면 통 튐(빛 번쩍임 대신)
    for n, t, (x, y) in ((1, 4.1, (1180, 330)), (2, 9.9, (1180, 610)), (3, 16.4, (1600, 470))):
        s = must(s, f'DR("#n{n}R", ', f'tl.fromTo("#n{n}", {{ scaleX: 1.16, scaleY: 0.86, svgOrigin: "{x} {y}" }}, {{ scaleX: 1, scaleY: 1, svgOrigin: "{x} {y}", duration: 0.9, ease: "elastic.out(1,0.4)", immediateRender: false }}, {t}); DR("#n{n}R", ')
    s = must(s, 'FIN("#grid", 18.7, 0.05);', 'FIN("#grid", 18.7, 0.05); gsap.set(".cell", { opacity: 0 }); tl.to(".cell", { opacity: 1, duration: 0.5, ease: "sine.out", stagger: 0.07 }, 18.7);')
    s = must(s, '{ opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out"', '{ opacity: 0, y: 16, scale: 0.7 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "elastic.out(1,0.7)"')
    return s


def clay_rest(s):
    s = s.replace("<defs>", "<defs>" + CLAY.format(id="clayU", box='filterUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"'), 1)
    C = ' filter="url(#clayS)"'
    # 장비·건물: 찰흙 판(외곽선 없이 면으로), 선은 찰흙 끈
    s = re.sub(r'((?:id="swb"|class="rk")[^>]*) fill="#120d24" stroke="#fff" stroke-opacity="[^"]*" stroke-width="[^"]*"', rf'\1 fill="#F4EFFF"{C}', s)
    s = re.sub(r'(class="port"[^>]*) fill="#0c0916" stroke="#fff" stroke-opacity="[^"]*" stroke-width="[^"]*"', rf'\1 fill="{PUR}"', s)
    s = re.sub(r'(class="rslot"[^>]*) fill="none" stroke="#fff" stroke-opacity="[^"]*" stroke-width="[^"]*"', r'\1 fill="#E1D7FB"', s)
    s = re.sub(r'(<(?:rect|path) class="bld"(?! x="250")[^>]*) fill="none" stroke="#fff" stroke-opacity="[^"]*" stroke-width="[^"]*"', rf'\1 fill="#F4EFFF"{C}', s)
    s = re.sub(r'(<rect class="bld" x="250"[^>]*stroke-width=")[^"]*"', rf'\g<1>4"{C}', s)
    s = re.sub(r'(class="bdet" [^>]*) fill="none" stroke="#fff" stroke-opacity="[^"]*"', r'\1 fill="#D9CCFF"', s)
    s = re.sub(r'(<path class="cab"[^>]*stroke-width=")[^"]*"', rf'\g<1>4"{C}', s)
    s = re.sub(r'(<g class="ic" id="ic\d")', rf'\1{C}', s)
    s = must(s, 'stroke="#fff" stroke-opacity=".75" stroke-width="2"/>', f'stroke="{PUR}" stroke-width="12" stroke-linecap="round" filter="url(#clayU)"/>')
    s = must(s, 'r="16" fill="#0c0916" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"', f'r="26" fill="#CDBDF8"{C}', 4)
    s = re.sub(r'(class="mkf"[^>]*) fill="#fff"', rf'\1 fill="{PUR}"{C}', s)
    s = must(s, "{ attr: { r: 9 }", "{ attr: { r: 26 }")
    s = re.sub(r'(class="(?:pulse|lpu)"[^>]*r=")5" fill="#fff"', rf'\g<1>10" fill="#FF7A62"{C}', s)
    # ── 움직임: 면이 선보다 먼저 보이지 않게, 모두 톡 튀어나오며 등장 ──
    s = must(s, "// ── 2. 네트워크 인프라", POP + "// ── 2. 네트워크 인프라")
    s = must(s, 'DR("#swb", N, 0.8); DR(".port", N + 0.2, 0.5, "power2.out", 0.03);', 'POP("#swb", N); POP(".port", N + 0.35, 0.04, 0.5); gsap.set(".pled", { opacity: 0 }); tl.to(".pled", { opacity: 1, duration: 0.3 }, N + 0.6);')
    s = must(s, 'DR(".rk", N + 0.1, 0.9, "power2.inOut", 0.12); DR(".rslot", N + 0.4, 0.5, "power2.out", 0.008);', 'POP(".rk", N + 0.15, 0.12); gsap.set(".rslot", { opacity: 0 }); tl.to(".rslot", { opacity: 1, duration: 0.3, stagger: 0.008 }, N + 0.75);')
    s = must(s, 'gsap.set(".rled", { opacity: 0.12 });', 'gsap.set(".rled", { opacity: 0 }); tl.to(".rled", { opacity: 0.12, duration: 0.3 }, N + 0.9);')
    s = must(s, 'DR(".bld", 11.4, 1.0, "power2.inOut", 0.25);', 'POP(".bld", 11.5, 0.22);')
    s = must(s, 'FIN(".bdet", 12.2, 0.6);', 'FIN(".bdet", 12.2, 0.35);')
    s = must(s, 'FIN(["#gd", ".mk"], 15.3, 0.6);', 'FIN("#gd", 15.3, 0.6); tl.set(".mk", { opacity: 1 }, 15.3); gsap.utils.toArray(".mk").forEach((m, i) => { gsap.set(m, { scale: 0, svgOrigin: MX[i] + " " + MY }); tl.to(m, { scale: 1, svgOrigin: MX[i] + " " + MY, duration: 0.8, ease: "elastic.out(1,0.55)" }, 15.35 + i * 0.1); });')
    # 교집합 원: 먼저 보였다가 깜빡이던 것 수정(처음엔 숨기고, 제 차례에 부풀듯 나타남)
    s = must(s, 'gsap.set("#gA", { x: -200 }); gsap.set("#gB", { x: 200 });', 'gsap.set("#gA", { x: -200, opacity: 0 }); gsap.set("#gB", { x: 200, opacity: 0 });')
    s = must(s, 'tl.fromTo("#gA", { x: -200, opacity: 0 }, { x: -200, opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }, 21.8);',
             'tl.fromTo("#gA", { x: -200, opacity: 0, scale: 0.5, svgOrigin: "820 440" }, { x: -200, opacity: 1, scale: 1, duration: 0.9, ease: "back.out(1.6)", immediateRender: false }, 21.8);')
    s = must(s, 'tl.fromTo("#gB", { x: 200, opacity: 0 }, { x: 200, opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }, 21.95);',
             'tl.fromTo("#gB", { x: 200, opacity: 0, scale: 0.5, svgOrigin: "1100 440" }, { x: 200, opacity: 1, scale: 1, duration: 0.9, ease: "back.out(1.6)", immediateRender: false }, 21.95);')
    return s


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
    s = clay_convai(s)
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
    s = clay_rest(s)
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
