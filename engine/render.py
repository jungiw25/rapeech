"""숏츠 MP4와 카드뉴스 PNG 렌더."""
import multiprocessing as mp
import subprocess
from pathlib import Path

from PIL import Image

from . import scene as SC
from . import style as S

_G = {}  # fork된 작업 프로세스가 공유하는 상태


def _slides_for(spec, fmt):
    key = "in_" + fmt
    return [s for s in spec["slides"] if s.get(key, True)]


def prepare(spec, fmt):
    slides = _slides_for(spec, fmt)
    n = len(slides)
    bg = SC.background(fmt, seed=hash(spec["meta"]["id"]) % 1000)
    out, warns = [], []
    for i, s in enumerate(slides):
        els, w, anim_end = SC.build_slide(s, fmt)
        warns += [f"{i + 1:02d}장: {x}" for x in w]
        top = SC.topbar_static(fmt, s.get("label", ""), i, n)
        dur = float(s.get("dur", S.DEFAULT_DUR))
        out.append(dict(els=els, top=top, dur=dur, anim_end=anim_end))
    return bg, out, warns


def compose(bg, sl, t, idx, n, fmt, final=False):
    canvas = bg.copy()
    for el in sl["els"]:
        el.draw(canvas, t, final=final)
    if not final:
        a = 1.0
        if t > sl["dur"] - S.T_OUT and idx < n - 1:
            a = max(0.0, (sl["dur"] - t) / S.T_OUT)
        if a < 1:
            canvas = Image.blend(bg, canvas, a)
    canvas.alpha_composite(sl["top"])
    SC.draw_progress(canvas, fmt, idx, n, 1.0 if final else min(1.0, t / sl["dur"]))
    return canvas


def _frame(job):
    idx, t = job
    bg, slides, fmt = _G["bg"], _G["slides"], _G["fmt"]
    sl = slides[idx]
    n = len(slides)
    cache = _G.setdefault("static", {})
    if sl["anim_end"] < t < sl["dur"] - S.T_OUT:
        # 애니메이션이 끝난 구간: 콘텐츠는 고정, 진행 바만 다시 그린다
        if idx not in cache:
            c = bg.copy()
            for el in sl["els"]:
                el.draw(c, 1e9, final=True)
            cache[idx] = c
        canvas = cache[idx].copy()
        canvas.alpha_composite(sl["top"])
        SC.draw_progress(canvas, fmt, idx, n, min(1.0, t / sl["dur"]))
    else:
        canvas = compose(bg, sl, t, idx, n, fmt)
    return canvas.convert("RGB").tobytes()


def render_shorts(spec, out_path, wav_path, workers=None):
    fmt = "shorts"
    bg, slides, warns = prepare(spec, fmt)
    _G.update(bg=bg, slides=slides, fmt=fmt)
    jobs = []
    for i, sl in enumerate(slides):
        nf = int(round(sl["dur"] * S.FPS))
        jobs += [(i, k / S.FPS) for k in range(nf)]
    F = S.FORMATS[fmt]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{F['W']}x{F['H']}",
           "-r", str(S.FPS), "-i", "-", "-i", str(wav_path), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out_path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ctx = mp.get_context("fork")
    with ctx.Pool(workers or max(1, mp.cpu_count())) as pool:
        for buf in pool.imap(_frame, jobs, chunksize=6):
            p.stdin.write(buf)
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg 실패")
    return sum(s["dur"] for s in slides), warns


def total_duration(spec):
    return sum(float(s.get("dur", S.DEFAULT_DUR)) for s in _slides_for(spec, "shorts"))


def render_cards(spec, out_dir):
    fmt = "cards"
    bg, slides, warns = prepare(spec, fmt)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    paths = []
    for i, sl in enumerate(slides):
        im = compose(bg, sl, 1e9, i, len(slides), fmt, final=True).convert("RGB")
        p = out_dir / f"{i + 1:02d}.png"
        im.save(p, optimize=True)
        paths.append(p)
    return paths, warns


def shorts_stills(spec, out_dir):
    """숏츠 각 장의 완성 화면(검수용)."""
    fmt = "shorts"
    bg, slides, _ = prepare(spec, fmt)
    ims = [compose(bg, sl, 1e9, i, len(slides), fmt, final=True).convert("RGB") for i, sl in enumerate(slides)]
    return ims


def contact_sheet(ims, path, cols, thumb_w=360):
    th = [im.resize((thumb_w, int(im.size[1] * thumb_w / im.size[0])), Image.LANCZOS) for im in ims]
    h = th[0].size[1]
    rows = (len(th) + cols - 1) // cols
    g = 12
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * g, rows * h + (rows + 1) * g), (40, 40, 40))
    for i, t in enumerate(th):
        sheet.paste(t, (g + (i % cols) * (thumb_w + g), g + (i // cols) * (h + g)))
    sheet.save(path, quality=88)
    return path
