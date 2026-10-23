"""홈페이지 '우리가 걸어온 길' 섹션 배경 이미지.

인트로 영상과 같은 시각 언어: 어두운 보라 바탕, 브랜드 그라데이션 빛줄기, 로고 사선 12개,
네트워크 노드, 음성 파형. 텍스트(제목)와 연혁 패널은 HTML로 올라가므로 그 자리는 비워 둔다.

사용법: python3 -m intro.history_bg  → intro/out/history_bg.(png|jpg|webp), history_bg_mock.jpg
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent / "out"
FONT = Path(__file__).resolve().parent.parent / "assets" / "fonts"
W, H = 2560, 1420          # 스크린샷 비율(약 1.8:1)
SS = 2

DARK = np.array((14, 10, 34), float)
MAG = (255, 3, 200)
MID = (165, 24, 164)
BV = (60, 36, 243)
LIL = (157, 121, 255)
PURP = (86, 0, 207)


def grad3(t):
    t = min(1, max(0, t))
    if t < 0.5:
        a, b, k = MAG, MID, t * 2
    else:
        a, b, k = MID, BV, (t - 0.5) * 2
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def blob(img, cx, cy, r, color, strength):
    """부드러운 빛 덩어리(가산)."""
    h, w, _ = img.shape
    ys, xs = np.ogrid[:h, :w]
    d2 = ((xs - cx) ** 2 + (ys - cy) ** 2) / (r * r)
    img += np.exp(-d2 * 2.2)[..., None] * np.array(color, float) * strength


def path_pts(n=400):
    """연혁 길: 왼쪽 아래에서 시작해 완만하게 굽이치며 오른쪽 위로."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = -0.03 + 1.08 * t
        y = 0.86 - 0.50 * (t ** 1.35) + 0.05 * math.sin(t * math.pi * 2.2 + 0.4) * (1 - t * 0.5)
        pts.append((x * W * SS, y * H * SS))
    return pts


