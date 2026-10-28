"""인트로 효과음과 배경 패드. 잡음 없이 음정 있는 소리(사인과 배음)로만 만든다."""
import numpy as np

from engine.bgm import SR, add, env, hz, kick, lowpass, noise_report, tone, write_wav

C_MAJ9 = [48, 55, 59, 62, 64]          # C E? → C G B D E (부드러운 Cmaj9 보이싱)
PENTA = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98]


def sweep(f0, f1, dur, partials=((1, 1.0), (2, 0.25)), a=0.05, r=0.05, rise=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(amp * np.sin(k * ph) for k, amp in partials)
    shape = (t / dur) ** 2 if rise else np.ones(n)
    return y * shape * env(n, a, r)


def pop(f0=700, f1=260, dur=0.14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.04, decay=0.05)


def bell(m, dur=1.2, decay=0.35):
    return tone(hz(m), dur, ((1, 1), (2.0, 0.18), (3.01, 0.06)), a=0.004, r=0.2, decay=decay)


def finish(buf, duration, fade=0.9):
    buf = lowpass(buf, 9000)[: int(duration * SR)]
    fo = int(fade * SR)
    buf[-fo:] *= ((1 + np.cos(np.linspace(0, np.pi, fo))) / 2)[:, None]
    buf *= 10 ** (-1.5 / 20) / np.abs(buf).max()
    return buf


def pad(buf, notes, t, dur, gain=0.02):
    for m in notes:
        add(buf, tone(hz(m), dur, ((1, 1), (2, 0.08)), a=0.6, r=0.9), t, gain, 0.3 if m % 2 else -0.3)


def build(duration):
    """인트로: 효과음은 장면이 바뀌는 순간에만, 나머지는 잔잔한 패드."""
    buf = np.zeros((int((duration + 0.5) * SR), 2))
    add(buf, tone(hz(36), 0.9, ((1, 1),), a=0.2, r=0.4), 0.0, 0.22)          # 시작 숨
    add(buf, sweep(260, 1040, 0.7), 0.35, 0.07)                                # 빛줄기
    pad(buf, (57, 64, 67, 71, 74), 1.0, 3.6)                                   # 목소리 구간 패드
    add(buf, pop(760, 300), 4.05, 0.18, -0.25)                                 # 고객 말풍선
    add(buf, bell(84, 0.9, 0.3), 4.8, 0.05, 0.3)                               # AI 답(한 번)
    add(buf, bell(91, 0.9, 0.3), 4.88, 0.04, 0.3)
    pad(buf, (53, 60, 64, 69, 72), 4.75, 2.4)                                  # 네트워크 구간 패드
    add(buf, sweep(180, 1400, 0.45, partials=((1, 1), (2, 0.3), (3, 0.1))), 6.55, 0.07)   # 원형 전환
    add(buf, kick(1.0), 8.03, 0.45)                                            # 로고 완성
    for m in C_MAJ9:
        add(buf, tone(hz(m + 12), 3.6, ((1, 1), (2, 0.15), (3, 0.04)), a=0.01, r=1.2, decay=1.6), 8.03, 0.05)
    add(buf, bell(79, 1.5, 0.6), 9.8, 0.022)                                   # 태그라인
    return finish(buf, duration)


def build_outro(duration):
    """아웃트로: 빛줄기 → 로고 완성 → 여운. 인트로보다 더 적게."""
    buf = np.zeros((int((duration + 0.5) * SR), 2))
    add(buf, sweep(300, 900, 0.55), 0.05, 0.05)
    pad(buf, (60, 64, 67, 71, 74), 0.4, 2.2, 0.018)
    add(buf, sweep(200, 1200, 0.6, partials=((1, 1), (2, 0.3))), 1.4, 0.05)
    add(buf, kick(1.0), 2.62, 0.35)
    for m in C_MAJ9:
        add(buf, tone(hz(m + 12), 4.0, ((1, 1), (2, 0.15), (3, 0.04)), a=0.02, r=1.6, decay=2.0), 2.62, 0.045)
    add(buf, bell(84, 1.6, 0.7), 3.55, 0.018)
    return finish(buf, duration, fade=1.6)


def write_outro(path, duration):
    b = build_outro(duration)
    write_wav(path, b)
    return noise_report(b)


def write(path, duration):
    b = build(duration)
    write_wav(path, b)
    return noise_report(b)
