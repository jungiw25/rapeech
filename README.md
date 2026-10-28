# Rapeech AI 콘텐츠 공장

주제 하나 → 블로그 글 · 인스타 카드뉴스(1080×1350) · 유튜브 숏츠(1080×1920, 배경음악 포함)를 자동으로 만들고, 사람 검수 후 게시합니다.

- Claude Code에서: `/topics` → 후보 선택 → `/make 2` → 검수 → 승인
- 직접 빌드: `python3 -m engine.build content/01-ai-dangjik` (Python 3, Pillow, numpy, ffmpeg 필요)
- 규칙·디자인·스펙: `CLAUDE.md`

폰트: Pretendard (SIL OFL 1.1), JetBrains Mono (OFL/Apache-2.0) — 재배포 가능, `assets/fonts/`.
