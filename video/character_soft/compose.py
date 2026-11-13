"""캐릭터 렌더(투명 배경) 뒤에 그림 같은 배경을 그려 합친다. 사용법: python3 compose.py [이름…]"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def background(w, h, seed=0):
    bg = Image.new("RGB", (w, h))
    px = bg.load()
    a, b = (244, 238, 255), (196, 178, 255)          # 왼쪽 위는 밝게, 오른쪽 아래는 연보라
    for y in range(h):
        for x in range(0, w):
            t = min(1, max(0, (x / w) * 0.55 + (y / h) * 0.6))
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, r = w * 0.52, h * 0.5, h * 0.38                  # 캐릭터 뒤 큰 원
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(178, 156, 255, 120))
    for k, (rr, a0, a1) in enumerate(((h * 0.36, 200, 300), (h * 0.46, 215, 330))):   # 가는 흰 호
        d.arc((cx - rr - 120 + k * 200, cy - rr - 40, cx + rr - 120 + k * 200, cy + rr - 40), a0, a1, fill=(255, 255, 255, 170), width=4)
    def streak(x0, y0, length, thick, col):              # 대각선 빛줄기(평행사변형)
        ang = math.radians(-28)
        dx, dy = math.cos(ang) * length, math.sin(ang) * length
        nx, ny = -math.sin(ang) * thick, math.cos(ang) * thick
        d.polygon([(x0, y0), (x0 + dx, y0 + dy), (x0 + dx + nx, y0 + dy + ny), (x0 + nx, y0 + ny)], fill=col)
    streak(-60, h * 0.78, w * 0.32, 46, (140, 108, 245, 150))
    streak(w * 0.02, h * 0.86, w * 0.24, 14, (255, 255, 255, 160))
    streak(w * 0.7, h * 0.42, w * 0.34, 54, (150, 118, 250, 140))
    streak(w * 0.74, h * 0.6, w * 0.16, 22, (255, 140, 120, 150))
    streak(w * 0.68, h * 0.72, w * 0.22, 12, (140, 108, 245, 160))
    for (x, y, rr, col) in ((w * 0.22, h * 0.3, 9, (232, 70, 110, 230)), (w * 0.79, h * 0.75, 11, (140, 108, 245, 220))):
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(1.6))
    bg = Image.alpha_composite(bg.convert("RGBA"), lay)
    # 반짝이 별(네 갈래)
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    def star(x, y, s):
        sd.polygon([(x, y - s), (x + s * .2, y - s * .2), (x + s, y), (x + s * .2, y + s * .2), (x, y + s), (x - s * .2, y + s * .2), (x - s, y), (x - s * .2, y - s * .2)], fill=(255, 255, 255, 240))
    star(w * 0.62, h * 0.16, 30); star(w * 0.3, h * 0.2, 12)
    return Image.alpha_composite(bg, st.filter(ImageFilter.GaussianBlur(0.6)))


if __name__ == "__main__":
    for name in sys.argv[1:] or ["hero"]:
        ch = Image.open(OUT / f"{name}_char.png").convert("RGBA")
        # 바닥 그림자(검은 반투명)를 보랏빛 그림자로
        px = ch.load()
        for y in range(ch.size[1]):
            for x in range(ch.size[0]):
                r, g, b_, a_ = px[x, y]
                if 0 < a_ < 250 and r + g + b_ < 60:
                    px[x, y] = (96, 66, 190, int(a_ * 0.6))
        img = Image.alpha_composite(background(*ch.size), ch)
        img.convert("RGB").save(OUT / f"{name}.png")
        print(OUT / f"{name}.png")
