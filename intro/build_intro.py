"""라피치 브랜드 인트로 영상 (약 12초).

흐름: 빛줄기 → 12갈래 → VOICE(파형) → CONVERSATION(말풍선) → NETWORK(노드) → 흰 화면 원형 전환
      → 사선 12개가 날아와 로고 조립 → 삼각형 팝 → 워드마크 펼침 → 태그라인

사용법:
  python3 -m intro.build_intro                 # 16:9, 9:16 둘 다
  python3 -m intro.build_intro --fmt 16x9
  python3 -m intro.build_intro --stills 1,3,4.5,8.3,11   # 검수용 정지 화면만
"""
import argparse
import math
import multiprocessing as mp
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from intro import logo as LG
from intro import sfx

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "out"
FONT = ROOT / "assets" / "fonts"
FPS = 60
DUR = 12.0
SS = 2  # 슈퍼샘플링

DARK = (12, 9, 22)
LIGHT = (250, 249, 253)
MAG = (255, 3, 200)
MID = (165, 24, 164)
BV = (60, 36, 243)
LIL = (157, 121, 255)
PURP = (86, 0, 207)
INK = (34, 34, 34)
TAGLINE = "Conversational AI  ·  Network Infrastructure"

# 로고 사선 방향(왼쪽 아래 → 오른쪽 위)
_dx, _dy = 83.967 - 55.374, 4.045 - 73.183
_n = math.hypot(_dx, _dy)
DIR = (_dx / _n, _dy / _n)
NRM = (-DIR[1], DIR[0])


# ---------------------------------------------------------------- 이징
def clamp(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def out_back(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def in_back(x, s=1.6):
    x = clamp(x)
    return (s + 1) * x ** 3 - s * x ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c0, c1, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c0, c1))


G_RGB = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in
         ["#FF03C8", "#EE06C1", "#DE0ABA", "#CD0EB4", "#BD12AD", "#AD16A7", "#9B19AB", "#881BB9", "#751DC7", "#621FD6", "#4F21E4", "#3C24F3"]]


def grad3(t):
    """브랜드 그라데이션 마젠타 → 퍼플 → 블루바이올렛."""
    return mix(MAG, MID, t * 2) if t < 0.5 else mix(MID, BV, (t - 0.5) * 2)


_fonts = {}


def font(name, size):
    k = (name, int(size))
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(str(FONT / name), int(size))
    return _fonts[k]


