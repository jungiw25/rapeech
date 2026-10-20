"""회차 빌드: 검사 → 카드뉴스 → 배경음악 → 숏츠 → 검수 자료.

사용법:
  python3 -m engine.build content/01-ai-dangjik            # 전부
  python3 -m engine.build content/01-ai-dangjik --cards    # 카드뉴스와 검수 이미지만(빠름)
  python3 -m engine.build content/01-ai-dangjik --check    # 문구 검사만
"""
import argparse
import json
import sys
import time
import zlib
from pathlib import Path

from . import bgm, check, render


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--cards", action="store_true", help="카드뉴스와 검수 이미지만")
    ap.add_argument("--check", action="store_true", help="문구 검사만")
    a = ap.parse_args()
    ep = Path(a.episode)
    spec = json.loads((ep / "spec.json").read_text(encoding="utf-8"))
    out = ep / "out"
    out.mkdir(exist_ok=True)

    res = check.check(ep)
    if a.check:
        print(check.report(res))
        sys.exit(1 if any(l == "FAIL" for l, _ in res) else 0)

    t0 = time.time()
    cards, w1 = render.render_cards(spec, out / "cards")
    render.contact_sheet([__import__("PIL.Image", fromlist=["Image"]).open(p) for p in cards],
                         out / "review_cards.jpg", cols=4, thumb_w=300)
    stills = render.shorts_stills(spec, out)
    render.contact_sheet(stills, out / "review_shorts.jpg", cols=5, thumb_w=270)
    print(f"카드뉴스 {len(cards)}장, 검수 이미지 완료 ({time.time() - t0:.0f}초)")
    warns = w1
    video = wav_noise = None
    if not a.cards:
        dur = render.total_duration(spec)
        seed = zlib.crc32(spec["meta"]["id"].encode())
        music = bgm.synth(dur, seed=spec["meta"].get("bgm_seed", seed))
        wav_noise = bgm.noise_report(music)
        bgm.write_wav(out / "bgm.wav", music)
        video = out / "shorts.mp4"
        t1 = time.time()
        _, w2 = render.render_shorts(spec, video, out / "bgm.wav")
        warns += w2
        print(f"숏츠 렌더 완료 ({time.time() - t1:.0f}초)")
    res = check.check(ep, video=video, cards=cards, wav_noise=wav_noise)
    res += [("WARN", "레이아웃: " + x) for x in dict.fromkeys(warns)]
    rep = check.report(res)
    (out / "check.txt").write_text(rep + "\n", encoding="utf-8")
    print(rep)
    sys.exit(1 if any(l == "FAIL" for l, _ in res) else 0)


if __name__ == "__main__":
    main()
