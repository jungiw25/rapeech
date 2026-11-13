"""캐릭터 모션그래픽 샘플(10초, 16:9). 회사 영상과 무관한 독립 샘플.

자체 캐릭터: 민트색 조약돌 몸, 큰 흰 눈, 남색 눈동자·눈썹, 분홍 볼, 짧은 팔다리, 손에는 흰 종이비행기.
연출 원칙(화면 크기 바꾸기 · 카메라 밀고 당기기 · 모양으로 장면 잇기 · 예비동작/충돌/반동)만 참고했고
다른 작품의 캐릭터·프롬프트는 쓰지 않았다.

  0.0–1.3  눈 클로즈업: 깜빡임 → 눈썹이 모이며 결심 → 눈동자에 반짝임 → 흰 빛이 화면을 덮음(마스크 전환)
  1.3–2.7  낮은 각도 중간 샷: 비행기를 든 팔을 낮췄다가(예비동작) 대각선 위로 번쩍, 카메라가 살짝 밀고 들어감
           → 비행기 빛줄기가 대각선으로 화면을 가르며 와이프 전환
  2.7–4.2  와이드: 몸을 낮췄다가 왼쪽→오른쪽으로 달림, 배경 도형이 층마다 다른 속도로 지나감(시차)
  4.2–6.2  점프: 공중에서 한 바퀴 돌며 비행기를 던짐, 도는 한가운데 잠깐 느려짐. 비행기가 그린 원이 화면을 채움
  6.2–8.0  바닥 가까운 초저각: 쿵 착지 → 몸이 눌렸다가 돌아옴, 발밑에서 동그란 충격파가 퍼짐(→ 다음 장면으로 이어짐)
  8.0–10.0 정면 영웅 포즈: 비행기가 머리 위를 한 바퀴 돌아 손으로, 카메라가 넓게 빠지며 작은 별이 반짝
사용법: python3 video/samples/character/build.py && cd video/samples/character && npx hyperframes render --fps 60 --quality delivery --output out/character_sample.mp4
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(HERE.parent.parent))
sys.path.insert(0, str(REPO))
from kit_v2 import page, setup_project  # noqa: E402

DUR = 10.0
NAVY, CORAL, MINT1, MINT2, CREAM = "#23305e", "#ff7a6b", "#8ff0d2", "#2fbfa6", "#fff6ea"


def char(c, arm_up=False):
    """캐릭터 한 명. 모든 부품 좌표는 캐릭터 기준(몸 가운데 0,0 / 발바닥 y=150)."""
    plane = (f'<g id="{c}-pl"><path d="M70 64 L140 40 L96 86 Z" fill="#fff" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M70 64 L108 62 L96 86" fill="#e8ecff" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/></g>')
    return f'''<g id="{c}"><g id="{c}-b">
  <ellipse id="{c}-sh" cx="0" cy="152" rx="96" ry="14" fill="{NAVY}" opacity=".16"/>
  <rect id="{c}-l1" x="-56" y="92" width="34" height="58" rx="17" fill="{MINT2}"/>
  <rect id="{c}-l2" x="22" y="92" width="34" height="58" rx="17" fill="{MINT2}"/>
  <rect id="{c}-a2" x="-128" y="-4" width="32" height="70" rx="16" fill="{MINT2}"/>
  <rect x="-110" y="-130" width="220" height="240" rx="104" fill="url(#mint)"/>
  <ellipse cx="-30" cy="-92" rx="36" ry="16" fill="#fff" opacity=".35"/>
  <g id="{c}-f">
    <ellipse cx="-40" cy="-28" rx="30" ry="34" fill="#fff"/><ellipse cx="40" cy="-28" rx="30" ry="34" fill="#fff"/>
    <g id="{c}-pp"><circle cx="-34" cy="-24" r="15" fill="{NAVY}"/><circle cx="46" cy="-24" r="15" fill="{NAVY}"/>
      <circle cx="-29" cy="-30" r="5" fill="#fff"/><circle cx="51" cy="-30" r="5" fill="#fff"/></g>
    <rect id="{c}-lid" x="-74" y="-66" width="148" height="0" fill="{MINT1}"/>
    <path id="{c}-w1" d="M-66 -74 Q-42 -86 -16 -76" fill="none" stroke="{NAVY}" stroke-width="11" stroke-linecap="round"/>
    <path id="{c}-w2" d="M16 -76 Q42 -86 66 -74" fill="none" stroke="{NAVY}" stroke-width="11" stroke-linecap="round"/>
    <ellipse cx="-64" cy="14" rx="16" ry="9" fill="#ff9fb0" opacity=".8"/><ellipse cx="64" cy="14" rx="16" ry="9" fill="#ff9fb0" opacity=".8"/>
    <path d="M-12 26 Q0 34 12 26" fill="none" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"/>
  </g>
  <g id="{c}-a1" transform="{'rotate(-135 112 -4)' if arm_up else ''}"><rect x="96" y="-4" width="32" height="70" rx="16" fill="{MINT2}"/>{plane}</g>
</g></g>'''


def shapes(sid, n, seed, far=True):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        x, y, s = rng.uniform(-200, 2120), rng.uniform(80, 1000), rng.uniform(30, 90) * (0.7 if far else 1.3)
        col, op = (NAVY, 0.1) if far else (CORAL, 0.55)
        if i % 3 == 0:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s / 2:.0f}" fill="{col}" opacity="{op}"/>')
        elif i % 3 == 1:
            out.append(f'<path d="M{x:.0f} {y - s / 2:.0f} L{x + s / 2:.0f} {y + s / 2:.0f} L{x - s / 2:.0f} {y + s / 2:.0f} Z" fill="{col}" opacity="{op}"/>')
        else:
            out.append(f'<path d="M{x - s:.0f} {y:.0f} Q{x:.0f} {y - s:.0f} {x + s:.0f} {y:.0f}" fill="none" stroke="{col if far else "#fff"}" stroke-width="8" stroke-linecap="round" opacity="{op + 0.2}"/>')
    return f'<g id="{sid}">{"".join(out)}</g>'


def build():
    star = lambda i, x, y, r: (f'<path id="{i}" d="M{x} {y - r} L{x + r * .28} {y - r * .28} L{x + r} {y} L{x + r * .28} {y + r * .28} L{x} {y + r} '
                               f'L{x - r * .28} {y + r * .28} L{x - r} {y} L{x - r * .28} {y - r * .28} Z" fill="#fff"/>')
    svg = f'''<svg class="layer" viewBox="0 0 1920 1080">
<defs><linearGradient id="mint" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MINT1}"/><stop offset="1" stop-color="{MINT2}"/></linearGradient>
  <linearGradient id="bgg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CREAM}"/><stop offset="1" stop-color="#ffd9cc"/></linearGradient></defs>
<rect width="1920" height="1080" fill="url(#bgg)"/>
<g id="s1"><g transform="translate(960 640)">{char("c1")}</g>{star("glint", 931, 609, 22)}</g>
<g id="s2">{shapes("s2far", 14, 2)}<rect x="-400" y="900" width="2720" height="400" fill="#ffc9b8"/>
  <g transform="translate(860 700) scale(1.7)">{char("c2")}</g>
  <path id="trail2" d="M1080 380 C 1300 260, 1600 160, 2100 -60" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round"/></g>
<g id="s3">{shapes("s3far", 18, 3)}<rect x="-2000" y="820" width="6000" height="400" fill="#ffc9b8"/>{shapes("s3near", 10, 4, far=False)}
  <g transform="translate(300 700) scale(.55)"><g id="c3w">{char("c3", arm_up=True)}</g></g>
  <path id="trail3" d="M200 560 C 700 640, 1100 420, 1500 520 S 2000 300, 2200 160" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".9"/></g>
<g id="s4">{shapes("s4far", 16, 5)}
  <g transform="translate(960 640)"><g id="c4w">{char("c4", arm_up=True)}</g></g>
  <g id="fly4"><path d="M-35 0 L35 -24 L-9 22 Z" fill="#fff" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/></g>
  <circle id="ring4" cx="960" cy="540" r="300" fill="none" stroke="#fff" stroke-width="18"/></g>
<g id="s5">{shapes("s5far", 12, 6)}<rect x="-400" y="960" width="2720" height="400" fill="#ffc9b8"/>
  <circle class="wave5" cx="960" cy="960" r="60" fill="none" stroke="{CORAL}" stroke-width="10"/>
  <circle class="wave5" cx="960" cy="960" r="60" fill="none" stroke="{NAVY}" stroke-width="5" opacity=".6"/>
  <g id="tri5">{"".join(f'<path class="t5" d="M{960 + 70 * np.cos(a):.0f} {930 + 40 * np.sin(a):.0f} l18 -30 l18 30 Z" fill="{CORAL if k % 2 else NAVY}" opacity=".8"/>' for k, a in enumerate(np.linspace(np.pi, 2 * np.pi, 7)))}</g>
  <g transform="translate(960 810)"><g id="c5w">{char("c5", arm_up=True)}</g></g></g>
<g id="s6">{shapes("s6far", 16, 7)}<rect x="-1200" y="860" width="4320" height="600" fill="#ffc9b8"/>
  <g transform="translate(960 710)"><g id="c6w">{char("c6", arm_up=True)}</g></g>
  <g id="fly6"><path d="M-35 0 L35 -24 L-9 22 Z" fill="#fff" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/></g>
  {star("spark6", 0, 0, 22)}</g>
<circle id="flash" cx="960" cy="560" r="0" fill="#fff"/>
<rect id="wipe" x="-200" y="-200" width="2320" height="1480" fill="{CORAL}"/>
</svg>'''
    js = """
