"""브랜드 필름 리뉴얼 시안 C·D·E (A·B와 같은 이야기·타이밍·소리, 22초).

C 페이퍼   : 08 페이퍼 컷아웃 + 03 클레이모피즘. 밝은 종이 층, 팝업 카드, 말랑한 착지
D 바우하우스: 12 바우하우스 + 06 키네틱 타이포. 격자 위 평면 도형, 빛 효과 없음
E 하프톤   : 04 하프톤 + 09 인피니트 줌. 망점으로 찍은 장면, 노드 속으로 들어가는 한 번의 줌
사용법: python3 video/samples/build_samples2.py → video/samples/{c,d,e}/index.html
"""
import json
import shutil

from build_samples import ARR, DEP, HERE, STEPS, page, project, texts, TEXT_JS

VALS = json.dumps([s[2] for s in STEPS], ensure_ascii=False)
LABS = ["전산 설계", "통합배선", "네트워크", "출입보안", "통합관제", "유지보수"]


def common_js(extra):
    return (f"const ARR = {json.dumps(ARR)}, DEP = {json.dumps(DEP)}, VALS = {VALS};\n"
            + "const cl = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v)); const seg = (t, a, b) => cl((t - a) / (b - a));\n"
            + "const io = (x) => x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; const io3 = (x) => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;\n"
            + "const lerp = (a, b, u) => a + (b - a) * u;\n" + TEXT_JS + extra)


