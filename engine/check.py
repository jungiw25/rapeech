"""콘텐츠 원칙 자동 검사. FAIL이 하나라도 있으면 검수 요청 전에 고친다."""
import json
import re
import subprocess
from pathlib import Path

from . import style as S

RULES = json.loads((Path(__file__).parent / "rules.json").read_text(encoding="utf-8"))


def _strings(obj, skip=("source", "sources", "url", "label", "_note")):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from _strings(x, skip)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip:
                yield from _strings(v, skip)


def _find(term, text):
    if re.fullmatch(r"[A-Za-z0-9+\- ]+", term):
        return re.search(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", text, re.I)
    return term in text


def scan_text(text, where):
    res = []
    for group, level in (("negative_phrases", "FAIL"), ("excluded_topics", "FAIL"),
                         ("customer_names", "FAIL"), ("competitor_names", "FAIL")):
        for term in RULES[group]:
            if _find(term, text):
                res.append((level, f"{where}: 금지 항목 '{term}' ({group})"))
    if re.search(r"보라|purple", text, re.I):
        res.append(("WARN", f"{where}: 보라색 언급 - 강조색은 주황만"))
    return res


def blog_body(md):
    """출처 절 앞까지 본문."""
    m = re.search(r"^#+\s*(출처|참고)", md, re.M)
    return md[: m.start()] if m else md


def count_chars(md):
    body = blog_body(md)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"[#>*`_\-|]", "", body)
    return len(re.sub(r"\s", "", body)), len(body.strip())


def check(ep_dir, video=None, cards=None, wav_noise=None):
    ep = Path(ep_dir)
    spec = json.loads((ep / "spec.json").read_text(encoding="utf-8"))
    res = []
    # 1) 슬라이드 문구
    for i, s in enumerate(spec["slides"]):
        res += scan_text("\n".join(_strings(s)), f"슬라이드 {i + 1}")
        if s.get("part") == "news" and not s.get("source"):
            res.append(("FAIL", f"슬라이드 {i + 1}: 뉴스 장에 출처 태그 없음"))
    # 2) 출처 목록
    srcs = spec["meta"].get("sources", [])
    if not srcs:
        res.append(("FAIL", "meta.sources 비어 있음"))
    for s in srcs:
        if not s.get("url") or not s.get("date"):
            res.append(("WARN", f"출처에 url/date 누락: {s.get('name')}"))
    # 3) 뉴스:라피치 비율
    body = [s for s in spec["slides"] if s.get("part") in ("news", "insight", "rapeech")]
    if body:
        r = sum(s["part"] == "rapeech" for s in body) / len(body)
        lo, hi = RULES["rapeech_ratio"]
        lvl = "OK" if lo <= r <= hi else "WARN"
        res.append((lvl, f"라피치 비중 {r:.0%} (목표 약 40%, 허용 {lo:.0%}~{hi:.0%})"))
    # 4) 장 수
    ns = sum(s.get("in_shorts", True) for s in spec["slides"])
    nc = sum(s.get("in_cards", True) for s in spec["slides"])
    for name, n, key in (("숏츠", ns, "shorts_slides"), ("카드뉴스", nc, "cards_slides")):
        lo, hi = RULES[key]
        res.append(("OK" if lo <= n <= hi else "FAIL", f"{name} {n}장 (기준 {lo}~{hi})"))
    # 5) 블로그
    bp = ep / "blog.md"
    if bp.exists():
        md = bp.read_text(encoding="utf-8")
        res += scan_text(blog_body(md), "블로그")
        nospace, withspace = count_chars(md)
        lo, hi = RULES["blog_chars"]
        res.append(("OK" if lo <= withspace <= hi + 300 else "WARN",
                    f"블로그 본문 {withspace}자(공백 포함) / {nospace}자(공백 제외), 기준 {lo}~{hi}자"))
        if not re.search(r"^#+\s*(출처|참고)", md, re.M):
            res.append(("FAIL", "블로그에 출처 절 없음"))
        if len(re.findall(r"^## ", md, re.M)) < 3:
            res.append(("WARN", "블로그 소제목(##)이 3개 미만"))
    else:
        res.append(("WARN", "blog.md 없음"))
    cp = ep / "caption.md"
    if cp.exists():
        res += scan_text(blog_body(cp.read_text(encoding="utf-8")), "캡션")
    # 6) 결과물 규격
    if video and Path(video).exists():
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                              "-of", "json", str(video)], capture_output=True, text=True).stdout
        info = json.loads(out)
        v = [s for s in info["streams"] if s.get("width")][0]
        dur = float(info["format"]["duration"])
        ok = (v["width"], v["height"]) == (1080, 1920) and v["r_frame_rate"] == "30/1"
        res.append(("OK" if ok else "FAIL", f"숏츠 규격 {v['width']}x{v['height']} {v['r_frame_rate']}fps"))
        lo, hi = RULES["shorts_seconds"]
        res.append(("OK" if lo <= dur <= hi else "WARN", f"숏츠 길이 {dur:.1f}초 (기준 {lo}~{hi})"))
    if cards:
        from PIL import Image
        sizes = {Image.open(p).size for p in cards}
        res.append(("OK" if sizes == {(1080, 1350)} else "FAIL", f"카드뉴스 크기 {sizes}"))
    if wav_noise is not None:
        res.append(("OK" if wav_noise < 0.002 else "WARN", f"배경음악 고음역 에너지 {wav_noise:.5f} (노이즈 없음 기준 < 0.002)"))
    return res


def report(res):
    lines = []
    for lvl, msg in res:
        icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}[lvl]
        lines.append(f"- {icon} {msg}")
    return "\n".join(lines)
