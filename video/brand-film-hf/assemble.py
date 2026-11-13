"""A안 전체 영상 조립: 인트로 → 콜봇 흐름 → ConvAI → 네트워크 → 아웃트로. 소리는 v16과 같은 기존 효과음·배경음.
사용법: python3 video/brand-film-hf/assemble.py rapeech_brand_film_A1.mp4
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "video"))
import assemble_film as AF  # noqa: E402

AF.SEGS = [
    AF.SEGS[0],
    (HERE / "full/flow/out/raw.mp4", 0.0, 32.6),
    (HERE / "full/convai/out/raw.mp4", 0.0, 28.0),
    (HERE / "full/rest/out/raw.mp4", 5.6, 29.6),
    (HERE / "full/outro/out/raw.mp4", 0.0, 4.5),
]

if __name__ == "__main__":
    name = sys.argv[1]
    AF.main(name, classic=True)
    (HERE / "out").mkdir(exist_ok=True)
    shutil.move(REPO / "video/brand-film-v3b/out" / name, HERE / "out" / name)
    print(HERE / "out" / name)