# ─────────────────────────────────────────────── C 페이퍼
def build_c():
    css = """
html, body, #root { background: #f3eff8; }
.hl { color: #1b1530; }
.g { background: linear-gradient(100deg, #e0119d, #8a3cf0 60%, #4a32f0); -webkit-background-clip: text; background-clip: text; color: transparent; }
.mono { color: #5d5480; }
.c-cw { position: absolute; perspective: 1400px; }
.c-card { width: 360px; height: 190px; padding: 30px 32px; border-radius: 22px; background: #fff;
  box-shadow: 0 1px 0 rgba(255,255,255,.9) inset, 0 14px 26px rgba(70,40,140,.14), 0 3px 6px rgba(70,40,140,.10); }
.c-ico { position: absolute; right: 26px; top: 26px; width: 30px; height: 30px; border-radius: 50%; }
.c-fw { position: absolute; left: 1040px; width: 520px; height: 74px; perspective: 1600px; }
.c-fl { position: absolute; inset: 0; border-radius: 16px; display: flex; align-items: center; gap: 12px; padding: 0 28px;
  box-shadow: 0 10px 20px rgba(70,40,140,.13), 0 2px 4px rgba(70,40,140,.10); }
.c-led { width: 12px; height: 12px; border-radius: 50%; box-shadow: inset 0 -2px 2px rgba(0,0,0,.12); }
.c-slot { flex: 1; height: 10px; border-radius: 5px; background: rgba(60,40,120,.08); margin-left: 10px; }
.c-flab { position: absolute; left: 1588px; font-size: 21px; font-weight: 700; color: #4a4170; white-space: nowrap; }
.c-glab { position: absolute; left: 1588px; font-size: 26px; font-weight: 800; color: #1b1530; white-space: nowrap; }
"""
    cols = ["#ff5cd6", "#9d6bff", "#5a5cff"]
    cards = "".join(
        f'<div class="c-cw" style="left:{160 + i * 420}px;top:520px"><div class="c-card" id="c-card{i}">'
        f'<div class="c-ico" style="background:{cols[min(i, 2)] if i < 3 else "#ff5cd6"}"></div>'
        f'<div class="mono" style="position:relative;font-size:18px">{n}  {lab}</div>'
        f'<div class="val" id="c-v{i}" style="position:relative;margin-top:22px;font-size:34px;color:#1b1530"></div></div></div>'
        for i, (n, lab, _) in enumerate(STEPS))
    floors = ""
    for f in range(6):
        top = 900 - (f + 1) * 82
        leds = "".join(f'<span class="c-led" style="background:{cols[(f + j) % 3] if (f * 5 + j * 3) % 4 else "#e4dcf7"}"></span>' for j in range(7))
        floors += (f'<div class="c-fw" style="top:{top}px"><div class="c-fl" id="c-fl{f}" style="background:{"#ffffff" if f % 2 == 0 else "#f1ebfc"}">{leds}<span class="c-slot"></span></div></div>'
                   f'<div class="c-flab" id="c-lb{f}" style="top:{top + 22}px">{LABS[f]}</div>')
    body = f'''<canvas id="paper" class="layer" width="1920" height="1080"></canvas>
<svg id="c-waves" class="layer" viewBox="0 0 1920 1080"><defs><filter id="c-sh" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="-6" stdDeviation="9" flood-color="#46288c" flood-opacity=".16"/></filter></defs>
{"".join(f'<path id="c-w{i}" fill="{c}" filter="url(#c-sh)"/>' for i, c in enumerate(["#c9b8f4", "#dccff8", "#ff8de3", "#ebe3fb", "#ffffff"]))}</svg>
<div class="layer" id="c-s2">
  <div id="c-strip" style="position:absolute;left:160px;top:786px;height:12px;width:0;border-radius:6px;background:#e2d6fa;box-shadow:0 4px 8px rgba(70,40,140,.12)"></div>
  <div id="c-disc" style="position:absolute;left:0;top:774px;width:36px;height:36px;margin-left:-18px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffb3ee,#ff4fd8 60%,#d81fb0);box-shadow:0 8px 14px rgba(200,20,160,.28)"></div>
  {cards}
</div>
<div class="layer" id="c-bld">{floors}
  <div class="c-glab" id="c-gai" style="top:470px">AI · 대화</div><div class="c-glab" id="c-gni" style="top:760px">NI · 인프라</div>
  <div id="c-drop" style="position:absolute;left:1300px;top:0;width:64px;height:64px;margin-left:-32px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffc2f1,#ff4fd8 58%,#cc1aa6);box-shadow:0 12px 20px rgba(200,20,160,.3)"></div>
</div>
{texts()}'''
    js = common_js("""
const SX = [340, 760, 1180, 1600];
// ── 2. 종이 원반이 지나간 자리까지만 종이 띠가 깔림, 도착하면 카드가 팝업북처럼 일어섬
gsap.set("#c-disc", { x: 160, opacity: 0 });
tl.fromTo("#c-disc", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(2)", immediateRender: false }, 3.9);
gsap.set(".c-card", { rotationX: -96, transformOrigin: "50% 100%", opacity: 0 });
for (let i = 0; i < 4; i++) {
  const d = ARR[i] - DEP[i];
  tl.to("#c-disc", { x: SX[i], duration: d, ease: "power2.inOut" }, DEP[i]);
  tl.to("#c-strip", { width: SX[i] - 160, duration: d, ease: "power2.inOut" }, DEP[i]);
  tl.to("#c-disc", { scaleY: 0.8, scaleX: 1.18, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1 }, ARR[i] - 0.05);
  tl.fromTo("#c-card" + i, { rotationX: -96, opacity: 0 }, { rotationX: 0, opacity: 1, duration: 1.0, ease: "back.out(1.5)", immediateRender: false }, ARR[i] - 0.15);
  SCRAMBLE(document.getElementById("c-v" + i), VALS[i], ARR[i] + 0.3, 0.8);
}
tl.to(".c-card", { rotationX: -96, opacity: 0, duration: 0.6, ease: "power2.in", stagger: 0.06 }, 11.95);
tl.to(["#c-strip", "#c-disc"], { opacity: 0, duration: 0.5 }, 12.1);
// ── 3. 종이 층이 아래부터 하나씩 일어서며 건물이 됨
gsap.set(".c-fl", { rotationX: 96, transformOrigin: "50% 100%", opacity: 0 });
gsap.set([".c-flab", "#c-gai", "#c-gni", "#c-drop"], { opacity: 0 });
for (let f = 0; f < 6; f++) {
  const t = 13.0 + f * 0.36;
  tl.fromTo("#c-fl" + f, { rotationX: 96, opacity: 0 }, { rotationX: 0, opacity: 1, duration: 0.95, ease: "back.out(1.6)", immediateRender: false }, t);
  tl.fromTo("#c-lb" + f, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, t + 0.3);
}
// ── 4. 위 세 층은 AI(분홍 종이), 아래 세 층은 인프라로 나뉘고, 목소리 원반이 말랑하게 내려앉음
tl.to(".c-flab", { opacity: 0, duration: 0.4 }, 16.6);
[3, 4, 5].forEach((f, j) => { tl.to("#c-fl" + f, { backgroundColor: ["#ffe3f6", "#ffd3f1", "#ffc2ec"][j], duration: 0.8, ease: "sine.inOut" }, 17.0); tl.to("#c-fl" + f, { y: -30, duration: 0.9, ease: "power3.inOut" }, 17.0); });
[0, 1, 2].forEach((f, j) => tl.to("#c-fl" + f, { backgroundColor: ["#dcd0fa", "#e6dcfb", "#efe8fd"][j], duration: 0.8, ease: "sine.inOut" }, 17.0));
tl.fromTo("#c-gai", { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 18.1);
tl.fromTo("#c-gni", { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 18.25);
tl.fromTo("#c-drop", { y: -120, opacity: 1 }, { y: 312, opacity: 1, duration: 0.75, ease: "power2.in", immediateRender: false }, 18.2);
tl.fromTo("#c-drop", { scaleX: 1, scaleY: 1 }, { scaleX: 1.3, scaleY: 0.7, transformOrigin: "50% 100%", duration: 0.12, ease: "power2.out", immediateRender: false }, 18.95);
tl.to("#c-drop", { scaleX: 1, scaleY: 1, duration: 0.9, ease: "elastic.out(1, 0.35)" }, 19.07);
tl.to("#c-drop", { y: 300, duration: 0.5, ease: "power2.out", yoyo: true, repeat: 1 }, 19.07);

// ── 배경: 종이 결(한 번만 그림) + 1장면의 종이 물결(시간 t로만 결정)
const pc = document.getElementById("paper").getContext("2d");
pc.fillStyle = "#f3eff8"; pc.fillRect(0, 0, 1920, 1080);
const nz = pc.createImageData(1920, 1080);
for (let i = 0; i < nz.data.length; i += 4) { const v = 120 + Math.floor(hsh(i >> 2, 99) * 135); nz.data[i] = nz.data[i + 1] = nz.data[i + 2] = v; nz.data[i + 3] = 10; }
const tmpc = document.createElement("canvas"); tmpc.width = 1920; tmpc.height = 1080; tmpc.getContext("2d").putImageData(nz, 0, 0);
pc.drawImage(tmpc, 0, 0);
const WB = [690, 745, 800, 850, 905], WA = [46, 40, 30, 36, 28], WK = [0.0042, 0.0051, 0.0068, 0.0047, 0.0058], WW = [0.9, -1.1, 1.6, -0.8, 1.2];
function drawWaves(t) {
  for (let L = 0; L < 5; L++) {
    const rise = (1 - io3(seg(t, 0.15 + L * 0.12, 1.45 + L * 0.12))) * 480 + io3(seg(t, 3.6 + (4 - L) * 0.06, 4.6 + (4 - L) * 0.06)) * 520;
    const env = 0.75 + 0.25 * Math.sin(t * 1.3 + L);
    let d = `M-40 1120 L-40 ${WB[L] + rise}`;
    for (let x = -40; x <= 1960; x += 40) d += ` L${x} ${(WB[L] + rise + WA[L] * env * Math.sin(x * WK[L] + t * WW[L] + L * 1.7)).toFixed(1)}`;
    d += " L1960 1120 Z";
    document.getElementById("c-w" + L).setAttribute("d", d);
  }
}
window.addEventListener("hf-seek", (e) => drawWaves(e.detail.time));
drawWaves(0);
""")
    return page("Rapeech 시안 C", css, body, js)