const shots = ["#s1", "#s2", "#s3", "#s4", "#s5", "#s6"], T = [0, 1.3, 2.7, 4.2, 6.2, 8.0, 10.0];
gsap.set(shots, { opacity: 0 });
shots.forEach((s, i) => { tl.set(s, { opacity: 1 }, T[i]); if (i < 5) tl.set(s, { opacity: 0 }, T[i + 1]); });
gsap.set(["#glint", "#spark6", "#fly4", "#fly6", "#wipe", "#ring4", ".wave5", ".t5", "#c4-sh"], { opacity: 0 });
const CAM = (s, from, to, t, d, e = "power2.inOut") => tl.fromTo(s, Object.assign({ svgOrigin: "960 540" }, from), Object.assign({ svgOrigin: "960 540", duration: d, ease: e, immediateRender: false }, to), t);
gsap.set(shots, { svgOrigin: "960 540" });

// ── 1. 눈 클로즈업
CAM("#s1", { scale: 4.4, x: 0, y: -297 }, { scale: 5.0, x: 0, y: -340 }, 0, 1.3, "power1.in");
tl.fromTo("#c1-lid", { attr: { height: 0 } }, { attr: { height: 76 }, duration: 0.08, ease: "power1.in", yoyo: true, repeat: 1 }, 0.14);
tl.to("#c1-w1", { attr: { d: "M-66 -66 Q-42 -80 -14 -82" }, duration: 0.35, ease: "power2.out" }, 0.42);
tl.to("#c1-w2", { attr: { d: "M14 -82 Q42 -80 66 -66" }, duration: 0.35, ease: "power2.out" }, 0.42);
tl.to("#c1-pp", { x: -8, duration: 0.3, ease: "power2.out" }, 0.4);
tl.fromTo("#glint", { opacity: 0, scale: 0.2, svgOrigin: "931 609" }, { opacity: 1, scale: 1.3, rotation: 45, svgOrigin: "931 609", duration: 0.25, ease: "power2.out", immediateRender: false }, 0.82);
tl.fromTo("#flash", { attr: { r: 0, cx: 926, cy: 616 }, opacity: 1 }, { attr: { r: 2300 }, duration: 0.42, ease: "power3.in", immediateRender: false }, 0.9);
tl.to("#flash", { opacity: 0, duration: 0.35, ease: "sine.out" }, 1.32);

