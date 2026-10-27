"""아웃트로 v3(15초): 영상을 마무리하는 사인오프 + 유튜브 최종 화면(엔드 스크린)용 여백.

  0.0– 0.3 어두운 화면(어떤 영상 뒤에 붙여도 자연스럽게)
  0.3– 1.4 가운데에 가는 선이 그어짐(대화가 끝나는 한 줄)
  1.3– 2.4 선에서 빛이 위아래로 열림(밝은 바탕)
  2.0– 3.4 로고가 아래에서 올라오고, 영문 태그라인이 이어짐
  4.6– 5.6 로고가 화면 위쪽 1/3로 올라감 → 아래쪽 절반은 유튜브 최종 화면 요소(구독, 다음 영상) 자리
  5.6–15.0 아주 느린 배경 빛 + 화면 맨 아래 가는 진행선(끝나 감을 알림)
유튜브 최종 화면은 영상 끝 5~20초에 넣을 수 있다. 이 아웃트로는 마지막 10초를 그 자리로 비워 둔다.
사용법: python3 video/outro-v3/build.py && cd video/outro-v3 && npx hyperframes render --fps 60 --quality delivery --output out/raw.mp4
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from kit_v2 import REPO, page, setup_project  # noqa: E402

DUR = 15.0
LW = 620                       # 로고 너비(244 x 90 비율)
LH = LW * 90 / 244


def build():
    body = f'''<div id="dark" class="layer" style="background:#0c0916"></div>
<div id="lightwrap" class="layer"><div id="light" class="layer" style="background:#faf9fd"></div>
  <div id="b1" class="blob" style="left:-260px;top:420px;width:1100px;height:900px;background:radial-gradient(closest-side,rgba(255,79,216,.13),rgba(255,79,216,0))"></div>
  <div id="b2" class="blob" style="left:1100px;top:-260px;width:1100px;height:900px;background:radial-gradient(closest-side,rgba(106,77,255,.14),rgba(106,77,255,0))"></div></div>
<div id="line" style="position:absolute;left:{960 - 520}px;top:539px;width:1040px;height:2px;background:linear-gradient(90deg,rgba(255,3,200,0),#ff4fd8 18%,#b25cff 50%,#6a5cff 82%,rgba(60,36,243,0))"></div>
<div id="brand" style="position:absolute;left:0;top:0;width:1920px;height:1080px">
  <div id="logoMask" style="position:absolute;left:{960 - LW / 2:.0f}px;top:{540 - LH / 2 - 30:.0f}px;width:{LW}px;height:{LH + 6:.0f}px;overflow:hidden">
    <img id="logo" src="assets/logo.svg" style="position:absolute;left:0;top:0;width:{LW}px;height:{LH:.0f}px" /></div>
  <div id="tagw" style="position:absolute;left:0;top:{540 + LH / 2 + 4:.0f}px;width:1920px;text-align:center;overflow:hidden">
    <span id="tag" style="display:inline-block;font-size:26px;font-weight:600;letter-spacing:.2em;color:#4a4170">Conversational AI&nbsp;&nbsp;·&nbsp;&nbsp;Network Infrastructure</span></div>
</div>
<div id="prog" style="position:absolute;left:0;top:1072px;width:1920px;height:3px;background:linear-gradient(90deg,#ff4fd8,#b25cff 50%,#6a5cff);transform-origin:0 50%;opacity:.55"></div>'''
    css = ".blob { position: absolute; border-radius: 50%; }"
    js = """
gsap.set(["#lightwrap", "#brand", "#prog"], { opacity: 0 });
gsap.set("#lightwrap", { clipPath: "inset(540px 0px 540px 0px)" });
// ── 가운데에 가는 선
tl.fromTo("#line", { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 1.1, ease: "power2.inOut" }, 0.3);
// ── 선에서 빛이 위아래로 열림
FIN("#lightwrap", 1.3, 0.01, "none");
tl.fromTo("#lightwrap", { clipPath: "inset(540px 0px 540px 0px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: 1.1, ease: "power3.inOut", immediateRender: false }, 1.3);
tl.to("#line", { opacity: 0, duration: 0.5, ease: "sine.inOut" }, 1.9);
// ── 로고가 아래에서 올라오고 태그라인이 이어짐
FIN("#brand", 2.0, 0.01, "none");
tl.fromTo("#logo", { yPercent: 105 }, { yPercent: 0, duration: 1.2, ease: "expo.out" }, 2.05);
tl.fromTo("#tag", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 1.0, ease: "expo.out", immediateRender: false }, 2.6);
// ── 로고가 위쪽 1/3로: 아래 절반은 유튜브 최종 화면 자리
tl.to("#brand", { y: -250, scale: 0.8, transformOrigin: "960px 540px", duration: 1.1, ease: "power3.inOut" }, 4.6);
// ── 아주 느린 배경 빛 + 진행선
tl.fromTo("#b1", { x: 0, y: 0 }, { x: 220, y: -120, duration: 13, ease: "sine.inOut" }, 2.0);
tl.fromTo("#b2", { x: 0, y: 0 }, { x: -260, y: 140, duration: 13, ease: "sine.inOut" }, 2.0);
FIN("#prog", 5.6, 0.5);
tl.fromTo("#prog", { scaleX: 0 }, { scaleX: 1, duration: 9.4, ease: "none" }, 5.6);
"""
    return page("Rapeech outro v3", body, js, DUR, css,
                audio=f'<audio id="sfx" class="clip" src="assets/outro_sfx.wav" data-start="0" data-duration="{DUR}" data-track-index="2" data-volume="1"></audio>')


def sound(out):
    from engine.bgm import SR, add, hz, lowpass, tone, write_wav
    from intro.sfx import bell, sweep
    buf = np.zeros((int((DUR + 1) * SR), 2))
    add(buf, sweep(260, 780, 1.1, partials=((1, 1), (2, 0.3)), a=0.2, r=0.3, rise=True), 0.3, 0.035)
    add(buf, sweep(300, 1200, 1.2, partials=((1, 1), (2, 0.2)), a=0.3, r=0.4, rise=True), 1.3, 0.03)
    # 로고: 따뜻한 화음 + 띠링, 길게 남음
    for m in (60, 64, 67, 72, 76):
        add(buf, tone(hz(m), 5.5, ((1, 1), (2, 0.12)), a=0.02, r=3.0, decay=3.5), 2.1, 0.035)
    add(buf, tone(hz(36), 2.0, ((1, 1), (2, 0.3)), a=0.01, r=1.0, decay=1.0), 2.1, 0.18)
    add(buf, bell(88, 1.2, 0.5), 2.15, 0.1); add(buf, bell(95, 1.6, 0.7), 2.25, 0.09)
    # 남은 시간: 아주 옅은 지속음이 서서히 사라짐
    for m in (67, 72, 79):
        add(buf, tone(hz(m), 9.0, ((1, 1),), a=1.5, r=5.0, decay=8.0), 5.5, 0.012)
    buf = lowpass(buf, 9000)[: int(DUR * SR)]
    fade = np.linspace(1, 0, int(1.5 * SR))
    buf[-len(fade):] *= fade[:, None]
    buf *= 10 ** (-4 / 20) / np.abs(buf).max()
    write_wav(out, buf)


if __name__ == "__main__":
    a = setup_project(HERE, "outro-v3", [(REPO / "brand" / "ko" / "logotype" / "ko_logo_purple.svg", "logo.svg")])
    (HERE / "index.html").write_text(build(), encoding="utf-8")
    sound(a / "outro_sfx.wav")
    print("ok")
