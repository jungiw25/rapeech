"""아웃트로 v4(4.5초, 인트로와 같은 길이).

첫 화면: 어두운 바탕 가운데의 라피치 심볼(회사 소개 영상의 마지막 장면에서 교집합이 바뀐 그 모습 그대로)
  0.2–1.3 심볼 자리에서 밝은 빛이 원형으로 퍼짐
  0.4–1.5 심볼이 로고 속 제자리로 이동하며 커짐
  1.5–2.4 로고 글자와 태그라인이 왼쪽에서 오른쪽으로 드러남
  2.4–4.5 정지(마지막 프레임 = 인트로 마지막 프레임, 로고 가운데)
사용법: python3 video/outro-v4/build.py && cd video/outro-v4 && npx hyperframes render --fps 60 --quality delivery --output out/raw.mp4
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import FILM, page, setup_project  # noqa: E402

DUR = 4.5
SYM_S = 1920 * 0.5 / 314
SYM_X, SYM_Y = 960 - 122 * SYM_S, 540 - 45 * SYM_S - 40
SYM_W, SYM_H = 84 * SYM_S, 90 * SYM_S


def build():
    body = f'''<div id="dark" class="layer" style="background:#0c0916"></div>
<div id="vigL" class="layer vig"></div>
<div id="light" class="layer" style="background:#faf9fd"></div>
<img id="last" class="layer" src="assets/intro_last.png" />
<img id="sym" src="assets/symbol_purple.svg" style="position:absolute;left:{960 - 75}px;top:{540 - 80.36:.2f}px;width:150px;height:160.71px" />'''
    tx, ty = SYM_X + SYM_W / 2 - 960, SYM_Y + SYM_H / 2 - 540
    js = f"""
gsap.set("#light", {{ clipPath: "circle(0px at 960px 540px)" }});
gsap.set("#last", {{ opacity: 0 }});
// 심볼 자리에서 빛이 퍼짐
tl.fromTo("#light", {{ clipPath: "circle(0px at 960px 540px)" }}, {{ clipPath: "circle(1250px at 960px 540px)", duration: 1.1, ease: "power2.inOut", immediateRender: false }}, 0.2);
FOUT("#vigL", 0.6, 0.6);
// 심볼이 로고 속 제자리로
tl.to("#sym", {{ x: {tx:.2f}, y: {ty:.2f}, scale: {SYM_W / 150:.4f}, transformOrigin: "50% 50%", duration: 1.1, ease: "power3.inOut" }}, 0.4);
// 로고 글자·태그라인이 부드럽게 나타남(심볼은 이미 제자리에 겹쳐 있음)
tl.fromTo("#last", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.9, ease: "sine.inOut", immediateRender: false }}, 1.45);
tl.to("#sym", {{ opacity: 0, duration: 0.4, ease: "sine.inOut" }}, 2.3);
"""
    return page("Rapeech outro v4", body, js, DUR, "",
                audio=f'<audio id="sfx" class="clip" src="assets/outro_sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, sweep
    buf = np.zeros((int((DUR + 1) * SR), 2))
    add(buf, sweep(300, 1200, 1.1, partials=((1, 1), (2, 0.2)), a=0.3, r=0.4, rise=True), 0.2, 0.03)
    for m in (60, 64, 67, 72, 76):
        add(buf, tone(hz(m), 3.2, ((1, 1), (2, 0.12)), a=0.02, r=1.8, decay=2.0), 1.5, 0.035)
    add(buf, tone(hz(36), 1.8, ((1, 1), (2, 0.3)), a=0.01, r=0.9, decay=0.9), 1.5, 0.16)
    add(buf, bell(88, 1.2, 0.5), 1.55, 0.1); add(buf, bell(95, 1.6, 0.7), 1.65, 0.09)
    buf = lowpass(buf, 9000)[: int(DUR * SR)]
    fade = np.linspace(1, 0, int(0.8 * SR))
    buf[-len(fade):] *= fade[:, None]
    buf *= 10 ** (-4 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "outro-v4", [(FILM / "assets" / "intro_last.png", "intro_last.png"),
                                         (FILM / "assets" / "brand" / "symbol_purple.svg", "symbol_purple.svg")])
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "outro_sfx.wav")
    print("ok")
