"""회사 소개 영상 2안: 장(章) 구분 화면 3장(각 2.4초, 한 영상에 이어 붙여 렌더한 뒤 잘라 씀).

장마다 로고 그라데이션 면이 왼쪽에서 쓸려 들어와 화면을 덮고, 큰 제목이 왼쪽 정렬로 올라온 뒤,
면이 오른쪽으로 빠지며 다음 장면의 첫 화면이 드러난다.
들어올 때 밑에 깔린 화면 = 앞 장면의 마지막 프레임, 빠질 때 드러나는 화면 = 다음 장면의 첫 프레임이라 이음새가 없다.
  assets/in{k}.png, out{k}.png 는 조립 스크립트가 렌더 결과에서 뽑아 넣는다.
사용법: python3 video/chapters/build.py && cd video/chapters && npx hyperframes render --fps 60 --quality delivery --output out/raw.mp4
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import page, setup_project  # noqa: E402

D = 2.4
CARDS = [("AI 콜봇", "목소리로 시작하는<br>상담"),
         ("ConvAI", "상담사와<br>함께 일하는 AI"),
         ("네트워크 인프라", "대화가 흐르는<br>길까지")]
DUR = D * len(CARDS)
CSS = """
.still { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
.field { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
  background: linear-gradient(115deg, #3c24f3 0%, #a518a4 55%, #ff03c8 100%); }
.kick { position: absolute; left: 160px; top: 330px; overflow: hidden; font-size: 38px; font-weight: 700; color: rgba(255,255,255,.82); padding-bottom: 6px; }
.ttl { position: absolute; left: 152px; top: 400px; overflow: hidden; font-size: 132px; font-weight: 800; line-height: 1.04; letter-spacing: -0.04em; color: #fff; padding-bottom: 12px; }
.kick span, .ttl span { display: inline-block; }
"""


def build():
    body = ""
    for k, (kick, ttl) in enumerate(CARDS):
        body += (f'<img class="still" id="in{k}" src="assets/in{k}.png" />'
                 f'<img class="still" id="out{k}" src="assets/out{k}.png" />'
                 f'<div class="field" id="f{k}"><div class="kick"><span class="t{k}">{kick}</span></div>'
                 f'<div class="ttl"><span class="t{k}">{ttl}</span></div></div>')
    js = f"const D = {D}, N = {len(CARDS)};\n" + """
for (let k = 0; k < N; k++) {
  const t = k * D;
  gsap.set(["#in" + k, "#out" + k, "#f" + k], { opacity: 0 });
  // 앞 장면의 마지막 화면 위로 그라데이션 면이 왼쪽에서 들어옴
  tl.set("#in" + k, { opacity: 1 }, t);
  tl.set("#f" + k, { opacity: 1 }, t);
  tl.fromTo("#f" + k, { clipPath: "inset(0px 1920px 0px 0px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: 0.55, ease: "power3.inOut", immediateRender: false }, t);
  tl.set("#in" + k, { opacity: 0 }, t + 0.56);
  tl.set("#out" + k, { opacity: 1 }, t + 0.56);
  // 제목은 줄 마스크로 올라옴(작은 말 먼저, 큰 제목이 이어서)
  tl.fromTo(".t" + k, { yPercent: 115 }, { yPercent: 0, duration: 0.9, ease: "expo.out", stagger: 0.12, immediateRender: false }, t + 0.32);
  // 면이 오른쪽으로 빠지며 다음 장면의 첫 화면이 드러남
  tl.to("#f" + k, { clipPath: "inset(0px 0px 0px 1920px)", duration: 0.5, ease: "power3.inOut" }, t + D - 0.52);
  tl.set(["#out" + k, "#f" + k], { opacity: 0 }, t + D);
}
"""
    return page("Rapeech chapters", body, js, DUR, CSS,
                audio=f'<audio id="sfx" class="clip" src="assets/ch_sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import sweep
    buf = np.zeros((int((DUR + 1) * SR), 2))
    for k in range(len(CARDS)):
        t = k * D
        add(buf, sweep(240, 820, 0.55, partials=((1, 1), (2, 0.25)), a=0.12, r=0.2, rise=True), t, 0.03)
        for m in (60, 67, 72):
            add(buf, tone(hz(m + (0, 2, -3)[k]), 1.6, ((1, 1), (2, 0.1)), a=0.04, r=1.0, decay=1.4), t + 0.35, 0.03)
        add(buf, sweep(780, 260, 0.5, partials=((1, 1), (2, 0.25)), a=0.08, r=0.2, rise=False), t + D - 0.52, 0.025)
    buf = lowpass(buf, 8000)[: int(DUR * SR)]
    buf *= 10 ** (-8 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "chapters")
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "ch_sfx.wav")
    print("ok")
