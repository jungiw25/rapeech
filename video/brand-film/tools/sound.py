"""브랜드 필름 소리: 배경음악(bed.wav) + 효과음(sfx.wav). 모두 직접 합성(노이즈 없음, 상업 사용 가능).

효과음 시각은 본편 시작(인트로 끝, 12 s) 기준이며 장면 생성기의 타이밍과 맞춘다.
사용법: python3 tools/sound.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent.parent))
from engine.bgm import SR, add, env, hz, lowpass, noise_report, synth, tone, write_wav  # noqa: E402
from intro.sfx import bell, pop, sweep  # noqa: E402

BODY = 66.5          # 본편 + 아웃트로 길이(배경음악)
FLOW = 0.0           # flow 장면 시작(본편 기준)
S08, S09, S10, S11, S12 = 35.0, 40.0, 49.0, 53.0, 57.0
ARR = [9.7, 13.6, 17.2, 20.8, 24.4]
TRV = [12.2, 15.8, 19.4, 23.0]
RET = 30.0


def chime(buf, t, gain=0.16, hi=False):
    """띠링: 위로 오르는 맑은 두 음."""
    a, b = (91, 98) if hi else (88, 95)
    add(buf, bell(a, 0.9, 0.35), t, gain, -0.1)
    add(buf, bell(b, 1.2, 0.5), t + 0.085, gain * 0.95, 0.1)


def whoosh(buf, t, up=True, gain=0.05, dur=0.6):
    f0, f1 = (220, 900) if up else (900, 220)
    add(buf, sweep(f0, f1, dur, partials=((1, 1), (2, 0.3), (3, 0.1)), a=0.08, r=0.15, rise=up), t, gain)


def ringtone(buf, t, gain=0.09):
    notes = [76, 81, 84, 81, 88, 84]
    for r in range(2):
        for i, m in enumerate(notes):
            add(buf, tone(hz(m), 0.22, ((1, 1), (2, 0.25), (4, 0.06)), a=0.004, r=0.08, decay=0.18), t + r * 1.05 + i * 0.1, gain, 0.25)


def build_sfx():
    buf = np.zeros((int((BODY + 1) * SR), 2))
    # 로고 → 점 → 선
    whoosh(buf, FLOW + 1.15, up=False, gain=0.04, dur=1.1)
    add(buf, pop(900, 420, 0.16), FLOW + 2.05, 0.12)
    whoosh(buf, FLOW + 2.95, up=True, gain=0.05, dur=1.2)
    add(buf, pop(700, 350), FLOW + 3.5, 0.10)
    # 전화벨, 고객의 말
    ringtone(buf, FLOW + 6.0)
    add(buf, pop(820, 380), FLOW + 7.8, 0.12, -0.3)
    whoosh(buf, FLOW + 8.5, up=True, gain=0.035, dur=0.9)
    # 단계마다 이동 소리와 띠링
    for t in TRV:
        whoosh(buf, FLOW + t, up=True, gain=0.032, dur=1.2)
    for t in ARR:
        chime(buf, FLOW + t + 0.02)
    # 콜봇 답변, 풀백, 답이 돌아옴, 상담사 연결
    add(buf, pop(980, 420), FLOW + 24.8, 0.11, 0.3)
    whoosh(buf, FLOW + 27.0, up=False, gain=0.05, dur=2.0)
    chime(buf, FLOW + RET + 0.02, gain=0.15, hi=True)
    add(buf, pop(600, 300), FLOW + 29.5, 0.09)
    # 모든 빛이 한 점으로
    whoosh(buf, FLOW + 32.6, up=False, gain=0.05, dur=1.4)
    add(buf, tone(hz(84), 1.6, ((1, 1), (2, 0.12)), a=0.02, r=0.8, decay=0.7), FLOW + 33.6, 0.06)
    # 서버 랙 줌 아웃
    whoosh(buf, S08 + 0.05, up=False, gain=0.06, dur=2.6)
    # 데이터센터 층이 하나씩 내려앉음
    for f, t in enumerate([0.5, 1.75, 3.0, 4.25, 5.5, 6.6]):
        add(buf, tone(hz(43 + f), 0.5, ((1, 1), (2, 0.4), (3, 0.12)), a=0.005, r=0.1, decay=0.2), S09 + t + 0.85, 0.16)
        add(buf, bell(79 + f * 2, 0.6, 0.18), S09 + t + 0.9, 0.035)
    # 지도: 한국 → 미국
    whoosh(buf, S10 + 0.9, up=True, gain=0.04, dur=1.2)
    for i in range(5):
        add(buf, pop(1000 + i * 60, 450), S10 + 1.9 + i * 0.08, 0.06, 0.4)
    # 한 팀: 클라이맥스(영상에서 한 번)
    add(buf, sweep(160, 1300, 1.2, partials=((1, 1), (2, 0.3), (3, 0.1))), S11 + 0.2, 0.07)
    add(buf, tone(hz(36), 1.4, ((1, 1), (2, 0.3)), a=0.005, r=0.5, decay=0.5), S11 + 1.35, 0.32)
    for m in (60, 64, 67, 71, 74):
        add(buf, tone(hz(m + 12), 2.4, ((1, 1), (2, 0.15)), a=0.01, r=0.9, decay=1.2), S11 + 1.35, 0.05)
    # 아웃트로로 모임
    whoosh(buf, S12 + 0.2, up=False, gain=0.045, dur=1.0)
    buf = lowpass(buf, 10000)[: int(BODY * SR)]
    pk = np.abs(buf).max()
    buf *= 10 ** (-3 / 20) / pk
    return buf


if __name__ == "__main__":
    bed = synth(BODY, seed=21, bpm=92)
    write_wav(ROOT / "assets" / "bed.wav", bed)
    sfx = build_sfx()
    write_wav(ROOT / "assets" / "sfx.wav", sfx)
    print("bed noise", round(noise_report(bed), 6), "sfx noise", round(noise_report(sfx), 6))
