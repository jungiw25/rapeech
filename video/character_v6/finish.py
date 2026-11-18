"""v6 마감: 장면 전환(섬광·대각선 와이프·번짐), 빛 번짐(블룸), 가장자리 어둡게, 효과음 → mp4.
사용법: python3 video/character_v6/finish.py → out/rapi_v6.mp4
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
    # 장면 1→2: 눈 반짝임이 흰 빛으로 번짐 / 4→5: 회전 끝 흰 번짐 / 내려찍기 착지 섬광
    f = max(bump(t, 0.95, 1.2, 1.42), bump(t, 5.8, 6.0, 6.2) * 0.9, bump(t, 7.78, 7.83, 7.95) * 0.4)
    if f > 0:
        a = a * (1 - f) + f
    # 장면 2→3: 대각선 빛 와이프
    if 2.42 < t < 2.82:
        p = (t - 2.42) / 0.4
        d = (xx / w) * 0.75 - (yy / h) * 0.45
        band = np.exp(-((d - (-0.5 + p * 1.5)) / 0.05) ** 2)[..., None]
        a = a * (1 - band) + np.array([0.93, 0.89, 1.0]) * band
    # 장면 3→4, 5→6: 가로로 훅 번짐
    s = max(bump(t, 4.08, 4.2, 4.34), bump(t, 7.08, 7.2, 7.34))
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

    put(synth(SEC + 1, seed=11, bpm=124)[: len(buf)], 0, 0.3)
    put(load("click-soft", 4), 0.5, 0.2); put(load("sparkle"), 0.75, 0.45); put(load("whoosh-cinematic", 2), 0.95, 0.3)
    put(load("whoosh-short", -2), 1.45, 0.3)                        # 칼 들어 올림
    put(load("whoosh", 5), 1.74, 0.5); put(load("pop", -3), 1.88, 0.25)   # 내려베기
    put(load("whoosh-cinematic", 4), 2.35, 0.3)                    # 와이프
    for k, t in enumerate((2.8, 3.05, 3.3, 3.55, 3.8)):              # 좌우 베기 + 깡총
        put(load("whoosh-short", 3 + (k % 3)), t - 0.02, 0.4); put(load("click-soft", -5 + k % 2 * 2), t + 0.12, 0.18)
    put(load("whoosh-short", 1), 4.1, 0.3)
    put(load("whoosh-cinematic", 1), 4.4, 0.45); put(load("whoosh", 6), 4.8, 0.3); put(load("whoosh", 3), 5.3, 0.3)   # 회전 베기
    put(load("whoosh-short", 4), 5.8, 0.3)
    for t in (6.16, 6.44, 6.72):                                       # 찌르기
        put(load("whoosh-short", 7), t - 0.03, 0.35); put(load("pop", 2), t + 0.02, 0.3)
    put(load("whoosh-short", 2), 7.1, 0.3)
    put(load("whoosh", 4), 7.38, 0.45)                                # 점프
    put(load("impact-bass-2", -1), 7.78, 0.7); put(load("pop", -6), 7.82, 0.35)   # 내려찍기
    put(load("impact-bass-1", 3), 8.4, 0.2)
    put(load("sparkle", 1), 8.7, 0.5)                                 # 칼끝 반짝
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
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT / "rapi_v6.mp4")], check=True)
    print(OUT / "rapi_v6.mp4")
