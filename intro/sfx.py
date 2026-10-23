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


def build(duration):
    buf = np.zeros((int((duration + 0.5) * SR), 2))
    # 0.0 낮은 숨소리 같은 서브 톤
    add(buf, tone(hz(36), 0.9, ((1, 1),), a=0.2, r=0.4), 0.0, 0.25)
    # 0.35 빛줄기 상승음 → 1.0 반짝
    add(buf, sweep(260, 1040, 0.7), 0.35, 0.10)
    add(buf, bell(88, 1.4, 0.5), 1.02, 0.07, 0.2)
    add(buf, bell(95, 1.2, 0.4), 1.06, 0.04, -0.3)
    # 1.15~1.6 12갈래 퍼짐: 짧은 플링크
    for k in range(12):
        add(buf, bell(PENTA[k] - 12, 0.5, 0.12), 1.15 + k * 0.035, 0.035, (k - 5.5) / 6)
    # 2.4~7.0 패드(Am9 → Fmaj7)
    for m in (57, 64, 67, 71, 74):
        add(buf, tone(hz(m), 2.6, ((1, 1), (2, 0.08)), a=0.6, r=0.8), 2.3, 0.022, 0.3 if m % 2 else -0.3)
    for m in (53, 60, 64, 69, 72):
        add(buf, tone(hz(m), 2.4, ((1, 1), (2, 0.08)), a=0.6, r=0.9), 4.75, 0.022, 0.3 if m % 2 else -0.3)
    # 2.5~3.9 VOICE: 음절처럼 끊기는 낮은 펄스
    for k in range(9):
        t0 = 2.5 + k / 3.1 * 0.5 * 2 / 2 + k * 0.0
        add(buf, tone(hz(45 + (k % 3) * 2), 0.14, ((1, 1), (2, 0.35), (3, 0.1)), a=0.01, r=0.06, decay=0.08), 2.52 + k * 0.161, 0.18)
    # 3.85 막대가 점으로
    add(buf, sweep(900, 300, 0.25, rise=False), 3.85, 0.04)
    # 4.05, 4.45 말풍선 팝 / 타이핑 / 4.95 답장 차임
    add(buf, pop(760, 300), 4.05, 0.32, -0.25)
    add(buf, pop(980, 380), 4.45, 0.30, 0.25)
    for k in range(2):
        add(buf, tone(1500, 0.03, ((1, 1),), a=0.003, r=0.015), 4.55 + k * 0.1, 0.05, 0.3)
    add(buf, bell(84, 0.9, 0.3), 4.8, 0.06, 0.3)
    add(buf, bell(91, 0.9, 0.3), 4.88, 0.05, 0.3)
    # 5.25 말풍선 사라짐
    add(buf, sweep(700, 250, 0.22, rise=False), 5.38, 0.035)
    # 5.42~5.9 노드 등장 블립
    for i in range(13):
        ring = 0 if i == 0 else 1 if i < 7 else 2
        add(buf, tone(hz(76 + ring * 5 + (i % 3) * 2), 0.12, ((1, 1), (2, 0.2)), a=0.003, r=0.05, decay=0.05),
            5.5 + ring * 0.09 + i * 0.011, 0.05, ((i * 37) % 11 - 5) / 6)
    # 6.0~6.6 신호 아르페지오
    for k in range(8):
        add(buf, bell(PENTA[(k * 2) % 12], 0.5, 0.15), 6.0 + k * 0.075, 0.03, 0.4 if k % 2 else -0.4)
    # 6.55~7.0 역방향 스웰 → 원형 전환
    add(buf, sweep(180, 1400, 0.45, partials=((1, 1), (2, 0.3), (3, 0.1))), 6.55, 0.10)
    add(buf, tone(hz(84), 1.6, ((1, 1), (2, 0.1)), a=0.02, r=0.8, decay=0.6), 7.0, 0.05)
    # 7.3~ 사선 12개가 박힐 때마다 상승 플럭
    for i in range(12):
        st = 7.3 + i * 0.05 + 0.12
        add(buf, bell(PENTA[i], 0.6, 0.12), st, 0.03, ((i % 2) * 2 - 1) * 0.4)
    # 8.0 로고 팝: 서브 붐 + Cmaj9 화음
    k = kick(1.0)
    add(buf, k, 8.03, 0.55)
    for m in C_MAJ9:
        add(buf, tone(hz(m + 12), 3.6, ((1, 1), (2, 0.15), (3, 0.04)), a=0.01, r=1.2, decay=1.6), 8.03, 0.06)
    for m in (72, 76, 79, 83, 86):
        add(buf, bell(m, 2.5, 0.9), 8.05, 0.03, 0.2)
    # 9.05 워드마크 글자 반짝
    for i in range(7):
        add(buf, bell(PENTA[4 + i], 0.5, 0.1), 9.08 + i * 0.055, 0.022, -0.5 + i / 6)
    # 9.75 태그라인, 10.5 빛 스윕
    add(buf, bell(79, 1.5, 0.6), 9.78, 0.03)
    add(buf, sweep(800, 2400, 0.6, partials=((1, 1),)), 10.45, 0.018)
    add(buf, bell(96, 1.4, 0.5), 11.0, 0.025)
    buf = lowpass(buf, 9000)[: int(duration * SR)]
    fo = int(0.9 * SR)
    buf[-fo:] *= ((1 + np.cos(np.linspace(0, np.pi, fo))) / 2)[:, None]
    peak = np.abs(buf).max()
    buf *= 10 ** (-1.5 / 20) / peak
    return buf


def write(path, duration):
    b = build(duration)
    write_wav(path, b)
    return noise_report(b)
