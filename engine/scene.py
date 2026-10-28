"""슬라이드 JSON → 화면 요소(Element) 목록.

숏츠와 카드뉴스가 같은 코드를 쓴다. 카드뉴스는 모든 애니메이션이 끝난 마지막 상태를 PNG로 저장한다.
"""
import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import style as S


# ---------------------------------------------------------------- 기본 도구
@lru_cache(maxsize=256)
def font(kind, size):
    return ImageFont.truetype(str(S.FONT_DIR / S.FONTS[kind]), max(8, int(round(size))))


def text_font(kind, size, text):
    """모노 폰트에는 한글이 없으므로 한글이 섞이면 Pretendard로 바꾼다."""
    if kind.startswith("mono") and re.search(r"[\uac00-\ud7a3\u3131-\u318e]", text):
        return font("semi", size * 0.98)
    return font(kind, size)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def parse_marks(text):
    """'이제 [AI]가' → [('이제 ', False), ('AI', True), ('가', False)]"""
    out = []
    for i, part in enumerate(re.split(r"\[|\]", text)):
        if part:
            out.append((part, i % 2 == 1))
    return out


def plain(text):
    return text.replace("[", "").replace("]", "")


def wrap_rich(text, f, maxw):
    """[..] 표시를 유지한 채 폭에 맞춰 줄바꿈. 반환: 줄 목록, 줄마다 (문자열, 강조여부) 목록."""
    lines = []
    for para in text.split("\n"):
        chars = []
        for seg, hl in parse_marks(para):
            chars += [(c, hl) for c in seg]
        # 단어 단위(공백 포함)로 묶기
        words, cur = [], []
        for c in chars:
            cur.append(c)
            if c[0] == " ":
                words.append(cur)
                cur = []
        if cur:
            words.append(cur)
        line = []
        for w in words:
            trial = line + w
            if f.getlength("".join(c for c, _ in trial).rstrip()) <= maxw or not line:
                if f.getlength("".join(c for c, _ in trial).rstrip()) > maxw:
                    # 단어 하나가 너무 길면 글자 단위로 자른다
                    for c in w:
                        if f.getlength("".join(x for x, _ in line + [c])) > maxw and line:
                            lines.append(line)
                            line = []
                        line.append(c)
                else:
                    line = trial
            else:
                lines.append(line)
                line = list(w)
        lines.append(line)
    # 끝 공백 제거 후 run으로 합치기
    result = []
    for line in lines:
        while line and line[-1][0] == " ":
            line = line[:-1]
        runs = []
        for c, hl in line:
            if runs and runs[-1][1] == hl:
                runs[-1][0] += c
            else:
                runs.append([c, hl])
        result.append([(t, h) for t, h in runs])
    return result


def rich_width(runs, f):
    return f.getlength("".join(t for t, _ in runs))


def draw_runs(d, x, y, runs, f, color, hl_color, anchor="ls"):
    for t, hl in runs:
        d.text((x, y), t, font=f, fill=hl_color if hl else color, anchor=anchor)
        x += f.getlength(t)


def rounded(size, radius, fill):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return im


