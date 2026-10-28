"""회사 소개 영상 2안 조립: 인트로 → [장1] → 콜봇 흐름 → [장2] → ConvAI → 9칸이 한 점으로 → [장3] → 네트워크 → 아웃트로.

장 구분 화면의 밑그림(들어올 때·빠질 때 화면)을 렌더 결과에서 뽑아 넣고, 장 구분 화면을 렌더한 뒤 하나로 잇는다.
사용법: python3 video/chapters/assemble.py [출력 파일 이름]
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
INTRO = REPO / "intro/out/rapeech_intro_logo_16x9.mp4"
OUTRO = REPO / "intro/out/rapeech_outro_v4_16x9.mp4"
FLOW = REPO / "video/brand-film/out/raw.mp4"
FLOW_SFX = REPO / "video/brand-film/assets/sfx.wav"
CONV = REPO / "video/convai-samples/b/out/raw.mp4"
CONV_SFX = REPO / "video/convai-samples/b/assets/sfx_b_nobed.wav"
REST = REPO / "video/brand-film-v3b/out/rest.mp4"
BED = REPO / "video/brand-film-v3b/assets/bed.wav"
CH = HERE / "out/raw.mp4"

FLOW0, FLOW1 = 12.0 + 1.2, 12.0 + 32.6   # 로고 글자가 사라진 뒤부터(심볼이 점으로 줄어드는 중)
CONV0, CONV1 = 1.1, 28.0                  # 앞 장면 사진이 다 사라진 뒤부터
REST0, REST_SPLIT, REST1 = 5.6, 7.45, 29.6  # 7.45초: 9칸이 다 모여 점 하나만 남은 순간 → 장3
D = 2.4


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True)


def still(src, t, out, sseof=False):
    ff(*(["-sseof", "-0.02"] if sseof else ["-ss", f"{t:.3f}"]), "-i", src, "-frames:v", "1", "-update", "1", out)


def main(name):
    a = HERE / "assets"
    still(INTRO, 0, a / "in0.png", sseof=True)
    still(FLOW, FLOW0, a / "out0.png")
    still(FLOW, FLOW1 - 1 / 60, a / "in1.png")
    still(CONV, CONV0, a / "out1.png")
    still(REST, REST_SPLIT, a / "in2.png")
    still(REST, REST_SPLIT, a / "out2.png")
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
    subprocess.run([sys.executable, str(HERE / "build.py")], check=True)
    subprocess.run(["npx", "hyperframes", "render", "--fps", "60", "--quality", "delivery", "--output", "out/raw.mp4"], cwd=HERE, env=env, check=True,
                   stdout=subprocess.DEVNULL)

    V = "fps=60,format=yuv420p,setsar=1"
    A = "aresample=48000,aformat=channel_layouts=stereo"
    segs = [  # (영상 입력, 시작, 끝, 소리 입력 또는 None=영상의 소리, 소리 시작)
        (0, 0, 4.5, None, 0),
        (1, 0, D, None, 0),
        (2, FLOW0, FLOW1, 3, FLOW0 - 12.0),
        (1, D, 2 * D, None, D),
        (4, CONV0, CONV1, 5, CONV0),
        (6, REST0, REST_SPLIT, None, REST0),
        (1, 2 * D, 3 * D, None, 2 * D),
        (6, REST_SPLIT, REST1, None, REST_SPLIT),
        (7, 0, 4.5, None, 0),
    ]
    inputs = [INTRO, CH, FLOW, FLOW_SFX, CONV, CONV_SFX, REST, OUTRO, BED]
    fc, cat = [], ""
    for i, (vi, s, e, ai, as_) in enumerate(segs):
        fc.append(f"[{vi}:v]{V},trim={s:.4f}:{e:.4f},setpts=PTS-STARTPTS[v{i}]")
        src = vi if ai is None else ai
        fc.append(f"[{src}:a]atrim={as_:.4f}:{as_ + e - s:.4f},asetpts=PTS-STARTPTS,{A}[a{i}]")
        cat += f"[v{i}][a{i}]"
    total = sum(e - s for _, s, e, _, _ in segs)
    bed = total - 9.0
    fc.append(f"{cat}concat=n={len(segs)}:v=1:a=1[v][ac]")
    fc.append(f"[8:a]atrim=0:{bed:.3f},afade=t=in:st=0:d=1.5,afade=t=out:st={bed - 2.6:.3f}:d=2.6,volume=0.42,adelay=4500|4500,aresample=48000[bed]")
    fc.append("[ac][bed]amix=inputs=2:duration=first:normalize=0[a]")
    args = []
    for p in inputs:
        args += ["-i", p]
    out = REPO / "video/brand-film-v3b/out" / name
    ff(*args, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-level", "4.2",
       "-r", "60", "-g", "120", "-crf", "14", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out)
    print(out, f"{total:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rapeech_brand_film_2an.mp4")
