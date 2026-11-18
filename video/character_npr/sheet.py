"""렌더 결과로 디자인 시트를 만든다. 사용법: python3 sheet.py → out/rapi3_sheet.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FONT = HERE.parent / "brand-film/assets/fonts"
f = lambda w, s: ImageFont.truetype(str(FONT / f"Pretendard-{w}.otf"), s)
INK, SUB, ACC = "#2b1d55", "#75699a", "#7c51ff"

sheet = Image.new("RGB", (2400, 1500), "#fff3ea")
d = ImageDraw.Draw(sheet)
d.text((90, 50), "라피", font=f("Black", 96), fill=INK)
d.text((340, 92), "라피치 캐릭터 시안 3 · 3D 툰 셰이딩 · 가칭", font=f("SemiBold", 34), fill=SUB)
sheet.paste(Image.open(OUT / "hero.png").convert("RGB").resize((1040, 1040)), (40, 170))
for i, (n, lab) in enumerate((("front", "앞"), ("side", "옆"), ("back", "뒤"), ("cheer", "화이팅!"))):
    x, y = 1130 + (i % 2) * 630, 170 + (i // 2) * 560
    sheet.paste(Image.open(OUT / f"{n}.png").convert("RGB").resize((500, 500)), (x, y))
    d.text((x + 250, y + 520), lab, font=f("Bold", 32), fill=INK, anchor="mm")
notes = [("그림체", "3D 모델 + 툰(셀) 셰이딩: 그림자 두 단계, 보라빛 그림자, 굵은 외곽선"),
         ("몸", "말랑한 말풍선 모양, 왼쪽 아래 작은 꼬리로 '대화'를 담음"),
         ("헤드폰", "목소리를 듣고 답하는 대화형 AI"),
         ("잎 세 가닥", "라피치 로고의 비스듬한 줄무늬를 살짝")]
for i, (k, v) in enumerate(notes):
    y = 1260 + i * 56
    d.text((90, y), k, font=f("Bold", 30), fill=ACC)
    d.text((290, y), v, font=f("SemiBold", 30), fill=INK)
sheet.save(OUT / "rapi3_sheet.png")
print(OUT / "rapi3_sheet.png")