// ── 2. 낮은 각도 중간 샷: 예비동작 → 비행기를 대각선 위로
CAM("#s2", { scale: 1.0, rotation: -3, y: 0 }, { scale: 1.1, rotation: -5, y: -20 }, 1.3, 1.4, "sine.inOut");
tl.fromTo("#c2-a1", { rotation: 0, svgOrigin: "112 -4" }, { rotation: 25, svgOrigin: "112 -4", duration: 0.3, ease: "power2.out", immediateRender: false }, 1.4);
tl.to("#c2-a1", { rotation: -135, svgOrigin: "112 -4", duration: 0.32, ease: "back.out(1.6)" }, 1.75);
tl.fromTo("#c2-b", { scaleY: 1, scaleX: 1, svgOrigin: "0 150" }, { scaleY: 0.93, scaleX: 1.05, svgOrigin: "0 150", duration: 0.3, ease: "power2.out", immediateRender: false }, 1.4);
tl.to("#c2-b", { scaleY: 1.04, scaleX: 0.97, svgOrigin: "0 150", duration: 0.25, ease: "power2.out" }, 1.75);
tl.to("#c2-b", { scaleY: 1, scaleX: 1, svgOrigin: "0 150", duration: 0.3, ease: "sine.out" }, 2.0);
DR("#trail2", 2.05, 0.45, "power2.in");
tl.fromTo("#wipe", { opacity: 1, clipPath: "polygon(0px 1280px, 0px 1280px, -400px 1280px, -400px 1280px)" },
  { opacity: 1, clipPath: "polygon(0px 1280px, 2520px -200px, 2120px -200px, -400px 1280px)", duration: 0.3, ease: "power2.in", immediateRender: false }, 2.4);
