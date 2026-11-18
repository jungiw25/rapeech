"""회사 소개 영상 개선 시안: 첫 장면 8초를 두 가지 그림 방향으로 만든다.
A안 = 밝은 클레이 3D, C안 = 평면 그래픽. 캐릭터 그림은 힉스필드(gpt_image_2_6)로 만든 assets_src/*.png.
사용법: python3 video/brand-film-hf/build.py  → a/index.html, c/index.html (HyperFrames로 렌더)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from kit_v2 import FONT_CSS, setup_project  # noqa: E402

DUR = 8.4
CAPS = [(0.35, "모든 대화는, [목소리]에서 시작합니다"), (2.7, "고객이 [전화]를 걸면"), (5.3, "AI 콜봇이 목소리를 듣고 [글로 옮기고]")]
SAY = "카드를 잃어버렸어요"


def crop(src, dst):
    im = Image.open(src).convert("RGBA")
    a = np.asarray(im)[..., 3] > 24
    ys, xs = np.where(a)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst)
    return (xs.max() + 1 - xs.min()) / (ys.max() + 1 - ys.min())


def grain(dst, amp):
    r = np.random.default_rng(3)
    n = np.clip(255 - np.abs(r.normal(0, amp, (540, 960))), 0, 255).astype(np.uint8)
    Image.fromarray(n, "L").convert("RGB").save(dst)


def caps(cls_hl):
    out = []
    for i, (_, t) in enumerate(CAPS):
        a, rest = t.split("[")
        h, b = rest.split("]")
        ws = [(x, "") for x in a.split()] + [(h, cls_hl)] + [(x, "") for x in b.split()]
        k = len(a.split())
        glue = set()                      # 왼쪽 낱말에 붙는 낱말의 번호
        if a and not a.endswith(" "): glue.add(k)
        if b and not b.startswith(" "): glue.add(k + 1)
        sp = lambda j, x, c: f'<span class="w {c}{" gl" if j in glue else ""}{" gr" if j + 1 in glue else ""}">{"<b class=blk></b>" if c else ""}<i>{x}</i></span>'
        out.append(f'<div class="cap" id="cap{i}">' + "".join(sp(j, x, c) for j, (x, c) in enumerate(ws)) + "</div>")
    return "\n".join(out)


def typed():
    return "".join(f'<span class="ch">{c if c != " " else "&nbsp;"}</span>' for c in f"“{SAY}”")


PAGE = """<!doctype html>
<html lang="ko" data-resolution="landscape">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>{title}</title>
<script src="assets/gsap.min.js"></script>
<style>{font}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; }}
#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: "Pretendard", sans-serif; }}
.abs {{ position: absolute; }}
.cap {{ position: absolute; left: 0; width: 1920px; text-align: center; white-space: nowrap; }}
.w {{ position: relative; display: inline-block; overflow: hidden; vertical-align: top; margin: 0 .12em; }}
.w i {{ position: relative; display: inline-block; font-style: normal; }}
.blk {{ position: absolute; display: none; }}
.w.gl {{ margin-left: 0 !important; }} .w.gr {{ margin-right: 0 !important; }}
.ch {{ display: inline-block; }}
#grain {{ position: absolute; left: -60px; top: -60px; width: 2040px; height: 1200px; background: url(assets/grain.png); background-size: 960px 540px; mix-blend-mode: multiply; pointer-events: none; }}
{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-fps="60" data-width="1920" data-height="1080">
{body}
<div id="grain"></div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const CAPT = {capt};
{js}
tl.to({{}}, {{ duration: 0.01 }}, {dur} - 0.01);
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body></html>"""

# ───────────────────────── A안: 밝은 클레이 3D ─────────────────────────
A_H, A_L, A_B, A_Y = 400, 110, 720, 528          # 캐릭터 높이·왼쪽·바닥, 관 높이
A_N = (1010, 1750)


def build_a(ar):
    w = A_H * ar
    top = A_B - A_H
    x0 = A_L + w - 26
    css = f"""
#root {{ background: #F6F4F0; }}
#floor {{ left: 0; top: 0; width: 1920px; height: 1080px; background: radial-gradient(ellipse 1300px 520px at 46% 60%, #fffdf9 0%, rgba(255,253,249,0) 70%), linear-gradient(#f6f4f0 55%, #ece8e1); }}
#grain {{ opacity: .22; }}
.cap {{ top: 118px; font-size: 84px; font-weight: 900; letter-spacing: -0.035em; color: #1B1B1F; line-height: 1.25; }}
.hl i {{ color: #6A3DE8; }}
.sh {{ border-radius: 50%; background: rgba(60,40,110,.28); filter: blur(16px); }}
#tube {{ left: {x0}px; top: {A_Y - 13}px; width: {1960 - x0}px; height: 26px; border-radius: 13px; transform-origin: 0 50%;
  background: linear-gradient(#9373f6 0%, #6f45ea 38%, #5a31d4 78%, #4b27b8 100%); box-shadow: 0 22px 20px -8px rgba(70,45,130,.30), inset 0 -3px 4px rgba(40,15,110,.35); }}
.nd {{ width: 92px; height: 92px; margin: -46px 0 0 -46px; border-radius: 50%; }}
.nd .off, .nd .on {{ position: absolute; inset: 0; border-radius: 50%; }}
.nd .off {{ background: radial-gradient(circle at 36% 30%, #f1eaff 0%, #cdbcfb 42%, #a98ff0 100%); box-shadow: 0 24px 22px -10px rgba(70,45,130,.38), inset 0 -6px 10px rgba(90,50,200,.25); }}
.nd .on {{ background: radial-gradient(circle at 36% 30%, #b79cff 0%, #6f45ea 46%, #4a25bd 100%); box-shadow: 0 24px 22px -10px rgba(70,45,130,.45), inset 0 -6px 10px rgba(30,10,100,.4); }}
.nd .core {{ position: absolute; left: 31px; top: 31px; width: 30px; height: 30px; border-radius: 50%; background: radial-gradient(circle at 38% 32%, #ffd0c4, #ff7a62 55%, #e85a45); box-shadow: inset 0 -3px 4px rgba(150,30,20,.3); }}
#pulse {{ width: 40px; height: 40px; margin: -20px 0 0 -20px; border-radius: 50%; background: radial-gradient(circle at 38% 32%, #ffd0c4, #ff7a62 55%, #e85a45); box-shadow: 0 16px 14px -6px rgba(120,40,40,.35); }}
.ray {{ width: 26px; height: 9px; margin: -4px 0 0 0; border-radius: 5px; background: #ff6b55; transform-origin: 0 50%; }}
#bub {{ left: {A_L + 30}px; top: {top - 104}px; height: 76px; padding: 0 34px; border-radius: 38px; background: #fff; font-size: 32px; font-weight: 700; line-height: 76px; color: #1B1B1F; letter-spacing: -0.02em; white-space: nowrap;
  box-shadow: 0 18px 26px -10px rgba(70,45,130,.28), 0 2px 0 rgba(255,255,255,.9) inset; transform-origin: 22% 100%; }}
#bub:after {{ content: ""; position: absolute; left: 86px; bottom: -13px; width: 30px; height: 30px; background: #fff; border-radius: 6px; transform: rotate(45deg); }}
#card {{ left: {A_N[0] - 250}px; top: {A_Y + 96}px; width: 500px; padding: 26px 30px 30px; border-radius: 30px; background: #fff; box-shadow: 0 26px 34px -14px rgba(70,45,130,.30); text-align: center; transform-origin: 50% 0; }}
#card .lb {{ display: inline-block; height: 38px; padding: 0 18px; border-radius: 19px; background: #ece5ff; color: #5a31d4; font-size: 21px; font-weight: 700; line-height: 38px; letter-spacing: .02em; }}
#card .tx {{ margin-top: 14px; font-size: 36px; font-weight: 800; color: #1B1B1F; letter-spacing: -0.03em; white-space: nowrap; }}
"""
    body = f"""<div id="floor" class="abs"></div>
{caps("hl")}
<div id="tubeW" class="abs" style="left:0;top:0;width:1920px;height:1080px"><div id="tube" class="abs"></div></div>
{"".join(f'<div class="abs sh" id="ns{i}" style="left:{x - 50}px;top:{A_Y + 44}px;width:100px;height:22px"></div><div class="abs nd" id="n{i}" style="left:{x}px;top:{A_Y}px"><div class="off"></div><div class="on"></div><div class="core"></div></div>' for i, x in enumerate(A_N))}
<div id="pulse" class="abs" style="left:{x0 + 30}px;top:{A_Y}px"></div>
<div class="abs sh" id="csh" style="left:{A_L + 10}px;top:{A_B - 26}px;width:{w - 30}px;height:44px"></div>
<div id="who" class="abs" style="left:{A_L}px;top:{top}px;width:{w}px;height:{A_H}px;transform-origin:42% 100%"><img src="assets/customer.png" style="width:100%;height:100%"/>
  {"".join(f'<div class="abs ray" id="r{k}" style="left:{w * 0.675}px;top:{A_H * 0.415}px;transform:rotate({a}deg) translateX(8px)"></div>' for k, a in enumerate((-32, 0, 32)))}
  <svg class="abs" id="wav" style="left:{w * 0.93}px;top:{A_H * 0.06}px;overflow:visible" width="110" height="110" viewBox="0 0 110 110" fill="none" stroke="#6A3DE8" stroke-width="11" stroke-linecap="round">
    <path class="wv" d="M0 76 A24 24 0 0 1 24 100"/><path class="wv" d="M0 50 A50 50 0 0 1 50 100"/><path class="wv" d="M0 24 A76 76 0 0 1 76 100"/></svg>
</div>
<div id="bub" class="abs">{SAY}</div>
<div id="card" class="abs"><span class="lb">음성 인식</span><div class="tx">{typed()}</div></div>"""
    js = f"""
const X0 = {x0 + 30}, N = {list(A_N)};
gsap.set(["#who", "#csh", "#bub", "#card", "#pulse", ".nd", ".sh", ".ray", ".wv", ".ch"], {{ opacity: 0 }});
gsap.set(".nd .on, .nd .core", {{ opacity: 0 }});
gsap.set("#tube", {{ scaleX: 0 }});
CAPT.forEach((t, i) => {{
  const q = "#cap" + i + " i";
  gsap.set(q, {{ yPercent: 110 }});
  tl.to(q, {{ yPercent: 0, duration: 0.7, ease: "expo.out", stagger: 0.06 }}, t);
  if (i < CAPT.length - 1) tl.to(q, {{ yPercent: -110, duration: 0.4, ease: "power3.in", stagger: 0.03 }}, CAPT[i + 1] - 0.5);
}});
// 캐릭터: 위에서 툭 내려앉고 눌렸다가 돌아옴
tl.fromTo("#who", {{ y: -240, scaleX: 0.92, scaleY: 1.1, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.42, ease: "power2.in", immediateRender: false }}, 0.3)
  .to("#who", {{ scaleX: 1.1, scaleY: 0.86, duration: 0.1, ease: "power2.out" }}, 0.72)
  .to("#who", {{ scaleX: 1, scaleY: 1, duration: 0.7, ease: "elastic.out(1,0.45)" }}, 0.82)
  .fromTo("#csh", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.42, ease: "power2.in", immediateRender: false }}, 0.3);
// 관이 굴러 나오고, 지나간 자리에서 단추가 튀어 오름
tl.to("#tube", {{ scaleX: 1, duration: 1.25, ease: "power3.inOut" }}, 0.95);
N.forEach((x, i) => {{
  const t = 1.35 + i * 0.42;
  tl.fromTo("#n" + i, {{ opacity: 0, scale: 0, y: 30 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.75, ease: "elastic.out(1,0.5)", immediateRender: false }}, t)
    .fromTo("#ns" + i, {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "power2.out", immediateRender: false }}, t);
}});
// 숨 쉬듯 살짝
tl.to("#who", {{ scaleY: 1.018, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: 5 }}, 1.6);
// 전화: 캐릭터가 몸을 기울이고 전파가 번짐
tl.to("#who", {{ rotation: 4, duration: 0.35, ease: "back.out(2)" }}, 2.75).to("#who", {{ rotation: 0, duration: 0.9, ease: "elastic.out(1,0.4)" }}, 3.1);
[0, 1, 2].forEach(k => {{
  [2.85, 3.75].forEach(t0 => {{
    tl.fromTo(".wv:nth-child(" + (k + 1) + ")", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, immediateRender: false }}, t0 + k * 0.12)
      .to(".wv:nth-child(" + (k + 1) + ")", {{ opacity: 0, duration: 0.3 }}, t0 + 0.5 + k * 0.12);
  }});
}});
// 말하기: 말풍선이 튀어나오고 입 앞의 선이 깜빡
tl.fromTo("#bub", {{ opacity: 0, scale: 0.3, y: 30, rotation: -8 }}, {{ opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.7, ease: "elastic.out(1,0.55)", immediateRender: false }}, 4.0);
for (let j = 0; j < 4; j++) {{
  tl.fromTo(".ray", {{ opacity: 0, scaleX: 0.2 }}, {{ opacity: 1, scaleX: 1, duration: 0.12, stagger: 0.03, immediateRender: false }}, 4.0 + j * 0.32)
    .to(".ray", {{ opacity: 0, scaleX: 1.3, duration: 0.14 }}, 4.16 + j * 0.32);
  tl.to("#who", {{ y: -8, duration: 0.1, yoyo: true, repeat: 1, ease: "sine.inOut" }}, 4.0 + j * 0.32);
}}
// 목소리가 구슬이 되어 관 위를 굴러감 → 첫 단추에 닿으면 색이 바뀜
tl.fromTo("#pulse", {{ opacity: 0, scale: 0, x: 0, y: 0 }}, {{ opacity: 1, scale: 1, y: -30, duration: 0.3, ease: "back.out(2.5)", immediateRender: false }}, 5.25)
  .to("#pulse", {{ x: N[0] - X0, duration: 0.85, ease: "power2.inOut" }}, 5.5)
  .to("#pulse", {{ y: -64, duration: 0.36, ease: "power2.out" }}, 5.56).to("#pulse", {{ y: -30, duration: 0.43, ease: "power2.in" }}, 5.92)
  .to("#pulse", {{ scale: 0.3, opacity: 0, y: 0, duration: 0.12 }}, 6.35)
  .to("#n0", {{ scaleY: 0.72, scaleX: 1.2, duration: 0.09, ease: "power2.out" }}, 6.35)
  .to("#n0", {{ scaleY: 1, scaleX: 1, duration: 0.8, ease: "elastic.out(1,0.4)" }}, 6.44)
  .to("#n0 .on", {{ opacity: 1, duration: 0.15 }}, 6.38)
  .fromTo("#n0 .core", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(3)", immediateRender: false }}, 6.45)
  .to("#bub", {{ opacity: 0.45, duration: 0.4 }}, 6.4);
// 글자 카드
tl.fromTo("#card", {{ opacity: 0, scale: 0.6, y: -40 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.65, ease: "elastic.out(1,0.6)", immediateRender: false }}, 6.5)
  .to(".ch", {{ opacity: 1, duration: 0.04, stagger: 0.055 }}, 6.85);
"""
    return PAGE.format(title="A안", font=FONT_CSS, css=css, body=body, js=js, dur=DUR, capt=[c[0] for c in CAPS])


# ───────────────────────── C안: 평면 그래픽 ─────────────────────────
C_H, C_L, C_Y = 620, 60, 706
C_N = (1130, 1790)
INK, PUR, CRM, COR, BG = "#1E1640", "#5B35E0", "#FFF0CF", "#F2634B", "#EDE7FB"


def build_c(ar):
    w = C_H * ar
    top = 1080 - C_H
    x0 = C_L + w - 14
    css = f"""
#root {{ background: {BG}; }}
#grain {{ opacity: .55; }}
.cap {{ top: 96px; font-size: 128px; font-weight: 900; letter-spacing: -0.05em; color: {INK}; line-height: 1.22; }}
.w {{ margin: 0 .09em; }}
.hl {{ padding: 0 .12em; }}
.hl .blk {{ display: block; left: 0; top: .08em; width: 100%; height: 1.06em; background: {PUR}; transform-origin: 0 50%; }}
.hl i {{ color: {CRM}; }}
#poly1 {{ left: 0; top: 0; width: 1920px; height: 1080px; background: {COR}; clip-path: polygon(52% 100%, 100% 86%, 100% 100%); }}
#poly2 {{ left: 0; top: 0; width: 1920px; height: 1080px; background: {INK}; clip-path: polygon(0 88%, 62% 100%, 0 100%); }}
#lineS, #line {{ left: {x0}px; width: {1940 - x0}px; height: 28px; transform-origin: 0 50%; }}
#line {{ top: {C_Y - 14}px; background: {PUR}; }}
#lineS {{ top: {C_Y - 4}px; background: {COR}; }}
.nd {{ width: 128px; height: 128px; margin: -64px 0 0 -64px; }}
.nd div {{ position: absolute; border-radius: 50%; }}
.nd .s {{ inset: 0; background: {COR}; transform: translate(9px, 9px); }}
.nd .o {{ inset: 0; background: {PUR}; }}
.nd .r {{ inset: 26px; background: {CRM}; }}
.nd .c {{ inset: 46px; background: {COR}; }}
#pulse {{ width: 54px; height: 54px; margin: -27px 0 0 -27px; border-radius: 50%; background: {CRM}; border: 10px solid {COR}; }}
#bub {{ left: {C_L + 40}px; top: {top - 112}px; height: 92px; padding: 0 36px; background: {CRM}; font-size: 40px; font-weight: 800; line-height: 92px; color: {INK}; letter-spacing: -0.03em; white-space: nowrap; box-shadow: 10px 10px 0 {COR}; transform-origin: 30% 100%; }}
#bub:after {{ content: ""; position: absolute; left: 120px; bottom: -34px; border: 18px solid transparent; border-top-color: {CRM}; border-left-color: {CRM}; }}
#card {{ left: {C_N[0] - 280}px; top: {C_Y + 100}px; width: 560px; background: {CRM}; box-shadow: 12px 12px 0 {INK}; transform-origin: 0 0; }}
#card .lb {{ height: 50px; padding: 0 24px; background: {INK}; color: {CRM}; font-size: 24px; font-weight: 800; line-height: 50px; letter-spacing: .08em; }}
#card .tx {{ padding: 22px 24px 28px; font-size: 42px; font-weight: 900; color: {INK}; letter-spacing: -0.04em; white-space: nowrap; }}
.arc {{ fill: none; stroke: {COR}; stroke-width: 16; }}
.tri {{ width: 0; height: 0; border: 15px solid transparent; border-left: 34px solid {COR}; margin-top: -15px; transform-origin: 0 50%; }}
"""
    body = f"""<div id="poly1" class="abs"></div><div id="poly2" class="abs"></div>
{caps("hl")}
<div id="lineS" class="abs"></div><div id="line" class="abs"></div>
{"".join(f'<div class="abs nd" id="n{i}" style="left:{x}px;top:{C_Y}px"><div class="s"></div><div class="o"></div><div class="r"></div><div class="c"></div></div>' for i, x in enumerate(C_N))}
<div id="pulse" class="abs" style="left:{x0 + 20}px;top:{C_Y}px"></div>
<div id="whoM" class="abs" style="left:{C_L}px;top:{top}px;width:{w + 200}px;height:{C_H}px;overflow:hidden">
 <div id="who" class="abs" style="left:0;top:0;width:{w}px;height:{C_H}px;transform-origin:40% 100%"><img src="assets/customer.png" style="width:100%;height:100%"/></div>
</div>
<svg class="abs" id="wav" style="left:{C_L + w * 0.9}px;top:{top + C_H * 0.02}px;overflow:visible" width="160" height="160" viewBox="0 0 160 160">
  <path class="arc" d="M0 110 A30 30 0 0 1 30 140"/><path class="arc" d="M0 76 A64 64 0 0 1 64 140"/><path class="arc" d="M0 42 A98 98 0 0 1 98 140"/></svg>
<div id="bub" class="abs">{SAY}</div>
<div id="card" class="abs"><div class="lb">음성 인식</div><div class="tx">{typed()}</div></div>"""
    js = f"""
const X0 = {x0 + 20}, N = {list(C_N)};
const SNAP = "expo.out";
gsap.set(["#bub", "#card", "#pulse", ".nd", ".arc", ".ch"], {{ opacity: 0 }});
gsap.set(".nd .r, .nd .c", {{ scale: 0 }});
gsap.set(["#line", "#lineS"], {{ scaleX: 0 }});
gsap.set("#who", {{ yPercent: 105 }});
gsap.set("#poly1", {{ xPercent: 60 }}); gsap.set("#poly2", {{ xPercent: -70 }});
// 종이 질감이 12fps로 살짝 떨림(인쇄물 느낌)
for (let t = 0, k = 0; t < {DUR}; t += 1 / 12, k++) tl.set("#grain", {{ x: (k * 37) % 50, y: (k * 53) % 50 }}, t);
CAPT.forEach((t, i) => {{
  const q = "#cap" + i + " i", b = "#cap" + i + " .blk";
  gsap.set(q, {{ yPercent: 110 }}); gsap.set(b, {{ scaleX: 0 }});
  tl.to(b, {{ scaleX: 1, duration: 0.45, ease: "expo.inOut" }}, t + 0.1)
    .to(q, {{ yPercent: 0, duration: 0.55, ease: SNAP, stagger: 0.07 }}, t);
  if (i < CAPT.length - 1) tl.to(q, {{ yPercent: -110, duration: 0.32, ease: "expo.in", stagger: 0.03 }}, CAPT[i + 1] - 0.48)
    .to(b, {{ scaleX: 0, transformOrigin: "100% 50%", duration: 0.3, ease: "expo.in" }}, CAPT[i + 1] - 0.4);
}});
// 바닥 도형이 미끄러져 들어오고, 캐릭터가 아래에서 솟음
tl.to("#poly2", {{ xPercent: 0, duration: 0.8, ease: SNAP }}, 0.15).to("#poly1", {{ xPercent: 0, duration: 0.9, ease: SNAP }}, 0.3)
  .to("#who", {{ yPercent: 0, duration: 0.7, ease: "back.out(1.5)" }}, 0.4);
// 선: 주황 그림자가 한 박자 늦게 따라옴(판화 어긋남)
tl.to("#line", {{ scaleX: 1, duration: 0.9, ease: "expo.inOut" }}, 0.95).to("#lineS", {{ scaleX: 1, duration: 0.9, ease: "expo.inOut" }}, 1.05);
N.forEach((x, i) => {{
  const t = 1.4 + i * 0.3;
  tl.fromTo("#n" + i, {{ opacity: 1, scale: 0, rotation: -90 }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "back.out(2.4)", immediateRender: false }}, t);
}});
tl.to("#who", {{ rotation: 1.2, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: 5 }}, 1.4);
// 전화: 전파 세 줄이 딱딱 끊어서 켜짐
[2.85, 3.6].forEach(t0 => [0, 1, 2].forEach(k => {{
  tl.set(".arc:nth-child(" + (k + 1) + ")", {{ opacity: 1 }}, t0 + k * 0.1).set(".arc:nth-child(" + (k + 1) + ")", {{ opacity: 0 }}, t0 + 0.45 + k * 0.06);
}}));
tl.to("#who", {{ y: -18, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1 }}, 2.8);
// 말풍선
tl.fromTo("#bub", {{ opacity: 1, scaleX: 0, scaleY: 0.6, rotation: -6 }}, {{ scaleX: 1, scaleY: 1, rotation: 0, duration: 0.5, ease: "back.out(2)", immediateRender: false }}, 4.0);
for (let j = 0; j < 3; j++) tl.to("#who", {{ y: -10, duration: 0.09, yoyo: true, repeat: 1, ease: "power1.out" }}, 4.05 + j * 0.3);
// 목소리 → 선을 따라 이동 → 첫 원이 열림
tl.fromTo("#pulse", {{ opacity: 1, scale: 0, x: 0 }}, {{ scale: 1, duration: 0.25, ease: "back.out(3)", immediateRender: false }}, 5.3)
  .to("#pulse", {{ x: N[0] - X0, duration: 0.8, ease: "expo.inOut" }}, 5.5)
  .to("#pulse", {{ scaleX: 1.9, scaleY: 0.7, duration: 0.4, ease: "power2.in", yoyo: true, repeat: 1 }}, 5.5)
  .set("#pulse", {{ opacity: 0 }}, 6.3)
  .to("#n0", {{ scale: 1.25, duration: 0.1, ease: "power2.out" }}, 6.3).to("#n0", {{ scale: 1, duration: 0.5, ease: "back.out(3)" }}, 6.4)
  .to("#n0 .r", {{ scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, 6.32).to("#n0 .c", {{ scale: 1, duration: 0.4, ease: "back.out(3)" }}, 6.42)
  .to("#bub", {{ scaleX: 0, duration: 0.3, ease: "expo.in" }}, 6.2);
// 글자 카드: 왼쪽 위에서 펼쳐지고 글자가 한 자씩 찍힘
tl.fromTo("#card", {{ opacity: 1, scaleX: 0, scaleY: 0 }}, {{ scaleX: 1, scaleY: 1, duration: 0.5, ease: SNAP, immediateRender: false }}, 6.5)
  .set(".ch", {{ opacity: 1, stagger: 0.06 }}, 6.85);
"""
    return PAGE.format(title="C안", font=FONT_CSS, css=css, body=body, js=js, dur=DUR, capt=[c[0] for c in CAPS])


if __name__ == "__main__":
    for k, fn, amp in (("a", build_a, 10), ("c", build_c, 22)):
        d = HERE / k
        a = setup_project(d, f"hf-{k}")
        ar = crop(HERE / f"assets_src/{k}_customer.png", a / "customer.png")
        grain(a / "grain.png", amp)
        (d / "index.html").write_text(fn(ar))
        print(d / "index.html")
