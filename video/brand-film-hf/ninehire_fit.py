"""나인하이어 홈 첫 화면용: 영상 내용을 74%로 줄여 가운데보다 조금 아래에 둔다(화면이 잘려도 내용이 보이게).
홈 첫 화면은 영상을 '창 너비 x (창 높이 - 60px)' 상자에 꽉 채우고 넘치는 위아래를 자른다(실측: 노트북에서 높이의 77~83%만 보임).
바깥 여백은 안쪽 화면의 가장자리 색을 바깥으로 늘여 크게 흐린 것으로 채우고(바탕의 밝기 변화가 끊기지 않게), 안쪽 화면의 가장자리는 부드럽게 녹인다.
사용법: python3 video/brand-film-hf/ninehire_fit.py <입력.mp4> <출력.mp4>
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

K = 0.74
OFFY = 40            # 안쪽 화면을 아래로 내려 위쪽(메뉴 바로 아래) 여유를 더 둠
W, H = 1920, 1080
w, h = int(W * K) // 2 * 2, int(H * K) // 2 * 2
FX, FY = 60, 44          # 가장자리를 녹이는 폭

src, dst = sys.argv[1], sys.argv[2]
mask = Path(dst).with_suffix(".mask.png")
x = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / FX, 0, 1)
y = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / FY, 0, 1)
s = lambda t: t * t * (3 - 2 * t)
Image.fromarray((np.outer(s(y), s(x)) * 255).astype(np.uint8), "L").save(mask)
fc = (f"[0:v]split[a][b];[a]scale=364:206:flags=area,pad=480:270:58:32,fillborders=left=58:right=58:top=32:bottom=32:mode=smear,gblur=sigma=14,scale={W}:{H}:flags=bicubic[bg];"
      f"[b]scale={w}:{h}:flags=lanczos,format=yuva444p[fg];[1:v]format=gray[m];[fg][m]alphamerge[fa];"
      f"[bg][fa]overlay={(W - w) // 2}:{(H - h) // 2 + OFFY}:format=auto,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-framerate", "60", "-i", str(mask), "-filter_complex", fc, "-map", "[v]", "-map", "0:a?", "-shortest",
                "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-r", "60", "-g", "120", "-crf", "16", "-preset", "slow", "-c:a", "copy", "-movflags", "+faststart", dst], check=True)
mask.unlink()
print(dst)
