"""아웃트로 v2: 인트로 v2와 같은 언어로 앞에 3.5초를 더하고, 그 뒤는 기존 아웃트로(7.5초)를 그대로 붙인다(총 11초).

  0.0–0.25 기존 아웃트로 첫 프레임(막대 12개) 그대로 → 회사 소개 영상 마지막 프레임과 이어짐
  0.25–1.0 막대 12개가 가운데로 모이며 AI 노드가 됨
  1.3–2.3  게이지가 차고 띠링과 함께 반짝
  2.45–3.3 노드가 다시 막대 12개로 펼쳐짐
  3.3–3.5  기존 아웃트로 첫 프레임으로 정확히 돌아옴
  3.5–11.0 기존 아웃트로 그대로(마지막 프레임 = 인트로 마지막 프레임)
사용법: python3 video/outro-v2/build.py && cd video/outro-v2 && npx hyperframes render --fps 60 --quality delivery --output out/raw.mp4
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import G, REPO, SVG_DEFS, node, page, setup_project  # noqa: E402

PRE = 3.5
DUR = PRE + 7.5


def build():
    dashes = "".join(f'<div class="dash" id="d{k}" style="left:{960 + (k - 5.5) * 46 - 9:.1f}px;background:{G[k]}"></div>' for k in range(12))
    body = f'''<svg class="layer" viewBox="0 0 1920 1080">{SVG_DEFS}{node("n", 960, 540, 74, "AI", 38)}</svg>
{dashes}
<img id="still" class="layer" src="assets/outro_first.png" />
<video id="orig" class="clip layer" src="assets/outro.mp4" data-start="{PRE}" data-duration="7.5" data-media-start="0" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index: 5"></video>'''
    css = ".dash { position: absolute; top: 535.8px; width: 18px; height: 8.4px; border-radius: 4.2px; }"
    js = """
gsap.set("#n", { scale: 0, opacity: 0, transformOrigin: "960px 540px" });
// 시작: 기존 아웃트로 첫 프레임 → 같은 자리의 막대로 바뀜
tl.to("#still", { opacity: 0, duration: 0.05, ease: "none" }, 0.2);
gsap.utils.toArray(".dash").forEach((el, k) => {
  const dx = 960 - (960 + (k - 5.5) * 46);
  tl.to(el, { x: dx, scaleX: 0.4, opacity: 0, duration: 0.75, ease: "power3.inOut" }, 0.25 + Math.abs(k - 5.5) * 0.02);
  tl.to(el, { x: 0, scaleX: 1, opacity: 1, duration: 0.6, ease: "expo.out" }, 2.75 + (5.5 - Math.abs(k - 5.5)) * 0.015);
});
tl.fromTo("#n", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: "power3.out", immediateRender: false }, 0.75);
GAUGE("n", 1.3, 1.0);
tl.to("#n", { scale: 0.1, opacity: 0, duration: 0.45, ease: "power3.in" }, 2.45);
// 끝: 기존 아웃트로 첫 프레임으로 정확히 돌아옴
tl.fromTo("#still", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "none", immediateRender: false }, 3.33);
"""
    return page("Rapeech outro v2", body, js, DUR, css,
                audio=f'<audio id="sfx" class="clip" src="assets/pre_sfx.wav" data-start="0" data-duration="{PRE}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    from engine.bgm import SR, add, lowpass, write_wav
    from intro.sfx import bell, pop, sweep
    buf = np.zeros((int(PRE * SR), 2))
    add(buf, sweep(800, 300, 0.7, partials=((1, 1), (2, 0.3)), a=0.08, r=0.2, rise=False), 0.25, 0.04)
    add(buf, pop(760, 380, 0.14), 0.8, 0.08)
    add(buf, sweep(400, 1100, 1.0, partials=((1, 1), (2, 0.2)), a=0.3, r=0.25, rise=True), 1.3, 0.025)
    add(buf, bell(88, 0.9, 0.35), 2.3, 0.12); add(buf, bell(95, 1.2, 0.5), 2.38, 0.11)
    add(buf, sweep(300, 900, 0.6, partials=((1, 1), (2, 0.3)), a=0.06, r=0.15, rise=True), 2.7, 0.035)
    buf = lowpass(buf, 10000)
    buf *= 10 ** (-4 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "outro-v2", [(REPO / "intro" / "out" / "rapeech_outro_16x9.mp4", "outro.mp4")])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a / "outro.mp4"), "-frames:v", "1", str(a / "outro_first.png")], check=True)
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "pre_sfx.wav")
    print("ok")
