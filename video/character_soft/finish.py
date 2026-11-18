"""렌더한 투명 프레임을 그림 배경 위에 얹고 효과음을 붙여 mp4로. 사용법: python3 finish.py → out/rapi4_short.mp4"""
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(REPO))
from compose import background  # noqa: E402
from engine.bgm import SR, synth, write_wav  # noqa: E402

OUT = HERE / "out"
SEC = 6.0
LIB = REPO / ".claude/skills/media-use/audio/assets/sfx"


def load(n, semis=0.0):
    y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / f"{n}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                                     capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(float)
    if semis:
        r = 2 ** (semis / 12)
        x = np.arange(int(len(y) / r)) * r
        y = np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(2)], 1)
    return y


def sound(path):
    buf = np.zeros((int((SEC + 3) * SR), 2))

    def put(y, t, g):
        i = int(t * SR); y = y[: len(buf) - i]; buf[i:i + len(y)] += y * g

    put(synth(SEC + 1, seed=5, bpm=104)[: len(buf)], 0, 0.3)
    put(load("whoosh", 3), 0.0, 0.35)              # 떨어짐
    put(load("impact-bass-1", 2), 0.42, 0.45)       # 착지
    put(load("pop", -4), 0.45, 0.3)
    put(load("click-soft", 5), 1.2, 0.2); put(load("click-soft", 3), 1.8, 0.2)   # 두리번
    put(load("whoosh-short", 4), 2.35, 0.3)         # 팔 번쩍
    put(load("sparkle"), 2.85, 0.4)                 # 말풍선 등장
    for i in range(3):
        put(load("pop", 4 + i * 2), 3.75 + i * 0.25, 0.22)    # 점 세 개
    for i in range(3):
        put(load("pop", 6 + i * 2), 5.15 + i * 0.25, 0.18)
    buf = buf[: int(SEC * SR)]
    fade = np.linspace(1, 0, int(0.6 * SR)); buf[-len(fade):] *= fade[:, None]
    buf *= 10 ** (-2 / 20) / np.abs(buf).max()
    write_wav(path, buf)


if __name__ == "__main__":
    background(1280, 720).convert("RGB").save(OUT / "anim_bg.png")
    sound(OUT / "anim_sfx.wav")
    # 바닥 그림자(검은 반투명)만 보랏빛으로 옅게(캐릭터의 진한 눈·눈썹은 불투명이라 건드리지 않음)
    from PIL import Image
    tint = OUT / "frames_t"; tint.mkdir(exist_ok=True)
    for p in sorted((OUT / "frames").glob("f_*.png")):
        a_ = np.asarray(Image.open(p).convert("RGBA")).copy()
        m = (a_[..., 3] > 0) & (a_[..., 3] < 250) & (a_[..., :3].astype(int).sum(-1) < 60)
        a_[m, :3] = (96, 66, 190); a_[m, 3] = (a_[m, 3] * 0.6).astype(np.uint8)
        Image.fromarray(a_).save(tint / p.name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "24", "-i", str(OUT / "anim_bg.png"),
                    "-framerate", "24", "-i", str(OUT / "frames_t/f_%04d.png"), "-i", str(OUT / "anim_sfx.wav"),
                    "-filter_complex", "[0:v][1:v]overlay=shortest=1,scale=1920:1080:flags=lanczos,format=yuv420p[v]",
                    "-map", "[v]", "-map", "2:a", "-shortest", "-r", "24", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT / "rapi4_short.mp4")], check=True)
    print(OUT / "rapi4_short.mp4")
