"""회사 소개 영상 최종 조립: 인트로 → 콜봇 흐름 → ConvAI → 네트워크 → 아웃트로(영상만 이어 붙이고 소리는 film_audio.wav 하나).

먼저 각 장면을 렌더하고 python3 video/film_audio.py 로 소리를 만든 뒤 실행한다.
사용법: python3 video/assemble_film.py rapeech_brand_film_v13.mp4
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEGS = [  # (파일, 시작, 끝)
    (REPO / "intro/out/rapeech_intro_logo_16x9.mp4", 0.0, 4.5),
    (REPO / "video/brand-film/out/raw.mp4", 12.0, 44.6),
    (REPO / "video/convai-samples/b/out/raw.mp4", 0.0, 28.0),
    (REPO / "video/brand-film-v3b/out/rest.mp4", 5.6, 29.6),
    (REPO / "intro/out/rapeech_outro_v4_16x9.mp4", 0.0, 4.5),
]
AUDIO = REPO / "video/brand-film-v3b/assets/film_audio.wav"


def main(name):
    args, fc = [], []
    for i, (p, s, e) in enumerate(SEGS):
        args += ["-i", str(p)]
        fc.append(f"[{i}:v]fps=60,format=yuv420p,setsar=1,trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0[v]")
    out = REPO / "video/brand-film-v3b/out" / name
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-i", str(AUDIO), "-filter_complex", ";".join(fc),
                    "-map", "[v]", "-map", f"{len(SEGS)}:a", "-shortest",
                    "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-r", "60", "-g", "120", "-crf", "14", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rapeech_brand_film.mp4")