tl.to("#wipe", { clipPath: "polygon(2520px -200px, 2520px -200px, 2120px -200px, 2120px -200px)", duration: 0.32, ease: "power2.out" }, 2.72);
tl.set("#wipe", { opacity: 0 }, 3.05);

// ── 3. 와이드: 웅크렸다가 질주, 배경 시차
tl.fromTo("#c3w", { x: 0 }, { x: 1300, duration: 1.15, ease: "power2.in", immediateRender: false }, 3.0);
tl.fromTo("#c3-b", { scaleY: 1, svgOrigin: "0 150" }, { scaleY: 0.82, scaleX: 1.12, svgOrigin: "0 150", duration: 0.22, ease: "power2.out", immediateRender: false }, 2.78);
tl.to("#c3-b", { scaleY: 1, scaleX: 1, rotation: 12, svgOrigin: "0 150", duration: 0.2, ease: "power2.out" }, 3.0);
for (let k = 0; k < 7; k++) {
  tl.to("#c3-l1", { rotation: k % 2 ? 35 : -35, svgOrigin: "-39 96", duration: 0.13, ease: "sine.inOut" }, 3.0 + k * 0.13);
  tl.to("#c3-l2", { rotation: k % 2 ? -35 : 35, svgOrigin: "39 96", duration: 0.13, ease: "sine.inOut" }, 3.0 + k * 0.13);
  tl.to("#c3-b", { y: k % 2 ? 0 : -14, duration: 0.13, ease: "sine.inOut" }, 3.0 + k * 0.13);
}
CAM("#s3", { x: 0 }, { x: -520 }, 2.7, 1.5, "power1.in");
tl.fromTo("#s3far", { x: 0 }, { x: 260, duration: 1.5, ease: "power1.in", immediateRender: false }, 2.7);
tl.fromTo("#s3near", { x: 0 }, { x: -700, duration: 1.5, ease: "power1.in", immediateRender: false }, 2.7);
DR("#trail3", 3.15, 1.0, "power2.in");