def with_shadow(im, blur=22, offset=12, alpha=70):
    """카드 그림자. 반환 이미지와 원본의 (x, y) 오프셋."""
    pad = blur * 2
    W, H = im.size[0] + pad * 2, im.size[1] + pad * 2 + offset
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: v * alpha // 255)
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
    blk.putalpha(a)
    sh.paste(blk, (pad, pad + offset), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(im, (pad, pad))
    return sh, pad


# ---------------------------------------------------------------- 요소
class Element:
    """화면 요소 하나. t0에 페이드인하며 올라온다."""

    def __init__(self, img, x, y, t0, ox=0, oy=0):
        self.img, self.x, self.y, self.t0 = img, x, y, t0
        self.ox, self.oy = ox, oy  # 그림자 여백
        self.end = t0 + S.T_FADE

    def frame(self, t):
        return self.img

    def draw(self, canvas, t, final=False):
        if final:
            p = 1.0
        else:
            p = ease_out((t - self.t0) / S.T_FADE)
            if p <= 0:
                return
        img = self.frame(1e9 if final else t)
        if img is None:
            return
        dy = int(S.T_RISE * (1 - p))
        pos = (int(self.x - self.ox), int(self.y - self.oy + dy))
        if p >= 1:
            canvas.alpha_composite(img, clip_dest(canvas, img, pos)[0], clip_dest(canvas, img, pos)[1])
        else:
            a = img.getchannel("A").point(lambda v, p=p: int(v * p))
            tmp = img.copy()
            tmp.putalpha(a)
            dest, src = clip_dest(canvas, tmp, pos)
            canvas.alpha_composite(tmp, dest, src)


def clip_dest(canvas, img, pos):
    x, y = pos
    sx, sy = max(0, -x), max(0, -y)
    return (max(0, x), max(0, y)), (sx, sy)


class SweepTitleLine(Element):
    """타이틀 한 줄. 강조 단어는 주황 박스가 왼쪽에서 쓸려 들어온다."""

    def __init__(self, base, hl, boxes, x, y, t0):
        super().__init__(base, x, y, t0)
        self.hl, self.boxes = hl, boxes  # boxes: [(x0, x1)] 줄 이미지 기준
        self.end = t0 + 0.15 + S.T_SWEEP + 0.1
        self._cache = {}

    def frame(self, t):
        if not self.boxes:
            return self.img
        p = ease_out((t - self.t0 - 0.15) / S.T_SWEEP)
        key = round(p, 3)
        if key in self._cache:
            return self._cache[key]
        im = self.img.copy()
        if p > 0:
            mask = Image.new("L", im.size, 0)
            md = ImageDraw.Draw(mask)
            for x0, x1 in self.boxes:
                md.rectangle([x0, 0, x0 + (x1 - x0) * p, im.size[1]], fill=255)
            layer = self.hl.copy()
            layer.putalpha(Image.fromarray(np.minimum(np.array(layer.getchannel("A")), np.array(mask))))
            im.alpha_composite(layer)
        if p >= 1 or len(self._cache) < 64:
            self._cache[key] = im
        return im


class CountTile(Element):
    """숫자 타일. 값이 0부터 카운트업."""

    def __init__(self, bg, painter, value, x, y, t0, ox, oy):
        super().__init__(bg, x, y, t0, ox, oy)
        self.painter, self.value = painter, value
        m = re.search(r"\d[\d,]*(\.\d+)?", value)
        self.m = m
        self.end = t0 + S.T_COUNT + 0.05
        self._cache = {}

    def text_at(self, t):
        if not self.m:
            return self.value
        p = ease_out((t - self.t0) / S.T_COUNT)
        num = self.m.group(0)
        dec = len(num.split(".")[1]) if "." in num else 0
        target = float(num.replace(",", ""))
        v = target * p
        s = f"{v:,.{dec}f}" if "," in num else f"{v:.{dec}f}"
        return self.value[: self.m.start()] + s + self.value[self.m.end():]

    def frame(self, t):
        s = self.text_at(t)
        if s not in self._cache:
            im = self.img.copy()
            self.painter(im, s)
            self._cache[s] = im
        return self._cache[s]


# ---------------------------------------------------------------- 레이아웃
class Builder:
    def __init__(self, fmt, scale_mul=1.0):
        self.F = S.FORMATS[fmt]
        self.fmt = fmt
        self.k = self.F["scale"] * scale_mul
        self.W = self.F["W"]
        self.cw = self.W - S.MARGIN * 2  # 콘텐츠 폭
        self.els = []
        self.y = self.F["content_top"]
        self.t = 0.0
        self.warnings = []

    def px(self, v):
        return int(round(v * self.k))

    def add(self, el):
        self.els.append(el)

    # ---- 배지: 검정 알약 + 노란 별
    def badge(self, spec):
        stars = int(spec.get("stars", 3))
        text = spec.get("text", "")
        fs = self.px(31)
        f = font("bold", fs)
        # 별은 직접 그린다
        sw = self.px(29)
        gap = self.px(14)
        tw = f.getlength(text)
        h = self.px(60)
        w = int(self.px(28) * 2 + sw * 3 + gap + tw)
        im = rounded((w, h), h // 2, CARD_RGBA())
        d = ImageDraw.Draw(im)
        x = self.px(28)
        for i in range(3):
            draw_star(d, x + sw / 2 + i * sw, h / 2, sw * 0.46, S.YELLOW if i < stars else (110, 108, 104))
        d.text((x + sw * 3 + gap, h / 2), text, font=f, fill=S.WHITE, anchor="lm")
        self.add(Element(im, (self.W - w) / 2, self.y, self.t))
        self.y += h + self.px(34)

    def kicker(self, text):
        f = font("semi", self.px(40))
        w = int(f.getlength(text)) + 4
        h = self.px(56)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, h * 0.78), text, font=f, fill=(70, 67, 62), anchor="ls")
        self.add(Element(im, (self.W - w) / 2, self.y, self.t))
        self.y += h + self.px(14)
        self.t += S.T_LINE_GAP

    def title(self, lines, size=112):
        fs = self.px(size)
        for line in lines:
            f = font("black", fs)
            segs = parse_marks(line)
            pad = int(fs * 0.13)
            # 너무 길면 줄 크기를 줄인다
            fs_line = fs
            while True:
                f = font("black", fs_line)
                pad = int(fs_line * 0.13)
                width = sum(f.getlength(t) + (pad * 2 if hl else 0) for t, hl in segs)
                if width <= self.cw or fs_line < fs * 0.7:
                    break
                fs_line -= 2
            if fs_line != fs:
                self.warnings.append(f"타이틀 줄이 길어 글자를 줄임: {plain(line)}")
            lh = int(fs * 1.24)
            w = int(width) + 4
            base = Image.new("RGBA", (w, lh), (0, 0, 0, 0))
            hl = Image.new("RGBA", (w, lh), (0, 0, 0, 0))
            db, dh = ImageDraw.Draw(base), ImageDraw.Draw(hl)
            bl = int(lh * 0.80)  # baseline
            gb = f.getbbox("가", anchor="ls")
            top, bot = bl + gb[1] - int(fs_line * 0.10), bl + gb[3] + int(fs_line * 0.12)
            x, boxes = 0, []
            for t, is_hl in segs:
                tw = f.getlength(t)
                if is_hl:
                    dh.rounded_rectangle([x, top, x + tw + pad * 2, bot], radius=int(fs_line * 0.14), fill=S.ORANGE)
                    dh.text((x + pad, bl), t, font=f, fill=S.WHITE, anchor="ls")
                    boxes.append((x, x + tw + pad * 2))
                    x += tw + pad * 2
                else:
                    db.text((x, bl), t, font=f, fill=S.INK, anchor="ls")
                    x += tw
            self.add(SweepTitleLine(base, hl, boxes, (self.W - w) / 2, self.y, self.t))
            self.y += lh
            self.t += S.T_LINE_GAP
        self.y += self.px(40)

    def sub(self, text, size=36, color=None):
        f = font("medium", self.px(size))
        for runs in wrap_rich(text, f, self.cw):
            w = int(rich_width(runs, f)) + 4
            h = int(self.px(size) * 1.45)
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw_runs(ImageDraw.Draw(im), 0, int(h * 0.75), runs, f, color or S.GRAY_ON_LIGHT, S.ORANGE)
            self.add(Element(im, (self.W - w) / 2, self.y, self.t))
            self.y += h
            self.t += S.T_LINE_GAP * 0.6
        self.y += self.px(30)

    # ---- 블록(카드)
    def start_blocks(self):
        self.t = max(self.t, S.T_CARD)

    def card_frame(self, w, h, fill=None):
        return rounded((w, h), self.px(30), fill or CARD_RGBA())

    def place_card(self, im, x=None, el_cls=None):
        sh, pad = with_shadow(im, blur=self.px(22), offset=self.px(14))
        x = S.MARGIN if x is None else x
        self.add(Element(sh, x, self.y, self.t, pad, pad))

    def card_title(self, d, text, x, y, color=None):
        f = font("semi", self.px(29))
        d.text((x, y), text, font=f, fill=color or S.GRAY_ON_DARK, anchor="ls")

    def block(self, b):
        kind = b["type"]
        getattr(self, "blk_" + kind)(b)
        self.y += self.px(26)
        self.t += S.T_CARD_GAP

    def blk_tiles(self, b):
        items = b["items"]
        cols = b.get("cols", 2 if len(items) != 3 else 3)
        gap = self.px(22)
        tw = (self.cw - gap * (cols - 1)) // cols
        th = self.px(b.get("height", 200))
        vs = self.px(b.get("value_size", 84 if cols == 2 else 70))
        rows = math.ceil(len(items) / cols)
        for r in range(rows):
            for c in range(cols):
                i = r * cols + c
                if i >= len(items):
                    break
                it = items[i]
                bg = self.card_frame(tw, th, CARD_RGBA(dim=it.get("dim")))
                lf = font("semi", self.px(30))
                lines = wrap_rich(it.get("label", ""), lf, tw - self.px(30))
                d = ImageDraw.Draw(bg)
                ly = th - self.px(30) - (len(lines) - 1) * int(self.px(30) * 1.3)
                for k, runs in enumerate(lines):
                    lw = rich_width(runs, lf)
                    draw_runs(d, (tw - lw) / 2, ly + k * int(self.px(30) * 1.3), runs, lf, S.GRAY_ON_DARK, S.YELLOW)
                vf = font("xbold", vs)
                col = S.YELLOW if not it.get("white") else S.WHITE
                vy = int(th * 0.52) if lines and lines[0] else int(th * 0.62)

                def painter(im, s, vf=vf, col=col, vy=vy, tw=tw, value=it["value"]):
                    dd = ImageDraw.Draw(im)
                    # 최종 값 폭으로 가운데 정렬해 카운트 중 흔들리지 않게
                    fw = vf.getlength(value)
                    pad = self.pad_shadow
                    dd.text((pad + (tw - fw) / 2, pad + vy), s, font=vf, fill=col, anchor="ls")
                    if fw > tw - 20:
                        pass

                if vf.getlength(it["value"]) > tw - self.px(24):
                    self.warnings.append(f"타일 숫자가 칸보다 김: {it['value']}")
                sh, pad = with_shadow(bg, blur=self.px(22), offset=self.px(14))
                self.pad_shadow = pad
                x = S.MARGIN + c * (tw + gap)
                el = CountTile(sh, painter, it["value"], x, self.y, self.t + i * S.T_ROW_GAP, pad, pad)
                self.add(el)
            self.y += th + (gap if r < rows - 1 else 0)
        self.t += (len(items) - 1) * S.T_ROW_GAP

    def _rows_card(self, b, rows_fn):
        """표·불릿·타임라인 공통: 카드 바탕 + 행마다 따로 등장."""
        padx, pady = self.px(44), self.px(40)
        inner = self.cw - padx * 2
        title = b.get("title")
        rows = rows_fn(inner)  # [(height, painter(draw, x, y))]
        th = self.px(46) if title else 0
        h = pady * 2 + th + sum(r[0] for r in rows)
        bg = self.card_frame(self.cw, h, CARD_RGBA(dim=b.get("dim")))
        if title:
            self.card_title(ImageDraw.Draw(bg), title, padx, pady + self.px(24))
        sh, pad = with_shadow(bg, blur=self.px(22), offset=self.px(14))
        self.add(Element(sh, S.MARGIN, self.y, self.t, pad, pad))
        y = pady + th
        t = self.t + 0.12
        for rh, painter in rows:
            im = Image.new("RGBA", (self.cw, rh), (0, 0, 0, 0))
            painter(ImageDraw.Draw(im), padx, 0)
            self.add(Element(im, S.MARGIN, self.y + y, t))
            y += rh
            t += S.T_ROW_GAP
        self.y += h
        self.t = t - S.T_ROW_GAP

    def blk_table(self, b):
        fs = self.px(b.get("size", 40))
        kf, vf = font("semi", fs), font("xbold", fs)

        def rows(inner):
            out = []
            n = len(b["rows"])
            for i, row in enumerate(b["rows"]):
                k, v = row[0], row[1]
                trend = row[2] if len(row) > 2 else None
                vw = inner * 0.58
                vlines = wrap_rich(v, vf, vw)
                lh = int(fs * 1.35)
                rh = max(1, len(vlines)) * lh + self.px(30)

                def p(d, x, y, k=k, vlines=vlines, trend=trend, rh=rh, last=(i == n - 1), lh=lh):
                    d.text((x, y + self.px(15) + lh * 0.78), plain(k), font=kf, fill=S.GRAY_ON_DARK, anchor="ls")
                    right = x + inner - (self.px(40) if trend else 0)
                    for j, runs in enumerate(vlines):
                        w = rich_width(runs, vf)
                        draw_runs(d, right - w, y + self.px(15) + lh * 0.78 + j * lh, runs, vf, S.WHITE, S.YELLOW)
                    if trend:
                        cx, cy = x + inner - self.px(14), y + self.px(15) + lh * 0.5
                        draw_arrow(d, cx, cy, self.px(15), trend)
                    if not last:
                        d.line([x, rh - 1, x + inner, rh - 1], fill=(58, 58, 58), width=2)
                out.append((rh, p))
            return out

        self._rows_card(b, rows)

    def blk_bullets(self, b):
        fs = self.px(b.get("size", 38))
        f = font("semi", fs)

        def rows(inner):
            out = []
            for it in b["items"]:
                lines = wrap_rich(it, f, inner - self.px(34))
                lh = int(fs * 1.42)
                rh = len(lines) * lh + self.px(16)

                def p(d, x, y, lines=lines, lh=lh):
                    r = self.px(7)
                    d.ellipse([x, y + lh * 0.5 - r, x + 2 * r, y + lh * 0.5 + r], fill=S.ORANGE)
                    for j, runs in enumerate(lines):
                        draw_runs(d, x + self.px(34), y + lh * 0.74 + j * lh, runs, f, S.WHITE, S.YELLOW)
                out.append((rh, p))
            return out

        self._rows_card(b, rows)

    def blk_timeline(self, b):
        fs = self.px(b.get("size", 36))
        tf = font("semi", fs)

        def rows(inner):
            out = []
            items = b["items"]
            yw = max(text_font("mono", self.px(36), it["year"]).getlength(it["year"]) for it in items)
            for i, it in enumerate(items):
                tx = int(self.px(32) + yw + self.px(26))
                lines = wrap_rich(it["text"], tf, inner - tx)
                lh = int(fs * 1.42)
                rh = len(lines) * lh + self.px(26)

                def p(d, x, y, it=it, lines=lines, lh=lh, rh=rh, last=(i == len(items) - 1), first=(i == 0), tx=tx):
                    cx = x + self.px(8)
                    if not last:
                        d.line([cx, y + lh * 0.5, cx, rh], fill=(80, 80, 80), width=3)
                    if not first:
                        d.line([cx, 0, cx, y + lh * 0.5], fill=(80, 80, 80), width=3)
                    r = self.px(8)
                    d.ellipse([cx - r, y + lh * 0.5 - r, cx + r, y + lh * 0.5 + r], fill=S.ORANGE)
                    d.text((x + self.px(32), y + lh * 0.74), it["year"], font=text_font("mono", self.px(36), it["year"]), fill=S.YELLOW, anchor="ls")
                    for j, runs in enumerate(lines):
                        draw_runs(d, x + tx, y + lh * 0.74 + j * lh, runs, tf, S.WHITE, S.YELLOW)
                out.append((rh, p))
            return out

        self._rows_card(b, rows)

    def blk_compare(self, b):
        gap = self.px(22)
        w = (self.cw - gap) // 2
        fs = self.px(b.get("size", 32))
        f = font("semi", fs)
        lh = int(fs * 1.42)
        cols = [b["before"], b["after"]]
        wrapped = [[wrap_rich(it, f, w - self.px(70)) for it in c["items"]] for c in cols]
        body_h = max(sum(len(x) * lh + self.px(14) for x in col) for col in wrapped)
        h = self.px(40) * 2 + self.px(64) + body_h
        for ci, c in enumerate(cols):
            after = ci == 1
            bg = self.card_frame(w, h, CARD_RGBA(dim=not after))
            d = ImageDraw.Draw(bg)
            px0, y = self.px(34), self.px(40)
            lab = c.get("label", "AFTER" if after else "BEFORE")
            d.text((px0, y + self.px(30)), lab, font=text_font("mono", self.px(26), lab),
                   fill=S.YELLOW if after else S.GRAY_ON_DARK, anchor="ls")
            d.text((px0, y + self.px(66)), c.get("title", ""), font=font("xbold", self.px(32)), fill=S.WHITE, anchor="ls")
            y += self.px(64) + self.px(26)
            for lines in wrapped[ci]:
                r = self.px(6)
                d.ellipse([px0, y + lh * 0.5 - r, px0 + 2 * r, y + lh * 0.5 + r], fill=S.ORANGE if after else (120, 118, 112))
                for j, runs in enumerate(lines):
                    draw_runs(d, px0 + self.px(26), y + lh * 0.74 + j * lh, runs, f,
                              S.WHITE if after else (200, 197, 190), S.YELLOW)
                y += len(lines) * lh + self.px(14)
            if y > h:
                self.warnings.append("비교 카드 내용이 넘침")
            sh, pad = with_shadow(bg, blur=self.px(22), offset=self.px(14))
            self.add(Element(sh, S.MARGIN + ci * (w + gap), self.y, self.t + ci * 0.25, pad, pad))
        self.y += h
        self.t += 0.25

    def blk_hero(self, b):
        """큰 숫자 하나 + 설명 (도넛 그래프 선택)."""
        h = self.px(b.get("height", 330))
        bg = self.card_frame(self.cw, h)
        d = ImageDraw.Draw(bg)
        ring = b.get("ring")
        lx = self.px(60)
        if ring is not None:
            R = int(h * 0.36)
            cx, cy = self.px(60) + R, h // 2
            wdt = self.px(26)
            d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(64, 64, 64), width=wdt)
            d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * ring / 100, fill=S.ORANGE, width=wdt)
            lx = cx + R + self.px(50)
            vcx = cx
        tf = font("xbold", self.px(42))
        sf = font("medium", self.px(28))
        y = self.px(70)
        if b.get("kicker"):
            d.text((lx, y), b["kicker"], font=font("semi", self.px(26)), fill=S.GRAY_ON_DARK, anchor="ls")
            y += self.px(56)
        for runs in wrap_rich(b.get("text", ""), tf, self.cw - lx - self.px(40)):
            draw_runs(d, lx, y, runs, tf, S.WHITE, S.YELLOW)
            y += int(self.px(42) * 1.3)
        y += self.px(12)
        for runs in wrap_rich(b.get("desc", ""), sf, self.cw - lx - self.px(40)):
            draw_runs(d, lx, y, runs, sf, S.GRAY_ON_DARK, S.YELLOW)
            y += int(self.px(28) * 1.4)
        if y > h:
            self.warnings.append("hero 카드 내용이 넘침")
        sh, pad = with_shadow(bg, blur=self.px(22), offset=self.px(14))
        vf = font("xbold", self.px(b.get("value_size", 76 if ring is not None else 110)))
        value = b["value"]

        def painter(im, s):
            dd = ImageDraw.Draw(im)
            if ring is not None:
                dd.text((pad + vcx, pad + h // 2), s, font=vf, fill=S.WHITE, anchor="mm")
            else:
                dd.text((pad + self.px(60), pad + h - self.px(60)), s, font=vf, fill=S.YELLOW, anchor="ls")

        self.add(CountTile(sh, painter, value, S.MARGIN, self.y, self.t, pad, pad))
        self.y += h

    def blk_chips(self, b):
        f = font("bold", self.px(28))
        h = self.px(58)
        gap = self.px(14)
        ims = []
        for it in b["items"]:
            hl = it.startswith("[") and it.endswith("]")
            t = plain(it)
            w = int(f.getlength(t) + self.px(48))
            im = rounded((w, h), h // 2, (*S.ORANGE, 255) if hl else CARD_RGBA())
            ImageDraw.Draw(im).text((w / 2, h / 2), t, font=f, fill=S.WHITE, anchor="mm")
            ims.append(im)
        total = sum(i.size[0] for i in ims) + gap * (len(ims) - 1)
        x = (self.W - total) / 2
        for k, im in enumerate(ims):
            self.add(Element(im, x, self.y, self.t + k * 0.08))
            x += im.size[0] + gap
        self.y += h

    def blk_box(self, b):
        """작은 검정 요약 상자(표지용)."""
        w = self.cw - self.px(80)
        tf, sf = font("bold", self.px(34)), font("medium", self.px(26))
        h = self.px(150) if b.get("sub") else self.px(100)
        bg = self.card_frame(w, h)
        d = ImageDraw.Draw(bg)
        d.text((w / 2, self.px(62)), b["text"], font=tf, fill=S.WHITE, anchor="ms")
        if b.get("sub"):
            d.text((w / 2, self.px(108)), b["sub"], font=sf, fill=S.GRAY_ON_DARK, anchor="ms")
        sh, pad = with_shadow(bg, blur=self.px(22), offset=self.px(14))
        self.add(Element(sh, (self.W - w) / 2, self.y, self.t, pad, pad))
        self.y += h

    def blk_note(self, b):
        """연한 상자에 한 줄 비교(예: 2.5¢ vs 3¢)."""
        f = font("bold", self.px(32))
        lines = wrap_rich(b["text"], f, self.cw - self.px(80))
        lh = int(self.px(32) * 1.45)
        h = len(lines) * lh + self.px(44)
        im = rounded((self.cw, h), self.px(20), (*S.PILL_BG, 255))
        d = ImageDraw.Draw(im)
        for j, runs in enumerate(lines):
            w = rich_width(runs, f)
            draw_runs(d, (self.cw - w) / 2, self.px(22) + lh * 0.75 + j * lh, runs, f, S.INK, S.ORANGE)
        self.add(Element(im, S.MARGIN, self.y, self.t))
        self.y += h

    # ---- 캡션과 출처
    def caption(self, lines):
        self.t += 0.1
        for i, line in enumerate(lines):
            f = font("bold" if i == 0 else "semi", self.px(35 if i == 0 else 30))
            for runs in wrap_rich(line, f, self.cw):
                w = int(rich_width(runs, f)) + 4
                h = int(f.size * 1.45)
                im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw_runs(ImageDraw.Draw(im), 0, int(h * 0.75), runs, f, S.INK if i == 0 else S.ORANGE, S.ORANGE)
                self.add(Element(im, (self.W - w) / 2, self.y, self.t))
                self.y += h
            self.t += S.T_LINE_GAP

    def source(self, text):
        f = text_font("mono_m", self.px(24), text)
        h = self.px(50)
        tw = f.getlength(text)
        w = int(tw + self.px(84))
        im = rounded((w, h), h // 2, (*S.PILL_BG, 255))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, outline=S.LINE, width=2)
        draw_arrow_ne(d, self.px(30), h / 2, self.px(9))
        d.text((self.px(54), h / 2), text, font=f, fill=S.GRAY_ON_LIGHT, anchor="lm")
        self.y += self.px(14)
        self.add(Element(im, (self.W - w) / 2, self.y, self.t + 0.15))
        self.y += h

    # ---- 마지막 장
    def outro(self, o):
        logo = o.get("logo", True)
        if o.get("kicker"):
            self.kicker(o["kicker"])
        self.title(o.get("title", ["매주 AI 소식,", "[1분]이면 끝"]))
        self.sub(o.get("sub", "다음 주 소식도 놓치지 않으려면"))
        bf = font("xbold", self.px(40))
        label = o.get("button", "팔로우하기")
        bw, bh = int(bf.getlength(label) + self.px(130)), self.px(98)
        im = rounded((bw, bh), bh // 2, (*S.ORANGE, 255))
        ImageDraw.Draw(im).text((bw / 2, bh / 2), label, font=bf, fill=S.WHITE, anchor="mm")
        sh, pad = with_shadow(im, blur=self.px(18), offset=self.px(10), alpha=60)
        self.t = max(self.t, S.T_CARD)
        self.add(Element(sh, (self.W - bw) / 2, self.y, self.t, pad, pad))
        self.y += bh + self.px(34)
        hf = font("medium", self.px(28))
        hint = o.get("hint", "좋아요 · 저장 · 공유도 부탁드려요")
        w = int(hf.getlength(hint)) + 4
        him = Image.new("RGBA", (w, self.px(44)), (0, 0, 0, 0))
        ImageDraw.Draw(him).text((0, self.px(34)), hint, font=hf, fill=S.GRAY_ON_LIGHT, anchor="ls")
        self.t += 0.2
        self.add(Element(him, (self.W - w) / 2, self.y, self.t))
        self.y += self.px(44)
        if logo:
            sym = Image.open(S.BRAND_DIR / "symbol" / "symbol_purple.png").convert("RGBA")
            lw = self.px(o.get("logo_size", 150))
            sym = sym.resize((lw, int(sym.size[1] * lw / sym.size[0])), Image.LANCZOS)
            self.y += self.px(90)
            self.t += 0.25
            self.add(Element(sym, (self.W - sym.size[0]) / 2, self.y, self.t))
            self.y += sym.size[1]


def CARD_RGBA(dim=False):
    return (*(S.CARD_DIM if dim else S.CARD), 255)


def draw_star(d, cx, cy, r, color):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=color)


def draw_arrow(d, cx, cy, s, trend):
    up = trend in ("up", "↑", "+")
    color = S.GREEN if up else S.ORANGE
    if up:
        d.polygon([(cx, cy - s), (cx - s * 0.8, cy), (cx + s * 0.8, cy)], fill=color)
        d.rectangle([cx - s * 0.25, cy, cx + s * 0.25, cy + s], fill=color)
    else:
        d.polygon([(cx, cy + s), (cx - s * 0.8, cy), (cx + s * 0.8, cy)], fill=color)
        d.rectangle([cx - s * 0.25, cy - s, cx + s * 0.25, cy], fill=color)


def draw_arrow_ne(d, cx, cy, s):
    w = max(2, int(s * 0.32))
    d.line([cx - s, cy + s, cx + s, cy - s], fill=S.ORANGE, width=w)
    d.line([cx - s * 0.1, cy - s, cx + s, cy - s], fill=S.ORANGE, width=w)
    d.line([cx + s, cy - s, cx + s, cy + s * 0.1], fill=S.ORANGE, width=w)


# ---------------------------------------------------------------- 슬라이드 → 요소
def build_slide(slide, fmt):
    """요소 목록과 경고를 돌려준다. 카드뉴스에서 넘치면 전체 크기를 줄여 다시 짠다."""
    over = slide.get(fmt, {}) if isinstance(slide.get(fmt), dict) else {}
    slide = {**slide, **over}
    mul = slide.get("scale", 1.0)
    for _ in range(8):
        b = Builder(fmt, mul)
        if slide.get("type") == "outro":
            if slide.get("badge"):
                b.badge(slide["badge"])
            b.outro(slide)
        else:
            if slide.get("badge"):
                b.badge(slide["badge"])
            if slide.get("kicker"):
                b.kicker(slide["kicker"])
            if slide.get("title"):
                b.title(slide["title"], slide.get("title_size", 112))
            if slide.get("sub"):
                b.sub(slide["sub"])
            if slide.get("blocks"):
                b.start_blocks()
                for blk in slide["blocks"]:
                    b.block(blk)
            if slide.get("caption"):
                b.caption(slide["caption"] if isinstance(slide["caption"], list) else [slide["caption"]])
            if slide.get("source"):
                b.source(slide["source"])
        bottom = b.y
        limit = b.F["content_bottom"]
        if bottom <= limit:
            break
        mul *= 0.94
    else:
        b.warnings.append(f"내용이 화면을 넘침 ({bottom}px > {limit}px)")
    if mul != slide.get("scale", 1.0):
        b.warnings.append(f"[{fmt}] 넘쳐서 크기를 {mul:.2f}배로 줄임")
    # 세로 가운데 정렬(넘치지 않을 때만): 위쪽 기준이 예시 영상과 같다. 남는 공간이 크면 약간 내린다
    free = b.F["content_bottom"] - bottom
    shift = int(min(free * 0.25, 120 * b.k)) if slide.get("valign", "top") == "top" else free // 2
    for el in b.els:
        el.y += shift
    anim_end = max((getattr(el, "end", 0) for el in b.els), default=0)
    return b.els, b.warnings, anim_end


# ---------------------------------------------------------------- 배경·상단
def background(fmt, seed=7):
    F = S.FORMATS[fmt]
    W, H = F["W"], F["H"]
    base = np.zeros((H, W, 3), np.float32) + np.array(S.BG, np.float32)
    rng = np.random.default_rng(seed)
    tex = rng.normal(0, 1, (H // 4 + 1, W // 4 + 1)).astype(np.float32)
    tex_im = Image.fromarray(((tex * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    tex_im = tex_im.filter(ImageFilter.GaussianBlur(1.2))
    t = (np.array(tex_im, np.float32) - 128) / 40 * 1.6  # 아주 약한 종이 질감
    base += t[..., None]
    im = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for x in range(0, W + 1, 120):
        d.line([x, 0, x, H], fill=S.GRID, width=1)
    for y in range(0, H + 1, 120):
        d.line([0, y, W, y], fill=S.GRID, width=1)
    return im.convert("RGBA")


def topbar_static(fmt, label, idx, n):
    """라벨·페이지·구분선(진행 바 제외)."""
    F = S.FORMATS[fmt]
    W = F["W"]
    im = Image.new("RGBA", (W, F["rule_y"] + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("mono", int(24 * (1 if fmt == "shorts" else 0.92)))
    d.text((S.MARGIN, F["label_y"]), label, font=f, fill=(92, 88, 82), anchor="ls")
    d.text((W - S.MARGIN, F["label_y"]), f"{idx + 1:02d} / {n:02d}", font=f, fill=(92, 88, 82), anchor="rs")
    d.line([S.MARGIN, F["rule_y"], W - S.MARGIN, F["rule_y"]], fill=S.LINE, width=2)
    return im


def draw_progress(canvas, fmt, idx, n, frac):
    F = S.FORMATS[fmt]
    W = F["W"]
    d = ImageDraw.Draw(canvas)
    gap = 10
    seg = (W - S.MARGIN * 2 - gap * (n - 1)) / n
    y = F["bar_y"]
    h = 6
    for i in range(n):
        x0 = S.MARGIN + i * (seg + gap)
        d.rounded_rectangle([x0, y, x0 + seg, y + h], radius=3, fill=S.LINE)
        f = 1.0 if i < idx else (frac if i == idx else 0)
        if f > 0:
            d.rounded_rectangle([x0, y, x0 + seg * f, y + h], radius=3, fill=S.INK)
