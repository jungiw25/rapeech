"""렌더한 이미지로 캐릭터 디자인 시트를 만든다. 사용법: python3 sheet.py → out/rapi_sheet.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FONT = HERE.parent / "brand-film/assets/fonts"
f = lambda w, s: ImageFont.truetype(str(FONT / f"Pretendard-{w}.otf"), s)
INK, SUB, ACC = "#1e1245", "#6e6390", "#7c51ff"

W, H = 2400, 1500
sheet = Image.new("RGB", (W, H), "#fff7f3")
d = ImageDraw.Draw(sheet)

# 왼쪽: 대표 이미지
hero = Image.open(OUT / "hero.png").convert("RGB").resize((1000, 1000))
sheet.paste(hero, (60, 200))
d.text((80, 60), "라피", font=f("Black", 88), fill=INK)
d.text((300, 92), "RAPI · 라피치 캐릭터 시안", font=f("SemiBold", 34), fill=SUB)

# 오른쪽 위: 앞·옆·뒤
x0, y0 = 1120, 200
d.text((x0, y0 - 6), "돌려 보기", font=f("Bold", 34), fill=INK)
for i, (n, lab) in enumerate((("front", "앞"), ("side", "옆"), ("back", "뒤"))):
    im = Image.open(OUT / f"{n}.png").convert("RGBA").resize((400, 400))
    sheet.paste(im, (x0 + i * 410, y0 + 40), im)
    d.text((x0 + i * 410 + 200, y0 + 440), lab, font=f("SemiBold", 28), fill=SUB, anchor="mm")

# 오른쪽 가운데: 표정
y1 = 720
d.text((x0, y1), "표정", font=f("Bold", 34), fill=INK)
for i, (n, lab) in enumerate((("e_brave", "자신감"), ("e_listen", "듣는 중"), ("e_think", "생각 중"))):
    im = Image.open(OUT / f"{n}.png").convert("RGBA").resize((400, 400))
    bg = Image.new("RGBA", im.size, "#f3ecff")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 399, 399), 36, fill=255)
    bg.alpha_composite(im)
    sheet.paste(bg, (x0 + i * 410, y1 + 50), mask)
    d.text((x0 + i * 410 + 200, y1 + 480), lab, font=f("SemiBold", 28), fill=SUB, anchor="mm")

# 아래: 설계 의도
y2 = 1250
notes = [("몸", "라피치 심볼의 아래쪽 삼각형을 둥근 모서리의 두툼한 입체로"),
         ("머리 볏", "심볼 위쪽의 줄무늬를 목소리 파형처럼 세움"),
         ("헤드셋", "고객의 목소리를 듣고 답하는 대화형 AI(콜봇·상담)"),
         ("색", "로고의 보라 그라데이션, 헤드셋과 볏 끝은 분홍 포인트")]
for i, (k, v) in enumerate(notes):
    x = 80 + (i % 2) * 1160
    y = y2 + (i // 2) * 90
    d.rounded_rectangle((x, y, x + 150, y + 56), 28, fill=ACC)
    d.text((x + 75, y + 28), k, font=f("Bold", 26), fill="#fff", anchor="mm")
    d.text((x + 175, y + 28), v, font=f("SemiBold", 30), fill=INK, anchor="lm")

sheet.save(OUT / "rapi_sheet.png")
print(OUT / "rapi_sheet.png")
