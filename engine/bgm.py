"""저작권 걱정 없는 배경음악 합성기.

규칙: 노이즈 성분 금지(잡음 스네어·하이햇·레코드 질감 없음). 모든 음은 사인/배음 기반이고
시작·끝을 부드럽게 줄여 클릭음을 막는다. 회차 id로 시드를 정해 매주 조금씩 다른 곡이 나온다.
"""
import wave

import numpy as np

SR = 48000

# (근음 반음 오프셋, 화음 구성) — C 기준. 회차마다 하나 고른다
PROGRESSIONS = [
    [(9, "m7"), (5, "maj7"), (0, "maj7"), (7, "7sus")],   # Am7 Fmaj7 Cmaj7 Gsus
    [(2, "m7"), (7, "7"), (0, "maj7"), (9, "m7")],        # Dm7 G7 Cmaj7 Am7
    [(5, "maj7"), (4, "m7"), (2, "m7"), (0, "maj9")],     # Fmaj7 Em7 Dm7 Cmaj9
    [(0, "maj9"), (9, "m7"), (5, "maj7"), (7, "6")],      # Cmaj9 Am7 Fmaj7 G6
]
CHORDS = {"maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "7": [0, 4, 7, 10], "7sus": [0, 5, 7, 10],
          "maj9": [0, 4, 7, 14], "6": [0, 4, 7, 9]}
PENTA = [0, 2, 4, 7, 9]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, a, r, sustain=1.0, decay=None):
    """attack/release를 가진 엔벨로프. 끝은 반드시 0으로(클릭 방지)."""
    e = np.ones(n) * sustain
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    na = min(na, n // 2)
    nr = min(nr, n - na)
    e[:na] = (1 - np.cos(np.linspace(0, np.pi, na))) / 2 * sustain
    if decay:
        t = np.arange(n - na) / SR
        e[na:] = sustain * np.exp(-t / decay)
    e[n - nr:] *= (1 + np.cos(np.linspace(0, np.pi, nr))) / 2
    return e


def tone(f, dur, partials=((1, 1.0),), a=0.01, r=0.08, decay=None, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k, amp in partials:
        y += amp * np.sin(2 * np.pi * f * k * (1 + detune) * t)
    return y * env(n, a, r, decay=decay)


def add(buf, y, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= buf.shape[0]:
        return
    y = y[: buf.shape[0] - i]
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(y), 0] += y * gain * lg
    buf[i:i + len(y), 1] += y * gain * rg


def kick(dur=0.38):
    # 피치가 떨어지는 사인. 잡음 없음
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.003, 0.06, decay=0.12)


def lowpass(x, cutoff):
    """FFT로 부드럽게 고음을 깎는다(외부 라이브러리 불필요)."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    X *= (1 / np.sqrt(1 + (f / cutoff) ** 4))[:, None]
    return np.fft.irfft(X, n=x.shape[0], axis=0)


def synth(duration, seed=0, bpm=92, key=0):
    rng = np.random.default_rng(seed)
    prog = PROGRESSIONS[seed % len(PROGRESSIONS)]
    beat = 60 / bpm
    bar = beat * 4
    n = int((duration + 1) * SR)
    buf = np.zeros((n, 2))
    nbars = int(np.ceil(duration / bar)) + 1
    base = 48 + key  # C3
    motif = [int(x) for x in rng.choice(len(PENTA), 6)]
    for b in range(nbars):
        t0 = b * bar
        root, kind = prog[b % len(prog)]
        notes = [base + root + iv for iv in CHORDS[kind]]
        intro = b == 0
        # 패드: 살짝 어긋난 사인 두 겹(좌우)
        for m in notes:
            for dt, pan in ((-0.0012, -0.6), (0.0012, 0.6)):
                add(buf, tone(hz(m + 12), bar + 0.4, ((1, 1), (2, 0.12)), a=0.5, r=0.6, detune=dt), t0, 0.035, pan)
        # 베이스: 1, 3박
        for bt in (0, 2):
            add(buf, tone(hz(base + root - 12), beat * 1.6, ((1, 1), (2, 0.25)), a=0.012, r=0.12, decay=0.9),
                t0 + bt * beat, 0.22)
        # 킥: 1, 3박 (첫 마디는 쉼)
        if not intro:
            for bt in (0, 2):
                add(buf, kick(), t0 + bt * beat, 0.32)
        # 일렉 피아노풍 스탭: 2박 반, 4박
        for bt in (1.5, 3):
            for m in notes[1:]:
                add(buf, tone(hz(m + 12), beat * 1.2, ((1, 1), (2, 0.3), (3, 0.08)), a=0.006, r=0.15, decay=0.45),
                    t0 + bt * beat, 0.05, rng.uniform(-0.3, 0.3))
        # 아르페지오(벨): 8분음표, 사인 + 약한 배음
        if not intro:
            for k in range(8):
                m = notes[(k * 3) % len(notes)] + 24
                add(buf, tone(hz(m), beat * 0.9, ((1, 1), (3, 0.06)), a=0.005, r=0.2, decay=0.22),
                    t0 + k * beat / 2, 0.032, 0.5 if k % 2 else -0.5)
        # 멜로디: 2마디마다 짧은 동기
        if b % 2 == 1 and b > 1:
            for j, deg in enumerate(motif[:4]):
                m = base + 24 + PENTA[deg]
                add(buf, tone(hz(m), beat * 0.9, ((1, 1), (2, 0.15)), a=0.01, r=0.25, decay=0.5),
                    t0 + j * beat * 0.75, 0.06, 0.15)
    # 짧은 스테레오 딜레이(음향 공간감, 잡음 없음)
    d = int(beat * 0.75 * SR)
    wet = np.zeros_like(buf)
    wet[d:, 0] = buf[:-d, 1] * 0.22
    wet[d:, 1] = buf[:-d, 0] * 0.22
    buf += wet
    buf = lowpass(buf, 7000)
    buf = buf[: int(duration * SR)]
    # 페이드 인/아웃
    fi, fo = int(0.8 * SR), int(2.2 * SR)
    buf[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
    buf[-fo:] *= ((1 + np.cos(np.linspace(0, np.pi, fo))) / 2)[:, None]
    # 레벨: 평균 약 -20dBFS, 피크 -3dBFS 제한
    rms = np.sqrt(np.mean(buf ** 2)) + 1e-9
    buf *= 10 ** (-20 / 20) / rms
    peak = np.abs(buf).max()
    if peak > 10 ** (-3 / 20):
        buf *= 10 ** (-3 / 20) / peak
    return buf


def write_wav(path, buf):
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def noise_report(buf):
    """고음역(>9kHz) 에너지 비율. 노이즈가 섞이면 커진다."""
    x = buf.mean(axis=1)
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    return float(spec[freqs > 9000].sum() / (spec.sum() + 1e-12))