# ─────────────────────────────────────────────── D 바우하우스
def build_d():
    K, P, B, V = "#14111f", "#ff03c8", "#3c24f3", "#a518a4"
    css = """
html, body, #root { background: #f2eee6; }
.hl { color: #14111f; }
.g { background: none; -webkit-background-clip: initial; background-clip: initial; color: #e0119d; }
.mono { color: #5d566f; }
"""
    grid = "".join(f'<line x1="{160 + i * 1600 / 12:.1f}" y1="0" x2="{160 + i * 1600 / 12:.1f}" y2="1080" stroke="{K}" stroke-opacity=".07" stroke-width="1"/>' for i in range(13))
    grid += "".join(f'<line x1="0" y1="{y}" x2="1920" y2="{y}" stroke="{K}" stroke-opacity=".07" stroke-width="1"/>' for y in (120, 480, 900))
    bars1 = "".join(f'<rect class="d-b1" x="{1000 + j * 44}" y="{880 - h}" width="26" height="{h}" fill="{K}"/>' for j, h in enumerate([90, 160, 240, 130, 300, 200, 110, 180, 70]))
    s1 = (f'<g id="d-s1"><circle id="d-c1" cx="1400" cy="520" r="250" fill="{B}"/>'
          f'<path id="d-h1" d="M1400 270 A250 250 0 0 1 1400 770 Z" fill="{P}"/>'
          f'<rect id="d-sq" x="1640" y="170" width="70" height="70" fill="{K}"/>{bars1}</g>')
    mods = []
    for i in range(4):
        ox = 160 + i * 420
        if i == 0:
            g = "".join(f'<rect class="d-m0b" x="{70 + j * 34}" y="{170 - h}" width="20" height="{h}" fill="{K}"/>' for j, h in enumerate([60, 110, 160, 90, 140, 70, 120]))
        elif i == 1:
            g = f'<circle cx="180" cy="90" r="78" fill="{B}"/><path id="d-q" d="M180 90 L180 12 A78 78 0 0 1 258 90 Z" fill="{P}"/>'
        elif i == 2:
            g = "".join(f'<circle class="d-ring" cx="180" cy="90" r="{r}" fill="none" stroke="{K}" stroke-width="8"/>' for r in (18, 38, 58, 78))
        else:
            g = f'<rect x="105" y="14" width="152" height="152" fill="{K}"/><polyline id="d-chk" points="140,92 172,124 228,58" fill="none" stroke="{P}" stroke-width="20" stroke-linecap="square"/>'
        mods.append(f'<g id="d-m{i}" transform="translate({ox} 520)"><g id="d-mi{i}">{g}</g></g>')
    racks = ""
    hs = [300, 380, 260, 420, 340, 400, 280, 360, 320]
    for c, h in enumerate(hs):
        x = 1000 + c * 76
        racks += f'<rect class="d-rk" x="{x}" y="{900 - h}" width="60" height="{h}" fill="{K}"/>'
        for r in range(int(h / 46)):
            if (c * 7 + r * 3) % 4 == 0:
                continue
            racks += f'<rect class="d-led" x="{x + 12}" y="{900 - h + 20 + r * 46}" width="14" height="14" fill="{[P, B, V, "#f2eee6"][(c + r) % 4]}"/>'
    s4 = (f'<rect id="d-ni" x="1000" y="600" width="668" height="300" fill="{K}"/>'
          f'<circle id="d-sun" cx="1560" cy="300" r="120" fill="{B}"/>'
          f'<path id="d-ai" d="M1114 600 A220 220 0 0 1 1554 600 Z" fill="{P}"/>'
          f'<text id="d-ait" x="1334" y="545" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">AI</text>'
          f'<text id="d-nit" x="1334" y="770" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">NI</text>')
    labels = "".join(f'<div class="mono d-sl" id="d-sl{i}" style="left:{160 + i * 420}px;top:716px;font-size:18px">{n}  {lab}</div>'
                     f'<div class="val d-sv" id="d-sv{i}" style="left:{158 + i * 420}px;top:752px;font-size:34px;color:#14111f"></div>'
                     for i, (n, lab, _) in enumerate(STEPS))
    body = f'''<svg class="layer" viewBox="0 0 1920 1080">{grid}{s1}
<line id="d-rule" x1="160" y1="480" x2="160" y2="480" stroke="{K}" stroke-width="6"/>
<rect id="d-mk" x="-13" y="-13" width="26" height="26" fill="{P}"/>
{"".join(mods)}<g id="d-dc">{racks}</g><g id="d-s4">{s4}</g></svg>
<div class="layer">{labels}</div>
{texts()}'''
    js = common_js("""
const SX = [340, 760, 1180, 1600];
// ── 1. 목소리: 큰 원, 반원, 막대(파형)가 격자 위에 차례로 놓임
tl.fromTo("#d-c1", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 1.1, ease: "expo.out" }, 0.35);
tl.fromTo("#d-h1", { rotation: 180, svgOrigin: "1400 520", opacity: 0 }, { rotation: 0, svgOrigin: "1400 520", opacity: 1, duration: 1.2, ease: "expo.out" }, 0.7);
tl.fromTo(".d-b1", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.9, ease: "expo.out", stagger: 0.06 }, 1.0);
gsap.utils.toArray(".d-b1").forEach((el, j) => { for (let k = 0; k < 3; k++) tl.to(el, { scaleY: 0.45 + 0.55 * hsh(j, k), duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 1 }, 2.0 + k * 0.5 + j * 0.03); });
tl.fromTo("#d-sq", { rotation: -90, svgOrigin: "1675 205", scale: 0 }, { rotation: 0, svgOrigin: "1675 205", scale: 1, duration: 1.0, ease: "back.out(1.6)" }, 1.3);
tl.to(["#d-c1", "#d-h1", "#d-sq", ".d-b1"], { x: 1100, duration: 0.7, ease: "power3.in", stagger: 0.03 }, 3.7);
// ── 2. 검은 선이 표식이 지나간 자리까지 그어지고, 단계마다 도형 모듈이 격자 칸에 들어옴
gsap.set("#d-mk", { x: 160, y: 480, rotation: 45, transformOrigin: "50% 50%", opacity: 0 });
tl.fromTo("#d-mk", { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)", immediateRender: false }, 3.95);
gsap.set(["#d-mi0", "#d-mi1", "#d-mi2", "#d-mi3", ".d-sl"], { opacity: 0 });
for (let i = 0; i < 4; i++) {
  const d = ARR[i] - DEP[i];
  tl.to("#d-mk", { x: SX[i], rotation: 45 + 90 * (i + 1), duration: d, ease: "power2.inOut" }, DEP[i]);
  tl.to("#d-rule", { attr: { x2: SX[i] }, duration: d, ease: "power2.inOut" }, DEP[i]);
  const t = ARR[i];
  tl.fromTo("#d-mi" + i, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.9, ease: "expo.out", immediateRender: false }, t - 0.1);
  tl.fromTo("#d-sl" + i, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, t + 0.1);
  SCRAMBLE(document.getElementById("d-sv" + i), VALS[i], t + 0.2, 0.8);
}
tl.fromTo(".d-m0b", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.8, ease: "expo.out", stagger: 0.05 }, ARR[0] - 0.05);
tl.fromTo("#d-q", { rotation: -90, svgOrigin: "180 90" }, { rotation: 0, svgOrigin: "180 90", duration: 0.9, ease: "expo.out" }, ARR[1]);
DRAWS(".d-ring", ARR[2] - 0.05, 0.7, "power3.out", 0.08);
DRAWS("#d-chk", ARR[3] + 0.1, 0.5, "power3.out");
tl.to(["#d-mi0", "#d-mi1", "#d-mi2", "#d-mi3", ".d-sl", ".d-sv"], { opacity: 0, y: -40, duration: 0.5, ease: "power3.in", stagger: 0.03 }, 11.95);
tl.to(["#d-rule", "#d-mk"], { opacity: 0, duration: 0.4 }, 12.1);
// ── 3. 검은 랙이 한 칸씩 솟고, 작은 색 사각형(LED)이 켜짐
tl.fromTo(".d-rk", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.9, ease: "expo.out", stagger: 0.12 }, 13.0);
tl.fromTo(".d-led", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.35, ease: "back.out(2)", stagger: 0.015 }, 14.1);
// ── 4. 랙이 한 덩어리(인프라)가 되고, 분홍 반원(AI)이 그 위에 놓임
gsap.set(["#d-ni", "#d-ait", "#d-nit"], { opacity: 0 });
tl.fromTo("#d-ni", { opacity: 0, scaleY: 0, transformOrigin: "50% 100%" }, { opacity: 1, scaleY: 1, duration: 0.9, ease: "expo.inOut", immediateRender: false }, 16.9);
tl.to(".d-led", { scale: 0, duration: 0.3, ease: "power2.in", stagger: 0.004 }, 16.8);
tl.to(".d-rk", { opacity: 0, duration: 0.01 }, 17.8);
tl.fromTo("#d-ai", { y: -760 }, { y: 0, duration: 1.0, ease: "back.out(1.15)" }, 17.8);
tl.fromTo("#d-sun", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 1.1, ease: "expo.out" }, 18.6);
tl.fromTo(["#d-ait", "#d-nit"], { opacity: 0 }, { opacity: 1, duration: 0.5, stagger: 0.15, immediateRender: false }, 18.9);
""")
    return page("Rapeech 시안 D", css, body, js)


