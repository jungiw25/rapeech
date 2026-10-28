"""홈페이지 채용 배너('지금, 우리의 여정에 함께하세요.') 배경.

연혁 배경(history_bg.py)과 같은 연보라 스타일. 가운데는 흰 제목·버튼이 올라가므로 비워 두고,
오른쪽에는 연혁 길이 이어져 올라가 끝에 '다음 멤버' 자리 노드가 빛난다.

사용법: python3 -m intro.recruit_bg → intro/out/recruit_bg.(png|jpg|webp), recruit_bg_mock.jpg
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from intro.history_bg import FONT, OUT, grad3, lerp_blob, mix2

W, H = 3200, 954   # 스크린샷 비율(약 3.35:1), 2배 해상도
SS = 2


def base_img():
    w, h = W // 4, H // 4
    ys = np.linspace(-1, 1, h)[:, None, None]
    xs = np.linspace(-1, 1, w)[None, :, None]
    r = np.sqrt((xs / 1.0) ** 2 + (ys / 1.6) ** 2)  # 가로로 긴 타원
    c0, c1 = np.array((124, 100, 255.)), np.array((206, 196, 255.))
    t = np.clip((r - 0.25) / 0.9, 0, 1) ** 1.3
    base = (c0 + (c1 - c0) * t) * np.ones((h, w, 3))
    lerp_blob(base, w * 0.12, h * 0.0, w * 0.16, (190, 96, 255), 0.45)
    lerp_blob(base, w * 0.93, h * 1.0, w * 0.20, (236, 228, 255), 0.5)
    lerp_blob(base, w * 0.50, h * 0.50, w * 0.22, (116, 90, 255), 0.35)
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)
    return im.filter(ImageFilter.GaussianBlur(6))


def build():
    canvas = base_img().convert("RGBA")
    glow = Image.new("RGB", canvas.size, (0, 0, 0))
    g = ImageDraw.Draw(glow)
    U = SS * W / 3200 * 1.6  # 배너 높이 기준 단위

    def layer():
        L = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        return L, ImageDraw.Draw(L)

    # 1) 네트워크 점(양옆만, 가운데 텍스트 자리는 비움)
    rng = np.random.default_rng(5)
    nodes = []
    while len(nodes) < 26:
        x, y = rng.uniform(0, 1), rng.uniform(0, 1)
        if 0.25 < x < 0.75:
            continue
        nodes.append((x * W * SS, y * H * SS))
    L, ld = layer()
    for i, a in enumerate(nodes):
        for dd, j in sorted((math.dist(a, b), j) for j, b in enumerate(nodes) if j != i)[:2]:
            if dd < 260 * U:
                ld.line([a, nodes[j]], fill=(255, 255, 255, 45), width=int(1.4 * U))
    for k, (x, y) in enumerate(nodes):
        r = (2.4 + (k % 3)) * U
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 160))
        g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=(40, 30, 70))
    canvas.alpha_composite(L)

    # 2) 로고 사선 12개(왼쪽 위, 위로 잘려 나감)
    dx, dy = 28.593, -69.138
    n = math.hypot(dx, dy)
    dv, nv = (dx / n, dy / n), (69.138 / n, 28.593 / n)
    cx, cy = W * SS * 0.155, 40 * U
    L, ld = layer()
    for k in range(12):
        o = (k - 5.5) * 24 * U
        Ln = (70 + 12 * (11 - k)) * U
        px, py = cx + nv[0] * o, cy + nv[1] * o
        p0 = (px - dv[0] * Ln * 0.3, py - dv[1] * Ln * 0.3)
        p1 = (px + dv[0] * Ln, py + dv[1] * Ln)
        col = mix2((255, 130, 228), (200, 186, 255), k / 11)
        wd = 10 * U
        ld.line([p0, p1], fill=(*col, 190), width=int(wd))
        for p in (p0, p1):
            ld.ellipse([p[0] - wd / 2, p[1] - wd / 2, p[0] + wd / 2, p[1] + wd / 2], fill=(*col, 190))
        g.line([p0, p1], fill=tuple(int(c * 0.45) for c in col), width=int(wd * 2.6))
    canvas.alpha_composite(L)

    # 3) 말풍선(왼쪽) + 음성 파형(왼쪽 아래)
    L, ld = layer()
    bx, by, bw, bh = W * SS * 0.155, H * SS * 0.40, 100 * U, 52 * U
    ld.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(bh / 2), outline=(255, 255, 255, 200), width=int(3 * U))
    ld.polygon([(bx + 22 * U, by + bh - 2 * U), (bx + 10 * U, by + bh + 15 * U), (bx + 40 * U, by + bh - 2 * U)], fill=(255, 255, 255, 200))
    for k in range(3):
        r = 5.5 * U
        x = bx + bw / 2 + (k - 1) * 19 * U
        ld.ellipse([x - r, by + bh / 2 - r, x + r, by + bh / 2 + r], fill=(255, 255, 255, 230))
    wx, wy = W * SS * 0.045, H * SS * 0.80
    for k in range(18):
        a = abs(math.sin(k * 0.9) * math.sin(k * 0.37 + 1)) * math.sin(math.pi * (k + 0.5) / 18) ** 0.6
        hh = (8 + 52 * a) * U
        x = wx + k * 15 * U
        ld.rounded_rectangle([x, wy - hh, x + 6 * U, wy + hh], radius=int(3 * U), fill=(255, 255, 255, 130))
    canvas.alpha_composite(L)

    # 4) 여정의 길: 아래 가운데에서 오른쪽 위로
    pts = []
    for i in range(301):
        t = i / 300
        x = 0.57 + 0.43 * t
        y = 1.10 - 0.86 * (t ** 1.1) + 0.04 * math.sin(t * math.pi * 1.6)
        pts.append((x * W * SS, y * H * SS))
    L, ld = layer()
    ld.line(pts, fill=(255, 255, 255, 40), width=int(80 * U), joint="curve")
    ld.line(pts, fill=(255, 255, 255, 34), width=int(38 * U), joint="curve")
    L = L.filter(ImageFilter.GaussianBlur(5 * U))
    canvas.alpha_composite(L)
    L, ld = layer()
    for i in range(len(pts) - 1):
        col = grad3(0.15 + 0.85 * i / (len(pts) - 1))
        ld.line([pts[i], pts[i + 1]], fill=(*col, 255), width=int(6 * U))
        g.line([pts[i], pts[i + 1]], fill=tuple(int(c * 0.55) for c in col), width=int(22 * U))
    acc = 0.0
    for i in range(len(pts) - 1):
        if int(acc / (30 * U)) % 2 == 0:
            ld.line([pts[i], pts[i + 1]], fill=(255, 255, 255, 190), width=int(2.4 * U))
        acc += math.dist(pts[i], pts[i + 1])
    canvas.alpha_composite(L)
    # 노드: 지나온 길 2개 + 지금 1개 + 끝의 '다음 멤버' 자리(빈 링)
    L, ld = layer()
    for k, s in enumerate((0.20, 0.42, 0.61)):
        x, y = pts[int(s * 300)]
        r = 12 * U
        col = grad3(0.15 + 0.85 * s)
        ld.ellipse([x - r * 2.1, y - r * 2.1, x + r * 2.1, y + r * 2.1], outline=(255, 255, 255, 120), width=int(2.2 * U))
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
        ld.ellipse([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55], fill=(*col, 255))
        g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=tuple(int(c * 0.8) for c in col))
    x, y = pts[int(0.80 * 300)]
    r = 18 * U
    for rr, a in ((r * 3.2, 70), (r * 2.2, 120)):
        ld.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 255, a), width=int(2.4 * U))
    ld.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 255), width=int(5 * U))
    # 빈 자리 안에 + 표시(새 멤버를 기다림)
    pl = r * 0.5
    ld.line([x - pl, y, x + pl, y], fill=(255, 255, 255, 255), width=int(4 * U))
    ld.line([x, y - pl, x, y + pl], fill=(255, 255, 255, 255), width=int(4 * U))
    g.ellipse([x - r * 3.5, y - r * 3.5, x + r * 3.5, y + r * 3.5], fill=(120, 90, 255))
    canvas.alpha_composite(L)

    # 5) 반짝이는 작은 점
    L, ld = layer()
    for k in range(14):
        x = rng.uniform(0, 1)
        if 0.3 < x < 0.7:
            continue
        x, y = x * W * SS, rng.uniform(0.1, 0.9) * H * SS
        r = rng.uniform(3, 7) * U
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 150))
        g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=(60, 50, 90))
    canvas.alpha_composite(L)

    gs = glow.resize((glow.size[0] // 8, glow.size[1] // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
    gs = gs.resize(canvas.size, Image.BILINEAR)
    a, gg = np.array(canvas.convert("RGB"), float), np.array(gs, float)
    out = (255 - (255 - a) * (255 - gg * 0.8) / 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out).reduce(SS)


def mock(img):
    m = img.copy()
    d = ImageDraw.Draw(m)
    s = W / 1600
    fb = ImageFont.truetype(str(FONT / "Pretendard-Bold.otf"), int(46 * s))
    fs = ImageFont.truetype(str(FONT / "Pretendard-Medium.otf"), int(14 * s))
    fbt = ImageFont.truetype(str(FONT / "Pretendard-SemiBold.otf"), int(15 * s))
    cx = W / 2
    d.text((cx, 162 * s), "지금, 우리의 여정에 함께하세요.", font=fb, fill="white", anchor="mm")
    d.text((cx, 236 * s), "저희와 함께 더 나은 채용 문화를 만들어 나갈 멤버를 기다리고 있습니다.", font=fs, fill="white", anchor="mm")
    bw, bh = 210 * s, 48 * s
    d.rounded_rectangle([cx - bw / 2, 305 * s, cx + bw / 2, 305 * s + bh], radius=int(bh / 2), fill="white")
    d.text((cx, 305 * s + bh / 2), "진행 중인 공고 보러가기 ↗", font=fbt, fill=(20, 20, 30), anchor="mm")
    return m


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    img = build()
    img.save(OUT / "recruit_bg.png", optimize=True)
    img.save(OUT / "recruit_bg.jpg", quality=92)
    img.save(OUT / "recruit_bg.webp", quality=90)
    mock(img).save(OUT / "recruit_bg_mock.jpg", quality=88)
    print("ok")
