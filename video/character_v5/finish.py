"""v5 마감: 장면 전환(섬광·대각선 와이프·번짐), 빛 번짐(블룸), 가장자리 어둡게, 효과음 → mp4.
사용법: python3 video/character_v5/finish.py → out/rapi_v5.mp4
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))
from engine.bgm import SR, synth, write_wav  # noqa: E402

OUT = HERE / "out"
FPS, SEC = 24, 10.0
LIB = REPO / ".claude/skills/media-use/audio/assets/sfx"


def bump(t, a, peak, b):
    """a에서 올라 peak에 1, b에서 0인 부드러운 언덕."""
    if t <= a or t >= b:
        return 0.0
    x = (t - a) / (peak - a) if t < peak else (b - t) / (b - peak)
    return float(np.sin(np.pi / 2 * x) ** 2)


def post(i, im):
    t = i / FPS
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    h, w, _ = a.shape
    # 빛 번짐: 밝은 부분만 흐려 더함
    br = np.clip((a - 0.78) * 3.0, 0, 1)
    glow = np.asarray(Image.fromarray((br * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    a = 1 - (1 - a) * (1 - glow * 0.55)
    # 가장자리 살짝 어둡게
    yy, xx = np.mgrid[0:h, 0:w]
    v = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    a *= (1 - 0.16 * np.clip(v - 0.35, 0, 1))[..., None]
    # 장면 1→2: 눈 반짝임이 흰 빛으로 번짐
    f = bump(t, 1.0, 1.25, 1.5)
    # 장면 4→5: 회전 끝의 흰 번짐
    f = max(f, bump(t, 5.75, 6.0, 6.2) * 0.9)
    # 착지 순간 짧은 섬광
    f = max(f, bump(t, 6.28, 6.33, 6.45) * 0.35)
    if f > 0:
        a = a * (1 - f) + f
    # 장면 2→3: 지팡이 빛줄기가 대각선으로 화면을 가름(와이프)
    if 2.55 < t < 2.95:
        p = (t - 2.55) / 0.4
        d = (xx / w) * 0.75 - (yy / h) * 0.45          # 대각선 좌표
        edge = -0.5 + p * 1.5
        band = np.exp(-((d - edge) / 0.05) ** 2)[..., None]
        col = np.array([0.93, 0.89, 1.0])
        a = a * (1 - band) + col * band
    # 장면 3→4: 오른쪽으로 훅 번짐(가로 흐림 섞기)
    s = bump(t, 4.12, 4.25, 4.4)
    if s > 0:
        bl = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(40 * s) + 1))).astype(np.float32) / 255
        a = a * (1 - s) + bl * s
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def load(n, semis=0.0):
    y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / f"{n}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                                     capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(float)
    if semis:
        r = 2 ** (semis / 12); x = np.arange(int(len(y) / r)) * r
        y = np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(2)], 1)
    return y


def sound(path):
    buf = np.zeros((int((SEC + 3) * SR), 2))

    def put(y, t, g):
        i = int(t * SR); y = y[: len(buf) - i]; buf[i:i + len(y)] += y * g

    put(synth(SEC + 1, seed=7, bpm=120)[: len(buf)], 0, 0.32)
    put(load("click-soft", 4), 0.55, 0.2)            # 눈동자
    put(load("sparkle"), 0.85, 0.45)                 # 눈 반짝
    put(load("whoosh-cinematic", 2), 0.95, 0.3)      # 흰 빛 전환
    put(load("whoosh-short", -3), 1.45, 0.3)         # 웅크림
    put(load("whoosh", 4), 1.75, 0.45)               # 지팡이 번쩍
    put(load("sparkle", 3), 1.95, 0.3)
    put(load("whoosh-cinematic", 4), 2.45, 0.35)     # 대각선 와이프
    for k in range(6):
        put(load("click-soft", -4 + (k % 2) * 2), 2.8 + k * 0.23, 0.22)   # 발걸음
    put(load("whoosh", -2), 2.9, 0.3); put(load("whoosh", 1), 3.6, 0.3)  # 속도
    put(load("whoosh-short", 3), 4.1, 0.35)          # 번짐 전환
    put(load("whoosh", 5), 4.45, 0.45)               # 점프
    put(load("whoosh-cinematic", -1), 4.7, 0.35)     # 회전
    put(load("whoosh-short", 6), 5.7, 0.35)
    put(load("impact-bass-2", -1), 6.28, 0.65)       # 착지
    put(load("pop", -6), 6.33, 0.35)
    put(load("impact-bass-1", 3), 7.0, 0.25)         # 영웅 클로즈업
    put(load("sparkle", 1), 8.6, 0.5)                # 지팡이 끝 반짝
    buf = buf[: int(SEC * SR)]
    fade = np.linspace(1, 0, int(0.7 * SR)); buf[-len(fade):] *= fade[:, None]
    buf *= 10 ** (-1.5 / 20) / np.abs(buf).max()
    write_wav(path, buf)


if __name__ == "__main__":
    pd = OUT / "post"; pd.mkdir(exist_ok=True)
    frames = sorted((OUT / "frames").glob("f_*.png"))
    for i, p in enumerate(frames):
        post(i, Image.open(p)).save(pd / p.name)
    sound(OUT / "sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(pd / "f_%04d.png"), "-i", str(OUT / "sfx.wav"),
                    "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT / "rapi_v5.mp4")], check=True)
    print(OUT / "rapi_v5.mp4")