// ── 4. 점프 + 회전 + 던지기(도는 한가운데 잠깐 느려짐)
CAM("#s4", { scale: 1.25, rotation: 6 }, { scale: 1.0, rotation: -6 }, 4.2, 2.0, "sine.inOut");
tl.fromTo("#c4w", { y: 0 }, { y: -280, duration: 0.5, ease: "power2.out", immediateRender: false }, 4.2);
tl.fromTo("#c4-b", { rotation: 0, svgOrigin: "0 0" }, { rotation: 150, svgOrigin: "0 0", duration: 0.45, ease: "power2.in", immediateRender: false }, 4.3);
tl.to("#c4-b", { rotation: 210, svgOrigin: "0 0", duration: 0.55, ease: "none" }, 4.75);            // 느려지는 구간
tl.to("#c4-b", { rotation: 360, svgOrigin: "0 0", duration: 0.35, ease: "power2.out" }, 5.3);
tl.to("#c4w", { y: -60, duration: 0.6, ease: "power2.in" }, 5.4);
tl.set("#c4-pl", { opacity: 0 }, 4.95);
tl.set("#fly4", { opacity: 1 }, 4.95);
const q4 = { a: 0 };
tl.fromTo(q4, { a: 0 }, { a: 1, duration: 1.15, ease: "power1.inOut", immediateRender: false, onUpdate: () => {
  const r = 120 + q4.a * 520, ang = -1.2 + q4.a * 5.6;
  gsap.set("#fly4", { x: 960 + r * Math.cos(ang), y: 500 + r * 0.62 * Math.sin(ang), rotation: (ang * 180 / Math.PI) + 90 });
} }, 4.95);
tl.fromTo("#ring4", { attr: { r: 160, "stroke-width": 4 }, opacity: 0 }, { attr: { r: 1400, "stroke-width": 380 }, opacity: 1, duration: 0.75, ease: "power2.in", immediateRender: false }, 5.45);

// ── 5. 초저각 착지: 눌림 → 반동, 충격파
CAM("#s5", { scale: 1.35, y: -120 }, { scale: 1.0, y: 0 }, 6.2, 0.55, "power2.out");
CAM("#s5", { scale: 1.0, y: 0 }, { scale: 1.12, y: -40 }, 6.75, 1.25, "sine.inOut");
tl.fromTo("#c5w", { y: -900 }, { y: 0, duration: 0.35, ease: "power2.in", immediateRender: false }, 6.2);
tl.fromTo("#c5-b", { scaleY: 1.12, scaleX: 0.92, svgOrigin: "0 150" }, { scaleY: 0.72, scaleX: 1.25, svgOrigin: "0 150", duration: 0.12, ease: "power2.out", immediateRender: false }, 6.55);
tl.to("#c5-b", { scaleY: 1.08, scaleX: 0.95, svgOrigin: "0 150", duration: 0.2, ease: "power2.out" }, 6.67);
tl.to("#c5-b", { scaleY: 1, scaleX: 1, svgOrigin: "0 150", duration: 0.35, ease: "sine.out" }, 6.87);
gsap.utils.toArray(".wave5").forEach((el, k) => tl.fromTo(el, { attr: { r: 60 }, opacity: 0.9 }, { attr: { r: 900 + k * 200 }, opacity: 0, duration: 1.1, ease: "power2.out", immediateRender: false }, 6.58 + k * 0.12));
gsap.utils.toArray(".t5").forEach((el, k) => { const a = Math.PI + k * Math.PI / 6;
  tl.fromTo(el, { x: 0, y: 0, opacity: 0 }, { x: 520 * Math.cos(a), y: 260 * Math.sin(a), rotation: (k - 3) * 40, opacity: 0.85, duration: 0.9, ease: "power3.out", immediateRender: false }, 6.6); });
tl.to(".t5", { opacity: 0, duration: 0.4 }, 7.5);
// 충격파 고리가 커지며 다음 장면으로(같은 모양으로 잇기)
tl.fromTo("#flash", { attr: { r: 0, cx: 960, cy: 960 }, opacity: 0.95 }, { attr: { r: 2000 }, duration: 0.45, ease: "power3.in", immediateRender: false }, 7.6);
tl.to("#flash", { opacity: 0, duration: 0.4, ease: "sine.out" }, 8.02);