def build():
    w, h = W // 4, H // 4  # 배경 빛은 저해상도로 만들고 확대(매끈하게)
    base = np.zeros((h, w, 3)) + DARK
    # 화면 전체 보랏빛(기존 페이지의 밝은 보라 분위기를 어둡게 이어받음)
    ys = np.linspace(0, 1, h)[:, None, None]
    xs = np.linspace(0, 1, w)[None, :, None]
    base += (np.array(PURP) * 0.22) * (0.6 + 0.4 * xs) * (0.7 + 0.3 * (1 - ys))
    blob(base, w * 0.38, h * 0.48, w * 0.42, BV, 0.55)
    blob(base, w * 0.92, h * 0.12, w * 0.30, BV, 0.45)
    blob(base, w * 0.05, h * 0.05, w * 0.22, MAG, 0.30)
    blob(base, w * 0.20, h * 0.95, w * 0.30, MID, 0.25)
    blob(base, w * 0.75, h * 0.70, w * 0.35, PURP, 0.35)
    bg = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)
    bg = bg.filter(ImageFilter.GaussianBlur(6))

    canvas = bg.convert("RGBA")
    glow = Image.new("RGB", canvas.size, (0, 0, 0))
    d = ImageDraw.Draw(canvas)
    g = ImageDraw.Draw(glow)
    U = SS * W / 1920  # 1920 기준 단위

    # 1) 옅은 네트워크 별자리(오른쪽 위, 아래쪽 여백)
    rng = np.random.default_rng(11)
    nodes = []
    for _ in range(34):
        x = rng.uniform(0.0, 1.0)
        y = rng.uniform(0.0, 1.0)
        # 제목 자리(왼쪽 위)는 비운다
        if (x < 0.45 and y < 0.36) or x < 0.28:
            continue
        nodes.append((x * W * SS, y * H * SS))
    for i, a in enumerate(nodes):
        dist = sorted(((math.dist(a, b), j) for j, b in enumerate(nodes) if j != i))[:2]
        for dd, j in dist:
            if dd < 230 * U:
                d.line([a, nodes[j]], fill=(*LIL, 26), width=int(1.4 * U))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k, (x, y) in enumerate(nodes):
        r = (2.5 + (k % 3) * 1.2) * U
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(*LIL, 100))
        g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=tuple(int(c * 0.25) for c in LIL))
    canvas.alpha_composite(layer)

    # 2) 로고 사선 12개(왼쪽 위, 화면 밖으로 이어짐)
    dx, dy = 28.593, -69.138
    n = math.hypot(dx, dy)
    dv = (dx / n, dy / n)
    nv = (-dv[1], dv[0])
    cx, cy = 120 * U, 150 * U
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k in range(12):
        o = (k - 5.5) * 26 * U
        L = (120 + 16 * (11 - k)) * U
        px, py = cx + nv[0] * o, cy + nv[1] * o
        p0 = (px - dv[0] * L * 0.4, py - dv[1] * L * 0.4)
        p1 = (px + dv[0] * L, py + dv[1] * L)
        col = grad3(k / 11)
        wdt = 11 * U
        ld.line([p0, p1], fill=(*col, 170), width=int(wdt))
        for p in (p0, p1):
            ld.ellipse([p[0] - wdt / 2, p[1] - wdt / 2, p[0] + wdt / 2, p[1] + wdt / 2], fill=(*col, 170))
        g.line([p0, p1], fill=tuple(int(c * 0.55) for c in col), width=int(wdt * 2.6))
    canvas.alpha_composite(layer)

    # 3) 음성 파형(왼쪽 아래, 길 위쪽에 은은하게)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    bx, by = 120 * U, 640 * U
    for k in range(22):
        a = abs(math.sin(k * 0.9) * math.sin(k * 0.37 + 1)) * math.sin(math.pi * (k + 0.5) / 22) ** 0.6
        hh = (10 + 70 * a) * U
        x = bx + k * 17 * U
        col = grad3(k / 21)
        ld.rounded_rectangle([x, by - hh, x + 7 * U, by + hh], radius=int(3.5 * U), fill=(*col, 95))
    canvas.alpha_composite(layer)

    # 4) 말풍선(왼쪽 가운데, 테두리만)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    bx, by, bw, bh = 250 * U, 430 * U, 120 * U, 62 * U
    ld.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(bh / 2), outline=(255, 255, 255, 150), width=int(3 * U))
    ld.polygon([(bx + 26 * U, by + bh - 2 * U), (bx + 12 * U, by + bh + 18 * U), (bx + 46 * U, by + bh - 2 * U)], fill=(255, 255, 255, 150))
    for k in range(3):
        r = 6 * U
        x = bx + bw / 2 + (k - 1) * 22 * U
        ld.ellipse([x - r, by + bh / 2 - r, x + r, by + bh / 2 + r], fill=(255, 255, 255, 200))
    canvas.alpha_composite(layer)

    # 5) 연혁 길: 넓은 빛 띠 + 밝은 중심선 + 점선 + 연도 노드
    pts = path_pts()
    # 넓은 띠(유리 같은 반투명 길)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.line(pts, fill=(255, 255, 255, 30), width=int(84 * U), joint="curve")
    ld.line(pts, fill=(255, 255, 255, 26), width=int(40 * U), joint="curve")
    layer = layer.filter(ImageFilter.GaussianBlur(5 * U))
    canvas.alpha_composite(layer)
    # 중심선(그라데이션) + 빛
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 1)
        col = grad3(t)
        ld.line([pts[i], pts[i + 1]], fill=(*col, 255), width=int(6 * U))
        g.line([pts[i], pts[i + 1]], fill=tuple(int(c * 0.6) for c in col), width=int(24 * U))
    # 평행한 가는 선 두 줄(음성 신호처럼)
    for off, alpha in ((-26, 90), (26, 60)):
        sp = []
        for i in range(len(pts)):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            nn = math.hypot(tx, ty) or 1
            wav = math.sin(i * 0.22) * 6 * U
            sp.append((pts[i][0] - ty / nn * (off * U + wav), pts[i][1] + tx / nn * (off * U + wav)))
        ld.line(sp, fill=(*LIL, alpha), width=int(2 * U), joint="curve")
    # 점선(진행 방향)
    acc = 0.0
    for i in range(len(pts) - 1):
        seglen = math.dist(pts[i], pts[i + 1])
        if int(acc / (34 * U)) % 2 == 0:
            ld.line([pts[i], pts[i + 1]], fill=(255, 255, 255, 170), width=int(2.4 * U))
        acc += seglen
    canvas.alpha_composite(layer)

    # 연도 노드 6개(2005 → 2026): 앞쪽은 작게, 마지막은 크게
    stops = [0.10, 0.27, 0.44, 0.60, 0.76, 0.92]
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k, s in enumerate(stops):
        x, y = pts[int(s * (len(pts) - 1))]
        last = k == len(stops) - 1
        r = (13 if not last else 20) * U
        col = grad3(s)
        for rr, a in ((r * 3.4, 40), (r * 2.2, 70)) if last else ((r * 2.1, 55),):
            ld.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(*col, a), width=int(2.4 * U))
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
        ri = r * 0.55
        ld.ellipse([x - ri, y - ri, x + ri, y + ri], fill=(*col, 255))
        g.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=tuple(int(c * 0.9) for c in col))
    canvas.alpha_composite(layer)

    # 빛 합성
    gs = glow.resize((glow.size[0] // 8, glow.size[1] // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
    gs = gs.resize(canvas.size, Image.BILINEAR)
    out = np.clip(np.array(canvas.convert("RGB"), float) + np.array(gs, float) * 0.9, 0, 255).astype(np.uint8)
    # 아주 약한 비네팅
    yy, xx = np.ogrid[:out.shape[0], :out.shape[1]]
    v = ((xx / out.shape[1] - 0.5) ** 2 + (yy / out.shape[0] - 0.5) ** 2)
    out = (out * (1 - 0.35 * v)[..., None]).astype(np.uint8)
    img = Image.fromarray(out).reduce(SS)
    return img


def mock(img):
    """제목과 반투명 패널을 얹은 확인용 합성."""
    m = img.convert("RGBA")
    s = W / 1216
    panel = Image.new("RGBA", m.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    box = [int(592 * s), int(52 * s), int(1062 * s), int(632 * s)]
    region = m.crop(box).filter(ImageFilter.GaussianBlur(18))
    m.paste(region, box[:2])
    pd.rounded_rectangle(box, radius=int(18 * s), fill=(255, 255, 255, 120))
    m.alpha_composite(panel)
    d = ImageDraw.Draw(m)
    fb = ImageFont.truetype(str(FONT / "Pretendard-Bold.otf"), int(34 * s))
    fs = ImageFont.truetype(str(FONT / "Pretendard-SemiBold.otf"), int(11 * s))
    d.text((int(166 * s), int(64 * s)), "우리가 걸어온 길", font=fs, fill="white")
    d.text((int(166 * s), int(96 * s)), "우리는 새로운 역사를", font=fb, fill="white")
    d.text((int(166 * s), int(152 * s)), "쓰고 있습니다.", font=fb, fill="white")
    fy = ImageFont.truetype(str(FONT / "Pretendard-Bold.otf"), int(17 * s))
    fl = ImageFont.truetype(str(FONT / "Pretendard-Medium.otf"), int(10.5 * s))
    y = 80
    for yr, n in (("2026", 1), ("2025", 3), ("2024", 3), ("2020 ~ 2023", 4), ("2006 ~ 2019", 3), ("2005", 1)):
        d.text((int(620 * s), int(y * s)), yr, font=fy, fill=(40, 40, 50))
        y += 26
        for _ in range(n):
            d.text((int(620 * s), int(y * s)), "연혁 내용 자리", font=fl, fill=(60, 60, 70))
            y += 18
        y += 18
    return m.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    img = build()
    img.save(OUT / "history_bg.png", optimize=True)
    img.save(OUT / "history_bg.jpg", quality=92)
    img.save(OUT / "history_bg.webp", quality=90)
    mock(img).save(OUT / "history_bg_mock.jpg", quality=88)
    print("ok")
