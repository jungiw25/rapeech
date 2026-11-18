"""라피치 캐릭터 시안 2: 손으로 그린 듯한 평면 일러스트(외곽선 + 단색 + 그림자 한 단계 + 하이라이트 한 점).

말풍선 모양의 말랑한 몸(왼쪽 아래 작은 꼬리) → '대화'
머리 위 비스듬한 잎 세 가닥 → 로고 줄무늬를 아주 살짝만
동그란 헤드폰과 작은 마이크 → 목소리를 듣고 답하는 AI
사용법: python3 build.py && node shot.mjs → out/rapi2_sheet.png
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINE, BODY, SHADE, HI, PINK, PINK2, CHEEK = "#2b1d55", "#9a7cff", "#7a58ee", "#c4b2ff", "#ff7cc4", "#ffb3dd", "#ff9ec4"
BODY_D = ("M300 178 C392 178 456 230 460 312 C464 394 404 452 300 452 C252 452 214 444 186 426 "
          "C176 440 160 452 140 458 C152 442 158 424 158 404 C142 380 138 348 140 314 C144 228 208 178 300 178 Z")
SW = 7  # 외곽선 굵기


def eyes(kind):
    if kind == "happy":   # 웃는 눈(^ ^)
        return "".join(f'<path d="M{x - 17} 304 Q{x} 284 {x + 17} 304" fill="none" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>' for x in (256, 344))
    dx, dy, ry = {"look": (0, 0, 21), "listen": (6, -5, 21), "think": (-7, -7, 19), "wow": (0, -2, 25)}[kind]
    out = ""
    for x in (256, 344):
        out += (f'<ellipse cx="{x + dx}" cy="{300 + dy}" rx="{15 if kind != "wow" else 17}" ry="{ry}" fill="{LINE}"/>'
                f'<circle cx="{x + dx + 5}" cy="{300 + dy - 8}" r="5.5" fill="#fff"/>')
    return out


def mouth(kind):
    return {
        "smile": f'<path d="M286 334 Q300 346 314 334" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>',
        "open": (f'<path d="M282 330 Q300 330 318 330 Q316 356 300 356 Q284 356 282 330 Z" fill="{LINE}" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M290 349 Q300 342 310 349 Q306 355 300 355 Q294 355 290 349 Z" fill="#ff7a9c"/>'),
        "o": f'<ellipse cx="300" cy="340" rx="9" ry="11" fill="{LINE}"/>',
        "flat": f'<path d="M288 340 Q294 336 300 340 Q306 344 312 340" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>',
    }[kind]


def arm(x, y, rot, front=True):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><ellipse cx="0" cy="0" rx="25" ry="34" fill="{BODY}" stroke="{LINE}" stroke-width="{SW}"/>'
            f'<path d="M-12 14 Q0 26 12 14" fill="none" stroke="{SHADE}" stroke-width="7" stroke-linecap="round"/></g>')


def rapi(expr="look", mouth_kind="smile", pose="stand", extra="", back=False):
    arms = {
        "stand": arm(150, 392, 34) + arm(450, 392, -34),
        "wave": arm(150, 392, 34) + arm(492, 236, -140) + f'<path d="M520 182 q14 -6 22 4 M532 214 q14 0 18 12" fill="none" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>',
        "listen": arm(150, 392, 34) + arm(486, 300, -165),
        "think": arm(226, 392, 150) + arm(450, 392, -34),
        "cheer": arm(110, 236, 150) + arm(490, 236, -150),
    }[pose]
    return f'''<svg viewBox="0 0 600 560" xmlns="http://www.w3.org/2000/svg">
<defs><clipPath id="bc"><path d="{BODY_D}"/></clipPath></defs>
<ellipse cx="300" cy="490" rx="130" ry="15" fill="{LINE}" opacity=".09"/>
<ellipse cx="256" cy="462" rx="36" ry="20" fill="{SHADE}" stroke="{LINE}" stroke-width="{SW}"/>
<ellipse cx="344" cy="462" rx="36" ry="20" fill="{SHADE}" stroke="{LINE}" stroke-width="{SW}"/>
<!-- 헤드폰 띠(머리 뒤) -->
<path d="M152 290 C150 96 450 96 448 290" fill="none" stroke="{LINE}" stroke-width="22" stroke-linecap="round"/>
<path d="M152 290 C150 96 450 96 448 290" fill="none" stroke="{PINK2}" stroke-width="9" stroke-linecap="round"/>
<!-- 잎 세 가닥(로고 줄무늬를 살짝) -->
<g stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round">
  <path d="M276 184 C270 160 278 140 292 128 C300 146 296 168 286 184 Z" fill="{PINK}"/>
  <path d="M296 182 C296 152 310 128 330 116 C334 142 324 166 308 182 Z" fill="{PINK}"/>
  <path d="M318 184 C324 162 340 148 358 142 C358 162 346 178 330 188 Z" fill="{PINK2}"/>
</g>
<!-- 몸 -->
<path d="{BODY_D}" fill="{SHADE}"/>
<g clip-path="url(#bc)"><ellipse cx="282" cy="296" rx="176" ry="150" fill="{BODY}"/></g>
<path d="{BODY_D}" fill="none" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M206 236 Q222 214 248 206" fill="none" stroke="{HI}" stroke-width="12" stroke-linecap="round"/>
<circle cx="196" cy="258" r="7" fill="{HI}"/>
<!-- 얼굴 -->
{"" if back else f'<ellipse cx="214" cy="336" rx="22" ry="13" fill="{CHEEK}" opacity=".85"/><ellipse cx="386" cy="336" rx="22" ry="13" fill="{CHEEK}" opacity=".85"/>'}
{"" if back else eyes(expr) + mouth(mouth_kind)}
<!-- 헤드폰 귀 + 마이크 -->
<rect x="128" y="262" width="44" height="74" rx="22" fill="{PINK}" stroke="{LINE}" stroke-width="{SW}"/>
<rect x="428" y="262" width="44" height="74" rx="22" fill="{PINK}" stroke="{LINE}" stroke-width="{SW}"/>
{"" if back else f'<path d="M440 330 C430 372 400 384 360 380" fill="none" stroke="{LINE}" stroke-width="{SW}" stroke-linecap="round"/>'}
{"" if back else f'<circle cx="356" cy="380" r="11" fill="{LINE}"/>'}
{arms}{extra}
</svg>'''


def sheet():
    think_bubble = (f'<g stroke="{LINE}" stroke-width="5" fill="#fff"><circle cx="150" cy="190" r="9"/><circle cx="120" cy="150" r="14"/>'
                    f'<rect x="40" y="70" width="110" height="60" rx="30"/></g>'
                    f'<g fill="{LINE}"><circle cx="72" cy="100" r="6"/><circle cx="95" cy="100" r="6"/><circle cx="118" cy="100" r="6"/></g>')
    exprs = [("반가워요", rapi("happy", "open", "wave")), ("듣고 있어요", rapi("listen", "o", "listen")),
             ("음… 생각 중", rapi("think", "flat", "think", think_bubble)), ("어!", rapi("wow", "o", "stand"))]
    poses = [("기본", rapi("look", "smile", "stand")), ("뒷모습", rapi(back=True).replace("<svg ", '<svg style="transform:scaleX(-1)" ', 1)), ("화이팅!", rapi("happy", "open", "cheer"))]
    chips = [(BODY, "몸"), (SHADE, "그림자"), (PINK, "헤드폰·잎"), (LINE, "선")]
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: P; font-weight: 900; src: url("../brand-film/assets/fonts/Pretendard-Black.otf"); }}
@font-face {{ font-family: P; font-weight: 700; src: url("../brand-film/assets/fonts/Pretendard-Bold.otf"); }}
@font-face {{ font-family: P; font-weight: 600; src: url("../brand-film/assets/fonts/Pretendard-SemiBold.otf"); }}
body {{ margin: 0; }}
#s {{ width: 2400px; height: 1500px; background: #fff8ef; font-family: P; color: {LINE}; position: relative; overflow: hidden; }}
h1 {{ position: absolute; left: 90px; top: 50px; margin: 0; font-size: 96px; font-weight: 900; letter-spacing: -0.02em; }}
.sub {{ position: absolute; left: 350px; top: 92px; font-size: 34px; font-weight: 600; color: #75699a; }}
.main {{ position: absolute; left: 40px; top: 170px; width: 1040px; height: 970px; background: #f1eaff; border-radius: 48px; }}
.main svg {{ width: 1000px; height: 933px; margin: 20px; }}
.ex {{ position: absolute; top: 170px; width: 300px; text-align: center; font-size: 30px; font-weight: 700; }}
.ex .card {{ width: 300px; height: 300px; background: #fff; border-radius: 36px; box-shadow: inset 0 0 0 4px #efe6ff; }}
.ex svg {{ width: 280px; height: 262px; margin-top: 18px; }}
.ex p {{ margin: 14px 0 0; }}
h2 {{ position: absolute; left: 1140px; margin: 0; font-size: 36px; font-weight: 700; }}
.chip {{ position: absolute; top: 1010px; display: flex; align-items: center; gap: 16px; font-size: 28px; font-weight: 600; }}
.chip i {{ width: 64px; height: 64px; border-radius: 50%; display: inline-block; box-shadow: inset 0 0 0 5px {LINE}; }}
.note {{ position: absolute; left: 1140px; top: 1150px; width: 1180px; font-size: 30px; font-weight: 600; line-height: 1.75; }}
.note b {{ display: inline-block; min-width: 150px; color: #7c51ff; }}
</style></head><body><div id="s">
<h1>라피</h1><div class="sub">라피치 캐릭터 시안 2 · 가칭</div>
<div class="main">{rapi("look", "smile", "wave")}</div>
<h2 style="top:120px">표정</h2>
<h2 style="top:520px">자세</h2>
{"".join(f'<div class="ex" style="left:{1140 + i * 315}px"><div class="card">{svg}</div><p>{lab}</p></div>' for i, (lab, svg) in enumerate(exprs))}
{"".join(f'<div class="ex" style="left:{1140 + i * 315}px;top:570px"><div class="card">{svg}</div><p>{lab}</p></div>' for i, (lab, svg) in enumerate(poses))}
<h2 style="top:940px">색</h2>
{"".join(f'<div class="chip" style="left:{1140 + i * 300}px"><i style="background:{c}"></i>{lab}</div>' for i, (c, lab) in enumerate(chips))}
<div class="note">
<b>몸</b>말랑한 말풍선 모양. 왼쪽 아래 작은 꼬리로 '대화'를 담음<br>
<b>헤드폰</b>고객의 목소리를 듣고 답하는 대화형 AI<br>
<b>잎 세 가닥</b>라피치 로고의 비스듬한 줄무늬를 아주 살짝만<br>
<b>그림체</b>굵은 외곽선, 단색 + 그림자 한 단계 + 하이라이트, 점 눈과 볼터치
</div>
</div></body></html>'''


if __name__ == "__main__":
    (HERE / "sheet.html").write_text(sheet(), encoding="utf-8")
    (HERE / "rapi.svg").write_text(rapi("look", "smile", "wave"), encoding="utf-8")
    print("ok")
