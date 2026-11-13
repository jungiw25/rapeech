"""만든 이미지를 실제 사이트와 같은 방식(cover + 가운데 자르기)으로 화면 너비별로 잘라 보고, 실제 글자 자리를 얹어 확인한다.
수치는 rapeech.careers 를 Chromium으로 열어 잰 값(섹션 크기, 글자 영역). → out/check_*.jpg
"""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
# (화면 너비, 섹션 [w, h], 글자 상자들 [l, t, r, b] …)
M = {
    "history_bg": [(2560, (2560, 1582), [(680, 209, 1180, 330), (1246, 206, 1880, 1582)]), (1920, (1920, 1582), [(360, 209, 860, 330), (926, 206, 1560, 1582)]),
                   (1440, (1440, 1582), [(120, 209, 620, 330), (686, 206, 1320, 1582)]), (1280, (1280, 1582), [(48, 209, 548, 330), (607, 206, 1232, 1582)]),
                   (1024, (1024, 1822), [(48, 209, 465, 390), (489, 206, 976, 1822)]), (768, (768, 1824), [(24, 209, 524, 330), (24, 467, 744, 1824)]), (390, (390, 2592), [(24, 209, 366, 330), (24, 467, 366, 2592)])],
    "bottom_banner": [(2560, (2560, 477), [(980, 134, 1580, 338)]), (1920, (1920, 477), [(660, 134, 1260, 338)]), (1440, (1440, 477), [(420, 134, 1020, 338)]), (1280, (1280, 477), [(340, 134, 940, 338)]),
                      (1024, (1024, 477), [(212, 134, 812, 338)]), (768, (768, 454), [(172, 131, 596, 316)]), (390, (390, 533), [(44, 131, 346, 394)])],
    "about_hero": [(2560, (2560, 438), [(815, 107, 1745, 195), (935, 200, 1625, 240), (1210, 290, 1350, 342)]), (1920, (1920, 438), [(495, 107, 1425, 195), (615, 200, 1305, 240), (890, 290, 1030, 342)]),
                   (1440, (1440, 438), [(255, 107, 1185, 195), (375, 200, 1065, 240), (650, 290, 790, 342)]), (1280, (1280, 438), [(175, 107, 1105, 195), (295, 200, 985, 240), (570, 290, 710, 342)]),
                   (1024, (1024, 510), [(92, 107, 932, 414)]), (768, (768, 464), [(38, 106, 730, 367)]), (390, (390, 572), [(28, 106, 362, 475)])],
    # 채용 공고 배너: 그림 상자(가운데 정렬)와 실제로 보이는 화면 너비
    "recruit_banner": [(2560, (1920, 560), []), (1920, (1920, 560), []), (1440, (1440, 560), []), (1280, (1280, 560), []), (1024, (1024, 560), []), (768, (768, 320), []), (390, (390, 320), [])],
}
BOX = {"recruit_banner": {1280: (1296, 561), 1024: (1296, 561), 768: (863, 321), 390: (863, 321)}}


def cover(im, w, h):
    k = max(w / im.width, h / im.height)
    r = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


for name, rows in M.items():
    im = Image.open(OUT / f"{name}.jpg").convert("RGB")
    tiles = []
    for vw, (w, h), boxes in rows:
        bw, bh = BOX.get(name, {}).get(vw, (w, h))
        v = cover(im, bw, bh)
        if (bw, bh) != (w, h): x = (bw - w) // 2; v = v.crop((x, 0, x + w, h))
        d = ImageDraw.Draw(v, "RGBA")
        for b in boxes: d.rectangle(b, fill=(255, 255, 255, 110), outline=(255, 255, 255, 230), width=2)
        k = 300 / v.height if name != "history_bg" else 520 / v.height
        v = v.resize((max(1, round(v.width * k)), round(v.height * k)))
        t = Image.new("RGB", (v.width, v.height + 26), "white"); t.paste(v, (0, 26)); ImageDraw.Draw(t).text((4, 6), f"{vw}px", fill="black")
        tiles.append(t)
    W = sum(t.width for t in tiles) + 10 * (len(tiles) + 1)
    if name == "history_bg":
        g = Image.new("RGB", (W, tiles[0].height + 20), "white"); x = 10
        for t in tiles: g.paste(t, (x, 10)); x += t.width + 10
    else:
        W = max(t.width for t in tiles) + 20; g = Image.new("RGB", (W, sum(t.height + 8 for t in tiles) + 12), "white"); y = 8
        for t in tiles: g.paste(t, (10, y)); y += t.height + 8
    g.save(OUT / f"check_{name}.jpg", quality=85); print(OUT / f"check_{name}.jpg", g.size)
