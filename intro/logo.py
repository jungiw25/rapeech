"""라피치 영문 로고 SVG를 조각(사선 12개, 삼각형, 글자 7개)으로 나눠 래스터화한다.

외부 SVG 라이브러리 없이 path(M L H V C Z)만 해석한다. 기본은 국문 로고(brand/ko/logotype/ko_logo_purple.svg). RAPEECH_LOGO=en 이면 영문 로고.
"""
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import os

_LANG = os.environ.get("RAPEECH_LOGO", "ko")
SVG = Path(__file__).resolve().parent.parent / "brand" / _LANG / "logotype" / f"{_LANG}_logo_purple.svg"
# 로고 전체 폭(viewBox 단위). 심볼은 두 로고가 같고 워드마크 폭만 다르다
LOGO_W = float(re.search(r'viewBox="0 0 ([\d.]+)', SVG.read_text()).group(1))


def parse_path(d, steps=20):
    """path d → 하위 경로(점 목록) 목록."""
    toks = re.findall(r"[MmLlHhVvCcZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    subs, cur, i = [], [], 0
    x = y = 0.0
    cmd = None
    start = (0.0, 0.0)

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                if cur:
                    subs.append(cur)
                cur = []
                x, y = start
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            if cur:
                subs.append(cur)
            cur = [(x, y)]
            start = (x, y)
            cmd = "l" if rel else "L"
        elif c == "L":
            nx, ny = num(), num()
            x, y = (x + nx, y + ny) if rel else (nx, ny)
            cur.append((x, y))
        elif c == "H":
            nx = num()
            x = x + nx if rel else nx
            cur.append((x, y))
        elif c == "V":
            ny = num()
            y = y + ny if rel else ny
            cur.append((x, y))
        elif c == "C":
            p = [num() for _ in range(6)]
            if rel:
                p = [p[0] + x, p[1] + y, p[2] + x, p[3] + y, p[4] + x, p[5] + y]
            x0, y0 = x, y
            for k in range(1, steps + 1):
                s = k / steps
                a, b, cc, dd = (1 - s) ** 3, 3 * (1 - s) ** 2 * s, 3 * (1 - s) * s ** 2, s ** 3
                cur.append((a * x0 + b * p[0] + cc * p[2] + dd * p[4], a * y0 + b * p[1] + cc * p[3] + dd * p[5]))
            x, y = p[4], p[5]
    if cur:
        subs.append(cur)
    return subs


def load():
    s = SVG.read_text()
    ds = re.findall(r'<path d="([^"]+)"', s)
    assert len(ds) >= 15, len(ds)
    tri = parse_path(ds[0])
    stripes = [parse_path(d) for d in ds[1:13]]
    clip = parse_path(ds[13])
    letters = [parse_path(d) for d in ds[14:]]
    letters.sort(key=lambda subs: min(p[0] for p in subs[0]))  # 왼쪽 글자부터
    return dict(tri=tri, stripes=stripes, clip=clip, letters=letters)


def mask_of(subs, scale, size, off, ss=4):
    """even-odd 채우기 마스크(L). off: 로고 좌표 원점의 픽셀 위치."""
    W, H = size
    m = Image.new("L", (W * ss, H * ss), 0)
    for sub in subs:
        t = Image.new("L", m.size, 0)
        ImageDraw.Draw(t).polygon([((px * scale + off[0]) * ss, (py * scale + off[1]) * ss) for px, py in sub], fill=255)
        m = ImageChops.logical_xor(m.convert("1"), t.convert("1")).convert("L") if len(subs) > 1 else t
    return m.resize((W, H), Image.LANCZOS)


def hgrad(size, x0, x1, c0, c1, off, scale):
    """로고 좌표 x0→x1 가로 그라데이션."""
    W, H = size
    xs = (np.arange(W) - off[0]) / scale
    t = np.clip((xs - x0) / (x1 - x0), 0, 1)[None, :, None]
    c0, c1 = np.array(c0, float), np.array(c1, float)
    rgb = (c0 + (c1 - c0) * t) * np.ones((H, 1, 1))
    return rgb.astype(np.uint8)


def bbox(subs):
    xs = [p[0] for s in subs for p in s]
    ys = [p[1] for s in subs for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def piece(subs, scale, fill, clip=None, pad=2):
    """조각 RGBA 이미지와, 그 이미지 왼쪽 위의 로고 좌표를 돌려준다."""
    x0, y0, x1, y1 = bbox(subs)
    W = int((x1 - x0) * scale) + pad * 2 + 1
    H = int((y1 - y0) * scale) + pad * 2 + 1
    off = (-x0 * scale + pad, -y0 * scale + pad)
    m = mask_of(subs, scale, (W, H), off)
    if clip is not None:
        cm = mask_of(clip, scale, (W, H), off)
        m = ImageChops.multiply(m, cm)
    if callable(fill):
        rgb = fill((W, H), off)
    else:
        rgb = np.zeros((H, W, 3), np.uint8) + np.array(fill, np.uint8)
    im = Image.fromarray(rgb, "RGB").convert("RGBA")
    im.putalpha(m)
    return im, (x0 - pad / scale, y0 - pad / scale)


def build_pieces(scale):
    L = load()
    tri_fill = lambda size, off: hgrad(size, 20.02, 73.04, (0x8F, 0x66, 0xFF), (0x56, 0x00, 0xCF), off, scale)
    str_fill = lambda size, off: hgrad(size, 4.84, 77.54, (0x9D, 0x79, 0xFF), (0x7C, 0x51, 0xFF), off, scale)
    tri = piece(L["tri"], scale, tri_fill)
    stripes = [piece(s, scale, str_fill, clip=L["clip"]) for s in L["stripes"]]
    letters = [piece(s, scale, (0x22, 0x22, 0x22)) for s in L["letters"]]
    return dict(tri=tri, stripes=stripes, letters=letters, raw=L)