# ─────────────────────────────────────────────── E 하프톤
def build_e():
    SX = [400, 800, 1200, 1600]
    labels = "".join(f'<div class="cwrap" style="left:{x}px;top:686px"><div class="mono e-sl" id="e-sl{i}" style="position:relative">{n}  {lab}</div>'
                     f'<div class="val e-sv" id="e-sv{i}" style="position:relative;margin-top:14px;font-size:34px"></div></div>'
                     for i, (x, (n, lab, _)) in enumerate(zip(SX, STEPS)))
    body = f'''<canvas id="ht" class="layer" width="1920" height="1080"></canvas>
<div class="layer">{labels}</div>
{texts()}'''
    js = common_js("""
const SX = [400, 800, 1200, 1600], START = 160, LY = 640, ZS = 14;
gsap.set(".e-sl", { opacity: 0 });
for (let i = 0; i < 4; i++) {
  tl.fromTo("#e-sl" + i, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, ARR[i] + 0.1);
  SCRAMBLE(document.getElementById("e-sv" + i), VALS[i], ARR[i] + 0.2, 0.9);
  if (i < 3) tl.to(["#e-sl" + i, "#e-sv" + i], { opacity: 0.38, duration: 0.6 }, ARR[i + 1] - 0.3);
}
tl.to([".e-sl", ".e-sv"], { opacity: 0, duration: 0.5 }, 11.95);

// ───────── 장면을 낮은 해상도로 그린 뒤, 칸마다 밝기만큼 망점을 찍음(시간 t로만 결정)
const CELL = 10, GW = 1920 / CELL, GH = 1080 / CELL;
const off = document.createElement("canvas"); off.width = GW; off.height = GH;
const o = off.getContext("2d", { willReadFrequently: true });
const out = document.getElementById("ht").getContext("2d");
const BK = 10, BCOL = [];
for (let b = 0; b < BK; b++) {
  const u = b / (BK - 1), A = u < 0.5 ? [255, 60, 210] : [170, 90, 255], Bc = u < 0.5 ? [170, 90, 255] : [80, 80, 255], v = (u % 0.5) * 2;
  BCOL.push(A.map((c, i) => Math.round(c + (Bc[i] - c) * (u === 1 ? 1 : v))));
}
function orbX(t) {
  let x = START;
  for (let i = 0; i < 4; i++) if (t >= DEP[i]) x = lerp(i ? SX[i - 1] : START, SX[i], io(seg(t, DEP[i], ARR[i])));
  return x;
}
function sphere(x, y, r, gain = 1) {
  if (r <= 0.5) return;
  const g = o.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.05, x, y, r);
  g.addColorStop(0, `rgba(255,255,255,${gain})`); g.addColorStop(0.45, `rgba(150,150,150,${gain})`); g.addColorStop(1, `rgba(25,25,25,${gain})`);
  o.fillStyle = g; o.beginPath(); o.arc(x, y, r, 0, Math.PI * 2); o.fill();
}
const C30 = Math.cos(Math.PI / 6), KK = 50;
const iso = (x, y, z) => [(x - y) * C30 * KK, (x + y) * 0.5 * KK - z * KK];
function plate(z, a, flash) {
  const P = (x, y, zz) => iso(x - 3.5, y - 2, zz + z - 1.6);
  const poly = (pts, c) => { o.fillStyle = c; o.beginPath(); pts.forEach((p, i) => i ? o.lineTo(p[0], p[1]) : o.moveTo(p[0], p[1])); o.closePath(); o.fill(); };
  const g = (v) => `rgba(${v},${v},${v},${a})`;
  poly([P(0, 4, 0), P(7, 4, 0), P(7, 4, 0.14), P(0, 4, 0.14)], g(70 + flash * 60));
  poly([P(7, 0, 0), P(7, 4, 0), P(7, 4, 0.14), P(7, 0, 0.14)], g(110 + flash * 60));
  poly([P(0, 0, 0.14), P(7, 0, 0.14), P(7, 4, 0.14), P(0, 4, 0.14)], g(150 + flash * 100));
  o.strokeStyle = `rgba(255,255,255,${a})`; o.lineWidth = 6; o.beginPath();
  const e = [P(0, 4, 0.14), P(7, 4, 0.14), P(7, 0, 0.14)]; e.forEach((p, i) => i ? o.lineTo(p[0], p[1]) : o.moveTo(p[0], p[1])); o.stroke();
}
function drawScene(t) {
  o.setTransform(1, 0, 0, 1, 0, 0); o.fillStyle = "#000"; o.fillRect(0, 0, GW, GH);
  o.setTransform(1 / CELL, 0, 0, 1 / CELL, 0, 0);
  // 카메라: 마지막 노드 속으로 들어가는 줌(인피니트 줌)
  const zu = io3(seg(t, 12.2, 13.9)), s = Math.pow(ZS, zu);
  const Ox = lerp(1600, 1290, zu), Oy = lerp(640, 560, zu);
  o.translate(Ox, Oy); o.scale(s, s); o.translate(-1600, -640);
  const fade = 1 - seg(s, 2, 5);
  // 1. 목소리: 큰 구와 퍼지는 고리 → 작은 점으로 줄어 출발점으로
  const mv = io3(seg(t, 3.5, 4.4));
  const r0 = 210 * io3(seg(t, 0.2, 1.3)), px = lerp(1300, START, mv), py = lerp(560, LY, mv), rr = lerp(r0, 26, mv);
  if (t < 4.5) for (let k = 0; k < 3; k++) {
    const ph = ((t - 0.8 - k * 0.45) % 1.4 + 1.4) % 1.4 / 1.4;
    if (t < 0.8 + k * 0.45) continue;
    o.strokeStyle = `rgba(255,255,255,${0.55 * (1 - ph) * (1 - mv)})`; o.lineWidth = 16; o.beginPath(); o.arc(1300, 560, 220 + ph * 260, 0, Math.PI * 2); o.stroke();
  }
  // 2. 길과 노드
  const x = t < 4.4 ? px : orbX(t);
  if (t > 3.9 && fade > 0) {
    o.strokeStyle = `rgba(255,255,255,${0.85 * fade})`; o.lineWidth = 7; o.beginPath(); o.moveTo(START, LY); o.lineTo(x, LY); o.stroke();
    SX.forEach((sx, i) => {
      const on = seg(t, ARR[i] - 0.05, ARR[i] + 0.3);
      o.strokeStyle = `rgba(255,255,255,${(0.35 + 0.5 * on) * fade * seg(t, 3.9, 4.6)})`; o.lineWidth = 6;
      o.beginPath(); o.arc(sx, LY, 38, 0, Math.PI * 2); o.stroke();
      if (on > 0) { o.fillStyle = `rgba(255,255,255,${0.8 * on * fade})`; o.beginPath(); o.arc(sx, LY, 16 * on, 0, Math.PI * 2); o.fill(); }
    });
  }
  if (t < 12.4) sphere(t < 4.4 ? px : x, t < 4.4 ? py : LY, t < 4.4 ? rr : 26 + 6 * Math.exp(-Math.pow((t - ARR.find((a) => a > t - 0.6) || 99) / 0.25, 2)), 1);
  // 3. 노드 안에 있던 데이터센터(1/ZS 크기)가 줌으로 화면을 채움 → 층이 아래부터 쌓임 → 4. 두 층으로 모임
  if (s > 1.5) {
    o.save(); o.translate(1600, 640); o.scale(1 / ZS, 1 / ZS);
    const Z = [0, 0.12, 0.24, 3.0, 3.12, 3.24], cv = io3(seg(t, 16.85, 18.15));
    for (let f = 0; f < 6; f++) {
      const ap = io3(seg(t, 13.3 + f * 0.36, 14.1 + f * 0.36));
      if (ap <= 0) continue;
      const z = lerp(f * 1.0, Z[f], cv) + (1 - ap) * 0.6;
      const fl = f < 3 ? Math.exp(-Math.pow((t - 19.3) / 0.35, 2)) : Math.exp(-Math.pow((t - 18.85) / 0.35, 2));
      plate(z, ap * seg(s, 2, 6), fl);
    }
    const dy = lerp(-700, iso(0, 0, 3.24 - 1.6 + 0.14)[1], io(seg(t, 18.3, 18.95)));
    if (t > 18.3 && t < 19.9) sphere(0, t < 18.95 ? dy : lerp(dy, iso(0, 0, 0.38 - 1.6)[1], io(seg(t, 18.95, 19.35))), 22 * (1 - seg(t, 19.4, 19.9)), 1);
    o.restore();
  }
  // 망점 찍기
  const im = o.getImageData(0, 0, GW, GH).data;
  out.fillStyle = "#0c0916"; out.fillRect(0, 0, 1920, 1080);
  const paths = BCOL.map(() => new Path2D()), white = new Path2D();
  for (let gy = 0; gy < GH; gy++) for (let gx = 0; gx < GW; gx++) {
    const i = (gy * GW + gx) * 4, lum = (im[i] + im[i + 1] + im[i + 2]) / 765;
    const r = CELL * 0.56 * Math.sqrt(0.035 + 0.965 * lum);
    const cx = gx * CELL + CELL / 2 + (gy % 2 ? CELL / 2 : 0) * 0, cy = gy * CELL + CELL / 2;
    const p = lum > 0.82 ? white : paths[Math.min(BK - 1, Math.floor((gx / GW + gy / GH * 0.25) / 1.25 * BK))];
    p.moveTo(cx + r, cy); p.arc(cx, cy, r, 0, Math.PI * 2);
  }
  paths.forEach((p, b) => { out.fillStyle = `rgb(${BCOL[b].join(",")})`; out.fill(p); });
  out.fillStyle = "#fff4fd"; out.fill(white);
}
window.addEventListener("hf-seek", (e) => drawScene(e.detail.time));
drawScene(0);
""")
    return page("Rapeech 시안 E", "", body, js)


if __name__ == "__main__":
    for name, fn in (("c", build_c), ("d", build_d), ("e", build_e)):
        d = project(name, fn())
        for f in ("bed.wav", "sfx.wav"):
            shutil.copy(HERE / "a" / "assets" / f, d / "assets" / f)
    print("ok")
