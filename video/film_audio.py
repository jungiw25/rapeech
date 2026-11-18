"""회사 소개 영상 전체 소리(배경음악 + 효과음)를 한 번에 만든다.

- 배경음악: 아이오와 대학 악기 샘플(MIS, "어떤 프로젝트에도 제한 없이 사용 가능")의 실제 피아노 소리로 장면 흐름에 맞춰 작곡
  · 1부(콜봇 흐름): 드문드문 펼친화음 / 2부(ConvAI): 화음이 넓어지고 낮은 현 패드 / 3부(네트워크): 잔잔한 8분 박동 → 벤다이어그램에서 정점
  · 마디마다 셈여림·타이밍·음 배치를 조금씩 바꿔 같은 소리가 똑같이 반복되지 않게
- 효과음: hyperframes media-use 스킬에 들어 있는 실제 녹음 효과음(Pixabay 라이선스, 상업 사용 가능, 출처 표기 불필요)
  · 같은 종류도 여러 파일을 번갈아 쓰고 음높이·크기를 조금씩 바꿈
  · 단계가 켜지는 '띠링'은 지금 흐르는 화음의 피아노 음으로 내서 음악과 어울리게
인트로·아웃트로 구간은 각 영상의 원래 소리를 그대로 쓴다.
사용법: python3 video/film_audio.py → video/brand-film-v3b/assets/film_audio.wav
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from engine.bgm import SR, hz, lowpass, write_wav  # noqa: E402

PIANO = REPO / "video/audio_src/piano"
SFX = REPO / ".claude/skills/media-use/audio/assets/sfx"
INTRO = REPO / "intro/out/rapeech_intro_logo_16x9.mp4"
OUTRO = REPO / "intro/out/rapeech_outro_v4_16x9.mp4"
OUT = REPO / "video/brand-film-v3b/assets/film_audio.wav"

# 영상 구간(초): 인트로 0–4.5 / 콜봇 흐름 4.5–37.1 / ConvAI 37.1–65.1 / 네트워크 65.1–89.1 / 아웃트로 89.1–93.6
F, B, R = 4.5, 37.1, 65.1 - 5.6          # 각 장면 시각 → 영상 시각으로 바꿀 때 더하는 값
END_BODY, TOTAL = 89.1, 93.6
rng = np.random.default_rng(7)


def decode(path, start=None, dur=None):
    a = ["ffmpeg", "-v", "error"] + (["-ss", str(start)] if start is not None else []) + ["-i", str(path)]
    a += (["-t", str(dur)] if dur else []) + ["-vn", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(a, check=True, capture_output=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)


def place(buf, y, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(y) <= 0:
        return
    y = y[: len(buf) - i] * gain
    buf[i:i + len(y), 0] += y[:, 0] * (1 - max(0, pan))
    buf[i:i + len(y), 1] += y[:, 1] * (1 + min(0, pan))


def shift(y, semis):
    """음높이 바꾸기(재표본화)."""
    if abs(semis) < 1e-3:
        return y
    r = 2 ** (semis / 12)
    n = int(len(y) / r)
    x = np.arange(n) * r
    return np.stack([np.interp(x, np.arange(len(y)), y[:, c]) for c in range(2)], 1)


# ───────────────────────────── 피아노
NAMES = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
SAMPLES = {}


def fetch_piano():
    """샘플이 없으면 아이오와 대학 MIS에서 받는다(약 190 MB, 저장소에는 올리지 않음)."""
    PIANO.mkdir(parents=True, exist_ok=True)
    for n in ("C2 Eb2 Gb2 A2 C3 Eb3 Gb3 A3 C4 Eb4 Gb4 A4 C5 Eb5 Gb5 A5 C6 Eb6").split():
        for v in ("mf", "pp"):
            f = PIANO / f"Piano.{v}.{n}.aiff"
            if not f.exists():
                subprocess.run(["curl", "-sS", "-m", "180", "-o", str(f),
                                f"https://theremin.music.uiowa.edu/sound%20files/MIS/Piano_Other/piano/{f.name}"], check=True)


def load_piano():
    fetch_piano()
    for p in sorted(PIANO.glob("Piano.*.aiff")):
        _, dyn, note = p.stem.split(".")
        midi = 12 * (int(note[-1]) + 1) + NAMES[note[:-1]]
        y = decode(p)
        on = np.argmax(np.abs(y).max(1) > 0.004)          # 녹음 앞의 빈 구간 자르기
        y = y[max(0, on - 48): on + int(9 * SR)]
        y *= np.r_[np.ones(len(y) - 4800), np.linspace(1, 0, 4800)][:, None]
        SAMPLES[(dyn, midi)] = y / (np.abs(y).max() + 1e-9)


def piano(midi, vel, dur):
    """vel 0~1. dur 뒤에는 댐퍼처럼 0.35초에 걸쳐 줄어듦."""
    dyn = "pp" if vel < 0.45 else "mf"
    src = min((m for d, m in SAMPLES if d == dyn), key=lambda m: abs(m - midi))
    y = shift(SAMPLES[(dyn, src)], midi - src)
    n = min(len(y), int((dur + 0.35) * SR))
    y = y[:n].copy()
    k = int(dur * SR)
    if k < n:
        y[k:] *= np.linspace(1, 0, n - k)[:, None]
    g = (0.35 + 0.65 * vel) * (0.55 if dyn == "pp" else 0.8)
    return y * g


def pad(midis, dur, a=1.6, r=2.2):
    """낮은 현 같은 패드: 배음이 적은 톱니파 여러 개를 살짝 어긋나게 겹쳐 아주 어둡게 거름."""
    n = int((dur + r) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for m in midis:
        f = hz(m)
        for d in (-0.06, 0.0, 0.07):
            ph = rng.random() * 6.28
            for h, amp in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.09)):
                y += amp * np.sin(2 * np.pi * f * (1 + d / 100) * h * t + ph * h)
    e = np.minimum(1, t / a) * np.clip((dur + r - t) / r, 0, 1)
    y = y * e / (len(midis) * 3)
    y = lowpass(np.stack([y, np.roll(y, 240)], 1), 1600)
    return y


def reverb(x, sec=2.6, wet=0.22):
    n = int(sec * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 3.2)[:, None]
    ir = lowpass(ir, 5200)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0))
    L = len(x) + n
    N = 1 << (L - 1).bit_length()
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], N) * np.fft.rfft(ir[:, c], N), N)[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 3.0


# ───────────────────────────── 곡(84 BPM, C장조)
BEAT = 60 / 84
BAR = 4 * BEAT
# (근음, 오른손 화음 음들) — 마디 단위. 1부 → 2부 → 3부
CH = {
    "C": (36, [64, 67, 71, 74]), "Am": (33, [64, 67, 69, 72]), "F": (29, [65, 69, 72, 76]), "G": (31, [62, 67, 71, 74]),
    "Gs": (31, [62, 65, 67, 72]), "Em": (28, [64, 67, 71, 74]), "Dm": (26, [62, 65, 69, 72]), "CE": (28, [64, 67, 72, 76]),
}
PROG = (["C", "C", "Am", "Am", "F", "F", "Gs", "G", "C", "Am", "F", "G"]          # 1부 4.5–38.8
        + ["F", "G", "Em", "Am", "F", "G", "CE", "CE", "Dm", "Gs"]                 # 2부 38.8–67.4
        + ["F", "G", "Am", "Em", "F", "G", "C", "C", "C"])                         # 3부 67.4–
T0 = F


def chord_at(t):
    i = int((t - T0) // BAR)
    return CH[PROG[max(0, min(len(PROG) - 1, i))]]


def score(buf):
    for i, name in enumerate(PROG):
        t = T0 + i * BAR
        if t > END_BODY + 1:
            break
        root, rh = CH[name]
        part = 1 if t < B + 1.5 else (2 if t < R + 5.6 + 2.3 else 3)
        hum = lambda: rng.normal(0, 0.012)
        # 왼손: 근음(2·3부는 옥타브)
        place(buf, piano(root + 12, 0.42 + 0.06 * part, BAR * 0.95), t + hum(), 0.55, -0.15)
        if part >= 2:
            place(buf, piano(root + 24, 0.32, BAR * 0.9), t + BEAT * 2 + hum(), 0.32, -0.1)
        # 오른손: 1부는 드문 펼친화음, 2부는 촘촘히, 3부는 8분 박동
        if part == 1:
            pat = rng.permutation(rh)[: 3] if i % 2 else rh[::-1][:3]
            for k, m in enumerate(pat):
                if rng.random() < 0.85:
                    place(buf, piano(m, 0.28 + 0.12 * rng.random(), BEAT * 1.6), t + (k * 1.25 + 0.5) * BEAT + hum(), 0.42, 0.15)
        elif part == 2:
            seq = rh + [rh[1] + 12] if i % 2 == 0 else [rh[2], rh[0], rh[3], rh[1]]
            for k, m in enumerate(seq):
                place(buf, piano(m, 0.32 + 0.15 * rng.random(), BEAT * 1.1), t + k * BEAT * (0.98 + 0.04 * rng.random()) + hum(), 0.4, 0.2 - 0.1 * k)
        else:
            for k in range(8):
                m = rh[[0, 2, 1, 3, 0, 2, 3, 1][k] if i % 2 else [1, 3, 0, 2, 1, 0, 3, 2][k]]
                accent = 0.42 if k % 4 == 0 else 0.26
                place(buf, piano(m + (12 if k == 7 and i % 3 == 2 else 0), accent + 0.08 * rng.random(), BEAT * 0.6),
                      t + k * BEAT / 2 + hum(), 0.32, 0.25 * np.sin(k))
        # 패드: 2부부터, 3부에서 조금 더
        if part >= 2:
            place(buf, pad([root + 24, root + 31, rh[0] - 12], BAR * 1.02), t, 0.16 if part == 2 else 0.2)
    # 3부 정점(벤다이어그램이 겹치는 순간) — 넓은 C 화음, 그리고 아웃트로 쪽으로 사라짐
    peak = R + 24.15
    for m, v in ((36, 0.7), (48, 0.6), (55, 0.5), (64, 0.55), (67, 0.5), (72, 0.6), (74, 0.45), (79, 0.4)):
        place(buf, piano(m, v, 4.5), peak + rng.normal(0, 0.008), 0.42)
    place(buf, pad([48, 55, 64, 71], 4.0, a=0.6, r=3.0), peak, 0.22)


def confirm(buf, t, step=0, gain=1.0):
    """단계가 켜질 때: 지금 화음의 높은 피아노 두 음(단계가 오를수록 조금씩 높게) + 아주 옅은 반짝임."""
    _, rh = chord_at(t)
    hi = sorted(rh)
    a, b = hi[step % 4] + 12, hi[(step + 2) % 4] + 12 + (12 if hi[(step + 2) % 4] < hi[step % 4] else 0)
    place(buf, piano(a, 0.5, 1.2), t, 0.5 * gain, 0.2)
    place(buf, piano(b, 0.45, 1.4), t + 0.075, 0.42 * gain, 0.3)
    place(buf, shift(S["sparkle"], rng.uniform(-1, 1)), t + 0.02, 0.06 * gain, 0.4)


S = {}


def sfx(buf, name, t, gain, semis=None, pan=0.0):
    y = S[name]
    semis = rng.uniform(-1.2, 1.2) if semis is None else semis
    place(buf, shift(y, semis), t, gain * 10 ** (rng.uniform(-1.5, 1.5) / 20), pan)


WH = ["whoosh", "whoosh-short"]


def effects(buf):
    w = iter(range(1000))
    wh = lambda t, g=0.22, p=0.0: sfx(buf, WH[next(w) % 2], t, g, pan=p)
    soft = lambda t, g=0.16, p=0.0: sfx(buf, "click-soft", t, g, pan=p)
    pop = lambda t, g=0.18, p=0.0: sfx(buf, "pop", t, g, semis=rng.uniform(-2, 2), pan=p)
    # ── 콜봇 흐름
    sfx(buf, "whoosh-cinematic", F + 0.9, 0.12, semis=-2)
    pop(F + 2.05, 0.12); wh(F + 2.95, 0.16); soft(F + 3.5)
    for t0 in (6.0, 7.05):                     # 휴대폰 진동(짧은 모터 떨림)
        n = int(0.72 * SR); tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * 172 * tt) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 11 * tt))) * np.minimum(1, tt / 0.02) * np.minimum(1, (0.72 - tt) / 0.06)
        place(buf, lowpass(np.stack([y, y], 1), 900), F + t0, 0.05, -0.3)
    pop(F + 7.8, 0.14, -0.3); wh(F + 8.3, 0.14)
    for t in (12.2, 15.8, 19.4, 23.0):
        wh(F + t, 0.13, 0.2)
    for k, t in enumerate((9.7, 13.6, 17.2, 20.8, 24.4)):
        confirm(buf, F + t + 0.02, k)
    for t in (17.2 + 0.45 + 6 * 0.045 + 0.35, 20.8 + 0.45 + 7 * 0.045 + 0.35):
        soft(F + t, 0.12)
    pop(F + 24.8, 0.14, 0.3)
    sfx(buf, "whoosh-cinematic", F + 26.4, 0.11, semis=-3)
    wh(F + 28.3, 0.1, -0.2)
    confirm(buf, F + 30.02, 4, 1.1); soft(F + 29.5, 0.12)
    # ── ConvAI
    wh(B + 0.0, 0.14)
    pop(B + 1.9, 0.12, -0.3); wh(B + 2.5, 0.11); confirm(buf, B + 4.1, 0); pop(B + 4.1, 0.08, 0.4); soft(B + 4.6, 0.12)
    pop(B + 7.0, 0.12, -0.3); wh(B + 7.7, 0.11); confirm(buf, B + 9.8, 1); pop(B + 9.8, 0.08, 0.4); soft(B + 10.3, 0.12)
    pop(B + 12.7, 0.12, -0.3); wh(B + 13.4, 0.1); wh(B + 14.5, 0.12, 0.3); confirm(buf, B + 16.0, 2); pop(B + 16.2, 0.08, 0.4)
    sfx(buf, "whoosh-cinematic", B + 17.3, 0.12, semis=-1)
    sfx(buf, "sparkle", B + 19.0, 0.05, semis=-2)
    wh(B + 23.0, 0.1); sfx(buf, "impact-bass-1", B + 23.6, 0.08, semis=-1); confirm(buf, B + 23.7, 3)
    # ── 9칸이 한 점으로 → 네트워크
    sfx(buf, "whoosh-cinematic", R + 5.2, 0.12, semis=-2); pop(R + 6.85, 0.12); confirm(buf, R + 6.9, 1, 0.8)
    wh(R + 7.75, 0.12); soft(R + 8.5, 0.18)
    for i in range(6):
        sfx(buf, "click-soft", R + 9.0 + i * 0.09, 0.05, semis=6 + i, pan=(i % 3 - 1) * 0.4)
    sfx(buf, "whoosh-cinematic", R + 10.3, 0.11, semis=-3)
    for i in range(3):
        sfx(buf, "impact-bass-2", R + 11.5 + i * 0.25, 0.05, semis=2 - i)
    pop(R + 15.4, 0.1)
    for k, (a, b) in enumerate([[15.8, 16.6], [17.2, 18.0], [18.6, 19.4], [20.0, 20.8]]):
        wh(R + a, 0.07, -0.3 + k * 0.2); confirm(buf, R + b, k, 0.75)
    wh(R + 21.8, 0.1); wh(R + 23.0, 0.1)
    sfx(buf, "impact-bass-2", R + 24.15, 0.12, semis=-2); sfx(buf, "sparkle", R + 24.2, 0.07, semis=-1)
    sfx(buf, "sparkle", R + 27.5, 0.06, semis=-3)


def main():
    load_piano()
    for n in ("whoosh", "whoosh-short", "whoosh-cinematic", "pop", "click-soft", "sparkle", "impact-bass-1", "impact-bass-2"):
        S[n] = decode(SFX / f"{n}.mp3")
    music = np.zeros((int((TOTAL + 4) * SR), 2))
    score(music)
    music = reverb(music, 2.8, 0.3)
    fx = np.zeros_like(music)
    effects(fx)
    fx = reverb(fx, 1.6, 0.14)
    # 음악은 흐름 장면에서 서서히 들어와 아웃트로 직전에 정리됨
    t = np.arange(len(music)) / SR
    env = np.clip((t - F) / 2.0, 0, 1) * np.clip((END_BODY + 0.6 - t) / 2.4, 0, 1)
    music *= env[:, None]
    sl = slice(int((F + 3) * SR), int((END_BODY - 3) * SR))
    rms = lambda x: np.sqrt((x[sl] ** 2).mean())
    music *= 10 ** (-23.5 / 20) / rms(music)          # 음악은 이전 영상의 배경음과 비슷한 크기
    fx *= 10 ** (-5 / 20) / np.abs(fx).max()          # 효과음은 가장 큰 순간이 -5 dB
    body = lowpass(music + fx, 14000)
    body = np.tanh(body * 1.2) / 1.2                  # 겹치는 순간만 부드럽게 눌러 줌
    n, i0, i1 = int(TOTAL * SR), int(F * SR), int(END_BODY * SR)
    out = body[:n].copy()
    intro = decode(INTRO, 0, F)[:i0]
    out[: len(intro)] = intro                         # 인트로 구간은 인트로 소리 그대로
    outro = decode(OUTRO, 0, TOTAL - END_BODY)
    m = min(len(outro), n - i1)
    fade = np.clip(1 - np.arange(m) / (1.2 * SR), 0, 1)[:, None]   # 음악의 마지막 울림만 아웃트로 밑으로 잠깐 남음
    out[i1:i1 + m] = outro[:m] + body[i1:i1 + m] * fade
    out *= 10 ** (-1.5 / 20) / np.abs(out).max()
    write_wav(OUT, out)
    print(OUT, f"{len(out) / SR:.2f}s")


if __name__ == "__main__":
    main()
