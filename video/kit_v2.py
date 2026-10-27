"""인트로 v2와 같은 시각 언어(가는 선, 게이지 노드, 한글 소제목)를 아웃트로·회사 소개 영상에서 함께 쓰기 위한 공용 부품.

- 노드: 어두운 원 + 둘레 게이지(브랜드 그라데이션). 게이지가 다 차면 띠링과 함께 반짝(크기는 그대로)
- 소제목: 화면 아래 가운데, 작은 태그 + 큰 문장, 줄 마스크로 천천히 올라옴
- 모든 움직임은 GSAP 타임라인 tl 위의 절대 시각
"""
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILM = REPO / "video" / "brand-film"
G = ["#ff03c8", "#e807c3", "#d10bbd", "#ba0fb8", "#a518a4", "#8f1ab8", "#7a1dcc", "#661fdc", "#5422e6", "#4823ee", "#4024f1", "#3c24f3"]
DARK, LIGHT = "#0c0916", "#faf9fd"

FONT_CSS = "".join(f'@font-face {{ font-family: "Pretendard"; font-weight: {w}; src: url("assets/fonts/Pretendard-{n}.otf"); }}\n'
                   for w, n in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")))
CSS = FONT_CSS + """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #0c0916; }
#root { position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: "Pretendard", sans-serif; background: #0c0916; }
.layer { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
.vig { background: radial-gradient(ellipse at 50% 45%, rgba(60,36,243,.10), rgba(0,0,0,0) 55%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.45)); }
.bar { position: absolute; width: 12px; height: 220px; margin-top: -110px; border-radius: 6px; box-shadow: 0 0 14px currentColor; }
.who { position: relative; flex: none; height: 40px; padding: 0 18px; border-radius: 20px; font-size: 20px; font-weight: 700; line-height: 40px; white-space: nowrap; }
.cap { position: absolute; left: 0; top: 760px; width: 1920px; text-align: center; }
.tag { overflow: hidden; font-size: 20px; font-weight: 600; letter-spacing: 0.24em; color: #b5abd8; padding-bottom: 4px; }
.ct { overflow: hidden; margin-top: 16px; font-size: 52px; font-weight: 800; color: #fff; letter-spacing: -0.03em; padding-bottom: 8px; white-space: nowrap; }
.tag span, .ct span.cw { display: inline-block; }
.g { background: linear-gradient(100deg, #ff4fd8, #b25cff 55%, #7a6bff); -webkit-background-clip: text; background-clip: text; color: transparent; }
.mono { font-weight: 600; font-size: 19px; letter-spacing: 0.2em; color: #b5abd8; white-space: nowrap; }
.dlab { font-family: "Pretendard"; font-weight: 600; font-size: 20px; letter-spacing: 3px; fill: #cfc6ec; }
.cwrap { position: absolute; width: 0; display: flex; flex-direction: column; align-items: center; }
.val { font-weight: 700; font-size: 30px; color: #fff; letter-spacing: -0.02em; white-space: nowrap; margin-top: 10px; }
.pill { position: relative; flex: none; height: 64px; padding: 0 30px; border-radius: 32px; font-size: 28px; font-weight: 700; color: #fff; line-height: 60px; white-space: nowrap;
  background: rgba(20,15,42,.9); border: 2px solid rgba(157,121,255,.6); }
"""

SVG_DEFS = """<defs>
  <radialGradient id="nodeg" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#2a1f55"/><stop offset="1" stop-color="#140f2a"/></radialGradient>
  <filter id="gl2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="gl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="dotg"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#ff8be6" stop-opacity=".8"/><stop offset="1" stop-color="#ff4fd8" stop-opacity="0"/></radialGradient>
</defs>"""


def node(nid, x, y, r, text="", size=34, sub=""):
    """게이지 노드. JS의 GAUGE(nid, t, d)로 게이지를 채우고 반짝인다."""
    return (f'<g class="node" id="{nid}"><linearGradient id="{nid}-g" x1="{x - r}" y1="0" x2="{x + r}" y2="0" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#nodeg)" stroke="#fff" stroke-opacity=".25" stroke-width="1.5"/>'
            f'<circle class="ring" id="{nid}-ring" cx="{x}" cy="{y}" r="{r + 10}" fill="none" stroke="url(#{nid}-g)" stroke-width="4" stroke-linecap="round" transform="rotate(-90 {x} {y})" filter="url(#gl2)"/>'
            f'<circle class="fin" id="{nid}-fin" cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="0"/>'
            f'<circle class="fring" id="{nid}-fr" cx="{x}" cy="{y}" r="{r + 10}" fill="none" stroke="#fff" stroke-width="2" opacity="0"/>'
            + (f'<text x="{x}" y="{y + size * 0.35:.0f}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="{size}" fill="#fff">{text}</text>' if text else "")
            + sub + '</g>')


def cap_html(cid, tag, text):
    t = text
    while "[" in t:
        a, b = t.index("["), t.index("]")
        t = t[:a] + f'<span class="g">{t[a + 1:b]}</span>' + t[b + 1:]
    return (f'<div class="cap" id="{cid}"><div class="tag"><span class="{cid}-l">{tag}</span></div>'
            f'<div class="ct"><span class="cw {cid}-l">{t}</span></div></div>')


JS = r"""
const tl = gsap.timeline({ paused: true });
const hsh = (a, b) => { let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
const prep = (el) => { const L = el.getTotalLength(); el.setAttribute("stroke-dasharray", `${L} ${L}`); el.setAttribute("stroke-dashoffset", L); return L; };
const DR = (sel, t, d, e = "power2.inOut", s = 0) => gsap.utils.toArray(sel).forEach((el, i) => {
  const L = prep(el);
  tl.fromTo(el, { attr: { "stroke-dashoffset": L } }, { attr: { "stroke-dashoffset": 0 }, duration: d, ease: e, immediateRender: false }, t + i * s);
});
// 게이지가 d초 동안 차고, 다 차면 반짝(안쪽 흰빛 + 퍼지는 고리 + 게이지 잠깐 굵게)
const GAUGE = (id, t, d = 0.9) => {
  DR("#" + id + "-ring", t, d, "power2.inOut");
  const r = +document.getElementById(id + "-fr").getAttribute("r");
  tl.fromTo("#" + id + "-fin", { opacity: 0 }, { opacity: 0.55, duration: 0.08, ease: "none", immediateRender: false }, t + d);
  tl.to("#" + id + "-fin", { opacity: 0, duration: 0.6, ease: "power2.out" }, t + d + 0.08);
  tl.fromTo("#" + id + "-fr", { opacity: 0.9, attr: { r } }, { opacity: 0, attr: { r: r + 34 }, duration: 0.8, ease: "power2.out", immediateRender: false }, t + d);
  tl.fromTo("#" + id + "-ring", { attr: { "stroke-width": 4 } }, { attr: { "stroke-width": 7 }, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }, t + d);
};
const CAP = (id, a, b) => {
  tl.fromTo("#" + id, { opacity: 1 }, { opacity: 1, duration: 0.01, immediateRender: false }, a);
  tl.fromTo("." + id + "-l", { yPercent: 120 }, { yPercent: 0, duration: 1.0, ease: "expo.out", stagger: 0.08 }, a);
  if (b) tl.to("." + id + "-l", { yPercent: -120, duration: 0.45, ease: "power2.in", stagger: 0.04 }, b);
};
const FIN = (sel, t, d = 0.6, e = "power2.out") => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: d, ease: e, immediateRender: false }, t);
const FOUT = (sel, t, d = 0.5, e = "sine.inOut") => tl.to(sel, { opacity: 0, duration: d, ease: e }, t);
const speak = (sel, t0, t1, seed, step = 0.24) => gsap.utils.toArray(sel).forEach((el, k) => {
  let t = t0, s = 0;
  while (t < t1) { tl.to(el, { scaleY: 0.2 + 0.8 * hsh(k + seed, ++s) * Math.sin(Math.PI * (k + 0.5) / 7), duration: step, ease: "sine.inOut" }, t); t += step; }
});
// 점이 지나간 자리까지만 선이 그려짐(점과 선이 같은 진행값)
const ALONG = (pathSel, dotSel, t, d, e = "power2.inOut", drawLine = true) => {
  const p = document.querySelector(pathSel), L = drawLine ? prep(p) : p.getTotalLength(), q = { v: 0 };
  tl.fromTo(q, { v: 0 }, { v: 1, duration: d, ease: e, immediateRender: false, onUpdate: () => {
    const pt = p.getPointAtLength(q.v * L); gsap.set(dotSel, { x: pt.x, y: pt.y });
    if (drawLine) p.setAttribute("stroke-dashoffset", L * (1 - q.v));
  } }, t);
};
"""


def page(title, body, js, dur, extra_css="", audio=""):
    return f"""<!doctype html>
<html lang="ko" data-resolution="landscape">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>{title}</title>
<script src="assets/gsap.min.js"></script>
<style>{CSS}{extra_css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-fps="60" data-width="1920" data-height="1080">
{body}
{audio}
</div>
<script>
{JS}
{js}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body></html>"""


def setup_project(d: Path, pid, extra=()):
    a = d / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (FILM / "assets" / "fonts").glob("Pretendard-*"):
        shutil.copy(f, a / "fonts" / f.name)
    shutil.copy(FILM / "assets" / "gsap.min.js", a / "gsap.min.js")
    for src, name in extra:
        shutil.copy(src, a / name)
    shutil.copy(FILM / "hyperframes.json", d / "hyperframes.json")
    (d / "meta.json").write_text(json.dumps({"id": pid, "name": pid}))
    return a
