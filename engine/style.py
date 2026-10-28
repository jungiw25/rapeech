"""디자인 상수. 예시 영상(diripda 형식) 기준. 색을 바꿀 땐 여기만 고친다."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
BRAND_DIR = ROOT / "brand"

# 색
BG = (232, 228, 220)        # 베이지 #E8E4DC
GRID = (220, 215, 205)      # 옅은 그리드
INK = (22, 22, 22)          # 타이틀 검정
CARD = (27, 27, 27)         # 데이터 카드 #1B1B1B
CARD_DIM = (58, 56, 53)     # BEFORE 등 보조 카드
YELLOW = (242, 193, 78)     # 숫자 #F2C14E
ORANGE = (215, 56, 46)      # 강조 #D7382E (보라 금지: 보라는 로고만)
WHITE = (255, 255, 255)
GRAY_ON_DARK = (165, 162, 156)
GRAY_ON_LIGHT = (112, 108, 100)
LINE = (204, 199, 189)      # 구분선, 진행 바 빈 칸
PILL_BG = (243, 240, 234)
GREEN = (88, 190, 120)

# 폰트 파일
FONTS = {
    "black": "Pretendard-Black.otf",
    "xbold": "Pretendard-ExtraBold.otf",
    "bold": "Pretendard-Bold.otf",
    "semi": "Pretendard-SemiBold.otf",
    "medium": "Pretendard-Medium.otf",
    "regular": "Pretendard-Regular.otf",
    "mono": "JetBrainsMono-Bold.ttf",
    "mono_m": "JetBrainsMono-Medium.ttf",
}

# 규격
FORMATS = {
    # 숏츠: 하단 350px은 유튜브/릴스 UI가 덮으므로 비워 둔다
    "shorts": dict(W=1080, H=1920, scale=1.0, bar_y=130, label_y=186, rule_y=236,
                   content_top=330, content_bottom=1560),
    # 카드뉴스(인스타 4:5)
    "cards": dict(W=1080, H=1350, scale=0.86, bar_y=64, label_y=116, rule_y=160,
                  content_top=236, content_bottom=1290),
}
MARGIN = 60
FPS = 30

# 애니메이션 타이밍(초)
T_LINE_GAP = 0.13     # 줄 간격 등장
T_FADE = 0.45         # 페이드인 길이
T_RISE = 36           # 올라오는 거리(px)
T_CARD = 0.75         # 카드 첫 등장
T_CARD_GAP = 0.28     # 카드 사이
T_ROW_GAP = 0.12      # 표/불릿 행 사이
T_COUNT = 0.9         # 숫자 카운트업
T_SWEEP = 0.38        # 강조 박스 쓸림
T_OUT = 0.32          # 장 끝 페이드아웃
DEFAULT_DUR = 5.6     # 장당 길이