// ── 6. 정면 영웅 포즈: 비행기가 한 바퀴 돌아 손으로, 넓게 빠짐
CAM("#s6", { scale: 1.7, y: 140 }, { scale: 1.0, y: 0 }, 8.0, 1.8, "power3.inOut");
tl.set("#c6-pl", { opacity: 0 }, 8.0);
tl.set("#fly6", { opacity: 1 }, 8.0);
const q6 = { a: 0 };
tl.fromTo(q6, { a: 0 }, { a: 1, duration: 1.3, ease: "power2.inOut", immediateRender: false, onUpdate: () => {
  const ang = Math.PI * 0.9 + q6.a * Math.PI * 2.15, r = 260 - q6.a * 110;
  gsap.set("#fly6", { x: 960 + r * Math.cos(ang), y: 470 + r * 0.45 * Math.sin(ang), rotation: ang * 180 / Math.PI + 95 });
} }, 8.05);
tl.set("#fly6", { opacity: 0 }, 9.35);
tl.set("#c6-pl", { opacity: 1 }, 9.35);
tl.fromTo("#c6-b", { scaleY: 1, svgOrigin: "0 150" }, { scaleY: 1.03, scaleX: 0.985, svgOrigin: "0 150", duration: 0.32, ease: "sine.inOut", yoyo: true, repeat: 1, immediateRender: false }, 9.3);
tl.fromTo("#spark6", { opacity: 0, scale: 0.2, x: 1078, y: 430 }, { opacity: 1, scale: 1.1, rotation: 90, duration: 0.3, ease: "power2.out", immediateRender: false }, 9.38);
tl.to("#spark6", { scale: 0.7, opacity: 0.9, duration: 0.5, ease: "sine.inOut" }, 9.7);
"""
    return page("Character sample", svg, js, DUR, "#root, html, body { background: #fff6ea; }",
                audio=f'<audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    import subprocess
    from engine.bgm import SR, synth, write_wav
    lib = REPO / ".claude/skills/media-use/audio/assets/sfx"

    def load(n, semis=0.0):
        y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(lib / f"{n}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                                         capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(float)
        if semis:
            r = 2 ** (semis / 12)
            x = np.arange(int(len(y) / r)) * r
            y = np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(2)], 1)
        return y

    buf = np.zeros((int((DUR + 3) * SR), 2))

    def put(y, t, g):
        i = int(t * SR)
        y = y[: len(buf) - i]
        buf[i:i + len(y)] += y * g

    bed = synth(DUR + 1, seed=3, bpm=118)
    put(bed[: len(buf)], 0, 0.35)
    put(load("click-soft", 4), 0.14, 0.25)            # 깜빡임
    put(load("sparkle"), 0.82, 0.3)                   # 눈동자 반짝임
    put(load("whoosh", -2), 0.95, 0.4)                # 흰 빛
    put(load("whoosh-short", 3), 1.75, 0.35)          # 팔 번쩍
    put(load("whoosh-cinematic"), 2.2, 0.25)          # 와이프
    for k in range(4):
        put(load("click-soft", -3 + k), 3.0 + k * 0.26, 0.18)   # 발걸음
    put(load("whoosh", 1), 4.2, 0.4)                  # 점프
    put(load("whoosh-short", -4), 4.95, 0.35)         # 던지기
    put(load("whoosh-cinematic", 2), 5.45, 0.25)
    put(load("impact-bass-1"), 6.55, 0.55)            # 착지
    put(load("pop", -5), 6.62, 0.3)
    put(load("whoosh", 4), 7.6, 0.3)
    put(load("whoosh-short", 2), 8.1, 0.3)            # 비행기 한 바퀴
    put(load("pop", 3), 9.35, 0.3)                    # 손에 쏙
    put(load("sparkle", 2), 9.38, 0.4)                # 별
    buf = buf[: int(DUR * SR)]
    fade = np.linspace(1, 0, int(0.6 * SR))
    buf[-len(fade):] *= fade[:, None]
    buf *= 10 ** (-2 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "character-sample")
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "sfx.wav")
    print("ok")