# ---------------------------------------------------------------- 장면 준비
class Scene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.CW, self.CH = W * SS, H * SS
        self.u = min(W, H) / 1080 * SS
        self.cx, self.cy = self.CW / 2, self.CH / 2
        self.portrait = H > W
        self.diag = math.hypot(self.CW, self.CH)
        # 로고 크기: 가로 영상은 화면 폭의 50%, 세로 영상은 78%
        self.s = (self.CW * (0.78 if self.portrait else 0.50)) / 314
        self.P = LG.build_pieces(self.s)
        self.tagline_y = None
        # 네트워크 노드(고정 시드)
        rng = np.random.default_rng(3)
        nodes = [(0.0, 0.0, 0)]
        for k in range(6):
            a = k * math.pi / 3 + 0.3 + rng.uniform(-0.15, 0.15)
            nodes.append((170 * math.cos(a), 170 * math.sin(a), 1))
        for k in range(6):
            a = k * math.pi / 3 + 0.82 + rng.uniform(-0.2, 0.2)
            r = 320 + rng.uniform(-30, 30)
            nodes.append((r * math.cos(a) * (0.85 if self.portrait else 1.25), r * math.sin(a), 2))
        self.nodes = nodes
        edges = [(0, k) for k in range(1, 7)]
        edges += [(k, k % 6 + 1) for k in range(1, 7)]
        edges += [(k, 6 + k) for k in range(1, 7)]
        edges += [(6 + k, 6 + (k % 6) + 1) for k in range(1, 7) if k % 2 == 0]
        self.edges = edges
        # 말풍선 글꼴
        self.fb = font("Pretendard-SemiBold.otf", 46 * self.u)
        self.fcap = font("JetBrainsMono-Bold.ttf", 30 * self.u)
        self.ftag = font("Pretendard-Medium.otf", (30 if not self.portrait else 34) * self.u)

    # ---- 공용 그리기
    def line(self, d, p0, p1, w, color):
        d.line([p0, p1], fill=color, width=max(1, int(w)))
        r = w / 2
        for p in (p0, p1):
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)

    def caption(self, d, text, t, a, b):
        if not (a - 0.01 < t < b + 0.3):
            return
        p = out_cubic(seg(t, a, a + 0.3)) * (1 - seg(t, b, b + 0.25))
        if p <= 0:
            return
        f = self.fcap
        sp = 6 * self.u
        w = sum(f.getlength(c) for c in text) + sp * (len(text) - 1)
        x = self.cx - w / 2
        y = self.cy + (330 if not self.portrait else 520) * self.u + (1 - p) * 20 * self.u
        col = mix(DARK, LIL, p)
        for c in text:
            d.text((x, y), c, font=f, fill=col, anchor="ls")
            x += f.getlength(c) + sp

    # ---- 1. 빛줄기와 12갈래, 파형
    def bars(self, d, g, t):
        u = self.u
        if t < 0.4:
            p = 0.5 + 0.5 * math.sin(t * 30)
            r = 7 * u * out_back(seg(t, 0.0, 0.25))
            c = mix(DARK, LIL, p)
            d.ellipse([self.cx - r, self.cy - r, self.cx + r, self.cy + r], fill=c)
            g.ellipse([self.cx - r * 3, self.cy - r * 3, self.cx + r * 3, self.cy + r * 3], fill=mix((0, 0, 0), MAG, 0.5 * p))
            return
        if t > 4.15:
            return
        # 하나의 줄 → 12갈래 → 세로 막대
        L0 = 0.55 * self.diag * out_expo(seg(t, 0.35, 1.05))
        spread = out_cubic(seg(t, 1.15, 1.75))
        rot = in_out(seg(t, 1.85, 2.55))
        shrink = in_out(seg(t, 1.6, 2.5))
        ang0 = math.atan2(DIR[1], DIR[0])
        ang = lerp(ang0, -math.pi / 2, rot)
        dv = (math.cos(ang), math.sin(ang))
        nv = (-dv[1], dv[0])
        sp = lerp(70 * u, 46 * u, rot) * spread
        voice = seg(t, 2.5, 2.8)
        out = in_back(seg(t, 3.8, 4.15))
        n = 12
        for k in range(n):
            o = (k - (n - 1) / 2) * sp * (1 - 0.6 * out)
            Lk = lerp(L0, 70 * u, shrink)
            if voice > 0:
                tt = t - 2.5
                env = abs(math.sin(math.pi * 3.1 * tt)) ** 0.7
                a = 0.5 + 0.5 * math.sin(2 * math.pi * (1.9 * tt + k * 0.37)) * math.sin(2 * math.pi * (0.7 * tt + k * 0.13) + 1)
                win = math.sin(math.pi * (k + 0.5) / n) ** 0.8
                vh = (24 + 210 * a * env * win) * u
                Lk = lerp(Lk, vh, voice)
            Lk = lerp(Lk, 11 * u, out)
            w = lerp(4 * u, 22 * u, rot)
            if spread == 0:
                w = 5 * u
            cx = self.cx + nv[0] * o
            cy = self.cy + nv[1] * o
            p0 = (cx - dv[0] * Lk, cy - dv[1] * Lk)
            p1 = (cx + dv[0] * Lk, cy + dv[1] * Lk)
            col = grad3(k / (n - 1)) if spread > 0 else mix(LIL, (255, 255, 255), 0.5)
            fade = 1 - seg(t, 4.0, 4.15)
            col = mix(DARK, col, fade)
            self.line(d, p0, p1, w, col)
            self.line(g, p0, p1, w * 2.6, mix((0, 0, 0), col, 0.55 * fade))
            if spread == 0:
                break
        self.caption(d, "01  VOICE AI", t, 2.6, 3.75)

    # ---- 2. 말풍선
    def bubble(self, canvas, g, t, text, t0, right, typing_until=None):
        u = self.u
        if t < t0 or t > 5.65:
            return
        f = self.fb
        pad_x, h = 52 * u, 124 * u
        full_w = f.getlength(text) + pad_x * 2
        typing = typing_until is not None and t < typing_until
        tw = 210 * u if typing_until is not None else full_w
        if typing_until is not None and t >= typing_until:
            tw = lerp(210 * u, full_w, out_cubic(seg(t, typing_until, typing_until + 0.25)))
        sc = out_back(seg(t, t0, t0 + 0.32)) * (1 - in_back(seg(t, 5.38, 5.6)))
        if sc <= 0.01:
            return
        off = 120 * u if not self.portrait else 40 * u
        dy = -95 * u if not right else 95 * u
        if right:
            x1 = self.cx + max(full_w, 470 * u) / 2 + off
            x0 = x1 - tw
        else:
            x0 = self.cx - max(full_w, 470 * u) / 2 - off
            x1 = x0 + tw
        y0, y1 = self.cy + dy - h / 2, self.cy + dy + h / 2
        img = Image.new("RGBA", (int(x1 - x0) + 40, int(h) + 40), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        bw, bh = x1 - x0, h
        if right:
            fill = grad_img(int(bw), int(bh), MAG, BV)
            m = Image.new("L", fill.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=int(bh / 2), fill=255)
            fill.putalpha(m)
            img.alpha_composite(fill, (20, 20))
            dd.polygon([(20 + bw - 36 * u, 20 + bh - 8), (20 + bw + 6 * u, 20 + bh + 14 * u), (20 + bw - 70 * u, 20 + bh - 8)], fill=BV)
            tc = (255, 255, 255)
        else:
            dd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=int(bh / 2), fill=(255, 255, 255))
            dd.polygon([(20 + 36 * u, 20 + bh - 8), (20 - 6 * u, 20 + bh + 14 * u), (20 + 70 * u, 20 + bh - 8)], fill=(255, 255, 255))
            tc = INK
        if typing:
            for k in range(3):
                bounce = max(0.0, math.sin((t - t0) * 12 - k * 0.9)) * 10 * u
                r = 10 * u
                cx = 20 + bw / 2 + (k - 1) * 36 * u
                cy = 20 + bh / 2 - bounce
                dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
        else:
            ta = seg(t, (typing_until or t0) + 0.12, (typing_until or t0) + 0.35) if typing_until else seg(t, t0 + 0.15, t0 + 0.35)
            if ta > 0:
                tl = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(tl).text((20 + pad_x, 20 + bh / 2), text, font=f, fill=tc, anchor="lm")
                if ta < 1:
                    tl.putalpha(tl.getchannel("A").point(lambda v: int(v * ta)))
                img.alpha_composite(tl)
        # 꼬리 쪽을 기준으로 크기 변환
        if sc != 1:
            nw, nh = max(1, int(img.size[0] * sc)), max(1, int(img.size[1] * sc))
            img = img.resize((nw, nh), Image.BILINEAR)
        ax = x1 + 20 - img.size[0] if right else x0 - 20
        ay = y1 + 20 - img.size[1] + (20 * u * (1 - sc))
        comp(canvas, img, ax, ay)
        if right:
            gx0, gy0 = ax + 20 * sc, ay + 20 * sc
            g.rounded_rectangle([gx0, gy0, gx0 + bw * sc, gy0 + bh * sc], radius=int(bh * sc / 2), fill=mix((0, 0, 0), BV, 0.45))

    # ---- 3. 네트워크
    def network(self, d, g, t):
        if t < 5.45 or t > 7.15:
            return
        u = self.u
        col_scale = 1 - in_back(seg(t, 6.6, 7.05))
        rot = 0.7 * in_back(seg(t, 6.6, 7.05))
        ent = out_cubic(seg(t, 5.45, 5.9))

        def pos(i):
            x, y, _ = self.nodes[i]
            x, y = x * u * col_scale * lerp(0.6, 1.0, ent), y * u * col_scale * lerp(0.6, 1.0, ent)
            c, s = math.cos(rot), math.sin(rot)
            return (self.cx + x * c - y * s, self.cy + x * s + y * c)

        for ei, (a, b) in enumerate(self.edges):
            ring = max(self.nodes[a][2], self.nodes[b][2])
            p = out_cubic(seg(t, 5.62 + ring * 0.1 + ei * 0.007, 6.0 + ring * 0.1 + ei * 0.007))
            if p <= 0:
                continue
            pa, pb = pos(a), pos(b)
            pe = (lerp(pa[0], pb[0], p), lerp(pa[1], pb[1], p))
            d.line([pa, pe], fill=mix(DARK, LIL, 0.45), width=int(3 * u))
            # 신호 펄스
            if t > 6.0:
                ph = ((t - 6.0) * 1.6 + ei * 0.17) % 1.0
                q = (lerp(pa[0], pb[0], ph), lerp(pa[1], pb[1], ph))
                r = 5 * u
                c = grad3((ei % 7) / 6)
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=c)
                g.ellipse([q[0] - r * 3, q[1] - r * 3, q[0] + r * 3, q[1] + r * 3], fill=mix((0, 0, 0), c, 0.6))
        for i, (x, y, ring) in enumerate(self.nodes):
            p = out_back(seg(t, 5.5 + ring * 0.09 + i * 0.011, 5.8 + ring * 0.09 + i * 0.011))
            if p <= 0:
                continue
            q = pos(i)
            r = (20 if ring == 0 else 10 if ring == 1 else 8) * u * p
            c = PURP if ring == 0 else LIL if ring == 1 else mix(LIL, MAG, 0.5)
            if ring == 0:
                c = mix(PURP, LIL, 0.35)
            d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=c)
            g.ellipse([q[0] - r * 2.6, q[1] - r * 2.6, q[0] + r * 2.6, q[1] + r * 2.6], fill=mix((0, 0, 0), c, 0.6))
        self.caption(d, "03  AI × NETWORK", t, 5.6, 6.55)

    # ---- 4. 로고
    def lockup_origin(self, t):
        s = self.s
        o_sym = (self.cx - 43 * s, self.cy - 50 * s)
        lift = (40 if not self.portrait else 60) * self.u
        o_fin = (self.cx - LG.LOGO_W / 2 * s, self.cy - 45 * s - lift)
        k = in_out(seg(t, 8.85, 9.6))
        return (lerp(o_sym[0], o_fin[0], k), lerp(o_sym[1], o_fin[1], k)), o_fin

    def logo(self, canvas, t):
        if t < 7.2:
            return
        s, u = self.s, self.u
        (ox, oy), o_fin = self.lockup_origin(t)
        # 삼각형 팝(사선 뒤)
        tp = seg(t, 8.0, 8.42)
        if tp > 0:
            k = out_back(tp, 2.2)
            im, (lx, ly) = self.P["tri"]
            piv = (43.8, 57.6)
            if k > 0.02:
                nw, nh = max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k))
                sim = im.resize((nw, nh), Image.BICUBIC)
                px = ox + (piv[0] + (lx - piv[0]) * k) * s
                py = oy + (piv[1] + (ly - piv[1]) * k) * s
                comp(canvas, sim, px, py)
            # 링 파동
            rp = seg(t, 8.05, 8.75)
            if 0 < rp < 1:
                ring = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                R = (40 + 260 * out_cubic(rp)) * u
                c = (*LIL, int(200 * (1 - rp)))
                cx, cy = ox + piv[0] * s, oy + piv[1] * s
                ImageDraw.Draw(ring).ellipse([cx - R, cy - R, cx + R, cy + R], outline=c, width=max(1, int(6 * u * (1 - rp))))
                canvas.alpha_composite(ring)
        # 사선 12개(오른쪽부터 차례로 날아옴)
        for i, (im, (lx, ly)) in enumerate(self.P["stripes"]):
            st = 7.3 + i * 0.05
            p = seg(t, st, st + 0.6)
            if p <= 0:
                continue
            e = out_expo(p)
            sign = 1 if i % 2 == 0 else -1
            dist = (1 - e) * 900 * u * sign
            px = ox + lx * s + DIR[0] * dist
            py = oy + ly * s + DIR[1] * dist
            if p < 0.25:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v, a=p / 0.25: int(v * a)))
            comp(canvas, im, px, py)
        # 워드마크: 심볼 뒤에서 오른쪽으로 펼쳐짐
        if t > 9.0:
            layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            for i, (im, (lx, ly)) in enumerate(self.P["letters"]):
                st = 9.05 + i * 0.055
                p = seg(t, st, st + 0.55)
                if p <= 0:
                    continue
                e = out_expo(p)
                dx = -(1 - e) * 70 * s
                px, py = ox + lx * s + dx, oy + ly * s
                if p < 0.4:
                    im = im.copy()
                    im.putalpha(im.getchannel("A").point(lambda v, a=p / 0.4: int(v * a)))
                comp(layer, im, px, py)
            clip_x = int(ox + 90 * s)
            a = np.array(layer.getchannel("A"))
            a[:, :max(0, clip_x)] = 0
            layer.putalpha(Image.fromarray(a))
            canvas.alpha_composite(layer)
        # 태그라인(흐림에서 부드럽게)
        self.tagline(canvas, in_out(seg(t, 9.7, 10.8)), o_fin)
        # 마지막 빛 스윕(사선 위를 지나가는 하이라이트)
        sp_t = seg(t, 10.5, 11.2)
        if 0 < sp_t < 1:
            band = Image.new("L", canvas.size, 0)
            bx = ox + lerp(-20, 110, in_out(sp_t)) * s
            bd = ImageDraw.Draw(band)
            wdt = 14 * s
            bd.polygon([(bx, oy - 10 * s), (bx + wdt, oy - 10 * s), (bx + wdt - 40 * s, oy + 100 * s), (bx - 40 * s, oy + 100 * s)], fill=110)
            band = band.filter(ImageFilter.GaussianBlur(6 * s))
            sym = Image.new("L", canvas.size, 0)
            for im, (lx, ly) in [self.P["tri"]] + self.P["stripes"]:
                sym.paste(im.getchannel("A"), (int(ox + lx * s), int(oy + ly * s)), im.getchannel("A"))  # paste는 음수 좌표 허용
            m = ImageChops.multiply(band, sym)
            white = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
            white.putalpha(m)
            canvas.alpha_composite(white)

    def tagline(self, canvas, e, o_fin):
        """로고 아래 한 줄. e=1이면 인트로·아웃트로가 같은 픽셀로 그린다."""
        if e <= 0:
            return
        s, u = self.s, self.u
        f = self.ftag
        sp = 3 * u
        w = sum(f.getlength(c) for c in TAGLINE) + sp * (len(TAGLINE) - 1)
        x = self.cx - w / 2
        y = o_fin[1] + 90 * s + (70 if not self.portrait else 90) * u
        col = (92, 84, 112)
        if e >= 1:
            d = ImageDraw.Draw(canvas)
            for c in TAGLINE:
                d.text((x, y), c, font=f, fill=col, anchor="ls")
                x += f.getlength(c) + sp
            return
        layer = Image.new("RGBA", canvas.size, (*col, 0))
        d = ImageDraw.Draw(layer)
        y += (1 - e) * 12 * u
        for c in TAGLINE:
            d.text((x, y), c, font=f, fill=(*col, 255), anchor="ls")
            x += f.getlength(c) + sp
        r = (1 - e) * 10 * u
        if r > 0.3:
            layer = layer.filter(ImageFilter.GaussianBlur(r))
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * e)))
        canvas.alpha_composite(layer)

    # ---- 아웃트로(인트로와 같은 마지막 화면, 다른 움직임)
    def outro_logo(self, canvas, t):
        s, u = self.s, self.u
        o_sym = (self.cx - 43 * s, self.cy - 50 * s)
        lift = (40 if not self.portrait else 60) * u
        o_fin = (self.cx - LG.LOGO_W / 2 * s, self.cy - 45 * s - lift)
        k = in_out(seg(t, 2.6, 3.25))
        ox, oy = lerp(o_sym[0], o_fin[0], k), lerp(o_sym[1], o_fin[1], k)
        # 삼각형: 살짝 돌며 커짐
        p = seg(t, 2.0, 2.65)
        if p > 0:
            im, (lx, ly) = self.P["tri"]
            if p >= 1:
                comp(canvas, im, ox + lx * s, oy + ly * s)
            else:
                sc = 0.55 + 0.45 * out_back(p, 1.4)
                ang = -28 * (1 - out_cubic(p))
                sim = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.BICUBIC).rotate(ang, Image.BICUBIC, expand=True)
                sim.putalpha(sim.getchannel("A").point(lambda v, a=min(1, p / 0.35): int(v * a)))
                cx, cy = ox + (lx + im.size[0] / s / 2) * s, oy + (ly + im.size[1] / s / 2) * s
                comp(canvas, sim, cx - sim.size[0] / 2, cy - sim.size[1] / 2)
        # 사선: 아래(왼쪽)에서 위(오른쪽)로 그려지듯 차례로
        cache = self.__dict__.setdefault("_proj", {})
        for i, (im, (lx, ly)) in enumerate(self.P["stripes"]):
            f = out_cubic(seg(t, 1.6 + i * 0.035, 2.15 + i * 0.035))
            if f <= 0:
                continue
            if f >= 1:
                comp(canvas, im, ox + lx * s, oy + ly * s)
                continue
            if i not in cache:
                hh, ww = im.size[1], im.size[0]
                yy, xx = np.mgrid[0:hh, 0:ww]
                pr = xx * DIR[0] + yy * DIR[1]
                a0 = np.array(im.getchannel("A")) > 8
                lo, hi = (pr[a0].min(), pr[a0].max()) if a0.any() else (pr.min(), pr.max())
                cache[i] = ((pr - lo) / max(1e-6, hi - lo), np.array(im.getchannel("A"), np.float32))
            pr, al = cache[i]
            soft = 0.08
            m = np.clip((f * (1 + soft) - pr) / soft, 0, 1)
            sim = im.copy()
            sim.putalpha(Image.fromarray((al * m).astype(np.uint8)))
            comp(canvas, sim, ox + lx * s, oy + ly * s)
        # 글자: 아래에서 차례로 떠오름
        for i, (im, (lx, ly)) in enumerate(self.P["letters"]):
            e = out_expo(seg(t, 2.85 + i * 0.08, 3.6 + i * 0.08))
            if e <= 0:
                continue
            if e >= 1:
                comp(canvas, im, ox + lx * s, oy + ly * s)
                continue
            sim = im.copy()
            sim.putalpha(sim.getchannel("A").point(lambda v, a=min(1, e * 1.4): int(v * a)))
            comp(canvas, sim, ox + lx * s, oy + ly * s + (1 - e) * 16 * u)
        self.tagline(canvas, in_out(seg(t, 3.5, 4.7)), o_fin)

    def outro_frame(self, t):
        S, u = SS, self.u
        iris = seg(t, 1.45, 2.05)
        canvas = Image.new("RGBA", (self.CW, self.CH), (*DARK, 255))
        if iris < 1:
            glow = Image.new("RGB", (self.CW, self.CH), (0, 0, 0))
            d, g = ImageDraw.Draw(canvas), ImageDraw.Draw(glow)
            # 가운데에서 가로 빛줄기(앞 영상의 막대 12개에서 이어짐)
            lp = out_expo(seg(t, 0.05, 0.6)) * (1 - seg(t, 0.55, 0.8))
            if lp > 0:
                half = 700 * S * out_expo(seg(t, 0.05, 0.6))
                n = 28
                for j in range(n):
                    x0 = self.cx - half + 2 * half * j / n
                    x1 = self.cx - half + 2 * half * (j + 1) / n
                    c = mix(DARK, grad3(j / (n - 1)), lp)
                    d.line([(x0, self.cy), (x1, self.cy)], fill=c, width=int(6 * S))
            amps = [0.55, 0.92, 0.38, 0.78, 0.5]
            env = lambda k: math.sin(math.pi * (k + 0.5) / 12) ** 0.7
            tilt = in_out(seg(t, 1.3, 1.8))
            ang0, ang1 = -math.pi / 2, math.atan2(DIR[1], DIR[0])
            for k in range(12):
                cx = (960 + (k - 5.5) * 46) * S
                # 높이: 점선 → 말하듯 → 기울며 짧아짐
                h = 8.4
                if t > 0.55:
                    q = (t - 0.55) / 0.15
                    i0 = min(len(amps) - 1, int(q))
                    i1 = min(len(amps) - 1, i0 + 1)
                    fr = in_out(q - int(q)) if q < len(amps) - 1 else 1
                    a = lerp(amps[i0], amps[i1], fr) * (0.75 + 0.25 * ((k * 7) % 5) / 4)
                    rise = out_cubic(seg(t, 0.55, 0.8))
                    h = lerp(8.4, max(8.4, a * env(k) * 420), rise)
                h = lerp(h, 420 * 0.22, tilt)
                col = G_RGB[k]
                if tilt <= 0 and h <= 8.5:
                    d.rounded_rectangle([cx - 9 * S, self.cy - 4.2 * S, cx + 9 * S, self.cy + 4.2 * S], radius=int(4.2 * S), fill=col)
                    continue
                ang = lerp(ang0, ang1, tilt)
                ccx = cx + (k - 5.5) * -34 * S * tilt
                ccy = self.cy - 75 * S * tilt
                dx, dy = math.cos(ang) * (h - 18) / 2 * S, math.sin(ang) * (h - 18) / 2 * S
                fade = 1 - seg(t, 1.75, 2.0)
                c = mix(DARK, col, fade)
                self.line(d, (ccx - dx, ccy - dy), (ccx + dx, ccy + dy), 18 * S, c)
                self.line(g, (ccx - dx, ccy - dy), (ccx + dx, ccy + dy), 18 * S * 2.4, mix((0, 0, 0), c, 0.45 * min(1, (h - 8.4) / 60)))
            gs = glow.resize((self.CW // 8, self.CH // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
            canvas = ImageChops.add(canvas.convert("RGB"), gs.resize((self.CW, self.CH), Image.BILINEAR)).convert("RGBA")
        if iris > 0:
            light = Image.new("RGBA", canvas.size, (*LIGHT, 255))
            self.outro_logo(light, t)
            if iris >= 1:
                canvas = light
            else:
                R = in_out(iris) * self.diag * 0.62
                m = Image.new("L", canvas.size, 0)
                cyy = self.cy * 0.86
                ImageDraw.Draw(m).ellipse([self.cx - R, cyy - R, self.cx + R, cyy + R], fill=255)
                canvas.paste(light, (0, 0), m)
        return canvas.convert("RGB").reduce(SS)

    # ---- 프레임
    def frame(self, t):
        u = self.u
        wipe = seg(t, 6.95, 7.5)
        if t < 7.5:
            canvas = Image.new("RGBA", (self.CW, self.CH), (*DARK, 255))
            glow = Image.new("RGB", (self.CW, self.CH), (0, 0, 0))
            d, g = ImageDraw.Draw(canvas), ImageDraw.Draw(glow)
            self.bars(d, g, t)
            self.bubble(canvas, g, t, "카드를 잃어버렸어요", 4.05, False)
            self.bubble(canvas, g, t, "분실 신고, 바로 도와드릴게요", 4.45, True, typing_until=4.78)
            self.caption(d, "02  CONVERSATIONAL AI", t, 4.15, 5.4)
            self.network(d, g, t)
            gs = glow.resize((self.CW // 8, self.CH // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
            gs = gs.resize((self.CW, self.CH), Image.BILINEAR)
            rgb = ImageChops.add(canvas.convert("RGB"), gs)
            canvas = rgb.convert("RGBA")
            if wipe > 0:
                R = out_cubic(wipe) * self.diag * 0.55
                m = Image.new("L", canvas.size, 0)
                ImageDraw.Draw(m).ellipse([self.cx - R, self.cy - R, self.cx + R, self.cy + R], fill=255)
                light = Image.new("RGBA", canvas.size, (*LIGHT, 255))
                self.logo(light, t)
                canvas.paste(light, (0, 0), m)
        else:
            canvas = Image.new("RGBA", (self.CW, self.CH), (*LIGHT, 255))
            self.logo(canvas, t)
        # 끝 0.4초 동안 아주 살짝 어두워지지 않고 그대로 유지(로고 정지 화면으로 끝)
        return canvas.convert("RGB").reduce(SS)


def comp(canvas, im, x, y):
    """화면 밖으로 나가도 안전한 합성."""
    x, y = int(x), int(y)
    sx, sy = max(0, -x), max(0, -y)
    if sx >= im.size[0] or sy >= im.size[1] or x >= canvas.size[0] or y >= canvas.size[1]:
        return
    w = min(im.size[0] - sx, canvas.size[0] - max(0, x))
    h = min(im.size[1] - sy, canvas.size[1] - max(0, y))
    canvas.alpha_composite(im.crop((sx, sy, sx + w, sy + h)), (max(0, x), max(0, y)))


def grad_img(w, h, c0, c1):
    t = np.linspace(0, 1, max(1, w))[None, :, None]
    rgb = (np.array(c0) + (np.array(c1) - np.array(c0)) * t) * np.ones((max(1, h), 1, 1))
    return Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")


_S = {}


def _render(i):
    sc = _S["scene"]
    return (sc.outro_frame(i / FPS) if _S.get("kind") == "outro" else sc.frame(i / FPS)).tobytes()


OUTRO_DUR = 7.5


def render(fmt, kind="intro"):
    W, H = (1920, 1080) if fmt == "16x9" else (1080, 1920)
    OUT.mkdir(exist_ok=True)
    dur = DUR if kind == "intro" else OUTRO_DUR
    wav = OUT / f"{kind}_sfx.wav"
    (sfx.write if kind == "intro" else sfx.write_outro)(wav, dur)
    _S["scene"] = Scene(W, H)
    _S["kind"] = kind
    path = OUT / f"rapeech_{kind}_{fmt}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * FPS)
    with mp.get_context("fork").Pool(mp.cpu_count()) as pool:
        for buf in pool.imap(_render, range(n), chunksize=4):
            p.stdin.write(buf)
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg 실패")
    return path


def stills(fmt, times, kind="intro"):
    W, H = (1920, 1080) if fmt == "16x9" else (1080, 1920)
    sc = Scene(W, H)
    ims = [(sc.outro_frame(t) if kind == "outro" else sc.frame(t)) for t in times]
    tw = 480 if fmt == "16x9" else 270
    th = int(tw * H / W)
    cols = min(4 if fmt == "16x9" else 6, len(ims))
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 8) + 8), (60, 60, 60))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + 8)))
    OUT.mkdir(exist_ok=True)
    path = OUT / f"stills_{kind}_{fmt}.jpg"
    sheet.save(path, quality=90)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmt", default="all", choices=["all", "16x9", "9x16"])
    ap.add_argument("--kind", default="intro", choices=["intro", "outro"])
    ap.add_argument("--stills")
    a = ap.parse_args()
    fmts = ["16x9", "9x16"] if a.fmt == "all" else [a.fmt]
    for f in fmts:
        if a.stills:
            print(stills(f, [float(x) for x in a.stills.split(",")], a.kind))
        else:
            print(render(f, a.kind))
