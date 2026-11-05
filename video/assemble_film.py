"""회사 소개 영상 최종 조립: 인트로 → 콜봇 흐름 → ConvAI → 네트워크 → 아웃트로(영상만 이어 붙이고 소리는 film_audio.wav 하나).

먼저 각 장면을 렌더하고 python3 video/film_audio.py 로 소리를 만든 뒤 실행한다.
사용법: python3 video/assemble_film.py rapeech_brand_film_v13.mp4
       python3 video/assemble_film.py rapeech_brand_film_v14.mp4 --classic   (기존 효과음·배경음 사용)
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
# 기존 소리(--classic): 장면마다 만든 효과음 + 합성 배경음(bed.wav)을 4.5초부터 깐다
CLASSIC_SFX = [None, (REPO / "video/brand-film/assets/sfx.wav", 0.0), (REPO / "video/convai-samples/b/assets/sfx_b_nobed.wav", 0.0), None, None]
BED = REPO / "video/brand-film-v3b/assets/bed.wav"
A = "aresample=48000,aformat=channel_layouts=stereo"


def main(name, classic=False):
    args, fc = [], []
    for i, (p, s, e) in enumerate(SEGS):
        args += ["-i", str(p)]
        fc.append(f"[{i}:v]fps=60,format=yuv420p,setsar=1,trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
    n = len(SEGS)
    if classic:
        k = n
        for i, (p, s, e) in enumerate(SEGS):
            if CLASSIC_SFX[i]:
                args += ["-i", str(CLASSIC_SFX[i][0])]
                src, a0 = k, CLASSIC_SFX[i][1]
                k += 1
            else:
                src, a0 = i, s
            fc.append(f"[{src}:a]atrim={a0}:{a0 + e - s},asetpts=PTS-STARTPTS,{A}[a{i}]")
        args += ["-i", str(BED)]
        body = sum(e - s for _, s, e in SEGS) - 9.0
        fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][ac]")
        fc.append(f"[{k}:a]atrim=0:{body:.2f},afade=t=in:st=0:d=1.5,afade=t=out:st={body - 2.6:.2f}:d=2.6,volume=0.42,adelay=4500|4500,aresample=48000[bed]")
        fc.append("[ac][bed]amix=inputs=2:duration=first:normalize=0[a]")
        amap = ["-map", "[a]"]
    else:
        fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]")
        args += ["-i", str(AUDIO)]
        amap = ["-map", f"{n}:a", "-shortest"]
    out = REPO / "video/brand-film-v3b/out" / name
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(fc),
                    "-map", "[v]", *amap,
                    "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-r", "60", "-g", "120", "-crf", "14", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(names[0] if names else "rapeech_brand_film.mp4", classic="--classic" in sys.argv)
