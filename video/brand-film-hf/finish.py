"""시안 영상에 효과음을 붙인다. 사용법: python3 video/brand-film-hf/finish.py → out/pilot_A.mp4, out/pilot_C.mp4"""
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))
from engine.bgm import SR, write_wav  # noqa: E402

LIB = REPO / ".claude/skills/media-use/audio/assets/sfx"
SEC = 8.4


def load(n, semis=0.0):
    y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / f"{n}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                                     capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(float)
    if semis:
        r = 2 ** (semis / 12); x = np.arange(int(len(y) / r)) * r
        y = np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(2)], 1)
    return y


def sound(path, soft):
    buf = np.zeros((int((SEC + 3) * SR), 2))

    def put(n, t, g, s=0.0):
        y = load(n, s); i = int(t * SR); y = y[: len(buf) - i]; buf[i:i + len(y)] += y * g

    put("pop", 0.68 if soft else 0.5, 0.3, -5)                 # 캐릭터 등장
    put("whoosh-short", 0.95, 0.22, -2)                        # 선
    put("pop", 1.4, 0.2, 2); put("pop", 1.4 + (0.42 if soft else 0.3), 0.2, 5)   # 단추
    put("click-soft", 2.85, 0.25, 4); put("click-soft", 3.65, 0.25, 4)            # 전화
    put("pop", 4.0, 0.3, 0)                                    # 말풍선
    put("whoosh-short", 5.45, 0.2, 3)                          # 목소리 이동
    put("pop", 6.34, 0.35, -3); put("sparkle", 6.4, 0.18)      # 도착
    for k in range(12):
        put("click-soft", 6.85 + k * 0.058, 0.09, 6 + (k % 3))  # 글자
    buf2 = buf[: int(SEC * SR)]
    buf2 *= 10 ** (-6 / 20) / np.abs(buf2).max()
    write_wav(path, buf2)


if __name__ == "__main__":
    out = HERE / "out"; out.mkdir(exist_ok=True)
    for k, name in (("a", "pilot_A_clay"), ("c", "pilot_C_flat")):
        wav = out / f"{k}.wav"; sound(wav, k == "a")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / k / "out/raw.mp4"), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(out / f"{name}.mp4")], check=True)
        print(out / f"{name}.mp4")
