"""렌더 결과로 시안 4 디자인 시트를 만든다. 사용법: python3 sheet.py → out/rapi4_sheet.png (먼저 compose.py hero)"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FONT = HERE.parent / "brand-film/assets/fonts"
f = lambda w, s: ImageFont.truetype(str(FONT / f"Pretendard-{w}.otf"), s)
INK, SUB, ACC, CARD = "#22134a", "#76699c", "#7c51ff", (236, 229, 255)


def cutout(name, size):
    """투명 렌더의 바닥 그림자를 보랏빛으로 옅게 바꾸고 카드 색 위에 올림."""
    im = Image.open(OUT / f"{name}.png").convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            if 0 < a < 250 and r + g + b < 60:
                px[x, y] = (96, 66, 190, int(a * 0.45))
    card = Image.new("RGBA", im.size, CARD + (255,))
    card.alpha_composite(im)
    return card.resize(size)


def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.size[0] - 1, img.size[1] - 1), r, fill=255)
    return m


sheet = Image.new("RGB", (2400, 1500), "#faf7ff")
d = ImageDraw.Draw(sheet)
d.text((80, 46), "라피", font=f("Black", 96), fill=INK)
d.text((330, 88), "라피치 캐릭터 시안 4 · 가칭", font=f("SemiBold", 34), fill=SUB)

hero = Image.open(OUT / "hero.png").convert("RGB").resize((1180, 811))
sheet.paste(hero, (60, 170), rounded(hero, 40))

x0 = 1300
d.text((x0, 150), "돌려 보기", font=f("Bold", 34), fill=INK)
for i, (n, lab) in enumerate((("front", "앞"), ("side", "옆"), ("back", "뒤"))):
    im = cutout(n, (330, 330))
    sheet.paste(im, (x0 + i * 350, 205), rounded(im, 30))
    d.text((x0 + i * 350 + 165, 560), lab, font=f("SemiBold", 28), fill=SUB, anchor="mm")

d.text((x0, 615), "표정", font=f("Bold", 34), fill=INK)
for i, (n, lab) in enumerate((("e_brave", "자신감"), ("e_happy", "반가워요"), ("e_surprise", "어?"), ("e_listen", "듣는 중"))):
    im = cutout(n, (250, 250))
    sheet.paste(im, (x0 + i * 265, 670), rounded(im, 26))
    d.text((x0 + i * 265 + 125, 950), lab, font=f("SemiBold", 28), fill=SUB, anchor="mm")

notes = [("그림체", "외곽선 없는 부드러운 무광 3D, 위는 보라 · 아래는 분홍으로 번지는 색"),
         ("몸", "모서리가 둥근 블록 + 왼쪽 아래 작은 말풍선 꼬리('대화')"),
         ("얼굴", "크고 동그란 눈과 굵은 눈썹으로 표정을 냄(입은 필요할 때만)"),
         ("소품", "한쪽 귀 헤드셋과 마이크(목소리 AI), 수정처럼 빛나는 말풍선"),
         ("색", "라피치 보라·분홍만 사용, 로고 모양은 직접 쓰지 않음")]
for i, (k, v) in enumerate(notes):
    y = 1030 + i * 82
    d.rounded_rectangle((80, y, 230, y + 52), 26, fill=ACC)
    d.text((155, y + 26), k, font=f("Bold", 26), fill="#fff", anchor="mm")
    d.text((256, y + 26), v, font=f("SemiBold", 30), fill=INK, anchor="lm")
for i, (c, lab) in enumerate((("#b39aff", "윗몸"), ("#8d5cff", "가운데"), ("#ff6fb4", "아랫몸"), ("#ff4fae", "헤드셋"), ("#22134a", "눈썹·눈동자"))):
    x, y = 1300 + (i % 3) * 330, 1040 + (i // 3) * 110
    d.ellipse((x, y, x + 64, y + 64), fill=c)
    d.text((x + 84, y + 32), lab, font=f("SemiBold", 28), fill=INK, anchor="lm")
d.text((1300, 990), "색", font=f("Bold", 34), fill=INK)
sheet.save(OUT / "rapi4_sheet.png")
print(OUT / "rapi4_sheet.png")
